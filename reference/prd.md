# How to write the PRD

Read this at project start, before any code. The PRD answers **what we are building, why, and what counts as done** — never *how* (structure belongs in the architecture doc). One page. Write it WITH the human: their answers set direction.

Use the requirements binding in `reference/orchestrator.md` for the design dialogue;
return here for this document's content and location.

Why it exists: it is much easier to change your mind on paper than in code. The PRD's job is to catch "building the wrong thing" before anything is built.

## Sections (all four, keep each short)

1. **One sentence** — what this is, for whom.
2. **Why build it** — the problem or itch; what's wrong with not building it.
3. **Features as user value** — what the user can do, not how it works. Include **"What we are NOT doing"** — the explicit non-goals; this list prevents more wasted work than anything else.
4. **Definition of done (release criteria)** — concrete, checkable statements. These are the project-level ancestors of every task's done-check: tasks derive their bars from this list.
5. **Constraints** — hard limits worth writing down (compatibility, performance, budget, deadlines). Skip if none.

## Rules

- What/why only. The moment you write a component name or a data flow, move it to the architecture doc.
- Every release criterion must be mechanically checkable — "feels good" is not a criterion.
- Keep it maintained: when direction changes (through the human), update the PRD in the same change.

## Setup mechanics (the whole setup phase, not just the PRD)

The order below is not a style preference: each step is what makes the next one permitted.
Founding is the orchestrator's work, and it configures nothing: the guard has no settings file
(`reference/orchestrator.md`'s Guarded operations section).

1. **Create the repo**, after asking the human two things: the name, and public or private.
2. **Push the founding commits directly to main** — this PRD, the architecture doc, the skeleton,
   the CI and Dependabot files from `reference/ci-pipelines.md`, the `/.claude/worktrees/` line in
   `.gitignore`, and the repo-root `CLAUDE.md` if the project has anything to put in it.
3. **Apply branch protection last**: `guard protection --apply --check NAME` on main, naming the
   status check the CI file in step 2 reports. Use `scripts/guard protection --help` for the
   command contract; provisioning is the human's or the main session's work. From here everything
   lands through a PR, both checks and `scripts/guard merge`.

The architecture doc settled with the human IS the skeleton's design, and that settling is its
challenge — setup work needs no separate design spec. Keep that first skeleton minimal, with
interfaces and boundaries written as real code to pin where parallel tasks connect.

## Template

```markdown
# <Project> — PRD

## One sentence
<what this is, for whom>

## Why build it
<the problem; why now>

## Features (as user value)
- <user can ...>
- <user can ...>

### What we are NOT doing
- <non-goal>

## Definition of done
1. <checkable statement>
2. <checkable statement>

## Constraints
- <hard limit>
```

Omit the entire Constraints section if none apply.

Lands in the target repo as `docs/PRD.md` by default; an adopted repository's established convention
may supply another path (`reference/in-repo-writes.md`).
