from machine import SPI, Pin

_MCP3008_VREF = 3.3
P0, P1, P2, P3, P4, P5, P6, P7 = 0, 1, 2, 3, 4, 5, 6, 7


class _MCP3008:
    """Minimal MicroPython driver for the MCP3008 8-channel SPI ADC."""

    def __init__(self, spi: SPI, cs_pin: Pin):
        self._spi = spi
        self._cs = cs_pin
        self._cs.value(1)
        self._buf = bytearray(3)

    def read(self, channel: int) -> int:
        """Returns the raw 10-bit ADC value for the given channel (0–7)."""
        self._buf[0] = 0x01
        self._buf[1] = 0x80 | (channel << 4)
        self._buf[2] = 0x00
        self._cs.value(0)
        self._spi.write_readinto(self._buf, self._buf)
        self._cs.value(1)
        return ((self._buf[1] & 0x03) << 8) | self._buf[2]


class _AnalogIn:
    """Exposes a .voltage property for a single MCP3008 channel."""

    def __init__(self, mcp: "_MCP3008", channel: int):
        self._mcp = mcp
        self._channel = channel

    @property
    def voltage(self) -> float:
        return self._mcp.read(self._channel) * _MCP3008_VREF / 1023
