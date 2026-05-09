# 08 — Subsystems and Interaction

What lives on the engineering board, what each subsystem represents in the
fiction, how kids physically interact with it, and the early thinking on
puzzle design.

Counterpart to the in-progress physical-installation notes captured in
[`docs/images/README.md`](../docs/images/README.md): the image notes cover
shape and placement; this doc covers function and behavior.

## How to read this doc

Each subsystem section answers, in roughly this order:

- **What it is** physically — the hardware on the board.
- **What it represents** in-game — the simulated thing.
- **State** the firmware tracks for it.
- **Kid interaction** — how a player physically affects or reads it.
- **Firmware module(s)** — pointer into `engineering-board/engineering-board/`.

Scenario / puzzle thinking is **early and speculative** and lives at the
bottom of the doc, separate from the subsystem catalog.

---

## Subsystem catalog

### Wings (Left Wing, Right Wing)

The two large 16×16 NeoPixel grids on the left side of the **left board**,
with a seven-segment display sitting between them showing the current power
each wing is delivering.

In the fiction, each wing is a **power source**. Total available power per
wing is normally constant — current puzzle thinking puts it in the 500–5000
range — until combat damage or an emergency drops or zeroes it.

Tracked state: max power, target power, current power, damage flag.

Kid interaction is indirect via the **switchboard sources** to the wings'
right (next subsystem). Wings have no direct controls; their state is
driven from the executive (which is what runs the simulation).

Firmware: `power_grid/` (the 16×16 NeoPixel animation), `power_display/`
(the wing seven-segs). Named resources `LEFT_WING` / `RIGHT_WING` in
`utils/protocol_resources.py`. Data class: `EnginePower` (the firmware
internally calls these "engines" alongside their wing identity).

### Switchboard

The patch-panel system spanning both boards. Bright red electric-guitar
cables connect 1/4″ audio jacks. Pulling and re-routing cables changes
the power topology in real time. The switchboard is **one of two tools**
kids use to respond to changing power conditions; the other is moving
**power cards** between trays (described below). Of the two, **moving
cards is the more frequent action** — fewer pieces, simpler change, used
constantly. The switchboard is reached for less often, mostly when
damage forces a higher-level reroute.

The switchboard endpoints physically live on multiple subsystems (wings
expose sources; transformers expose sinks AND sources; power busses
expose sinks). The Switchboard *system* is the connectivity graph these
endpoints participate in.

Connectivity rules from current design:

- A wing can be connected to **0–4 transformers**.
- A transformer can be connected to **0–1 wings**.
- A transformer can drive **0–2 power busses** via its source jacks
  feeding bus sinks on the right board.
- A power bus has a single sink jack — one source connection at a time.

Typical scenario shape: a switchboard reroute almost always triggers
power-card moves too, because a re-routed transformer now serves
different busses with different consumption profiles. "Reroute the cable"
and "move the cards" are usually beats in the same scenario, not
alternatives.

Kid interaction: physically trace and re-route cables when the situation
demands it.

Firmware: `switchboard/` (`SwitchboardEndpoint`, `SwitchboardSource`,
`SwitchboardSink`). Per-device flags `LEFT_SWITCHBOARD` /
`RIGHT_SWITCHBOARD` in `utils/device_manager.py`. The current
implementation is a working but crude polling scan — see
[TODO § Switchboard protocol redesign](../TODO.md#switchboard-protocol-redesign)
for the future direction.

### Transformers (4×)

The four transformer modules on the right side of the **left board**.
Each transformer carries (board-inside outward):

- Four **switchboard sinks** (1/4″ audio jacks) — connections from a wing.
- A red seven-segment display showing the transformer's max output capacity
  (summed across its connected busses).
- An 8×8 NeoPixel grid showing animated power output.
- Two **switchboard sources** — drive Power Busses on the right board.

In the fiction, a transformer routes power from a wing to up to two power
busses, acting as a capacity-limited intermediary.

Kid interaction is cable routing on the source/sink jacks. No other direct
controls.

Firmware: `power_grid/` (the 8×8 animation), `power_display/` (the
seven-seg), `switchboard/` (the jacks). Named resources `TRANS1`–`TRANS4`
in `utils/protocol_resources.py`. Data class:
`TransformerPower(Name, MaxPower, PowerUsage)`.

### Power Busses (6×)

Six power busses on the **right board**, one per row. Each bus has, on
the far-left "control cluster" (top-to-bottom):

- A red seven-segment showing **power available** to the bus.
- The bus's switchboard sink — the cable input from a transformer.
- A yellow seven-segment showing **power consumed** by the bus's trays.

The remainder of the bus row is the five Power Card Trays (next subsystem).

In the fiction, a bus is a power-delivery rail to a set of ship systems.
Power flows in from a transformer; the trays' loaded cards consume it
**in parallel** — the bus is modeled as a parallel circuit, with each
loaded card drawing current proportional to its system's demand. The
bus's "power consumed" display is the sum across loaded trays.

Up the chain, transformers and wings allocate to their connected sinks
on the same parallel-distribution model. The fiction is intentionally
faithful to real electrical-distribution behavior — the engineering
board is a STEM teaching surface as well as a game piece, so when we
expand the fiction we keep parallel-circuit semantics consistent.

Kid interaction is two-fold: cable routing at the sink jack, and slotting
power cards into the trays. Both decisions affect whether the bus is over-
or under-supplied.

Firmware: `power_display/` (seven-segs), `switchboard/` (sink jack). The
bus itself is more a logical unit than a self-contained module — its
power balance is computed from connected sources and the trays' draws.
Data class: `SystemPower(Name, Power, CardCount)` in
`utils/protocol_resources.py`.

### Power Card Trays (5 per bus, 30 total)

The five trays per bus row on the right board. Each tray is:

- A 5-pixel **status bar** along the top.
- An 8×8 **animation grid** in the middle (the slotted card's animation).
- A 5-pixel **status bar** along the bottom.
- Underneath: two **pogo-pin contact points** that read the slotted
  card's identifying resistor (one ADC channel per tray, see "card
  identification" below).

Tray status states (firmware: `PowerStateEnum`, `CARD_TRAY_COLORS`):
empty, in use (powered), in use (brownout), damaged — likely more.

The 30 trays are **functionally indistinguishable** beyond which bus
they belong to. Any card can go in any tray, and cards are routinely
moved tray-to-tray and bus-to-bus during play.

#### Card attachment — magnetic, polarity-keyed

The front of each tray is flat. Power cards stick to it via **four
neodymium magnets** in the corners of the card frame, aligning with
matching magnets in the tray. **One of the four magnets is reversed**
on each side so cards can only be attached the right way up — the
mismatched polarity will repel an upside-down card.

> Terminology: David and Alex still say "slot a card in" / "pull it
> out" — the slot-style language is vestigial from earlier card
> designs. The actual mechanism today is magnetic, but "slotting" is
> the verb in conversational use.

#### Card identification

The pogo pins under each tray connect to one channel of an MCP3008 SPI
ADC. A pull-up resistor on the firmware side and the card's frame
resistor form a voltage divider; the ADC reading identifies which card
is seated. Not directly kid-facing — kids just see the tray respond
when they slot a card.

Firmware today has the tray hardware split into two modules:
`card_tray/` (`PowerCardTray`, `PowerTrayManager`) for the LEDs and
state, and `card_reader/` (`CardReader`, `CardReaderManager`) plus
`drivers/mcp3008.py` for the ADC scan. The split is historical — the
"Card Reader" name dates from an earlier RFID-based identification
attempt — and these should be merged into a unified Power Card Tray
module. Tracked in
[TODO § Merge card_reader/ into card_tray/](../TODO.md#merge-card_reader-into-card_tray).
Per-device flags `POWER_TRAY` and `CARD_READER` in
`utils/device_manager.py` will collapse to a single flag at the same
time.

### Power Cards

The physical playing pieces. Each card is a clear acrylic rectangle
with a 3D-printed frame around the edge. The frame holds the four
attachment magnets (see Card Trays above for the polarity-keying
detail) and two pogo-pin contacts backed by a card-specific resistor
that identifies the card via voltage divider.

In the fiction, **each power card represents a Thorium ship system**
that the engineering crew can choose to power. Slotting a card into a
tray assigns that system to the bus the tray is on; pulling the card
disconnects the system.

Card catalog: there are **25 canonical Thorium systems**, each with a
named card definition in `power_cards/card_ids.py` and animation
frames in `power_cards/frames/*.py` (one file per card — laser
cannon, warp field, aft shields, fusion engines, navigation, life
support, etc.). Depending on puzzle complexity, **a single Thorium
system may have 1–5 physical card copies** that all share the same
identifying resistor — the cards are indistinguishable to the firmware
but give the kids more flexibility in physical card placement.

A separate per-card *category* concept exists in
`power_cards/categories.py` but it's currently broken — the categories
were an early classification attempt during animation authoring and
haven't been kept in sync with the Thorium system list. Most current
animations are monochrome, with a couple of multi-color test cases.
The category question gets revisited when we refactor the animation
pipeline; tracked in
[TODO § Revisit power-card categories](../TODO.md#revisit-power-card-categories-with-the-animation-refactor).

Kid interaction is physical: pick a card from the available pool,
slot it onto a chosen tray. The tray's 8×8 animation is the per-card
visual that the **content team** is responsible for authoring (see
[06-school-context.md](06-school-context.md)) once the
[animation designer is rebuilt](../TODO.md#animation-designer-overhaul).

Firmware: `power_cards/` (catalog, animation frames, ID-to-resistor
mapping).

### Pico ↔ Executive comms

Each Pico runs an MQTT client (current target) over Wi-Fi to the executive
on the engineering-room Mac. The executive owns scenario logic and
simulator integration; the Picos handle hardware. Architecture detail in
[ARCHITECTURE.md § Comms](../ARCHITECTURE.md#comms) and
[§ Executive layer](../ARCHITECTURE.md#executive-layer).

Not patron-visible.

Firmware: `comms/` (`ProtocolManager`).

### Diagnostics

When something goes wrong (Pico can't reach the executive, peripheral init
fails, a watchdog fires), each Pico signals errors visually through
whatever display it owns — red NeoPixel patterns on the card-tray and
left-panel controllers, numeric error codes on the switchboard/display
controller's seven-segs. Architecture detail in
[ARCHITECTURE.md § Diagnostics](../ARCHITECTURE.md#diagnostics).

Patron-visible only if something has already gone wrong, at which point
the mission is probably already paused.

Firmware: TBD — see
[TODO § Diagnostics](../TODO.md#diagnostics).

---

## Puzzle and scenario thinking (speculative)

Nothing in this section is committed. Puzzle design hasn't started.
Captured here so the constraints we've already noted in passing don't get
lost, and so future puzzle work has a starting point.

### Difficulty tiers

Patrons span 3rd to 10th grade, and the same scenario may be run for
either end of that range. Puzzles need scalable difficulty.

Examples seeded so far:

- **Bus over-consumption.** 3rd-grade tier: trays show blinking-red
  status bars; no in-game consequence (a warning). 10th-grade tier: bus
  actually overloads — ship damage, scenario-failure consequence, etc.
- **Wing power.** Likely 0 (damaged) or in the 500–5000 operational
  range. Combat damage / emergencies are the trigger for changes.

The DSL question (how puzzles are authored, by whom) lives in
[ARCHITECTURE.md § Executive layer](../ARCHITECTURE.md#executive-layer).
Authoring tiers and difficulty tiers are distinct concerns — *who creates*
vs. *who consumes*.

### Communication constraint

The engineering room and the bridge are **physically separate, with no
intercom between them** (see
[06-school-context.md § The space](06-school-context.md#the-space)). Bridge
crew yells through the wall or sends a runner. Implication for puzzle
design: scenarios **cannot depend on precise verbal coordination between
bridge and engineering**. Anything where the captain says X and the
engineer must do Y at a specific moment is broken by the latency of
"yell, hope it's heard, hope it's understood." Mediating through the
executive (which both ends can read) or designing puzzles that tolerate
re-asking is the way forward.

### Damage model

**Anything in the system can be damaged** — wings, transformers, power
busses, individual trays, individual power cards. A damaged power card
is dead in any tray it's slotted into; that's how the firmware
identifies "card X is broken" rather than "this tray slot is broken."

Damage isn't a single state. The current thinking allows a range:

- **Unusable** — the thing produces zero output / consumes zero / is
  fully offline.
- **Reduced capacity** — partial output (e.g. a transformer's max-power
  drops to a fraction; a card's system runs degraded).
- **Other states yet to be designed** — flicker, intermittent, requires
  reset, etc.

Damage events are the most common reason scenarios force kids to act —
a damaged wing reduces upstream supply, a damaged transformer narrows
the routing options, a damaged card forces a re-prioritization of which
ship systems get powered.

### Likely scenario primitives

Surfaces the subsystems support, not specific designs:

- **Combat damage to a wing** → upstream supply drops/zeroes → kids
  reroute remaining wing capacity via the switchboard, then reshuffle
  cards across busses to fit reduced supply.
- **Damaged transformer** → its sinks become unreachable from the
  damaged wing → a switchboard reroute moves the affected busses to
  the other wing, with card moves to balance the new load.
- **Power-bus overload** via bad routing or excessive consumption →
  cascading effects per difficulty tier.
- **Forced card pulls during emergency** (specific cards become
  unavailable) → kids re-prioritize which ship systems stay powered.
  This is the "Life Support vs. Shields" decision moment.
- **Specific card combinations** enable specific ship capabilities (no
  fixed list yet; depends on card-catalog design).

A typical scenario beat probably combines **at least two** of these —
e.g. damage forces a switchboard reroute, the reroute changes capacity,
the capacity change forces card moves. Scenarios where the kids only
move cards (no switchboard work) are likely common; scenarios where
they only move cables are likely rare.

---

## Coverage check against firmware

Verified 2026-05-09. The subsystems above match what's in
`engineering-board/engineering-board/`. Nothing in the firmware is missing
from this catalog as a player-facing concept.

What is in the firmware but is *infrastructure* rather than a subsystem
(intentionally not in this doc): `utils/pixel_strip_manager`,
`utils/demo_data_manager`, `utils/profiling`, `utils/eng_utils`,
`utils/device_manager`, the `drivers/` tree.

## Open items to fill in here

Things worth cataloguing properly when we get to them, but not yet
written up:

- **The full Thorium-system list** — the 25 canonical systems mapped to
  card definitions in `power_cards/card_ids.py`. Worth enumerating in
  this doc once we've reconciled them against the current Thorium
  build. (The **categories** question is parked for the animation
  refactor — see
  [TODO § Revisit power-card categories](../TODO.md#revisit-power-card-categories-with-the-animation-refactor).)
- **Per-system card-count plan** — how many physical card copies each
  Thorium system gets (1–5), driven by puzzle design. No allocation
  decided yet.
- **The warp-core prop** — adjacent to the engineering room,
  integrating with the executive — tracked in
  [ARCHITECTURE.md pending](../ARCHITECTURE.md#pending--to-be-discussed)
  and [TODO § Warp core](../TODO.md#integrate-the-warp-core-prop-with-the-executive),
  not duplicated here.
