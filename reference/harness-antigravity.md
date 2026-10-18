# DevStandard's Antigravity CLI executor

Antigravity is a dispatched CLI executor, not the method's host. Use
`scripts/dispatch ... --implementation agy --wait` for a worker and
`scripts/review-packet start ... --implementation agy --wait` for a fresh gating reviewer.
The dispatcher owns the child process and the existing independent one-off reviewer checkout;
`reference/orchestrator.md` owns selection and `reference/code-review-prompt.md` owns review authority.

## Prerequisites and permissions

`agy` must be on PATH and authenticated. Its consumer token lives at
`~/.gemini/antigravity-cli/antigravity-oauth-token`; its normal host HOME must permit conversation
and artifact persistence. A readable token alone does not prove authentication: verify a model turn.
Workers need their role's superpowers skills installed in the agy host.

Both roles run with `--dangerously-skip-permissions`, reporting `permission_mode: always-proceed`.
The reviewer is read-only by contract in its disposable checkout; dispatch adds no permission
profile, temporary HOME or MCP filter. The bypass makes every configured and enabled agy MCP
server callable. The operator must not configure a server a role must not reach; there is no
admission layer. The qualifying host has papervault enabled. This is host/tool permission access,
not an independent OS sandbox restricting the worker to its lane.

`--mode auto` is a rollout gap on the qualifying CLI: a listed flag is not evidence that the mode
is available to the account. Dispatch uses the settled bypass posture rather than relying on auto.

## Headless input, results and continuation

The worker anchor is `gemini-3.8-flash` at `high`; the reviewer anchor is `gemini-4-argon` at
`medium`. Dispatch passes `--model MODEL-EFFORT` (for example `gemini-3.8-flash-high`) and omits
`--effort`: a separately specified effort must match the decorated model or the CLI refuses it.

A short standalone prompt may use `-p=<prompt>`. Full briefs and packets always use
`--input-format stream-json --output-format stream-json`, with one NDJSON stdin message:

```json
{"event":"user","message":{"content":"<whole brief or packet>"}}
```

The envelope is verified on agy 1.4.2. `type: user` and `event: user_message` are invalid. No prompt
is placed in argv or truncated. The `init` event names the conversation and permission mode; the
final `{"event":"result","result":{...}}` contains `status`, `response`, `conversation_id` and
`usage`. Dispatch keeps the raw stream at the run's `events` path, writes the final response to
`output`, and records conversation and usage in the returned run and completed issue receipt.
Nonzero exit, any nonempty `denied_actions` in any event, unsuccessful status, or malformed/missing
final result is a harness failure. A later success cannot erase an earlier denial.

A continuing worker uses `--conversation <recorded-id>` in the same lane. The full current brief
still arrives on stdin. Reviewers always start a fresh process without conversation history.
If posting the completed issue receipt fails, dispatch preserves the observed run in stdout with
`receipt_error` and `receipt` (the saved comment path), and exits 2. Retry
`gh issue comment ISSUE --repo REPO --body-file RECEIPT` before continuing a worker, so its
conversation remains recoverable. The reviewer result remains available for normal publication.
Run directories and output remain until lane cleanup; process exit is not task acceptance.
Python dispatch supports macOS/Linux; Windows is not qualified.

<!-- BEGIN ANTIGRAVITY WORKER MECHANICS -->
## Worker mechanics

`scripts/dispatch` delivers this section with `reference/worker.md` to every Antigravity CLI worker.
That page is the contract; this section describes the agy harness beneath it.

An Antigravity CLI worker runs under host/tool permissions with `--dangerously-skip-permissions`.
The assigned branch and worktree bound its authority; agy adds no independent OS sandbox. Every
configured and enabled MCP server is callable. Task-local helpers use agy's native subagent tools,
never another CLI process or the orchestrator's dispatch scripts.

The CLI begins in its lane. When it is a linked worktree on a matching `task/<issue>-...` branch,
`origin` identifies the repository. The latest matching `devstandard-dispatch-v1` process-run
receipt names the lane and its absolute brief holds the packet in full. The receipt fits only when
branch and worktree match exactly and all required fields are present. A missing, equally-new or
unreadable receipt or brief leaves the binding unrecovered; a checkout summary is not the packet.
Continuation uses the completed receipt's `conversation_id` in this same lane.
<!-- END ANTIGRAVITY WORKER MECHANICS -->
