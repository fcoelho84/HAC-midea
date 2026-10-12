from hashlib import md5, sha256

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Util.strxor import strxor

from ..const import LAN_SIGN_KEY

MSGTYPE_HANDSHAKE_REQUEST = 0x0
MSGTYPE_HANDSHAKE_RESPONSE = 0x1
MSGTYPE_ENCRYPTED_RESPONSE = 0x3
MSGTYPE_ENCRYPTED_REQUEST = 0x6


class LocalSecurity:
    """LAN crypto for M-Smart TCP packets (V2 AES-ECB + V3 0x8370)."""

    def __init__(self) -> None:
        self.iv = b"\0" * 16
        self.aes_key = md5(LAN_SIGN_KEY).digest()
        self.salt = LAN_SIGN_KEY
        self._tcp_key: bytes | None = None
        self._request_count = 0
        self._response_count = 0

    def aes_decrypt(self, raw: bytes) -> bytes:
        try:
            return unpad(AES.new(self.aes_key, AES.MODE_ECB).decrypt(bytearray(raw)), 16)
        except ValueError:
            return bytearray()

    def aes_encrypt(self, raw: bytes) -> bytes:
        return AES.new(self.aes_key, AES.MODE_ECB).encrypt(bytearray(pad(raw, 16)))

    def aes_cbc_decrypt(self, raw: bytes, key: bytes) -> bytes:
        return AES.new(key=key, mode=AES.MODE_CBC, iv=self.iv).decrypt(raw)

    def aes_cbc_encrypt(self, raw: bytes, key: bytes) -> bytes:
        return AES.new(key=key, mode=AES.MODE_CBC, iv=self.iv).encrypt(raw)

    def encode32_data(self, raw: bytes) -> bytes:
        return md5(raw + self.salt).digest()

    def tcp_key(self, response: bytes, key: bytes) -> bytes:
        if response == b"ERROR":
            raise ValueError("authentication failed")
        if len(response) != 64:
            raise ValueError("unexpected handshake length")
        payload = response[:32]
        sign = response[32:]
        plain = self.aes_cbc_decrypt(payload, key)
        if sha256(plain).digest() != sign:
            raise ValueError("handshake sign mismatch")
        self._tcp_key = strxor(plain, key)
        self._request_count = 0
        self._response_count = 0
        return self._tcp_key

    def encode_8370(self, data: bytes, msgtype: int) -> bytes:
        if self._tcp_key is None and msgtype in (
            MSGTYPE_ENCRYPTED_RESPONSE,
            MSGTYPE_ENCRYPTED_REQUEST,
        ):
            raise ValueError("tcp key missing")
        header = bytearray([0x83, 0x70])
        size = len(data)
        padding = 0
        if msgtype in (MSGTYPE_ENCRYPTED_RESPONSE, MSGTYPE_ENCRYPTED_REQUEST):
            if (size + 2) % 16 != 0:
                padding = 16 - ((size + 2) & 0xF)
            size += padding + 32
            data += get_random_bytes(padding)
        header += size.to_bytes(2, "big")
        header += bytearray([0x20, (padding << 4) | msgtype])
        data = self._request_count.to_bytes(2, "big") + data
        self._request_count = (self._request_count + 1) & 0xFFFF
        if msgtype in (MSGTYPE_ENCRYPTED_RESPONSE, MSGTYPE_ENCRYPTED_REQUEST):
            sign = sha256(header + data).digest()
            data = self.aes_cbc_encrypt(raw=data, key=self._tcp_key) + sign
        return header + data

    def decode_8370(self, data: bytes) -> tuple[list[bytes], bytes]:
        if len(data) < 6:
            return [], data
        header = data[:6]
        if header[0] != 0x83 or header[1] != 0x70:
            raise ValueError("not an 8370 message")
        size = int.from_bytes(header[2:4], "big") + 8
        if len(data) < size:
            return [], data
        leftover = data[size:] if len(data) > size else b""
        packet = data[:size]
        padding = header[5] >> 4
        msgtype = header[5] & 0xF
        body = packet[6:]
        if msgtype in (MSGTYPE_ENCRYPTED_RESPONSE, MSGTYPE_ENCRYPTED_REQUEST):
            if self._tcp_key is None:
                raise ValueError("tcp key missing")
            sign = body[-32:]
            body = body[:-32]
            body = self.aes_cbc_decrypt(raw=body, key=self._tcp_key)
            if sha256(header + body).digest() != sign:
                raise ValueError("sign mismatch")
            if padding:
                body = body[:-padding]
        self._response_count = int.from_bytes(body[:2], "big")
        body = body[2:]
        if leftover:
            more, incomplete = self.decode_8370(leftover)
            return [body] + more, incomplete
        return [body], b""
