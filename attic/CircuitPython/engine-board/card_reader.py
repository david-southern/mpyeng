import board
from analogio import AnalogIn
import adafruit_logging as logging
from power_card import PowerCard
import neopixel
from utils import BLACK, BLUE, LED_COUNT, LED_DATA_PIN, LEDS_PER_READER, READER_MAX_VOLTAGE

_ALL_CARD_READERS: list["CardReader"] = []

logger = logging.getLogger('CardReader')
pixels = neopixel.NeoPixel(LED_DATA_PIN, LED_COUNT,
                           brightness=1.0, auto_write=False, pixel_order="GRB")
pixels.fill(BLACK)
pixels.show()

logger.info(f"Creating {LED_COUNT} reader pixels")


class CardReader:
    # @classmethod
    # def InitializeCardReaders(cls):
    #     global _ALL_CARD_READERS
    #     _ALL_CARD_READERS = []
    #     _ALL_CARD_READERS.append(CardReader(1, board.A1))
    #     _ALL_CARD_READERS.append(CardReader(2, board.A2))
    #     _ALL_CARD_READERS.append(CardReader(3, board.A3))
    #     _ALL_CARD_READERS.append(CardReader(4, board.A4))
    #     _ALL_CARD_READERS.append(CardReader(5, board.A5))
    #     _ALL_CARD_READERS.append(CardReader(6, board.A6))
    #     _ALL_CARD_READERS.append(CardReader(7, board.A7))
    #     _ALL_CARD_READERS.append(CardReader(8, board.A8))
    #     _ALL_CARD_READERS.append(CardReader(9, board.A9))
    #     _ALL_CARD_READERS.append(CardReader(10, board.A10))

    @classmethod
    def AllReaders(cls) -> list["CardReader"]:
        return _ALL_CARD_READERS

    @classmethod
    def ShowPixels(cls):
        pixels.show()

    def __init__(self, uid, analogPin, baseLEDIndex=-1, ledCount=-1):
        global _ALL_CARD_READERS

        self.uid = uid
        self.analogPin = analogPin
        self.pinName = str(analogPin).replace("board.", "")
        self.baseLEDIndex = baseLEDIndex if baseLEDIndex > - \
            1 else len(_ALL_CARD_READERS) * LEDS_PER_READER
        self.ledCount = ledCount if ledCount > -1 else LEDS_PER_READER

        duplicates = [
            reader for reader in _ALL_CARD_READERS if reader.UID == uid]

        if(len(duplicates) > 0):
            raise Exception(
                f"CardReader({self}): duplicate UID with reader {duplicates[0]}")

        self.analogIn = AnalogIn(analogPin)

        overlaps = [
            reader for reader in _ALL_CARD_READERS if reader.AnalogPin == self.AnalogPin]
        if(len(overlaps) > 0):
            raise Exception(
                f"CardReader({self}): analog pin overlaps with reader {overlaps[0]}")

        overlaps = [reader for reader in _ALL_CARD_READERS if reader.MaxLEDIndex >=
                    self.MinLEDIndex and reader.MinLEDIndex <= self.MaxLEDIndex]
        if(len(overlaps) > 0):
            badCard = overlaps[0]
            raise Exception(f"CardReader({self}): LED range ({self.MinLEDIndex}-{self.MaxLEDIndex}) "
                            + f"overlaps with reader {badCard} LED range ({badCard.MinLEDIndex}-{badCard.MaxLEDIndex})")

        self.ledColor = None
        self.LEDColor = BLACK

        logger.info(f"Created CardReader: {self}")

        _ALL_CARD_READERS.append(self)

    @property
    def UID(self):
        return self.uid

    @property
    def AnalogPin(self):
        return self.analogPin

    @property
    def PinName(self):
        return self.pinName

    @property
    def BaseLEDIndex(self):
        return self.baseLEDIndex

    @property
    def LEDCount(self):
        return self.ledCount

    @property
    def MinLEDIndex(self):
        return self.baseLEDIndex

    @property
    def MaxLEDIndex(self):
        return self.baseLEDIndex + self.ledCount - 1

    @property
    def Voltage(self):
        return (self.analogIn.value * READER_MAX_VOLTAGE) / 65536

    @property
    def RefV(self):
        return self.analogIn.reference_voltage

    @property
    def CardPresent(self) -> PowerCard:
        card = PowerCard.CheckSensorMatch(self.Voltage)
        return card

    @property
    def LEDColor(self):
        return self.ledColor

    @LEDColor.setter
    def LEDColor(self, value):
        global pixels

        # if(self.ledColor != value):
        #     logger.info(f"Reader({self}) Set color {self.ledColor} pix {self.MinLEDIndex} - {self.MaxLEDIndex}")

        self.ledColor = value

        if(self.MinLEDIndex >= 0):
            for ledIndex in range(self.MinLEDIndex, self.MaxLEDIndex + 1):
                pixels[ledIndex] = self.ledColor

    def __str__(self):
        return f"{self.UID}/{self.PinName}"
