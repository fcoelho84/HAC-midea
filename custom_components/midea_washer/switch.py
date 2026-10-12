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
            WasherPowerSwitch(coordinator, entry),
            WasherRunningSwitch(coordinator, entry),
        ]
    )


class WasherPowerSwitch(MideaWasherEntity, SwitchEntity):
    _attr_icon = "mdi:washing-machine"

    def __init__(self, coordinator: MideaWasherCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "power", "Energia")

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get("power"))

    async def async_turn_on(self, **kwargs) -> None:
        await self.hass.async_add_executor_job(self.coordinator.client.set_power, True)
        self.coordinator.async_set_updated_data(dict(self.coordinator.client.status))

    async def async_turn_off(self, **kwargs) -> None:
        await self.hass.async_add_executor_job(self.coordinator.client.set_power, False)
        self.coordinator.async_set_updated_data(dict(self.coordinator.client.status))


class WasherRunningSwitch(MideaWasherEntity, SwitchEntity):
    _attr_icon = "mdi:play-pause"

    def __init__(self, coordinator: MideaWasherCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry, "start", "Ciclo em andamento")

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get("start"))

    async def async_turn_on(self, **kwargs) -> None:
        await self.hass.async_add_executor_job(self.coordinator.client.set_start, True)
        self.coordinator.async_set_updated_data(dict(self.coordinator.client.status))

    async def async_turn_off(self, **kwargs) -> None:
        await self.hass.async_add_executor_job(self.coordinator.client.set_start, False)
        self.coordinator.async_set_updated_data(dict(self.coordinator.client.status))
