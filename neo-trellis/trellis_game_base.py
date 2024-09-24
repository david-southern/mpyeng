from adafruit_neotrellis.neotrellis import NeoTrellis
from eng_utils import eng_logger
from neotrellis_manager import NeoTrellisManager

class TrellisGame:
    def __init__(self):
        NeoTrellisManager.subscribe(self.buttonEvent)

    def buttonEvent(self, x, y, edge):
        eng_logger.info(f"Base: Button Event: {x}, {y}, {edge}")
        if edge == NeoTrellis.EDGE_RISING:
            self.buttonPressed(x, y)

    def buttonPressed(self, x, y):
        eng_logger.info(f"Base: Button Pressed: {x}, {y}")

    def Update(self):
        NeoTrellisManager.Update()