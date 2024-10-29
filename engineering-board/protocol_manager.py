import time
from card_manager import CardReaderManager
from pixel_manager import PixelManager
from power_display_manager import PowerDisplayManager
from power_grid_manager import PowerGridManager
from protocol_resources import FAKE_ENGINE_POWER_DATA, FAKE_SYSTEM_POWER_DATA, FAKE_TRANSFORMER_POWER_DATA, EnginePower, SystemPower, TransformerPower, json_string
from switchboard_manager import SwitchboardManager
import usb_cdc
from eng_utils import format_hex_list, shortString, logger
import json

# If we receive a CR, then wait this long to see if an LF is going to show up, so we don't have stray LF's when reading
# from a CRLF controller
PENDING_CRLF_DELAY_SEC = 0.1
BYTE_CR = 0x0D
BYTE_LF = 0x0A

SER_PROTO_DIAGS = 2
SER_PROTO_RESPONSE_DELIMITER = "|"

SER_PROTO_INIT_HEADER = "SP_INIT"
SER_PROTO_INIT_RESPONSE = "SP_READY"
SER_PROTO_OK = "SP_OK"
SER_PROTO_ERR = "SP_ERR"

SER_PROTO_QUERY = "_QUERY"
SER_PROTO_RESPONSE = "_RESPONSE"
SER_PROTO_SET = "_SET"

SER_PROTO_ENGINE_POWER = "SP_ENG_POWER"
SER_PROTO_ENGINE_POWER_QUERY = SER_PROTO_ENGINE_POWER + SER_PROTO_QUERY
SER_PROTO_ENGINE_POWER_RESPONSE = SER_PROTO_ENGINE_POWER + SER_PROTO_RESPONSE
SER_PROTO_ENGINE_POWER_SET = SER_PROTO_ENGINE_POWER + SER_PROTO_SET

SER_PROTO_TRANSFORMER_POWER = "SP_TRANS_POWER"
SER_PROTO_TRANSFORMER_POWER_QUERY = SER_PROTO_TRANSFORMER_POWER + SER_PROTO_QUERY
SER_PROTO_TRANSFORMER_POWER_RESPONSE = SER_PROTO_TRANSFORMER_POWER + SER_PROTO_RESPONSE
SER_PROTO_TRANSFORMER_POWER_SET = SER_PROTO_TRANSFORMER_POWER + SER_PROTO_SET

SER_PROTO_SYSTEM_POWER = "SP_SYS_POWER"
SER_PROTO_SYSTEM_POWER_QUERY = SER_PROTO_SYSTEM_POWER + SER_PROTO_QUERY
SER_PROTO_SYSTEM_POWER_RESPONSE = SER_PROTO_SYSTEM_POWER + SER_PROTO_RESPONSE
SER_PROTO_SYSTEM_POWER_SET = SER_PROTO_SYSTEM_POWER + SER_PROTO_SET

class ProtocolManagerClass:
    def __init__(self):
        if usb_cdc.data is None:
            raise ConnectionError("Unable to open USB_cdc.data Serial connection")

        self.__dataSerial = usb_cdc.data
        self.__dataSerial.timeout = 0
        self.__pendingCommand = bytearray(0)
        self.__lastReadTime = 0
        self.__total_commands_handled = 0
        self.__total_bytes_sent = 0
        self.__total_bytes_read = 0

        logger.info("Initializing ProtocolManager")

    @property
    def IsConnected(self):
        return self.__dataSerial.connected

    @property
    def TotalBytesRead(self):
        return self.__total_bytes_read

    @property
    def TotalBytesSent(self):
        return self.__total_bytes_sent

    @property
    def TotalCommandsHandled(self):
        return self.__total_commands_handled

    def HandleComms(self):
        if self.__dataSerial.connected and self.__dataSerial.in_waiting > 0:
            chunkBytes = self.__dataSerial.readline()
            if SER_PROTO_DIAGS > 4:
                logger.info(f"Read serial chunk: {format_hex_list(chunkBytes)}")
            self.__pendingCommand += chunkBytes
            if SER_PROTO_DIAGS > 3:
                logger.info(f"Pending command: {format_hex_list(self.__pendingCommand)}")
            self.__lastReadTime = time.monotonic()
        self.__CheckCommand()

    def __SendPacket(self, command, data=None):
        packet = command
        if data is not None:
            jsonData = json_string(data)
            packet += f"{SER_PROTO_RESPONSE_DELIMITER}{jsonData}"
        packet += "\n"

        if SER_PROTO_DIAGS > 0:
            logger.info(f"Sending response packet: {packet}")

        self.__dataSerial.write(packet.encode("utf-8"))
        self.__dataSerial.flush()

    def __HandleCommand(self, command, data=None):
        if command == SER_PROTO_INIT_HEADER:
            if SER_PROTO_DIAGS > 0:
                logger.info(f"Received INIT command")

            # Clear the buffers in case there are any unsent/received bytes waiting (possibly from another failed communication)
            self.__dataSerial.reset_input_buffer()
            self.__dataSerial.reset_output_buffer()

            self.__SendPacket(SER_PROTO_INIT_RESPONSE)
            self.__total_commands_handled += 1
            return

        if command == SER_PROTO_ENGINE_POWER_QUERY:
            if SER_PROTO_DIAGS > 0:
                logger.info(f"Received ENGINE POWER QUERY command")

            self.__SendPacket(SER_PROTO_ENGINE_POWER_RESPONSE, FAKE_ENGINE_POWER_DATA)
            self.__total_commands_handled += 1
            return

        if command == SER_PROTO_TRANSFORMER_POWER_QUERY:
            if SER_PROTO_DIAGS > 0:
                logger.info(f"Received TRANSFORMER POWER QUERY command")

            self.__SendPacket(SER_PROTO_TRANSFORMER_POWER_RESPONSE, FAKE_TRANSFORMER_POWER_DATA)
            self.__total_commands_handled += 1
            return

        if command == SER_PROTO_SYSTEM_POWER_QUERY:
            if SER_PROTO_DIAGS > 0:
                logger.info(f"Received SYSTEM POWER QUERY command")

            self.__SendPacket(SER_PROTO_SYSTEM_POWER_RESPONSE, FAKE_SYSTEM_POWER_DATA)
            self.__total_commands_handled += 1
            return

        if command == SER_PROTO_ENGINE_POWER_SET:
            if data is None:
                logger.error(f"Received SET ENGINE POWER command with no data")
                return

            if SER_PROTO_DIAGS > 0:
                logger.info(f"Received SET ENGINE POWER command: {shortString(data)}")

            try:
                FAKE_ENGINE_POWER_DATA.clear()
                for powerDict in data:
                    powerResource = EnginePower.from_json_dict(powerDict)
                    logger.info(f"Adding ENGINE POWER: {powerResource}")
                    FAKE_ENGINE_POWER_DATA.append(powerResource)
                    
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
                logger.error(f"Received SET TRANSFORMER POWER command with no data")
                return

            if SER_PROTO_DIAGS > 0:
                logger.info(f"Received SET TRANSFORMER POWER command: {shortString(data)}")

            try:
                FAKE_TRANSFORMER_POWER_DATA.clear()
                for powerDict in data:
                    powerResource = TransformerPower.from_json_dict(powerDict)
                    logger.info(f"Adding TRANSFORMER POWER: {powerResource}")
                    FAKE_TRANSFORMER_POWER_DATA.append(powerResource)

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
                logger.error(f"Received SET SYSTEM POWER command with no data")
                return

            if SER_PROTO_DIAGS > 0:
                logger.info(f"Received SET SYSTEM POWER command: {shortString(data)}")

            try:
                FAKE_SYSTEM_POWER_DATA.clear()
                for powerDict in data:
                    powerResource = SystemPower.from_json_dict(powerDict)
                    logger.info(f"Adding SYSTEM POWER: {powerResource}")
                    FAKE_SYSTEM_POWER_DATA.append(powerResource)

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

        if self.__pendingCommand[-1] == BYTE_CR and time.monotonic() - self.__lastReadTime > PENDING_CRLF_DELAY_SEC:
            commandFinished = True

        if commandFinished:
            self.__total_bytes_read += len(self.__pendingCommand)

            command = self.__pendingCommand.decode("utf-8").replace("\r", "").replace("\n", "")
            self.__pendingCommand = bytearray(0)

            if len(command) < 1:
                logger.error(f"Empty command received")
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
