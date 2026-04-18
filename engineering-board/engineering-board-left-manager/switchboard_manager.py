# import threading
# import time

from machine import Pin  # pyright: ignore[reportMissingImports]
from eng_utils import ENABLE_RIGHT_SWITCHBOARD, ENABLE_LEFT_SWITCHBOARD, ENABLE_SWITCHBOARD, disabledString, logger

# The number of seconds to wait between checks of the Switchboard state.  Makes sure that the scanning thread doesn't
# take too much of the system's resources
SCANNING_INTERVAL = 0.2

class SwitchboardEndpoint:
    def __init__(self, uid: int, name: str, pin_num: int):
        self.uid = int(uid)
        self.__name = name
        self.__pin_num = pin_num
        self.__pin = Pin(pin_num, Pin.IN, Pin.PULL_UP) if ENABLE_SWITCHBOARD else None
        logger.info(f"Created SwitchboardEndpoint: {self}{disabledString(ENABLE_SWITCHBOARD)}")

    def deinit(self):
        pass  # machine.Pin has no deinit

    @property
    def UID(self) -> int:
        return self.uid

    @property
    def Name(self) -> str:
        return self.__name

    @property
    def Pin(self) -> int:
        return self.__pin_num

    @property
    def DIO(self) -> "Pin | None":
        return self.__pin

    def __str__(self):
        return f"{self.Name}/{self.Pin}{disabledString(ENABLE_SWITCHBOARD)}"


class Switchboard:
    def __init__(self, uid: int, name: str, sources: list[SwitchboardEndpoint], sinks: list[SwitchboardEndpoint]):
        self.uid = int(uid)
        self.__name = name

        # if len(sources) < 1:
        #     raise Exception(f"{self}: A Switchboard must have at least one Source")
        # if len(sinks) < 1:
        #     raise Exception(f"{self}: A Switchboard must have at least one Sink")

        self.__sources = sources
        self.__sinks = sinks

        if ENABLE_SWITCHBOARD:
            for source in self.__sources:
                source.DIO.init(Pin.IN, pull=Pin.PULL_UP)

            for sink in self.__sinks:
                sink.DIO.init(Pin.IN, pull=Pin.PULL_UP)

        logger.info(f"Created Switchboard: {self}{disabledString(ENABLE_SWITCHBOARD)}")

    def deinit(self):
        # Release the DIO pins
        if ENABLE_SWITCHBOARD:
            for source in self.__sources:
                source.deinit()
            for sink in self.__sinks:
                sink.deinit()

    def __enter__(self):
        """No-op used by Context Managers."""
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """
        Automatically de-initializes when exiting a context.
        """
        self.deinit()

    @property
    def UID(self) -> int:
        return self.uid

    @property
    def Name(self) -> str:
        return self.__name

    @property
    def Connections(self) -> list[list[str]]:
        retval = []

        if ENABLE_SWITCHBOARD:
            for source in self.__sources:
                source.DIO.init(Pin.OUT, value=0)

                for sink in self.__sinks:
                    if not sink.DIO.value():
                        retval.append([source.Name, sink.Name])

                source.DIO.value(1)
                source.DIO.init(Pin.IN, pull=Pin.PULL_UP)

        return retval

    def __str__(self):
        return f"{self.UID}/{self.Name}{disabledString(ENABLE_SWITCHBOARD)}"


class SwitchboardManagerClass:
    def __init__(self) -> None:
        self.__leftSwitchboard = Switchboard(1, "NullLeftSB", [], [])
        self.__rightSwitchboard = Switchboard(2, "NullCenterSB", [], [])

        if ENABLE_SWITCHBOARD:
            if ENABLE_LEFT_SWITCHBOARD:
                self.__leftSwitchboard = Switchboard(
                    1,
                    "LeftSwitchboard",
                    [
                        SwitchboardEndpoint(1, "EngineTop", 22),    # TODO: verify GP22 for RP2350 wiring
                        SwitchboardEndpoint(2, "EngineBottom", 42),  # TODO: verify GP42 for RP2350 wiring
                    ],
                    [
                        SwitchboardEndpoint(3, "Dist1_In", 24),  # TODO: verify GP24 for RP2350 wiring
                        SwitchboardEndpoint(4, "Dist2_In", 23),  # TODO: verify GP23 for RP2350 wiring
                        SwitchboardEndpoint(5, "Dist3_In", 44),  # TODO: verify GP44 for RP2350 wiring
                        SwitchboardEndpoint(6, "Dist4_In", 43),  # TODO: verify GP43 for RP2350 wiring
                    ],
                )

            if ENABLE_RIGHT_SWITCHBOARD:
                self.__rightSwitchboard = Switchboard(
                    2,
                    "CenterSwitchboard",
                    [
                        SwitchboardEndpoint(7, "Dist1_Out", 38),   # TODO: verify GP38 for RP2350 wiring
                        SwitchboardEndpoint(8, "Dist1_Out", 39),   # TODO: verify GP39 for RP2350 wiring
                        SwitchboardEndpoint(9, "Dist1_Out", 40),   # TODO: verify GP40 for RP2350 wiring
                        SwitchboardEndpoint(10, "Dist1_Out", 41),  # TODO: verify GP41 for RP2350 wiring
                    ],
                    [
                        SwitchboardEndpoint(11, "Bus1", 42),  # TODO: verify GP42 for RP2350 wiring
                        SwitchboardEndpoint(12, "Bus2", 43),  # TODO: verify GP43 for RP2350 wiring
                        SwitchboardEndpoint(13, "Bus3", 44),  # TODO: verify GP44 for RP2350 wiring
                        SwitchboardEndpoint(14, "Bus4", 45),  # TODO: verify GP45 for RP2350 wiring
                        SwitchboardEndpoint(15, "Bus5", 46),  # TODO: verify GP46 for RP2350 wiring
                        SwitchboardEndpoint(16, "Bus6", 47),  # TODO: verify GP47 for RP2350 wiring
                    ],
                )

    def ConnectionStatus(self) -> list[list[str]]:
        return self.__leftSwitchboard.Connections + self.__rightSwitchboard.Connections

SwitchboardManager = SwitchboardManagerClass()
