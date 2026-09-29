# 0047 — DevStandard ships the collaboration machinery, and dispatch is the default

Status: Amended by 0050 (2026-09-09). Accepted (2026-09-07). Supersedes 0006 and 0008. Amends 0015 (its executor and
conflict-handling points), 0036 and 0040 (their rung vocabulary, which now names a retired
ladder). Amended (2026-09-07). Amended (2026-09-11). Amended by 0056 (2026-09-11). Amended (2026-09-20). Amended by 0063 (2026-09-29).

*This ADR changes what DevStandard ships — executable scripts, hooks and agent definitions inside
the installed plugin, and a different default for who does the work — so a reader in a seeded
project should take it as method.*

## Context

0006 refused to bundle orchestration machinery. What it actually rejected was a proposal for three
chained, parameterized workflow scripts loaded by Claude's Workflow tool, and its reasons were that
the loader was undocumented and had open field bugs, and that wrapping a harness in another harness
is over-engineering. 0008 then replaced "a Workflow per task" with the execution ladder — in-session
by default, then subagents, then workflow runs — because agent spend rather than orchestration is
the whole cost, and a run with no fan-out or loop is pure overhead.

Both answered the same question: how one task is executed. The approved collaboration architecture
asks a different one. PRD §1.1 is that the human ends up as the scheduler; §1.2 is that a
self-reported completion gets trusted. Neither is fixed by authoring a better per-task workflow.
Both need transitions the native harness does not provide and that no instruction reliably survives:
a dispatch that refuses an unfilled issue contract, a lane record that outlives the session that
made it, an admission gate that refuses a red or unreported head, a review packet assembled from
current state rather than copied, round accounting, and a merge that refuses a head no verdict
covers.

The rebuild built exactly those, as plain scripts and hooks in the plugin (#201/#208, #202/#213,
#203/#222, #204/#223) rather than as Workflow-tool runs. In the same rebuild the shipped pages
stopped naming the ladder at all: `core.md` limits the orchestrator's own concrete work to
one-or-two-line edits and research and dispatches everything else.

## Decision

**1. The plugin ships machinery.** `scripts/dispatch`, `scripts/review-packet`, `scripts/guard` and
their shared modules, the SessionStart and PreToolUse hooks, and the `agents/` role definitions are
shipped, versioned, and gated by this repository's tests. **0006's refusal survives where it was
aimed:** DevStandard still bundles no *per-task execution* machinery — no stage scripts, no authored
workflow templates, no fan-out pipeline — and still bundles nothing through the Workflow-tool loader
0006 found undocumented. What is overturned is the blanket "method, not machinery". The
collaboration protocol's fixed transitions are mechanism, and leaving them as instructions is what
made them optional in practice.

**2. Dispatch is the default; the ladder is retired.** The orchestrator's own concrete work is
limited to one-or-two-line edits and research, and everything else goes into a dispatched lane. The
method no longer picks among four rungs. It picks **purpose** — worker, reviewer, or a resolver as a
worker assigned conflicts — times **implementation**, and 0040 decides the implementation: Codex
where installed, a Claude-native subagent where the work especially suits one. Workflow runs and
chained runs are no longer named as executor forms.

**3. What survives from 0008 is restated here rather than left in a superseded file.** Run sizing's
substance — one coherent unit, split at human-decision and inspection points, never split for
capacity — is now the issue's bounds and the orchestrator's scope cutting. Rationing survives as
per-PR round accounting and the 7-round cap. 0024's cap and tier names are untouched. And 0008's
finding that a run cannot be steered mid-flight is why the **lane**, not the executor, is the durable
unit: a goal-fix round re-enters the same branch, worktree and PR, with a fresh executor if need be.

Rejected: **keeping the ladder as vocabulary beside the dispatcher** — two names for one choice, and
which rung a dispatched lane sits on answers nothing that purpose × implementation does not.
Rejected: **building these transitions as Workflow-tool runs** — 0006's loader objection stands, and
a run that cannot be steered mid-flight cannot host a same-lane continuation.

## Consequences

The installed plugin now has executable surface. It has to be tested — `.github/test-dispatch.py`,
`.github/test-review-packet.py`, `.github/test-hard-edges.py` are its gates — and a target project
inherits scripts it must be able to run: Python 3.9+, git, and an authenticated `gh`. A harness or
platform change can now break the method mechanically instead of merely making a page stale. That is
the trade, and those tests are what makes it visible rather than silent.

Losing the in-session default costs latency on genuinely small work, bounded by the one-or-two-line
carve-out. The machinery is exercised against this repository only; nothing here claims a second
repository has run it.

**What to watch:** a script is now a second place a rule can live. A rule stated in a script and
restated on a page is the drift the single-site discipline exists to prevent — the page owns
operation and policy, the script owns the mechanism, and `reference/hard-edges.md` is where that
division is stated for the guard.

**Amendment (2026-09-07, issue #279):** Decision point 3 says what survives from 0008 "is restated
here rather than left in a superseded file", and one clause is missing from the restatement: 0008's
**discipline backbone** — design refuted before code, verification-heavy token spend, evidence-based
closing — which 0008 applied at every rung and which applies unchanged to every dispatched lane. It
is alive on the shipped pages: `reference/orchestrator.md` commissions a clean challenge before
implementation and dispatches only the accepted design, and `core.md` requires the done-check on the
final state with its evidence. 0008's *"SDD remains optional"* is likewise still held, by 0017 as
its refinement rather than by this ADR — the design spec is trigger-gated, with meaning-preserving
refactors, objective improvements and invisible changes exempt (`reference/design-spec.md`).
Recorded so a reader who meets 0008 under `Superseded by 0047` does not read its backbone as having
died with its ladder. Nothing in this ADR's decision changes.

**Amendment (2026-09-09, see 0050):** Decision 3's statement that 0024's cap is untouched is
superseded by the human's 2026-09-09 ruling on issue #309. The model/effort ladder by kind of work
lives in `reference/external-agent.md`, “Route it explicitly”. This routing ladder does not
restore the retired execution rungs; dispatch, run sizing, rationing and the lane lifecycle
remain unchanged.

**Amendment (2026-09-11, see issue #332):** Decision 2 restates the implementation choice as
*"0040 decides the implementation: Codex where installed, a Claude-native subagent where the work
especially suits one"*. The routing half still holds — 0040 does decide it — and the content is
reversed: as amended on 2026-09-11, 0040 makes the host's own subagent the default, with Codex
selected by the human's instruction for one dispatch or standing until their next
(`reference/external-agent.md`, "When a subagent, when Codex"). What this ADR itself decides is
untouched: dispatch is still the default against in-session work, the ladder stays retired, and the
choice is still purpose × implementation.

**Amendment (2026-09-11, see 0056):** 0056 restores Codex as a host using this ADR's collaboration
machinery. Both hosts use their native workers; Codex native dispatch prepares a full-role receipt
for the caller's actual spawn/wait tools. Codex gating review uses an independent read-only CLI.
Dispatch-first execution, issue/branch/worktree lanes, review accounting and the refusal to bundle
per-task workflows remain unchanged.

**Amendment (2026-09-20, issue #434):** Decision point 3's *"Rationing survives as per-PR round
accounting and the 7-round cap"* loses the cap. Per-PR round accounting survives exactly as
described; the count is reported and warned about rather than enforced, because no record exists of
the cap ever firing and the reviewer's non-convergence clause carries the stop signal #173 measured.
0046's 2026-09-20 block states it; `reference/orchestrator.md`'s Review packets section carries the
operative wording.

**Amendment (2026-09-29, see 0063):** 0063 removes Codex hosting and its native-dispatch receipts.
Dispatch runs from a Claude Code orchestrator; Codex is the `--implementation codex` CLI executor.
Dispatch-first execution, issue/branch/worktree lanes, review accounting and the refusal to bundle
per-task workflows are unchanged.
