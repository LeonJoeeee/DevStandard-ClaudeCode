# 0008 — Execution ladder: pick the cheapest rung; workflows are rationed

Status: Amended by 0050 (2026-09-09). Superseded by 0047 (2026-09-07). Amended by 0047 (2026-09-07). Originally Accepted (2026-06-11). Amended by 0045 (2026-09-05). Supersedes 0003. Amended by 0017 (2026-07-16), 0024 (2026-07-25). Amended by 0039 (2026-08-26). Amended by 0056 (2026-09-11). Amended by 0063 (2026-09-29).

## Context

ADR 0003 made a Workflow mandatory for every task. Reality intervened on two fronts. **Quota:** on the human's 20x plan, a top-tier-resident workflow can burn a 5-hour usage window in ~20 minutes; community reports match (a 22-agent run consuming a full session limit in 10 minutes). **Evidence:** the deep-dive (`_source/workflow-deep-dive-report.md`) showed runs cannot be intervened in mid-flight, agent spend — not orchestration — is the entire cost, and a workflow with no real fan-out or loop is pure overhead over direct subagent calls. The flagship Bun Zig→Rust port (750k lines / 11 days / 99.8% tests passing, yet unsound code — oven-sh/bun#30719) confirmed both that chained small runs are how large work actually ships and that the done-check defines the only quality you get.

## Decision

Replace "Workflow mandatory" with the **execution ladder** — pick the cheapest rung that holds the work:

1. **In-session directly** — the default;
2. **1–3 clean-context subagents** (Agent tool) — an independent piece or review helps; no loops, no wide fan-out;
3. **One small workflow run** — only for a real fan-out (review panel) or a real loop (fix-until-green);
4. **Several chained runs** — the work crosses decision points.

Companion rules:
- **Run sizing:** a run = one coherent stage you can fly blind through (no mid-run intervention exists). Split at human-decision and inspection points, never for capacity. Lower bound: no fan-out/loop → no run.
- **Rationing:** every run is spend-capped before launch (fixed panel sizes, MAX_ROUNDS, budget guards); runs are reserved for verification-dense work (design refutation, fix-until-green, pre-merge audit).
- **Model routing by role, in relative tiers:** judgment/synthesis → strongest available; review panels → one tier down; mechanical work → two tiers down. DevBook names no concrete models — the concrete mapping and quota policy are personal config (`~/.claude/CLAUDE.md`), not method.

What survives from 0003 unchanged: SDD remains optional; the discipline backbone (design refuted before code; verification-heavy token spend; evidence-based closing) applies at **every** rung, not only inside workflows.

## Consequences

Execution cost now scales with the work instead of being fixed at "fan-out always"; the discipline is preserved where it was always load-bearing (verification), and the method no longer embeds model-market ephemera. The cost: rung selection is a judgment call — core.md states the rule in one line so the call is cheap and consistent.

**Amendment (2026-07-16, see 0017):** "SDD remains optional" is refined, not reversed — a substantial change (shared/public interface, a real feature whose design could go more than one way, expensive to undo) now writes a 1–3-page design spec before code; ordinary tasks still write nothing.

**Amendment (2026-07-25, see 0024):** the model-routing bullet's second sentence — the one delegating the concrete mapping and quota policy to personal config — is reversed. The method now names Claude's tiers outright and caps every agent it spawns at `opus`, whatever the main session runs: `opus` is both cap and default, every review that gates progress included, with `sonnet`/`haiku` reserved for genuinely mechanical work; the model is set on every spawn that takes one (no inheritance). Routing by role as a principle, the ladder, run sizing, and rationing stand; the concrete role→tier mapping both moves into the method and changes — a review that gates progress is no longer "one tier down" but at the cap.

**Amendment (2026-08-26, see 0039):** the ladder is read harness-neutrally, and the 0024-era
tier language in the amendment below binds agents spawned through Claude's harness; a Codex main
session routes within its own models. The ladder's shape, run sizing, and rationing are unchanged.

**Amendment (2026-09-05, see 0045):** The 0039 amendment's Codex-main-session routing is removed from scope. Claude-spawned agents retain the existing tier rule; Codex is a process executor configured explicitly by its dispatcher under `reference/external-agent.md`. This removal does not implement the separate ladder rebuild.

**Amendment (2026-09-07, see 0047):** Superseded by 0047. The execution ladder is retired — the
shipped pages no longer name rungs, dispatch is the default, and the executor is chosen as a purpose
times an implementation. Run sizing and rationing survive in 0047 as the issue's bounds, the
orchestrator's scope cutting, per-PR round accounting and the 7-round cap. 0024's cap and tier names
are untouched by the retirement.

**Amendment (2026-09-09, see 0050):** The cap and role-to-tier mapping relayed by the earlier
amendments are superseded by issue #309's 2026-09-09 ruling. Follow the model/effort ladder in
`reference/external-agent.md`,
“Route it explicitly”. The execution-ladder retirement, run sizing and rationing remain as 0047
records them.

**Amendment (2026-09-11, see 0056):** The 0045 block's removal of Codex-main routing is retired by
0056. This ADR remains superseded by 0047; restoring the host does not restore the execution ladder.
The current model/effort rule remains on `reference/external-agent.md`; Codex hosts use native
workers and independent read-only CLI gating reviewers.

**Amendment (2026-09-29, see 0063):** 0063 removes Codex hosts and native Codex workers again; Codex
takes part as a dispatched CLI worker or read-only reviewer. The model/effort rule is
`reference/orchestrator.md`'s Model and effort section — the page the 0056 block names no longer
exists. This ADR remains superseded by 0047.
