from machine import unique_id  # pyright: ignore[reportMissingImports]

import utils.eng_utils as eng_utils


class DeviceManager:
    """Identifies the device by unique ID and configures module enable flags."""

    KNOWN_DEVICES = {
        "F412FA59B3E0": (
            "Feather ESP32-S3 TFT",
            {
                "ENABLE_PROTOCOL_MANAGER": False,
                "ENABLE_POWER_DISPLAY": False,
                "ENABLE_PIXELS": True,
                "ENABLE_CARD_READER": False,
                "ENABLE_POWER_GRID": False,
                "ENABLE_SWITCHBOARD": False,
                "ENABLE_LEFT_SWITCHBOARD": False,
                "ENABLE_RIGHT_SWITCHBOARD": False,
                "ENABLE_LEFT_PIXELS": False,
                "ENABLE_RIGHT_PIXELS": True,
                "ENABLE_POWER_TRAY": True,
            },
            {
                "power_tray": {
                    "strip_data": 12,
                },
                "power_grid": {
                    "strip_data": 5,
                },
                "power_display": {
                    "displays": [
                        (2, 3),
                        (4, 5),
                        (6, 7),
                        (8, 9),
                        (10, 11),
                        (12, 13),
                        (14, 15),
                        (16, 17),
                        (18, 19),
                        (20, 22),
                    ],
                },
                "card_reader": {
                    "spi_id": 2,
                    "spi_sck": 18,
                    "spi_mosi": 19,
                    "spi_miso": 16,
                    "cs_pins": [9, 10, 11, 12],
                },
                "switchboard": {
                    "left_sources": [
                        (1, "EngineTop", 22),
                        (2, "EngineBottom", 42),
                    ],
                    "left_sinks": [
                        (3, "Dist1_In", 24),
                        (4, "Dist2_In", 23),
                        (5, "Dist3_In", 44),
                        (6, "Dist4_In", 43),
                    ],
                    "right_sources": [
                        (7, "Dist1_Out", 38),
                        (8, "Dist1_Out", 39),
                        (9, "Dist1_Out", 40),
                        (10, "Dist1_Out", 41),
                    ],
                    "right_sinks": [
                        (11, "Bus1", 42),
                        (12, "Bus2", 43),
                        (13, "Bus3", 44),
                        (14, "Bus4", 45),
                        (15, "Bus5", 46),
                        (16, "Bus6", 47),
                    ],
                },
            },
        ),
    }

    def __init__(self):
        raw_id = unique_id()
        self.device_id = "".join(f"{byte:02X}" for byte in raw_id)
        self._pins: dict = {}

        if self.device_id in self.KNOWN_DEVICES:
            self.device_name, flags, self._pins = self.KNOWN_DEVICES[self.device_id]
            self.device_recognized = True
            for flag_name, flag_value in flags.items():
                setattr(eng_utils, flag_name, flag_value)
            eng_utils.logger.info(f"DeviceManager: Recognized device '{self.device_name}' (ID: {self.device_id})")
        else:
            self.device_name = "Unknown"
            self.device_recognized = False
            eng_utils.logger.error(f"DeviceManager: Unrecognized device ID: {self.device_id}. No modules enabled.")

    def resolve_pin(self, module: str, key: str, default=None):
        """Resolve a pin configuration value for a module.

        Args:
            module: The module name key (e.g. "power_tray", "card_reader").
            key: The pin config key within that module (e.g. "strip_data", "cs_pins").
            default: Fallback value if the module or key is not defined.

        Returns:
            The configured value, or default if not found.
        """
        return self._pins.get(module, {}).get(key, default)


device_manager = DeviceManager()
