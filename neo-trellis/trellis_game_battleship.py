import time
import adafruit_logging as logging # pyright: ignore[reportMissingImports]
from random import randrange
from adafruit_led_animation import color as AdaColors
from adafruit_neotrellis.neotrellis import NeoTrellis
from eng_utils import COMMON_COLORS, EnumName, eng_logger
from neotrellis_manager import NeoTrellisManager, NeoTrellisManagerClass
from trellis_game_base import TrellisGame

eng_logger = logging.getLogger("battleship")
eng_logger.setLevel(logging.INFO) # pyright: ignore[reportAttributeAccessIssue]

SHOW_DIAGNOSTICS = False

class HintMode():
    Half = 1
    Quarter = 2

class HintDirection():
    X = 1
    Y = 2
    
class GameState():
    Guessing = 1
    AnimatingHint = 2
    AnimatingWin = 3
    
class TrellisGameBattleship(TrellisGame):
    def __init__(self):
        TrellisGame.__init__(self)
        self.lastLogString = ""
        self.HintMode = HintMode.Quarter
        self.resetGame()

    def resetGame(self):
        self.targetX = randrange(NeoTrellisManagerClass.TRELLIS_WIDTH)
        self.targetY = randrange(NeoTrellisManagerClass.TRELLIS_HEIGHT)
        self.gameState = GameState.Guessing
        self.hintCountdown = 0
        self.hintDirection = HintDirection.X
        self.winRadius = 0
        self.winColor = AdaColors.BLACK
        # NeoTrellisManager.setButtonColor(self.targetX, self.targetY, AdaColors.AMBER)


    def buttonPressed(self, x, y, event):
        super().buttonPressed(x, y, event)

        if x == self.targetX and y == self.targetY:
            self.createWinAnimation()
            return

        NeoTrellisManager.setButtonColor(x, y, AdaColors.BLUE)
        self.createHint(x,y)

    def createWinAnimation(self):
        self.gameState = GameState.AnimatingWin
        self.winColor = AdaColors.RED
        self.winRadius = 0

    def animateWin(self):
        didDraw = False
        for y in range(NeoTrellisManagerClass.TRELLIS_HEIGHT):
            for x in range(NeoTrellisManagerClass.TRELLIS_WIDTH):
                pixRadius = ((x - self.targetX) ** 2 + (y - self.targetY) ** 2) ** 0.5
                if pixRadius < self.winRadius:
                    NeoTrellisManager.setButtonColor(x, y, AdaColors.BLACK)
                if(abs(pixRadius - self.winRadius) <= 1):                
                    NeoTrellisManager.setButtonColor(x, y, self.winColor)
                    didDraw = True

        self.winRadius += 1

        if not didDraw:
            self.resetGame()

    def createHint(self, shotX, shotY):
        self.gameState = GameState.AnimatingHint
        self.hintCountdown = time.monotonic() + 0.3
        hintXStart = 0
        hintXEnd = NeoTrellisManagerClass.TRELLIS_WIDTH
        hintYStart = 0
        hintYEnd = NeoTrellisManagerClass.TRELLIS_HEIGHT

        eng_logger.info(f"Shot: {shotX}, {shotY}, Target: {self.targetX}, {self.targetY}")

        if self.HintMode == HintMode.Quarter or self.hintDirection == HintDirection.X:
            if shotX <= self.targetX:
                hintXStart = shotX
                eng_logger.info(f"Mushy Hint: X <= Target, XStart: {hintXStart}")
            elif shotX >= self.targetX:
                hintXEnd = shotX + 1
                eng_logger.info(f"Mushy Hint: X >= Target, XEnd: {hintXEnd}")

        if self.HintMode == HintMode.Quarter or self.hintDirection == HintDirection.Y:
            if shotY <= self.targetY:
                hintYStart = shotY
                eng_logger.info(f"Mushy Hint: Y <= Target, YStart: {hintYStart}")
            elif shotY >= self.targetY:
                hintYEnd = shotY + 1
                eng_logger.info(f"Mushy Hint: Y >= Target, YEnd: {hintYEnd}")

        self.hintDirection = HintDirection.X if self.hintDirection == HintDirection.Y else HintDirection.Y

        eng_logger.info(f"Drawing Hint: ({hintXStart}, {hintYStart}) - ({hintXEnd}, {hintYEnd})")

        for y in range(hintYStart, hintYEnd):
            for x in range(hintXStart, hintXEnd):
                curColor = NeoTrellisManager.getButtonColor(x, y)
                if curColor == AdaColors.BLACK:
                    NeoTrellisManager.setButtonColor(x, y, AdaColors.GREEN)

    def animateHint(self):
        if self.hintCountdown <= 0:
            return
        if(time.monotonic() < self.hintCountdown):
            return
        
        self.hintCountdown = 0
        for y in range(NeoTrellisManagerClass.TRELLIS_HEIGHT):
            for x in range(NeoTrellisManagerClass.TRELLIS_WIDTH):
                curColor = NeoTrellisManager.getButtonColor(x, y)
                if curColor == AdaColors.GREEN:
                    NeoTrellisManager.setButtonColor(x, y, AdaColors.BLACK)
        self.gameState = GameState.Guessing

    def Update(self):
        if SHOW_DIAGNOSTICS:
            log_string = f"Game State: {EnumName(GameState, self.gameState)}, " + \
                f"winRadius: {self.winRadius}, winColor: {self.winColor}, hintCountdown: {self.hintCountdown}"
            if self.lastLogString != log_string:
                eng_logger.info(log_string)
                self.lastLogString = log_string

        if self.gameState == GameState.AnimatingHint:
            self.animateHint()

        if self.gameState == GameState.AnimatingWin:
            self.animateWin()

        TrellisGame.Update(self)
