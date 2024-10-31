from eng_utils import logger
import board
import digitalio
from adafruit_debouncer import Debouncer  # type: ignore # pylint: disable=import-error

from protocol_resources import EnginePower, SystemPower, TransformerPower

FAKE_ENGINE_POWER_DATA = [
    EnginePower("Left Wing", 1500, 900),
    EnginePower("Right Wing", 2000, 450),
]

FAKE_TRANSFORMER_POWER_DATA = [
    TransformerPower("T1", 1500, 100),
    TransformerPower("T2", 750, 500),
    TransformerPower("T3", 1000, 700),
    TransformerPower("T4", 500, 50),
]

FAKE_SYSTEM_POWER_DATA = [
    SystemPower("Thrusters", 100, 1),
    SystemPower("Warp", 100, 1),
    SystemPower("Shields", 0, 0),
    SystemPower("Phasers", 400, 8),
    SystemPower("Life Support", 50, 1),
]


green_pin = digitalio.DigitalInOut(board.D11)
green_pin.direction = digitalio.Direction.INPUT
green_pin.pull = digitalio.Pull.UP
warp_green = Debouncer(green_pin)

yellow_pin = digitalio.DigitalInOut(board.D10)
yellow_pin.direction = digitalio.Direction.INPUT
yellow_pin.pull = digitalio.Pull.UP
warp_yellow = Debouncer(yellow_pin)

red_pin = digitalio.DigitalInOut(board.D9)
red_pin.direction = digitalio.Direction.INPUT
red_pin.pull = digitalio.Pull.UP
warp_red = Debouncer(red_pin)

blue_pin = digitalio.DigitalInOut(board.D7)
blue_pin.direction = digitalio.Direction.INPUT
blue_pin.pull = digitalio.Pull.UP
shields = Debouncer(blue_pin, interval=0.1)


def set_warp_power(power: int):
    for power_resource in FAKE_SYSTEM_POWER_DATA:
        if power_resource.Name == "Warp":
            power_resource.Power = power
            power_resource.CardCount = int(power / 100)
            break

    logger.info(f"FAKES: Warp Power to {power}")


def set_shield_power(power: int):
    for power_resource in FAKE_SYSTEM_POWER_DATA:
        if power_resource.Name == "Shields":
            power_resource.Power = power
            power_resource.CardCount = int(power / 50)
            break

    logger.info(f"FAKES: Shield Power to {power}")


class FakeDataManager:
    @staticmethod
    def update_fake_data():
        warp_green.update()
        warp_yellow.update()
        warp_red.update()
        shields.update()

        if warp_green.fell:
            set_warp_power(100)

        if warp_yellow.fell:
            set_warp_power(500)

        if warp_red.fell:
            set_warp_power(800)

        if shields.fell:
            logger.info("FAKES: Shield Power to 300")
            set_shield_power(300)

        if shields.rose:
            logger.info("FAKES: Shield Power to 0")
            set_shield_power(0)

        # for power_resource in FAKE_ENGINE_POWER_DATA:
        #     power_resource.PowerUsage = power_resource.PowerUsage + 1
        #     if power_resource.PowerUsage > power_resource.MaxPower:
        #         power_resource.PowerUsage = 0

        # for power_resource in FAKE_TRANSFORMER_POWER_DATA:
        #     power_resource.PowerUsage = power_resource.PowerUsage + 1
        #     if power_resource.PowerUsage > power_resource.MaxPower:
        #         power_resource.PowerUsage = 0

        # for power_resource in FAKE_SYSTEM_POWER_DATA:
        #     power_resource.Power = power_resource.Power + 1
        #     if power_resource.Power > 1000:
        #         power_resource.Power = 0

    @staticmethod
    def GetEnginePowerData():
        return FAKE_ENGINE_POWER_DATA

    @staticmethod
    def ClearEnginePowerData():
        FAKE_ENGINE_POWER_DATA.clear()

    @staticmethod
    def AddEnginePowerResource(power_resource: EnginePower):
        FAKE_ENGINE_POWER_DATA.append(power_resource)

    @staticmethod
    def GetTransformerPowerData():
        return FAKE_TRANSFORMER_POWER_DATA

    @staticmethod
    def ClearTransformerPowerData():
        FAKE_TRANSFORMER_POWER_DATA.clear()

    @staticmethod
    def AddTransformerPowerResource(power_resource: TransformerPower):
        FAKE_TRANSFORMER_POWER_DATA.append(power_resource)

    @staticmethod
    def GetSystemPowerData():
        return FAKE_SYSTEM_POWER_DATA

    @staticmethod
    def ClearSystemPowerData():
        FAKE_SYSTEM_POWER_DATA.clear()

    @staticmethod
    def AddSystemPowerResource(power_resource: SystemPower):
        FAKE_SYSTEM_POWER_DATA.append(power_resource)
