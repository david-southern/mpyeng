# import threading
# import time

import board
import microcontroller
import digitalio
from eng_utils import ENABLE_RIGHT_SWITCHBOARD, ENABLE_LEFT_SWITCHBOARD, ENABLE_SWITCHBOARD, disabledString, logger

# The number of seconds to wait between checks of the Switchboard state.  Makes sure that the scanning thread doesn't
# take too much of the system's resources
SCANNING_INTERVAL = 0.2

class SwitchboardEndpoint:
    def __init__(self, uid: int, name: str, pin: microcontroller.Pin):
        self.uid = int(uid)
        self.__name = name
        self.__pin = pin
        self.__dio = None

        if ENABLE_SWITCHBOARD:
            self.__dio = digitalio.DigitalInOut(pin)

        logger.info(f"Created SwitchboardEndpoint: {self}{disabledString(ENABLE_SWITCHBOARD)}")

    def deinit(self):
        if not self.__dio is None:
            self.__dio.deinit()

    @property
    def UID(self) -> int:
        return self.uid

    @property
    def Name(self) -> str:
        return self.__name

    @property
    def Pin(self) -> int:
        return self.__pin

    @property
    def DIO(self) -> digitalio.DigitalInOut:
        return self.__dio

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
                source.DIO.switch_to_input(pull=digitalio.Pull.UP)

            for sink in self.__sinks:
                sink.DIO.switch_to_input(pull=digitalio.Pull.UP)

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
                source.DIO.switch_to_output(value=False, drive_mode=digitalio.DriveMode.PUSH_PULL)

                for sink in self.__sinks:
                    if(not sink.DIO.value):
                        retval.append([source.Name, sink.Name])

                source.DIO.value = True
                source.DIO.switch_to_input(pull=digitalio.Pull.UP)

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
                        SwitchboardEndpoint(1, "EngineTop", board.D22),
                        SwitchboardEndpoint(2, "EngineBottom", board.D42),
                    ],
                    [
                        SwitchboardEndpoint(3, "Dist1_In", board.D24),
                        SwitchboardEndpoint(4, "Dist2_In", board.D23),
                        SwitchboardEndpoint(5, "Dist3_In", board.D44),
                        SwitchboardEndpoint(6, "Dist4_In", board.D43),
                    ],
                )

            if ENABLE_RIGHT_SWITCHBOARD:
                self.__rightSwitchboard = Switchboard(
                    2,
                    "CenterSwitchboard",
                    [
                        SwitchboardEndpoint(7, "Dist1_Out", board.D38),
                        SwitchboardEndpoint(8, "Dist1_Out", board.D39),
                        SwitchboardEndpoint(9, "Dist1_Out", board.D40),
                        SwitchboardEndpoint(10, "Dist1_Out", board.D41),
                    ],
                    [
                        SwitchboardEndpoint(11, "Bus1", board.D42),
                        SwitchboardEndpoint(12, "Bus2", board.D43),
                        SwitchboardEndpoint(13, "Bus3", board.D44),
                        SwitchboardEndpoint(14, "Bus4", board.D45),
                        SwitchboardEndpoint(15, "Bus5", board.D46),
                        SwitchboardEndpoint(16, "Bus6", board.D47),
                    ],
                )

    def ConnectionStatus(self) -> list[list[str]]:
        return self.__leftSwitchboard.Connections + self.__rightSwitchboard.Connections

SwitchboardManager = SwitchboardManagerClass()
