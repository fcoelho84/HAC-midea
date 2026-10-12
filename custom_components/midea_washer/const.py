DOMAIN = "midea_washer"
PLATFORMS = ["sensor", "switch", "select", "number"]

CONF_DEVICE_ID = "device_id"
CONF_DEVICE_TYPE = "device_type"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_PROTOCOL = "protocol"
CONF_TOKEN = "token"
CONF_KEY = "key"
CONF_MODEL = "model"

DEFAULT_PORT = 6444
DEFAULT_PROTOCOL = 3
SCAN_INTERVAL_SECONDS = 15

DEVICE_TYPE_TOP_LOAD = 0xDA
DEVICE_TYPE_FRONT_LOAD = 0xDB
DEVICE_TYPE_DRYER = 0xDC

WASHER_TYPES = {
    DEVICE_TYPE_TOP_LOAD: "Top Load Washer",
    DEVICE_TYPE_FRONT_LOAD: "Front Load Washer",
    DEVICE_TYPE_DRYER: "Clothes Dryer",
}

OEM_COMMON_AES_KEY_HEX = "f526b03e0b591a6eeddf4fe77b9517fa"
LAN_SIGN_KEY = b"xhdiwjnchekd4d512chdjx5d8e4c394D2D7S"

STATUS_MAP = {
    0: "idle",
    1: "standby",
    2: "start",
    3: "pause",
    4: "end",
    5: "fault",
    6: "delay",
}

MODE_MAP = {
    0: "normal",
    1: "factory_test",
    2: "service",
    3: "normal_continus",
}

WATER_LEVEL_MAP = {
    0x01: "low",
    0x02: "mid",
    0x03: "high",
    0x04: "4",
    0x05: "auto",
    0xFF: "default",
}

DEHYDRATION_SPEED_MAP = {
    0x00: "0",
    0x01: "400",
    0x02: "600",
    0x03: "800",
    0x04: "1000",
    0x05: "1200",
    0x06: "1400",
    0x07: "1600",
    0x08: "1300",
    0xFF: "default",
}

TEMPERATURE_MAP = {
    0x01: "0",
    0x02: "20",
    0x03: "30",
    0x04: "40",
    0x05: "60",
    0x06: "95",
    0x07: "70",
    0xFF: "default",
}

PROGRESS_LABELS = (
    "idle",
    "spin",
    "rinse",
    "wash",
    "pre_wash",
    "dry",
    "weight",
    "hi_speed_spin",
    "unknown",
)

PROGRAM_MAP = {
    0x00: "cotton",
    0x01: "eco",
    0x02: "fast_wash",
    0x03: "mixed_wash",
    0x04: "fiber",
    0x05: "wool",
    0x06: "enzyme",
    0x07: "ssp",
    0x08: "sport_clothes",
    0x09: "single_dehydration",
    0x0A: "rinsing_dehydration",
    0x0B: "big",
    0x0C: "baby_clothes",
    0x0D: "outdoor",
    0x0E: "air_wash",
    0x0F: "down_jacket",
    0x10: "color",
    0x11: "intelligent",
    0x12: "quick_wash",
    0x13: "kids",
    0x14: "water_cotton",
    0x15: "single_drying",
    0x16: "single_drying_alt",
    0x17: "fast_wash_30",
    0x18: "fast_wash_60",
    0x19: "water_intelligent",
    0x1A: "water_steep",
    0x1B: "water_fast_wash_30",
    0x1C: "shirt",
    0x1D: "steep",
    0x1E: "new_water_cotton",
    0x1F: "water_mixed_wash",
    0x20: "water_fiber",
    0x21: "water_kids",
    0x22: "water_underwear",
    0x23: "specialist",
    0x24: "water_eco",
    0x25: "wash_drying_60",
    0x26: "self_wash_5",
    0x27: "fast_wash_min",
    0x28: "mixed_wash_min",
    0x29: "dehydration_min",
    0x2A: "self_wash_min",
    0x2B: "baby_clothes_min",
    0x2C: "prevent_allergy",
    0x2D: "cold_wash",
    0x2E: "soft_wash",
    0x2F: "remove_mite_wash",
    0x30: "water_intense_wash",
    0x31: "fast_dry",
    0x32: "water_outdoor",
    0x33: "spring_autumn_wash",
    0x34: "summer_wash",
    0x35: "winter_wash",
    0x36: "jean",
    0x37: "new_clothes_wash",
    0x38: "silk",
    0x39: "insight_wash",
    0x3A: "fitness_clothes",
    0x3B: "mink",
    0x3C: "fresh_air",
    0x3D: "bucket_dry",
    0x3E: "jacket",
    0x3F: "bath_towel",
    0x40: "night_fresh_wash",
    0x50: "water_fiber_alt",
    0x51: "diy0",
    0x52: "diy2",
    0x60: "heart_wash",
    0x61: "water_cold_wash",
    0x62: "water_prevent_allergy",
    0x63: "water_remove_mite_wash",
    0x64: "water_ssp",
    0x65: "silk_wash",
    0x66: "standard",
    0x67: "green_wool",
    0x68: "cook_wash",
    0x69: "fresh_remove_wrinkle",
    0x6A: "steam_sterilize_wash",
    0x6B: "aromatherapy",
    0x6C: "eco_40_60",
    0x6D: "steam_care",
    0x6E: "allergy_care",
    0x70: "sterilize_wash",
    0x73: "bulky",
    0x80: "wash_and_dry",
    0x82: "time_dry",
    0xFE: "love",
    0xFF: "default",
}

# washing_data byte index within body[3:16]
WASH_IDX_MODE = 0
WASH_IDX_PROGRAM = 1
WASH_IDX_WATER_LEVEL = 2
WASH_IDX_TEMPERATURE = 4
WASH_IDX_DEHYDRATION_SPEED = 5
WASH_IDX_WASH_TIME = 6
WASH_IDX_DEHYDRATION_TIME = 7
WASH_IDX_DETERGENT = 8
WASH_IDX_SOFTENER = 9
