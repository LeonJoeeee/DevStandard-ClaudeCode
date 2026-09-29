# DevStandard's Codex CLI executor

Codex does not host the method: the orchestrator is a Claude Code session (ADR 0063). It dispatches
Codex as a CLI process — `--implementation codex` for a worker or a read-only gating reviewer — and
this page maps that executor's mechanics for the dispatching session. Method paths resolve from the
installed plugin root. The marked section below is the part `scripts/dispatch` hands a Codex worker.

## Dispatching Codex

Dispatch a worker with `scripts/dispatch ... --implementation codex`, and commission a gating review
through `scripts/review-packet start ... --implementation codex`, which uses the fresh read-only
Codex CLI process and whole-verdict publication path. The CLI must be installed and authenticated,
and a worker needs superpowers installed into Codex: its craft bindings name superpowers skills, and
Codex resolves skills from its own roots, never from Claude Code's (`README.md`'s Install section).
`reference/orchestrator.md`'s Dispatching to an executor section owns when Codex is chosen and its
permission boundaries.

**Verified Codex mechanics.** Run Codex CLI in the foreground of its detached supervisor. A linked
worktree needs write grants to both the common `.git` directory and its `.git/worktrees/<name>`
directory; the first grant is not recursive. Codex's `review` subcommand cannot take this contract
and its sandbox controls, so gating review uses plain read-only `exec`. Inspect actual output shape,
including newlines and attribution, before accepting it. These are Codex-specific observations, not
claims about another tool.

Codex CLI dispatch supplies role, task, model, effort and sandbox, and sets child-only
`DEVSTANDARD_ROLE=worker|reviewer`; the fixed role hook it installs uses that role. **It also admits
the host's MCP tools, for both purposes.** `codex exec` is non-interactive, so its approval policy is
`never`, and `never` auto-rejects every MCP tool call — a child that sees the tools, is refused on
the call, and cannot tell that from an unreachable server. On 0.153.4 the per-server
`mcp_servers.<name>.default_tools_approval_mode = "approve"` is the only admission that keeps an
explicit sandbox mode: `exec` ignores every `approval_policy` value, `--approve-for-me` cannot be
combined with `-s`, and the bypass flag would cost the OS sandbox the gating reviewer is built on.
Dispatch asks `codex mcp list --json` which servers the host has and passes that key per enabled
server, so it reads and edits no configuration file; a server it cannot admit is named in the run
record rather than left silently refused. Each purpose keeps the sandbox mode it had. Every role
then reaches every attached server — the residual `reference/orchestrator.md`'s Guarded operations
section accepts, whose remedy is not attaching such a server to a session that runs workers. What an
executor must do when a visible tool is refused anyway is `reference/worker.md`'s harness-limit rule.

The hook-trust bypass dispatch passes is invocation-wide, so every hook source Codex has enabled
runs in the child. A DevStandard Codex plugin left installed from a release before 2.0.0 is one such
source: remove it with `codex plugin remove`.

The run's advisory lock identifies an active supervisor across PID namespaces; PIDs are diagnostic.
Only the atomic completion marker reports an observed CLI exit. Missing completion with an absent
supervisor is lost or unknown and blocks reuse, which no attestation clears. Preserve lifecycle
scratch until lane cleanup; `reference/orchestrator.md`'s Dispatching to an executor section owns
explicit lost-run reconciliation and publication recovery. `--wait` changes lifetime only: it adds
no runtime-directory access, authentication, hook trust or nested sandbox capability. Python
supervision supports macOS/Linux without external `setsid` or `nohup`; Windows is not qualified.

<!-- BEGIN CODEX WORKER MECHANICS -->
## Worker mechanics

`scripts/dispatch` delivers this section with `reference/worker.md` to every Codex worker. That
page carries the contract, including what a worker does when the packet cannot be recovered; this
section is the Codex harness under it.

A Codex CLI worker runs inside the OS sandbox dispatch scoped to its lane. A nested `codex exec` is
not a subagent inside your sandbox. Its own subagents go through the host's native subagent tool.

A CLI process begins in its lane. When that directory is a linked worktree on a matching
`task/<issue>-...` branch, `origin` identifies the repository, the latest matching
`devstandard-dispatch-v1` process-run receipt names the lane, and its absolute brief holds the
packet in full. The receipt fits this lane only when its branch and worktree match exactly and
every required field is present; a missing, equally-new, or unreadable receipt or brief leaves the
packet unrecovered, and a partial summary found in the checkout is not one.
<!-- END CODEX WORKER MECHANICS -->
