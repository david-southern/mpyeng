# 04 — Refactoring Backlog

Prioritized for impact on **maintainability** of the active firmware
(`engineering-board/engineering-board/`). Performance work is split out into the next-steps
doc — these are pure quality-of-life items unless otherwise noted.

> Caveat: `AGENTS.md` in that subtree explicitly says "no opportunistic refactoring" and
> "no tests unless asked." This list assumes you'll authorize each item before I touch it.

## Tier 1 — Worth doing soon

### R1. Finish `organization-refactor.plan.md`
The plan is written, partially executed (per-subsystem package dirs exist with
`constants.py` / `*_manager.py` / class-per-file split), but not all imports may have been
fully cleaned up and the plan calls out specific risks (deploy script paths, sys.path in
`convert_animations.py`). Verify completion against the plan's Phase 4 checklist
(`ruff`/`pyright` clean, deploy script unchanged). If anything is still on the old layout,
finish it. **Why now:** every subsequent refactor builds on this skeleton.

### R2. Eliminate `eng_utils.py` + `device_manager.py` import cycle
`utils/eng_utils.py:46` does `from utils.device_manager import DeviceManager` *at module
bottom*, and `device_manager.py` imports `logger` and `set_flags` from `eng_utils` at the
top. The cycle works only because `eng_utils` exposes `set_flags` before the late
import — a fragile arrangement. Move `set_flags` and `logger` to a tiny
`utils/_bootstrap.py` (or similar) that has no dependency on `device_manager`. Both modules
then import from there cleanly.

### R3. Replace `set_flags` injection into `eng_utils` globals
`DeviceManager.__init__` writes flag values into `eng_utils`'s `globals()`. Subsystems do
`if DeviceManager.IsEnabled(...):` instead of consuming those module globals — so the
injection happens but isn't actually consumed. Either remove the injection or make the
consumption explicit. Action-at-a-distance like this is a maintenance trap.

### R4. Drop the `# pyright: reportAttributeAccessIssue=false` suppressions
Several files (notably `device_manager.py:1`) suppress entire pyright categories at file
scope to silence MicroPython-specific issues. Tighter, line-scoped `# type: ignore[...]`
markers limit blast radius and keep the type checker useful elsewhere in the file.

### R5. Centralize `logger` levels and gate noisy logs at runtime
Today every `logger.info` runs unconditionally. The `HEARTBEAT_LOGGING`, `showProtocolDiags`,
`showDemoData`, etc. booleans in `main.py` gate *some* logs but it's ad-hoc. Add a single
`LOG_LEVEL` (or per-subsystem flag dict) and fold the `show*Diags` flags into it.
Memory/perf-sensitive: f-string formatting still runs in MicroPython if the call is reached.

### R6. Split `DeviceConfiguration.system_flags` into typed structure
Today `system_flags` is `dict[str, bool]` keyed by string constants from `Systems`. A
mistyped `Systems.POWER_GRD` would silently pass — `IsEnabled(...)` returns False on miss.
Either move to a frozen `IntFlag` enum + bitmask, or wrap the dict in a class that validates
keys at construction. Same idea for `PinNames` (currently a deeply nested class hierarchy of
string constants — fine but a single typo kills a board silently).

### R7. Make pin-reservation completeness checkable
`DeviceConfiguration` enforces no-duplicates but not "every pin a subsystem will need is
present." Subsystems currently fail with `KeyError` deep in init when a pin isn't
reserved. Add a per-subsystem method that *declares* required pins and validate against it
at startup so the failure is "PowerGrid needs `pixels.power_grid`, not configured for
`Pico 2 W`" rather than a generic KeyError trace.

## Tier 2 — Worth doing eventually

### R8. Module-load side effects → explicit init
Every `*_manager.py` runs side effects on import: builds singletons, allocates pixel ranges,
configures pins. Conditional imports in `main.py` work around this but it's brittle (any
inadvertent import re-triggers init). Convert managers to a two-phase `Manager()` ctor +
`Manager.Initialize()` pattern, with `main.py` calling `Initialize()` explicitly. Bonus:
makes the boot order visible in one place.

### R9. Clarify the `power_card_tray.py` / `tray_manager.py` boundary
The plan splits `PowerCardTray` (one tray) from `PowerTrayManagerClass` (singleton
fleet manager). Verify the split is clean and the tray class doesn't reach back into the
manager. Same audit for `card_reader/`, `power_grid/`, `power_display/`, `switchboard/`.

### R10. Consolidate `tm1637.py` and `dave_tm1637.py`
The plan keeps both ("unused backup, keep, don't delete"). That's a preservation choice from
the migration phase. Once you trust `dave_tm1637`, delete the unused one — comments in the
file should explain *why* one exists if both are kept long-term, otherwise this is just
clutter.

### R11. PascalCase Python conventions — pick a lane
The codebase mixes PascalCase (`IsEnabled`, `Power`, `SetPixelData`) with snake_case
(`update_demo_data`, `log_free_ram`, `register_timer`). Decide on either:
(a) PEP 8 everywhere, or (b) PascalCase for public class API, snake_case for module-level
free functions (which is roughly the *current* split, just unwritten). Document the choice
in `AGENTS.md` so it's not relitigated each session.

### R12. Move `ANIMATION_TARGET_FPS` and other magic numbers into constants per package
Constants like `ANIMATION_TARGET_FPS` (currently 5, per the optimization plan), tray pixel
counts, brightness defaults, profile-report cadence — surface these in each
package's `constants.py` with comments on the units and tuning rationale. Several are
inlined in `main.py` today (`HEARTBEAT_FREQUENCY_SEC`, `PROFILE_REPORT_FREQUENCY_SEC`,
`DEMO_DATA_FREQUENCY_SEC`, `PROTOCOL_FREQUENCY_SEC`).

### R13. `PowerGrid.SetPixelData` caller compatibility
The Viper plan flags that `PowerGrid.Update()` passes a list comprehension to
`SetPixelData` rather than an `array.array('I')`. `ENABLE_POWER_GRID` is False on the main
device today, so it's latent — but if you ever flip it on without updating the caller,
it'll break in a Viper-typed branch. Update the call site preemptively.

### R14. Split `card_manager.py` per the plan
The plan has step 18 splitting `card_manager.py` into `card_reader/{constants,
card_reader, reader_manager}.py` and pulling `_MCP3008` / `_AnalogIn` into `utils/mcp3008.py`.
If this hasn't been completed, finishing it removes the last bundled-responsibilities file
from the active tree.

### R15. Tidy up the C# host-client situation
Two things to untangle:

1. **`engineering-board/engineering-board-usb-client-csharp/`** is just an abandoned
   placeholder dir (`.vscode/` only). Delete it — the actual C# client lives at
   `engineering-board/engineering-board/host_comms/`.
2. **`host_comms/`** itself needs three small refactors when there's time:
   - Rename `usb-protocol-client.csproj` / `.sln` / `RootNamespace` —
     it's been TCP since the port; "usb" in the name is a lie.
   - Replace the FT232H-era `README.md` with current TCP setup instructions.
   - Move the hardcoded `EngineeringBoardIP` / `DefaultTCPPort` from
     `CircuitPythonBoardManager.cs` into config (matching the `TODO` comment already
     in that file).
   - Make sure the directory is excluded from any firmware deploy script
     (`deploy-micropython.ps1` / `mpremote cp` patterns) so the C# tree never gets
     copied to the Pico.

## Tier 3 — Quality-of-life

### R16. Move repo-root research notes into a `docs/` folder
`thorium-power-notes.txt` and `thorium-qraphql-notes.txt` (note the typo: "qraphql" — keep
or rename?) are research transcripts, not specs. Put them under `docs/research/` so the
repo root reflects only buildable artifacts. Same for the `assets/` design files —
arguably belongs under `docs/hardware/` instead of next to code.

### R17. Standardize `code.py` (CircuitPython) vs `main.py` (MicroPython) hand-off
The CircuitPython side projects (`neo-trellis`, `prop-maker`, `current-monitor-circuitpython`)
use `code.py`; the MicroPython side uses `main.py`. That's correct per each runtime's
convention. Just document it in a top-level `README.md` so it's not surprising.

### R18. Top-level `README.md` is missing
There is no README at the repo root. Even a 30-line orientation file ("this repo holds the
Thorium engineering-board firmware, plus side projects, see `_familiarization/` for
details") would save future-you a lot of re-orientation.

### R19. Attic survey
`attic/` holds frozen prototypes from at least four different platforms (Arduino,
Pi-engine-room, Phaser.js, RFID/PlatformIO, old .NET, CircuitPython). For each: confirm
whether you'd ever want to revive it. If not, delete it from this branch. If yes, add a
one-paragraph `attic/<name>/STATUS.md` describing what it was, why it stopped, and what
would be needed to restart.

### R20. The `engineering-board-assets/` directory
I didn't deeply explore this — likely board layouts, schematics, BOM. If it's binary
artifacts only, consider moving it out of the firmware repo into a separate hardware repo
or Git LFS. Binaries in the same repo as code make `git clone` slow over time.

## Items NOT recommended for refactoring

- **`AGENTS.md` itself** — it captures real preferences about how to work with this code.
  Leave it.
- **The PIO-based `local_neopixel.py`** — it's recently rewritten, well-commented, and
  performance-critical. Don't touch unless you have a specific reason.
- **The Manager-singleton pattern overall** — though OO purists would object, it's
  well-suited to a single-board single-app firmware and replacing it with DI would be pure
  cost. Live with it.
- **CircuitPython side projects** — fine where they are, no maintenance cost to ignore them.
