"""Istoricul cheltuielilor per vehicul, salvat in .storage/vehicle_manager.expenses."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
import secrets
from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import DOMAIN, EXPENSE_CATEGORIES

STORAGE_KEY = f"{DOMAIN}.expenses"
STORAGE_VERSION = 1

DATA_COSTS = "cost_manager"

WS_SUBSCRIBE = f"{DOMAIN}/expenses/subscribe"
WS_ADD = f"{DOMAIN}/expenses/add"
WS_DELETE = f"{DOMAIN}/expenses/delete"

NOTE_MAX = 200
AMOUNT_MAX = 10_000_000

# Campurile unei cheltuieli, comune serviciilor si comenzilor websocket.
EXPENSE_FIELDS = {
    vol.Required("category"): vol.In(list(EXPENSE_CATEGORIES)),
    vol.Required("amount"): vol.All(vol.Coerce(float), vol.Range(min=0, max=AMOUNT_MAX)),
    vol.Optional("date"): cv.date,
    vol.Optional("mileage"): vol.Any(None, vol.All(vol.Coerce(int), vol.Range(min=0))),
    vol.Optional("note"): vol.All(cv.string, vol.Length(max=NOTE_MAX)),
}


def signal_expenses(entry_id: str) -> str:
    """Semnalul trimis cand se schimba cheltuielile unui vehicul."""
    return f"{DOMAIN}_expenses_{entry_id}"


class CostManager:
    """Pastreaza cheltuielile tuturor vehiculelor si anunta modificarile."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: dict[str, list[dict[str, Any]]] = {}

    async def async_load(self) -> None:
        stored = await self._store.async_load()
        self._data = (stored or {}).get("expenses", {})

    def expenses(self, entry_id: str) -> list[dict[str, Any]]:
        """Cheltuielile unui vehicul, cele mai noi primele."""
        return sorted(
            self._data.get(entry_id, []),
            key=lambda item: (item["date"], item["id"]),
            reverse=True,
        )

    def summary(self, entry_id: str, year: int | None = None) -> dict[str, Any]:
        """Totaluri pentru senzori: pe tot istoricul si pe anul dat (implicit cel curent)."""
        year = year or dt_util.now().year
        prefix = f"{year:04d}-"
        total = 0.0
        year_total = 0.0
        by_category: dict[str, float] = defaultdict(float)
        count = 0
        for item in self._data.get(entry_id, []):
            total += item["amount"]
            if item["date"].startswith(prefix):
                year_total += item["amount"]
                by_category[item["category"]] += item["amount"]
                count += 1
        return {
            "total": round(total, 2),
            "year": year,
            "year_total": round(year_total, 2),
            "year_count": count,
            "year_by_category": {
                key: round(by_category[key], 2)
                for key in EXPENSE_CATEGORIES
                if by_category.get(key)
            },
        }

    async def async_add(
        self,
        entry_id: str,
        *,
        category: str,
        amount: float,
        date_: date | None = None,
        mileage: int | None = None,
        note: str = "",
    ) -> dict[str, Any]:
        item = {
            "id": secrets.token_hex(8),
            "date": (date_ or dt_util.now().date()).isoformat(),
            "category": category,
            "amount": round(float(amount), 2),
            "mileage": mileage,
            "note": (note or "").strip()[:NOTE_MAX],
        }
        self._data.setdefault(entry_id, []).append(item)
        await self._async_changed(entry_id)
        return item

    async def async_delete(self, expense_id: str) -> bool:
        for entry_id, items in self._data.items():
            for index, item in enumerate(items):
                if item["id"] == expense_id:
                    del items[index]
                    await self._async_changed(entry_id)
                    return True
        return False

    async def async_remove_entry(self, entry_id: str) -> None:
        if self._data.pop(entry_id, None) is not None:
            await self._store.async_save({"expenses": self._data})

    async def _async_changed(self, entry_id: str) -> None:
        await self._store.async_save({"expenses": self._data})
        async_dispatcher_send(self.hass, signal_expenses(entry_id))


def get_cost_manager(hass: HomeAssistant) -> CostManager:
    return hass.data[DOMAIN][DATA_COSTS]


async def async_setup_costs(hass: HomeAssistant) -> CostManager:
    """Incarca cheltuielile si inregistreaza comenzile websocket, o singura data."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if DATA_COSTS in domain_data:
        return domain_data[DATA_COSTS]

    manager = CostManager(hass)
    await manager.async_load()
    domain_data[DATA_COSTS] = manager

    websocket_api.async_register_command(hass, ws_subscribe_expenses)
    websocket_api.async_register_command(hass, ws_add_expense)
    websocket_api.async_register_command(hass, ws_delete_expense)
    return manager


def _known_entry(hass: HomeAssistant, entry_id: str) -> bool:
    return entry_id in hass.data.get(DOMAIN, {}).get("coordinators", {})


@websocket_api.websocket_command(
    {vol.Required("type"): WS_SUBSCRIBE, vol.Required("entry_id"): str}
)
@callback
def ws_subscribe_expenses(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Trimite lista cheltuielilor unui vehicul si apoi fiecare modificare."""
    entry_id = msg["entry_id"]
    if not _known_entry(hass, entry_id):
        connection.send_error(msg["id"], "not_found", "Vehicul necunoscut")
        return
    manager = get_cost_manager(hass)

    @callback
    def forward() -> None:
        connection.send_message(
            websocket_api.event_message(
                msg["id"],
                {
                    "expenses": manager.expenses(entry_id),
                    "currency": hass.config.currency,
                },
            )
        )

    connection.subscriptions[msg["id"]] = async_dispatcher_connect(
        hass, signal_expenses(entry_id), forward
    )
    connection.send_result(msg["id"])
    forward()


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_ADD,
        vol.Required("entry_id"): str,
        **EXPENSE_FIELDS,
    }
)
@websocket_api.async_response
async def ws_add_expense(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Adauga o cheltuiala din card."""
    if not _known_entry(hass, msg["entry_id"]):
        connection.send_error(msg["id"], "not_found", "Vehicul necunoscut")
        return
    item = await get_cost_manager(hass).async_add(
        msg["entry_id"],
        category=msg["category"],
        amount=msg["amount"],
        date_=msg.get("date"),
        mileage=msg.get("mileage"),
        note=msg.get("note", ""),
    )
    connection.send_result(msg["id"], item)


@websocket_api.websocket_command(
    {vol.Required("type"): WS_DELETE, vol.Required("expense_id"): str}
)
@websocket_api.async_response
async def ws_delete_expense(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Sterge o cheltuiala din card."""
    if not await get_cost_manager(hass).async_delete(msg["expense_id"]):
        connection.send_error(msg["id"], "not_found", "Cheltuiala nu exista")
        return
    connection.send_result(msg["id"])
