# 0026 — A PR is owned until its checks report green; the duty transfers with delivery

Status: Accepted (2026-08-03). Extends 0009 and 0022 (the lifecycle's step-3 finish line). Cites 0011 and 0025 without amending them: the two gates, the reviewed-diff-is-the-merged-diff rule and the check-2 fallback stand exactly as written, and RED remains a non-trigger. Amended by 0032 (2026-08-13). Amended (2026-09-07). Amended (2026-09-20). Amended (2026-10-07).

## Context

The method defined the doer's finish line as "a PR open and linked to the issue, rebased clean on current main, evidence in the description" — a state reached before any check has reported. The observed failure: the PR is opened and abandoned; CI goes red afterwards, review bots post findings, nobody drives it back, and the human's reviewer arrives at work that was never ready. The method also had no concept of a review bot at all, because every repo it had run on was ours end to end — while 0021 makes Dependabot standard in every DevStandard project, so bot-authored PRs already exist here.

Four forces shaped the rule. A dispatched subagent physically cannot watch a run that finishes after it terminates, so "own it until green" needs a named transfer rather than a fiction nobody can satisfy. A red check and a bot finding sit side by side on a PR page but are different objects — one is a gate, one is an opinion. Any "stay until green" rule invites three escapes: reading a red check as CI being unavailable (0025's fallback), loosening a check until it passes (the done-check weakening ban), and the softest one — declaring done by *narrating* the red check in a handback. And the rule must not fire in the one state where green is impossible by design: a declared 0025 fallback, where the required check never reports and 0011's gate 2 is already degraded under its own rules.

## Decision

Whoever opens a PR owns it until every check on it **reports** green and every review-bot finding is fixed or answered on the PR. An unreported check is not a green one — the handoff point is "machines satisfied", never "I pushed it". A PR a bot opened has no session behind it and is the main session's from the moment it appears, like every other open PR on its to-do list.

- **Bot findings reuse verify-then-refute**, the discipline `aids/worker-brief.md` already prescribes for check-1 findings, with exactly one stated delta: the answer goes on the PR, because no re-review settles a bot. A parallel bot-specific rule was rejected — a duplicate drifts from the rule it duplicates, and a worker that generalised "reply on the PR" back onto a check-1 finding would be dodging a blocking finding with narrative, which 0011 and `aids/code-review-prompt.md` forbid.
- **A red check is the gate, not an opinion**, and it has three states, not two: your diff caused it (fix the diff); your change deliberately staled the check's assumption (fix the check in the same PR, naming the staled assumption in the implementer's report and the PR description); or it is neither — a red `main` (0020's revert-first path), or an aged pipeline that is yours to fix in this diff only when your task already touches that workflow file — otherwise neither is yours to fix and neither is yours to work around. core.md carries the gate and the ban ("fix the cause, never loosen the check") and NOT the repair licence: the force-read page is what a separate session reads, and a permission whose guards live in files it may never open fails in the wrong direction. `aids/code-review-prompt.md` judges the repair, since a diff touching CI cannot be vouched for by CI.
- **Handing back is not finishing.** A doer that must return before a check reports hands back the PR link and names the unreported checks — never a check it watched go red, which is unfinished work that a sentence in a handback does not finish. Without this the rule would be weaker than the finish line it replaces, because it would put a written blessing on returning a known-red PR.
- **The duty transfers with delivery.** The main session inherits when it takes delivery, and its first act on a returned PR is the PR's checks, not spawning check 1. It then finishes the PR itself on the worker's branch (the worker has terminated, so one-writer-per-worktree holds) or re-dispatches with the new CI output and bot findings — which is the "change something before you re-dispatch" the ladder already requires, and which transfers that branch and worktree to the new worker outright. Where a worker spawned a worker, the handback rides up the chain like a stop message; passing it on is each intermediate's job. A PR the main session opened itself never transfers.
- **Not a route into 0025, and 0025 is not a breach of this.** The fallback triggers on no run at all from two named platform causes; a run that starts and fails is CI working. In reverse, while a fallback is in force there are no checks to drive green, and a required check parked at "Expected — waiting for status to be reported" is that state, not a never-green check to escalate.
- **Nothing waits forever, and nothing is waived into main.** A check that can never go green — someone else's broken required check, a job needing an absent secret, a bot demanding what the human vetoed — is named on the PR and escalated: doer → main session → human. What ends the block is a change landed through the ordinary ceremony (a tracked quarantine, a pipeline fix in its own PR, or the human deliberately editing the required-check list), never a waiver improvised in chat and never an agent switching a check off.

Rejected: (a) fix everything a bot raises — a bot is a confident false-positive generator, and forced compliance corrupts code to satisfy a machine; (b) reply-and-dismiss for both signal kinds alike — it lets a gate be argued away in prose, the one thing a gate exists to prevent; (c) leaving the duty with the doer unconditionally — unsatisfiable for a subagent that terminates, and an unsatisfiable rule is ignored rather than obeyed; (d) a polling "PR nanny" role or a watch loop — recurring cost with no owner, when open PRs are already the main session's to-do list; (e) keeping the whole rule in `howto/cicd.md` — the finish line it corrects is stated in the force-read page, so the correction must be there too; (f) letting a handback cover a check the doer saw fail — it converts the rule into "say something and leave", weaker than the finish line it replaces; (g) a human waiver at merge time for a permanently red check — a bypass of check 2 strictly cheaper than 0025's fallback, with no local run, no `CI-FALLBACK` marker, no evidence comment, no check-1 audit and nothing for the return sweep to find, after which the honest fallback would never be used again; (h) a not-our-repo lane (their checks and reviewers are the gate, nobody on our side merges, step 4 and the fallback do not apply) — true, but stating it anywhere is a substantive change to 0011 and 0022 requiring dated amendments to both, it is scope the observed failure never asked for, and core.md line 63 already gates entry on the human's explicit handoff; deferred to its own ADR if and when such work is actually handed over, rather than smuggled in on this one; (i) putting the stale-check repair licence in core.md — see above; (j) an explicit "this is not the check-2 fallback" line in core.md — the fallback paragraph nine lines below already names red a non-trigger, so core would pay twice for one guard.

## Consequences

core.md pays ~135 tokens (4,183 → 4,318 of 5,000) for the ownership rule, the reported-not-merely-absent test, the bot/check asymmetry with the never-loosen ban, the narrow handback and the transfer; core.zh-CN.md mirrors it clause for clause. `howto/cicd.md` carries the operational half — what green means, the three red states and the stale-check repair, the two-directional non-route with 0025, taking delivery and re-dispatch, bot-opened PRs, handing-back-is-not-finishing, and the never-green escalation with no chat waiver. `aids/worker-brief.md` carries everything a dispatched worker must do, since a worker never reads core.md: the DO/NEVER additions, the bot-findings delta beside the existing check-1 paragraph, the red-check-is-the-gate paragraph, the fallback carve-out, a new stop-trigger reconciled with the existing flaky-done-check rule, and a rewritten Done. `aids/code-review-prompt.md` extends its gate-change item to judge check repairs, anchored to the implementer's report. `docs/architecture.md` §4 drops the stale "delivers a PR and never merges" finish line.

What to watch: check repairs riding PRs — the new weakening surface, now check 1's alone; PRs handed back with a red check described as merely unreported; PRs parked as "can never go green" with no escalation comment, the old rot in the new rule's clothes; and flakes re-run once into a green the flaky-check rule would have quarantined.

Three holes are accepted knowingly rather than closed, and are the joints most likely to bend:

- **The doer that returns the instant the PR opens**, for which every check is legitimately "unreported" — the guard there is self-judged, deliberately. "Wait for it if you can" and "only when you actually have to" cannot be machine-checked, and the alternatives were worse: a rule a terminating subagent cannot satisfy is ignored rather than obeyed (Rejected (c)), and a polling nanny has recurring cost with no owner (Rejected (d)). What contains it is that the duty transfers rather than evaporating, and that no unreported check can reach main — check 2 is untouched. The symptom to watch is a doer whose handbacks are always instant.
- **Check 1 cannot verify that a bot finding was answered.** The reviewer is handed the diff, the requirements and the implementer's report and nothing else — never the PR page — so "every finding fixed or answered" has no gate behind it, and an audit item asking for one would be unenforceable by the only party asked to enforce it. It is the merging session's act at delivery instead, which is why `howto/cicd.md` puts it in the first act on a returned PR rather than in `aids/code-review-prompt.md`.
- **The handback chain has no receipt.** Where a worker spawned a worker, an unreported check named in a handback survives only if each intermediate passes it on; nothing detects a summary that quietly drops it, and the duty then ends up held by nobody. The mitigation is that it rides the same chain as a stop message, which agents already relay.

**Amendment (2026-08-13, see 0032):** **the three-states rule is unchanged in every word and every
consequence** — what moved is where it is written. Decision bullet 3 stated it in full, and the
implementation put near-verbatim copies in both `reference/driving-a-pr-green.md` (218 words) and
`reference/worker-brief.md` (224 words), which is the drift shape this ADR's own bullet 2 rejected a
duplicate for ("a duplicate drifts from the rule it duplicates"). It now has one statement, in
`reference/red-check.md`; both former sites carry the trigger — *a red check is the gate, and there
are three states, not two* — plus the pointer. 0032 records why the file is new rather than one site
pointing at the other: a pointer from `driving-a-pr-green.md` into the 2,209-word brief would have
cost 2,209 words to answer a 218-word question. (`aids/` above is history: 0031 renamed the
directory to `reference/`.)

**Amendment (2026-09-07, issue #279):** Decision bullet 5's repair route is overtaken by 0047, whose
Amends list did not reach this ADR. **The transfer stands** — the main session inherits when it
takes delivery, and its first act on a returned PR is still the PR's checks rather than spawning
check 1. What changed is what it does next. Dispatch is the default: the orchestrator's own concrete
work is bounded to one-or-two-line edits, and anything larger — including conflict resolution — is
a dispatched continuation into the **same** lane, carrying the named gap (`core.md`;
`reference/orchestrator.md`; `reference/driving-a-pr-green.md`). So *"finishes the PR itself on the
worker's branch"* is no longer the ordinary path, and the premise it rested on has gone with it: the
lane is now the durable unit and the executor is disposable, so one-writer-per-worktree is held by
the lane rather than by the worker having terminated. *"the 'change something before you
re-dispatch' the ladder already requires"* is the retired ladder's vocabulary; the requirement itself
survives as the named goal gap a continuation brief must carry, bounded by the 7-round cap.

**Amendment (2026-09-07, issue #279):** Decision bullet 3's placement clause — *"core.md carries
the gate and the ban … **and NOT the repair licence**"*, repeated as Rejected (i) — is scoped to
the pre-split page. `core.md`'s red-check trigger row now names the visible repair of a deliberately
staled assumption alongside the gate and the escalation, so the licence is resident. The ground the
clause gave has lapsed rather than been overruled: it reasoned that "the force-read page is what a
separate session reads", and under 0049 a worker is not delivered `core.md` at all — the page's
reader is the orchestrator, who can open `reference/red-check.md`, while `reference/worker.md`
carries the same trigger with its guards for a worker. What the clause protected is intact: the
licence has exactly one full statement, in `reference/red-check.md` since the 2026-08-13 block above,
and what sits on `core.md` is the trigger that makes a reader go there. That block's *"both former
sites carry the trigger … plus the pointer"* still holds with one address corrected: they are
`reference/driving-a-pr-green.md` and `reference/worker.md`, the latter being what
`reference/worker-brief.md` became before #270 deleted it.

**Amendment (2026-09-20, issue #434):** the 2026-09-07 block's closing *"bounded by the 7-round
cap"* no longer names a bound. The named goal gap a continuation brief must carry is unchanged; what
goes is the count as a gate on how many continuations may run. 0046's 2026-09-20 block states it.

**Amendment (2026-10-07, issue #478):** the Consequences' capability rationale for *"Check 1
cannot verify that a bot finding was answered"* no longer holds: reviewers can read repository
files and network history, including the PR page. The PR owner's duty to fix or publicly answer
every bot finding, and the merging session's delivery check, remain unchanged. This capability
change adds no judging criterion; the canonical Goal/Floor/Notes contract still defines check 1.
