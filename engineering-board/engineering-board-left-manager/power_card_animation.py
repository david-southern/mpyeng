import math
import random

from color_utils import Color
from power_card_categories import PowerCardCategories
from power_card_ids import PowerCardIds
from profiling import register_profile, start_profile, stop_profile

PROFILE_ANIM_ENSURE_PAL = "anim_ensure_pal"
PROFILE_ANIM_RENDER = "anim_render"

register_profile(PROFILE_ANIM_ENSURE_PAL)
register_profile(PROFILE_ANIM_RENDER)

class CardAnimationHelpers:
    WIDTH = 8
    HEIGHT = 8
    CARD_PIXEL_COUNT = WIDTH * HEIGHT
    PALETTE_SIZE = 26

    # Baked frame string character classes:
    #   '.' = black (0x000000)
    #   'a'-'z' = category palette index (a=dim, z=bright, 26 levels)
    #   'A'-'Z' = random color palette index (26 pre-computed random colors)
    #
    # Original mask character types (resolved during frame baking):
    #   '.' = black
    #   '~' = wave (smooth ping-pong between bright and dim)
    #   '@' = random brightness (random category palette entry each frame)
    #   '%' = random color (random entry from shared random palette, biased toward black)
    #   '>' = fade out (bright → black over the cycle)
    #   '<' = fade in (black → bright over the cycle)
    #   '*' = lightning (random flicker, biased toward bright)
    #   '0'-'9' = static brightness (digit/9 interpolation from dim to bright)
    #   'a'-'z' = delay (black → bright over a delay fraction of the cycle)

    ANIMATED_MASK_CHARS = frozenset('~@%><*')
    DEFAULT_ANIMATION_DURATION = 3.0

    # Pre-computed cosine LUT for wave animation (64 entries, 0-256 scale)
    _COS_LUT_SIZE = 64
    _COS_LUT = [int(128 - 128 * math.cos(i * 2 * math.pi / 64)) for i in range(64)]

    # Shared render buffer (single pre-allocated list, reused every frame)
    _render_buffer: list[int] = [0] * CARD_PIXEL_COUNT

    # Palette caches (regenerated when brightness changes)
    _category_palettes: dict = {}      # category_name -> list[int] (26 entries)
    _random_palette: list[int] = [0] * PALETTE_SIZE
    _palette_brightness: float = -1.0
    _category_color_defs: dict = {}    # category_name -> (bright_Color, dim_Color)
    _category_luts: dict = {}          # category_name -> list[int] (123 entries: byte value -> packed int)
    # LUT layout: index 46='.' -> 0, 65-90='A'-'Z' -> random palette, 97-122='a'-'z' -> category palette

    @classmethod
    def register_category_colors(cls, category: str, bright_color: Color, dim_color: Color):
        if category not in cls._category_color_defs:
            cls._category_color_defs[category] = (bright_color, dim_color)

    @classmethod
    def _regenerate_palettes(cls, brightness: float):
        ps = cls.PALETTE_SIZE
        ps_1 = ps - 1
        for cat_name, (bright, dim) in cls._category_color_defs.items():
            palette = [0] * ps
            br, bg, bb = bright.R, bright.G, bright.B
            dr, dg, db = dim.R, dim.G, dim.B
            for i in range(ps):
                t = i / ps_1
                r = int((dr + (br - dr) * t) * brightness)
                g = int((dg + (bg - dg) * t) * brightness)
                b = int((db + (bb - db) * t) * brightness)
                palette[i] = (r << 16) | (g << 8) | b
            cls._category_palettes[cat_name] = palette

        rp = cls._random_palette
        for i in range(ps):
            r = int(random.random() * 255 * brightness)
            g = int(random.random() * 255 * brightness)
            b = int(random.random() * 255 * brightness)
            rp[i] = (r << 16) | (g << 8) | b

        # Build per-category render LUTs: byte value -> packed int (no branching at render time)
        for cat_name, palette in cls._category_palettes.items():
            lut = [0] * 123  # covers ord('.') through ord('z')
            # 'A'-'Z' (65-90): random palette
            for i in range(ps):
                lut[65 + i] = rp[i]
            # 'a'-'z' (97-122): category palette
            for i in range(ps):
                lut[97 + i] = palette[i]
            # index 46 ('.') stays 0 (black)
            cls._category_luts[cat_name] = lut

        cls._palette_brightness = brightness

    @classmethod
    def ensure_palettes(cls, brightness: float):
        if cls._palette_brightness != brightness:
            cls._regenerate_palettes(brightness)

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
    
    def __init__(self, uid: str, name: str, category: str, bright_color: Color, string_mask: list[str], dim_color: Color | None = None, animation_duration: float = CardAnimationHelpers.DEFAULT_ANIMATION_DURATION):
        self.id = uid
        self.name = name
        self.category = category
        self.bright_color = bright_color
        self.dim_color = dim_color if dim_color else bright_color.copy().scale(PowerCardAnimation.DIM_BRIGHTNESS)
        self.string_mask = string_mask
        self.animation_duration = animation_duration

        # Register category for shared palette generation
        CardAnimationHelpers.register_category_colors(category, bright_color, self.dim_color)

        # Determine frame count: 1 for fully static masks, 10 for animated
        mask_h = len(string_mask)
        mask_w = len(string_mask[0]) if mask_h > 0 else 0
        has_animated = False
        for row in string_mask:
            for ch in row:
                if ch in CardAnimationHelpers.ANIMATED_MASK_CHARS or ('a' <= ch <= 'z'):
                    has_animated = True
                    break
            if has_animated:
                break
        num_frames = 10 if has_animated else 1

        # Bake frame strings (each is 64 bytes in serpentine pixel order)
        self._frame_strings: list[bytes] = []
        for fi in range(num_frames):
            self._frame_strings.append(
                self._bake_frame(fi, num_frames, mask_w, mask_h)
            )

    @staticmethod
    def _intensity_to_char(f: float) -> str:
        """Map intensity fraction (0.0=black, 1.0=bright) to a frame char.
        Returns '.' for black, 'a'-'z' for the category palette range (dim to bright).
        Values below DIM_BRIGHTNESS map to '.' since the palette only covers dim-to-bright.
        """
        dim = PowerCardAnimation.DIM_BRIGHTNESS
        if f < dim:
            return '.'
        idx = int((f - dim) / (1.0 - dim) * 25)
        return chr(97 + min(25, idx))

    def _bake_frame(self, frame_index: int, num_frames: int, mask_w: int, mask_h: int) -> bytes:
        cycle_progress = frame_index / num_frames
        n = mask_w * mask_h
        frame = ['.'] * n

        # Pre-compute wave char for this frame
        cos_lut = CardAnimationHelpers._COS_LUT
        cos_size = CardAnimationHelpers._COS_LUT_SIZE
        wave_lut_val = cos_lut[int(cycle_progress * cos_size) % cos_size]
        # LUT: 0 = bright end, 256 = dim end. Palette: a(0)=dim, z(25)=bright
        wave_idx = 25 - min(25, (wave_lut_val * 25) >> 8)
        wave_char = chr(97 + wave_idx)

        _random = random.random
        _randint = random.randint
        _i2c = PowerCardAnimation._intensity_to_char

        for y in range(mask_h):
            for x in range(mask_w):
                ch = self.string_mask[y][x]
                idx = CardAnimationHelpers.xy_to_index(x, y, width=mask_w, height=mask_h)
                if ch == '.':
                    pass  # already '.'
                elif ch == '~':
                    frame[idx] = wave_char
                elif ch == '@':
                    frame[idx] = chr(97 + _randint(0, 25))
                elif ch == '%':
                    if _random() < 0.6:
                        pass  # stays '.' (black)
                    else:
                        frame[idx] = chr(65 + _randint(0, 25))
                elif ch == '>':
                    frame[idx] = _i2c(1.0 - cycle_progress)
                elif ch == '<':
                    frame[idx] = _i2c(cycle_progress)
                elif ch == '*':
                    if _random() < 0.75:
                        frame[idx] = 'z'
                    # else stays '.' (black)
                elif 'a' <= ch <= 'z':
                    delay_fraction = (ord(ch) - 97) / 25
                    if delay_fraction <= 0 or cycle_progress >= delay_fraction:
                        frame[idx] = 'z'
                    else:
                        frame[idx] = _i2c(cycle_progress / delay_fraction)
                elif '0' <= ch <= '9':
                    # Digits map directly to palette: 0→a (dim), 9→z (bright)
                    frame[idx] = chr(97 + min(25, int((ord(ch) - 48) / 9 * 25)))
                # else stays '.'
        return bytes(''.join(frame), 'ascii')

    def PixelBuffer(self, cycle_progress: float, brightness: float = 1.0) -> list[int]:
        """Translate a baked frame string to packed neopixel ints via palette lookup.
        Returns the shared render buffer — caller must consume before the next PixelBuffer call.
        """
        start_profile(PROFILE_ANIM_ENSURE_PAL)
        CardAnimationHelpers.ensure_palettes(brightness)
        stop_profile(PROFILE_ANIM_ENSURE_PAL)

        start_profile(PROFILE_ANIM_RENDER)
        nf = len(self._frame_strings)
        frame_idx = int(cycle_progress * nf) % nf
        frame = self._frame_strings[frame_idx]

        buf = CardAnimationHelpers._render_buffer
        lut = CardAnimationHelpers._category_luts[self.category]

        for i in range(64):
            buf[i] = lut[frame[i]]
        stop_profile(PROFILE_ANIM_RENDER)

        return buf


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
