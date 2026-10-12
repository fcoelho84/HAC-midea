from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, WASHER_TYPES

_LOGGER = logging.getLogger(__name__)


class MideaWasherEntity(Entity):
    """Push entity — same pattern as midea_ac_lan MideaEntity."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        device: Any,
        entry: ConfigEntry,
        key: str,
        name: str,
        icon: str | None = None,
    ) -> None:
        self._device = device
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}.{device.device_id}_{key}"
        if icon:
            self._attr_icon = icon
        device_type = int(entry.data["device_type"])
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(device.device_id))},
            name=entry.data.get("name")
            or f"{WASHER_TYPES.get(device_type, 'Washer')} {entry.data.get('host')}",
            manufacturer="Midea",
            model=entry.data.get("model")
            or WASHER_TYPES.get(device_type, "Washer"),
        )

    @property
    def available(self) -> bool:
        return bool(getattr(self._device, "available", True))

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._device.register_update(self.update_state)

    async def async_will_remove_from_hass(self) -> None:
        await super().async_will_remove_from_hass()
        unregister = getattr(self._device, "unregister_update", None)
        if unregister is not None:
            unregister(self.update_state)

    @callback
    def update_state(self, status: Any) -> None:
        if not self.hass:
            return
        if self._key not in status and "available" not in status:
            return
        if self.hass.is_stopping:
            return
        loop = getattr(self.hass, "loop", None)
        if loop is not None and loop.is_closed():
            return
        try:
            self.schedule_update_ha_state()
        except RuntimeError:
            if loop is not None and not loop.is_closed():
                raise
            _LOGGER.debug("Ignoring update for %s during shutdown", self.name)
