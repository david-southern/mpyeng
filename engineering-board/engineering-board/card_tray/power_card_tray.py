import random
import time

from utils.color_utils import neo_packed_to_buffer
from utils.eng_utils import SlowLog, check_timer, register_timer, logger
from utils.pixel_strip_manager import PixelStripManager
from power_cards.power_card import PowerCard

from card_tray.constants import (
    CARD_PIXEL_COUNT,
    DEMO_LOGGING,
    DEMO_ANIMATION,
    PIXEL_CARD_TRAY_LEDS,
    PIXEL_CARD_TRAY_TOTAL_LEDS,
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

        self.__startPixelIndex = self.__pixelStripManager.ReservePixelRange(PIXEL_CARD_TRAY_TOTAL_LEDS)
        self.__tray_pixel_buffer = bytearray(PIXEL_CARD_TRAY_TOTAL_LEDS * 3)
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
        color = CARD_TRAY_COLORS[value]
        for status_index in range(PIXEL_CARD_TRAY_LEDS):
            neo_packed_to_buffer(color, self.__tray_pixel_buffer, status_index * 3)
            neo_packed_to_buffer(
                color, self.__tray_pixel_buffer, (PIXEL_CARD_TRAY_LEDS + CARD_PIXEL_COUNT + status_index) * 3
            )

    def Update(self):
        simTime = time.ticks_ms()

        if check_timer((id(self), TIMER_TRAY_DEMO)):
            if DEMO_ANIMATION:
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

        SlowLog(f"Updating Power Card Tray {self.UID} state")

        if not self.CurrentPowerCard:
            card_buf_index = PIXEL_CARD_TRAY_LEDS * 3
            for clear_index in range(CARD_PIXEL_COUNT * 3):
                self.__tray_pixel_buffer[card_buf_index + clear_index] = 0
        else:
            cardAnimation = self.CurrentPowerCard.CardAnimation
            elapsed_ms = time.ticks_diff(time.ticks_ms(), self.__currentCardChangedTime)
            elapsed_sec = elapsed_ms / 1000.0
            animationProgress = (elapsed_sec % cardAnimation.animation_duration) / cardAnimation.animation_duration

            pixel_buffer = self.CurrentPowerCard.PixelBuffer(animationProgress, TRAY_BRIGHTNESS)
            self.__tray_pixel_buffer[PIXEL_CARD_TRAY_LEDS * 3 : (PIXEL_CARD_TRAY_LEDS + CARD_PIXEL_COUNT) * 3] = (
                pixel_buffer
            )

        self.__pixelStripManager.SetPixelData(
            self.__startPixelIndex,
            PIXEL_CARD_TRAY_TOTAL_LEDS,
            self.__tray_pixel_buffer,
        )

        self.__refreshCount += 1

    def __str__(self):
        return f"PowerCardTray: {self.UID}"
