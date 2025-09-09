import adafruit_logging as logging  # pyright: ignore[reportMissingImports]

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

# Running the TM1637 displays when the board is does not have an external +5V supply causes the Arduino to crash
# erratically.  Not sure why, but it definitely happens.  Providing the external +5V supply stops this happening, but
# I'll leave this enable flag here so that the board can be run without external power if desired.
ENABLE_POWER_DISPLAY = False
ENABLE_PIXELS = False
ENABLE_CARD_READER = False
ENABLE_POWER_GRID = False
ENABLE_SWITCHBOARD = False
ENABLE_LEFT_SWITCHBOARD = False
ENABLE_RIGHT_SWITCHBOARD = False


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
