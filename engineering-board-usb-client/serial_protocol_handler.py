import json
import threading

import serial

from eng_board_resources import (
    EnginePower,
    SystemPower,
    TransformerPower,
)
from utils import log_debug


class SerialProtocolHandler:
    """
    A class to handle serial communication with a specific protocol.
    Methods:
        is_connected() -> bool:
            Checks if the serial port is open and the connection is valid.
        reset_port():
            Resets the input and output buffers of the serial port.
        establish_connection() -> bool:
            Establishes a connection by sending an initialization command and checking the response.
        query_engine_power() -> list[EnginePower]:
            Queries the engine power data from the device.
        query_transformer_power() -> list[TransformerPower]:
            Queries the transformer power data from the device.
        query_system_power() -> list[SystemPower]:
            Queries the system power data from the device.
        query_list(protocol_token: str) -> list:
            Sends a query command and returns the parsed response as a list.
        set_engine_power(data: list[EnginePower]) -> str:
            Sends a set command with engine power data.
        set_transformer_power(data: list[TransformerPower]) -> str:
            Sends a set command with transformer power data.
        set_system_power(data: list[SystemPower]) -> str:
            Sends a set command with system power data.
        set_list(protocol_token: str, data: list) -> str:
            Sends a set command with the given data and returns the response.
    """

    DEFAULT_BAUD_RATE = 9600

    SER_PROTO_RESPONSE_DELIMITER = "|"
    SER_PROTO_QUERY = "_QUERY"
    SER_PROTO_RESPONSE = "_RESPONSE"
    SER_PROTO_SET = "_SET"

    SER_PROTO_INIT_HEADER = "SP_INIT"
    SER_PROTO_INIT_RESPONSE = "SP_READY"
    SER_PROTO_OK = "SP_OK"
    SER_PROTO_ERR = "SP_ERR;"
    SER_PROTO_ENGINE_POWER = "SP_ENG_POWER"
    SER_PROTO_TRANSFORMER_POWER = "SP_TRANS_POWER"
    SER_PROTO_SYSTEM_POWER = "SP_SYS_POWER"

    def __init__(self, port_name: str, board_name: str):
        self.port_name = port_name
        self.board_name = board_name
        self.communication_lock = threading.Lock()
        self.is_valid = False

        self.port = serial.Serial(
            port=port_name,
            baudrate=self.DEFAULT_BAUD_RATE,
            parity=serial.PARITY_NONE,
            bytesize=serial.EIGHTBITS,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.5,
            write_timeout=0.5,
        )
        self.port.dtr = True

    @property
    def is_connected(self) -> bool:
        return self.port.is_open and self.is_valid

    def reset_port(self):
        self.port.reset_input_buffer()
        self.port.reset_output_buffer()

    def establish_connection(self) -> bool:
        if self.port is None:
            return False

        with self.communication_lock:
            try:
                self.reset_port()
                self.port.write((self.SER_PROTO_INIT_HEADER + "\n").encode("utf-8"))
                response = self.port.readline().decode("utf-8").strip()

                if response != self.SER_PROTO_INIT_RESPONSE:
                    print(
                        f"ERR: {self} is not a SerProto client: Invalid init response: {response}"
                    )
                    return False

                self.is_valid = True
                return True
            except serial.SerialTimeoutException:
                print(
                    f"ERR: {self} is not a SerProto client: Timeout during establish_connection"
                )
            except Exception as ex:
                print(
                    f"ERR: {self} is not a SerProto client: Unknown exception in establish_connection: {str(ex)}",
                    exc_info=True,
                )

            return False

    def query_engine_power(self) -> list[EnginePower]:
        log_debug("Sending QueryEnginePower")
        return [
            EnginePower.from_json(jsonBlob)
            for jsonBlob in self.query_list(self.SER_PROTO_ENGINE_POWER)
        ]

    def query_transformer_power(self) -> list[TransformerPower]:
        log_debug("Sending QueryTransformerPower")
        return [
            TransformerPower.from_json(jsonBlob)
            for jsonBlob in self.query_list(self.SER_PROTO_TRANSFORMER_POWER)
        ]

    def query_system_power(self) -> list[SystemPower]:
        log_debug("Sending QuerySystemPower")
        return [
            SystemPower.from_json(jsonBlob)
            for jsonBlob in self.query_list(self.SER_PROTO_SYSTEM_POWER)
        ]

    def query_list(self, protocol_token: str) -> list:
        empty_result = []

        with self.communication_lock:
            try:
                self.reset_port()
                protocol_command = protocol_token + self.SER_PROTO_QUERY

                log_debug(f"DBG: QueryList: Sending: {protocol_command}")
                self.port.write((protocol_command + "\n").encode("utf-8"))
                response = self.port.readline().decode("utf-8").strip()
                log_debug(f"DBG: QueryList: Received: {response}")

                response_parts = response.split(self.SER_PROTO_RESPONSE_DELIMITER)

                if (
                    len(response_parts) != 2
                    or response_parts[0] != protocol_token + self.SER_PROTO_RESPONSE
                ):
                    print(
                        f"ERR: SerProto {self.port_name}({self.board_name}): Invalid query list response: {response}"
                    )
                    return empty_result

                try:
                    return json.loads(response_parts[1])
                except Exception as ex:
                    print(
                        f"ERR: SerProto {self.port_name}({self.board_name}): Invalid query list response format: {response}: {str(ex)}",
                        exc_info=True,
                    )
                    return empty_result
            except serial.SerialTimeoutException:
                print(
                    f"ERR: SerProto {self.port_name}({self.board_name}): Timeout during query list"
                )

            return empty_result

    def set_engine_power(self, data: list[EnginePower]) -> str:
        json_blob = [EnginePower.to_json(enginePower) for enginePower in data]
        return self.set_list(self.SER_PROTO_ENGINE_POWER, json_blob)

    def set_transformer_power(self, data: list[TransformerPower]) -> str:
        json_blob = [
            TransformerPower.to_json(transformerPower) for transformerPower in data
        ]
        return self.set_list(self.SER_PROTO_TRANSFORMER_POWER, json_blob)

    def set_system_power(self, data: list[SystemPower]) -> str:
        json_blob = [SystemPower.to_json(systemPower) for systemPower in data]
        return self.set_list(self.SER_PROTO_SYSTEM_POWER, json_blob)

    def set_list(self, protocol_token: str, data: list) -> str:
        with self.communication_lock:
            try:
                self.reset_port()

                request = (
                    protocol_token
                    + self.SER_PROTO_SET
                    + self.SER_PROTO_RESPONSE_DELIMITER
                    + json.dumps(data)
                )
                self.port.write((request + "\n").encode("utf-8"))
                response = self.port.readline().decode("utf-8").strip()

                if response != self.SER_PROTO_OK and not response.startswith(
                    self.SER_PROTO_ERR
                ):
                    print(f"ERR: {self}: Invalid set list response: {response}")
                    return self.SER_PROTO_ERR

                return response
            except serial.SerialTimeoutException:
                print(f"ERR: {self}: Timeout during set list")
                return self.SER_PROTO_ERR + ":Timeout"

    def __str__(self):
        return f"SerProto:{self.port_name}({self.board_name})"

    def __del__(self):
        self.dispose()

    def dispose(self):
        log_debug(f"{self}: Disposing")
        self.is_valid = False
        if self.port.is_open:
            log_debug(f"{self}: Closing SerialPort")
            self.port.close()
        log_debug(f"{self}: Disposing SerialPort")
        del self.port
