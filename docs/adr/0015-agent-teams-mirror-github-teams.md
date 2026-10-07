# 0015 — Agent teams mirror a human GitHub team: issues dispatch, PRs return, the ladder picks the executor

Status: Accepted (2026-07-09). Amended by 0045 (2026-09-05). Supersedes 0005. Amends 0007 (its
every-session budget, relaxed to carry the collaboration model inline) and 0009 (its "= one
session" invariant). Amended by 0022 (2026-07-24, small-change ceremony exemption). Amended
(2026-08-22). Amended by 0039 (2026-08-26). Amended by 0047 (2026-09-07). Amended by 0049
(2026-09-07). Amended (2026-09-07). Amended by 0056 (2026-09-11). Amended by 0063 (2026-09-29).
Amended (2026-10-07).

## Context

0005 fixed the parallel model as "one session = one branch = one worktree = one task." Three things push a refinement.

1. **"= one session" is the weakest link.** What is load-bearing is one-branch-one-worktree (isolation + clean integration); *who* executes inside is an execution-ladder choice, not a fixed identity. The rigid identity also contradicts 0009's own doctrine — sessions are mortal, and work must survive into another session.
2. **In practice the human does the core thinking with one persistent "main" session** (project definition, requirements drilling), and most tasks, once drilled, are baked enough to hand to a subagent or a workflow rather than a whole separate session — the cheapest rung that holds the work.
3. **Dispatch and hand-back had no durable substrate:** a worker's assignment lived in an ephemeral first prompt, and "who merges" was defined three incompatible ways across the docs.

## Decision

Model the agent team on a human GitHub team, on GitHub-native, durable artifacts:

1. **The main session is the cockpit** (human + Claude): core discussion, project definition, requirements drilling, dispatch, and integration decisions live here. It is the outer layer's single hub — it fans work out and fans it back in.
2. **Dispatch = a GitHub issue.** Work that earns a branch is filed as an issue: the durable, inspectable task spec carrying the done-check (replacing the ephemeral first prompt). A trivial in-repo change skips this — done in-session (the anti-ceremony floor, 0014).
3. **Executor = the cheapest ladder rung that holds the work** (the execution ladder, 0008). One task = one branch = one worktree; the executor inside is chosen, not fixed: trivial → the cockpit directly; baked/bounded → a subagent or workflow; too big to pre-specify (needs mid-flight steering) / long-running and parallel across time / another human's → a separate live session. "= one session" is retired as an invariant and becomes the top rung.
4. **Return = a PR** linked to the issue; the worker never writes main. While the author is live it rebases its own branch onto current main and resolves its own conflicts (it has the context); it never performs the merge. When the author is ephemeral (a subagent/workflow that ended at PR-open) and a later merge forces a conflicting re-rebase, the cockpit files it as a new bounded issue and dispatches a fresh worker — the rebase duty falls to whoever is live, never to a dead author.
5. **Integration is the cockpit's act as decision-maker.** For each PR it spawns a **fresh clean-context reviewer** (sees only the diff + the issue) — never grading its own work, never anchored by the cockpit's accumulated context — then green CI against current main (the two gates, 0011); then, with the human for judgment (good enough? touches architecture → human + ADR), it merges and closes the issue.
6. **Roles and boundaries are written down** so any executor knows them: you own your branch, you deliver a PR, you never merge or tag, your done-check is in the issue. A separate session learns this from injected `core.md`; a subagent, which gets no injection, learns it from `aids/worker-brief.md` pasted in at dispatch.

Surviving 0005 unchanged: CI/CD in the standard (green-before-merge; tag-triggered release; the human decides when to ship); architecture-touching merges pass the human + an ADR; a worktree dies with its task (0012).

## Consequences

The team runs on issues → branches → PRs → merges — the flow humans already converged on (0009), now literally reused. Everything durable is a GitHub artifact, so the cockpit is reconstructable for free (worklist = open issues + PRs) — no special rule needed. Executor cost scales with task difficulty instead of paying for a full session every time. Cost: the collaboration model is now large enough that it must be stated in full for workers, so core.md's every-session budget is relaxed (recorded as an amendment on 0007: hard ceiling ~3,000, kept lean) to carry roles, contract, and boundaries inline. The issue→PR flow binds work that earns a branch; trivial changes stay in-session.

**Amendment (2026-07-24, see 0022):** Decision point 2's small-work exemption ("a trivial in-repo change skips this — done in-session") is overturned — ceremony is now universal (every change rides a branch + PR + fresh review + CI). 0015's issues-dispatch / PRs-return / ladder-picks-executor core is unchanged.

**Amendment (2026-08-22):** Decision point 6 is stale on three counts, found while resolving issue
#122. *"injected `core.md`"* is superseded by 0019 — delivery is a forced read, not injection.
*"`aids/worker-brief.md`"* is superseded by 0031's rename to `reference/`. And the contrast itself —
a subagent gets the brief pasted, a separate session needs nothing more — understated what a separate
session's task can legitimately be: as unspecified as a subagent's task is not, per `core.md`'s own
routing rule. Measured, the brief carries operational detail `core.md` does not restate (a named
base, copying untracked files, vetting the issue at receipt, the flaky-check quarantine). Two things
now correct the third without touching point 6's text: `reference/worker-brief.md` is written to serve a
separate session reading it directly (issue #120), and `core.md`'s own pointer to it was strengthened
in the same pass (issue #122) so a separate session is told the brief adds detail rather than reading
the contrast as "you already have this."

**Amendment (2026-08-26, see 0039):** the cockpit this ADR's Decision names as "human + Claude"
is the human + the main session, whatever harness runs it. And the 2026-08-22 amendment's
load-bearing pointer (core.md's worker parenthetical routing a separate session to the brief) moved:
core.md now carries a neutral, third-person dispatch trigger — every dispatched worker receives, or
opens, the brief before acting — with the same effect and no self-classification.

**Amendment (2026-09-05, see 0045):** The 0039 amendment's harness-neutral cockpit is narrowed to the human and a Claude Code orchestrator. Codex participates only as a dispatched worker or reviewer process; worker identity and obligations still ride the dispatch brief.

**Amendment (2026-09-07, see 0047):** decision points 3 and 4 are overtaken. "Executor = the cheapest
ladder rung" retires with the ladder: dispatch is the default, and the executor is a purpose —
worker, reviewer, or a resolver as a worker assigned conflicts — times an implementation. And point
4's rebase clause is no longer conditioned on the author being ephemeral: the lane persists, and a
conflict found after handback always goes to a resolver dispatched into that affected lane, never
repaired by the orchestrator in its own worktree. The resolver's changed head takes a full review.
The cockpit, dispatch as an issue, and return as a PR stand as written; point 2's small-change
exemption had already gone to 0022.

**Amendment (2026-09-07, see 0049):** decision point 6's delivery contrast — a separate session
learns the rules from injected `core.md`, a subagent from a pasted brief — is retired. Static
context is one delivered artifact per role: an orchestrator's arrives by hook injection, and a
worker's or reviewer's arrives through dispatch, both naming the same operative role source. What
the point exists for — roles and boundaries written down so any executor knows them — is what the
split preserves.

**Amendment (2026-09-07, issue #279):** two corrections to the record; the decision is unchanged.
**Address.** The 2026-08-22 block's *"`reference/worker-brief.md` is written to serve a separate
session reading it directly (issue #120)"* names a page #235 reduced to a compatibility pointer and
#270 deleted. `reference/worker.md` is the operative source, and it carries the operational detail
that block measured — a named base, the copy-list, vetting the issue at receipt, the flaky-check
quarantine. Its reader is different, though: under 0045 and 0047 the standalone live-session lane is
outside the supported configuration (`reference/external-agent.md`; `docs/architecture.md` ch. 1), so
the page reaches a worker through dispatch rather than by being opened directly. The block's point —
that the brief adds detail `core.md` does not restate — is what the role split made structural.
**Status form.** The line above gains `Amends 0007` and `Amends 0009`, the form `reference/adr.md`
requires; both have announced `Amended by 0015 (2026-07-09)` since that date.

**Amendment (2026-09-11, see 0056):** The 0045 block's Claude-only cockpit is retired by 0056. One
Claude Code or Codex orchestrator uses the shared role source and its host's native workers. Codex
uses an independent read-only CLI for gating review. Separate live-session worker lanes remain
outside the configuration, and dispatch still supplies worker identity.

**Amendment (2026-09-29, see 0063):** 0063 restores the Claude-only cockpit: one Claude Code
orchestrator with its native workers. Codex takes part only as a dispatched CLI worker or read-only
gating reviewer, its role supplied by the dispatch brief. Separate live-session worker lanes remain
outside the configuration.

**Amendment (2026-10-07, issue #478):** Decision point 5's *"sees only the diff + the issue"*
describes the earlier supplied context, not a current restriction on independent evidence reads.
The complete review packet is the reviewer's primary judging context; repository and network
reads are available, with CLI reviewers in an independent pinned checkout. Clean context still
means no anchoring on the cockpit's accumulated session history. The judging contract and the
cockpit's integration authority are unchanged.
