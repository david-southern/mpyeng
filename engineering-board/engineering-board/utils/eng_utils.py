import gc
import time

APP_START_TIME = time.ticks_ms()


class LoggerClass:
    def timestamp(self):
        ts = time.ticks_diff(time.ticks_ms(), APP_START_TIME) / 1000
        return f"{ts:7.3f}s"

    def info(self, message):
        print(f"[{self.timestamp()}] {message}")

    def error(self, message):
        print(f"[{self.timestamp()}] ERROR: {message}")


logger = LoggerClass()

logger.info("Logger initialized.")


# Record free RAM at startup for baseline comparison in logs
def log_free_ram(label: str = ""):
    """Log the current free RAM after forcing a garbage collection for consistent readings."""
    gc.collect()
    free = gc.mem_free()
    prefix = f"[{label}] " if label else ""
    logger.info(f"{prefix}Free RAM: {free} bytes")


log_free_ram("power-on")


def set_flags(flags: dict):
    """Set module-level enable flags from a dict of {flag_name: value} pairs."""
    module_globals = globals()
    for key, value in flags.items():
        logger.info(f"Setting flag {key} to {value}")
        module_globals[key] = value


# DeviceManager import triggers device identification and sets enable flags
# via set_flags on this module. Must be imported after flag defaults are defined.
from utils.device_manager import DeviceManager  # noqa: E402, F401  # pyright: ignore[reportUnusedImport]

ENABLE_SLOW_LOG = True

SLOW_LOG_FREQUENCY = 1
slowLogCount = {}

TIMER_SLOW_LOG = "slow_log"

_timers = {}
_timer_intervals = {}


def register_timer(key, interval_sec: float):
    """Registers a timer with the given key and interval. Must be called before check_timer.
    key: any hashable value (str, tuple, etc.) to identify this timer."""
    _timer_intervals[key] = interval_sec
    _timers[key] = time.ticks_ms()


def timer_elapsed_sec(key) -> float:
    """Returns the number of seconds elapsed since the last time check_timer returned True for this key.
    Raises ValueError if the key has not been registered with register_timer."""
    if key not in _timer_intervals:
        raise ValueError(f"Timer key {repr(key)} has not been registered. Call register_timer first.")
    now = time.ticks_ms()
    return time.ticks_diff(now, _timers[key]) / 1000


def reset_timer(key):
    """Resets the timer for the given key to start counting from now."""
    if key not in _timer_intervals:
        raise ValueError(f"Timer key {repr(key)} has not been registered. Call register_timer first.")
    _timers[key] = time.ticks_ms()


def check_timer(key) -> bool:
    """Returns True if the registered interval has elapsed for the given key, resetting the timer.
    Returns False if the interval has not yet elapsed.
    Raises ValueError if the key has not been registered with register_timer."""
    if key not in _timer_intervals:
        raise ValueError(f"Timer key {repr(key)} has not been registered. Call register_timer first.")
    if timer_elapsed_sec(key) >= _timer_intervals[key]:
        reset_timer(key)
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
        logger.info(f"SlowLog: (rpt: {logCount}) {logMessage}")
    slowLogCount = {}


def safeString(thingy, defaultString):
    return str(thingy) if thingy is not None else defaultString


def shortString(string, maxLen=200):
    if (string is None) or (len(string) == 0):
        return ""
    if len(string) > maxLen:
        return string[:maxLen] + "..."
    return string


def gridToStripIndex(x: int, y: int, width: int = 8, height: int = 8) -> int:
    """Convert a Quadrant I (x, y) grid coordinate to the bottom-up serpentine layout that our
    NeoPixel grids use."""
    return y * width + (x if y % 2 == 0 else (width - 1 - x))


def format_hex_list(listVal, delimiter=", "):
    return delimiter.join(f"0x{int(val):02X}" for val in listVal)
