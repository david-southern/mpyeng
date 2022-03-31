import time
import adafruit_logging as logging
import usb_cdc
from utils import format_hex, format_hex_list
import json

# If we receive a CR, then wait this long to see if an LF is going to show up, so we don't have stray LF's when reading
# from a CRLF controller
PENDING_CRLF_DELAY_SEC = 0.1
BYTE_CR = 0x0D
BYTE_LF = 0x0A

SER_PROTO_DIAGS = 1

SER_PROTO_RESPONSE_DELIMITER = ":"

SER_PROTO_INIT_HEADER = "SP_INIT"
SER_PROTO_INIT_RESPONSE = "SP_READY"
SER_PROTO_CARDS_QUERY = "SP_C_Q"
SER_PROTO_CARDS_RESPONSE = "SP_C_R"

# Only check the serial line this often so we don't use up all the client's cycles
SERIAL_READ_FREQUENCY_SEC = 0.01
HEARTBEAT_FREQUENCY_SEC = 5

logger = logging.getLogger('main')
logger.setLevel(logging.INFO)

if usb_cdc.data is None:
    raise ConnectionError("Unable to open USB_cdc.data Serial connection")

data_serial = usb_cdc.data
data_serial.timeout = 0

logger.info("Initializing SerClient")

next_heartbeat = time.monotonic() + HEARTBEAT_FREQUENCY_SEC
total_bytes_read = 0
total_commands_handled = 0

pending_command = bytearray(0)
last_read = 0

def send_packet(protocolCommand, data=None):
    packet = protocolCommand
    if(data is not None):
        jsonData = json.dumps(data)
        packet += f"{SER_PROTO_RESPONSE_DELIMITER}{jsonData}"
    packet += "\n"

    if(SER_PROTO_DIAGS > 0):
        logger.info(f"Sending response packet: {packet}")

    data_serial.write(packet.encode("utf-8"))
    data_serial.flush()


def handle_command(command):
    global total_commands_handled

    if(command == SER_PROTO_INIT_HEADER):
        if(SER_PROTO_DIAGS > 0):
            logger.info(f"Received INIT command")

        # Clear the buffers in case there are any unsent/received bytes waiting (possibly from another failed communcation)
        data_serial.reset_input_buffer()
        data_serial.reset_output_buffer()

        send_packet(SER_PROTO_INIT_RESPONSE)
        total_commands_handled += 1
        return

    if(command == SER_PROTO_CARDS_QUERY):
        if(SER_PROTO_DIAGS > 0):
            logger.info(f"Received CARD QUERY command")

        send_packet(SER_PROTO_CARDS_RESPONSE, [8, 6, 7, 5, 3, 0, 9])
        total_commands_handled += 1
        return

    logger.error(f"Unknown protocol command: {command}")

def check_command():
    global pending_command, total_bytes_read

    if(len(pending_command) < 1):
        return

    if(pending_command[-1] == BYTE_LF or (pending_command[-1] == BYTE_CR and time.monotonic() - last_read > PENDING_CRLF_DELAY_SEC)):
        total_bytes_read += len(pending_command)

        command = pending_command.decode("utf-8").replace("\r", "").replace("\n", "")
        if(SER_PROTO_DIAGS > 1):
            logger.info(f"Handling command: {command}")
        handle_command(command)
        pending_command = bytearray(0)


while True:
    if data_serial.connected and data_serial.in_waiting > 0:
        chunk_bytes = data_serial.readline()
        if(SER_PROTO_DIAGS > 4):
            logger.info(f"Read serial chunk: {format_hex_list(chunk_bytes)}")
        pending_command += chunk_bytes
        if(SER_PROTO_DIAGS > 3):
            logger.info(f"Pending command: {format_hex_list(pending_command)}")
        last_read = time.monotonic()

    check_command()

    if(time.monotonic() > next_heartbeat):
        connState = "Connected" if data_serial.connected else "UNCONNECTED"
        logger.info(f"Heartbeat: SerProto: {connState}, bytes read: {total_bytes_read}, commands handled: {total_commands_handled}")
        next_heartbeat = time.monotonic() + HEARTBEAT_FREQUENCY_SEC

    time.sleep(SERIAL_READ_FREQUENCY_SEC)
