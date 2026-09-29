# 0019 — Deliver core.md by hook-forced first-action read, not full-text injection

Status: Accepted (2026-07-24). Amended by 0045 (2026-09-05). Amends 0007 (delivery mechanism only; the one-page shape and the token ceiling are unchanged). Amended (2026-07-24). Amended by 0038 (2026-08-26). Amended by 0039 (2026-08-26). Amended by 0049 (2026-09-07). Amended (2026-09-07). Amended by 0056 (2026-09-11). Amended by 0063 (2026-09-29).

## Context

Since 0007 the SessionStart hook delivered the method by **injecting core.md's full text** as `additionalContext`. That silently stopped working. Claude Code inline-caps hook `additionalContext` at **~10,000 bytes** (undocumented, hardcoded, no settings key or env var to change it, and it applies to every hook event): above the cap the harness persists the full text to a `.txt` file and injects only a **~2KB preview plus the file path**. core.md is now ~14 KB, so every session since ~v0.4.2 — when the page first crossed the cap — received a fragment: the trigger rule survived in the preview, the task flow, merge checks, worker rules, and safety rules sat behind a file the model was never told to open (issue #35, with the harness-cap research in its comments).

The CI token gate never caught this because it measures a **different axis**. 10KB of hook output is ~2,300 tokens by our `words×1.35` formula — far under the 5,000-token ceiling — so the byte cap binds long before the token ceiling ever could. A green token gate coexisted with a two-thirds-truncated delivery for months.

The reference is proven: the human's research project delivers 20–57KB orchestrator/executor playbooks reliably by having a SessionStart hook instruct a first-action read, in daily use since June 2026.

## Decision

The SessionStart hook stops embedding core.md. It emits a short imperative instruction (well under 1,500 bytes) — *MANDATORY FIRST ACTION, before responding to the user and before any other tool call: Read `<plugin_root>/core.md` IN FULL* — plus a `systemMessage` so the human sees the hook fire. The full page is delivered by the model reading the file, so its size no longer bounds delivery. hooks.json's matcher is unchanged (`startup|clear|compact`, resume still excluded — context is not lost on resume), so the instruction re-fires and the page is re-read exactly when context was compacted or cleared.

Options considered:

- **Trim core.md back under the cap** (target ≤ ~9KB) — rejected by the human: "短了它不够用" — the page needs its length to state the full collaboration model inline for clean-context workers (the reason 0007's ceiling was raised to 5,000 tokens in the first place). Trimming would also partly reverse that decision's intent.
- **Split injection across multiple SessionStart hook registrations** — undocumented whether the cap is per-registration, untested, and fragile across harness updates. Fallback only.
- **Forced first-action read (chosen)** — size-independent, and a pattern already proven in daily use in the human's research project.

A CI byte gate is added alongside the unchanged token gate: total hook output must stay **< 4,000 bytes** (a wide margin under the ~10KB cap), so delivery can never silently regress to a preview again — the regression gate the byte cap itself never gave us.

## Consequences

Delivery is no longer byte-bound: core.md can grow to whatever the method needs without the harness quietly truncating it. The **5,000-token ceiling (0007 as amended) stays** — no longer as a delivery limit but as the context-cost governor, since the model still pays to read the whole page every session. The scheme now **relies on model compliance** rather than a guaranteed inline paste — the persisted-file fallback disappears, because the instruction *is* the delivery. Mitigations: the imperative is unmistakable (a ⭐ FIRST ACTION header, "before any other tool call"), the `systemMessage` makes the hook visible to the human when it fires, and the matcher re-fires the instruction on every compaction/clear so a re-read follows a context loss. The hook now also reads stdin to surface the `source` subtype in the `systemMessage` (pure sed, no jq; `timeout` — absent by default on macOS — is used only for this stdin nicety, and its absence degrades to no source, never to broken output); it never blocks on a terminal and bad or absent stdin degrades to no source. See 0007 for the one-page shape and budget history this amends.

> **Amendment 2026-07-24 (issue #56):** the emitted wording dropped the MANDATORY-FIRST-ACTION exclusivity claim in favor of a composable form ("IN FULL before acting on the user's request / any substantive reply", plus a composition-blind yield rule). The forced-read delivery mechanism this ADR decides is unchanged.

**Amendment (2026-08-26, see 0038):** the SessionStart hook this ADR decided now *branches by
harness*: under Claude Code its behavior — the forced read of core.md described here — is
byte-identical and this ADR's reasoning is untouched; under Codex the same script delivers the
worker role instead (0038), and an unidentifiable harness gets a visible warning and nothing else.
Every sentence here describing what the hook emits is scoped to the Claude branch.

**Amendment (2026-08-26, see 0039):** the 0038-era block above is corrected — under Codex the
same script delivers the same forced read this ADR decided (core.md, plus the bounded mappings
page), not a worker role. Every sentence here describing the emitted instruction remains scoped to
the Claude branch byte-for-byte.

**Amendment (2026-09-05, see 0045):** The Codex branch described by the 0038/0039 amendments is removed. The Claude forced-read instruction, output budget, stdin handling, and hook matcher remain unchanged. Unsupported environments still receive a visible warning and no method read instruction.

**Amendment (2026-09-07, see 0049):** the delivery mechanism changes back, per artifact. Under the
human's delivery ruling on issue #179, direct injection is the default: the hook emits one output
per delivered artifact and inlines that artifact whole when its complete `additionalContext` fits
the cap it measures, keeping the forced read this ADR decided only for an artifact that does not fit
— and CI now fails that case rather than living in it. The diagnosis, the matcher (`startup|clear|compact`,
resume excluded), the stdin handling, and the unsupported-environment warning stand as written.

**Amendment (2026-09-07, issue #279):** the Decision's CI byte gate — *"total hook output must stay
**< 4,000 bytes**"* — is retired, and with it the 2026-09-05 block's re-affirmation of that "output
budget" as unchanged. Under 0049 the hook emits **one output per delivered artifact**, so a single
total is no longer the quantity to bound, and the 4,000-byte figure describes a shape the hook no
longer has. `.github/check-core-budget.py` enforces the replacement: a per-artifact byte budget for
`core.md`, and a per-artifact inline cap that every delivered artifact's complete `additionalContext`
must fit — the gate **fails** when one does not, rather than reporting an instructed read. This ADR
states no figure for either, because the current ones are the gate's to report; the measurement's
method and date are recorded once, in `docs/specs/2026-09-06-core-md-rule-ledger.md`. What the
retired gate existed to prevent is what the new one prevents, more strictly: delivery can still never
regress to a preview unnoticed, because an over-cap artifact is now a red check instead of a
degradation. The diagnosis, the matcher, the stdin handling and the unsupported-environment warning
stand as the 2026-09-07 (see 0049) block leaves them.

**Amendment (2026-09-11, see 0056):** The Codex-branch removal in the 0045 block is retired by 0056.
Both hosts receive the shared role artifacts under 0049's per-artifact inline rule. Their matcher
stays `startup|clear|compact`; only the Codex adapter adds resume, instructing reads of missing
shared sources. Hookless recovery is an explicit source-reading skill, not automatic delivery or
hook trust.

**Amendment (2026-09-29, see 0063):** 0063 removes the Codex SessionStart branch, with its cap,
handler set, adapter resume trigger and hookless-recovery skill. Only the Claude hook delivers the
role artifact, on `startup|clear|compact`; a Codex environment gets the unsupported-environment
warning.
