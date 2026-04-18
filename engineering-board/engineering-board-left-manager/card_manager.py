import time
from machine import SPI, Pin  # pyright: ignore[reportMissingImports]
from power_card import PowerCard
from eng_utils import ENABLE_CARD_READER, disabledString, logger

VOLTAGE_CHECK_FREQUENCY = 0.2

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


class CardReader:
    def __init__(self, uid: int, analogIn: _AnalogIn):
        self.uid = int(uid)

        self.inputPin = analogIn
        self.lastVoltageCheck = time.ticks_ms()
        self.lastCard = None
        logger.info(f"Created CardReader-Analog: {self}")

    @property
    def UID(self) -> int:
        return self.uid

    @property
    def CardPresent(self) -> PowerCard | None:
        if time.ticks_diff(time.ticks_ms(), self.lastVoltageCheck) < int(VOLTAGE_CHECK_FREQUENCY * 1000):
            return self.lastCard

        self.lastVoltageCheck = time.ticks_ms()
        logger.info(
            f"CardReader({self}): Checking pin present - voltage {self.inputPin.voltage}"
        )

        self.lastCard = PowerCard.FindCard(self.inputPin.voltage)
        return self.lastCard

    @property
    def CardID(self) -> str | None:
        card = self.CardPresent
        return card.UID if card else None

    def __str__(self):
        retval = f"{self.uid}{disabledString(ENABLE_CARD_READER)}"
        return retval


class CardReaderManagerClass:

    def __init__(self) -> None:

        self.__ALL_CARD_READERS: list["CardReader"] = []
        self.__ALL_CARD_READERS = []
        if not ENABLE_CARD_READER:
            logger.info("CardReaderManager: Card readers disabled")
            return

        self.spi = SPI(
            0,
            baudrate=1_000_000,
            polarity=0,
            phase=0,
            sck=Pin(18),   # TODO: verify GP18 for RP2350 wiring
            mosi=Pin(19),  # TODO: verify GP19 for RP2350 wiring
            miso=Pin(16),  # TODO: verify GP16 for RP2350 wiring
        )

        self.channel09 = _MCP3008(self.spi, Pin(9, Pin.OUT))   # TODO: verify GP9 for RP2350 wiring
        self.channel10 = _MCP3008(self.spi, Pin(10, Pin.OUT))  # TODO: verify GP10 for RP2350 wiring
        self.channel11 = _MCP3008(self.spi, Pin(11, Pin.OUT))  # TODO: verify GP11 for RP2350 wiring
        self.channel12 = _MCP3008(self.spi, Pin(12, Pin.OUT))  # TODO: verify GP12 for RP2350 wiring

        self.__ALL_CARD_READERS.append(CardReader(0, _AnalogIn(self.channel09, P0)))
        self.__ALL_CARD_READERS.append(CardReader(1, _AnalogIn(self.channel09, P1)))
        self.__ALL_CARD_READERS.append(CardReader(2, _AnalogIn(self.channel09, P2)))
        # self.__ALL_CARD_READERS.append(CardReader(3, AnalogIn(self.channel09, MCP.P3)))
        # self.__ALL_CARD_READERS.append(CardReader(4, AnalogIn(self.channel09, MCP.P4)))
        # self.__ALL_CARD_READERS.append(CardReader(5, AnalogIn(self.channel09, MCP.P5)))
        # self.__ALL_CARD_READERS.append(CardReader(6, AnalogIn(self.channel09, MCP.P6)))
        # self.__ALL_CARD_READERS.append(CardReader(7, AnalogIn(self.channel09, MCP.P7)))

        # self.__ALL_CARD_READERS.append(CardReader(8, AnalogIn(self.channel10, MCP.P0)))
        # self.__ALL_CARD_READERS.append(CardReader(9, AnalogIn(self.channel10, MCP.P1)))
        # self.__ALL_CARD_READERS.append(CardReader(10, AnalogIn(self.channel10, MCP.P2)))
        # self.__ALL_CARD_READERS.append(CardReader(11, AnalogIn(self.channel10, MCP.P3)))
        # self.__ALL_CARD_READERS.append(CardReader(12, AnalogIn(self.channel10, MCP.P4)))
        # self.__ALL_CARD_READERS.append(CardReader(13, AnalogIn(self.channel10, MCP.P5)))
        # self.__ALL_CARD_READERS.append(CardReader(14, AnalogIn(self.channel10, MCP.P6)))
        # self.__ALL_CARD_READERS.append(CardReader(15, AnalogIn(self.channel10, MCP.P7)))

        # self.__ALL_CARD_READERS.append(CardReader(16, AnalogIn(self.channel11, MCP.P0)))
        # self.__ALL_CARD_READERS.append(CardReader(17, AnalogIn(self.channel11, MCP.P1)))
        # self.__ALL_CARD_READERS.append(CardReader(18, AnalogIn(self.channel11, MCP.P2)))
        # self.__ALL_CARD_READERS.append(CardReader(19, AnalogIn(self.channel11, MCP.P3)))
        # self.__ALL_CARD_READERS.append(CardReader(20, AnalogIn(self.channel11, MCP.P4)))
        # self.__ALL_CARD_READERS.append(CardReader(21, AnalogIn(self.channel11, MCP.P5)))
        # self.__ALL_CARD_READERS.append(CardReader(22, AnalogIn(self.channel11, MCP.P6)))
        # self.__ALL_CARD_READERS.append(CardReader(23, AnalogIn(self.channel11, MCP.P7)))

        # self.__ALL_CARD_READERS.append(CardReader(24, AnalogIn(self.channel12, MCP.P0)))
        # self.__ALL_CARD_READERS.append(CardReader(25, AnalogIn(self.channel12, MCP.P1)))
        # self.__ALL_CARD_READERS.append(CardReader(26, AnalogIn(self.channel12, MCP.P2)))
        # self.__ALL_CARD_READERS.append(CardReader(27, AnalogIn(self.channel12, MCP.P3)))
        # self.__ALL_CARD_READERS.append(CardReader(28, AnalogIn(self.channel12, MCP.P4)))
        # self.__ALL_CARD_READERS.append(CardReader(29, AnalogIn(self.channel12, MCP.P5)))
        # self.__ALL_CARD_READERS.append(CardReader(30, AnalogIn(self.channel12, MCP.P6)))
        # self.__ALL_CARD_READERS.append(CardReader(31, AnalogIn(self.channel12, MCP.P7)))

        logger.info(
            f"CardReaderManager: Creating {len(self.__ALL_CARD_READERS)} card readers"
        )

    def AllReaders(self) -> list[CardReader]:
        return self.__ALL_CARD_READERS

    def ReaderStatus(self) -> list[str]:
        return [
            reader.CardID
            for reader in self.__ALL_CARD_READERS
            if reader.CardID is not None
        ]

    def ReaderCards(self) -> list[str]:
        retval = [
            f"{reader}{disabledString(ENABLE_CARD_READER)}: {reader.CardPresent.CardName}"
            for reader in self.__ALL_CARD_READERS
            if reader.CardPresent is not None
        ]
        return retval


CardReaderManager = CardReaderManagerClass()
