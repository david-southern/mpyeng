from __future__ import annotations

_ALL_POWER_CARDS: list[PowerCard]
CARD_VOLTAGE_THRESHOLD = 0.05


class PowerCard:
    @classmethod
    def FindCard(cls, cardVoltage) -> PowerCard | None:
        if _ALL_POWER_CARDS is None:
            InitializePowerCards()

        matchingCards = [
            card for card in _ALL_POWER_CARDS if card.VoltageMatches(cardVoltage)
        ]
        return matchingCards[0] if len(matchingCards) > 0 else None

    def __init__(self, uid, cardVoltage, requiredPower, cardName=None):
        duplicates = [card for card in _ALL_POWER_CARDS if card.UID == uid]

        if len(duplicates) > 0:
            raise Exception(
                f"PowerCard({uid}/{cardName}): duplicate UID with card {duplicates[0].UID}/{duplicates[0].CardName}"
            )

        self.uid = int(uid)
        self.voltage = cardVoltage
        self.requiredPower = int(requiredPower)
        self.cardName = cardName if cardName else f"C{uid:02d}"

    @property
    def UID(self) -> int:
        return self.uid

    @property
    def CardName(self) -> str:
        return self.cardName

    @property
    def RequiredPower(self):
        return self.requiredPower

    def VoltageMatches(self, cardVoltage) -> bool:
        return abs(self.voltage - cardVoltage) < CARD_VOLTAGE_THRESHOLD

    def __str__(self):
        return f"{self.UID}/{self.CardName}({self.voltage:.2f}V)"


def InitializePowerCards():
    global _ALL_POWER_CARDS
    _ALL_POWER_CARDS = []
    _ALL_POWER_CARDS.append(PowerCard(1, 0.10, 50))
    _ALL_POWER_CARDS.append(PowerCard(2, 0.20, 80))
    _ALL_POWER_CARDS.append(PowerCard(3, 0.30, 50))
    _ALL_POWER_CARDS.append(PowerCard(4, 0.40, 40))
    _ALL_POWER_CARDS.append(PowerCard(5, 0.50, 90))
    _ALL_POWER_CARDS.append(PowerCard(6, 0.60, 10))
    _ALL_POWER_CARDS.append(PowerCard(7, 0.70, 10))
    _ALL_POWER_CARDS.append(PowerCard(8, 0.80, 60))
    _ALL_POWER_CARDS.append(PowerCard(9, 0.90, 30))
    _ALL_POWER_CARDS.append(PowerCard(10, 1.00, 30))
    _ALL_POWER_CARDS.append(PowerCard(11, 1.10, 30))
    _ALL_POWER_CARDS.append(PowerCard(12, 1.20, 60))
    _ALL_POWER_CARDS.append(PowerCard(13, 1.30, 70))
    _ALL_POWER_CARDS.append(PowerCard(14, 1.40, 70))
    _ALL_POWER_CARDS.append(PowerCard(15, 1.50, 50))
    _ALL_POWER_CARDS.append(PowerCard(16, 1.60, 50))
    _ALL_POWER_CARDS.append(PowerCard(17, 1.70, 40))
    _ALL_POWER_CARDS.append(PowerCard(18, 1.80, 90))
    _ALL_POWER_CARDS.append(PowerCard(19, 1.90, 40))
    _ALL_POWER_CARDS.append(PowerCard(20, 2.00, 50))
    _ALL_POWER_CARDS.append(PowerCard(21, 2.10, 80))
    _ALL_POWER_CARDS.append(PowerCard(22, 2.20, 80))
    _ALL_POWER_CARDS.append(PowerCard(23, 2.30, 40))
    _ALL_POWER_CARDS.append(PowerCard(24, 2.40, 30))
    _ALL_POWER_CARDS.append(PowerCard(25, 2.50, 20))
    _ALL_POWER_CARDS.append(PowerCard(26, 2.60, 20))
    _ALL_POWER_CARDS.append(PowerCard(27, 2.70, 20))
    _ALL_POWER_CARDS.append(PowerCard(28, 2.80, 70))
    _ALL_POWER_CARDS.append(PowerCard(29, 2.90, 60))
    _ALL_POWER_CARDS.append(PowerCard(30, 3.00, 20))
    _ALL_POWER_CARDS.append(PowerCard(31, 3.10, 70))
