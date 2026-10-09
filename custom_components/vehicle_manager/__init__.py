"""Integrarea Vehicle Manager: evidenta actelor si caracteristicilor auto."""

from __future__ import annotations

import calendar
import logging
import os
from datetime import date
from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_AREA_ID, ATTR_DEVICE_ID, ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_AMOUNT,
    ATTR_CATEGORY,
    ATTR_COST,
    ATTR_DATE,
    ATTR_DOCUMENT,
    ATTR_EXPENSE_ID,
    ATTR_INTERVAL_KM,
    ATTR_INTERVAL_MONTHS,
    ATTR_KM,
    ATTR_MILEAGE,
    ATTR_MONTHS,
    ATTR_NOTE,
    CARD_FILENAME,
    HACS_CARD_REPO,
    CONF_MEDIA_ID,
    CONF_MILEAGE,
    DOC_REVIZIE,
    DOCUMENTS,
    DOMAIN,
    MEDIA_DIRNAME,
    PLATFORMS,
    SERVICE_ADD_EXPENSE,
    SERVICE_DELETE_EXPENSE,
    SERVICE_MARK_SERVICE_DONE,
    SERVICE_RENEW_DOCUMENT,
    SERVICE_SET_DOCUMENT,
    SERVICE_SET_MILEAGE,
    URL_BASE,
    VERSION,
    date_key,
    km_key,
)
from .coordinator import VehicleCoordinator, as_date, as_int
from .costs import EXPENSE_FIELDS, async_setup_costs, get_cost_manager
from .theme import async_setup_theme

_LOGGER = logging.getLogger(__name__)

DATA_COORDINATORS = "coordinators"
DATA_FRONTEND = "frontend_registered"
DATA_SERVICES = "services_registered"


def add_months(start: date, months: int) -> date:
    """Adauga un numar de luni la o data, fara dependente externe."""
    total = start.month - 1 + months
    year = start.year + total // 12
    month = total % 12 + 1
    day = min(start.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


# ----------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configureaza un vehicul."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    domain_data.setdefault(DATA_COORDINATORS, {})

    # Migrare: sursa de adevar este entry.options.
    if not entry.options:
        hass.config_entries.async_update_entry(entry, options=dict(entry.data))

    await _async_ensure_media_dir(hass)
    await async_setup_theme(hass)
    await async_setup_costs(hass)
    await _async_register_frontend(hass)

    coordinator = VehicleCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    domain_data[DATA_COORDINATORS][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_entry_updated))

    _async_register_services(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Descarca un vehicul."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN][DATA_COORDINATORS].pop(entry.entry_id, None)
    return unloaded


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Sterge fisierele media si istoricul cheltuielilor vehiculului eliminat."""
    costs = await async_setup_costs(hass)
    await costs.async_remove_entry(entry.entry_id)

    media_dir = Path(hass.config.path("www", MEDIA_DIRNAME))
    options = entry.options or entry.data
    media_id = options.get(CONF_MEDIA_ID) or entry.entry_id[:12]

    def _cleanup() -> None:
        if not media_dir.is_dir():
            return
        for item in media_dir.glob(f"{media_id}*"):
            try:
                item.unlink()
            except OSError as err:  # pragma: no cover - depinde de FS
                _LOGGER.warning("Nu am putut sterge %s: %s", item, err)

    await hass.async_add_executor_job(_cleanup)


async def _async_entry_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Recalculeaza starea dupa salvarea opțiunilor, fara reload."""
    coordinator: VehicleCoordinator | None = (
        hass.data.get(DOMAIN, {}).get(DATA_COORDINATORS, {}).get(entry.entry_id)
    )
    if coordinator is None:
        return
    # Titlul poate fi schimbat din options flow; entitatile il citesc din entry.
    coordinator.handle_entry_update()


async def _async_ensure_media_dir(hass: HomeAssistant) -> None:
    """Creeaza config/www/vehicle_manager pentru poze si modele 3D."""
    target = hass.config.path("www", MEDIA_DIRNAME)
    await hass.async_add_executor_job(lambda: os.makedirs(target, exist_ok=True))


async def _async_register_frontend(hass: HomeAssistant) -> None:
    """Serveste si inregistreaza automat cardul Lovelace."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get(DATA_FRONTEND):
        return

    www_dir = str(Path(__file__).parent / "www")
    try:
        from homeassistant.components.http import StaticPathConfig

        await hass.http.async_register_static_paths(
            [StaticPathConfig(URL_BASE, www_dir, False)]
        )
    except ImportError:  # HA < 2024.7
        hass.http.register_static_path(URL_BASE, www_dir, False)

    # Daca cardul e instalat separat din HACS (categoria Dashboard), HACS il
    # incarca drept resursa Lovelace; copia inclusa aici nu se mai incarca,
    # altfel ar castiga mereu ea (se incarca prima) si ar ignora versiunea HACS.
    hacs_card = Path(hass.config.path("www", "community", HACS_CARD_REPO))
    if await hass.async_add_executor_job(hacs_card.is_dir):
        _LOGGER.info(
            "Cardul este instalat din HACS (%s); copia inclusa in integrare nu se incarca",
            hacs_card,
        )
        domain_data[DATA_FRONTEND] = True
        return

    try:
        from homeassistant.components.frontend import add_extra_js_url

        # Versiunea din URL urmareste fisierul, ca WebView-ul din aplicatia
        # mobila sa nu pastreze in cache o varianta veche a cardului.
        card_path = Path(www_dir) / CARD_FILENAME
        mtime = await hass.async_add_executor_job(lambda: int(card_path.stat().st_mtime))
        add_extra_js_url(hass, f"{URL_BASE}/{CARD_FILENAME}?v={VERSION}-{mtime}")
    except Exception as err:  # pragma: no cover - depinde de versiunea HA
        _LOGGER.warning(
            "Nu am putut inregistra automat cardul; adauga-l manual ca resursa "
            "Lovelace de tip module la %s/%s (%s)",
            URL_BASE,
            CARD_FILENAME,
            err,
        )

    domain_data[DATA_FRONTEND] = True


# ----------------------------------------------------------------------
# Servicii
# ----------------------------------------------------------------------
TARGET_SCHEMA = dict(cv.TARGET_SERVICE_FIELDS)

SET_MILEAGE_SCHEMA = vol.Schema(
    {
        **TARGET_SCHEMA,
        vol.Required(ATTR_MILEAGE): vol.All(vol.Coerce(int), vol.Range(min=0)),
    }
)

SET_DOCUMENT_SCHEMA = vol.Schema(
    {
        **TARGET_SCHEMA,
        vol.Required(ATTR_DOCUMENT): vol.In(list(DOCUMENTS)),
        vol.Optional(ATTR_DATE): cv.date,
        vol.Optional(ATTR_KM): vol.All(vol.Coerce(int), vol.Range(min=0)),
    }
)

RENEW_DOCUMENT_SCHEMA = vol.Schema(
    {
        **TARGET_SCHEMA,
        vol.Required(ATTR_DOCUMENT): vol.In(list(DOCUMENTS)),
        vol.Optional(ATTR_MONTHS, default=12): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=120)
        ),
        vol.Optional(ATTR_INTERVAL_KM): vol.All(vol.Coerce(int), vol.Range(min=0)),
        vol.Optional(ATTR_COST): vol.All(vol.Coerce(float), vol.Range(min=0)),
    }
)

MARK_SERVICE_DONE_SCHEMA = vol.Schema(
    {
        **TARGET_SCHEMA,
        vol.Optional(ATTR_DOCUMENT, default=DOC_REVIZIE): vol.In(list(DOCUMENTS)),
        vol.Optional(ATTR_MILEAGE): vol.All(vol.Coerce(int), vol.Range(min=0)),
        vol.Optional(ATTR_INTERVAL_MONTHS, default=12): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=120)
        ),
        vol.Optional(ATTR_INTERVAL_KM, default=15000): vol.All(
            vol.Coerce(int), vol.Range(min=0)
        ),
        vol.Optional(ATTR_COST): vol.All(vol.Coerce(float), vol.Range(min=0)),
    }
)

ADD_EXPENSE_SCHEMA = vol.Schema({**TARGET_SCHEMA, **EXPENSE_FIELDS})

DELETE_EXPENSE_SCHEMA = vol.Schema({vol.Required(ATTR_EXPENSE_ID): cv.string})


def _resolve_coordinators(
    hass: HomeAssistant, call: ServiceCall
) -> list[VehicleCoordinator]:
    """Gaseste coordinatorii vizati de un apel de serviciu."""
    coordinators: dict[str, VehicleCoordinator] = hass.data[DOMAIN][DATA_COORDINATORS]
    entry_ids: set[str] = set()

    device_reg = dr.async_get(hass)
    entity_reg = er.async_get(hass)

    def add_device(device_id: str) -> None:
        device = device_reg.async_get(device_id)
        if device is not None:
            entry_ids.update(device.config_entries & coordinators.keys())

    def add_entity(entity_id: str) -> None:
        registry_entry = entity_reg.async_get(entity_id)
        if registry_entry is None:
            return
        if registry_entry.config_entry_id in coordinators:
            entry_ids.add(registry_entry.config_entry_id)
        elif registry_entry.device_id:
            add_device(registry_entry.device_id)

    for device_id in cv.ensure_list(call.data.get(ATTR_DEVICE_ID) or []):
        add_device(device_id)

    for entity_id in cv.ensure_list(call.data.get(ATTR_ENTITY_ID) or []):
        add_entity(entity_id)

    for area_id in cv.ensure_list(call.data.get(ATTR_AREA_ID) or []):
        for device in dr.async_entries_for_area(device_reg, area_id):
            entry_ids.update(device.config_entries & coordinators.keys())
        for registry_entry in er.async_entries_for_area(entity_reg, area_id):
            if registry_entry.config_entry_id in coordinators:
                entry_ids.add(registry_entry.config_entry_id)

    if not entry_ids:
        raise ServiceValidationError(
            "Nu am gasit niciun vehicul Vehicle Manager pentru tinta aleasa."
        )

    return [coordinators[entry_id] for entry_id in entry_ids]


def _async_register_services(hass: HomeAssistant) -> None:
    """Inregistreaza serviciile integrarii o singura data."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    if domain_data.get(DATA_SERVICES):
        return

    async def _set_mileage(call: ServiceCall) -> None:
        for coordinator in _resolve_coordinators(hass, call):
            await coordinator.async_set_options(
                {CONF_MILEAGE: call.data[ATTR_MILEAGE]}
            )

    async def _set_document(call: ServiceCall) -> None:
        doc = call.data[ATTR_DOCUMENT]
        changes: dict[str, Any] = {}
        if ATTR_DATE in call.data:
            changes[date_key(doc)] = call.data[ATTR_DATE]
        if ATTR_KM in call.data:
            if not DOCUMENTS[doc]["uses_km"]:
                raise ServiceValidationError(
                    f"Documentul {DOCUMENTS[doc]['label']} nu foloseste kilometraj."
                )
            changes[km_key(doc)] = call.data[ATTR_KM]
        if not changes:
            raise ServiceValidationError("Specifica cel putin data sau kilometrajul.")
        for coordinator in _resolve_coordinators(hass, call):
            await coordinator.async_set_options(changes)

    async def _renew_document(call: ServiceCall) -> None:
        doc = call.data[ATTR_DOCUMENT]
        months = call.data[ATTR_MONTHS]
        interval_km = call.data.get(ATTR_INTERVAL_KM)
        today = dt_util.now().date()

        for coordinator in _resolve_coordinators(hass, call):
            opts = coordinator.options
            current = as_date(opts.get(date_key(doc)))
            base = current if current and current > today else today
            changes: dict[str, Any] = {date_key(doc): add_months(base, months)}
            if interval_km is not None and DOCUMENTS[doc]["uses_km"]:
                mileage = as_int(opts.get(CONF_MILEAGE)) or 0
                changes[km_key(doc)] = mileage + interval_km
            await coordinator.async_set_options(changes)
            await _record_cost(coordinator, doc, call.data.get(ATTR_COST))

    async def _mark_service_done(call: ServiceCall) -> None:
        doc = call.data[ATTR_DOCUMENT]
        today = dt_util.now().date()

        for coordinator in _resolve_coordinators(hass, call):
            mileage = call.data.get(ATTR_MILEAGE)
            if mileage is None:
                mileage = as_int(coordinator.options.get(CONF_MILEAGE)) or 0
            changes: dict[str, Any] = {
                CONF_MILEAGE: mileage,
                date_key(doc): add_months(today, call.data[ATTR_INTERVAL_MONTHS]),
            }
            if DOCUMENTS[doc]["uses_km"]:
                changes[km_key(doc)] = mileage + call.data[ATTR_INTERVAL_KM]
            await coordinator.async_set_options(changes)
            await _record_cost(coordinator, doc, call.data.get(ATTR_COST), mileage)

    async def _record_cost(
        coordinator: VehicleCoordinator,
        doc: str,
        cost: float | None,
        mileage: int | None = None,
    ) -> None:
        """Inregistreaza costul reinnoirii, daca a fost dat (categoria = actul)."""
        if cost is None:
            return
        if mileage is None:
            mileage = as_int(coordinator.options.get(CONF_MILEAGE))
        await get_cost_manager(hass).async_add(
            coordinator.entry.entry_id, category=doc, amount=cost, mileage=mileage
        )

    async def _add_expense(call: ServiceCall) -> None:
        for coordinator in _resolve_coordinators(hass, call):
            await get_cost_manager(hass).async_add(
                coordinator.entry.entry_id,
                category=call.data[ATTR_CATEGORY],
                amount=call.data[ATTR_AMOUNT],
                date_=call.data.get(ATTR_DATE),
                mileage=call.data.get(ATTR_MILEAGE),
                note=call.data.get(ATTR_NOTE, ""),
            )

    async def _delete_expense(call: ServiceCall) -> None:
        if not await get_cost_manager(hass).async_delete(call.data[ATTR_EXPENSE_ID]):
            raise ServiceValidationError("Cheltuiala cu acest id nu exista.")

    hass.services.async_register(
        DOMAIN, SERVICE_SET_MILEAGE, _set_mileage, schema=SET_MILEAGE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SET_DOCUMENT, _set_document, schema=SET_DOCUMENT_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_RENEW_DOCUMENT, _renew_document, schema=RENEW_DOCUMENT_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_MARK_SERVICE_DONE,
        _mark_service_done,
        schema=MARK_SERVICE_DONE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_ADD_EXPENSE, _add_expense, schema=ADD_EXPENSE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_DELETE_EXPENSE, _delete_expense, schema=DELETE_EXPENSE_SCHEMA
    )

    domain_data[DATA_SERVICES] = True
