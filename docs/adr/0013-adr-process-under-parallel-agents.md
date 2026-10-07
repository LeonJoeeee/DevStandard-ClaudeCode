# 0013 — The ADR log survives parallel agents: dated amendments + merge-time numbering

Status: Accepted (2026-07-09). Amends 0000 (its supersede-never-edit rule and its
four-digit sequential numbering). Amended (2026-08-04). Amended (2026-08-13). Amended by 0033
(2026-08-13). Amended (2026-09-07). Amended (2026-10-07).

## Context

Two holes in the ADR house rules (0000, `howto/adr.md`) surface once real parallel agents write ADRs.

1. **"Supersede, never edit; the only permitted change is a status flip"** cannot express the two states a live log actually reaches: a *partial* supersession (the core call stands, one detail was overtaken) and a *post-hoc factual note* (a referenced file was later deleted). Forced to choose, an author either leaves an accepted ADR misleading — the exact "a future session burns cost re-deriving why" failure ADRs exist to prevent — or wholly supersedes it, falsely signalling the core decision died. The project's own tree already broke the rule (0006 and 0010 carry appended notes); that is diagnostic, not sloppy — the rule lacked the expressiveness, so the author routed around it.
2. **Sequential numbering** ("four digits, never reused") collides silently under parallelism: two branches each allocate the same next `NNNN`; different kebab titles let git merge both with no conflict, and "never reused" breaks with nothing to alert anyone.

## Decision

1. **Dated amendments are legal.** An accepted ADR may carry an appended, clearly-marked block — `**Amendment (YYYY-MM-DD, see NNNN):** …` — that never rewrites the original text. It records a partial supersession or a factual correction while the body stays immutable. Full supersession (a new ADR + status flip) remains the tool when the *whole* decision is replaced. A third status, `Amended by NNNN`, may sit alongside `Accepted` and `Superseded by NNNN`.
2. **Final ADR numbers are assigned at merge — main's act.** In-flight branches draft as `docs/adr/DRAFT-kebab-title.md`; whoever integrates at main renames to the next free `NNNN`. Numbering is allocated by the single integration point, never by parallel branches — consistent with "merging is main's act."

## Consequences

The append-only property the rule actually protects is preserved (originals are never rewritten); agents get a legal path to correct the record; parallel ADR-writing stops colliding. This ADR's first use is its own introduction — 0000 receives an amendment note pointing here, and the pre-existing notes on 0006/0010 are reformatted into the sanctioned block. Bootstrap note: this ADR and its siblings (0011–0015) were authored in one change and numbered directly, not via the `DRAFT-` path they introduce — the merge-time-numbering rule binds subsequent parallel work, not the change that establishes it. Cost: one more status value and one naming convention in `howto/adr.md`.

**Amendment (2026-08-04, see issue #78):** Decision 2 is replaced; decision 1 stands (this block is an instance of it). Merge-time numbering was never once practised: `git log --all --diff-filter=A -- 'docs/adr/DRAFT*'` returns nothing — no `DRAFT-` file has ever existed in this repo — and every ADR added after this one (0016–0026) was added already numbered, by a single-parent feature commit on its own branch, never by a merge commit renaming a draft. Where check 1 recorded its reasoning, it cleared the number after confirming it was free (PRs #23, #67, #72, #77). The rule the log actually runs on is **verify-then-claim**: the writer claims the number when the ADR is written, having checked every place a number can already be claimed — the merged log, every remote branch, every open PR, and any reservation held in an open issue — and records that check in the PR description. On a repo whose main session serialises dispatch, that is the same collision guarantee as merge-time renaming at a fraction of the ceremony — and a dead-letter rule is worse than either, because it quietly teaches that this log's conventions are optional. `howto/adr.md` carries the operative wording.

**Amendment (2026-08-13, caused by 0031):** in the 2026-08-04 amendment above, "`howto/adr.md` carries
the operative wording" now reads `reference/adr.md`; `howto/` was merged into `reference/`. The
wording it names is unchanged. The two earlier mentions of `howto/adr.md` are left as written, for
different reasons: the Consequences one ("Cost: one more … convention in `howto/adr.md`") is a
ledger of what this change touched; the Context one ("Two holes in the ADR house rules (0000,
`howto/adr.md`)") records the situation at decision time. A reader acts on neither.

**Amendment (2026-08-13, see 0033):** this ADR gave the amendment mechanism **one** block form and
**one** new status, and never said what a block that cites something *other* than an amending ADR
pairs with — so half the pairing was never stated and the correspondence could not be. Two sites
drifted for that reason before a pairing audit found them (issue #115). The rule is now explicit in
`reference/adr.md`: a block reading `(date, see NNNN)` pairs with `Amended by NNNN`, and **every
other citation** — a commit, an issue, a PR, or an ADR that merely *caused* the change — pairs with
`Amended (date)`; and **every block must appear in the status line**, because the status line is the
index a future session searches. `0019` had carried an amendment since 2026-07-24 that the index
never announced. This repository additionally enforces it as a CI gate — target projects get the
rule and check it however they check anything else. The mechanism this ADR decides is unchanged.

**Amendment (2026-09-07, issue #279):** the status line above gains `Amends 0000`, the form
`reference/adr.md` requires of an amending ADR (*"The new ADR carries `Supersedes NNNN` or `Amends
NNNN (<what it amends>)` in its own status line"*). 0000 has announced `Amended by 0013` since
2026-07-09 and again since 2026-08-04; only this side of the pair was missing, and
`.github/check-adr-index.py` cannot see it because it checks the amended ADR's side alone. The
decision is unchanged.

**Amendment (2026-10-07, see issue #500):** after PR #498, the numbering-rule pointer in the
2026-08-04 amendment, relocated on 2026-08-13, now names two sources. `reference/adr.md` carries
the general number-selection rule. This repository's root `CLAUDE.md`, under **ADRs in this
repo**, carries the four-place audit and the obligation to record the claimed number and what
was checked in the PR description.
