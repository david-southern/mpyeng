"""Convert existing animation definitions (pixel_mask / color_mask / frame_mask)
to pre-baked bytes([...]) frame arrays compatible with the new 256-entry LUT.

Run from the engineering-board-left-manager directory:

    python convert_animations.py > converted_animations.py

Then review converted_animations.py and paste the CARD_ANIMATION_DEFS dict into
power_card_animation.py as part of the Step 4 refactor.

Notes:
- This script re-implements the baking logic standalone so it runs cleanly on
  CPython (which applies name-mangling to __ attributes unlike CircuitPython).
- Animations with random effects (@, %, *) are expanded to 16 varied frames using
  deterministic seeds, so the output is reproducible but looks varied at runtime.
- The output uses the new palette offsets (PALETTE_SIZE=20, GREY_OFFSET=0,
  WEAPONS_OFFSET=20 ... SPECTRUM_OFFSET=180).
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from power_card_animation import CARD_ANIMATION_DEFS, CardAnimationHelpers
from power_card_categories import PowerCardCategories
from power_card_ids import PowerCardIds


# ---------------------------------------------------------------------------
# Reverse-lookup: string ID value -> PowerCardIds attribute name
# ---------------------------------------------------------------------------
_ID_TO_CONST = {
    v: k for k, v in vars(PowerCardIds).items()
    if not k.startswith("_") and isinstance(v, str) and k.endswith("_ID")
}

# ---------------------------------------------------------------------------
# Palette offset table — mirrors the new CardAnimationHelpers layout
# ---------------------------------------------------------------------------
_CAT_OFFSETS = {
    PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME:     CardAnimationHelpers.WEAPONS_OFFSET,
    PowerCardCategories.PROPULSION_SYSTEMS_CATEGORY_NAME:  CardAnimationHelpers.PROPULSION_OFFSET,
    PowerCardCategories.UTILITY_SYSTEMS_CATEGORY_NAME:     CardAnimationHelpers.UTILITY_OFFSET,
    PowerCardCategories.POWER_SYSTEMS_CATEGORY_NAME:       CardAnimationHelpers.POWER_OFFSET,
    PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME:   CardAnimationHelpers.DEFENSIVE_OFFSET,
    PowerCardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME: CardAnimationHelpers.INFORMATION_OFFSET,
}

_COLOR_MASK_TO_CAT = {
    "P": PowerCardCategories.POWER_SYSTEMS_CATEGORY_NAME,
    "D": PowerCardCategories.DEFENSIVE_SYSTEMS_CATEGORY_NAME,
    "W": PowerCardCategories.WEAPONS_SYSTEMS_CATEGORY_NAME,
    "R": PowerCardCategories.PROPULSION_SYSTEMS_CATEGORY_NAME,
    "I": PowerCardCategories.INFORMATION_SYSTEMS_CATEGORY_NAME,
    "U": PowerCardCategories.UTILITY_SYSTEMS_CATEGORY_NAME,
}

_SPECTRUM_OFFSET = CardAnimationHelpers.SPECTRUM_OFFSET   # 180
_ANIMATED_CHARS = frozenset("~@%><*")
_RANDOM_CHARS = frozenset("@%*")

# ---------------------------------------------------------------------------
# COS LUT (identical to CardAnimationHelpers.__COS_LUT)
# ---------------------------------------------------------------------------
_COS_LUT_SIZE = 64
_COS_LUT = [int(128 - 128 * math.cos(i * 2 * math.pi / 64)) for i in range(64)]


# ---------------------------------------------------------------------------
# Baking helpers (CPython-safe re-implementation, no name-mangling issues)
# ---------------------------------------------------------------------------

def _xy_to_index(x: int, y: int, width: int = 8, height: int = 8) -> int:
    """Serpentine layout with y-flip (matches CardAnimationHelpers.xy_to_index)."""
    y = height - 1 - y
    return y * width + (x if y % 2 == 0 else (width - 1 - x))


def _intensity_to_palette_index(f: float) -> int:
    """Map 0.0–1.0 intensity to palette index 0–19. Returns -1 for black."""
    dim = 0.25
    if f < dim:
        return -1
    return min(19, int((f - dim) / (1.0 - dim) * 19))


def _compute_pixel_offsets(anim) -> list:
    mask_h = len(anim.pixel_mask)
    mask_w = len(anim.pixel_mask[0]) if mask_h > 0 else 0
    own_offset = _CAT_OFFSETS[anim.category]
    pixel_offsets = [own_offset] * (mask_w * mask_h)

    if anim.color_mask:
        for y in range(mask_h):
            for x in range(mask_w):
                cm_ch = anim.color_mask[y][x]
                if cm_ch == ".":
                    continue
                elif cm_ch == "?":
                    pixel_offsets[_xy_to_index(x, y, mask_w, mask_h)] = _SPECTRUM_OFFSET
                elif cm_ch in _COLOR_MASK_TO_CAT:
                    cat = _COLOR_MASK_TO_CAT[cm_ch]
                    pixel_offsets[_xy_to_index(x, y, mask_w, mask_h)] = _CAT_OFFSETS[cat]

    return pixel_offsets


def _compute_frame_active_masks(anim, num_frames: int) -> list:
    mask_h = len(anim.pixel_mask)
    mask_w = len(anim.pixel_mask[0]) if mask_h > 0 else 0
    all_active = (1 << num_frames) - 1
    frame_active = [all_active] * (mask_w * mask_h)

    if anim.frame_mask:
        for y in range(mask_h):
            for x in range(mask_w):
                cell = anim.frame_mask[y][x]
                if cell == ".":
                    continue
                bitmask = 0
                for ch in cell:
                    if "0" <= ch <= "9":
                        bitmask |= (1 << int(ch))
                frame_active[_xy_to_index(x, y, mask_w, mask_h)] = bitmask

    return frame_active


def _determine_num_frames(anim) -> int:
    has_animated = any(ch in _ANIMATED_CHARS for row in anim.pixel_mask for ch in row)
    num_frames = 10 if has_animated else 1
    if anim.frame_mask:
        for fm_row in anim.frame_mask:
            for cell in fm_row:
                for ch in cell:
                    if "0" <= ch <= "9":
                        f = int(ch) + 1
                        if f > num_frames:
                            num_frames = f
    return num_frames


def _bake_frame(
    anim,
    frame_index: int,
    num_frames: int,
    pixel_offsets: list,
    frame_active: list,
) -> bytes:
    mask_h = len(anim.pixel_mask)
    mask_w = len(anim.pixel_mask[0]) if mask_h > 0 else 0
    cycle_progress = frame_index / num_frames
    buf = bytearray(mask_w * mask_h)

    wave_lut_val = _COS_LUT[int(cycle_progress * _COS_LUT_SIZE) % _COS_LUT_SIZE]
    wave_pal_idx = 19 - min(19, (wave_lut_val * 19) >> 8)
    frame_bit = 1 << frame_index

    for y in range(mask_h):
        for x in range(mask_w):
            ch = anim.pixel_mask[y][x]
            if ch == ".":
                continue
            idx = _xy_to_index(x, y, mask_w, mask_h)
            if not (frame_active[idx] & frame_bit):
                continue
            offset = pixel_offsets[idx]
            if ch == "~":
                buf[idx] = offset + wave_pal_idx
            elif ch == "@":
                buf[idx] = offset + random.randint(0, 19)
            elif ch == "%":
                if random.random() >= 0.6:
                    buf[idx] = _SPECTRUM_OFFSET + random.randint(0, 49)
            elif ch == ">":
                pi = _intensity_to_palette_index(1.0 - cycle_progress)
                buf[idx] = (offset + pi) if pi >= 0 else 0
            elif ch == "<":
                pi = _intensity_to_palette_index(cycle_progress)
                buf[idx] = (offset + pi) if pi >= 0 else 0
            elif ch == "*":
                if random.random() < 0.75:
                    buf[idx] = offset + 19
            elif "0" <= ch <= "9":
                buf[idx] = offset + min(19, int((ord(ch) - 48) / 9 * 19))
            else:
                buf[idx] = offset + 19  # unrecognised char = max brightness

    return bytes(buf)


def _get_frames(anim) -> list:
    """Return baked frames for one animation.

    Random-effect animations are expanded to 16 varied frames using
    deterministic seeds so the output is reproducible.
    """
    has_random = any(ch in _RANDOM_CHARS for row in anim.pixel_mask for ch in row)
    num_frames = 16 if has_random else _determine_num_frames(anim)

    pixel_offsets = _compute_pixel_offsets(anim)
    frame_active = _compute_frame_active_masks(anim, num_frames)

    frames = []
    for frame_index in range(num_frames):
        if has_random:
            random.seed(frame_index * 7919)  # Deterministic but visually varied
        frames.append(_bake_frame(anim, frame_index, num_frames, pixel_offsets, frame_active))

    return frames


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def main():
    print("# Auto-generated by convert_animations.py")
    print("# Review each animation's frames before pasting into power_card_animation.py")
    print()
    print("CARD_ANIMATION_DEFS = {")

    for anim_id, anim in CARD_ANIMATION_DEFS.items():
        const_name = _ID_TO_CONST.get(anim_id, anim_id)
        frames = _get_frames(anim)

        duration_arg = ""
        if anim.animation_duration != CardAnimationHelpers.DEFAULT_ANIMATION_DURATION:
            duration_arg = f",\n        animation_duration={anim.animation_duration}"

        print(f"    PowerCardIds.{const_name}: PowerCardAnimation(")
        print(f"        uid=PowerCardIds.{const_name},")
        print(f'        name="{anim.name}"{duration_arg},')
        print(f"        frames=[")
        for frame_index, frame in enumerate(frames):
            frame_str = ", ".join(str(b) for b in frame)
            print(f"            bytes([{frame_str}]),  # frame {frame_index}")
        print(f"        ],")
        print(f"    ),")

    print("}")


if __name__ == "__main__":
    main()
