from array import array

import micropython

import neopixel
from machine import Pin
from utils.eng_utils import check_timer, register_timer, SlowLog, logger, ENABLE_PIXELS
from utils.profiling import register_profile, start_profile, stop_profile

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

# The PixelManager doesn't update the strip every time a caller sets pixel data, instead it sends
# the pixel data on the PIXEL_REFRESH_SECONDS timer.  This allows multiple callers to set pixel data
# without causing the strip to update multiple times in quick succession, as well as re-sending the
# strip data at a regular interval in case of interference or other issues causing the strip to lose
# data.

PIXEL_REFRESH_SECONDS = 0.05
TIMER_PIXEL_REFRESH = "pixel_refresh"

PROFILE_PIXELS = register_profile("pixel_update")


@micropython.viper
def _unpack_pixels_to_buf(src: ptr32, dst: ptr8, dst_byte_offset: int, src_length: int):  # pyright: ignore[reportUndefinedVariable] # noqa: F821
    """Unpack <src_length> neo_packed ints from <src> into our NeoPixel.buf, which is a bytearray.
    <src> must be array('I'); <dst> must be bytearray."""
    copy_index: int = 0
    while copy_index < src_length:
        neo_packed: int = src[copy_index]
        base: int = dst_byte_offset + copy_index * 3
        # neo_packed ints are already in the correct byte order for the strip layout, per the
        # color_utils.NEO_PACKED_PIXEL_OFFSETS constant, so just copy them in
        dst[base] = (neo_packed >> 16) & 0xFF
        dst[base + 1] = (neo_packed >> 8) & 0xFF
        dst[base + 2] = neo_packed & 0xFF
        copy_index += 1


class PixelStripManager:
    def __init__(self, LED_DATA_PIN: Pin, TOTAL_LED_COUNT: int, profileKey: list | None = None):
        self.name = "PixelStripManager" + f"({profileKey[0]})" if profileKey else ""
        self.LED_DATA_PIN = LED_DATA_PIN
        self.TOTAL_LED_COUNT = TOTAL_LED_COUNT
        self.currentPixelIndex = 0
        self.profileKey = profileKey
        self.__dirty = False
        register_timer((id(self), TIMER_PIXEL_REFRESH), PIXEL_REFRESH_SECONDS)

        logger.info(
            f"{self.name}: Creating NeoPixel strip on LED_DATA_PIN {LED_DATA_PIN} with {TOTAL_LED_COUNT} pixels"
        )

        if ENABLE_PIXELS:
            self.enabledString = ""
            self.pixels = neopixel.NeoPixel(LED_DATA_PIN, TOTAL_LED_COUNT)

            logger.info(f"{self.name}: Clearing {TOTAL_LED_COUNT} total pixels")

            self.pixels.fill((0, 0, 0))
            self.pixels.write()

    def ReservePixelRange(self, pixelCount: int) -> int:
        if self.currentPixelIndex + pixelCount > self.TOTAL_LED_COUNT:
            raise Exception(
                f"{self.name}: Unable to reserve {pixelCount} pixels, only {self.TOTAL_LED_COUNT - self.currentPixelIndex} pixels remaining."
            )

        reservedPixelIndex = self.currentPixelIndex
        self.currentPixelIndex += pixelCount

        return reservedPixelIndex

    def SetPixelData(self, startIndex: int, pixelCount: int, pixelData: array[int]):
        if not ENABLE_PIXELS:
            return

        if pixelCount < 1:
            logger.error(f"SetPixelRangeColor: pixelCount {pixelCount} is invalid.")
            return

        if pixelCount != len(pixelData):
            logger.error(
                f"SetPixelRangeColor: pixelCount {pixelCount} does not match length of pixelData {len(pixelData)}."
            )
            return

        if startIndex < 0 or startIndex >= self.TOTAL_LED_COUNT:
            logger.error(f"SetPixelRangeColor: Pixel start index {startIndex} is out of range.")
            return

        endIndex = startIndex + pixelCount - 1

        if endIndex < 0 or endIndex >= self.TOTAL_LED_COUNT:
            logger.error(f"SetPixelRangeColor: Pixel end index {endIndex} is out of range.")
            return

        SlowLog(f"{self.name}: Setting Pixel range {startIndex}-{endIndex}")

        _unpack_pixels_to_buf(pixelData, self.pixels.buf, startIndex * 3, pixelCount)

        self.__dirty = True

    def ShowPixels(self):
        if not ENABLE_PIXELS:
            return

        if not self.__dirty:
            return

        SlowLog("Showing pixel data")
        if self.profileKey:
            start_profile(self.profileKey)
        self.pixels.write()
        if self.profileKey:
            stop_profile(self.profileKey)
        self.__dirty = False

    def Update(self):
        if not ENABLE_PIXELS:
            return

        if check_timer((id(self), TIMER_PIXEL_REFRESH)):
            start_profile(PROFILE_PIXELS)
            self.ShowPixels()
            stop_profile(PROFILE_PIXELS)

    def __str__(self):
        return f"{self.name}"
