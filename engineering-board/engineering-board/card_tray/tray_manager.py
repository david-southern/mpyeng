from utils.eng_utils import register_timer, check_timer
from utils.device_manager import DeviceManager, PinNames, Systems
from utils.pixel_strip_manager import PixelStripManager
from utils.profiling import register_profile, start_profile, stop_profile
from card_tray.constants import CARD_TRAY_COUNT, CARD_TRAY_TOTAL_PIXELS
from card_tray.power_card_tray import PowerCardTray

CARD_ANIMATION_TARGET_FPS = 10
ANIMATION_UPDATE_FREQUENCY_SEC = 1.0 / CARD_ANIMATION_TARGET_FPS
TIMER_POWER_TRAY_UPDATE = "tray_update"


register_timer(TIMER_POWER_TRAY_UPDATE, ANIMATION_UPDATE_FREQUENCY_SEC)
PROFILE_TRAYS = register_profile(f"power_trays*{CARD_TRAY_COUNT}")

PROFILE_PSM = register_profile("psm_right")


class PowerTrayManagerClass:
    def __init__(self):
        self.TestPowerCardTrays: list[PowerCardTray] = []
        self.RightPixelStrip: PixelStripManager | None = None

        if not DeviceManager.IsEnabled(Systems.POWER_TRAY):
            return

        strip_data_pin = DeviceManager.ResolvePin(PinNames.Pixels.CARD_TRAY).Pin

        self.RIGHT_STRIP_LED_COUNT = CARD_TRAY_TOTAL_PIXELS * CARD_TRAY_COUNT
        self.RightPixelStrip = PixelStripManager(strip_data_pin, self.RIGHT_STRIP_LED_COUNT, PROFILE_PSM)
        self.TestPowerCardTrays = [
            PowerCardTray(tray_index, self.RightPixelStrip) for tray_index in range(CARD_TRAY_COUNT)
        ]

    def Update(self):
        if not DeviceManager.IsEnabled(Systems.POWER_TRAY):
            return

        if check_timer(TIMER_POWER_TRAY_UPDATE):
            start_profile(PROFILE_TRAYS)
            for tray in self.TestPowerCardTrays:
                tray.Update()
            self.RightPixelStrip.Update()  # pyright: ignore[reportOptionalMemberAccess]
            stop_profile(PROFILE_TRAYS)


PowerTrayManager = PowerTrayManagerClass()
