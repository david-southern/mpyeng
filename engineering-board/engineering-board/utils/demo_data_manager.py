import random
import time
from machine import Pin
from utils.device_manager import DeviceManager, Systems
from utils.eng_utils import (
    check_timer,
    register_timer,
    logger,
)

if DeviceManager.IsEnabled(Systems.POWER_DISPLAY):
    from power_display.display_manager import PowerDisplayManager

from utils.protocol_resources import (
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

if DeviceManager.IsEnabled(Systems.POWER_GRID):
    from power_grid.grid_manager import PowerGridManager


class Debouncer:
    """Minimal debounce wrapper for a MicroPython machine.Pin."""

    def __init__(self, pin: Pin, interval: float = 0.05):
        self._pin = pin
        self._interval_ms = int(interval * 1000)
        self._state = pin.value()
        self._last_change = time.ticks_ms()
        self.fell = False
        self.rose = False

    def update(self):
        """Must be called regularly to update the debounced state."""
        self.fell = False
        self.rose = False
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_change) < self._interval_ms:
            return
        new_state = self._pin.value()
        if new_state != self._state:
            self._last_change = now
            if new_state == 0:
                self.fell = True
            else:
                self.rose = True
            self._state = new_state


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

TEST_BUTTONS = False

if TEST_BUTTONS:
    warp_green = Debouncer(Pin(4, Pin.IN, Pin.PULL_UP))  # TODO: verify GP4 for ESP32-S3 wiring
    warp_yellow = Debouncer(Pin(5, Pin.IN, Pin.PULL_UP))  # TODO: verify GP5 for ESP32-S3 wiring
    warp_red = Debouncer(Pin(6, Pin.IN, Pin.PULL_UP))  # TODO: verify GP6 for ESP32-S3 wiring
    shields = Debouncer(Pin(13, Pin.IN, Pin.PULL_UP), interval=0.1)  # TODO: verify GP13 for ESP32-S3 wiring


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


class DemoDataManagerClass:
    __firstUpdate = True

    @staticmethod
    def update_demo_data():
        if TEST_BUTTONS:
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
                    if DeviceManager.IsEnabled(Systems.POWER_GRID):
                        PowerGridManager.SetWingMaxPower(wing.Name, wing.MaxPower)
                    if DeviceManager.IsEnabled(Systems.POWER_DISPLAY):
                        PowerDisplayManager.SetDisplayValue(wing.Name, wing.MaxPower)

                for _, transformer in enumerate(DEMO_TRANSFORMER_POWER_DATA):
                    if DeviceManager.IsEnabled(Systems.POWER_GRID):
                        PowerGridManager.SetTransformerMaxPower(transformer.Name, transformer.MaxPower)
                    if DeviceManager.IsEnabled(Systems.POWER_DISPLAY):
                        PowerDisplayManager.SetDisplayMaxValue(transformer.Name, transformer.MaxPower)

            for power_resource in DEMO_ENGINE_POWER_DATA:
                power_resource.PowerUsage = random.randint(0, power_resource.MaxPower)
                if DeviceManager.IsEnabled(Systems.POWER_GRID):
                    PowerGridManager.SetWingTargetPower(power_resource.Name, power_resource.PowerUsage)

            for power_resource in DEMO_TRANSFORMER_POWER_DATA:
                power_resource.PowerUsage = random.randint(0, power_resource.MaxPower)
                if DeviceManager.IsEnabled(Systems.POWER_GRID):
                    PowerGridManager.SetTransformerTargetPower(power_resource.Name, power_resource.PowerUsage)
                if DeviceManager.IsEnabled(Systems.POWER_DISPLAY):
                    PowerDisplayManager.SetDisplayCurValue(power_resource.Name, power_resource.PowerUsage)

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


DemoDataManager = DemoDataManagerClass()
