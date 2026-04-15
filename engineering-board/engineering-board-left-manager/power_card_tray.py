import random
import time
import board

from eng_utils import ENABLE_RIGHT_PIXELS, SlowLog, scaledColor, logger
from pixel_strip_manager import BLUE, GREEN, RED, YELLOW, PixelStripManager
from power_grid_manager import RandomGridGenerator

PIXEL_CARD_TRAYS = 5
PIXEL_CARD_TRAY_LEDS = 5
PIXEL_CARD_TRAY_GRID_SIZE = 8
PIXEL_CARD_TRAY_GRID_LEDS = PIXEL_CARD_TRAY_GRID_SIZE * PIXEL_CARD_TRAY_GRID_SIZE

PIXEL_CARD_TRAY_TOTAL_LEDS = PIXEL_CARD_TRAY_LEDS * 2 + PIXEL_CARD_TRAY_GRID_LEDS

TRAY_BRIGHTNESS = 0.95
CARD_TRAY_COLORS = [scaledColor(BLUE, TRAY_BRIGHTNESS), scaledColor(GREEN, TRAY_BRIGHTNESS), scaledColor(YELLOW, TRAY_BRIGHTNESS), scaledColor(RED, TRAY_BRIGHTNESS)]

TRAY_REFRESH_SECONDS = 0.2
TRAY_COLOR_CHANGE_SECONDS = 3.0

class PowerCardTray:
    def __init__(self, uid, pixelStripManager: PixelStripManager):
        self.__uid = uid
        self.__pixelStripManager = pixelStripManager

        self.__topTrayPixelIndex = self.__pixelStripManager.ReservePixelRange(PIXEL_CARD_TRAY_LEDS)
        self.__gridPixelIndex = self.__pixelStripManager.ReservePixelRange(PIXEL_CARD_TRAY_GRID_LEDS)
        self.__bottomTrayPixelIndex = self.__pixelStripManager.ReservePixelRange(PIXEL_CARD_TRAY_LEDS)

        self.__randomGridGenerator = RandomGridGenerator(PIXEL_CARD_TRAY_GRID_SIZE)

        self.__nextUpdate = time.monotonic() + TRAY_REFRESH_SECONDS
        self.__nextTrayColorUpdate = time.monotonic() + TRAY_COLOR_CHANGE_SECONDS

    @property
    def UID(self):
        return self.__uid

    @property
    def TargetLevel(self):
        return self.__targetLevel

    @TargetLevel.setter
    def TargetLevel(self, value):
        self.__targetLevel = value
        self.__randomGridGenerator.TargetLevel = value

    def Update(self):
        simTime = time.monotonic()

        if simTime > self.__nextUpdate:
            SlowLog(f"Updating Power Card Tray {self.UID} state")

            self.__randomGridGenerator.UpdateGridState()

            self.__pixelStripManager.SetPixelData(
                self.__gridPixelIndex,
                PIXEL_CARD_TRAY_GRID_LEDS,
                self.__randomGridGenerator.PixelColors,
            )

            if simTime > self.__nextTrayColorUpdate:
                newColor = CARD_TRAY_COLORS[random.randint(0, len(CARD_TRAY_COLORS) - 1)]

                self.__pixelStripManager.SetPixelData(
                    self.__topTrayPixelIndex,
                    PIXEL_CARD_TRAY_LEDS,
                    [newColor for i in range(PIXEL_CARD_TRAY_LEDS)],
                )
                self.__pixelStripManager.SetPixelData(
                    self.__bottomTrayPixelIndex,
                    PIXEL_CARD_TRAY_LEDS,
                    [newColor for i in range(PIXEL_CARD_TRAY_LEDS)],
                )
                
                self.__nextTrayColorUpdate = simTime + TRAY_COLOR_CHANGE_SECONDS
            
            self.__nextUpdate = simTime + TRAY_REFRESH_SECONDS

    def __str__(self):
        return f"PowerCardTray: {self.UID}"

if board.board_id == "grandcentral_m4_express":
    RIGHT_STRIP_DATA_PIN = board.D21
else:
    RIGHT_STRIP_DATA_PIN = board.D25

RIGHT_STRIP_LED_COUNT = PIXEL_CARD_TRAY_TOTAL_LEDS * PIXEL_CARD_TRAYS

RightPixelStrip = PixelStripManager(RIGHT_STRIP_DATA_PIN, RIGHT_STRIP_LED_COUNT)

TestPowerCardTrays = [ PowerCardTray(i, RightPixelStrip) for i in range(PIXEL_CARD_TRAYS) ]
