from machine import unique_id, PinLike  # pyright: ignore[reportMissingImports]
from utils.eng_utils import logger, set_flags


class DeviceConfiguration:
    """Immutable Structured configuration for a known device."""

    def __init__(
        self,
        name: str,
        functionality_flags: dict[str, bool],
        pin_reservations: dict[str, list[PinLike]],
    ):
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "functionality_flags", functionality_flags)
        object.__setattr__(self, "pin_reservations", pin_reservations)

    @property
    def Name(self) -> str:
        """Get the human-readable name of the device."""
        return getattr(self, "name", "Unknown")

    @property
    def FunctionalityFlags(self) -> dict[str, bool]:
        """Get the functionality flags for this device."""
        return getattr(self, "functionality_flags", {})

    @property
    def PinReservations(self) -> dict[str, list[PinLike]]:
        """Get the pin reservations for this device."""
        return getattr(self, "pin_reservations", {})

    def __setattr__(self, name: str, value) -> None:
        raise AttributeError("DeviceConfiguration is immutable and cannot be modified after creation.")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("DeviceConfiguration is immutable and cannot be modified after creation.")


class DeviceManagerClass:
    """Identifies the device by unique ID and configures module enable flags."""

    KNOWN_DEVICES: dict[str, DeviceConfiguration] = {
        "F412FA59B3E0": DeviceConfiguration(
            name="Feather ESP32-S3 TFT",
            functionality_flags={
                "ENABLE_PIXELS": True,
                "ENABLE_SLOW_LOG": True,
            },
            pin_reservations={
                "neopixel_strip": [12],
                "seven_seg": [2, 3],
                "spi_sck": [36],
                "spi_mosi": [35],
                "spi_miso": [37],
                "cs_pins": [9, 10, 11, 12],
                "switchboard_left_wing_source": [],
                "switchboard_right_wing_source": [],
                "switchboard_dist1_sink": [],
                "switchboard_dist1_source": [],
                "switchboard_bus1_sink": [],
            },
        )
    }

    def __init__(self):
        raw_id = unique_id()
        self.DEVICE_ID = "".join(f"{byte:02X}" for byte in raw_id)
        logger.info(f"DeviceManager: checking device ID: '{self.DEVICE_ID}' against KNOWN_DEVICES")

        if self.DEVICE_ID in self.KNOWN_DEVICES:
            self.DEVICE_CONFIGURATION = self.KNOWN_DEVICES[self.DEVICE_ID]
            self.DEVICE_RECOGNIZED = True
            set_flags(self.DEVICE_CONFIGURATION.FunctionalityFlags)
            logger.info(f"DeviceManager: Recognized device '{self.DEVICE_CONFIGURATION.Name}' (ID: {self.DEVICE_ID})")
        else:
            self.DEVICE_RECOGNIZED = False
            logger.error(f"DeviceManager: Unrecognized device ID: {self.DEVICE_ID}. No modules enabled.")

    def IsEnabled(self, flag_name: str) -> bool:
        """Check if a functionality flag is enabled for this device."""
        return self.DEVICE_CONFIGURATION.FunctionalityFlags.get(flag_name, False)

    def ModulePins(self, module_name: str) -> list[PinLike]:
        """Get the list of pins reserved for a specific module."""
        return self.DEVICE_CONFIGURATION.PinReservations.get(module_name, [])


DeviceManager = DeviceManagerClass()
