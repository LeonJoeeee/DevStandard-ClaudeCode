# When CI cannot run at all (the check-2 fallback)

Your role page makes green CI on the merged result check 2 because it is automated, impartial, and doesn't grade its own work. A local run gives up all three — same machine, same environment, run by an interested party — so what follows is a declared, evidenced, temporary degradation, never a second lane.

## First: the answer is almost always to wait

An outage is measured in hours; a minutes quota resets on a known date. **Waiting keeps check 2 intact and costs a delay — the fallback costs a full local run, a published evidence block, a reviewer's audit, and a return sweep, and still ends with an unverified merge.** Almost no merge is worth that trade. Everything below applies only once you can say *why* waiting was ruled out.

Take that seriously even when the outage is real and the trigger below genuinely fires: **declining this page and waiting is still usually the right call.** Recognising the trigger and refusing it is a correct outcome, not a failure to act.

**The trigger is the platform, not your patience and not your repo** — two halves, both required: the cause is **outside this repo**, *and* it stops the platform producing a run **for any push**. Not both → this page does not apply. In practice that is exactly two situations, and both can be proved: the Actions minutes quota is exhausted (private repos only), or GitHub is down (check the public status page, or the self-hosted instance's own admin or incident channel; the two-part test is unchanged). Prove it, and tell the human — removing the cause is theirs. ("Would pushing again produce a run?" settles nothing: pushing to a broken workflow also produces nothing. Ask the two halves.)

Every row below fails one half or the other. That is the whole reason each is excluded, so the table gives the routing rather than repeating it.

| Not a trigger | Where it goes instead |
|---|---|
| slow, queued, or flaky CI; the session nearly over | wait — a queued run *is* a run (`queued` precedes `in_progress`) |
| self-hosted runner offline — platform up, run queued | tell the human to check or restart the runner (`reference/ci-pipelines.md` — with ephemeral runners an empty runner list is the idle state; a job `queued` past five minutes with the list still empty is the loop being down) |
| red CI — a run that started and failed is CI working | branch → fix the branch; main → `reference/orchestrator.md`'s red-main recovery; the pipeline aged → `reference/ci-pipelines.md` |
| no run because of this repo: invalid workflow YAML, the workflow disabled in the Actions tab, `on:` filters no longer matching | fix it in a PR — CI is back in minutes |
| Actions switched off at the org level — outside this repo, but not a platform event | the human's or an org admin's to lift; the merge waits |
| the repo has no CI at all — no check 2 to degrade | settle CI as a task and use the template from `reference/ci-pipelines.md` |
| you cannot tell: no `gh` auth, no network, an unreadable Actions tab | establish the state, or wait — an unproven outage is not an outage |

A job that never starts for billing reasons is not a red run — that is the quota case above. **Reaching for the local suite in any row is the self-grading bypass this rule exists to prevent.**

**Who runs it, and on what tree.** The merging main session — never the worker, never a helper — and never the branch as pushed. Fetch the current base and PR head, materialise their exact merge as a synthetic two-parent commit, and check that commit out in a disposable worktree:

    set -e
    REPO_ROOT=$(git rev-parse --show-toplevel)
    git fetch origin main
    BASE_SHA=$(git rev-parse FETCH_HEAD)
    git fetch origin "pull/<PR>/head"
    HEAD_SHA=$(git rev-parse FETCH_HEAD)
    MERGE_TREE=$(git merge-tree --write-tree "$BASE_SHA" "$HEAD_SHA")
    MERGE_COMMIT=$(printf 'CI fallback: merge %s into %s\n' "$HEAD_SHA" "$BASE_SHA" |
      git -c user.name=CI-Fallback -c user.email=ci-fallback@invalid \
        commit-tree "$MERGE_TREE" -p "$BASE_SHA" -p "$HEAD_SHA")
    FALLBACK_CHECKOUT=
    cleanup() {
      cd "$REPO_ROOT" || true
      git worktree remove --force "$FALLBACK_CHECKOUT" 2>/dev/null || true
      rm -rf "$FALLBACK_ROOT"
    }
    FALLBACK_ROOT=$(mktemp -d)
    trap cleanup EXIT
    trap 'exit 129' HUP
    trap 'exit 130' INT
    trap 'exit 143' TERM
    FALLBACK_CHECKOUT="$FALLBACK_ROOT/checkout"
    git worktree add --detach "$FALLBACK_CHECKOUT" "$MERGE_COMMIT"
    cd "$FALLBACK_CHECKOUT"

Run every job CI would have run from that worktree, unfiltered and to completion (not just the tests the change touches). The traps return to the stable repository root and remove both the registered worktree and its temporary root on success, failure, HUP, INT, or TERM. Record the synthetic commit and tree identities with the command shown in the evidence template; base/head labels plus a clean checkout are not proof of the merge tree. Any rebase or head move invalidates the materialisation and the run. This keeps two of CI's three properties: the merged state against current main, and a run nobody can quietly skip. Impartiality is the one genuinely lost, which is why the run is published and audited instead of self-certified — including when the merging session wrote the diff itself, the ordinary case for a main-session short-branch fix. A worker's own done-check evidence is never check 2, whatever it ran.

**A partial run is never check 2.** If a job can't run locally — it needs secrets, a live service, another OS, a GPU — you have no fallback for that job. Wait for the platform, make the job runnable (a seeded fixture, a container, a documented local mode, in its own PR), or take it to the human. Never merge on the subset that happened to be runnable and call it evidence.

**Unblocking a protected main is the human's call, not yours.** With the required check never reporting, the PR sits at "Expected — waiting for status to be reported" and the merge button is dead — for admins too, because "Do not allow bypassing" is on. Do NOT drop the required check, untick the bypass setting, edit the ruleset, or push to main directly. Name the PR to the human and ask; the human either removes the cause (top up minutes, make the repo public) or waives the check, and protection is restored in the same session the merge lands. An agent that switches the gate off to get past it has done more damage than the unverified merge. Where protection doesn't apply (free-plan private repos) the gate is convention-only — the same evidence and the same audit are owed all the same. `reference/orchestrator.md`'s Branch protection section owns how the guard recognizes GitHub's plan-limit response and records the unavailable server-side gate.

**Evidence first, then check 1.** As with ordinary green-PR admission, evidence precedes review. Under the fallback, run the suite and post the evidence *before* check 1, and hand that comment to the reviewer with the diff — an impartial clean reader auditing the run is the closest available substitute for an impartial runner. If check 1 sends the diff back, or the rebase moves, redo the run: the last evidence on the PR must come from the tree that actually merged.

**Post this with it.** The reviewer is a clean context with repository and network reads. The
checklist still travels with the evidence so the audit's required context does not depend on a
later file or link — in the same PR comment as the `CI-FALLBACK` block below. Commission the review
with `scripts/review-packet start --ci-fallback <that comment's URL>`, and the assembler carries
the whole comment into the CI-fallback placeholder of `reference/code-review-prompt.md`, which
otherwise reads `NONE`:

    Audit the CI-fallback evidence above against all four items:
    - Is the stated cause outside this repo (minutes exhausted, platform
      outage) and proven — not "slow", "queued", "flaky", "red", or anything
      this repo or its org could fix?
    - Do the merging session's timestamped fetch/ref captures identify the
      current remote main tip and PR head, matching the published base/head
      and this packet's pins? Does its successful merge-tree capture use
      those exact SHAs and produce the published tree? Does the captured
      checkout identity show a commit whose first parent is that base,
      second parent is that head, and tree is that captured merge tree?
      Compare the supplied captures; do not execute commands. Missing or
      inconsistent captures cannot establish that the run tested their merge.
    - Is the run fresh (a UTC timestamp) and tracked state clean before it
      (`git diff --quiet` and `git diff --cached --quiet`)? Are permitted
      untracked inputs enumerated—only paths already on the pre-run baseline
      and named by the worktree copy-list, never an invented fixture? Do
      before/after `git status --porcelain -uall` snapshots match? Is every
      ignored input the run depends on named?
    - Is every CI job covered, unfiltered, with commands and exit codes shown?

**What goes on the PR**, in that same comment before the merge, so GitHub alone reconstructs why this change merged without a CI run. Keep the `CI-FALLBACK` marker literal — the return sweep searches for it:

    CI-FALLBACK (check 2 degraded)
    Reason: minutes quota exhausted | provider outage
            + proof (billing/usage page or `gh api` output; status-page incident id)
    Merged state: base <SHA> = current remote main tip; head <SHA> = this PR's head
    Materialised merge: commit <SHA>; tree <TREE-ID>
    Run at: <UTC timestamp>
    Runner: main session — <OS, toolchain versions>
    Captured at: <UTC timestamp; fresh for this review's base/head>
    $ git fetch origin main              -> exit 0
    $ git rev-parse FETCH_HEAD            -> <base SHA>
    $ git fetch origin pull/<PR>/head     -> exit 0
    $ git rev-parse FETCH_HEAD            -> <head SHA>
    $ git merge-tree --write-tree <base SHA> <head SHA> -> exit 0
      <merge tree>
    $ git rev-parse HEAD HEAD^1 HEAD^2 'HEAD^{tree}'
      <synthetic merge commit>
      <base>
      <head>
      <tree>
    $ git diff --quiet                    -> exit 0
    $ git diff --cached --quiet           -> exit 0
    Permitted untracked inputs: <baseline + copy-list paths, or NONE>
    Ignored inputs used by the run: <paths, or NONE>
    $ git status --porcelain -uall (before) -> <snapshot>
    $ <command>          -> exit <code>
    <output tail>
    (one block per CI job; every job covered, none skipped or filtered)
    $ git status --porcelain -uall (after)  -> <identical snapshot>

**No releases under the fallback.** The release pipeline is a workflow too: pushing `vX.Y.Z` while runs are impossible publishes nothing and leaves a tag that looks shipped. Hold the release until the return, then tag.

**Main is unverified, not red.** Dispatch continues — the stop-the-line rule answers a failing run, and there is no run. What ends the uncertainty is the sweep, not a pause.

**The return path.** The fallback ends the moment a push can produce a run again — no grace period, no standing "fallback mode"; the next merge is back on check 2. Re-verification is free: `main`'s first CI run after the return covers every commit merged under the fallback at once. Green closes them — nothing is re-reviewed. Red makes them the prime suspects: search closed PRs for `CI-FALLBACK` to get the list, and the red-main rule applies as written (revert first; fix forward only when the fix is obvious and takes minutes). Don't let that first run wait for the next task — when minutes reset or the outage clears, trigger a run on `main` yourself, and confirm protection is back on.

**If the fallback fires more than occasionally, the pipeline is the bug, not the gate** — see the minutes paragraph in `reference/ci-pipelines.md`.
