import board
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
from tm1637 import TM1637
from eng_utils import ENABLE_POWER_DISPLAY, disabledString, logger

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
                logger.info(
                    f"Setting PowerDisplay {self}{disabledString(ENABLE_POWER_DISPLAY)} to value {value}"
                )

    def __str__(self):
        return f"{self.DisplayName}/D:{self.DataPin}/C:{self.ClockPin}{disabledString(ENABLE_POWER_DISPLAY)}"


class PowerDisplayManagerClass:
    def __init__(self) -> None:
        self._ALL_POWER_DISPLAYS: list[PowerDisplay] = []
        self._ALL_POWER_DISPLAYS = []
        if ENABLE_POWER_DISPLAY:
            self._ALL_POWER_DISPLAYS.append(
                PowerDisplay(1, board.D2, board.D3, LEFT_WING)
            )
            self._ALL_POWER_DISPLAYS.append(
                PowerDisplay(2, board.D53, board.D49, RIGHT_WING)
            )
            self._ALL_POWER_DISPLAYS.append(
                PowerDisplay(3, board.D26, board.D25, TRANS1 + MAX_DISPLAY)
            )
            self._ALL_POWER_DISPLAYS.append(
                PowerDisplay(4, board.D28, board.D27, TRANS1 + CUR_DISPLAY)
            )
            self._ALL_POWER_DISPLAYS.append(
                PowerDisplay(5, board.D30, board.D29, TRANS2 + MAX_DISPLAY)
            )
            self._ALL_POWER_DISPLAYS.append(
                PowerDisplay(6, board.D32, board.D31, TRANS2 + CUR_DISPLAY)
            )
            self._ALL_POWER_DISPLAYS.append(
                PowerDisplay(7, board.D34, board.D33, TRANS3 + MAX_DISPLAY)
            )
            self._ALL_POWER_DISPLAYS.append(
                PowerDisplay(8, board.D36, board.D35, TRANS3 + CUR_DISPLAY)
            )
            self._ALL_POWER_DISPLAYS.append(
                PowerDisplay(9, board.D46, board.D45, TRANS4 + MAX_DISPLAY)
            )
            self._ALL_POWER_DISPLAYS.append(
                PowerDisplay(10, board.D48, board.D47, TRANS4 + CUR_DISPLAY)
            )

    def AllDisplays(self) -> list[PowerDisplay]:
        return self._ALL_POWER_DISPLAYS

    def SetDisplayCurValue(self, displayName: str, value: int):
        displayName += CUR_DISPLAY
        try:
            display = next(
                d for d in self._ALL_POWER_DISPLAYS if d.DisplayName == displayName
            )
        except StopIteration:
            display = None

        if display is None:
            logger.error(f"Unknown display name '{displayName}'.")
            return

        # logger.info(f"Setting PowerDisplay {displayIndex}{disabledString(ENABLE_POWER_DISPLAY)} to value {value}")
        display.Value = value

    def SetDisplayMaxValue(self, displayName: str, value: int):
        displayName += MAX_DISPLAY
        try:
            display = next(
                d for d in self._ALL_POWER_DISPLAYS if d.DisplayName == displayName
            )
        except StopIteration:
            display = None

        if display is None:
            logger.error(f"Unknown display name '{displayName}'.")
            return

        # logger.info(f"Setting PowerDisplay {displayIndex}{disabledString(ENABLE_POWER_DISPLAY)} to value {value}")
        display.Value = value

    def SetDisplayValue(self, displayName: str, value: int):
        try:
            display = next(
                d for d in self._ALL_POWER_DISPLAYS if d.DisplayName == displayName
            )
        except StopIteration:
            display = None

        if display is None:
            logger.error(f"Unknown display name '{displayName}'.")
            return

        # logger.info(f"Setting PowerDisplay {displayIndex}{disabledString(ENABLE_POWER_DISPLAY)} to value {value}")
        display.Value = value


PowerDisplayManager = PowerDisplayManagerClass()
