# Familiarization Notes

Initial pass written by Claude during a 45-minute hand-off, 2026-05-08. Treat as a
first-impression brief; corrections welcome.

| File | Audience | What's in it |
| --- | --- | --- |
| [01-nature-of-code.md](01-nature-of-code.md) | Developers | What kind of code this is — languages, runtimes, target hardware, conventions |
| [02-project-explanation.md](02-project-explanation.md) | Developers | What the project IS — Thorium engineering bridge, audience, subdirectory map |
| [03-technical-overview.md](03-technical-overview.md) | Developers | Architecture, boot order, animation pipeline, comms, profiling |
| [04-refactoring-backlog.md](04-refactoring-backlog.md) | Developers | Refactoring opportunities for maintenance and code quality |
| [05-next-steps.md](05-next-steps.md) | Developers  | In-flight work, new features, verification, docs — ordered by closeness to current line of work. Pretty technical, Project Managers (Alex) might want to have a look, but we really need to create a higher-level doc for Alex. |
| [06-school-context.md](06-school-context.md) | Stakeholders | David's running notes on the school's space-sim program — internal background |
| [07-physical-installation.md](07-physical-installation.md) | Developers, Alex, Sim teams | Physical rig — frames, panels, where it lives, what's behind the patron-facing surface |
| [08-subsystems-and-interaction.md](08-subsystems-and-interaction.md) | Developers, Alex, Sim teams | Subsystem catalog: what each thing on the board IS, how it's used, firmware mapping, early puzzle thinking |

**Audience legend:**

- *Developers* — anyone writing or reviewing firmware, executive, or
  tooling code.
- *Alex* — the school's STEM / space-sim teacher; smart but with a physics
  background and basic programming knowledge. The on-site domain partner.
- *Sim teams* — the student teams contributing to the simulator: content
  (animations, visuals), authors / actors (scenario design and in-room
  performance), and admin / second-chair (operating the simulator during
  a mission).
- *Stakeholders* — the full space-sim group, other teachers, school admin, and etc???.

## Confidence map

- **High confidence:** purpose of `engineering-board/` firmware, animation pipeline shape,
  DeviceManager pattern, comms protocol shape, what's in attic, what's in dotnet, what's
  in solar-system-generator.
- **Medium confidence:** completeness of the organization-refactor plan (didn't run ruff /
  pyright to confirm), exact state of the PIO NeoPixel rewrite (read driver but not all
  callers), the 4 ESP32-S3 pin TODOs (subagent flagged them — I didn't open the file
  myself).
- **Lower confidence / not verified:**
  - Whether `card-resistance-tester/` (CircuitPython) is actually still in use or just
    not-deleted-yet.
  - Whether the `engineering-board-assets/` directory holds source schematics or compiled
    artifacts.
  - Whether any side-project code shares modules with the firmware in some non-obvious way
    (the explore agents say no, but I treated them as separate-and-related rather than
    walking every import).

## How I structured the docs

Each doc stands alone — you can hand any one to a new collaborator without the others.
There's some overlap between them (the same DeviceManager pattern shows up in 01, 02,
and 03) which is intentional for that reason.

Refactoring (04) and next-steps (05) are intentionally separated: refactoring items don't
add features, next-steps items do. A few things straddle the line — I put them in
whichever doc better matched their primary intent.
