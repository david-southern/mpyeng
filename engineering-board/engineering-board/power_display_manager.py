from machine import Pin
from protocol_resources import (
    LEFT_WING,
    RIGHT_WING,
    TRANS1,
    TRANS2,
    TRANS3,
    TRANS4,
    CUR_DISPLAY,
    MAX_DISPLAY,
)
from dave_tm1637 import TM1637
from eng_utils import ENABLE_POWER_DISPLAY, disabledString, logger
from device_manager import device_manager

SHOW_POWER_DISPLAY_DIAGS = False


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


class PowerDisplayManagerClass:
    _DISPLAY_NAMES = [
        LEFT_WING,
        RIGHT_WING,
        TRANS1 + MAX_DISPLAY,
        TRANS1 + CUR_DISPLAY,
        TRANS2 + MAX_DISPLAY,
        TRANS2 + CUR_DISPLAY,
        TRANS3 + MAX_DISPLAY,
        TRANS3 + CUR_DISPLAY,
        TRANS4 + MAX_DISPLAY,
        TRANS4 + CUR_DISPLAY,
    ]

    _DEFAULT_DISPLAY_PINS = [
        (2, 3),
        (4, 5),
        (6, 7),
        (8, 9),
        (10, 11),
        (12, 13),
        (14, 15),
        (16, 17),
        (18, 19),
        (20, 22),
    ]

    def __init__(self) -> None:
        self.__ALL_POWER_DISPLAYS: list[PowerDisplay] = []
        self.__ALL_POWER_DISPLAYS = []
        if ENABLE_POWER_DISPLAY:
            display_pins = device_manager.resolve_pin("power_display", "displays", self._DEFAULT_DISPLAY_PINS)
            for display_index, (data_pin, clock_pin) in enumerate(display_pins):
                self.__ALL_POWER_DISPLAYS.append(
                    PowerDisplay(
                        display_index + 1,
                        Pin(data_pin),
                        Pin(clock_pin),
                        self._DISPLAY_NAMES[display_index],
                    )
                )

    def AllDisplays(self) -> list[PowerDisplay]:
        return self.__ALL_POWER_DISPLAYS

    def SetDisplayCurValue(self, displayName: str, value: int):
        if not ENABLE_POWER_DISPLAY:
            return

        displayName += CUR_DISPLAY
        try:
            display = next(d for d in self.__ALL_POWER_DISPLAYS if d.DisplayName == displayName)
        except StopIteration:
            display = None

        if display is None:
            logger.error(f"Unknown display name '{displayName}'.")
            return

        # logger.info(f"Setting PowerDisplay {displayIndex}{disabledString(ENABLE_POWER_DISPLAY)} to value {value}")
        display.Value = value

    def SetDisplayMaxValue(self, displayName: str, value: int):
        if not ENABLE_POWER_DISPLAY:
            return

        displayName += MAX_DISPLAY
        try:
            display = next(d for d in self.__ALL_POWER_DISPLAYS if d.DisplayName == displayName)
        except StopIteration:
            display = None

        if display is None:
            logger.error(f"Unknown display name '{displayName}'.")
            return

        # logger.info(f"Setting PowerDisplay {displayIndex}{disabledString(ENABLE_POWER_DISPLAY)} to value {value}")
        display.Value = value

    def SetDisplayValue(self, displayName: str, value: int):
        if not ENABLE_POWER_DISPLAY:
            return

        try:
            display = next(d for d in self.__ALL_POWER_DISPLAYS if d.DisplayName == displayName)
        except StopIteration:
            display = None

        if display is None:
            logger.error(f"Unknown display name '{displayName}'.")
            return

        # logger.info(f"Setting PowerDisplay {displayIndex}{disabledString(ENABLE_POWER_DISPLAY)} to value {value}")
        display.Value = value


PowerDisplayManager = PowerDisplayManagerClass()
