from utils.color_utils import BLUE, GREEN, YELLOW, RED

ENABLE_DEMO_LOGGING = False
ENABLE_DEMO_ANIMATION = True

PIXEL_CARD_TRAYS = 30
PIXEL_CARD_TRAY_LEDS = 5
PIXEL_CARD_TRAY_GRID_SIZE = 8
PIXEL_CARD_TRAY_GRID_LEDS = PIXEL_CARD_TRAY_GRID_SIZE * PIXEL_CARD_TRAY_GRID_SIZE

PIXEL_CARD_TRAY_TOTAL_LEDS = PIXEL_CARD_TRAY_LEDS * 2 + PIXEL_CARD_TRAY_GRID_LEDS

TRAY_BRIGHTNESS = 0.15


class PowerStateEnum:
    OFF = 0
    FULL_POWER = 1
    PARTIAL_POWER = 2
    NO_POWER = 3
    ERROR = 4


def _color_to_scaled_int(color, brightness):
    return (int(color.R * brightness) << 16) | (int(color.G * brightness) << 8) | int(color.B * brightness)


CARD_TRAY_COLORS = {
    PowerStateEnum.OFF: 0,
    PowerStateEnum.FULL_POWER: _color_to_scaled_int(GREEN, TRAY_BRIGHTNESS),
    PowerStateEnum.PARTIAL_POWER: _color_to_scaled_int(YELLOW, TRAY_BRIGHTNESS),
    PowerStateEnum.NO_POWER: _color_to_scaled_int(RED, TRAY_BRIGHTNESS),
    PowerStateEnum.ERROR: _color_to_scaled_int(BLUE, TRAY_BRIGHTNESS),
}

TRAY_DEMO_CHANGE_SECONDS = 6.0
TIMER_TRAY_DEMO = "tray_demo"
