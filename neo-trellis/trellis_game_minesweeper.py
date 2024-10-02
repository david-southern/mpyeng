from collections import deque
import time
import adafruit_logging as logging # pyright: ignore[reportMissingImports]
from random import randrange
from adafruit_led_animation import color as AdaColors
from animation_blink import Blink, ListBlink, ListDisco
from animation_manager import Animatable, AnimationManager
from eng_utils import EnumName, eng_logger
from neotrellis_manager import ButtonEvent, NeoTrellisManager, NeoTrellisManagerClass
from trellis_game_base import Coord, TrellisGame

eng_logger = logging.getLogger("minesweeper")
eng_logger.setLevel(logging.INFO) # pyright: ignore[reportAttributeAccessIssue]

SHOW_DIAGNOSTICS = False
TARGET_COUNT = 10

class GameState():
    Guessing = 1
    Animating = 2
    WaitingForReset = 3

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
        super()
        self.name = "Mines"
        self.lastLogString = ""
        self.resetGame()

    def resetGame(self):
        self.animationCountdown = None
        NeoTrellisManager.fill(GroundColor)
        self.openedButtons = set()
        self.winCount = 0
        self.minesFlagged = 0
        self.mines = [
            [ False ] * NeoTrellisManagerClass.TRELLIS_WIDTH
            for y in range(NeoTrellisManagerClass.TRELLIS_HEIGHT) 
        ]
        self.firstPress = True

        self.winCount = NeoTrellisManagerClass.TRELLIS_WIDTH * NeoTrellisManagerClass.TRELLIS_HEIGHT

        if TEST_BOARD is not None:
            for coord in TEST_BOARD: # pyright: ignore
                self.mines[coord.x][coord.y] = True
                self.winCount -= 1
                eng_logger.info(f"Add Mines: {coord.x}, {coord.y}")
                # NeoTrellisManager.setButtonColor(coord.x, coord.y, AdaColors.MAGENTA)
        else:
            for i in range(TARGET_COUNT):
                targetX, targetY = self.getSafeLocation()
                self.mines[targetX][targetY] = True
                self.winCount -= 1
                # NeoTrellisManager.setButtonColor(targetX, targetY, AdaColors.MAGENTA)

        self.gameState = GameState.Guessing

        # AnimationManager.add(Blink(0, 0, 0.5, AdaColors.RED, AdaColors.BLACK, 10))

    def getSafeLocation(self):
        while True:
            targetX = randrange(NeoTrellisManagerClass.TRELLIS_WIDTH)
            targetY = randrange(NeoTrellisManagerClass.TRELLIS_HEIGHT)
            eng_logger.info(f"Add Mines: {targetX}, {targetY}")
            if self.mines[targetX][targetY] == 0:
                break
            
        return (targetX, targetY)


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
        
        if self.gameState == GameState.Animating:
            return
        
        if self.gameState == GameState.WaitingForReset:
            self.resetGame()
            return
        
        eng_logger.info(f"Mines: Button Pressed: {x}, {y}, Event: {event}")

        if event == ButtonEvent.LONG_PRESS:
            if(NeoTrellisManager.getButtonColor(x, y) == AdaColors.RED):
                self.minesFlagged -= 1
                NeoTrellisManager.setButtonColor(x, y, GroundColor)
            else:
                self.minesFlagged += 1
                NeoTrellisManager.setButtonColor(x, y, AdaColors.RED)
                if len(self.openedButtons) == self.winCount and self.minesFlagged == TARGET_COUNT:
                    self.createWinAnimation()
            return

        if self.mines[x][y]:
            if self.firstPress:
                self.mines[x][y] = False
                targetX, targetY = self.getSafeLocation()
                self.mines[targetX][targetY] = True
            else:
                self.createLossAnimation(x, y)
                return
            
        self.firstPress = False

        count = self.minesAround(x, y)
        self.floodFill(x, y)

        eng_logger.info(f"Button Pressed: {x}, {y}, Mines Around: {count}, color: {MineColors[count]}, winCount: {self.winCount}, Opened: {len(self.openedButtons)}, Flagged: {self.minesFlagged}")

        if len(self.openedButtons) == self.winCount and self.minesFlagged == TARGET_COUNT:
            self.createWinAnimation()

    def floodFill(self, x, y):
        self.floodLocations = deque([Coord(x, y)], 64)

        while len(self.floodLocations) > 0:
            self.floodFillWorker()

    def floodFillWorker(self):
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
        if (x, y) in self.openedButtons:
            return
        
        self.openedButtons.add((x, y))
        mineCount = self.minesAround(x, y)
        log_string = f"Flood: {x}, {y}, buttonCount: {mineCount}"

        log_string += f" - Set: {MineColors[mineCount]}"
        NeoTrellisManager.setButtonColor(x, y, MineColors[mineCount])

        if mineCount > 0:
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
        self.gameState = GameState.Animating

        animCoords = []
        for x in range(NeoTrellisManagerClass.TRELLIS_WIDTH):
            for y in range(NeoTrellisManagerClass.TRELLIS_HEIGHT):
                if NeoTrellisManager.getButtonColor(x, y) == AdaColors.BLACK:
                    animCoords.append(Coord(x, y))

        winAnimation = ListDisco(animCoords, 0.5, AdaColors.BLACK, 30)
        winAnimation.SetAnimationComplete(self.buttonResetGame)
        AnimationManager.add(winAnimation)

    def createLossAnimation(self, x, y):
        self.gameState = GameState.Animating
        lossAnimation = Blink(x, y, 0.5, AdaColors.BLACK, AdaColors.RED, 30)
        lossAnimation.SetAnimationComplete(self.buttonResetGame)
        AnimationManager.add(lossAnimation)
        for x in range(NeoTrellisManagerClass.TRELLIS_WIDTH):
            for y in range(NeoTrellisManagerClass.TRELLIS_HEIGHT):
                if NeoTrellisManager.getButtonColor(x, y) == GroundColor:
                    NeoTrellisManager.setButtonColor(x, y, AdaColors.RED if self.mines[x][y] else AdaColors.BLACK)

    def buttonResetGame(self):
        self.gameState = GameState.WaitingForReset

    def Update(self):
        if SHOW_DIAGNOSTICS:
            log_string = f"Game State: {EnumName(GameState, self.gameState)}"
            if self.lastLogString != log_string:
                eng_logger.info(log_string)
                self.lastLogString = log_string

        TrellisGame.Update(self)
