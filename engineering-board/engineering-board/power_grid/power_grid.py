import random

from utils.eng_utils import ENABLE_POWER_GRID, SlowLog, disabledString
from utils.pixel_strip_manager import PixelStripManager


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

    def Update(self):
        SlowLog(f"Updating Power Card Tray {self.UID} state")

        self.__pixelStripManager.SetPixelData(
            self.__pixelIndex,
            self.pixelCount - 1,
            [
                (random.randint(0, 255) << 16) | (random.randint(0, 255) << 8) | random.randint(0, 255)
                for pixIndex in range(self.pixelCount - 1)
            ],
        )

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
