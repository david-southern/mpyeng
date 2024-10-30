from eng_board_resources import ClientType, EnginePower, SystemPower, TransformerPower
from serial_protocol_handler import SerialProtocolHandler


class CircuitPythonBoard:
    """
    A class to represent a CircuitPython board and manage its communication via a serial protocol.
    Attributes:
    -----------
    name : str
        The name of the CircuitPython board.
    vid : str
        The vendor ID of the CircuitPython board.
    pid : str
        The product ID of the CircuitPython board.
    client_types : list[ClientType]
        A list of client types associated with the board.
    protocol_handler : SerialProtocolHandler, optional
        The protocol handler for serial communication
    Methods:
    --------
    set_com_port(com_port: str) -> bool:
        Sets the communication port for the board and establishes a connection.
    is_connected() -> bool:
        Checks if the board is connected.
    com_port() -> str:
        Returns the communication port name.
    query_engine_power() -> list[EnginePower]:
        Queries the engine power data from the board.
    query_transformer_power() -> list[TransformerPower]:
        Queries the transformer power data from the board.
    query_system_power() -> list[SystemPower]:
        Queries the system power data from the board.
    set_engine_power(data: list[EnginePower]) -> str:
        Sets the engine power data on the board.
    set_transformer_power(data: list[TransformerPower]) -> str:
        Sets the transformer power data on the board.
    set_system_power(data: list[SystemPower]) -> str:
        Sets the system power data on the board.
    """
    
    def __init__(self, name: str, vid: str, pid: str, client_types: list[ClientType]):
        self.name = name
        self.vid = vid
        self.pid = pid
        self.client_types = client_types
        self.protocol_handler = None

    def set_com_port(self, com_port: str) -> bool:
        self.protocol_handler = SerialProtocolHandler(com_port, self.name)

        if not self.protocol_handler.establish_connection():
            self.protocol_handler.dispose()
            self.protocol_handler = None
            return False

        return True

    @property
    def is_connected(self) -> bool:
        return self.protocol_handler.is_connected if self.protocol_handler else False

    @property
    def com_port(self) -> str:
        return self.protocol_handler.port_name if self.protocol_handler else None

    def query_engine_power(self) -> list[EnginePower]:
        return (
            self.protocol_handler.query_engine_power() if self.protocol_handler else []
        )

    def query_transformer_power(self) -> list[TransformerPower]:
        return (
            self.protocol_handler.query_transformer_power()
            if self.protocol_handler
            else []
        )

    def query_system_power(self) -> list[SystemPower]:
        return (
            self.protocol_handler.query_system_power() if self.protocol_handler else []
        )

    def set_engine_power(self, data: list[EnginePower]) -> str:
        return (
            self.protocol_handler.set_engine_power(data)
            if self.protocol_handler
            else ""
        )

    def set_transformer_power(self, data: list[TransformerPower]) -> str:
        return (
            self.protocol_handler.set_transformer_power(data)
            if self.protocol_handler
            else ""
        )

    def set_system_power(self, data: list[SystemPower]) -> str:
        return (
            self.protocol_handler.set_system_power(data)
            if self.protocol_handler
            else ""
        )

    def __str__(self) -> str:
        client_types_str = ", ".join(str(ct) for ct in self.client_types)
        return f"{self.name}//{self.vid} - ClientTypes: {client_types_str}"
