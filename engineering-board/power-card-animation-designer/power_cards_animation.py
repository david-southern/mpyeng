"""
power-card icon data and rendering helpers.

Each static image is an 8x8 tuple-of-tuples of (r, g, b) tuples.
Each animation is a tuple of 3-9 frames, where each frame is also an 8x8
tuple-of-tuples of (r, g, b) tuples.
"""

import math
import random

from color_utils import Color

class CardCategories:
    OFF_COLOR = Color("#000000")
    POWER_SYSTEMS_COLOR = Color("#00B428")
    DEFENSIVE_SYSTEMS_COLOR = Color("#005AFF")
    WEAPONS_SYSTEMS_COLOR = Color("#FF2814")
    PROPULSION_SYSTEMS_COLOR = Color("#FFAA00")
    INFORMATION_SYSTEMS_COLOR = Color("#8C28FF")
    UTILITY_SYSTEMS_COLOR = Color("#E8B998")

    POWER_SYSTEMS_CATEGORY_NAME = "Power & Core Systems"
    DEFENSIVE_SYSTEMS_CATEGORY_NAME = "Defensive Systems"
    WEAPONS_SYSTEMS_CATEGORY_NAME = "Weapons Systems"
    PROPULSION_SYSTEMS_CATEGORY_NAME = "Propulsion & Movement"
    INFORMATION_SYSTEMS_CATEGORY_NAME = "Information Systems"
    UTILITY_SYSTEMS_CATEGORY_NAME = "Utility Systems"

    CATEGORY_COLORS = {
        POWER_SYSTEMS_CATEGORY_NAME: POWER_SYSTEMS_COLOR,
        DEFENSIVE_SYSTEMS_CATEGORY_NAME: DEFENSIVE_SYSTEMS_COLOR,
        WEAPONS_SYSTEMS_CATEGORY_NAME: WEAPONS_SYSTEMS_COLOR,
        PROPULSION_SYSTEMS_CATEGORY_NAME: PROPULSION_SYSTEMS_COLOR,
        INFORMATION_SYSTEMS_CATEGORY_NAME: INFORMATION_SYSTEMS_COLOR,
        UTILITY_SYSTEMS_CATEGORY_NAME: UTILITY_SYSTEMS_COLOR,
    }

class CardSpecHelpers:
    WIDTH = 8
    HEIGHT = 8
    PIXELS_PER_ICON = WIDTH * HEIGHT

    # Power card color_mask legend:
    COLOR_MASK_BLACK = "." # transparent/black
    COLOR_MASK_WAVE = "~" # animated "wave" pixel (cycle smoothly from O color to o color and back again)
    COLOR_MASK_RANDOM_BRIGHTNESS = "@" # animated "random brightness" pixel (random flickering between the O color and the o color)
    COLOR_MASK_RANDOM_COLOR = "%" # animated "random" pixel (random flickering rbg colors - each frame, each X pixel is a random color, with more time spent at black than the random color)
    COLOR_MASK_FADE_OUT = ">" # animated "fade out" pixel (Start each animation cycle at the O color and smoothly fade to black at the end of the cycle)
    COLOR_MASK_FADE_IN = "<" # animated "fade in" pixel (Start each animation cycle at black and smoothly fade to the O color)
    COLOR_MASK_LIGHTNING = "*" # animated "lightning" pixel (Alternate (no smoothing, immediate transitions) between O color and black in a random pattern, with more time spent at O color than black) Power card
    # * digits 0 - 9 = interpolate between the spec's dim color (0) and bright color (9) based on the digit
    # * a-z = animated "delay" pixel (Start each animation cycle at black, smoothly transition to the spec's
    #   bright color over a delay of <letter index> / <letter z index> of the animation duration,
    #   then remain at the bright color for the rest of the animation cycle - e.g. 'a' will arrive
    #   at full brightness very quickly (1/26 of the animation duration), while 'm' will take half of the animation duration to reach full brightness)

    DEFAULT_ANIMATION_DURATION = 3.0

    FUSION_ENGINES_ID = "fusion_engines"
    WARP_FIELD_ID = "warp_field"
    MAIN_COMPUTER_ID = "main_computer"
    FORE_SHIELDS_ID = "fore_shields"
    AFT_SHIELDS_ID = "aft_shields"
    PORT_SHIELDS_ID = "port_shields"
    STARBOARD_SHIELDS_ID = "starboard_shields"
    DORSAL_SHIELDS_ID = "dorsal_shields"
    VENTRAL_SHIELDS_ID = "ventral_shields"
    LASER_CANNON_ID = "laser_cannon"
    TRACTOR_BEAM_ID = "tractor_beam"
    STEALTH_FIELDS_ID = "stealth_fields"
    TARGETING_ID = "targeting"
    SIGNAL_JAMMER_ID = "signal_jammer"
    ALCUBIERRE_WARP_DRIVE_ID = "alcubierre_warp_drive"
    THRUSTERS_ID = "thrusters"
    NAVIGATION_ID = "navigation"
    EXTERNAL_SENSORS_ID = "external_sensors"
    INTERNAL_SENSORS_ID = "internal_sensors"
    LONG_RANGE_COMMS_ID = "long_range_comms"
    RADIO_COMMUNICATIONS_ID = "radio_communications"
    TRANSPORTERS_ID = "transporters"
    CO2_SCRUBBERS_ID = "co2_scrubbers"
    OXYGEN_GENERATORS_ID = "oxygen_generators"
    GRAVITY_FIELD_ID = "gravity_field"

    ALL_CARD_IDS = [
        FUSION_ENGINES_ID,
        WARP_FIELD_ID,
        MAIN_COMPUTER_ID,
        FORE_SHIELDS_ID,
        AFT_SHIELDS_ID,
        PORT_SHIELDS_ID,
        STARBOARD_SHIELDS_ID,
        DORSAL_SHIELDS_ID,
        VENTRAL_SHIELDS_ID,
        LASER_CANNON_ID,
        TRACTOR_BEAM_ID,
        STEALTH_FIELDS_ID,
        TARGETING_ID,
        SIGNAL_JAMMER_ID,
        ALCUBIERRE_WARP_DRIVE_ID,
        THRUSTERS_ID,
        NAVIGATION_ID,
        EXTERNAL_SENSORS_ID,
        INTERNAL_SENSORS_ID,
        LONG_RANGE_COMMS_ID,
        RADIO_COMMUNICATIONS_ID,
        TRANSPORTERS_ID,
        CO2_SCRUBBERS_ID,
        OXYGEN_GENERATORS_ID,
        GRAVITY_FIELD_ID,
    ]

    @classmethod
    def getCardSpec(cls, spec_id: str):
        return CARD_SPECS[spec_id]

    @classmethod
    def color_buffer(cls, static_string_mask: list[str], bright_color: Color, dim_color: Color, cycle_progress: float) -> list[Color]:
        """Convert a string mask to a flat list of Colors, ordered in the serpentine layout
        used by our NeoPixel grids.
        """
        mask_height = len(static_string_mask)
        mask_width = len(static_string_mask[0]) if mask_height > 0 else 0
        result: list[Color] = [CardCategories.OFF_COLOR] * (mask_width * mask_height)
        for y in range(mask_height):
            for x in range(mask_width):
                ch = static_string_mask[y][x]
                idx = cls.xy_to_index(x, y, width=mask_width, height=mask_height)
                if ch == cls.COLOR_MASK_BLACK:
                    result[idx] = CardCategories.OFF_COLOR
                elif ch == cls.COLOR_MASK_WAVE:
                    # Smooth ping-pong between bright and dim
                    wave_t = 0.5 - 0.5 * math.cos(cycle_progress * 2 * math.pi)
                    result[idx] = bright_color.lerp(dim_color, wave_t)
                elif ch == cls.COLOR_MASK_RANDOM_BRIGHTNESS:
                    # Random value between dim and bright each frame
                    t = random.random()
                    result[idx] = dim_color.lerp(bright_color, t)
                elif ch == cls.COLOR_MASK_RANDOM_COLOR:
                    # Random RGB flash, biased toward black
                    if random.random() < 0.6:
                        result[idx] = CardCategories.OFF_COLOR
                    else:
                        result[idx] = Color(
                            (int(random.random() * 255), int(random.random() * 255), int(random.random() * 255))
                        )
                elif ch == cls.COLOR_MASK_FADE_OUT:
                    # Bright -> black over the cycle
                    result[idx] = bright_color.lerp(CardCategories.OFF_COLOR, cycle_progress)
                elif ch == cls.COLOR_MASK_FADE_IN:
                    # Black -> bright over the cycle
                    result[idx] = CardCategories.OFF_COLOR.lerp(bright_color, cycle_progress)
                elif ch == cls.COLOR_MASK_LIGHTNING:
                    # Immediate random flicker, biased toward bright
                    if random.random() < 0.75:
                        result[idx] = bright_color
                    else:
                        result[idx] = CardCategories.OFF_COLOR
                elif "a" <= ch <= "z":
                    # Delay pixel: stay black until delay%, then fade to bright
                    delay_fraction = (ord(ch) - ord("a")) / (ord("z") - ord("a"))
                    if cycle_progress >= delay_fraction:
                        result[idx] = bright_color
                    else:
                        t = (cycle_progress / delay_fraction)
                        result[idx] = CardCategories.OFF_COLOR.lerp(bright_color, t)
                elif "0" <= ch <= "9":
                    brightness = (ord(ch) - ord("0")) / 9
                    result[idx] = dim_color.lerp(bright_color, brightness)
                else:
                    result[idx] = CardCategories.OFF_COLOR
        return result

    @classmethod
    def xy_to_index(cls, x, y, flip_y = True, width=None, height=None, layout="serpentine"):
        """Map x,y to a NeoPixel index.

        layout options:
          - "row-major": rows laid out left->right, top->bottom
          - "serpentine": even rows left->right, odd rows right->left
          - "column-major": columns laid out top->bottom, left->right

        flip_y: will flip the y axis (so y=0 is the bottom row instead of the top) - our card
          masks are laid out with y=0 at the top, but our NeoPixel grids have y=0 at the bottom, so this
          makes it easy to convert between them.
        """
        if width is None: width = cls.WIDTH
        if height is None: height = cls.HEIGHT

        if(flip_y): y = height - 1 - y
        
        if layout == "row-major":
            return y * width + x
        if layout == "serpentine":
            return y * width + (x if y % 2 == 0 else (width - 1 - x))
        if layout == "column-major":
            return x * height + y
        raise ValueError("Unknown layout: {}".format(layout))


class PowerCardSpec:
    DIM_BRIGHTNESS = 0.25
    
    def __init__(self, uid: str, name: str, category: str, bright_color: Color, string_mask: list[str], dim_color: Color | None = None, animation_duration: float = CardSpecHelpers.DEFAULT_ANIMATION_DURATION):
        self.id = uid
        self.name = name
        self.category = category
        self.bright_color = bright_color
        self.dim_color = dim_color if dim_color else bright_color.lerp(CardCategories.OFF_COLOR, PowerCardSpec.DIM_BRIGHTNESS)
        self.string_mask = string_mask
        self.animation_duration = animation_duration

    def color_buffer(self, cycle_progress: float):
        """Convert the card's string mask to a flat list of Colors, ordered in the serpentine layout
        used by our NeoPixel grids.
        """
        return CardSpecHelpers.color_buffer(self.string_mask, self.bright_color, self.dim_color, cycle_progress)



CARD_SPECS = {
    CardSpecHelpers.FUSION_ENGINES_ID: PowerCardSpec(
        uid=CardSpecHelpers.FUSION_ENGINES_ID,
        name="Fusion Engines",
        category=CardCategories.POWER_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.POWER_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '........',
            '.2....2.',
            '..2..2..',
            '...44...',
            '...77...',
            '...99...',
            '...99...',
            '........',
        ],

    ),
    CardSpecHelpers.WARP_FIELD_ID: PowerCardSpec(
        uid=CardSpecHelpers.WARP_FIELD_ID,
        name="Warp Field",
        category=CardCategories.POWER_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.POWER_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '..~~~~..',
            '.~....~.',
            '~..99..~',
            '~.9..9.~',
            '~.9..9.~',
            '~..99..~',
            '.~....~.',
            '..~~~~..',
        ],

    ),
    CardSpecHelpers.MAIN_COMPUTER_ID: PowerCardSpec(
        uid=CardSpecHelpers.MAIN_COMPUTER_ID,
        name="Main Computer",
        category=CardCategories.POWER_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.POWER_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '..9999..',
            '.9....9.',
            '9.%%%%.9',
            '9.%%%%.9',
            '9.%%%%.9',
            '9.%%%%.9',
            '.9....9.',
            '..9999..',
        ],

    ),
    CardSpecHelpers.FORE_SHIELDS_ID: PowerCardSpec(
        uid=CardSpecHelpers.FORE_SHIELDS_ID,
        name="Fore Shields",
        category=CardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '..~~~~..',
            '.3....3.',
            '...99...',
            '..9999..',
            '..9999..',
            '...99...',
            '........',
            '........',
        ],

    ),
    CardSpecHelpers.AFT_SHIELDS_ID: PowerCardSpec(
        uid=CardSpecHelpers.AFT_SHIELDS_ID,
        name="Aft Shields",
        category=CardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '........',
            '........',
            '...99...',
            '..9999..',
            '..9999..',
            '...99...',
            '.3....3.',
            '..~~~~..',
        ],

    ),
    CardSpecHelpers.PORT_SHIELDS_ID: PowerCardSpec(
        uid=CardSpecHelpers.PORT_SHIELDS_ID,
        name="Port Shields",
        category=CardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '........',
            '.3......',
            '~..99...',
            '~.9999..',
            '~.9999..',
            '~..99...',
            '.3......',
            '........',
        ],

    ),
    CardSpecHelpers.STARBOARD_SHIELDS_ID: PowerCardSpec(
        uid=CardSpecHelpers.STARBOARD_SHIELDS_ID,
        name="Starboard Shields",
        category=CardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '........',
            '......3.',
            '...99..~',
            '..9999.~',
            '..9999.~',
            '...99..~',
            '......3.',
            '........',
        ],

    ),
    CardSpecHelpers.DORSAL_SHIELDS_ID: PowerCardSpec(
        uid=CardSpecHelpers.DORSAL_SHIELDS_ID,
        name="Dorsal Shields",
        category=CardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '........',
            '..~~~~..',
            '.~~~~~~.',
            '.~~~~~~.',
            '.~~~~~~.',
            '.~~~~~~.',
            '..~~~~..',
            '........',
        ],

    ),
    CardSpecHelpers.VENTRAL_SHIELDS_ID: PowerCardSpec(
        uid=CardSpecHelpers.VENTRAL_SHIELDS_ID,
        name="Ventral Shields",
        category=CardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '........',
            '..~~~~..',
            '.~~99~~.',
            '.~9999~.',
            '.~9999~.',
            '.~~99~~.',
            '..~~~~..',
            '........',
        ],

    ),
    CardSpecHelpers.LASER_CANNON_ID: PowerCardSpec(
        uid=CardSpecHelpers.LASER_CANNON_ID,
        name="Laser Cannon",
        category=CardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '.....999',
            '.....999',
            '......99',
            '....a...',
            '....a...',
            'f..b....',
            'edc.f...',
            'dcde....',
        ],
        animation_duration=1.5
    ),
    CardSpecHelpers.TRACTOR_BEAM_ID: PowerCardSpec(
        uid=CardSpecHelpers.TRACTOR_BEAM_ID,
        name="Tractor Beam",
        category=CardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '..9999..',
            '...99...',
            '...**...',
            '..*33*..',
            '..*44*..',
            '..*55*..',
            '.*6666*.',
            '.*6666*.',
        ],
    ),
    CardSpecHelpers.STEALTH_FIELDS_ID: PowerCardSpec(
        uid=CardSpecHelpers.STEALTH_FIELDS_ID,
        name="Stealth Fields",
        category=CardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '........',
            '..@@@@..',
            '.@@@@@@.',
            '.@@@@@@.',
            '.@@@@@@.',
            '.@@@@@@.',
            '..@@@@..',
            '........',
        ],

    ),
    CardSpecHelpers.TARGETING_ID: PowerCardSpec(
        uid=CardSpecHelpers.TARGETING_ID,
        name="Targeting",
        category=CardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '........',
            '..999...',
            '...2....',
            '.92.29..',
            '...2....',
            '..999...',
            '........',
            '........',
        ],

    ),
    CardSpecHelpers.SIGNAL_JAMMER_ID: PowerCardSpec(
        uid=CardSpecHelpers.SIGNAL_JAMMER_ID,
        name="Signal Jammer",
        category=CardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '%%%%%%%%',
            '%%%%%%%%',
            '%%%%%%%%',
            '%%%%%%%%',
            '%%%%%%%%',
            '%%%%%%%%',
            '%%%%%%%%',
            '%%%%%%%%',
        ],

    ),
    CardSpecHelpers.ALCUBIERRE_WARP_DRIVE_ID: PowerCardSpec(
        uid=CardSpecHelpers.ALCUBIERRE_WARP_DRIVE_ID,
        name="Alcubierre Warp Drive",
        category=CardCategories.PROPULSION_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.PROPULSION_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '..9999..',
            '.9.yy.9.',
            '9..xx..9',
            '9..vv..9',
            '9..ss..9',
            '9..mm..9',
            '.9.aa.9.',
            '..9999..',
        ],

    ),
    CardSpecHelpers.THRUSTERS_ID: PowerCardSpec(
        uid=CardSpecHelpers.THRUSTERS_ID,
        name="Thrusters",
        category=CardCategories.PROPULSION_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.PROPULSION_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '..3333..',
            '...33...',
            '...99...',
            '...99...',
            '..@66@..',
            '.@@33@@.',
            '@@@@@@@@',
            '...@@...',
        ],

    ),
    CardSpecHelpers.NAVIGATION_ID: PowerCardSpec(
        uid=CardSpecHelpers.NAVIGATION_ID,
        name="Navigation",
        category=CardCategories.PROPULSION_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.PROPULSION_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '........',
            '........',
            '..9.....',
            '.929....',
            '..2.....',
            '..2..1..',
            '..22221.',
            '.....1..',
        ],

    ),
    CardSpecHelpers.EXTERNAL_SENSORS_ID: PowerCardSpec(
        uid=CardSpecHelpers.EXTERNAL_SENSORS_ID,
        name="External Sensors",
        category=CardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '..@@@@..',
            '.@....@.',
            '@......@',
            '@..99..@',
            '@..99..@',
            '@......@',
            '.@....@.',
            '..@@@@..',
        ],

    ),
    CardSpecHelpers.INTERNAL_SENSORS_ID: PowerCardSpec(
        uid=CardSpecHelpers.INTERNAL_SENSORS_ID,
        name="Internal Sensors",
        category=CardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '........',
            '........',
            '...99...',
            '..9@@9..',
            '..9@@9..',
            '...99...',
            '........',
            '........',
        ],

    ),
    CardSpecHelpers.LONG_RANGE_COMMS_ID: PowerCardSpec(
        uid=CardSpecHelpers.LONG_RANGE_COMMS_ID,
        name="Long Range Comms",
        category=CardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '..6996..',
            '.3....3.',
            '........',
            '...77...',
            '..5..5..',
            '........',
            '...55...',
            '...99...',
        ],

    ),
    CardSpecHelpers.RADIO_COMMUNICATIONS_ID: PowerCardSpec(
        uid=CardSpecHelpers.RADIO_COMMUNICATIONS_ID,
        name="Radio Communications",
        category=CardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '........',
            '........',
            '........',
            '..7997..',
            '.5....5.',
            '...66...',
            '..2442..',
            '...99...',
        ],

    ),
    CardSpecHelpers.TRANSPORTERS_ID: PowerCardSpec(
        uid=CardSpecHelpers.TRANSPORTERS_ID,
        name="Transporters",
        category=CardCategories.UTILITY_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.UTILITY_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '...999..',
            '...777..',
            '....5...',
            '.@@333@@',
            '....@...',
            '...@.@..',
            '..@...@.',
            '..@...@.',
        ],

    ),
    CardSpecHelpers.CO2_SCRUBBERS_ID: PowerCardSpec(
        uid=CardSpecHelpers.CO2_SCRUBBERS_ID,
        name="CO2 Scrubbers",
        category=CardCategories.UTILITY_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.UTILITY_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '@7@7@7@7',
            '.....9..',
            '........',
            '3@3@39..',
            '........',
            '3@3@39..',
            '@7@7@7@7',
            '.....9..',
        ],

    ),
    CardSpecHelpers.OXYGEN_GENERATORS_ID: PowerCardSpec(
        uid=CardSpecHelpers.OXYGEN_GENERATORS_ID,
        name="Oxygen Generators",
        category=CardCategories.UTILITY_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.UTILITY_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '...99...',
            '..9@@9..',
            '.555555.',
            '..9@@9..',
            '..9@@9..',
            '.555555.',
            '..9@@9..',
            '...99...',
        ],

    ),
    CardSpecHelpers.GRAVITY_FIELD_ID: PowerCardSpec(
        uid=CardSpecHelpers.GRAVITY_FIELD_ID,
        name="Gravity Field",
        category=CardCategories.UTILITY_SYSTEMS_CATEGORY_NAME,
        bright_color=CardCategories.CATEGORY_COLORS[CardCategories.UTILITY_SYSTEMS_CATEGORY_NAME],
        string_mask=[
            '..9999..',
            '.9~~~~9.',
            '9~~~~~~9',
            '9~~~~~~9',
            '9~~~~~~9',
            '9~~~~~~9',
            '.9~~~~9.',
            '..9999..',
        ],

    ),
}
