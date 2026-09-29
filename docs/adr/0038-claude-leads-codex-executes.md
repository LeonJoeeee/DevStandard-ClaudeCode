# 0038 — Claude Code leads, Codex executes: one plugin, one branching hook, marker-scoped

Status: Superseded by 0045 (2026-09-05). Amended by 0045 (2026-09-05). Originally Accepted (2026-08-26). Amended by 0039 (2026-08-26). Amended by 0040 (2026-08-26). Amended (2026-09-11). Amends 0036 (its executor-neutrality gains a settled default on the
Claude/Codex axis), 0019 (the SessionStart hook now branches by harness; the Claude branch and its
forced read of core.md are unchanged), 0007 (same scoping of the hook's description), and 0018 (its
AGENTS.md note is reframed: the fallback block is delivery, not memory). Supersedes nothing on main;
an earlier draft of this number recorded a symmetric either-side-may-lead design that was abandoned
before any merge — it survives in the branch history and in
`docs/specs/2026-08-25-devstandard-codex-adapter.md` (kept as `abandoned`), and this ADR is the
decision that replaced it. Amended by 0056 (2026-09-11). Amended by 0063 (2026-09-29).

*This ADR decides what DevStandard ships and how its projects are topologized — a reader in any
seeded project should take it as method.*

## Context

The human ruled (#148): on all these projects, **Claude Code is the main session — it plans,
dispatches, reviews, and merges; Codex is the executor.** The plugin installs on both harnesses, but
the sides carry different halves: Claude's is `core.md` entire; Codex's is only how to execute and
cooperate.

The evidence behind the ruling (#148/#153): every concrete community pairing surveyed runs
Claude-as-orchestrator, and a curated ecosystem directory lists no instance of the reverse; a
measured study (arXiv 2607.21656) finds Codex-writes/Claude-reviews the productive review direction
(+18.1pp) and the reverse harmful on average (−8.6pp; the harm mode — reviewers rewriting instead of
repairing — is structurally excluded by this method's non-writing check-1 reviewer, and its lesson
is kept as: an external reviewer's findings are verified, never auto-applied).

The delivery mechanics were settled by building, across nine adversarial challenge rounds run by
Codex itself (the full log is on #148); the load-bearing measurements, on `codex-cli 0.144.6` and
Claude Code 2.1.245:

- **Codex discovers a plugin's `hooks/hooks.json` and runs its SessionStart hook** after a one-time
  interactive trust confirmation; thereafter it fires flag-less in any directory, and trust survives
  plugin updates and script edits. (An earlier pilot concluded plugin hooks never fire; it had never
  walked the trust flow — an untrusted hook is skipped silently.)
- **The hook runtime discriminates the harness**: Codex sets `PLUGIN_DATA`/`PLUGIN_ROOT` and
  equal-valued `CLAUDE_`-prefixed aliases; Claude Code sets only its own pair. Equality of the two
  DATA values is the test — inheritance-resistant, since a contaminated environment inherits a
  *different* `PLUGIN_DATA`. This is a **version-scoped compatibility boundary**: any Claude or
  Codex release that changes its plugin-hook environment blocks support until the discriminator is
  re-measured.
- **Codex parses the Claude-style JSON hook output** — `additionalContext` reaches the model.
- Codex reads a repo's `AGENTS.md` chain natively; that channel is kept only as the **fallback**
  delivery where hooks are unavailable.

## Decision

**One plugin, one hook entry, one script.** `hooks/session-start` branches on the discriminator:
the **Claude branch is byte-identical to the pre-0038 hook** (ADR 0019's forced read of `core.md`);
the **Codex branch delivers the worker role** — and only inside a repo that has opted in with a
committed, regular-file `.devstandard` marker at its git toplevel; everywhere else it emits nothing.
An unidentifiable harness gets a visible warning and no instructions, never a blocked session.

**The worker role** lives in `reference/harness-codex.md` (size-gated): the main session is Claude
Code; a Codex session executes — implementation (with the placement validation, the
`worker-brief.md` and `CLAUDE.md` reads), review/challenge (read-only), or advice; never merge, tag,
or release; the record is GitHub. A direct human request without an issue runs a state machine that
opens and claims the issue, routes substantial changes to the main session, and puts eligible small
work in a dedicated worktree under `.claude/worktrees/` — never the opened checkout.

**Adoption is a committed change.** `scripts/codex-adopt` (in the plugin) writes the marker, the
`/.claude/worktrees/` gitignore entry, and — on request — a delimited, prepended `AGENTS.md`
fallback block; the marker doubles as the ownership manifest; the resulting diff rides a normal PR,
so git is the provenance and the undo, and a linked worktree created after adoption carries the
marker automatically. The dispatcher verifies the marker is committed on the branch it dispatches
onto. `CLAUDE.md` remains the operational-memory file on every harness — a Codex worker reads it
explicitly and writes back through its PR; `AGENTS.md` never carries memory.

**On the Claude side**, dispatching to an external agent now defaults to Codex where installed
(`core.md` "Who does the work"; `reference/external-agent.md` carries the adoption duty and the
verify-never-auto-apply stance). 0036's neutrality stands for every other tool.

## Consequences

- **The delivery asymmetry is stated, not hidden**: Claude delivery is automatic per install; Codex
  delivery is per-machine trust (once) plus per-repo adoption (a committed marker). A repo without
  the marker gives Codex sessions nothing — absent, not degraded.
- **Role obedience is model compliance** — the same bet ADR 0019 made for the Claude side — and is
  probed adversarially (a capability-controlled merge refusal test, re-run when the model or either
  CLI changes) rather than assumed.
- **Rollback has two named layers**: the delivery layer is additive (the branch is one `if`;
  reverting it restores the pre-0038 hook byte-for-byte; a repo unadopts via the same script); the
  policy migration — the operative clauses in `core.md`, `reference/worker-brief.md`,
  `reference/external-agent.md`, and this ADR's amendments — is a coordinated set, enumerated in
  `docs/specs/2026-08-26-claude-leads-codex-executes.md`.
- The `claude -p` reverse-dispatch mechanics and the Codex-as-main design were measured and are
  preserved on #148 for the day a ruling wants them; they ship nowhere.

**Amendment (2026-08-26, see 0039):** the identity and scoping this ADR decided — Codex as
permanent executor, the `.devstandard` marker, the adoption ceremony, the role-delivering hook
branch — are overturned by the human's correction the day this shipped: both harnesses receive the
same method, and worker identity is announced only by a dispatch brief. The measured delivery
mechanics recorded here (plugin-hook discovery, one-time trust, the discriminator, the
byte-identical Claude branch) stand and are what 0039 builds on.

**Amendment (2026-08-26, see 0040):** "dispatching to an external agent now defaults to Codex where installed" is no longer a soft, Claude-side default: at rung 2, on either harness, dispatched work goes to Codex where it is installed and a harness-native subagent only where the work especially suits one (`reference/external-agent.md`, "When a subagent, when Codex"); the standing model and effort are written once on that page. The adoption duty this sentence also named was already retired by 0039.

**Amendment (2026-09-05, see 0045):** Superseded by 0045. The plugin manifest, Codex hook branch, mappings page, and Codex startup fallback are removed. The supported configuration is a Claude Code orchestrator with dispatched executors; Codex receives its role through the dispatch brief. The measurements above remain history; they no longer require Codex plugin compatibility work. The Claude hook behavior and unknown-harness warning remain.

**Amendment (2026-09-11, see issue #332):** "dispatched work goes to Codex where it is installed"
is reversed. Dispatched work goes to the host's own subagent unless the human's instruction selects
Codex, for one dispatch or standing until their next (ADR 0040's 2026-09-11 amendment;
`reference/external-agent.md`). Claude still leads and Codex still executes when it is the choice;
only which executor is presumed has changed.

**Amendment (2026-09-11, see 0056):** 0056 supersedes 0045's host removal without reinstating this
ADR's permanent Codex-worker identity, marker or adoption ceremony. Main sessions may use either
host; dispatch supplies worker identity. The earlier measurements remain historical evidence, not
current compatibility qualification.

**Amendment (2026-09-29, see 0063):** 0063 supersedes 0056. Main sessions are Claude Code only;
Codex executes when dispatched, with its identity supplied by dispatch. This ADR stays superseded,
and its measurements stay history.
