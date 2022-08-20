import time
import board
import adafruit_logging as logging
import neopixel

from utils import ENABLE_PIXELS, disabledString

# Power Consumption notes: Powering 768 red (255,0,0) pixels at 10% brightness pulls 1.35 amps, according to my
# multimeter.  Increasing the brightness to 0.2 draws 2.3 amps.  If you increase the brightness, make sure that your
# power supply can handle the current draw
PIXEL_BRIGHTNESS = 0.1
#  #px | Color         | Current Draw @ brightness = 0.1
#  768 |   0,   0,  0  | 0.64
#  768 | 255,   0,  0  | 1.35
#  768 |   0, 255,  0  | 1.33
#  768 |   0,   0, 255 | 1.33
#  768 | 255, 255,   0 | 2.04
#  768 | 255,   0, 255 | 2.04
#  768 |   0, 255, 255 | 2.02
#  768 | 255, 255, 255 | 2.55

# Usually the component color updaters will send the pixel data as part of the update.  The PixelManager will
# automatically re-send the pixel data this often, in case an update is missed
PIXEL_REFRESH_SECONDS = 0.25

logger = logging.getLogger("PixelManager")

LED_DATA_PIN = board.D32

PIXEL_GRID_COUNT = 6

LARGE_GRID_COUNT = 2
LARGE_GRID_SIZE = 16
LEDS_PER_LARGE_GRID = LARGE_GRID_SIZE * LARGE_GRID_SIZE
LARGE_GRID_LED_BASE_INDEX = 0

SMALL_GRID_COUNT = 4
SMALL_GRID_SIZE = 8
LEDS_PER_SMALL_GRID = SMALL_GRID_SIZE * SMALL_GRID_SIZE
SMALL_GRID_LED_BASE_INDEX = LARGE_GRID_LED_BASE_INDEX + LEDS_PER_LARGE_GRID * LARGE_GRID_COUNT

READER_COUNT = 0
LEDS_PER_READER = 11
READERS_LED_BASE_INDEX = SMALL_GRID_LED_BASE_INDEX + LEDS_PER_SMALL_GRID * SMALL_GRID_COUNT

TOTAL_LED_COUNT = READERS_LED_BASE_INDEX + READER_COUNT * LEDS_PER_READER

# Pixel Map
# Large Grid #0 - 256 px
# Large Grid #1 - 256 px
# Small Grid #2 - 64 px
# Small Grid #3 - 64 px
# Small Grid #4 - 64 px
# Small Grid #5 - 64 px

PixelGridLEDStartIndex = {
    0 : LARGE_GRID_LED_BASE_INDEX,
    1 : LARGE_GRID_LED_BASE_INDEX + LEDS_PER_LARGE_GRID,
    2 : SMALL_GRID_LED_BASE_INDEX,
    3 : SMALL_GRID_LED_BASE_INDEX + LEDS_PER_SMALL_GRID,
    4 : SMALL_GRID_LED_BASE_INDEX + LEDS_PER_SMALL_GRID * 2,
    5 : SMALL_GRID_LED_BASE_INDEX + LEDS_PER_SMALL_GRID * 3,
}

PixelGridLEDLength = {
    0 : LEDS_PER_LARGE_GRID,
    1 : LEDS_PER_LARGE_GRID,
    2 : LEDS_PER_SMALL_GRID,
    3 : LEDS_PER_SMALL_GRID,
    4 : LEDS_PER_SMALL_GRID,
    5 : LEDS_PER_SMALL_GRID,
}

PixelGridSize = {
    0 : LARGE_GRID_SIZE,
    1 : LARGE_GRID_SIZE,
    2 : SMALL_GRID_SIZE,
    3 : SMALL_GRID_SIZE,
    4 : SMALL_GRID_SIZE,
    5 : SMALL_GRID_SIZE,
}

BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

logger = logging.getLogger("PixelManager")

class PixelManagerClass:
    def __init__(self):
        self.pixels = None
        self.__nextPixelUpdate = time.monotonic() + PIXEL_REFRESH_SECONDS
        self.heartbeatColor = BLUE
        self.heartbeatFreq = 4
        self.heartbeatCount = 0
        self.powerGridPixels = 0
        
        if ENABLE_PIXELS:
            self.enabledString = "";
            self.pixels = neopixel.NeoPixel(
                LED_DATA_PIN,
                TOTAL_LED_COUNT,
                brightness=PIXEL_BRIGHTNESS,
                auto_write=False,
                pixel_order="GRB",
            )
            self.pixels.fill(BLACK)
            self.pixels.show()

        logger.info(f"Created PixelManager{disabledString(ENABLE_PIXELS)} with {TOTAL_LED_COUNT} pixels")

    def SetReaderColor(self, readerIndex: int, color: tuple):
        if readerIndex < 0 or readerIndex >= READER_COUNT:
            logger.error(f"Reader index {readerIndex} is out of range.")
            return

        logger.info(f"PixelManager{disabledString(ENABLE_PIXELS)}: Setting CardReader #{readerIndex} to color: {color}")

        readerPixelIndexStart = READERS_LED_BASE_INDEX + readerIndex * LEDS_PER_READER
        readerPixelIndexEnd = readerPixelIndexStart + LEDS_PER_READER

        if ENABLE_PIXELS:
            for pixelIndex in range(readerPixelIndexStart, readerPixelIndexEnd):
                self.pixels[pixelIndex] = color

    def SetPowerGridColor(self, gridIndex: int, x: int, y: int, color: tuple):
        if gridIndex < 0 or gridIndex >= PIXEL_GRID_COUNT:
            logger.error(f"Pixel Grid index {gridIndex} is out of range.")
            return

        gridSize = PixelGridSize[gridIndex]

        if x < 0 or x >= gridSize or y < 0 or y >= gridSize:
            logger.error(f"Pixel Grid index {gridIndex} coordinates ({x}, {y}) is out of range.")
            return

        gridPixelIndex = PixelGridLEDStartIndex[gridIndex] + y * gridSize

        # The pixel grids that we are using map the pixels as a zig-zag linear string: Pixel zero starts at the
        # bottom-left of the grid, and the pixels increment to the right until the string reaches the edge of the grid.
        # Then the string moves up one pixel, and proceeds incrementing to the left.
        if y % 2 == 0:
            gridPixelIndex += x
        else:
            gridPixelIndex += (gridSize - 1) - x

        self.powerGridPixels += 1
        # logger.info(f"PixelManager{disabledString(ENABLE_PIXELS)}: Setting PixelGrid #{gridIndex}({x}, {y}) (LED index {gridPixelIndex})to color: {color}")

        if ENABLE_PIXELS:
            self.pixels[gridPixelIndex] = color

    def ShowPixels(self):
        if ENABLE_PIXELS:
            self.pixels.show()

    def UpdatePixelData(self):
        if not ENABLE_PIXELS:
            return

        if time.monotonic() > self.__nextPixelUpdate:
            if self.heartbeatFreq > 0:
                self.heartbeatCount += 1
                if self.heartbeatCount >= self.heartbeatFreq:
                    self.heartbeatCount = 0
                    self.heartbeatColor = BLACK if self.heartbeatColor == BLUE else BLUE
                    self.powerGridPixels = 0
                self.pixels[0] = self.heartbeatColor

            self.__nextPixelUpdate = time.monotonic() + PIXEL_REFRESH_SECONDS
            self.pixels.show()

    def CylonTest(self):
        logger.info("Running Cylon Pixel Test")

        testCount = 768
        brightness = 0.1

        CYLON_COLOR = (255, 0, 0)
        BASE_COLOR = (0, 0, 0)

        cylon = 0
        prevCylon = 0

        cylonSpeed = 0.01
        cylonCount = 0
        self.pixels.fill(BASE_COLOR)

        while True:
            self.pixels[prevCylon] = BASE_COLOR
            self.pixels[cylon] = CYLON_COLOR

            prevCylon = cylon
            cylon += 1

            if cylon % 100 == 0:
                logger.info(f"Cylon Pixel Test color: {BASE_COLOR}, brightness: {brightness} {cylon}/{testCount}")

            if cylon >= testCount:
                cylonCount += 1
                logger.info(f"Cylon Pixel Test {cylonCount}")
                cylon = 0

            self.pixels.show()


    def __str__(self):
        return f"PixelManager{disabledString(ENABLE_PIXELS)}"


PixelManager = PixelManagerClass()
