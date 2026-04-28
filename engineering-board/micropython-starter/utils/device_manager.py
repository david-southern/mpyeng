# pyright: reportAttributeAccessIssue=false

from machine import unique_id, Pin  # pyright: ignore[reportMissingImports]
from utils.eng_utils import logger, set_flags


class DeviceConfiguration:
    class PinNames:
        RIGHT_NEOPIXEL = "right_neopixel_strip"
        SEVEN_SEG_DATA = "seven_seg_data"
        SEVEN_SEG_CLK = "seven_seg_clk"
        SPI_CLK = "spi_sck"
        SPI_MOSI = "spi_mosi"
        SPI_MISO = "spi_miso"
        SPI_CS = "spi_cs"
        LEFT_WING_SOURCE = "switchboard_left_wing_source"
        RIGHT_WING_SOURCE = "switchboard_right_wing_source"
        DIST1_SINK = "switchboard_dist1_sink"
        DIST1_SOURCE = "switchboard_dist1_source"
        BUS1_SINK = "switchboard_bus1_sink"

    """Immutable Structured configuration for a known device."""

    def __init__(
        self,
        name: str,
        functionality_flags: dict[str, bool],
        pin_reservations: dict[str, Pin],
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
    def PinReservations(self) -> dict[str, Pin]:
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
                DeviceConfiguration.PinNames.RIGHT_NEOPIXEL: Pin.board.GP16,
                DeviceConfiguration.PinNames.SEVEN_SEG_DATA: Pin.board.GP1,
                DeviceConfiguration.PinNames.SEVEN_SEG_CLK: Pin.board.GP1,
                DeviceConfiguration.PinNames.SPI_CLK: Pin.board.GP1,
                DeviceConfiguration.PinNames.SPI_MOSI: Pin.board.GP1,
                DeviceConfiguration.PinNames.SPI_MISO: Pin.board.GP1,
                DeviceConfiguration.PinNames.SPI_CS: Pin.board.GP1,
                DeviceConfiguration.PinNames.LEFT_WING_SOURCE: Pin.board.GP1,
                DeviceConfiguration.PinNames.RIGHT_WING_SOURCE: Pin.board.GP1,
                DeviceConfiguration.PinNames.DIST1_SINK: Pin.board.GP1,
                DeviceConfiguration.PinNames.DIST1_SOURCE: Pin.board.GP1,
                DeviceConfiguration.PinNames.BUS1_SINK: Pin.board.GP1,
            },
        ),
        "B29EF8BE7E93C6C6": DeviceConfiguration(
            name="RP2350 Pico W",
            functionality_flags={
                "ENABLE_PIXELS": True,
                "ENABLE_SLOW_LOG": True,
            },
            pin_reservations={
                DeviceConfiguration.PinNames.RIGHT_NEOPIXEL: Pin.board.GP16,
                DeviceConfiguration.PinNames.SEVEN_SEG_DATA: Pin.board.GP1,
                DeviceConfiguration.PinNames.SEVEN_SEG_CLK: Pin.board.GP1,
                DeviceConfiguration.PinNames.SPI_CLK: Pin.board.GP1,
                DeviceConfiguration.PinNames.SPI_MOSI: Pin.board.GP1,
                DeviceConfiguration.PinNames.SPI_MISO: Pin.board.GP1,
                DeviceConfiguration.PinNames.SPI_CS: Pin.board.GP1,
                DeviceConfiguration.PinNames.LEFT_WING_SOURCE: Pin.board.GP1,
                DeviceConfiguration.PinNames.RIGHT_WING_SOURCE: Pin.board.GP1,
                DeviceConfiguration.PinNames.DIST1_SINK: Pin.board.GP1,
                DeviceConfiguration.PinNames.DIST1_SOURCE: Pin.board.GP1,
                DeviceConfiguration.PinNames.BUS1_SINK: Pin.board.GP1,
            },
        ),
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

    def ModulePins(self, module_name: str) -> Pin | None:
        """Get the pin reserved for a specific module."""
        return self.DEVICE_CONFIGURATION.PinReservations.get(module_name, None)


DeviceManager = DeviceManagerClass()
