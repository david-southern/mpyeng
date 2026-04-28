from utils.protocol_resources import (
    CUR_DISPLAY,
    MAX_DISPLAY,
)
from utils.eng_utils import logger
from utils.device_manager import DeviceManager, PinNames, Systems
from power_display.power_display import PowerDisplay


class PowerDisplayManagerClass:
    _DISPLAY_NAMES = [
        "LEFT_WING",
        "RIGHT_WING",
        "TRANS1",
        "TRANS2",
        "TRANS3",
        "TRANS4",
        "BUS1",
        "BUS2",
        "BUS3",
        "BUS4",
        "BUS5",
        "BUS6",
    ]

    _DEFAULT_DISPLAY_PINS = [
        (
            DeviceManager.ResolvePin(getattr(PinNames.PowerDisplays.Max.Data, displayName)),
            DeviceManager.ResolvePin(getattr(PinNames.PowerDisplays.Max.Clock, displayName)),
        )
        for displayName in _DISPLAY_NAMES
    ] + [
        (
            DeviceManager.ResolvePin(getattr(PinNames.PowerDisplays.Current.Data, displayName)),
            DeviceManager.ResolvePin(getattr(PinNames.PowerDisplays.Current.Clock, displayName)),
        )
        for displayName in _DISPLAY_NAMES
    ]

    def __init__(self) -> None:
        self.__ALL_POWER_DISPLAYS: list[PowerDisplay] = []
        self.__ALL_POWER_DISPLAYS = []
        if DeviceManager.IsEnabled(Systems.POWER_DISPLAY):
            for display_index, (data_pin, clock_pin) in enumerate(self._DEFAULT_DISPLAY_PINS):
                displayName = self._DISPLAY_NAMES[display_index % len(self._DISPLAY_NAMES)]
                self.__ALL_POWER_DISPLAYS.append(PowerDisplay(display_index + 1, displayName, data_pin, clock_pin))

    def AllDisplays(self) -> list[PowerDisplay]:
        return self.__ALL_POWER_DISPLAYS

    def SetDisplayCurValue(self, displayName: str, value: int):
        if not DeviceManager.IsEnabled(Systems.POWER_DISPLAY):
            return

        displayName += CUR_DISPLAY
        try:
            display = next(d for d in self.__ALL_POWER_DISPLAYS if d.DisplayName == displayName)
        except StopIteration:
            display = None

        if display is None:
            logger.error(f"Unknown display name '{displayName}'.")
            return

        # logger.info(f"Setting PowerDisplay {displayIndex}{DeviceManager.SystemName(DeviceManager.IsEnabled(Systems.POWER_DISPLAY))} to value {value}")
        display.Value = value

    def SetDisplayMaxValue(self, displayName: str, value: int):
        if not DeviceManager.IsEnabled(Systems.POWER_DISPLAY):
            return

        displayName += MAX_DISPLAY
        try:
            display = next(d for d in self.__ALL_POWER_DISPLAYS if d.DisplayName == displayName)
        except StopIteration:
            display = None

        if display is None:
            logger.error(f"Unknown display name '{displayName}'.")
            return

        # logger.info(f"Setting PowerDisplay {displayIndex}{DeviceManager.SystemName(DeviceManager.IsEnabled(Systems.POWER_DISPLAY))} to value {value}")
        display.Value = value

    def SetDisplayValue(self, displayName: str, value: int):
        if not DeviceManager.IsEnabled(Systems.POWER_DISPLAY):
            return

        try:
            display = next(d for d in self.__ALL_POWER_DISPLAYS if d.DisplayName == displayName)
        except StopIteration:
            display = None

        if display is None:
            logger.error(f"Unknown display name '{displayName}'.")
            return

        # logger.info(f"Setting PowerDisplay {displayIndex}{DeviceManager.SystemName(DeviceManager.IsEnabled(Systems.POWER_DISPLAY))} to value {value}")
        display.Value = value


PowerDisplayManager = PowerDisplayManagerClass()
