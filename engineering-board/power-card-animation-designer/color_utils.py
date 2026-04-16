import webcolors
from typing import Self

class Color:
    def __init__(self, input_color: str | tuple[int, int, int] | Self):
        if isinstance(input_color, str):
            rgb = webcolors.hex_to_rgb(input_color)
            self.R = max(0, min(255, rgb[0]))
            self.G = max(0, min(255, rgb[1]))
            self.B = max(0, min(255, rgb[2]))
        elif isinstance(input_color, tuple):
            self.R = max(0, min(255, input_color[0]))
            self.G = max(0, min(255, input_color[1]))
            self.B = max(0, min(255, input_color[2]))
        elif isinstance(input_color, Color):
            self.R = input_color.R
            self.G = input_color.G
            self.B = input_color.B 

    def lerp(self, end: Self, progress: float) -> Self:
        new_color = (
            int(self.R + (end.R - self.R) * progress),
            int(self.G + (end.G - self.G) * progress),
            int(self.B + (end.B - self.B) * progress)
        )
        return type(self)(new_color)
