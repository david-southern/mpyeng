import time
import adafruit_logging as logging
from card_reader import CardReader

from power_bus import PowerBus
from power_card import PowerCard

logger = logging.getLogger('main')

logger.setLevel(logging.INFO)

logger.info("Initializing PowerCards")
PowerCard.InitializePowerCards()
logger.info("Initializing PowerBuses")
PowerBus.InitializePowerBusses()

animationDelay = 0.1

while True:
    for bus in PowerBus.AllPowerBuses():
        bus.UpdateState()

    CardReader.ShowPixels()
    time.sleep(animationDelay)




