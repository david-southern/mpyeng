# ESP32-S3 NeoPixel Animation Performance — Implementation Plan

## Project Context

- **Platform:** ESP32-S3 with MicroPython
- **Goal:** Drive 2220 NeoPixel LEDs at 10 FPS (currently achieving ~3 FPS)
- **Current State:**
    - 255 pre-baked frames stored in power_cards/animation.py:CARD_ANIMATION_DEFS as `bytes()` (≈2MB
      total → lives in PSRAM)
    - A single GLOBAL_PALETTE_LOOKUP list[int] used to do fast color lookups from the byte arrays
    - A single GLOBAL_RENDER_BUFFER list[int] that the card animation code writes in
      CardAnimationHelpers.PixelBuffer(). This occurs every frame.
    - A PowerCardTray.Update method that calls PixelBuffer and sends it to
      PixelStripManager.SetPixelData
    - SetPixelData transcribes the buffer into the NeoPixel strip via `np[i] = (r, g, b)` per pixel,
      which is the bottleneck
- **Approach:**
    - Replace the Python per-pixel unpack loop with a `@micropython.viper` function that writes
      directly into the NeoPixel internal buffer, bypassing the `__setitem__` API entirely
    - Consider all other per-frame hotspot functions for conversion to Viper as well, but the unpack
      loop is the primary target
    - The pre-baked frame data (≈2MB) will remain in PSRAM, which is acceptable since it is read
      sequentially
    - The NeoPixel working buffer (8880 bytes: 2220 pixels \* 4 bytes per pixel) should be allocated in SRAM at boot
    - The GLOBAL_PALETTE_LOOKUP and GLOBAL_RENDER_BUFFER will be allocated in SRAM
    - The entire per-frame render processing should not create any new objects, or access PSRAM except
      for the initial read of the packed frame data into the GLOBAL_RENDER_BUFFER

---

## Root Cause Summary

The 3 FPS bottleneck is caused by:

1. **Python interpreter loop overhead** — 2000+ iterations per frame in bytecode
2. **Tuple allocation per pixel** — 2000+ heap objects per frame, thrashing the GC
3. **NeoPixel `__setitem__` overhead** — Python-level API call per pixel
4. **PSRAM latency** — frame data in PSRAM accessed with random/slow patterns from Python

The wire transfer (`np.write()`) costs a fixed ~6ms at 800kHz and is not the bottleneck.

---

## Frame Data Format

Each frame is stored as a flat `bytes()` which is transcribed into a list[int] of packed 32-bit integers:

```
Bit layout per pixel: 0x00RRGGBB
```

The Viper function unpacks these into the NeoPixel buffer in **GRB byte order**
(as required by WS2812/NeoPixel protocol):

```
dst[i*3 + 0] = G  (bits 15:8)
dst[i*3 + 1] = R  (bits 23:16)
dst[i*3 + 2] = B  (bits 7:0)
```

---

## Implementation Tasks

### Task 1 — Verify Existing Frame Data Format

Before writing any new code, confirm the data formats used in the existing render pipeline as
described in the Current State section.

---

### Task 2 — Allocate SRAM Working Buffer at Boot

All SRAM buffers must be allocated **before** PSRAM fills the heap.
Place this at the very top of `animation.py`, before any large allocations:

```python
import micropython
import neopixel
import machine

NUM_PIXELS = 2220
PIN_NUM    = 48    # adjust to actual data pin

# Allocate the NeoPixel object early so its internal buf lands in SRAM.
# The internal bytearray np.buf (NUM_PIXELS * 3 bytes = 6660 bytes) must
# be in SRAM for fast writes from the Viper function.
pin = machine.Pin(PIN_NUM)
np  = neopixel.NeoPixel(pin, NUM_PIXELS)

# np.buf is now a 6660-byte bytearray in SRAM.
# Do NOT reassign np.buf after this point.
```

**Why this matters:** On ESP32-S3 with PSRAM enabled, MicroPython's heap allocator
will begin placing objects in PSRAM once SRAM fills up. Allocating `np` first
ensures the 6KB working buffer stays in fast SRAM. Frame data (≈2MB) will
naturally live in PSRAM, which is acceptable since it is read sequentially.

---

### Task 3 — Write the Viper Unpack Function

Add this function to your animation module. The `ptr32` and `ptr8` Viper types
compile to direct pointer dereferences — there is no Python object allocation
inside the loop whatsoever.

```python
@micropython.viper
def unpack_frame(src: ptr32, dst: ptr8, n: int):
    """
    Unpack n pixels from packed-int frame buffer (src) into NeoPixel
    GRB byte buffer (dst). No heap allocation. Runs as native machine code.

    src: array.array('I') of 0x00RRGGBB packed pixels  (PSRAM is fine)
    dst: np.buf bytearray, 3 bytes per pixel, GRB order (must be SRAM)
    n:   number of pixels
    """
    i: int = 0
    while i < n:
        p: int = src[i]
        dst[i * 3]     = (p >> 8)  & 0xFF   # G
        dst[i * 3 + 1] = (p >> 16) & 0xFF   # R
        dst[i * 3 + 2] =  p        & 0xFF   # B
        i += 1
```

**Note on `ptr32` with `array.array`:** Viper's `ptr32` accepts any object that
exposes a raw buffer (which `array.array('I')` does). Do not wrap in `memoryview`
before passing — pass the array object directly.

---

### Task 4 — Rewrite the Animation Loop

Replace the existing per-pixel Python loop with:

```python
import utime

def run_animation(frames, np, loop=True):
    """
    frames: list/tuple of array.array('I') objects, one per animation frame
    np:     NeoPixel object (np.buf must be pre-allocated in SRAM, see Task 2)
    loop:   if True, repeat animation indefinitely
    """
    n = len(np)  # number of pixels

    while True:
        for frame in frames:
            t0 = utime.ticks_ms()

            unpack_frame(frame, np.buf, n)  # Viper: ~3-6ms from PSRAM
            np.write()                       # Wire transfer: ~6ms fixed

            elapsed = utime.ticks_diff(utime.ticks_ms(), t0)
            # Optional: print FPS during development
            # print("frame ms:", elapsed, " FPS:", 1000 // elapsed)

        if not loop:
            break
```

**What was removed:**

- `for i in range(n):` Python loop — eliminated
- `np[i] = (r, g, b)` tuple creation — eliminated
- All per-pixel `__setitem__` calls — eliminated
- GC pressure from 2000+ tuple allocations per frame — eliminated

---

### Task 5 — Suppress GC During Playback

The GC can fire mid-frame and cause jitter. Frame timing is critical, so:

```python
import gc

gc.collect()          # collect once before starting
gc.disable()          # disable during playback
run_animation(frames, np)
gc.enable()
```

Since the Viper loop allocates nothing, GC has nothing to collect during playback.
It is safe to disable it for the duration of the animation loop.

---

### Task 6 — Benchmark and Validate

**Expected results:**

- Avg frame time: 10–15ms
- Achieved FPS: 12–20 FPS
- The wire floor of ~6ms is unavoidable physics

---

## Performance Model

| Component             | Time estimate | Notes                                  |
| --------------------- | ------------- | -------------------------------------- |
| Viper unpack loop     | 3–6 ms        | Sequential PSRAM reads, cache-friendly |
| `np.write()` (wire)   | ~6.1 ms       | Fixed: 2220 × 24 bits @ 800kHz         |
| Python frame overhead | < 0.5 ms      | Loop bookkeeping, negligible           |
| **Total per frame**   | **~10–13 ms** | **~75–100 FPS theoretical ceiling**    |

The 10 FPS target (100ms budget) has ~87–90ms of headroom after the Viper approach.

## Key Constraints & Gotchas

| Concern                 | Detail                                                                                         |
| ----------------------- | ---------------------------------------------------------------------------------------------- |
| `array.array` type code | Must be `'I'` (unsigned int, 4 bytes). `'i'` (signed) also works but check your existing data. |
| Pixel count             | Hardcode `NUM_PIXELS` or pass `len(np)` — avoid calling `len()` inside the hot loop            |
| PSRAM frame data        | Sequential access pattern is cache-friendly; PSRAM latency is mitigated                        |
| `np.buf` ownership      | Do not reassign `np.buf`. The NeoPixel object owns this buffer. Write into it in-place.        |
| Viper integer width     | Viper `int` is 32-bit. The `& 0xFF` masks are necessary to avoid sign-extension issues.        |
