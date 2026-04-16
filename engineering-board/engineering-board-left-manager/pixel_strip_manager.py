from __future__ import annotations

import board

from neopixel import NeoPixel  # pyright: ignore[reportMissingImports]
from eng_utils import check_timer, register_timer, SlowLog, disabledString, logger, ENABLE_PIXELS

# Power Consumption notes: Powering 768 red (255,0,0) pixels at 10% brightness pulls 1.35 amps, according to my
# multimeter.  Increasing the brightness to 0.2 draws 2.3 amps.  If you increase the brightness, make sure that your
# power supply can handle the current draw
PIXEL_BRIGHTNESS = 0.9
#  #px | Color         | Current Draw @ brightness = 0.1
#  768 |   0,   0,  0  | 0.64
#  768 | 255,   0,  0  | 1.35
#  768 |   0, 255,  0  | 1.33
#  768 |   0,   0, 255 | 1.33
#  768 | 255, 255,   0 | 2.04
#  768 | 255,   0, 255 | 2.04
#  768 |   0, 255, 255 | 2.02
#  768 | 255, 255, 255 | 2.55

# The PixelManager doesn't update the strip every time a caller sets pixel data, instead if sends
# the pixel on the PIXEL_REFRESH_SECONDS timer.  This allows multiple callers to set pixel data
# without causing the strip to update multiple times in quick succession, as well as re-sending the
# strip data at a regular interval in case of interference or other issues causing the strip to lose
# data.
PIXEL_REFRESH_SECONDS = 0.1
TIMER_PIXEL_REFRESH = "pixel_refresh"

class PixelStripManager:

    def __init__(self, LED_DATA_PIN: board.Pin, TOTAL_LED_COUNT: int):
        self.LED_DATA_PIN = LED_DATA_PIN
        self.TOTAL_LED_COUNT = TOTAL_LED_COUNT
        self.currentPixelIndex = 0
        register_timer((id(self), TIMER_PIXEL_REFRESH), PIXEL_REFRESH_SECONDS)

        logger.info(
            f"Creating PixelStripManager{disabledString(ENABLE_PIXELS)} on LED_DATA_PIN {LED_DATA_PIN} with {TOTAL_LED_COUNT} pixels"
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

            self.pixels.fill(0)
            self.pixels.show()

    def ReservePixelRange(self, pixelCount: int) -> int:
        if self.currentPixelIndex + pixelCount > self.TOTAL_LED_COUNT:
            raise Exception(
                f"PixelManager{disabledString(ENABLE_PIXELS)}: Unable to reserve {pixelCount} pixels, only {self.TOTAL_LED_COUNT - self.currentPixelIndex} pixels remaining."
            )

        reservedPixelIndex = self.currentPixelIndex
        self.currentPixelIndex += pixelCount

        logger.info(
            f"PixelManager{disabledString(ENABLE_PIXELS)}: Reserved pixel range {reservedPixelIndex}-{self.currentPixelIndex - 1} (count: {pixelCount})"
        )

        return reservedPixelIndex

    def SetPixelData(self, startIndex: int, pixelCount: int, pixelData: list[int]):
        if not ENABLE_PIXELS:
            return

        if(pixelCount < 1):
            logger.error(f"SetPixelRangeColor: pixelCount {pixelCount} is invalid.")
            return

        if pixelCount != len(pixelData):
            logger.error(f"SetPixelRangeColor: pixelCount {pixelCount} does not match length of pixelData {len(pixelData)}.")
            return

        if startIndex < 0 or startIndex >= self.TOTAL_LED_COUNT:
            logger.error(f"SetPixelRangeColor: Pixel start index {startIndex} is out of range.")
            return

        endIndex = startIndex + pixelCount - 1

        if endIndex < 0 or endIndex >= self.TOTAL_LED_COUNT:
            logger.error(f"SetPixelRangeColor: Pixel end index {endIndex} is out of range.")
            return

        SlowLog(
            f"PixelManager{disabledString(ENABLE_PIXELS)}: Setting Pixel range {startIndex}-{endIndex}"
        )

        self.pixels[startIndex:startIndex + pixelCount] = pixelData

    def ShowPixels(self):
        if not ENABLE_PIXELS:
            return

        SlowLog("Showing pixel data")
        self.pixels.show()


    def Update(self):
        if not ENABLE_PIXELS:
            return

        if check_timer((id(self), TIMER_PIXEL_REFRESH)):
            self.ShowPixels()

    def __str__(self):
        return f"PixelManager{disabledString(ENABLE_PIXELS)}"