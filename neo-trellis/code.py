import time
from animation_manager import AnimationManager
from eng_utils import eng_logger
from adafruit_led_animation import color as AdaColors
from neotrellis_manager import NeoTrellisManager
from trellis_game_battleship import TrellisGameBattleship
from trellis_game_minesweeper import TrellisGameMinesweeper
from trellis_game_random import TrellisGameRandom
from trellis_game_selector import TrellisGameSelector
from trellis_game_base import TrellisGame

eng_logger.info("Starting NeoTrellis Game")

GAME_LOOP_SPEED = 0.02

gameSelector = TrellisGameSelector()

gameSelector.addGame("Minesweeper", 'M', AdaColors.OLD_LACE, TrellisGameMinesweeper)
gameSelector.addGame("Battleship", 'B', AdaColors.BLUE, TrellisGameBattleship)
gameSelector.addGame("Random", 'R', AdaColors.RED, TrellisGameRandom)

while gameSelector.selectedGameClass is None:
    gameSelector.Update()

gameClassName = gameSelector.selectedGameClass.__name__ # pyright: ignore

print(f"Selected Game: {gameClassName}")

NeoTrellisManager.fill(AdaColors.BLACK)

gameCons = globals()[gameClassName]
game: TrellisGame = gameCons()

while True:
    game.Update()
    AnimationManager.Update()
    time.sleep(GAME_LOOP_SPEED)