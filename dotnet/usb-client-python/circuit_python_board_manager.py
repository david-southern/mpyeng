from circuit_python_board import CircuitPythonBoard
from eng_board_resources import ClientType
from serial_port_info import SerialPortInfo


class CircuitPythonBoardManager:
    """
    Manages CircuitPython boards by maintaining mappings of known boards, ports, and client types.
    Methods:
        register_cpy_board(name: str, vid: int, pid: int, client_types: list[int]):
            Registers a new CircuitPython board with the manager.
        find_board(client_type: int) -> CircuitPythonBoard:
            Finds and returns a connected board for a given client type, scanning serial ports if
            necessary.
    """

    __KnownCPyBoards: dict[str, CircuitPythonBoard] = {}
    __PortToBoardMap: dict[str, CircuitPythonBoard] = {}
    __ClientTypeMap: dict[int, CircuitPythonBoard] = {}

    @staticmethod
    def register_cpy_board(name: str, vid: int, pid: int, client_types: list[int]):
        board_key = CircuitPythonBoardManager.__make_key(vid, pid)
        CircuitPythonBoardManager.__KnownCPyBoards[board_key] = CircuitPythonBoard(
            name, vid, pid, client_types
        )

    @staticmethod
    def __make_key(vid: int, pid: int) -> str:
        return f"{vid}//{pid}"

    @staticmethod
    def __get_board(vid: int, pid: int) -> CircuitPythonBoard:
        if vid is None or pid is None:
            return None
        return CircuitPythonBoardManager.__KnownCPyBoards.get(
            CircuitPythonBoardManager.__make_key(vid, pid)
        )

    @staticmethod
    def __unmap_board(client_board: CircuitPythonBoard):
        remove_client_mappings = [
            k
            for k, v in CircuitPythonBoardManager.__ClientTypeMap.items()
            if v == client_board
        ]
        for k in remove_client_mappings:
            del CircuitPythonBoardManager.__ClientTypeMap[k]

        remove_port_mappings = [
            k
            for k, v in CircuitPythonBoardManager.__PortToBoardMap.items()
            if v == client_board
        ]
        for k in remove_port_mappings:
            del CircuitPythonBoardManager.__PortToBoardMap[k]

    @staticmethod
    def find_board(client_type: int) -> CircuitPythonBoard:
        """
        Finds and returns a CircuitPythonBoard based on the given client type. This method first
        checks if there is a cached board for the client type and verifies its connection status. If
        no cached board is found or the cached board is not connected, it scans available serial
        ports to find a matching board.
        
        Args:
            client_type (int): The type of client to find the board for.
        Returns:
            CircuitPythonBoard: The found CircuitPythonBoard instance, or None if no matching board
            is found.
        """
        
        client_board = CircuitPythonBoardManager.__ClientTypeMap.get(client_type)
        if client_board:
            if client_board.is_connected:
                return client_board
            CircuitPythonBoardManager.__unmap_board(client_board)

        serial_ports = SerialPortInfo.scan_serial_ports()

        for port_info in serial_ports:
            if port_info.name is None:
                continue

            port_board = CircuitPythonBoardManager.__PortToBoardMap.get(port_info.name)
            if port_board:
                if not port_board.is_connected or port_board.com_port != port_info.name:
                    CircuitPythonBoardManager.__unmap_board(port_board)
                elif client_type in port_board.client_types:
                    return port_board

            board_info = CircuitPythonBoardManager.__get_board(
                port_info.vid, port_info.pid
            )
            if board_info is None:
                continue

            if client_type in board_info.client_types:
                if board_info.set_com_port(port_info.name):
                    for ct in board_info.client_types:
                        CircuitPythonBoardManager.__ClientTypeMap[ct] = board_info
                    CircuitPythonBoardManager.__PortToBoardMap[port_info.name] = (
                        board_info
                    )
                    return board_info

        print(f"No {client_type} board found")
        return None


# Initialization
def initialize_circuit_python_board_manager():
    all_clients = [ClientType.EngineeringBoard]

    CircuitPythonBoardManager.register_cpy_board(
        "Adafruit Feather RP2040", 0x239A, 0x80F2, all_clients
    )
    CircuitPythonBoardManager.register_cpy_board(
        "Adafruit Grand Central M4 Express with samd51p20",
        0x239A,
        0x8032,
        all_clients,
    )
    CircuitPythonBoardManager.register_cpy_board(
        "Adafruit ItsyBitsy M4 Express with samd51g19",
        0x239A,
        0x802C,
        all_clients,
    )
    CircuitPythonBoardManager.register_cpy_board(
        "Adafruit Feather M4 Express with samd51j19",
        0x239A,
        0x8026,
        all_clients,
    )
    CircuitPythonBoardManager.register_cpy_board(
        "Adafruit Trinket M0 with samd21e18", 0x239A, 0x801F, all_clients
    )


initialize_circuit_python_board_manager()
