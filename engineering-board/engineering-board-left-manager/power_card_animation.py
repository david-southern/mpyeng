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

    # Pre-computed cosine LUT for wave animation (64 entries, 0-256 scale)
    # Maps cycle_progress to wave_t: 0 at progress=0, 256 at progress=0.5, 0 at progress=1.0
    _COS_LUT_SIZE = 64
    _COS_LUT = [int(128 - 128 * math.cos(i * 2 * math.pi / 64)) for i in range(64)]

    @classmethod
    def getCardAnimation(cls, spec_id: str):
        return CARD_ANIMATION_DEFS[spec_id]

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
    PRECOMPUTED_FRAME_COUNT = 10
    
    def __init__(self, uid: str, name: str, category: str, bright_color: Color, string_mask: list[str], dim_color: Color | None = None, animation_duration: float = CardAnimationHelpers.DEFAULT_ANIMATION_DURATION):
        self.id = uid
        self.name = name
        self.category = category
        self.bright_color = bright_color
        self.dim_color = dim_color if dim_color else bright_color.copy().scale(PowerCardAnimation.DIM_BRIGHTNESS)
        self.string_mask = string_mask
        self.animation_duration = animation_duration

        # Pre-extract RGB components for integer math
        self._bright_r = bright_color.R
        self._bright_g = bright_color.G
        self._bright_b = bright_color.B
        self._dim_r = self.dim_color.R
        self._dim_g = self.dim_color.G
        self._dim_b = self.dim_color.B

        # Parse mask: classify each pixel
        mask_h = len(string_mask)
        mask_w = len(string_mask[0]) if mask_h > 0 else 0
        self._pixel_count = mask_w * mask_h
        self._static_digits = []    # list of (idx, t_256) for digits 0-9
        self._animated_pixels = []  # list of (idx, char, param) for animated types

        for y in range(mask_h):
            for x in range(mask_w):
                ch = string_mask[y][x]
                idx = CardAnimationHelpers.xy_to_index(x, y, width=mask_w, height=mask_h)
                if ch == '.':
                    pass  # black, stays 0
                elif '0' <= ch <= '9':
                    self._static_digits.append((idx, int((ord(ch) - 48) * 256 / 9)))
                elif 'a' <= ch <= 'z':
                    self._animated_pixels.append((idx, ch, (ord(ch) - 97) / 25))
                else:
                    self._animated_pixels.append((idx, ch, 0))

        # Frames are baked on first use per brightness value
        self._cached_brightness = -1.0
        self._frames: list[list[int]] = []

    def _bake_frames(self, brightness: float):
        """Pre-compute all frames as list[int] for the given brightness."""
        n = self._pixel_count
        nf = PowerCardAnimation.PRECOMPUTED_FRAME_COUNT
        cos_lut = CardAnimationHelpers._COS_LUT
        cos_size = CardAnimationHelpers._COS_LUT_SIZE

        # Pre-compute brightness-scaled base colors as ints
        br = int(self._bright_r * brightness)
        bg = int(self._bright_g * brightness)
        bb = int(self._bright_b * brightness)
        dr = int(self._dim_r * brightness)
        dg = int(self._dim_g * brightness)
        db = int(self._dim_b * brightness)
        max_rand = int(255 * brightness)

        # Bake static base buffer once (digits + dots)
        static_buf = [0] * n
        b_r, b_g, b_b = self._bright_r, self._bright_g, self._bright_b
        d_r, d_g, d_b = self._dim_r, self._dim_g, self._dim_b
        for idx, t_256 in self._static_digits:
            r = d_r + (((b_r - d_r) * t_256) >> 8)
            g = d_g + (((b_g - d_g) * t_256) >> 8)
            b = d_b + (((b_b - d_b) * t_256) >> 8)
            r = int(r * brightness)
            g = int(g * brightness)
            b = int(b * brightness)
            static_buf[idx] = (r << 16) | (g << 8) | b

        # Bright packed int for quick assignment
        bright_int = (br << 16) | (bg << 8) | bb

        frames = []
        _random = random.random
        for fi in range(nf):
            cycle_progress = fi / nf
            buf = static_buf[:]

            wave_t = cos_lut[int(cycle_progress * cos_size) % cos_size]

            for idx, ch, param in self._animated_pixels:
                if ch == '~':
                    r = br + (((dr - br) * wave_t) >> 8)
                    g = bg + (((dg - bg) * wave_t) >> 8)
                    b = bb + (((db - bb) * wave_t) >> 8)
                    buf[idx] = (r << 16) | (g << 8) | b
                elif ch == '@':
                    t = int(_random() * 256)
                    r = dr + (((br - dr) * t) >> 8)
                    g = dg + (((bg - dg) * t) >> 8)
                    b = db + (((bb - db) * t) >> 8)
                    buf[idx] = (r << 16) | (g << 8) | b
                elif ch == '%':
                    if _random() >= 0.6:
                        buf[idx] = (int(_random() * max_rand) << 16) | (int(_random() * max_rand) << 8) | int(_random() * max_rand)
                elif ch == '>':
                    f = 1.0 - cycle_progress
                    if f > 0:
                        buf[idx] = (int(br * f) << 16) | (int(bg * f) << 8) | int(bb * f)
                elif ch == '<':
                    if cycle_progress > 0:
                        buf[idx] = (int(br * cycle_progress) << 16) | (int(bg * cycle_progress) << 8) | int(bb * cycle_progress)
                elif ch == '*':
                    if _random() < 0.75:
                        buf[idx] = bright_int
                elif 'a' <= ch <= 'z':
                    if cycle_progress >= param:
                        buf[idx] = bright_int
                    elif param > 0:
                        t = cycle_progress / param
                        buf[idx] = (int(br * t) << 16) | (int(bg * t) << 8) | int(bb * t)

            frames.append(buf)

        self._cached_brightness = brightness
        self._frames = frames

    def PixelBuffer(self, cycle_progress: float, brightness: float = 1.0) -> list[int]:
        """Return a pre-computed frame as list[int]. Animation time is quantized to the nearest
        pre-computed frame for maximum throughput.
        """
        if self._cached_brightness != brightness:
            self._bake_frames(brightness)
        nf = PowerCardAnimation.PRECOMPUTED_FRAME_COUNT
        frame_idx = int(cycle_progress * nf) % nf
        return self._frames[frame_idx][:]


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
