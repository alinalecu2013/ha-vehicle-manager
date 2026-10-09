"""Senzori pentru Vehicle Manager."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import (
    CONF_COLOR,
    CONF_ENGINE_CAPACITY,
    CONF_FUEL_TYPE,
    CONF_MAKE,
    CONF_MODEL,
    CONF_PLATE,
    CONF_VIN,
    CONF_YEAR,
    DOCUMENTS,
    DOMAIN,
    STATUS_EXPIRED,
    STATUS_OK,
    STATUS_UNKNOWN,
    STATUS_WARNING,
    date_key,
    km_key,
)
from .coordinator import VehicleCoordinator
from .costs import get_cost_manager, signal_expenses
from .entity import VehicleEntity

STATUS_ICONS = {
    STATUS_OK: "mdi:shield-check",
    STATUS_WARNING: "mdi:shield-alert",
    STATUS_EXPIRED: "mdi:shield-remove",
    STATUS_UNKNOWN: "mdi:shield-off-outline",
}

SPECS: tuple[tuple[str, str, str], ...] = (
    ("make", CONF_MAKE, "mdi:car-side"),
    ("model", CONF_MODEL, "mdi:car-info"),
    ("year", CONF_YEAR, "mdi:calendar"),
    ("color", CONF_COLOR, "mdi:palette"),
    ("engine_capacity", CONF_ENGINE_CAPACITY, "mdi:engine"),
    ("fuel_type", CONF_FUEL_TYPE, "mdi:gas-station"),
    ("license_plate", CONF_PLATE, "mdi:card-text-outline"),
    ("vin", CONF_VIN, "mdi:barcode"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Creeaza senzorii vehiculului."""
    coordinator: VehicleCoordinator = hass.data[DOMAIN]["coordinators"][entry.entry_id]

    entities: list[SensorEntity] = [VehicleStatusSensor(coordinator)]
    entities.extend(VehicleDocumentSensor(coordinator, doc) for doc in DOCUMENTS)
    entities.extend(
        VehicleSpecSensor(coordinator, key, option, icon) for key, option, icon in SPECS
    )
    entities.append(VehicleExpenseSensor(coordinator, yearly=True))
    entities.append(VehicleExpenseSensor(coordinator, yearly=False))
    entities.append(VehicleFuelSensor(coordinator))
    async_add_entities(entities)


class VehicleStatusSensor(VehicleEntity, SensorEntity):
    """Senzorul principal: starea generala plus toate datele pentru card."""

    _attr_translation_key = "status"
    # cardul citeste starea curenta; in istoric nu pastram datele mari si locul de parcare
    _unrecorded_attributes = frozenset(
        {"vehicle", "documents", "entities", "photo", "model_3d", "attention", "updated"}
    )

    def __init__(self, coordinator: VehicleCoordinator) -> None:
        """Initializeaza senzorul de stare."""
        super().__init__(coordinator, "status")

    @property
    def native_value(self) -> str:
        """Starea cea mai grava dintre toate actele."""
        return self.coordinator.data["status"]

    @property
    def icon(self) -> str:
        """Pictograma in functie de stare."""
        return STATUS_ICONS.get(self.native_value, "mdi:car")

    def _related_entities(self) -> dict[str, str]:
        """Harta cheie -> entity_id, ca sa poata cardul deschide more-info."""
        registry = er.async_get(self.hass)
        entry_id = self.coordinator.entry.entry_id

        def lookup(domain: str, key: str) -> str | None:
            return registry.async_get_entity_id(domain, DOMAIN, f"{entry_id}_{key}")

        wanted: list[tuple[str, str]] = [
            ("number", "mileage"),
            ("image", "photo"),
            ("binary_sensor", "attention"),
            ("binary_sensor", "expired"),
            ("sensor", "expenses_year"),
            ("sensor", "fuel_consumption"),
            ("device_tracker", "parking_location"),
        ]
        for doc, meta in DOCUMENTS.items():
            wanted.append(("date", date_key(doc)))
            wanted.append(("sensor", f"{doc}_days"))
            if meta["uses_km"]:
                wanted.append(("number", km_key(doc)))

        mapping: dict[str, str] = {}
        for domain, key in wanted:
            entity_id = lookup(domain, key)
            if entity_id:
                mapping[key] = entity_id
        return mapping

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Toate datele vehiculului, consumate de cardul Lovelace."""
        data = self.coordinator.data
        return {
            "vm_card": True,
            "vm_version": 1,
            "entry_id": data["entry_id"],
            "vehicle_name": data["name"],
            "vehicle": data["vehicle"],
            "documents": data["documents"],
            "photo": data["photo"],
            "model_3d": data["model_3d"],
            "attention": data["attention"],
            "warn_days": data["warn_days"],
            "warn_km": data["warn_km"],
            "updated": data["updated"],
            "entities": self._related_entities(),
        }


class VehicleDocumentSensor(VehicleEntity, SensorEntity):
    """Zile ramase pana la expirarea unui act."""

    _attr_native_unit_of_measurement = UnitOfTime.DAYS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: VehicleCoordinator, doc: str) -> None:
        """Initializeaza senzorul de document."""
        super().__init__(coordinator, f"{doc}_days")
        self._doc = doc
        self._attr_translation_key = f"{doc}_days"
        self._attr_icon = DOCUMENTS[doc]["icon"]

    @property
    def _document(self) -> dict[str, Any]:
        """Datele documentului din coordinator."""
        return self.coordinator.data["documents"][self._doc]

    @property
    def native_value(self) -> int | None:
        """Zile ramase (negativ daca a expirat)."""
        return self._document["days"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Detalii despre document."""
        document = self._document
        attributes: dict[str, Any] = {
            "document": document["label"],
            # cheia folosita de servicii (ex. renew_document), pentru automatizari
            "document_key": self._doc,
            "expira_la": document["date"],
            "stare": document["status"],
        }
        if document["uses_km"]:
            attributes["scadent_la_km"] = document["due_km"]
            attributes["km_ramasi"] = document["km_remaining"]
        return attributes


class VehicleSpecSensor(VehicleEntity, SensorEntity):
    """O caracteristica a vehiculului (marca, model, an, culoare...)."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self, coordinator: VehicleCoordinator, key: str, option: str, icon: str
    ) -> None:
        """Initializeaza senzorul de caracteristica."""
        super().__init__(coordinator, key)
        self._option = option
        self._attr_translation_key = key
        self._attr_icon = icon
        if option == CONF_ENGINE_CAPACITY:
            self._attr_native_unit_of_measurement = "cm3"

    @property
    def native_value(self) -> Any:
        """Valoarea caracteristicii."""
        vehicle = self.coordinator.data["vehicle"]
        if self._option == CONF_FUEL_TYPE:
            return vehicle.get("fuel_label")
        return vehicle.get(self._option)

    @property
    def icon(self) -> str:
        """Pictograma; pentru combustibil depinde de tip."""
        if self._option == CONF_FUEL_TYPE:
            return self.coordinator.data["vehicle"].get("fuel_icon", self._attr_icon)
        return self._attr_icon

    @property
    def available(self) -> bool:
        """Indisponibil daca utilizatorul nu a completat caracteristica."""
        return super().available and self.native_value not in (None, "")


class VehicleExpenseSensor(VehicleEntity, SensorEntity):
    """Totalul cheltuielilor: pe anul curent sau pe tot istoricul."""

    _attr_device_class = SensorDeviceClass.MONETARY
    # TOTAL (nu TOTAL_INCREASING): stergerea unei cheltuieli poate scadea totalul.
    _attr_state_class = SensorStateClass.TOTAL
    _attr_suggested_display_precision = 2

    def __init__(self, coordinator: VehicleCoordinator, *, yearly: bool) -> None:
        """Initializeaza senzorul de cheltuieli."""
        key = "expenses_year" if yearly else "expenses_total"
        super().__init__(coordinator, key)
        self._yearly = yearly
        self._attr_translation_key = key
        self._attr_icon = "mdi:cash-multiple" if yearly else "mdi:cash-register"
        # moneda setata in Home Assistant (Setari > Sistem > General)
        self._attr_native_unit_of_measurement = coordinator.hass.config.currency

    async def async_added_to_hass(self) -> None:
        """Se actualizeaza imediat la fiecare cheltuiala adaugata sau stearsa."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                signal_expenses(self.coordinator.entry.entry_id),
                self.async_write_ha_state,
            )
        )

    @property
    def _summary(self) -> dict[str, Any]:
        return get_cost_manager(self.hass).summary(self.coordinator.entry.entry_id)

    @property
    def native_value(self) -> float:
        """Suma cheltuielilor (anul curent sau total)."""
        summary = self._summary
        return summary["year_total"] if self._yearly else summary["total"]

    @property
    def last_reset(self) -> datetime | None:
        """Totalul anual porneste de la zero la 1 ianuarie."""
        if not self._yearly:
            return None
        now = dt_util.now()
        return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Defalcarea pe categorii pentru anul curent."""
        if not self._yearly:
            return None
        summary = self._summary
        return {
            "an": summary["year"],
            "numar_cheltuieli": summary["year_count"],
            "pe_categorii": summary["year_by_category"],
        }


class VehicleFuelSensor(VehicleEntity, SensorEntity):
    """Consumul mediu calculat din alimentari, metoda "plin la plin"."""

    _attr_translation_key = "fuel_consumption"
    _attr_icon = "mdi:gas-station-outline"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 1

    def __init__(self, coordinator: VehicleCoordinator) -> None:
        """Initializeaza senzorul de consum."""
        super().__init__(coordinator, "fuel_consumption")

    async def async_added_to_hass(self) -> None:
        """Se recalculeaza la fiecare alimentare adaugata sau stearsa."""
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                signal_expenses(self.coordinator.entry.entry_id),
                self.async_write_ha_state,
            )
        )

    @property
    def native_unit_of_measurement(self) -> str:
        """kWh/100 km pentru masini electrice, altfel L/100 km."""
        electric = self.coordinator.option(CONF_FUEL_TYPE) == "electric"
        return "kWh/100 km" if electric else "L/100 km"

    @property
    def _summary(self) -> dict[str, Any] | None:
        return get_cost_manager(self.hass).fuel(self.coordinator.entry.entry_id)["summary"]

    @property
    def native_value(self) -> float | None:
        """Consumul mediu pe toate intervalele masurate (gol pana la doua plinuri)."""
        summary = self._summary
        return summary["consumption"] if summary else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Ultimul plin, costul pe km si distanta pe care s-a masurat."""
        summary = self._summary
        if not summary:
            return None
        return {
            "ultimul_plin": summary["last_consumption"],
            "data_ultimului_plin": summary["last_date"],
            "cost_pe_km": summary["cost_per_km"],
            "km_masurati": summary["km"],
            "cantitate_totala": summary["quantity"],
        }
