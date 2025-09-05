# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring

from utils import log
import time
import board
import digitalio
from adafruit_debouncer import Debouncer  # type: ignore # pylint: disable=import-error
from adafruit_circuitplayground import cp

HEARTBEAT_FREQUENCY = 1
NEXT_HEARTBEAT = time.monotonic() + HEARTBEAT_FREQUENCY
POLLING_SLEEP = 0.1

limit_switch_pin = digitalio.DigitalInOut(board.A3)
limit_switch_pin.direction = digitalio.Direction.INPUT
limit_switch_pin.pull = digitalio.Pull.DOWN
limit_switch = Debouncer(limit_switch_pin)

warning_timeout = 15
warning_start = None

warning_on = False
warning_freq = 678
warning_pixel_color = (255, 0, 0)
warning_pulse_length = 1
next_warning_pulse = 0
pulse_on = False


def warning_pulse(mode):
    if mode:
        cp.start_tone(warning_freq)
        cp.pixels.fill(warning_pixel_color)
    else:
        cp.stop_tone()
        cp.pixels.fill((0, 0, 0))


while True:
    limit_switch.update()

    if limit_switch.rose:
        log("Limit switch released")
        warning_start = time.monotonic() + warning_timeout

    if warning_start and time.monotonic() > warning_start:
        warning_on = True
        next_warning_pulse = time.monotonic() + warning_pulse_length
        pulse_on = True
        warning_pulse(pulse_on)
        warning_start = None

    if limit_switch.fell:
        log("Limit switch closed")
        warning_on = False
        warning_start = None
        warning_pulse(False)

    if warning_on and time.monotonic() > next_warning_pulse:
        pulse_on = not pulse_on
        warning_pulse(pulse_on)
        next_warning_pulse = time.monotonic() + warning_pulse_length

    if time.monotonic() > NEXT_HEARTBEAT:
        log("Heartbeat")

        NEXT_HEARTBEAT = time.monotonic() + HEARTBEAT_FREQUENCY

    time.sleep(POLLING_SLEEP)
