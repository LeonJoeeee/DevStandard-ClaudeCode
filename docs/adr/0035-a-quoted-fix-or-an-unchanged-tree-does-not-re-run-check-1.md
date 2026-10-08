# 0035 — A verdict's own quoted fix, or a fix that never touches the tree, does not re-run check 1

Status: Accepted (2026-08-22). Amends 0011 (the reviewed-diff-is-the-merged-diff rule gains two
narrow, evidenced exceptions; both gates and their order are unchanged; rule 2 narrows the
Critical/Important-block-then-re-review semantic for findings that never touch the merged tree,
and only there — rule 1 never touches it). Amended by 0044 (2026-09-02). Amended by 0046 (2026-09-05). Amended (2026-09-07). Amended by 0056 (2026-09-11). Amended (2026-09-20). Amended by 0063 (2026-09-29). Amended (2026-10-08).

## Context

`core.md`'s rule is unconditional: any change to the diff after check 1 re-runs check 1, because
the reviewed diff must be the merged diff. Two situations expose a real cost in that rule that the
method has never separated from the risk it exists to prevent.

**Case 1 — the reviewer's own prescribed text.** PR #77's round 3 verdict cleared the PR with one
Minor and an exact replacement sentence quoted in the verdict itself. The worker applied that
sentence verbatim — one line, in an ADR. The round-4 reviewer then died on an API session limit
before producing a verdict, which `core.md` counts as a failure, not a pass. The merging session
merged anyway, disclosed the exception rather than claiming a verdict it did not have, and could
re-run the mechanical half of round 4's brief itself (finding nothing) but not the judgement half
— whether the prescribed sentence reads coherently in its paragraph.

**#77's own quote would not qualify under the rule below, and that is deliberate, not an oversight
found late.** It was an inline code span inside a running-prose sentence, opening with an elision
mark spliced into an existing bullet — not a fix standing alone in its own fenced block. What made
it tolerable at the time was that the finding was a **Minor**, not that the quote was mechanically
reproducible; the rule that follows requires both, because reproducibility is what lets a later
reader verify the match without trusting an assertion, and #77's shape offers nothing to verify
against. The rule is stricter than the case that prompted writing it down.

**Case 2 — a finding against something outside the tree.** PR #85's round 3 returned *With fixes*
on one Important: the PR **description** still reported the pre-round-1 state, including three
clearings rounds 1 and 2 had already overturned. The reviewer prescribed exact replacement text and
said explicitly: *"Fix it with `gh pr edit` and merge; the diff needs no fourth review round, and I
would not spend one on it."* Applying it changed the description; `git diff` on the merged tree
before and after was empty. This is not case 1 — nothing in the merged tree changed at all, so
`core.md`'s reviewed-diff rule is not engaged in the first place. What actually blocks in this state
is the Critical/Important-findings-block-the-merge clause, and that clause is satisfied the moment
the finding — against the description — is fixed.

**Four design-challenge rounds on a combined spec covering both cases returned Survives-with-fixes,
Blocked, Blocked, Blocked** — each revision answered a round's findings by adding a mechanism, and
the mechanism generated the next round's findings. Round 4 recommended splitting delivery: state
what survived cleanly, decide the two remaining unsettled points here rather than in a fifth round
on the combined document.

**Decoupled from issue #83 on purpose.** #83 named the general question — what the method does
when check 1 itself cannot run — and was closed on the human's decision to remove the cause (a
subscription tier change eliminated the session-limit deaths that produced every instance). This
ADR's exception is **not conditioned on reviewer availability**: keying it to unavailability would
create the one incentive the whole design has to avoid — an agent that wants to skip a round
reaching for "the reviewer was unavailable" as the trigger. Because it is unconditioned, #83's
closure does not resolve it and this ADR does not depend on #83's cause being real or fixed.

**The abuse path, named because it decided the design.** "The reviewer suggested something like
this" is a short walk from "the reviewer prescribed exactly this." An exception keyed on the
implementer's own claim of verbatimness is self-certified — the same failure shape as issue #75's
instant-return doer. Both cases below are built so a later reader checks the claim from two SHAs,
never from an assertion.

## Decision

Two exceptions to *"the reviewed diff must be the merged diff"*, both narrow, both evidenced, both
independent of reviewer availability. Full text in `reference/code-review-prompt.md`; `core.md`
carries the trigger.

**1. Verbatim-quoted fix, on a verdict that already blocked nothing.** The verdict must be
**complete** (it states its verdict with its reasoning — a run that stopped partway does not
qualify) and its finding inventory must hold only Minors or none — the inventory governs, not the
Assessment's label: a verdict labelled *Yes* that in fact recorded an Important does not qualify; a
verdict labelled *With fixes* whose findings are all Minor does. A Minor's own **quoted** text
closes without a further round when applied byte-identical, with the diff containing nothing but the
quoted text of that verdict's Minors. **This never applies to a Critical or Important finding,
however exactly the reviewer's text matched what was applied** — those still fix, then re-review,
unchanged from 0011. Check 1's own prompt asks for *"how to fix"* on every finding, so a Critical
routinely arrives with quoted replacement text too; letting that close the loop without a fresh
review is precisely the bypass this design exists to prevent, which is why the gate is *"the verdict
blocked nothing"* and not *"the fix was quoted."* **"Quoted", not "prescribed":** a reviewer writing
*"and mirror it in Chinese"* with no Chinese text written out does not qualify, nor does text
embedded in running prose, nor does one of two candidates the implementer picks between — the fix
must stand alone, in its own fenced block — never a blockquote, whose stored `> ` marker the
comparison procedure below has no way to strip without judgement — typed out rather than gestured
at. Any adaptation, however small, voids the exception: the changes that need judgement are exactly
the ones that lose it. **The fix lands as a new commit, never an amend** — an amend orphans
`<verdict-SHA>`, the one endpoint a later reader needs. Evidence: both SHAs, and the diff showing
the applied text matches the quoted text — compared against the verdict's raw stored comment body,
never a rendered view, after stripping the common leading-whitespace prefix shared by every
**non-blank** (empty or whitespace-only counts as blank) line of the fenced block and nothing else,
which keeps a Markdown-significant blank line or a trailing hard-break intact rather than destroyed
by a looser comparison.

**2. Tree-unchanged fix.** A finding against something outside the merged tree — most commonly the
PR description — is closed by editing that artifact, whatever the finding's severity: `core.md`'s
reviewed-diff rule is not engaged at all, because the merged tree never moved. **Evidence: both
SHAs, and in a genuine case they are the same commit** — nothing in the repo was touched, so
`<verdict-SHA>` and `<post-fix-SHA>` are identical; if they differ, the exception does not apply,
whatever the tree diff between them shows. **Caveat, found in round 4: an amended commit message is
not covered** even though the tree's files are unchanged — it rewrites text the record-language
check reads, so it is a change to the record and re-runs check 1 like any other. Nor is a rebase, an
amend, a commit reorder, or a force-push that happens to leave the tree identical: those are exactly
the *"any rebase or amend"* `core.md` already forbids, and SHA equality is what rules them out — an
empty tree diff between two different SHAs does not.

**Neither exception is available because a reviewer is unavailable, slow, or expensive to
re-dispatch.** Availability is never the trigger for either — which is also why rule 1 requires a
*complete* verdict rather than however far a dying reviewer got. A finding described but not
quoted, a fix needing one word of judgement, a second file or line riding along, any doubt about
which case applies — re-runs check 1, whatever the size of the change.

Rejected: **(a) a single combined rule** — four challenge rounds on that shape each produced a new
finding from the previous round's fix; splitting into two independently-conditioned rules is what
stopped the cycle, because the two cases fail on different axes (case 1 on whether text was
adapted; case 2 on whether the tree moved at all) and a shared condition set kept licensing one
case's failure mode through the other's clause. **(b) keying the exception to reviewer
availability** — the incentive problem above; also makes the rule untestable by a later reader,
since "was the reviewer actually unavailable" is not something a diff can prove. **(c) folding case
2 under case 1's conditions** (treating a PR-description fix as a degenerate "quoted fix with an
empty tree diff") — case 1's conditions are about text-matching a quote; case 2 has no quote to
match against and is evidenced by tree identity instead, so forcing it through case 1's shape adds
a vacuous condition 1 is not designed to check.

## Consequences

`core.md` pays ~30 words for the trigger; the two rules in full live in
`reference/code-review-prompt.md`, read by the merging session at exactly the point it is deciding
whether a round is needed.

**What to watch:** whether "quoted" gets read loosely in practice — a reviewer who writes a long
prose description that happens to contain the right words embedded in it is not the same as a
reviewer who wrote out the replacement text as replacement text, and the line between them is a
judgement call the merging session has to make honestly, once, before either exception can apply at
all. If that line proves unworkable in practice, the fix is to tighten the definition of "quoted",
not to widen "adaptation" — loosening the latter is how this design failed four times before it
split.

The concrete cases behind this ADR — PR #77's round 4, PR #85's round 3 — are already merged and
are not reopened by this ADR; it is the rule the next such case gets, not a retroactive audit of
those two.

**Amendment (2026-09-02, see 0044):** under the new check-1 contract, exception 1 applies to a
Note's own quoted fix only when the Goal verdict is Yes and both Floor checks pass. It never applies
to a Goal-verdict ground or a Floor failure. Exception 2 still covers an artifact-only correction
that leaves the reviewed SHA unchanged. The byte-identical comparison, SHA evidence, new-commit
requirement, and availability-independent triggers remain unchanged; the operative wording stays in
`reference/code-review-prompt.md`.

**Amendment (2026-09-05, see 0046):** the approved option-A path permits prior acceptance after a conflict-free rebase only when every PR-changed path remains byte/mode-identical and CI passes on the current merged result. `reference/hard-edges.md` carries the guarded CLI and proof contract. This is distinct from an arbitrary unchanged tree or amended commit; failed proof returns to full review. The original quoted-Note and artifact-only exceptions remain as recorded, but the CLI conservatively requires full review for a changed head outside its rebase proof.

**Amendment (2026-09-07, issues #242 and #256):** the byte/mode-identical clause in the 0046 block
above carries one exemption — the two Claude manifest version lines, when both move in lockstep to
the value the reviewed head declared and that value sorts strictly above the one it replaces read as
a dotted numeric release. It changes nothing about this ADR's own two exceptions, which turn on a
quoted Note and an untouched tree rather than on a rebase. `reference/hard-edges.md` carries the
operative wording.

**Amendment (2026-09-11, see 0056):** the version-line exemption above now includes
`.codex-plugin/plugin.json` alongside the Claude manifests. All three must carry equal old and new
versions with only their declared version lines changed; the existing mode and rebase-ordering
checks remain. `reference/hard-edges.md` carries the operative predicate.

**Amendment (2026-09-20, issue #428):** the exceptions now live on
`reference/orchestrator.md`, in its Two narrow exceptions to re-running check 1 section, because the
actor is the merging session and not the reviewer. That replaces every live routing sentence above
naming `reference/code-review-prompt.md` as their full text or operative wording — the Decision's
*"Full text in `reference/code-review-prompt.md`"*, the Consequences sentence, and the 2026-09-02
block's closing clause. The review contract keeps one sentence saying whose call a changed head is
and where the cases are stated. Both exceptions, their conditions, their evidence and their
independence from reviewer availability are unchanged; this ADR carries the mechanics the shorter
statement points at.

**Amendment (2026-09-29, see 0063):** 0063 deletes `.codex-plugin/plugin.json`. The version-line
exemption covers the two Claude manifests' version lines; the mode and rebase-ordering checks are
unchanged. `reference/orchestrator.md`'s Merge and rebase proof section carries the operative
predicate.

**Amendment (2026-10-08, issue #507):** neither narrow exception applies to Floor-2 correction,
including an artifact-only correction that leaves the reviewed SHA unchanged. The failed verdict
remains permanently on the PR and an explicit boundary-restoration ruling admits only full review,
never reuse of acceptance. `reference/orchestrator.md`'s Review packets section states this boundary.
