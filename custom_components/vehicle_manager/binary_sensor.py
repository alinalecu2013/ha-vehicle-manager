"""Senzori binari pentru alerte, utili in automatizari."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, STATUS_EXPIRED, STATUS_WARNING
from .coordinator import VehicleCoordinator
from .entity import VehicleEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Creeaza senzorii binari ai vehiculului."""
    coordinator: VehicleCoordinator = hass.data[DOMAIN]["coordinators"][entry.entry_id]
    async_add_entities(
        [
            VehicleAttentionBinarySensor(coordinator),
            VehicleExpiredBinarySensor(coordinator),
        ]
    )


class _BaseAlert(VehicleEntity, BinarySensorEntity):
    """Baza pentru alertele vehiculului."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def _documents(self, statuses: tuple[str, ...]) -> list[str]:
        """Etichetele actelor care se afla in starile cerute."""
        return [
            document["label"]
            for document in self.coordinator.data["documents"].values()
            if document["status"] in statuses
        ]


class VehicleAttentionBinarySensor(_BaseAlert):
    """Pornit cand cel putin un act expira curand sau a expirat."""

    _attr_translation_key = "attention"
    _attr_icon = "mdi:alert-decagram"

    def __init__(self, coordinator: VehicleCoordinator) -> None:
        """Initializeaza senzorul de atentionare."""
        super().__init__(coordinator, "attention")

    @property
    def is_on(self) -> bool:
        """True daca exista acte de rezolvat."""
        return bool(self.coordinator.data["attention"])

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Lista actelor care necesita atentie."""
        return {
            "acte": self.coordinator.data["attention"],
            "expira_curand": self._documents((STATUS_WARNING,)),
            "expirate": self._documents((STATUS_EXPIRED,)),
        }


class VehicleExpiredBinarySensor(_BaseAlert):
    """Pornit cand cel putin un act a expirat."""

    _attr_translation_key = "expired"
    _attr_icon = "mdi:close-octagon"

    def __init__(self, coordinator: VehicleCoordinator) -> None:
        """Initializeaza senzorul de expirare."""
        super().__init__(coordinator, "expired")

    @property
    def is_on(self) -> bool:
        """True daca exista acte expirate."""
        return bool(self._documents((STATUS_EXPIRED,)))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Lista actelor expirate."""
        return {"expirate": self._documents((STATUS_EXPIRED,))}
