from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MINUTE_KEYS, PRIMARY_SENSORS, SENSOR_LABELS, SENSOR_SKIP
from .entity import MideaWasherEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    device = hass.data[DOMAIN][entry.entry_id]["device"]
    entities: list[WasherSensor] = []
    for key in device.attributes:
        attr = str(key)
        if attr in SENSOR_SKIP:
            continue
        name, icon = SENSOR_LABELS.get(attr, (attr.replace("_", " ").title(), "mdi:eye"))
        entities.append(WasherSensor(device, entry, attr, name, icon))
    async_add_entities(entities)


class WasherSensor(MideaWasherEntity, SensorEntity):
    def __init__(
        self,
        device: Any,
        entry: ConfigEntry,
        key: str,
        name: str,
        icon: str,
    ) -> None:
        super().__init__(device, entry, key, name, icon)
        if key not in PRIMARY_SENSORS:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        if key in MINUTE_KEYS:
            self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> Any:
        value = self._device.get_attribute(self._key)
        if self._key not in MINUTE_KEYS:
            return value
        if value is None:
            return None
        try:
            return max(0, int(value))
        except (TypeError, ValueError):
            return None
