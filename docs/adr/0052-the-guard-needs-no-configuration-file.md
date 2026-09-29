# 0052 — The guard needs no configuration file

Status: Accepted (2026-09-10). Amends 0046 (authorization record, founding admission) and 0051 (the
policy read). Amended by 0056 (2026-09-11). Amended (2026-09-13). Amended (2026-09-20). Amended by
0062 (2026-09-20). Amended by 0063 (2026-09-29).

## Context

ADR 0051 cut the role hook down to one rule per role on 2026-09-10 and left the configuration file
it read standing. The rest of that day showed what the file was still costing. Reading the layers
back in the order they were built:

1. **A hook**, to stop a subagent writing to GitHub in a way its role must never write.
2. **A policy file**, so the hook could know who the human was, which checks to require, which
   branch was the default one, and whether a release had been delegated — facts the hook did not
   have and could not derive.
3. **Rules for reading the file**: where to read it from so an unmerged edit granted nothing (a
   remote ref, then a local one), what to do when the read failed (transport classification, a
   bounded retry, a distinct refusal reason), and what a repository being *founded* did before the
   file existed (the founding carve-out, then the narrowing of its protection half).
4. **An issue about where the file lives** (#303, #321), because a hook that reads a file has to
   decide what a missing repository, a missing ref and unparseable JSON each mean.

Every layer solved the problem the previous layer created. Nothing in layers 2–4 guarded anything a
role must never do; they existed so layer 1 could run. The human's ruling on 2026-09-10:
每次遇到一个问题，考虑的永远不是"减"…最后去擦一大堆屁股 — the answer to a problem is never
subtraction, and it ends in cleaning up after a pile of them.

The measurement that makes this concrete: none of the retired pieces ever refused an operation a
role must not perform. The one that came closest — the head-bound `devstandard-authorization-v1`
record — was a publishing-identity check on an account the agents also use, and it said so in its
own documentation.

## Decision

**The hook stays, with its refusals as reminders. Everything that exists only to feed it goes.**

**Zero configuration.** The word lists per role are in the source. The default branch is `main` or
`master`, by name; a repository that calls its default branch something else is outside the worker's
push rule, and nothing the hook could read would tell it otherwise. There is **no policy read at
all**: `settings_for`, `POLICY_PATH`, `policy_words`, `command_patterns`, `default_branches`,
`standing_delegation` and the founding carve-out are deleted, and the hook decides in a bare
directory that is no repository at all exactly as it decides inside one.

**The orchestrator's push to the default branch is admitted, with no rule and no exception.**
Founding means those first commits to land there, and once founding has applied branch protection
GitHub rejects the push server-side — which is the layer that check belongs to. The founding
exception is now the absence of a rule rather than a carve-out with a condition to prove.

**Release is not the hook's business.** `tag` and `release` leave the orchestrator's word list.
`core.md` already says releasing needs the human's authorization or the project's standing
delegation; the orchestrator follows the page, not a machine-readable record of it. The
`standing_release` field, its read and the release-command recognition go.

**`guard merge` keeps its own GitHub reads and drops the policy.** It requires the whole verdict on
the PR, the merged-result check pinned to this exact base and head, every observed check on the head
green — the #314 fallback becomes the only rule, with no `required_checks` list anywhere — and it
merges with squash. An **architecture-level PR needs one comment of the repository owner's own on
that PR**, the owner read from the repository's API record. There is no JSON record, no
authorization issue (#204) and no `human_logins` / `record_logins` / `authorization_issue`.
`guard protection --apply` takes its check names from `--check` on the command line and refuses with
none rather than PUT an empty context list.

**Founding seeds nothing.** `reference/prd.md`'s setup sequence loses the authorization-issue step
and the policy-file step; the shipped template file and this repository's own policy file are
deleted in the same change; and `CLAUDE.md` records the release delegation as issue #37 and nothing
machine-readable.

**A review finding of the form "a subagent could now do X by tampering or obfuscating" is a Note.**
This is ADR 0051's residual clause applied to what this ADR removes, and it is operative for the
same reason: without it the next round rebuilds the file. The pieces retired here never stopped such
a subagent; what does is `guard merge`'s reviewed-head verification, GitHub's branch protection, and
the per-role OS sandbox.

The alternative rejected is the one the file was heading for: keep it, and add a rule for each thing
a reader of it must now decide. That is the chain above, and it converges on maintaining a
configuration language for a fence whose gate is documented as open.

## Consequences

The method is smaller in the way that matters to a reader: adopting the guard is installing the
plugin, and founding a repository is three steps instead of five. A whole class of failure — an
unreadable file, a malformed field, a policy that says one thing while the tree says another —
cannot happen, because there is nothing to read.

Four behaviours narrow or widen, and both directions ship in one minor version. **Widened:** an
orchestrator's `tag`, `release` and default-branch `push` are admitted by the hook, so the
discipline behind them is the role's page rather than a refusal. **Narrowed:** a target can no
longer add its own words for a role, rename the integration check, name its required contexts, or
declare a third default-branch name — a project needing any of those changes its own CI job names
or accepts that the rule does not cover it.

The architecture-level sign-off changes shape rather than strength. It was a record on an issue
under an allowlist; it is now a comment on the PR under the repository's owner. Both are
publishing-identity checks on an account the agents can also use, and neither is proof that a human
typed it — which the pages have always said. What changes is that a human signing off now does the
obvious thing, on the change itself, and nothing has to be kept in step for it to work.

`.github/test-hard-edges.py` keeps the word-list sweep unchanged in mechanism — every role's words
across the bare, quoted, here-doc, substitution and `cd … && …` positions and both tool-input
formats — with the orchestrator's retired words removed from its table and its admitted list gaining
the founding push and the release commands. The policy, authorization-record, standing-delegation
and founding-carve-out probes are deleted rather than weakened; a new fixture shows the hook
deciding in a bare directory with no repository and inside one with every network call failing, and
`guard merge`'s four refusals and its squash merge are probed against a doubled PR.

**This ADR decides what the method ships**, not only how this repository operates: every seeded
project's guard behaves this way, and no seeded project receives a configuration file.

**Amendment (2026-09-11, see 0056):** Under 0056, the per-role OS sandbox clause applies to Codex
CLI. Native Codex and Claude CLI workers retain host/tool permissions and their assigned-worktree
duty; they do not supply a per-child read-only sandbox. The guard still has no configuration file,
and the command-word-list and accepted-residual decisions stand. See `reference/external-agent.md`
for the implementation boundaries.

**Amendment (2026-09-13, issue #361):** the owner-comment architecture gate is deleted rather than
reshaped again. No incident justified it, and the same shared owner credentials that made it a
publishing-identity check also let an agent satisfy it alone. The architecture-level declaration
still selects review depth and routing, and the human-wait rule remains in `core.md` and
`reference/orchestrator.md`; it is no longer enforced by a comment predicate in the guard. The
all-observed-green rule remains the integration check and still has no configured name list.

**Amendment (2026-09-20, issue #426):** the Decision's *"every observed check on the head green"*,
and with it the 2026-09-13 block's closing *"The all-observed-green rule remains the integration
check and still has no configured name list"*, narrow to: no observed check may have failed. The
pinned merged-result check must still be `success`, a head reporting no check at all still refuses,
and there is still no configured name list anywhere; what goes is the refusal on a pending or
skipped check nothing requires. `reference/orchestrator.md`'s Merge and rebase proof section carries
the operative wording.

**Amendment (2026-09-20, see 0062):** the Decision's *"Release is not the hook's business"* now
holds for every role, not the orchestrator alone: `tag` and `release` leave the worker's and the
reviewer's lists too, and `reference/orchestrator.md` — prose — is the only thing that decides a
release. The Decision's *"The word lists per role are in the source"* and the zero-configuration
guarantee are untouched; what changed is only how much source there is. The Consequences'
**Widened** sentence gains the lane roles' `tag`, `release`, `--force`, branch and worktree
deletion and recursive `rm`, and the orchestrator's local `git merge`; the discipline behind each
is the role's page rather than a refusal, exactly as that sentence already says for the
orchestrator's three. `.github/test-hard-edges.py` keeps the sweep unchanged in mechanism, with the
retired words moved from its refusal table to a table of the benign work each one used to refuse.

**Amendment (2026-09-29, see 0063):** 0063 removes native Codex workers. The per-role OS sandbox
applies to the Codex CLI; Claude-native and Claude CLI workers retain host/tool permissions and
their assigned-worktree duty. The guard still has no configuration file;
`reference/orchestrator.md`'s Dispatching to an executor section owns the implementation boundaries.
