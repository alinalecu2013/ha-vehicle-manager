"""Entitate image: poza vehiculului."""

from __future__ import annotations

import mimetypes
from pathlib import Path

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import UNDEFINED
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import VehicleCoordinator
from .entity import VehicleEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Creeaza entitatea cu poza vehiculului."""
    coordinator: VehicleCoordinator = hass.data[DOMAIN]["coordinators"][entry.entry_id]
    async_add_entities([VehiclePhotoImage(hass, coordinator)])


class VehiclePhotoImage(VehicleEntity, ImageEntity):
    """Poza vehiculului, fie dintr-un URL, fie dintr-un fisier local."""

    _attr_translation_key = "photo"

    def __init__(self, hass: HomeAssistant, coordinator: VehicleCoordinator) -> None:
        """Initializeaza entitatea de imagine."""
        VehicleEntity.__init__(self, coordinator, "photo")
        ImageEntity.__init__(self, hass)
        self._source: str | None = None
        self._bytes: bytes | None = None
        self._apply_source()

    # ------------------------------------------------------------------
    @callback
    def _handle_coordinator_update(self) -> None:
        """Reseteaza cache-ul daca poza s-a schimbat."""
        self._apply_source()
        super()._handle_coordinator_update()

    @callback
    def _apply_source(self) -> None:
        """Preia sursa curenta a pozei din coordinator."""
        source = self.coordinator.data.get("photo")
        if source == self._source:
            return
        self._source = source
        self._bytes = None
        self._cached_image = None
        self._attr_image_last_updated = dt_util.utcnow()

        if source and source.startswith(("http://", "https://")):
            self._attr_image_url = source
        else:
            self._attr_image_url = UNDEFINED

        if source:
            guessed = mimetypes.guess_type(source)[0]
            self._attr_content_type = guessed or "image/jpeg"

    # ------------------------------------------------------------------
    def _local_path(self) -> Path | None:
        """Rezolva sursa intr-un fisier din interiorul directorului de config."""
        source = self._source
        if not source or source.startswith(("http://", "https://")):
            return None

        if source.startswith("/local/"):
            candidate = Path(self.hass.config.path("www", source[len("/local/") :]))
        elif Path(source).is_absolute():
            candidate = Path(source)
        else:
            candidate = Path(self.hass.config.path(source))

        try:
            resolved = candidate.resolve()
            config_dir = Path(self.hass.config.config_dir).resolve()
            resolved.relative_to(config_dir)
        except (OSError, ValueError):
            return None

        return resolved

    @property
    def available(self) -> bool:
        """Disponibil doar daca exista o poza configurata."""
        return super().available and bool(self._source)

    async def async_image(self) -> bytes | None:
        """Returneaza octetii pozei."""
        if self._attr_image_url is not UNDEFINED:
            return await super().async_image()

        if self._bytes is not None:
            return self._bytes

        path = self._local_path()
        if path is None:
            return None

        def _read() -> bytes | None:
            try:
                return path.read_bytes()
            except OSError:
                return None

        self._bytes = await self.hass.async_add_executor_job(_read)
        return self._bytes
