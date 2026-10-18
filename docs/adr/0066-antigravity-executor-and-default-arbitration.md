# 0066 — Antigravity joins the dispatched executors and becomes the default arbitration source

Status: Accepted (2026-10-18). Amends 0036 (the blanket no-bypass permission rule), 0050 and 0064 (arbitration order), and 0061 (the set of executor mechanics pages).

## Context

Issue #519 settles Antigravity CLI as a worker and reviewer executor under the existing lane/PR
contract, after #517 simplified CLI lifetime. It also selects the Gemini model anchors and makes
Antigravity the first arbitration source. The supplied continuation verifies the actual stdin
schema and authorizes a disposable test HOME to qualify the real CLI inside a sandbox whose normal
agy home is read-only. That test accommodation does not change production permission design.

## Decision

Add `--implementation agy` without changing the default worker/reviewer executor, Codex. Deliver
the shared worker role and the marked `reference/harness-antigravity.md` mechanics, or the existing
reviewer contract, through one stream-json stdin user message. The verified envelope is
`{"event":"user","message":{"content":"<whole prompt>"}}`. Retain the raw events, extract the
final response, record conversation ID and usage, and use `--conversation <id>` for same-lane
worker continuation. Reviewers start fresh in the existing disposable pinned checkout.
A nonzero exit, any denied action, or an invalid/unsuccessful result is a harness failure.

Use `--dangerously-skip-permissions` for both roles, matching the selected host posture. Delete the
orchestrator's blanket bypass prohibition; each harness page owns its permission posture. An agy
reviewer remains read-only by the unchanged judging contract. There is no permission profile,
temporary HOME or MCP filtering in production dispatch. Every configured and enabled agy MCP
server is callable under bypass, so the operator must not configure one a role must not reach.
There is no admission layer; the host currently enables papervault. `--mode auto` is not the
selected posture and has a rollout gap on the qualifying CLI.

The worker anchor is `gemini-3.8-flash` at `high`; the reviewer anchor is `gemini-4-argon` at
`medium`. CLI model IDs encode effort as `<model>-<effort>`; dispatch omits a separate effort flag.
Arbitration defaults to `gemini-4-argon` at `high`, falling back explicitly to Codex `gpt-6-astra`
at `max`, then Claude `fable` at `max`. Each source is fresh and independent, receives the question
on stdin or its native brief, and remains read-only by contract. The caller publishes its answer.

The issue supplies these choices; no other alternatives were part of this worker's design record.

## Consequences

The executor changes the carrier while retaining worker scope, reviewer authority, evidence and
publication duties. A configured agy host needs an authenticated CLI and writable normal runtime
home. Permission bypass also exposes host tools and configured MCP servers: lane and remote-write
boundaries rely on the role contract, not an agy sandbox. The CLI's model IDs and stream event
schema are a compatibility dependency qualified by integration tests and live smoke evidence.
