from micropython import const
import micropython

"""Utility functions for color manipulation, including conversions between different formats and
basic operations like clamping and interpolation.

NOTE: pixel buffers are array.array('I') (one 32-bit unsigned int per pixel) in the project's
neo-packed layout (0x00GGRRBB). 4-byte alignment per pixel matches the PIO's 32-bit autopull —
sm.put(buf, 8) shifts the GRB bits into the upper 24 bits of each FIFO word, where the PIO program
shifts them out MSB-first to produce G, R, B on the wire (WS2812 order).

Functions here avoid heap allocation (no tuples, no per-pixel object creation) so they're safe to
call from animation hot paths without GC churn. For maximum throughput, prefer slice copies of
pre-baked buffers over per-pixel iteration in Python.
"""


# Bytes per pixel in the strip / animation buffer. One 32-bit packed int = 4 bytes per pixel
# (3 used for color, 1 padding, see neo-packed layout above).
NEO_PACKED_BPP = const(4)

# Bit offsets into a neo-packed color int (0x00GGRRBB).
NEO_PACKED_OFFSET_R = const(8)
NEO_PACKED_OFFSET_G = const(16)
NEO_PACKED_OFFSET_B = const(0)


@micropython.viper
def copy_buffer_pixels(src_buffer: ptr32, dest_buffer: ptr32, dest_pixel_offset: int, pixel_count: int):  # pyright: ignore[reportUndefinedVariable] # noqa: F821
    """Copy <pixel_count> packed-int pixels from <src_buffer> into <dest_buffer> starting at
    <dest_pixel_offset>. Both buffers must be 4-byte-aligned (array.array('I') is)."""
    i: int = 0
    while i < pixel_count:
        dest_buffer[dest_pixel_offset + i] = src_buffer[i]
        i += 1


def to_neo_packed(red: int, green: int, blue: int) -> int:
    """Convert RGB byte values to a neo-packed int (0x00GGRRBB)."""
    return (
        ((red & 0xFF) << NEO_PACKED_OFFSET_R)
        | ((green & 0xFF) << NEO_PACKED_OFFSET_G)
        | ((blue & 0xFF) << NEO_PACKED_OFFSET_B)
    )


@micropython.viper
def neo_packed_to_buffer(neo_packed: int, buf: ptr32, pixel_index: int, pixel_count: int):  # pyright: ignore[reportUndefinedVariable] # noqa: F821
    """Fill <pixel_count> entries of <buf> with <neo_packed>, starting at <pixel_index>."""
    i: int = 0
    while i < pixel_count:
        buf[pixel_index + i] = neo_packed
        i += 1


def buffer_to_neo_packed(buf, pixel_index: int) -> int:
    """Return the neo-packed int at <pixel_index> in <buf> (array.array('I'))."""
    return buf[pixel_index]


def neo_packed_red(neo_packed: int) -> int:
    """Extract the red component from a neo-packed color integer."""
    return (neo_packed >> NEO_PACKED_OFFSET_R) & 0xFF


def neo_packed_green(neo_packed: int) -> int:
    """Extract the green component from a neo-packed color integer."""
    return (neo_packed >> NEO_PACKED_OFFSET_G) & 0xFF


def neo_packed_blue(neo_packed: int) -> int:
    """Extract the blue component from a neo-packed color integer."""
    return (neo_packed >> NEO_PACKED_OFFSET_B) & 0xFF


def hex_to_neo_packed(hex_color: str) -> int:
    """Convert a hex color string to a neo-packed int."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError("Hex color must be in the format #RRGGBB")
    return to_neo_packed(int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))


def lerp_neo_packed(start_neo_packed: int, end_neo_packed: int, progress: float) -> int:
    """Linearly interpolate between two neo-packed color integers."""
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
