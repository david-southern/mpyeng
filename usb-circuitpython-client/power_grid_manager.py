import time
import board
from pixel_manager import BLACK, BLUE, GREEN, RED, YELLOW, PixelManager
from utils import ENABLE_POWER_GRID, disabledString, logger

GRID_SCROLL_SECONDS = 1
POWER_VALUE_LERP_PER_SECOND = 0.6
ANIMATION_SPEED_MS = 5
STEP_SPEED_MS = 100

LARGE_LOW_POWER_LEVEL = 5
LARGE_SAFE_POWER_LEVEL = 9
LARGE_WARNING_POWER_LEVEL = 13

SMALL_LOW_POWER_LEVEL = 1
SMALL_SAFE_POWER_LEVEL = 3
SMALL_WARNING_POWER_LEVEL = 5

LOW_COLOR = BLUE
SAFE_COLOR = GREEN
WARNING_COLOR = YELLOW
DANGER_COLOR = RED

class PowerGrid:
    def __init__(self, uid, isLarge):
        self.__uid = uid
        self.__isLarge = isLarge
        self.__maxLevel = 100
        self.__targetLevel = 0
        self.__curLevel = 0
        self.__warnMode = False
        self.__deadMode = False
        self.__gridSize = 16 if isLarge else 8

        if isLarge:
            self.lowPowerLevel = LARGE_LOW_POWER_LEVEL
            self.safePowerLevel = LARGE_SAFE_POWER_LEVEL
            self.warningPowerLevel = LARGE_WARNING_POWER_LEVEL
        else:
            self.lowPowerLevel = SMALL_LOW_POWER_LEVEL
            self.safePowerLevel = SMALL_SAFE_POWER_LEVEL
            self.warningPowerLevel = SMALL_WARNING_POWER_LEVEL

        self.__pixelColors = [[BLACK for x in range(self.__gridSize)] for y in range(self.__gridSize)]

        self.__gridScrollSeconds = GRID_SCROLL_SECONDS / self.__gridSize
        self.__lastScrollTime = time.monotonic()
        self.__nextGridScrollTime = self.__lastScrollTime + self.__gridScrollSeconds

    def UpdateGridState(self):
        simTime = time.monotonic()

        if simTime > self.__nextGridScrollTime:
            elapsedTime = simTime - self.__lastScrollTime

            diag = f"{self}"

            delta = abs(self.__curLevel - self.__targetLevel)

            if delta > 0:
                delta = min(delta, self.ValueLerpPerSecond * elapsedTime)

                if self.__curLevel > self.__targetLevel:
                    delta = -delta

                self.__curLevel += delta

            currentLevel = self.__curLevel / self.__maxLevel

            currentY = int(currentLevel * self.__gridSize)

            for y in range(self.__gridSize):
                for x in range(self.__gridSize):
                    pixelColor = BLACK

                    if x < self.__gridSize - 1:
                        pixelColor = self.__pixelColors[x + 1][y]
                    elif y <= currentY:
                        pixelLevel = y / float(self.__gridSize)

                        pixelColor = DANGER_COLOR

                        if y <= self.lowPowerLevel:
                            pixelColor = LOW_COLOR
                        elif y <= self.safePowerLevel:
                            pixelColor = SAFE_COLOR
                        elif y <= self.warningPowerLevel:
                            pixelColor = WARNING_COLOR

                    if pixelColor != self.__pixelColors[x][y]:
                        self.__pixelColors[x][y] = pixelColor
                        PixelManager.SetPowerGridColor(self.UID, x, y, pixelColor)

            self.__lastScrollTime = simTime
            self.__nextGridScrollTime = self.__lastScrollTime + self.__gridScrollSeconds

    @property
    def UID(self):
        return self.__uid

    @property
    def IsLarge(self):
        return self.__isLarge

    @property
    def CurLevel(self):
        return self.__curLevel

    @property
    def ValueLerpPerSecond(self):
        return self.__maxLevel * POWER_VALUE_LERP_PER_SECOND

    @property
    def MaxLevel(self):
        return self.__maxLevel

    @MaxLevel.setter
    def MaxLevel(self, value):
        self.__maxLevel = value

    @property
    def TargetLevel(self):
        return self.__targetLevel

    @TargetLevel.setter
    def TargetLevel(self, value):
        self.__targetLevel = value

    @property
    def WarnMode(self):
        return self.__warnMode

    @WarnMode.setter
    def WarnMode(self, value):
        self.__warnMode = value
        self.__deadMode = False

    @property
    def DeadMode(self):
        return self.__deadMode

    @DeadMode.setter
    def DeadMode(self, value):
        self.__deadMode = value
        self.__warnMode = False

    def __str__(self):
        return f"{self.UID}{disabledString(ENABLE_POWER_GRID)}: TGT:{self.TargetLevel}, CUR:{self.CurLevel}"


class PowerGridManagerClass:
    def __init__(self) -> None:
        self._ALL_POWER_GRIDS: list[PowerGrid] = []
        self._ALL_POWER_GRIDS = []
        self._ALL_POWER_GRIDS.append(PowerGrid(0, True))
        self._ALL_POWER_GRIDS.append(PowerGrid(1, True))
        self._ALL_POWER_GRIDS.append(PowerGrid(2, False))
        self._ALL_POWER_GRIDS.append(PowerGrid(3, False))
        self._ALL_POWER_GRIDS.append(PowerGrid(4, False))
        self._ALL_POWER_GRIDS.append(PowerGrid(5, False))

    def AllGrids(self) -> list[PowerGrid]:
        return self._ALL_POWER_GRIDS

    def UpdateGridState(self):
        for grid in self._ALL_POWER_GRIDS:
            grid.UpdateGridState()

    def SetGridMaxLevel(self, gridIndex: int, maxLevel: int):
        if gridIndex < 0 or gridIndex >= len(self._ALL_POWER_GRIDS):
            logger.error(f"Grid index {gridIndex} is out of range.")
            return

        logger.info(f"Setting PowerGrid {gridIndex}{disabledString(ENABLE_POWER_GRID)} max power level to {maxLevel}")
        self._ALL_POWER_GRIDS[gridIndex].MaxLevel = maxLevel

    def SetGridCurLevel(self, gridIndex: int, curLevel: int):
        if gridIndex < 0 or gridIndex >= len(self._ALL_POWER_GRIDS):
            logger.error(f"Grid index {gridIndex} is out of range.")
            return

        # logger.info(f"Setting PowerGrid {gridIndex}{disabledString(ENABLE_POWER_GRID)} cur power level to {curLevel}")
        self._ALL_POWER_GRIDS[gridIndex].TargetLevel = curLevel

    def SetGridPowerWarning(self, gridIndex: int, warnMode: bool):
        if gridIndex < 0 or gridIndex >= len(self._ALL_POWER_GRIDS):
            logger.error(f"Grid index {gridIndex} is out of range.")
            return

        logger.info(f"Setting PowerGrid {gridIndex}{disabledString(ENABLE_POWER_GRID)} power warning to {warnMode}")
        self._ALL_POWER_GRIDS[gridIndex].WarnMode = warnMode

    def SetGridPowerDead(self, gridIndex: int, deadMode: bool):
        if gridIndex < 0 or gridIndex >= len(self._ALL_POWER_GRIDS):
            logger.error(f"Grid index {gridIndex} is out of range.")
            return

        logger.info(f"Setting PowerGrid {gridIndex}{disabledString(ENABLE_POWER_GRID)} power DEAD to {deadMode}")
        self._ALL_POWER_GRIDS[gridIndex].DeadMode = deadMode


PowerGridManager = PowerGridManagerClass()
