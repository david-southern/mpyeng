# May 11 AM — Session Handoff

Microcontroller work completed in the May 10 evening + May 11 morning sessions.
Captures the current state of the firmware tree so a new Claude session can
pick up without re-discovery.

## What got done

### 1. Single-channel DMA in `LocalNeoPixel` (deployed, validated)

Replaced the blocking `sm.put(self.buf, 8)` in
`engineering-board/engineering-board/drivers/local_neopixel.py` with a DMA-driven
push to the SM's TX FIFO. Three additions to that file:

- **`_PIO_BASE`** tuple of RP2350 PIO MMIO bases (PIO0/1/2 at
  `0x50200000` / `0x50300000` / `0x50400000`). FIFO address for SM `sm_id` is
  `_PIO_BASE[sm_id // 4] + 0x10 + 4 * (sm_id % 4)`.
- **`_preshift_to_wire_buf` Viper helper** that shifts each pixel word left
  by 8 (`0x00GGRRBB → 0xGGRRBB00`) into a shadow wire buffer. DMA can't do the
  inline shift `sm.put()` did, so the driver owns it now. Cost is ~30 ns/word
  in Viper — negligible.
- **DMA channel + control word** allocated in `__init__` per instance.
  `pack_ctrl(size=2, inc_read=True, inc_write=False, treq_sel=...)`. TX DREQ
  for SM `sm_id` is `(sm_id // 4) * 8 + (sm_id % 4)` — i.e. 0..3 for PIO0,
  8..11 for PIO1, 16..19 for PIO2.

`write()` now: spin on prior DMA, pre-shift main buffer → wire buffer, configure
DMA with `trigger=True`, return immediately.

**Empirical results (CARD_TRAY_COUNT=5 single-chain proxy, deployed May 10–11):**

| Metric | Pre-DMA | Post-DMA |
|---|---|---|
| `psm_right` avg | ~11 ms | 0.36–0.55 ms |
| Outer loop | 29.3 Hz | 29.1 Hz (capped at the 30 Hz target) |
| Idle | ~75–80% | ~91–93% (9100–9260 ms / 10000) |
| RAM cost | — | +1.9 KB per strip (shadow wire buffer) |

Validated overnight (10:35 PM May 10 → 9:36 AM May 11) — no degradation.

### 2. Long Range Comms animation: 1 frame → 28 frames

`engineering-board/engineering-board/power_cards/frames/long_range_comms.py`
replaced. Now 4 color cycles (red/green/blue/yellow) × 7 wave positions = 28
unique frames.

**Wave shape:** compact 3-row "Y" that travels up the display from the white
2-pixel ship at row 0:

- Bow: cols 3,4 at 100% (palette `offset+19`); widens to cols 2–5 on frame 6
- Inside trail: cols 2,5 at ~50% (palette `offset+6`), 1 row behind bow
- Outside trail: cols 1,6 at 25% (palette `offset+0`), 2 rows behind bow

Wave elements emerge sequentially over the first three frames of each cycle
(bow only → bow + inside → full Y), then advance one row per frame. **Previous
row positions go dark — no persistent trail.** This was a tweak David asked
for after seeing the first version, which had a cumulative wake.

Color cycle uses the bright/mid/dim entries of each palette family:
- Red (Weapons offset 20): 39 / 26 / 20
- Green (Power offset 100): 119 / 106 / 100
- Blue (Defensive offset 140): 159 / 146 / 140
- Yellow (offset 80): 99 / 86 / 80
- Ship is BRIGHT_WHITE = 234

### 3. Animation memory checkpoint added

`engineering-board/engineering-board/power_cards/animation.py` got a new
`log_free_ram("anim-overhead")` call placed between the
`from power_cards.frames import ...` block and the `CARD_ANIMATION_DEFS` dict
construction. Three RAM checkpoints now appear at boot:

1. `pre-animation-baking` — before any frame source loaded
2. `anim-overhead` — source `FRAMES` lists for all 25 modules resident, no
   baking yet
3. `post-animation-baking` — baked `array.array('I')` frames also resident

`(2) − (1)` is pure source-bytes cost; `(3) − (2)` is pure baked-storage cost.
Without this marker, expanding any animation's frame count gets *partially*
attributed to Fusion Engines (the first animation baked, which sees the
already-loaded source FRAMES of all later modules).

## Current working tree (uncommitted)

```
M engineering-board/engineering-board/drivers/local_neopixel.py     ← DMA
M engineering-board/engineering-board/power_cards/animation.py       ← anim-overhead marker
M engineering-board/engineering-board/power_cards/frames/long_range_comms.py  ← 28-frame Y-wave
M engineering-board/engineering-board/card_tray/constants.py         ← CARD_TRAY_COUNT = 5 (TEMP)
M engineering-board/engineering-board/power_cards/power_card.py      ← David edited (only-LRC display tweak)
```

`card_tray/constants.py` still has the `CARD_TRAY_COUNT = 5  # TEMP 2026-05-09 ...`
marker that David added for the single-chain perf preview. Plan: keep it until
the multi-chain refactor lands and gets validated, then revert to 30 (or to
whatever the per-chain count works out to).

## What's next

**The multi-chain DMA refactor** is the headline upcoming work, captured in
`TODO.md § Animation pipeline performance`:

- Split the 2,220-pixel chain into **6 parallel chains × 5 cards × 74 px**
- Each chain on its own GPIO data pin, its own PIO state machine, its own
  DMA channel
- All 6 DMAs triggered concurrently in `write()` so the 6 wire transfers run
  in parallel — wall-clock should stay at ~11 ms (single-chain time) instead of
  serializing back to ~67 ms (current 30-tray total)

**Hardware prerequisite:** David needs to wire 5 additional GPIO data pins and
physically re-segment the chain into 6 segments. This may or may not be done
when the new session starts — confirm before attempting end-to-end validation.

**Architecture call to make:** option A vs B
- **A** (recommended): new `MultiChainNeoPixel` class in `local_neopixel.py`
  that takes a list of pins + per-chain pixel counts. Presents the same flat
  buffer API as `LocalNeoPixel` so `PixelStripManager` is untouched except for
  the constructor swap.
- **B**: six `PixelStripManager`s in `PowerTrayManager`, one per chain, with
  trays owning a chain index. Cleaner separation but ripples into
  `PowerCardTray`. More churn for less benefit.

**Pivot fallback** if DMA work bogs down: `@micropython.viper` round-robin
function that walks all 6 SM TX FIFO registers in a tight loop. CPU stays
busy for the full 11 ms, but the parallel SM drain still delivers the ~6×
wire-time win.

## Key gotchas / context for the new session

- **Hardware is original WS2812, not WS2812B** — no overclock path. 1.6 Mbps
  was tested 2026-05-09 on a single ~80-pixel grid and produced no output at
  all. Don't suggest overclock as a path to higher FPS. Captured in
  `~/.claude/projects/.../memory/hardware_pixel_grids.md`.
- **MicroPython `rp2.DMA` is assumed available** — first single-channel deploy
  didn't error, so it works on the device's MicroPython build (v1.28.0 per
  the boot log). Multi-channel work can rely on it.
- **The deploy script does mtime-based comparison.** On May 10 the
  `long_range_comms.py` edit silently didn't deploy across three deploy
  attempts (showed up only as `Skipped 68 file(s) with unchanged timestamp`).
  If a code change doesn't seem to take effect, check whether the file actually
  got copied — or `touch` it before deploying.
- **Profile interpretation:** `power_trays*5` = outer loop calls (the `*5` is
  the `CARD_TRAY_COUNT` multiplier in the profile name). `psm_right*` is the
  pixel-strip wire write — sub-1 ms post-DMA, was ~11 ms pre-DMA. The first
  10-second profile interval after boot reports `Idle = 0` because it hasn't
  accumulated yet — disregard. Subsequent intervals are honest.
- **`PixelStripManager` has a dirty flag.** It only writes to wire when at
  least one pixel changed since last refresh. So `psm_right*` call counts vary
  between intervals (96–248 over various 10s windows) depending on how many
  outer ticks dirty the buffer.

## Branch / repo status

- Active branch: `micropython` (per project CLAUDE.md, this is becoming the
  new `main`; no need to reconcile with current `main`).
- All work on this branch is uncommitted. David typically commits at his own
  cadence — don't auto-commit.
