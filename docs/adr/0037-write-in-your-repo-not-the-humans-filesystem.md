# 0037 — An agent writes in its repo, not across the human's filesystem

Status: Accepted (2026-08-25). Amends 0018 (its Gotchas kind gains a declared out-of-repo root; the
one-page fence and the three-kinds rule are unchanged). Amended by 0042 (2026-08-31). Amended
(2026-09-07). Amended (2026-10-07).

## Context

`core.md`'s "Stay in your own repo" governs *other repositories*: a session works the repo it was
opened for and files an issue rather than editing a neighbour. The filesystem *between* repositories
had no rule at all — no page named `$HOME`, `~/Desktop`, `/tmp`, or any scratch location. So every
agent defaulted to the one place a shell starts, and the defaults accumulated.

An audit of one human's `$HOME` (issue #147) found nine agent-created entries, none the human's:
18 GB of model weights at `~/data/mage-vl` (an `hf download` that overrode HuggingFace's own cache to
build the path by hand), a 19 GB `~/services` deploy root, tool clones at `~/tools` and `~/labs`, a
perception log at `~/memory`, and deliverables dropped on the Desktop. The directory had been cleaned
once, three weeks earlier, and refilled. Cleaning is not the fix; the missing rule is.

Three of the nine are outside anything a method text can reach, and are scoped out rather than
counted: `~/memory` (OpenClaw — never a DevStandard session), three unattributable directories, and
six `~/.claude.json.tmp.*` files that are the harness's own atomic-write leftovers, not an agent
decision. The rule forecloses the path that produced the other six; it does not claim to have cleaned
a directory.

## Decision

**An agent writes to the repo it works in, to the scratch its session provides, or to a location a
tool's own documented convention or the repo's own docs name — and nowhere else. The human's home
directory and Desktop are theirs, exactly as another repository is.** The operative rule lives in
`reference/out-of-repo-writes.md`; `core.md`'s "Stay in your own repo" bullet gains the trigger.

Four calls in it were each forced by a review round and are recorded so a future session does not
reopen them:

**The line is conventional, not visible.** A tool's documented cache (`~/.cache/huggingface`, `~/.npm`)
is fine; `~/data/x` and `~/.mydata/x` are both an agent inventing a location, and the dot changes
nothing. An earlier draft drew the line at "visible", which permitted an invented dot-directory —
exactly the clutter the human objected to, which is not about what `ls` shows.

**"Invented" is the agent choosing the location itself.** A path the human handed over, or the repo's
own docs declare, is not invented — the same escape "Stay in your own repo" gives for another
repository. This reconciles "never under `$HOME`" with "a location the repo's docs name": a declared
`~/services` is named, not invented.

**The undeclared case is an ask, not a new axis, and it does not collide with the "act on your own"
default.** `core.md`'s ask-rule is exclusive ("Ask the human ONLY when…"), so a new "ask here" sentence
would lose to it under pressure — the failure two draft rounds hit from opposite directions. The fix
is to widen the rule's own third axis: "anything leaving the repo" now names a durable write onto the
human's filesystem with no place declared. A worker's equivalent is a new stop-list entry in
`reference/worker-brief.md`. **Rejected: adding the stop-list entry without the frequency defense** —
a stop-trigger for a frequent, cheap event is the one ADR 0026 Rejected (c) says gets ignored. It
survives because it is rare by construction (only a durable write with no tool default and no declared
root fires it) and **self-extinguishing**: the escalation's natural resolution is a declared root in
that repo's `CLAUDE.md`, after which every later write of that kind takes the silent declared-root
branch. The entry fires roughly once per repo per class of need, then never again.

**Disclosure is a discipline, not a gate — and the method says which.** An out-of-repo write leaves no
trace in a git diff when it is done by an ad hoc command, which is what every audited row was; merge
check 1 sees the diff and the report and nothing else, so it cannot catch an omission. A write the
diff *commits* — in a script, a Makefile, a CI step — is reviewable like any line, and the reviewer
prompt flags an invented location there. The rest is a disclosure the acting agent makes in the PR,
the same ungated shape ADR 0036 named for executor attribution; the reviewer asks where a write went
when a task plainly needed one, as a question, not a blocking finding.

Rejected: **a method-chosen default path** — the opinion the method refuses for deploy targets and
model tiers alike. Rejected: **routing the undeclared case through "touches top-level design"** — its
definition (structure, interfaces, dependencies, a quality goal) does not admit a filesystem location,
so a literal reader proceeds.

## Consequences

`core.md`'s "Stay in your own repo" bullet gains the filesystem half and the widened third ask-axis;
`reference/out-of-repo-writes.md` (new) carries the full rule; `reference/worker-brief.md` gains a
before-you-write trigger, a stop-list entry, and a disclosure line in Done; `reference/code-review-prompt.md`
gains a reviewer line, self-contained because a clean reviewer cannot open this file;
`reference/repo-claude-md.md`'s Gotchas gains a declared-root line, argued in its own prose as an
environment gotcha of the existing kind. `docs/architecture.md` §2 and `README.md`'s two enumerations
list the new file.

**Amendment to ADR 0018, below and on its status line**, records the fence ruling where 0018's own
history keeps such rulings, following the 2026-08-06 precedent (0030) of arguing new content fits an
existing kind rather than widening the fence to a new one.

What to watch: whether the disclosure duty is kept, given nothing enforces it — the same watch ADR
0036 set for attribution, and the same honest answer, that this is guidance and the method does not
pretend otherwise.

**Amendment (2026-08-31, see 0042):** `reference/where-it-goes.md` is now the placement entry point,
replacing both live routing claims above that name `reference/out-of-repo-writes.md` as the operative
or full rule. This ADR's undeclared-case ask, the widened ask-axis, and the worker stop trigger now
apply only after the entry point has established that a write belongs outside the project; the
ordinary unnamed case takes the in-project default instead. The former “rare by construction (only a
durable write with no tool default and no declared root)” frequency defence no longer holds: a secret or
confidential file, application state for a program that outlives the task, or a release deliverable
may ask whether or not the write is durable.

A documented cache remains fine unless it would be the only durable copy of something that must be
kept. Disclosure is narrowed to every durable external write and names the PR or, where there is no
PR, the handback. Both claims above that a repo document names an external destination are qualified:
the destination or an authority assigning it to this project must already exist, or the human must
choose it; the document only relays that authority and never originates it. A same-change document
may repeat an already-existing target, but cannot invent one, and a handoff or session-state document
relays nothing either way. Finally, “Rejected: a method-chosen default path” refused a default outside
the project; it does not refuse the ordinary in-project default recorded by 0042.

**Amendment (2026-09-07, issue #279):** the Decision's *"A worker's equivalent is a new stop-list
entry in `reference/worker-brief.md`"* names a page #235 reduced to a compatibility pointer and #270
deleted. `reference/worker.md` carries both halves this ADR placed on a worker, in the shape the
2026-08-31 block above left them: the placement stop — no assigned place for secret or confidential
data, for state belonging to a program that outlives the task, or for a release deliverable means
stop and return to the orchestrator, taken only after `reference/where-it-goes.md` has established
that the write belongs outside the project — and the disclosure duty, which names every durable
write outside the repo, with its path and reason, in the PR. The Consequences sentence listing which
files that change touched is history and stays as written. The rule and the narrowed frequency
defence are unchanged.

**Amendment (2026-10-07, issue #478):** the Consequences' rationale that a clean reviewer cannot
open this file no longer describes its capabilities. CLI reviewers can read repository files and
network history from an independent pinned checkout; native Claude reviewers retain the session's
directory and follow the written prohibition on file changes. The self-contained placement rule
still belongs in the review prompt so the judging context receives it whole. The placement,
disclosure and finding rules above are unchanged.
