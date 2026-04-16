import time
import board

import adafruit_logging as logging  # pyright: ignore[reportMissingImports]

logger = logging.getLogger("main")
logger.setLevel(
    logging.INFO  # pylint: disable=no-member # pyright: ignore[reportAttributeAccessIssue]
)

ENABLE_SLOW_LOG = False

# Running the TM1637 displays when the board is does not have an external +5V supply causes the
# Arduino to crash erratically. Not sure why, but it definitely happens. Providing the external +5V
# supply stops this happening, but I'll leave this enable flag here so that the board can be run
# without external power if desired.
ENABLE_POWER_DISPLAY = False

ENABLE_PIXELS = False
ENABLE_CARD_READER = False
ENABLE_POWER_GRID = False
ENABLE_SWITCHBOARD = False
ENABLE_LEFT_SWITCHBOARD = False
ENABLE_RIGHT_SWITCHBOARD = False

ENABLE_LEFT_PIXELS = False
ENABLE_RIGHT_PIXELS = False

if board.board_id == "grandcentral_m4_express":
    ENABLE_POWER_DISPLAY = False
    ENABLE_PIXELS = True
    ENABLE_CARD_READER = True
    ENABLE_POWER_GRID = False
    ENABLE_SWITCHBOARD = True
    ENABLE_LEFT_SWITCHBOARD = False
    ENABLE_RIGHT_SWITCHBOARD = True
    ENABLE_RIGHT_PIXELS = True

if board.board_id == "adafruit_feather_rp2040":
    ENABLE_PIXELS = True
    ENABLE_RIGHT_PIXELS = True

SLOW_LOG_FREQUENCY = 1
slowLogCount = {}

TIMER_SLOW_LOG = "slow_log"

_timers = {}
_timer_intervals = {}


def register_timer(key, interval_sec: float):
    """Registers a timer with the given key and interval. Must be called before check_timer.
    key: any hashable value (str, tuple, etc.) to identify this timer."""
    _timer_intervals[key] = interval_sec
    _timers[key] = time.monotonic() + interval_sec


def check_timer(key) -> bool:
    """Returns True if the registered interval has elapsed for the given key, resetting the timer.
    Returns False if the interval has not yet elapsed.
    Raises ValueError if the key has not been registered with register_timer."""
    if key not in _timer_intervals:
        raise ValueError(f"Timer key {repr(key)} has not been registered. Call register_timer first.")
    now = time.monotonic()
    if now >= _timers[key]:
        _timers[key] = now + _timer_intervals[key]
        return True
    return False


register_timer(TIMER_SLOW_LOG, SLOW_LOG_FREQUENCY)


def SlowLog(message: str):
    global slowLogCount

    if not ENABLE_SLOW_LOG:
        return

    if message not in slowLogCount:
        slowLogCount[message] = 0
    slowLogCount[message] += 1

    if not check_timer(TIMER_SLOW_LOG):
        return

    for logMessage, logCount in slowLogCount.items():
        logger.info(
            f"PixelManager{disabledString(ENABLE_PIXELS)}: (rpt: {logCount}) {logMessage}"
        )
    slowLogCount = {}


def disabledString(enabled: bool):
    return "" if enabled else "(DISABLED)"


def safeString(thingy, defaultString):
    return str(thingy) if thingy is not None else defaultString


def shortString(string, maxLen=200):
    if (string is None) or (len(string) == 0):
        return ""
    if len(string) > maxLen:
        return string[:maxLen] + "..."
    return string


def format_hex(val):
    return f"0x{int(val):02X}"


def format_hex_list(listVal, delimiter=", "):
    return delimiter.join(f"{format_hex(val)}" for val in listVal)
