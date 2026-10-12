import logging
import socket
import threading
import time
from typing import Any

from .message import (
    code_for_select,
    parse_washer_status,
    patch_washing_data,
    power_message,
    query_message,
    start_message,
    wash_index_for_attr,
    washing_params_message,
)
from .packet import PacketBuilder
from .security import (
    MSGTYPE_ENCRYPTED_REQUEST,
    MSGTYPE_HANDSHAKE_REQUEST,
    LocalSecurity,
)

_LOGGER = logging.getLogger(__name__)

_EMPTY_STATUS: dict[str, Any] = {
    "power": False,
    "start": False,
    "status": None,
    "mode": None,
    "program": None,
    "water_level": None,
    "temperature": None,
    "dehydration_speed": None,
    "wash_time": None,
    "dehydration_time": None,
    "detergent": None,
    "softener": None,
    "progress": "unknown",
    "time_remaining": None,
    "stains": None,
    "wash_time_value": None,
    "dehydration_time_value": None,
    "dirty_degree": None,
    "washing_data": b"",
    "washing_data_hex": "",
    "available": False,
}


class WasherClient:
    def __init__(
        self,
        device_id: int,
        device_type: int,
        host: str,
        port: int,
        protocol: int,
        token: str = "",
        key: str = "",
    ) -> None:
        self.device_id = device_id
        self.device_type = device_type
        self.host = host
        self.port = port
        self.protocol = protocol
        self._token = bytes.fromhex(token) if token else b""
        self._key = bytes.fromhex(key) if key else b""
        self._security = LocalSecurity()
        self._protocol_version = 0
        self._sock: socket.socket | None = None
        self._buffer = b""
        self._lock = threading.Lock()
        self.status: dict[str, Any] = dict(_EMPTY_STATUS)

    @property
    def connected(self) -> bool:
        return self._sock is not None

    def connect(self) -> None:
        with self._lock:
            self._connect_locked()

    def close(self) -> None:
        with self._lock:
            self._close_locked()

    def refresh(self) -> dict[str, Any]:
        with self._lock:
            self._ensure_connected_locked()
            frame = query_message(self.device_type, self._protocol_version)
            self._send_uart_locked(frame)
            self._drain_locked(timeout=3.0, expect_status=True)
            return dict(self.status)

    def set_power(self, value: bool) -> None:
        with self._lock:
            self._ensure_connected_locked()
            frame = power_message(self.device_type, self._protocol_version, value)
            self._send_uart_locked(frame)
            self.status["power"] = value
            if not value:
                self.status["start"] = False
                self.status["status"] = "idle"
            else:
                self.status["status"] = "standby"
            self._drain_locked(timeout=1.5, expect_status=False)

    def set_start(self, value: bool) -> None:
        with self._lock:
            self._ensure_connected_locked()
            washing = self.status.get("washing_data") or b""
            frame = start_message(
                self.device_type,
                self._protocol_version,
                value,
                bytes(washing),
            )
            self._send_uart_locked(frame)
            self.status["start"] = value
            self.status["power"] = True
            self.status["status"] = "start" if value else "pause"
            self._drain_locked(timeout=1.5, expect_status=False)

    def set_select(self, attr: str, option: str) -> None:
        code = code_for_select(attr, option)
        index = wash_index_for_attr(attr)
        if code is None or index is None:
            raise ValueError(f"unsupported select {attr}={option}")
        with self._lock:
            washing = patch_washing_data(
                self.status.get("washing_data") or b"", index, code
            )
            self._push_washing_data_locked(washing)
            self.status[attr] = option
            self.status[f"{attr}_code"] = code

    def set_number(self, attr: str, value: int) -> None:
        index = wash_index_for_attr(attr)
        if index is None:
            raise ValueError(f"unsupported number {attr}")
        with self._lock:
            washing = patch_washing_data(
                self.status.get("washing_data") or b"",
                index,
                int(value),
            )
            self._push_washing_data_locked(washing)
            self.status[attr] = int(value)

    def _push_washing_data_locked(self, washing: bytes) -> None:
        self._ensure_connected_locked()
        frame = washing_params_message(
            self.device_type,
            self._protocol_version,
            washing,
        )
        self._send_uart_locked(frame)
        self.status["washing_data"] = washing
        self.status["washing_data_hex"] = washing.hex()
        self._drain_locked(timeout=1.5, expect_status=False)

    def _connect_locked(self) -> None:
        self._close_locked()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(8)
        sock.connect((self.host, self.port))
        self._sock = sock
        self._buffer = b""
        self._security = LocalSecurity()
        if self.protocol == 3:
            self._authenticate_locked()
        frame = query_message(self.device_type, self._protocol_version)
        self._send_uart_locked(frame)
        self._drain_locked(timeout=4.0, expect_status=True)
        self.status["available"] = True

    def _close_locked(self) -> None:
        if self._sock is None:
            return
        try:
            self._sock.close()
        except OSError:
            pass
        self._sock = None
        self._buffer = b""
        self.status["available"] = False

    def _ensure_connected_locked(self) -> None:
        if self._sock is not None:
            return
        self._connect_locked()

    def _authenticate_locked(self) -> None:
        if not self._token or not self._key:
            raise ValueError("protocol V3 requires token and key")
        if self._sock is None:
            raise ConnectionError("not connected")
        request = self._security.encode_8370(self._token, MSGTYPE_HANDSHAKE_REQUEST)
        self._sock.send(request)
        response = self._sock.recv(512)
        if len(response) < 20:
            raise ValueError("handshake failed")
        self._security.tcp_key(response[8:72], self._key)

    def _send_uart_locked(self, uart: bytes) -> None:
        if self._sock is None:
            raise ConnectionError("not connected")
        packet = PacketBuilder(self.device_id, uart).finalize()
        if self.protocol == 3:
            packet = self._security.encode_8370(packet, MSGTYPE_ENCRYPTED_REQUEST)
        self._sock.send(packet)

    def _drain_locked(self, timeout: float, expect_status: bool) -> None:
        """Read available packets until timeout. Never raise on idle timeout."""
        if self._sock is None:
            return
        deadline = time.monotonic() + timeout
        got_status = False
        while time.monotonic() < deadline:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            self._sock.settimeout(min(remaining, 0.5))
            try:
                raw = self._sock.recv(2048)
            except socket.timeout:
                if got_status or not expect_status:
                    break
                continue
            except OSError as err:
                _LOGGER.debug("recv error: %s", err)
                self._close_locked()
                if expect_status:
                    raise
                return
            if not raw:
                self._close_locked()
                if expect_status and not got_status:
                    raise ConnectionError("connection closed")
                return
            messages = self._unwrap(raw)
            for message in messages:
                before = self.status.get("status")
                self._handle_lan_message(message)
                if self.status.get("status") is not None or self.status.get(
                    "washing_data"
                ):
                    got_status = True
                if before != self.status.get("status"):
                    got_status = True
            if got_status and not expect_status:
                break
        self._sock.settimeout(8)
        if expect_status and not got_status:
            _LOGGER.debug("no status within %.1fs", timeout)

    def _unwrap(self, raw: bytes) -> list[bytes]:
        if self.protocol == 3:
            messages, self._buffer = self._security.decode_8370(self._buffer + raw)
            return messages
        messages, self._buffer = _split_v2(self._buffer + raw)
        return messages

    def _handle_lan_message(self, message: bytes) -> None:
        if message == b"ERROR" or len(message) <= 56:
            return
        crypto = message[40:-16]
        if len(crypto) % 16 != 0:
            return
        decrypted = self._security.aes_decrypt(crypto)
        if not decrypted or decrypted[0] != 0xAA:
            return
        if len(decrypted) > 9:
            self._protocol_version = decrypted[8]
        parsed = parse_washer_status(decrypted)
        if not parsed:
            return
        self.status.update(parsed)
        _LOGGER.debug("washer status: %s", parsed)


def _split_v2(msg: bytes) -> tuple[list[bytes], bytes]:
    result: list[bytes] = []
    while len(msg) >= 6:
        length = msg[4] + (msg[5] << 8)
        if length < 6 or len(msg) < length:
            break
        result.append(msg[:length])
        msg = msg[length:]
    return result, msg
