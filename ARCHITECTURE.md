# Architecture

Living document. Updated as decisions are confirmed in conversation. If something isn't
here, it's either not yet discussed or not yet confirmed for the forward direction.
For broader (but more speculative) familiarization notes, see `_familiarization/`.

---

## Repo strategy

The plan of record is that **this branch (`micropython`) becomes the new `main`** once
the codebase is in good enough shape, and the current `main` is archived. The 2026-05-08
"Clean up all the ancient cruft" commit (`d5b3e6a`) on the old `main` will not be
reconciled with this branch — its file-level divergence is moot.

Until then, treat this branch as the authoritative working state.

---

## Embedded scope

**The MicroPython board controller is the only embedded project carried forward.**

Everything else with embedded code in this repo (`neo-trellis/`, `prop-maker/`,
`current-monitor-circuitpython/`, `examples/`, the CircuitPython
`card-resistance-tester/`, the in-flight MicroPython `mp-card-resistance-tester/`) is
either explicitly retired or pending triage. Don't treat any of it as load-bearing for
the forward direction.

---

## Controller topology

### History

Originally one MCU for both panels: Mega2560 → ESP32 → RP2350 (Pico 2 W). Each transition
was driven by ceiling problems on the prior chip — pin count first, then performance.

### Forward direction

The current Pico-pixel-optimization work makes it clear that even an RP2350 with
Viper-optimized inner loops can't drive the full LED count in a single image on a
single core within the desired frame budget. Combined with the inherited pin-count
constraints, the plan is to **split the controller into three Pico 2 Ws by role**,
each owning one subsystem slice:

| Role | Responsibility | Pixel load | Notes |
| --- | --- | --- | --- |
| Card-tray controller | Card-tray animations (right panel) | ~2,220 NeoPixels (30 trays × 74 LEDs) | Performance hot path. The PIO + Viper animation work targets this controller. |
| Switchboard / display controller | Switchboard scan + seven-segment displays | None | Bottleneck is digital I/O scan + TM1637 clocked writes, not NeoPixels. |
| Left-panel controller | Left-panel LED animations | ~768 NeoPixels (David's estimate, to verify) | Substantially less pixel load than the card-tray controller. |

(David previously referred to these as "Pico 1 / 2 / 3"; that was casual numbering
and not a board identity. The boards are interchangeable Pico 2 Ws — David has four
on hand currently, three roles assigned, one spare. More can be added if needed.)

**No external-comms responsibility is bundled into any one role.** The Pico 2 W's
onboard Wi-Fi means each board is its own peer to the executive — see
[Comms](#comms) below.

This is a **vague plan** at the topology level — the responsibility split above is
the current intent but pin maps and exact subsystem boundaries are not yet decided.

### Module-flags-by-hardware-ID pattern

The existing `DeviceManager` pattern in
`engineering-board/engineering-board/utils/device_manager.py` is **kept** under the
multi-Pico topology. Adding a Pico to the fleet is:

1. Read the new device's `machine.unique_id()`.
2. Add an entry to `DeviceManagerClass.KNOWN_DEVICES` with the appropriate
   `system_flags` and `pin_reservations`.
3. Conditional imports in `main.py` already do the right thing — only the subsystems
   flagged for that device's role get loaded.

A single firmware image can therefore continue to ship to all three Picos. No
per-controller fork.

---

## Power

**Single +5V bus. No separate 3.3V rail at supply level.**

The Pico 2 W's VSYS pin accepts 1.8–5.5V (per the
[Pico 2 W datasheet](docs/pico-2-w-datasheet.pdf)) and the on-board RT6150 buck-boost
SMPS produces the regulated 3.3V the RP2350 and its GPIO need. TM1637 displays and
other 5V-native peripherals are powered directly from the same bus.

This avoids the complexity of a dual-rail supply. It was made viable specifically by
the Pico's wide VSYS range — running 5V into a Mega2560 was fine; running 5V into a
Pico is also fine, and now we don't have to choose.

When connecting an external +5V supply alongside USB power for development, follow the
Pico datasheet's guidance: a Schottky diode (or P-channel MOSFET) in series with the
external supply path, so neither source back-feeds the other.

### Supply spec and brightness ceiling

Reference point: the existing **warp-core prop** on the bridge runs ~1000–1500
NeoPixels on a **10 A 5 V** supply with no observed brownouts. The engineering board
will spec **at least** that — probably more, given the card-tray controller alone
sees ~2,220 pixels — but **not enough to drive every pixel to full white
simultaneously** (which would be ~133 A peak, well outside any reasonable bench
supply).

Today the firmware compensates for the gap with a hard-coded brightness multiplier
of ~0.15 (look for `TRAY_BRIGHTNESS` and similar in `card_tray/`). That's an
acceptable prototype-stage clamp but a poor production answer:

- It limits headroom for highlight effects — a kid notices when the alert flash
  doesn't actually look brighter than baseline.
- It bakes the ceiling into the firmware rather than into the supply spec.

Forward direction: **size the supply for typical-use full-color content (not
all-pixels-white worst case)**, and replace the static multiplier with a smarter
software solution — likely dynamic per-frame current estimation with a real-time
clamp, or a pre-computed peak-brightness budget per animation. Detail to be
designed when we get there; tracked under
[Pending](#pending--to-be-discussed).

---

## Comms

### Current state — mid-refactor

The codebase has both a custom **USB-serial protocol** (Mega-era; lives in
`engineering-board/engineering-board-usb-client-python/`, `host_comms/` for the FT232H
notes, and the Blazor `engine-sim/` host-side dashboard) **and** a custom
**TCP/JSON-over-Wi-Fi protocol** (`engineering-board/engineering-board/comms/protocol_manager.py`).

Both exist because we're partway through a USB → Wi-Fi refactor that became viable
when the controller moved to the Pico 2 W. The original Mega2560 had no Wi-Fi and
David didn't want to set up an external Wi-Fi bridge for development, so USB-host was
the only option at the time.

### Forward direction

**Wi-Fi + TCP/JSON.** USB-host is being retired. **Each Pico runs its own TCP server
and connects independently to the [executive layer](#executive-layer).** There is
no inter-Pico communication by design — all coordination flows through the executive.
The Picos never speak to the simulator directly; the executive owns that link.

The Pico 2 W's onboard Wi-Fi makes "every controller is its own peer" the natural
shape, so we'll only add an inter-Pico bus (UART / SPI / I2C between boards) if a
real reason emerges. None has so far.

Outstanding hardware verification: the panel frames are sheet metal — see
[TODO.md § Confirm Wi-Fi works inside the panel frame](TODO.md#confirm-wi-fi-works-inside-the-panel-frame).
If the frame is too RF-opaque, fallbacks include an external antenna lead through the
frame, a wired access point, or partially walking back the USB → Wi-Fi refactor.

---

## Executive layer

A Mac in the engineering room runs an **executive** process that manages the high-level
game / puzzle logic and brokers between the starship simulator and the embedded
controllers. The Picos handle hardware — pixel writes, ADC scans, switchboard
debouncing, display updates — but **they don't make game-state decisions**.

The executive owns:

- **The STEM-puzzle loop.** Example: "power is fine → damage to the left wing, power
  lost → the kids must shuffle power cards around to restore critical systems."
  Decisions about what damage to inflict, when, and how to score the response live
  here, not on the Picos.
- **The simulator integration.** Thorium GraphQL (current target) or Horizons MQTT
  (possible future target) terminates at the executive. The Picos never speak to the
  simulator directly.
- **Cross-Pico coordination.** If a power-card move detected on Pico 1 (card-tray
  controller) needs to drive a seven-seg update on Pico 2, the executive observes
  and dispatches — the Picos don't gossip between themselves.

The interface from executive to Pico is a **command / query** protocol layered on
the WiFi/TCP transport already in `engineering-board/engineering-board/comms/`:

- *Queries* — "what's the state of the power buses?", "what cards are in the trays?",
  "what's the switchboard currently wired as?"
- *Commands* — "play animation X on card Y", "set bus N to power level P", "drop
  power on the left wing".

### Current state — to be designed

The two Blazor projects in `dotnet/` (`engine-sim/` and `engine_sim_blazor/`) are the
**seeds** of this executive layer, but they are out of date — they predate the current
firmware-side subsystems and the multi-Pico topology — and **none of the executive
logic above has been written yet**. The C# host-side client at
`engineering-board/engineering-board/host_comms/` is closer to current (already
TCP-ported and wire-compatible with the firmware) but is a smoke-test client, not the
executive.

Forward-direction questions still open:

- **Stack** — stay on .NET / Blazor, switch to Python, switch to a headless service?
- **Puzzle DSL** — code, config, or scripted-scenario file format?
- **UI surface** — dashboard for the engineering-room Mac, headless service with the
  Picos as the only "UI", or both?
- **Recovery** — on Pico restart, does the executive re-snapshot from the Pico, or
  drive state back from a cache?
- **Authoring tiers.** Initial puzzle authoring is David + Alex. As the program
  scales, Alex will likely want his content-team and scenario / actors-team
  students involved (see
  [school context](_familiarization/06-school-context.md#the-student-teams)).
  Whether the puzzle DSL is approachable by a 14-year-old becomes a real design
  constraint — the same multi-tier authorship problem the
  [animation designer](TODO.md#animation-designer-overhaul) has. Decide tiers
  before locking in the DSL.
- **Difficulty tiers.** Patrons are school kids 3rd–10th grade — the same
  scenario may be run for 8-year-olds and for 15-year-olds. The DSL needs to
  express scalable difficulty (separate scenarios per age band, graduated
  difficulty within a scenario, or some hybrid). Distinct from authoring
  tiers — that question is about who *creates*, this is about who *consumes*.
- **Authoring loop** — how new puzzle scenarios get written, tested, and shipped
  to the production Mac. Distinct from the tiers question above; this is workflow,
  that is language design.

---

## MVP / sim integration

The MVP requires integration with a starship-bridge simulator running elsewhere on the
network. The current target of record is **Thorium**, with caveats:

- The Thorium integration code in this repo (`dotnet/engine_sim_blazor/` GraphQL
  client; firmware-side TCP protocol shape) is **untested end-to-end**.
- It's 2–3 years old and predates most of the current card-tray / power-grid /
  switchboard subsystems.
- Thorium is hard to bring up locally. Alex DeBirk (STEM teacher at the school) has
  the only working instance, and David is rarely on-site.

The integration is **owned by the [executive layer](#executive-layer)**, not the
firmware. The Picos are insulated from the simulator's protocol entirely.

**Sim integration is the last work item in the project ordering.** Finish the rest of
the board first; integrate at the end.

By the time we get there, the target sim may have shifted. Alex has been trying to
migrate to **Horizons Starship Simulator** (MQTT-based, much friendlier integration
surface) for a year or two. Whether Thorium or Horizons is the deployment target is
a deploy-time decision, not a now decision. Keep the integration adapter loose enough
that the switch is local.

Tracked in [TODO.md § Finish the Thorium integration](TODO.md#finish-the-thorium-integration-deferred--last-item).

---

## Pending — to be discussed

Items likely to land in this document but not yet confirmed. Some are real design
topics that need their own session; others are smaller disambiguations.

### Design topics

- **Comms hardening / security.** The executive ↔ Pico TCP and the Pico Wi-Fi
  configuration need to be hardened so school kids on the same network can't reach
  the Picos or the executive outside the intended interface. Threat model is "school
  kid with a network sniffer," not nation-state — but the firmware is currently wide
  open. Tracked in [TODO § Security / hardening](TODO.md#security--hardening).
- **Warp-core prop integration.** The bridge has a pre-existing warp-core prop —
  ~1000–1500 NeoPixels driven by what's probably a Raspberry Pi 3 — that the
  executive will need to coordinate alongside the engineering-board controllers.
  Old controller code lives under `attic/pi-engine-room/WarpCoreController/` and
  adjacent projects; we'll need to audit what's still useful when designing the
  executive's prop-coordination surface. Tracked in
  [TODO § Integrate the warp-core prop](TODO.md#integrate-the-warp-core-prop-with-the-executive).
- **PIO + animation-pipeline design.** The PIO work in flight is exploratory —
  David's typical workflow is start coding, capture the design once the shape is
  clear. The existing `viper-animation-optimization.plan.md` is already out of date
  (Claude-generated weeks ago, before David was up to speed). Once Claude is up to
  speed on the project and the
  [emulator workflow](TODO.md#micropython-emulator--iteration-loop-for-claude) is in
  place, we'll generate a proper PIO + animation-pipeline design before touching
  the implementation. Includes the captured
  [4-byte-aligned ints idea](TODO.md#captured-perf-idea--4-byte-aligned-ints-throughout).
- **Software brightness ceiling.** Replace the static `TRAY_BRIGHTNESS ~0.15`
  multiplier with a real solution — see
  [Power § Supply spec and brightness ceiling](#supply-spec-and-brightness-ceiling).
- **Audio / DMX integration.** Whether the engineering board ever participates in
  the bridge's lighting and sound rig. Aspirational; recorded in
  [TODO § Long-range](TODO.md#long-range--not-anytime-soon).

### Smaller disambiguations

- **Wire-protocol shape.** Currently custom JSON over TCP. Might stay; might move to
  MQTT (especially attractive if Horizons ends up the deployment target).
  - David note: Pretty sure Micropython can do MQTT. I sort of like the idea of having the executive
    <==> pico link being MQTT even if we're still on Thorium. Horizons has a number of extensibility
    points (we need to get you read in on that at some point) I could see a future where the
    executive lives in Horizons and the Picos talk to it directly.
- **ESP32-S3 in `KNOWN_DEVICES`.** Today's registry has one ESP32-S3 (Feather TFT)
  and one Pico 2 W. Forward direction is three Pico 2 W roles. Does the ESP32-S3
  retire from the registry, stay around for dev/test, or take some specific role?
  - David Note: ESP32 is off the table. I still have it, but I'm pretty sure we'll get better
    results from RP2350, especially given the PIO work. Keep the current ESP32 code around in case I
    need another board for dev/test, but it will not be in the final deployment. Do not make any
    design or architectural decisions around it, I'll remove it before compromising our design.
- **Hardware-asset story.** `engineering-board-assets/`, OpenSCAD models,
  manufacturing files — including which were correctly vs. incorrectly removed in
  the 2026-05-08 `main`-branch cleanup.
- **Per-subsystem deep dives.** CardReader, PowerGrid, PowerDisplay, Switchboard,
  PowerTray.
- **Build / deploy story.** `mpremote`, `secrets.py` handling, multi-Pico flashing,
  executive deployment to the engineering-room Mac.

*(Already-placed: `dotnet/` engine-sim projects, `host_comms/`, and the USB clients —
see [Executive layer](#executive-layer) and [Comms](#comms).
`solar-system-generator/` is held long-range in
[TODO.md](TODO.md#long-range--not-anytime-soon).)*

This list will shrink as items move into the body and grow as the system-analyst
interview surfaces gaps.
