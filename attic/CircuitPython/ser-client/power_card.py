# Analog Card Detection Circuit notes:
# * By providing 3.3V input lines with differing resistance on each line, we can combine the lines in a parallel circuit
#   that will have a unique total resistance for each combination of input lines.
#   * Remember that the overall resistance of a parallel circuit is expressed by the reciprocal of the sum of the
#     reciprocals of the individual line voltages:
#     * 1 / Rtot = 1 / R1 + 1/R2 + ... + 1/Rn

# * In order to make the sensor work, we place the analog sensor pin in the middle of a +3.3V -> GND voltage divider
#   with a fixed R1 resistor on the ground side, essentially creating a "binary potentiometer".  In the chart below, I
#   am showing the Vtot as the voltage drop of the variable side of the divider.

# * This chart indicates the actual resistance and sensor voltage along with the raw analog sensor signal, and the
#   maximum 'safe' raw signal delta for all permutations of 5 input lines with these resistance values [R1: 10Kohm, R2:
#   4.7Kohm, R3: 2.2Kohm, R4: 1Kohm, R5: 470ohm ] and a voltage divider resistor of 470ohm.
#   *  Card No   R1     R2    R3    R4    R5   Rtot    Vtot  dSig
#   *        0   0      0     0     0     0    -       -     -
#   *       16   10000  0     0     0     0    10,000  1.76  0.031
#   *        8   0      4700  0     0     0    4,700   1.84  0.026
#   *       24   10000  4700  0     0     0    3,197   1.90  0.026
#   *        4   0      0     2200  0     0    2,200   1.99  0.024
#   *       20   10000  0     2200  0     0    1,803   2.05  0.024
#   *       12   0      4700  2200  0     0    1,499   2.11  0.022
#   *       28   10000  4700  2200  0     0    1,303   2.17  0.022
#   *        2   0      0     0     1000  0    1,000   2.29  0.019
#   *       18   10000  0     0     1000  0    909     2.33  0.019
#   *       10   0      4700  0     1000  0    825     2.39  0.018
#   *       26   10000  4700  0     1000  0    762     2.43  0.018
#   *        6   0      0     2200  1000  0    688     2.49  0.016
#   *       22   10000  0     2200  1000  0    643     2.53  0.016
#   *       14   0      4700  2200  1000  0    600     2.58  0.015
#   *       30   10000  4700  2200  1000  0    566     2.62  0.015
#   *        1   0      0     0     0     470  470     2.75  0.013
#   *       17   10000  0     0     0     470  449     2.78  0.013
#   *       9    0      4700  0     0     470  427     2.82  0.013
#   *       25   10000  4700  0     0     470  410     2.85  0.013
#   *        5   0      0     2200  0     470  387     2.89  0.012
#   *       21   10000  0     2200  0     470  373     2.92  0.012
#   *       13   0      4700  2200  0     470  358     2.95  0.011
#   *       29   10000  4700  2200  0     470  345     2.98  0.011
#   *        3   0      0     0     1000  470  320     3.04  0.010
#   *       19   10000  0     0     1000  470  310     3.06  0.010
#   *       11   0      4700  0     1000  470  299     3.09  0.010
#   *       27   10000  4700  0     1000  470  291     3.12  0.010
#   *        7   0      0     2200  1000  470  279     3.15  0.009
#   *       23   10000  0     2200  1000  470  272     3.17  0.009
#   *       15   0      4700  2200  1000  470  264     3.20  0.009
#   *       31   10000  4700  2200  1000  470  257     3.22  0.009
#
# Definition of 'safe' raw signal delta: In practice, with the tolerance of the resistors that I am using, the raw
# sensor values are usually within 2-3 units of the expected value. Having said that, it still makes sense to be as
# generous as possible with our voltage detection, so I checked the delta(sensor) values of all asjacent sensor
# readings, and calculated a 'safe' signal delta (fudge factor) as being 80% of 1/2 of the delta from each expected
# signal value to the nearest adjacent signal value.  Even with this safe signal delta, it still makes sense to encode
# the cards with the widest sensor range first, so I've also sorted the above list in reverse order of safe signal
# delta. You should encode the cards in the order shown above.

_ALL_POWER_CARDS: list["PowerCard"] = []


class PowerCard:
    @classmethod
    def InitializePowerCards(cls):
        global _ALL_POWER_CARDS
        _ALL_POWER_CARDS = []
        _ALL_POWER_CARDS.append(PowerCard(1, 50, 1.655, 0.015))
        _ALL_POWER_CARDS.append(PowerCard(2, 80, 1.058, 0.028))
        _ALL_POWER_CARDS.append(PowerCard(3, 50, 1.97, 0.01))
        _ALL_POWER_CARDS.append(PowerCard(4, 40, 0.583, 0.041))
        _ALL_POWER_CARDS.append(PowerCard(5, 90, 1.815, 0.012))
        _ALL_POWER_CARDS.append(PowerCard(6, 10, 1.344, 0.021))
        _ALL_POWER_CARDS.append(PowerCard(7, 10, 2.077, 0.008))
        _ALL_POWER_CARDS.append(PowerCard(8, 60, 0.301, 0.049))
        _ALL_POWER_CARDS.append(PowerCard(9, 30, 1.734, 0.014))
        _ALL_POWER_CARDS.append(PowerCard(10, 30, 1.202, 0.025))
        _ALL_POWER_CARDS.append(PowerCard(11, 30, 2.022, 0.009))
        _ALL_POWER_CARDS.append(PowerCard(12, 60, 0.79, 0.035))
        _ALL_POWER_CARDS.append(PowerCard(13, 70, 1.879, 0.011))
        _ALL_POWER_CARDS.append(PowerCard(14, 70, 1.454, 0.019))
        _ALL_POWER_CARDS.append(PowerCard(15, 50, 2.121, 0.008))
        _ALL_POWER_CARDS.append(PowerCard(16, 50, 0.149, 0.059))
        _ALL_POWER_CARDS.append(PowerCard(17, 40, 1.693, 0.015))
        _ALL_POWER_CARDS.append(PowerCard(18, 90, 1.128, 0.028))
        _ALL_POWER_CARDS.append(PowerCard(19, 40, 1.995, 0.01))
        _ALL_POWER_CARDS.append(PowerCard(20, 50, 0.684, 0.041))
        _ALL_POWER_CARDS.append(PowerCard(21, 80, 1.846, 0.012))
        _ALL_POWER_CARDS.append(PowerCard(22, 80, 1.397, 0.021))
        _ALL_POWER_CARDS.append(PowerCard(23, 40, 2.098, 0.008))
        _ALL_POWER_CARDS.append(PowerCard(24, 30, 0.424, 0.049))
        _ALL_POWER_CARDS.append(PowerCard(25, 20, 1.768, 0.014))
        _ALL_POWER_CARDS.append(PowerCard(26, 20, 1.263, 0.025))
        _ALL_POWER_CARDS.append(PowerCard(27, 20, 2.045, 0.009))
        _ALL_POWER_CARDS.append(PowerCard(28, 70, 0.877, 0.035))
        _ALL_POWER_CARDS.append(PowerCard(29, 60, 1.908, 0.011))
        _ALL_POWER_CARDS.append(PowerCard(30, 20, 1.502, 0.019))
        _ALL_POWER_CARDS.append(PowerCard(31, 70, 2.141, 0.008))

    @classmethod
    def CheckSensorMatch(cls, sensorVoltage) -> "PowerCard":
        matches = [card for card in _ALL_POWER_CARDS if card.MatchesValue(sensorVoltage)]
        if len(matches) > 1:
            badCards = ", ".join(map(lambda x: f"{x.CardName}({x.UID})", matches))
            raise Exception(f"PowerCard: Multiple PowerCards match sensorVoltage '{sensorVoltage}': {badCards}")
        return matches[0] if len(matches) > 0 else None

    def __init__(self, uid, requiredPower, cardVoltage, dVoltage, cardName=None):
        duplicates = [card for card in _ALL_POWER_CARDS if card.UID == uid]

        if len(duplicates) > 0:
            raise Exception(
                f"PowerCard({uid}/{cardName}): duplicate UID with card {duplicates[0].UID}/{duplicates[0].CardName}"
            )

        self.uid = int(uid)
        self.requiredPower = int(requiredPower)
        self.normalizedValue = float(cardVoltage)
        self.deltaValue = float(dVoltage)
        self.cardName = cardName if cardName else f"C{uid:02d}"

        if self.normalizedValue <= 0 or self.normalizedValue >= 5:
            raise ValueError(f"PowerCard({uid}): Invalid cardVoltage: {cardVoltage}")
        if self.deltaValue <= 0 or self.deltaValue >= 5:
            raise ValueError(f"PowerCard({uid}): Invalid dVoltage: {dVoltage}")

        overlaps = [
            card for card in _ALL_POWER_CARDS if card.MaxValue >= self.MinValue and card.MinValue <= self.MaxValue
        ]

        if len(overlaps) > 0:
            raise Exception(
                f"PowerCard({uid}/{cardName}): voltage range overlaps with card {overlaps[0].UID}/{overlaps[0].CardName}"
            )

    @property
    def UID(self) -> int:
        return self.uid

    @property
    def CardName(self) -> str:
        return self.cardName

    @property
    def NormalizedCardValue(self) -> float:
        return self.normalizedValue

    @property
    def DeltaValue(self) -> float:
        return self.deltaValue

    @property
    def MinValue(self) -> float:
        return self.normalizedValue - self.deltaValue

    @property
    def MaxValue(self) -> float:
        return self.normalizedValue + self.deltaValue

    def MatchesValue(self, sensorValue) -> bool:
        return abs(self.normalizedValue - sensorValue) < self.deltaValue

    @property
    def RequiredPower(self):
        return self.requiredPower

    def __str__(self):
        return f"{self.UID}/{self.CardName}"
