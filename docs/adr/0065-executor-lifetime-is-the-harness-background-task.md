# 0065 — Executor lifetime is the harness background task

Status: Accepted (2026-10-18). Amends 0056 and 0063 (CLI lifetime and reviewer-copy ownership).

**Scope: this ADR decides what the method ships.** Issue #517 fixes the executor process structure
and the orchestrator's invocation convention.

## Context

Two requirements decide liveness: a dispatched executor finishing must wake the orchestrator
immediately, without cron or polling delay; an executor dying silently must wake it through the
same exit notification. Claude Code session death is excluded: if that session dies, the run is
abandoned.

Detached supervision, completion and launch-failure marker files, exact-run reconciliation and the
sentinel watcher served session survival. The watcher also required the orchestrator to remember
a second step after dispatch, which it did not perform in practice. The advisory lock guarded a
double-writer failure that has never been observed. Neither mechanism earns its cost under this
scope.

## Decision

Keep explicit `--wait` and require it for CLI dispatch. Dispatch starts the executor as its own
child, waits in-process, and exits with the observed result. Its returned JSON retains the signed
executor exit code; signal deaths produce a nonzero shell status of 128 plus the signal number.
The issue-side run record, lane, brief, output and log paths stay.

Codex `review-packet start --wait` waits for dispatch, records its return and publishes the whole
verdict itself before exiting. No verdict means a failed attempt without a returned round. While
the reviewer has not exited, the attempt remains pending even if output already exists. Native
Claude review keeps its existing caller-publication contract. Dispatch owns creation and removal of
the independent reviewer checkout before returning. If publication fails, start includes its observed
return in the harness task output. Publication retry can explicitly consume that captured output,
bound to the same attempt and pinned reviewer; it discovers no process or lifecycle file.

Run dispatch and Codex review start as harness background tasks. The harness's native task-exit
notification supplies the wakeup for normal completion and silent executor death. Read the output
and report; process exit remains distinct from task acceptance.

Rejected alternatives, from the accepted issue:

- Detached supervision and lost-run reconciliation: they exist to outlive the session, which is
  excluded.
- Sentinel watchers or marker polling: they add a remembered arming step and a polling delay.
- An executor timeout: Codex has not been observed failing to exit; add one only after a real
  incident.
- Advisory locking and its liveness checks: the guarded double-writer failure has not been
  observed; add one only after a real incident.

## Consequences

Process structure carries liveness, with no background observer, lifecycle files or reconciliation
path. One orchestrator still owns one executor per lane. Session death offers no recovery promise;
a reviewer that remains running remains pending. The integration tests exercise real parent/child
relationships, signal exits, synchronous whole-verdict publication and round accounting. Native
harness notification timing still requires live-host qualification.

This changes the CLI contract: non-waiting dispatch is removed and dispatch now propagates nonzero
executor results. The implementing PR carries the synchronized 3.0.0 major version bump.
