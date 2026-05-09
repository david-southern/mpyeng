# 06 — Stakeholders and School Program Context

David's understanding, gathered over five years of conversations with Alex DeBirk — the school's
STEM / space-sim teacher — and helping with construction of the bridge, installation of warp core,
etc. **David has never been on-site for an actual run.** Treat the details below as second-hand and
approximate; clarify in the system-analyst interview if any of it turns out to be load-bearing.

## The program

The school runs a **Space Simulator** as a full-year class students can take.
Students help Alex design and run the simulator throughout the year. The actual
"missions" are run for school kids only — probably because Alex's actor-students
are all minors, so the participants need to be too. There have been a few pilot
**after-hours performances for outside adult audiences**, but the current status
of that is unclear.

## The space

- **The bridge.** The main set — fully decorated, DMX lighting, full sound
  rig, rumble panels, the works. Alex once demoed a "red alert, damage to
  the starboard wing" scenario for David in person; reportedly very
  impressive.
- **The engineering room.** Roughly 5×5′ of human-usable space (true
  east-west extent is closer to 8–9 ft including the control desk's
  footprint). Holds **this project's engineering boards** (placement TBD;
  see [07](07-physical-installation.md)), the **warp-core prop** (a
  Raspberry-Pi-driven NeoPixel display already deployed, mounted on the
  west wall above the control station), and the **control station** —
  the desk that will run the Mac executive. **Physically separate from
  the bridge — not visible from there, and no intercom.** Access is
  through the medbay / security room. Bridge↔engineering communication
  during a mission happens by shouting through the wall or by a runner —
  a real puzzle-design constraint: **scenarios cannot depend on precise
  verbal coordination across that boundary.**
- **The medbay / security room.** Repurposed depending on the scenario;
  also the corridor between the bridge and the engineering room.
- **The hallway and "transporter."** A corridor leaves the bridge through
  an opaque rotating door (the in-fiction transporter). It leads to —
- **The Galileo.** A physical prop of an away shuttle, sized to send 4–5
  patrons out on a mission. As of David's visit ~a year ago, still under
  construction. Possibly used as a static set in the meantime; exact
  current status unknown.

## The student teams

David's mental identifiers — not necessarily Alex's actual team names.

### Set design

Builds and maintains the physical sets — bridge décor, the engineering closet,
the Galileo, the rotating-door rig, etc. Probably the team this project has the
least direct overlap with.

### Content kids

Make the special effects: animations, videos for "leaving port," planet
surfaces, viewport content, set-piece visual effects. **This is the team most
likely to take over the power-card animations once the tooling is good enough.**
The current animations were placeholders David authored using a viewer-shaped
tool that no kid can be productive in — see
[TODO § Make the designer actually a designer](../TODO.md#make-the-designer-actually-a-designer-crud).

### Scenario / actors

Students who play roles during a mission, interacting with patrons in real time.
The team is actually a cluster of related in-the-room jobs:

- **Costumed actors.** Play characters during the mission — the Admiral phoning
  in with an emergency, the security officer assigned to an away team, the evil
  alien who transports onto the bridge.
- **"Prod the patrons" support.** Keep patrons moving when they get stuck on a
  scenario beat or puzzle. Less about playing a character, more about steering
  the experience.
- **Judges.** Adjudicate physical interactions the simulator can't resolve.
  Example: when the evil alien transports onto the bridge, the judge calls
  whether the redshirt patron with the Nerf blaster actually hits the monster.
- **Sound and "second chair" control.** A few kids help Alex run the sound
  mixers and operate Thorium as second chair. May overlap with the other roles
  above; David's not sure of the boundaries.

This team is the most likely to **author or contribute to STEM-puzzle
scenarios** for the [executive layer](../ARCHITECTURE.md#executive-layer), so
whether they can be productive in the puzzle DSL is a real design constraint.

### The patrons

Patrons are also school kids — typically **3rd grade through 10th grade**. A
single scenario may be run for a group of 8-year-olds and (separately) for a
group of 15-year-olds, so any puzzle the executive runs needs **scalable
difficulty**: separate scenarios per age band, graduated difficulty within a
scenario, or some hybrid. This is its own design constraint, separate from who
*authors* the scenarios.

### The "Coders" team that hasn't worked

Alex has tried several times over the years to establish a fourth team — kids
who write software for the simulator's custom hardware (i.e. the kind of work
this project is). It hasn't stuck. The realistic complexity is too high for the
typical incoming experience level, and a single school year isn't enough to
ramp a beginner from zero to productive on a system like this.

**Implication:** don't plan to hand any of the firmware / executive / DSL
implementation work off to school students. Animation content (via a good
designer tool) and puzzle scenarios (via an approachable DSL) are the
realistic kid-touchable surfaces; the engines below them are not.

## How this maps to the project

- **Alex** is the on-site partner and the domain decision-maker for the
  simulator software (Thorium / Horizons), the bridge integration, and what
  features the engineering board needs to support to be useful in a mission.
- **David** is building and shipping the engineering board, with Alex providing
  domain input. Both are on the hook for initial puzzle design.
- **Content kids** will eventually own the animation content, once the
  tooling is good enough for them to be productive.
- **Scenario / actors kids** may eventually author puzzle scenarios for the
  executive layer — a constraint on the puzzle DSL.
- **Set-design kids** are mostly out of scope here; their work is the physical
  environment around the engineering room.
- **No "Coders" team.** Implementation work stays with David and Claude.

## Open questions

- Is `solar-system-generator/` still in active use by the content team? (Drives
  the polish-vs-archive decision in
  [TODO § solar-system-generator](../TODO.md#solar-system-generator--split-out-and-possibly-polish).)
- Are there other school-pipeline tools we should know about or interoperate with?
- Have the after-hours adult performances continued? Relevant if we want a less
  unforgiving audience for the first integration runs.
