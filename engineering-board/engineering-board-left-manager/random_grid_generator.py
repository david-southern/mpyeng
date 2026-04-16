import time

from color_utils import BLUE, GREEN, RED, YELLOW
from power_card import CardAnimationHelpers
from power_card_tray import BLACK

GRID_SCROLL_SECONDS = 1
POWER_VALUE_LERP_PER_SECOND = 0.6
ANIMATION_SPEED_MS = 5
STEP_SPEED_MS = 100

LOW_POWER_LEVEL_16 = 5
SAFE_POWER_LEVEL_16 = 9
WARNING_POWER_LEVEL_16 = 13

LOW_POWER_LEVEL_8 = 1
SAFE_POWER_LEVEL_8 = 3
WARNING_POWER_LEVEL_8 = 5

LOW_POWER_LEVEL_5 = 1
SAFE_POWER_LEVEL_5 = 2
WARNING_POWER_LEVEL_5 = 4

GRID_BRIGHTNESS = 0.1
LOW_COLOR = BLUE.scale(GRID_BRIGHTNESS)
SAFE_COLOR = GREEN.scale(GRID_BRIGHTNESS)
WARNING_COLOR = YELLOW.scale(GRID_BRIGHTNESS)
DANGER_COLOR = RED.scale(GRID_BRIGHTNESS)

class RandomGridGenerator:
    def __init__(self, gridSize):
        self.__maxLevel = 100
        self.__targetLevel = 0
        self.__curLevel: float = 0
        self.__gridSize = gridSize
        self.__valueLerpPerSecond =  self.__maxLevel * POWER_VALUE_LERP_PER_SECOND

        self.lowPowerLevel = LOW_POWER_LEVEL_16 if gridSize == 16 else LOW_POWER_LEVEL_8 if gridSize == 8 else LOW_POWER_LEVEL_5
        self.safePowerLevel = SAFE_POWER_LEVEL_16 if gridSize == 16 else SAFE_POWER_LEVEL_8 if gridSize == 8 else SAFE_POWER_LEVEL_5
        self.warningPowerLevel = WARNING_POWER_LEVEL_16 if gridSize == 16 else WARNING_POWER_LEVEL_8 if gridSize == 8 else WARNING_POWER_LEVEL_5

        self.__pixelColors = [BLACK for pixIndex in range(self.__gridSize * self.__gridSize)]

        self.__gridScrollSeconds = GRID_SCROLL_SECONDS / self.__gridSize
        self.__lastScrollTime = time.monotonic()
        self.__nextGridScrollTime = self.__lastScrollTime + self.__gridScrollSeconds


    @property
    def PixelColors(self):
        return CardAnimationHelpers.pixel_buffer(self.__pixelColors)

    @property
    def TargetLevel(self):
        return self.__targetLevel

    @TargetLevel.setter
    def TargetLevel(self, value):
        self.__targetLevel = value

    def PixelIndex(self, x, y):
        pixelIndex = y * self.__gridSize

        # The pixel grids that we are using map the pixels as a zig-zag linear string: Pixel zero
        # starts at the bottom-left of the grid, and the pixels increment to the right until the
        # string reaches the edge of the grid. Then the string moves up one pixel, and proceeds
        # incrementing to the left.
        if y % 2 == 0:
            pixelIndex += x
        else:
            pixelIndex += (self.__gridSize - 1) - x

        return pixelIndex

    def UpdateGridState(self):
        simTime = time.monotonic()

        if simTime > self.__nextGridScrollTime:
            elapsedTime = simTime - self.__lastScrollTime
            self.__lastScrollTime = simTime
            self.__nextGridScrollTime = self.__lastScrollTime + self.__gridScrollSeconds

            delta = abs(self.__curLevel - self.__targetLevel)
            if delta > 0:
                delta = min(delta, self.__valueLerpPerSecond * elapsedTime)
                if self.__curLevel > self.__targetLevel:
                    delta = -delta
                self.__curLevel += delta

            currentLevel = self.__curLevel / self.__maxLevel
            currentY = int(currentLevel * self.__gridSize)

            for y in range(self.__gridSize):
                for x in range(self.__gridSize):
                    pixelColor = BLACK
                    pixelIndex = self.PixelIndex(x, y)

                    if x < self.__gridSize - 1:
                        pixelColor = self.__pixelColors[self.PixelIndex(x + 1, y)]

                    elif y <= currentY:
                        pixelColor = DANGER_COLOR

                        if y <= self.lowPowerLevel:
                            pixelColor = LOW_COLOR
                        elif y <= self.safePowerLevel:
                            pixelColor = SAFE_COLOR
                        elif y <= self.warningPowerLevel:
                            pixelColor = WARNING_COLOR

                    if pixelColor != self.__pixelColors[pixelIndex]:
                        self.__pixelColors[pixelIndex] = pixelColor

    def __str__(self):
        return f"RandomGridGenerator(GridSize: {self.__gridSize})"
