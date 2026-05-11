# space-sim

A custom **physical engineering room controller** for the school's space-sim program. Patrons
standing at the two engineering panels route power from reactors through transformers and buses to
ship systems by physically slotting **power cards** into trays and re-routing **electrical patch
connections** on a switchboard. Power-allocation actions on the physical board change the state of
the simulated ship in real time, and reactor/system state from the sim feeds back to the board's
LEDs and 7-segment displays.

The firmware lives at [`engineering-board/engineering-board/`](engineering-board/engineering-board/)
and runs on a Raspberry Pi Pico 2 W (RP2350) under MicroPython, with `@micropython.viper`
and PIO/DMA in the performance-sensitive paths. It drives **30 card trays × 74 WS2812
NeoPixels** (2,220 total) plus TM1637 seven-segments, identifies physical cards via per-card
resistors read through an MCP3008 ADC, scans the switchboard for routing changes, and
exchanges state with an executive layer over a custom TCP/JSON protocol on Wi-Fi.

The executive layer (a separate server-side app, not in this repo) bridges that protocol to
Thorium's GraphQL API. Boards are addressed by MCU `unique_id()` — a single firmware image
runs on multiple physical board variants, with `DeviceManager` injecting per-board pin maps
and subsystem flags at boot. See [`_familiarization/`](_familiarization/) for orientation
docs; [`ARCHITECTURE.md`](ARCHITECTURE.md) and [`TODO.md`](TODO.md) capture forward design
and parked work.

## Other projects in this repo

**Tooling and subprojects of the engineering bridge** (under `engineering-board/`):

- **[`power-card-animation-designer/`](engineering-board/power-card-animation-designer/)** — Python 3 + Tkinter desktop app for painting the 8×8 per-card animation frames that ship as data files in the firmware.
- **[`mp-card-resistance-tester/`](engineering-board/mp-card-resistance-tester/)** — MicroPython bench tool for measuring the identifying resistor on a physical power card.
- **[`micropython-starter/`](engineering-board/micropython-starter/)** — minimal MicroPython
  starting point for new microcontroller projects.
- **[`engineering-board-assets/`](engineering-board/engineering-board-assets/)** — board-design artifacts: Illustrator panel layouts, OpenSCAD/STL parts.

**Other props in the engineering room:**

- **[`pi-engine-room/`](pi-engine-room/)** — Raspberry-Pi-driven **warp-core prop**: Blazor WASM control UI, `WarpCoreController` animation engine (Chaser, Fog-1D, Fog-2D, Progress, Pulse effects), and an `rpi_kens` WS281x driver.
- **[`phaser/`](phaser/)** — Laser **phaser prop**: three implementations (CircuitPython, ESP32, native PlatformIO) plus design notes and wiring diagrams.

**Independent side projects:**

- **[`current-monitor-circuitpython/`](current-monitor-circuitpython/)** — Standalone CircuitPython bench tool: INA219 current sensor + SH1107 OLED display.
- **[`side-projects/neo-trellis/`](side-projects/neo-trellis/)** — CircuitPython game framework for the Adafruit NeoTrellis 8×8 button grid (Battleship, Minesweeper, Random).
- **[`side-projects/solar-system-generator/`](side-projects/solar-system-generator/)** — Unrelated Blazor WASM + three.js procedural orbital-mechanics sim, deployed independently to GitHub Pages.

**Frozen:**

- **[`attic/rfid-test/`](attic/rfid-test/)** — historical MFRC522 RFID card-identification experiment; predates the current resistor-divider approach. Kept for reference.
