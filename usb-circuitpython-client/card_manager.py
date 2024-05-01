import time
import board
from analogio import AnalogIn
from power_card import PowerCard
from utils import ENABLE_CARD_READER, disabledString, logger

VOLTAGE_CHECK_FREQUENCY = 0.2

class CardReader:
    def __init__(self, uid: int, inputPinId: Pin):
        self.uid = int(uid)

        self.inputPinId = inputPinId
        self.inputPin = AnalogIn(inputPinId)
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
        pinVoltage =(self.inputPin.value * 3.3) / 65536
        logger.info(f"CardReader({self}): Checking pin present - voltage {pinVoltage}")

        self.lastCard = PowerCard.FindCard(pinVoltage)
        return self.lastCard

    @property
    def CardID(self) -> int:
        card = self.CardPresent
        return card.UID if card else None

    def __str__(self):
        retval = f"{self.inputPinId}{disabledString(ENABLE_CARD_READER)}"
        return retval


class CardReaderManagerClass:
    def __init__(self) -> None:
        logger.info(f"CardReaderManager: Creating card readers on A0 - A2")

        self._ALL_CARD_READERS: list["CardReader"] = []
        self._ALL_CARD_READERS = []
        self._ALL_CARD_READERS.append(CardReader(0, board.A0))
        # self._ALL_CARD_READERS.append(CardReader(1, board.A1))
        # self._ALL_CARD_READERS.append(CardReader(2, board.A2))

    def AllReaders(self) -> list[CardReader]:
        return self._ALL_CARD_READERS

    def ReaderStatus(self) -> list[int]:
        return [reader.CardID for reader in self._ALL_CARD_READERS if reader.CardID is not None]

    def ReaderCards(self) -> list[str]:
        retval = [ f"{reader}{disabledString(ENABLE_CARD_READER)}: {reader.CardPresent.CardName}" for reader in self._ALL_CARD_READERS if reader.CardPresent is not None]
        return retval


CardReaderManager = CardReaderManagerClass()
