from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    COMMON_PROGRAMS,
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
    ("program", "Programa", PROGRAM_MAP, "mdi:format-list-bulleted", True),
    ("water_level", "Nível de água", WATER_LEVEL_MAP, "mdi:water", False),
    ("temperature", "Temperatura", TEMPERATURE_MAP, "mdi:thermometer", False),
    ("dehydration_speed", "Centrifugação", DEHYDRATION_SPEED_MAP, "mdi:rotate-right", False),
    ("mode", "Modo", MODE_MAP, "mdi:cog", False),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MideaWasherCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            WasherSelect(
                coordinator, entry, key, name, options_map, icon, filter_common
            )
            for key, name, options_map, icon, filter_common in _SELECTS
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
        icon: str,
        filter_common: bool,
    ) -> None:
        super().__init__(coordinator, entry, key, name)
        self._attr_icon = icon
        self._all_options = sorted(set(options_map.values()))
        self._filter_common = filter_common
        self._common = set(COMMON_PROGRAMS) if filter_common else set(self._all_options)

    @property
    def options(self) -> list[str]:
        current = self.current_option
        values = [o for o in self._all_options if o in self._common]
        if current and current not in values:
            values.append(current)
        return sorted(values)

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
        self.coordinator.async_set_updated_data(dict(self.coordinator.client.status))
