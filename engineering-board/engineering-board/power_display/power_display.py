from machine import Pin

from utils.dave_tm1637 import TM1637
from utils.eng_utils import ENABLE_POWER_DISPLAY, disabledString, logger
from power_display.constants import SHOW_POWER_DISPLAY_DIAGS


class PowerDisplay:
    def __init__(self, uid, dataPin, clockPin, displayName=None):
        self.__uid = uid
        self.__displayName = displayName
        self.__clockPin = clockPin
        self.__dataPin = dataPin

        if ENABLE_POWER_DISPLAY:
            self.__display = TM1637(clockPin, dataPin)

        self.Value = uid

    @property
    def UID(self):
        return self.__uid

    @property
    def DisplayName(self):
        return self.__displayName

    @property
    def ClockPin(self):
        return self.__clockPin

    @property
    def DataPin(self):
        return self.__dataPin

    @property
    def Value(self):
        return self.__value

    @Value.setter
    def Value(self, value):
        self.__value = value
        if ENABLE_POWER_DISPLAY:
            if isinstance(value, int):
                self.__display.number(value)
            else:
                self.__display.show(str(value))
            if SHOW_POWER_DISPLAY_DIAGS:
                logger.info(f"Setting PowerDisplay {self}{disabledString(ENABLE_POWER_DISPLAY)} to value {value}")

    def __str__(self):
        return f"{self.DisplayName}/D:{self.DataPin}/C:{self.ClockPin}{disabledString(ENABLE_POWER_DISPLAY)}"
