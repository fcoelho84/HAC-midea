from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DEHYDRATION_SPEED_MAP,
    DOMAIN,
    MODE_MAP,
    PROGRAM_MAP,
    TEMPERATURE_MAP,
    WATER_LEVEL_MAP,
)
from .coordinator import MideaWasherCoordinator
from .entity import MideaWasherEntity

_SELECTS = (
    ("program", "Program", PROGRAM_MAP),
    ("mode", "Mode", MODE_MAP),
    ("water_level", "Water Level", WATER_LEVEL_MAP),
    ("temperature", "Wash Temperature", TEMPERATURE_MAP),
    ("dehydration_speed", "Spin Speed", DEHYDRATION_SPEED_MAP),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MideaWasherCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            WasherSelect(coordinator, entry, key, name, options_map)
            for key, name, options_map in _SELECTS
        ]
    )


class WasherSelect(MideaWasherEntity, SelectEntity):
    def __init__(
        self,
        coordinator: MideaWasherCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        options_map: dict[int, str],
    ) -> None:
        super().__init__(coordinator, entry, key, name)
        self._options = sorted(set(options_map.values()))
        self._attr_options = self._options

    @property
    def current_option(self) -> str | None:
        value = self.coordinator.data.get(self._key)
        if value is None:
            return None
        return str(value)

    async def async_select_option(self, option: str) -> None:
        await self.hass.async_add_executor_job(
            self.coordinator.client.set_select,
            self._key,
            option,
        )
        await self.coordinator.async_request_refresh()
