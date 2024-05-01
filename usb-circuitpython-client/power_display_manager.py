import board
from tm1637 import TM1637
from utils import ENABLE_POWER_DISPLAY, disabledString, logger

#   CLK = board.D6
#   DIO = board.D13
#   time.sleep(5)
#   while True:
#     t = time.localtime()
#     time.sleep(60-(t.tm_sec%60))

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
        # logger.info(f"Setting PowerDisplay {self.UID}{disabledString(ENABLE_POWER_DISPLAY)} to value {value}")

    def __str__(self):
        return f"{self.UID}/{self.DisplayName}{disabledString(ENABLE_POWER_DISPLAY)}"


class PowerDisplayManagerClass:
    def __init__(self) -> None:
        self._ALL_POWER_DISPLAYS: list[PowerDisplay] = []
        self._ALL_POWER_DISPLAYS = []
        self._ALL_POWER_DISPLAYS.append(PowerDisplay(1, board.D0, board.D1, "Eng1"))
        self._ALL_POWER_DISPLAYS.append(PowerDisplay(2, board.D2, board.D3, "Eng2"))
        self._ALL_POWER_DISPLAYS.append(PowerDisplay(3, board.D4, board.D5, "Dist1Max"))
        self._ALL_POWER_DISPLAYS.append(PowerDisplay(4, board.D6, board.D7, "Dist1Cur"))
        self._ALL_POWER_DISPLAYS.append(PowerDisplay(5, board.D8, board.D9, "Dist2Max"))
        self._ALL_POWER_DISPLAYS.append(PowerDisplay(6, board.D10, board.D11, "Dist2Cur"))
        self._ALL_POWER_DISPLAYS.append(PowerDisplay(7, board.D12, board.D13, "Dist3Max"))
        self._ALL_POWER_DISPLAYS.append(PowerDisplay(8, board.D14, board.D15, "Dist3Cur"))
        self._ALL_POWER_DISPLAYS.append(PowerDisplay(9, board.D16, board.D17, "Dist4Max"))
        self._ALL_POWER_DISPLAYS.append(PowerDisplay(10, board.D18, board.D19, "Dist4Cur"))

    def AllDisplays(self) -> list[PowerDisplay]:
        return self._ALL_POWER_DISPLAYS

    def SetDisplayValue(self, displayIndex, value):
        if displayIndex < 0 or displayIndex >= len(self._ALL_POWER_DISPLAYS):
            logger.error(f"Display index {displayIndex} is out of range.")
            return

        # logger.info(f"Setting PowerDisplay {displayIndex}{disabledString(ENABLE_POWER_DISPLAY)} to value {value}")
        self._ALL_POWER_DISPLAYS[displayIndex].Value = value


PowerDisplayManager = PowerDisplayManagerClass()
