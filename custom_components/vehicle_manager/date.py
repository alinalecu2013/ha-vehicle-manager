"""Entitati date editabile pentru expirarea actelor."""

from __future__ import annotations

from datetime import date

from homeassistant.components.date import DateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOCUMENTS, DOMAIN, date_key
from .coordinator import VehicleCoordinator, as_date
from .entity import VehicleEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Creeaza cate o entitate date pentru fiecare act."""
    coordinator: VehicleCoordinator = hass.data[DOMAIN]["coordinators"][entry.entry_id]
    async_add_entities(VehicleDocumentDate(coordinator, doc) for doc in DOCUMENTS)


class VehicleDocumentDate(VehicleEntity, DateEntity):
    """Data de expirare a unui act, editabila direct din interfata."""

    def __init__(self, coordinator: VehicleCoordinator, doc: str) -> None:
        """Initializeaza entitatea de data."""
        super().__init__(coordinator, date_key(doc))
        self._doc = doc
        self._attr_translation_key = date_key(doc)
        self._attr_icon = DOCUMENTS[doc]["icon"]

    @property
    def native_value(self) -> date | None:
        """Data de expirare configurata."""
        return as_date(self.coordinator.options.get(date_key(self._doc)))

    async def async_set_value(self, value: date) -> None:
        """Salveaza data noua de expirare."""
        await self.coordinator.async_set_options({date_key(self._doc): value})
