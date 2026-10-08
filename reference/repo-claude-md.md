# The repo-root `CLAUDE.md`

CI settles the project's commands — capture them while they're fresh: generate a repo-root `CLAUDE.md` — when there is something to put in it (below), as admitted by `reference/in-repo-writes.md`. Claude Code reads it natively at every session start in the repo, so it is the one place operational facts reach every clean-context worker automatically.

**`CLAUDE.md` stays the operational-memory file on every harness.** The Claude Code main session and every dispatched worker read it; a Codex worker reads it explicitly (`reference/orchestrator.md` and `reference/worker.md`). Write discoveries back here through the PR. Respect a project's existing `AGENTS.md` instructions, which Codex loads natively, while keeping each operational fact at its established source. Do not duplicate this memory or install a managed method block in `AGENTS.md`.

**The file belongs to the repository owner.** DevStandard recommends content; it never gates a
change on the file's content or length. Since every session reads it, and architecture, decisions,
and tasks already have homes, we recommend short operational notes with pointers to those homes.
These three kinds, plus a conditional fourth below, are a useful starting point:

- **Commands** — install, test, run (the same ones CI just encoded);
- **Environment gotchas** — ports in use, services that must be up, local-vs-CI differences;
- **Untracked files a new worktree must copy** — the allowlist `reference/orchestrator.md`'s Worktree lifecycle section copies from (`.env`, keys, local config).

A cache or deploy root outside the tree is an environment gotcha of exactly this kind only when the
root itself already existed as an authority for this project's files or the human chose it. Recording
that place relays the authority so a clean-context worker does not invent another
(`reference/where-it-goes.md`); a `CLAUDE.md` line added in the same change never authorises a root the
change invented. The example below puts that relay under Gotchas.

A useful conditional fourth item: a `## Record language` line, when the repo's durable record is not English. It sits here because a clean-context worker must see it natively; the reasoning behind the choice is better kept in that repo's ADR log. Its absence means English.

A repo-wide language declaration in root `CLAUDE.md` overrides English for the whole record,
never per file or per agent. An established non-English record earns that declaration: write it
and follow the existing record, never start a mixed record. A human-facing translation is a marked
mirror naming its canonical file and changes in the same diff as that file.

Generate it only when the project actually has some of that to say. A file that merely transcribes what CI already encodes, or that would stand empty under every heading with no record language to declare, is noise every later session pays to read — skip it, and let the first real command, gotcha, copy-list line or record-language declaration create it through the same write-back lane.

It grows one line at a time: whoever merges a task that exposed a command, environment gotcha, worktree copy-list entry, or record-language declaration writes it back (the worktree checklist's Death step) through a short-branch PR like any other change.

For DevStandard's own operational notes, the writer keeps the 30-line cap (roughly twice the
example below) at write time: a write-back that would cross it also drops the line it most clearly
supersedes, or otherwise the stalest gotcha among those notes — never a separate cleanup pass.
This is the method writer's discipline, not a limit on what the owner's file may hold or permission
to remove the owner's chosen content.

This template is a good example to adapt:

```markdown
# <Project> — repo notes for agents

## Commands
- install: <command>
- test: <command>
- run: <command>

## Gotchas
- <port / service / local-vs-CI difference worth one line>
- <cache or deploy root already assigned to this project or chosen by the human, e.g. ~/.cache/foo or /srv/app — this line relays that place; it does not authorise a root this change invented>

## New worktree: copy these untracked files
- <path>   (or: none — everything load-bearing is tracked)

Architecture: see docs/architecture.md. Decisions: docs/adr/ unless the architecture doc points elsewhere. Tasks: GitHub issues.
```
