# 02 — Project Explanation

## What this project IS

The headline product is a **physical "Engineering Bridge" controller** that kids stand in front
of during a [Thorium](https://thoriumsim.com) starship-bridge simulation. Thorium is a free,
open-source crewed-bridge simulator (think Artemis-style) used for STEM/educational starship
experiences. The kids assigned to "Engineering" use this physical board to manage power on
the simulated ship: **route power from reactors through transformers and buses to the
ship's systems** (shields, thrusters, lasers, life-support, etc.), each represented by a
**physical "power card"** that they slot into a tray on the board.

The board talks to the Thorium server (via TCP for the firmware, GraphQL for the host-side
Blazor variant) so power-allocation actions on the physical board change the state of the
simulated ship in real time, and reactor/wing/system state from the sim feeds back to the
board's LEDs and 7-segment displays.

## Who it's for

A solo build by you (David), aimed at a kid-facing space-sim experience. The design tone
matches that — cooperative play, tactile feedback (LEDs, switches, RFID-ish card detection,
seven-segment readouts), no production-ops baggage.

## The hardware story (as inferred)

A single board uses a **MicroPython MCU** (RP2350 Pico 2 W in production, with a Feather
ESP32-S3 TFT used for development/secondary roles) as its brain. Around the MCU:

- **Power card trays** — 30 of them, each holds one physical card. Each tray has 74
  WS2812 NeoPixels (5 status LEDs top + 64-pixel 8×8 animation grid + 5 status LEDs bottom).
  Total **2,220 LEDs** driven from a single PIO state machine on the RP2350. Cards are
  identified by per-card resistor values measured through the **MCP3008 SPI ADC** (4 chips,
  8 channels each = 32 reader channels).
- **Power displays** — multiple 4-digit **TM1637 7-segment** modules showing per-bus,
  per-transformer, per-wing power numbers.
- **Switchboard** — physical patch-panel-style routing for the kids to wire power sources
  (left wing / right wing / four transformers) to sinks (transformers / six buses).
- **Power grid display** — a separate NeoPixel grid showing aggregate power flow.
- **External +5V supply** is required when running TM1637 displays (a code comment notes
  the board crashes erratically without it).

The board enumerates its identity via the MCU's `unique_id()` and looks itself up in
`DeviceManager.KNOWN_DEVICES` to pick its pin map and which subsystems are wired. Two
device IDs are currently registered (one ESP32-S3, one Pico 2 W).

## Subdirectory map (what each top-level folder *is*)

### Active embedded firmware

- **`engineering-board/engineering-board/`** — *the product*. Production MicroPython firmware
  for the bridge controller. Orchestrated by `main.py`, broken into per-subsystem packages
  (`card_reader/`, `card_tray/`, `power_grid/`, `power_display/`, `switchboard/`, `comms/`,
  `power_cards/`). Drivers in `drivers/`. Shared infra in `utils/`.
- **`engineering-board/micropython-starter/`** — minimal MicroPython template that mirrors the
  shared `utils/` layout from `engineering-board/`. Acts as a starting point / proof of life
  for new device IDs. Code is *similar but not shared* — it's a copy-evolve sibling, not a
  library import.
- **`engineering-board/mp-card-resistance-tester/`** — MicroPython port of the
  CircuitPython resistance-measurement bench tool (work in progress).
- **`engineering-board/card-resistance-tester/`** — original CircuitPython resistance-
  measurement tool, still functional. Used to measure the resistors on physical power cards
  so they can be entered into `card_ids.py`.
- **`neo-trellis/`** — CircuitPython game framework for the Adafruit NeoTrellis 8×8 button
  grid. Includes Battleship, Minesweeper, and Random games. Side project, not part of the
  bridge controller.
- **`prop-maker/`** — minimal CircuitPython sketch for an Adafruit Prop-Maker Feather. Stub.
- **`current-monitor-circuitpython/`** — CircuitPython INA219+SH1107 OLED bench
  power-monitor. Standalone tool.
- **`examples/buzzer/`, `examples/prop-maker/`** — CircuitPython feature demos with
  manager classes for NeoSlider, PixGrid, RotaryEncoder, 7-seg display.

### Host-side software

- **`engineering-board/engineering-board/host_comms/`** — **the C# host-side client.**
  net8.0 `Exe` (`usb-protocol-client.csproj` + matching `.sln`). This is where the
  engineering-board protocol was originally developed and where it's been kept up to
  date — including a port from USB-serial to TCP/JSON (see `TcpProtocolHandler.cs`).
  Contains `Program.cs`, `CircuitPythonBoardManager/` (board, manager, handler),
  `ProtocolResources.cs`, and a full `Helpers/` utility set. The `usb-protocol-client`
  name and the FT232H-era `README.md` are both stale; the code itself is current and
  runnable. Misleadingly nested *inside* the firmware project's directory because David
  copied it in during the TCP refactor — should be excluded from the firmware deploy.
- **`engineering-board/engineering-board-usb-client-python/`** — Python 3 port of the
  C# client above, written a few years later when one of the kids wanted to learn
  programming. Not the canonical implementation.
- **`engineering-board/engineering-board-usb-client-csharp/`** — empty placeholder dir
  (just `.vscode/`). Probably an abandoned spot before the C# project landed in
  `host_comms/`. Safe to delete.
- **`engineering-board/power-card-animation-designer/`** — Python 3 + Tkinter GUI on the
  desktop. Lets you visually paint the 8×8 animation frames per power card and the color
  masks (wave, fade, lightning, etc.). Outputs the data that ends up in
  `engineering-board/power_cards/frames/*.py` (one file per card type — laser_cannon, warp_field,
  shields, thrusters, etc.).
- **`dotnet/engine-sim/`** — Blazor WebAssembly + ASP.NET Core 6.0 dashboard that talks to
  the firmware *directly* over USB-serial. Hardware-bench mode.
- **`dotnet/engine_sim_blazor/`** — same shape but adds a **GraphQL client** pointed at the
  Thorium server. Production dashboard mode. Renders Thorium reactor/wing/system state in a
  browser, complementary to the physical board.
- **`engineering-board/engineering-board-assets/`** — board-design artifacts (probably KiCAD
  / Illustrator).

### Side project (unrelated to the bridge)

- **`solar-system-generator/SSG.Client/`** — Blazor WebAssembly app using **MudBlazor** UI
  and **three.js** to procedurally generate solar systems with orbital mechanics. Exports
  COLLADA/PLY for use in other engines. Deployed to GitHub Pages
  (`david-southern.github.io/ssg-demo/`). Has no relationship to the engineering board.

### Reference / archived

- **`assets/`** — schematics, BOMs, AI/PNG board layouts, audio-jack/seven-seg/phaser
  reference material. Documentation, not code.
- **`attic/`** — frozen prototypes from earlier directions: Arduino C++ reactor controllers
  (`arduino-reactor-core/`, FastLED-based), Pi-side simulators (`pi-engine-room/`,
  `pi-sim/`), the original .NET engine-sim, an old Phaser.js attempt, RFID-test PlatformIO
  experiments, early CircuitPython work. Don't expect any of this to build or run.
- **`thorium-power-notes.txt`, `thorium-qraphql-notes.txt`** — your reverse-engineering
  notes on Thorium's GraphQL/power model. Not specs; transcripts of "what does Thorium do."

## Relationships at a glance

```
                         Thorium Sim Server
                  (http://172.19.48.1:4444/graphql)
                              |
              +---------------+----------------+
              |                                |
     custom TCP/JSON                    GraphQL subs
              |                                |
   ┌──────────────────────┐         ┌─────────────────────┐
   │ engineering-board    │         │ dotnet/             │
   │ MicroPython firmware │         │ engine_sim_blazor   │
   │ (Pico 2 W / ESP32-S3)│         │ (Blazor WASM)       │
   └──────────┬───────────┘         └─────────────────────┘
              │ FT232H USB
              ▼
   ┌──────────────────────┐         ┌─────────────────────┐
   │ usb-client-python    │         │ dotnet/engine-sim   │
   │ (testing)            │         │ (hw-direct mode)    │
   └──────────────────────┘         └─────────────────────┘

   Animation data is generated by:
   power-card-animation-designer (Python/Tkinter)
       --emits-->  power_cards/frames/*.py  (firmware data files)
```

## What's "active" on the `micropython` branch

Recent commit messages tell the story:
- `MP Conversion Step 1` / `Step 1.1` — moving from CircuitPython to MicroPython.
- `Major bytearray refactor completed` — animation data format change.
- `Optimize deployment script fix animation data representation`.
- `Pre-work on viper optimization plan` / `Optimization plan update` — performance push.
- `Refactor how DeviceManager handles Pin reservations` — recent.
- `First part of re-writing NeoPixel to use PIO rather than bit-banging (MPY bitstream)` —
  newest commit (HEAD).

So: a CircuitPython→MicroPython port, a NeoPixel/PIO rewrite, and a Viper-based pixel-loop
optimization pass are all currently in flight.
