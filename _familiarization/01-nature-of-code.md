# 01 — Nature of the Code

## Headline

This repo is a **multi-language hardware/software ecosystem** centered on a custom physical
**engineering bridge controller** for the [Thorium](https://github.com/Thorium-Sim/thorium)
starship-bridge simulator. The active code is overwhelmingly **embedded firmware (MicroPython,
some lingering CircuitPython)**, with a smaller orbit of **host-side .NET/Blazor dashboards**
and **Python desktop tooling**. There is also one unrelated **Blazor WebAssembly + three.js**
side project (`solar-system-generator`).

You are on the `micropython` branch of `mpyeng`, which appears to be the active development
branch — the most recent commits are MicroPython conversion work and a PIO-based NeoPixel
rewrite. `main` is older.

## What "kind" of code this is

| Layer | Stack | State |
| --- | --- | --- |
| Embedded firmware (production) | **MicroPython 1.28.0** on **RP2350 Pico 2 W** & **Feather ESP32-S3 TFT** | Active, primary focus |
| Embedded firmware (legacy) | **CircuitPython** on Adafruit Feather/Metro boards | Being ported to MicroPython |
| Host-side dashboards | **Blazor WebAssembly + ASP.NET Core 6.0** | One Thorium-connected, one hardware-direct |
| Host-side tooling | **Python 3 + Tkinter** desktop apps | Functional |
| Host-side USB clients | **Python 3** (working), **C#** (stub) | Mixed |
| Side project | **Blazor WASM + three.js + MudBlazor** orbital sim | Working, deployed to GH Pages |
| Attic | Arduino C++/PlatformIO, old CircuitPython, Phaser.js, Pi-side simulators | Frozen prototypes |

## Languages, runtimes, and toolchains

- **Python (MicroPython flavor)** — most current code under `engineering-board/`,
  `micropython-starter/`, `mp-card-resistance-tester/`. Targets ESP32-S3 and RP2350.
  Performance-sensitive — `@micropython.viper` is being introduced for hot loops.
- **Python (CircuitPython flavor)** — `neo-trellis/`, `prop-maker/`,
  `current-monitor-circuitpython/`, `examples/`, `card-resistance-tester/`. Uses Adafruit
  ecosystem (`displayio`, `adafruit_*` libraries, `code.py` entry point).
- **Python (CPython 3.x)** — desktop tooling: `power-card-animation-designer/` (Tkinter),
  `engineering-board-usb-client-python/` (FT232H over `pyftdi`/`Iot.Device`), and
  `convert_animations.py` build-time helpers.
- **C# / .NET 6.0** — Blazor WebAssembly clients in `dotnet/engine-sim/` and
  `dotnet/engine_sim_blazor/`, plus `solar-system-generator/SSG.Client/` and
  `engineering-board/host_comms/` (FT232H driver via `Microsoft.Iot.Device.Bindings`).
- **PowerShell** — deploy scripts (`deploy-micropython.ps1`,
  `install-circuitpython-library.ps1`, `activate-venv.ps1`).
- **PIO assembly (RP2 inline)** — `drivers/local_neopixel.py` uses `@rp2.asm_pio` for the
  WS2812 timing program.
- **JavaScript/TypeScript + Webpack + SCSS** — only inside `solar-system-generator/SSG.Client/`
  for three.js asset processing.

## Style and conventions

- **PascalCase property/method names in Python** (`Power`, `IsConnected`, `IsEnabled`,
  `SetPixelData`). This is non-PEP8 but consistent across the firmware codebase — it appears
  intentional, modeled on the C# host-client style.
- **Manager singleton pattern** is the dominant architectural unit. Every subsystem has a
  `XxxManager` class that gets instantiated once at module load
  (e.g. `DeviceManager = DeviceManagerClass()`), then accessed as a module global. This is the
  CircuitPython-era pattern carried into MicroPython.
- **Module-level enable flags via `set_flags`** — `DeviceManager` writes Boolean flags
  into `eng_utils`'s globals so subsystems can `if DeviceManager.IsEnabled(Systems.X):` gate
  imports and behavior. Enables a single firmware image to run on multiple board variants.
- **One class per file** is the *target* (per `organization-refactor.plan.md`) but not yet
  fully realized — `power_card_tray.py`, `card_manager.py`, etc. still bundle multiple
  responsibilities.
- **`AGENTS.md` is present** in `engineering-board/` and dictates strict minimal-change /
  no-opportunistic-refactor / no-tests policy for AI agents working in that subtree. Honor
  it when editing.
- **`ruff.toml`** governs Python linting in `engineering-board/`.
- **Type hints + Pylance** are used for IDE-side checking; MicroPython stubs
  (`micropython-esp32-stubs`) are installed for IntelliSense. `# pyright: ignore` comments
  appear where MicroPython-only imports trip the type checker.
- **Indentation/formatting** appears auto-formatted by ruff in newer files.

## Performance posture

Performance is treated as a first-class concern — see `viper-animation-optimization.plan.md`
which calls out that the firmware is driving **2,220 NeoPixels (30 trays × 74 LEDs)** and
the per-frame Python loop is the critical hotspot. The plan moves render-buffer LUT
expansion and pixel-buffer unpacking into `@micropython.viper` functions writing directly
into `np.buf`. The codebase already includes profiling hooks (`utils/profiling.py`) and
free-RAM logging (`log_free_ram`).

## What this code is *not*

- **Not test-driven.** There are no unit tests in the repo and `AGENTS.md` explicitly says
  "Do NOT introduce any tests unless explicitly requested." Verification is integration-style
  — flash to hardware, run, watch the LEDs.
- **Not packaged.** No `pyproject.toml`, no published library, no package manager entry.
  Files are deployed via `mpremote cp` directly to MicroPython filesystems.
- **Not multi-author.** All commits are solo work, mostly direct-to-branch.
- **Not GraphQL-active in firmware.** The firmware uses a custom **TCP line protocol** over
  Wi-Fi (see `comms/protocol_manager.py`). The GraphQL bits are in the
  `engine_sim_blazor/` host-side dashboard which talks to Thorium directly. The two notes
  files at the repo root (`thorium-power-notes.txt`, `thorium-qraphql-notes.txt`) are
  research transcripts, not specs.
