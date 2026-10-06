# 0009 — Position DevBook as the GitHub flow extended to agent teams; the outer layer stays

Status: Accepted (2026-07-01). Amended by 0015 (2026-07-09). Amended (2026-09-07). Amended (2026-09-11). Amended by 0064 (2026-10-04).

## Context

Two things converged. First, DevBook is going public — it needs a reason a stranger should care, not "one developer's habits." Second, a real challenge to its design: Claude Code now allows subagents to spawn their own subagents (recursive delegation), so a main agent can act as a deep orchestrator. Does that make DevBook's outer layer — one task = one branch/worktree/session, merging owned by main, CI gate, architecture changes reviewed — obsolete?

## Decision

**Positioning.** One person could never build a large project alone; that is why software teams exist, and the coordination system humanity converged on for them is the GitHub flow — branches, PRs, CI, reviews, an append-only record of why. Working with AI agents recreates *the same collaboration problem in the same shape*: one human directing several agents, or several humans each bringing their own agents. DevBook's bet: **do not invent a new coordination system for agents — reuse the one that already won.** Not GitHub for GitHub's sake: for medium-to-large projects this is simply the highest-efficiency arrangement available, it is the only substrate humans can *see* (agents' work becomes branches and PRs a teammate can review), and it composes with the open internet — strangers can join a project bringing their own agent teams, through the exact flow they already know.

**The recursion question.** Recursive delegation raises single-session *capacity* — and capacity was never the binding constraint (the same verdict as the single-workflow-run analysis, `_source/workflow-deep-dive-report.md`). The outer layer exists for four things recursion cannot touch:

1. **Durable memory** — an orchestrator is mortal (context fills, sessions crash, quota windows close, laptops sleep); a recursive agent tree lives in memory and evaporates with its root. Branches, commits, and docs live on disk and survive into tomorrow, another machine, another person or agent.
2. **Gates** — inside an agent tree every change lands as one blob in one working tree with no CI/review checkpoint; the outer layer forces integration through reviewable units.
3. **Human visibility** — teammates cannot see an agent tree; they can see PRs. Git is the only shared language between humans and agents; drop it and humans are excluded from the collaboration.
4. **Quota windows** — multi-day work must chain through on-disk state regardless of agent topology.

So recursion changes the **inner** layer only: a task session can digest a larger task before the outer flow takes over (the execution ladder's rung 2 gets richer — noted in core.md). The outer layer is untouched, and under the multi-human-multi-agent positioning it matters *more*, because it is the half of the system humans participate in. DevBook stands on git, not on any agent topology — which is also why Claude Code updates do not shake it.

## Consequences

The README leads with this argument; the repo (including `docs/` and `_source/` — the evidence that DevBook built itself with its own rules) goes public under MIT. The cost: as a public standard the wording must stay plain and the personal specifics (models, quotas) must stay out — already the case (personal policy lives in the owner's own config, ADR 0008).

**Amendment (2026-07-09, see 0015):** The outer layer stands, but "one task = one branch/worktree/session" (Context, above) is refined — one-branch/one-worktree is the invariant; "= one session" is retired to the execution ladder's top rung (the executor is chosen per task: a subagent, a workflow, or a separate session). The GitHub-flow bet and the four durable-memory / gates / visibility / quota arguments are unchanged.

**Amendment (2026-09-07, issue #279):** the 2026-07-09 block above retires *"= one session"* **to
the execution ladder's top rung**, and names a subagent, a workflow, or a separate session as the
rungs it is chosen from. 0047 retired the ladder itself and its Amends list did not reach this ADR.
The invariant this block protects is unchanged — one task = one branch = one worktree. What
replaces the rung is **purpose × implementation**: worker, reviewer, or a resolver as a worker
assigned conflicts, times the executor that runs it — Codex where installed, a Claude-native
subagent where the work especially suits one (0040, 0047; `reference/external-agent.md`). Workflow
runs, chained runs and standalone live-session lanes are no longer executor forms. This ADR's own
recursion argument stands as written, including its Decision paragraph on the inner layer: the ladder
sentence there is the vocabulary of its day, and what the paragraph decides — recursion changes the
inner layer only — is untouched.

**Amendment (2026-09-11, see issue #332):** the 2026-09-07 block above states the implementation
half of purpose × implementation as *"Codex where installed, a Claude-native subagent where the work
especially suits one"*. That half is reversed: the default executor is the host's own subagent, and
the human's instruction — for one dispatch, or standing until their next — selects Codex instead
(0040's 2026-09-11 amendment; `reference/external-agent.md`, "When a subagent, when Codex"). What
that block protects is untouched — one task = one branch = one worktree, and purpose × implementation
as the replacement for the retired rung; only which implementation is presumed has changed.

**Amendment (2026-10-04, see 0064):** The 2026-09-11 block's dispatch default is superseded: Codex CLI is the default worker and
reviewer executor, and the human's instruction selects another supported executor for one dispatch
or standing. `reference/orchestrator.md`'s Dispatching to an executor section now carries the
operative wording, replacing the removed `reference/external-agent.md` pointer. One task, branch
and worktree and the purpose × implementation construct remain unchanged.
