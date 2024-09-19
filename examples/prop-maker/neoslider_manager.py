import board
import busio
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
        # self.neoslider = Seesaw(busio.I2C(board.D9, board.D10), i2cAddress)
        self.neoslider = Seesaw(board.STEMMA_I2C(), i2cAddress)
        self.valueInput = AnalogInput(self.neoslider, NEOSLIDER_ANALOG_PIN)
        self.neopixels = neopixel.NeoPixel(self.neoslider, NEOSLIDER_PIX_PIN, NEOSLIDER_PIX_COUNT)

        self.neopixels.brightness = 1.0
        self.neopixels.fill((250, 0, 0))
        self.neopixels.show()

    @property
    def Value(self):
        return self.valueInput.value

    def SetPixelColor(self, color):
        self.neopixels.fill(color)
        self.neopixels.show()

    def __str__(self):
        return f"NeoSlider: Volt: {self.Value}"

NeoSliderManager = NeoSliderManagerClass()
