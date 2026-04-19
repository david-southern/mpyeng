from power_cards.animation import ANIMATION_TARGET_FPS
from utils.profiling import log_free_ram

from utils.eng_utils import (
    ENABLE_CARD_READER,
    ENABLE_POWER_DISPLAY,
    ENABLE_POWER_GRID,
    ENABLE_POWER_TRAY,
    ENABLE_PROTOCOL_MANAGER,
    ENABLE_SWITCHBOARD,
    check_timer,
    register_timer,
    logger,
)
from utils.device_manager import device_manager
from utils.profiling import register_profile, start_profile, stop_profile, report_all_profiles
from utils.demo_data_manager import DemoDataManager

if ENABLE_POWER_TRAY:
    from card_tray.tray_manager import PowerTrayManager

if ENABLE_POWER_GRID:
    from power_grid.grid_manager import PowerGridManager

if ENABLE_POWER_DISPLAY:
    from power_display.display_manager import PowerDisplayManager

if ENABLE_CARD_READER:
    from card_reader.reader_manager import CardReaderManager

if ENABLE_SWITCHBOARD:
    from switchboard.switchboard_manager import SwitchboardManager

if ENABLE_PROTOCOL_MANAGER:
    from comms.protocol_manager import ProtocolManager

ENABLE_HEARTBEAT_LOGGING = False

PROTOCOL_FREQUENCY_SEC = 0.01
TIMER_PROTOCOL = "protocol"

HEARTBEAT_FREQUENCY_SEC = 2
TIMER_HEARTBEAT = "heartbeat"

PROFILE_REPORT_FREQUENCY_SEC = 10.0
TIMER_PROFILE_REPORT = "profile_report"

DEMO_DATA_FREQUENCY_SEC = 0.25
TIMER_DEMO_DATA = "demo_data"

ANIMATION_UPDATE_FREQUENCY_SEC = 1.0 / ANIMATION_TARGET_FPS
TIMER_POWER_TRAY_UPDATE = "tray_update"

PROFILE_PROTOCOL = register_profile("protocol")
PROFILE_DEMO_DATA = register_profile("demo_data")
PROFILE_HEARTBEAT = register_profile("heartbeat")

showProtocolDiags = False
showProtocolStats = False

showCardReaderDiags = False
showSwitchboardDiags = False
showDemoData = False

TIMER_UNKNOWN_DEVICE_LOG = "unknown_device_log"
UNKNOWN_DEVICE_LOG_FREQUENCY_SEC = 1.0

register_timer(TIMER_HEARTBEAT, HEARTBEAT_FREQUENCY_SEC)
register_timer(TIMER_PROFILE_REPORT, PROFILE_REPORT_FREQUENCY_SEC)
register_timer(TIMER_PROTOCOL, PROTOCOL_FREQUENCY_SEC)
register_timer(TIMER_DEMO_DATA, DEMO_DATA_FREQUENCY_SEC)
register_timer(TIMER_POWER_TRAY_UPDATE, ANIMATION_UPDATE_FREQUENCY_SEC)
register_timer(TIMER_UNKNOWN_DEVICE_LOG, UNKNOWN_DEVICE_LOG_FREQUENCY_SEC)


def log_heartbeat():
    if not ENABLE_HEARTBEAT_LOGGING:
        return

    logString = "** Heartbeat"

    if ENABLE_PROTOCOL_MANAGER and showProtocolDiags:
        connState = "Connected" if ProtocolManager.IsConnected else "UNCONNECTED"
        logString += f": Proto: {connState}"

    if ENABLE_PROTOCOL_MANAGER and showProtocolStats:
        logString += (
            f", bytes read/sent: {ProtocolManager.TotalBytesRead}/{ProtocolManager.TotalBytesSent}, "
            + f"commands handled: {ProtocolManager.TotalCommandsHandled}"
        )

    if showSwitchboardDiags and ENABLE_SWITCHBOARD:
        logString += f": Switchboard: {SwitchboardManager.ConnectionStatus()}"

    if showDemoData:
        powerDiag = [f"{power.Name}: {power.Power}" for power in DemoDataManager.GetSystemPowerData()]
        logString += f", DemoData: {powerDiag}"

    if showCardReaderDiags and ENABLE_CARD_READER:
        cardLog = ", ".join(CardReaderManager.ReaderCards())
        logString += f", ReaderState: {cardLog}"

    logger.info(logString)


def initialize():
    log_free_ram("startup")

    if ENABLE_POWER_GRID:
        for powerGrid in PowerGridManager.AllGrids():
            powerGrid.MaxLevel = 1000

    if ENABLE_POWER_DISPLAY:
        for powerDisplay in PowerDisplayManager.AllDisplays():
            powerDisplay.Value = 888


def mainLoop():
    if not device_manager.device_recognized:
        while True:
            if check_timer(TIMER_UNKNOWN_DEVICE_LOG):
                logger.error(
                    f"Device ID '{device_manager.device_id}' does not have a module definition. No modules enabled."
                )

    initialize()

    while True:
        if ENABLE_PROTOCOL_MANAGER and check_timer(TIMER_PROTOCOL):
            start_profile(PROFILE_PROTOCOL)
            ProtocolManager.HandleComms()
            stop_profile(PROFILE_PROTOCOL)

        if check_timer(TIMER_DEMO_DATA):
            start_profile(PROFILE_DEMO_DATA)
            DemoDataManager.update_demo_data()
            if ENABLE_POWER_GRID:
                PowerGridManager.Update()
            stop_profile(PROFILE_DEMO_DATA)

        if ENABLE_POWER_TRAY and check_timer(TIMER_POWER_TRAY_UPDATE):
            # PowerTray profiling is done internal to the class
            PowerTrayManager.Update()

        if check_timer(TIMER_HEARTBEAT):
            start_profile(PROFILE_HEARTBEAT)
            log_heartbeat()
            stop_profile(PROFILE_HEARTBEAT)

        if check_timer(TIMER_PROFILE_REPORT):
            report_all_profiles()


mainLoop()
