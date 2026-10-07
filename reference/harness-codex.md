# DevStandard's Codex CLI executor

Codex does not host the method: the orchestrator is a Claude Code session (ADR 0063). It dispatches
Codex as a CLI process — `--implementation codex` for a worker or a read-only gating reviewer — and
this page maps that executor's mechanics for the dispatching session. Method paths resolve from the
installed plugin root. The marked section below is the part `scripts/dispatch` hands a Codex worker.

## Dispatching Codex

Dispatch a worker with `scripts/dispatch ... --implementation codex`, and commission a gating review
through `scripts/review-packet start ... --implementation codex`, which uses the fresh
Codex CLI process and whole-verdict publication path. The CLI must be installed and authenticated,
and a worker needs superpowers installed into Codex: its craft bindings name superpowers skills, and
Codex resolves skills from its own roots, never from Claude Code's (`README.md`'s Install section).
`reference/orchestrator.md`'s Dispatching to an executor section owns when Codex is chosen and its
permission boundaries.

**Verified Codex mechanics.** Run Codex CLI in the foreground of its detached supervisor. A linked
worktree needs write grants to both the common `.git` directory and its `.git/worktrees/<name>`
directory; the first grant is not recursive. Codex's `review` subcommand cannot take this contract
and its sandbox controls, so gating review uses plain `exec`. Inspect actual output shape,
including newlines and attribution, before accepting it. These are Codex-specific observations, not
claims about another tool.

A CLI reviewer runs with `workspace-write` and network in a one-off checkout of the packet's
pinned head, under its run scratch (`TMPDIR` or the system temporary directory). Its Git metadata
lives beside that checkout; the only extra write grant is to that copy's metadata, so fetching
history cannot alter the lane's refs or objects. The supervisor creates the independent clone,
restores the upstream origin, and removes the copy before recording completion, including a
nonzero exit or handled cancellation. Creation failure records `launch-failure` and launches no
reviewer; it never falls back to the lane. A killed/lost supervisor requires the existing exact-run
recovery; its known disposable copy may remain for caller cleanup.

Read-only describes authority toward the repository and its remote: the reviewer never comments,
edits a PR or issue, pushes, or changes remote state. Disposable experiments stay in the copy and
evidence stays pinned; `reference/code-review-prompt.md` carries this rule in every CLI brief.
The caller publishes the verdict. The reviewer `gh api` write-flag hook remains a reminder,
not a complete remote boundary.

For MCP access in a dispatched Codex executor, see `scripts/dispatch`'s `mcp_tool_admission`.
Do not attach a server a worker must not reach to a session that runs workers. When a visible tool
is refused, use `reference/worker.md`'s harness-limit rule.

The hook-trust bypass dispatch passes is invocation-wide, so every hook source Codex has enabled
runs in the child. A DevStandard Codex plugin left installed from a release before 2.0.0 is one such
source: remove it with `codex plugin remove`.

For a Codex CLI run's liveness, lost-run recovery and `--wait` semantics, use
`scripts/dispatch --help` and `reference/orchestrator.md`'s Dispatching to an executor section.
Preserve lifecycle scratch until lane cleanup and read the returned output itself.
Python supervision supports macOS/Linux; Windows is not qualified.

<!-- BEGIN CODEX WORKER MECHANICS -->
## Worker mechanics

`scripts/dispatch` delivers this section with `reference/worker.md` to every Codex worker. That
page carries the contract, including what a worker does when the packet cannot be recovered; this
section is the Codex harness under it.

A Codex CLI worker runs inside the OS sandbox dispatch scoped to its lane. A nested `codex exec` is
not a subagent inside your sandbox. Its own subagents go through Codex's native subagent tool, never
a Claude process, each with the model and effort the packet's `Helpers:` line gives for its work.

A CLI process begins in its lane. When that directory is a linked worktree on a matching
`task/<issue>-...` branch, `origin` identifies the repository, the latest matching
`devstandard-dispatch-v1` process-run receipt names the lane, and its absolute brief holds the
packet in full. The receipt fits this lane only when its branch and worktree match exactly and
every required field is present; a missing, equally-new, or unreadable receipt or brief leaves the
packet unrecovered, and a partial summary found in the checkout is not one.
<!-- END CODEX WORKER MECHANICS -->
