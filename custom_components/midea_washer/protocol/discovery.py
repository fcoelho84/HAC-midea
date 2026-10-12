import logging
import socket
from typing import Any

_LOGGER = logging.getLogger(__name__)

DISCOVERY_MSG = bytes(
    [
        0x5A,
        0x5A,
        0x01,
        0x11,
        0x48,
        0x00,
        0x92,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x7F,
        0x75,
        0xBD,
        0x6B,
        0x3E,
        0x4F,
        0x8B,
        0x76,
        0x2E,
        0x84,
        0x9B,
        0xE7,
        0xBD,
        0x9E,
        0x7C,
        0xD1,
        0x4D,
        0x7A,
        0xA5,
        0xE1,
        0x0A,
        0x1B,
        0x5A,
        0x7D,
        0xE6,
        0x3E,
        0x4F,
        0x8B,
        0x76,
        0x2E,
        0x84,
        0x9B,
    ]
)


def discover(timeout: float = 3.0) -> list[dict[str, Any]]:
    """UDP broadcast discovery on port 6445."""
    found: dict[int, dict[str, Any]] = {}
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)
    try:
        sock.sendto(DISCOVERY_MSG, ("255.255.255.255", 6445))
        while True:
            try:
                data, addr = sock.recvfrom(512)
            except socket.timeout:
                break
            device = _parse_discovery(data, addr[0])
            if device is None:
                continue
            found[device["device_id"]] = device
    finally:
        sock.close()
    return list(found.values())


def _parse_discovery(data: bytes, ip: str) -> dict[str, Any] | None:
    if len(data) < 40:
        return None
    if data[0] != 0x5A or data[1] != 0x5A:
        return None
    device_id = int.from_bytes(data[20:26], "little")
    if device_id == 0:
        device_id = int.from_bytes(data[20:28], "little")
    device_type = data[38] if len(data) > 38 else 0
    model = ""
    if len(data) >= 46:
        model = data[40:46].hex()
    protocol = 3 if len(data) >= 50 and data[8] != 0 else 2
    return {
        "device_id": device_id,
        "device_type": device_type,
        "host": ip,
        "port": 6444,
        "protocol": protocol,
        "model": model,
    }
