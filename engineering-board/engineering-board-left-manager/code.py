# This is the main entry point for the USB Client. It is responsible for
# managing the various components of the client, including the USB serial
# connection, the card reader, the switchboard, and the power grid. It also
# handles the heartbeat and logging for the client.

import supervisor
import time
from power_card_tray import RightPixelStrip, TestPowerCardTrays
import usb_cdc  # pyright: ignore[reportMissingImports]

from eng_utils import logger
from fake_data_manager import FakeDataManager

from power_grid_manager import LeftPixelStrip, PowerGridManager
from power_display_manager import PowerDisplayManager

from card_manager import CardReaderManager
from protocol_manager import ProtocolManager
from switchboard_manager import SwitchboardManager

logger.info("Initializing USB Client")

# Only check the serial line this often so we don't use up all the client's cycles
SERIAL_READ_FREQUENCY_SEC = 0.01
HEARTBEAT_FREQUENCY_SEC = 2

if usb_cdc.data is None:
    raise ConnectionError("Unable to open USB_cdc.data Serial connection")

nextHeartbeat = time.monotonic() + HEARTBEAT_FREQUENCY_SEC

showSerialDiags = False
showSerialStats = False

showCardReaderDiags = False
showSwitchboardDiags = False
showFakeData = True

prevSwitchboard = ""

GRID_CHANGE_FREQ = 0.2
nextGridChange = time.monotonic() + GRID_CHANGE_FREQ

for powerGrid in PowerGridManager.AllGrids():
    powerGrid.MaxLevel = 1000

for powerDisplay in PowerDisplayManager.AllDisplays():
    powerDisplay.Value = 888

def profile_time(time_sec: float) -> str:
        return f"{time_sec:.2f}"

def mainLoop():
    global nextGridChange
    global nextHeartbeat

    last_profile_time = time.monotonic()
    profile_report_freq = 5.0
    profile_samples = 0
    fake_data_time = 0
    comms_time = 0
    grid_time = 0
    trays_time = 0
    left_pixels_time = 0
    right_pixels_time = 0
    heartbeat_time = 0
    sleep_time = 0
    
    while True:
        start_time = supervisor.ticks_ms()
        time.sleep(SERIAL_READ_FREQUENCY_SEC)
        sleep_time += supervisor.ticks_ms() - start_time

        start_time = supervisor.ticks_ms()
        FakeDataManager.update_fake_data()
        fake_data_time += supervisor.ticks_ms() - start_time

        start_time = supervisor.ticks_ms()
        ProtocolManager.HandleComms()
        comms_time += supervisor.ticks_ms() - start_time

        start_time = supervisor.ticks_ms()
        PowerGridManager.UpdateGridState()
        grid_time += supervisor.ticks_ms() - start_time

        start_time = supervisor.ticks_ms()
        for tray in TestPowerCardTrays:
            tray.Update()
            break
        trays_time += supervisor.ticks_ms() - start_time

        start_time = supervisor.ticks_ms()
        LeftPixelStrip.Update()
        left_pixels_time += supervisor.ticks_ms() - start_time

        start_time = supervisor.ticks_ms()
        RightPixelStrip.Update()
        right_pixels_time += supervisor.ticks_ms() - start_time

        start_time = supervisor.ticks_ms()
        if time.monotonic() > nextGridChange:
            nextGridChange = time.monotonic() + GRID_CHANGE_FREQ

        if time.monotonic() > nextHeartbeat:
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

            # logger.info(logString)

            nextHeartbeat = time.monotonic() + HEARTBEAT_FREQUENCY_SEC
        heartbeat_time += supervisor.ticks_ms() - start_time

        profile_samples += 1
        report_factor = 1
                
        if time.monotonic() - last_profile_time > profile_report_freq:
            logger.info(f"Performance profile ({profile_samples} samples over last {profile_time(time.monotonic() - last_profile_time)} seconds) - SLP: {profile_time(sleep_time / report_factor)}, FD: {profile_time(fake_data_time / report_factor)}, C: {profile_time(comms_time / report_factor)}, G: {profile_time(grid_time / report_factor)}, T: {profile_time(trays_time / report_factor)}, LP: {profile_time(left_pixels_time / report_factor)}, RP: {profile_time(right_pixels_time / report_factor)}, HB: {profile_time(heartbeat_time / report_factor)}")
            last_profile_time = time.monotonic()
            profile_samples = 0
            fake_data_time = 0
            comms_time = 0
            grid_time = 0
            trays_time = 0
            left_pixels_time = 0
            right_pixels_time = 0
            heartbeat_time = 0
            sleep_time = 0


mainLoop()
