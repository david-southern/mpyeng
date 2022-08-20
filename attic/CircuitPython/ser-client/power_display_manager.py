import board
import adafruit_logging as logging
from tm1637 import TM1637

logger = logging.getLogger("PowerDisplayManager")


class PowerDisplay:
    def __init__(self, uid, dataPin, clockPin, displayName=None):
        self.__uid = uid
        self.__displayName = displayName
        self.__clockPin = clockPin
        self.__dataPin = dataPin

        self.__display = TM1637(clk=clockPin, dio=dataPin)
        self.Value = 0

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
        if type(value) == int:
            self.__display.number(value)
        else:
            self.__display.show(str(value))

    def __str__(self):
        return f"{self.UID}/{self.DisplayName}"


class PowerDisplayManagerClass:
    def __init__(self) -> None:
        self._ALL_POWER_DISPLAYS: list[PowerDisplay] = []
        self._ALL_POWER_DISPLAYS = []
        self._ALL_POWER_DISPLAYS.append(PowerDisplay(1, board.D8, board.D9, "Bus1"))
        self._ALL_POWER_DISPLAYS.append(PowerDisplay(2, board.D10, board.D11, "Bus2"))
        self._ALL_POWER_DISPLAYS.append(PowerDisplay(3, board.D12, board.D13, "Bus3"))
        self._ALL_POWER_DISPLAYS.append(PowerDisplay(4, board.D14, board.D15, "Bus4"))
        self._ALL_POWER_DISPLAYS.append(PowerDisplay(5, board.D16, board.D17, "Bus5"))
        self._ALL_POWER_DISPLAYS.append(PowerDisplay(6, board.D18, board.D19, "Bus6"))

    def AllDisplays(self) -> list[PowerDisplay]:
        return self._ALL_POWER_DISPLAYS

    def SetDisplayValue(self, displayIndex, value):
        if displayIndex < 0 or displayIndex >= len(self._ALL_POWER_DISPLAYS):
            logger.error(f"Display index {displayIndex} is out of range.")
            return

        logger.info(f"Setting PowerDisplay {displayIndex} to value {value}")
        self._ALL_POWER_DISPLAYS[displayIndex].Value = value


PowerDisplayManager = PowerDisplayManagerClass()
