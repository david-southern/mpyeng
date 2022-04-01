import time
import adafruit_logging as logging
from protocol_manager import ProtocolManager
import usb_cdc
from utils import format_hex, format_hex_list
import json

# Only check the serial line this often so we don't use up all the client's cycles
SERIAL_READ_FREQUENCY_SEC = 0.01
HEARTBEAT_FREQUENCY_SEC = 5

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

if usb_cdc.data is None:
    raise ConnectionError("Unable to open USB_cdc.data Serial connection")

logger.info("Initializing SerClient")

next_heartbeat = time.monotonic() + HEARTBEAT_FREQUENCY_SEC

while True:
    ProtocolManager.HandleComms()

    if time.monotonic() > next_heartbeat:
        connState = "Connected" if ProtocolManager.IsConnected else "UNCONNECTED"
        logger.info(
            f"Heartbeat: SerProto: {connState}, bytes read/sent: "
            + f"{ProtocolManager.TotalBytesRead}/{ProtocolManager.TotalBytesSent}, "
            + f"commands handled: {ProtocolManager.TotalCommandsHandled}"
        )
        next_heartbeat = time.monotonic() + HEARTBEAT_FREQUENCY_SEC

    time.sleep(SERIAL_READ_FREQUENCY_SEC)
