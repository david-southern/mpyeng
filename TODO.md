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

**Priority: Task #1, before any new firmware design work begins.** The PIO design
session is gated on this.

The current iteration loop is: Claude proposes a change → David flashes it to a Pico
→ watches the result → reports back. That cycle is slow enough that it heavily
constrains how many design iterations we can run per session. Investing in tooling
that lets Claude exercise the firmware directly should pay back many times over.

Two acceptable shapes for the goal:

- **MicroPython emulator on David's PC**, ideally with enough hardware fidelity to
  run the firmware unmodified (or with minimal hooks). Candidates worth a serious
  look:
  - The MicroPython **`unix-port`** REPL (real MP, no hardware modules — fine for
    pure-Python code paths, useless for `machine` / `rp2` / `neopixel`).
  - **Wokwi** — browser-based MicroPython sim with simulated peripherals; reportedly
    has Pico support and NeoPixel rendering.
  - A **custom shim layer** that stubs `machine`, `rp2`, `neopixel` against a
    headless renderer or a logging mock. Lower fidelity but tight integration with
    Claude's tooling.
- **Direct hardware access** — a path for Claude to push code to a connected Pico
  via `mpremote`, drive the REPL, and read state back. Probably the highest-fidelity
  answer but depends on whether Claude's Bash sandbox can hold a serial handle
  reliably. Worth testing.

Either path is a win; both is best (emulator for fast iteration, real hardware for
final verification).

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

Surfaces to think about when we get to this:

- **TCP listeners on each Pico** — bind only to the executive's IP rather than
  `0.0.0.0`? Add a shared-secret handshake on connect? Move to TLS / mutual auth
  (heavy on a Pico, but possible)?
  - DavidS note: No TLS, it's not that bad. The single-IP bind sounds good, but lets talk about the
    configuration/deploy path there. I don't want to have to remember why the Picos broke if someone
    else swaps out the Mac or changes network config in the future.
- **Wi-Fi network** — separate SSID for the engineering-board kit, isolated from
  the patron-accessible school network? VLAN / firewall rules?
  - DavidS note: I'm almost positive Alex has his own (school approved) WiFi router in the control
    closet. Access to the school network won't happen, they are very protective. I've asked for VPN
    access before, and was shut down immediately. Having said that, not sure we could get another
    router approved, so unless we can run multiple SSIDs off the same router, we'll probably have
    take that off the table.
- **The executive itself** — what management surfaces does it expose, and are any
  of them reachable from the school LAN?
  - DavidS note: We will definitely put it on the isolated router. But I have no idea of that setup.
    I **think** Alex had the school's IT guy set it up, but it's very possible he just plugged it in
    himself. I don't know if it has any security in either case. The school guy is always
    overloaded, even if he configured it, he might not have considered it a threat if it is isolated
    from the school network. Almost sure that it is broadcasting it's SSID, but again, not
    confirmed. Regardless of all this, I don't want to open a network discussion with Alex. Next
    time I am onsite, I'll ask if I can take a look at the router config (assuming I even remember),
    but for now let's assume that it's an isolated network that we can't modify and design
    accordingly.

Don't over-engineer; the threat model is "school kid with curiosity and a network
scanner," not nation-state. But the firmware as it stands is wide open and that's
not deploy-ready.

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

#### Captured perf idea — 4-byte-aligned ints throughout

When we revisit perf after the PIO design lands, the relevant fact is that the WS2812
PIO program consumes **4 bytes per pixel** from the TX FIFO (32-bit autopull with
`pull_thresh=24`) but only uses 24 of them (G, R, B) — the high byte of every 32-bit
word is discarded by the next autopull. The current Viper optimization plan was written
when the firmware was bit-banging and a 3-byte-per-pixel storage shape was the natural
match. The Pico has plenty of SRAM, so we're no longer memory-constrained.

Hypothesis worth testing once the PIO design settles: store and manipulate frame data
as **proper 32-bit ints throughout** — accepting one byte of padding per pixel — and
expect that to outperform shuffling 3-byte sequences. Viper in particular should
generate tighter code if 4-byte alignment is guaranteed at every step (`ptr32` reads
and writes without extra masking). The output of the designer needs to agree with
whatever shape the firmware lands on, which is why this idea anchors here rather than
purely in `viper-animation-optimization.plan.md`.

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

DavidS note: I'm fine paying up to $100 for a tool that saves us time. Also, regarding the palette
question, once the PIO stuff lands, I'd like to remove the pallete stuff. That's when we thought we
were RAM constrained, and we were trying the get the stored animations down to one byte per pixel.
Thus the 256 element palette. Now that we don't have memory problems, let's store the raw frame data
in the same full-int format we'll be using. Should make the animation tool integration easier as
well? Also note: the palette LUT scheme did serve to make sure that all colors in an animation were
consistent, which was nice for the designer. If we remove the palette, we'll want to make sure the
designer still has some way to manage color consistency across the all animations (and probably the
rest of the lighting??).

Outcome decides whether the previous TODO (full CRUD rewrite) stays in scope or shrinks
to "write a one-way exporter from `<tool>` to `power_cards/frames/*.py`."

---

## Hardware verification

### Confirm Wi-Fi works inside the panel frame

Each panel mounts to a thick sheet-metal frame shaped like a 3D trapezoid (frustum-like)
~4″ deep front-to-back, with a large opening on the front face for the panel itself.
All electronics — Picos, NeoPixel chains, MCP3008s, TM1637s — live inside the frame.

Sheet metal is an enclosure. 2.4 GHz Wi-Fi inside an enclosed metal box is asking for
trouble: potential Faraday-cage attenuation, multipath issues, and dropped packets to
the Pico 3 controller (which carries the external comms responsibility).

- DavidS note: Worth mentioning that if I am correct about the WiFi router situation, the access
  point is in a room on the other side of the space sim suite, probably around 30-40 feet away with
  multiple walls in between. Need to keep that in mind as well. I wouldn't be surprised if that was
  a long reach for the pico antenna. Do they have "antenna extenders" that might help, esp getting
  outside of the frame? Would have to be invidible to the patrons, but I could come up with some
  "piping" decoration around the frame?

This needs to be verified before we commit final hardware to the Wi-Fi/TCP comms path.
A cheap test: temporarily mount a Pico 2 W inside a representative frame, connect it
to the test access point, log RSSI and packet loss across normal room distances and
through-wall scenarios.

- DavidS: I've got the frames with me. Only one wall in the basement, but I could put it 60 feet away. Let's
  prioritize a test earlier rather than later.
- DavidS: This is completely in the wrong section, but I just thought about it. I've stared initial
  work on the prop build itself. Would pictures of the frames, the WIP left and right panels, etc.
  be helpful to you? Don't need it for documentation, anyone who reads this will have the hardware
  on hand, and I don't want to waste your context if it's not useful.

Fallbacks if signal is unusable:

- External antenna lead poked through a small hole in the frame (Pico 2 W has a U.FL
  pad — confirm).
- Wi-Fi access-point cabled into the frame (defeats the purpose of going wireless).
- Walk back the USB→Wi-Fi refactor and stay on USB-host comms.

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

### Audio / DMX integration with the bridge

The bridge has a full DMX lighting rig and a sound system, today run by Alex and the
second-chair student. There's a possible future where the engineering board
participates — e.g. a wing-damage event triggers a "red alert" sound cue and a
lighting effect, not just a card-animation change.

**Aspirational. Way behind everything else** — recorded so the idea isn't lost. By
the time we revisit, we'll have a much better sense of what the executive ↔ board
loop already does and where DMX/audio actually belongs in the stack (board-driven,
executive-driven, or stays entirely Alex's responsibility).
