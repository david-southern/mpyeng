import array

from power_cards.card_ids import PowerCardIds
from utils.color_utils import to_neo_packed
from utils.profiling import log_free_ram

log_free_ram("pre-animation-baking")

ANIMATION_BRIGHTNESS = 0.15

CARD_WIDTH = 8
CARD_HEIGHT = 8
CARD_GRID_PIXELS = CARD_WIDTH * CARD_HEIGHT

# Globally shared palette LUT (regenerated when brightness changes)
GLOBAL_PALETTE_LOOKUP = [0] * 256
GLOBAL_PALETTE_BRIGHTNESS: float = -1.0


class CardAnimationHelpers:
    PALETTE_SIZE = 20

    # Global LUT layout (256 entries):
    #   Bytes   0–19:  Grey ramp (0 = black, 19 = bright white)
    #   Bytes  20–39:  Weapons Systems    (red    #FF2814)
    #   Bytes  40–59:  Propulsion Systems (orange #FF9600)
    #   Bytes  60–79:  Utility Systems    (beige  #E8B998)
    #   Bytes  80–99:  Yellow Systems     (yellow #FFE000)  — new
    #   Bytes 100–119: Power Systems      (green  #00B428)
    #   Bytes 120–139: Teal Systems       (teal   #00C8B4)  — new
    #   Bytes 140–159: Defensive Systems  (blue   #005AFF)
    #   Bytes 160–179: Information Systems (purple #8C28FF)
    #   Bytes 180–229: Spectrum hues — deterministic HSV 0°–352.8° in 7.2° steps
    #   Bytes 230–249: Special spots (see constants below)
    #   Bytes 250–255: Reserved (black / TBD)
    GREY_OFFSET = 0
    WEAPONS_OFFSET = 20
    PROPULSION_OFFSET = 40
    UTILITY_OFFSET = 60
    YELLOW_OFFSET = 80
    POWER_OFFSET = 100
    TEAL_OFFSET = 120
    DEFENSIVE_OFFSET = 140
    INFORMATION_OFFSET = 160
    SPECTRUM_OFFSET = 180
    SPECTRUM_COUNT = 50
    SPECIAL_OFFSET = 230

    # Special spot color constants (indices 230–249):
    # Alerts (230–234):
    ALERT_RED = 230
    WARNING_ORANGE = 231
    CAUTION_YELLOW = 232
    READY_GREEN = 233
    BRIGHT_WHITE = 234
    # Sci-fi accents (235–239):
    SCIFI_CYAN = 235
    ELECTRIC_BLUE = 236
    SCIFI_TEAL = 237
    HOT_PINK = 238
    MAGENTA = 239
    # Warm accents (240–244):
    GOLD = 240
    DEEP_ORANGE = 241
    CORAL = 242
    PEACH = 243
    DEEP_CRIMSON = 244
    # Neutrals (245–249):
    SILVER = 245
    WARM_GREY = 246
    STEEL_BLUE = 247
    SLATE = 248
    ICE_BLUE = 249

    DEFAULT_ANIMATION_DURATION = 1.0

    @classmethod
    def __regenerate_palettes(cls, brightness: float):
        global GLOBAL_PALETTE_LOOKUP, GLOBAL_PALETTE_BRIGHTNESS

        ps = cls.PALETTE_SIZE
        ps_1 = ps - 1
        lut = GLOBAL_PALETTE_LOOKUP

        # All entries are stored in the project's neo-packed format (0x00GGRRBB) so they can be
        # written directly into the strip buffer with no per-pixel byte shuffling. We use the
        # to_neo_packed() helper to keep the bit layout in one place.

        # Grey ramp (0–19): index 0 = black, index 19 = bright white
        for i in range(ps):
            v = int(i / ps_1 * 255 * brightness)
            lut[i] = to_neo_packed(v, v, v)

        # Color categories — 8 blocks of 20, each lerped dim→bright × brightness.
        # Order matches palette layout: Weapons, Propulsion, Utility, Yellow, Power,
        # Teal, Defensive, Information.
        dim_factor = 0.25
        for offset, (br, bg, bb) in [
            (cls.WEAPONS_OFFSET, (0xFF, 0x28, 0x14)),
            (cls.PROPULSION_OFFSET, (0xFF, 0x96, 0x00)),
            (cls.UTILITY_OFFSET, (0xE8, 0xB9, 0x98)),
            (cls.YELLOW_OFFSET, (0xFF, 0xE0, 0x00)),
            (cls.POWER_OFFSET, (0x00, 0xB4, 0x28)),
            (cls.TEAL_OFFSET, (0x00, 0xC8, 0xB4)),
            (cls.DEFENSIVE_OFFSET, (0x00, 0x5A, 0xFF)),
            (cls.INFORMATION_OFFSET, (0x8C, 0x28, 0xFF)),
        ]:
            dr = int(br * dim_factor)
            dg = int(bg * dim_factor)
            db = int(bb * dim_factor)
            for i in range(ps):
                t = i / ps_1
                r = int((dr + (br - dr) * t) * brightness)
                g = int((dg + (bg - dg) * t) * brightness)
                b = int((db + (bb - db) * t) * brightness)
                lut[offset + i] = to_neo_packed(r, g, b)

        # Spectrum hues (180–229): 50 deterministic HSV entries, full S+V, scaled by
        # brightness. Manual HSV→RGB — colorsys is not available on CircuitPython.
        sp_offset = cls.SPECTRUM_OFFSET
        v_val = int(255 * brightness)
        for i in range(cls.SPECTRUM_COUNT):
            hue = i / cls.SPECTRUM_COUNT
            h6 = hue * 6.0
            sector = int(h6)
            frac = h6 - sector
            q = int((1.0 - frac) * 255 * brightness)
            t_val = int(frac * 255 * brightness)
            if sector == 0:
                r, g, b = v_val, t_val, 0
            elif sector == 1:
                r, g, b = q, v_val, 0
            elif sector == 2:
                r, g, b = 0, v_val, t_val
            elif sector == 3:
                r, g, b = 0, q, v_val
            elif sector == 4:
                r, g, b = t_val, 0, v_val
            else:
                r, g, b = v_val, 0, q
            lut[sp_offset + i] = to_neo_packed(r, g, b)

        # Special spots (230–249): pre-defined RGB values × brightness
        _b = brightness
        for index, (r, g, b) in [
            # Alerts (230–234):
            (cls.ALERT_RED, (255, 40, 20)),
            (cls.WARNING_ORANGE, (255, 140, 0)),
            (cls.CAUTION_YELLOW, (255, 220, 0)),
            (cls.READY_GREEN, (40, 220, 40)),
            (cls.BRIGHT_WHITE, (255, 255, 255)),
            # Sci-fi accents (235–239):
            (cls.SCIFI_CYAN, (0, 240, 220)),
            (cls.ELECTRIC_BLUE, (50, 100, 255)),
            (cls.SCIFI_TEAL, (0, 180, 160)),
            (cls.HOT_PINK, (255, 20, 140)),
            (cls.MAGENTA, (220, 0, 200)),
            # Warm accents (240–244):
            (cls.GOLD, (255, 200, 0)),
            (cls.DEEP_ORANGE, (255, 70, 0)),
            (cls.CORAL, (255, 110, 80)),
            (cls.PEACH, (255, 180, 140)),
            (cls.DEEP_CRIMSON, (160, 0, 40)),
            # Neutrals (245–249):
            (cls.SILVER, (200, 200, 210)),
            (cls.WARM_GREY, (180, 160, 140)),
            (cls.STEEL_BLUE, (70, 110, 150)),
            (cls.SLATE, (90, 100, 120)),
            (cls.ICE_BLUE, (180, 220, 255)),
        ]:
            lut[index] = to_neo_packed(int(r * _b), int(g * _b), int(b * _b))

        # TBD entries (250–255): black
        for i in range(250, 256):
            lut[i] = 0

        GLOBAL_PALETTE_BRIGHTNESS = brightness

    @classmethod
    def ensure_palettes(cls, brightness: float):
        global GLOBAL_PALETTE_BRIGHTNESS
        if GLOBAL_PALETTE_BRIGHTNESS != brightness:
            cls.__regenerate_palettes(brightness)

    @classmethod
    def getCardAnimation(cls, spec_id: str):
        return CARD_ANIMATION_DEFS[spec_id]


CardAnimationHelpers.ensure_palettes(ANIMATION_BRIGHTNESS)


def bake_frames(frames):
    """Convert each source frame (bytes() of palette indices) into an array.array('I') of
    neo-packed pixel ints, ready for direct copy into the NeoPixel buffer. Runs once at
    startup; eliminates per-frame palette indirection from the animation hot path."""
    retval = []
    lut = GLOBAL_PALETTE_LOOKUP
    for frame in frames:
        retval.append(array.array("I", [lut[idx] for idx in frame]))
    return retval


class PowerCardAnimation:
    def __init__(
        self,
        uid: str,
        name: str,
        frames: list[bytes],
        animation_duration: float = CardAnimationHelpers.DEFAULT_ANIMATION_DURATION,
    ):
        self.id = uid
        self.name = name
        self._frames = bake_frames(frames)
        log_free_ram(f"{self.name} Baking Animation Frames")
        self.animation_duration = animation_duration

    def AnimationFrame(self, cycle_progress: float):
        nf = len(self._frames)
        frame_idx = int(cycle_progress * nf) % nf
        return frame_idx

    def PixelBuffer(self, frame_idx: int):
        return self._frames[frame_idx]


# ruff: noqa: E402
from power_cards.frames import fusion_engines
from power_cards.frames import warp_field
from power_cards.frames import main_computer
from power_cards.frames import fore_shields
from power_cards.frames import aft_shields
from power_cards.frames import port_shields
from power_cards.frames import starboard_shields
from power_cards.frames import dorsal_shields
from power_cards.frames import ventral_shields
from power_cards.frames import laser_cannon
from power_cards.frames import tractor_beam
from power_cards.frames import stealth_fields
from power_cards.frames import targeting
from power_cards.frames import signal_jammer
from power_cards.frames import alcubierre_warp_drive
from power_cards.frames import thrusters
from power_cards.frames import navigation
from power_cards.frames import external_sensors
from power_cards.frames import internal_sensors
from power_cards.frames import long_range_comms
from power_cards.frames import radio_communications
from power_cards.frames import transporters
from power_cards.frames import co2_scrubbers
from power_cards.frames import oxygen_generators
from power_cards.frames import gravity_field

log_free_ram("anim-overhead")

CARD_ANIMATION_DEFS = {
    PowerCardIds.FUSION_ENGINES_ID: PowerCardAnimation(
        uid=PowerCardIds.FUSION_ENGINES_ID,
        name="Fusion Engines",
        animation_duration=1.0,
        frames=fusion_engines.FRAMES,
    ),
    PowerCardIds.WARP_FIELD_ID: PowerCardAnimation(
        uid=PowerCardIds.WARP_FIELD_ID,
        name="Warp Field",
        frames=warp_field.FRAMES,
    ),
    PowerCardIds.MAIN_COMPUTER_ID: PowerCardAnimation(
        uid=PowerCardIds.MAIN_COMPUTER_ID,
        name="Main Computer",
        frames=main_computer.FRAMES,
    ),
    PowerCardIds.FORE_SHIELDS_ID: PowerCardAnimation(
        uid=PowerCardIds.FORE_SHIELDS_ID,
        name="Fore Shields",
        frames=fore_shields.FRAMES,
    ),
    PowerCardIds.AFT_SHIELDS_ID: PowerCardAnimation(
        uid=PowerCardIds.AFT_SHIELDS_ID,
        name="Aft Shields",
        frames=aft_shields.FRAMES,
    ),
    PowerCardIds.PORT_SHIELDS_ID: PowerCardAnimation(
        uid=PowerCardIds.PORT_SHIELDS_ID,
        name="Port Shields",
        frames=port_shields.FRAMES,
    ),
    PowerCardIds.STARBOARD_SHIELDS_ID: PowerCardAnimation(
        uid=PowerCardIds.STARBOARD_SHIELDS_ID,
        name="Starboard Shields",
        frames=starboard_shields.FRAMES,
    ),
    PowerCardIds.DORSAL_SHIELDS_ID: PowerCardAnimation(
        uid=PowerCardIds.DORSAL_SHIELDS_ID,
        name="Dorsal Shields",
        frames=dorsal_shields.FRAMES,
    ),
    PowerCardIds.VENTRAL_SHIELDS_ID: PowerCardAnimation(
        uid=PowerCardIds.VENTRAL_SHIELDS_ID,
        name="Ventral Shields",
        frames=ventral_shields.FRAMES,
    ),
    PowerCardIds.LASER_CANNON_ID: PowerCardAnimation(
        uid=PowerCardIds.LASER_CANNON_ID,
        name="Laser Cannon",
        animation_duration=1.5,
        frames=laser_cannon.FRAMES,
    ),
    PowerCardIds.TRACTOR_BEAM_ID: PowerCardAnimation(
        uid=PowerCardIds.TRACTOR_BEAM_ID,
        name="Tractor Beam",
        frames=tractor_beam.FRAMES,
    ),
    PowerCardIds.STEALTH_FIELDS_ID: PowerCardAnimation(
        uid=PowerCardIds.STEALTH_FIELDS_ID,
        name="Stealth Fields",
        frames=stealth_fields.FRAMES,
    ),
    PowerCardIds.TARGETING_ID: PowerCardAnimation(
        uid=PowerCardIds.TARGETING_ID,
        name="Targeting",
        frames=targeting.FRAMES,
    ),
    PowerCardIds.SIGNAL_JAMMER_ID: PowerCardAnimation(
        uid=PowerCardIds.SIGNAL_JAMMER_ID,
        name="Signal Jammer",
        frames=signal_jammer.FRAMES,
    ),
    PowerCardIds.ALCUBIERRE_WARP_DRIVE_ID: PowerCardAnimation(
        uid=PowerCardIds.ALCUBIERRE_WARP_DRIVE_ID,
        name="Alcubierre Warp Drive",
        frames=alcubierre_warp_drive.FRAMES,
    ),
    PowerCardIds.THRUSTERS_ID: PowerCardAnimation(
        uid=PowerCardIds.THRUSTERS_ID,
        name="Thrusters",
        frames=thrusters.FRAMES,
    ),
    PowerCardIds.NAVIGATION_ID: PowerCardAnimation(
        uid=PowerCardIds.NAVIGATION_ID,
        name="Navigation",
        frames=navigation.FRAMES,
    ),
    PowerCardIds.EXTERNAL_SENSORS_ID: PowerCardAnimation(
        uid=PowerCardIds.EXTERNAL_SENSORS_ID,
        name="External Sensors",
        frames=external_sensors.FRAMES,
    ),
    PowerCardIds.INTERNAL_SENSORS_ID: PowerCardAnimation(
        uid=PowerCardIds.INTERNAL_SENSORS_ID,
        name="Internal Sensors",
        frames=internal_sensors.FRAMES,
    ),
    PowerCardIds.LONG_RANGE_COMMS_ID: PowerCardAnimation(
        uid=PowerCardIds.LONG_RANGE_COMMS_ID,
        name="Long Range Comms",
        frames=long_range_comms.FRAMES,
    ),
    PowerCardIds.RADIO_COMMUNICATIONS_ID: PowerCardAnimation(
        uid=PowerCardIds.RADIO_COMMUNICATIONS_ID,
        name="Radio Communications",
        frames=radio_communications.FRAMES,
    ),
    PowerCardIds.TRANSPORTERS_ID: PowerCardAnimation(
        uid=PowerCardIds.TRANSPORTERS_ID,
        name="Transporters",
        frames=transporters.FRAMES,
    ),
    PowerCardIds.CO2_SCRUBBERS_ID: PowerCardAnimation(
        uid=PowerCardIds.CO2_SCRUBBERS_ID,
        name="CO2 Scrubbers",
        frames=co2_scrubbers.FRAMES,
    ),
    PowerCardIds.OXYGEN_GENERATORS_ID: PowerCardAnimation(
        uid=PowerCardIds.OXYGEN_GENERATORS_ID,
        name="Oxygen Generators",
        frames=oxygen_generators.FRAMES,
    ),
    PowerCardIds.GRAVITY_FIELD_ID: PowerCardAnimation(
        uid=PowerCardIds.GRAVITY_FIELD_ID,
        name="Gravity Field",
        frames=gravity_field.FRAMES,
    ),
}

log_free_ram("post-animation-baking")
