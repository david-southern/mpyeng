from collections import namedtuple
from adafruit_neotrellis.neotrellis import NeoTrellis
from eng_utils import eng_logger
from neotrellis_manager import NeoTrellisManager

Coord = namedtuple('Coord', ['x', 'y'])

class TrellisGame:
    def __init__(self):
        self.name = "Base"
        self.enabled = False
        pass

    def Enable(self):
        self.enabled = True
        eng_logger.info(f"Base({self.name}:{id(self)}): Subbing {id(self)}")
        NeoTrellisManager.subscribe(self)

    def Disable(self):
        self.enabled = False
        eng_logger.info(f"Base({self.name}:{id(self)}): Unsubbing {id(self)}")
        NeoTrellisManager.unsubscribe(self)

    def buttonPressed(self, x, y, event):
        if not self.enabled:
            return
        eng_logger.info(f"Base({self.name}): Button Pressed: {x}, {y}, Event: {event}")

    def Update(self):
        if not self.enabled:
            return
        NeoTrellisManager.Update()