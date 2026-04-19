from machine import Pin

from utils.eng_utils import ENABLE_POWER_TRAY
from utils.device_manager import device_manager
from utils.pixel_strip_manager import PixelStripManager
from utils.profiling import register_profile, start_profile, stop_profile
from card_tray.constants import PIXEL_CARD_TRAYS, PIXEL_CARD_TRAY_TOTAL_LEDS
from card_tray.power_card_tray import PowerCardTray

PROFILE_TRAYS = register_profile("power_trays")


class PowerTrayManagerClass:
    def __init__(self):
        self.TestPowerCardTrays: list[PowerCardTray] = []
        self.RightPixelStrip: PixelStripManager | None = None

        if not ENABLE_POWER_TRAY:
            return

        strip_data_pin = Pin(device_manager.resolve_pin("power_tray", "strip_data", 12))

        self.RIGHT_STRIP_LED_COUNT = PIXEL_CARD_TRAY_TOTAL_LEDS * PIXEL_CARD_TRAYS
        self.RightPixelStrip = PixelStripManager(strip_data_pin, self.RIGHT_STRIP_LED_COUNT)
        self.TestPowerCardTrays = [
            PowerCardTray(tray_index, self.RightPixelStrip) for tray_index in range(PIXEL_CARD_TRAYS)
        ]

    def Update(self):
        if not ENABLE_POWER_TRAY:
            return

        start_profile(PROFILE_TRAYS)
        for tray in self.TestPowerCardTrays:
            tray.Update()
        self.RightPixelStrip.Update()  # pyright: ignore[reportOptionalMemberAccess]
        stop_profile(PROFILE_TRAYS)


PowerTrayManager = PowerTrayManagerClass()
