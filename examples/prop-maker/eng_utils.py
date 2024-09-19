from collections import namedtuple
import adafruit_logging as logging # pyright: ignore[reportMissingImports]

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

def lerp(begin, end, t):
    return begin + (end - begin) * t

def lerp_color(begin, end, t):
    return tuple(int(lerp(begin[i], end[i], t)) for i in range(3))

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
