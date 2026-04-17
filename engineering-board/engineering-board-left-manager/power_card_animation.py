import math
import random

from color_utils import Color
from power_card_categories import PowerCardCategories
from power_card_ids import PowerCardIds

class CardAnimationHelpers:
    WIDTH = 8
    HEIGHT = 8
    CARD_PIXEL_COUNT = WIDTH * HEIGHT
    PALETTE_SIZE = 26

    # Global LUT layout (256 bytes):
    #   Byte 0 = black
    #   Bytes 1-26   = category 0 palette (dim→bright, 26 levels)
    #   Bytes 27-52  = category 1 palette
    #   ...up to 6 categories (bytes 1-156)
    #   Bytes 157-182 = random color palette (26 entries)
    #   Bytes 183-255 = reserved
    BLACK_BYTE = 0
    RANDOM_PALETTE_OFFSET = 157

    POWER_SYSTEMS_COLOR = Color("#00B428")
    DEFENSIVE_SYSTEMS_COLOR = Color("#005AFF")
    WEAPONS_SYSTEMS_COLOR = Color("#FF2814")
    PROPULSION_SYSTEMS_COLOR = Color("#FF9600")
    INFORMATION_SYSTEMS_COLOR = Color("#8C28FF")
    UTILITY_SYSTEMS_COLOR = Color("#E8B998")
    
    # Color mask characters for cross-category pixels:
    # * '.' in color_mask = own category (default)
    # * 'P'= Power (green)
    # * 'D'= Defensive (blue)
    # * 'W'= Weapons (red)
    # * 'R'= Propulsion (orange)
    # * 'I'= Information (purple)
    # * 'U'= Utility (beige)
    #   '?'=random palette
    COLOR_MASK_CHARS: dict = {}  # char -> category_name (populated by register)

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
    __COS_LUT_SIZE = 64
    __COS_LUT = [int(128 - 128 * math.cos(i * 2 * math.pi / 64)) for i in range(64)]

    # Shared render buffer (single pre-allocated list, reused every frame)
    __render_buffer: list[int] = [0] * CARD_PIXEL_COUNT

    # Palette / LUT caches (regenerated when brightness changes)
    __global_lut: list[int] = [0] * 256
    __palette_brightness: float = -1.0
    __category_color_defs: dict = {}    # category_name -> (bright_Color, dim_Color)
    __category_offsets: dict = {}       # category_name -> int (byte offset into global LUT)
    __next_category_offset: int = 1     # next available byte offset (0 reserved for black)

    @classmethod
    def register_category_colors(cls, category: str, bright_color: Color, dim_color: Color, color_mask_char: str = ''):
        if category not in cls.__category_color_defs:
            cls.__category_color_defs[category] = (bright_color, dim_color)
            cls.__category_offsets[category] = cls.__next_category_offset
            cls.__next_category_offset += cls.PALETTE_SIZE
            if color_mask_char:
                cls.COLOR_MASK_CHARS[color_mask_char] = category

    @classmethod
    def get_category_offset(cls, category: str) -> int:
        return cls.__category_offsets[category]

    @classmethod
    def __regenerate_palettes(cls, brightness: float):
        ps = cls.PALETTE_SIZE
        ps_1 = ps - 1
        lut = cls.__global_lut
        lut[0] = 0  # black

        for cat_name, (bright, dim) in cls.__category_color_defs.items():
            offset = cls.__category_offsets[cat_name]
            br, bg, bb = bright.R, bright.G, bright.B
            dr, dg, db = dim.R, dim.G, dim.B
            for i in range(ps):
                t = i / ps_1
                r = int((dr + (br - dr) * t) * brightness)
                g = int((dg + (bg - dg) * t) * brightness)
                b = int((db + (bb - db) * t) * brightness)
                lut[offset + i] = (r << 16) | (g << 8) | b

        rp_offset = cls.RANDOM_PALETTE_OFFSET
        for i in range(ps):
            r = int(random.random() * 255 * brightness)
            g = int(random.random() * 255 * brightness)
            b = int(random.random() * 255 * brightness)
            lut[rp_offset + i] = (r << 16) | (g << 8) | b

        cls.__palette_brightness = brightness

    @classmethod
    def ensure_palettes(cls, brightness: float):
        if cls.__palette_brightness != brightness:
            cls.__regenerate_palettes(brightness)

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
    
    def __init__(self, uid: str, name: str, category: str, bright_color: Color, pixel_mask: list[str], dim_color: Color | None = None, animation_duration: float = CardAnimationHelpers.DEFAULT_ANIMATION_DURATION, color_mask: list[str] | None = None):
        self.id = uid
        self.name = name
        self.category = category
        self.bright_color = bright_color
        self.dim_color = dim_color if dim_color else bright_color.copy().scale(PowerCardAnimation.DIM_BRIGHTNESS)
        self.pixel_mask = pixel_mask
        self.color_mask = color_mask
        self.animation_duration = animation_duration

        # Register category for shared palette generation
        CardAnimationHelpers.register_category_colors(category, bright_color, self.dim_color)

        # Pre-compute per-pixel palette offsets (64 ints in serpentine order)
        # Each entry is the byte offset into the global LUT for that pixel's category
        mask_h = len(pixel_mask)
        mask_w = len(pixel_mask[0]) if mask_h > 0 else 0
        own_offset = CardAnimationHelpers.get_category_offset(category)
        rp_offset = CardAnimationHelpers.RANDOM_PALETTE_OFFSET
        self.__pixel_offsets: list[int] = [own_offset] * (mask_w * mask_h)

        if color_mask:
            color_mask_chars = CardAnimationHelpers.COLOR_MASK_CHARS
            cat_offsets = CardAnimationHelpers.__category_offsets
            for y in range(mask_h):
                for x in range(mask_w):
                    cm_ch = color_mask[y][x]
                    if cm_ch == '.':
                        pass  # own category, already set
                    elif cm_ch == '?':
                        idx = CardAnimationHelpers.xy_to_index(x, y, width=mask_w, height=mask_h)
                        self.__pixel_offsets[idx] = rp_offset
                    elif cm_ch in color_mask_chars:
                        idx = CardAnimationHelpers.xy_to_index(x, y, width=mask_w, height=mask_h)
                        self.__pixel_offsets[idx] = cat_offsets[color_mask_chars[cm_ch]]

        # Determine frame count: 1 for fully static masks, 10 for animated
        has_animated = False
        for row in pixel_mask:
            for ch in row:
                if ch in CardAnimationHelpers.ANIMATED_MASK_CHARS or ('a' <= ch <= 'z'):
                    has_animated = True
                    break
            if has_animated:
                break
        num_frames = 10 if has_animated else 1

        # Bake frame bytes (each is 64 bytes in serpentine pixel order)
        # Byte values are direct indices into the global LUT
        self.__frame_bytes: list[bytes] = []
        for fi in range(num_frames):
            self.__frame_bytes.append(
                self.__bake_frame(fi, num_frames, mask_w, mask_h)
            )

    @staticmethod
    def __intensity_to_palette_index(f: float) -> int:
        """Map intensity fraction (0.0-1.0) to a palette index (0-25).
        Returns -1 for black (below DIM_BRIGHTNESS threshold).
        """
        dim = PowerCardAnimation.DIM_BRIGHTNESS
        if f < dim:
            return -1
        return min(25, int((f - dim) / (1.0 - dim) * 25))

    def __bake_frame(self, frame_index: int, num_frames: int, mask_w: int, mask_h: int) -> bytes:
        cycle_progress = frame_index / num_frames
        n = mask_w * mask_h
        frame = bytearray(n)  # all zeros = BLACK_BYTE

        # Pre-compute wave palette index for this frame
        cos_lut = CardAnimationHelpers.__COS_LUT
        cos_size = CardAnimationHelpers.__COS_LUT_SIZE
        wave_lut_val = cos_lut[int(cycle_progress * cos_size) % cos_size]
        wave_pal_idx = 25 - min(25, (wave_lut_val * 25) >> 8)

        _random = random.random
        _randint = random.randint
        _i2pi = PowerCardAnimation.__intensity_to_palette_index
        pixel_offsets = self.__pixel_offsets
        rp_offset = CardAnimationHelpers.RANDOM_PALETTE_OFFSET
        black = CardAnimationHelpers.BLACK_BYTE

        for y in range(mask_h):
            for x in range(mask_w):
                ch = self.pixel_mask[y][x]
                if ch == '.':
                    continue  # stays BLACK_BYTE (0)
                idx = CardAnimationHelpers.xy_to_index(x, y, width=mask_w, height=mask_h)
                offset = pixel_offsets[idx]
                if ch == '~':
                    frame[idx] = offset + wave_pal_idx
                elif ch == '@':
                    frame[idx] = offset + _randint(0, 25)
                elif ch == '%':
                    if _random() >= 0.6:
                        frame[idx] = rp_offset + _randint(0, 25)
                    # else stays BLACK_BYTE
                elif ch == '>':
                    pi = _i2pi(1.0 - cycle_progress)
                    frame[idx] = (offset + pi) if pi >= 0 else black
                elif ch == '<':
                    pi = _i2pi(cycle_progress)
                    frame[idx] = (offset + pi) if pi >= 0 else black
                elif ch == '*':
                    if _random() < 0.75:
                        frame[idx] = offset + 25  # brightest
                    # else stays BLACK_BYTE
                elif 'a' <= ch <= 'z':
                    delay_fraction = (ord(ch) - 97) / 25
                    if delay_fraction <= 0 or cycle_progress >= delay_fraction:
                        frame[idx] = offset + 25  # brightest
                    else:
                        pi = _i2pi(cycle_progress / delay_fraction)
                        frame[idx] = (offset + pi) if pi >= 0 else black
                elif '0' <= ch <= '9':
                    frame[idx] = offset + min(25, int((ord(ch) - 48) / 9 * 25))

        return bytes(frame)

    def PixelBuffer(self, cycle_progress: float, brightness: float = 1.0) -> list[int]:
        """Translate baked frame bytes to packed neopixel ints via global LUT lookup.
        Returns the shared render buffer — caller must consume before the next PixelBuffer call.
        """
        CardAnimationHelpers.ensure_palettes(brightness)

        nf = len(self.__frame_bytes)
        frame_idx = int(cycle_progress * nf) % nf
        frame = self.__frame_bytes[frame_idx]

        buf = CardAnimationHelpers.__render_buffer
        lut = CardAnimationHelpers.__global_lut

        for i in range(64):
            buf[i] = lut[frame[i]]

        return buf


# Pre-register all categories with their color_mask characters so that
# color_mask grids can reference any category by single letter.
# DIM_BRIGHTNESS scaling applied automatically per category.
_dim = PowerCardAnimation.DIM_BRIGHTNESS
for _cat_name, _color, _char in [
    (PowerCardCategories.POWER_SYSTEMS_CATEGORY_NAME,       PowerCardCategories.POWER_SYSTEMS_COLOR,       'P'),
    (PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME,   PowerCardCategories.DEFENSIVE_SYSTEMS_COLOR,   'D'),
    (PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME,     PowerCardCategories.WEAPONS_SYSTEMS_COLOR,     'W'),
    (PowerCardCategories.PROPULSION_SYSTEMS_CATEGORY_NAME,  PowerCardCategories.PROPULSION_SYSTEMS_COLOR,  'R'),
    (PowerCardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME, PowerCardCategories.INFORMATION_SYSTEMS_COLOR, 'I'),
    (PowerCardCategories.UTILITY_SYSTEMS_CATEGORY_NAME,     PowerCardCategories.UTILITY_SYSTEMS_COLOR,     'U'),
]:
    CardAnimationHelpers.register_category_colors(_cat_name, _color, _color.copy().scale(_dim), _char)


CARD_ANIMATION_DEFS = {
    PowerCardIds.FUSION_ENGINES_ID: PowerCardAnimation(
        uid=PowerCardIds.FUSION_ENGINES_ID,
        name="Fusion Engines",
        category=PowerCardCategories.POWER_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.POWER_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '........',
            '.2....2.',
            '..2..2..',
            '...44...',
            '...77...',
            '...99...',
            '...99...',
            '........',
        ],
        color_mask=[
            '........',
            '.P....P.',
            '..P..P..',
            '...PP...',
            '...PP...',
            '...PP...',
            '...PP...',
            '........',
        ],

    ),
    PowerCardIds.WARP_FIELD_ID: PowerCardAnimation(
        uid=PowerCardIds.WARP_FIELD_ID,
        name="Warp Field",
        category=PowerCardCategories.POWER_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.POWER_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '..~~~~..',
            '.~....~.',
            '~..99..~',
            '~.9..9.~',
            '~.9..9.~',
            '~..99..~',
            '.~....~.',
            '..~~~~..',
        ],
        color_mask=[
            '..PPPP..',
            '.P....P.',
            'P..PP..P',
            'P.P..P.P',
            'P.P..P.P',
            'P..PP..P',
            '.P....P.',
            '..PPPP..',
        ],

    ),
    PowerCardIds.MAIN_COMPUTER_ID: PowerCardAnimation(
        uid=PowerCardIds.MAIN_COMPUTER_ID,
        name="Main Computer",
        category=PowerCardCategories.POWER_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.POWER_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '..9999..',
            '.9....9.',
            '9.%%%%.9',
            '9.%%%%.9',
            '9.%%%%.9',
            '9.%%%%.9',
            '.9....9.',
            '..9999..',
        ],
        color_mask=[
            '..PPPP..',
            '.P....P.',
            'P.PPPP.P',
            'P.PPPP.P',
            'P.PPPP.P',
            'P.PPPP.P',
            '.P....P.',
            '..PPPP..',
        ],

    ),
    PowerCardIds.FORE_SHIELDS_ID: PowerCardAnimation(
        uid=PowerCardIds.FORE_SHIELDS_ID,
        name="Fore Shields",
        category=PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '..~~~~..',
            '.3....3.',
            '...99...',
            '..9999..',
            '..9999..',
            '...99...',
            '........',
            '........',
        ],
        color_mask=[
            '..DDDD..',
            '.D....D.',
            '...DD...',
            '..DDDD..',
            '..DDDD..',
            '...DD...',
            '........',
            '........',
        ],

    ),
    PowerCardIds.AFT_SHIELDS_ID: PowerCardAnimation(
        uid=PowerCardIds.AFT_SHIELDS_ID,
        name="Aft Shields",
        category=PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '........',
            '........',
            '...99...',
            '..9999..',
            '..9999..',
            '...99...',
            '.3....3.',
            '..~~~~..',
        ],
        color_mask=[
            '........',
            '........',
            '...DD...',
            '..DDDD..',
            '..DDDD..',
            '...DD...',
            '.D....D.',
            '..DDDD..',
        ],

    ),
    PowerCardIds.PORT_SHIELDS_ID: PowerCardAnimation(
        uid=PowerCardIds.PORT_SHIELDS_ID,
        name="Port Shields",
        category=PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '........',
            '.3......',
            '~..99...',
            '~.9999..',
            '~.9999..',
            '~..99...',
            '.3......',
            '........',
        ],
        color_mask=[
            '........',
            '.D......',
            'D..DD...',
            'D.DDDD..',
            'D.DDDD..',
            'D..DD...',
            '.D......',
            '........',
        ],

    ),
    PowerCardIds.STARBOARD_SHIELDS_ID: PowerCardAnimation(
        uid=PowerCardIds.STARBOARD_SHIELDS_ID,
        name="Starboard Shields",
        category=PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '........',
            '......3.',
            '...99..~',
            '..9999.~',
            '..9999.~',
            '...99..~',
            '......3.',
            '........',
        ],
        color_mask=[
            '........',
            '......D.',
            '...DD..D',
            '..DDDD.D',
            '..DDDD.D',
            '...DD..D',
            '......D.',
            '........',
        ],

    ),
    PowerCardIds.DORSAL_SHIELDS_ID: PowerCardAnimation(
        uid=PowerCardIds.DORSAL_SHIELDS_ID,
        name="Dorsal Shields",
        category=PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '........',
            '..~~~~..',
            '.~~~~~~.',
            '.~~~~~~.',
            '.~~~~~~.',
            '.~~~~~~.',
            '..~~~~..',
            '........',
        ],
        color_mask=[
            '........',
            '..DDDD..',
            '.DDDDDD.',
            '.DDDDDD.',
            '.DDDDDD.',
            '.DDDDDD.',
            '..DDDD..',
            '........',
        ],

    ),
    PowerCardIds.VENTRAL_SHIELDS_ID: PowerCardAnimation(
        uid=PowerCardIds.VENTRAL_SHIELDS_ID,
        name="Ventral Shields",
        category=PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '........',
            '..~~~~..',
            '.~~99~~.',
            '.~9999~.',
            '.~9999~.',
            '.~~99~~.',
            '..~~~~..',
            '........',
        ],
        color_mask=[
            '........',
            '..DDDD..',
            '.DDDDDD.',
            '.DDDDDD.',
            '.DDDDDD.',
            '.DDDDDD.',
            '..DDDD..',
            '........',
        ],

    ),
    PowerCardIds.LASER_CANNON_ID: PowerCardAnimation(
        uid=PowerCardIds.LASER_CANNON_ID,
        name="Laser Cannon",
        category=PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '.....999',
            '.....999',
            '......99',
            '....a...',
            '....a...',
            'f..b....',
            'edc.f...',
            'dcde....',
        ],
        color_mask=[
            '.....WWW',
            '.....WWW',
            '......WW',
            '....W...',
            '....W...',
            'W..W....',
            'WWW.W...',
            'WWWW....',
        ],
        animation_duration=1.5
    ),
    PowerCardIds.TRACTOR_BEAM_ID: PowerCardAnimation(
        uid=PowerCardIds.TRACTOR_BEAM_ID,
        name="Tractor Beam",
        category=PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '..9999..',
            '...99...',
            '...**...',
            '..*33*..',
            '..*44*..',
            '..*55*..',
            '.*6666*.',
            '.*6666*.',
        ],
        color_mask=[
            '..WWWW..',
            '...WW...',
            '...WW...',
            '..WWWW..',
            '..WWWW..',
            '..WWWW..',
            '.WWWWWW.',
            '.WWWWWW.',
        ],
    ),
    PowerCardIds.STEALTH_FIELDS_ID: PowerCardAnimation(
        uid=PowerCardIds.STEALTH_FIELDS_ID,
        name="Stealth Fields",
        category=PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '........',
            '..@@@@..',
            '.@@@@@@.',
            '.@@@@@@.',
            '.@@@@@@.',
            '.@@@@@@.',
            '..@@@@..',
            '........',
        ],
        color_mask=[
            '........',
            '..WWWW..',
            '.WWWWWW.',
            '.WWWWWW.',
            '.WWWWWW.',
            '.WWWWWW.',
            '..WWWW..',
            '........',
        ],

    ),
    PowerCardIds.TARGETING_ID: PowerCardAnimation(
        uid=PowerCardIds.TARGETING_ID,
        name="Targeting",
        category=PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '........',
            '..999...',
            '...2....',
            '.92.29..',
            '...2....',
            '..999...',
            '........',
            '........',
        ],
        color_mask=[
            '........',
            '..WWW...',
            '...W....',
            '.WW.WW..',
            '...W....',
            '..WWW...',
            '........',
            '........',
        ],

    ),
    PowerCardIds.SIGNAL_JAMMER_ID: PowerCardAnimation(
        uid=PowerCardIds.SIGNAL_JAMMER_ID,
        name="Signal Jammer",
        category=PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '%%%%%%%%',
            '%%%%%%%%',
            '%%%%%%%%',
            '%%%%%%%%',
            '%%%%%%%%',
            '%%%%%%%%',
            '%%%%%%%%',
            '%%%%%%%%',
        ],
        color_mask=[
            'WWWWWWWW',
            'WWWWWWWW',
            'WWWWWWWW',
            'WWWWWWWW',
            'WWWWWWWW',
            'WWWWWWWW',
            'WWWWWWWW',
            'WWWWWWWW',
        ],

    ),
    PowerCardIds.ALCUBIERRE_WARP_DRIVE_ID: PowerCardAnimation(
        uid=PowerCardIds.ALCUBIERRE_WARP_DRIVE_ID,
        name="Alcubierre Warp Drive",
        category=PowerCardCategories.PROPULSION_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.PROPULSION_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '..9999..',
            '.9.yy.9.',
            '9..xx..9',
            '9..vv..9',
            '9..ss..9',
            '9..mm..9',
            '.9.aa.9.',
            '..9999..',
        ],
        color_mask=[
            '..RRRR..',
            '.R.RR.R.',
            'R..RR..R',
            'R..RR..R',
            'R..RR..R',
            'R..RR..R',
            '.R.RR.R.',
            '..RRRR..',
        ],

    ),
    PowerCardIds.THRUSTERS_ID: PowerCardAnimation(
        uid=PowerCardIds.THRUSTERS_ID,
        name="Thrusters",
        category=PowerCardCategories.PROPULSION_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.PROPULSION_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '..3333..',
            '...33...',
            '...99...',
            '...99...',
            '..@66@..',
            '.@@33@@.',
            '@@@@@@@@',
            '...@@...',
        ],
        color_mask=[
            '..RRRR..',
            '...RR...',
            '...RR...',
            '...RR...',
            '..RRRR..',
            '.RRRRRR.',
            'RRRRRRRR',
            '...RR...',
        ],

    ),
    PowerCardIds.NAVIGATION_ID: PowerCardAnimation(
        uid=PowerCardIds.NAVIGATION_ID,
        name="Navigation",
        category=PowerCardCategories.PROPULSION_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.PROPULSION_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '........',
            '........',
            '..9.....',
            '.929....',
            '..2.....',
            '..2..1..',
            '..22221.',
            '.....1..',
        ],
        color_mask=[
            '........',
            '........',
            '..R.....',
            '.RRR....',
            '..R.....',
            '..R..R..',
            '..RRRRR.',
            '.....R..',
        ],

    ),
    PowerCardIds.EXTERNAL_SENSORS_ID: PowerCardAnimation(
        uid=PowerCardIds.EXTERNAL_SENSORS_ID,
        name="External Sensors",
        category=PowerCardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '..@@@@..',
            '.@....@.',
            '@......@',
            '@..99..@',
            '@..99..@',
            '@......@',
            '.@....@.',
            '..@@@@..',
        ],
        color_mask=[
            '..IIII..',
            '.I....I.',
            'I......I',
            'I..II..I',
            'I..II..I',
            'I......I',
            '.I....I.',
            '..IIII..',
        ],

    ),
    PowerCardIds.INTERNAL_SENSORS_ID: PowerCardAnimation(
        uid=PowerCardIds.INTERNAL_SENSORS_ID,
        name="Internal Sensors",
        category=PowerCardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '........',
            '........',
            '...99...',
            '..9@@9..',
            '..9@@9..',
            '...99...',
            '........',
            '........',
        ],
        color_mask=[
            '........',
            '........',
            '...II...',
            '..IIII..',
            '..IIII..',
            '...II...',
            '........',
            '........',
        ],

    ),
    PowerCardIds.LONG_RANGE_COMMS_ID: PowerCardAnimation(
        uid=PowerCardIds.LONG_RANGE_COMMS_ID,
        name="Long Range Comms",
        category=PowerCardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '..6996..',
            '.3....3.',
            '........',
            '...77...',
            '..5..5..',
            '........',
            '...55...',
            '...99...',
        ],
        color_mask=[
            '..IIII..',
            '.I....I.',
            '........',
            '...II...',
            '..I..I..',
            '........',
            '...II...',
            '...II...',
        ],

    ),
    PowerCardIds.RADIO_COMMUNICATIONS_ID: PowerCardAnimation(
        uid=PowerCardIds.RADIO_COMMUNICATIONS_ID,
        name="Radio Communications",
        category=PowerCardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '........',
            '........',
            '........',
            '..7997..',
            '.5....5.',
            '...66...',
            '..2442..',
            '...99...',
        ],
        color_mask=[
            '........',
            '........',
            '........',
            '..IIII..',
            '.I....I.',
            '...II...',
            '..IIII..',
            '...II...',
        ],

    ),
    PowerCardIds.TRANSPORTERS_ID: PowerCardAnimation(
        uid=PowerCardIds.TRANSPORTERS_ID,
        name="Transporters",
        category=PowerCardCategories.UTILITY_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.UTILITY_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '...999..',
            '...777..',
            '....5...',
            '.@@333@@',
            '....@...',
            '...@.@..',
            '..@...@.',
            '..@...@.',
        ],
        color_mask=[
            '...RRR..',
            '...UUU..',
            '....W...',
            '.UWWWWWU',
            '....W...',
            '...U.U..',
            '..U...U.',
            '..U...U.',
        ],

    ),
    PowerCardIds.CO2_SCRUBBERS_ID: PowerCardAnimation(
        uid=PowerCardIds.CO2_SCRUBBERS_ID,
        name="CO2 Scrubbers",
        category=PowerCardCategories.UTILITY_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.UTILITY_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '@7@7@7@7',
            '.....9..',
            '........',
            '3@3@39..',
            '........',
            '3@3@39..',
            '@7@7@7@7',
            '.....9..',
        ],
        color_mask=[
            'UUUUUUUU',
            '.....U..',
            '........',
            'UUUUUU..',
            '........',
            'UUUUUU..',
            'UUUUUUUU',
            '.....U..',
        ],

    ),
    PowerCardIds.OXYGEN_GENERATORS_ID: PowerCardAnimation(
        uid=PowerCardIds.OXYGEN_GENERATORS_ID,
        name="Oxygen Generators",
        category=PowerCardCategories.UTILITY_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.UTILITY_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '...99...',
            '..9@@9..',
            '.555555.',
            '..9@@9..',
            '..9@@9..',
            '.555555.',
            '..9@@9..',
            '...99...',
        ],
        color_mask=[
            '...UU...',
            '..UUUU..',
            '.UUUUUU.',
            '..UUUU..',
            '..UUUU..',
            '.UUUUUU.',
            '..UUUU..',
            '...UU...',
        ],

    ),
    PowerCardIds.GRAVITY_FIELD_ID: PowerCardAnimation(
        uid=PowerCardIds.GRAVITY_FIELD_ID,
        name="Gravity Field",
        category=PowerCardCategories.UTILITY_SYSTEMS_CATEGORY_NAME,
        bright_color=PowerCardCategories.CATEGORY_COLORS[PowerCardCategories.UTILITY_SYSTEMS_CATEGORY_NAME],
        pixel_mask=[
            '..9999..',
            '.9~~~~9.',
            '9~~~~~~9',
            '9~~~~~~9',
            '9~~~~~~9',
            '9~~~~~~9',
            '.9~~~~9.',
            '..9999..',
        ],
        color_mask=[
            '..UUUU..',
            '.UUUUUU.',
            'UUUUUUUU',
            'UUUUUUUU',
            'UUUUUUUU',
            'UUUUUUUU',
            '.UUUUUU.',
            '..UUUU..',
        ],

    ),
}
