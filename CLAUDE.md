# CLAUDE.md — mpyeng

Repo-level guidance for Claude Code working in this codebase. Loaded automatically
on session start.

## On startup

**Read `_familiarization/` first.** The README there indexes a set of current-state
docs covering what this code is, what it does, the architecture, the school program
it'll deploy into, and the active backlog. They're maintained incrementally as
David and Claude discuss; treat them as the canonical orientation material for a
new session.

The two other top-level reference docs:

- **`ARCHITECTURE.md`** — the forward-direction design doc. Only items confirmed
  in conversation go in. When in doubt, do **not** add to it; capture instead in
  `_familiarization/` or `TODO.md` and surface for confirmation.
- **`TODO.md`** — parked work organized by category. Long-range items at the
  bottom are explicitly *not anytime soon* and shouldn't be acted on without an
  explicit ask.

External reference material (datasheets, hardware docs) lives in `docs/`.

## Working mode

Default mode is **disjointed** — David reads through one of the familiarization
docs, surfaces corrections or new context for a specific topic, and Claude updates
the relevant files. Don't try to "complete" a topic in one turn. Record the new
info, surface clarification questions if something seems off, wait for the next
chunk.

A periodic **system-analyst interview** pass cleans up the accumulated state and
upgrades it into proper design docs / dev plans. The aim is for `_familiarization/`
to eventually be a current-state-accurate set of docs that can either bootstrap a
new Claude session or be handed to a future human collaborator.

## Subtree-specific guidance

The firmware tree at `engineering-board/engineering-board/` has its own
`AGENTS.md` with strict rules: minimal-change edits, no opportunistic refactoring,
no tests unless asked, performance-sensitive throughout. **Honor it when editing
in that subtree.** It captures real preferences from the firmware-perf work, not
generic boilerplate.

## Branch awareness

The active branch is `micropython`. The plan of record is for it to become the
new `main` once the codebase is in good enough shape; current `main` will be
archived. Do not try to reconcile divergence between the two branches — see
`ARCHITECTURE.md § Repo strategy`.
