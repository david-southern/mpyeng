import time
import board
import adafruit_logging as logging
from analogio import AnalogIn
from card_reader import CardReader
from power_display import PowerDisplay
from utils import BLUE, GREEN, RED, YELLOW

DIAGS_INTERVAL = 1

_ALL_POWER_BUSES: list["PowerBus"] = []

logger = logging.getLogger('PowerBus')

class PowerBus:
    @classmethod
    def InitializePowerBusses(cls):
        global _ALL_POWER_BUSES
        _ALL_POWER_BUSES = []
        # disp1 = 

        _ALL_POWER_BUSES.append(PowerBus(1, board.D31, PowerDisplay(1, board.D9, board.D8, "Bus1"), [
            CardReader(1, board.A1), 
            CardReader(2, board.A2),
            CardReader(3, board.A3),
            CardReader(4, board.A4),
            CardReader(5, board.A5)
        ]))

        _ALL_POWER_BUSES.append(PowerBus(2, board.D32, PowerDisplay(2, board.D11, board.D10, "Bus2"), [
            CardReader(6, board.A6),
            CardReader(7, board.A7),
            CardReader(8, board.A8),
            CardReader(9, board.A9),
            CardReader(10, board.A10)            
        ]))

    @classmethod
    def AllPowerBuses(cls) -> list["PowerBus"]:
        return _ALL_POWER_BUSES

    def __init__(self, uid, inputPin, display:PowerDisplay, readers:list[CardReader]):
        self.uid = uid
        self.inputPin = inputPin
        self.display = display
        self.powerAvailable = 100
        self.overloadPower = 140
        self.nextDiags = time.monotonic() + DIAGS_INTERVAL

        if readers is None or len(readers) != 5:
            raise Exception(
                f"PowerBus({self}): invalid reader collection")

        self.readers = readers

        duplicates = [
            bus for bus in _ALL_POWER_BUSES if bus.UID == uid]

        if(len(duplicates) > 0):
            raise Exception(
                f"PowerBus({self}): duplicate UID with bus {duplicates[0]}")

        overlaps = [
            bus for bus in _ALL_POWER_BUSES if bus.InputPin == self.InputPin]
        if(len(overlaps) > 0):
            raise Exception(
                f"PowerBus({self}): input pin overlaps with bus {overlaps[0]}")

        logger.info(f"Created PowerBus: {self}")

        self.lastState = None

        for reader in readers:
            reader.LEDColor = BLUE

    @property
    def UID(self):
        return self.uid

    @property
    def InputPin(self):
        return self.inputPin

    @property
    def PowerAvailable(self):
        return self.powerAvailable

    @PowerAvailable.setter
    def PowerAvailable(self, value):
        self.powerAvailable = value

    @property
    def OverloadPower(self):
        return self.overloadPower

    @OverloadPower.setter
    def OverloadPower(self, value):
        self.overloadPower = value

    def UpdateState(self):
        showDiags = False

        if time.monotonic() > self.nextDiags:
            showDiags = True
            self.nextDiags = time.monotonic() + DIAGS_INTERVAL

        requestedPower = 0

        cardDiag = []

        for reader in self.readers:
            curCard = reader.CardPresent

            if(curCard is not None):
                cardDiag.append(curCard.CardName)
                requestedPower += curCard.RequiredPower

        cardString = ", ".join(cardDiag)

        if(requestedPower >= self.OverloadPower):
            for reader in self.readers:
                reader.LEDColor = RED

            self.display.Value = "dead"

        else:
            self.display.Value = min(self.PowerAvailable, requestedPower)

        allocatedPower = 0

        for reader in self.readers:
            curCard = reader.CardPresent

            if(curCard is None):
                reader.LEDColor = BLUE
                continue

            allocatedPower += curCard.RequiredPower

            reader.LEDColor = GREEN if allocatedPower <= self.PowerAvailable else YELLOW

        if(self.lastState != cardString):
            logger.info(f"{self}: power: {requestedPower} requested / {self.PowerAvailable} ({cardString})")
            self.lastState = cardString

    def __str__(self):
        return f"{self.UID}"
