from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import MideaWasherCoordinator
from .entity import MideaWasherEntity

_NUMBERS = (
    ("wash_time", "Ajuste tempo lavagem", "mdi:timer-plus", 0, 30, 1),
    ("dehydration_time", "Ajuste tempo centrifugação", "mdi:timer-plus-outline", 0, 30, 1),
    ("detergent", "Ajuste detergente", "mdi:bottle-tonic-plus", 0, 5, 1),
    ("softener", "Ajuste amaciante", "mdi:bottle-tonic-plus-outline", 0, 5, 1),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MideaWasherCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            WasherNumber(coordinator, entry, key, name, icon, minimum, maximum, step)
            for key, name, icon, minimum, maximum, step in _NUMBERS
        ]
    )


class WasherNumber(MideaWasherEntity, NumberEntity):
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self,
        coordinator: MideaWasherCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        icon: str,
        minimum: float,
        maximum: float,
        step: float,
    ) -> None:
        super().__init__(coordinator, entry, key, name)
        self._attr_icon = icon
        self._attr_native_min_value = minimum
        self._attr_native_max_value = maximum
        self._attr_native_step = step

    @property
    def native_value(self) -> float | None:
        value = self.coordinator.data.get(self._key)
        if value is None:
            return None
        return float(value)

    async def async_set_native_value(self, value: float) -> None:
        await self.hass.async_add_executor_job(
            self.coordinator.client.set_number,
            self._key,
            int(value),
        )
        self.coordinator.async_set_updated_data(dict(self.coordinator.client.status))
