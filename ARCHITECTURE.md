# Architecture

Living document. Updated as decisions are confirmed in conversation. If something isn't
here, it's either not yet discussed or not yet confirmed for the forward direction.
For broader (but more speculative) familiarization notes, see `_familiarization/`.

**Decisions are renegotiable by default.** Entries explicitly tagged `committed` are
locked — don't reopen without an explicit ask. See
[CLAUDE.md § Design flexibility](CLAUDE.md#design-flexibility).

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

### Board variant on hand

The actual Pico 2 W in David's stock is the **Pimoroni Pico Plus 2 W**
(Adafruit product 6243). Same RP2350 + Raspberry Pi RM2 wireless module as
the bare Pico 2 W, with a few extras worth knowing about:

- **8 MB onboard PSRAM.** Substantially more memory headroom than the bare
  Pico 2 W. Relevant to the
  [drop-the-palette / 4-byte-aligned-ints animation refactor](TODO.md#captured-perf-idea--drop-the-palette-store-full-rgb-ints).
- **USB-C** for power and programming.
- **Qwiic / STEMMA QT (I2C) connector** and a **JST-SH 3-pin SWD debug
  header.**
- **No U.FL pad on the carrier.** The RM2's onboard chip antenna is the
  only easy Wi-Fi option; an external antenna would require module-level
  soldering. Reflected in the
  [Wi-Fi remediation order](TODO.md#confirm-wi-fi-works-inside-the-panel-frame).
- Otherwise standard Pico 2 W pinout.

### Frame allocation

The three Picos distribute across the two physical frames as follows:

- **Right frame:** the card-tray controller. Owns everything on the right
  board — 30 trays, bus seven-segs, bus switchboard sinks, card
  identification.
- **Left frame:** the other two Picos, dividing left-board responsibility.
  Likely split: one handles the NeoPixel grids (wings + transformer 8×8s),
  the other handles the seven-segs and switchboard endpoints. Final split
  will depend on per-Pico load once we benchmark.

**The switchboard spans both frames.** Sources live on the left board
(wing outputs, transformer outputs); sinks live on both (transformer
inputs on left, bus inputs on right). The current polling-based
switchboard implementation can't scan across two physically separate
Picos — it requires per-source-pulse coordination with sinks. We've
committed to **no installed wiring between frames** (cables are the
patrons' transient guitar leads, nothing else), which forces a redesign:
sources broadcast a distinguishing pattern, sinks read it independently
and report what they see. This is now **pre-MVP and on the critical
path** — see
[TODO § Switchboard protocol redesign](TODO.md#switchboard-protocol-redesign).

### Performance target

Animation target is **30 FPS** for all NeoPixel grids, with seven-seg
and switchboard updates appearing visually instant to the kids. Goal is
not committed — it can relax if the hardware doesn't reach it — but it's
the design driver behind the PIO + Viper work and the multi-Pico
topology. David's preference is to **add more Picos before adding
inter-frame wiring or sacrificing 30 FPS**.

**Realized state (2026-05-09):** the right-board card-tray controller (single Pico 2 W,
2,220 pixels on one chain at 800 kbps) is wire-bound at **~12 FPS effective**. PIO write
takes ~67 ms (2,220 px × 30 µs); the loop is now ~99% CPU-saturated, with the WS2812 line
the bottleneck — not Python, not the PIO program, not the buffer copy. Reaching 30 FPS on
this Pico requires either bumping the PIO bit rate (WS2812B variants typically tolerate
1.0–1.6 Mbps over short runs) or splitting the chain into two parallel state machines on
different data pins. Other controllers driving smaller chains are not wire-bound.

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

The current `KNOWN_DEVICES` registry also contains an entry for an ESP32-S3 Feather
TFT — that's **dev/test legacy from the migration, not a deployment target**.
Leave the entry and any ESP32-specific code paths alone for now (they're useful as
a backup dev board), but don't let their presence shape design decisions; they'll
be removed before we ship.

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

**Wi-Fi + MQTT.** USB-host is being retired and the existing custom TCP/JSON
code is also a transitional shape — the wire protocol from each Pico to the
[executive](#executive-layer) is **MQTT**, mediated by a broker. Better fit
than custom TCP for "many publishers, one broker," and it keeps the long-tail
option open of the executive logic eventually moving inside Horizons (which
reportedly ships with an MQTT integration point), with the Picos publishing
to that broker directly.

This is a decision, not a `committed` lock — renegotiable per the
[design-flexibility principle](CLAUDE.md#design-flexibility) if we hit
specific problems with MQTT in MicroPython or with the broker model.

Each Pico is its own peer to the broker. There is no inter-Pico communication
by design — all coordination flows through the broker / executive. The Picos
never speak to the simulator directly; the executive owns that link.

Outstanding hardware verification: the panel frames are sheet metal — see
[TODO.md § Confirm Wi-Fi works inside the panel frame](TODO.md#confirm-wi-fi-works-inside-the-panel-frame).
If the frame is too RF-opaque, fallbacks include an external antenna lead
through the frame, a wired access point, or partially walking back the
USB → Wi-Fi refactor.

### Broker placement

The MQTT broker lives on **the Mac executive itself for now**. The Mac is an
~5-year-old Mac Mini — somewhat underpowered, but the broker load at our
scale shouldn't stress it.

**Future option to revisit** (gated on the
[Wi-Fi-in-frame question](TODO.md#confirm-wi-fi-works-inside-the-panel-frame)
landing): move the broker — and potentially the executive itself — to one of
the **two high-spec PCs in Alex's control booth** that already run Thorium.
Reasons it's attractive:

- More horsepower than the Mac Mini.
- Horizons reportedly ships with its own MQTT broker, so if Horizons becomes
  the deployment target, integrating against the control-booth broker is a
  smaller delta than running our own.

Reason it's not yet committed: the control booth is across the space-sim
suite from the engineering room, compounding the Wi-Fi signal-attenuation
question. Needs the network-signal work to land first before this is even a
serious option.

---

## Diagnostics

A deployed Pico lives inside a sealed metal frame with no console attached. When
something goes wrong — TCP can't reach the executive after a Mac swap, a sensor
init fails, a watchdog fires — the classic "look at the serial output" path
isn't available.

**Each Pico signals unrecoverable errors through whatever display surface it
owns** (`committed`):

- **Card-tray controller** and **left-panel controller** — flash distinctive
  red patterns on their NeoPixels.
- **Switchboard / display controller** — flash numeric error codes on the
  seven-segment displays.

The model is the old PC BIOS POST beep-codes idea: a known-distinctive output
that doesn't depend on comms or a working host. Future-us walks up to the rig,
sees "this Pico is flashing red, that's not normal," greps the codebase for the
pattern, and finds out what failed.

**Implementation requirement:** every error pattern is documented as a code
comment at the point where it's raised — pattern shape / number plus a
plain-English description — so the failure can be diagnosed without logs, a
console, or a working executive.

The initial motivating case is the fixed-IP-bind failure scenario from
[Comms](#comms) hardening, but the framework applies generally to any
hard-to-diagnose unrecoverable error.

In addition, **each deployed Pico exposes a hidden USB port through the
frame** (`committed`, MVP-required) — patron-invisible but accessible without
opening the frame. Visual signaling is the read-only error-reporting path;
USB pass-through is what makes firmware updates and interactive debugging
possible post-deploy. Without it, any code change to a deployed Pico would
require disassembling the frame, which isn't viable. The two together cover
the read and write sides of deployed-Pico maintenance.

Code catalog, per-Pico implementation, and USB-pass-through design candidates
live in [TODO.md § Diagnostics](TODO.md#diagnostics).

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

- **Comms hardening / security.** Application-layer only — `committed`: no SSID
  work, no router configuration, no VLANs. Hardening lives in the firmware and
  executive. Starting point is **fixed-IP bind on each Pico's TCP listener**
  (no TLS, optional shared-secret as a second layer); the deploy-path story for
  the IP-bind is the real open question. Threat model is "school kid with a
  network scanner," not nation-state. Tracked in
  [TODO § Security / hardening](TODO.md#security--hardening).
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

- **Horizons read-in.** Horizons reportedly has several extensibility points
  worth understanding properly — both the MQTT integration point and whatever
  else is in there. Decision-relevant for the eventual sim choice and for
  whether the executive logic ever moves inside Horizons.
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
