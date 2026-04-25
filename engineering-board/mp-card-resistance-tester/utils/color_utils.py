"""Utility functions for color manipulation, including conversions between different formats and
basic operations like clamping and interpolation. NOTE: these functions are designed to work with
RGB colors represented as packed ints (e.g., 0xRRGGBB), as using tuples (required by the vanilla
NeoPixel code) would be too slow for the performance-dependent parts of the codebase due to GC
thrashing caused by allocation of thousands of objects (tuples), which is extremely expensive. As
written, none of these function do any heap allocation, so they should be usable in basic NeoPixel
code without causing GC thrashing. Having said that, function calls in Python are also very
expensive, so for a tight animation loop, you should pre-bake your frame buffers so that the hot
path is just copying slices of byte arrays.
"""

# NeoPixels typically use GRB order, but this can be changed if needed
NEO_PACKED_PIXEL_OFFSETS = {
    "R": 8,
    "G": 16,
    "B": 0,
}


def to_neo_packed(red: int, green: int, blue: int) -> int:
    """Convert the color to a single integer in the format expected by NeoPixel libraries."""
    return (
        ((red & 0xFF) << NEO_PACKED_PIXEL_OFFSETS["R"])
        | ((green & 0xFF) << NEO_PACKED_PIXEL_OFFSETS["G"])
        | ((blue & 0xFF) << NEO_PACKED_PIXEL_OFFSETS["B"])
    )


def neo_packed_red(color: int) -> int:
    """Extract the red component from a neo_packed color integer."""
    return (color >> NEO_PACKED_PIXEL_OFFSETS["R"]) & 0xFF


def neo_packed_green(color: int) -> int:
    """Extract the green component from a neo_packed color integer."""
    return (color >> NEO_PACKED_PIXEL_OFFSETS["G"]) & 0xFF


def neo_packed_blue(color: int) -> int:
    """Extract the blue component from a neo_packed color integer."""
    return (color >> NEO_PACKED_PIXEL_OFFSETS["B"]) & 0xFF


def hex_to_neo_packed(hex_color: str) -> int:
    """Convert a hex color string to a neo_packed int."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError("Hex color must be in the format #RRGGBB")
    return to_neo_packed(int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))


def lerp(start: int, end: int, progress: float) -> int:
    """Linearly interpolate between two neo_packed color integers."""
    r = int(neo_packed_red(start) + (neo_packed_red(end) - neo_packed_red(start)) * progress)
    g = int(neo_packed_green(start) + (neo_packed_green(end) - neo_packed_green(start)) * progress)
    b = int(neo_packed_blue(start) + (neo_packed_blue(end) - neo_packed_blue(start)) * progress)
    return to_neo_packed(r, g, b)


def scale(color: int, factor: float) -> int:
    return to_neo_packed(
        int(neo_packed_red(color) * factor), int(neo_packed_green(color) * factor), int(neo_packed_blue(color) * factor)
    )


BLACK: int = hex_to_neo_packed("#000000")
WHITE: int = hex_to_neo_packed("#FFFFFF")
RED: int = hex_to_neo_packed("#FF0000")
GREEN: int = hex_to_neo_packed("#00FF00")
BLUE: int = hex_to_neo_packed("#0000FF")
CYAN: int = hex_to_neo_packed("#00FFFF")
MAGENTA: int = hex_to_neo_packed("#FF00FF")
YELLOW: int = hex_to_neo_packed("#FFFF00")
