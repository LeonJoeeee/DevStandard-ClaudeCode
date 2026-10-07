# 0064 — Codex is the default executor for the anchored roles; the method names Codex models and Claude tier aliases, never a cross-harness pairing

Status: Accepted (2026-10-04). Amends 0050 (its 2026-09-29 block's anchors, tier-equivalence basis, helper routing and arbitration fallback) and 0040 (its 2026-09-11 block's reversal of the executor preference). Also amends 0009, 0011, 0036, 0047 and 0060 (their live dispatch-default statements). Amended (2026-10-07).

**Scope: this ADR decides what the method ships.** It changes which executor is primary and what the pages assert about models.

## Context

The method carries two executor columns because the two harnesses take different arguments: Codex
takes a model id, the Claude Code Agent tool takes a tier alias. Until 2026-09-29 the pages also
asserted a pairing across them — "Claude `opus` and Codex `gpt-6-astra` are one tier" — so a reader
could translate between the columns.

On 2026-10-04 the human, on a host with no Claude models at all, ruled that the pairing goes and
that the anchored roles belong on Codex. Two observations drove it.

**Harness matching.** A GPT model run through Claude Code's subagent harness carries a mismatch for
no gain — that harness's tool surface, prompts and effort knobs are not what the model was built
for — while `codex exec` is its native harness. The reviewer's enforced read-only sandbox is
Codex-only; `scripts/dispatch` already refuses `--implementation claude-cli --purpose reviewer`
for lack of one.

**The pairing was never the method's to make.** "Claude `opus` and Codex `gpt-6-astra` are one
tier" states a fact about two models. `opus` is a tier alias, and the host's environment decides
which model it names. On a host where `opus` resolves to a non-Anthropic model the sentence is
false, and the method has no way to know. What the Agent tool accepts — `opus`, `sonnet`, `haiku`,
`fable` — is a harness interface; what those names resolve to is not the method's business.

The 2026-10-06 ruling raises the anchored efforts, makes the helper middle row the closing
default, updates its Codex settings, and adds a Claude quota fallback for arbitration.

## Decision

1. `scripts/dispatch` and `scripts/review-packet` default to `codex`. The human's instruction still
   selects another executor for one dispatch or standing. **When it is not there** still governs a
   missing, unauthenticated or erroring Codex, and a gate with no executor preserving its properties
   stays blocked, never lowered.
2. The worker and the reviewer are anchored on Codex `gpt-6.1-sol` at `xhigh` — one model for both.
   The Claude column takes `opus` at `max`.
3. The pages state the Codex tier order (`gpt-6-astra` above `gpt-6.1-sol` above `gpt-6-sol`;
   `gpt-6-luna` cheapest) and state that the Claude Code side names only a tier alias the host
   resolves. **No sentence asserts that a Claude tier and a Codex model are the same capability.**
4. A helper whose conclusion directly decides a merge or a design takes Codex `gpt-6-astra` at
   `max`; mechanical work keeps `gpt-6-luna` at `max`. The middle row is **the default — everything
   else**, Codex `gpt-6.1-sol` at `high`, including demanding work that decides neither. The Claude
   helper column stays byte-unchanged: `opus`, `sonnet`, `sonnet`; effort inherits the caller's.

Arbitration keeps Codex `gpt-6-astra` at `max`, fresh and read-only. When Codex is out of quota it
falls back to the built-in Claude `fable` at `max`, with that effort inherited from the session;
this adds no arbitration tier and preserves the fresh, independent, read-only contract and durable
answer publication. `gpt-6-astra` is the top Codex tier and keeps arbitration and the
decision-critical helper row.

Rejected: **(a)** reword the pairing to `opus` ≈ `gpt-6.1-sol` — still a claim about models the
method does not host; **(b)** drop the Claude column — the Agent tool requires a tier alias, so the
Claude path cannot be expressed without one; **(c)** put full model ids in the Claude column —
0024's "tier aliases, never version ids" stands, and a full id is version-pinned prose; **(d)**
collapse the anchored roles onto the host's cheapest model and keep a tier ladder for helpers —
the human wants one model for both anchored roles and retained distinct settings for helpers whose
conclusions decide a merge or a design and for mechanical helpers.

## Consequences

A reader can no longer translate between the two columns by tier; they read the column their
executor takes. That is the point — the translation was never the method's to make. The anchored
roles run on the executor that gives the reviewer a real sandbox and the worker a native harness.

A target project without Codex now passes `--implementation claude` explicitly rather than getting
it by default. **When it is not there** already covers Codex missing entirely; the change is which
path is tried first, not what happens when the first path is absent.

A future re-route of the anchored model is one table cell per role in `reference/orchestrator.md`
plus an amendment here. No pairing sentence is left to keep in sync, which is the maintenance
saving this ADR buys.

**Amendment (2026-10-07, issue #478):** The Context's enforced-read-only-sandbox rationale records
the old implementation, not a remaining executor distinction. Codex and Claude CLI reviewers now use
independent disposable pinned-head checkouts; Codex runs `workspace-write` with network. Native
Claude keeps the session cwd under the written no-file-write rule. Reviewer read-only means
authority toward the repository and its remote, with verdict publication owned by the caller. The
anchored settings, executor preference, helper routing and arbitration decision are unchanged.

`reference/code-review-prompt.md` carries the repository/remote rule; `reference/orchestrator.md`'s
Dispatching to an executor section and `reference/harness-codex.md` carry the environment mechanics.
