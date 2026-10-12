from collections.abc import Callable

from homeassistant.components.button import ButtonEntity
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
            WasherButton(
                coordinator,
                entry,
                "btn_power_on",
                "Ligar",
                "mdi:power",
                lambda c: c.set_power(True),
            ),
            WasherButton(
                coordinator,
                entry,
                "btn_power_off",
                "Desligar",
                "mdi:power-off",
                lambda c: c.set_power(False),
            ),
            WasherButton(
                coordinator,
                entry,
                "btn_start",
                "Iniciar",
                "mdi:play",
                lambda c: c.set_start(True),
            ),
            WasherButton(
                coordinator,
                entry,
                "btn_pause",
                "Pausar",
                "mdi:pause",
                lambda c: c.set_start(False),
            ),
            WasherButton(
                coordinator,
                entry,
                "btn_refresh",
                "Atualizar status",
                "mdi:refresh",
                lambda c: c.refresh(),
            ),
        ]
    )


class WasherButton(MideaWasherEntity, ButtonEntity):
    def __init__(
        self,
        coordinator: MideaWasherCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        icon: str,
        action: Callable,
    ) -> None:
        super().__init__(coordinator, entry, key, name)
        self._attr_icon = icon
        self._action = action

    async def async_press(self) -> None:
        await self.hass.async_add_executor_job(self._action, self.coordinator.client)
        await self.coordinator.async_request_refresh()
