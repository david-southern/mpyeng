from collections import namedtuple
from adafruit_neotrellis.neotrellis import NeoTrellis
from eng_utils import eng_logger
from neotrellis_manager import NeoTrellisManager

Coord = namedtuple('Coord', ['x', 'y'])

class TrellisGame:
    def __init__(self):
        NeoTrellisManager.subscribe(self.buttonPressed)

    def buttonPressed(self, x, y, event):
        eng_logger.info(f"Base: Button Pressed: {x}, {y}, Event: {event}")

    def Update(self):
        NeoTrellisManager.Update()