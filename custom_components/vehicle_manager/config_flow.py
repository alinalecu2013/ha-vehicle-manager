"""Config flow pentru Vehicle Manager (un vehicul per config entry)."""

from __future__ import annotations

import logging
import shutil
import uuid
from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector

from .const import (
    CONF_COLOR,
    CONF_ENGINE_CAPACITY,
    CONF_FUEL_TYPE,
    CONF_MAKE,
    CONF_MEDIA_ID,
    CONF_MILEAGE,
    CONF_MILEAGE_SOURCE,
    CONF_PARKING_BT_DEVICE,
    CONF_PARKING_BT_SENSOR,
    CONF_PARKING_TRACKER,
    CONF_MODEL,
    CONF_MODEL_3D,
    CONF_MODEL_3D_UPLOAD,
    CONF_PHOTO,
    CONF_PHOTO_UPLOAD,
    CONF_PLATE,
    CONF_VIN,
    CONF_WARN_DAYS,
    CONF_WARN_KM,
    CONF_YEAR,
    DEFAULT_WARN_DAYS,
    DEFAULT_WARN_KM,
    DOCUMENTS,
    DOMAIN,
    FUEL_TYPES,
    MEDIA_DIRNAME,
    date_key,
    km_key,
)

_LOGGER = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
MODEL_EXTENSIONS = {".glb", ".gltf"}


# ----------------------------------------------------------------------
# Scheme
# ----------------------------------------------------------------------
def _vehicle_schema() -> vol.Schema:
    """Schema pentru caracteristicile vehiculului."""
    return vol.Schema(
        {
            vol.Required(CONF_NAME): selector.TextSelector(),
            vol.Required(CONF_MAKE): selector.TextSelector(),
            vol.Required(CONF_MODEL): selector.TextSelector(),
            vol.Required(CONF_PLATE): selector.TextSelector(),
            vol.Optional(CONF_YEAR): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1900, max=2100, step=1, mode=selector.NumberSelectorMode.BOX
                )
            ),
            vol.Optional(CONF_MILEAGE): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=3000000,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="km",
                )
            ),
            vol.Optional(CONF_COLOR): selector.TextSelector(),
            vol.Optional(CONF_ENGINE_CAPACITY): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=10000,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="cm3",
                )
            ),
            vol.Optional(CONF_FUEL_TYPE): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=FUEL_TYPES,
                    translation_key=CONF_FUEL_TYPE,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(CONF_VIN): selector.TextSelector(),
        }
    )


def _documents_schema() -> vol.Schema:
    """Schema pentru datele de expirare ale actelor."""
    fields: dict[Any, Any] = {}
    for doc, meta in DOCUMENTS.items():
        fields[vol.Optional(date_key(doc))] = selector.DateSelector()
        if meta["uses_km"]:
            fields[vol.Optional(km_key(doc))] = selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=3000000,
                    step=1,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="km",
                )
            )
    return vol.Schema(fields)


def _media_schema() -> vol.Schema:
    """Schema pentru poza si modelul 3D (upload sau URL)."""
    fields: dict[Any, Any] = {}

    try:
        fields[vol.Optional(CONF_PHOTO_UPLOAD)] = selector.FileSelector(
            selector.FileSelectorConfig(accept="image/*")
        )
        fields[vol.Optional(CONF_MODEL_3D_UPLOAD)] = selector.FileSelector(
            selector.FileSelectorConfig(accept=".glb,.gltf,model/gltf-binary")
        )
    except (AttributeError, TypeError, vol.Invalid):  # pragma: no cover
        _LOGGER.debug("FileSelector indisponibil; folosesc doar camp URL")

    fields[vol.Optional(CONF_PHOTO)] = selector.TextSelector()
    fields[vol.Optional(CONF_MODEL_3D)] = selector.TextSelector()
    return vol.Schema(fields)


def _thresholds_schema() -> vol.Schema:
    """Schema pentru pragurile de avertizare."""
    return vol.Schema(
        {
            vol.Optional(CONF_WARN_DAYS, default=DEFAULT_WARN_DAYS): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1, max=365, step=1, mode=selector.NumberSelectorMode.BOX
                )
            ),
            vol.Optional(CONF_WARN_KM, default=DEFAULT_WARN_KM): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=0,
                    max=50000,
                    step=100,
                    mode=selector.NumberSelectorMode.BOX,
                    unit_of_measurement="km",
                )
            ),
        }
    )


# ----------------------------------------------------------------------
# Utilitare
# ----------------------------------------------------------------------
def _clean(data: dict[str, Any]) -> dict[str, Any]:
    """Elimina valorile goale si normalizeaza numerele intregi."""
    result: dict[str, Any] = {}
    for key, value in data.items():
        if value in (None, ""):
            continue
        if key in (CONF_YEAR, CONF_MILEAGE, CONF_ENGINE_CAPACITY, CONF_WARN_DAYS, CONF_WARN_KM):
            result[key] = int(float(value))
        elif key.endswith("_km"):
            result[key] = int(float(value))
        else:
            result[key] = value
    return result


async def _async_store_upload(
    hass: HomeAssistant,
    file_id: str,
    media_id: str,
    allowed: set[str],
    fallback_ext: str,
) -> str | None:
    """Copiaza un fisier incarcat in config/www/vehicle_manager si da URL-ul /local."""
    from homeassistant.components.file_upload import process_uploaded_file

    target_dir = Path(hass.config.path("www", MEDIA_DIRNAME))

    def _store() -> str | None:
        with process_uploaded_file(hass, file_id) as source:
            extension = Path(source.name).suffix.lower()
            if extension not in allowed:
                extension = fallback_ext
            target_dir.mkdir(parents=True, exist_ok=True)
            # un singur fisier activ per tip: curata variantele vechi
            for old in target_dir.glob(f"{media_id}*"):
                if old.suffix.lower() in allowed:
                    old.unlink(missing_ok=True)
            destination = target_dir / f"{media_id}{extension}"
            shutil.copyfile(source, destination)
            return f"/local/{MEDIA_DIRNAME}/{destination.name}"

    try:
        return await hass.async_add_executor_job(_store)
    except Exception as err:  # pragma: no cover - depinde de FS
        _LOGGER.error("Nu am putut salva fisierul incarcat: %s", err)
        return None


async def _async_apply_media(
    hass: HomeAssistant, user_input: dict[str, Any], media_id: str
) -> dict[str, Any]:
    """Transforma rezultatul pasului media in valori de configurare."""
    result = dict(user_input)

    photo_upload = result.pop(CONF_PHOTO_UPLOAD, None)
    if photo_upload:
        url = await _async_store_upload(
            hass, photo_upload, f"{media_id}-photo", IMAGE_EXTENSIONS, ".jpg"
        )
        if url:
            result[CONF_PHOTO] = url

    model_upload = result.pop(CONF_MODEL_3D_UPLOAD, None)
    if model_upload:
        url = await _async_store_upload(
            hass, model_upload, f"{media_id}-model", MODEL_EXTENSIONS, ".glb"
        )
        if url:
            result[CONF_MODEL_3D] = url

    return result


# ----------------------------------------------------------------------
# Config flow
# ----------------------------------------------------------------------
class VehicleManagerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Adauga un vehicul nou."""

    VERSION = 1

    def __init__(self) -> None:
        """Initializeaza fluxul."""
        self._data: dict[str, Any] = {}
        self._media_id = uuid.uuid4().hex[:12]

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Pasul 1: caracteristicile vehiculului."""
        if user_input is not None:
            plate = str(user_input[CONF_PLATE]).replace(" ", "").upper()
            await self.async_set_unique_id(plate)
            self._abort_if_unique_id_configured()

            cleaned = _clean(user_input)
            cleaned[CONF_PLATE] = plate
            self._data.update(cleaned)
            self._data[CONF_MEDIA_ID] = self._media_id
            return await self.async_step_documents()

        return self.async_show_form(step_id="user", data_schema=_vehicle_schema())

    async def async_step_documents(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Pasul 2: actele vehiculului."""
        if user_input is not None:
            self._data.update(_clean(user_input))
            return await self.async_step_media()

        return self.async_show_form(
            step_id="documents", data_schema=_documents_schema()
        )

    async def async_step_media(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Pasul 3: poza si modelul 3D."""
        if user_input is not None:
            resolved = await _async_apply_media(self.hass, user_input, self._media_id)
            self._data.update(_clean(resolved))
            self._data.setdefault(CONF_WARN_DAYS, DEFAULT_WARN_DAYS)
            self._data.setdefault(CONF_WARN_KM, DEFAULT_WARN_KM)
            return self.async_create_entry(
                title=self._data[CONF_NAME], data=self._data
            )

        return self.async_show_form(step_id="media", data_schema=_media_schema())

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> VehicleManagerOptionsFlow:
        """Returneaza fluxul de opțiuni."""
        return VehicleManagerOptionsFlow(config_entry.entry_id)


# ----------------------------------------------------------------------
# Options flow
# ----------------------------------------------------------------------
class VehicleManagerOptionsFlow(OptionsFlow):
    """Editeaza un vehicul existent."""

    def __init__(self, entry_id: str) -> None:
        """Retine doar id-ul, pentru compatibilitate intre versiuni de HA."""
        self._entry_id = entry_id

    @property
    def _entry(self) -> ConfigEntry:
        """Config entry-ul curent."""
        entry = self.hass.config_entries.async_get_entry(self._entry_id)
        assert entry is not None
        return entry

    @property
    def _current(self) -> dict[str, Any]:
        """Configuratia curenta."""
        entry = self._entry
        return dict(entry.options or entry.data)

    @property
    def _media_id(self) -> str:
        """Prefixul fisierelor media ale vehiculului."""
        return self._current.get(CONF_MEDIA_ID) or self._entry_id[:12]

    async def _async_save(self, changes: dict[str, Any], drop: set[str]) -> ConfigFlowResult:
        """Salveaza modificarile peste configuratia existenta."""
        options = self._current
        for key in drop:
            options.pop(key, None)
        options.update(changes)
        options[CONF_MEDIA_ID] = self._media_id

        new_name = changes.get(CONF_NAME)
        if new_name and str(new_name) != self._entry.title:
            self.hass.config_entries.async_update_entry(
                self._entry, title=str(new_name)
            )
            # Numele device-ului se preia la re-inregistrarea entitatilor.
            self.hass.async_create_task(
                self.hass.config_entries.async_reload(self._entry_id)
            )

        return self.async_create_entry(title="", data=options)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Meniul principal."""
        return self.async_show_menu(
            step_id="init",
            menu_options=[
                "vehicle",
                "documents",
                "media",
                "thresholds",
                "mileage_source",
                "parking",
            ],
        )

    async def async_step_vehicle(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Editeaza caracteristicile."""
        if user_input is not None:
            cleaned = _clean(user_input)
            if CONF_PLATE in cleaned:
                cleaned[CONF_PLATE] = str(cleaned[CONF_PLATE]).replace(" ", "").upper()
            drop = {
                key
                for key in (
                    CONF_YEAR,
                    CONF_MILEAGE,
                    CONF_COLOR,
                    CONF_ENGINE_CAPACITY,
                    CONF_FUEL_TYPE,
                    CONF_VIN,
                )
                if key not in cleaned
            }
            return await self._async_save(cleaned, drop)

        return self.async_show_form(
            step_id="vehicle",
            data_schema=self.add_suggested_values_to_schema(
                _vehicle_schema(), self._current
            ),
        )

    async def async_step_documents(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Editeaza actele."""
        if user_input is not None:
            cleaned = _clean(user_input)
            all_keys = set()
            for doc, meta in DOCUMENTS.items():
                all_keys.add(date_key(doc))
                if meta["uses_km"]:
                    all_keys.add(km_key(doc))
            return await self._async_save(cleaned, all_keys - set(cleaned))

        return self.async_show_form(
            step_id="documents",
            data_schema=self.add_suggested_values_to_schema(
                _documents_schema(), self._current
            ),
        )

    async def async_step_media(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Inlocuieste poza sau modelul 3D."""
        if user_input is not None:
            resolved = await _async_apply_media(
                self.hass, user_input, self._media_id
            )
            cleaned = _clean(resolved)
            drop = {
                key for key in (CONF_PHOTO, CONF_MODEL_3D) if key not in cleaned
            }
            return await self._async_save(cleaned, drop)

        suggested = {
            CONF_PHOTO: self._current.get(CONF_PHOTO),
            CONF_MODEL_3D: self._current.get(CONF_MODEL_3D),
        }
        return self.async_show_form(
            step_id="media",
            data_schema=self.add_suggested_values_to_schema(
                _media_schema(), suggested
            ),
            description_placeholders={
                "photo": self._current.get(CONF_PHOTO) or "-",
                "model_3d": self._current.get(CONF_MODEL_3D) or "-",
            },
        )

    async def async_step_mileage_source(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Alege senzorul din care se preia automat kilometrajul."""
        errors: dict[str, str] = {}
        if user_input is not None:
            source = user_input.get(CONF_MILEAGE_SOURCE)
            if not source:
                return await self._async_save({}, {CONF_MILEAGE_SOURCE})
            state = self.hass.states.get(source)
            usable = state is None or state.state in ("unknown", "unavailable")
            if not usable:
                from .mileage import mileage_from_state

                usable = mileage_from_state(state) is not None
            if usable:
                return await self._async_save({CONF_MILEAGE_SOURCE: source}, set())
            errors[CONF_MILEAGE_SOURCE] = "not_numeric"

        return self.async_show_form(
            step_id="mileage_source",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(
                    {
                        vol.Optional(CONF_MILEAGE_SOURCE): selector.EntitySelector(
                            selector.EntitySelectorConfig(
                                domain=["sensor", "number", "input_number"]
                            )
                        )
                    }
                ),
                user_input or self._current,
            ),
            errors=errors,
        )

    async def async_step_parking(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Telefonul si Bluetooth-ul masinii, pentru locul de parcare automat."""
        keys = (CONF_PARKING_TRACKER, CONF_PARKING_BT_SENSOR, CONF_PARKING_BT_DEVICE)
        errors: dict[str, str] = {}
        if user_input is not None:
            cleaned = {k: str(user_input[k]).strip() for k in keys if user_input.get(k)}
            if not cleaned:
                return await self._async_save({}, set(keys))
            if len(cleaned) == len(keys):
                return await self._async_save(cleaned, set())
            errors["base"] = "parking_incomplete"

        return self.async_show_form(
            step_id="parking",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(
                    {
                        vol.Optional(CONF_PARKING_TRACKER): selector.EntitySelector(
                            selector.EntitySelectorConfig(domain="device_tracker")
                        ),
                        vol.Optional(CONF_PARKING_BT_SENSOR): selector.EntitySelector(
                            selector.EntitySelectorConfig(domain="sensor")
                        ),
                        vol.Optional(CONF_PARKING_BT_DEVICE): selector.TextSelector(),
                    }
                ),
                user_input or self._current,
            ),
            errors=errors,
        )

    async def async_step_thresholds(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Editeaza pragurile de avertizare."""
        if user_input is not None:
            return await self._async_save(_clean(user_input), set())

        return self.async_show_form(
            step_id="thresholds",
            data_schema=self.add_suggested_values_to_schema(
                _thresholds_schema(), self._current
            ),
        )
