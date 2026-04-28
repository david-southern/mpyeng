from machine import SPI

from utils.eng_utils import logger
from utils.device_manager import DeviceManager, Systems, PinNames
from drivers.mcp3008 import MCP3008, MCPAnalogIn
from card_reader.card_reader import CardReader


class CardReaderManagerClass:
    def __init__(self) -> None:

        self.__ALL_CARD_READERS: list["CardReader"] = []
        self.__ALL_CARD_READERS = []
        if not DeviceManager.IsEnabled(Systems.CARD_READER):
            logger.info("CardReaderManager: Card readers disabled")
            return

        self.spi = SPI(
            0,
            sck=DeviceManager.ResolvePin(PinNames.CardReader.SPI_CLK).Pin,  # noqa: F821
            mosi=DeviceManager.ResolvePin(PinNames.CardReader.SPI_MOSI).Pin,
            miso=DeviceManager.ResolvePin(PinNames.CardReader.SPI_MISO).Pin,
        )

        self.channel01 = MCP3008(self.spi, DeviceManager.ResolvePin(PinNames.CardReader.SPI_CS_MCP1).Pin)
        self.channel02 = MCP3008(self.spi, DeviceManager.ResolvePin(PinNames.CardReader.SPI_CS_MCP2).Pin)
        self.channel03 = MCP3008(self.spi, DeviceManager.ResolvePin(PinNames.CardReader.SPI_CS_MCP3).Pin)
        self.channel04 = MCP3008(self.spi, DeviceManager.ResolvePin(PinNames.CardReader.SPI_CS_MCP4).Pin)

        self.__ALL_CARD_READERS.append(CardReader(0, MCPAnalogIn(self.channel01, 0)))
        self.__ALL_CARD_READERS.append(CardReader(1, MCPAnalogIn(self.channel01, 1)))
        self.__ALL_CARD_READERS.append(CardReader(2, MCPAnalogIn(self.channel01, 2)))
        self.__ALL_CARD_READERS.append(CardReader(3, MCPAnalogIn(self.channel01, 3)))
        self.__ALL_CARD_READERS.append(CardReader(4, MCPAnalogIn(self.channel01, 4)))
        self.__ALL_CARD_READERS.append(CardReader(5, MCPAnalogIn(self.channel01, 5)))
        self.__ALL_CARD_READERS.append(CardReader(6, MCPAnalogIn(self.channel01, 6)))
        self.__ALL_CARD_READERS.append(CardReader(7, MCPAnalogIn(self.channel01, 7)))
        self.__ALL_CARD_READERS.append(CardReader(8, MCPAnalogIn(self.channel02, 0)))
        self.__ALL_CARD_READERS.append(CardReader(9, MCPAnalogIn(self.channel02, 1)))

        self.__ALL_CARD_READERS.append(CardReader(10, MCPAnalogIn(self.channel02, 2)))
        self.__ALL_CARD_READERS.append(CardReader(11, MCPAnalogIn(self.channel02, 3)))
        self.__ALL_CARD_READERS.append(CardReader(12, MCPAnalogIn(self.channel02, 4)))
        self.__ALL_CARD_READERS.append(CardReader(13, MCPAnalogIn(self.channel02, 5)))
        self.__ALL_CARD_READERS.append(CardReader(14, MCPAnalogIn(self.channel02, 6)))
        self.__ALL_CARD_READERS.append(CardReader(15, MCPAnalogIn(self.channel02, 7)))
        self.__ALL_CARD_READERS.append(CardReader(16, MCPAnalogIn(self.channel03, 0)))
        self.__ALL_CARD_READERS.append(CardReader(17, MCPAnalogIn(self.channel03, 1)))
        self.__ALL_CARD_READERS.append(CardReader(18, MCPAnalogIn(self.channel03, 2)))
        self.__ALL_CARD_READERS.append(CardReader(19, MCPAnalogIn(self.channel03, 3)))

        self.__ALL_CARD_READERS.append(CardReader(20, MCPAnalogIn(self.channel03, 4)))
        self.__ALL_CARD_READERS.append(CardReader(21, MCPAnalogIn(self.channel03, 5)))
        self.__ALL_CARD_READERS.append(CardReader(22, MCPAnalogIn(self.channel03, 6)))
        self.__ALL_CARD_READERS.append(CardReader(23, MCPAnalogIn(self.channel03, 7)))
        self.__ALL_CARD_READERS.append(CardReader(24, MCPAnalogIn(self.channel04, 0)))
        self.__ALL_CARD_READERS.append(CardReader(25, MCPAnalogIn(self.channel04, 1)))
        self.__ALL_CARD_READERS.append(CardReader(26, MCPAnalogIn(self.channel04, 2)))
        self.__ALL_CARD_READERS.append(CardReader(27, MCPAnalogIn(self.channel04, 3)))
        self.__ALL_CARD_READERS.append(CardReader(28, MCPAnalogIn(self.channel04, 4)))
        self.__ALL_CARD_READERS.append(CardReader(29, MCPAnalogIn(self.channel04, 5)))

        logger.info(f"CardReaderManager: Creating {len(self.__ALL_CARD_READERS)} card readers")

    def AllReaders(self) -> list[CardReader]:
        return self.__ALL_CARD_READERS

    def ReaderStatus(self) -> list[str]:
        return [reader.CardID for reader in self.__ALL_CARD_READERS if reader.CardID is not None]

    def ReaderCards(self) -> list[str]:
        retval = [
            f"{reader}: {reader.CardPresent.CardName}"
            for reader in self.__ALL_CARD_READERS
            if reader.CardPresent is not None
        ]
        return retval


CardReaderManager = CardReaderManagerClass()
