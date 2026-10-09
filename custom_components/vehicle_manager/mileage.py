"""Kilometraj automat: preia valoarea dintr-un senzor existent (OBD, aplicatia masinii...)."""

from __future__ import annotations

import logging
import time
from typing import Any

from homeassistant.const import ATTR_UNIT_OF_MEASUREMENT, STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, State, callback
from homeassistant.helpers.event import async_call_later, async_track_state_change_event

from .const import CONF_MILEAGE, CONF_MILEAGE_SOURCE
from .coordinator import VehicleCoordinator, as_int

_LOGGER = logging.getLogger(__name__)

# In mers, senzorul se poate actualiza la cateva secunde; config entry-ul
# (scris pe disc) se actualizeaza cel mult o data la acest interval.
MIN_WRITE_INTERVAL = 300

# Factor de conversie spre km, dupa unitatea senzorului.
UNIT_TO_KM: dict[str, float] = {
    "km": 1.0,
    "mi": 1.609344,
    "m": 0.001,
}


def mileage_from_state(state: State | None) -> int | None:
    """Kilometrajul in km dintr-o stare de senzor, sau None daca nu e utilizabil."""
    if state is None or state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE, ""):
        return None
    try:
        value = float(state.state)
    except ValueError:
        return None
    unit = str(state.attributes.get(ATTR_UNIT_OF_MEASUREMENT) or "km").strip().lower()
    factor = UNIT_TO_KM.get(unit)
    if factor is None or value < 0:
        return None
    return int(value * factor)


class MileageTracker:
    """Urmareste senzorul ales si mareste kilometrajul vehiculului.

    Valoarea doar creste: o citire mai mica (senzor resetat, eroare, 0) e ignorata,
    ca o valoare gresita sa nu strice scadentele pe kilometraj.
    """

    def __init__(self, hass: HomeAssistant, coordinator: VehicleCoordinator) -> None:
        self.hass = hass
        self.coordinator = coordinator
        self.source: str | None = None
        self._unsub_state: CALLBACK_TYPE | None = None
        self._unsub_timer: CALLBACK_TYPE | None = None
        self._pending: int | None = None
        self._last_write = 0.0

    @callback
    def async_refresh_source(self) -> None:
        """Porneste/opreste urmarirea dupa optiunea curenta a vehiculului."""
        source = self.coordinator.option(CONF_MILEAGE_SOURCE)
        if source == self.source:
            return
        self.async_stop()
        self.source = source
        if not source:
            return
        self._unsub_state = async_track_state_change_event(
            self.hass, [source], self._async_state_changed
        )
        # valoarea de acum, fara sa asteptam urmatoarea schimbare
        self._async_offer(mileage_from_state(self.hass.states.get(source)))

    @callback
    def async_stop(self) -> None:
        """Opreste urmarirea si scrie valoarea ramasa in asteptare."""
        if self._unsub_state:
            self._unsub_state()
            self._unsub_state = None
        if self._unsub_timer:
            self._unsub_timer()
            self._unsub_timer = None
        if self._pending is not None:
            self._async_write()
        self.source = None

    @callback
    def _async_state_changed(self, event: Event[Any]) -> None:
        self._async_offer(mileage_from_state(event.data.get("new_state")))

    @callback
    def _async_offer(self, km: int | None) -> None:
        if km is None:
            return
        current = as_int(self.coordinator.option(CONF_MILEAGE)) or 0
        if km <= max(current, self._pending or 0):
            return
        self._pending = km

        wait = self._last_write + MIN_WRITE_INTERVAL - time.monotonic()
        if wait <= 0:
            self._async_write()
        elif self._unsub_timer is None:
            self._unsub_timer = async_call_later(self.hass, wait, self._async_timer_fired)

    @callback
    def _async_timer_fired(self, _now: Any) -> None:
        self._unsub_timer = None
        self._async_write()

    @callback
    def _async_write(self) -> None:
        km, self._pending = self._pending, None
        if km is None:
            return
        self._last_write = time.monotonic()
        _LOGGER.debug("%s: kilometraj %s km din %s", self.coordinator.vehicle_name, km, self.source)
        self.hass.async_create_task(self.coordinator.async_set_options({CONF_MILEAGE: km}))
