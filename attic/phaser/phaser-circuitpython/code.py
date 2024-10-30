import random
import board
import time

import usb_cdc
import adafruit_logging as logging

import neopixel

if usb_cdc.data is None:
    raise ConnectionError("Unable to open USB_cdc.data Serial connection")

# Power Consumption notes: Powering 768 red (255,0,0) pixels at 10% brightness pulls 1.35 amps, according to my
# multimeter.  Increasing the brightness to 0.2 draws 2.3 amps.  If you increase the brightness, make sure that your
# power supply can handle the current draw
PIXEL_BRIGHTNESS = 0.1

# Usually the component color updaters will send the pixel data as part of the update.  The PixelManager will
# automatically re-send the pixel data this often, in case an update is missed
PIXEL_REFRESH_SECONDS = 0.25

LED_DATA_PIN = board.D12

POWER_PIXEL_COUNT = 10
BARREL_PIXEL_COUNT = 20
EMITTER_PIXEL_COUNT = 3

TOTAL_LED_COUNT = POWER_PIXEL_COUNT + BARREL_PIXEL_COUNT + EMITTER_PIXEL_COUNT

BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

logger.info("Initializing Phaser Manager")

LOOP_FREQUENCY_SEC = 0.1
HEARTBEAT_FREQUENCY_SEC = 1.0

next_heartbeat = time.monotonic() + HEARTBEAT_FREQUENCY_SEC
next_pixel_update = time.monotonic() + PIXEL_REFRESH_SECONDS
pixelColors = [BLACK, RED, YELLOW, GREEN, BLUE]
pixelColorIndex = 0

pixels = neopixel.NeoPixel(
    LED_DATA_PIN,
    TOTAL_LED_COUNT,
    brightness=PIXEL_BRIGHTNESS,
    auto_write=False,
    pixel_order="GRB",
)
pixels.fill(pixelColors[pixelColorIndex])
pixels.show()

while True:
    if time.monotonic() > next_pixel_update:
        pixelColorIndex += 1
        if pixelColorIndex >= len(pixelColors):
            pixelColorIndex = 0

        for pixelIndex in range(0, TOTAL_LED_COUNT):
            pixels[pixelIndex] = pixelColors[pixelColorIndex]

        pixels.show()

        next_pixel_update = time.monotonic() + PIXEL_REFRESH_SECONDS

    if time.monotonic() > next_heartbeat:
        logString = f"Heartbeat"
        logger.info(logString)
        next_heartbeat = time.monotonic() + HEARTBEAT_FREQUENCY_SEC

    time.sleep(LOOP_FREQUENCY_SEC)
