# 0041 — Seeded projects admit documents deliberately and hand back clean trees

Status: Accepted (2026-08-28). Amends 0012 (pre-handback cleanup before teardown inventory), 0017
(trigger gating and established path selection for every document kind), and 0018 (its write-back is
limited to the existing `CLAUDE.md` fence). Amended by 0042 (2026-08-31). Amended (2026-10-08).

## Context

ADR 0037 decides where an agent may write when the destination is outside its repository. The method
still treated “write to the repo” as sufficient authority. In seeded projects that left two durable
gaps: an agent could invent a handoff or a second copy of an architectural authority, and an untracked
artifact could survive every diff review one `git add -A` away from becoming part of the record.

The named project documents already had individual triggers, and worktree teardown already refused to
eat unknown work. What was missing was a general admission decision before a document is added and a
pre-write baseline that distinguishes the doer's artifacts from state it inherited.

## Decision

DevStandard governs the repositories it seeds with two sibling rules:

- `reference/in-repo-writes.md` admits an added document only when its method trigger fired, an
  established convention in the pinned pre-work base both owns the kind and reached its creation
  condition, or a durable authority requested it. Method triggers and `CLAUDE.md`'s content fence
  cannot be bypassed by the other arms. Established locations may replace default paths, declared by
  the canonical architecture entry point. Handoff/session state must qualify on every edit, and two
  competing authorities at one scope are forbidden.
- `reference/clean-handback.md` requires every doer to record and publish a
  `git status --porcelain -uall` baseline before task-generated writes, compare it after the final
  repository-touching command, and commit or remove every new visible path. The doer deletes only
  artifacts it created and knows are disposable; unknown or inherited state is surfaced and blocks
  handback until its owner decides.

The issue or PR carries task state. A CI path-shape assertion guards this repository's own canonical
Markdown layout; semantic admission remains merge check 1 because a clean checkout cannot infer why a
document exists, and it cannot see a local leftover that never entered the commit.

Rejected: a filename allowlist as the method's semantic rule (it rejects legitimate project
conventions and admits unnecessary documents with plausible names); allowing an established handoff
custom (session end is the defect); and deleting everything not in the diff (a worktree can contain
copy-listed secrets, configuration, or seeded data the doer does not own).

## Consequences

Every task pays one pre-write and one final status snapshot. Added documentation has a decidable
provenance, adopted repositories keep established locations without growing competing trees, and
session state stays on GitHub instead of becoming a new source of truth. Cleanup happens before
delivery; worktree Death remains the surface-never-eat backstop for anything still unexplained.

Ignored paths remain outside the promise, and semantic admission remains a reviewer duty. Those are
explicit limits rather than claims CI cannot support. This is shipped method for seeded projects, not
a maintenance-only rule for the DevStandard repository.

**Amendment (2026-08-31, see 0042):** the commit-or-remove arm is qualified: a new visible path is
committed only when it is material the repo maintains, and otherwise removed. “Ignored paths remain
outside the promise” describes snapshot visibility and ignored paths nobody has named; it does not
license losing a known must-keep artifact. Any kept file whose only durable copy is in the worktree is
named and moved out or discarded before teardown, even when the snapshot cannot see it.

**Amendment (2026-10-08, issue #503):** the Decision's claim that `CLAUDE.md`'s content fence
cannot be bypassed is retired. `reference/in-repo-writes.md` still admits the repo-root file on
its own trigger — operational memory needs an update — and reserves that entry point, but tests
none of its content. `reference/repo-claude-md.md` offers guidance; the repository owner chooses
what the file holds. The predicate's other arms and method triggers are unchanged. What a
document is still governs every edit: a handoff or session-state artifact must qualify on every
edit whatever its path, syntax, or extension, including when it is called `CLAUDE.md`. The clean-tree
and competing-authority rules stand, as does the operational write-back duty.
