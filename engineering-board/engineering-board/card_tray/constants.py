from power_cards.animation import CARD_GRID_PIXELS
from utils.color_utils import BLUE, GREEN, YELLOW, RED, scale_neo_packed

DEMO_LOGGING = False
DEMO_ANIMATION = True

CARD_TRAY_COUNT = 30
CARD_TRAY_STATUS_PIXELS = 5

CARD_TRAY_TOTAL_PIXELS = CARD_GRID_PIXELS + CARD_TRAY_STATUS_PIXELS * 2

CARD_TRAY_BRIGHTNESS = 0.15


class PowerStateEnum:
    OFF = 0
    FULL_POWER = 1
    PARTIAL_POWER = 2
    NO_POWER = 3
    ERROR = 4


CARD_TRAY_COLORS = {
    PowerStateEnum.OFF: 0,
    PowerStateEnum.FULL_POWER: scale_neo_packed(GREEN, CARD_TRAY_BRIGHTNESS),
    PowerStateEnum.PARTIAL_POWER: scale_neo_packed(YELLOW, CARD_TRAY_BRIGHTNESS),
    PowerStateEnum.NO_POWER: scale_neo_packed(RED, CARD_TRAY_BRIGHTNESS),
    PowerStateEnum.ERROR: scale_neo_packed(BLUE, CARD_TRAY_BRIGHTNESS),
}

TRAY_DEMO_CHANGE_SECONDS = 6.0
TIMER_TRAY_DEMO = "tray_demo"
