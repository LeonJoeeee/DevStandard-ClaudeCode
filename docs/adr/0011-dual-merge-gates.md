# 0011 — Two ordered merge gates: clean-context diff review, then green CI

Status: Accepted (2026-07-02). Amended by 0045 (2026-09-05). Amended by 0025 (2026-08-02). Amended by 0035 (2026-08-22). Amended by 0040 (2026-08-26). Amended by 0044 (2026-09-02). Amended by 0046 (2026-09-05). Amended (2026-09-07). Amended (2026-09-11). Amended by 0056 (2026-09-11). Amended by 0063 (2026-09-29). Amended by 0064 (2026-10-04). Amended (2026-10-07).

## Context

A source-grounded dissection of the two dominant published agent-dev methods found neither composes agent review with a deterministic CI gate. superpowers layers clean-context review over locally-run tests and then self-merges locally — the exact self-graded finish DevStandard forbids; a community PR adding a CI gate (obra/superpowers#1505) was closed unmerged. GitHub Spec Kit (~117k stars) prescribes neither review nor CI after implementation: tests are "OPTIONAL", the lifecycle ends at "report to user". Notably, superpowers' own doctrine argues the composition it never built: "tests passing" is explicitly *not sufficient* for "requirements met", and its task reviewer is told **not** to re-run the suite — review and deterministic checks are layers with different jobs.

Meanwhile DevStandard's own merge rule ("CI must be green") had two verified holes. First, no eyes on the diff at the merge boundary: design refutation happens *before* implementation, CI checks only what tests encode — so a non-architecture PR merged with zero review of the code itself, dropping the one safeguard human GitHub flow is built around. Second, green-on-branch ≠ green-after-merge: a branch tested against a stale base can merge a red main out of two individually green branches, and the failure rate grows with exactly the parallelism the method advertises.

## Decision

Per task, the merge is guarded by **two ordered gates**:

1. **Clean-context review of the branch diff.** The reviewer is a **fresh subagent spawned per merge** — it must not have written the code, and must not be the cockpit's own accumulated context (0015); a saturated reviewer is anchored, not clean. It gets the diff (base/head SHAs), the requirements/issue, and the implementer's report as unverified claims — never any session history. Critical/Important findings block: fix, then re-review. Minor findings are recorded, never block. The reviewer does not re-run the test suite — CI owns pass/fail; the reviewer owns what tests can't see (spec fit, test quality, design, check integrity).
2. **Green CI on the merge result against current main**, as a required check that binds admins ("require branches to be up to date"; a merge queue only for conflict-free fast-forwards).

**The reviewed diff is the merged diff.** Any rebase after gate 1 — conflict resolution, or a base that moved — re-triggers gate 1 on the new diff; a merge queue never auto-rebases past review. Otherwise conflict-resolution code reaches main unreviewed — exactly the two-green-branches case gate 2 was written to catch.

Layers, not substitutes: no agent verdict substitutes for CI; no green CI substitutes for review. Both gates and the merge are the cockpit's act as integration decision-maker (0015); a worker never merges. Rejected: agent review as the *final* gate (superpowers' model) — a probabilistic gate as the last word reintroduces the self-grading failure the field converged on eliminating; the deterministic gate says the last word.

## Consequences

core.md's collaboration standards carry the ordered chain; reviewer-context rules land in `aids/code-review-prompt.md`; `howto/cicd.md` hardens branch protection (up-to-date requirement, no admin bypass, free-plan-private caveat). Review scope shrinks (no suite re-runs), making reviews cheaper and non-overlapping with CI. Cost: one review round-trip per PR — paid from the parallelism budget the method already earmarks for verification.

**Amendment (2026-08-02, see 0025):** gate 2 stands exactly as written whenever CI can run.
Newly covered is the case this ADR never contemplated — the platform can produce no run at
all (Actions minutes exhausted on a private repo, provider outage). There, and only there,
check 2 degrades to a declared local run by the merging session on the merged result,
evidenced on the PR under a `CI-FALLBACK` marker and audited by check 1 — which is also the
one case where gate 2's evidence precedes gate 1 — ending at the first push that produces a
run; `main`'s next green CI re-verifies everything merged under it. A slow, queued, flaky or
RED CI is not this case, nor is anything this repo or its org could fix, nor a repo with no CI.

**Amendment (2026-08-22, see 0035):** the reviewed-diff-is-the-merged-diff rule (Decision, above)
gains two narrow, evidenced exceptions. **The first never touches a Critical or Important finding**
— it applies only when the verdict already returned Ready to merge with nothing but Minors, and one
Minor's own quoted text is applied verbatim and nothing else; a Critical or Important still fixes,
then re-reviews, exactly as this ADR states, however exact the reviewer's own replacement text was.
**The second — a fix that never touches the merged tree, most commonly a PR description — does
narrow the fix-then-re-review semantic**, for findings of any severity, because the reviewed-diff
rule was never engaged in the first place: the tree it governs did not move. Neither exception is
conditioned on reviewer availability; both are evidenced by two SHAs a later reader checks directly
rather than trusting an assertion. Both gates and their order are unchanged. Full conditions in
`reference/code-review-prompt.md`.

**Amendment (2026-08-26, see 0040):** "a fresh subagent spawned per merge" names the executor of its day. The gate's requirement is the property — a fresh, process-isolated, read-only, clean-context reviewer that did not write the code — and where Codex is installed that reviewer is a read-only `codex exec` run; a harness-native executor only where it keeps those properties, and where none can (a Codex main session's `spawn_agent` inherits the writable sandbox) the gate is blocked, not lowered (`reference/external-agent.md`, "When a subagent, when Codex" and "When it is not there"). Everything else in gate 1 stands as written.

**Amendment (2026-09-02, see 0044):** check 1's severity-ranked findings are replaced by the
goal-centric judging contract in `reference/code-review-prompt.md`: goal fulfillment and its
two-check Floor alone decide readiness, while peripheral observations are Notes. Reviewer isolation,
packet inputs and integrity, the no-suite-rerun boundary, both ordered gates, and the
reviewed-diff-is-the-merged-diff rule remain unchanged.

**Amendment (2026-09-05, see 0045):** The Codex-main-session fallback example in the 0040 amendment is outside the supported configuration. The reviewer remains a fresh, process-isolated, read-only executor; if none can preserve those properties, the gate remains blocked (`reference/external-agent.md`, "When it is not there").

**Amendment (2026-09-05, see 0046):** the approved option-A path permits prior acceptance after a conflict-free rebase only when every PR-changed path remains byte/mode-identical and CI passes on the current merged result. `reference/hard-edges.md` carries the guarded CLI and proof contract. This is distinct from an arbitrary unchanged tree or amended commit; failed proof returns to full review. The original quoted-Note and artifact-only exceptions remain as recorded, but the CLI conservatively requires full review for a changed head outside its rebase proof.

**Amendment (2026-09-07, issues #242 and #256):** the byte/mode-identical clause in the 0046 block
above has one exemption. Because the version bump rides the change PR, the two Claude manifest
version lines may differ across the proof — but only when both move in lockstep to the same value,
that value is the one the reviewed head itself declared, and it sorts strictly above the version it
replaces read as a dotted numeric release. Any other byte or mode difference on any path still
refuses to full review. `reference/hard-edges.md` carries the operative wording.

**Amendment (2026-09-07, issue #280):** gate 2's parenthetical permission for "a merge queue only
for conflict-free fast-forwards" (Decision, item 2) is withdrawn — the queue stays off, in every
configuration. Since 0046 the merge is the orchestrator's guarded act, and GitHub's queue merges
server-side: what lands is a commit the server built, so gate 1's reviewed commit is not the one
that reaches main and the guarded entry point never runs — however the queue is configured, and
whatever checks it runs on its own commit. The Decision's own "a merge queue never auto-rebases past
review" is unaffected, as are both gates and the reviewed-diff-is-the-merged-diff rule. `reference/hard-edges.md` carries the operative wording, and
`guard protection` reports an enabled `merge_queue` rule as non-conforming.

**Amendment (2026-09-07, issues #226 and #234):** the Decision's *"Layers, not substitutes: … no
green CI substitutes for review"* has one narrow exemption, on the human's ruling of 2026-09-06 that
the version bump rides the change PR. An unavoidable **bare bump PR changing only the two Claude
manifest version lines** needs no check-1 reviewer: CI's lockstep gate covers the whole of that
diff, so it is that PR's review rather than a substitute for one. Gate 2, the gate order, the
reviewed-diff-is-the-merged-diff rule and the guarded merge are untouched, and every other change
still takes both gates. 0022 carries the carve-out and its ground; `core.md` carries the operative
wording.

**Amendment (2026-09-11, see issue #332):** "where Codex is installed that reviewer is a read-only
`codex exec` run" now reads: the reviewer runs on whichever executor the human's instruction names,
and by default on the host's own freshly spawned subagent (ADR 0040's 2026-09-11 amendment;
`reference/external-agent.md`, "When a subagent, when Codex"). Gate 1's requirement is unchanged —
the properties, and blocked rather than lowered where no available executor keeps them.

**Amendment (2026-09-11, see 0056):** Codex main sessions return under 0056, so the 0045 block's
exclusion of that topology is retired. Their gating reviewers use the existing fresh read-only
process path; an unavailable qualified reviewer still blocks the gate. The two checks are unchanged;
the version-line exemptions now cover all three synchronized release manifests under the same
byte/mode and ordering checks (`reference/hard-edges.md`).

**Amendment (2026-09-29, see 0063):** 0063 removes Codex main sessions again, so the 0045 block's
exclusion of that topology applies again; a Codex gating reviewer is the fresh read-only CLI process
a Claude Code orchestrator dispatches. The version-line exemptions cover the two Claude manifests,
`.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, under the same byte/mode and
ordering checks; `reference/orchestrator.md`'s Merge and rebase proof section carries the operative
wording.

**Amendment (2026-10-04, see 0064):** The 2026-09-11 issue #332 block's default reviewer is superseded: the default is the fresh
read-only Codex CLI process; the human's instruction still selects another qualified executor.
`reference/orchestrator.md`'s Dispatching to an executor section carries the operative wording,
replacing the removed `reference/external-agent.md` pointer. Both ordered checks and the blocked
rather than lowered unavailable-reviewer rule remain unchanged.

**Amendment (2026-10-07, issue #478):** Gate 1's read-only property in the executor amendments is
authority toward the repository and its remote, not an OS read-only mode. CLI reviewers use
independent one-off pinned-head checkouts (Codex `workspace-write` with network); native Claude
inherits the session cwd and follows a no-file-write rule. The reviewer never comments, edits a PR
or issue, pushes or changes remote state; the caller publishes the verdict. The fresh-context
requirement, two checks and version-line exemptions are unchanged.

`reference/code-review-prompt.md` carries the repository/remote rule; `reference/orchestrator.md`'s
Dispatching to an executor section and `reference/harness-codex.md` carry the environment mechanics.
