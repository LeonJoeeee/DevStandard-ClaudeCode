# How to write ADRs

Read this at project start (to seed the log) and whenever a significant decision lands. An ADR records **one decision and its why**, dated, one page — so no future session burns cost re-deriving "why was it done this way".

## When to write one (and when not)

The admission test is **cost of change**, on two axes — either one fires:
- the decision **touches top-level design** (structure, interfaces, dependencies, a key quality goal), or its effects scatter across the codebase instead of staying local to one component; or
- it is **costly to reverse**.

Skip: trivial single-person choices, temporary workarounds/spikes, anything already covered by an existing ADR or the architecture doc. Litmus test: *would a future session burn real cost re-deriving why this was chosen?* No → no ADR. A log that records everything protects nothing: if every decision is architectural, no decision is architectural.

ADRs are the natural by-product of asking the human: when a change gets the human's approval because it touches top-level design, that approval gets an ADR in the same merge.

## Mechanics

Write the ADR at decision time from the actual discussion; if the real alternatives considered cannot be recalled, say so rather than inventing plausible ones.

- Files by default: `docs/adr/NNNN-kebab-title.md` — or the established location an adopted repository uses — four digits, sequential, zero-padded, never reused. Seed the log at project start with `0000-record-architecture-decisions.md` (the ADR saying this project uses ADRs, containing the trigger rules above).
- **Claim the number when you write the ADR: the next above the highest claimed anywhere, never the lowest free** — checking *unmerged* work too, since an open branch, an open PR, or an issue that reserved one holds a number before it exists in the tree; record in the PR description which number you took and what you checked it against, so check 1 can verify the claim.
- **Supersede, never edit — but dated amendments are legal.** A changed decision = a NEW ADR stating "Supersedes NNNN"; the old one's status flips to "Superseded by MMMM". Original text is never rewritten. For a *partial* supersession (the core call stands, one detail was overtaken) or a *factual correction*, append a dated block instead, leaving the body immutable: `**Amendment (YYYY-MM-DD, see NNNN):** …` when an ADR amends this one, and otherwise `**Amendment (YYYY-MM-DD, <what caused it>):** …` — or `**Amendment (YYYY-MM-DD):** …` with nothing to cite.
- Statuses: `Accepted`, `Superseded by NNNN`, and `Amended by NNNN` (which sits alongside Accepted). The new ADR carries `Supersedes NNNN` or `Amends NNNN (<what it amends>)` in its own status line.
- When appending an amendment, use `.github/check-adr-index.py` for its status-line announcement and citation pairing.
- One decision per file — separate files keep parallel sessions conflict-free and let agents read only what's relevant (`ls <decision-log-path>` is the index; filenames carry the summary).

## Template

```markdown
# NNNN — <decision in one line>

Status: Accepted (<date>)

## Context
<the situation and forces; what made this a real decision>

## Decision
<what was decided, concretely. If real alternatives existed,
one line each on what was rejected and why>

## Consequences
<what gets better, what it costs, what to watch>
```

Lands in the target repo under `docs/adr/` by default; an adopted repository's established convention
may supply another location, which `docs/architecture.md` declares (`reference/in-repo-writes.md`).
