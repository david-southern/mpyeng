import random
import board
import digitalio
from adafruit_debouncer import Debouncer  # pyright: ignore[reportMissingImports]

from eng_utils import check_timer, register_timer, logger

from power_card_tray import CARD_TRAY_COLORS, TestPowerCardTrays
from power_display_manager import PowerDisplayManager
from protocol_resources import (
    LEFT_WING,
    RIGHT_WING,
    TRANS1,
    TRANS2,
    TRANS3,
    TRANS4,
    EnginePower,
    SystemPower,
    TransformerPower,
)
from power_grid_manager import PowerGridManager

DEMO_ENGINE_POWER_DATA = [
    EnginePower(LEFT_WING, 1500, 900),
    EnginePower(RIGHT_WING, 2000, 450),
]

DEMO_TRANSFORMER_POWER_DATA = [
    TransformerPower(TRANS1, 1500, 100),
    TransformerPower(TRANS2, 750, 500),
    TransformerPower(TRANS3, 1000, 700),
    TransformerPower(TRANS4, 500, 50),
]

DEMO_SYSTEM_POWER_DATA = [
    SystemPower("Thrusters", 50, 1),
    SystemPower("Warp", 110, 1),
    SystemPower("Shields", 60, 0),
    SystemPower("Phasers", 70, 8),
    SystemPower("Life Support", 30, 1),
]

RANDOM_POWER_UPDATE_FREQ = 1
TIMER_DEMO_DATA = "demo_data"

register_timer(TIMER_DEMO_DATA, RANDOM_POWER_UPDATE_FREQ)

ENABLE_TEST_BUTTONS = False

if ENABLE_TEST_BUTTONS:
    green_pin = digitalio.DigitalInOut(board.D4)
    green_pin.direction = digitalio.Direction.INPUT
    green_pin.pull = digitalio.Pull.UP
    warp_green = Debouncer(green_pin)

    yellow_pin = digitalio.DigitalInOut(board.D5)
    yellow_pin.direction = digitalio.Direction.INPUT
    yellow_pin.pull = digitalio.Pull.UP
    warp_yellow = Debouncer(yellow_pin)

    red_pin = digitalio.DigitalInOut(board.D6)
    red_pin.direction = digitalio.Direction.INPUT
    red_pin.pull = digitalio.Pull.UP
    warp_red = Debouncer(red_pin)

    blue_pin = digitalio.DigitalInOut(board.D13)
    blue_pin.direction = digitalio.Direction.INPUT
    blue_pin.pull = digitalio.Pull.UP
    shields = Debouncer(blue_pin, interval=0.1)


def set_warp_power(power: int):
    for power_resource in DEMO_SYSTEM_POWER_DATA:
        if power_resource.Name == "Warp":
            power_resource.Power = power
            power_resource.CardCount = int(power / 100)
            break

    logger.info(f"DEMOS: Warp Power to {power}")


def set_shield_power(power: int):
    for power_resource in DEMO_SYSTEM_POWER_DATA:
        if power_resource.Name == "Shields":
            power_resource.Power = power
            power_resource.CardCount = int(power / 50)
            break

    logger.info(f"DEMOS: Shield Power to {power}")


class DemoDataManager:
    __firstUpdate = True

    @staticmethod
    def update_demo_data():
        if ENABLE_TEST_BUTTONS:
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
                logger.info("DEMOS: Shield Power to 300")
                set_shield_power(300)

            if shields.rose:
                logger.info("DEMOS: Shield Power to 0")
                set_shield_power(0)
        else:
            if not check_timer(TIMER_DEMO_DATA):
                return

            if DemoDataManager.__firstUpdate:
                DemoDataManager.__firstUpdate = False
                for _, wing in enumerate(DEMO_ENGINE_POWER_DATA):
                    PowerGridManager.SetWingMaxPower(wing.Name, wing.MaxPower)
                    PowerDisplayManager.SetDisplayValue(wing.Name, wing.MaxPower)

                for _, transformer in enumerate(DEMO_TRANSFORMER_POWER_DATA):
                    PowerGridManager.SetTransformerMaxPower(
                        transformer.Name, transformer.MaxPower
                    )
                    PowerDisplayManager.SetDisplayMaxValue(
                        transformer.Name, transformer.MaxPower
                    )

            for tray in TestPowerCardTrays:
                tray.PowerState = random.choice(list(CARD_TRAY_COLORS.keys()))

            for power_resource in DEMO_ENGINE_POWER_DATA:
                power_resource.PowerUsage = random.randint(0, power_resource.MaxPower)
                PowerGridManager.SetWingTargetPower(
                    power_resource.Name, power_resource.PowerUsage
                )

            for power_resource in DEMO_TRANSFORMER_POWER_DATA:
                power_resource.PowerUsage = random.randint(0, power_resource.MaxPower)
                PowerGridManager.SetTransformerTargetPower(
                    power_resource.Name, power_resource.PowerUsage
                )
                PowerDisplayManager.SetDisplayCurValue(
                    power_resource.Name, power_resource.PowerUsage
                )

            for power_resource in DEMO_SYSTEM_POWER_DATA:
                power_resource.CardCount = random.randint(1, 5)

    @staticmethod
    def GetEnginePowerData():
        return DEMO_ENGINE_POWER_DATA

    @staticmethod
    def ClearEnginePowerData():
        DEMO_ENGINE_POWER_DATA.clear()

    @staticmethod
    def AddEnginePowerResource(power_resource: EnginePower):
        DEMO_ENGINE_POWER_DATA.append(power_resource)

    @staticmethod
    def GetTransformerPowerData():
        return DEMO_TRANSFORMER_POWER_DATA

    @staticmethod
    def ClearTransformerPowerData():
        DEMO_TRANSFORMER_POWER_DATA.clear()

    @staticmethod
    def AddTransformerPowerResource(power_resource: TransformerPower):
        DEMO_TRANSFORMER_POWER_DATA.append(power_resource)

    @staticmethod
    def GetSystemPowerData():
        return DEMO_SYSTEM_POWER_DATA

    @staticmethod
    def ClearSystemPowerData():
        DEMO_SYSTEM_POWER_DATA.clear()

    @staticmethod
    def AddSystemPowerResource(power_resource: SystemPower):
        DEMO_SYSTEM_POWER_DATA.append(power_resource)
