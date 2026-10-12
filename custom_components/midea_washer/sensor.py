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

# Controles principais ficam em switch/select/button.
# Aqui só status de leitura + extras.
_SENSORS = (
    ("status", "Status", "mdi:information", None, None, None, False),
    ("progress", "Etapa do ciclo", "mdi:progress-helper", None, None, None, False),
    ("time_remaining", "Tempo restante", "mdi:timer-sand", SensorDeviceClass.DURATION, SensorStateClass.MEASUREMENT, "min", False),
    ("wash_time_value", "Tempo de lavagem", "mdi:timer", SensorDeviceClass.DURATION, SensorStateClass.MEASUREMENT, "min", False),
    ("dehydration_time_value", "Tempo de centrifugação", "mdi:timer", SensorDeviceClass.DURATION, SensorStateClass.MEASUREMENT, "min", False),
    ("detergent", "Detergente", "mdi:bottle-tonic", None, SensorStateClass.MEASUREMENT, None, False),
    ("softener", "Amaciante", "mdi:bottle-tonic-outline", None, SensorStateClass.MEASUREMENT, None, False),
    ("stains", "Manchas", "mdi:blot", None, SensorStateClass.MEASUREMENT, None, True),
    ("dirty_degree", "Sujeira", "mdi:gauge", None, SensorStateClass.MEASUREMENT, None, True),
    ("wash_time", "Nível tempo lavagem", "mdi:numeric", None, SensorStateClass.MEASUREMENT, None, True),
    ("dehydration_time", "Nível tempo centrifugação", "mdi:numeric", None, SensorStateClass.MEASUREMENT, None, True),
    ("washing_data_hex", "Dados brutos do ciclo", "mdi:hexadecimal", None, None, None, True),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MideaWasherCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            WasherSensor(
                coordinator,
                entry,
                key,
                name,
                icon,
                device_class,
                state_class,
                unit,
                diagnostic,
            )
            for key, name, icon, device_class, state_class, unit, diagnostic in _SENSORS
        ]
    )


class WasherSensor(MideaWasherEntity, SensorEntity):
    def __init__(
        self,
        coordinator: MideaWasherCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        icon: str,
        device_class,
        state_class,
        unit,
        diagnostic: bool = False,
    ) -> None:
        super().__init__(coordinator, entry, key, name)
        self._attr_icon = icon
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_native_unit_of_measurement = unit
        if diagnostic:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)
