_ALL_POWER_CARDS: list["PowerCard"] = None

class PowerCard:
    @classmethod
    def FindCard(cls, cardId) -> "PowerCard":
        if(cardId == 0):
            return None
            
        if(_ALL_POWER_CARDS is None):
            InitializePowerCards()

        if(cardId < 0) or (cardId > len(_ALL_POWER_CARDS)):
            raise Exception(f"PowerCard.FindCard({cardId}): invalid card ID")

        return _ALL_POWER_CARDS[cardId - 1]

    def __init__(self, uid, requiredPower, cardName=None):
        duplicates = [card for card in _ALL_POWER_CARDS if card.UID == uid]

        if len(duplicates) > 0:
            raise Exception(
                f"PowerCard({uid}/{cardName}): duplicate UID with card {duplicates[0].UID}/{duplicates[0].CardName}"
            )

        self.uid = int(uid)
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

    def __str__(self):
        return f"{self.UID}/{self.CardName}"

def InitializePowerCards():
    global _ALL_POWER_CARDS
    _ALL_POWER_CARDS = []
    _ALL_POWER_CARDS.append(PowerCard(1,  50))
    _ALL_POWER_CARDS.append(PowerCard(2,  80))
    _ALL_POWER_CARDS.append(PowerCard(3,  50))
    _ALL_POWER_CARDS.append(PowerCard(4,  40))
    _ALL_POWER_CARDS.append(PowerCard(5,  90))
    _ALL_POWER_CARDS.append(PowerCard(6,  10))
    _ALL_POWER_CARDS.append(PowerCard(7,  10))
    _ALL_POWER_CARDS.append(PowerCard(8,  60))
    _ALL_POWER_CARDS.append(PowerCard(9,  30))
    _ALL_POWER_CARDS.append(PowerCard(10, 30))
    _ALL_POWER_CARDS.append(PowerCard(11, 30))
    _ALL_POWER_CARDS.append(PowerCard(12, 60))
    _ALL_POWER_CARDS.append(PowerCard(13, 70))
    _ALL_POWER_CARDS.append(PowerCard(14, 70))
    _ALL_POWER_CARDS.append(PowerCard(15, 50))
    _ALL_POWER_CARDS.append(PowerCard(16, 50))
    _ALL_POWER_CARDS.append(PowerCard(17, 40))
    _ALL_POWER_CARDS.append(PowerCard(18, 90))
    _ALL_POWER_CARDS.append(PowerCard(19, 40))
    _ALL_POWER_CARDS.append(PowerCard(20, 50))
    _ALL_POWER_CARDS.append(PowerCard(21, 80))
    _ALL_POWER_CARDS.append(PowerCard(22, 80))
    _ALL_POWER_CARDS.append(PowerCard(23, 40))
    _ALL_POWER_CARDS.append(PowerCard(24, 30))
    _ALL_POWER_CARDS.append(PowerCard(25, 20))
    _ALL_POWER_CARDS.append(PowerCard(26, 20))
    _ALL_POWER_CARDS.append(PowerCard(27, 20))
    _ALL_POWER_CARDS.append(PowerCard(28, 70))
    _ALL_POWER_CARDS.append(PowerCard(29, 60))
    _ALL_POWER_CARDS.append(PowerCard(30, 20))
    _ALL_POWER_CARDS.append(PowerCard(31, 70))

