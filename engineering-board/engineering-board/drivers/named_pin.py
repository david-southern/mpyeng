from machine import Pin


# For some reason, Micropython does not provide a way to get the name of a Pin from the Pin object
# itself, even though the name is required to construct the Pin. This class wraps a Pin and stores
# its name for easy access.
class NamedPin:
    def __init__(self, name: str):
        self.__name = name
        self.__pin = Pin(name)

    @property
    def Name(self) -> str:
        return self.__name

    @property
    def Pin(self) -> Pin:
        return self.__pin
