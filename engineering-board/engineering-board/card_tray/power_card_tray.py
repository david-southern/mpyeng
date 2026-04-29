import random
import time

from card_tray.tray_manager import register_profile
from utils.eng_utils import check_timer, register_timer, logger
from utils.pixel_strip_manager import PixelStripManager
from power_cards.power_card import PowerCard

from card_tray.constants import (
    DEMO_LOGGING,
    DEMO_ANIMATION,
    CARD_TRAY_STATUS_PIXELS,
    CARD_GRID_PIXELS,
    TRAY_DEMO_CHANGE_SECONDS,
    CARD_TRAY_COLORS,
    TIMER_TRAY_DEMO,
    PowerStateEnum,
)
from utils.profiling import start_profile, stop_profile

PROFILE_DEMO = register_profile("tray_demo")
PROFILE_ANIM = register_profile("tray_anim")


class PowerCardTray:
    def __init__(self, uid, pixelStripManager: PixelStripManager):
        self.__uid = uid
        self.__pixelStripManager = pixelStripManager
        self.__powerState = PowerStateEnum.OFF
        self.__allPowerCards = PowerCard.GetAllPowerCards()
        self.DEMO_CARD_INDEX = 0
        self.CurrentPowerCard = self.__allPowerCards[self.DEMO_CARD_INDEX % len(self.__allPowerCards)]

        self.__bottomStatusPixelIndex = self.__pixelStripManager.ReservePixelRange(CARD_TRAY_STATUS_PIXELS)
        self.__gridPixelIndex = self.__pixelStripManager.ReservePixelRange(CARD_GRID_PIXELS)
        self.__topStatusPixelIndex = self.__pixelStripManager.ReservePixelRange(CARD_TRAY_STATUS_PIXELS)
        self.__refreshCount = 0
        self.__lastAnimationFrame = -1
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
        color = CARD_TRAY_COLORS[value]
        self.__pixelStripManager.FillPixelData(color, self.__bottomStatusPixelIndex, CARD_TRAY_STATUS_PIXELS)
        self.__pixelStripManager.FillPixelData(color, self.__topStatusPixelIndex, CARD_TRAY_STATUS_PIXELS)

    def Update(self):
        start_profile(PROFILE_ANIM)
        try:
            simTime = time.ticks_ms()

            if check_timer((id(self), TIMER_TRAY_DEMO)):
                if DEMO_ANIMATION:
                    start_profile(PROFILE_DEMO)
                    _power_states = list(CARD_TRAY_COLORS.keys())
                    self.PowerState = _power_states[random.randint(0, len(_power_states) - 1)]

                    self.DEMO_CARD_INDEX += 1
                    self.CurrentPowerCard = self.__allPowerCards[self.DEMO_CARD_INDEX % len(self.__allPowerCards)]
                    if self.UID == 0 and DEMO_LOGGING:
                        elapsed_sec = time.ticks_diff(simTime, self.__lastFrameRateReport) / 1000.0
                        logger.info(
                            f"PowerCardTray(self.UID): Frame rate: {self.__refreshCount / elapsed_sec}, current power card: {self.CurrentPowerCard.CardName if self.CurrentPowerCard else 'None'}"
                        )
                    self.__refreshCount = 0
                    self.__lastFrameRateReport = time.ticks_ms()
                    stop_profile(PROFILE_DEMO)

            if not self.CurrentPowerCard:
                if self.__lastAnimationFrame != -1:
                    self.__lastAnimationFrame = -1
                    return
                self.__pixelStripManager.FillPixelData(0, self.__gridPixelIndex, CARD_GRID_PIXELS)
            else:
                cardAnimation = self.CurrentPowerCard.CardAnimation
                elapsed_ms = time.ticks_diff(time.ticks_ms(), self.__currentCardChangedTime)
                elapsed_sec = elapsed_ms / 1000.0
                animationProgress = (elapsed_sec % cardAnimation.animation_duration) / cardAnimation.animation_duration

                animationFrame = cardAnimation.AnimationFrame(animationProgress)
                if self.__lastAnimationFrame == animationFrame:
                    return

                self.__lastAnimationFrame = animationFrame
                source_pixel_buffer = self.CurrentPowerCard.PixelBuffer(animationFrame)

                self.__pixelStripManager.SetPixelData(source_pixel_buffer, self.__gridPixelIndex, CARD_GRID_PIXELS)

                self.__refreshCount += 1
        finally:
            stop_profile(PROFILE_ANIM)

    def __str__(self):
        return f"PowerCardTray: {self.UID}"
