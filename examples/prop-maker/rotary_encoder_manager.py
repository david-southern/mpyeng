import board
from eng_utils import logger
from adafruit_seesaw.seesaw import Seesaw
# from adafruit_seesaw.rotaryio import RotaryIO
from adafruit_seesaw import rotaryio
from adafruit_seesaw.digitalio import DigitalIO
from adafruit_seesaw.neopixel import NeoPixel

ROTARY_ENCODER_KNOB_PRESS_PIN = 24
ROTARY_ENCODER_PIX_PIN = 6
ROTARY_ENCODER_PIX_COUNT = 1

logger.info("Initializing Rotary Encoder Manager")

class RotaryEncoderManagerClass:
    def __init__(self, i2cAddress=0x36):
        self.seesaw = Seesaw(board.STEMMA_I2C(), i2cAddress)
        self.seesaw.pin_mode(ROTARY_ENCODER_KNOB_PRESS_PIN, Seesaw.INPUT_PULLUP)

        self.encoder = rotaryio.IncrementalEncoder(self.seesaw)
        self.button = DigitalIO(self.seesaw, ROTARY_ENCODER_KNOB_PRESS_PIN)

        self.neopixel = NeoPixel(self.seesaw, ROTARY_ENCODER_PIX_PIN, ROTARY_ENCODER_PIX_COUNT)
        self.neopixel.brightness = 0.1

    @property
    def Position(self):
        # negate the position to make clockwise rotation positive
        return -self.encoder.position
    
    @property
    def ButtonPressed(self):
        return self.button.value

    def SetPixelColor(self, color):
        self.neopixel.fill(color)
        self.neopixel.show()

    def __str__(self):
        return f"RotaryEncoder: Position: {self.Position}"

RotaryEncoderManager = RotaryEncoderManagerClass()
