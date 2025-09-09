from __future__ import annotations

from math import floor
import time
import board

from neopixel import NeoPixel  # pyright: ignore[reportMissingImports]
from eng_utils import disabledString, logger, ENABLE_PIXELS

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

LED_DATA_PIN = board.D7

PIXEL_GRID_COUNT = 6

LARGE_GRID_COUNT = 2
LARGE_GRID_SIZE = 16
LEDS_PER_LARGE_GRID = LARGE_GRID_SIZE * LARGE_GRID_SIZE
LARGE_GRID_LED_BASE_INDEX = 0

SMALL_GRID_COUNT = 4
SMALL_GRID_SIZE = 8
LEDS_PER_SMALL_GRID = SMALL_GRID_SIZE * SMALL_GRID_SIZE
SMALL_GRID_LED_BASE_INDEX = (
    LARGE_GRID_LED_BASE_INDEX + LEDS_PER_LARGE_GRID * LARGE_GRID_COUNT
)

CARD_BUS_COUNT = 6
CARDS_PER_BUS = 5
LEDS_PER_CARD = 25

TRAYS_PER_BUS = 2
TRAY_LEDS_PER_CARD = 4
LEDS_PER_TRAY = TRAY_LEDS_PER_CARD * CARDS_PER_BUS

CARDS_LED_BASE_INDEX = (
    SMALL_GRID_LED_BASE_INDEX + LEDS_PER_SMALL_GRID * SMALL_GRID_COUNT
)
CARD_TRAYS_LED_BASE_INDEX = (
    CARDS_LED_BASE_INDEX + CARD_BUS_COUNT * CARDS_PER_BUS * LEDS_PER_CARD
)

TOTAL_LED_COUNT = (
    CARD_TRAYS_LED_BASE_INDEX + CARD_BUS_COUNT * TRAYS_PER_BUS * LEDS_PER_TRAY
)

BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class PixelManagerClass:
    PixelGridLEDStartIndex = [
        LARGE_GRID_LED_BASE_INDEX,
        LARGE_GRID_LED_BASE_INDEX + LEDS_PER_LARGE_GRID,
        SMALL_GRID_LED_BASE_INDEX,
        SMALL_GRID_LED_BASE_INDEX + LEDS_PER_SMALL_GRID,
        SMALL_GRID_LED_BASE_INDEX + LEDS_PER_SMALL_GRID * 2,
        SMALL_GRID_LED_BASE_INDEX + LEDS_PER_SMALL_GRID * 3,
    ]

    PixelGridLEDLength = [
        LEDS_PER_LARGE_GRID,
        LEDS_PER_LARGE_GRID,
        LEDS_PER_SMALL_GRID,
        LEDS_PER_SMALL_GRID,
        LEDS_PER_SMALL_GRID,
        LEDS_PER_SMALL_GRID,
    ]

    PixelGridSize = [
        LARGE_GRID_SIZE,
        LARGE_GRID_SIZE,
        SMALL_GRID_SIZE,
        SMALL_GRID_SIZE,
        SMALL_GRID_SIZE,
        SMALL_GRID_SIZE,
    ]

    CardLEDStartIndex: list[list[int]] = []
    CardTrayLEDStartIndex: list[list[list[int]]] = []

    @classmethod
    def classInitialize(cls):
        if len(cls.CardLEDStartIndex) < 1:
            PixelManagerClass.CardLEDStartIndex = [
                [
                    CARDS_LED_BASE_INDEX + (bus * CARDS_PER_BUS + card) * LEDS_PER_CARD
                    for card in range(CARDS_PER_BUS)
                ]
                for bus in range(CARD_BUS_COUNT)
            ]

        if len(cls.CardTrayLEDStartIndex) < 1:
            PixelManagerClass.CardTrayLEDStartIndex = [
                [
                    [
                        CARD_TRAYS_LED_BASE_INDEX
                        + (bus * TRAYS_PER_BUS + tray) * LEDS_PER_TRAY
                        + card * TRAY_LEDS_PER_CARD
                        for card in range(CARDS_PER_BUS)
                    ]
                    for tray in range(TRAYS_PER_BUS)
                ]
                for bus in range(CARD_BUS_COUNT)
            ]

    def __init__(self):
        PixelManagerClass.classInitialize()
        self.__nextPixelUpdate = time.monotonic() + PIXEL_REFRESH_SECONDS
        self.heartbeatColor = BLUE
        self.heartbeatFreq = 4
        self.heartbeatCount = 0
        self.powerGridPixels = 0

        logger.info(
            f"Creating PixelManager{disabledString(ENABLE_PIXELS)} with {TOTAL_LED_COUNT} pixels"
        )

        # Dump out one log line for each pixel grid, indicating the pixel index range for that grid
        logger.info(f"Pixel Grids: {PIXEL_GRID_COUNT} total")
        for gridIndex in range(PIXEL_GRID_COUNT):
            startIndex = PixelManagerClass.PixelGridLEDStartIndex[gridIndex]
            length = PixelManagerClass.PixelGridLEDLength[gridIndex]
            logger.info(
                f"  Pixel Grid #{gridIndex}: LED index {startIndex} to {startIndex + length - 1} ({length} LEDs)"
            )

        # Dump out one log line for each card, indicating the pixel index range for that card
        logger.info(
            f"Cards: {len(PixelManagerClass.CardLEDStartIndex)} buses"
        )
        logger.info(
            f"Cards: {len(PixelManagerClass.CardLEDStartIndex[0])} cards per bus"
        )
        for busIndex in range(CARD_BUS_COUNT):
            for cardIndex in range(CARDS_PER_BUS):
                startIndex = PixelManagerClass.CardLEDStartIndex[busIndex][cardIndex]
                logger.info(
                    f"  Card B{busIndex}/C{cardIndex}: LED index {startIndex} to {startIndex + LEDS_PER_CARD - 1} ({LEDS_PER_CARD} LEDs)"
                )

        # Dump out one log line for each card tray, indicating the pixel index range for that tray
        logger.info(
            f"Card Reader Trays: {CARD_BUS_COUNT} buses, {TRAYS_PER_BUS} trays per bus, {CARDS_PER_BUS} cards per tray"
        )
        for busIndex in range(CARD_BUS_COUNT):
            for trayIndex in range(TRAYS_PER_BUS):
                for cardIndex in range(CARDS_PER_BUS):
                    startIndex = PixelManagerClass.CardTrayLEDStartIndex[busIndex][
                        trayIndex
                    ][cardIndex]
                    logger.info(
                        f"  Tray B{busIndex}/T{trayIndex}/C{cardIndex}: LED index {startIndex} to {startIndex + LEDS_PER_TRAY - 1} ({LEDS_PER_TRAY} LEDs)"
                    )

        if ENABLE_PIXELS:
            self.enabledString = ""
            self.pixels = NeoPixel(
                LED_DATA_PIN,
                TOTAL_LED_COUNT,
                brightness=PIXEL_BRIGHTNESS,
                auto_write=False,
                pixel_order="GRB",
            )

            logger.info(
                f"PixelManager{disabledString(ENABLE_PIXELS)}: Clearing {TOTAL_LED_COUNT} total pixels"
            )

            self.pixels.fill(BLACK)
            self.pixels.show()

    def SetTrayColor(self, bus: int, card: int, color: tuple):
        if bus < 0 or bus >= CARD_BUS_COUNT:
            logger.error(f"Pixel Bus index {bus} is out of range.")
            return

        if card < 0 or card >= CARDS_PER_BUS:
            logger.error(f"Pixel Card index {card} is out of range.")
            return

        logger.info(
            f"PixelManager{disabledString(ENABLE_PIXELS)}: Setting Tray B{bus}/C{card} to color: {color}"
        )

        for tray in range(TRAYS_PER_BUS):
            readerPixelIndexStart = PixelManagerClass.CardTrayLEDStartIndex[bus][tray][
                card
            ]
            readerPixelIndexEnd = readerPixelIndexStart + LEDS_PER_TRAY

            if ENABLE_PIXELS:
                for pixelIndex in range(readerPixelIndexStart, readerPixelIndexEnd):
                    self.pixels[pixelIndex] = color

    def SetPowerGridColor(self, gridIndex: int, x: int, y: int, color: tuple):
        if gridIndex < 0 or gridIndex >= PIXEL_GRID_COUNT:
            logger.error(f"Pixel Grid index {gridIndex} is out of range.")
            return

        gridSize = PixelManagerClass.PixelGridSize[gridIndex]

        if x < 0 or x >= gridSize or y < 0 or y >= gridSize:
            logger.error(
                f"Pixel Grid index {gridIndex} coordinates ({x}, {y}) is out of range."
            )
            return

        gridPixelIndex = (
            PixelManagerClass.PixelGridLEDStartIndex[gridIndex] + y * gridSize
        )

        # The pixel grids that we are using map the pixels as a zig-zag linear string: Pixel zero starts at the
        # bottom-left of the grid, and the pixels increment to the right until the string reaches the edge of the grid.
        # Then the string moves up one pixel, and proceeds incrementing to the left.
        if y % 2 == 0:
            gridPixelIndex += x
        else:
            gridPixelIndex += (gridSize - 1) - x

        self.powerGridPixels += 1

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
        self.pixels.fill(BASE_COLOR)

        cylon = 0
        prevCylon = 0
        deltaCylon = 1
        cylonSpeed = 0.05
        nextCylonUpdate = time.monotonic() + cylonSpeed

        cylonCount = 0

        heartbeatFreq = 2
        nextHeartbeat = time.monotonic() + heartbeatFreq

        while True:
            if time.monotonic() > nextHeartbeat:
                logger.info(
                    f"Cylon Pixel Test color: {BASE_COLOR}, brightness: {brightness} {cylon}/{testCount}"
                )
                nextHeartbeat = time.monotonic() + heartbeatFreq

            if nextCylonUpdate > time.monotonic():
                nextCylonUpdate = time.monotonic() + cylonSpeed

                prevCylon = cylon
                cylon += deltaCylon

                if cylon < 0 or cylon >= testCount:
                    deltaCylon = -deltaCylon
                    cylon += deltaCylon
                    cylonCount += 1
                    logger.info(f"Cylon Pixel Test {cylonCount}")

                if floor(cylon) != floor(prevCylon):
                    self.pixels[floor(prevCylon)] = BASE_COLOR
                    self.pixels[floor(cylon)] = CYLON_COLOR
                    self.pixels.show()

    def __str__(self):
        return f"PixelManager{disabledString(ENABLE_PIXELS)}"


PixelManager = PixelManagerClass()
