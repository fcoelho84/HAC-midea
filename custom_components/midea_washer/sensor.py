from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import MideaWasherCoordinator
from .entity import MideaWasherEntity

_SENSORS = (
    ("status", "Status", None, None, None),
    ("mode", "Mode", None, None, None),
    ("program", "Program", None, None, None),
    ("progress", "Progress", None, None, None),
    ("water_level", "Water Level", None, None, None),
    ("temperature", "Wash Temperature", None, None, None),
    ("dehydration_speed", "Spin Speed", None, None, None),
    ("wash_time", "Wash Time Level", None, SensorStateClass.MEASUREMENT, None),
    ("wash_time_value", "Wash Time Value", SensorDeviceClass.DURATION, SensorStateClass.MEASUREMENT, "min"),
    ("dehydration_time", "Spin Time Level", None, SensorStateClass.MEASUREMENT, None),
    ("dehydration_time_value", "Spin Time Value", SensorDeviceClass.DURATION, SensorStateClass.MEASUREMENT, "min"),
    ("time_remaining", "Time Remaining", SensorDeviceClass.DURATION, SensorStateClass.MEASUREMENT, "min"),
    ("detergent", "Detergent", None, SensorStateClass.MEASUREMENT, None),
    ("softener", "Softener", None, SensorStateClass.MEASUREMENT, None),
    ("stains", "Stains", None, SensorStateClass.MEASUREMENT, None),
    ("dirty_degree", "Dirty Degree", None, SensorStateClass.MEASUREMENT, None),
    ("washing_data_hex", "Washing Data", None, None, None),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MideaWasherCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        WasherSensor(
            coordinator,
            entry,
            key,
            name,
            device_class,
            state_class,
            unit,
            diagnostic=(key == "washing_data_hex"),
        )
        for key, name, device_class, state_class, unit in _SENSORS
    ]
    async_add_entities(entities)


class WasherSensor(MideaWasherEntity, SensorEntity):
    def __init__(
        self,
        coordinator: MideaWasherCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        device_class,
        state_class,
        unit,
        diagnostic: bool = False,
    ) -> None:
        super().__init__(coordinator, entry, key, name)
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = unit
        if diagnostic:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)
