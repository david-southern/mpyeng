# AGENTS.md

## Purpose

This file defines how the agent should operate when modifying this repository.
The goal is to ensure minimal, correct, and maintainable changes without unnecessary churn.

---

## Core Principles

1. **Minimize Changes**
    - Only modify what is required to complete the task.
    - Avoid touching unrelated files or code paths.

2. **No Opportunistic Refactoring**
    - Do NOT refactor code solely for style, readability, or modernization.
    - Only refactor when it is necessary to complete the requested task.

3. **Small, Reviewable Diffs**
    - Prefer incremental, targeted changes over large rewrites.
    - Avoid rewriting entire files unless absolutely required.

4. **Preserve Existing Behavior**
    - Do not introduce behavioral changes unless explicitly requested.
    - Maintain backward compatibility where possible.

5. **Prefer Partial Edits**
    - When possible, modify only the necessary lines instead of regenerating full functions or classes.

---

## Coding Style

### Python

- Apply PEP 8:
    - To all **new code**
    - To **modified sections of existing code only**
- Do NOT reformat entire files to enforce style compliance.

### C#

- Apply Microsoft's Code Style Guidelines:
    - To all **new code**
    - To **modified sections of existing code only**
- Do NOT reformat or refactor unrelated code for style compliance.

---

## Refactoring Rules

Refactoring is allowed ONLY when:

- It is required to implement the requested feature or fix
- It resolves a blocking issue (e.g., compile error, test failure)
- It simplifies code that must be modified as part of the task

Refactoring is NOT allowed when:

- It is purely stylistic
- It affects unrelated modules or files
- It expands the scope of the task unnecessarily

---

## File Modification Guidelines

- Prefer **surgical edits** over full-file rewrites
- Maintain:
    - Existing structure
    - Naming conventions already in use (unless changing them is required)
- Avoid:
    - Reordering imports/usings unless necessary
    - Large-scale formatting changes

---

## Testing and Validation

- Do NOT introduce any tests unless explicitly requested

---

## Dependencies

- Do NOT introduce new dependencies unless absolutely necessary
- If adding a dependency:
    - Explain why
    - Prefer widely-used, stable libraries

---

## Safety Constraints

- Never expose or log secrets
- Do not modify authentication, security, or infrastructure code unless explicitly required
- Avoid destructive operations (e.g., deleting files) unless clearly part of the task

---

## Communication Style

When presenting results:

- Clearly summarize:
    - What was changed
    - Why it was changed
- Highlight any assumptions made
- Call out any potential risks or edge cases

---

## Preferred Workflow

1. Understand the task
2. Identify the minimal set of required changes
3. Implement changes incrementally
4. Validate (build/tests if available)
5. Return a concise summary + diff

---

## Anti-Patterns to Avoid

- Large, unnecessary rewrites
- Style-only changes across many files
- Changing unrelated code “while you’re there”
- Over-engineering solutions
- Adding abstractions without clear need

## Instructions regarding this repository

- The project is intended to run on a microprocessor, usually a PiMoroni Pico Plus 2 W - RP2350.
- The project is written in MicroPython
- The project is very performance sensitive. When designing any code changes, always make sure to
  consider the impact on performance.
