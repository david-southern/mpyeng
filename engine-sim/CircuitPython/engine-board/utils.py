import board

LED_DATA_PIN = board.D27
READER_COUNT = 10
LEDS_PER_READER = 11
LED_COUNT = READER_COUNT * LEDS_PER_READER

BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

READER_MAX_VOLTAGE = 3.3

def safeString(thingy, defaultString):
    return str(thingy) if thingy is not None else defaultString