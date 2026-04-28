# import threading
# import time

from machine import Pin

from utils.device_manager import Systems, DeviceManager
from utils.eng_utils import logger


class SwitchboardEndpoint:
    def __init__(self, name: str, is_source: bool = True):
        self.__name = name
        self.__is_source = is_source
        self.__pin = DeviceManager.ResolvePin(name) if DeviceManager.IsEnabled(Systems.ANY_SWITCHBOARD) else None
        self.__name = f"{'SwSource' if is_source else 'SwSink'}({name})"
        logger.info(f"Created SwitchboardEndpoint: {self}")

    @property
    def UID(self):
        return self.__name

    @property
    def Name(self):
        return self.__name

    @property
    def IsSource(self):
        return self.__is_source

    @property
    def DIO(self):
        return self.__pin

    def __str__(self):
        return self.Name


class SwitchboardSource(SwitchboardEndpoint):
    def __init__(self, name: str):
        super().__init__(name, is_source=True)
        self.__connectedSinks: list[SwitchboardSink] = []
        if self.DIO:
            self.DIO.Pin.init(mode=Pin.OUT)
            self.DIO.Pin.off()

    @property
    def ConnectedSinks(self) -> "list[SwitchboardSink]":
        return self.__connectedSinks


class SwitchboardSink(SwitchboardEndpoint):
    def __init__(self, name: str):
        super().__init__(name, is_source=False)
        self.__connectedSource: SwitchboardSource | None = None
        if self.DIO:
            self.DIO.Pin.init(mode=Pin.IN)

    @property
    def ConnectedSource(self) -> "SwitchboardSource | None":
        return self.__connectedSource


class Switchboard:
    def __init__(self, uid: int, name: str, sources: list[SwitchboardSource], sinks: list[SwitchboardSink]):
        self.uid = int(uid)
        self.__name = name

        # if len(sources) < 1:
        #     raise Exception(f"{self}: A Switchboard must have at least one Source")
        # if len(sinks) < 1:
        #     raise Exception(f"{self}: A Switchboard must have at least one Sink")

        self.__sources = sources
        self.__sinks = sinks

        logger.info(f"Created Switchboard: {self}{DeviceManager.SystemName(Systems.ANY_SWITCHBOARD)}")

    @property
    def UID(self) -> int:
        return self.uid

    @property
    def Name(self) -> str:
        return self.__name

    @property
    def Connections(self) -> list[tuple[str, str]]:
        retval = []

        if DeviceManager.IsEnabled(Systems.ANY_SWITCHBOARD):
            for sink in self.__sinks:
                if sink.ConnectedSource:
                    retval.append((sink.ConnectedSource.Name, sink.Name))

        return retval

    def __str__(self):
        return f"{self.UID}/{self.Name}{DeviceManager.SystemName(Systems.ANY_SWITCHBOARD)}"
