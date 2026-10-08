"""Entitati number editabile: kilometraj si scadente pe km."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_MILEAGE, DOCUMENTS, DOMAIN, km_key
from .coordinator import VehicleCoordinator, as_int
from .entity import VehicleEntity

MAX_KM = 3000000


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Creeaza entitatile number ale vehiculului."""
    coordinator: VehicleCoordinator = hass.data[DOMAIN]["coordinators"][entry.entry_id]

    entities: list[NumberEntity] = [VehicleMileageNumber(coordinator)]
    entities.extend(
        VehicleDocumentKmNumber(coordinator, doc)
        for doc, meta in DOCUMENTS.items()
        if meta["uses_km"]
    )
    async_add_entities(entities)


class _BaseKmNumber(VehicleEntity, NumberEntity):
    """Baza pentru valorile exprimate in kilometri."""

    _attr_native_min_value = 0
    _attr_native_max_value = MAX_KM
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX
    _attr_native_unit_of_measurement = UnitOfLength.KILOMETERS


class VehicleMileageNumber(_BaseKmNumber):
    """Kilometrajul curent, editabil din interfata."""

    _attr_translation_key = "mileage"
    _attr_icon = "mdi:counter"

    def __init__(self, coordinator: VehicleCoordinator) -> None:
        """Initializeaza entitatea de kilometraj."""
        super().__init__(coordinator, "mileage")

    @property
    def native_value(self) -> float | None:
        """Kilometrajul curent."""
        return self.coordinator.data["vehicle"][CONF_MILEAGE]

    async def async_set_native_value(self, value: float) -> None:
        """Salveaza kilometrajul nou."""
        await self.coordinator.async_set_options({CONF_MILEAGE: int(value)})


class VehicleDocumentKmNumber(_BaseKmNumber):
    """Kilometrajul la care devine scadent un document (revizie, distributie)."""

    def __init__(self, coordinator: VehicleCoordinator, doc: str) -> None:
        """Initializeaza entitatea de scadenta pe km."""
        super().__init__(coordinator, km_key(doc))
        self._doc = doc
        self._attr_translation_key = km_key(doc)
        self._attr_icon = DOCUMENTS[doc]["icon"]

    @property
    def native_value(self) -> float | None:
        """Kilometrajul scadent configurat."""
        return as_int(self.coordinator.options.get(km_key(self._doc)))

    async def async_set_native_value(self, value: float) -> None:
        """Salveaza kilometrajul scadent."""
        await self.coordinator.async_set_options({km_key(self._doc): int(value)})
