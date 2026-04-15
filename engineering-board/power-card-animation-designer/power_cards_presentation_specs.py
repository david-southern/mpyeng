"""
power-card icon data and rendering helpers.

Each static image is an 8x8 tuple-of-tuples of (r, g, b) tuples.
Each animation is a tuple of 3-9 frames, where each frame is also an 8x8
tuple-of-tuples of (r, g, b) tuples.
"""

from coloraide import Color

import math
import random

from color_utils import lerp_color, ok_to_css

WIDTH = 8
HEIGHT = 8
PIXELS_PER_ICON = WIDTH * HEIGHT

OFF = Color("#000000")
POWER_SYSTEMS_COLOR = Color("#00B428")
DEFENSIVE_SYSTEMS_COLOR = Color("#005AFF")
WEAPONS_SYSTEMS_COLOR = Color("#FF2814")
PROPULSION_SYSTEMS_COLOR = Color("#FFAA00")
INFORMATION_SYSTEMS_COLOR = Color("#8C28FF")
UTILITY_SYSTEMS_COLOR = Color("#DCDCDC")

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

# Power card color_mask legend:
COLOR_MASK_BLACK = "." # transparent/black
COLOR_MASK_FULL_COLOR = "O" # solid color pixel (color defined in spec)
COLOR_MASK_DIM_COLOR = "o" # dimmer solid color pixel (color defined in spec, but rendered at 25-75% brightness)
COLOR_MASK_WAVE = "~" # animated "wave" pixel (cycle smoothly from O color to o color and back again)
COLOR_MASK_RANDOM_BRIGHTNESS = "x" # animated "random brightness" pixel (random flickering between the O color and the o color)
COLOR_MASK_RANDOM_COLOR = "X" # animated "random" pixel (random flickering rbg colors - each frame, each X pixel is a random color, with more time spent at black than the random color)
COLOR_MASK_FADE_OUT = "v" # animated "fade out" pixel (Start each animation cycle at the O color and smoothly fade to black at the end of the cycle)
COLOR_MASK_FADE_IN = "^" # animated "fade in" pixel (Start each animation cycle at black and smoothly fade to the O color)
COLOR_MASK_LIGHTNING = "*" # animated "lightning" pixel (Alternate (no smoothing, immediate transitions) between O color and black in a random pattern, with more time spent at O color than black) Power card
# * 1-9 = animated "delay" pixel (Start each animation cycle at black, wait for a delay of 10-90% of #   the animation duration, then smoothly transition to color_mask color by the end of the animation
#   duration)



DEFAULT_ANIMATION_DURATION = 3000  # milliseconds


class PowerCardSpec:
    def __init__(self, id: str, name: str, category: str, bright_color: Color, static_string_mask: list[str], dim_color: Color | None = None, animation_duration: int = DEFAULT_ANIMATION_DURATION):
        self.id = id
        self.name = name
        self.category = category
        self.bright_color = bright_color
        self.dim_color = dim_color if dim_color else lerp_color(bright_color, OFF, 0.3)
        self.static_mask = convert_string_mask_to_color_mask(static_string_mask, self.bright_color, self.dim_color, 0.0)
        self.animation_duration = animation_duration

    def render_frame(self):
        """Render one 8x8 RGB tuple frame to a NeoPixel object."""
        pixel_strip:list[tuple[int, int, int]] = [(0, 0, 0)] * len(self.static_mask)
        for idx, color in enumerate(self.static_mask):
            rgbColor = ok_to_css(color)
            rgbDict = rgbColor.to_dict()
            pixel_strip[idx] = (
                int(rgbDict["coords"][0] * 255),
                int(rgbDict["coords"][1] * 255),
                int(rgbDict["coords"][2] * 255),
            )

        return pixel_strip

def xy_to_index(x, y, flip_y = True, width=WIDTH, height=HEIGHT, layout="serpentine"):
    """Map x,y to a NeoPixel index.

    layout options:
      - "row-major": rows laid out left->right, top->bottom
      - "serpentine": even rows left->right, odd rows right->left
      - "column-major": columns laid out top->bottom, left->right

    flip_y: will flip the y axis (so y=0 is the bottom row instead of the top) - our card
      masks are laid out with y=0 at the top, but our NeoPixel grids have y=0 at the bottom, so this
      makes it easy to convert between them.
    """

    if(flip_y): y = height - 1 - y
    
    if layout == "row-major":
        return y * width + x
    if layout == "serpentine":
        return y * width + (x if y % 2 == 0 else (width - 1 - x))
    if layout == "column-major":
        return x * height + y
    raise ValueError("Unknown layout: {}".format(layout))

def convert_string_mask_to_color_mask(
    mask: list[str],
    bright_color: Color,
    dim_color: Color,
    cycle_progress: float,
) -> list[Color]:
    """Convert an 8x8 string mask to a flat list of Colors.

    Each character in the mask strings is mapped to a color based on the
    COLOR_MASK_* constants.  ``cycle_progress`` (0.0 - 1.0) drives all
    animated mask types.
    """
    result: list[Color] = [OFF] * PIXELS_PER_ICON
    for y in range(HEIGHT):
        for x in range(WIDTH):
            ch = mask[y][x]
            idx = xy_to_index(x, y)
            if ch == COLOR_MASK_BLACK:
                result[idx] = OFF
            elif ch == COLOR_MASK_FULL_COLOR:
                result[idx] = bright_color
            elif ch == COLOR_MASK_DIM_COLOR:
                result[idx] = dim_color
            elif ch == COLOR_MASK_WAVE:
                # Smooth ping-pong between bright and dim
                wave_t = 0.5 - 0.5 * math.cos(cycle_progress * 2 * math.pi)
                result[idx] = lerp_color(bright_color, dim_color, wave_t)
            elif ch == COLOR_MASK_RANDOM_BRIGHTNESS:
                # Random value between dim and bright each frame
                t = random.random()
                result[idx] = lerp_color(dim_color, bright_color, t)
            elif ch == COLOR_MASK_RANDOM_COLOR:
                # Random RGB flash, biased toward black
                if random.random() < 0.6:
                    result[idx] = OFF
                else:
                    result[idx] = Color(
                        "srgb",
                        [random.random(), random.random(), random.random()],
                    )
            elif ch == COLOR_MASK_FADE_OUT:
                # Bright -> black over the cycle
                result[idx] = lerp_color(bright_color, OFF, cycle_progress)
            elif ch == COLOR_MASK_FADE_IN:
                # Black -> bright over the cycle
                result[idx] = lerp_color(OFF, bright_color, cycle_progress)
            elif ch == COLOR_MASK_LIGHTNING:
                # Immediate random flicker, biased toward bright
                if random.random() < 0.75:
                    result[idx] = bright_color
                else:
                    result[idx] = OFF
            elif ch.isdigit() and "1" <= ch <= "9":
                # Delay pixel: stay black until delay%, then fade to bright
                delay_fraction = int(ch) / 10.0
                if cycle_progress < delay_fraction:
                    result[idx] = OFF
                else:
                    t = (cycle_progress - delay_fraction) / (1.0 - delay_fraction)
                    result[idx] = lerp_color(OFF, bright_color, t)
            else:
                result[idx] = OFF
    return result


ALL_CARD_IDS = [
    "fusion_engines",
    "warp_field",
    "main_computer",
    "fore_shields",
    "aft_shields",
    "port_shields",
    "starboard_shields",
    "dorsal_shields",
    "ventral_shields",
    "laser_cannon",
    "tractor_beam",
    "stealth_fields",
    "targeting",
    "signal_jammer",
    "alcubierre_warp_drive",
    "thrusters",
    "navigation",
    "external_sensors",
    "internal_sensors",
    "long_range_comms",
    "radio_communications",
    "transporters",
    "co2_scrubbers",
    "oxygen_generators",
    "gravity_field",
]


CARD_SPECS = [
    PowerCardSpec(
        id="fusion_engines",
        name="Fusion Engines",
        category="Power & Core Systems",
        bright_color=CATEGORY_COLORS["Power & Core Systems"],
        static_string_mask=[
            '........',
            '.o....o.',
            '..o..o..',
            '...oo...',
            '...OO...',
            '...OO...',
            '...OO...',
            '........',
        ],

    ),
    PowerCardSpec(
        id="warp_field",
        name="Warp Field",
        category="Power & Core Systems",
        bright_color=CATEGORY_COLORS["Power & Core Systems"],
        static_string_mask=[
            '..~~~~..',
            '.~....~.',
            '~..OO..~',
            '~.O..O.~',
            '~.O..O.~',
            '~..OO..~',
            '.~....~.',
            '..~~~~..',
        ],

    ),
    PowerCardSpec(
        id="main_computer",
        name="Main Computer",
        category="Power & Core Systems",
        bright_color=CATEGORY_COLORS["Power & Core Systems"],
        static_string_mask=[
            '..OOOO..',
            '.O....O.',
            'O.XXXX.O',
            'O.XXXX.O',
            'O.XXXX.O',
            'O.XXXX.O',
            '.O....O.',
            '..OOOO..',
        ],

    ),
    PowerCardSpec(
        id="fore_shields",
        name="Fore Shields",
        category="Defensive Systems",
        bright_color=CATEGORY_COLORS["Defensive Systems"],
        static_string_mask=[
            '..~~~~..',
            '.o....o.',
            '...OO...',
            '..O..O..',
            '..O..O..',
            '...OO...',
            '........',
            '........',
        ],

    ),
    PowerCardSpec(
        id="aft_shields",
        name="Aft Shields",
        category="Defensive Systems",
        bright_color=CATEGORY_COLORS["Defensive Systems"],
        static_string_mask=[
            '........',
            '........',
            '...OO...',
            '..O..O..',
            '..O..O..',
            '...OO...',
            '.o....o.',
            '..~~~~..',
        ],

    ),
    PowerCardSpec(
        id="port_shields",
        name="Port Shields",
        category="Defensive Systems",
        bright_color=CATEGORY_COLORS["Defensive Systems"],
        static_string_mask=[
            '........',
            '.o......',
            '~..OO...',
            '~.O..O..',
            '~.O..O..',
            '~..OO...',
            '.o......',
            '........',
        ],

    ),
    PowerCardSpec(
        id="starboard_shields",
        name="Starboard Shields",
        category="Defensive Systems",
        bright_color=CATEGORY_COLORS["Defensive Systems"],
        static_string_mask=[
            '........',
            '......o.',
            '...OO..~',
            '..O..O.~',
            '..O..O.~',
            '...OO..~',
            '......o.',
            '........',
        ],

    ),
    PowerCardSpec(
        id="dorsal_shields",
        name="Dorsal Shields",
        category="Defensive Systems",
        bright_color=CATEGORY_COLORS["Defensive Systems"],
        static_string_mask=[
            '........',
            '..OooO..',
            '.O.OO.O.',
            '.oOOOOo.',
            '.oOOOOo.',
            '.O.OO.O.',
            '..OooO..',
            '........',
        ],

    ),
    PowerCardSpec(
        id="ventral_shields",
        name="Ventral Shields",
        category="Defensive Systems",
        bright_color=CATEGORY_COLORS["Defensive Systems"],
        static_string_mask=[
            '........',
            '..oooo..',
            '.o.OO.o.',
            '.oO..Oo.',
            '.oO..Oo.',
            '.o.OO.o.',
            '..oooo..',
            '........',
        ],

    ),
    PowerCardSpec(
        id="laser_cannon",
        name="Laser Cannon",
        category="Weapons Systems",
        bright_color=CATEGORY_COLORS["Weapons Systems"],
        static_string_mask=[
            '.....OOO',
            '.....OOO',
            '.....*OO',
            '....*...',
            '....*...',
            '.9.*....',
            '87*9....',
            '7*78....',
        ],

    ),
    PowerCardSpec(
        id="tractor_beam",
        name="Tractor Beam",
        category="Weapons Systems",
        bright_color=CATEGORY_COLORS["Weapons Systems"],
        static_string_mask=[
            '..OOOO..',
            '...OO...',
            '...**...',
            '..*oo*..',
            '..*oo*..',
            '..*oo*..',
            '.*oooo*.',
            '.*oooo*.',
        ],
    ),
    PowerCardSpec(
        id="stealth_fields",
        name="Stealth Fields",
        category="Weapons Systems",
        bright_color=CATEGORY_COLORS["Weapons Systems"],
        static_string_mask=[
            '........',
            '...xx...',
            '.xxxxxx.',
            '.xxxxxx.',
            '.xxxxxx.',
            '.xxxxxx.',
            '...xx...',
            '........',
        ],

    ),
    PowerCardSpec(
        id="targeting",
        name="Targeting",
        category="Weapons Systems",
        bright_color=CATEGORY_COLORS["Weapons Systems"],
        static_string_mask=[
            '........',
            '..OOO...',
            '.o.o.o..',
            '.Oo.oO..',
            '.o.o.o..',
            '..OOO...',
            '........',
            '........',
        ],

    ),
    PowerCardSpec(
        id="signal_jammer",
        name="Signal Jammer",
        category="Weapons Systems",
        bright_color=CATEGORY_COLORS["Weapons Systems"],
        static_string_mask=[
            'XXXXXXXX',
            'XXXXXXXX',
            'XXXXXXXX',
            'XXXXXXXX',
            'XXXXXXXX',
            'XXXXXXXX',
            'XXXXXXXX',
            'XXXXXXXX',
        ],

    ),
    PowerCardSpec(
        id="alcubierre_warp_drive",
        name="Alcubierre Warp Drive",
        category="Propulsion & Movement",
        bright_color=CATEGORY_COLORS["Propulsion & Movement"],
        static_string_mask=[
            '..OOOO..',
            '.O.99.O.',
            'O..88..O',
            'O..77..O',
            'O..44..O',
            'O..22..O',
            '.O.11.O.',
            '..OOOO..',
        ],

    ),
    PowerCardSpec(
        id="thrusters",
        name="Thrusters",
        category="Propulsion & Movement",
        bright_color=CATEGORY_COLORS["Propulsion & Movement"],
        static_string_mask=[
            '...OO...',
            '...OO...',
            '...OO...',
            '...OO...',
            '..xoox..',
            '.xxooxx.',
            'xxxooxxx',
            '...oo...',
        ],

    ),
    PowerCardSpec(
        id="navigation",
        name="Navigation",
        category="Propulsion & Movement",
        bright_color=CATEGORY_COLORS["Propulsion & Movement"],
        static_string_mask=[
            '........',
            '........',
            '..O.....',
            '.OoO....',
            '..o.....',
            '..o..o..',
            '..ooooo.',
            '.....o..',
        ],

    ),
    PowerCardSpec(
        id="external_sensors",
        name="External Sensors",
        category="Information Systems",
        bright_color=CATEGORY_COLORS["Information Systems"],
        static_string_mask=[
            '..xxxx..',
            '.x....x.',
            'x......x',
            'x..OO..x',
            'x..OO..x',
            'x......x',
            '.x....x.',
            '..xxxx..',
        ],

    ),
    PowerCardSpec(
        id="internal_sensors",
        name="Internal Sensors",
        category="Information Systems",
        bright_color=CATEGORY_COLORS["Information Systems"],
        static_string_mask=[
            '........',
            '........',
            '...OO...',
            '..OxxO..',
            '..OxxO..',
            '...OO...',
            '........',
            '........',
        ],

    ),
    PowerCardSpec(
        id="long_range_comms",
        name="Long Range Comms",
        category="Information Systems",
        bright_color=CATEGORY_COLORS["Information Systems"],
        static_string_mask=[
            '..oOOo..',
            '.o....o.',
            '........',
            '...OO...',
            '..o..o..',
            '........',
            '...oo...',
            '...OO...',
        ],

    ),
    PowerCardSpec(
        id="radio_communications",
        name="Radio Communications",
        category="Information Systems",
        bright_color=CATEGORY_COLORS["Information Systems"],
        static_string_mask=[
            '........',
            '........',
            '........',
            '..oOOo..',
            '.o....o.',
            '...OO...',
            '..oooo..',
            '...OO...',
        ],

    ),
    PowerCardSpec(
        id="transporters",
        name="Transporters",
        category="Utility Systems",
        bright_color=CATEGORY_COLORS["Utility Systems"],
        static_string_mask=[
            '...OOO..',
            '...OOO..',
            '....o...',
            '.xxoooxx',
            '....x...',
            '...x.x..',
            '..x...x.',
            '..x...x.',
        ],

    ),
    PowerCardSpec(
        id="co2_scrubbers",
        name="CO2 Scrubbers",
        category="Utility Systems",
        bright_color=CATEGORY_COLORS["Utility Systems"],
        static_string_mask=[
            '.o.o.o.o',
            '.....O..',
            '.o.o.o.o',
            '.....O..',
            '.....O..',
            'o.o.oO..',
            '.o.o.o.o',
            '.....O..',
        ],

    ),
    PowerCardSpec(
        id="oxygen_generators",
        name="Oxygen Generators",
        category="Utility Systems",
        bright_color=CATEGORY_COLORS["Utility Systems"],
        static_string_mask=[
            '...OO...',
            '..OxxO..',
            '.OOOOOO.',
            '..OxxO..',
            '..OxxO..',
            '.OOOOOO.',
            '..OxxO..',
            '...OO...',
        ],

    ),
    PowerCardSpec(
        id="gravity_field",
        name="Gravity Field",
        category="Utility Systems",
        bright_color=CATEGORY_COLORS["Utility Systems"],
        static_string_mask=[
            '..OOOO..',
            '.O....O.',
            'O..~~..O',
            'O.~~~~.O',
            'O.~~~~.O',
            'O..~~..O',
            '.O....O.',
            '..OOOO..',
        ],

    ),
]
