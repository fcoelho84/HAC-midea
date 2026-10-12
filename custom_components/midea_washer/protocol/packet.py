from datetime import datetime

from .security import LocalSecurity


def uart_checksum(data: bytes) -> int:
    """8-bit two's complement checksum.

    Matches libmidea_oem_core.so ms_uart_pro_check_sum (REA/Ghidra):
    sum bytes then return -sum (mod 256).
    """
    return (-sum(data)) & 0xFF


def build_uart_frame(
    device_type: int,
    protocol_version: int,
    message_type: int,
    body: bytes,
) -> bytes:
    """Build appliance UART frame starting with 0xAA.

    Frame shape corroborated by OEM ms_make_query_uart_frame (header 0xAA)
    and community M-Smart message serializers.
    """
    header = bytearray(
        [
            0xAA,
            0x00,
            device_type & 0xFF,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            protocol_version & 0xFF,
            message_type & 0xFF,
        ]
    )
    stream = header + body
    stream[1] = len(stream) + 1
    stream.append(uart_checksum(stream[1:]))
    return bytes(stream)


class PacketBuilder:
    """Wrap a UART command into a LAN 5A5A packet."""

    def __init__(self, device_id: int, command: bytes) -> None:
        self._security = LocalSecurity()
        self._packet = bytearray(
            [
                0x5A,
                0x5A,
                0x01,
                0x11,
                0x00,
                0x00,
                0x20,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
                0x00,
            ]
        )
        self._packet[12:20] = self._packet_time()
        self._packet[20:28] = device_id.to_bytes(8, "little")
        self._command = command

    def finalize(self, msg_type: int = 1) -> bytes:
        if msg_type != 1:
            self._packet[3] = 0x10
            self._packet[6] = 0x7B
        else:
            self._packet.extend(self._security.aes_encrypt(self._command))
        self._packet[4:6] = (len(self._packet) + 16).to_bytes(2, "little")
        self._packet.extend(self._security.encode32_data(self._packet))
        return bytes(self._packet)

    @staticmethod
    def _packet_time() -> bytes:
        stamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:16]
        out = bytearray()
        for i in range(0, len(stamp), 2):
            out.insert(0, int(stamp[i : i + 2]))
        return bytes(out)
