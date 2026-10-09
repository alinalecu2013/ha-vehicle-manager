"""Locul de parcare al vehiculului, ca entitate pe harta Home Assistant."""

from __future__ import annotations

from typing import Any

from homeassistant.components.device_tracker import SourceType, TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_PARKING, DOMAIN
from .coordinator import VehicleCoordinator
from .entity import VehicleEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Creeaza entitatea cu locul de parcare."""
    coordinator: VehicleCoordinator = hass.data[DOMAIN]["coordinators"][entry.entry_id]
    async_add_entities([VehicleParkingTracker(coordinator)])


class VehicleParkingTracker(VehicleEntity, TrackerEntity):
    """Ultima pozitie in care a fost parcata masina."""

    _attr_translation_key = "parking_location"
    _attr_icon = "mdi:car-brake-parking"

    def __init__(self, coordinator: VehicleCoordinator) -> None:
        """Initializeaza entitatea."""
        super().__init__(coordinator, "parking_location")

    @property
    def _parking(self) -> dict[str, Any]:
        return self.coordinator.option(CONF_PARKING) or {}

    @property
    def source_type(self) -> SourceType:
        return SourceType.GPS

    @property
    def latitude(self) -> float | None:
        return self._parking.get("latitude")

    @property
    def longitude(self) -> float | None:
        return self._parking.get("longitude")

    @property
    def location_accuracy(self) -> int:
        return int(self._parking.get("accuracy") or 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Momentul parcarii si daca masina e acum in mers."""
        parking = self._parking
        return {"stare": parking.get("state"), "din": parking.get("time")}
