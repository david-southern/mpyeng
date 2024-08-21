# This is the main entry point for the USB Client. It is responsible for
# managing the various components of the client, including the USB serial
# connection, the card reader, the switchboard, and the power grid. It also
# handles the heartbeat and logging for the client.

import random
import time

import usb_cdc # type: ignore

from pixel_manager import BLACK, PixelManager
from power_grid_manager import PowerGridManager
from power_display_manager import PowerDisplayManager

from card_manager import CardReaderManager
from protocol_manager import ProtocolManager
from switchboard_manager import SwitchboardManager
from eng_utils import logger

# Only check the serial line this often so we don't use up all the client's cycles
SERIAL_READ_FREQUENCY_SEC = 0.01
HEARTBEAT_FREQUENCY_SEC = 2

if usb_cdc.data is None:
    raise ConnectionError("Unable to open USB_cdc.data Serial connection")

logger.info("Initializing USB Client")

next_heartbeat = time.monotonic() + HEARTBEAT_FREQUENCY_SEC

showSerialDiags = False
showSerialStats = False

showCardReaderDiags = True
showSwitchboardDiags = True

prevSwitchboard = ""

GRID_CHANGE_FREQ = 0.2
nextGridChange = time.monotonic() + GRID_CHANGE_FREQ

for powerGrid in PowerGridManager.AllGrids():
    powerGrid.MaxLevel = 1000

for powerDisplay in PowerDisplayManager.AllDisplays():
    powerDisplay.Value = 888

def mainLoop():
    global nextGridChange
    global next_heartbeat
    global showSerialDiags
    global showSerialStats
    global showCardReaderDiags
    global showSwitchboardDiags

    ProtocolManager.HandleComms()
    PixelManager.UpdatePixelData()
    PowerGridManager.UpdateGridState()

    if time.monotonic() > nextGridChange:
        nextGridChange = time.monotonic() + GRID_CHANGE_FREQ
        gridIndex = random.randint(0, 5)
        newValue = random.randint(0, 1000)
        PowerGridManager.SetGridCurLevel(gridIndex, newValue)
        readerIndex = gridIndex if gridIndex < 2 else (gridIndex - 2) * 2 + 3
        PowerDisplayManager.SetDisplayValue(readerIndex, newValue)

    if time.monotonic() > next_heartbeat:
        logString = f"Heartbeat"

        if(showSerialDiags):
            connState = "Connected" if ProtocolManager.IsConnected else "UNCONNECTED"
            logString += f": SerProto: {connState}"

        if showSerialStats:
            logString += (
                f", bytes read/sent: {ProtocolManager.TotalBytesRead}/{ProtocolManager.TotalBytesSent}, "
                + f"commands handled: {ProtocolManager.TotalCommandsHandled}"
            )

        if(showSwitchboardDiags):
            logString += f": Switchboard: {SwitchboardManager.ConnectionStatus()}"

        if(showCardReaderDiags):
            cardLog = ", ".join(CardReaderManager.ReaderCards())
            logString += f", ReaderState: {cardLog}"

        logger.info(logString)

        next_heartbeat = time.monotonic() + HEARTBEAT_FREQUENCY_SEC

TEST_LOOP_REPORT_FREQUENCY = 0.25
testChannelIndex = 0

def testLoop():
    global nextGridChange
    global testChannelIndex

    if time.monotonic() > nextGridChange:
        nextGridChange = time.monotonic() + TEST_LOOP_REPORT_FREQUENCY


while True:
    mainLoop()
    time.sleep(SERIAL_READ_FREQUENCY_SEC)
 