# DevStandard in Claude Code

This page maps the Claude harness for a dispatched worker; `reference/worker.md`, delivered with
it, carries the contract — including what a worker does when the packet cannot be recovered.

## The built-in subagent

The Claude harness loads an agent definition's body as the subagent's system prompt, and
`agents/worker.md`'s body is `reference/worker.md` followed by this page, byte for byte. Both
reach every Claude worker without a read, and both survive compaction.

A native child starts in its caller's directory, not in the lane; the packet names the worktree its
contract has it validate and work in. It inherits the host's permissions and adds no sandbox of its
own. Its own subagents go through the Agent tool, never a Codex process; the tool takes `model` per
call and no effort, so an undefined effort inherits this session's. Spawn `opus` for a helper whose
conclusion directly decides a merge or a design (checking a worker's diff, challenging a design), and
`sonnet` for ordinary judgment or mechanical work.

### Recovering the binding

The host's record of a child's own conversation is this harness's lane-specific carrier. A
model-written compaction summary, the caller's current directory and another lane's receipt each
describe something other than this lane, so none of them identifies the packet. The record does:
emit a nonce through any tool call, then `grep -rl <that nonce> ~/.claude/projects` matches exactly
one recorded child conversation, whose first line is the packet as delivered. More than one match
means the nonce no longer picks out a single lane, and the packet is not recovered.

## The Claude CLI worker

`scripts/dispatch --implementation claude-cli` runs that same definition as a top-level process
started in the assigned worktree, under host and tool permissions with noninteractive
`acceptEdits`, and adds no OS sandbox of its own.

A dispatched CLI worker runs with session persistence off, so the host records nothing about its
conversation and the lane lookup below is its carrier instead. An executor with neither carrier has
no lane-specific source left.

A CLI process begins in its lane. When that directory is a linked worktree on a matching
`task/<issue>-...` branch, `origin` identifies the repository, the latest matching
`devstandard-dispatch-v1` process-run receipt names the lane, and its absolute brief holds the
packet in full. The receipt fits this lane only when its branch and worktree match exactly and
every required field is present; a missing, equally-new, or unreadable receipt or brief leaves the
packet unrecovered, and a partial summary found in the checkout is not one.
