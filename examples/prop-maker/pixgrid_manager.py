import board
from eng_utils import logger
from adafruit_is31fl3741.adafruit_rgbmatrixqt import Adafruit_RGBMatrixQT as RGBMatrix
import adafruit_is31fl3741
from rainbowio import colorwheel

ENABLE_PIX_GRID = False

logger.info("Initializing Pixel Grid Manager")

class PixGridManagerClass:
    def __init__(self):
        self.pixGrid = None
        if not ENABLE_PIX_GRID:
            return
        
        try:
            self.pixGrid = RGBMatrix(board.STEMMA_I2C(), allocate=adafruit_is31fl3741.PREFER_BUFFER)
        except Exception as e:
            logger.error(f"Error initializing PixGrid: {e}")
            return
            
        self.pixGrid.set_led_scaling(0x10)  # LEDs brightness scaling
        self.pixGrid.global_current = 0x10
        self.pixGrid.enable = True
        self.rainbowOffset = 0

    def UpdateRainbow(self):
        if self.pixGrid is None:
            return
        
        for y in range(9):
            for x in range(13):
                self.pixGrid.pixel(x, y, colorwheel((y * 13 + x) * 2 + self.rainbowOffset))

        self.rainbowOffset += 5
        self.pixGrid.show()

    def __str__(self):
        return f"PixGrid"

PixGridManager = PixGridManagerClass()
