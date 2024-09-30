import adafruit_logging as logging # pyright: ignore[reportMissingImports]
from animation_manager import Animatable, AnimationManager
from neotrellis_manager import NeoTrellisManager

class Blink(Animatable):
    def __init__(self, x, y, blinkFreq, onColor, offColor, maxBlinks = 0):
        super().__init__()
        self.x = x
        self.y = y
        self.onColor = onColor
        self.offColor = offColor
        self.blinkFreq = blinkFreq
        self.maxBlinks = maxBlinks
        self.blinkOn = True
        self.blinkAccum = 0

    def Draw(self, delta_time, total_time):
        self.blinkAccum += delta_time
        # eng_logger.info(f"Blink.Draw: {self.x}, {self.y}, blinkT: {self.blinkAccum}, blinkFreq: {self.blinkFreq}")
        if  self.blinkAccum > self.blinkFreq:
            self.maxBlinks -= 1
            if self.maxBlinks == 0:
                # eng_logger.info(f"Removing Blink: {self.x}, {self.y}")
                AnimationManager.remove(self)
                if(self.AnimationComplete):
                    self.AnimationComplete()

                return
            
            self.blinkAccum = 0
            self.blinkOn = not self.blinkOn
            blinkColor = self.onColor if self.blinkOn else self.offColor
            NeoTrellisManager.setButtonColor(self.x, self.y, blinkColor)
            # eng_logger.info(f"Blink: {self.x}, {self.y}, {blinkColor}")
            self.startTime = total_time

class ListBlink(Animatable):
    def __init__(self, coords, blinkFreq, onColor, offColor, maxBlinks = 0):
        super().__init__()
        self.coords = coords
        self.onColor = onColor
        self.offColor = offColor
        self.blinkFreq = blinkFreq
        self.maxBlinks = maxBlinks
        self.blinkOn = True
        self.blinkAccum = 0

    def Draw(self, delta_time, total_time):
        self.blinkAccum += delta_time
        # eng_logger.info(f"Blink.Draw: {self.x}, {self.y}, blinkT: {self.blinkAccum}, blinkFreq: {self.blinkFreq}")
        if  self.blinkAccum > self.blinkFreq:
            self.maxBlinks -= 1
            if self.maxBlinks == 0:
                # eng_logger.info(f"Removing Blink: {self.x}, {self.y}")
                AnimationManager.remove(self)
                if(self.AnimationComplete):
                    self.AnimationComplete()
                return
            
            self.blinkAccum = 0
            self.blinkOn = not self.blinkOn
            blinkColor = self.onColor if self.blinkOn else self.offColor
            for coord in self.coords:
                NeoTrellisManager.setButtonColor(coord.x, coord.y, blinkColor)
            self.startTime = total_time
