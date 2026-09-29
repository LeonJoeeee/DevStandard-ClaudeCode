# 0059 — Each role page is self-contained; there is no shared core page

Status: Accepted (2026-09-14). Amended by 0060 (2026-09-15). Amended (2026-09-20). Amended by 0063 (2026-09-29).

**Scope: this ADR decides what the method ships.** `reference/orchestrator.md` and
`reference/worker.md` each carry the whole contract their role needs; this record carries the
reason and the transition it was made through.

## Context

`core.md` was delivered to every role. An orchestrator session therefore read the worktree,
red-check and PR-ownership triggers written for workers, and a worker read the commissioning,
merge and release instructions written for the orchestrator. Every session paid for the other
role's rules, on a method whose stated end is returning the human's scarce time.

The second cost was drift. The shared page and the two role pages restated each other, and a
change that updated one statement and not the others left them disagreeing; four such live
contradictions stood on `main` on the morning of 2026-09-14. Nothing mechanical catches a stale
restatement of prose, so each one survived until a reader happened to hit both sites.

An earlier lane (issue #385, PR #388) tried to fix this in one diff: decide what was
orchestrator-facing, move it, apply an audit's cuts and restructure the result. Check 1 returned
Floor 1, correctly — a reviewer cannot tell whether a sentence is absent because it was
deliberately cut or because it was dropped in the move. The human ruled that the order should be
reversed: copy first, edit second.

The shape was also constrained by a measurement rather than by the reader. A role page had to fit
one hook output, so what a role could be told was bounded by a delivery limit.

## Decision

**Role pages are self-contained per role, not a shared core plus a role supplement.** Each role
page carries the shared workflow contract, the role interlock and the resident triggers together
with its own operations. A session receives exactly one page for its role, and `core.md` no longer
exists. Which carrier brings it is the host's, not this decision's: the SessionStart hook for an
orchestrator session, the dispatch brief for a CLI or native-Codex worker, and — on the default
native Claude Agent path, whose prompt is the task packet alone — an instructed IN FULL read of the
named role source, which `agents/worker.md` has always required and which no constructed test can
witness a model performing (`docs/architecture.md` records that as **Unverified**).

**The transition is a verbatim copy followed by a separate review.** `core.md`'s bytes were
appended, unchanged and in order, to both role pages under one heading; nothing was reordered,
deduplicated, compressed or corrected in that step, and the only edits to the surrounding pages
were pointers that named the deleted file. That leaves both pages repetitive and badly ordered on
purpose: it makes the copy mechanically provable, so the editing pass that follows is reviewed as
editing rather than as a move. Doing both at once is what Floor 1 rejected.

**Delivery stops capping a page.** An artifact larger than one hook output is emitted across as
many ordered handler calls as `hooks/hooks.json` declares, and the parts concatenate — with
nothing between them — to the file's exact bytes. The calls are ordered; their arrival is not. A
host appends each part's context as that handler's process finishes, and the same three-part page
reached Claude Code sessions in all six orders of its parts. Each part therefore carries its own
number and says the parts may appear in any order, and both the delivery's instruction and both
hosts' tests reassemble by number rather than by position. The cap in `hooks/session-start` now
bounds one part. A page the declared handlers cannot carry, or one whose single line exceeds a
part, degrades visibly to an instructed read, which CI refuses for any shipped artifact; losing a
page's tail in silence is the one outcome worse than asking for a read.

Two alternatives were rejected. Keeping the shared page and trimming it addresses neither cost:
each role still reads the other's rules, and two statements of one rule still drift. Splitting the
content by judging each sentence's audience during the move is the combined diff that already
failed review.

Earlier delivery decisions stand as written: 0007 (the hook injects one page, no router), 0019 and
0049 (role context is injected per artifact) recorded what was true when they were made. Which page
the hook injects, and that one artifact may take several outputs, is decided here.

## Consequences

**The duplication is real and must be maintained as duplication.** The shared clauses now exist in
two files, and nothing mechanical reconciles them. Rewording one of them means rewording the other
in the same diff — the *search twice* discipline this repository already follows, now with a known
second site rather than a discovered one. That is the price paid for each role reading only its own
page, and it was accepted knowing that the earlier arrangement also duplicated these clauses, less
visibly and with a third copy to keep in step.

**Nothing about what a role pays changes at the transition.** An orchestrator session received the
two artifacts' bytes before and receives the same content as one page after; a worker likewise.
Only the shape changed, which is what made the step safe to take without judgement.

**A role page can now be as long as the role needs.** Length is still a cost every session pays and
is still argued page by page, but it is no longer settled by a delivery limit. The gate that used to
enforce a byte budget now proves that every shipped artifact arrives whole through the handlers
declared for it.

**The per-part cap is now the smaller of two measured host limits, and it is measured.** Claude
Code persists a SessionStart `additionalContext` whose stored JSON reaches about 10,000 characters
to a file and injects a 2KB preview and that path instead; Codex drops the middle of anything above
its per-handler token limit. Neither had been measured against a page large enough to reach it,
because until this change no shipped artifact came close. The cap in `hooks/session-start` now sits
under both, bounds one part, and is proved by both hosts' real-CLI tests: they take each part out
of the host's own model request, reassemble by part number, and compare the result to the file's
bytes — not a header line that survives truncation, and not each part searched for on its own,
which is text presence rather than the page.

**Claude Code compaction has no shared page to fall back on.** A native Agent child's compaction
fires the main session's hook with no agent identity (issue #375), so that source cannot prove it is
an orchestrator and must not receive the orchestrator page. The shared page used to be what arrived
there and asked an orchestrator to re-read its own. A short role-neutral notice now carries that ask
and tells a dispatched worker or reviewer not to act on it.

**The editing pass is owed.** Both pages are repetitive and out of order until issue #385 reviews
and restructures them. That work is reviewable as editing precisely because this step lost nothing.

**Amendment (2026-09-15, see 0060):** the Decision's carrier sentence — *"on the default native
Claude Agent path, whose prompt is the task packet alone — an instructed IN FULL read of the named
role source, which `agents/worker.md` has always required and which no constructed test can witness
a model performing"* — no longer describes that path. `agents/worker.md`'s body is now
`reference/worker.md` verbatim, so the harness loads the page as the subagent's system prompt: the
worker receives it with no read, and `.github/test-claude-runtime.py` asserts its byte-identical
arrival rather than recording an unproven carrier. The decision this amends is untouched — each role
page is still self-contained, and which carrier brings it is still the host's — only the fourth
carrier changed.

**Amendment (2026-09-20, issue #415):** the Consequence headed *"The per-part cap is now the
smaller of two measured host limits, and it is measured"*, and its sentence *"The cap in
`hooks/session-start` now sits under both"*, no longer describe the arrangement. There is no single
number under both limits: the cap is per host, and the two are defined beside each other in
`hooks/session-start` — `CLAUDE_CAP_BYTES` under Claude Code's fixed persistence boundary,
`CODEX_CAP_BYTES` under the `additionalContextLimit` ceiling measured on codex-cli 0.153.4, which is
high enough that every shipped artifact reaches a Codex session in one part while the Claude host
still splits. `hooks/hooks.json` declares a handler set per host to match, and why that shape was
kept rather than one set serving both hosts is recorded beside `CODEX_CAP_BYTES`. Each cap is still
measured, and the rest of this ADR is untouched: delivery still does not cap a page, and how large
one output may be is still the host's answer rather than ours.

**Amendment (2026-09-29, see 0063):** 0063 removes the Codex host. `hooks/session-start` defines one
cap, `CLAUDE_CAP_BYTES`, and `hooks/hooks.json` declares one handler set whose handlers name the
artifact, part and total and no host; `CODEX_CAP_BYTES` and the per-host sets are gone. So is the
native-Codex carrier: a Codex CLI worker's carrier is the dispatch brief, and
`.github/test-claude-runtime.py` is the one real-CLI delivery test.
