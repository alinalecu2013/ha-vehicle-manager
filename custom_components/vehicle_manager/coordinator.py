"""Coordinator: sursa unica de date pentru un vehicul."""

from __future__ import annotations

import logging
import re
import unicodedata
from datetime import date, datetime
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import (
    COLOR_HEX,
    CONF_COLOR,
    CONF_ENGINE_CAPACITY,
    CONF_FUEL_TYPE,
    CONF_MAKE,
    CONF_MILEAGE,
    CONF_MILEAGE_SOURCE,
    CONF_PARKING,
    CONF_MODEL,
    CONF_MODEL_3D,
    CONF_PHOTO,
    CONF_PLATE,
    CONF_VIN,
    CONF_WARN_DAYS,
    CONF_WARN_KM,
    CONF_YEAR,
    DEFAULT_COLOR_HEX,
    DEFAULT_WARN_DAYS,
    DEFAULT_WARN_KM,
    DOCUMENTS,
    DOMAIN,
    FUEL_ICONS,
    FUEL_LABELS,
    STATUS_EXPIRED,
    STATUS_OK,
    STATUS_ORDER,
    STATUS_UNKNOWN,
    STATUS_WARNING,
    UPDATE_INTERVAL,
    date_key,
    km_key,
)

_LOGGER = logging.getLogger(__name__)


def _strip_diacritics(value: str) -> str:
    """Normalizeaza diacriticele, de exemplu Rosu cu diacritice -> rosu."""
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower().strip()


def color_to_hex(raw: Any) -> str:
    """Converteste un nume de culoare (sau un hex) in hex pentru modelul 3D."""
    if not raw:
        return DEFAULT_COLOR_HEX
    text = str(raw).strip()
    # doar hex valid: valoarea ajunge in stilul cardului
    if re.fullmatch(r"#(?:[0-9a-fA-F]{3}){1,2}", text):
        return text
    key = _strip_diacritics(text)
    if key in COLOR_HEX:
        return COLOR_HEX[key]

    # Potrivire pe cuvinte intregi, de la cel mai lung nume spre cel mai scurt,
    # ca "albastru metalizat" sa nu fie confundat cu "alb".
    names = sorted(COLOR_HEX, key=len, reverse=True)
    words = set(re.split(r"[^a-z0-9]+", key))
    for name in names:
        if name in words:
            return COLOR_HEX[name]
    for name in names:
        if name in key:
            return COLOR_HEX[name]
    return DEFAULT_COLOR_HEX


def as_date(raw: Any) -> date | None:
    """Parseaza o valoare din options in date."""
    if not raw:
        return None
    if isinstance(raw, datetime):
        return raw.date()
    if isinstance(raw, date):
        return raw
    return dt_util.parse_date(str(raw))


def as_int(raw: Any) -> int | None:
    """Parseaza o valoare din options in int."""
    if raw is None or raw == "":
        return None
    try:
        return int(float(raw))
    except (TypeError, ValueError):
        return None


class VehicleCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Calculeaza si distribuie starea unui vehicul.

    Sursa de adevar este entry.options; orice scriere trece prin
    async_set_options, care persista in config entry si recalculeaza.
    """

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initializeaza coordinatorul."""
        self.entry = entry
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=UPDATE_INTERVAL,
        )

    # ------------------------------------------------------------------
    # Acces la configuratie
    # ------------------------------------------------------------------
    @property
    def options(self) -> dict[str, Any]:
        """Configuratia curenta a vehiculului."""
        return dict(self.entry.options or self.entry.data)

    def option(self, key: str, default: Any = None) -> Any:
        """Citeste o singura valoare de configurare."""
        value = self.options.get(key, default)
        return default if value in (None, "") else value

    @property
    def vehicle_name(self) -> str:
        """Numele vehiculului."""
        return self.entry.title

    async def async_set_options(self, changes: dict[str, Any]) -> None:
        """Persista modificari in config entry si recalculeaza starea."""
        new_options = self.options
        for key, value in changes.items():
            if isinstance(value, datetime):
                value = value.date().isoformat()
            elif isinstance(value, date):
                value = value.isoformat()
            new_options[key] = value
        self.hass.config_entries.async_update_entry(self.entry, options=new_options)
        self.async_set_updated_data(self._build())

    # ------------------------------------------------------------------
    # Calcul stare
    # ------------------------------------------------------------------
    async def _async_update_data(self) -> dict[str, Any]:
        """Recalculeaza starea derivata din configuratie."""
        return self._build()

    def _build(self) -> dict[str, Any]:
        """Construieste dict-ul de stare complet pentru vehicul."""
        opts = self.options
        today = dt_util.now().date()

        warn_days = as_int(opts.get(CONF_WARN_DAYS))
        if warn_days is None:
            warn_days = DEFAULT_WARN_DAYS
        warn_km = as_int(opts.get(CONF_WARN_KM))
        if warn_km is None:
            warn_km = DEFAULT_WARN_KM
        mileage = as_int(opts.get(CONF_MILEAGE)) or 0

        documents: dict[str, Any] = {}
        attention: list[str] = []
        overall = STATUS_UNKNOWN

        for doc, meta in DOCUMENTS.items():
            due_date = as_date(opts.get(date_key(doc)))
            due_km = as_int(opts.get(km_key(doc))) if meta["uses_km"] else None

            days = (due_date - today).days if due_date else None
            km_remaining = (due_km - mileage) if due_km is not None else None

            status = STATUS_UNKNOWN
            if days is not None or km_remaining is not None:
                status = STATUS_OK
                if (days is not None and days < 0) or (
                    km_remaining is not None and km_remaining < 0
                ):
                    status = STATUS_EXPIRED
                elif (days is not None and days <= warn_days) or (
                    km_remaining is not None and km_remaining <= warn_km
                ):
                    status = STATUS_WARNING

            documents[doc] = {
                "key": doc,
                "label": meta["label"],
                "icon": meta["icon"],
                "uses_km": meta["uses_km"],
                "horizon": meta["horizon"],
                "date": due_date.isoformat() if due_date else None,
                "days": days,
                "due_km": due_km,
                "km_remaining": km_remaining,
                "status": status,
            }

            if status in (STATUS_WARNING, STATUS_EXPIRED):
                attention.append(meta["label"])
            if STATUS_ORDER[status] > STATUS_ORDER[overall]:
                overall = status

        fuel = opts.get(CONF_FUEL_TYPE) or "altul"

        vehicle = {
            "name": self.vehicle_name,
            CONF_MAKE: opts.get(CONF_MAKE),
            CONF_MODEL: opts.get(CONF_MODEL),
            CONF_YEAR: as_int(opts.get(CONF_YEAR)),
            CONF_COLOR: opts.get(CONF_COLOR),
            "color_hex": color_to_hex(opts.get(CONF_COLOR)),
            CONF_ENGINE_CAPACITY: as_int(opts.get(CONF_ENGINE_CAPACITY)),
            CONF_FUEL_TYPE: fuel,
            "fuel_label": FUEL_LABELS.get(fuel, fuel),
            "fuel_icon": FUEL_ICONS.get(fuel, "mdi:gas-station"),
            CONF_PLATE: opts.get(CONF_PLATE),
            CONF_VIN: opts.get(CONF_VIN),
            CONF_MILEAGE: mileage,
            # kilometrajul vine automat dintr-un senzor (vezi mileage.py)
            "mileage_auto": bool(opts.get(CONF_MILEAGE_SOURCE)),
            "parking": opts.get(CONF_PARKING),
        }

        return {
            "name": self.vehicle_name,
            "entry_id": self.entry.entry_id,
            "vehicle": vehicle,
            "photo": opts.get(CONF_PHOTO) or None,
            "model_3d": opts.get(CONF_MODEL_3D) or None,
            "documents": documents,
            "status": overall,
            "attention": attention,
            "warn_days": warn_days,
            "warn_km": warn_km,
            "updated": dt_util.now().isoformat(timespec="seconds"),
        }

    def handle_entry_update(self) -> None:
        """Recalculeaza sincron cand config entry-ul s-a schimbat."""
        self.async_set_updated_data(self._build())
