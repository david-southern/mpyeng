from utils.device_manager import DeviceManager, PinNames, Systems
from switchboard.switchboard import Switchboard, SwitchboardSink, SwitchboardSource


class SwitchboardManagerClass:
    def __init__(self) -> None:
        self.__leftSwitchboard = Switchboard(1, "NullLeftSB", [], [])
        self.__rightSwitchboard = Switchboard(2, "NullCenterSB", [], [])

        if DeviceManager.IsEnabled(Systems.ANY_SWITCHBOARD):
            if DeviceManager.IsEnabled(Systems.LEFT_SWITCHBOARD):
                left_sources = [
                    SwitchboardSource(PinNames.Switchboard.Sources.LEFT_WING),
                    SwitchboardSource(PinNames.Switchboard.Sources.RIGHT_WING),
                    SwitchboardSource(PinNames.Switchboard.Sources.TRANS1),
                    SwitchboardSource(PinNames.Switchboard.Sources.TRANS2),
                    SwitchboardSource(PinNames.Switchboard.Sources.TRANS3),
                    SwitchboardSource(PinNames.Switchboard.Sources.TRANS4),
                ]
                left_sinks = [
                    SwitchboardSink(PinNames.Switchboard.Sinks.TRANS1),
                    SwitchboardSink(PinNames.Switchboard.Sinks.TRANS2),
                    SwitchboardSink(PinNames.Switchboard.Sinks.TRANS3),
                    SwitchboardSink(PinNames.Switchboard.Sinks.TRANS4),
                ]
                self.__leftSwitchboard = Switchboard(1, "LeftSwitchboard", left_sources, left_sinks)

            if DeviceManager.IsEnabled(Systems.RIGHT_SWITCHBOARD):
                right_sinks = [
                    SwitchboardSink(PinNames.Switchboard.Sinks.BUS1),
                    SwitchboardSink(PinNames.Switchboard.Sinks.BUS2),
                    SwitchboardSink(PinNames.Switchboard.Sinks.BUS3),
                    SwitchboardSink(PinNames.Switchboard.Sinks.BUS4),
                    SwitchboardSink(PinNames.Switchboard.Sinks.BUS5),
                    SwitchboardSink(PinNames.Switchboard.Sinks.BUS6),
                ]
                self.__rightSwitchboard = Switchboard(2, "CenterSwitchboard", [], right_sinks)

    def ConnectionStatus(self) -> list[tuple[str, str]]:
        return self.__leftSwitchboard.Connections + self.__rightSwitchboard.Connections


SwitchboardManager = SwitchboardManagerClass()
