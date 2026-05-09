# TODO

Repo-level parked work. Maintained by hand and during conversation; not auto-generated.

---

## Tooling

### Set up Claude to read PDFs locally

PDF support in Claude's `Read` tool requires `pdftoppm` (from poppler-utils) on PATH.
It's not installed on the home dev machine — first hit on this came when fetching the
Pico 2 W datasheet 2026-05-08, which had to be answered via web search instead of reading
the PDF directly.

Install options:

- **Native Windows poppler binaries** — `winget install --id=oschwartz10612.Poppler` or
  download from the [poppler-windows](https://github.com/oschwartz10612/poppler-windows)
  releases, add `bin/` to PATH.
- **Via WSL** — `apt install poppler-utils`. Works if Claude is invoked from WSL or if a
  small wrapper bridges the call.
- **Python fallback** — a tiny `pdf-extract.py` using `pypdf` or `pdfplumber` that
  Claude can invoke via Bash if the native Read path stays awkward on Windows.

Native poppler is the lowest-friction option since `Read` already knows how to use it.

### MicroPython emulator + iteration loop for Claude

**Priority: Task #1, before any new firmware design work begins.** The PIO
design session is gated on this.

The current iteration loop is: Claude proposes a change → David flashes it to
a Pico → watches the result → reports back. That cycle is slow enough that it
heavily constrains how many design iterations we run per session. Tooling that
lets Claude exercise the firmware directly should pay back many times over.

#### Pencilled in: Wokwi as the primary emulator

Investigation 2026-05-09 — **Wokwi is the chosen path** (not `committed`;
revisit if it fights us in practice). Reasons:

- **PIO support works** for `@rp2.asm_pio` programs — verified via the
  `micropython-pio-7segment` example. The WS2812 driver should run as-is.
- **NeoPixel rendering is real** and configurable (rows × cols, serpentine
  wiring, square/circle pixelate modes). Visualizing one card animation at a
  time in the browser is a genuine win.
- **CLI + MCP integration** for AI-driven sim runs: `wokwi-cli` is headless,
  supports YAML automation scenarios with `--expect-text` / screenshot
  capture, and ships **experimental MCP** support so Claude can drive sims
  directly.
- **Free for personal use** (with the caveats below).

Accepted caveats:

- **RP2350 not yet supported in Wokwi.** Wokwi runs RP2040 (original Pico,
  Pico W). We'll target RP2040 for emulator runs. Should be a one-config
  change — the firmware uses no RP2350-specific surface (same `@rp2.asm_pio`
  syntax, same `machine` / `network` modules; RP2040's 264 KB SRAM is plenty
  for our footprint). Verify before committing.
- **Public projects on the free tier.** Unlisted/private projects require a
  paid plan. Revisit if the project becomes sensitive enough that public
  exposure is a problem.
- **Performance characteristics don't reflect real hardware** — functional
  correctness yes, timing no. Final perf tuning still requires real hardware.

Reference links to review:

- [Wokwi MicroPython docs](https://docs.wokwi.com/guides/micropython)
- [Wokwi Pi Pico reference](https://docs.wokwi.com/parts/wokwi-pi-pico)
- [Wokwi CLI usage](https://docs.wokwi.com/wokwi-ci/cli-usage)
- [Wokwi CLI getting started (CI / Actions)](https://docs.wokwi.com/wokwi-ci/getting-started)
- [Wokwi automation scenarios](https://docs.wokwi.com/wokwi-ci/automation-scenarios)
- [`wokwi-cli` GitHub](https://github.com/wokwi/wokwi-cli)
- [LED matrix component docs](https://docs.wokwi.com/parts/wokwi-led-matrix)
- [`micropython-pio-7segment` worked example](https://wokwi.com/projects/300936948537623048)
- [Wokwi pricing](https://wokwi.com/pricing)
- [RP2350 support tracking issue](https://github.com/wokwi/rp2040js/issues/142)

#### Backup: `rp2040-pio-emulator` for PIO-only verification

[NathanY3G/rp2040-pio-emulator](https://github.com/NathanY3G/rp2040-pio-emulator)
is a pure-Python PIO state-machine emulator that supports both RP2040 and
**RP2350**. Apache-2.0, mature (v0.87.0 March 2026). Provides pin-level
waveform observation — perfect for verifying WS2812 GRB timing without
hardware.

Held as a backup for the specific case where Wokwi falls through or where
waveform-level rigor matters more than visual rendering. Doesn't replace
Wokwi — no firmware-level emulation, no NeoPixel visualization, accepts only
raw assembled instructions rather than `@rp2.asm_pio` source. The
one-stop-shop value of Wokwi is what's pencilling it in over this option.

#### Concrete next moves

1. Verify the firmware runs unchanged on an RP2040 target (or in Wokwi
   pointed at Pico W). Probably yes; one config flip.
2. Stand up a Wokwi project mirroring the firmware structure.
3. Install `wokwi-cli` locally; try the MCP integration so Claude can drive
   sims headlessly from session.
4. Decide free-vs-paid tier based on how much of the codebase ends up
   visible in the Wokwi project.

#### Direct-hardware access (complementary, not replaced)

A path for Claude to push code to a connected Pico via `mpremote`, drive
the REPL, and read state back is still wanted as the **final verification
step** — perf testing, hardware-specific bugs, "does this actually work on
the deployed board." Wokwi is for fast iteration; real hardware is for
ground truth. Plan for both.

### Explore text / CAD-style hardware descriptions as a context-cheap photo alternative

Photos are good for "let me see what this looks like" but expensive in tokens
even after downsampling (~2k tokens per 1500-px image, multiplied across a
session). For repeated context — the same frame geometry, the same panel
layout referenced across many sessions — a **structured text description** is
much cheaper without losing the geometric information that matters.

Idea worth trying: rough orthographic "CAD-style" views of the frame and
panels as ASCII or compact SVG, with dimensions and labeled features. Check
them in alongside the photos and reference them from
`_familiarization/07-physical-installation.md` for geometry-focused
questions. Photos stay around for the visual cases (texture, color, finish,
"is this seated correctly?") that text can't carry.

Not urgent. Try once the photos and the physical-installation doc are
settled and see if the text descriptions can carry routine work.

---

## Alex / sim-team collaboration

### Professionalize the documentation tone for Alex hand-off (target: 2026-05-10)

**Bumped from Long-range to near-term.** Alex is ready to read these docs —
David has been in contact with him and committed to sending them, probably
tomorrow.

Important context update: **Alex has been using Claude since spring 2026.**
That raises his effective ceiling well above the "physics background, basic
programming" baseline currently in the audience legend. Update the
[familiarization README audience legend](_familiarization/README.md) and
anywhere else Alex's level is implied (doc 06 framing, etc.).

The cleanup pass:

- Replace "kids" with "students" (or specific team names: content team,
  scenario / actors team, second-chair team).
- Tone down parenthetical asides and inside-jokes; keep substance, cut
  working-conversation flavor.
- Audit for any references that wouldn't make sense to a reader who
  hasn't been part of the David ↔ Claude conversation history.
- Fold in the Alex-skill-update on first read.

Bar for "done": David would send any of these docs to Alex without a
follow-up apology email.

### Set up the "Claude space sim" starter repo for Alex's coding team

Alex has a coding-team idea brewing again, and David committed to spinning
up an empty starter repo Alex's team can clone to begin hacking on
Horizons.

Starter repo contents:

- A repo-level **`CLAUDE.md`** with working-style guidance reframed for the
  space-sim domain (Horizons hacking, not microcontroller firmware).
- Possibly **custom agents** if any of ours port well — e.g. a Horizons-API
  research agent, a scenario-design helper.
- Possibly **skills** — TBD; brainstorm what's actually useful for their
  workflow once we understand it better.
- A starter README orienting a new collaborator on what the repo is, what
  Horizons is, what they'd use Claude for.

Scope for Alex's team (per David):

- **Yes:** Horizons integration / extensibility work, possibly the animation
  editor (over time, as they ramp).
- **No:** the engineering-board microcontroller firmware. That stays with
  David and Claude.

Coordinate scope and timing with Alex once he has bandwidth to engage.

---

## Code cleanup

### Tidy up the C# host_comms project

The C# host-side client at `engineering-board/engineering-board/host_comms/` is current
and runnable, but carries leftover artifacts from the USB-era project it was copied
from during the TCP refactor. Five small fixes:

- Delete `engineering-board/engineering-board-usb-client-csharp/` — empty placeholder
  dir (`.vscode/` only), abandoned before the project landed in `host_comms/`.
- Rename `usb-protocol-client.csproj` / `.sln` / `RootNamespace` to something
  TCP-accurate (e.g. `host-comms-client` or `tcp-protocol-client`). The `usb-` prefix
  is now misleading.
- Replace `host_comms/README.md` — the current contents are FT232H setup notes from
  the USB era and don't apply anymore.
- Move `EngineeringBoardIP` and `DefaultTCPPort` out of the hardcoded constants in
  `CircuitPythonBoardManager.cs` and into config. There's already a `// TODO:` comment
  there flagging it.
- Make sure `host_comms/` is excluded from the firmware deploy
  (`deploy-micropython.ps1` and any `mpremote cp` patterns) so the C# tree never gets
  copied to a Pico.

### Merge `card_reader/` into `card_tray/`

Historical artifact: the firmware splits the Power Card Tray hardware
into two modules — `card_tray/` (LEDs, state) and `card_reader/`
(MCP3008 ADC scan). The split dates from an earlier RFID-based card-ID
attempt that didn't make it past the prototype phase (worked, but ID
misses were too frequent — speculatively from interference between 30
adjacent low-gain antennas). The current resistor-divider scheme
should logically live with the rest of the tray code.

Refactor:

- Merge `card_reader/` into `card_tray/`. The `CardReader` /
  `CardReaderManager` classes become tray-internal.
- Collapse `Systems.POWER_TRAY` and `Systems.CARD_READER` flags into a
  single per-device flag.
- Update `device_manager.py` `KNOWN_DEVICES` entries accordingly.

Not urgent. Do during the next pass through the card-handling code.

### Switchboard protocol redesign — **pre-MVP, critical path**

Current implementation works and is tested, but is crude — a polling
scan that brings each source high in turn and reads each sink to see
which goes high, then drops the source and tries the next. Linear in
sources × sinks per scan cycle, **and assumes a single Pico drives
both ends of the patch panel**.

The single-Pico assumption no longer holds. The
[multi-frame topology](ARCHITECTURE.md#frame-allocation) puts switchboard
sources on the left frame and bus-input sinks on the right frame, with
**no installed wiring between frames** (committed; only the patrons'
transient guitar cables cross the gap). The current scan can't span
that boundary — coordinating per-source-pulse timing across two Picos
over MQTT-via-Mac round-trips will not be low-enough latency.

Forward direction: sources **broadcast a distinguishing pattern**;
sinks read the pattern continuously and publish which source they're
seeing. Likely a custom serial-style protocol rather than I2C — the
cable runs are 6′ of 1/4″ audio cable per connection, electrically
closer to "long unshielded line" than "short PCB trace." A
NeoPixel-style self-clocking pulse train with **~10 ms pulse widths**
gives margin against noise and attenuation; a short framing pulse
delimits each pattern repeat.

Wins from the rewrite: scan-time independent of (sources × sinks);
real-time connection feedback rather than per-cycle latency; correct
behavior across the multi-Pico topology; better behavior under cable
noise.

**Bumped from "code cleanup, not urgent" to MVP-required.** Without
this, the multi-frame topology doesn't function. Schedule it before
the executive integration work starts so we don't build executive
behavior on a switchboard model that's about to change.

### Revisit power-card categories with the animation refactor

`power_cards/categories.py` currently maps cards into groupings (life
support, weapons, propulsion, sensors, …). The grouping was an early
classification attempt during animation authoring and **doesn't line
up with the Thorium system list** any more — categories haven't been
maintained as cards came and went. Most current animations are
monochrome; one or two were experimental multi-color cases.

When we revisit, the questions:

- Do per-card categories still serve a purpose now that the palette
  LUT is going away (see
  [§ Captured perf idea](#captured-perf-idea--drop-the-palette-store-full-rgb-ints))?
- If yes, what's the right grouping — should it match a Thorium-side
  taxonomy, or be a separate engineering-board concept?
- Does the grouping inform animation visual style (shared color
  palette per category, etc.) or is it purely metadata?

Pairs naturally with the
[animation designer overhaul](#animation-designer-overhaul) work.

---

## Security / hardening

### Restrict access to Picos and the executive to the intended interface only

The executive will run on a Mac in the engineering room. Each Pico will run an open
TCP server on the school's Wi-Fi. Patrons are 3rd–10th-grade students; Alex's actor
and content students are a similar demographic.

**Some of those kids will absolutely try to reach the Picos directly or poke at
the executive outside its intended surface** — David's prior, from his own
high-school self, is that a non-trivial subset of any age group enjoys exactly this
kind of mischief.

### Approach — `committed`

**Application-layer hardening only.** We use whatever Wi-Fi network the kit
finds itself on (almost certainly Alex's school-approved router in the control
closet) and design as if it's wide open — no SSID work, no VLANs, no router
configuration. The hardening lives entirely in the firmware and executive code.

### Surfaces

- **TCP listeners on each Pico — fixed-IP bind as the starting point.** Bind to
  the executive's IP rather than `0.0.0.0`. **No TLS** — overkill for the threat
  model and heavy on a Pico. Optional shared-secret handshake stays on the table
  as a second layer.

  The deploy story for the IP-bind needs real design effort: if the Mac is
  swapped or the network changes DHCP behavior, we don't want a future
  debugging session that starts with "the Picos stopped working and nobody
  remembers why." Possible shapes: self-discovery on first boot, config-by-mDNS
  hostname, a clearly-documented manual refresh path, or some combination.
- **The executive's management surfaces.** Whatever Mac-side process or web
  interface the executive exposes, assume it's reachable by anything on the
  same Wi-Fi. Don't bind admin endpoints to `0.0.0.0`; require auth on anything
  state-changing; log access.

Don't over-engineer; the threat model is "school kid with curiosity and a network
scanner," not nation-state. But the firmware as it stands is wide open and that's
not deploy-ready.

---

## Diagnostics

### Define the on-device error-signaling catalog

Per the [diagnostics commitment](ARCHITECTURE.md#diagnostics): each Pico
signals unrecoverable errors through its own display surface, BIOS-POST-beep
style. Work needed:

- **Catalog the error codes** we want to surface. Initial seeds:
  - "Cannot reach executive at the configured IP" — the Mac-swap / IP-bind
    failure that motivated this whole approach.
  - Likely early additions: `secrets.py` missing or malformed, peripheral
    init failure (NeoPixel chain, MCP3008, TM1637), unrecognized device ID
    in `KNOWN_DEVICES`, watchdog-triggered reset.
- **Pattern vocabulary per display surface.**
  - NeoPixel-driven controllers (card-tray, left-panel) — red-flash patterns.
    Possible shapes: number-of-blinks (3 fast / 5 slow / etc.), pixel-location
    (corner-only / full-strip / specific row), or hybrid. Pick a vocabulary
    that's easy to read at a glance from across the room.
  - Seven-segment controller — numeric codes (`E01`, `E02`, …) with a blinking
    attention-getter so it's clearly distinct from normal display content.
- **Code-comment requirement.** Every place in firmware that raises a pattern
  carries a comment with the pattern shape / number and a one-line English
  description, so future-us can grep the codebase by what they're seeing on
  the rig.
- **Implementation.** A small diagnostics module per Pico that owns the
  error-signaling loop. Must run independently of comms — this is the fallback
  when comms is broken.

Bar for "done": a future debugging session that opens with "the card-tray
Pico is flashing this pattern" can be resolved by greping the firmware for the
pattern code and reading the comment, without needing logs, a console, or the
executive running.

### Hidden USB pass-through for console + firmware updates (`committed`, MVP-required)

Once the rig is fully deployed, opening a panel frame is a **big lift** —
fasteners, the panel itself, delicate wiring inside. The visual diagnostics
above cover the read-only error-reporting case, but two things still require
a USB connection to each Pico:

- **Firmware updates** — bug fixes, feature additions, configuration tweaks.
  Without USB access, we have **no way to change anything on a deployed Pico**
  short of cracking the frame open. That's not viable.
- **Interactive debugging** via the serial REPL when an unanticipated failure
  needs more than a flashing pattern can convey.

Design problem: find a way to **invisibly expose a USB port for each Pico**
on the outside of the frame, so future maintenance never needs to crack the
frame open. Possible shapes:

- Bulkhead-mount USB connector on a patron-invisible edge of the frame (back,
  underside, behind a removable decorative cover).
- Short pigtail from the Pico inside to a USB-C panel-mount jack.
- Magnetic or latched cover so the port sits flush when not in use.

**Required for MVP.** Lock the design in *before* the frame goes in for final
installation — retrofitting a hole into a sealed metal frame is much worse
than designing one in.

---

## Animation designer overhaul

`engineering-board/power-card-animation-designer/` is a Python 3 + Tkinter desktop tool
David used to author the initial set of card animations several years ago. It hasn't
been touched since, and three separate problems block its forward use.

### Refactor the designer to track the firmware-side performance refactor

The designer predates the `array.array('I')` / packed-RGB / Viper pipeline that
`viper-animation-optimization.plan.md` is introducing on the firmware side, and the
larger PIO design that's in flight. Once those settle, the designer needs to emit
data in whatever final shape the firmware expects.

**Wait until the PIO + Viper firmware design is settled before touching this** — David
has additional performance-refactor ideas for the designer-to-firmware pipeline that
he wants to discuss when we get there.

#### Captured perf idea — drop the palette, store full RGB ints

When we revisit perf after the PIO design lands, the relevant facts are:

- The WS2812 PIO program consumes **4 bytes per pixel** from the TX FIFO (32-bit
  autopull with `pull_thresh=24`) but only uses 24 of them (G, R, B) — the high
  byte of every 32-bit word is discarded by the next autopull.
- The existing palette-LUT-plus-byte-indices format was a **RAM-pressure
  workaround** from when we were bit-banging on memory-constrained boards. One
  byte per pixel + a 256-entry lookup got the stored animations small enough to
  fit. The Pico has plenty of SRAM; we no longer have that constraint.

Forward direction: **drop the 256-entry palette indirection and store animation
frame data as raw 32-bit ints throughout** (one full RGB value per pixel, with
the high byte of each word as padding to match the PIO consumption shape).
This pulls double duty:

- **Performance.** Viper should generate tighter code with guaranteed 4-byte
  alignment — `ptr32` reads and writes without extra masking, no LUT
  indirection, no expansion step in `PixelBuffer()`.
- **Tooling alignment.** The designer no longer has to maintain a palette
  abstraction the firmware doesn't use. Output format and on-board format are
  the same. Should make any third-party-tool integration in the next bullet
  much simpler.

#### Designer-side consequence — single shared swatch palette (`committed`)

The palette LUT did one thing well that we want to preserve: it enforced a
limited shared palette across all of a card's animations, which kept things
visually coherent. **Removing the LUT means the designer needs to take that
job over.**

Decision: **one hard-coded swatch palette shared across all cards**, with
**no free-form or custom-color picker in the editor**. Authoring colors stay
in-palette by construction. **The swatch is the existing 256-entry palette
LUT** — that's already the de-facto color set every current animation works
in, so adopting it directly means no migration of color data and no new
color-curation work. If Alex or the content team want more flexibility,
they can ask.

This shapes the tool we pick — or build — in the next bullet: it has to
either support a fixed-indexed-palette mode natively (Aseprite, Piskel) or
expose enough configuration that we can lock the palette down on our side.

### Make the designer actually a designer (CRUD)

Despite the name, the current tool is mostly a **viewer**: it renders a card's frames
and supports right-click → change one pixel at a time. There is no real way to author
or edit an animation. The intended users — kids on the content team at the school —
cannot realistically be productive with this surface.

Minimum useful scope: create / edit / delete frames in a card; reorder frames;
add / remove cards; manage the palette; save changes back to
`power_cards/frames/*.py`. Probably also: timeline scrubber with playback and FPS
control, fill/copy/paste over grid regions, brush draw (not just one-pixel-per-click
on right-click), and undo/redo.

Bar for "done": a content kid can be productive in 15 minutes with no programmer
hand-holding.

### Research free/cheap existing pixel-animation tools first

Before committing to a CRUD-rewrite of our own designer, check whether an existing tool
can do most of the job — leaving us only on the hook for an exporter to our
`power_cards/frames/*.py` format.

Candidates worth a serious look:

- **Aseprite** (paid but cheap; **LibreSprite** is the free fork) — the standard
  pixel-art tool with frame timeline and palette management. 8×8 work is fine. Key
  question: can it (or a script plugin) emit per-frame palette-indexed bytes matching
  our wire format?
- **Piskel** — free, browser-based, frame-based pixel editor. Good for quick CRUD;
  weaker on palette management.
- **PixelBlaze**, **Glediator**, **Jinx!** — LED-pixel-mapping animation tools. More
  effect-driven than frame-by-frame; likely the wrong abstraction for card frames but
  worth a look in case the model fits a subset of cards.
- **WLED** — has a 2D effect engine and a mature ecosystem. Way more than we need, but
  its file format / effect library might be a useful reference.

Budget for a paid tool that saves real time: **up to ~$100 is fine**. Aseprite
specifically is well under that and is the strongest candidate on the list.

Outcome decides whether the previous TODO (full CRUD rewrite) stays in scope or
shrinks to "write a one-way exporter from `<tool>` to `power_cards/frames/*.py`."
Note that whichever path we take, the tool will need a way to enforce color
consistency across animations now that the palette LUT is going away — see the
design-consequence note above.

---

## Hardware verification

### Confirm Wi-Fi works inside the panel frame

**Bumped to early priority** — the frames are at David's home now, and a
representative test can run in the basement (one intervening wall, can put the
access point ~60 ft away). No need to wait for the on-site deploy environment.

Reminder on the production-room layout that this test eventually has to
work in: the engineering room is roughly 5×5′ usable (8–9 ft east-west).
**Warp core sits on the west wall** above the control station; the
**boards are pencilled in to the north-east corner** (final placement
TBD with Alex). With that geometry, the panel faces are oriented
neither directly toward the control-closet router (down the hall) nor
toward the warp core — the repeater likely wants to live on the
south-west or south wall, not on the warp core. Cameras already in the
room give cover for hiding additional small gear. Final placement
follows the board placement.

Each panel mounts to a thick sheet-metal frame shaped like a 3D trapezoid
(frustum-like) ~4″ deep front-to-back, with a large opening on the front face for
the panel itself. All electronics — Picos, NeoPixel chains, MCP3008s, TM1637s —
live inside the frame. Sheet metal is an enclosure; 2.4 GHz Wi-Fi inside an
enclosed metal box risks Faraday-cage attenuation, multipath issues, and dropped
packets.

Worse, the production environment likely has the access point in a different
room across the space-sim suite — Alex's school-approved router lives in the
control closet, probably 30–40 ft away with multiple walls between it and the
engineering room. That's a long reach for the Pico 2 W's onboard chip antenna
even before the frame's contribution. The basement test stresses the
distance dimension at home; the frame's own attenuation is the part we can
actually verify locally.

What to measure: RSSI, packet loss, and TCP-reconnect frequency at 60 ft
through one wall, with the Pico inside a representative frame. Compare against
the same Pico outside the frame at the same distance to isolate the frame
contribution. Repeat at shorter distances for a sanity baseline.

If signal is unusable, remediation options in rough preference order:

- **Wi-Fi repeater in the engineering room.** Most attractive option — a single
  added box can solve the suite-distance / through-walls problem cleanly with
  no per-Pico hardware work. There's a candidate mount point on the warp core
  itself, directly in front of the boards and near the ceiling, with good line
  of sight to the Picos inside the frames. Worth trying first if the test
  shows the problem is "too far from the AP" rather than "the frame is opaque
  to RF" — those are different failure modes and want different fixes.
- **External antenna via a U.FL pigtail.** **Ruled out.** Confirmed against the
  [RM2 datasheet](../docs/rm2-datasheet.pdf): the RM2 wireless module that
  every Pi-RM2-based Pico 2 W uses has a fixed inverted-F PCB antenna and
  **no RF pin on any of its 21 pads**. The Pimoroni Pico Plus 2 W carrier
  doesn't add a U.FL pad either. The only physical path to an external
  antenna is lifting the antenna trace on the RM2 module and soldering coax
  directly — fine-pitch surgery on a $20 part with high risk of damaging
  the module or its impedance matching. The "switch to a different
  RP2350 board with U.FL" workaround is also out: boards like the
  [iLabs Challenger+ RP2350 WiFi6/BLE5](https://ilabs.se/product/challenger-rp2350-wifi6-ble5-ipex3/)
  exist (RP2350 + ESP32-C6 + IPEX3 connector) but switching mid-project
  would require rewriting the network stack against a different wireless
  chip — not worth it to dodge a problem the in-room repeater solves
  cleanly. **External antenna is off the table.**
- **Wi-Fi access-point cabled into the frame** (defeats the purpose of going
  wireless, but technically works).

(USB-host as a deployment fallback is **off the table** — Wi-Fi/MQTT is the
committed direction and adding installed inter-frame cables for comms
contradicts the no-installed-cables-between-frames preference. The hidden
USB pass-through per Pico is still in scope but only for **debugging and
firmware updates**; see
[§ Hidden USB pass-through](#hidden-usb-pass-through-for-console--firmware-updates-committed-mvp-required).)

**Downstream of this test:** once the signal-attenuation picture is clear,
revisit broker placement — the control-booth PCs become a serious option for
hosting the MQTT broker (and possibly the executive) only if signal in the
engineering room is solid enough to reach across the suite. See
[ARCHITECTURE.md § Broker placement](ARCHITECTURE.md#broker-placement).

---

## Project completion

### Finish the Thorium integration (deferred — last item)

The MVP requires integration with the school's bridge simulator. The current target
of record is **Thorium**, but the integration story has rotted:

- Some integration code exists (`dotnet/engine_sim_blazor/`'s GraphQL client; the
  firmware's TCP protocol surface). **None of it has been tested end-to-end.**
- The integration code is at least 2–3 years old and predates most of the current
  card-tray / power-grid / switchboard / power-display subsystems on the firmware side.
- Thorium is painful to bring up locally. The only working instance lives at the
  school. David is rarely on-site, so iteration is slow.

**Stay last in the project ordering.** Get the rest of the board functioning first;
do sim integration when the hardware side is otherwise complete.

### Watch for Alex's move from Thorium to Horizons Starship Simulator

Alex DeBirk (STEM / space-sim teacher at the school) has been trying to migrate from
Thorium to **Horizons Starship Simulator** for a year or two. Horizons reportedly has
a much friendlier integration interface (MQTT — to confirm). Alex is chronically
under-resourced and hasn't completed the migration.

Given the slow pace of this project, there's a realistic chance Horizons will be the
production target by the time we're ready to integrate. Don't pre-build for it; just
keep the architecture loose enough that swapping Thorium↔Horizons is "rewrite the
adapter," not "redesign the firmware."

Resolve at deploy time. If Horizons has won by then, MQTT-on-Pico is straightforward
(plenty of MicroPython libraries) and the integration we don't write for Thorium is
the integration we write for Horizons.

### Integrate the warp-core prop with the executive

The bridge has a pre-existing **warp-core prop** — ~1000–1500 NeoPixels driven by
what's probably a **Raspberry Pi 3** — that the executive will need to coordinate
alongside the engineering-board controller fleet. The warp core and the engineering
board are co-resident on the bridge and will share scenarios.

Existing controller code is buried in this repo's attic, primarily:

- `attic/pi-engine-room/WarpCoreController/`
- `attic/pi-engine-room/Server/`, `Client/`, `Shared/`
- Possibly `attic/pi-engine-room/rpi_kens/` (suggests a per-prop variant)

This work is 2–3 years old and probably out of date relative to the current bridge
configuration. Work needed when we get there:

- Audit the attic warp-core projects, recover the protocol shape and current
  hardware behavior, identify what's still useful vs. fully obsolete.
- Decide the forward direction — keep the Pi-side firmware as-is (with the
  executive driving it via the existing protocol), reflash with new firmware that
  matches the Pico-side protocol, or retire the Pi entirely and roll its
  responsibilities into the new executive surface.
- Integrate warp-core control into the executive design alongside the
  engineering-board controllers.

---

## Long-range — not anytime soon

Items recorded so they don't fall out of memory, but explicitly **not scheduled** and
not load-bearing for the current direction. Visit when there's a forcing function or
spare cycles, not before.

### `solar-system-generator/` — split out, and possibly polish

The Blazor + three.js + MudBlazor app was originally built so the school's content-team
kids could produce "realistic" reference shots of various solar systems. It probably
belongs in its own repo rather than living alongside the engineering-board firmware,
but **don't move it yet** — wait until something else creates pressure to act.

Open question: is it still in active use by the kids? Worth asking Alex when we next
talk to him. The answer determines whether the next step is "extract to its own repo
and polish it" or "extract to its own repo and archive it."

If we end up polishing it: David's note from when he wrote the original — getting the
orbital mechanics correct was hard, and most of the math ended up faked. Visually it
still looks good, but if real students are using it as a teaching aid the physics
deserves a proper review (Kepler's third law, eccentricity, inclination, all the fudge
factors that crept in). Code to look at: `SSG.Client/Pages/SystemDisplay.razor*` and
the TypeScript renderer / orbital code under
`SSG.Client/wwwroot/js/` (`ssg.renderer.ts`, `celestial-object.ts`, `ssg.utils.ts`).
David would specifically like a Claude pass over this when the time comes.

### Re-route the left-board wiring on its back side

The back of the Left Engineering Board is a hand-built rat's nest from the
prior incarnation — see `docs/images/left-board-back.jpeg`. Many wires
routed freehand, masking-tape labels everywhere, no orthogonal discipline.

A year or so back David had to demo the board and a couple of wires had
pulled free; tracing them back through the chaos took non-trivial time. The
maintenance burden grows every visit.

Cleanup wanted, **low priority and low urgency** — but worth doing before
the next time we need to debug the board, not during:

- Re-route wires in an orthogonal layout (horizontal/vertical runs only,
  right-angle turns).
- Tape or otherwise secure each run to the back of the board so wires don't
  migrate or pull free.
- Re-label legibly — printed labels or a proper legend, not the
  masking-tape tags that are there now.

Goal: future-Dave can chase a pulled wire in five minutes, not forty-five.

### Make tray magnet wells look white

The four neodymium magnets in each Power Card Tray sit in printed wells
covered by a thin layer (0.25–0.5 mm) of white 3D-printer filament. The
covering exists; cosmetics are the issue — the wells are visually
distinguishable from the rest of the white tray face and break the
clean look. Cards aren't affected (their magnets are intentionally
exposed for contact).

Find a way to make the tray-side wells visually disappear into the
surrounding white — thicker filament cap, post-processing paint, a
different material, etc. Aesthetic-only; doesn't affect function.

### Audio / DMX integration with the bridge

The bridge has a full DMX lighting rig and a sound system, today run by Alex and the
second-chair student. There's a possible future where the engineering board
participates — e.g. a wing-damage event triggers a "red alert" sound cue and a
lighting effect, not just a card-animation change.

**Aspirational. Way behind everything else** — recorded so the idea isn't lost. By
the time we revisit, we'll have a much better sense of what the executive ↔ board
loop already does and where DMX/audio actually belongs in the stack (board-driven,
executive-driven, or stays entirely Alex's responsibility).
