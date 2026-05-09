# 07 — Physical Installation

What the engineering board physically *is* — frames, panels, where it
lives, what's behind the patron-facing surface. Audience is a future
collaborator who's about to touch code but hasn't been in the room yet.

Counterpart to [08-subsystems-and-interaction.md](08-subsystems-and-interaction.md):
this doc covers **shape and placement**; 08 covers **function and behavior**.

Reference photographs and per-image notes live in
[`../docs/images/`](../docs/images/). When the description here is unclear
or ambiguous, look at the photos — they're the source of truth.

## Where it lives

The engineering boards mount on the walls of the **engineering room** —
a roughly 5×5′ space (human-usable extent; true east-west axis is closer
to 8–9 ft) physically separate from the bridge, accessed through the
medbay / security room. See
[06-school-context.md § The space](06-school-context.md#the-space) for
the broader spatial context.

The room already contains:

- The **warp-core prop** on the **west wall**, above the control station
  — a Raspberry-Pi-driven NeoPixel display, already deployed.
- The **control station** on the south side — a desk that will run the
  Mac executive plus its monitor.
- An **archway to the medbay** (south wall, partially blocked by the
  control desk).
- A 32″ TV currently on the north wall — likely retired when the
  engineering boards are installed.

### Frame placement (TBD; pencil-in)

The exact placement of the two engineering-board frames is still open —
needs Alex on-site to measure the room. Two open walls (east, north) are
the likely candidates. **Pencilled in: north-east corner**, with the two
frames close enough that the 6′ guitar cables of the switchboard reach
between them but far enough apart that students aren't snagging cables
or running into each other in the working space.

Side-by-side on a single wall was the original plan but probably won't
fit — two 78 cm-wide frames want ~156 cm of wall and the room can't
quite spare it without putting a frame in front of the control desk.
This is one of the open items to confirm with Alex.

## Two boards, two frames

The engineering board is **two physical boards**, each in its own frame:

- **Left board** — wing power sources, the wing-side switchboard
  sources, and four transformers (with their displays, sources, and
  sinks).
- **Right board** — six power busses, each with a bus-control cluster
  and five power card trays.

Each board sits in its own independent frame; the only relationship
between the two frames is that both mount to the wall of the engineering
room. Their relative position on that wall isn't formally pinned down here
— check the photos or ask David — but they're close enough that the kids
can run guitar-cable connections between them as part of the switchboard.

## The frames

The frames are **2 mm sheet metal**, trapezoidal in profile (frustum-style
— front opening is the larger face, sides taper inward toward the back).
Each frame is **heavy** — install will likely be a two-person job. They've
spent four-plus years in storage so the surface is currently weathered;
they'll be **repainted before installation** (probably white, final
choice with Alex).

Approximate dimensions: **108 cm tall × 78 cm wide × ~4″ deep front-to-back**.

- Around the back perimeter, a **flat flange ~10 cm wide** that the frame
  mounts to the wall through.
- Around the front opening, a **~10 mm rebate** that the MDF panel seats
  into. The panel sits flush with the frame's front face. Decorative
  piping hides the seam between the panel edge and the frame.

> Dimensions in this doc are approximate. The frames already exist as
> physical objects we won't be modifying. The functional facts that matter
> are: there's roughly 4″ of working depth behind each panel for
> electronics, and the panels mount flush in the front rebate.

## The panels

Each panel is a **5 mm MDF board, 3′ tall × 2′ wide** (~91 × 61 cm). The
panel sits in the frame's front rebate. All the patron-facing features
(card-tray cutouts, audio-jack mounts, display windows, NeoPixel
windows) are routed into the MDF.

Detailed layout per board — what components live where — lives in
[08-subsystems-and-interaction.md](08-subsystems-and-interaction.md).
Photos of both boards (left front, left back, right WIP) are in
[`../docs/images/`](../docs/images/) and start there for the visual
picture.

## Behind the panel

The volume between the MDF panel (at the front rebate) and the back flange
of the frame — roughly 4″ of depth — is where **everything else lives**:

- The board's Pico controllers (see
  [ARCHITECTURE.md § Controller topology](../ARCHITECTURE.md#controller-topology))
  — current plan is **two Picos in the left frame** (sharing left-board
  responsibilities) and **one Pico in the right frame** (the card-tray
  animation controller).
- NeoPixel chains driving the wing grids, transformer grids, and tray
  animations.
- MCP3008 ADC chips for power-card identification (right board).
- TM1637 seven-segment displays.
- Wiring harnesses, connectors, the +5 V power-distribution rail.
- A **hidden USB pass-through** to each Pico (see
  [TODO § Hidden USB pass-through](../TODO.md#hidden-usb-pass-through-for-console--firmware-updates-committed-mvp-required)) —
  required for firmware updates and console debugging without opening the
  frame.

The frame, once mounted to the wall and the panel seated, is a **big lift
to open**. Plan accordingly: anything that needs post-deploy access (USB
ports, antenna leads, power connections) gets an external feature.
Anything else can live entirely inside the closed frame.

## RF environment

Worth knowing while writing comms code: the 2 mm steel frame is opaque
to 2.4 GHz Wi-Fi on five sides; the front face — where the 5 mm MDF
panel sits — is largely RF-permeable. Signal escapes mostly through the
panel face. Combined with the engineering room's distance from Alex's
control-closet Wi-Fi router (estimated 30–40 ft through walls), the
[in-frame Wi-Fi test](../TODO.md#confirm-wi-fi-works-inside-the-panel-frame)
is on early priority.

A repeater inside the engineering room is the leading remediation if the
test shows we need help. **Where** the repeater goes depends on where
the boards end up: if frames sit in the north-east corner, one panel
faces ~90° to the warp core (west wall) and the other ~90° to the
distant router — neither orientation is ideal for the panel's
RF-permeable face, so the repeater likely wants to be in the south-west
or south corner, well away from both frames. Cameras already in the
room give us cover for hiding additional small gear; finalize when
board placement does.

## Cross-references

- **Photos:** [`../docs/images/`](../docs/images/) and its README.
- **What each component does:** [08-subsystems-and-interaction.md](08-subsystems-and-interaction.md).
- **The school context the engineering room sits in:** [06-school-context.md](06-school-context.md).
- **Engineering decisions about the rig:** [`../ARCHITECTURE.md`](../ARCHITECTURE.md).
