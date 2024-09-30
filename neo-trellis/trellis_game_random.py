import time
from random import randrange
from adafruit_led_animation import color as AdaColors
from adafruit_neotrellis.neotrellis import NeoTrellis
from eng_utils import COMMON_COLORS, eng_logger
from neotrellis_manager import NeoTrellisManager
from trellis_game_base import TrellisGame

class TrellisGameRandom(TrellisGame):
    def __init__(self):
        TrellisGame.__init__(self)

    def buttonPressed(self, x, y, event):
        super().buttonPressed(x, y, event)
        eng_logger.info(f"Rand: Button Pressed: {x}, {y}")
        curColor = NeoTrellisManager.getButtonColor(x, y)
        newColor = AdaColors.BLACK if curColor != AdaColors.BLACK else COMMON_COLORS[randrange(len(COMMON_COLORS))]
        NeoTrellisManager.setButtonColor(x, y, newColor)
