from machine import SPI, Pin

"""
MicroPython Library for MCP3008 8-channel ADC with SPI

Datasheet for the MCP3008: https://www.microchip.com/datasheet/MCP3008

This code makes much use of Adafruit's CircuitPython code at
https://github.com/adafruit/Adafruit_CircuitPython_MCP3xxx
adapted for MicroPython.

Tested on the Raspberry Pi Pico.

Thanks, @Raspberry_Pi and @Adafruit, for all you've given us!
"""


class MCP3008:
    VREF = 3.3

    def __init__(self, spi: SPI, cs: Pin):
        """
        Create MCP3008 instance

        Args:
            spi: configured SPI bus
            cs: pin to use for chip select
        """
        self.cs = cs
        self.cs.value(1)  # ncs on
        self._spi = spi
        self._out_buf = bytearray(3)
        self._out_buf[0] = 0x01
        self._in_buf = bytearray(3)

    def read(self, channel: int, is_differential: bool = False) -> int:
        """
        read a voltage or voltage difference using the MCP3008.

        Args:
            channel: the MCP3008 channel to read (0-8)
            is_differential: if true, return the potential difference between two pins,


        Returns:
            voltage in range [0, 1023] where 1023 = VREF (3V3)
        """

        self.cs.value(0)  # select
        self._out_buf[1] = ((not is_differential) << 7) | (channel << 4)
        self._spi.write_readinto(self._out_buf, self._in_buf)
        self.cs.value(1)  # turn off
        return ((self._in_buf[1] & 0x03) << 8) | self._in_buf[2]


class MCPAnalogIn:
    """Exposes a a single MCP3008 channel as a pseudo Analog input."""

    def __init__(self, mcp: MCP3008, channel: int):
        self._mcp = mcp
        self._channel = channel

    @property
    def voltage(self) -> float:
        return self._mcp.read(self._channel) * MCP3008.VREF / 1023
