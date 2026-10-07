# 0025 — Check 2 falls back to a declared local run only when the platform can produce no run

Status: Accepted (2026-08-02). Amends 0011 (check 2's availability, and gate order under
the fallback only; the two gates themselves, the reviewed-diff-is-the-merged-diff rule,
and the deterministic-last-word principle stand). Amended by 0032 (2026-08-13). Amended
(2026-09-01). Amended (2026-09-07). Amended (2026-09-20). Amended (2026-10-07).

## Context

0011 made green CI on the merged result the final word precisely because it is automated,
impartial, and does not grade its own work — and it assumed CI can always run. On private
repos GitHub Actions minutes are a finite monthly quota, and an exhausted balance stops
every workflow: the gate is not red, it is absent. A provider outage produces the same
state. With no rule, an agent facing an absent gate has two bad options — block every merge
until billing resets, or invent a bypass on the spot. The invented one is always "I ran the
tests locally", which surrenders all three properties at once: same machine, same
environment, run by the party with an interest in green.

The failure to design against is not the honest quota case; it is the fallback becoming the
path of least resistance wherever CI is merely slow, queued or annoying, the near-miss of
reading a RED run as "CI unavailable" (0020 already owns that path), and the case that
looks identical from the outside but is self-inflicted: a broken, disabled or mis-scoped
workflow, where "no run appeared" is a two-minute repo fix rather than a platform event.

One more state 0011 never contemplated: on a protected main the required check does not
merely go unreported — it holds the merge button shut, admins included, wherever "Do not
allow bypassing" is set. A rule that authorises the merge without saying who may unblock it
invites the worst available outcome, an agent disabling the gate to satisfy the page that
told it to merge.

## Decision

Check 2 gets exactly one fallback, framed as a degradation rather than an alternative.

**Trigger — the platform, not patience and not this repo.** It fires only when the platform
produces no run for any push, and only for two named causes: Actions minutes exhausted
(private repos), or a provider outage. The trigger is keyed to the cause, not the effect,
and deliberately so — "no run appeared" admits org-level disablement and a repo with no CI,
both of which this ADR excludes by name, so an effect-keyed rule would authorise on the
force-read page what it rejects here. Slow, queued, flaky and RED are never triggers — a
run that starts and fails is CI working, though a job that never starts for billing reasons
is the quota case rather than a red one. Repo-side silence (invalid workflow YAML, a
disabled workflow, `on:` filters that no longer match) is a bug to fix, not a trigger, and
is settled by asking *is the cause outside this repo?* rather than "would pushing again
produce a run?"; Actions switched off at the org level is outside this repo yet still not a
platform event — the human's or org admin's to lift, and the merge waits. If the state
cannot be established at all, CI can run — an unproven outage is not an outage.

**A repo with no CI is out of scope.** It has no check 2 to degrade and no platform event
that could end a fallback; the human's light-start declaration governs, or CI gets set up.

**Runner and tree.** The merging main session, never the worker, on the merge result built
locally against current `main`, running every job CI would have run, unfiltered — a partial
run is not check 2. This keeps two of CI's three properties: the merged state against
current main, and a run nobody can quietly skip. Impartiality is the one genuinely lost —
including when the merging session wrote the diff, the ordinary case for a main-session
short-branch fix — which is why the run is published rather than self-certified.

**Evidence, and the order flips.** The proven reason, the merged SHAs, the environment, and
the commands with exit codes and output are posted to the PR before the merge under a
literal `CI-FALLBACK` marker, and that comment goes to the check-1 reviewer with the diff.
An impartial clean reader auditing the run is the closest available substitute for an
impartial runner, and it keeps "why did this merge without CI" reconstructable from GitHub
alone. This is the one case where gate 2's evidence precedes gate 1.

**Unblocking is the human's act.** An agent never removes a required check, never unticks
the bypass ban, never edits a ruleset, and never pushes to main to get past a stuck gate.
It names the PR to the human, who removes the cause or waives the check; protection is
restored in the same session the merge lands. No release ships under the fallback — a tag
push is a workflow too, and would leave a tag that looks shipped.

**Return.** The fallback ends at the first push that can produce a run — no grace period.
Re-verification is `main`'s first CI run after the return, covering every fallback-merged
commit at once: green closes them; red makes them the prime suspects (search
`CI-FALLBACK`) under the ordinary red-main rule.

Rejected: (a) block all merges until quota returns — turns a billing event into a project
stop and pressures agents into an unwritten bypass anyway; (b) accept the author's or
worker's done-check evidence as check 2 — exactly the self-graded finish 0011 forbids;
(c) "the merging session, never the author" — unsatisfiable for main-session short-branch
work under 0022, where merger and author are the same session, so the rule bans the runner
it prescribes; impartiality is delegated to check 1's audit instead; (d) have the check-1
reviewer run the suite — it re-merges the layers 0011 separated, and a clean reviewer has
no tree to run on; (e) counting "no CI in this repo yet" as a trigger — it makes a
"temporary" degradation permanent, since no platform event can end it; (f) keeping the rule
in howto/cicd.md only — the gate is stated in the force-read page, so its one exception must
be there too, or every session re-derives it differently; (g) a time or PR-count expiry —
arbitrary and unenforceable, where "a run became possible" is objective and the return
sweep already bounds the exposure.

## Consequences

core.md pays ~154 tokens (total ~4,183 of 5,000) for the two named causes, the non-triggers,
the runner, the evidence handed to check 1, the protected-main rule, the no-release rule and
the return; `howto/cicd.md` carries the operational detail — the outside-this-repo test, the
repo-side-silence, org-level and no-CI cases, the billing-job discriminator, the partial-run
ban, the comment template, the branch-protection mechanics and the return sweep — plus a
minutes-as-symptom paragraph beside artifact hygiene, since exhausted minutes usually mean a
pipeline spending more than it needs, and the self-hosted runner as the non-degrading way
out when minutes rather than the platform are the constraint.
`aids/code-review-prompt.md` gains a CI-FALLBACK audit item and an evidence placeholder,
since the reviewer becomes the only impartial party in the chain; `aids/worker-brief.md`
gains an explicit ban on merging under an unavailable CI or offering a local run as check 2,
because a worker never reads core.md; `docs/architecture.md` §4 carries the qualifier, being
the baseline every worker reads. What to watch: fallback frequency — more than occasional
use means the pipeline's spend, not the gate, is the bug — marker discipline, since the
return sweep is only as good as `CI-FALLBACK` being searchable, and any protection change
made under fallback pressure, which check 1 is now told to flag.

**Amendment (2026-08-13, see 0032):** of the five sites this ADR's family came to occupy, exactly
one is narrowed — `reference/code-review-prompt.md`. **The fallback rule itself, its trigger, its
non-triggers and its evidence template are unchanged**, and `reference/worker-brief.md`, `core.md`
and `reference/ci-pipelines.md` are not narrowed. In `reference/code-review-prompt.md` the CI-FALLBACK audit item stood unconditional
in a prompt pasted at *every* merge, two lines below a placeholder that reads `NONE` on essentially
every review — 226 words charged to the 99% of merges where no fallback exists. The audit checklist
now lives in `reference/ci-cannot-run.md` and travels *with* the evidence: the merging session pastes
both into the placeholder, because the reviewer is a clean context and cannot open this plugin's
files. The prompt keeps a conditional item and the Critical-if-gapped rule, which is the trigger.
The reasoning above stands exactly — the reviewer *is* the only impartial party under the fallback,
and that is why the checklist still reaches it. `reference/worker-brief.md`'s ban is unchanged.
(`aids/` above is history: 0031 renamed the directory to `reference/` and split `cicd.md` four ways.)

**Amendment (2026-09-01, issue #169):** the Decision's evidence list was incomplete: naming the
base and head did not bind the local checkout to their merge. The operative identity proof and its
audit comparison now live in `reference/ci-cannot-run.md`; this ADR's trigger, authority, gate order,
and return path stand.

**Amendment (2026-09-07, issue #279):** the 2026-08-13 block's two live pointers to
`reference/worker-brief.md` — that it was **not** narrowed, and that *"its ban is unchanged"* —
now read `reference/worker.md` (#235 split the role sources; #270 deleted the compatibility pointer
the old page had become). The ban is on that page's Never list, in the same shape: never substitute
your local tests for check 2, never merge because CI is unavailable, never invent a CI fallback; and
the worker source adds that under an already-declared fallback the worker hands back final-state
evidence and says so, because running the fallback is solely the merging session's act. The fallback
rule, its trigger, its non-triggers, its evidence template and the narrowing of
`reference/code-review-prompt.md` are unchanged.

**Amendment (2026-09-20, issue #434):** the 2026-08-13 block's *"the merging session pastes both
into the placeholder"* becomes a commissioned assembly. The merging session posts the `CI-FALLBACK`
evidence and the audit checklist in one PR comment and passes that comment's URL to
`scripts/review-packet start --ci-fallback`, which carries the whole comment into the placeholder;
without the flag the placeholder still reads `NONE`. Until now the slot was hardwired to `NONE`, so
this ADR's fallback could not be commissioned through the assembler at all (#298 item 2). The
reason the checklist reaches the reviewer — it is the only impartial party under the fallback, and
it cannot open this file or follow a link — is unchanged, and so are the rule, its trigger, its
non-triggers and its evidence template. `reference/ci-cannot-run.md` carries the operative wording.

**Amendment (2026-10-07, issue #478):** The 2026-08-13 and 2026-09-20 blocks' assumption that the
reviewer cannot open files or follow links is retired: reviewers now have repository and network
reads. The checklist still travels with the CI-FALLBACK evidence in one published comment, so the
clean reader receives the complete audit context without relying on a later file or link. The
fallback's trigger, non-triggers, evidence template and audit semantics are unchanged;
`reference/ci-cannot-run.md` carries the operative wording.
