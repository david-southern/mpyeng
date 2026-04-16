# This is the main entry point for the USB Client. It is responsible for
# managing the various components of the client, including the USB serial
# connection to receive commands from the server

from power_card_tray import RightPixelStrip, TestPowerCardTrays
import usb_cdc  # pyright: ignore[reportMissingImports]

from eng_utils import check_timer, register_timer, logger
from profiling import register_profile, start_profile, stop_profile, report_all_profiles, log_free_ram
from fake_data_manager import FakeDataManager

from power_grid_manager import LeftPixelStrip, PowerGridManager
from power_display_manager import PowerDisplayManager

from card_manager import CardReaderManager
from protocol_manager import ProtocolManager
from switchboard_manager import SwitchboardManager

ENABLE_HEARTBEAT_LOGGING = False

logger.info("Initializing USB Client")

log_free_ram("power-on")

# Only check the serial line this often so we don't use up all the client's cycles
SERIAL_READ_FREQUENCY_SEC = 0.01
TIMER_SERIAL_READ = "serial_read"
HEARTBEAT_FREQUENCY_SEC = 2
TIMER_HEARTBEAT = "heartbeat"
PROFILE_REPORT_FREQUENCY_SEC = 10.0
TIMER_PROFILE_REPORT = "profile_report"

PROFILE_COMMS = "comms"
PROFILE_FAKE_DATA = "fake_data"
PROFILE_GRID = "grid"
PROFILE_TRAYS = "trays"
PROFILE_LEFT_PIXELS = "left_pixels"
PROFILE_RIGHT_PIXELS = "right_pixels"
PROFILE_HEARTBEAT = "heartbeat"

if usb_cdc.data is None:
    raise ConnectionError("Unable to open USB_cdc.data Serial connection")

showSerialDiags = False
showSerialStats = False

showCardReaderDiags = False
showSwitchboardDiags = False
showFakeData = True

register_timer(TIMER_HEARTBEAT, HEARTBEAT_FREQUENCY_SEC)
register_timer(TIMER_PROFILE_REPORT, PROFILE_REPORT_FREQUENCY_SEC)
register_timer(TIMER_SERIAL_READ, SERIAL_READ_FREQUENCY_SEC)

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

    if showFakeData:
        powerDiag = [
            f"{power.Name}: {power.Power}"
            for power in FakeDataManager.GetSystemPowerData()
        ]
        logString += f", FakeData: {powerDiag}"

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

    register_profile(PROFILE_COMMS)
    register_profile(PROFILE_FAKE_DATA)
    register_profile(PROFILE_GRID)
    register_profile(PROFILE_TRAYS)
    register_profile(PROFILE_LEFT_PIXELS)
    register_profile(PROFILE_RIGHT_PIXELS)
    register_profile(PROFILE_HEARTBEAT)

def mainLoop():
    initialize()

    while True:
        start_profile(PROFILE_COMMS)
        if check_timer(TIMER_SERIAL_READ):
            ProtocolManager.HandleComms()
        stop_profile(PROFILE_COMMS)

        start_profile(PROFILE_FAKE_DATA)
        FakeDataManager.update_fake_data()
        stop_profile(PROFILE_FAKE_DATA)

        start_profile(PROFILE_GRID)
        PowerGridManager.UpdateGridState()
        stop_profile(PROFILE_GRID)

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

        start_profile(PROFILE_HEARTBEAT)
        if check_timer(TIMER_HEARTBEAT):
            log_heartbeat()
        stop_profile(PROFILE_HEARTBEAT)

        if check_timer(TIMER_PROFILE_REPORT):
            report_all_profiles()


mainLoop()
