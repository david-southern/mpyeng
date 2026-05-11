import array
import random

from power_cards.animation import CARD_GRID_PIXELS, CardAnimationHelpers
from power_cards.card_ids import PowerCardIds

CARD_VOLTAGE_THRESHOLD = 0.05

# All-zero pixel buffer used as a "no card / blank" frame. array.array('I'), one neo-packed
# int per pixel, matching the format every animation frame uses post-bake.
BLACK_BUFFER = array.array("I", [0] * CARD_GRID_PIXELS)


class PowerCard:
    __ALL_POWER_CARDS = []

    @classmethod
    def GetAllPowerCards(cls) -> list["PowerCard"]:
        return PowerCard.__ALL_POWER_CARDS

    @classmethod
    def FindCard(cls, cardVoltage) -> "PowerCard | None":
        matchingCards = [card for card in PowerCard.__ALL_POWER_CARDS if card.VoltageMatches(cardVoltage)]
        return matchingCards[0] if len(matchingCards) > 0 else None

    @classmethod
    def RandomCard(cls) -> "PowerCard | None":
        return PowerCard.__ALL_POWER_CARDS[random.randint(0, len(PowerCard.__ALL_POWER_CARDS) - 1)]

    def __init__(self, cardId: str, cardVoltage: float, requiredPower: int):
        if not PowerCardIds.validate_id(cardId):
            raise Exception(f"PowerCard: unknown card_id: {cardId}")

        self.__cardAnimation = CardAnimationHelpers.getCardAnimation(cardId)

        if not self.__cardAnimation:
            raise Exception(f"PowerCard({cardId}): no animation found for card id {cardId}")

        self.__cardId = cardId
        self.__cardName = self.__cardAnimation.name

        duplicates = [card for card in PowerCard.__ALL_POWER_CARDS if card.UID == cardId]

        if len(duplicates) > 0:
            raise Exception(
                f"PowerCard({cardId}/{self.__cardName}): duplicate UID with card {duplicates[0].UID}/{duplicates[0].CardName}"
            )

        self.__voltage = cardVoltage
        self.__requiredPower = int(requiredPower)

    @property
    def UID(self) -> str:
        return self.__cardId

    @property
    def CardName(self) -> str:
        return self.__cardName

    @property
    def CardAnimation(self):
        return self.__cardAnimation

    @property
    def RequiredPower(self):
        return self.__requiredPower

    def VoltageMatches(self, cardVoltage) -> bool:
        return abs(self.__voltage - cardVoltage) < CARD_VOLTAGE_THRESHOLD

    def AnimationFrame(self, animationProgress: float):
        if self.__cardAnimation is not None:
            return self.__cardAnimation.AnimationFrame(animationProgress)
        else:
            return -1

    def PixelBuffer(self, animationFrame: int):
        """Return the baked pixel buffer for <animationFrame> (an array.array('I') of
        neo-packed pixel ints), or BLACK_BUFFER if there's no animation or the frame index
        is invalid."""
        if self.__cardAnimation is not None and animationFrame >= 0:
            return self.__cardAnimation.PixelBuffer(animationFrame)
        else:
            return BLACK_BUFFER

    def __str__(self):
        return f"{self.UID}/{self.CardName}({self.__voltage:.2f}V)"


PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.FUSION_ENGINES_ID, 0.10, 50))
PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.LONG_RANGE_COMMS_ID, 2.00, 50))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.WARP_FIELD_ID, 0.20, 80))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.TRANSPORTERS_ID, 2.20, 80))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.MAIN_COMPUTER_ID, 0.30, 50))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.FORE_SHIELDS_ID, 0.40, 40))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.AFT_SHIELDS_ID, 0.50, 90))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.PORT_SHIELDS_ID, 0.60, 10))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.STARBOARD_SHIELDS_ID, 0.70, 10))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.DORSAL_SHIELDS_ID, 0.80, 60))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.VENTRAL_SHIELDS_ID, 0.90, 30))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.LASER_CANNON_ID, 1.00, 30))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.TRACTOR_BEAM_ID, 1.10, 30))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.STEALTH_FIELDS_ID, 1.20, 60))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.TARGETING_ID, 1.30, 70))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.SIGNAL_JAMMER_ID, 1.40, 70))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.ALCUBIERRE_WARP_DRIVE_ID, 1.50, 50))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.THRUSTERS_ID, 1.60, 50))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.NAVIGATION_ID, 1.70, 40))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.EXTERNAL_SENSORS_ID, 1.80, 90))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.INTERNAL_SENSORS_ID, 1.90, 40))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.RADIO_COMMUNICATIONS_ID, 2.10, 80))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.CO2_SCRUBBERS_ID, 2.30, 40))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.OXYGEN_GENERATORS_ID, 2.40, 30))
# PowerCard.__ALL_POWER_CARDS.append(PowerCard(PowerCardIds.GRAVITY_FIELD_ID, 2.50, 20))
