from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import MideaWasherCoordinator
from .entity import MideaWasherEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: MideaWasherCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            WasherBoolSwitch(coordinator, entry, "power", "Power", "set_power"),
            WasherBoolSwitch(coordinator, entry, "start", "Start", "set_start"),
        ]
    )


class WasherBoolSwitch(MideaWasherEntity, SwitchEntity):
    def __init__(
        self,
        coordinator: MideaWasherCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        method: str,
    ) -> None:
        super().__init__(coordinator, entry, key, name)
        self._method = method

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get(self._key))

    async def async_turn_on(self, **kwargs) -> None:
        await self.hass.async_add_executor_job(
            getattr(self.coordinator.client, self._method),
            True,
        )
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self.hass.async_add_executor_job(
            getattr(self.coordinator.client, self._method),
            False,
        )
        await self.coordinator.async_request_refresh()
