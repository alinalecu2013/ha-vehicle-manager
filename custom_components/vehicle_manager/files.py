"""Dosarul vehiculului: poze si PDF-uri atasate actelor (polita, talon...).

Fisierele sunt in config/vehicle_manager_documente/<vehicul>/, in afara folderului
www: /local este public, iar actele contin date personale. Se servesc doar prin
API-ul autentificat (cardul foloseste linkuri semnate, valabile un minut).
"""

from __future__ import annotations

import secrets
import shutil
from pathlib import Path
from typing import Any
from urllib.parse import quote

from aiohttp import web
import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import CONF_FILES_ADMIN_ONLY, DOCUMENTS, DOMAIN

STORAGE_KEY = f"{DOMAIN}.files"
STORAGE_VERSION = 1
FILES_DIRNAME = "vehicle_manager_documente"

DATA_FILES = "file_manager"
# Pe langa acte: talon, cartea masinii, procese-verbale etc.
GENERAL_SLOT = "general"
MAX_BYTES = 20 * 1024 * 1024
# limite pe vehicul, ca un cont compromis sa nu poata umple discul
MAX_FILES_PER_VEHICLE = 100
MAX_TOTAL_BYTES = 200 * 1024 * 1024
NAME_MAX = 120

WS_SUBSCRIBE = f"{DOMAIN}/files/subscribe"
WS_DELETE = f"{DOMAIN}/files/delete"

# Tipul se stabileste din continut, nu din extensia trimisa de browser.
SIGNATURES: tuple[tuple[bytes, int, str, str], ...] = (
    (b"\xff\xd8\xff", 0, ".jpg", "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n", 0, ".png", "image/png"),
    (b"GIF8", 0, ".gif", "image/gif"),
    (b"WEBP", 8, ".webp", "image/webp"),
    (b"%PDF-", 0, ".pdf", "application/pdf"),
)


def detect_type(head: bytes) -> tuple[str, str] | None:
    """(extensie, mime) dupa primii octeti, sau None daca tipul nu e acceptat."""
    for signature, offset, extension, mime in SIGNATURES:
        if head[offset : offset + len(signature)] == signature:
            return extension, mime
    return None


def valid_slot(slot: str) -> bool:
    return slot == GENERAL_SLOT or slot in DOCUMENTS


def signal_files(entry_id: str) -> str:
    return f"{DOMAIN}_files_{entry_id}"


def clean_name(name: str) -> str:
    """Numele afisat: fara cai sau caractere de control."""
    name = Path(name or "").name.strip()
    name = "".join(ch for ch in name if ch.isprintable() and ch not in '"\\/')
    return name[:NAME_MAX] or "document"


class FileManager:
    """Metadatele fisierelor (in .storage) si fisierele de pe disc."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.root = Path(hass.config.path(FILES_DIRNAME))
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: dict[str, list[dict[str, Any]]] = {}

    async def async_load(self) -> None:
        stored = await self._store.async_load()
        self._data = (stored or {}).get("files", {})

    def files(self, entry_id: str) -> list[dict[str, Any]]:
        """Fisierele unui vehicul, cele mai noi primele (fara calea de pe disc)."""
        items = sorted(self._data.get(entry_id, []), key=lambda f: f["uploaded"], reverse=True)
        return [{k: v for k, v in item.items() if k != "file"} for item in items]

    def usage(self, entry_id: str) -> tuple[int, int]:
        """(numar de fisiere, octeti) folositi de un vehicul."""
        items = self._data.get(entry_id, [])
        return len(items), sum(item["size"] for item in items)

    def find(self, entry_id: str, file_id: str) -> tuple[dict[str, Any], Path] | None:
        for item in self._data.get(entry_id, []):
            if item["id"] == file_id:
                return item, self.root / entry_id / item["file"]
        return None

    async def async_add(
        self, entry_id: str, slot: str, name: str, content: bytes, extension: str, mime: str
    ) -> dict[str, Any]:
        file_id = secrets.token_hex(8)
        filename = f"{file_id}{extension}"
        target = self.root / entry_id / filename

        def _write() -> None:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)

        await self.hass.async_add_executor_job(_write)
        item = {
            "id": file_id,
            "slot": slot,
            "name": clean_name(name),
            "mime": mime,
            "size": len(content),
            "uploaded": dt_util.now().isoformat(timespec="seconds"),
            "file": filename,
        }
        self._data.setdefault(entry_id, []).append(item)
        await self._async_changed(entry_id)
        return {k: v for k, v in item.items() if k != "file"}

    async def async_delete(self, file_id: str) -> bool:
        for entry_id, items in self._data.items():
            for index, item in enumerate(items):
                if item["id"] == file_id:
                    del items[index]
                    path = self.root / entry_id / item["file"]
                    await self.hass.async_add_executor_job(lambda: path.unlink(missing_ok=True))
                    await self._async_changed(entry_id)
                    return True
        return False

    async def async_remove_entry(self, entry_id: str) -> None:
        self._data.pop(entry_id, None)
        await self._store.async_save({"files": self._data})
        folder = self.root / entry_id
        await self.hass.async_add_executor_job(lambda: shutil.rmtree(folder, ignore_errors=True))

    async def _async_changed(self, entry_id: str) -> None:
        await self._store.async_save({"files": self._data})
        async_dispatcher_send(self.hass, signal_files(entry_id))


def get_file_manager(hass: HomeAssistant) -> FileManager:
    return hass.data[DOMAIN][DATA_FILES]


async def async_setup_files(hass: HomeAssistant) -> FileManager:
    """Incarca metadatele si inregistreaza API-ul, o singura data."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if DATA_FILES in domain_data:
        return domain_data[DATA_FILES]

    manager = FileManager(hass)
    await manager.async_load()
    domain_data[DATA_FILES] = manager

    websocket_api.async_register_command(hass, ws_subscribe_files)
    websocket_api.async_register_command(hass, ws_delete_file)
    hass.http.register_view(VehicleFilesView(hass))
    return manager


def _known_entry(hass: HomeAssistant, entry_id: str) -> bool:
    return entry_id in hass.data.get(DOMAIN, {}).get("coordinators", {})


def admin_only(hass: HomeAssistant, entry_id: str) -> bool:
    """Optiunea vehiculului: dosarul il vad doar administratorii."""
    coordinator = hass.data.get(DOMAIN, {}).get("coordinators", {}).get(entry_id)
    return bool(coordinator and coordinator.option(CONF_FILES_ADMIN_ONLY))


class VehicleFilesView(HomeAssistantView):
    """POST: incarca un fisier pentru un act. GET: descarca un fisier."""

    url = "/api/vehicle_manager/files/{entry_id}/{key}"
    name = "api:vehicle_manager:files"
    requires_auth = True

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def post(self, request: web.Request, entry_id: str, key: str) -> web.Response:
        if not _known_entry(self.hass, entry_id):
            return self.json_message("Vehicul necunoscut", 404)
        if not valid_slot(key):
            return self.json_message("Act necunoscut", 400)
        if not request["hass_user"].is_admin:
            return self.json_message("Doar administratorii pot încărca documente.", 403)
        count, used = get_file_manager(self.hass).usage(entry_id)
        if count >= MAX_FILES_PER_VEHICLE:
            return self.json_message(f"Dosarul are deja {MAX_FILES_PER_VEHICLE} de fișiere.", 413)

        reader = await request.multipart()
        field = await reader.next()
        while field is not None and field.name != "file":
            field = await reader.next()
        if field is None:
            return self.json_message("Lipsește fișierul.", 400)

        content = bytearray()
        while chunk := await field.read_chunk():
            content.extend(chunk)
            if len(content) > MAX_BYTES:
                return self.json_message("Fișierul depășește 20 MB.", 413)

        if used + len(content) > MAX_TOTAL_BYTES:
            return self.json_message("Dosarul vehiculului depășește 200 MB.", 413)

        detected = detect_type(bytes(content[:16]))
        if detected is None:
            return self.json_message("Format neacceptat. Folosește o poză (JPG, PNG, WebP) sau PDF.", 415)

        item = await get_file_manager(self.hass).async_add(
            entry_id, key, field.filename or "document", bytes(content), *detected
        )
        return self.json(item)

    async def get(self, request: web.Request, entry_id: str, key: str) -> web.StreamResponse:
        if admin_only(self.hass, entry_id) and not request["hass_user"].is_admin:
            return self.json_message("Doar administratorii pot vedea dosarul.", 403)
        found = get_file_manager(self.hass).find(entry_id, key)
        if found is None:
            return self.json_message("Fișierul nu există", 404)
        item, path = found
        if not await self.hass.async_add_executor_job(path.is_file):
            return self.json_message("Fișierul lipsește de pe disc", 404)
        return web.FileResponse(
            path,
            headers={
                "Content-Type": item["mime"],
                # numele cu diacritice merge doar in forma filename* (RFC 6266)
                "Content-Disposition": (
                    f'inline; filename="{item["name"].encode("ascii", "replace").decode()}"; '
                    f"filename*=UTF-8''{quote(item['name'])}"
                ),
                "Cache-Control": "private, no-store",
                # browserul nu trebuie sa interpreteze niciodata un fisier ca pagina web
                "X-Content-Type-Options": "nosniff",
            },
        )


@websocket_api.websocket_command({vol.Required("type"): WS_SUBSCRIBE, vol.Required("entry_id"): str})
@callback
def ws_subscribe_files(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Lista fisierelor unui vehicul si apoi fiecare modificare."""
    entry_id = msg["entry_id"]
    if not _known_entry(hass, entry_id):
        connection.send_error(msg["id"], "not_found", "Vehicul necunoscut")
        return
    manager = get_file_manager(hass)
    is_admin = connection.user.is_admin

    @callback
    def forward() -> None:
        restricted = admin_only(hass, entry_id) and not is_admin
        connection.send_message(
            websocket_api.event_message(
                msg["id"],
                {
                    "files": [] if restricted else manager.files(entry_id),
                    "restricted": restricted,
                    "can_edit": is_admin,
                },
            )
        )

    connection.subscriptions[msg["id"]] = async_dispatcher_connect(
        hass, signal_files(entry_id), forward
    )
    connection.send_result(msg["id"])
    forward()


@websocket_api.websocket_command({vol.Required("type"): WS_DELETE, vol.Required("file_id"): str})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_delete_file(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Sterge un fisier din dosar."""
    if not await get_file_manager(hass).async_delete(msg["file_id"]):
        connection.send_error(msg["id"], "not_found", "Fișierul nu există")
        return
    connection.send_result(msg["id"])
