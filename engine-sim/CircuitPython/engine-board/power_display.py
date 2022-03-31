import board
import adafruit_logging as logging
from tm1637 import TM1637

class PowerDisplay:
    def __init__(self, uid, clockPin, dataPin, displayName=None):
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
