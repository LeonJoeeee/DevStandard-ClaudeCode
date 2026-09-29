# 0006 — The Workflow tool IS the harness; DevBook ships a thin shell, not machinery

Status: Superseded by 0047 (2026-09-07). Amended by 0047 (2026-09-07). Originally Accepted (2026-06-10). Amended by 0045 (2026-09-05). Amended by 0007/0008 (2026-07-09). Amended by 0039 (2026-08-26). Amended by 0056 (2026-09-11). Amended by 0063 (2026-09-29).

## Context

While designing per-task execution, a proposal emerged to ship canonical orchestration machinery in the plugin: three chained, parameterized, plugin-bundled workflow scripts (design-and-refute → implement-slices → close). Research confirmed plugins *can* bundle named workflows — but the loader is undocumented and has open field bugs (name resolution, args dropping). More fundamentally, the human rejected the direction: the Workflow tool is already an excellent harness — parallelism, schema handoffs, budgets, and quality patterns are native. Wrapping a harness in another harness is over-engineering.

## Decision

DevBook ships **method, not machinery**. Per-task execution is delivered as ONE reference file (`task-workflow-how.md`) — a thin shell the session reads before **authoring a fresh workflow fitted to the task at hand**. The shell carries:

- the five-stage skeleton (set the bar → design → refutation → sequential slices → evidence-based close);
- the hard authoring rules: no code before refutation passes; dependent slices written sequentially in a plain loop; an absent reviewer counts as red; evidence means command + exit code + output; panel sizes scale with task weight; budget loops guarded;
- the gate rule: a workflow cannot ask the human mid-run, so a two-axis hit ends the run and the session gates in the main loop before continuing;
- one compact example skeleton (~30 lines) to copy and adapt.

No plugin-bundled named workflows; no fixed stage scripts; task shapes are handled naturally at authoring time (prompts fit the shape), so no per-shape variants exist either.

## Consequences

Each task gets a workflow shaped to it, and DevBook stays decoupled from an undocumented, still-buggy loader path. The discipline that mattered (design-refute-before-code, evidence-based closing) survives as authoring rules. The cost: per-task authoring variance — mitigated by keeping the rules short, hard, and backed by a concrete example. The Workflow-feature research remains the source for the rule text (`_source/workflow-feature-research.md`).

**Amendment (2026-07-09, see 0007/0008):** The core call stands — no bundled machinery; the Workflow tool is the harness. The delivery vehicle was overtaken: `task-workflow-how.md` never shipped, and its authoring rules were folded into `core.md` (0007, 0008).

**Amendment (2026-08-26, see 0039):** "the Workflow tool is the harness" generalizes: each
supported harness's native orchestration (Claude's Workflow tool; Codex's subagent and loop
primitives) is that harness's own machinery, and this ADR's core call — DevStandard bundles none of
it — stands unchanged across harnesses.

**Amendment (2026-09-05, see 0045):** The 0039 amendment's Codex-native orchestration extension is retired. The supported orchestrator is Claude Code; Codex is a dispatched CLI executor. This removal adds no orchestration machinery; the remaining rebuild disposition is in architecture chapter 7.

**Amendment (2026-09-07, see 0047):** Superseded by 0047. The plugin now ships the collaboration
protocol's fixed transitions as scripts, hooks and agent definitions, so "method, not machinery" no
longer describes what it delivers. What this ADR actually refused stands, restated in 0047: no
bundled per-task execution machinery, and nothing routed through the Workflow-tool loader. The
native harness still owns sessions, tools and agents.

**Amendment (2026-09-11, see 0056):** 0056 restores Codex as a host. The 0045 block's Claude-only
orchestrator scope is retired; the native harness still owns its orchestration. This ADR remains
superseded by 0047: no per-task execution machinery or Workflow-loader integration is restored.

**Amendment (2026-09-29, see 0063):** 0063 removes the Codex host again, so the 0056 block's
restoration no longer holds: Claude Code is the only orchestrator, and Codex executes only when
dispatched as a CLI process. This ADR remains superseded by 0047.
