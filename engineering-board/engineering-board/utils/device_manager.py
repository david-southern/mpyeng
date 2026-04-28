# pyright: reportAttributeAccessIssue=false

from machine import unique_id  # pyright: ignore[reportMissingImports]
from drivers.named_pin import NamedPin
from utils.eng_utils import logger, set_flags


class Boards:
    RP2350_PICO2_W = "RP2350 Pico2 W"
    FEATHER_ESP32_S3_TFT = "Feather ESP32-S3 TFT"


class Systems:
    PROTOCOL_MANAGER = "ProtocolManager"
    # FYI: Running the TM1637 displays when the board is does not have an external +5V supply causes the
    # Arduino to crash erratically. Not sure why, but it definitely happens. Providing the external +5V
    # supply stops this happening.
    POWER_DISPLAY = "PowerDisplays"
    CARD_READER = "CardReaders"
    POWER_GRID = "PowerGrids"
    ANY_SWITCHBOARD = "Switchboard"
    LEFT_SWITCHBOARD = "LeftSwitchboards"
    RIGHT_SWITCHBOARD = "RightSwitchboards"
    ANY_PIXEL_STRIP = "PixelStrip"
    LEFT_PIXELS = "LeftPixels"
    RIGHT_PIXELS = "RightPixels"
    POWER_TRAY = "PowerTrays"


class PinNames:
    class Pixels:
        POWER_GRID = "pixels.power_grid"
        CARD_TRAY = "pixels.card_tray"

    class PowerDisplays:
        class Max:
            class Clock:
                LEFT_WING = "power_display.max.clock.left_wing"
                RIGHT_WING = "power_display.max.clock.right_wing"
                TRANS1 = "power_display.max.clock.trans1"
                TRANS2 = "power_display.max.clock.trans2"
                TRANS3 = "power_display.max.clock.trans3"
                TRANS4 = "power_display.max.clock.trans4"
                BUS1 = "power_display.max.clock.bus1"
                BUS2 = "power_display.max.clock.bus2"
                BUS3 = "power_display.max.clock.bus3"
                BUS4 = "power_display.max.clock.bus4"
                BUS5 = "power_display.max.clock.bus5"
                BUS6 = "power_display.max.clock.bus6"

            class Data:
                LEFT_WING = "power_display.max.data.left_wing"
                RIGHT_WING = "power_display.max.data.right_wing"
                TRANS1 = "power_display.max.data.trans1"
                TRANS2 = "power_display.max.data.trans2"
                TRANS3 = "power_display.max.data.trans3"
                TRANS4 = "power_display.max.data.trans4"
                BUS1 = "power_display.max.data.bus1"
                BUS2 = "power_display.max.data.bus2"
                BUS3 = "power_display.max.data.bus3"
                BUS4 = "power_display.max.data.bus4"
                BUS5 = "power_display.max.data.bus5"
                BUS6 = "power_display.max.data.bus6"

        class Current:
            class Clock:
                TRANS1 = "power_display.current.clock.trans1"
                TRANS2 = "power_display.current.clock.trans2"
                TRANS3 = "power_display.current.clock.trans3"
                TRANS4 = "power_display.current.clock.trans4"
                BUS1 = "power_display.current.clock.bus1"
                BUS2 = "power_display.current.clock.bus2"
                BUS3 = "power_display.current.clock.bus3"
                BUS4 = "power_display.current.clock.bus4"
                BUS5 = "power_display.current.clock.bus5"
                BUS6 = "power_display.current.clock.bus6"

            class Data:
                TRANS1 = "power_display.current.data.trans1"
                TRANS2 = "power_display.current.data.trans2"
                TRANS3 = "power_display.current.data.trans3"
                TRANS4 = "power_display.current.data.trans4"
                BUS1 = "power_display.current.data.bus1"
                BUS2 = "power_display.current.data.bus2"
                BUS3 = "power_display.current.data.bus3"
                BUS4 = "power_display.current.data.bus4"
                BUS5 = "power_display.current.data.bus5"
                BUS6 = "power_display.current.data.bus6"

    class CardReader:
        SPI = "card_reader.spi"
        SPI_CLK = "card_reader.spi_sck"
        SPI_MOSI = "card_reader.spi_mosi"
        SPI_MISO = "card_reader.spi_miso"
        SPI_CS_MCP1 = "card_reader.mcp1.spi_cs"
        SPI_CS_MCP2 = "card_reader.mcp2.spi_cs"
        SPI_CS_MCP3 = "card_reader.mcp3.spi_cs"
        SPI_CS_MCP4 = "card_reader.mcp4.spi_cs"

    class Switchboard:
        class Sources:
            LEFT_WING = "switchboard.source.left_wing"
            RIGHT_WING = "switchboard.source.right_wing"
            TRANS1 = "switchboard.source.trans1"
            TRANS2 = "switchboard.source.trans2"
            TRANS3 = "switchboard.source.trans3"
            TRANS4 = "switchboard.source.trans4"

        class Sinks:
            TRANS1 = "switchboard.sink.trans1"
            TRANS2 = "switchboard.sink.trans2"
            TRANS3 = "switchboard.sink.trans3"
            TRANS4 = "switchboard.sink.trans4"
            BUS1 = "switchboard.sink.bus1"
            BUS2 = "switchboard.sink.bus2"
            BUS3 = "switchboard.sink.bus3"
            BUS4 = "switchboard.sink.bus4"
            BUS5 = "switchboard.sink.bus5"
            BUS6 = "switchboard.sink.bus6"


class DeviceConfiguration:
    """Immutable Structured configuration for a known device."""

    def __init__(
        self,
        name: str,
        system_flags: dict[str, bool],
        pin_reservations: dict[str, NamedPin],
    ):
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "system_flags", system_flags)
        object.__setattr__(self, "pin_reservations", pin_reservations)

    @property
    def Name(self) -> str:
        """Get the human-readable name of the device."""
        return getattr(self, "name", "Unknown")

    @property
    def SystemFlags(self) -> dict[str, bool]:
        """Get the system flags for this device."""
        return getattr(self, "system_flags", {})

    @property
    def PinReservations(self) -> dict[str, NamedPin]:
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
            name=Boards.FEATHER_ESP32_S3_TFT,
            system_flags={
                Systems.RIGHT_PIXELS: True,
                Systems.POWER_TRAY: True,
            },
            pin_reservations={
                PinNames.Pixels.CARD_TRAY: NamedPin("GP16"),
            },
        ),
        "B29EF8BE7E93C6C6": DeviceConfiguration(
            name=Boards.RP2350_PICO2_W,
            system_flags={
                Systems.RIGHT_PIXELS: True,
                Systems.POWER_TRAY: True,
            },
            pin_reservations={
                PinNames.Pixels.CARD_TRAY: NamedPin("GP16"),  # NamedPin("GP26"),
                # These SPI pin values come from the REPL: import machine; spi = machine.SPI(0):
                # sck=18, mosi=19, miso=16
                PinNames.CardReader.SPI_CLK: NamedPin("GP18"),
                PinNames.CardReader.SPI_MOSI: NamedPin("GP19"),
                PinNames.CardReader.SPI_MISO: NamedPin("GP16"),
                PinNames.CardReader.SPI_CS_MCP1: NamedPin("GP17"),
                PinNames.CardReader.SPI_CS_MCP2: NamedPin("GP20"),
                PinNames.CardReader.SPI_CS_MCP3: NamedPin("GP21"),
                PinNames.CardReader.SPI_CS_MCP4: NamedPin("GP22"),
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
            set_flags(self.DEVICE_CONFIGURATION.SystemFlags)
            logger.info(f"DeviceManager: Recognized device '{self.DEVICE_CONFIGURATION.Name}' (ID: {self.DEVICE_ID})")
        else:
            self.DEVICE_RECOGNIZED = False
            logger.error(f"DeviceManager: Unrecognized device ID: {self.DEVICE_ID}. No modules enabled.")
            return

        # Raise an error if they have included a ANY_* system flag, as this is only for checking
        # groups of systems, not for actual configuration
        for system_name in self.DEVICE_CONFIGURATION.SystemFlags.keys():
            if system_name.startswith("ANY_"):
                logger.error(
                    f"DeviceManager: Device '{self.DEVICE_CONFIGURATION.Name}' has invalid system flag '{system_name}'. Do not set Group System flags in the Device Configuration. Set the individual component system flags instead."
                )

        # make sure that all pins reserved for this device are unique and not duplicated across different pin names
        reserved_pins = [pin.Name for pin in self.DEVICE_CONFIGURATION.PinReservations.values()]
        duplicate_pin_names = set(pin_name for pin_name in reserved_pins if reserved_pins.count(pin_name) > 1)
        if duplicate_pin_names:
            logger.error(
                f"DeviceManager: Device '{self.DEVICE_CONFIGURATION.Name}' "
                + f"has duplicate pin reservations: {', '.join(duplicate_pin_names)}. "
                + "Each pin can only be reserved for one function."
            )

        # Now set the ANY_ systems to be the OR of their component system flags
        self.DEVICE_CONFIGURATION.SystemFlags[Systems.ANY_SWITCHBOARDS] = self.IsEnabled(
            Systems.LEFT_SWITCHBOARD
        ) or self.IsEnabled(Systems.RIGHT_SWITCHBOARD)

        self.DEVICE_CONFIGURATION.SystemFlags[Systems.ANY_PIXELS] = self.IsEnabled(
            Systems.LEFT_PIXELS
        ) or self.IsEnabled(Systems.RIGHT_PIXELS)

    def IsEnabled(self, system_name: str) -> bool:
        """Check if a system flag is enabled for this device."""
        return self.DEVICE_CONFIGURATION.SystemFlags.get(system_name, False)

    def SystemName(self, system_name: str) -> str:
        """Get the human-readable name of a system flag."""
        return f"{'' if self.IsEnabled(system_name) else 'Disabled'}{system_name}"

    def ResolvePin(self, pin_name: str) -> NamedPin:
        """Get the pin reserved for a specific name."""
        result = self.DEVICE_CONFIGURATION.PinReservations.get(pin_name)
        if result is None:
            raise KeyError(
                f"DeviceManager: Pin name '{pin_name}' is not reserved for device '{self.DEVICE_CONFIGURATION.Name}'."
            )
        return result


DeviceManager = DeviceManagerClass()
