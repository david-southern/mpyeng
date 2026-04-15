from coloraide import Color

def css_to_ok(color: Color) -> Color:
    return color.convert("oklch")

def ok_to_css(color: Color) -> Color:
    return color.convert("srgb")


def lerp_color(start: Color, end: Color, progress: float) -> Color:
    lerp_func = Color.interpolate([start, end], space="oklch")
    return lerp_func(progress)

def steps(start: Color, end: Color, num_steps: int):
    return Color.steps([start, end], steps=num_steps)

def example():
    magenta = css_to_ok(Color("#ff00ff"))
    yellow = css_to_ok(Color("#ffff00"))

    print(f"Interpolation:")
    for i in range(10):
        t = i / 9
        color = lerp_color(magenta, yellow, t)
        print(f"Step {i:2d} (t={t:.1f}): {ok_to_css(color)}")

    print(f"Steps:")
    for i, color in enumerate(steps(magenta, yellow, 10)):
        print(f"Step {i:2d}: {ok_to_css(color)}")
