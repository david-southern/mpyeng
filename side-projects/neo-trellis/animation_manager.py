import time

import adafruit_logging as logging # pyright: ignore[reportMissingImports]
from eng_utils import eng_logger

eng_logger = logging.getLogger("animations")
eng_logger.setLevel(logging.INFO) # pyright: ignore[reportAttributeAccessIssue]

class Animatable:
    def __init__(self):
        self.startTime = time.monotonic()
        self.lastUpdateTime = self.startTime
        self.AnimationComplete = None

    def Draw(self, delta_time, total_time):
        pass

    def Update(self):
        self.Draw(time.monotonic() - self.lastUpdateTime, time.monotonic() - self.startTime)

    def SetAnimationComplete(self, callback):
        self.AnimationComplete = callback
        pass


class AnimationManagerClass:
    def __init__(self):
        self.animatables: set[Animatable] = set()

    def add(self, animatable: Animatable):
        self.animatables.add(animatable)

    def remove(self, animatable: Animatable):
        self.animatables.remove(animatable)

    def Update(self):
        # eng_logger.info(f"AnimationManager.Update: Updating {len(self.animatables)} animatables")
        for animatable in self.animatables:
            animatable.Update()

AnimationManager = AnimationManagerClass()
