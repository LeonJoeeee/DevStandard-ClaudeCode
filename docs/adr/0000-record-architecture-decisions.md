# 0000 — Record architecture decisions as ADRs

Status: Accepted (2026-06-10). Amended by 0013 (2026-07-09). Amended by 0013 (2026-08-04). Amended (2026-08-13). Amended (2026-10-07).

## Context

This project is developed with DevBook's own method (dogfooding). Multiple parallel sessions need to know *why* things were decided; otherwise the same debates recur, or someone builds against a direction that was already overturned.

## Decision

Significant decisions are recorded in `docs/adr/NNNN-kebab-title.md`, four-digit sequential numbering, never reused.

**What counts as significant (two axes; either one fires):** the decision touches top-level design (structure, interfaces, dependencies, a key quality goal), or it is costly to reverse. Skip-list: trivial single-person choices, temporary workarounds/spikes, and anything already covered by an existing ADR or the architecture doc. Litmus test: **would a future me, or a fresh-context agent, burn real cost re-deriving why this was chosen?** If not, no ADR.

**Changing a decision = supersede, never edit.** A new decision gets a new ADR stating "Supersedes NNNN"; the only permitted edit to the old ADR is flipping its status to "Superseded by MMMM". Only two statuses are used: Accepted and Superseded (a solo project needs no "Proposed").

## Consequences

Decisions carry a dated *why*; the cost is one page per major decision. Parallel sessions should scan the ADR directory before starting work.

**Amendment (2026-07-09, see 0013):** The supersede-only rule is relaxed — an accepted ADR may carry a dated `**Amendment (…):**` block (this is one) that appends without rewriting the body, for partial supersessions and factual corrections. ADR numbers are assigned at merge, not on parallel branches, to avoid silent collisions. See 0013.

**Amendment (2026-08-04, see 0013 as amended):** The numbering half of the block above no longer holds. Numbers are **not** assigned at merge: the writer claims the number when the ADR is written, after verifying it is free in every place one can already be claimed — the merged log, every remote branch, every open PR, and any reservation held in an open issue — and records that check in the PR description (`howto/adr.md`). The dated-amendment half of the 2026-07-09 block is untouched.

**Amendment (2026-08-13, caused by 0031):** the `howto/adr.md` named in the 2026-08-04 block above is
now `reference/adr.md`; `howto/` was merged into `reference/`. The verify-then-claim rule and the
record-it-in-the-PR-description duty are unchanged — only the address.

**Amendment (2026-10-07, see issue #500):** after PR #498, the numbering-rule pointer in the
2026-08-04 amendment, relocated on 2026-08-13, now names two sources. `reference/adr.md` carries
the general number-selection rule. This repository's root `CLAUDE.md`, under **ADRs in this
repo**, carries the four-place audit and the obligation to record the claimed number and what
was checked in the PR description.
