import board
from eng_utils import logger
from adafruit_seesaw.seesaw import Seesaw
from adafruit_seesaw import rotaryio as RotaryIO
from adafruit_seesaw.digitalio import DigitalIO
from adafruit_seesaw.neopixel import NeoPixel

ROTARY_ENCODER_KNOB_PRESS_PIN = 24
ROTARY_ENCODER_PIX_PIN = 6
ROTARY_ENCODER_PIX_COUNT = 1

logger.info("Initializing Rotary Encoder Manager")

class RotaryEncoderManagerClass:
    def __init__(self, i2cAddress=0x36):
        self.seesaw = None
        try:
            self.seesaw = Seesaw(board.STEMMA_I2C(), i2cAddress)
        except Exception as e:
            logger.error(f"Error initializing RotaryEncoder: {e}")
            return

        self.seesaw.pin_mode(ROTARY_ENCODER_KNOB_PRESS_PIN, Seesaw.INPUT_PULLUP)

        self.encoder = RotaryIO.IncrementalEncoder(self.seesaw)
        self.button = DigitalIO(self.seesaw, ROTARY_ENCODER_KNOB_PRESS_PIN)

        self.neopixel = NeoPixel(self.seesaw, ROTARY_ENCODER_PIX_PIN, ROTARY_ENCODER_PIX_COUNT)
        self.neopixel.brightness = 0.1

    @property
    def Position(self):
        if self.seesaw is None:
            return 0
        
        # negate the position to make clockwise rotation positive
        return -self.encoder.position
    
    @property
    def ButtonPressed(self):
        if self.seesaw is None:
            return False
        
        return self.button.value

    def SetPixelColor(self, color):
        if self.seesaw is None:
            return

        self.neopixel.fill(color)
        self.neopixel.show()

    def __str__(self):
        return f"RotaryEncoder: Position: {self.Position}"

RotaryEncoderManager = RotaryEncoderManagerClass()
