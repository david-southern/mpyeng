import random
import time
import board

from color_utils import BLUE, GREEN, YELLOW, RED
from eng_utils import SlowLog, check_timer, register_timer, logger
from pixel_strip_manager import PixelStripManager
from power_card import PowerCard

ENABLE_DEMO_LOGGING = False
ENABLE_DEMO_ANIMATION = True

PIXEL_CARD_TRAYS = 30
PIXEL_CARD_TRAY_LEDS = 5
PIXEL_CARD_TRAY_GRID_SIZE = 8
PIXEL_CARD_TRAY_GRID_LEDS = PIXEL_CARD_TRAY_GRID_SIZE * PIXEL_CARD_TRAY_GRID_SIZE

PIXEL_CARD_TRAY_TOTAL_LEDS = PIXEL_CARD_TRAY_LEDS * 2 + PIXEL_CARD_TRAY_GRID_LEDS

TRAY_BRIGHTNESS = 0.15

class PowerStateEnum:
    OFF = 0
    FULL_POWER = 1
    PARTIAL_POWER = 2
    NO_POWER = 3
    ERROR = 4

def _color_to_scaled_int(color, brightness):
    return (int(color.R * brightness) << 16) | (int(color.G * brightness) << 8) | int(color.B * brightness)

CARD_TRAY_COLORS = {
    PowerStateEnum.OFF: 0,
    PowerStateEnum.FULL_POWER: _color_to_scaled_int(GREEN, TRAY_BRIGHTNESS),
    PowerStateEnum.PARTIAL_POWER: _color_to_scaled_int(YELLOW, TRAY_BRIGHTNESS),
    PowerStateEnum.NO_POWER: _color_to_scaled_int(RED, TRAY_BRIGHTNESS),
    PowerStateEnum.ERROR: _color_to_scaled_int(BLUE, TRAY_BRIGHTNESS)
}

TRAY_DEMO_CHANGE_SECONDS = 6.0
TIMER_TRAY_DEMO = "tray_demo"

class PowerCardTray:
    def __init__(self, uid, pixelStripManager: PixelStripManager):
        self.__uid = uid
        self.__pixelStripManager = pixelStripManager
        self.__powerState = PowerStateEnum.OFF
        self.__allPowerCards = PowerCard.GetAllPowerCards()
        self.DEMO_CARD_INDEX = 0
        self.CurrentPowerCard = self.__allPowerCards[self.DEMO_CARD_INDEX % len(self.__allPowerCards)]
        
        self.__topTrayPixelIndex = self.__pixelStripManager.ReservePixelRange(PIXEL_CARD_TRAY_LEDS)
        self.__gridPixelIndex = self.__pixelStripManager.ReservePixelRange(PIXEL_CARD_TRAY_GRID_LEDS)
        self.__bottomTrayPixelIndex = self.__pixelStripManager.ReservePixelRange(PIXEL_CARD_TRAY_LEDS)
        self.__refreshCount = 0
        self.__lastFrameRateReport = time.monotonic()
        
        register_timer((id(self), TIMER_TRAY_DEMO), TRAY_DEMO_CHANGE_SECONDS)

    @property
    def UID(self):
        return self.__uid

    @property
    def CurrentPowerCard(self):
        return self.__currentPowerCard

    @CurrentPowerCard.setter
    def CurrentPowerCard(self, value: PowerCard | None):
        self.__currentCardChangedTime = time.monotonic()
        self.__currentPowerCard = value

    @property
    def PowerState(self):
        return self.__powerState

    @PowerState.setter
    def PowerState(self, value: int):
        self.__powerState = value

    def Update(self):
        simTime = time.monotonic()

        if check_timer((id(self), TIMER_TRAY_DEMO)):
            if ENABLE_DEMO_ANIMATION:
                self.PowerState = random.choice(list(CARD_TRAY_COLORS.keys()))

                self.DEMO_CARD_INDEX += 1
                self.CurrentPowerCard = self.__allPowerCards[self.DEMO_CARD_INDEX % len(self.__allPowerCards)]
                if self.UID == 0 and ENABLE_DEMO_LOGGING:
                    logger.info(f"PowerCardTray(self.UID): Frame rate: {self.__refreshCount / (simTime - self.__lastFrameRateReport)}, current power card: {self.CurrentPowerCard.CardName if self.CurrentPowerCard else 'None'}")
                self.__refreshCount = 0
                self.__lastFrameRateReport = time.monotonic()

        SlowLog(f"Updating Power Card Tray {self.UID} state")

        pixel_buffer = [0] * PIXEL_CARD_TRAY_GRID_LEDS
        
        if not self.CurrentPowerCard:
            pixel_buffer = [0] * PIXEL_CARD_TRAY_GRID_LEDS
        else:
            cardAnimation = self.CurrentPowerCard.CardAnimation
            animationProgress = ((time.monotonic() - self.__currentCardChangedTime) % cardAnimation.animation_duration) / cardAnimation.animation_duration

            pixel_buffer = self.CurrentPowerCard.PixelBuffer(animationProgress, TRAY_BRIGHTNESS)

        self.__pixelStripManager.SetPixelData(
            self.__gridPixelIndex,
            PIXEL_CARD_TRAY_GRID_LEDS,
            pixel_buffer,
        )

        trayStateColor = CARD_TRAY_COLORS[self.PowerState]

        self.__pixelStripManager.SetPixelData(
            self.__topTrayPixelIndex,
            PIXEL_CARD_TRAY_LEDS,
            [trayStateColor] * PIXEL_CARD_TRAY_LEDS,
        )
        self.__pixelStripManager.SetPixelData(
            self.__bottomTrayPixelIndex,
            PIXEL_CARD_TRAY_LEDS,
            [trayStateColor] * PIXEL_CARD_TRAY_LEDS,
        )

        self.__refreshCount += 1

    def __str__(self):
        return f"PowerCardTray: {self.UID}"

class PowerTrayManagerClass:
    def __init__(self):
        if board.board_id == "grandcentral_m4_express":
            self.RIGHT_STRIP_DATA_PIN = board.D21
        else:
            self.RIGHT_STRIP_DATA_PIN = board.D25

        self.RIGHT_STRIP_LED_COUNT = PIXEL_CARD_TRAY_TOTAL_LEDS * PIXEL_CARD_TRAYS
        self.RightPixelStrip = PixelStripManager(self.RIGHT_STRIP_DATA_PIN, self.RIGHT_STRIP_LED_COUNT)
        self.TestPowerCardTrays = [ PowerCardTray(i, self.RightPixelStrip) for i in range(PIXEL_CARD_TRAYS) ]

    def Update(self):
        for tray in self.TestPowerCardTrays:
            tray.Update()
        self.RightPixelStrip.Update()


PowerTrayManager = PowerTrayManagerClass()