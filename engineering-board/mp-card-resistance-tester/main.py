from machine import ADC, Pin, reset

from utils.profiling import log_free_ram

from utils.eng_utils import (
    check_timer,
    register_timer,
    logger,
    reset_timer,
    timer_elapsed_sec,
)
from utils.device_manager import DeviceManager
from utils.profiling import register_profile, start_profile, stop_profile, report_all_profiles

ENABLE_HEARTBEAT_LOGGING = False

HEARTBEAT_FREQUENCY_SEC = 2
TIMER_HEARTBEAT = "heartbeat"

ANALOG_POLL_TIMER = "analog_poll"
ANALOG_POLL_FREQUENCY_SEC = 0.05

VOLTAGE_SMOOTHING_TIMER = "voltage_smoothing"
VOLTAGE_SMOOTHING_FREQUENCY_SEC = 1.0

LAST_EXCEPTION_TIMER = "last_exception"
LAST_EXCEPTION_FREQUENCY_SEC = 99999

PROFILE_REPORT_FREQUENCY_SEC = 5.0
TIMER_PROFILE_REPORT = "profile_report"

TIMER_UNKNOWN_DEVICE_LOG = "unknown_device_log"
UNKNOWN_DEVICE_LOG_FREQUENCY_SEC = 1.0

register_timer(TIMER_HEARTBEAT, HEARTBEAT_FREQUENCY_SEC)
register_timer(TIMER_PROFILE_REPORT, PROFILE_REPORT_FREQUENCY_SEC)
register_timer(TIMER_UNKNOWN_DEVICE_LOG, UNKNOWN_DEVICE_LOG_FREQUENCY_SEC)
register_timer(ANALOG_POLL_TIMER, ANALOG_POLL_FREQUENCY_SEC)
register_timer(VOLTAGE_SMOOTHING_TIMER, VOLTAGE_SMOOTHING_FREQUENCY_SEC)
register_timer(LAST_EXCEPTION_TIMER, LAST_EXCEPTION_FREQUENCY_SEC)

PROFILE_HEARTBEAT = register_profile(TIMER_HEARTBEAT)

V_REF = 3.3  # RP2350 uses the 3.3V supply as the reference voltage for ADC readings


def log_heartbeat():
    if not ENABLE_HEARTBEAT_LOGGING:
        return

    logString = "** Heartbeat"

    logger.info(logString)


def initialize():
    log_free_ram("startup")


def get_voltage(input_pin: ADC):
    """Returns the input_pin voltage on the range [0 - 3.3], based on the reference voltage and the
    16-bit ADC reading."""
    return (input_pin.read_u16() * V_REF) / 65536


def mainLoop():
    if not DeviceManager.DEVICE_RECOGNIZED:
        while True:
            if check_timer(TIMER_UNKNOWN_DEVICE_LOG):
                logger.error(
                    f"Device ID '{DeviceManager.DEVICE_ID}' does not have a module definition. No modules enabled."
                )

    initialize()

    ANALOG_PIN = 26
    test_pin = ADC(Pin(ANALOG_PIN))

    logger.info(f"Monitoring analog input on {ANALOG_PIN}")
    logger.info(f"Reference voltage {V_REF}V")

    max_delta_threshold = 0.02
    delta_exception_reset_threshold = 0.04
    delta_exceptions = 0
    reset_timer(LAST_EXCEPTION_TIMER)

    last_voltage = get_voltage(test_pin)

    # calculate the trailing average of the input value to smooth out noise
    trailing_average_samples = 0
    trailing_voltage = last_voltage
    trailing_deltav = 0
    total_delta_v = 0
    deltav_samples = 0
    max_voltage = 0.0
    min_voltage = 999.0
    max_deltav = 0.0

    while True:
        if check_timer(TIMER_HEARTBEAT):
            start_profile(PROFILE_HEARTBEAT)
            log_heartbeat()
            stop_profile(PROFILE_HEARTBEAT)

        if check_timer(TIMER_PROFILE_REPORT):
            report_all_profiles()

        if check_timer(TIMER_UNKNOWN_DEVICE_LOG):
            input_voltage = get_voltage(test_pin)
            trailing_voltage += input_voltage
            trailing_deltav += abs(input_voltage - last_voltage)
            last_voltage = input_voltage
            trailing_average_samples += 1

        if check_timer(VOLTAGE_SMOOTHING_TIMER):
            smoothed_voltage = trailing_voltage / trailing_average_samples
            smoothed_deltav = trailing_deltav / trailing_average_samples
            trailing_voltage = 0
            trailing_deltav = 0
            trailing_average_samples = 0

            max_voltage = max(max_voltage, smoothed_voltage)
            min_voltage = min(min_voltage, smoothed_voltage)

            max_deltav = max(max_deltav, smoothed_deltav)
            total_delta_v += smoothed_deltav
            deltav_samples += 1
            avg_deltav = total_delta_v / deltav_samples

            logString = f"V: {smoothed_voltage:4.2f}/∧{max_voltage:4.2f}/∨{min_voltage:<4.2f} "
            logString += f" - ΔV: {smoothed_deltav:6.4f} / μΔV {avg_deltav:<6.4f} / ∧ΔV {max_deltav:6.4f} "
            logString += f" - Excp {delta_exceptions} - reset: {timer_elapsed_sec(LAST_EXCEPTION_TIMER):.2f}s ago"

            if smoothed_deltav > max_delta_threshold:
                logString += " ***************"
                delta_exceptions += 1

                if smoothed_deltav >= delta_exception_reset_threshold:
                    max_voltage = 0.0
                    min_voltage = 999.0
                    max_deltav = 0.0
                    total_delta_v = 0.0
                    deltav_samples = 0
                    delta_exceptions = 0
                    reset_timer(LAST_EXCEPTION_TIMER)

            logger.info(logString)


mainLoop()
