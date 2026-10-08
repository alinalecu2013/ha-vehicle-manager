"""Calendar cu scadentele actelor unui vehicul."""

from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN, STATUS_EXPIRED
from .coordinator import VehicleCoordinator, as_date
from .entity import VehicleEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Creeaza calendarul vehiculului."""
    coordinator: VehicleCoordinator = hass.data[DOMAIN]["coordinators"][entry.entry_id]
    async_add_entities([VehicleCalendar(coordinator)])


def _format_km(value: int) -> str:
    return f"{value:,}".replace(",", ".")


class VehicleCalendar(VehicleEntity, CalendarEntity):
    """Un eveniment pe toata ziua pentru fiecare act cu data de scadenta.

    Actele urmarite doar pe kilometraj nu au o zi anume, deci nu apar aici.
    """

    _attr_translation_key = "deadlines"

    def __init__(self, coordinator: VehicleCoordinator) -> None:
        """Initializeaza calendarul."""
        super().__init__(coordinator, "deadlines")

    def _events(self) -> list[CalendarEvent]:
        vehicle = self.coordinator.vehicle_name
        events: list[CalendarEvent] = []

        for doc in self.coordinator.data["documents"].values():
            due = as_date(doc["date"])
            if due is None:
                continue

            details = [f"Scadenta {doc['label']} pentru {vehicle}."]
            if doc["due_km"] is not None:
                details.append(f"Sau la {_format_km(doc['due_km'])} km.")
            if doc["status"] == STATUS_EXPIRED:
                details.append("Actul este expirat.")

            events.append(
                CalendarEvent(
                    start=due,
                    end=due + timedelta(days=1),
                    summary=f"{doc['label']} · {vehicle}",
                    description=" ".join(details),
                    uid=f"{self.coordinator.entry.entry_id}_{doc['key']}",
                )
            )

        events.sort(key=lambda event: event.start)
        return events

    @property
    def event(self) -> CalendarEvent | None:
        """Urmatoarea scadenta (sau cea de azi)."""
        today = dt_util.now().date()
        return next((e for e in self._events() if e.end > today), None)

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Scadentele din intervalul cerut de interfata calendarului."""
        start = dt_util.as_local(start_date).date()
        end_local = dt_util.as_local(end_date)
        # sfarsitul intervalului e exclusiv: o zi intra doar daca intervalul trece de miezul ei
        end = end_local.date() + timedelta(days=1 if end_local.time() else 0)
        return [e for e in self._events() if e.end > start and e.start < end]
