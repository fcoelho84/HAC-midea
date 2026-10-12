from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_ACCOUNT,
    CONF_DEVICE_ID,
    CONF_DEVICE_TYPE,
    CONF_KEY,
    CONF_MODEL,
    CONF_PROTOCOL,
    CONF_TOKEN,
    DEFAULT_PORT,
    DEFAULT_PROTOCOL,
    DOMAIN,
    WASHER_TYPES,
)
from .protocol import WasherClient, discover
from .protocol.cloud import MSmartHomeCloud


class MideaWasherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    def __init__(self) -> None:
        self._cloud: MSmartHomeCloud | None = None
        self._washers: dict[int, dict[str, Any]] = {}
        self._account = ""
        self._password = ""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            cloud = MSmartHomeCloud(
                session,
                user_input[CONF_USERNAME].strip(),
                user_input[CONF_PASSWORD],
            )
            ok = await cloud.login()
            if not ok:
                errors["base"] = "invalid_auth"
            else:
                washers = await cloud.list_washers()
                if not washers:
                    return self.async_abort(reason="no_washers_in_account")
                self._cloud = cloud
                self._washers = washers
                self._account = user_input[CONF_USERNAME].strip()
                self._password = user_input[CONF_PASSWORD]
                return await self.async_step_select_device()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
            description_placeholders={"app": "MSmartHome / SmartHome"},
        )

    async def async_step_select_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        options = {
            str(device_id): (
                f"{info['name']} · "
                f"{WASHER_TYPES.get(info['device_type'], hex(info['device_type']))} · "
                f"{info.get('model') or '—'}"
            )
            for device_id, info in self._washers.items()
        }
        if user_input is None:
            return self.async_show_form(
                step_id="select_device",
                data_schema=vol.Schema(
                    {vol.Required(CONF_DEVICE_ID): vol.In(options)}
                ),
            )

        device_id = int(user_input[CONF_DEVICE_ID])
        info = self._washers[device_id]
        await self.async_set_unique_id(str(device_id))
        self._abort_if_unique_id_configured()

        assert self._cloud is not None
        keys = await self._cloud.get_token_key(device_id)
        if keys is None:
            return self.async_abort(reason="token_failed")
        token, key = keys

        lan = await self.hass.async_add_executor_job(discover)
        match = next((d for d in lan if int(d["device_id"]) == device_id), None)
        if match is None:
            self.context["auto"] = {
                CONF_DEVICE_ID: device_id,
                CONF_DEVICE_TYPE: info["device_type"],
                CONF_MODEL: info.get("model") or "",
                CONF_TOKEN: token,
                CONF_KEY: key,
                CONF_PROTOCOL: DEFAULT_PROTOCOL,
                CONF_PORT: DEFAULT_PORT,
                CONF_ACCOUNT: self._account,
                CONF_PASSWORD: self._password,
                "name": info["name"],
            }
            return await self.async_step_host()

        data = {
            CONF_HOST: match["host"],
            CONF_PORT: match.get("port", DEFAULT_PORT),
            CONF_DEVICE_ID: device_id,
            CONF_DEVICE_TYPE: info["device_type"],
            CONF_MODEL: info.get("model") or match.get("model") or "",
            CONF_PROTOCOL: match.get("protocol", DEFAULT_PROTOCOL),
            CONF_TOKEN: token,
            CONF_KEY: key,
            CONF_ACCOUNT: self._account,
            CONF_PASSWORD: self._password,
            "name": info["name"],
        }
        return await self._create_entry(data)

    async def async_step_host(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Only IP if LAN discovery missed the washer."""
        auto = self.context.get("auto") or {}
        errors: dict[str, str] = {}
        if user_input is not None:
            data = {**auto, CONF_HOST: user_input[CONF_HOST].strip()}
            return await self._create_entry(data)

        return self.async_show_form(
            step_id="host",
            data_schema=vol.Schema({vol.Required(CONF_HOST): str}),
            errors=errors,
            description_placeholders={
                "name": str(auto.get("name", "washer")),
                "device_id": str(auto.get(CONF_DEVICE_ID, "")),
            },
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
            self.context["auto"] = data
            return self.async_show_form(
                step_id="host",
                data_schema=vol.Schema(
                    {
                        vol.Required(
                            CONF_HOST, default=data.get(CONF_HOST, "")
                        ): str
                    }
                ),
                errors={"base": "cannot_connect"},
                description_placeholders={
                    "name": str(data.get("name", "washer")),
                    "device_id": str(data.get(CONF_DEVICE_ID, "")),
                },
            )
        finally:
            await self.hass.async_add_executor_job(client.close)

        title = data.get("name") or WASHER_TYPES.get(
            int(data[CONF_DEVICE_TYPE]), "Midea Washer"
        )
        return self.async_create_entry(
            title=f"{title} ({data[CONF_HOST]})",
            data=data,
        )
