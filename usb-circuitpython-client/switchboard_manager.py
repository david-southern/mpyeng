# import threading
# import time

import board
import microcontroller
import digitalio
import adafruit_logging as logging
from utils import ENABLE_SWITCHBOARD, disabledString

# The number of seconds to wait between checks of the Switchboard state.  Makes sure that the scanning thread doesn't
# take too much of the system's resources
SCANNING_INTERVAL = 0.2

logger = logging.getLogger("Switchboard")

class SwitchboardEndpoint:
    def __init__(self, uid: int, name: str, pin: microcontroller.Pin):
        self.uid = int(uid)
        self._name = name
        self._pin = pin
        self._dio = None

        if ENABLE_SWITCHBOARD:
            self._dio = digitalio.DigitalInOut(pin)

        logger.info(f"Created SwitchboardEndpoint: {self}{disabledString(ENABLE_SWITCHBOARD)}")

    def deinit(self):
        if not self.__dio is None:
            self.__dio.deinit()

    @property
    def UID(self) -> int:
        return self.uid

    @property
    def Name(self) -> int:
        return self._name

    @property
    def Pin(self) -> int:
        return self._pin

    @property
    def DIO(self) -> digitalio.DigitalInOut:
        return self._dio

    def __str__(self):
        return f"{self.UID}/{self.Name}{disabledString(ENABLE_SWITCHBOARD)} on pin {self.Pin}"


class Switchboard:
    def __init__(self, uid: int, name: str, sources: list[SwitchboardEndpoint], sinks: list[SwitchboardEndpoint]):
        self.uid = int(uid)
        self._name = name

        if len(sources) < 1:
            raise Exception(f"{self}: A Switchboard must have at least one Source")
        if len(sinks) < 1:
            raise Exception(f"{self}: A Switchboard must have at least one Sink")

        self._sources = sources
        self._sinks = sinks

        if ENABLE_SWITCHBOARD:
            for source in self._sources:
                source.DIO.switch_to_input(pull=digitalio.Pull.UP)

            for sink in self._sinks:
                sink.DIO.switch_to_input(pull=digitalio.Pull.UP)

        logger.info(f"Created Switchboard: {self}{disabledString(ENABLE_SWITCHBOARD)}")

    def deinit(self):
        # Release the DIO pins
        if ENABLE_SWITCHBOARD:
            for source in self._sources:
                source.deinit()
            for sink in self._sinks:
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
    def Name(self) -> int:
        return self._name

    @property
    def Connections(self) -> list[list[str]]:
        retval = []

        if ENABLE_SWITCHBOARD:
            for source in self._sources:
                source.DIO.switch_to_output(value=False, drive_mode=digitalio.DriveMode.PUSH_PULL)

                for sink in self._sinks:
                    if(not sink.DIO.value):
                        retval.append([source.Name, sink.Name])

                source.DIO.value = True
                source.DIO.switch_to_input(pull=digitalio.Pull.UP)

        return retval

    def __str__(self):
        return f"{self.UID}/{self.Name}{disabledString(ENABLE_SWITCHBOARD)}"


class SwitchboardManagerClass:
    def __init__(self) -> None:
        self._leftSwitchboard = Switchboard(
            1,
            "LeftSwitchboard",
            [
                SwitchboardEndpoint(1, "P1", board.D52),
                SwitchboardEndpoint(2, "P2", board.D53),
            ],
            [
                SwitchboardEndpoint(3, "DI1", board.D48),
                SwitchboardEndpoint(4, "DI2", board.D49),
                SwitchboardEndpoint(5, "DI3", board.D50),
                SwitchboardEndpoint(6, "DI4", board.D51),
            ],
        )

        self._rightSwitchboard = Switchboard(
            2,
            "RightSwitchboard",
            [
                SwitchboardEndpoint(7, "DO1", board.D38),
                SwitchboardEndpoint(8, "DO2", board.D39),
                SwitchboardEndpoint(9, "DO3", board.D40),
                SwitchboardEndpoint(10, "DO4", board.D41),
            ],
            [
                SwitchboardEndpoint(11, "B1", board.D42),
                SwitchboardEndpoint(12, "B2", board.D43),
                SwitchboardEndpoint(13, "B3", board.D44),
                SwitchboardEndpoint(14, "B4", board.D45),
                SwitchboardEndpoint(15, "B5", board.D46),
                SwitchboardEndpoint(16, "B6", board.D47),
            ],
        )

    def ConnectionStatus(self) -> list[list[str]]:
        return self._leftSwitchboard.Connections + self._rightSwitchboard.Connections

SwitchboardManager = SwitchboardManagerClass()
