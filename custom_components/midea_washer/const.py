from homeassistant.const import Platform

DOMAIN = "midea_washer"
PLATFORMS = [Platform.SENSOR]

CONF_DEVICE_ID = "device_id"
CONF_DEVICE_TYPE = "device_type"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_PROTOCOL = "protocol"
CONF_TOKEN = "token"
CONF_KEY = "key"
CONF_MODEL = "model"
CONF_ACCOUNT = "account"
CONF_PASSWORD = "password"
CONF_NAME = "name"
CONF_SUBTYPE = "subtype"

DEFAULT_PORT = 6444
DEFAULT_PROTOCOL = 3
DEFAULT_REFRESH_INTERVAL = 30

DEVICE_TYPE_TOP_LOAD = 0xDA
DEVICE_TYPE_FRONT_LOAD = 0xDB
DEVICE_TYPE_DRYER = 0xDC

WASHER_TYPES = {
    DEVICE_TYPE_TOP_LOAD: "Top Load Washer",
    DEVICE_TYPE_FRONT_LOAD: "Front Load Washer",
    DEVICE_TYPE_DRYER: "Clothes Dryer",
}

SENSOR_SKIP = frozenset({"washing_data"})

# Primary sensors stay on the main device card.
PRIMARY_SENSORS = frozenset(
    {
        "time_remaining",
        "status",
        "progress",
        "program",
    }
)

SENSOR_LABELS: dict[str, tuple[str, str]] = {
    "power": ("Energia", "mdi:power"),
    "start": ("Em ciclo", "mdi:play-pause"),
    "status": ("Status", "mdi:information-outline"),
    "mode": ("Modo", "mdi:cog-outline"),
    "program": ("Programa", "mdi:washing-machine"),
    "progress": ("Etapa", "mdi:rotate-360"),
    "water_level": ("Nível de água", "mdi:cup-water"),
    "temperature": ("Temperatura", "mdi:thermometer"),
    "dry_temperature": ("Temperatura secagem", "mdi:thermometer"),
    "dehydration_speed": ("Centrifugação", "mdi:speedometer"),
    "wash_time": ("Tempo lavagem (nível)", "mdi:timer-outline"),
    "wash_time_value": ("Tempo lavagem", "mdi:timer"),
    "soak_time": ("Tempo de molho", "mdi:timer-outline"),
    "dehydration_time": ("Tempo centrifugação (nível)", "mdi:timer-outline"),
    "dehydration_time_value": ("Tempo centrifugação", "mdi:timer"),
    "time_remaining": ("Tempo restante", "mdi:progress-clock"),
    "detergent": ("Detergente", "mdi:spray-bottle"),
    "softener": ("Amaciante", "mdi:tshirt-crew"),
    "stains": ("Manchas", "mdi:blot"),
    "dirty_degree": ("Sujeira", "mdi:gauge"),
    "error_code": ("Código de erro", "mdi:alert-circle-outline"),
    "rinse_count": ("Enxágues", "mdi:counter"),
    "rinse_level": ("Nível enxágue", "mdi:waves"),
    "wash_level": ("Nível lavagem", "mdi:waves"),
    "wash_strength": ("Força lavagem", "mdi:arm-flex"),
    "intensity": ("Intensidade", "mdi:speedometer"),
    "dryness_level": ("Nível secagem", "mdi:weather-sunny"),
    "door_warn": ("Porta", "mdi:door"),
    "ai_switch": ("IA", "mdi:robot"),
    "material": ("Material", "mdi:texture-box"),
    "water_box": ("Caixa d'água", "mdi:cup-water"),
}

# Minutes as number + unit (same as midea_ac_lan). No DURATION class.
MINUTE_KEYS = frozenset(
    {
        "time_remaining",
        "wash_time_value",
        "soak_time",
        "dehydration_time_value",
    }
)
