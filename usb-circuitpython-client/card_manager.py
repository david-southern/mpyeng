import time
import board
import busio # type: ignore
import digitalio # type: ignore
import board # type: ignore
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
from power_card import PowerCard
from eng_utils import ENABLE_CARD_READER, disabledString, logger

VOLTAGE_CHECK_FREQUENCY = 0.2

class CardReader:
    def __init__(self, uid: int, analogIn: AnalogIn):
        self.uid = int(uid)

        self.inputPin = analogIn
        self.lastVoltageCheck = time.monotonic()
        self.lastCard = None
        logger.info(f"Created CardReader-Analog: {self}")

    @property
    def UID(self) -> int:
        return self.uid

    @property
    def CardPresent(self) -> PowerCard:
        if time.monotonic() - self.lastVoltageCheck < VOLTAGE_CHECK_FREQUENCY:
            return self.lastCard
        
        self.lastVoltageCheck = time.monotonic()
        logger.info(f"CardReader({self}): Checking pin present - voltage {self.inputPin.voltage}")

        self.lastCard = PowerCard.FindCard(self.inputPin.voltage)
        return self.lastCard

    @property
    def CardID(self) -> int:
        card = self.CardPresent
        return card.UID if card else None

    def __str__(self):
        retval = f"{self.uid}{disabledString(ENABLE_CARD_READER)}"
        return retval


class CardReaderManagerClass:

    def __init__(self) -> None:

        self._ALL_CARD_READERS: list["CardReader"] = []
        self._ALL_CARD_READERS = []
        if not ENABLE_CARD_READER:
            logger.info(f"CardReaderManager: Card readers disabled")
            return
        
        self.spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

        self.channel09 = MCP.MCP3008(self.spi, digitalio.DigitalInOut(board.D9))
        self.channel10 = MCP.MCP3008(self.spi, digitalio.DigitalInOut(board.D10))
        self.channel11 = MCP.MCP3008(self.spi, digitalio.DigitalInOut(board.D11))
        self.channel12 = MCP.MCP3008(self.spi, digitalio.DigitalInOut(board.D12))

        self._ALL_CARD_READERS.append(CardReader(0, AnalogIn(self.channel09, MCP.P0)))
        self._ALL_CARD_READERS.append(CardReader(1, AnalogIn(self.channel09, MCP.P1)))
        self._ALL_CARD_READERS.append(CardReader(2, AnalogIn(self.channel09, MCP.P2)))
        # self._ALL_CARD_READERS.append(CardReader(3, AnalogIn(self.channel09, MCP.P3)))
        # self._ALL_CARD_READERS.append(CardReader(4, AnalogIn(self.channel09, MCP.P4)))
        # self._ALL_CARD_READERS.append(CardReader(5, AnalogIn(self.channel09, MCP.P5)))
        # self._ALL_CARD_READERS.append(CardReader(6, AnalogIn(self.channel09, MCP.P6)))
        # self._ALL_CARD_READERS.append(CardReader(7, AnalogIn(self.channel09, MCP.P7)))

        # self._ALL_CARD_READERS.append(CardReader(8, AnalogIn(self.channel10, MCP.P0)))
        # self._ALL_CARD_READERS.append(CardReader(9, AnalogIn(self.channel10, MCP.P1)))
        # self._ALL_CARD_READERS.append(CardReader(10, AnalogIn(self.channel10, MCP.P2)))
        # self._ALL_CARD_READERS.append(CardReader(11, AnalogIn(self.channel10, MCP.P3)))
        # self._ALL_CARD_READERS.append(CardReader(12, AnalogIn(self.channel10, MCP.P4)))
        # self._ALL_CARD_READERS.append(CardReader(13, AnalogIn(self.channel10, MCP.P5)))
        # self._ALL_CARD_READERS.append(CardReader(14, AnalogIn(self.channel10, MCP.P6)))
        # self._ALL_CARD_READERS.append(CardReader(15, AnalogIn(self.channel10, MCP.P7)))

        # self._ALL_CARD_READERS.append(CardReader(16, AnalogIn(self.channel11, MCP.P0)))
        # self._ALL_CARD_READERS.append(CardReader(17, AnalogIn(self.channel11, MCP.P1)))
        # self._ALL_CARD_READERS.append(CardReader(18, AnalogIn(self.channel11, MCP.P2)))
        # self._ALL_CARD_READERS.append(CardReader(19, AnalogIn(self.channel11, MCP.P3)))
        # self._ALL_CARD_READERS.append(CardReader(20, AnalogIn(self.channel11, MCP.P4)))
        # self._ALL_CARD_READERS.append(CardReader(21, AnalogIn(self.channel11, MCP.P5)))
        # self._ALL_CARD_READERS.append(CardReader(22, AnalogIn(self.channel11, MCP.P6)))
        # self._ALL_CARD_READERS.append(CardReader(23, AnalogIn(self.channel11, MCP.P7)))

        # self._ALL_CARD_READERS.append(CardReader(24, AnalogIn(self.channel12, MCP.P0)))
        # self._ALL_CARD_READERS.append(CardReader(25, AnalogIn(self.channel12, MCP.P1)))
        # self._ALL_CARD_READERS.append(CardReader(26, AnalogIn(self.channel12, MCP.P2)))
        # self._ALL_CARD_READERS.append(CardReader(27, AnalogIn(self.channel12, MCP.P3)))
        # self._ALL_CARD_READERS.append(CardReader(28, AnalogIn(self.channel12, MCP.P4)))
        # self._ALL_CARD_READERS.append(CardReader(29, AnalogIn(self.channel12, MCP.P5)))
        # self._ALL_CARD_READERS.append(CardReader(30, AnalogIn(self.channel12, MCP.P6)))
        # self._ALL_CARD_READERS.append(CardReader(31, AnalogIn(self.channel12, MCP.P7)))

        logger.info(f"CardReaderManager: Creating {len(self._ALL_CARD_READERS)} card readers")


    def AllReaders(self) -> list[CardReader]:
        return self._ALL_CARD_READERS

    def ReaderStatus(self) -> list[int]:
        return [reader.CardID for reader in self._ALL_CARD_READERS if reader.CardID is not None]

    def ReaderCards(self) -> list[str]:
        retval = [ f"{reader}{disabledString(ENABLE_CARD_READER)}: {reader.CardPresent.CardName}" for reader in self._ALL_CARD_READERS if reader.CardPresent is not None]
        return retval


CardReaderManager = CardReaderManagerClass()
