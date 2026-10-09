"""Unde am parcat: salveaza pozitia telefonului cand se deconecteaza de Bluetooth-ul masinii.

Aplicatia Home Assistant Companion are senzorul "Bluetooth connection", cu atributul
connected_paired_devices (ex. ["AA:BB:CC:DD:EE:FF (Opel Astra)"]). Cand masina dispare
din lista, pozitia GPS a telefonului (device_tracker) devine locul de parcare.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.const import ATTR_LATITUDE, ATTR_LONGITUDE
from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, State, callback
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util import dt as dt_util

from .const import (
    CONF_PARKING,
    CONF_PARKING_BT_DEVICE,
    CONF_PARKING_BT_SENSOR,
    CONF_PARKING_TRACKER,
)
from .coordinator import VehicleCoordinator

_LOGGER = logging.getLogger(__name__)

STATE_PARKED = "parked"
STATE_DRIVING = "driving"


def car_connected(state: State | None, device: str) -> bool | None:
    """True/False daca masina e in lista dispozitivelor conectate; None daca nu se stie."""
    if state is None or state.state in ("unknown", "unavailable"):
        return None
    devices = state.attributes.get("connected_paired_devices")
    if devices is None:
        return None
    needle = device.strip().lower()
    return any(needle in str(item).lower() for item in devices)


def position_of(state: State | None) -> dict[str, Any] | None:
    """Latitudinea/longitudinea unei entitati (device_tracker, person, zone)."""
    if state is None:
        return None
    lat = state.attributes.get(ATTR_LATITUDE)
    lon = state.attributes.get(ATTR_LONGITUDE)
    if lat is None or lon is None:
        return None
    position = {"latitude": round(float(lat), 6), "longitude": round(float(lon), 6)}
    accuracy = state.attributes.get("gps_accuracy")
    if accuracy is not None:
        position["accuracy"] = int(accuracy)
    return position


async def async_save_parking(
    coordinator: VehicleCoordinator, position: dict[str, Any] | None, state: str
) -> None:
    """Salveaza locul de parcare (sau doar starea "in mers", pastrand ultima pozitie)."""
    parking = dict(coordinator.option(CONF_PARKING) or {})
    if position is not None:
        parking = {k: v for k, v in parking.items() if k not in ("latitude", "longitude", "accuracy")}
        parking.update(position)
    parking["state"] = state
    parking["time"] = dt_util.now().isoformat(timespec="seconds")
    await coordinator.async_set_options({CONF_PARKING: parking})


class ParkingTracker:
    """Urmareste senzorul Bluetooth al telefonului pentru un vehicul."""

    def __init__(self, hass: HomeAssistant, coordinator: VehicleCoordinator) -> None:
        self.hass = hass
        self.coordinator = coordinator
        self._config: tuple[str, str, str] | None = None
        self._unsub: CALLBACK_TYPE | None = None
        self._connected: bool | None = None

    @callback
    def async_refresh_source(self) -> None:
        """Porneste/opreste urmarirea dupa optiunile vehiculului."""
        option = self.coordinator.option
        config = (
            option(CONF_PARKING_TRACKER),
            option(CONF_PARKING_BT_SENSOR),
            option(CONF_PARKING_BT_DEVICE),
        )
        if config == self._config:
            return
        self.async_stop()
        if not all(config):
            return
        self._config = config
        _tracker, sensor, device = config
        self._connected = car_connected(self.hass.states.get(sensor), device)
        self._unsub = async_track_state_change_event(self.hass, [sensor], self._async_changed)

    @callback
    def async_stop(self) -> None:
        if self._unsub:
            self._unsub()
            self._unsub = None
        self._config = None
        self._connected = None

    @callback
    def _async_changed(self, event: Event[Any]) -> None:
        if self._config is None:
            return
        tracker, _sensor, device = self._config
        connected = car_connected(event.data.get("new_state"), device)
        if connected is None or connected == self._connected:
            return
        previous, self._connected = self._connected, connected

        if connected:
            self.hass.async_create_task(async_save_parking(self.coordinator, None, STATE_DRIVING))
        elif previous:  # tocmai s-a deconectat de masina -> aici a parcat
            position = position_of(self.hass.states.get(tracker))
            if position is None:
                _LOGGER.warning(
                    "%s: deconectat de la masina, dar %s nu are pozitie GPS",
                    self.coordinator.vehicle_name,
                    tracker,
                )
            self.hass.async_create_task(
                async_save_parking(self.coordinator, position, STATE_PARKED)
            )
