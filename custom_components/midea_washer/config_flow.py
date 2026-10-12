from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_DEVICE_ID,
    CONF_DEVICE_TYPE,
    CONF_KEY,
    CONF_MODEL,
    CONF_PROTOCOL,
    CONF_TOKEN,
    DEFAULT_PORT,
    DEFAULT_PROTOCOL,
    DEVICE_TYPE_FRONT_LOAD,
    DOMAIN,
    WASHER_TYPES,
)
from .protocol import WasherClient, discover


class MideaWasherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._discovered: list[dict[str, Any]] = []
        self._pending: dict[str, Any] | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        return self.async_show_menu(
            step_id="user",
            menu_options=["discover", "manual"],
        )

    async def async_step_discover(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is None:
            devices = await self.hass.async_add_executor_job(discover)
            washers = [d for d in devices if d.get("device_type") in WASHER_TYPES]
            self._discovered = washers
            if not washers:
                return self.async_abort(reason="no_devices_found")
            options = {
                str(d["device_id"]): (
                    f"{WASHER_TYPES.get(d['device_type'], hex(d['device_type']))} "
                    f"{d['host']} ({d['device_id']})"
                )
                for d in washers
            }
            return self.async_show_form(
                step_id="discover",
                data_schema=vol.Schema({vol.Required(CONF_DEVICE_ID): vol.In(options)}),
            )

        device_id = int(user_input[CONF_DEVICE_ID])
        device = next(d for d in self._discovered if d["device_id"] == device_id)
        await self.async_set_unique_id(str(device_id))
        self._abort_if_unique_id_configured()
        self._pending = {
            CONF_HOST: device["host"],
            CONF_PORT: device["port"],
            CONF_DEVICE_ID: device["device_id"],
            CONF_DEVICE_TYPE: device["device_type"],
            CONF_PROTOCOL: device["protocol"],
            CONF_MODEL: device.get("model", ""),
        }
        if int(device.get("protocol", 3)) != 3:
            return await self._create_entry(
                {
                    **self._pending,
                    CONF_TOKEN: "",
                    CONF_KEY: "",
                }
            )
        return await self.async_step_credentials()

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is None:
            return self.async_show_form(
                step_id="manual",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_HOST): str,
                        vol.Required(CONF_DEVICE_ID): int,
                        vol.Required(
                            CONF_DEVICE_TYPE, default=DEVICE_TYPE_FRONT_LOAD
                        ): vol.In(WASHER_TYPES),
                        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                        vol.Optional(CONF_PROTOCOL, default=DEFAULT_PROTOCOL): vol.In(
                            [2, 3]
                        ),
                        vol.Optional(CONF_MODEL, default=""): str,
                        vol.Optional(CONF_TOKEN, default=""): str,
                        vol.Optional(CONF_KEY, default=""): str,
                    }
                ),
            )
        await self.async_set_unique_id(str(user_input[CONF_DEVICE_ID]))
        self._abort_if_unique_id_configured()
        return await self._create_entry(user_input)

    async def async_step_credentials(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        pending = self._pending or {}
        if user_input is None:
            return self.async_show_form(
                step_id="credentials",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_TOKEN): str,
                        vol.Required(CONF_KEY): str,
                    }
                ),
                description_placeholders={
                    "host": str(pending.get(CONF_HOST, "")),
                    "device_id": str(pending.get(CONF_DEVICE_ID, "")),
                },
            )
        return await self._create_entry(
            {
                **pending,
                CONF_TOKEN: user_input[CONF_TOKEN],
                CONF_KEY: user_input[CONF_KEY],
            }
        )

    async def _create_entry(self, data: dict[str, Any]) -> FlowResult:
        client = WasherClient(
            device_id=int(data[CONF_DEVICE_ID]),
            device_type=int(data[CONF_DEVICE_TYPE]),
            host=data[CONF_HOST],
            port=int(data.get(CONF_PORT, DEFAULT_PORT)),
            protocol=int(data.get(CONF_PROTOCOL, DEFAULT_PROTOCOL)),
            token=data.get(CONF_TOKEN, ""),
            key=data.get(CONF_KEY, ""),
        )
        try:
            await self.hass.async_add_executor_job(client.connect)
        except Exception:
            return self.async_show_form(
                step_id="manual",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_HOST, default=data[CONF_HOST]): str,
                        vol.Required(CONF_DEVICE_ID, default=data[CONF_DEVICE_ID]): int,
                        vol.Required(
                            CONF_DEVICE_TYPE, default=data[CONF_DEVICE_TYPE]
                        ): vol.In(WASHER_TYPES),
                        vol.Optional(
                            CONF_PORT, default=data.get(CONF_PORT, DEFAULT_PORT)
                        ): int,
                        vol.Optional(
                            CONF_PROTOCOL,
                            default=data.get(CONF_PROTOCOL, DEFAULT_PROTOCOL),
                        ): vol.In([2, 3]),
                        vol.Optional(CONF_MODEL, default=data.get(CONF_MODEL, "")): str,
                        vol.Optional(CONF_TOKEN, default=data.get(CONF_TOKEN, "")): str,
                        vol.Optional(CONF_KEY, default=data.get(CONF_KEY, "")): str,
                    }
                ),
                errors={"base": "cannot_connect"},
            )
        finally:
            await self.hass.async_add_executor_job(client.close)

        title = WASHER_TYPES.get(int(data[CONF_DEVICE_TYPE]), "Midea Washer")
        return self.async_create_entry(
            title=f"{title} {data[CONF_HOST]}",
            data=data,
        )
