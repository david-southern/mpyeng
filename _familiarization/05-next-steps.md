# 05 — Next Steps

What looks like "the next thing to do" based on commits, plan files, TODOs, and gaps. Not
prescriptive — these are options, ordered by what seems closest to your current line of
work.

## In flight (finish these)

### N1. Land the Viper animation optimization
`viper-animation-optimization.plan.md` is detailed and ready. Six tasks: convert the global
buffers to `array.array('I')`, add `_expand_frame_lut` + `_unpack_pixels_to_buf` Viper
functions, collapse the three `SetPixelData` calls per tray into one, then benchmark and
bump `ANIMATION_TARGET_FPS` (currently 5). Expected outcome: 2,220 LEDs at a usable frame
rate without Python interpreter overhead per pixel. **Wall-clock estimate (you + me):
1–2 sessions.** Most of the mechanical work is straightforward; the "did it actually go
faster" benchmarking is the part that matters.

### N2. Finish the PIO-based NeoPixel rewrite
The HEAD commit is `0819260 First part of re-writing NeoPixel to use PIO rather than
bit-banging (MPY bitstream)`. "First part" implies follow-up. Confirm:
- All call sites have moved off the bit-banged driver.
- `local_neopixel.py` matches the WS2812 spec including the 50µs latch (the existing code
  comment notes "this program does not appear to enforce the 50 microsecond latch time at
  the end of...") — figure out whether that's a TODO or a known-OK thing.
- Compare brightness/timing on the bench vs. previous implementation.

### N3. Verify the organization-refactor is complete
See R1 in the refactoring doc. Run `ruff` and `pyright` against the firmware and check that
nothing imports the pre-refactor flat layout. If anything still does, finish the move.

## Hardware-side TODOs you've left yourself

### N4. ESP32-S3 pin verification in `demo_data_manager.py`
The Explore subagent flagged 4 TODOs in `utils/demo_data_manager.py` for ESP32-S3 pins
(GP4, GP5, GP6, GP13). Trace what these are for and either pin-map them in
`DeviceManager.KNOWN_DEVICES["F412FA59B3E0"]` or remove the TODOs.

### N5. External +5V supply requirement for TM1637 displays
`device_manager.py:15-17` carries this note as a comment: running TM1637 without external
+5V crashes the Arduino erratically. Two follow-ups:
- Document this in the build instructions (probably a hardware doc, not code).
- If you can detect "no external +5V" at boot, fail fast with a clear error rather than
  a mid-frame crash.

### N6. Wire up the Card Reader path on Pico 2 W
`KNOWN_DEVICES["B29EF8BE7E93C6C6"]` (Pico 2 W) reserves SPI + 4 chip-selects for MCP3008s
but its `system_flags` dict doesn't include `Systems.CARD_READER: True`. Either the wiring
is staged but not enabled yet, or this is a bug. Verify intent.

## New work

### N7. Implement the C# USB client (or delete it)
`engineering-board/engineering-board-usb-client-csharp/` is an empty placeholder. The
Python equivalent at `engineering-board-usb-client-python/` already speaks the protocol —
porting to C# is a 1-session job and gives you a Windows-native debugging tool. If you
have no plan to ever use it, delete instead.

### N8. Finalize the `mp-card-resistance-tester/` MicroPython port
The CircuitPython tester (`card-resistance-tester/`) is functional. The MP port exists but
is marked work-in-progress. Finish so you have one runtime instead of two for this tool.

### N9. Auto-discovery for new physical cards
`card_ids.py` maps measured resistor values to card IDs via the resistance tester. Today
adding a card means: (1) measure with the tester, (2) hand-edit `card_ids.py`,
(3) add an entry to `categories.py`, (4) author frames in `power-card-animation-designer/`,
(5) run `convert_animations.py`. Worth a small CLI that does steps 2 and 3 from a
measurement input — would shorten the loop when you're prototyping new cards with kids
during play-testing.

### N10. Hot-reload from the animation designer
Right now `power-card-animation-designer/` saves to `power_cards/frames/*.py` and you
re-deploy the firmware to see the change. A WiFi-side "load this frame data live" command
in the protocol would make iteration much faster — pair it with the existing
`comms/protocol_manager.py` rather than building a new transport.

### N11. Thorium GraphQL → firmware TCP bridge
Today the firmware speaks a custom TCP/JSON protocol; Thorium speaks GraphQL. The Blazor
host (`engine_sim_blazor`) already has a `GraphQLConsumer` — extend it (or write a tiny
sidecar) to also relay relevant Thorium subscriptions to the firmware. Avoids duplicating
the GraphQL client in MicroPython, which would be painful.

## Verification / observability

### N12. Standing integration-test rig
Per your stated preference for integration over unit tests: a "plug in a board, run a
canned protocol script, watch for expected pixel/display state" rig would catch regressions
during refactors. Could live in `engineering-board-usb-client-python/` as a smoke-test
mode. The existing `DemoDataManager` makes for a useful canned-input source.

### N13. Profile output in a structured form
`report_all_profiles()` currently prints to stdout. If you want to spot regressions over
time, dump it as CSV/JSON over the protocol so you can chart it externally. Low priority
unless you're already doing perf work.

### N14. Free-RAM telemetry
`log_free_ram(label)` is great spot-check — pairing it with a circular buffer of
"free RAM at frame N" reported on demand would help you spot leaks during long sessions.

## Documentation

### N15. Top-level `README.md`
There isn't one. See R18. A short orientation reduces re-onboarding cost — including for
me, on the next session.

### N16. Wiring / hardware reference
The `assets/` folder has board layouts and BOMs. A `docs/hardware-reference.md` mapping
each `PinNames` constant to a physical pin per device variant would close the loop between
the firmware and the actual board.

### N17. "How a frame becomes light" walkthrough
Newcomers (or future-you in 6 months) would benefit from a single doc tracing one frame
from `power-card-animation-designer/` through `convert_animations.py` →
`power_cards/frames/*.py` → `CARD_ANIMATION_DEFS` → `PixelBuffer()` → `SetPixelData()` →
PIO → physical LED. The whole pipeline isn't long and the explanation is mostly already
written across the two `.plan.md` files — consolidate.

## Side projects (optional)

### N18. Decide the future of `solar-system-generator`
It's a working Blazor + three.js procedural orbital sim deployed to GH Pages. It sits in
this repo for convenience but has no relationship to the bridge controller. Either move it
to its own repo or accept that the cohabitation is permanent and add it to a top-level
README so it's not surprising.

### N19. `neo-trellis` — pick a destination
The game framework (Battleship/Minesweeper/Random) is functional. If it's purely for fun,
fine. If you want it to be a published thing, it deserves its own repo. As-is it adds
~6 files of CircuitPython that aren't building toward the bridge.

## What I'd do first when you're back

1. Tell me whether to proceed with **N1 (Viper optimization)** — it's the most concrete
   and the plan is already written.
2. Ask you about **N6 (Card Reader on Pico 2 W)** — it's a one-line `system_flags` change
   if it's just an oversight, or a real "not done yet" if not.
3. Confirm you want **R1 / R2** before I touch the import structure.

Everything else can wait for direction.
