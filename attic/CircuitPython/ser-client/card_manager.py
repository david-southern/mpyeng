import board
from analogio import AnalogIn
import adafruit_logging as logging
from microcontroller import Pin
from power_card import PowerCard

READER_MAX_VOLTAGE = 3.3

logger = logging.getLogger("CardReaderManager")


class CardReader:
    def __init__(self, uid: int, analogPin: Pin):
        self.uid = int(uid)
        self.analogPin = analogPin
        self.pinName = str(analogPin).replace("board.", "")

        self.analogIn = AnalogIn(analogPin)

        logger.info(f"Created CardReader: {self}")

    @property
    def UID(self) -> int:
        return self.uid

    @property
    def AnalogPin(self) -> Pin:
        return self.analogPin

    @property
    def PinName(self) -> str:
        return self.pinName

    @property
    def NormalizedValue(self) -> float:
        return self.analogIn.value / 65536

    @property
    def ActualVoltage(self) -> float:
        return self.NormalizedValue * READER_MAX_VOLTAGE

    @property
    def RefV(self) -> float:
        return self.analogIn.reference_voltage

    @property
    def CardPresent(self) -> PowerCard:
        card = PowerCard.CheckSensorMatch(self.NormalizedValue)
        return card

    @property
    def CardID(self) -> int:
        card = PowerCard.CheckSensorMatch(self.NormalizedValue)
        return card.UID if card else None

    def __str__(self):
        return f"{self.UID}/{self.PinName}"


class CardReaderManagerClass:
    def __init__(self) -> None:
        self._ALL_CARD_READERS: list["CardReader"] = []
        self._ALL_CARD_READERS = []
        self._ALL_CARD_READERS.append(CardReader(1, board.A1))
        self._ALL_CARD_READERS.append(CardReader(2, board.A2))
        self._ALL_CARD_READERS.append(CardReader(3, board.A3))
        self._ALL_CARD_READERS.append(CardReader(4, board.A4))
        self._ALL_CARD_READERS.append(CardReader(5, board.A5))
        self._ALL_CARD_READERS.append(CardReader(6, board.A6))
        self._ALL_CARD_READERS.append(CardReader(7, board.A7))
        self._ALL_CARD_READERS.append(CardReader(8, board.A8))
        self._ALL_CARD_READERS.append(CardReader(9, board.A9))
        self._ALL_CARD_READERS.append(CardReader(10, board.A10))

    def AllReaders(self) -> list[CardReader]:
        return self._ALL_CARD_READERS

    def ReaderStatus(self) -> list[int]:
        return [reader.CardID for reader in self._ALL_CARD_READERS if reader.CardID is not None]


CardReaderManager = CardReaderManagerClass()
