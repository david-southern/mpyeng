def to_neopixel(color: tuple[int, int, int] | "Color" | int) -> int:
    """Convert the color to a single integer in the format expected by NeoPixel libraries."""
    if isinstance(color, Color):
        return color.to_neopixel()
    elif isinstance(color, int):
        return color
    else:
        return (color[0] << 16) | (color[1] << 8) | color[2]


def hex_to_rgb(hex_color: str) -> list[int]:
    """Convert a hex color string to an (R, G, B) list."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError("Hex color must be in the format #RRGGBB")
    return [int(hex_color[i : i + 2], 16) for i in (0, 2, 4)]


class Color:
    def __init__(self, input_color: str | tuple[int, int, int] | "Color"):
        if isinstance(input_color, str):
            rgb = hex_to_rgb(input_color)
            self.R = self.clamp(rgb[0])
            self.G = self.clamp(rgb[1])
            self.B = self.clamp(rgb[2])
        elif isinstance(input_color, tuple):
            self.R = self.clamp(input_color[0])
            self.G = self.clamp(input_color[1])
            self.B = self.clamp(input_color[2])
        elif isinstance(input_color, Color):
            self.R = self.clamp(input_color.R)
            self.G = self.clamp(input_color.G)
            self.B = self.clamp(input_color.B)

    def clamp(self, value: int | float) -> int:
        return max(0, min(255, int(value)))

    def copy_from(self, other: "Color") -> "Color":
        self.R = other.R
        self.G = other.G
        self.B = other.B
        return self

    def set_rgb(self, r: int, g: int, b: int) -> "Color":
        self.R = r
        self.G = g
        self.B = b
        return self

    def lerp(self, end: "Color", progress: float) -> "Color":
        self.R = self.clamp(self.R + (end.R - self.R) * progress)
        self.G = self.clamp(self.G + (end.G - self.G) * progress)
        self.B = self.clamp(self.B + (end.B - self.B) * progress)
        return self

    def scale(self, factor: float) -> "Color":
        self.R = self.clamp(self.R * factor)
        self.G = self.clamp(self.G * factor)
        self.B = self.clamp(self.B * factor)
        return self

    def copy(self) -> "Color":
        return Color((self.R, self.G, self.B))

    def to_neopixel(self) -> int:
        """Convert the color to a single integer in the format expected by NeoPixel libraries."""
        return (self.R << 16) | (self.G << 8) | self.B

    def to_tuple(self) -> tuple[int, int, int]:
        """Convert the color to an (R, G, B) tuple."""
        return (self.R, self.G, self.B)


BLACK: Color = Color("#000000")
WHITE: Color = Color("#FFFFFF")
RED: Color = Color("#FF0000")
GREEN: Color = Color("#00FF00")
BLUE: Color = Color("#0000FF")
CYAN: Color = Color("#00FFFF")
MAGENTA: Color = Color("#FF00FF")
YELLOW: Color = Color("#FFFF00")
ORANGE: Color = Color("#FF9600")
PURPLE: Color = Color("#8C28FF")
