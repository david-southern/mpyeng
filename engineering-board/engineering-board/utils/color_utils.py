from micropython import const
import micropython

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


NEO_PACKED_BPP = const(3)

# NeoPixels typically use GRB order, but this can be changed if needed
NEOPIXEL_BYTE_OFFSET_R = const(1)
NEOPIXEL_BYTE_OFFSET_G = const(0)
NEOPIXEL_BYTE_OFFSET_B = const(2)

NEO_PACKED_OFFSET_R = const(8)
NEO_PACKED_OFFSET_G = const(16)
NEO_PACKED_OFFSET_B = const(0)


@micropython.viper
def copy_buffer_pixels(src_buffer: ptr8, dest_buffer: ptr8, dest_pixel_offset: int, pixel_count: int):  # pyright: ignore[reportUndefinedVariable] # noqa: F821
    """Copy <pixel_count> pixels from <src_buffer> to <dest_buffer> starting at <dest_pixel_offset>."""
    dest_byte_offset = dest_pixel_offset * NEO_PACKED_BPP
    byte_count = pixel_count * NEO_PACKED_BPP
    for byte_index in range(byte_count):
        dest_buffer[dest_byte_offset + byte_index] = src_buffer[byte_index]


def to_neo_packed(red: int, green: int, blue: int) -> int:
    """Convert the color to a single integer in the format expected by NeoPixel libraries."""
    return (
        ((red & 0xFF) << NEO_PACKED_OFFSET_R)
        | ((green & 0xFF) << NEO_PACKED_OFFSET_G)
        | ((blue & 0xFF) << NEO_PACKED_OFFSET_B)
    )


@micropython.viper
def neo_packed_to_buffer(neo_packed: int, buf: ptr8, pixel_index: int, pixel_count: int):  # pyright: ignore[reportUndefinedVariable] # noqa: F821
    """Convert a <neo_packed> color integer to its RGB components and write them into <buf> <count> times starting
    at <buf_index>."""
    byte_index: int = pixel_index * NEO_PACKED_BPP

    r: int = (neo_packed >> NEO_PACKED_OFFSET_R) & 0xFF
    g: int = (neo_packed >> NEO_PACKED_OFFSET_G) & 0xFF
    b: int = (neo_packed >> NEO_PACKED_OFFSET_B) & 0xFF

    if pixel_count == 1:
        buf[byte_index + NEOPIXEL_BYTE_OFFSET_R] = r
        buf[byte_index + NEOPIXEL_BYTE_OFFSET_G] = g
        buf[byte_index + NEOPIXEL_BYTE_OFFSET_B] = b
    else:
        for copy_index in range(pixel_count):
            buf[byte_index + NEOPIXEL_BYTE_OFFSET_R] = r
            buf[byte_index + NEOPIXEL_BYTE_OFFSET_G] = g
            buf[byte_index + NEOPIXEL_BYTE_OFFSET_B] = b
            byte_index += NEO_PACKED_BPP


def buffer_to_neo_packed(buf: bytearray, buf_index: int):
    """Return a neo_packed color integer from its RGB components in a bytearray buffer at the specified offset."""
    return (
        (buf[buf_index + NEOPIXEL_BYTE_OFFSET_R] << NEO_PACKED_OFFSET_R)
        | (buf[buf_index + NEOPIXEL_BYTE_OFFSET_G] << NEO_PACKED_OFFSET_G)
        | (buf[buf_index + NEOPIXEL_BYTE_OFFSET_B] << NEO_PACKED_OFFSET_B)
    )


def neo_packed_red(neo_packed: int) -> int:
    """Extract the red component from a neo_packed color integer."""
    return (neo_packed >> NEO_PACKED_OFFSET_R) & 0xFF


def neo_packed_green(neo_packed: int) -> int:
    """Extract the green component from a neo_packed color integer."""
    return (neo_packed >> NEO_PACKED_OFFSET_G) & 0xFF


def neo_packed_blue(neo_packed: int) -> int:
    """Extract the blue component from a neo_packed color integer."""
    return (neo_packed >> NEO_PACKED_OFFSET_B) & 0xFF


def hex_to_neo_packed(hex_color: str) -> int:
    """Convert a hex color string to a neo_packed int."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError("Hex color must be in the format #RRGGBB")
    return to_neo_packed(int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))


def lerp_neo_packed(start_neo_packed: int, end_neo_packed: int, progress: float) -> int:
    """Linearly interpolate between two neo_packed color integers."""
    r = int(
        neo_packed_red(start_neo_packed)
        + (neo_packed_red(end_neo_packed) - neo_packed_red(start_neo_packed)) * progress
    )
    g = int(
        neo_packed_green(start_neo_packed)
        + (neo_packed_green(end_neo_packed) - neo_packed_green(start_neo_packed)) * progress
    )
    b = int(
        neo_packed_blue(start_neo_packed)
        + (neo_packed_blue(end_neo_packed) - neo_packed_blue(start_neo_packed)) * progress
    )
    return to_neo_packed(r, g, b)


def scale_neo_packed(neo_packed: int, factor: float) -> int:
    return to_neo_packed(
        int(neo_packed_red(neo_packed) * factor),
        int(neo_packed_green(neo_packed) * factor),
        int(neo_packed_blue(neo_packed) * factor),
    )


BLACK: int = const(hex_to_neo_packed("#000000"))
WHITE: int = const(hex_to_neo_packed("#FFFFFF"))
RED: int = const(hex_to_neo_packed("#FF0000"))
GREEN: int = const(hex_to_neo_packed("#00FF00"))
BLUE: int = const(hex_to_neo_packed("#0000FF"))
CYAN: int = const(hex_to_neo_packed("#00FFFF"))
MAGENTA: int = const(hex_to_neo_packed("#FF00FF"))
YELLOW: int = const(hex_to_neo_packed("#FFFF00"))
