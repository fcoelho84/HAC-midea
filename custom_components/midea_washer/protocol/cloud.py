"""MSmartHome cloud client — login once, fetch LAN token/key."""

from __future__ import annotations

import base64
import datetime
import hmac
import json
import logging
import time
from hashlib import md5, sha256
from secrets import token_hex
from typing import Any

from aiohttp import ClientSession
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

_LOGGER = logging.getLogger(__name__)

APP_ID = "1010"
APP_KEY = "ac21b9f9cbfe4ca5a88562ef25e2b768"
IOT_KEY = "meicloud"
HMAC_KEY = "PROD_VnoClJI9aikS8dyy"
API_URL = "https://mp-prod.appsmb.com/mas/v5/app/proxy?alias="


def _device_id(account: str) -> str:
    return sha256(f"Hello, {account}!".encode("ascii")).hexdigest()[:16]


def _udp_id(appliance_id: int, method: int = 0) -> str:
    if method == 0:
        bytes_id = bytes(reversed(appliance_id.to_bytes(8, "big")))
    elif method == 1:
        bytes_id = appliance_id.to_bytes(6, "big")
    else:
        bytes_id = appliance_id.to_bytes(6, "little")
    data = bytearray(sha256(bytes_id).digest())
    for i in range(16):
        data[i] ^= data[i + 16]
    return data[:16].hex()


def _encrypt_password(login_id: str, password: str) -> str:
    digest = sha256(password.encode("ascii")).hexdigest()
    return sha256(f"{login_id}{digest}{APP_KEY}".encode("ascii")).hexdigest()


def _encrypt_iam_password(login_id: str, password: str) -> str:
    first = md5(password.encode("ascii")).hexdigest()
    second = md5(first.encode("ascii")).hexdigest()
    return sha256(f"{login_id}{second}{APP_KEY}".encode("ascii")).hexdigest()


def _sign(payload: str, random: str) -> str:
    msg = f"{IOT_KEY}{payload}{random}"
    return hmac.new(HMAC_KEY.encode("ascii"), msg.encode("ascii"), sha256).hexdigest()


def _aes_decrypt_hex(payload: str, key: bytes, iv: bytes) -> str:
    raw = bytes.fromhex(payload)
    return unpad(AES.new(key, AES.MODE_CBC, iv=iv).decrypt(raw), 16).decode()


class MSmartHomeCloud:
    def __init__(self, session: ClientSession, account: str, password: str) -> None:
        self._session = session
        self._account = account
        self._password = password
        self._device_id = _device_id(account)
        self._api_url = API_URL
        self._access_token: str | None = None
        self._uid: str | None = None
        self._login_id: str | None = None
        self._aes_key: bytes | None = None
        self._aes_iv: bytes | None = None
        self._auth_base = base64.b64encode(
            f"{APP_KEY}:{IOT_KEY}".encode("ascii")
        ).decode("ascii")

    def export_session(self) -> dict[str, str]:
        return {
            "account": self._account,
            "password": self._password,
            "access_token": self._access_token or "",
            "uid": self._uid or "",
            "login_id": self._login_id or "",
        }

    def _general(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "src": APP_ID,
            "format": "2",
            "stamp": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            "platformId": "1",
            "deviceId": self._device_id,
            "reqId": token_hex(16),
            "clientType": "1",
            "appId": APP_ID,
        }
        if self._uid is not None:
            data["uid"] = self._uid
        return data

    async def _request(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any] | None:
        if "reqId" not in data:
            data["reqId"] = token_hex(16)
        if "stamp" not in data:
            data["stamp"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        dump = json.dumps(data)
        random = str(int(time.time()))
        headers = {
            "content-type": "application/json; charset=utf-8",
            "secretVersion": "1",
            "sign": _sign(dump, random),
            "random": random,
            "x-recipe-app": APP_ID,
            "authorization": f"Basic {self._auth_base}",
        }
        if self._uid is not None:
            headers["uid"] = self._uid
        if self._access_token is not None:
            headers["accessToken"] = self._access_token
        url = self._api_url + endpoint
        try:
            async with self._session.post(
                url, headers=headers, data=dump, timeout=15
            ) as resp:
                raw = await resp.read()
        except Exception as err:
            _LOGGER.warning("cloud request failed %s: %s", endpoint, err)
            return None
        try:
            response = json.loads(raw)
        except json.JSONDecodeError:
            _LOGGER.warning("cloud bad json %s", endpoint)
            return None
        if int(response.get("code", -1)) != 0 or "data" not in response:
            _LOGGER.debug("cloud error %s: %s", endpoint, response)
            return None
        return response["data"]

    def _set_session_keys(self, access_token: str, random_data: str) -> None:
        digest = sha256(APP_KEY.encode("ascii")).hexdigest()
        tmp_key = digest[:16].encode("ascii")
        tmp_iv = digest[16:32].encode("ascii")
        self._aes_key = _aes_decrypt_hex(access_token, tmp_key, tmp_iv).encode("ascii")
        self._aes_iv = _aes_decrypt_hex(random_data, tmp_key, tmp_iv).encode("ascii")

    async def login(self) -> bool:
        route_data = self._general()
        route_data.update({"userType": "0", "userName": self._account})
        route = await self._request("/v1/multicloud/platform/user/route", route_data)
        if route and route.get("masUrl"):
            self._api_url = route["masUrl"]

        login_payload = self._general()
        login_payload["loginAccount"] = self._account
        login_id_resp = await self._request("/v1/user/login/id/get", login_payload)
        if not login_id_resp:
            return False
        self._login_id = login_id_resp.get("loginId")
        if not self._login_id:
            return False

        stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        iot_data = self._general()
        iot_data.pop("uid", None)
        iot_data.update(
            {
                "iampwd": _encrypt_iam_password(self._login_id, self._password),
                "loginAccount": self._account,
                "password": _encrypt_password(self._login_id, self._password),
                "stamp": stamp,
            }
        )
        data = {
            "iotData": iot_data,
            "data": {
                "appKey": APP_KEY,
                "deviceId": self._device_id,
                "platform": "2",
            },
            "stamp": stamp,
        }
        response = await self._request("/mj/user/login", data)
        if not response:
            return False
        self._uid = response.get("uid")
        self._access_token = response.get("mdata", {}).get("accessToken")
        access_token = response.get("accessToken")
        random_data = response.get("randomData")
        if access_token and random_data:
            try:
                self._set_session_keys(access_token, random_data)
            except Exception as err:
                _LOGGER.debug("session aes keys failed: %s", err)
        return bool(self._access_token)

    async def list_washers(self) -> dict[int, dict[str, Any]]:
        response = await self._request("/v1/appliance/user/list/get", self._general())
        if not response:
            return {}
        appliances: dict[int, dict[str, Any]] = {}
        for item in response.get("list") or []:
            try:
                device_type = int(item.get("type"), 16)
            except (TypeError, ValueError):
                continue
            if device_type not in (0xDA, 0xDB, 0xDC):
                continue
            appliance_id = int(item["id"])
            sn = item.get("sn") or ""
            if sn and self._aes_key and self._aes_iv:
                try:
                    sn = _aes_decrypt_hex(sn, self._aes_key, self._aes_iv)
                except Exception:
                    pass
            model = ""
            if isinstance(sn, str) and len(sn) > 17:
                model = sn[9:17]
            appliances[appliance_id] = {
                "device_id": appliance_id,
                "device_type": device_type,
                "name": item.get("name") or f"Washer {appliance_id}",
                "model": model or item.get("productModel") or "",
                "online": item.get("onlineStatus") == "1",
                "sn": sn if isinstance(sn, str) else "",
            }
        return appliances

    async def get_token_key(self, appliance_id: int) -> tuple[str, str] | None:
        for method in (1, 2, 0):
            udp = _udp_id(appliance_id, method)
            data = self._general()
            data.update({"udpid": udp, "applianceCodes": str(appliance_id)})
            response = await self._request("/v1/iot/secure/getToken", data)
            if not response or "tokenlist" not in response:
                continue
            for token in response["tokenlist"]:
                if token.get("udpId", "").lower() == udp.lower():
                    return token["token"].lower(), token["key"].lower()
        return None
