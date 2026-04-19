# import threading
# import time

from machine import Pin
from utils.eng_utils import ENABLE_SWITCHBOARD, disabledString, logger


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
                if source.DIO:
                    source.DIO.init(Pin.IN, pull=Pin.PULL_UP)

            for sink in self.__sinks:
                if sink.DIO:
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
                if source.DIO:
                    source.DIO.init(Pin.OUT, value=0)

                for sink in self.__sinks:
                    if sink.DIO and not sink.DIO.value():
                        retval.append([source.Name, sink.Name])

                if source.DIO:
                    source.DIO.value(1)
                    source.DIO.init(Pin.IN, pull=Pin.PULL_UP)

        return retval

    def __str__(self):
        return f"{self.UID}/{self.Name}{disabledString(ENABLE_SWITCHBOARD)}"
