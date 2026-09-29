# 0046 — Guard the reviewed head and prove a content-unchanged rebase

Status: Accepted (2026-09-05). Amends 0011 and 0035 (rebase exception). Amended (2026-09-07). Amended by 0051 (2026-09-10). Amended by 0052 (2026-09-10). Amended by 0056 (2026-09-11). Amended (2026-09-13). Amended (2026-09-20). Amended by 0063 (2026-09-29).

## Context

The approved collaboration architecture assigns mechanical enforcement to the merge transition.
Blanket full review after every base advance produces repeated reviews of disjoint, unchanged work.
The human's option-A ruling on issue #179 selects two hard layers: a conflict-free replay with
byte-identical PR-changed paths, then green CI on the merged result. Issue #204 implements those
interfaces; its human sign-off is still required before merge.

## Decision

The orchestrator enters through `scripts/guard merge`: current default base, latest whole verdict
for the exact head, protection, and CI bound to both base and head. Prior acceptance may be reused
only with its recorded old base/head and both rebase layers. Conflicts and changed path bytes or
modes refuse to full review. The API merge pins the verified head; strict protection supplies the
server's current-base check. Architecture-level merges also require recorded human authorization.

The guard consumes #203's attempt/ruling comment format. Seven returned reviews trigger the
orchestrator-first ruling; there is no eighth round, and a ruling cannot waive the Floor.

Role hooks reject recognized worker merge/release/external operations and require authorization
for recognized orchestrator irreversibles. Match lists and an expiring command/head-bound comment
are proposed configurable defaults, not a settled human ruling. Their authority is default-branch
policy, not worker files. The exact interfaces and limitations live in `reference/hard-edges.md`.

The alternative actually rejected by the approved option-A ruling is blanket re-review for every
rebase. This implementation does not claim an arbitrary-shell capability boundary: hook trust,
unsupported tool paths and shared credentials remain visible limitations. The main session runs
live executor probes; the worker's constructed tests cannot establish native enforcement.

## Consequences

Unchanged work can retain acceptance without ignoring integration changes. Tests can reproduce
both proof and refusal without moving the caller's branch. Missing evidence refuses conservatively.
Installing the plugin does not provision a target repository's CI or protection; the human/main
session owns that provisioning and this repository's final sign-off. The shipped protection script
is inspectable and runnable, and the worker's live negative probe uses an unprotected throwaway
branch without changing main's settings.

**Amendment (2026-09-07, issues #242 and #256):** the Decision's "changed path bytes or modes refuse
to full review" has one exemption, added after the human's ruling that the version bump rides the
change PR. The two Claude manifest version lines read as no difference when both move in lockstep to
the same value. Where that exemption is what admits the comparison, the guard additionally requires
the new head to declare a bump against the reviewed head, and that value — read as a dotted numeric
release — to sort above both the reviewed head's and the replay's, so a lane cannot rebase past a
merged bump and then set the manifests back. Every other path still refuses.
`reference/hard-edges.md` carries the operative wording; the admitted pair rides the proof as
`version_bump`.

**Amendment (2026-09-07, issue #274):** the Decision's "Conflicts and changed path bytes or modes
refuse to full review" carries that exemption on its conflict clause too. The replay is what feeds
the comparison, so when the reviewed head and the new base bump from one base to different versions
git cannot auto-merge the two version lines; refusing there sent a rebase that moved only those
lines back to a full review round (PR #271). A replay conflict confined to the two manifest version
lines is now resolved to the new base's value and the replay continues, leaving every check above
to run unchanged — including the ordering check, which still measures the new head against the
version the new base merged. A conflict on any other path, or on any other line of either manifest,
still refuses to full review. `reference/hard-edges.md` carries the operative wording.

**Amendment (2026-09-07, issue #279):** the status line above read *"Accepted architecture
(2026-09-05); implementation defaults pending human sign-off on #204"* — a value outside the three
`reference/adr.md` admits, carrying a precondition that has since been met. It now reads `Accepted
(2026-09-05)`, and this block records what the retired half of it said. **The sign-off was given.**
The human approved the architecture-level change on 2026-09-06 and delegated the three proposed
defaults to the main session, which decided them as recorded on PR #223
(https://github.com/LeonJoeeee/devstandard/pull/223#issuecomment-5557327712); #204's implementation
merged as `0c82b76`. So the Decision's *"Match lists and an expiring command/head-bound comment are
proposed configurable defaults, not a settled human ruling"* is settled: the documented synonym match
set extended additively by default-branch policy, the whole `devstandard-authorization-v1` comment
form bound to repository, head, kind, command digest and expiry with `standing_release` filled from
the 2026-07-24 delegation, and the repository-scoped Codex role-hook trust bypass all ship in
`.github/devstandard-guards.json`. Their authority is still default-branch policy, never worker
files. Nothing in the architecture this ADR decided changes, and its stated limitations stand: hook
trust, unsupported tool paths and shared credentials remain visible limits, and no complete
capability-boundary claim is made. `reference/hard-edges.md` carries the operative wording.

**Amendment (2026-09-07, issue #293):** the Decision's *"Role hooks … require
authorization for recognized orchestrator irreversibles"* has one exception, and it is the only one.
A repository being founded has no policy file on its default branch, so it has no
`authorization_issue`, so no record can exist — and the push that would land that file is itself a
recognized irreversible. Read literally the sentence made a project seeded from these pages
permanently unable to become guarded: it could never take its first step. The guard therefore admits
an **orchestrator's** plain `git push` whose every destination is the default branch, and only while
that branch provably carries neither a policy file nor protection. Both conditions are the argument:
with no policy there is nothing to bypass, and with no protection there is nothing to replace; the
push that lands the policy file closes the door behind itself. Absence must be proven — an explicit
404, including a default branch with no commits — and any other read failure still refuses.
`--force`, `--delete`, `--mirror`, `--tags`, a wildcard refspec, another destination, another
command, and every other role keep their refusal. Applying protection is deliberately *not* in the
exception: by then the policy file exists, so the ordinary record is available and is what a new
project's human authorizes first. The Consequences' *"the human/main session owns that
provisioning"* is unchanged. `reference/hard-edges.md` carries the operative wording, under
*Founding a repository*.

**Amendment (2026-09-07, issue #293):** the Decision's *"CI bound to both base and
head"* names a check whose spelling is now a target's to choose. The guard reads the required
contexts from `required_checks` and the integration check's name from `merged_result_check`,
defaulting to `merged-result / {base} / {head}`; a name that drops either pin refuses, so renaming
can never unbind the check from the exact merge result. `reference/ci-pipelines.md`'s CI template
ships the job that reports it, which it did not before — the guard required a check no seeded
project produced.

**Amendment (2026-09-10, see 0051):** the Decision's *"Role hooks reject recognized worker
merge/release/external operations and require authorization for recognized orchestrator
irreversibles"* is replaced, and this ADR's own limitation sentence — *"This implementation does not
claim an arbitrary-shell capability boundary"* — is why. Recognition grew into a closed shell
grammar with a ten-family refusal table, a policy read from the remote default branch on every tool
call, an authorization record for every irreversible orchestrator command, and a retry layer for
the network faults that read caused. It cost seven review rounds and three releases over
2026-09-09/10, still refused ordinary research commands, and still admitted, by its own statement,
anything an interpreter or an obfuscation could spell. The human ruled on 2026-09-10 that a guard
which cannot be complete should guard only the ordinary case, with a rule simple enough to hold in
one's head, and accept the residual.

So: the hook reads the command's raw text — quotes, here-doc bodies and substitution bodies
included — and refuses on a short word list per role. **Unparseable syntax is never a reason to
refuse, for any role.** The policy is read from the local `origin/main` ref, so **nothing in the
hook refuses because of a network fault**. The orchestrator's `gh pr merge` and `git merge` still
refuse to `scripts/guard merge`, which keeps every mechanism the Decision above gives it: current
default base, the whole verdict for the exact head, protection, CI bound to both pins, the rebase
proof, and the architecture-level sign-off. Deleting a merged branch or worktree is routine teardown
and is admitted with no record; `tag` and `release` ride the repository's standing delegation read
from policy. **The head-bound authorization record on the authorization issue survives for exactly
one caller — an architecture-level `guard merge` — and is the only record left.**

Two consequences this block records rather than leaves implied. Obfuscation, an interpreter script,
a forged local ref and an operation read from runtime data are outside the hook by design, and no
rule will be added for them; a review finding of that class is a Note. And `guard protection
--apply` is no longer gated by the hook at all — it stays the human's or the main session's by role
instruction and by who holds admin credentials. Nothing in the merge, rebase-proof or round-
accounting half of this ADR changes. `reference/hard-edges.md` carries the operative wording.

**Amendment (2026-09-10, see 0051):** the 2026-09-07 founding-push block above admits that push
*"only while that branch provably carries neither a policy file nor protection."* The protection
half is dropped: proving a branch unprotected required a GitHub read inside a tool call, which the
ruling above removes, and it was never the layer that mattered — GitHub's own branch protection
rejects the push server-side. The admission is now an orchestrator's push naming the default branch
while the local `origin/main` ref carries no `.github/devstandard-guards.json`, and the push that
lands that file still closes the door behind itself. Its refspec carve-outs go too: that block's
*"`--force`, `--delete`, `--mirror`, `--tags`, a wildcard refspec … keep their refusal"* named
options the orchestrator's word list no longer carries anywhere, guarded or not, so keeping them
here alone would be the grammar growing back inside the exception. The other clauses — the
orchestrator only, every other role refused, and the door closing — stand.

**Amendment (2026-09-10, see 0052):** the Decision's *"Architecture-level merges also require
recorded human authorization"* keeps its requirement and loses its record. There is no
`devstandard-authorization-v1` comment, no authorization issue and no `human_logins` allowlist:
`guard merge` requires **one comment of the repository owner's own on that PR**, the owner read from
the repository's API record, and any comment that is not one of the records this method publishes
there counts. The 2026-09-07 sign-off block above records that the match/authorization defaults were
settled and shipped in `.github/devstandard-guards.json`; **that file no longer exists.** It was
deleted whole — `required_checks`, `merged_result_check`, `record_logins`, `human_logins`,
`authorization_issue`, `standing_release`, `merge_method`, `command_patterns`,
`codex_role_hook_trust_bypass` — with every rule that existed to read it, so the 2026-09-07 block's
*"Their authority is still default-branch policy, never worker files"* now has no subject. The
Decision's *"CI bound to both base and head"* keeps its meaning under the fixed name
`merged-result / {base} / {head}`, which a target can no longer rename, plus the requirement that
every other check the head reports be green. `reference/hard-edges.md` carries the operative
wording.

**Amendment (2026-09-10, see 0052):** the 2026-09-07 founding-push block above, as narrowed by the
first 2026-09-10 block, is **retired outright**. Its remaining condition — *"only while that branch
carries no policy file"* — named a file that no longer exists, and the orchestrator's word list no
longer carries `push` at all, so there is nothing left to except. An orchestrator's push naming the
default branch is admitted with no rule, no condition and no proof to obtain; GitHub's own branch
protection, applied as the last founding step, is what ends it. The block's argument stands as
history and its mechanism is gone.

**Amendment (2026-09-11, see 0056):** the version-line exemption above now includes
`.codex-plugin/plugin.json` alongside the Claude manifests. All three must carry equal old and new
versions with only their declared version lines changed; the existing mode and rebase-ordering
checks remain. `reference/hard-edges.md` carries the operative predicate.

**Amendment (2026-09-13, issue #361):** the Decision's architecture-level human-authorization
precondition and every later owner-comment form of it are retired. No incident showed this extra
machine gate preventing an unauthorized integration, and an agent using the owner's shared
credentials could satisfy it alone. The architecture-level declaration remains review input, while
`core.md` and `reference/orchestrator.md` retain the human wait as a role obligation. The reviewed-
head verdict, current-base and ancestry checks, protection, merge-queue refusal, merged-result CI,
rebase proof and head-SHA precondition are unchanged.

**Amendment (2026-09-20, issue #426):** the first 2026-09-10 block's *"plus the requirement that
every other check the head reports be green"* narrows to: no check the head reports may have
failed. The `merged-result / {base} / {head}` check must still be `success` and a head reporting no
check at all still refuses — silence is never green — but a pending or skipped check that nothing
requires no longer blocks. It was the predicate #361 already deleted from the dispatcher, where an
unrelated queued run refused a ready head, and no incident showed it catching what the required
check did not. The merge path also stops reading the architecture-level flag, so the 2026-09-13
block's *"the architecture-level declaration remains review input"* is now the whole of it, supplied
to the reviewer through `review-packet --architecture-level`. Every other check the Decision names
is unchanged. `reference/orchestrator.md`'s Merge and rebase proof section carries the operative
wording.

**Amendment (2026-09-20, issue #435):** the word *protection* leaves the Decision's list of what
`scripts/guard merge` verifies, and with it the Decision's *"strict protection supplies the
server's current-base check"*, the first 2026-09-10 block's *"protection"* in the same list, and
the 2026-09-13 block's *"protection, merge-queue refusal"*. GitHub enforces strict up-to-date
checks, admin enforcement, the force-push and deletion bans and the merge queue server-side at the
merge itself, so reading them again at merge time could only convert an API hiccup into a refused
merge — it could never admit one GitHub would reject. **Nothing is dropped, only relocated:**
`guard protection` keeps every condition, including the merge-queue refusal 0011's 2026-09-07 block
records and the plan-limit carve-out, and it is now the only reader of the gate. No carve-out is
needed on the merge path, which makes no protection read at all. The reviewed-head verdict,
current-base and ancestry checks, merged-result CI, rebase proof and head-SHA precondition are
unchanged; the post-verification re-read narrows from the whole PR record to the PR head and base
SHAs, which is what the merge is pinned to. `reference/orchestrator.md`'s Branch protection section
carries the operative wording for the audit, and its Merge and rebase proof section for what the
merge verifies.

**Amendment (2026-09-20, issue #434):** the Decision's *"Seven returned reviews trigger the
orchestrator-first ruling; there is no eighth round"* keeps the orchestrator-first ruling and loses
the count as a gate. Nothing refuses on the number of returned rounds: `review-packet` counts them
and warns past seven, the guard's `review_history`, `round_check` and `merge_acceptance` stop
reading the count at all, and an eighth round with a continuation ruling is admitted like any
other. No record exists of the cap ever firing, and
#173 measured the real stop signal — findings of the same shape round after round, which the
reviewer's own non-convergence clause reports. Everything else the Decision states, including that
a ruling cannot waive the Floor, is unchanged. `reference/orchestrator.md`'s Review packets section
carries the operative wording.

**Amendment (2026-09-29, see 0063):** 0063 deletes `.codex-plugin/plugin.json`. The exemption covers
the two Claude manifests' version lines; the mode and rebase-ordering checks remain.
`reference/orchestrator.md`'s Merge and rebase proof section carries the operative predicate.
