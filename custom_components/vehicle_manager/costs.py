"""Istoricul cheltuielilor per vehicul, salvat in .storage/vehicle_manager.expenses."""

from __future__ import annotations

from collections import defaultdict
import csv
from datetime import date
import io
import secrets
from typing import Any

from aiohttp import web
import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import CONF_MILEAGE, DOMAIN, EXPENSE_CATEGORIES, FUEL_CATEGORY

STORAGE_KEY = f"{DOMAIN}.expenses"
STORAGE_VERSION = 1

DATA_COSTS = "cost_manager"

WS_SUBSCRIBE = f"{DOMAIN}/expenses/subscribe"
WS_ADD = f"{DOMAIN}/expenses/add"
WS_DELETE = f"{DOMAIN}/expenses/delete"

NOTE_MAX = 200
AMOUNT_MAX = 10_000_000
QUANTITY_MAX = 1_000

# Campurile unei cheltuieli, comune serviciilor si comenzilor websocket.
EXPENSE_FIELDS = {
    vol.Required("category"): vol.In(list(EXPENSE_CATEGORIES)),
    vol.Required("amount"): vol.All(vol.Coerce(float), vol.Range(min=0, max=AMOUNT_MAX)),
    vol.Optional("date"): cv.date,
    vol.Optional("mileage"): vol.Any(None, vol.All(vol.Coerce(int), vol.Range(min=0))),
    vol.Optional("note"): vol.All(cv.string, vol.Length(max=NOTE_MAX)),
    # doar pentru combustibil: litri (sau kWh) si daca s-a facut plinul complet
    vol.Optional("quantity"): vol.Any(
        None, vol.All(vol.Coerce(float), vol.Range(min=0, max=QUANTITY_MAX))
    ),
    vol.Optional("full_tank"): cv.boolean,
}


def fuel_segments(expenses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Consumul pe intervale "plin la plin".

    Intre doua plinuri complete se aduna cantitatea (si costul) tuturor alimentarilor,
    inclusiv cele partiale, si se imparte la kilometrii parcursi. Primul plin complet
    doar fixeaza punctul de pornire; alimentarile fara kilometraj sunt ignorate.
    """
    fills = sorted(
        (
            e
            for e in expenses
            if e["category"] == FUEL_CATEGORY
            and e.get("quantity")
            and e.get("mileage") is not None
        ),
        key=lambda e: (e["mileage"], e["date"], e["id"]),
    )
    segments: list[dict[str, Any]] = []
    start_km: int | None = None
    quantity = cost = 0.0
    for fill in fills:
        if start_km is None:
            if fill.get("full_tank", True):
                start_km = fill["mileage"]
            continue
        quantity += fill["quantity"]
        cost += fill["amount"]
        if not fill.get("full_tank", True):
            continue
        km = fill["mileage"] - start_km
        if km > 0:
            segments.append(
                {
                    "id": fill["id"],
                    "date": fill["date"],
                    "km": km,
                    "quantity": round(quantity, 2),
                    "cost": round(cost, 2),
                    "consumption": round(quantity / km * 100, 2),
                }
            )
        start_km = fill["mileage"]
        quantity = cost = 0.0
    return segments


def fuel_summary(segments: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Consumul mediu si costul pe km pe toate intervalele masurate."""
    km = sum(s["km"] for s in segments)
    if not km:
        return None
    quantity = sum(s["quantity"] for s in segments)
    cost = sum(s["cost"] for s in segments)
    return {
        "consumption": round(quantity / km * 100, 2),
        "cost_per_km": round(cost / km, 3),
        "km": km,
        "quantity": round(quantity, 2),
        "last_consumption": segments[-1]["consumption"],
        "last_date": segments[-1]["date"],
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
        quantity: float | None = None,
        full_tank: bool = True,
    ) -> dict[str, Any]:
        item = {
            "id": secrets.token_hex(8),
            "date": (date_ or dt_util.now().date()).isoformat(),
            "category": category,
            "amount": round(float(amount), 2),
            "mileage": mileage,
            "note": (note or "").strip()[:NOTE_MAX],
        }
        if category == FUEL_CATEGORY and quantity:
            item["quantity"] = round(float(quantity), 2)
            item["full_tank"] = bool(full_tank)
        self._data.setdefault(entry_id, []).append(item)
        await self._async_changed(entry_id)
        return item

    def fuel(self, entry_id: str) -> dict[str, Any]:
        """Intervalele de consum si rezumatul lor, pentru card si senzori."""
        segments = fuel_segments(self._data.get(entry_id, []))
        return {"segments": segments, "summary": fuel_summary(segments)}

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


async def async_add_expense(
    hass: HomeAssistant, entry_id: str, fields: dict[str, Any]
) -> dict[str, Any]:
    """Adauga o cheltuiala si, daca are un kilometraj mai mare, actualizeaza vehiculul."""
    item = await get_cost_manager(hass).async_add(
        entry_id,
        category=fields["category"],
        amount=fields["amount"],
        date_=fields.get("date"),
        mileage=fields.get("mileage"),
        note=fields.get("note", ""),
        quantity=fields.get("quantity"),
        full_tank=fields.get("full_tank", True),
    )
    coordinator = hass.data[DOMAIN].get("coordinators", {}).get(entry_id)
    mileage = item["mileage"]
    if coordinator is not None and mileage is not None:
        current = coordinator.option(CONF_MILEAGE)
        if current is None or mileage > int(float(current)):
            await coordinator.async_set_options({CONF_MILEAGE: mileage})
    return item


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
    hass.http.register_view(ExpensesCsvView(hass))
    return manager


def _ro_number(value: float | int | None, decimals: int = 2) -> str:
    """Numar cu virgula zecimala, cum il asteapta Excel in romana."""
    if value is None:
        return ""
    return f"{value:.{decimals}f}".replace(".", ",")


def expenses_csv(
    expenses: list[dict[str, Any]], currency: str, period: str
) -> str:
    """CSV cu separator ';' (Excel in romana), cele mai vechi primele."""
    rows = [e for e in expenses if period == "all" or e["date"].startswith(f"{period}-")]
    rows.sort(key=lambda e: (e["date"], e["id"]))
    out = io.StringIO()
    writer = csv.writer(out, delimiter=";", lineterminator="\r\n")
    writer.writerow(
        ["Data", "Categorie", "Suma", "Moneda", "Kilometraj", "Cantitate", "Plin complet", "Nota"]
    )
    for e in rows:
        writer.writerow(
            [
                e["date"],
                EXPENSE_CATEGORIES.get(e["category"], (e["category"],))[0],
                _ro_number(e["amount"]),
                currency,
                e["mileage"] if e.get("mileage") is not None else "",
                _ro_number(e.get("quantity")),
                {True: "da", False: "nu"}.get(e.get("full_tank"), "") if e.get("quantity") else "",
                e.get("note", ""),
            ]
        )
    writer.writerow([])
    writer.writerow(["Total", "", _ro_number(sum(e["amount"] for e in rows)), currency])
    # BOM: Excel recunoaste astfel UTF-8 (diacriticele din note)
    return "\ufeff" + out.getvalue()


class ExpensesCsvView(HomeAssistantView):
    """Exportul cheltuielilor unui vehicul. Cardul il deschide printr-un link semnat."""

    url = "/api/vehicle_manager/expenses/{entry_id}/{period}"
    name = "api:vehicle_manager:expenses_csv"
    requires_auth = True

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def get(self, request: web.Request, entry_id: str, period: str) -> web.Response:
        if not _known_entry(self.hass, entry_id):
            return self.json_message("Vehicul necunoscut", 404)
        period = period.removesuffix(".csv")
        if period != "all" and not (len(period) == 4 and period.isdigit()):
            return self.json_message("Perioada invalida", 400)

        entry = self.hass.config_entries.async_get_entry(entry_id)
        name = (entry.title if entry else "vehicul").replace(" ", "_")
        body = expenses_csv(
            get_cost_manager(self.hass).expenses(entry_id),
            self.hass.config.currency,
            period,
        )
        suffix = "toate" if period == "all" else period
        return web.Response(
            body=body.encode("utf-8"),
            content_type="text/csv",
            charset="utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="cheltuieli_{name}_{suffix}.csv"'
            },
        )


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
                    "fuel": manager.fuel(entry_id),
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
    item = await async_add_expense(hass, msg["entry_id"], msg)
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
        connection.send_error(msg["id"], "not_found", "Cheltuiala nu există")
        return
    connection.send_result(msg["id"])
