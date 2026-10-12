from enum import IntEnum

from ..const import (
    DEHYDRATION_SPEED_MAP,
    MODE_MAP,
    PROGRAM_MAP,
    PROGRESS_LABELS,
    STATUS_MAP,
    TEMPERATURE_MAP,
    WASH_IDX_DEHYDRATION_SPEED,
    WASH_IDX_DEHYDRATION_TIME,
    WASH_IDX_DETERGENT,
    WASH_IDX_MODE,
    WASH_IDX_PROGRAM,
    WASH_IDX_SOFTENER,
    WASH_IDX_TEMPERATURE,
    WASH_IDX_WASH_TIME,
    WASH_IDX_WATER_LEVEL,
    WATER_LEVEL_MAP,
)
from .packet import build_uart_frame


class MessageType(IntEnum):
    SET = 0x02
    QUERY = 0x03
    NOTIFY1 = 0x04


def _label(mapping: dict[int, str], value: int) -> str:
    return mapping.get(value, f"unknown_{value}")


def _reverse(mapping: dict[int, str], label: str) -> int | None:
    for key, name in mapping.items():
        if name == label:
            return key
    return None


def query_message(device_type: int, protocol_version: int) -> bytes:
    return build_uart_frame(
        device_type=device_type,
        protocol_version=protocol_version,
        message_type=MessageType.QUERY,
        body=bytes([0x03]),
    )


def power_message(device_type: int, protocol_version: int, power: bool) -> bytes:
    body = bytes([0x02, 0x01 if power else 0x00]) + bytes([0xFF] * 20)
    return build_uart_frame(
        device_type=device_type,
        protocol_version=protocol_version,
        message_type=MessageType.SET,
        body=body,
    )


def start_message(
    device_type: int,
    protocol_version: int,
    start: bool,
    washing_data: bytes,
) -> bytes:
    if start:
        body = bytes([0x02, 0xFF, 0x01]) + bytes(washing_data)
    else:
        body = bytes([0x02, 0xFF, 0x00])
    return build_uart_frame(
        device_type=device_type,
        protocol_version=protocol_version,
        message_type=MessageType.SET,
        body=body,
    )


def washing_params_message(
    device_type: int,
    protocol_version: int,
    washing_data: bytes,
) -> bytes:
    """Push cycle params without forcing start/pause."""
    padded = bytearray(washing_data)
    if len(padded) < 13:
        padded.extend([0xFF] * (13 - len(padded)))
    body = bytes([0x02, 0xFF, 0xFF]) + bytes(padded[:13])
    return build_uart_frame(
        device_type=device_type,
        protocol_version=protocol_version,
        message_type=MessageType.SET,
        body=body,
    )


def parse_washer_status(frame: bytes) -> dict:
    if len(frame) < 12:
        return {}
    body = frame[10:-1] if len(frame) > 11 else frame[10:]
    if len(body) < 19:
        return {}

    status_code = body[2]
    mode_code = body[3]
    program_code = body[4]
    water_level_code = body[5]
    temperature_code = body[7]
    dehydration_speed_code = body[8]
    wash_time = body[9]
    dehydration_time = body[10]
    detergent = body[11]
    softener = body[12]
    washing_data = bytes(body[3:16])

    progress_idx = 0
    for i in range(0, 7):
        if body[16] & (1 << i):
            progress_idx = i + 1
            break
    if progress_idx >= len(PROGRESS_LABELS):
        progress_idx = len(PROGRESS_LABELS) - 1

    power = body[1] > 0
    time_remaining = None
    if power:
        time_remaining = body[17] + (body[18] << 8)

    stains = body[26] if len(body) > 26 else None
    wash_time_value = body[27] if len(body) > 27 else None
    dehydration_time_value = body[28] if len(body) > 28 else None
    dirty_degree = body[30] if len(body) > 30 else None

    return {
        "power": power,
        "start": status_code in (2, 6),
        "status_code": status_code,
        "status": _label(STATUS_MAP, status_code),
        "mode_code": mode_code,
        "mode": _label(MODE_MAP, mode_code),
        "program_code": program_code,
        "program": _label(PROGRAM_MAP, program_code),
        "water_level_code": water_level_code,
        "water_level": _label(WATER_LEVEL_MAP, water_level_code),
        "temperature_code": temperature_code,
        "temperature": _label(TEMPERATURE_MAP, temperature_code),
        "dehydration_speed_code": dehydration_speed_code,
        "dehydration_speed": _label(DEHYDRATION_SPEED_MAP, dehydration_speed_code),
        "wash_time": wash_time,
        "dehydration_time": dehydration_time,
        "detergent": detergent,
        "softener": softener,
        "washing_data": washing_data,
        "washing_data_hex": washing_data.hex(),
        "progress": PROGRESS_LABELS[progress_idx],
        "progress_index": progress_idx,
        "time_remaining": time_remaining,
        "stains": stains,
        "wash_time_value": wash_time_value,
        "dehydration_time_value": dehydration_time_value,
        "dirty_degree": dirty_degree,
    }


def patch_washing_data(current: bytes, index: int, value: int) -> bytes:
    data = bytearray(current if current else bytes([0xFF] * 13))
    if len(data) < 13:
        data.extend([0xFF] * (13 - len(data)))
    data[index] = value & 0xFF
    return bytes(data[:13])


def code_for_select(attr: str, option: str) -> int | None:
    maps = {
        "mode": MODE_MAP,
        "program": PROGRAM_MAP,
        "water_level": WATER_LEVEL_MAP,
        "temperature": TEMPERATURE_MAP,
        "dehydration_speed": DEHYDRATION_SPEED_MAP,
    }
    mapping = maps.get(attr)
    if mapping is None:
        return None
    return _reverse(mapping, option)


def wash_index_for_attr(attr: str) -> int | None:
    return {
        "mode": WASH_IDX_MODE,
        "program": WASH_IDX_PROGRAM,
        "water_level": WASH_IDX_WATER_LEVEL,
        "temperature": WASH_IDX_TEMPERATURE,
        "dehydration_speed": WASH_IDX_DEHYDRATION_SPEED,
        "wash_time": WASH_IDX_WASH_TIME,
        "dehydration_time": WASH_IDX_DEHYDRATION_TIME,
        "detergent": WASH_IDX_DETERGENT,
        "softener": WASH_IDX_SOFTENER,
    }.get(attr)
