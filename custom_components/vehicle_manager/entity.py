"""Clasa de baza pentru entitatile Vehicle Manager."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_MAKE,
    CONF_MODEL,
    CONF_PLATE,
    CONF_YEAR,
    DOMAIN,
    VERSION,
)
from .coordinator import VehicleCoordinator


class VehicleEntity(CoordinatorEntity[VehicleCoordinator]):
    """Entitate atasata unui vehicul (un config entry = un vehicul)."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: VehicleCoordinator, key: str) -> None:
        """Initializeaza entitatea."""
        super().__init__(coordinator)
        self._key = key
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Grupeaza entitatile sub un singur device per vehicul."""
        opts = self.coordinator.options
        make = opts.get(CONF_MAKE) or "Vehicul"
        model = opts.get(CONF_MODEL) or ""
        year = opts.get(CONF_YEAR)
        model_label = " ".join(str(p) for p in (model, f"({year})" if year else "") if p)

        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.entry.entry_id)},
            name=self.coordinator.vehicle_name,
            manufacturer=str(make),
            model=model_label or None,
            serial_number=opts.get(CONF_PLATE) or None,
            sw_version=VERSION,
        )
