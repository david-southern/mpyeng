from random import randrange
import adafruit_logging as logging # pyright: ignore[reportMissingImports]
from adafruit_led_animation import color as AdaColors

eng_logger = logging.getLogger("main")
eng_logger.setLevel(logging.INFO) # pyright: ignore[reportAttributeAccessIssue]

COMMON_COLORS = [ 
    AdaColors.RED, 
    AdaColors.GREEN, 
    AdaColors.BLUE, 
    AdaColors.CYAN, 
    AdaColors.PURPLE, 
    AdaColors.YELLOW, 
    AdaColors.WHITE 
]

def randomColor():
    return (randrange(256), randrange(256), randrange(256))

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

def EnumName(enum, value):
    for k,v in enum.__dict__.items():
        if v == value:
            return k
    return None

def EnumValue(enum, name):
    return getattr(enum, name, None)