import math
import random

from color_utils import Color
from power_card_categories import PowerCardCategories
from power_card_ids import PowerCardIds

class CardAnimationHelpers:
    WIDTH = 8
    HEIGHT = 8
    CARD_PIXEL_COUNT = WIDTH * HEIGHT

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

    @classmethod
    def getCardAnimation(cls, spec_id: str):
        return CARD_ANIMATION_DEFS[spec_id]

    @classmethod
    def color_buffer(cls, result: list[Color], static_string_mask: list[str], bright_color: Color, dim_color: Color, cycle_progress: float, brightness: float) -> list[Color]:
        """Fill a pre-allocated Color buffer from a string mask, ordered in the serpentine layout
        used by our NeoPixel grids.  Brightness is applied during generation to avoid a second pass.
        """
        mask_height = len(static_string_mask)
        mask_width = len(static_string_mask[0]) if mask_height > 0 else 0
        # Compute wave_t once for the entire frame
        wave_t = 0.5 - 0.5 * math.cos(cycle_progress * 2 * math.pi)
        for y in range(mask_height):
            for x in range(mask_width):
                ch = static_string_mask[y][x]
                idx = cls.xy_to_index(x, y, width=mask_width, height=mask_height)
                pixel = result[idx]
                if ch == cls.COLOR_MASK_BLACK:
                    pixel.set_rgb(0, 0, 0)
                elif ch == cls.COLOR_MASK_WAVE:
                    # Smooth ping-pong between bright and dim
                    pixel.copy_from(bright_color).lerp(dim_color, wave_t).scale(brightness)
                elif ch == cls.COLOR_MASK_RANDOM_BRIGHTNESS:
                    # Random value between dim and bright each frame
                    t = random.random()
                    pixel.copy_from(dim_color).lerp(bright_color, t).scale(brightness)
                elif ch == cls.COLOR_MASK_RANDOM_COLOR:
                    # Random RGB flash, biased toward black
                    if random.random() < 0.6:
                        pixel.set_rgb(0, 0, 0)
                    else:
                        pixel.set_rgb(
                            int(random.random() * 255),
                            int(random.random() * 255),
                            int(random.random() * 255),
                        ).scale(brightness)
                elif ch == cls.COLOR_MASK_FADE_OUT:
                    # Bright -> black over the cycle
                    pixel.copy_from(bright_color).scale(1.0 - cycle_progress).scale(brightness)
                elif ch == cls.COLOR_MASK_FADE_IN:
                    # Black -> bright over the cycle
                    pixel.copy_from(bright_color).scale(cycle_progress).scale(brightness)
                elif ch == cls.COLOR_MASK_LIGHTNING:
                    # Immediate random flicker, biased toward bright
                    if random.random() < 0.75:
                        pixel.copy_from(bright_color).scale(brightness)
                    else:
                        pixel.set_rgb(0, 0, 0)
                elif "a" <= ch <= "z":
                    # Delay pixel: stay black until delay%, then fade to bright
                    delay_fraction = (ord(ch) - ord("a")) / (ord("z") - ord("a"))
                    if cycle_progress >= delay_fraction:
                        pixel.copy_from(bright_color).scale(brightness)
                    else:
                        t = (cycle_progress / delay_fraction)
                        pixel.copy_from(bright_color).scale(t * brightness)
                elif "0" <= ch <= "9":
                    digit_t = (ord(ch) - ord("0")) / 9
                    pixel.copy_from(dim_color).lerp(bright_color, digit_t).scale(brightness)
                else:
                    pixel.set_rgb(0, 0, 0)
        return result

    @classmethod
    def pixel_buffer(cls, colors: list[Color]):
        """Convert a list of Color to a list of integer color to send to our NeoPixel grids.
        """
        return [color.to_neopixel() for color in colors]

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


class PowerCardAnimation:
    DIM_BRIGHTNESS = 0.25
    
    def __init__(self, uid: str, name: str, category: str, bright_color: Color, string_mask: list[str], dim_color: Color | None = None, animation_duration: float = CardAnimationHelpers.DEFAULT_ANIMATION_DURATION):
        self.id = uid
        self.name = name
        self.category = category
        self.bright_color = bright_color
        self.dim_color = dim_color if dim_color else bright_color.copy().scale(PowerCardAnimation.DIM_BRIGHTNESS)
        self.string_mask = string_mask
        self.animation_duration = animation_duration
        self._pixel_buffer = [Color((0, 0, 0)) for _ in range(CardAnimationHelpers.CARD_PIXEL_COUNT)]

    def ColorBuffer(self, cycle_progress: float, brightness: float = 1.0):
        """Fill the pre-allocated pixel buffer from the card's string mask."""
        return CardAnimationHelpers.color_buffer(self._pixel_buffer, self.string_mask, self.bright_color, self.dim_color, cycle_progress, brightness)

    def PixelBuffer(self, cycle_progress: float, brightness: float = 1.0):
        """Fill the pre-allocated pixel buffer from the card's string mask."""
        return self.ColorBuffer(cycle_progress, brightness)


CARD_ANIMATION_DEFS = {
    PowerCardIds.FUSION_ENGINES_ID: PowerCardAnimation(
        uid=PowerCardIds.FUSION_ENGINES_ID,
        name="Fusion Engines",
        category=PowerCardCategories.POWER_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.POWER_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.WARP_FIELD_ID: PowerCardAnimation(
        uid=PowerCardIds.WARP_FIELD_ID,
        name="Warp Field",
        category=PowerCardCategories.POWER_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.POWER_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.MAIN_COMPUTER_ID: PowerCardAnimation(
        uid=PowerCardIds.MAIN_COMPUTER_ID,
        name="Main Computer",
        category=PowerCardCategories.POWER_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.POWER_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.FORE_SHIELDS_ID: PowerCardAnimation(
        uid=PowerCardIds.FORE_SHIELDS_ID,
        name="Fore Shields",
        category=PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.AFT_SHIELDS_ID: PowerCardAnimation(
        uid=PowerCardIds.AFT_SHIELDS_ID,
        name="Aft Shields",
        category=PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.PORT_SHIELDS_ID: PowerCardAnimation(
        uid=PowerCardIds.PORT_SHIELDS_ID,
        name="Port Shields",
        category=PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.STARBOARD_SHIELDS_ID: PowerCardAnimation(
        uid=PowerCardIds.STARBOARD_SHIELDS_ID,
        name="Starboard Shields",
        category=PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.DORSAL_SHIELDS_ID: PowerCardAnimation(
        uid=PowerCardIds.DORSAL_SHIELDS_ID,
        name="Dorsal Shields",
        category=PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.VENTRAL_SHIELDS_ID: PowerCardAnimation(
        uid=PowerCardIds.VENTRAL_SHIELDS_ID,
        name="Ventral Shields",
        category=PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.LASER_CANNON_ID: PowerCardAnimation(
        uid=PowerCardIds.LASER_CANNON_ID,
        name="Laser Cannon",
        category=PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.TRACTOR_BEAM_ID: PowerCardAnimation(
        uid=PowerCardIds.TRACTOR_BEAM_ID,
        name="Tractor Beam",
        category=PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.STEALTH_FIELDS_ID: PowerCardAnimation(
        uid=PowerCardIds.STEALTH_FIELDS_ID,
        name="Stealth Fields",
        category=PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.TARGETING_ID: PowerCardAnimation(
        uid=PowerCardIds.TARGETING_ID,
        name="Targeting",
        category=PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.SIGNAL_JAMMER_ID: PowerCardAnimation(
        uid=PowerCardIds.SIGNAL_JAMMER_ID,
        name="Signal Jammer",
        category=PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.ALCUBIERRE_WARP_DRIVE_ID: PowerCardAnimation(
        uid=PowerCardIds.ALCUBIERRE_WARP_DRIVE_ID,
        name="Alcubierre Warp Drive",
        category=PowerCardCategories.PROPULSION_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.PROPULSION_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.THRUSTERS_ID: PowerCardAnimation(
        uid=PowerCardIds.THRUSTERS_ID,
        name="Thrusters",
        category=PowerCardCategories.PROPULSION_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.PROPULSION_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.NAVIGATION_ID: PowerCardAnimation(
        uid=PowerCardIds.NAVIGATION_ID,
        name="Navigation",
        category=PowerCardCategories.PROPULSION_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.PROPULSION_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.EXTERNAL_SENSORS_ID: PowerCardAnimation(
        uid=PowerCardIds.EXTERNAL_SENSORS_ID,
        name="External Sensors",
        category=PowerCardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.INTERNAL_SENSORS_ID: PowerCardAnimation(
        uid=PowerCardIds.INTERNAL_SENSORS_ID,
        name="Internal Sensors",
        category=PowerCardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.LONG_RANGE_COMMS_ID: PowerCardAnimation(
        uid=PowerCardIds.LONG_RANGE_COMMS_ID,
        name="Long Range Comms",
        category=PowerCardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.RADIO_COMMUNICATIONS_ID: PowerCardAnimation(
        uid=PowerCardIds.RADIO_COMMUNICATIONS_ID,
        name="Radio Communications",
        category=PowerCardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.TRANSPORTERS_ID: PowerCardAnimation(
        uid=PowerCardIds.TRANSPORTERS_ID,
        name="Transporters",
        category=PowerCardCategories.UTILITY_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.UTILITY_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.CO2_SCRUBBERS_ID: PowerCardAnimation(
        uid=PowerCardIds.CO2_SCRUBBERS_ID,
        name="CO2 Scrubbers",
        category=PowerCardCategories.UTILITY_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.UTILITY_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.OXYGEN_GENERATORS_ID: PowerCardAnimation(
        uid=PowerCardIds.OXYGEN_GENERATORS_ID,
        name="Oxygen Generators",
        category=PowerCardCategories.UTILITY_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.UTILITY_SYSTEMS_CATEGORY_NAME],
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
    PowerCardIds.GRAVITY_FIELD_ID: PowerCardAnimation(
        uid=PowerCardIds.GRAVITY_FIELD_ID,
        name="Gravity Field",
        category=PowerCardCategories.UTILITY_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.UTILITY_SYSTEMS_CATEGORY_NAME],
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
