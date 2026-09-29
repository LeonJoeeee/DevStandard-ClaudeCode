# 0056 — Restore Codex host support with shared roles and native workers

Status: Superseded by 0063 (2026-09-29). Originally Accepted (2026-09-11). Supersedes 0045. Amended (2026-09-11). Amended (2026-09-12). Amended (2026-09-20).
Amended by 0061 (2026-09-19).
Amends 0006, 0007, 0008, 0011, 0015, 0016,
0018, 0019, 0022, 0024, 0035, 0036, 0038, 0039, 0040, 0046, 0047, 0049, 0050, 0051 and 0052 (their live host, delivery, routing, version-exemption or sandbox clauses).

**Scope: this ADR decides what the method ships.** Both Claude Code and Codex can host the
orchestrator; their shared workflow and the worker/reviewer contracts remain the same.

## Context

ADR 0045 removed unused Codex host packaging during the collaboration rebuild. The human now
wants to use DevStandard from Codex as well as Claude Code ([issue #342](https://github.com/LeonJoeeee/devstandard/issues/342))
and explicitly asked for whole-project reading, a plan and actual hook tests. Host installation is
therefore a required entry point rather than unused structure. The implementation plan
reuses the shipped role sources and dispatcher and ends with a tested PR, without merge or release.

The requested Codex host must use its own native workers. The existing Claude Agent receipt and
Codex CLI process are distinct implementations; selecting the latter for every Codex lane would not
satisfy that request. Native Codex tools can select model and reasoning effort but inherit host
permissions, so a native worker and a read-only gating reviewer need different delivery paths.

## Decision

Restore `.codex-plugin/plugin.json` and a repository marketplace under `.agents/plugins/`.
The shared SessionStart script delivers `core.md` and `reference/orchestrator.md` on either host,
plus the bounded `reference/harness-codex.md` adapter on Codex. Each artifact keeps its own inline
budget. The shared matcher remains `startup|clear|compact`; the adapter also runs on resume and
instructs a full read of any missing shared sources in an older session.

An explicit `devstandard` skill provides instruction recovery when hooks are unavailable or waiting
for trust. It reads the same sources and preserves an assigned worker/reviewer role. It is not the
self-triggered method delivery rejected by 0007, and it does not activate a tool guard. Hook trust
remains the host's mechanism; installation alone does not prove hooks run.

Each host defaults to its own native workers. `--implementation claude` prepares the existing
Claude Agent receipt; `--implementation codex-native` prepares a Codex native-worker receipt. The
latter carries the full shared role and task, assigned worktree, and explicit model/effort from
purpose routing on `reference/external-agent.md`, with per-field `--model`/`--effort` overrides. Its
semantic envelope is not a tool invocation:
the caller must pass the message and settings to the actual native API with conversation-history
forking disabled, record its returned handle, and observe it with the native wait/status tool.
Unsupported model/effort controls make that path unsupported; they do not authorize implicit defaults.

Fresh conversation does not remove inherited developer instructions, cwd or permissions. The worker
must operate from its assigned worktree. Native Codex cannot impose a per-child read-only sandbox,
so `codex-native` reviewer requests refuse before mutation; Codex-host gating reviews explicitly
select `--implementation codex`, the independent read-only CLI. CLI workers remain an explicit
choice. `--native-finished` attests completion of all outstanding native handles in that lane for one
operation, never bypassing CLI processes. No new handle journal or Codex agent-definition loader is
added. The plugin manifest has no `agents` loader. ADR 0055 still leaves internal delegation to the
worker. Explicit cross-host execution uses `codex` from Claude or the worker-only `claude-cli` from
Codex; existing `claude` retains its native Agent meaning. Claude CLI uses normal authentication,
host/tool permissions, the assigned worktree and noninteractive `acceptEdits`, never a bypass. It
does not provide Codex's OS sandbox, so Claude CLI reviewers also refuse before mutation.

Native children receive SubagentStart rather than main-session SessionStart; their full role comes
from dispatch. Inherited tool hooks treat a child `agent_id` with absent or `default` agent type as
worker-family after explicit role, recognized agent type and process-marker bindings; named Claude
research children retain their parent role, while Codex research children still take that fallback.
CLI dispatch supplies `DEVSTANDARD_ROLE` only to its child processes, overriding inherited values and suppressing orchestrator startup context. These
signals route context and hook roles, not authorization. The hook's word lists, Codex CLI sandboxes, review
publication, CI and merge guard keep their existing boundaries.
Detached Python sessions replace the external `setsid`/`nohup` prerequisite on macOS and Linux;
supervision and publication ignore SIGHUP. Windows is not qualified.

`CLAUDE.md` remains the operational-memory source, explicitly read by Codex. Existing `AGENTS.md`
instructions are respected without copying facts or adding managed method blocks. Superpowers is
installed on each executing host and resolved at the existing role triggers.

The three release manifests stay in version lockstep and share the existing version-line-only
bare-bump waiver and rebase exemption: old and new values must each agree across all manifests,
and non-version changes still refuse; the rebase proof retains its strict ordering checks.

Excluded: restoring the old repository-adoption marker, copying the method into global instructions,
or requiring custom Codex agent configuration. Shared sources and explicit native receipts suffice.

## Consequences

Codex can enter the same method as a main session without becoming a permanent worker. This costs
one bounded adapter and installation entry, a native worker receipt, and host qualification.
CLI command help, constructed tests and real runtime probes establish different facts; the release
evidence must distinguish them. Historical 0038/0039 measurements do not qualify a newer CLI.
Architecture labels remain explicit about unverified live behavior until that evidence exists.
The required aggregate `test` depends on both vendor matrix jobs with pinned npm packages and the
apt AppArmor profile; a yanked pin reds `test` and blocks merging and new dispatch, the accepted
cost of real-binary CI.
Claude also discovers `skills/devstandard` harmlessly and executes the extra `session-start codex`
hook, which prints `{}`.

Rollback removes the new host carriers and restores the previous shared-hook branch and supervisor
through a reviewed revert. It never edits a user's global instructions. The original ADR bodies and
historical specs remain intact; dated amendments reconcile their actionable routing statements.

**Amendment (2026-09-11, issue #342 continuation):** Real App orchestration transcribed two
worker-role passages differently while forwarding the inline native message. Native receipts now
prepend an instruction to read and verify the existing per-run canonical brief; its path and SHA-256
also travel in the envelope and run record. `reference/harness-codex.md`, Native workers, owns that
requirement. The complete inline role/task remains, and no extra state store or permission change is
introduced. This hardens source fidelity; deterministic native-runtime probes do not prove model
obedience to the read instruction.

**Amendment (2026-09-11, issue #342 CLI lifecycle):** A real Linux Codex tool lost its detached
supervisor when the enclosing PID namespace ended. Detachment and SIGHUP handling remain the default;
explicit CLI `--wait` now retains that originating invocation through observed completion, and
review-packet waiting includes synchronous whole-verdict publication. The existing scratch holds an
inherited advisory supervisor lock; PIDs are diagnostic only. A missing completion plus absent
supervision is lost/unknown, not permission to reuse the lane. Exact-run reconciliation records the
caller's claim of authoritative originating-host absence inspection on the original issue comment,
not an automated verification, and invents no exit evidence. Review publication confirms that
reconciliation before releasing a lost attempt as failed, including when scratch is gone. Retain lifecycle scratch until lane cleanup.
`reference/external-agent.md` owns these operations and limits. No service, durable completion
journal, authentication change, permission widening or native-lifecycle change is introduced.

**Amendment (2026-09-12, issue #352 native resume):** This ADR's native routing — pass the message
to the native API with conversation-history forking disabled, and continue through a fresh child —
described the only delivery then known. A live probe of Codex CLI 0.153.4 on both multi-agent
protocols found that a **finished** native child accepts a follow-up and answers with its prior
conversation intact (v1 `send_input`, v2 `followup_task`; commands, tool output and the child's own
second request are on issue #352). So `--continue --resume HANDLE` now applies to `codex-native` as
well as `claude`: the receipt then carries `resume`, sets `fresh_conversation: false`, and obliges
the caller to deliver the message to that existing child instead of spawning one. Fresh spawns are
unchanged, and a fresh child remains the continuation wherever no handle is held, the handle was
closed, or its spawning session has ended. `--native-finished` still gates the operation — the
resumed child has finished — and no new command, flag, handle journal or permission is added.
`reference/harness-codex.md` and `reference/external-agent.md` carry the operative wordings;
`reference/orchestrator.md` owns when to resume. The finding qualifies one CLI version on one host,
not a guarantee across future releases.

**Amendment (2026-09-19, see 0061):** The shared role source is sharpened, not withdrawn. Every
executor still receives one hand-written worker contract, `reference/worker.md`, and dispatch still
assembles it; what it no longer carries is any one harness's mechanics. Those moved to a page per
executor family — the new `reference/harness-claude.md` and a marked worker-facing section of
`reference/harness-codex.md` — and each worker is delivered its own and never the other's. Where this
ADR says a native Codex receipt "carries the full shared role and task", that role is now the
contract page plus that marked Codex section; the Claude paths take their harness page from the agent
definition body instead. Hook trust, sandbox modes, `DEVSTANDARD_ROLE` suppression, native receipt
verification and the version lockstep are untouched.

**Amendment (2026-09-20, issue #427):** `--native-finished` is deleted, so the Decision's *"attests
completion of all outstanding native handles in that lane for one operation, never bypassing CLI
processes"* and the 2026-09-12 block's *"still gates the operation"* no longer describe a flag that
exists. It verified nothing it claimed: the dispatcher's liveness check returned "running" for every
native record unconditionally, so the flag's only effect was to skip a check that could never
answer. A native handle is the caller's own, and the handle recorded on the issue is the evidence
its child finished. Everything the flag never touched is unchanged and is the part that mattered:
the CLI supervisor lock and completion marker still block a second writer on a running lane, and
missing completion with an absent supervisor is still lost or unknown. `reference/harness-codex.md`
and `reference/orchestrator.md` carry the operative wordings.

**Amendment (2026-09-20, issue #436):** Two dispatcher clauses lose enforcement they never needed.
The Decision's native-receipt routing — *"explicit model/effort from purpose routing ... with
per-field `--model`/`--effort` overrides"* — still holds, but a page row the dispatcher cannot find
or parse now warns and falls back to those overrides instead of refusing the lane; only a knob
neither the page nor a flag supplies refuses. And the 2026-09-11 CLI-lifecycle block's account of
exact-run reconciliation is unchanged in what it claims — the caller's originating-host absence
finding is recorded, never verified, and no exit is invented — while the bookkeeping around it is
gone: the HTTPS shape test on `--evidence`, which nothing ever fetched; the recorded-status and
comment-id preconditions; and the mid-reconciliation identity re-comparisons, so re-running the
command now overwrites the same comment instead of refusing a changed field as a conflict. What
that block relies on is untouched and is the part that mattered: the inherited advisory lock and
the atomic completion marker still refuse a second writer before, during and immediately before the
patch, and missing completion with absent supervision is still lost or unknown. The lane check that
precedes it keeps the two refusals that bound where a later `worktree remove` and `branch -D` would
land — another repository, and a main checkout rather than a linked worktree. The dispatcher also
no longer refuses a closed issue, recording `issue_state` on the run instead, and no longer searches
a `--brief` for placeholder tokens. `reference/orchestrator.md` and `scripts/dispatch --help` carry
the operative wordings.
