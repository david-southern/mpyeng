# ESP32-S3 NeoPixel Animation Performance — Implementation Plan

## Project Context

- **Platform:** ESP32-S3 Feather TFT with MicroPython v1.28.0
- **Goal:** Maximize animation frame rate for 2220 NeoPixel LEDs (30 trays × 74 LEDs/tray)
- **Current State:**
    - 25 power cards, each with a variable number of animation frames stored as `bytes()` in
      `CARD_ANIMATION_DEFS` (each frame is 64 bytes of palette indices for an 8×8 pixel grid)
    - A single `GLOBAL_PALETTE_LOOKUP list[int]` (256 entries) of brightness-scaled packed
      `0x00RRGGBB` ints, regenerated when brightness changes
    - A single `GLOBAL_RENDER_BUFFER list[int]` (64 entries) that `PixelBuffer()` writes into each
      frame via a Python LUT expansion loop — callers must consume before the next call
    - 30 `PowerCardTray` objects each calling `SetPixelData` **3 times** per frame update: once for
      5 top status LEDs, once for 64 animation grid LEDs, once for 5 bottom status LEDs (90 calls
      total per frame)
    - `SetPixelData` transcribes packed ints into the NeoPixel strip via `np[i] = (r, g, b)` per
      pixel — the primary performance bottleneck

- **Approach:**
    - Convert `GLOBAL_RENDER_BUFFER` and `GLOBAL_PALETTE_LOOKUP` from `list[int]` to
      `array.array('I')` so they can be passed as raw buffers to Viper functions
    - Replace the Python LUT expansion loop in `PixelBuffer()` with a `@micropython.viper` function
    - Replace the Python per-pixel unpack loop in `SetPixelData()` with a `@micropython.viper`
      function that writes directly into `np.buf`, bypassing the `__setitem__` API entirely
    - Combine the 3 `SetPixelData` calls per tray into 1 by pre-allocating a 74-pixel
      `array.array('I')` buffer per tray and updating status pixels only on state change

---

## Root Cause Summary

The current bottleneck is caused by:

1. **Tuple allocation per pixel** — 2220 heap objects per frame in `SetPixelData`, thrashing the GC
2. **Python interpreter loop overhead** — 2220 `__setitem__` iterations + 1920 LUT lookup iterations
   per frame, all in bytecode
3. **NeoPixel `__setitem__` overhead** — Python-level API call + ORDER remapping per pixel
4. **Redundant `SetPixelData` calls** — 90 calls per frame (3 per tray) with validation overhead
5. **Temporary list creation** — 60 × `[trayStateColor] * 5` allocations per frame (one per status
   region per tray)

The wire transfer (`np.write()`) costs a fixed ~6ms at 800kHz and is **not** the bottleneck.

---

## Architecture (Corrected from Original Plan)

The original plan described a single monolithic animation loop over all 2220 pixels. The actual
architecture is:

```
main.py
  └─ PowerTrayManager.Update()  (called at ANIMATION_TARGET_FPS)
       └─ for each of 30 PowerCardTray objects:
            ├─ PowerCard.PixelBuffer(progress, brightness)
            │    └─ loop 64: GLOBAL_RENDER_BUFFER[i] = GLOBAL_PALETTE_LOOKUP[frame[i]]
            ├─ SetPixelData(gridPixelIndex, 64, GLOBAL_RENDER_BUFFER)     ← 64-pixel write
            ├─ SetPixelData(topPixelIndex,   5, [statusColor] * 5)        ← 5-pixel write
            └─ SetPixelData(bottomPixelIndex, 5, [statusColor] * 5)       ← 5-pixel write
```

The Viper optimization must target the **inner loops of `PixelBuffer()` and `SetPixelData()`**,
not a top-level animation loop.

---

## Frame Data Format

Each frame is stored as a `bytes()` of 64 palette indices (one byte per pixel). `PixelBuffer()`
expands these into packed `0x00RRGGBB` ints via the LUT:

```
frame[i]  →  GLOBAL_PALETTE_LOOKUP[frame[i]]  →  GLOBAL_RENDER_BUFFER[i]  (0x00RRGGBB)
```

`SetPixelData()` then unpacks packed ints into the NeoPixel `buf` bytearray in **GRB order**
(as required by WS2812/NeoPixel protocol):

```
np.buf[pixel*3 + 0] = G  (bits 15:8  of 0x00RRGGBB)
np.buf[pixel*3 + 1] = R  (bits 23:16 of 0x00RRGGBB)
np.buf[pixel*3 + 2] = B  (bits 7:0   of 0x00RRGGBB)
```

This GRB layout matches what MicroPython's NeoPixel `__setitem__` produces when called with
`np[i] = (r, g, b)` (it applies ORDER=(1,0,2) remapping internally). The Viper path bypasses
`__setitem__` and writes GRB directly, producing identical output.

---

## Implementation Tasks

### Task 1 — Convert global buffers to `array.array` in `animation.py`

Viper's `ptr32` type requires objects that expose a raw C buffer. `list` does not; `array.array`
does. Change both global buffers:

```python
# Before:
import array  # add this import
GLOBAL_RENDER_BUFFER: list[int] = [0] * CARD_PIXEL_COUNT
GLOBAL_PALETTE_LOOKUP: list[int] = [0] * 256
```

```python
# After:
import array
GLOBAL_RENDER_BUFFER = array.array('I', [0] * CARD_PIXEL_COUNT)
GLOBAL_PALETTE_LOOKUP = array.array('I', [0] * 256)
```

All existing index-based writes to these buffers (`lut[i] = ...`, `buf[i] = ...`) are compatible
with `array.array` and require no other changes to `__regenerate_palettes`.

---

### Task 2 — Add Viper LUT expansion function to `animation.py`

This replaces the inner loop in `PowerCardAnimation.PixelBuffer()`. The `ptr8` type maps directly
to the raw bytes of the `bytes` frame object (read-only buffer); `ptr32` maps to the
`array.array('I')` buffers.

```python
@micropython.viper
def _expand_frame_lut(frame: ptr8, lut: ptr32, buf: ptr32, n: int):
    i: int = 0
    while i < n:
        buf[i] = lut[frame[i]]
        i += 1
```

Replace the loop inside `PixelBuffer()`:

```python
# Before:
for i in range(64):
    buf[i] = lut[frame[i]]

# After:
_expand_frame_lut(frame, lut, buf, CARD_PIXEL_COUNT)
```

**Note on `bytes` with `ptr8`:** MicroPython's Viper accepts `bytes` as a read-only `ptr8` since
`bytes` implements the buffer protocol. If a `TypeError` occurs at runtime, convert `_frames`
entries from `bytes(...)` to `bytearray(...)` at `PowerCardAnimation.__init__` time:

```python
self._frames = [bytearray(f) for f in frames]
```

---

### Task 3 — Add Viper unpack function to `pixel_strip_manager.py`

This replaces the inner loop in `SetPixelData()`. The `dst_byte_offset` parameter handles
sub-range writes (pixel `startIndex` maps to byte `startIndex * 3` in `np.buf`).

```python
@micropython.viper
def _unpack_pixels_to_buf(src: ptr32, dst: ptr8, dst_byte_offset: int, n: int):
    i: int = 0
    while i < n:
        p: int = src[i]
        base: int = dst_byte_offset + i * 3
        dst[base]     = (p >> 8)  & 0xFF   # G
        dst[base + 1] = (p >> 16) & 0xFF   # R
        dst[base + 2] =  p        & 0xFF   # B
        i += 1
```

Replace the loop inside `SetPixelData()`:

```python
# Before:
for pixIndex in range(pixelCount):
    val = pixelData[pixIndex]
    pixVal = ((val >> 16) & 0xFF, (val >> 8) & 0xFF, val & 0xFF)
    self.pixels[startIndex + pixIndex] = pixVal

# After:
_unpack_pixels_to_buf(pixelData, self.pixels.buf, startIndex * 3, pixelCount)
```

`pixelData` must be an `array.array('I')` for Viper `ptr32` to accept it. All callers are updated
in Task 4. `self.pixels.buf` is the `bytearray` exposed by MicroPython's `NeoPixel` object.

**Note on `power_grid.py`:** `PowerGrid.SetPixelData` is called with a list comprehension and
`ENABLE_POWER_GRID` is `False` on the main device. If power grid support is ever enabled, its
caller must be updated to pass `array.array('I')`.

---

### Task 4 — Combine 3 pixel writes per tray into 1 in `power_card_tray.py`

**4a. Reserve one contiguous pixel range at init instead of three:**

```python
# Before (3 separate reservations):
self.__topTrayPixelIndex = self.__pixelStripManager.ReservePixelRange(PIXEL_CARD_TRAY_LEDS)
self.__gridPixelIndex    = self.__pixelStripManager.ReservePixelRange(PIXEL_CARD_TRAY_GRID_LEDS)
self.__bottomTrayPixelIndex = self.__pixelStripManager.ReservePixelRange(PIXEL_CARD_TRAY_LEDS)

# After (one contiguous reservation):
self.__startPixelIndex = self.__pixelStripManager.ReservePixelRange(PIXEL_CARD_TRAY_TOTAL_LEDS)
```

**4b. Pre-allocate a per-tray combined pixel buffer:**

```python
self.__tray_pixel_buffer = array.array('I', [0] * PIXEL_CARD_TRAY_TOTAL_LEDS)
```

**4c. Update `PowerState.setter` to write status colors into the buffer:**

Status colors change rarely (only on state change) so write them into the combined buffer at the
setter rather than creating `[color] * 5` temporaries every frame:

```python
@PowerState.setter
def PowerState(self, value: int):
    self.__powerState = value
    color = CARD_TRAY_COLORS[value]
    for status_index in range(PIXEL_CARD_TRAY_LEDS):
        self.__tray_pixel_buffer[status_index] = color
        self.__tray_pixel_buffer[PIXEL_CARD_TRAY_LEDS + PIXEL_CARD_TRAY_GRID_LEDS + status_index] = color
```

Also call this initialization logic at the end of `__init__` to pre-fill status pixels.

**4d. Replace 3 `SetPixelData` calls in `Update()` with 1:**

```python
# Before (3 calls):
pixel_buffer = self.CurrentPowerCard.PixelBuffer(animationProgress, TRAY_BRIGHTNESS)
self.__pixelStripManager.SetPixelData(self.__gridPixelIndex, PIXEL_CARD_TRAY_GRID_LEDS, pixel_buffer)
self.__pixelStripManager.SetPixelData(self.__topTrayPixelIndex, PIXEL_CARD_TRAY_LEDS, [trayStateColor] * PIXEL_CARD_TRAY_LEDS)
self.__pixelStripManager.SetPixelData(self.__bottomTrayPixelIndex, PIXEL_CARD_TRAY_LEDS, [trayStateColor] * PIXEL_CARD_TRAY_LEDS)

# After (1 call):
pixel_buffer = self.CurrentPowerCard.PixelBuffer(animationProgress, TRAY_BRIGHTNESS)
self.__tray_pixel_buffer[PIXEL_CARD_TRAY_LEDS:PIXEL_CARD_TRAY_LEDS + PIXEL_CARD_TRAY_GRID_LEDS] = pixel_buffer
self.__pixelStripManager.SetPixelData(self.__startPixelIndex, PIXEL_CARD_TRAY_TOTAL_LEDS, self.__tray_pixel_buffer)
```

`array.array` slice assignment is a C-level memcpy — no Python objects are created.

---

### Task 5 — SRAM allocation notes

The original plan was concerned about the NeoPixel `buf` (6660 bytes) landing in PSRAM if the heap
fills before `NeoPixel` is constructed. In the current codebase:

- Frame data (25 cards × ~10–30 frames × 64 bytes) is in the range of **16–48 KB** — not ~2MB as
  originally estimated. SRAM pressure from frame data is minimal.
- The NeoPixel object is constructed in `PixelStripManager.__init__()` which is called at module
  load of `tray_manager.py`, after `animation.py` is fully imported. The small frame data footprint
  means SRAM is unlikely to be exhausted before that point.
- **No structural change to init order is required**, but it is worth verifying by checking
  `log_free_ram()` output before and after key allocations during a debug run.

---

### Task 6 — Benchmark and Validate

After all tasks are implemented:

1. Run with profiling enabled (`report_all_profiles()` already wired in `main.py`)
2. Check the `power_trays` and `pixel_update` profile entries for per-frame time
3. Check `ANIMATION_TARGET_FPS` in `animation.py` (currently 5) — increase it once performance
   headroom is confirmed

**Expected improvements over baseline:**

| Hotspot                      | Before                           | After                       |
| ---------------------------- | -------------------------------- | --------------------------- |
| LUT expansion (per frame)    | 1920 Python iterations           | 1920 Viper iterations       |
| Pixel unpack (per frame)     | 2220 Python iters + tuple allocs | 2220 Viper iterations       |
| `SetPixelData` call overhead | 90 calls × validation code       | 30 calls × validation code  |
| Status color temporaries     | 60 × `[color] * 5` allocations   | 0 (written on state change) |
| `np.write()` (wire)          | ~6 ms fixed                      | ~6 ms fixed (unchanged)     |

---

## Key Constraints & Gotchas

| Concern                          | Detail                                                                                                                                                                                                                                             |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `array.array` type code          | Must be `'I'` (unsigned 32-bit int). The `'i'` (signed) variant also works for bit ops but use `'I'` to match intent.                                                                                                                              |
| `bytes` as `ptr8`                | MicroPython Viper accepts `bytes` for read-only `ptr8`. If a `TypeError` occurs, change `_frames` to `bytearray` at construction.                                                                                                                  |
| `np.buf` attribute               | MicroPython's `NeoPixel` exposes its internal `bytearray` as `.buf`. This is a public attribute, not mangled. Confirmed for MicroPython v1.28.0.                                                                                                   |
| Viper integer width              | Viper `int` is 32-bit. The `& 0xFF` masks in `_unpack_pixels_to_buf` prevent sign-extension.                                                                                                                                                       |
| GRB layout                       | MicroPython NeoPixel stores G at byte 0, R at byte 1, B at byte 2. The Viper function matches this. Do not change the byte order.                                                                                                                  |
| `GLOBAL_RENDER_BUFFER` is shared | All 30 trays share one render buffer. The slice assignment (`tray_pixel_buffer[5:69] = pixel_buffer`) must happen immediately after `PixelBuffer()` returns, before the next tray's call overwrites it. This is already the existing call pattern. |
| `power_grid.py` compatibility    | `PowerGrid.Update()` passes a list comprehension to `SetPixelData`. `ENABLE_POWER_GRID` is `False` on the main device so this is not a current concern. Update it before enabling.                                                                 |
