from utils.eng_utils import ENABLE_SWITCHBOARD, ENABLE_RIGHT_SWITCHBOARD, ENABLE_LEFT_SWITCHBOARD
from utils.device_manager import device_manager
from switchboard.switchboard import Switchboard, SwitchboardEndpoint


class SwitchboardManagerClass:
    def __init__(self) -> None:
        self.__leftSwitchboard = Switchboard(1, "NullLeftSB", [], [])
        self.__rightSwitchboard = Switchboard(2, "NullCenterSB", [], [])

        if ENABLE_SWITCHBOARD:
            if ENABLE_LEFT_SWITCHBOARD:
                left_sources = device_manager.resolve_pin(
                    "switchboard",
                    "left_sources",
                    [
                        (1, "EngineTop", 22),
                        (2, "EngineBottom", 42),
                    ],
                )
                left_sinks = device_manager.resolve_pin(
                    "switchboard",
                    "left_sinks",
                    [
                        (3, "Dist1_In", 24),
                        (4, "Dist2_In", 23),
                        (5, "Dist3_In", 44),
                        (6, "Dist4_In", 43),
                    ],
                )
                self.__leftSwitchboard = Switchboard(
                    1,
                    "LeftSwitchboard",
                    [SwitchboardEndpoint(*ep) for ep in left_sources],
                    [SwitchboardEndpoint(*ep) for ep in left_sinks],
                )

            if ENABLE_RIGHT_SWITCHBOARD:
                right_sources = device_manager.resolve_pin(
                    "switchboard",
                    "right_sources",
                    [
                        (7, "Dist1_Out", 38),
                        (8, "Dist1_Out", 39),
                        (9, "Dist1_Out", 40),
                        (10, "Dist1_Out", 41),
                    ],
                )
                right_sinks = device_manager.resolve_pin(
                    "switchboard",
                    "right_sinks",
                    [
                        (11, "Bus1", 42),
                        (12, "Bus2", 43),
                        (13, "Bus3", 44),
                        (14, "Bus4", 45),
                        (15, "Bus5", 46),
                        (16, "Bus6", 47),
                    ],
                )
                self.__rightSwitchboard = Switchboard(
                    2,
                    "CenterSwitchboard",
                    [SwitchboardEndpoint(*ep) for ep in right_sources],
                    [SwitchboardEndpoint(*ep) for ep in right_sinks],
                )

    def ConnectionStatus(self) -> list[list[str]]:
        return self.__leftSwitchboard.Connections + self.__rightSwitchboard.Connections


SwitchboardManager = SwitchboardManagerClass()
