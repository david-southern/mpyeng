from drivers.local_neopixel import LocalNeoPixel
from machine import Pin
from utils.device_manager import DeviceManager, Systems
from utils.eng_utils import check_timer, log_free_ram, register_timer, logger
from utils.profiling import profile_name, start_profile, stop_profile

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


class PixelStripManager:
    def __init__(self, LED_DATA_PIN: Pin, TOTAL_LED_COUNT: int, profileKey: list | None = None):
        self.name = (
            f"{DeviceManager.SystemName(Systems.ANY_PIXEL_STRIP)}({profile_name(profileKey)})" if profileKey else ""
        )
        self.LED_DATA_PIN = LED_DATA_PIN
        self.TOTAL_LED_COUNT = TOTAL_LED_COUNT
        self.currentPixelIndex = 0
        self.profileKey = profileKey
        self.__dirty = False
        register_timer((id(self), TIMER_PIXEL_REFRESH), PIXEL_REFRESH_SECONDS)

        logger.info(
            f"{self.name}: Creating NeoPixel strip on LED_DATA_PIN {LED_DATA_PIN} with {TOTAL_LED_COUNT} pixels"
        )

        if DeviceManager.IsEnabled(Systems.ANY_PIXEL_STRIP):
            log_free_ram(f"{self.name} init - before NeoPixel allocation")
            self.pixels = LocalNeoPixel(LED_DATA_PIN, TOTAL_LED_COUNT)

            logger.info(f"{self.name}: Clearing {TOTAL_LED_COUNT} total pixels")

            self.pixels.fill(0, 0, TOTAL_LED_COUNT)
            self.pixels.write()

    def ReservePixelRange(self, pixelCount: int) -> int:
        if self.currentPixelIndex + pixelCount > self.TOTAL_LED_COUNT:
            raise Exception(
                f"{self.name}: Unable to reserve {pixelCount} pixels, only {self.TOTAL_LED_COUNT - self.currentPixelIndex} pixels remaining."
            )

        reservedPixelIndex = self.currentPixelIndex
        self.currentPixelIndex += pixelCount

        return reservedPixelIndex

    def FillPixelData(self, neo_packed_color: int, pixelStartIndex: int, pixelCount: int):
        if not DeviceManager.IsEnabled(Systems.ANY_PIXEL_STRIP):
            return

        if pixelCount < 1:
            logger.error(f"FillPixelData: pixelCount {pixelCount} is invalid.")
            return

        if pixelStartIndex < 0 or pixelStartIndex >= self.TOTAL_LED_COUNT:
            logger.error(
                f"FillPixelData: Pixel start index {pixelStartIndex} is out of range [0, {self.TOTAL_LED_COUNT - 1}]."
            )
            return

        endIndex = pixelStartIndex + pixelCount - 1

        if endIndex < 0 or endIndex >= self.TOTAL_LED_COUNT:
            logger.error(f"FillPixelData: Pixel end index {endIndex} is out of range [0, {self.TOTAL_LED_COUNT - 1}].")
            return

        self.pixels.fill(neo_packed_color, pixelStartIndex, pixelCount)

        self.__dirty = True

    def SetPixelData(self, pixelData: bytes, pixelStartIndex: int, pixelCount: int):
        if not DeviceManager.IsEnabled(Systems.ANY_PIXEL_STRIP):
            return

        if pixelCount < 1:
            logger.error(f"SetPixelData: pixelCount {pixelCount} is invalid.")
            return

        if pixelStartIndex < 0 or pixelStartIndex >= self.TOTAL_LED_COUNT:
            logger.error(
                f"SetPixelData: Pixel start index {pixelStartIndex} is out of range [0, {self.TOTAL_LED_COUNT - 1}]."
            )
            return

        endIndex = pixelStartIndex + pixelCount - 1

        if endIndex < 0 or endIndex >= self.TOTAL_LED_COUNT:
            logger.error(f"SetPixelData: Pixel end index {endIndex} is out of range [0, {self.TOTAL_LED_COUNT - 1}].")
            return

        self.pixels.set_buf(pixelData, pixelStartIndex, pixelCount)

        self.__dirty = True

    def Update(self):
        if not self.__dirty:
            return

        if not DeviceManager.IsEnabled(Systems.ANY_PIXEL_STRIP):
            return

        if check_timer((id(self), TIMER_PIXEL_REFRESH)):
            if self.profileKey:
                start_profile(self.profileKey)

            self.pixels.write()
            self.__dirty = False

            if self.profileKey:
                stop_profile(self.profileKey)

    def __str__(self):
        return f"{self.name}"
