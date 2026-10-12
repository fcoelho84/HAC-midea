from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_DEVICE_ID,
    CONF_DEVICE_TYPE,
    CONF_HOST,
    CONF_KEY,
    CONF_PORT,
    CONF_PROTOCOL,
    CONF_TOKEN,
    DOMAIN,
    SCAN_INTERVAL_SECONDS,
)
from .protocol import WasherClient

_LOGGER = logging.getLogger(__name__)


class MideaWasherCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL_SECONDS),
        )
        data = entry.data
        self.client = WasherClient(
            device_id=int(data[CONF_DEVICE_ID]),
            device_type=int(data[CONF_DEVICE_TYPE]),
            host=data[CONF_HOST],
            port=int(data.get(CONF_PORT, 6444)),
            protocol=int(data.get(CONF_PROTOCOL, 3)),
            token=data.get(CONF_TOKEN, ""),
            key=data.get(CONF_KEY, ""),
        )
        self.entry = entry

    async def _async_update_data(self):
        try:
            return await self.hass.async_add_executor_job(self._refresh)
        except Exception as err:
            raise UpdateFailed(str(err)) from err

    def _refresh(self):
        if not self.client.connected:
            self.client.connect()
            return self.client.status
        try:
            return self.client.refresh()
        except OSError:
            self.client.connect()
            return self.client.status
