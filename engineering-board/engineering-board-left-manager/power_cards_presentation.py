"""
CircuitPython power-card icon data and NeoPixel rendering helpers.

Each static image is an 8x8 tuple-of-tuples of (r, g, b) tuples.
Each animation is a tuple of 3-9 frames, where each frame is also an 8x8
tuple-of-tuples of (r, g, b) tuples.

Generated for the STEM power-distribution prop.
"""

from micropython import const
import neopixel
import time
import random

WIDTH = const(8)
HEIGHT = const(8)
PIXELS_PER_ICON = const(WIDTH * HEIGHT)

OFF = (0, 0, 0)

CATEGORY_COLORS = {
    "Power & Core Systems": (0, 180, 40),
    "Defensive Systems": (0, 90, 255),
    "Weapons Systems": (255, 40, 20),
    "Propulsion & Movement": (255, 170, 0),
    "Information Systems": (140, 40, 255),
    "Utility Systems": (220, 220, 220),
}

CARD_SPECS = [
    {"id": "fusion_engines", "name": "Fusion Engines", "category": "Power & Core Systems", "color": (0, 180, 40), "mask": ('........', '........', '..O..O..', '...OO...', '...OO...', '........', '........', '........'), "animation": "fusion"},
    {"id": "warp_field", "name": "Warp Field", "category": "Power & Core Systems", "color": (0, 180, 40), "mask": ('..OOOO..', '.O....O.', 'O..OO..O', 'O.O..O.O', 'O.O..O.O', 'O..OO..O', '.O....O.', '..OOOO..'), "animation": "warp"},
    {"id": "main_computer", "name": "Main Computer", "category": "Power & Core Systems", "color": (0, 180, 40), "mask": ('..OOOO..', '.O....O.', 'O.O.O..O', 'O..O.O.O', 'O.O.O..O', 'O..O.O.O', '.O....O.', '..OOOO..'), "animation": "computer"},
    {"id": "fore_shields", "name": "Fore Shields", "category": "Defensive Systems", "color": (0, 90, 255), "mask": ('..OOOO..', '........', '...OO...', '..O..O..', '..O..O..', '...OO...', '........', '........'), "animation": "shield_fore"},
    {"id": "aft_shields", "name": "Aft Shields", "category": "Defensive Systems", "color": (0, 90, 255), "mask": ('........', '........', '...OO...', '..O..O..', '..O..O..', '...OO...', '........', '..OOOO..'), "animation": "shield_aft"},
    {"id": "port_shields", "name": "Port Shields", "category": "Defensive Systems", "color": (0, 90, 255), "mask": ('........', '........', 'OO.OO...', 'O.O..O..', 'OO......', '...OO...', '........', '........'), "animation": "shield_port"},
    {"id": "starboard_shields", "name": "Starboard Shields", "category": "Defensive Systems", "color": (0, 90, 255), "mask": ('........', '........', '...OO.OO', '..O..O.O', '......OO', '...OO...', '........', '........'), "animation": "shield_starboard"},
    {"id": "dorsal_shields", "name": "Dorsal Shields", "category": "Defensive Systems", "color": (0, 90, 255), "mask": ('...OO...', '...OO...', '...OO...', '..O..O..', '..O..O..', '...OO...', '...OO...', '...OO...'), "animation": "shield_dorsal"},
    {"id": "ventral_shields", "name": "Ventral Shields", "category": "Defensive Systems", "color": (0, 90, 255), "mask": ('........', '........', '...OO...', '..O..O..', 'OOOOOOOO', '...OO...', '........', '........'), "animation": "shield_ventral"},
    {"id": "laser_cannon", "name": "Laser Cannon", "category": "Weapons Systems", "color": (255, 40, 20), "mask": ('....OOOO', '.....OOO', '......OO', '.......O', '........', '........', '........', '.OOOOOO.'), "animation": "laser"},
    {"id": "tractor_beam", "name": "Tractor Beam", "category": "Weapons Systems", "color": (255, 40, 20), "mask": ('..OOOOOO', '.OOOOOOO', '...OO...', '..OOOO..', '.OOOOOO.', 'OOOOOOOO', 'OOOOOOOO', 'OOOOOOOO'), "animation": "tractor"},
    {"id": "stealth_fields", "name": "Stealth Fields", "category": "Weapons Systems", "color": (255, 40, 20), "mask": ('...OO...', '..O..O..', '.O.O.O.O', '........', '........', '.O.O.O.O', '..O..O..', '...OO...'), "animation": "stealth"},
    {"id": "targeting", "name": "Targeting", "category": "Weapons Systems", "color": (255, 40, 20), "mask": ('...O....', '..O.O...', '.O...O..', 'O..O..O.', '.O...O..', '..O.O...', '...O....', '...O....'), "animation": "targeting"},
    {"id": "signal_jammer", "name": "Signal Jammer", "category": "Weapons Systems", "color": (255, 40, 20), "mask": ('...OO...', '..O..O..', '.O.O.O.O', '...OO...', '...OO...', '.O.O.O.O', '..O..O..', '...OO...'), "animation": "jammer"},
    {"id": "alcubierre_warp_drive", "name": "Alcubierre Warp Drive", "category": "Propulsion & Movement", "color": (255, 170, 0), "mask": ('..OOOO..', '.O....O.', 'O..OO..O', 'O..OO..O', 'O..OO..O', 'O..OO..O', '.O....O.', '..OOOO..'), "animation": "alcubierre"},
    {"id": "thrusters", "name": "Thrusters", "category": "Propulsion & Movement", "color": (255, 170, 0), "mask": ('...OO...', '...OO...', '...OO...', '...OO...', '..OOOO..', '.O.OO.O.', '...OO...', '........'), "animation": "thrusters"},
    {"id": "navigation", "name": "Navigation", "category": "Propulsion & Movement", "color": (255, 170, 0), "mask": ('...OO...', '..O..O..', '.O....O.', '...O....', '..O.O...', '.O....O.', '..O..O..', '...OO...'), "animation": "navigation"},
    {"id": "external_sensors", "name": "External Sensors", "category": "Information Systems", "color": (140, 40, 255), "mask": ('..OOOO..', '.O....O.', 'O......O', 'O..OO..O', 'O..OO..O', 'O......O', '.O....O.', '..OOOO..'), "animation": "ext_sensors"},
    {"id": "internal_sensors", "name": "Internal Sensors", "category": "Information Systems", "color": (140, 40, 255), "mask": ('...OO...', '..O..O..', '.O.OO.O.', '..OOOO..', '..OOOO..', '.O.OO.O.', '..O..O..', '...OO...'), "animation": "int_sensors"},
    {"id": "long_range_comms", "name": "Long Range Comms", "category": "Information Systems", "color": (140, 40, 255), "mask": ('...OO...', '..O..O..', '.O....O.', 'O......O', '.O....O.', '..O..O..', '...OO...', '........'), "animation": "long_comms"},
    {"id": "radio_communications", "name": "Radio Communications", "category": "Information Systems", "color": (140, 40, 255), "mask": ('...OO...', '..O..O..', '.O....O.', '..O..O..', '...OO...', '..O..O..', '.O....O.', '........'), "animation": "radio"},
    {"id": "transporters", "name": "Transporters", "category": "Utility Systems", "color": (220, 220, 220), "mask": ('...OO...', '..O..O..', '.O.O.O.O', '..O.O...', '..O.O...', '.O.O.O.O', '..O..O..', '...OO...'), "animation": "transporters"},
    {"id": "co2_scrubbers", "name": "CO2 Scrubbers", "category": "Utility Systems", "color": (220, 220, 220), "mask": ('...OO...', '..O..O..', '.O.O.O.O', '...O....', '...O....', '.O.O.O.O', '..O..O..', '...OO...'), "animation": "co2"},
    {"id": "oxygen_generators", "name": "Oxygen Generators", "category": "Utility Systems", "color": (220, 220, 220), "mask": ('...OO...', '..O..O..', '.O.OO.O.', '..O..O..', '..O..O..', '.O.OO.O.', '..O..O..', '...OO...'), "animation": "oxygen"},
    {"id": "gravity_field", "name": "Gravity Field", "category": "Utility Systems", "color": (220, 220, 220), "mask": ('..OOOO..', '.O....O.', 'O.O..O.O', 'O......O', 'O......O', 'O.O..O.O', '.O....O.', '..OOOO..'), "animation": "gravity"},
]

def blank_mask():
    return [[False for _ in range(WIDTH)] for _ in range(HEIGHT)]

def clone_mask(mask):
    return [list(row) for row in mask]

def mask_from_strings(rows):
    return [[c != "." for c in row] for row in rows]

def line_points(x0, y0, x1, y1):
    points = []
    dx = abs(x1 - x0)
    sx = 1 if x0 < x1 else -1
    dy = -abs(y1 - y0)
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            return points
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy

def mask_to_tuples(mask, color):
    return tuple(
        tuple(color if mask[y][x] else OFF for x in range(WIDTH))
        for y in range(HEIGHT)
    )

def blend(a, b, amount):
    # amount: 0.0..1.0
    return (
        int(a[0] + (b[0] - a[0]) * amount),
        int(a[1] + (b[1] - a[1]) * amount),
        int(a[2] + (b[2] - a[2]) * amount),
    )

def scale(color, amount):
    return (
        int(color[0] * amount),
        int(color[1] * amount),
        int(color[2] * amount),
    )

def frame_with_custom_colors(mask, base_color, custom=None):
    frame = []
    for y in range(HEIGHT):
        row = []
        for x in range(WIDTH):
            if not mask[y][x]:
                row.append(OFF)
            else:
                row.append(custom.get((x, y), base_color) if custom else base_color)
        frame.append(tuple(row))
    return tuple(frame)

def ship_core_mask():
    return mask_from_strings((
        "........",
        "........",
        "...OO...",
        "..O..O..",
        "..O..O..",
        "...OO...",
        "........",
        "........",
    ))

def apply_row_range(mask, y, x0, x1):
    for x in range(max(0, x0), min(WIDTH, x1 + 1)):
        mask[y][x] = True

def animation_frames(spec):
    kind = spec["animation"]
    color = spec["color"]
    static_mask = mask_from_strings(spec["mask"])

    if kind == "fusion":
        frames = []
        rows = [
            (
                "........",
                "........",
                ".O....O.",
                "........",
                "........",
                "........",
                "........",
                "........",
            ),
            (
                "........",
                "........",
                "..O..O..",
                "........",
                "........",
                "........",
                "........",
                "........",
            ),
            (
                "........",
                "........",
                "..O..O..",
                "...OO...",
                "...OO...",
                "........",
                "........",
                "........",
            ),
            (
                "........",
                "........",
                "........",
                "...OO...",
                "...OO...",
                "........",
                "........",
                "........",
            ),
        ]
        brightness = [0.35, 0.7, 1.0, 0.8]
        for r, b in zip(rows, brightness):
            frames.append(mask_to_tuples(mask_from_strings(r), scale(color, b)))
        return tuple(frames)

    if kind == "warp":
        inner_states = [
            (
                "..OOOO..",
                ".O....O.",
                "O.......",
                "O.......",
                "O.......",
                "O.......",
                ".O....O.",
                "..OOOO..",
            ),
            (
                "..OOOO..",
                ".O....O.",
                "O...O..O",
                "O.......",
                "O.......",
                "O...O..O",
                ".O....O.",
                "..OOOO..",
            ),
            spec["mask"],
            (
                "..OOOO..",
                ".O....O.",
                "O.OOOO.O",
                "O.O..O.O",
                "O.O..O.O",
                "O.OOOO.O",
                ".O....O.",
                "..OOOO..",
            ),
        ]
        return tuple(mask_to_tuples(mask_from_strings(rows), color) for rows in inner_states)

    if kind == "computer":
        interior_sets = [
            {(2,2):(0,180,40),(4,2):(255,0,0),(3,3):(0,120,255),(5,3):(255,170,0),(2,4):(180,0,255),(4,4):(0,200,200),(3,5):(255,60,180),(5,5):(150,255,0)},
            {(3,2):(255,170,0),(5,2):(0,200,255),(2,3):(180,0,255),(4,3):(0,255,60),(3,4):(255,0,0),(5,4):(255,255,0),(2,5):(0,120,255),(4,5):(255,80,160)},
            {(2,2):(255,0,0),(4,2):(0,255,60),(5,2):(0,120,255),(3,3):(255,255,0),(2,4):(255,80,160),(4,4):(0,255,255),(5,4):(255,170,0),(3,5):(160,0,255)},
            {(2,2):(0,120,255),(3,2):(255,170,0),(4,2):(255,0,80),(2,3):(0,255,60),(5,3):(180,0,255),(4,4):(255,255,0),(2,5):(0,255,255),(5,5):(255,255,255)},
        ]
        return tuple(frame_with_custom_colors(static_mask, color, custom) for custom in interior_sets)

    if kind.startswith("shield_"):
        frames = []
        rows = list(spec["mask"])
        shield_only = [list("........") for _ in range(HEIGHT)]
        if kind in ("shield_fore", "shield_aft"):
            y = 0 if kind == "shield_fore" else 7
            shield_only[y][3] = "O"
            shield_only[y][4] = "O"
            mid = tuple("".join(r) for r in shield_only)
            full = spec["mask"]
        elif kind in ("shield_port", "shield_starboard"):
            x = 0 if kind == "shield_port" else 7
            shield_only[2][x] = "O"
            shield_only[3][x] = "O"
            mid = tuple("".join(r) for r in shield_only)
            full = spec["mask"]
        elif kind == "shield_dorsal":
            for y in (0,1,6,7):
                shield_only[y][3] = "O"
                shield_only[y][4] = "O"
            mid = tuple("".join(r) for r in shield_only)
            full = spec["mask"]
        else:  # ventral
            for x in range(2,6):
                shield_only[4][x] = "O"
            mid = tuple("".join(r) for r in shield_only)
            full = spec["mask"]
        ship = ship_core_mask()
        frames.append(mask_to_tuples(ship, scale(color, 0.25)))
        # shield charge frame combines ship + partial shield
        charge = ship_core_mask()
        charge_rows = mask_from_strings(mid)
        for y in range(HEIGHT):
            for x in range(WIDTH):
                charge[y][x] = charge[y][x] or charge_rows[y][x]
        frames.append(mask_to_tuples(charge, color))
        frames.append(mask_to_tuples(mask_from_strings(full), color))
        frames.append(mask_to_tuples(charge, scale(color, 0.55)))
        return tuple(frames)

    if kind == "laser":
        origin = (7, 0)
        beam = line_points(7, 0, 1, 7)[:-1]
        frames = []
        for count in (2, 4, 6, len(beam)):
            mask = blank_mask()
            # emitter mass
            for y, x0, x1 in ((0,4,7),(1,5,7),(2,6,7),(3,7,7)):
                apply_row_range(mask, y, x0, x1)
            for x, y in beam[:count]:
                mask[y][x] = True
            frames.append(mask_to_tuples(mask, color))
        return tuple(frames)

    if kind == "tractor":
        widths = [2, 3, 5, 6]
        frames = []
        for max_width in widths:
            mask = blank_mask()
            # emitter dome
            for y, x0, x1 in ((0,2,7),(1,1,7)):
                apply_row_range(mask, y, x0, x1)
            beam_rows = [
                (2, 3, 4),
                (3, 2, 5),
                (4, 1, 6),
                (5, 0, 7 if max_width >= 6 else 6),
                (6, 0, 7 if max_width >= 6 else 6),
                (7, 0, 7 if max_width >= 6 else 6),
            ]
            for y, x0, x1 in beam_rows:
                width = x1 - x0 + 1
                if width > max_width:
                    center = (x0 + x1) // 2
                    half = max_width // 2
                    if max_width % 2 == 0:
                        x0 = center - half + 1
                        x1 = center + half
                    else:
                        x0 = center - half
                        x1 = center + half
                apply_row_range(mask, y, x0, x1)
            frames.append(mask_to_tuples(mask, color))
        return tuple(frames)

    if kind == "stealth":
        states = [
            spec["mask"],
            (
                "........",
                "..O..O..",
                "...O.O..",
                "........",
                "........",
                "..O.O...",
                "..O..O..",
                "........",
            ),
            (
                "........",
                "........",
                ".O....O.",
                "........",
                "........",
                ".O....O.",
                "........",
                "........",
            ),
            spec["mask"],
        ]
        bright = [1.0, 0.55, 0.25, 0.85]
        return tuple(mask_to_tuples(mask_from_strings(s), scale(color,b)) for s,b in zip(states, bright))

    if kind == "targeting":
        # crosshair pulse
        diamond = mask_from_strings((
            "...O....",
            "..O.O...",
            ".O...O..",
            "O.....O.",
            ".O...O..",
            "..O.O...",
            "...O....",
            "........",
        ))
        cross_small = mask_from_strings((
            "........",
            "........",
            "...O....",
            "..OOO...",
            "...O....",
            "........",
            "........",
            "........",
        ))
        cross_mid = mask_from_strings((
            "........",
            "...O....",
            "...O....",
            ".OOOOO..",
            "...O....",
            "...O....",
            "........",
            "........",
        ))
        full = mask_from_strings(spec["mask"])
        return (
            mask_to_tuples(diamond, scale(color, 0.5)),
            mask_to_tuples(cross_small, color),
            mask_to_tuples(cross_mid, color),
            mask_to_tuples(full, color),
        )

    if kind == "jammer":
        states = [
            (
                "........",
                "..O..O..",
                ".O.O.O..",
                "...O....",
                "....O...",
                "..O.O.O.",
                "..O..O..",
                "........",
            ),
            spec["mask"],
            (
                "........",
                ".O.O.O..",
                "...OO...",
                "..O..O..",
                ".O....O.",
                "...OO...",
                "..O.O...",
                "........",
            ),
            spec["mask"],
        ]
        return tuple(mask_to_tuples(mask_from_strings(s), color) for s in states)

    if kind == "alcubierre":
        states = [
            (
                "..OOOO..",
                ".O....O.",
                "O.......",
                "O...OO..",
                "O...OO..",
                "O.......",
                ".O....O.",
                "..OOOO..",
            ),
            (
                "..OOOO..",
                ".O....O.",
                "O...O..O",
                "O...O..O",
                "O...O..O",
                "O...O..O",
                ".O....O.",
                "..OOOO..",
            ),
            spec["mask"],
            (
                "..OOOO..",
                ".O....O.",
                "O.OOOO.O",
                "O.OOOO.O",
                "O.OOOO.O",
                "O.OOOO.O",
                ".O....O.",
                "..OOOO..",
            ),
        ]
        return tuple(mask_to_tuples(mask_from_strings(s), color) for s in states)

    if kind == "thrusters":
        states = [
            (
                "...OO...",
                "...OO...",
                "...OO...",
                "...OO...",
                "..OOOO..",
                "...OO...",
                "........",
                "........",
            ),
            (
                "...OO...",
                "...OO...",
                "...OO...",
                "...OO...",
                "..OOOO..",
                "..OOOO..",
                "...OO...",
                "........",
            ),
            spec["mask"],
            (
                "...OO...",
                "...OO...",
                "...OO...",
                "...OO...",
                "..OOOO..",
                ".OOOOOO.",
                "..OOOO..",
                "...OO...",
            ),
        ]
        return tuple(mask_to_tuples(mask_from_strings(s), color) for s in states)

    if kind == "navigation":
        states = [
            (
                "........",
                "....O...",
                "...OO...",
                "..O.O...",
                "...O....",
                "...O....",
                "........",
                "........",
            ),
            (
                "........",
                "........",
                "...OO...",
                "...O.O..",
                "...OO...",
                "........",
                "........",
                "........",
            ),
            spec["mask"],
            (
                "........",
                "........",
                "........",
                "...O....",
                "..O.O...",
                ".O..O...",
                "..OO....",
                "...O....",
            ),
        ]
        return tuple(mask_to_tuples(mask_from_strings(s), color) for s in states)

    if kind == "ext_sensors":
        states = [
            (
                "........",
                "...OO...",
                "..O..O..",
                ".O....O.",
                ".O....O.",
                "..O..O..",
                "...OO...",
                "........",
            ),
            (
                "..OOOO..",
                ".O....O.",
                "O......O",
                "O......O",
                "O......O",
                "O......O",
                ".O....O.",
                "..OOOO..",
            ),
            spec["mask"],
            (
                ".OOOOOO.",
                "O......O",
                "O......O",
                "O..OO..O",
                "O..OO..O",
                "O......O",
                "O......O",
                ".OOOOOO.",
            ),
        ]
        return tuple(mask_to_tuples(mask_from_strings(s), color) for s in states)

    if kind == "int_sensors":
        states = [
            (
                "........",
                "........",
                "...OO...",
                "..OOOO..",
                "..OOOO..",
                "...OO...",
                "........",
                "........",
            ),
            (
                "........",
                "...OO...",
                "..OOOO..",
                "..OOOO..",
                "..OOOO..",
                "..OOOO..",
                "...OO...",
                "........",
            ),
            spec["mask"],
            (
                "...OO...",
                "..OOOO..",
                ".OOOOOO.",
                ".OOOOOO.",
                ".OOOOOO.",
                ".OOOOOO.",
                "..OOOO..",
                "...OO...",
            ),
        ]
        return tuple(mask_to_tuples(mask_from_strings(s), color) for s in states)

    if kind == "long_comms":
        states = [
            (
                "........",
                "........",
                "...OO...",
                "..O..O..",
                "...OO...",
                "........",
                "........",
                "........",
            ),
            (
                "........",
                "...OO...",
                "..O..O..",
                ".O....O.",
                "..O..O..",
                "...OO...",
                "........",
                "........",
            ),
            spec["mask"],
            (
                "..OOOO..",
                ".O....O.",
                "O......O",
                "........",
                "O......O",
                ".O....O.",
                "..OOOO..",
                "........",
            ),
        ]
        return tuple(mask_to_tuples(mask_from_strings(s), color) for s in states)

    if kind == "radio":
        states = [
            (
                "........",
                "........",
                "...OO...",
                "..O..O..",
                "...OO...",
                "........",
                "........",
                "........",
            ),
            (
                "........",
                "...OO...",
                "........",
                "..O..O..",
                "...OO...",
                "..O..O..",
                "........",
                "........",
            ),
            spec["mask"],
            (
                "...OO...",
                "........",
                ".O....O.",
                "........",
                "...OO...",
                "........",
                ".O....O.",
                "........",
            ),
        ]
        return tuple(mask_to_tuples(mask_from_strings(s), color) for s in states)

    if kind == "transporters":
        states = [
            spec["mask"],
            (
                "........",
                "..O..O..",
                ".O.O.O.O",
                "..O.O...",
                "..O.O...",
                ".O.O.O.O",
                "..O..O..",
                "...OO...",
            ),
            (
                "........",
                "........",
                "..O..O..",
                ".O.O.O.O",
                "..O.O...",
                "..O.O...",
                ".O.O.O.O",
                "..O..O..",
            ),
            (
                "........",
                "........",
                "........",
                "..O..O..",
                ".O.O.O.O",
                "..O.O...",
                "..O.O...",
                ".O.O.O.O",
            ),
        ]
        return tuple(mask_to_tuples(mask_from_strings(s), color) for s in states)

    if kind == "co2":
        states = [
            (
                "........",
                "........",
                "...O....",
                "..O.O...",
                "...O....",
                "..O.O...",
                "...O....",
                "........",
            ),
            (
                "........",
                "...O....",
                "..O.O...",
                "...O....",
                "..O.O...",
                "...O....",
                "..O.O...",
                "........",
            ),
            spec["mask"],
            (
                "..O.O...",
                "...O....",
                "..O.O...",
                "...O....",
                "..O.O...",
                "...O....",
                "..O.O...",
                "...O....",
            ),
        ]
        return tuple(mask_to_tuples(mask_from_strings(s), color) for s in states)

    if kind == "oxygen":
        states = [
            (
                "........",
                "........",
                "...OO...",
                "........",
                "........",
                "...OO...",
                "........",
                "........",
            ),
            (
                "........",
                "...OO...",
                "..O..O..",
                "...OO...",
                "...OO...",
                "..O..O..",
                "...OO...",
                "........",
            ),
            spec["mask"],
            (
                "..OOOO..",
                ".O....O.",
                "O..OO..O",
                ".O....O.",
                ".O....O.",
                "O..OO..O",
                ".O....O.",
                "..OOOO..",
            ),
        ]
        return tuple(mask_to_tuples(mask_from_strings(s), color) for s in states)

    if kind == "gravity":
        states = [
            (
                "........",
                "...OO...",
                "..O..O..",
                "..O..O..",
                "..O..O..",
                "..O..O..",
                "...OO...",
                "........",
            ),
            (
                "...OO...",
                "..O..O..",
                ".O....O.",
                ".O....O.",
                ".O....O.",
                ".O....O.",
                "..O..O..",
                "...OO...",
            ),
            spec["mask"],
            (
                ".OOOOOO.",
                "O......O",
                "O.O..O.O",
                "O......O",
                "O......O",
                "O.O..O.O",
                "O......O",
                ".OOOOOO.",
            ),
        ]
        return tuple(mask_to_tuples(mask_from_strings(s), color) for s in states)

    raise ValueError("Unknown animation kind: {}".format(kind))

STATIC_IMAGES = {}
ANIMATION_FRAMES = {}
CARD_COLORS = {}
CARD_CATEGORIES = {}

for spec in CARD_SPECS:
    CARD_COLORS[spec["name"]] = spec["color"]
    CARD_CATEGORIES[spec["name"]] = spec["category"]
    STATIC_IMAGES[spec["name"]] = mask_to_tuples(mask_from_strings(spec["mask"]), spec["color"])
    ANIMATION_FRAMES[spec["name"]] = animation_frames(spec)

def xy_to_index(x, y, width=WIDTH, height=HEIGHT, layout="row-major"):
    """Map x,y to a NeoPixel index.

    layout options:
      - "row-major": rows laid out left->right, top->bottom
      - "serpentine": even rows left->right, odd rows right->left
      - "column-major": columns laid out top->bottom, left->right
    """
    if layout == "row-major":
        return y * width + x
    if layout == "serpentine":
        return y * width + (x if y % 2 == 0 else (width - 1 - x))
    if layout == "column-major":
        return x * height + y
    raise ValueError("Unknown layout: {}".format(layout))

def clear_pixels(pixels):
    for i in range(len(pixels)):
        pixels[i] = OFF
    pixels.show()

def render_frame(pixels, frame, *, offset=0, layout="row-major", brightness=1.0, auto_write=False):
    """Render one 8x8 RGB tuple frame to a NeoPixel object."""
    for y in range(HEIGHT):
        for x in range(WIDTH):
            r, g, b = frame[y][x]
            idx = offset + xy_to_index(x, y, layout=layout)
            pixels[idx] = (
                int(r * brightness),
                int(g * brightness),
                int(b * brightness),
            )
    if not auto_write:
        pixels.show()

def show_static_icon(pixels, card_name, *, offset=0, layout="row-major", brightness=1.0):
    render_frame(
        pixels,
        STATIC_IMAGES[card_name],
        offset=offset,
        layout=layout,
        brightness=brightness,
    )

def play_animation(
    pixels,
    card_name,
    *,
    offset=0,
    layout="row-major",
    brightness=1.0,
    frame_delay=0.12,
    loops=1,
):
    frames = ANIMATION_FRAMES[card_name]
    for _ in range(loops):
        for frame in frames:
            render_frame(
                pixels,
                frame,
                offset=offset,
                layout=layout,
                brightness=brightness,
            )
            time.sleep(frame_delay)

def demo_cycle(
    pixels,
    *,
    offset=0,
    layout="row-major",
    brightness=0.4,
    static_hold=0.6,
    frame_delay=0.12,
):
    for spec in CARD_SPECS:
        name = spec["name"]
        show_static_icon(
            pixels,
            name,
            offset=offset,
            layout=layout,
            brightness=brightness,
        )
        time.sleep(static_hold)
        play_animation(
            pixels,
            name,
            offset=offset,
            layout=layout,
            brightness=brightness,
            frame_delay=frame_delay,
            loops=2,
        )

# Example usage:
#
# import board
# import neopixel
# from power_cards_circuitpython import *
#
# pixels = neopixel.NeoPixel(board.D6, 64, auto_write=False)
#
# show_static_icon(pixels, "Fore Shields", layout="serpentine", brightness=0.25)
# time.sleep(1)
# play_animation(pixels, "Fore Shields", layout="serpentine", brightness=0.25, loops=3)
#
# # Cycle through everything:
# demo_cycle(pixels, layout="serpentine", brightness=0.25)
