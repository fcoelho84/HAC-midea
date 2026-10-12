"""Create long-lived LAN washer devices via midealan (midea_ac_lan stack)."""

from __future__ import annotations

import logging
from typing import Any

from midealan.device import ProtocolVersion
from midealan.devices import device_selector

_LOGGER = logging.getLogger(__name__)


def create_device(
    *,
    name: str,
    device_id: int,
    device_type: int,
    ip_address: str,
    port: int,
    token: str,
    key: str,
    protocol: int,
    model: str = "",
    subtype: int = 0,
    customize: str = "",
) -> Any:
    """Build washer/dryer device; call `.open()` to start TCP thread."""
    protocol_version = ProtocolVersion(protocol)
    device = device_selector(
        name=name,
        device_id=device_id,
        device_type=device_type,
        ip_address=ip_address,
        port=port,
        token=token or "",
        key=key or "",
        device_protocol=protocol_version,
        model=model or "",
        subtype=subtype,
        customize=customize or "",
    )
    if device is None:
        raise ValueError(f"unsupported device type {device_type:#x}")
    _LOGGER.debug(
        "created midealan device id=%s type=%#x ip=%s protocol=%s",
        device_id,
        device_type,
        ip_address,
        protocol,
    )
    return device
