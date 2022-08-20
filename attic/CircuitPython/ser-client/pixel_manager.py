import board
import adafruit_logging as logging
import neopixel

LED_DATA_PIN = board.D27
READER_COUNT = 10
LEDS_PER_READER = 11

BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

logger = logging.getLogger("PixelManager")


class PixelManagerClass:
    def __init__(self):
        self.BaseReaderLEDIndex = 0
        self.LedsPerReader = 11

        self.TotalLEDCount = READER_COUNT * LEDS_PER_READER

        self.pixels = neopixel.NeoPixel(
            LED_DATA_PIN,
            self.TotalLEDCount,
            brightness=1.0,
            auto_write=False,
            pixel_order="GRB",
        )
        self.pixels.fill(BLACK)
        self.pixels.show()

        logger.info(f"Created PixelManager with {self.TotalLEDCount} pixels for {READER_COUNT} readers")

    def SetReaderColor(self, readerIndex: int, color: tuple):
        if readerIndex < 0 or readerIndex >= READER_COUNT:
            logger.error(f"Reader index {readerIndex} is out of range.")
            return

        logger.info(f"Setting CardReader index {readerIndex} to color: {color}")

        readerPixelIndexStart = self.BaseReaderLEDIndex + readerIndex * self.LedsPerReader
        readerPixelIndexEnd = readerPixelIndexStart + self.LedsPerReader

        for pixelIndex in range(readerPixelIndexStart, readerPixelIndexEnd):
            self.pixels[pixelIndex] = color

    def ShowPixels(self):
        self.pixels.show()

    def __str__(self):
        return f"{self.UID}/{self.PinName}"


PixelManager = PixelManagerClass()
