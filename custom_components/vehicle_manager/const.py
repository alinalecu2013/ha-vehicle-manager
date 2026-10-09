"""Constante pentru integrarea Vehicle Manager."""

from __future__ import annotations

from datetime import timedelta
from typing import Final

DOMAIN: Final = "vehicle_manager"
VERSION: Final = "2.0.1"

PLATFORMS: Final = [
    "sensor",
    "binary_sensor",
    "number",
    "date",
    "image",
    "calendar",
    "device_tracker",
]

UPDATE_INTERVAL: Final = timedelta(minutes=15)

# Resurse statice / frontend
URL_BASE: Final = "/vehicle_manager_files"
CARD_FILENAME: Final = "vehicle-manager-card.js"
# Depozitul HACS separat al cardului (instalat in config/www/community/<repo>)
HACS_CARD_REPO: Final = "vehicle-manager-card"
MEDIA_DIRNAME: Final = "vehicle_manager"

# --- Caracteristici vehicul ---
CONF_MAKE: Final = "make"
CONF_MODEL: Final = "model"
CONF_YEAR: Final = "year"
CONF_MILEAGE: Final = "mileage"
# Senzorul din care se preia automat kilometrajul (optional)
CONF_MILEAGE_SOURCE: Final = "mileage_source"
# Unde am parcat (vezi parking.py)
CONF_PARKING: Final = "parking"
CONF_PARKING_TRACKER: Final = "parking_tracker"
CONF_PARKING_BT_SENSOR: Final = "parking_bt_sensor"
CONF_PARKING_BT_DEVICE: Final = "parking_bt_device"
CONF_COLOR: Final = "color"
CONF_ENGINE_CAPACITY: Final = "engine_capacity"
CONF_FUEL_TYPE: Final = "fuel_type"
CONF_PLATE: Final = "license_plate"
CONF_VIN: Final = "vin"

# --- Media ---
CONF_PHOTO: Final = "photo"
CONF_PHOTO_UPLOAD: Final = "photo_upload"
CONF_MODEL_3D: Final = "model_3d"
CONF_MODEL_3D_UPLOAD: Final = "model_3d_upload"
CONF_MEDIA_ID: Final = "media_id"

# --- Praguri de avertizare ---
CONF_WARN_DAYS: Final = "warn_days"
CONF_WARN_KM: Final = "warn_km"
DEFAULT_WARN_DAYS: Final = 30
DEFAULT_WARN_KM: Final = 1000

# --- Documente ---
DOC_RCA: Final = "rca"
DOC_ITP: Final = "itp"
DOC_ROVINIETA: Final = "rovinieta"
DOC_REVIZIE: Final = "revizie"
DOC_DISTRIBUTIE: Final = "distributie"
DOC_CASCO: Final = "casco"
DOC_TRUSA: Final = "trusa_medicala"
DOC_EXTINCTOR: Final = "extinctor"
DOC_IMPOZIT: Final = "impozit"
DOC_ANVELOPE: Final = "anvelope"

DOCUMENTS: Final[dict[str, dict]] = {
    DOC_RCA: {
        "label": "RCA",
        "icon": "mdi:shield-car",
        "uses_km": False,
        "horizon": 365,
    },
    DOC_ITP: {
        "label": "ITP",
        "icon": "mdi:car-wrench",
        "uses_km": False,
        "horizon": 730,
    },
    DOC_ROVINIETA: {
        "label": "Rovinieta",
        "icon": "mdi:road-variant",
        "uses_km": False,
        "horizon": 365,
    },
    DOC_REVIZIE: {
        "label": "Revizie",
        "icon": "mdi:oil",
        "uses_km": True,
        "horizon": 365,
    },
    DOC_DISTRIBUTIE: {
        "label": "Distributie",
        "icon": "mdi:cog-sync",
        "uses_km": True,
        "horizon": 1825,
    },
    # Acte optionale: apar in card doar dupa ce au o data (sau daca sunt bifate).
    DOC_CASCO: {
        "label": "CASCO",
        "icon": "mdi:shield-star",
        "uses_km": False,
        "horizon": 365,
    },
    DOC_TRUSA: {
        "label": "Trusa medicala",
        "icon": "mdi:medical-bag",
        "uses_km": False,
        "horizon": 1095,
    },
    DOC_EXTINCTOR: {
        "label": "Extinctor",
        "icon": "mdi:fire-extinguisher",
        "uses_km": False,
        "horizon": 365,
    },
    DOC_IMPOZIT: {
        "label": "Impozit auto",
        "icon": "mdi:bank",
        "uses_km": False,
        "horizon": 365,
    },
    DOC_ANVELOPE: {
        "label": "Schimb anvelope",
        "icon": "mdi:tire",
        "uses_km": False,
        "horizon": 182,
    },
}


def date_key(doc: str) -> str:
    """Cheia din options pentru data unui document."""
    return f"{doc}_date"


def km_key(doc: str) -> str:
    """Cheia din options pentru kilometrajul scadent al unui document."""
    return f"{doc}_km"


# --- Combustibil ---
FUEL_TYPES: Final = [
    "benzina",
    "diesel",
    "gpl",
    "benzina_gpl",
    "hibrid",
    "hibrid_plugin",
    "electric",
    "altul",
]

FUEL_LABELS: Final = {
    "benzina": "Benzina",
    "diesel": "Diesel",
    "gpl": "GPL",
    "benzina_gpl": "Benzina + GPL",
    "hibrid": "Hibrid",
    "hibrid_plugin": "Hibrid plug-in",
    "electric": "Electric",
    "altul": "Altul",
}

FUEL_ICONS: Final = {
    "benzina": "mdi:gas-station",
    "diesel": "mdi:fuel",
    "gpl": "mdi:gas-cylinder",
    "benzina_gpl": "mdi:gas-cylinder",
    "hibrid": "mdi:car-electric",
    "hibrid_plugin": "mdi:car-electric-outline",
    "electric": "mdi:lightning-bolt",
    "altul": "mdi:help-circle-outline",
}

# --- Stari ---
STATUS_OK: Final = "ok"
STATUS_WARNING: Final = "warning"
STATUS_EXPIRED: Final = "expired"
STATUS_UNKNOWN: Final = "unknown"

STATUS_ORDER: Final = {
    STATUS_UNKNOWN: 0,
    STATUS_OK: 1,
    STATUS_WARNING: 2,
    STATUS_EXPIRED: 3,
}

# --- Culori (nume RO/EN -> hex) pentru modelul 3D ---
COLOR_HEX: Final = {
    "alb": "#eef1f4",
    "white": "#eef1f4",
    "negru": "#15181c",
    "black": "#15181c",
    "gri": "#7b8591",
    "grey": "#7b8591",
    "gray": "#7b8591",
    "argintiu": "#c3cad1",
    "silver": "#c3cad1",
    "rosu": "#c0392b",
    "red": "#c0392b",
    "bordo": "#6d1f2b",
    "albastru": "#1f5fbf",
    "blue": "#1f5fbf",
    "bleumarin": "#16255a",
    "verde": "#1f8b4c",
    "green": "#1f8b4c",
    "galben": "#f1c40f",
    "yellow": "#f1c40f",
    "portocaliu": "#e67e22",
    "orange": "#e67e22",
    "maro": "#6b4423",
    "brown": "#6b4423",
    "bej": "#d8c9a3",
    "beige": "#d8c9a3",
    "mov": "#7d3c98",
    "purple": "#7d3c98",
    "auriu": "#c9a227",
    "gold": "#c9a227",
}

DEFAULT_COLOR_HEX: Final = "#9aa4af"

# --- Servicii ---
SERVICE_SET_MILEAGE: Final = "set_mileage"
SERVICE_SET_DOCUMENT: Final = "set_document"
SERVICE_RENEW_DOCUMENT: Final = "renew_document"
SERVICE_MARK_SERVICE_DONE: Final = "mark_service_done"

ATTR_DOCUMENT: Final = "document"
ATTR_DATE: Final = "date"
ATTR_KM: Final = "km"
ATTR_MONTHS: Final = "months"
ATTR_INTERVAL_KM: Final = "interval_km"
ATTR_INTERVAL_MONTHS: Final = "interval_months"
ATTR_MILEAGE: Final = "mileage"

# --- Cheltuieli ---
SERVICE_ADD_EXPENSE: Final = "add_expense"
SERVICE_DELETE_EXPENSE: Final = "delete_expense"
SERVICE_SET_PARKING: Final = "set_parking"

ATTR_CATEGORY: Final = "category"
ATTR_AMOUNT: Final = "amount"
ATTR_NOTE: Final = "note"
ATTR_EXPENSE_ID: Final = "expense_id"
ATTR_COST: Final = "cost"
ATTR_QUANTITY: Final = "quantity"
ATTR_FULL_TANK: Final = "full_tank"

# Categoria cheltuielilor din care se calculeaza consumul
FUEL_CATEGORY: Final = "combustibil"

# Cheie -> (eticheta, iconita). Ordinea e cea din card si din selectoare.
EXPENSE_CATEGORIES: Final[dict[str, tuple[str, str]]] = {
    "rca": ("RCA", "mdi:shield-car"),
    "itp": ("ITP", "mdi:car-wrench"),
    "rovinieta": ("Rovinieta", "mdi:road-variant"),
    "casco": ("CASCO", "mdi:shield-star"),
    "revizie": ("Revizie", "mdi:oil"),
    "distributie": ("Distributie", "mdi:cog-sync"),
    "reparatii": ("Reparatii", "mdi:wrench"),
    "anvelope": ("Anvelope", "mdi:tire"),
    "combustibil": ("Combustibil", "mdi:gas-station"),
    "spalare": ("Spalare", "mdi:car-wash"),
    "parcare": ("Parcare", "mdi:parking"),
    "amenzi": ("Amenzi", "mdi:file-document-alert"),
    "taxe": ("Taxe si impozit", "mdi:bank"),
    "accesorii": ("Accesorii", "mdi:car-seat"),
    "altele": ("Altele", "mdi:dots-horizontal"),
}

# Categoria de cost pentru reinnoirea unui act, cand nu are o categorie proprie.
DOC_EXPENSE_CATEGORY: Final[dict[str, str]] = {
    "trusa_medicala": "accesorii",
    "extinctor": "accesorii",
    "impozit": "taxe",
}
