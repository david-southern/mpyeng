import board
from tm1637 import TM1637
from eng_utils import ENABLE_POWER_DISPLAY, disabledString, logger

SHOW_POWER_DISPLAY_DIAGS = False

class PowerDisplay:
    def __init__(self, uid, dataPin, clockPin, displayName=None):
        self.__uid = uid
        self.__displayName = displayName
        self.__clockPin = clockPin
        self.__dataPin = dataPin

        self.__display = None
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
            if type(value) == int:
                self.__display.number(value)
            else:
                self.__display.show(str(value))
            if SHOW_POWER_DISPLAY_DIAGS:
                logger.info(f"Setting PowerDisplay {self}{disabledString(ENABLE_POWER_DISPLAY)} to value {value}")

    def __str__(self):
        return f"{self.DisplayName}/D:{self.DataPin}/C:{self.ClockPin}{disabledString(ENABLE_POWER_DISPLAY)}"

 
class PowerDisplayManagerClass:
    def __init__(self) -> None:
        self._ALL_POWER_DISPLAYS: list[PowerDisplay] = []
        self._ALL_POWER_DISPLAYS = []
        if ENABLE_POWER_DISPLAY:
            self._ALL_POWER_DISPLAYS.append(PowerDisplay(1, board.D2, board.D3, "Eng1"))
            self._ALL_POWER_DISPLAYS.append(PowerDisplay(2, board.D53, board.D49, "Eng2"))
            self._ALL_POWER_DISPLAYS.append(PowerDisplay(3, board.D26, board.D25, "Dist1Max"))
            self._ALL_POWER_DISPLAYS.append(PowerDisplay(4, board.D28, board.D27, "Dist1Cur"))
            self._ALL_POWER_DISPLAYS.append(PowerDisplay(5, board.D30, board.D29, "Dist2Max"))
            self._ALL_POWER_DISPLAYS.append(PowerDisplay(6, board.D32, board.D31, "Dist2Cur"))
            self._ALL_POWER_DISPLAYS.append(PowerDisplay(7, board.D34, board.D33, "Dist3Max"))
            self._ALL_POWER_DISPLAYS.append(PowerDisplay(8, board.D36, board.D35, "Dist3Cur"))
            self._ALL_POWER_DISPLAYS.append(PowerDisplay(9, board.D46, board.D45, "Dist4Max"))
            self._ALL_POWER_DISPLAYS.append(PowerDisplay(10, board.D48, board.D47, "Dist4Cur"))

    def AllDisplays(self) -> list[PowerDisplay]:
        return self._ALL_POWER_DISPLAYS

    def SetDisplayValue(self, displayIndex, value):
        if displayIndex < 0 or displayIndex >= len(self._ALL_POWER_DISPLAYS):
            logger.error(f"Display index {displayIndex} is out of range.")
            return

        # logger.info(f"Setting PowerDisplay {displayIndex}{disabledString(ENABLE_POWER_DISPLAY)} to value {value}")
        self._ALL_POWER_DISPLAYS[displayIndex].Value = value


PowerDisplayManager = PowerDisplayManagerClass()
