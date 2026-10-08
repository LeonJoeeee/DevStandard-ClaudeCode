# 0030 — A practice useful only for maintaining this plugin lives in its repo `CLAUDE.md`, not in the shipped pages

Status: Accepted (2026-08-06). Amended (2026-08-13). Amended (2026-10-08). Amends 0027 (its rule is withdrawn from the shipped method and
kept as repo practice), 0022 (the second doc-duty pass it added), 0018 (this repo carries a
root `CLAUDE.md` again, and its content fence widens here only), and 0029 (a pointer of its own
that this withdrawal stales).

## Context

The human drew a line this method had never stated: **the rules we use *to build* DevStandard
and the rules DevStandard *ships* are two different things, and an observation from the first
does not become a rule in the second.** Nothing in the review discipline asked that question —
every check-1 prompt asked whether the text was correct, complete and internally consistent,
never whether the rule belonged. Fitness-for-audience had no slot.

ADR 0027's two-pass sweep is the clearest instance. It was derived entirely from maintaining
*this* repo — six recorded cases (issue #79), all of them prose in a methodology project — and
then written into `core.md`, the page every session of every project is forced to read. Its
cost, measured across the three shipped pages:

| Page | Cost | Read by |
|---|---|---|
| `core.md` | **162 tokens** | every session, every project, forced |
| `aids/worker-brief.md` | 282 tokens | every dispatched worker |
| `aids/code-review-prompt.md` | 238 tokens | every check-1 reviewer |

**Where the product is code, the compiler catches most of this; here it catches none of it.**
Rename a function and the compiler names every caller; change an interface and the tests go red.
Reword a rule and nothing responds. The residue is real anywhere — a string-keyed config value
renamed, a rate limit stated in an OpenAPI description and a runbook, a review policy stated in
`CONTRIBUTING.md` and an ADR — but it is occasional there and constant here: a target project
building an application hits it rarely; we hit it six times in one PR. **The decisive argument is
frequency against price, not impossibility** — 162 tokens on a 5,000-token page every project
reads every session, for a rule whose whole evidence base and whose site list are ours.

Two symptoms had already been filed separately and are closed by this: the shipped checklist
enumerated *this plugin's own directory layout* — "the aids, the howtos" — to readers who have
neither (#87), and the whole question of whether the rule belonged (#90).

## Decision

**The sweep rule is withdrawn from the shipped method**, in all three places, together with the
four pointers that referenced it from `core.md`'s flow step and worker DO list, and from
`aids/worker-brief.md`'s DO list and Done line. `core.md` returns to **4,380 tokens**, its
v0.15.0 figure minus the rule.

**It is kept, operative, in a repo-root `CLAUDE.md`** — which is not part of the method, which no
shipped page points at, and which only a session opened on *this* repository reads. (It is copied
into the plugin package like `docs/` and `_source/`, where nothing reads it: Claude Code loads a
*project's* `CLAUDE.md`, never a plugin's.) The rule is real and
it earns its keep here: it caught three separate defects during the 0028/0029 work alone.

**And the general form, which is the part worth having:** *a practice useful only for
maintaining this project lives in the repo `CLAUDE.md`; the shipped pages carry only what a
target project needs.* This is the first artifact of the repo-ops/method distinction, and it
gives the distinction somewhere to live instead of being re-derived per change.

**The release delegation moves in with it.** Issue #37's standing delegation of per-release
approval had lost both doc homes it was given — the repo `CLAUDE.md` deleted in v0.12.1 and the
CHANGELOG header deleted in 0029 — leaving it reachable only by grepping the ADR log (#100, and
the reviewer of PR #101 confirmed the index does not lead to it). It belongs in exactly the file
this ADR re-creates.

**0018's conditional is met, and this ADR widens it for this repository only.** 0018 as amended
prescribes a repo-root `CLAUDE.md` when a project has something operational to declare, and
recorded that this repo then had nothing unique — true in v0.12.1, no longer. But 0018's Decision
fences the file to *commands, gotchas and the worktree copy-list, and nothing else*, and
`howto/cicd.md` ships that fence with one conditional fourth item — a `## Record language` line,
which it calls "the fence's only exception". Repo-ops practice is an **additional kind beyond
both**, admitted here for this repo alone; the shipped fence is unchanged for target projects. Saying the
conditional is simply "satisfied" would widen a shipped rule without deciding it.

Rejected: (a) **split the rule** — keep the "why" in `core.md` (~20 tokens) and move the
procedure to `howto/` — the author's recommendation, and the human's first instruction. Rejected
by the human on reading the full text: *"这里面的东西对于我们做别的东西都没有用"* — the whole
clause, not merely its procedure, is about maintaining this project. Keeping a 20-token stub on
the forced-read page would leave a rule with no operative content for its stated audience.
(b) **Delete it outright, keeping only ADR 0027 as history** — knowledge preserved, practice
lost: no agent reads an ADR at the moment it rewords a rule, so the three failure modes would
return. (c) **Keep it in `howto/`** — still ships, still names our directories, still asks a
target project to carry a page it does not need. (d) **Generalise the wording in place**
(#90's leading option) — drop our directory names, trigger on "a statement that exists in more
than one place", keep it on `core.md`. Rejected by the same reading: generalising the wording
does not change whose problem it is, and it keeps the full price on the forced-read page.

## Consequences

`core.md` regains **180 tokens** (4,560 → 4,380), and the two aids lose 520 more that every
worker and every reviewer was carrying. The shipped surface now states nothing about `aids/` or
`howto/` as places a *target project* should search, which closes #87 as a side effect rather
than as its own change.

**What is lost, and it is not nothing:** the reviewer no longer has a check item for this, so
the failure mode's backstop is gone from the one party that caught most instances. In this repo
that is covered — check-1 reviewers are dispatched from here and this `CLAUDE.md` is in their
session's repo. It is not covered for a target project, which is the point: the rule was never
theirs.

**One clause was deleted with it and has been put back, on check 1's ruling.** The reviewer check
item carried *"a rewritten ADR body is Critical"* — a check on `howto/adr.md`'s
supersede-never-edit rule, which is shipped method and survives. It was flagged rather than
smuggled, and check 1 ruled it belongs back on its own merits: `docs/adr/` is prescribed for
**every** project, `howto/adr.md` is read at project start rather than when a diff quietly edits
an ADR, and the failure is the irreversible kind — a rewritten body silently replaces what the
next session re-derives the *why* from, with nothing later to contradict it. Restored to
`aids/code-review-prompt.md` at 56 tokens, on an on-demand aid, off `core.md`'s budget.

What to watch: whether the repo `CLAUDE.md` accumulates. It has four sections and a stated
admission test; the signal is not a count but the first entry that fails the test — a rule a
target project would also need, parked here because here was convenient.

**Amendment (2026-08-13, caused by 0031):** the `howto/cicd.md` named above as shipping the three-kinds
fence is now `reference/repo-claude-md.md`. **Cleared as decision-time reasoning rather than
reconciled would have been defensible** — the sentence argues *why* the fence justified widening,
which is history — **but 0018's own amendment, written the same day by the same change, reconciled
the twin of this sentence.** Reconciling one of a pair and clearing the other is how a log starts
disagreeing with itself, so it is reconciled here too and the split is stated rather than left
silent.

**Amendment (2026-10-08, issue #503):** the 2026-08-13 block's paired routing statement is
reconciled alongside 0018: `reference/repo-claude-md.md` now carries content recommendations and
an example, not an admissibility fence. The Decision's argument for widening the then-existing
fence is decision-time reasoning and stays as history; a repository owner no longer needs that
content exception. The distinction this ADR decided — repo-only practice here, shipped method
on the target-facing pages — stands.
