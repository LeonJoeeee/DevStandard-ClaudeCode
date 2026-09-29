# 0007 — No router, no skill: the hook injects a one-page core

Status: Accepted (2026-06-11). Amended by 0045 (2026-09-05). Supersedes 0001. Amended by 0015 (2026-07-09); Amended (2026-07-16); Amended by 0019 (2026-07-24, delivery mechanism). Amended by 0031. Amended (2026-08-17). Amended by 0038 (2026-08-26). Amended by 0039 (2026-08-26). Amended by 0042 (2026-08-31). Amended by 0049 (2026-09-07). Amended (2026-09-07). Amended by 0056 (2026-09-11). Amended by 0063 (2026-09-29).

## Context

ADR 0001 shaped the plugin as manifest + hook + a lean ROUTER skill dispatching to ~12 reference files. Subsequent rulings shrank the content drastically: execution teaching was dropped entirely (the Workflow tool is the harness, ADR 0006; later hardened in ADR 0008 to "rules, not method"), and the per-phase methodology files collapsed into a handful of rules. With so little content left, a dispatcher has nothing to dispatch — the router became indirection for its own sake.

## Decision

Drop the router and the skill component entirely. The SessionStart hook injects **one file, `core.md` (~one page: trigger rule + execution discipline + collaboration standards + howto pointers)** directly as additionalContext. Everything else is plain on-demand files: `howto/` (PRD / architecture / ADR / CI-CD templates, read only at repo creation) and `aids/` (optional helpers, read when useful).

What survives from 0001 unchanged: the plugin shell (manifest + hook) as the trigger mechanism; the two on-demand loading seams; the absolute `@path` ban; the every-session token budget — now applied to core.md (target ≤ 800 tokens, ceiling ~1,000).

## Consequences

One less concept, one less hop, and the filename list under `howto/`/`aids/` is the only index needed. The cost: core.md must be ruthlessly edited — it is the single always-loaded artifact, so every line must earn permanent residency.

**Amendment (2026-07-09, see 0015):** The every-session budget is relaxed — hard ceiling ~3,000 tokens, kept as lean as the content earns (currently ~1,700) — so core.md can state the full collaboration model (roles, contract, worker boundaries) inline, because a subagent worker gets no injection and must be briefed from what the cockpit can quote. The hook-injected-one-page mechanism is unchanged; only the size ceiling moves — every line still earns its place.

**Amendment (2026-07-16):** The ceiling is raised again — hard ceiling 5,000 tokens (was ~3,000 via 0015), by the human's call: core.md reached ~3,000 after the v0.5–v0.8 rules (superpowers pointers, the design spec, the blanket clean-reviewer rule, docs-ride-the-diff) and every further line was fighting word-trims instead of clarity. The kept-as-lean-as-the-content-earns rule is unchanged — the ceiling is headroom, not a target.

**Amendment (2026-07-24, see 0019):** The **delivery mechanism** changes: the hook no longer injects core.md's full text as `additionalContext` (Claude Code inline-caps that at ~10KB and persisted the rest to a file behind a 2KB preview — issue #35). It now emits a short imperative instruction telling the model to **Read core.md in full as its mandatory first action**; the page is delivered by the read, not the paste. Everything else in this ADR is unchanged — no router, no skill, the one-page core, the on-demand `howto/`/`aids/` split, the `@path` ban, and the 5,000-token ceiling all stand (the ceiling is now the context-cost governor rather than a delivery limit).

**Amendment (2026-08-07, see 0031):** the two on-demand directories this ADR created — `howto/`
(templates, read when their artifact is due) and `aids/` (optional helpers) — are merged into one,
`reference/`. The split named a difference that produced no behaviour: both were read the same way
(core.md names a file, the agent reads it) and both resolved against the plugin root identically,
and two of the eight files already contradicted it. The on-demand property this ADR's cost argument
rests on is unchanged and now applies at finer grain — a file is as big as the smallest thing a
pointer asks for, so `howto/cicd.md`, which four separate core.md pointers each entered for a
different section at 5,196 tokens a time, became four files of 350–1,226 words.

**Amendment (2026-08-17, issue #91):** the 2026-07-09 amendment above says the relaxed budget is what lets
`core.md` *"state the full collaboration model (roles, contract, worker boundaries) inline"*. That
sentence is live — a reader deciding whether the page may drop worker material acts on it — so this
records what changed and what did not. **The worker's DO chain is no longer restated; the DONE
definition stays.** The DO chain was a second statement of things the page already says universally —
step 3 of the flow-at-a-glance gives the same build → docs → rebase → done-check → PR → green
sequence and gives it *better* (it says "on the final state", which the worker copy dropped), and the
doc duty, PR ownership and worktree teardown each have one universal statement elsewhere. The DONE
definition is retained essentially whole, because one of its clauses — **publishing the done-check
evidence in the PR description** — is stated nowhere else on the page. Check 1 caught that: the first
draft cut it as a duplicate, and a grep of the base page returns exactly one line. **Roles, boundaries
and the stop list stay inline, in full** — the model this sentence protects is intact; only the
duplication of it is gone.

**What a clean-context panel blocked — this paragraph is this repository's own record of how the
decision was reached, not an instruction to a seeded project.** The audit behind this (issue #91)
proposed cutting the whole block to a pointer, ~520 tokens. Six independent lenses
and three adversarial refuters cut that to ~190, and the decisive objection was not about weight:
**`reference/worker-brief.md` is a fill-in template with four `{PLACEHOLDER}` fields and a hard stop
— *"if any {field} above is still a placeholder … don't start"* — and the plugin's own copy is always
unfilled.** A separate live session is selected by `core.md` precisely when the work cannot be fully
specified up front, so pointing that reader at the brief aims it at the stop. **A pointer is only as
good as what it points at** — and the brief is a fine target when it is *filled and pasted*, which is
what it was built for; it is not yet a target a worker can read on its own.
Whether the NEVER list and the stop list may ever become a pointer is a question for the human
(0019 records the human rejecting a similar trade), not for an audit.

**Amendment (2026-08-17, issue #120):** the sentence above — *"it is not yet a target a worker can
read on its own"* — was true when the panel blocked the cut and is no longer.
`reference/worker-brief.md` now states the two ways a reader arrives at it, and scopes its
placeholder stop to a **pasted** brief: a separate live session is told its fields come from its own
issue, that it creates its own branch and worktree, and that what survives the paste is the *test* —
no result to reach and no machine-judgeable done-check means ask on the issue before building.

**The blocked cut is not thereby unblocked.** The panel's objection was one of two things standing in
its way; the other is the human's, recorded in 0019, and remains. What has changed is that the
pointer now has somewhere to point.

**Amendment (2026-08-26, see 0038):** the hook this ADR's delivery design relies on now branches by
harness; its Claude Code behavior is unchanged, and this ADR's description of the hook forcing a
read of core.md is scoped to that branch. On Codex the same script delivers the executor role
(0038).

**Amendment (2026-08-26, see 0039):** the 0038-era block above is corrected — the hook's Codex
branch does not deliver a worker role; it delivers the same forced read (core.md plus the bounded
mappings page), unconditionally. The Claude branch and this ADR's delivery reasoning are unchanged.

**Amendment (2026-08-31, see 0042):** the router this ADR refuses is an always-on dispatcher that
classifies requests and skills to choose what rule to load. `reference/where-it-goes.md` is not that
kind of router: it is an on-demand placement rule with a closing default, not a classifier.

**Amendment (2026-09-05, see 0045):** The Codex delivery described in the 0038/0039 amendments is removed, including the mappings page. The Claude Code hook still forces the same read of `core.md`; its existing budget and delivery reasoning stand.

**Amendment (2026-09-07, see 0049):** the one always-loaded page becomes one delivered artifact per
role — `core.md` for the shared contract, a separate operative source for each role — and this ADR's
every-session budget becomes a per-artifact byte budget that CI fails when an artifact's complete
hook context crosses the measured inline cap. The no-router, no-skill shape, the `@path` ban, and
the on-demand `reference/` split are unchanged.

**Amendment (2026-09-07, issue #279):** the 2026-08-17 (#120) block above routes a reader to
`reference/worker-brief.md`, which #235 reduced to a compatibility pointer and #270 deleted. The
operative worker source is `reference/worker.md`, and the two-ways-to-arrive framing that block
recorded did not survive the role split: a worker's role and task packet arrive by dispatch (0049),
so the page states one arrival and keeps the stop this ADR's panel cared about — a field that is
missing, still a placeholder, or too vague to act on cold is not started. The blocked cut was then
settled by the split rather than by either objection lapsing: `core.md`'s worker material is now a
role paragraph carrying the boundaries, the stop trigger and the pointer, while the full statement
moved to `reference/worker.md` — which is what the pointer now points at, and it is complete
without `core.md`.

**Amendment (2026-09-11, see 0056):** Codex host delivery returns under 0056 using the shared role
artifacts and a bounded adapter. The no-skill clause now excludes an explicit recovery entry that
reads those sources when hooks are unavailable; it does not replace automatic delivery with skill
self-triggering. No router, the on-demand reference split and the @path ban remain.

**Amendment (2026-09-29, see 0063):** 0063 removes Codex host delivery, its adapter and the
`devstandard` recovery skill, so the 0056 block's exception to the no-skill clause has nothing left
to except: the clause applies whole again. The Claude hook's per-artifact delivery, no router, the
on-demand reference split and the @path ban are unchanged.
