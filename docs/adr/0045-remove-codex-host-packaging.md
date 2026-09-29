# 0045 — Remove Codex host packaging; Codex is a dispatched executor

Status: Superseded by 0056 (2026-09-11). Originally Accepted (2026-09-05). Supersedes 0038 and 0039. Amends 0006, 0007, 0008, 0011,
0015, 0016, 0018, 0019, 0024, 0036, and 0040 (their live Codex host, delivery, and routing statements).
Amended (2026-09-07). Amended (2026-09-11). Amended by 0056 (2026-09-11). Amended (2026-09-12). Amended by 0063 (2026-09-29).

## Context

The human's ruling on issue #179, implemented by issue #200, selects one Claude Code
orchestrator with dispatched executors. Codex is used only as a CLI executor invoked by Claude
Code; the DevStandard Codex plugin was already uninstalled on both machines. Keeping its unused
packaging and forced per-worker read of `core.md` contradicts PRD §1.6's no-unused-structure
criterion and §5's separation of role context and delivery.

Architecture chapters 1, 3, 6, and 7 previously left the Codex host carriers unchanged without a
compatibility promise. Issue #200 rejects that alternative: the path is removed from scope.

## Decision

DevStandard ships as a Claude Code plugin only. Remove `.codex-plugin/`, the Codex delivery
branch of `hooks/session-start`, `reference/harness-codex.md`, and the Codex install/update and
hookless fallback instructions. The Claude hook retains its forced read, payload, stdin handling,
and matcher; unsupported environments retain a visible warning and receive no method instruction.
The former equal-valued compatibility aliases are unsupported, while Claude's environment with an
unrelated inherited `PLUGIN_DATA` keeps its existing behavior.

Codex remains a worker or reviewer process, with role constraints supplied by dispatch rather than
plugin startup. `reference/worker-brief.md` carries the necessary explicit operational-memory read,
craft-skill trigger, and scratch guidance. ADR 0040's executor preference and explicit standing
setting remain on `reference/external-agent.md`; Codex host orchestration is removed from scope.

## Consequences

The two Claude manifests stay in lockstep. CI retains the Claude hook and method budgets, verifies
unsupported-environment warnings and absent Codex host artifacts, and reconciles the old
manifest-description, fallback, and dual-footprint assertions. These are deliberately staled gate
assumptions under `reference/red-check.md`; the PR declares each for merge check 1.

Architecture chapters 1, 3, 6, 7, and the traceability table now describe removal. Dated amendments
reconcile live ADR instructions while preserving their original bodies and measured history.
Historical specs remain design records. This change does not implement the later role split,
inline-delivery choice, agent definitions, or dispatcher. Human architecture sign-off remains a
pre-merge duty of the main session.

**Amendment (2026-09-07, issue #279):** two of the Decision's live statements were overtaken by
0049, whose Amends list did not reach this ADR.

**The forced read is now the fallback, not a retained default.** *"The Claude hook retains its forced
read, payload, stdin handling, and matcher"* was true when this ADR removed the Codex branch. Under
0049 the SessionStart hook emits one output per delivered artifact and **inlines that artifact whole**
when its complete `additionalContext` fits the cap it measures; 0019's IN FULL read survives only for
an artifact that does not fit, and `.github/check-core-budget.py` fails that case rather than living
in it. The payload's stdin handling, the matcher, and the unsupported-environment warning stand
exactly as this ADR left them, as does the removal of the Codex delivery branch.

**The worker carrier is `reference/worker.md`.** *"`reference/worker-brief.md` carries the necessary
explicit operational-memory read, craft-skill trigger, and scratch guidance"* names a page #235
reduced to a compatibility pointer and #270 deleted. All three are on `reference/worker.md`: the
repo-root `CLAUDE.md` read **IN FULL**, stated to be explicit for Codex; the fenced worker-skill
bindings with their triggers; and the scratch rule — the harness's named location, or one dedicated
`mktemp -d` where it names none, with durable results published on the issue or PR. This ADR's own
decision is untouched: Codex is a worker or reviewer process whose role constraints are supplied by
dispatch rather than plugin startup.

**Amendment (2026-09-11, see issue #332):** the Decision's pointer — *"ADR 0040's executor
preference and explicit standing setting remain on `reference/external-agent.md`"* — still holds,
and that preference now runs the other way: the default is the host's own subagent, and Codex is the
human's choice for one dispatch or standing until their next (0040's 2026-09-11 amendment). Named
here so "executor preference", read inside an ADR titled for Codex, is not taken for the old
direction. Codex as a dispatched executor, with its role supplied by dispatch, is unchanged.

**Amendment (2026-09-11, see 0056):** Superseded by 0056. The human requests Codex host installation
again; shared core and role sources, a bounded adapter, trusted hooks and an explicit recovery skill
supply it. Codex workers/reviewers still receive their role through dispatch. Historical removal
evidence remains; no marker, adopter or managed AGENTS block returns. The guard's
two-Claude-manifest exemptions remain unchanged.

**Amendment (2026-09-12, see PR):** The final sentence of the 2026-09-11 block is stale. Since PR
#343, the guard's version proofs cover all three synchronized manifests: the two Claude manifests
and the Codex manifest.

**Amendment (2026-09-29, see 0063):** 0063 supersedes 0056 and removes Codex hosting again, deciding
the removal anew rather than reviving this ADR: its body and its blocks stay history. The guard's
version proofs cover the two Claude manifests, so the 2026-09-12 block's three-manifest sentence no
longer holds.
