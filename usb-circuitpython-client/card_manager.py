import board
import keypad
import adafruit_logging as logging
from power_card import PowerCard
from utils import ENABLE_CARD_READER, disabledString

logger = logging.getLogger("CardReaderManager")

class CardReader:
    def __init__(self, uid: int, readerKeysState: list[bool], readerKeys: list[int]):
        self.uid = int(uid)
        if len(readerKeys) != 5:
            raise Exception(f"{self}: Invalid reader keys count: {len(readerKeys)}")
        self.readerKeys = readerKeys

        keysStateValid = True
        for checkIndex in readerKeys:
            keysStateValid = keysStateValid and len(readerKeysState) > checkIndex

        if not keysStateValid:
            raise Exception(
                f"{self}: Invalid readerKeysState: does not contain a value for every readerKeys index: {readerKeys}"
            )

        self.readerKeysState = readerKeysState

        logger.info(f"Created CardReader: {self}")

    @property
    def UID(self) -> int:
        return self.uid

    @property
    def CardPresent(self) -> PowerCard:
        cardId = 0
        for (i, keyIndex) in enumerate(self.readerKeys):
            if self.readerKeysState[keyIndex]:
                cardId += 1 << i

        card = PowerCard.FindCard(cardId)
        return card

    @property
    def CardID(self) -> int:
        card = self.CardPresent
        return card.UID if card else None

    def __str__(self):
        keysStr = ",".join(str(keyIndex) for keyIndex in self.readerKeys)
        retval = f"{self.UID}/{keysStr}{disabledString(ENABLE_CARD_READER)}"
        return retval


class CardReaderManagerClass:
    def __init__(self) -> None:
        self.keypadManager = None

        if ENABLE_CARD_READER:
            self.keypadManager = keypad.KeyMatrix(
                row_pins=(board.D20, board.D21, board.D22, board.D23, board.D24, board.D25),
                column_pins=(board.D26, board.D27, board.D28, board.D29, board.D30), 
                columns_to_anodes=True,
                interval=0.05
            )

        self.currentKeyStatus = [False] * 10

        self._ALL_CARD_READERS: list["CardReader"] = []
        self._ALL_CARD_READERS = []
        self._ALL_CARD_READERS.append(CardReader(1, self.currentKeyStatus, [0, 1, 2, 3, 4]))
        self._ALL_CARD_READERS.append(CardReader(2, self.currentKeyStatus, [5, 6, 7, 8, 9]))

    def UpdateReaderState(self):
        if not ENABLE_CARD_READER:
            return

        if self.keypadManager.events.overflowed:
            logger.error(f"############################ KeypadManager overflow! ############################")
            self.keypadManager.events.clear()
            self.keypadManager.reset()

        checkEvent = self.keypadManager.events.get()
        while checkEvent:
            keyIndex = checkEvent.key_number
            keyDown = checkEvent.pressed
            if self.currentKeyStatus[keyIndex] != keyDown:
                logger.info(f"Got Key event: {keyIndex} {keyDown}")
            self.currentKeyStatus[keyIndex] = keyDown
            checkEvent = self.keypadManager.events.get()

    def AllReaders(self) -> list[CardReader]:
        self.UpdateReaderState()
        return self._ALL_CARD_READERS

    def ReaderStatus(self) -> list[int]:
        self.UpdateReaderState()
        return [reader.CardID for reader in self._ALL_CARD_READERS if reader.CardID is not None]

    def ReaderCards(self) -> list[str]:
        self.UpdateReaderState()
        retval = [f"R({reader.UID}){disabledString(ENABLE_CARD_READER)}: {reader.CardPresent.CardName}" for reader in self._ALL_CARD_READERS if reader.CardPresent is not None]
        return retval


CardReaderManager = CardReaderManagerClass()
