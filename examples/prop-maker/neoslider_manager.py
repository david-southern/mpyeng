import board
from eng_utils import logger
from adafruit_seesaw.seesaw import Seesaw
from adafruit_seesaw.analoginput import AnalogInput
from adafruit_seesaw import neopixel

NEOSLIDER_ANALOG_PIN = 18
NEOSLIDER_PIX_PIN = 14
NEOSLIDER_PIX_COUNT = 4

logger.info("Initializing NeoSlider Manager")

class NeoSliderManagerClass:
    def __init__(self, i2cAddress=0x30):
        self.neoslider = None
        try:
            self.neoslider = Seesaw(board.STEMMA_I2C(), i2cAddress)
        except Exception as e:
            logger.error(f"Error initializing NeoSlider: {e}")
            return

        self.valueInput = AnalogInput(self.neoslider, NEOSLIDER_ANALOG_PIN, delay=0.01)
        self.neopixels = neopixel.NeoPixel(self.neoslider, NEOSLIDER_PIX_PIN, NEOSLIDER_PIX_COUNT)

        self.neopixels.brightness = 1.0
        self.neopixels.fill((250, 0, 0))
        self.neopixels.show()

    @property
    def Value(self):
        if self.neoslider is None:
            return 0
        
        return self.valueInput.value

    def SetPixelColor(self, color):
        if self.neoslider is None:
            return
        
        self.neopixels.fill(color)
        self.neopixels.show()

    def __str__(self):
        return f"NeoSlider: Volt: {self.Value}"

NeoSliderManager = NeoSliderManagerClass()
