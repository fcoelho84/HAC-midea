"""Midea Washer LAN — thin HA glue over midealan long TCP (midea_ac_lan pattern)."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import Event, HomeAssistant

from .const import (
    CONF_DEVICE_ID,
    CONF_DEVICE_TYPE,
    CONF_HOST,
    CONF_KEY,
    CONF_MODEL,
    CONF_NAME,
    CONF_PORT,
    CONF_PROTOCOL,
    CONF_SUBTYPE,
    CONF_TOKEN,
    DEFAULT_PORT,
    DEFAULT_PROTOCOL,
    DEFAULT_REFRESH_INTERVAL,
    DOMAIN,
    PLATFORMS,
)
from .device import create_device

_LOGGER = logging.getLogger(__name__)


def _close_device(device: object) -> None:
    try:
        device.close()  # type: ignore[attr-defined]
    except (OSError, ConnectionError, AttributeError) as err:
        _LOGGER.warning("Failed to close Midea socket cleanly: %s", err)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    data = entry.data
    device_id = int(data[CONF_DEVICE_ID])
    name = data.get(CONF_NAME) or f"Washer {device_id}"
    device = await hass.async_add_executor_job(
        lambda: create_device(
            name=name,
            device_id=device_id,
            device_type=int(data[CONF_DEVICE_TYPE]),
            ip_address=data[CONF_HOST],
            port=int(data.get(CONF_PORT, DEFAULT_PORT)),
            token=data.get(CONF_TOKEN, "") or "",
            key=data.get(CONF_KEY, "") or "",
            protocol=int(data.get(CONF_PROTOCOL, DEFAULT_PROTOCOL)),
            model=data.get(CONF_MODEL, "") or "",
            subtype=int(data.get(CONF_SUBTYPE, 0) or 0),
        )
    )
    refresh = entry.options.get("refresh_interval", DEFAULT_REFRESH_INTERVAL)
    if refresh is not None:
        device.set_refresh_interval(int(refresh))
    device.open()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "device": device,
        "entry": entry,
    }

    async def _on_stop(_event: Event) -> None:
        await hass.async_add_executor_job(_close_device, device)

    remove_stop = hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _on_stop)
    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except Exception:
        remove_stop()
        hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        await hass.async_add_executor_job(_close_device, device)
        raise

    entry.async_on_unload(remove_stop)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        stored = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        if stored and stored.get("device") is not None:
            await hass.async_add_executor_job(_close_device, stored["device"])
    return unload_ok
