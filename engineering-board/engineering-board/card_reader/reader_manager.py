from machine import SPI, Pin

from utils.eng_utils import ENABLE_CARD_READER, disabledString, logger
from utils.device_manager import device_manager
from utils.mcp3008 import _MCP3008, _AnalogIn, P0, P1, P2
from card_reader.card_reader import CardReader


class CardReaderManagerClass:
    def __init__(self) -> None:

        self.__ALL_CARD_READERS: list["CardReader"] = []
        self.__ALL_CARD_READERS = []
        if not ENABLE_CARD_READER:
            logger.info("CardReaderManager: Card readers disabled")
            return

        self.spi = SPI(
            device_manager.resolve_pin("card_reader", "spi_id", 2),
            baudrate=1_000_000,
            polarity=0,
            phase=0,
            sck=Pin(device_manager.resolve_pin("card_reader", "spi_sck", 18)),
            mosi=Pin(device_manager.resolve_pin("card_reader", "spi_mosi", 19)),
            miso=Pin(device_manager.resolve_pin("card_reader", "spi_miso", 16)),
        )

        cs_pins = device_manager.resolve_pin("card_reader", "cs_pins", [9, 10, 11, 12])
        self.channel09 = _MCP3008(self.spi, Pin(cs_pins[0], Pin.OUT))
        self.channel10 = _MCP3008(self.spi, Pin(cs_pins[1], Pin.OUT))
        self.channel11 = _MCP3008(self.spi, Pin(cs_pins[2], Pin.OUT))
        self.channel12 = _MCP3008(self.spi, Pin(cs_pins[3], Pin.OUT))

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

        logger.info(f"CardReaderManager: Creating {len(self.__ALL_CARD_READERS)} card readers")

    def AllReaders(self) -> list[CardReader]:
        return self.__ALL_CARD_READERS

    def ReaderStatus(self) -> list[str]:
        return [reader.CardID for reader in self.__ALL_CARD_READERS if reader.CardID is not None]

    def ReaderCards(self) -> list[str]:
        retval = [
            f"{reader}{disabledString(ENABLE_CARD_READER)}: {reader.CardPresent.CardName}"
            for reader in self.__ALL_CARD_READERS
            if reader.CardPresent is not None
        ]
        return retval


CardReaderManager = CardReaderManagerClass()
