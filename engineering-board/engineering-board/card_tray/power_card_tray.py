import random
import time

from utils.eng_utils import SlowLog, check_timer, register_timer, logger
from utils.pixel_strip_manager import PixelStripManager
from power_cards.power_card import PowerCard
from card_tray.constants import (
    ENABLE_DEMO_LOGGING,
    ENABLE_DEMO_ANIMATION,
    PIXEL_CARD_TRAY_LEDS,
    PIXEL_CARD_TRAY_GRID_LEDS,
    TRAY_BRIGHTNESS,
    TRAY_DEMO_CHANGE_SECONDS,
    CARD_TRAY_COLORS,
    TIMER_TRAY_DEMO,
    PowerStateEnum,
)


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
        self.__lastFrameRateReport = time.ticks_ms()

        register_timer((id(self), TIMER_TRAY_DEMO), TRAY_DEMO_CHANGE_SECONDS)

    @property
    def UID(self):
        return self.__uid

    @property
    def CurrentPowerCard(self):
        return self.__currentPowerCard

    @CurrentPowerCard.setter
    def CurrentPowerCard(self, value: PowerCard | None):
        self.__currentCardChangedTime = time.ticks_ms()
        self.__currentPowerCard = value

    @property
    def PowerState(self) -> int:
        return self.__powerState

    @PowerState.setter
    def PowerState(self, value: int):
        self.__powerState = value

    def Update(self):
        simTime = time.ticks_ms()

        if check_timer((id(self), TIMER_TRAY_DEMO)):
            if ENABLE_DEMO_ANIMATION:
                _power_states = list(CARD_TRAY_COLORS.keys())
                self.PowerState = _power_states[random.randint(0, len(_power_states) - 1)]

                self.DEMO_CARD_INDEX += 1
                self.CurrentPowerCard = self.__allPowerCards[self.DEMO_CARD_INDEX % len(self.__allPowerCards)]
                if self.UID == 0 and ENABLE_DEMO_LOGGING:
                    elapsed_sec = time.ticks_diff(simTime, self.__lastFrameRateReport) / 1000.0
                    logger.info(
                        f"PowerCardTray(self.UID): Frame rate: {self.__refreshCount / elapsed_sec}, current power card: {self.CurrentPowerCard.CardName if self.CurrentPowerCard else 'None'}"
                    )
                self.__refreshCount = 0
                self.__lastFrameRateReport = time.ticks_ms()

        SlowLog(f"Updating Power Card Tray {self.UID} state")

        if not self.CurrentPowerCard:
            self.__pixelStripManager.pixels.fill((0, 0, 0))
        else:
            cardAnimation = self.CurrentPowerCard.CardAnimation
            elapsed_ms = time.ticks_diff(time.ticks_ms(), self.__currentCardChangedTime)
            elapsed_sec = elapsed_ms / 1000.0
            animationProgress = (elapsed_sec % cardAnimation.animation_duration) / cardAnimation.animation_duration

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
