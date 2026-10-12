from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_ACCOUNT,
    CONF_DEVICE_ID,
    CONF_DEVICE_TYPE,
    CONF_HOST,
    CONF_KEY,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_PROTOCOL,
    CONF_TOKEN,
    DOMAIN,
    SCAN_INTERVAL_SECONDS,
)
from .protocol import WasherClient
from .protocol.cloud import MSmartHomeCloud

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
        self.entry = entry
        self.client = WasherClient(
            device_id=int(data[CONF_DEVICE_ID]),
            device_type=int(data[CONF_DEVICE_TYPE]),
            host=data[CONF_HOST],
            port=int(data.get(CONF_PORT, 6444)),
            protocol=int(data.get(CONF_PROTOCOL, 3)),
            token=data.get(CONF_TOKEN, ""),
            key=data.get(CONF_KEY, ""),
        )

    async def _async_update_data(self):
        try:
            return await self.hass.async_add_executor_job(self._refresh)
        except ValueError as err:
            if "handshake" in str(err).lower() or "token" in str(err).lower():
                if await self._async_refresh_keys():
                    return await self.hass.async_add_executor_job(self._refresh)
            raise UpdateFailed(str(err)) from err
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

    async def _async_refresh_keys(self) -> bool:
        account = self.entry.data.get(CONF_ACCOUNT)
        password = self.entry.data.get(CONF_PASSWORD)
        if not account or not password:
            return False
        session = async_get_clientsession(self.hass)
        cloud = MSmartHomeCloud(session, account, password)
        if not await cloud.login():
            _LOGGER.warning("cloud re-login failed")
            return False
        keys = await cloud.get_token_key(int(self.entry.data[CONF_DEVICE_ID]))
        if keys is None:
            _LOGGER.warning("cloud token refresh failed")
            return False
        token, key = keys
        self.hass.config_entries.async_update_entry(
            self.entry,
            data={**self.entry.data, CONF_TOKEN: token, CONF_KEY: key},
        )
        self.client.close()
        self.client = WasherClient(
            device_id=int(self.entry.data[CONF_DEVICE_ID]),
            device_type=int(self.entry.data[CONF_DEVICE_TYPE]),
            host=self.entry.data[CONF_HOST],
            port=int(self.entry.data.get(CONF_PORT, 6444)),
            protocol=int(self.entry.data.get(CONF_PROTOCOL, 3)),
            token=token,
            key=key,
        )
        return True
