import time
from machine import ADC, Pin

from utils.profiling import log_free_ram

from utils.eng_utils import (
    check_timer,
    register_timer,
    logger,
    reset_timer,
)
from utils.device_manager import DeviceManager
from utils.profiling import register_profile, start_profile, stop_profile, report_all_profiles

ENABLE_HEARTBEAT_LOGGING = False

HEARTBEAT_FREQUENCY_SEC = 1
TIMER_HEARTBEAT = "heartbeat"

TIMER_ANALOG_POLL = "analog_poll"
ANALOG_POLL_FREQUENCY_SEC = 0.01

# Amount of time to wait after a resistor swap before tracking a new min/max voltage for the new resistor
TIMER_VOLTAGE_RESET = "voltage_reset"
VOLTAGE_RESET_OFFSET_SEC = 2.0

PROFILE_REPORT_FREQUENCY_SEC = 999999
TIMER_PROFILE_REPORT = "profile_report"

TIMER_UNKNOWN_DEVICE_LOG = "unknown_device_log"
UNKNOWN_DEVICE_LOG_FREQUENCY_SEC = 1.0

# Known fixed resistor in the voltage-divider circuit (ohms)
TEST_FIXED_RESISTANCE_OHMS = 1200
V_REF = 3.3  # RP2350 uses the 3.3V supply as the reference voltage for ADC readings
ANALOG_PIN = 26

# Smoothed voltage below this value is treated as "zero" (no resistor connected)
ZERO_VOLTAGE_THRESHOLD = 0.02

# Duration (seconds) that smoothed voltage must read near-zero before treating
# the resistor as absent and waiting for a new one
RESISTOR_CHANGE_SECONDS_THRESHOLD = 2.0

# EMA smoothing factor for voltage (0.05 ≈ 1s time constant at 50ms sample rate)
EMA_ALPHA = 0.05

SAMPLE_PROFILE = register_profile("samples")

register_timer(TIMER_HEARTBEAT, HEARTBEAT_FREQUENCY_SEC)
register_timer(TIMER_PROFILE_REPORT, PROFILE_REPORT_FREQUENCY_SEC)
register_timer(TIMER_UNKNOWN_DEVICE_LOG, UNKNOWN_DEVICE_LOG_FREQUENCY_SEC)
register_timer(TIMER_ANALOG_POLL, ANALOG_POLL_FREQUENCY_SEC)
register_timer(TIMER_VOLTAGE_RESET, VOLTAGE_RESET_OFFSET_SEC)

PROFILE_HEARTBEAT = register_profile(TIMER_HEARTBEAT)


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

    test_pin = ADC(Pin(ANALOG_PIN))

    logger.info(f"Monitoring analog input on {ANALOG_PIN}")
    logger.info(f"Reference voltage {V_REF}V")
    logger.info(f"Fixed resistance {TEST_FIXED_RESISTANCE_OHMS} ohm")

    # EMA-smoothed voltage; seeded with the first reading
    smoothed_voltage = get_voltage(test_pin)

    # Per-run tracking state
    max_voltage = smoothed_voltage
    min_voltage = smoothed_voltage

    # Resistor-absent state tracking
    resistor_absent = False
    zero_voltage_start_ticks = None

    while True:
        if check_timer(TIMER_HEARTBEAT):
            start_profile(PROFILE_HEARTBEAT)
            log_heartbeat()
            stop_profile(PROFILE_HEARTBEAT)

            if resistor_absent:
                logger.info("Test resistor is not present")
            else:
                log_str = f"V: {smoothed_voltage:6.4f} / ∧{max_voltage:6.4f} / ∨{min_voltage:<6.4f} "

                logger.info(log_str)

        if check_timer(TIMER_PROFILE_REPORT):
            report_all_profiles()

        if check_timer(TIMER_ANALOG_POLL):
            start_profile(SAMPLE_PROFILE)
            raw_voltage = get_voltage(test_pin)

            # EMA smoothing for voltage
            smoothed_voltage = EMA_ALPHA * raw_voltage + (1.0 - EMA_ALPHA) * smoothed_voltage
            stop_profile(SAMPLE_PROFILE)

            if not resistor_absent:
                if max_voltage == 0:
                    if check_timer(TIMER_VOLTAGE_RESET):
                        max_voltage = smoothed_voltage
                        min_voltage = smoothed_voltage
                else:
                    max_voltage = max(max_voltage, smoothed_voltage)
                    min_voltage = min(min_voltage, smoothed_voltage)

                # Detect resistor removal: voltage near zero for longer than the threshold
                if raw_voltage < ZERO_VOLTAGE_THRESHOLD:
                    if zero_voltage_start_ticks is None:
                        zero_voltage_start_ticks = time.ticks_ms()
                    elif (
                        time.ticks_diff(time.ticks_ms(), zero_voltage_start_ticks)
                        > RESISTOR_CHANGE_SECONDS_THRESHOLD * 1000
                    ):
                        resistor_absent = True
                else:
                    zero_voltage_start_ticks = None
            else:
                # Detect new resistor: wait for non-zero smoothed voltage, then reset run state
                if raw_voltage >= ZERO_VOLTAGE_THRESHOLD:
                    smoothed_voltage = raw_voltage
                    max_voltage = 0
                    min_voltage = 999
                    resistor_absent = False
                    zero_voltage_start_ticks = None
                    reset_timer(TIMER_VOLTAGE_RESET)


mainLoop()
