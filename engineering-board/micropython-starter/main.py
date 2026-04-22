from utils.profiling import log_free_ram

from utils.eng_utils import (
    check_timer,
    register_timer,
    logger,
)
from utils.device_manager import DeviceManager
from utils.profiling import register_profile, start_profile, stop_profile, report_all_profiles

ENABLE_HEARTBEAT_LOGGING = False

HEARTBEAT_FREQUENCY_SEC = 2
TIMER_HEARTBEAT = "heartbeat"

PROFILE_REPORT_FREQUENCY_SEC = 5.0
TIMER_PROFILE_REPORT = "profile_report"

TIMER_UNKNOWN_DEVICE_LOG = "unknown_device_log"
UNKNOWN_DEVICE_LOG_FREQUENCY_SEC = 1.0

register_timer(TIMER_HEARTBEAT, HEARTBEAT_FREQUENCY_SEC)
register_timer(TIMER_PROFILE_REPORT, PROFILE_REPORT_FREQUENCY_SEC)
register_timer(TIMER_UNKNOWN_DEVICE_LOG, UNKNOWN_DEVICE_LOG_FREQUENCY_SEC)

PROFILE_HEARTBEAT = register_profile(TIMER_HEARTBEAT)


def log_heartbeat():
    if not ENABLE_HEARTBEAT_LOGGING:
        return

    logString = "** Heartbeat"

    logger.info(logString)


def initialize():
    log_free_ram("startup")


def mainLoop():
    if not DeviceManager.DEVICE_RECOGNIZED:
        while True:
            if check_timer(TIMER_UNKNOWN_DEVICE_LOG):
                logger.error(
                    f"Device ID '{DeviceManager.DEVICE_ID}' does not have a module definition. No modules enabled."
                )

    initialize()

    while True:
        if check_timer(TIMER_HEARTBEAT):
            start_profile(PROFILE_HEARTBEAT)
            log_heartbeat()
            stop_profile(PROFILE_HEARTBEAT)

        if check_timer(TIMER_PROFILE_REPORT):
            report_all_profiles()


mainLoop()
