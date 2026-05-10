# 03 — Technical Overview

Focused on `engineering-board/engineering-board/` — that's the live firmware. Side projects
are touched on at the end.

## Boot and startup sequence

`main.py` is the entry point. The execution order is intentional and tightly coupled:

1. Imports `utils.profiling`, `utils.eng_utils`, `utils.device_manager`,
   `utils.demo_data_manager` unconditionally.
2. **`utils.eng_utils` triggers `from utils.device_manager import DeviceManager`** at module
   bottom (line 46). That construction:
   - Reads `machine.unique_id()` and hex-formats it.
   - Looks up the device in `KNOWN_DEVICES` (a `dict[str, DeviceConfiguration]`).
   - On match: pulls `system_flags` and `pin_reservations` out of the immutable
     `DeviceConfiguration`, then calls `set_flags()` to **inject those flags into
     `eng_utils`'s module globals**. This is how subsystem enable/disable propagates.
   - Validates: rejects `ANY_*` group flags in configs, detects duplicate pin reservations.
   - Computes derived `ANY_SWITCHBOARD` / `ANY_PIXEL_STRIP` flags as the OR of left/right.
3. `main.py` then does **conditional imports** based on `DeviceManager.IsEnabled(...)` — so a
   board configured without a switchboard never imports `switchboard_manager`.
4. Each subsystem's manager class is constructed **at module load time** (singletons). They
   wire up pins, allocate pixel ranges, instantiate drivers.
5. `main.py` registers timers (`TIMER_PROTOCOL`, `TIMER_HEARTBEAT`,
   `TIMER_DEMO_DATA`, `TIMER_PROFILE_REPORT`, `TIMER_UNKNOWN_DEVICE_LOG`) and profiles
   (`PROFILE_PROTOCOL`, `PROFILE_DEMO_DATA`, `PROFILE_HEARTBEAT`).
6. `mainLoop()` runs forever. If the device is unrecognized, it logs an error every second
   and does nothing else. Otherwise:
   - 100 Hz: `ProtocolManager.HandleComms()` polls the TCP socket for Thorium commands.
   - 4 Hz: `DemoDataManager.update_demo_data()` (canned data when not connected) +
     `PowerGridManager.Update()`.
   - Every loop iteration: `PowerTrayManager.Update()` (animation frame advance).
   - 0.5 Hz: optional heartbeat log.
   - 0.1 Hz: `report_all_profiles()` dumps timing stats.

## Subsystem map

```
main.py
 ├─ utils/
 │   ├─ device_manager.py       Boards, Systems, PinNames, DeviceConfiguration, DeviceManager
 │   ├─ eng_utils.py            logger, register_timer/check_timer, set_flags, SlowLog,
 │   │                          gridToStripIndex (serpentine NeoPixel mapping)
 │   ├─ profiling.py            register_profile, start/stop_profile, report_all_profiles,
 │   │                          log_free_ram
 │   ├─ color_utils.py          packed-int color helpers, NEO_PACKED_BPP, buffer_to/from packed
 │   ├─ pixel_strip_manager.py  shared NeoPixel controller — pixel-range reservation + writes
 │   ├─ demo_data_manager.py    fake reactor/system/transformer power data when unconnected;
 │   │                          Debouncer; SystemPower data class
 │   └─ protocol_resources.py   wire-format data classes: EnginePower, SystemPower,
 │                              TransformerPower, json_string()
 ├─ drivers/
 │   ├─ named_pin.py            NamedPin abstraction — pin-by-string → machine.Pin
 │   ├─ local_neopixel.py       RP2350 PIO-based WS2812 driver (asm_pio program included)
 │   ├─ mcp3008.py              SPI ADC driver (8-channel, used for card-resistor reading)
 │   └─ tm1637.py               4-digit 7-segment driver
 ├─ comms/
 │   ├─ constants.py            SER_PROTO_* command codes, delimiters
 │   └─ protocol_manager.py     Wi-Fi STA, TCP server :PORT, line-based command parser
 ├─ card_reader/                MCP3008 ADC channel scan → match resistor value to card ID
 ├─ card_tray/                  Per-tray PowerCardTray + PowerTrayManager singleton (30 trays)
 ├─ power_cards/                Card metadata, animation frames, animation engine
 │   ├─ power_card.py           PowerCard — wraps a card_id with its animation frames
 │   ├─ animation.py            CARD_ANIMATION_DEFS, GLOBAL_PALETTE_LOOKUP, GLOBAL_RENDER_BUFFER,
 │   │                          PowerCardAnimation.PixelBuffer(progress, brightness)
 │   ├─ card_ids.py             Resistor-value → PowerCardIds table (ID per physical card)
 │   ├─ categories.py           Card category groupings (life support / weapons / propulsion / …)
 │   └─ frames/*.py             One file per card type holding bytes-of-palette-indices frames
 ├─ power_grid/                 Aggregate power-flow NeoPixel grid + RandomGridGenerator
 ├─ power_display/              TM1637 display fleet (per-bus, per-transformer, per-wing)
 └─ switchboard/                Source-to-sink physical patch panel (left/right wing →
                                transformers/buses)
```

## Animation pipeline (the hot path)

This is where the design effort is concentrated and where the Viper optimization plan lives.

1. **Frame storage.** Each card type has N frames of 64 bytes each. Each byte is a palette
   index (0–255). Stored as `bytes()` in `power_cards/frames/*.py` and aggregated into
   `CARD_ANIMATION_DEFS` in `power_cards/animation.py`.
2. **Palette.** `GLOBAL_PALETTE_LOOKUP` is a 256-entry list of packed `0x00RRGGBB` ints,
   regenerated when global brightness changes.
3. **Render buffer.** `GLOBAL_RENDER_BUFFER` is a 64-entry list — one tray's worth of pixels.
   `PixelBuffer(progress, brightness)` does a Python LUT loop:
   `buf[i] = lut[frame[i]]`. Currently shared across all 30 trays — must be consumed before
   the next call.
4. **Pixel write.** `PixelStripManager.SetPixelData(start, count, packedInts)` unpacks each
   packed int into a `(r, g, b)` tuple and writes to `np[i]` — which internally rearranges to
   GRB and writes 3 bytes into `np.buf`.
5. **PowerCardTray.Update()** runs three `SetPixelData` calls per tray per frame:
   top-status (5 px), grid (64 px), bottom-status (5 px). 30 trays × 3 = **90 calls/frame**.
6. **NeoPixel wire transfer.** `np.write()` triggers the PIO state machine to clock all
   2,220 LEDs out at 800 kbps — **fixed cost ~67 ms; this is the dominant bottleneck.**
   The right-board card-tray controller is wire-bound at ~12 FPS effective. See
   `docs/ws2812-timing.xlsx` for the math; raising this ceiling requires bumping the PIO
   bit rate or splitting the chain across parallel state machines.

The optimization plan (`viper-animation-optimization.plan.md`) replaces steps 3 and 4 with
`@micropython.viper` functions, switches the buffers to `array.array('I')` to expose
`ptr32`/`ptr8`, and collapses the three writes per tray into one contiguous slice
assignment. Read that file before touching this path.

## Communications

`comms/protocol_manager.py` runs a **TCP server on the device** over Wi-Fi:

- Connects via `network.WLAN(network.STA_IF)` using `secrets.WIFI_SSID` / `WIFI_PASSWORD`.
- Binds `socket(AF_INET, SOCK_STREAM)` to `secrets.TCP_PORT` and listens non-blocking.
- Accepts a single client (`self.__client`).
- Read loop is line-based with `\r\n` delimiters and a per-frame pending-CRLF delay.
- Command vocabulary in `comms/constants.py`:
  - `SER_PROTO_INIT_HEADER` / `SER_PROTO_INIT_RESPONSE` — handshake.
  - `SER_PROTO_ENGINE_POWER_QUERY|SET|RESPONSE`
  - `SER_PROTO_TRANSFORMER_POWER_QUERY|SET|RESPONSE`
  - `SER_PROTO_SYSTEM_POWER_QUERY|SET|RESPONSE`
  - `SER_PROTO_OK|ERR|DIAGS`
- Payloads use `protocol_resources.json_string()` to serialize `EnginePower`,
  `SystemPower`, `TransformerPower` instances.

This protocol is **custom**, not Thorium's GraphQL. The translation between the two lives
on the host side (in `engine_sim_blazor/` for Thorium, or `engineering-board-usb-client-*`
for direct testing). FT232H notes in `host_comms/README.md` cover the USB-serial fallback
path.

## Device identification & pin allocation

`DeviceManager` is the keystone. It enables the codebase to ship a *single* image to two
boards (and any future ones) with different pinouts, by matching the MCU's hardware
`unique_id()` against `KNOWN_DEVICES`. Each entry is an immutable `DeviceConfiguration`
with:

- `system_flags: dict[str, bool]` — which subsystems are wired on this board.
- `pin_reservations: dict[str, NamedPin]` — name-keyed pin map.

Key invariants enforced at construction:
- `ANY_*` group flags are forbidden in raw configs.
- Pin reservations must be unique (no two functions on the same pin).
- Group flags are derived after the fact (`ANY_SWITCHBOARD = LEFT or RIGHT`).

Subsystems consume pins via `DeviceManager.ResolvePin(PinNames.X.Y)` and consume system
flags via `DeviceManager.IsEnabled(Systems.X)`.

This is also why `main.py` does conditional imports — to avoid loading drivers for
hardware that's not present, both for memory and to avoid pin-allocation failures.

## Profiling and observability

`utils/profiling.py` provides a lightweight named-profile API:

- `register_profile("name") -> handle`
- `start_profile(handle)` / `stop_profile(handle)`
- `report_all_profiles()` dumps cumulative ticks per profile

`log_free_ram(label)` calls `gc.collect()` and logs `gc.mem_free()`. Used at startup, after
big allocations (NeoPixel buffer construction), and on demand.

`SlowLog(message)` from `eng_utils` rate-limits identical log messages to once per second
with a count — useful for noisy inner loops.

`logger.info` / `logger.error` prefix every line with `time.ticks_ms() - APP_START_TIME`
in seconds, formatted as `"  X.XXXs"`. There is no log-level filter beyond info/error.

## Build/deploy

- `deploy-micropython.ps1` is the canonical deploy script. It uses `mpremote cp` to push
  changed files to the device.
- `activate-venv.ps1` activates the host-side Python virtualenv.
- `secrets.py` (per-board) holds Wi-Fi creds and TCP port — *not* checked in (`.gitignore`
  matches it).
- Frame data is precomputed at design time in `power-card-animation-designer/` and
  `convert_animations.py` writes the result into `power_cards/frames/*.py`.

## Host-side: Blazor dashboards

Both `dotnet/engine-sim/` and `dotnet/engine_sim_blazor/` are Blazor WASM apps with the same
project shape (`Client/Server/Shared/Helpers/CircuitPythonBoardManager`). The difference is
the data source:

- `engine-sim/Server/Program.cs` registers `CommsManager` for **direct serial** to the
  hardware via FT232H.
- `engine_sim_blazor/Server/Program.cs` adds a `GraphQLHttpClient` pointed at
  `Configuration["GraphQLURI"]` and a `GraphQLConsumer` scoped service. Talks to **Thorium**
  directly.

Use the second one when the bridge is running with Thorium; use the first one for hardware
bench testing without Thorium in the loop.

## Side project: solar-system-generator

`solar-system-generator/SSG.Client/Program.cs` registers MudBlazor + custom services
(`SSGEventService`, `ConfigurationService`). Procedurally generates solar systems with
orbital mechanics, renders in three.js (loaded via webpack/SCSS in `package.json`), exports
COLLADA/PLY. Deployed to `david-southern.github.io/ssg-demo/`. Independent of everything
else; lives here probably out of convenience.

## Game framework: neo-trellis

`neo-trellis/code.py` boots a `TrellisGameSelector` that lets users pick between Battleship,
Minesweeper, and Random. Games inherit from `TrellisGameBase` (`Enable`, `Disable`,
`buttonPressed(x,y,event)`, `Update`). `NeoTrellisManager` wraps Adafruit's `MultiTrellis`
with subscription-style button events. `AnimationManager` does callback-driven frame timing
with delta-time. Pure CircuitPython, Adafruit ecosystem. Side project.
