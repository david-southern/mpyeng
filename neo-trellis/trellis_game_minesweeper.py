from collections import deque
import time
import adafruit_logging as logging # pyright: ignore[reportMissingImports]
from random import randrange
from adafruit_led_animation import color as AdaColors
from animation_blink import ListBlink
from animation_manager import Animatable, AnimationManager
from eng_utils import EnumName, eng_logger
from neotrellis_manager import ButtonEvent, NeoTrellisManager, NeoTrellisManagerClass
from trellis_game_base import Coord, TrellisGame

eng_logger = logging.getLogger("minesweeper")
eng_logger.setLevel(logging.WARNING) # pyright: ignore[reportAttributeAccessIssue]

SHOW_DIAGNOSTICS = False
TARGET_COUNT = 11

class GameState():
    Guessing = 1
    AnimatingLoss = 2
    AnimatingWin = 3

GroundColor = (30, 30, 30)
MineColors = [
    (0, 0, 0),
    (0, 255, 0),
    (0, 0, 200),
    (0, 255, 255),
    (250, 100, 0),
    (255, 0, 255),
    (255, 100, 255),
    (255, 150, 255),
    (255, 200, 255),
    (255, 255, 255),
]

TEST_BOARD = None
SAVE_TEST_BOARD = [
    Coord(0, 0),
    Coord(2, 0),
    Coord(4, 0),
    Coord(6, 0),

    Coord(0, 1),

    Coord(0, 2),

    Coord(5, 3),

    Coord(0, 5),
    Coord(1, 5),

    Coord(3, 6),
    Coord(4, 6),
]    

class TrellisGameMinesweeper(TrellisGame):
    def __init__(self):
        TrellisGame.__init__(self)
        self.lastLogString = ""
        self.resetGame()

    def resetGame(self):
        self.animationCountdown = None
        NeoTrellisManager.fill(GroundColor)
        self.floodStop = set()
        self.winCount = 0
        self.mines = [
            [ False ] * NeoTrellisManagerClass.TRELLIS_WIDTH
            for y in range(NeoTrellisManagerClass.TRELLIS_HEIGHT) 
        ]

        self.winCount = NeoTrellisManagerClass.TRELLIS_WIDTH * NeoTrellisManagerClass.TRELLIS_HEIGHT

        if TEST_BOARD is not None:
            for coord in TEST_BOARD: # pyright: ignore
                self.mines[coord.x][coord.y] = True
                self.winCount -= 1
                eng_logger.info(f"Add Mines: {coord.x}, {coord.y}")
                # NeoTrellisManager.setButtonColor(coord.x, coord.y, AdaColors.MAGENTA)
        else:
            for i in range(TARGET_COUNT):
                while True:
                    targetX = randrange(NeoTrellisManagerClass.TRELLIS_WIDTH)
                    targetY = randrange(NeoTrellisManagerClass.TRELLIS_HEIGHT)
                    eng_logger.info(f"Add Mines: {targetX}, {targetY}")
                    if self.mines[targetX][targetY] == 0:
                        break

                self.mines[targetX][targetY] = True
                self.winCount -= 1
                # NeoTrellisManager.setButtonColor(targetX, targetY, AdaColors.MAGENTA)

        self.gameState = GameState.Guessing

        # AnimationManager.add(Blink(0, 0, 0.5, AdaColors.RED, AdaColors.BLACK, 10))

    def minesAround(self, x, y):
        count = 0
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if x + dx < 0 or x + dx >= NeoTrellisManagerClass.TRELLIS_WIDTH:
                    continue
                if y + dy < 0 or y + dy >= NeoTrellisManagerClass.TRELLIS_HEIGHT:
                    continue
                if self.mines[x + dx][y + dy]:
                    count += 1
        return count
    
    def buttonPressed(self, x, y, event):
        super().buttonPressed(x, y, event)

        if event == ButtonEvent.LONG_PRESS:
            if(NeoTrellisManager.getButtonColor(x, y) == AdaColors.RED):
                NeoTrellisManager.setButtonColor(x, y, GroundColor)
            else:
                NeoTrellisManager.setButtonColor(x, y, AdaColors.RED)
            return

        if self.mines[x][y]:
            self.createLossAnimation()
            return

        count = self.minesAround(x, y)
        self.floodFill(x, y, count)

        eng_logger.info(f"Button Pressed: {x}, {y}, Mines Around: {count}, color: {MineColors[count]}, winCount: {self.winCount}, floodStop: {len(self.floodStop)}")

        if len(self.floodStop) == self.winCount:
            self.createWinAnimation()

    def floodFill(self, x, y, fillCount):
        self.floodLocations = deque([Coord(x, y)], 64)

        while len(self.floodLocations) > 0:
            self.floodFillWorker(fillCount)

    def floodFillWorker(self, fillCount):
        if len(self.floodLocations) == 0:
            return
        
        floodLoc = self.floodLocations.popleft()
        x, y = floodLoc

        if x < 0 or x >= NeoTrellisManagerClass.TRELLIS_WIDTH:
            return
        if y < 0 or y >= NeoTrellisManagerClass.TRELLIS_HEIGHT:
            return
        if self.mines[x][y]:
            return
        if (x, y) in self.floodStop:
            return
        
        self.floodStop.add((x, y))
        buttonCount = self.minesAround(x, y)
        log_string = f"Flood: {x}, {y}, Target: {fillCount}, buttonCount: {buttonCount}"

        log_string += f" - Set: {MineColors[buttonCount]}"
        NeoTrellisManager.setButtonColor(x, y, MineColors[buttonCount])

        if buttonCount > fillCount:
            log_string += " - Stop"
            # eng_logger.info(log_string)
            return

        # eng_logger.info(log_string)        

        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                self.floodLocations.append(Coord(x + dx, y + dy))


    def createWinAnimation(self):
        self.gameState = GameState.AnimatingWin

        animCoords = []
        for x in range(NeoTrellisManagerClass.TRELLIS_WIDTH):
            for y in range(NeoTrellisManagerClass.TRELLIS_HEIGHT):
                if NeoTrellisManager.getButtonColor(x, y) == AdaColors.BLACK:
                    animCoords.append(Coord(x, y))

        winAnimation = ListBlink(animCoords, 0.5, AdaColors.WHITE, AdaColors.BLACK, 30)

        winAnimation.SetAnimationComplete(self.resetGame)
        AnimationManager.add(winAnimation)

    def animateWin(self):
        if self.animationCountdown is None or time.monotonic() < self.animationCountdown:
            return

        self.resetGame()

    def createLossAnimation(self):
        self.gameState = GameState.AnimatingLoss
        self.animationCountdown = time.monotonic() + 1
        NeoTrellisManager.fill(AdaColors.RED)

    def animateLoss(self):
        if self.animationCountdown is None or time.monotonic() < self.animationCountdown:
            return

        self.resetGame()

    def Update(self):
        if SHOW_DIAGNOSTICS:
            log_string = f"Game State: {EnumName(GameState, self.gameState)}"
            if self.lastLogString != log_string:
                eng_logger.info(log_string)
                self.lastLogString = log_string

        if self.gameState == GameState.AnimatingLoss:
            self.animateLoss()

        if self.gameState == GameState.AnimatingWin:
            self.animateWin()

        TrellisGame.Update(self)
