# PIO + animation pipeline — current design

> **Status 2026-05-09:** Implemented and deployed. The 30 FPS target is **not reached** —
> the right-board card-tray controller turned out to be wire-bound at **~12 FPS effective**
> on the WS2812 800 kbps line (2,220 px × 30 µs/px = ~67 ms per write). `PIXEL_REFRESH_SECONDS`
> is at 0.033 and `CARD_ANIMATION_TARGET_FPS` is 30 — both intentionally above the realized
> ceiling so the loop runs as fast as the PIO write allows. Reaching 30 FPS requires bumping
> `WS2812_PIO_FREQ` in `drivers/local_neopixel.py` (try 16 MHz → 1.6 Mbps first) or splitting
> the chain. See `docs/ws2812-timing.xlsx` and `ARCHITECTURE.md § Performance target`.

Replaces the now-stale `viper-animation-optimization.plan.md`. That earlier plan
described an animation pipeline that doesn't exist anymore — the codebase has
since acquired pre-baked frames, status-pixels-only-on-state-change, and
animation-frame-index-change detection. Several of its perf concerns are
already solved.

This doc captures the design for the *next* refactor: wiring the half-built
PIO driver to the rest of the firmware.

## What's already in place

- **Pre-baked frames.** `power_cards/animation.py:bake_frames()` runs at
  startup, expanding palette-indexed source frames into ready-to-write byte
  buffers. Hot path no longer does LUT expansion.
- **PowerCardTray.Update() is already efficient.** Status pixels are written
  to the strip only when `PowerState` changes (the setter calls
  `FillPixelData`); the animation grid is re-written only when
  `AnimationFrame()` returns a new frame index. The "3 SetPixelData calls per
  tray per frame" problem in the old plan no longer exists — current code is
  one `SetPixelData` per frame *change*, plus one `FillPixelData` per state
  change.
- **PIO program written.** `drivers/local_neopixel.py` has a working
  `@rp2.asm_pio` WS2812 driver, well-commented, with correct timing.
- **Pixel-strip writes are already throttled** at `PIXEL_REFRESH_SECONDS`
  (currently 0.05 = 20 Hz) inside `PixelStripManager.Update()`. We'll need to
  drop this to ~0.033 to actually hit the 30 FPS target.

## What's wrong / incomplete

- **`LocalNeoPixel.write()` is commented out.** The class still uses a
  3-byte-per-pixel `bytearray` buffer (`bytearray(n * NEO_PACKED_BPP)` with
  `NEO_PACKED_BPP=3`) and never actually drives the PIO state machine. The
  PIO program at module top-level is allocated but unused — it's set up by a
  module-level `sm = rp2.StateMachine(...)` followed by a `for i in range(4 *
  NUM_LEDS): ...` loop that runs at import. **That loop runs every time the
  module is imported** and isn't tied to any caller — that's a real bug and
  needs to go.
- **R/G channel swap in the LUT path.** `animation.py`'s
  `__regenerate_palettes` writes LUT entries as `(r << 16) | (g << 8) | b`
  (standard 0x00RRGGBB layout), but `_expand_frame_from_lut` reads them with
  `NEO_PACKED_OFFSET_R = 8`, which is the offset for R in the project's
  *neo-packed* format (0x00GGRRBB). The two formats disagree by an R↔G swap.
  Latent bug — only affects multi-color animations. Most current animations
  are monochrome, so no visible effect, but it'd bite the moment we author a
  multi-color card.
- **Buffer format doesn't match what PIO consumes.** The PIO program (with
  `autopull=True, pull_thresh=24`) reads 32-bit words from the FIFO and
  shifts out 24 bits per pixel; the high 8 bits of each word are discarded.
  Our 3-byte-per-pixel `bytearray` can't be fed to `sm.put()` cleanly —
  we'd need to either pad to 4 bytes per pixel or do per-pixel transposition
  on the fly. The right answer is the padded format.

## Design

### Buffer format — `array.array('I')`, one neo-packed int per pixel

Adopt **4 bytes per pixel** throughout, stored as `array.array('I')` (32-bit
unsigned ints), in the project's existing **neo-packed** layout
(0x00GGRRBB):

| Bits  | Field   |
| ----- | ------- |
| 31–24 | padding (zero) |
| 23–16 | G       |
| 15–8  | R       |
| 7–0   | B       |

This is exactly what `to_neo_packed(r, g, b)` already produces, and exactly
what the PIO consumes when written via `sm.put(buf, 8)`. The 8-bit left-shift
in the `put()` call moves the GRB bits into the upper 24 bits of each FIFO
word; the PIO shifts them out MSB-first → on-wire order is G, R, B per
WS2812.

Hot path becomes a memcpy: animation frame `array.array('I')` slice copied
into the per-strip `array.array('I')` buffer at the right offset. No
per-pixel byte shuffling, no tuple allocation, no `__setitem__` overhead.

### Concrete changes by file

**`utils/color_utils.py`**
- Keep neo-packed layout constants. They're already correct.
- Update `NEO_PACKED_BPP` semantics: change to mean *bytes per pixel in the
  buffer* = 4. (Or introduce a separate constant if the 3-byte format needs
  to live on for non-PIO contexts; in practice nothing else uses it now.)
- Replace `copy_buffer_pixels` with an `array.array('I')`-based copy
  function. Either keep as `@micropython.viper` over `ptr32` for the hot
  path, or use Python slice assignment `dest[off:off+n] = src[:n]`
  (`array.array` slice-assignment is a C-level memcpy in MicroPython).
- Replace `neo_packed_to_buffer` with an int-array fill: `for i in range(n):
  buf[off+i] = packed`. Trivially fast in Python; no need for Viper.
- `buffer_to_neo_packed` can stay (debug helper) or go (unused after
  refactor).

**`drivers/local_neopixel.py`**
- Delete the module-level demo loop (lines ~115–146). It runs at import,
  drives a state machine on a hardcoded pin, and serves no purpose in the
  current project.
- `LocalNeoPixel.__init__` allocates `self.buf = array.array('I', [0] * n)`
  and creates its own state machine bound to the caller's pin.
- `set_buf` becomes a slice copy (or Viper memcpy) into `self.buf`.
- `fill` becomes a Python loop assigning the packed int into `self.buf`
  positions.
- `__setitem__` / `__getitem__` work with packed ints directly.
- `write()` calls `self.sm.put(self.buf, 8)` — un-comment and connect.
- Remove the stale `bitstream(...)` reference.

**`power_cards/animation.py`**
- Fix the R/G swap: change LUT populate to use `to_neo_packed(r, g, b)`
  (which already produces 0x00GGRRBB) instead of the bare
  `(r << 16) | (g << 8) | b`. After the fix, `(lut_value >>
  NEO_PACKED_OFFSET_R) & 0xFF` correctly extracts R.
- Replace `bake_frames` / `_expand_frame_from_lut` with a much simpler
  function: `array.array('I', [lut[idx] for idx in frame])`. One int per
  pixel, neo-packed format, ready to copy to the strip buffer.
- Drop `NEOPIXEL_BYTE_OFFSET_*` imports (no longer needed).
- Brightness handling stays as-is — applied at LUT generation, frames baked
  at the chosen brightness. Forward direction (dynamic per-frame brightness)
  is out of scope for this refactor.

**`utils/pixel_strip_manager.py`**
- `SetPixelData` type-hint change: `pixelData: array.array` instead of
  `pixelData: bytes`. Internal call to `self.pixels.set_buf` is unchanged in
  shape.
- Drop `PIXEL_REFRESH_SECONDS` to `0.033` (or expose as a configurable;
  hard-code is fine for now) so the periodic strip write doesn't cap the
  frame rate at 20 Hz.

**`card_tray/`, `power_grid/`** — no logic changes. Type hints only as
needed.

### What's NOT in scope

- **Dynamic per-frame brightness / current-budget management.** Captured in
  ARCHITECTURE.md § Power for later. Static `ANIMATION_BRIGHTNESS = 0.15`
  stays.
- **Switchboard protocol redesign.** Tracked in TODO; pre-MVP but separate.
- **Multi-Pico topology mechanics.** This refactor targets the card-tray
  controller's single-Pico animation loop.
- **PIO program changes.** The program is correct as-is.
- **Wokwi setup.** Pushed to back of the queue per David's call.

## Implementation order

1. `color_utils.py` foundations — switch buffer-format constants and
   helpers.
2. `local_neopixel.py` — wire PIO write path, switch buffer to
   `array.array`, remove demo code.
3. `animation.py` — fix LUT bug, simplify `bake_frames`.
4. `pixel_strip_manager.py` — type hints, refresh-rate constant.
5. Sanity check — imports clean, ruff/pyright (where applicable) green.

## Verification (post-merge, on real hardware)

- Card-tray Pico boots without import errors.
- All 30 trays display animations.
- Multi-color animations (the existing test cases) display with correct R/G.
- Frame rate observed against the new 30 FPS target.
- Power draw spot-check at `ANIMATION_BRIGHTNESS = 0.15` matches prior
  measurements (no surprises from buffer format change).
