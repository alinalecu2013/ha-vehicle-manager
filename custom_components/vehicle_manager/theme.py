"""Tema cardului Vehicle Manager, salvata pe server si comuna tuturor dispozitivelor."""

from __future__ import annotations

import secrets
from pathlib import Path
from typing import Any

import voluptuous as vol
from aiohttp import web

from homeassistant.components import websocket_api
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
from homeassistant.helpers.storage import Store

from .const import DOMAIN, MEDIA_DIRNAME

STORAGE_KEY = f"{DOMAIN}.theme"
STORAGE_VERSION = 1

DATA_THEME = "theme_manager"
SIGNAL_THEME_UPDATED = f"{DOMAIN}_theme_updated"

WS_SUBSCRIBE = f"{DOMAIN}/theme/subscribe"
WS_SAVE = f"{DOMAIN}/theme/save"

HEX_COLOR = vol.Match(r"^#[0-9a-fA-F]{6}$")

# Imaginea de fundal: cale locala (/local/...) sau http(s). Fara ghilimele,
# paranteze sau spatii, ca valoarea sa poata fi pusa sigur in CSS url("...").
BG_URL_RE = r"^(https?://|/)[^\s\"'()<>\\]+$"
BG_UPLOAD_URL = f"/api/{DOMAIN}/theme/background"
BG_FILE_PREFIX = "theme-bg-"
BG_MAX_BYTES = 15 * 1024 * 1024

# Semnaturile acceptate, verificate pe continut, nu pe extensie.
IMAGE_SIGNATURES: tuple[tuple[bytes, int, str], ...] = (
    (b"\xff\xd8\xff", 0, ".jpg"),
    (b"\x89PNG\r\n\x1a\n", 0, ".png"),
    (b"GIF8", 0, ".gif"),
    (b"WEBP", 8, ".webp"),
)

COLOR_KEYS = (
    "accent",
    "accent2",
    "bg",
    "panel",
    "text",
    "dim",
    "line",
    "ok",
    "warn",
    "bad",
)

FONT_FAMILIES = ("default", "ha", "system", "mono", "serif", "rounded")


def _number(minimum: float, maximum: float) -> vol.All:
    return vol.All(vol.Coerce(float), vol.Range(min=minimum, max=maximum))


THEME_SCHEMA = vol.Schema(
    {
        vol.Optional("preset"): vol.All(str, vol.Length(max=32)),
        vol.Optional("follow_ha"): bool,
        **{vol.Optional(key): HEX_COLOR for key in COLOR_KEYS},
        vol.Optional("font_family"): vol.In(FONT_FAMILIES),
        vol.Optional("font_scale"): _number(0.75, 1.6),
        vol.Optional("spacing"): _number(0.6, 1.6),
        vol.Optional("radius"): _number(0, 2),
        vol.Optional("panel_opacity"): _number(0.1, 1),
        vol.Optional("blur"): _number(0, 24),
        vol.Optional("glow"): _number(0, 2),
        vol.Optional("grid"): bool,
        vol.Optional("stage_height"): _number(180, 640),
        vol.Optional("bg_image"): vol.Any(
            "", vol.All(str, vol.Length(max=512), vol.Match(BG_URL_RE))
        ),
        vol.Optional("bg_target"): vol.In(("card", "stage")),
        vol.Optional("bg_fit"): vol.In(("cover", "contain", "tile")),
        vol.Optional("bg_position"): vol.In(("center", "top", "bottom")),
        vol.Optional("bg_overlay"): _number(0, 0.95),
        vol.Optional("bg_blur"): _number(0, 20),
        # limba cardurilor: "auto" = limba din Home Assistant
        vol.Optional("language"): vol.In(("auto", "ro", "en")),
    },
    extra=vol.REMOVE_EXTRA,
)


class ThemeManager:
    """Pastreaza tema in .storage si anunta cardurile deschise la fiecare schimbare."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self.theme: dict[str, Any] | None = None

    async def async_load(self) -> None:
        data = await self._store.async_load()
        self.theme = (data or {}).get("theme")

    async def async_save(self, theme: dict[str, Any] | None) -> None:
        self.theme = theme
        await self._store.async_save({"theme": theme})
        async_dispatcher_send(self.hass, SIGNAL_THEME_UPDATED, theme)
        await self.hass.async_add_executor_job(self._cleanup_backgrounds)

    def _cleanup_backgrounds(self) -> None:
        """Sterge imaginile de fundal incarcate care nu mai sunt folosite."""
        keep = Path(str((self.theme or {}).get("bg_image") or "")).name
        media_dir = Path(self.hass.config.path("www", MEDIA_DIRNAME))
        if not media_dir.is_dir():
            return
        for item in media_dir.glob(f"{BG_FILE_PREFIX}*"):
            if item.name != keep:
                item.unlink(missing_ok=True)


def _image_extension(head: bytes) -> str | None:
    for signature, offset, extension in IMAGE_SIGNATURES:
        if head[offset : offset + len(signature)] == signature:
            return extension
    return None


class ThemeBackgroundView(HomeAssistantView):
    """Primeste imaginea de fundal din card si o salveaza in config/www."""

    url = BG_UPLOAD_URL
    name = f"api:{DOMAIN}:theme_background"
    requires_auth = True

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def post(self, request: web.Request) -> web.Response:
        reader = await request.multipart()
        field = await reader.next()
        while field is not None and field.name != "file":
            field = await reader.next()
        if field is None:
            return self.json_message("Lipseste fisierul.", 400)

        data = bytearray()
        while chunk := await field.read_chunk():
            data.extend(chunk)
            if len(data) > BG_MAX_BYTES:
                return self.json_message("Imaginea depaseste 15 MB.", 413)

        extension = _image_extension(bytes(data[:16]))
        if extension is None:
            return self.json_message(
                "Format neacceptat. Foloseste JPG, PNG, WebP sau GIF.", 415
            )

        filename = f"{BG_FILE_PREFIX}{secrets.token_hex(6)}{extension}"
        target = Path(self.hass.config.path("www", MEDIA_DIRNAME)) / filename

        def _write() -> None:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)

        await self.hass.async_add_executor_job(_write)
        return self.json({"url": f"/local/{MEDIA_DIRNAME}/{filename}"})


async def async_setup_theme(hass: HomeAssistant) -> None:
    """Incarca tema si inregistreaza comenzile websocket, o singura data."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if DATA_THEME in domain_data:
        return

    manager = ThemeManager(hass)
    await manager.async_load()
    domain_data[DATA_THEME] = manager

    websocket_api.async_register_command(hass, ws_subscribe_theme)
    websocket_api.async_register_command(hass, ws_save_theme)
    hass.http.register_view(ThemeBackgroundView(hass))


@websocket_api.websocket_command({vol.Required("type"): WS_SUBSCRIBE})
@callback
def ws_subscribe_theme(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Trimite tema curenta si apoi fiecare modificare."""
    manager: ThemeManager = hass.data[DOMAIN][DATA_THEME]

    @callback
    def forward(theme: dict[str, Any] | None) -> None:
        connection.send_message(
            websocket_api.event_message(msg["id"], {"theme": theme})
        )

    connection.subscriptions[msg["id"]] = async_dispatcher_connect(
        hass, SIGNAL_THEME_UPDATED, forward
    )
    connection.send_result(msg["id"])
    forward(manager.theme)


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_SAVE,
        # None = revenire la tema implicita a cardului
        vol.Required("theme"): vol.Any(None, THEME_SCHEMA),
    }
)
@websocket_api.async_response
async def ws_save_theme(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Salveaza tema pentru toate dispozitivele."""
    manager: ThemeManager = hass.data[DOMAIN][DATA_THEME]
    await manager.async_save(msg["theme"])
    connection.send_result(msg["id"], {"theme": manager.theme})
