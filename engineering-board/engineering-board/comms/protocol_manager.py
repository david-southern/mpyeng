import json
import time
import socket
import network
import secrets

from utils.demo_data_manager import DemoDataManager
from utils.protocol_resources import EnginePower, SystemPower, TransformerPower, json_string
from utils.eng_utils import format_hex_list, shortString, logger
from comms.constants import (
    PENDING_CRLF_DELAY_SEC,
    BYTE_CR,
    BYTE_LF,
    SER_PROTO_DIAGS,
    SER_PROTO_RESPONSE_DELIMITER,
    SER_PROTO_INIT_HEADER,
    SER_PROTO_INIT_RESPONSE,
    SER_PROTO_OK,
    SER_PROTO_ERR,
    SER_PROTO_ENGINE_POWER_QUERY,
    SER_PROTO_ENGINE_POWER_RESPONSE,
    SER_PROTO_ENGINE_POWER_SET,
    SER_PROTO_TRANSFORMER_POWER_QUERY,
    SER_PROTO_TRANSFORMER_POWER_RESPONSE,
    SER_PROTO_TRANSFORMER_POWER_SET,
    SER_PROTO_SYSTEM_POWER_QUERY,
    SER_PROTO_SYSTEM_POWER_RESPONSE,
    SER_PROTO_SYSTEM_POWER_SET,
)


class ProtocolManagerClass:
    def __init__(self):
        logger.info("ProtocolManager: Connecting to WiFi...")
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
            timeout_ms = 0
            while not wlan.isconnected() and timeout_ms < 30000:
                time.sleep_ms(100)
                timeout_ms += 100
            if not wlan.isconnected():
                raise RuntimeError("WiFi connection timed out after 30s")
        ip = wlan.ifconfig()[0]
        logger.info(f"WiFi connected: IP={ip}")

        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__server.bind(("", secrets.TCP_PORT))
        self.__server.listen(1)
        self.__server.setblocking(False)
        self.__client: socket.socket = None  # pyright: ignore[reportAttributeAccessIssue]
        self.__pendingCommand = bytearray(0)
        self.__lastReadTime = 0
        self.__total_commands_handled = 0
        self.__total_bytes_sent = 0
        self.__total_bytes_read = 0

        logger.info(f"TCP server listening on port {secrets.TCP_PORT}")

    @property
    def IsConnected(self):
        return self.__client is not None

    @property
    def TotalBytesRead(self):
        return self.__total_bytes_read

    @property
    def TotalBytesSent(self):
        return self.__total_bytes_sent

    @property
    def TotalCommandsHandled(self):
        return self.__total_commands_handled

    def __disconnect(self):
        if self.__client is not None:
            try:
                self.__client.close()
            except OSError:
                pass
            self.__client = None  # pyright: ignore[reportAttributeAccessIssue]
            self.__pendingCommand = bytearray(0)
            logger.info("TCP client disconnected")

    def HandleComms(self):
        if self.__client is None:
            try:
                self.__client, addr = self.__server.accept()
                self.__client.setblocking(False)
                logger.info(f"TCP client connected from {addr[0]}:{addr[1]}")
            except OSError:
                pass  # No pending connection — normal with non-blocking accept
            return

        try:
            chunk = self.__client.recv(256)
            if len(chunk) == 0:
                self.__disconnect()
                return
            if SER_PROTO_DIAGS > 4:
                logger.info(f"Read TCP chunk: {format_hex_list(chunk)}")
            self.__pendingCommand += chunk
            if SER_PROTO_DIAGS > 3:
                logger.info(f"Pending command: {format_hex_list(self.__pendingCommand)}")
            self.__lastReadTime = time.ticks_ms()
        except OSError:
            pass  # No data available — normal with non-blocking socket

        self.__CheckCommand()

    def __SendPacket(self, command, data=None):
        packet = command
        if data is not None:
            jsonData = json_string(data).replace("|", "").replace("\r", "").replace("\n", "")
            packet += f"{SER_PROTO_RESPONSE_DELIMITER}{jsonData}"
        packet += "\n"

        if SER_PROTO_DIAGS > 0:
            logger.info(f"Sending response packet: {packet}")

        try:
            self.__client.send(packet.encode("utf-8"))
            self.__total_bytes_sent += len(packet)
        except OSError as ex:
            logger.error(f"Error sending TCP packet: {ex}")
            self.__disconnect()

    def __HandleCommand(self, command, data=None):
        if command == SER_PROTO_INIT_HEADER:
            if SER_PROTO_DIAGS > 0:
                logger.info("Received INIT command")

            # Clear any pending buffered data from a previous (possibly failed) connection
            self.__pendingCommand = bytearray(0)

            self.__SendPacket(SER_PROTO_INIT_RESPONSE)
            self.__total_commands_handled += 1
            return

        if command == SER_PROTO_ENGINE_POWER_QUERY:
            if SER_PROTO_DIAGS > 0:
                logger.info("Received ENGINE POWER QUERY command")

            self.__SendPacket(SER_PROTO_ENGINE_POWER_RESPONSE, DemoDataManager.GetEnginePowerData())
            self.__total_commands_handled += 1
            return

        if command == SER_PROTO_TRANSFORMER_POWER_QUERY:
            if SER_PROTO_DIAGS > 0:
                logger.info("Received TRANSFORMER POWER QUERY command")

            self.__SendPacket(
                SER_PROTO_TRANSFORMER_POWER_RESPONSE,
                DemoDataManager.GetTransformerPowerData(),
            )
            self.__total_commands_handled += 1
            return

        if command == SER_PROTO_SYSTEM_POWER_QUERY:
            if SER_PROTO_DIAGS > 0:
                logger.info("Received SYSTEM POWER QUERY command")

            self.__SendPacket(SER_PROTO_SYSTEM_POWER_RESPONSE, DemoDataManager.GetSystemPowerData())
            self.__total_commands_handled += 1
            return

        if command == SER_PROTO_ENGINE_POWER_SET:
            if data is None:
                logger.error("Received SET ENGINE POWER command with no data")
                return

            if SER_PROTO_DIAGS > 0:
                logger.info(f"Received SET ENGINE POWER command: {shortString(data)}")

            try:
                DemoDataManager.ClearEnginePowerData()
                for power_dict in data:
                    power_resource = EnginePower.from_json_dict(power_dict)
                    logger.info(f"Adding ENGINE POWER: {power_resource}")
                    DemoDataManager.AddEnginePowerResource(power_resource)

                self.__SendPacket(SER_PROTO_OK)
            except TypeError as ex:
                logger.error(
                    f"Received invalid SET ENGINE POWER data: {str(ex)} data packet: {shortString(json_string(data))}"
                )
                self.__SendPacket(SER_PROTO_ERR, str(ex))

            self.__total_commands_handled += 1
            return

        if command == SER_PROTO_TRANSFORMER_POWER_SET:
            if data is None:
                logger.error("Received SET TRANSFORMER POWER command with no data")
                return

            if SER_PROTO_DIAGS > 0:
                logger.info(f"Received SET TRANSFORMER POWER command: {shortString(data)}")

            try:
                DemoDataManager.ClearTransformerPowerData()
                for power_dict in data:
                    power_resource = TransformerPower.from_json_dict(power_dict)
                    logger.info(f"Adding TRANSFORMER POWER: {power_resource}")
                    DemoDataManager.AddTransformerPowerResource(power_resource)

                self.__SendPacket(SER_PROTO_OK)
            except TypeError as ex:
                logger.error(
                    f"Received invalid SET TRANSFORMER POWER data: {str(ex)} data packet: {shortString(json_string(data))}"
                )
                self.__SendPacket(SER_PROTO_ERR, str(ex))

            self.__total_commands_handled += 1
            return

        if command == SER_PROTO_SYSTEM_POWER_SET:
            if data is None:
                logger.error("Received SET SYSTEM POWER command with no data")
                return

            if SER_PROTO_DIAGS > 0:
                logger.info(f"Received SET SYSTEM POWER command: {shortString(data)}")

            try:
                DemoDataManager.ClearSystemPowerData()
                for power_dict in data:
                    power_resource = SystemPower.from_json_dict(power_dict)
                    logger.info(f"Adding SYSTEM POWER: {power_resource}")
                    DemoDataManager.AddSystemPowerResource(power_resource)

                self.__SendPacket(SER_PROTO_OK)
            except TypeError as ex:
                logger.error(
                    f"Received invalid SET SYSTEM POWER data: {str(ex)} data packet: {shortString(json_string(data))}"
                )
                self.__SendPacket(SER_PROTO_ERR, str(ex))

            self.__total_commands_handled += 1
            return

    def __CheckCommand(self):
        if len(self.__pendingCommand) < 1:
            return

        commandFinished = self.__pendingCommand[-1] == BYTE_LF

        if self.__pendingCommand[-1] == BYTE_CR and time.ticks_diff(time.ticks_ms(), self.__lastReadTime) > int(
            PENDING_CRLF_DELAY_SEC * 1000
        ):
            commandFinished = True

        if commandFinished:
            self.__total_bytes_read += len(self.__pendingCommand)

            command = self.__pendingCommand.decode("utf-8").replace("\r", "").replace("\n", "")
            self.__pendingCommand = bytearray(0)

            if len(command) < 1:
                logger.error("Empty command received")
                return

            if SER_PROTO_DIAGS > 1:
                logger.info(f"Handling command: {command}")

            commandParts = command.split(SER_PROTO_RESPONSE_DELIMITER, 1)

            try:
                data = None if len(commandParts) < 2 else json.loads(commandParts[1])
            except:
                logger.error(f"Invalid JSON data for command '{commandParts[0]}': {commandParts[1]}")
                return

            self.__HandleCommand(commandParts[0], data)


ProtocolManager = ProtocolManagerClass()
