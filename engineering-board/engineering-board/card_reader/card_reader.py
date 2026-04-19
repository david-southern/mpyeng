import time

from power_cards.power_card import PowerCard
from utils.eng_utils import ENABLE_CARD_READER, disabledString, logger
from utils.mcp3008 import _AnalogIn
from card_reader.constants import VOLTAGE_CHECK_FREQUENCY


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
        logger.info(f"CardReader({self}): Checking pin present - voltage {self.inputPin.voltage}")

        self.lastCard = PowerCard.FindCard(self.inputPin.voltage)
        return self.lastCard

    @property
    def CardID(self) -> str | None:
        card = self.CardPresent
        return card.UID if card else None

    def __str__(self):
        retval = f"{self.uid}{disabledString(ENABLE_CARD_READER)}"
        return retval
