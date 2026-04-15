import time
import board
from eng_utils import ENABLE_POWER_GRID, SlowLog, disabledString, logger
from power_card_tray import PixelStripManager
from protocol_resources import LEFT_WING, RIGHT_WING, TRANS1, TRANS2, TRANS3, TRANS4
from random_grid_generator import RandomGridGenerator

GRID_REFRESH_SECONDS = 0.1

LARGE_GRID_SIZE = 16
LARGE_GRID_COUNT = 2

SMALL_GRID_SIZE = 8
SMALL_GRID_COUNT = 4

LEFT_STRIP_LED_COUNT = LARGE_GRID_SIZE * LARGE_GRID_SIZE * LARGE_GRID_COUNT + SMALL_GRID_SIZE * SMALL_GRID_SIZE * SMALL_GRID_COUNT

class PowerGrid:
    def __init__(self, uid, isLarge, pixelStripManager: PixelStripManager):
        self.__uid = uid
        self.__isLarge = isLarge
        self.__maxLevel = 100
        self.__targetLevel = 0
        self.__curLevel: float = 0
        self.__warnMode = False
        self.__deadMode = False
        self.__gridSize = 16 if isLarge else 8

        self.__pixelStripManager = pixelStripManager
        self.pixelCount = self.__gridSize * self.__gridSize
        self.__pixelIndex = self.__pixelStripManager.ReservePixelRange(self.pixelCount)

        self.__randomGridGenerator = RandomGridGenerator(self.__gridSize)
        self.__nextUpdate = time.monotonic() + GRID_REFRESH_SECONDS

    def Update(self):
        SlowLog(f"Updating Power Card Tray {self.UID} state")
        self.__randomGridGenerator.UpdateGridState()

        self.__pixelStripManager.SetPixelData(
            self.__pixelIndex,
            self.pixelCount - 1,
            self.__randomGridGenerator.PixelColors,
        )
        
        simTime = time.monotonic()

        if simTime > self.__nextUpdate:
            self.__nextUpdate = simTime + GRID_REFRESH_SECONDS

    @property
    def UID(self):
        return self.__uid

    @property
    def IsLarge(self):
        return self.__isLarge

    @property
    def CurLevel(self):
        return int(self.__curLevel)

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
    __WING_POWER_GRID_INDEXES = {LEFT_WING: 0, RIGHT_WING: 1}
    __TRANSFORMER_POWER_GRID_INDEXES = {TRANS1: 2, TRANS2: 3, TRANS3: 4, TRANS4: 5}

    def __init__(self, pixelStripManager: PixelStripManager) -> None:
        self._ALL_POWER_GRIDS: list[PowerGrid] = []
        self._ALL_POWER_GRIDS = []
        if ENABLE_POWER_GRID:
            self._ALL_POWER_GRIDS.append(PowerGrid(0, True, pixelStripManager))
            self._ALL_POWER_GRIDS.append(PowerGrid(1, True, pixelStripManager))
            self._ALL_POWER_GRIDS.append(PowerGrid(2, False, pixelStripManager))
            self._ALL_POWER_GRIDS.append(PowerGrid(3, False, pixelStripManager))
            self._ALL_POWER_GRIDS.append(PowerGrid(4, False, pixelStripManager))
            self._ALL_POWER_GRIDS.append(PowerGrid(5, False, pixelStripManager))

    def SetWingMaxPower(self, wingName: str, powerLevel: int):
        if not ENABLE_POWER_GRID:
            return

        gridIndex = self.__WING_POWER_GRID_INDEXES.get(wingName)
        if gridIndex is None:
            logger.error(f"Wing name {wingName} is not recognized.")
            return
        self.SetGridMaxLevel(gridIndex, powerLevel)

    def SetWingTargetPower(self, wingName: str, powerLevel: int):
        if not ENABLE_POWER_GRID:
            return

        gridIndex = self.__WING_POWER_GRID_INDEXES.get(wingName)
        if gridIndex is None:
            logger.error(f"Wing name {wingName} is not recognized.")
            return
        self.SetGridTargetLevel(gridIndex, powerLevel)

    def SetTransformerMaxPower(self, transformerName: str, powerLevel: int):
        if not ENABLE_POWER_GRID:
            return

        gridIndex = self.__TRANSFORMER_POWER_GRID_INDEXES.get(transformerName)
        if gridIndex is None:
            logger.error(f"Transformer index {gridIndex} is out of range.")
            return
        self.SetGridMaxLevel(gridIndex, powerLevel)

    def SetTransformerTargetPower(self, transformerName: str, powerLevel: int):
        if not ENABLE_POWER_GRID:
            return

        gridIndex = self.__TRANSFORMER_POWER_GRID_INDEXES.get(transformerName)
        if gridIndex is None:
            logger.error(f"Transformer index {gridIndex} is out of range.")
            return
        self.SetGridTargetLevel(gridIndex, powerLevel)

    def GetWingCurrentPower(self, wingName: str) -> int:
        if not ENABLE_POWER_GRID:
            return 0

        gridIndex = self.__WING_POWER_GRID_INDEXES.get(wingName)
        if gridIndex is None:
            logger.error(f"Wing name {wingName} is not recognized.")
            return 0
        return self._ALL_POWER_GRIDS[gridIndex].CurLevel

    def GetTransformerCurrentPower(self, transformerName: str) -> int:
        if not ENABLE_POWER_GRID:
            return 0

        gridIndex = self.__TRANSFORMER_POWER_GRID_INDEXES.get(transformerName)
        if gridIndex is None:
            logger.error(f"Transformer name {transformerName} is not recognized.")
            return 0
        return self._ALL_POWER_GRIDS[gridIndex].CurLevel

    def AllGrids(self) -> list[PowerGrid]:
        return self._ALL_POWER_GRIDS

    def UpdateGridState(self):
        for grid in self._ALL_POWER_GRIDS:
            grid.UpdateGridState()

    def SetGridMaxLevel(self, gridIndex: int, maxLevel: int):
        if not ENABLE_POWER_GRID:
            return

        if gridIndex < 0 or gridIndex >= len(self._ALL_POWER_GRIDS):
            logger.error(f"Grid index {gridIndex} is out of range.")
            return

        logger.info(
            f"Setting PowerGrid {gridIndex}{disabledString(ENABLE_POWER_GRID)} max power level to {maxLevel}"
        )
        self._ALL_POWER_GRIDS[gridIndex].MaxLevel = maxLevel

    def SetGridTargetLevel(self, gridIndex: int, curLevel: int):
        if not ENABLE_POWER_GRID:
            return

        if gridIndex < 0 or gridIndex >= len(self._ALL_POWER_GRIDS):
            logger.error(f"Grid index {gridIndex} is out of range.")
            return

        # logger.info(f"Setting PowerGrid {gridIndex}{disabledString(ENABLE_POWER_GRID)} cur power level to {curLevel}")
        self._ALL_POWER_GRIDS[gridIndex].TargetLevel = curLevel

    def SetGridPowerWarning(self, gridIndex: int, warnMode: bool):
        if not ENABLE_POWER_GRID:
            return

        if gridIndex < 0 or gridIndex >= len(self._ALL_POWER_GRIDS):
            logger.error(f"Grid index {gridIndex} is out of range.")
            return

        logger.info(
            f"Setting PowerGrid {gridIndex}{disabledString(ENABLE_POWER_GRID)} power warning to {warnMode}"
        )
        self._ALL_POWER_GRIDS[gridIndex].WarnMode = warnMode

    def SetGridPowerDead(self, gridIndex: int, deadMode: bool):
        if not ENABLE_POWER_GRID:
            return

        if gridIndex < 0 or gridIndex >= len(self._ALL_POWER_GRIDS):
            logger.error(f"Grid index {gridIndex} is out of range.")
            return

        logger.info(
            f"Setting PowerGrid {gridIndex}{disabledString(ENABLE_POWER_GRID)} power DEAD to {deadMode}"
        )
        self._ALL_POWER_GRIDS[gridIndex].DeadMode = deadMode

LEFT_STRIP_DATA_PIN = board.D5

LeftPixelStrip = PixelStripManager(LEFT_STRIP_DATA_PIN, LEFT_STRIP_LED_COUNT)

PowerGridManager = PowerGridManagerClass(LeftPixelStrip)
