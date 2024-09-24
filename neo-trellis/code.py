import time
from eng_utils import eng_logger
from trellis_game_battleship import TrellisGameBattleship
from trellis_game_random import TrellisGameRandom

eng_logger.info("Starting NeoTrellis Game")

game = TrellisGameBattleship()
# game = TrellisGameRandom()

while True:
    game.Update()
    # The NeoTrellis can only be read every 17 milliseconds or so
    time.sleep(0.02)