from drivers.named_pin import NamedPin
from utils.device_manager import DeviceManager, Systems
from utils.dave_tm1637 import TM1637
from utils.eng_utils import logger
from power_display.constants import SHOW_POWER_DISPLAY_DIAGS


class PowerDisplay:
    def __init__(self, uid, displayName: str, dataPin: NamedPin, clockPin: NamedPin):
        self.__uid = uid
        self.__displayName = displayName
        self.__clockPin = clockPin
        self.__dataPin = dataPin

        if DeviceManager.IsEnabled(Systems.POWER_DISPLAY):
            self.__display = TM1637(clockPin.Pin, dataPin.Pin)

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
        if DeviceManager.IsEnabled(Systems.POWER_DISPLAY):
            if isinstance(value, int):
                self.__display.number(value)
            else:
                self.__display.show(str(value))
            if SHOW_POWER_DISPLAY_DIAGS:
                logger.info(f"Setting PowerDisplay {self} to value {value}")

    def __str__(self):
        return f"{DeviceManager.SystemName(Systems.POWER_DISPLAY)}({self.DisplayName}/D:{self.DataPin.Name}/C:{self.ClockPin.Name})"
