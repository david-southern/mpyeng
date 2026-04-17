# This is the main entry point for the USB Client. It is responsible for
# managing the various components of the client, including the USB serial
# connection to receive commands from the server

from profiling import log_free_ram
log_free_ram("power-on")

from power_card_tray import RightPixelStrip, TestPowerCardTrays
import usb_cdc  # pyright: ignore[reportMissingImports]

from eng_utils import check_timer, register_timer, logger
from profiling import register_profile, start_profile, stop_profile, report_all_profiles
from demo_data_manager import DemoDataManager

from power_grid_manager import LeftPixelStrip, PowerGridManager
from power_display_manager import PowerDisplayManager

from card_manager import CardReaderManager
from protocol_manager import ProtocolManager
from switchboard_manager import SwitchboardManager

ENABLE_HEARTBEAT_LOGGING = False

logger.info("Initializing USB Client")

# Only check the serial line this often so we don't use up all the client's cycles
SERIAL_READ_FREQUENCY_SEC = 0.01
TIMER_SERIAL_READ = "serial_read"
HEARTBEAT_FREQUENCY_SEC = 2
TIMER_HEARTBEAT = "heartbeat"
PROFILE_REPORT_FREQUENCY_SEC = 10.0
TIMER_PROFILE_REPORT = "profile_report"
DEMO_DATA_FREQUENCY_SEC = 0.25
TIMER_DEMO_DATA = "demo_data"

PROFILE_COMMS         = register_profile("comms")
PROFILE_DEMO_DATA     = register_profile("demo_data")
PROFILE_TRAYS         = register_profile("trays")
PROFILE_LEFT_PIXELS   = register_profile("left_pixels")
PROFILE_RIGHT_PIXELS  = register_profile("right_pixels")
PROFILE_HEARTBEAT     = register_profile("heartbeat")

if usb_cdc.data is None:
    raise ConnectionError("Unable to open USB_cdc.data Serial connection")

showSerialDiags = False
showSerialStats = False

showCardReaderDiags = False
showSwitchboardDiags = False
showDemoData = False

register_timer(TIMER_HEARTBEAT, HEARTBEAT_FREQUENCY_SEC)
register_timer(TIMER_PROFILE_REPORT, PROFILE_REPORT_FREQUENCY_SEC)
register_timer(TIMER_SERIAL_READ, SERIAL_READ_FREQUENCY_SEC)
register_timer(TIMER_DEMO_DATA, DEMO_DATA_FREQUENCY_SEC)

def log_heartbeat():
    if not ENABLE_HEARTBEAT_LOGGING:
        return
    
    logString = "** Heartbeat"

    if showSerialDiags:
        connState = (
            "Connected" if ProtocolManager.IsConnected else "UNCONNECTED"
        )
        logString += f": SerProto: {connState}"

    if showSerialStats:
        logString += (
            f", bytes read/sent: {ProtocolManager.TotalBytesRead}/{ProtocolManager.TotalBytesSent}, "
            + f"commands handled: {ProtocolManager.TotalCommandsHandled}"
        )

    if showSwitchboardDiags:
        logString += f": Switchboard: {SwitchboardManager.ConnectionStatus()}"

    if showDemoData:
        powerDiag = [
            f"{power.Name}: {power.Power}"
            for power in DemoDataManager.GetSystemPowerData()
        ]
        logString += f", DemoData: {powerDiag}"

    if showCardReaderDiags:
        cardLog = ", ".join(CardReaderManager.ReaderCards())
        logString += f", ReaderState: {cardLog}"

    logger.info(logString)


def initialize():
    log_free_ram("startup")

    for powerGrid in PowerGridManager.AllGrids():
        powerGrid.MaxLevel = 1000

    for powerDisplay in PowerDisplayManager.AllDisplays():
        powerDisplay.Value = 888

def mainLoop():
    initialize()

    while True:
        if check_timer(TIMER_SERIAL_READ):
            start_profile(PROFILE_COMMS)
            ProtocolManager.HandleComms()
            stop_profile(PROFILE_COMMS)

        if check_timer(TIMER_DEMO_DATA):
            start_profile(PROFILE_DEMO_DATA)
            DemoDataManager.update_demo_data()
            PowerGridManager.UpdateGridState()
            stop_profile(PROFILE_DEMO_DATA)

        start_profile(PROFILE_TRAYS)
        for tray in TestPowerCardTrays:
            tray.Update()
        stop_profile(PROFILE_TRAYS)

        start_profile(PROFILE_LEFT_PIXELS)
        LeftPixelStrip.Update()
        stop_profile(PROFILE_LEFT_PIXELS)

        start_profile(PROFILE_RIGHT_PIXELS)
        RightPixelStrip.Update()
        stop_profile(PROFILE_RIGHT_PIXELS)

        if check_timer(TIMER_HEARTBEAT):
            start_profile(PROFILE_HEARTBEAT)
            log_heartbeat()
            stop_profile(PROFILE_HEARTBEAT)

        if check_timer(TIMER_PROFILE_REPORT):
            report_all_profiles()

mainLoop()
