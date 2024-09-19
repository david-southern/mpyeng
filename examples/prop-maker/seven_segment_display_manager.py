# If you get an error that the board module is not found, install it with this commnand:
#   pip install --break-system-packages adafruit-blinka

import board
from lib.tm1637 import TM1637
from eng_utils import logger

# Running the TM1637 displays when the board does not have an external +5V supply causes the Arduino
# to crash erratically. Providing an external +5V supply stops this happening, but I'll leave this
# enable flag here so that the board can be run without external power if desired.
ENABLE_SEVEN_SEGMENT_DISPLAY = True
SHOW_SEVEN_SEG_DIAGS = False

class SevenSegmentDisplay:
    def __init__(self, uid, dataPin, clockPin, displayName=None):
        self.__uid = uid
        self.__displayName = displayName
        self.__clockPin = clockPin
        self.__dataPin = dataPin
        if ENABLE_SEVEN_SEGMENT_DISPLAY:
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

        if ENABLE_SEVEN_SEGMENT_DISPLAY:
            if type(value) == int:
                self.__display.number(value)
            else:
                self.__display.show(str(value))

        if SHOW_SEVEN_SEG_DIAGS:
            logger.info(f"Setting SevenSegmentDisplay {self} to value {value}")

    def __str__(self):
        return f"{self.DisplayName}/D:{self.DataPin}/C:{self.ClockPin}"

 
class SevenSegmentDisplayManagerClass:
    def __init__(self) -> None:
        self._ALL_POWER_DISPLAYS: list[SevenSegmentDisplay] = []
        self._ALL_POWER_DISPLAYS.append(SevenSegmentDisplay(3, board.D5, board.D6, "SevenSeg1"))
        # self._ALL_POWER_DISPLAYS.append(SevenSegmentDisplay(4, board.D16, board.D17, "Dist1Cur"))

    def AllDisplays(self) -> list[SevenSegmentDisplay]:
        return self._ALL_POWER_DISPLAYS

    def SetDisplayValue(self, displayIndex, value):
        if displayIndex < 0 or displayIndex >= len(self._ALL_POWER_DISPLAYS):
            logger.error(f"Display index {displayIndex} is out of range.")
            return

        self._ALL_POWER_DISPLAYS[displayIndex].Value = value


SevenSegmentDisplayManager = SevenSegmentDisplayManagerClass()
