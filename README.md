# DevStandard

[![CI](https://github.com/LeonJoeeee/devstandard/actions/workflows/ci.yml/badge.svg)](https://github.com/LeonJoeeee/devstandard/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/LeonJoeeee/devstandard)](https://github.com/LeonJoeeee/devstandard/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**The GitHub flow, extended to agent teams.**

DevStandard is a development-method plugin for [Claude Code](https://code.claude.com/docs) — delivered by session hooks (see [Install](#install)) — that can also dispatch [Codex](https://developers.openai.com/codex) as a worker or reviewer. It adds the three things an agent harness doesn't do by itself:

1. **Discipline** — rules an agent won't impose on itself: settle what "done" means before starting, get designs torn apart before writing code, prove completion with evidence, know when to stop and ask you;
2. **Project memory** — a PRD, an architecture doc, a decision log, design specs for substantial changes, and a repo CLAUDE.md only when it has commands, gotchas, a worktree copy-list, or record-language declaration to hold, so parallel sessions (and human teammates) stay aligned on *what*, *how*, and *why*;
3. **Reliable delivery of both** — SessionStart delivers the orchestrator's self-contained role reference. Dispatched workers receive their own complete role context.

The bet behind it: directing agents is the same collaboration problem humans already solved with the GitHub flow — so agents follow the **same** branches / PRs / CI / review process your team already uses, instead of some new agent-coordination scheme ([why](docs/adr/0009-github-flow-extended-to-agent-teams.md)).

## Requirements

- **Claude Code**, with plugin and SessionStart-hook support. It is the only main session ([ADR 0063](docs/adr/0063-claude-code-is-the-only-main-session-codex-executes-when-dispatched.md)); Codex takes part only as a dispatched CLI worker or read-only gating reviewer ([Codex executor](reference/harness-codex.md)).
- **[superpowers](https://github.com/obra/superpowers)** — the craft layer. Install it alongside DevStandard, and into Codex as well if you dispatch Codex lanes (see [Install](#install)): the role pages point to its requirements, debugging, TDD and planning skills, and each executor resolves them from its own host ([ADR 0016](docs/adr/0016-superpowers-becomes-a-dependency.md)).
- **git**, and a **GitHub repo** for the full flow — the generated CI and release pipelines target GitHub Actions. The discipline itself works with any git hosting.
- **Python 3.9+ and an authenticated [`gh`](https://cli.github.com/) CLI** for the shipped commands — the dispatcher, review packets and guarded merge use GitHub through `gh`. Codex process lanes support macOS and Linux using Python's detached-session support; Windows is not qualified ([dispatch guide](reference/orchestrator.md)).
- **For Codex lanes only:** an installed, authenticated Codex CLI with superpowers installed into it, and, on Linux, its [sandbox prerequisites](https://learn.chatgpt.com/docs/sandboxing#prerequisites): the distribution's `bubblewrap` package and, where required, its scoped AppArmor profile.

## Install

**Claude Code.** Inside a session, run:

```
/plugin marketplace add LeonJoeeee/devstandard
/plugin install devstandard@devstandard
```

To check it took: start a new session and ask *"what does DevStandard tell you to do?"* — the agent should recite the trigger rule and the discipline.

Prefer to try before installing? From a shell (affects only that one session):

```bash
git clone https://github.com/LeonJoeeee/devstandard.git
claude --plugin-dir ./devstandard
```

**Updating.** Run `claude plugin marketplace update devstandard && claude plugin update devstandard@devstandard`, then start a new session. Confirm the same way as the install check above.

**Codex lanes.** DevStandard is not installed into Codex: the dispatcher supplies a Codex worker's
role. The worker still invokes superpowers' craft skills, and Codex finds skills only in its own
roots, so install superpowers into Codex from its marketplace:

```sh
codex plugin marketplace add https://github.com/obra/superpowers.git
codex plugin add superpowers@superpowers-dev
```

These command forms are checked against `codex-cli 0.153.4`. If a DevStandard release before 2.0.0
was installed into Codex, remove it with `codex plugin remove devstandard@devstandard`: every hook
Codex has enabled runs in a dispatched Codex child ([Codex executor](reference/harness-codex.md)).

## What you get

- **Set the result and why** — the orchestrator turns them into issues with bounds and observable done-checks. Document and review weight belongs to each task; a demo earns no automatic setup ceremony.
- **Keep one responsive orchestrator** — Claude Code discusses, dispatches, accepts and integrates. Direct work stays small enough not to block that conversation; other concrete work goes to a worker.
- **Run workers in parallel lanes** — one task, branch and worktree each, using Claude Code's native subagents by default. Codex CLI and Claude CLI workers are explicit choices; a Codex CLI worker runs in an OS sandbox scoped to its lane. Workers implement, rebase, prove the final state and deliver a green PR.
- **Accept against the goal** — a clean reviewer judges a green PR under the Goal/Floor/Notes contract. Both review and CI guard integration; architecture direction and major releases remain human-owned.
- **Load the relevant context** — the orchestrator's role reference, which carries the shared workflow with it, arrives at session start; workers receive their own role and execution craft. Other references load at their triggers.

## How you use it

**Day to day** — nothing visible changes. Ask for a bug fix or a small feature in an existing repo and the agent just does it, under standing discipline: it settles what "done" looks like first, and closes with evidence instead of "should work now".

**Starting something new** — say what you want to build and why. The orchestrator clarifies the outcome and chooses task bounds with you. A durable project definition, shared architecture, substantial design, or pipeline task triggers its corresponding document or template; a demo does not inherit a full lifecycle merely because it is new.

**Working a big project in parallel** — discuss direction with one Claude Code orchestrator. It creates issues, cuts independent scopes and dispatches N lanes through the [fixed dispatcher](reference/orchestrator.md). Workers return evidence-bearing PRs, drive CI green, and leave their worktrees for the orchestrator. A clean reviewer judges acceptance, the guarded integration path verifies the result, and the orchestrator closes the issue, cleans up and performs any authorized release. You own direction, irreversible authorization, architecture direction, and major releases.

Execution scales through isolated lanes: the orchestrator keeps direct work short and delegates
anything that would block the coordinating conversation; workers own concrete task lanes.

## What's actually installed

The orchestrator's static context is one self-contained page,
[`reference/orchestrator.md`](reference/orchestrator.md): the shared workflow contract, its event
loop and its operations. SessionStart delivers it inline: in one handler call wherever the host's
own limit admits the whole page, and otherwise across as many ordered calls as it needs — the parts
concatenate to the file's exact bytes — and CI fails any *shipped* artifact that would instead fall
back to an instruction to read it in full. Startup and clear repeat delivery; on compaction a
short notice asks an orchestrator to re-read the page instead, because an Agent child's compaction
fires the same hook naming no child. Runtime evidence and its limits are recorded in
[the architecture](docs/architecture.md).
The worker receives [`reference/worker.md`](reference/worker.md) — as its agent definition body on
the default Claude path, in the brief on the dispatched ones — plus one task packet from the
[fixed dispatcher](reference/orchestrator.md). That page is the shared contract; the mechanics of
the host it is running on come with it, from one page per executor family
([Claude](reference/harness-claude.md), or the worker-facing section of
[the Codex executor page](reference/harness-codex.md)), and a worker is never handed the other's. Those
pages are self-contained together: the role is complete without the orchestrator page. The reviewer judges under the sole
[judging contract](reference/code-review-prompt.md), which the review-packet script fills from
current sources, dispatches, and publishes whole on the PR.
Superpowers bindings live once per role, with Claude worker frontmatter checked against its source.
Explicit process paths are `codex` for Codex CLI and `claude-cli` for Claude CLI workers; `claude`
is the native Claude Agent. Claude CLI uses host/tool permissions and the assigned worktree, while
Codex CLI provides its role sandbox.
Other templates and procedures in [`reference/`](reference/) load at their triggers. The supported
configuration and guard limitations are in [the architecture](docs/architecture.md) and
[the guard guide](reference/orchestrator.md).

**A guard runs before your tools, and it denies with a reason.** `hooks/pre-tool-use` sees every tool
call, reads the command itself — not a here-document body or a quoted string it carries — and
refuses three things, each as a whole word: a worker's `merge`, an orchestrator's `gh pr merge`,
which routes to `scripts/guard merge` instead, and a reviewer's `gh api` write flags. A worker's
push naming the default branch is refused too, until branch protection takes that over. Everything
else is admitted — a tag, a release build, a force-push, an `rm -rf node_modules` — because a word
that refuses reversible work costs more in false refusals than it buys. Shell syntax is never a
reason to refuse, and no network failure can produce one.
**There is nothing to configure** — no settings file, no allowlist, no per-project word list — so
adopting it is installing the plugin. Every refusal is a
reminder rather than a wall: it names the word you wrote, what your role does instead, and the page
to read. This guards the ordinary
case and says so: an interpreter script or an obfuscated spelling is outside it, and `guard merge`,
branch protection and the available host sandbox supply separate enforcement layers. The rule and its limits are in
[the guard guide](reference/orchestrator.md).

## FAQ

**Will it slow down small edits?**
Weight follows the task. A small edit needs no invented PRD, architecture document or ADR;
the ordinary branch/PR gates still apply, with the
[two-checks paragraph](reference/orchestrator.md) naming the narrow exceptions. The agents run the commands.

**What exactly enters my context?**
CI measures every hook output against the host's cap and proves each shipped page arrives
whole, however many outputs it takes. The orchestrator page is delivered at session start; worker
and reviewer context travel through dispatch, except the default Claude worker's role page, which
is its agent definition body. A Codex worker respects existing `AGENTS.md` and explicitly reads the
project's `CLAUDE.md`, which remains the method's operational-memory source.
The [rule ledger](docs/specs/2026-09-06-core-md-rule-ledger.md) records the measurement and carrier choices.

**Does it depend on other plugins?**
One: [superpowers](https://github.com/obra/superpowers). The host supplies mechanics and superpowers supplies craft — at the step where a craft skill helps, the flow names it and the agent invokes it; the skill serves inside that one step, and on any conflict DevStandard's flow wins ([ADR 0016](docs/adr/0016-superpowers-becomes-a-dependency.md)). Two `reference/` files remain adapted from superpowers (MIT, attribution kept).

**Is it for teams or solo?**
The supported configuration is one Claude Code orchestrator per project and N isolated workers.
GitHub holds the durable collaboration record; the [architecture](docs/architecture.md) defines
the supported executor boundaries.

**Can I adopt it on an existing project?**
Yes. Changes are tasks from day one. Add each method document only when its own trigger fires; the paths in the templates are defaults that yield to an established convention, declared by the architecture doc, and a repo-root `CLAUDE.md` exists only when it has an admitted line to hold (`reference/in-repo-writes.md`).

## Layout

```
hooks/           SessionStart delivery and the per-role word-list PreToolUse guard
scripts/         the shipped machinery — fixed dispatcher, review packets, guarded merge
agents/          Claude-native worker and reviewer definitions
reference/       the self-contained orchestrator and worker role pages, each carrying
                 the shared workflow, role interlock, resident triggers, clean handback
                 and PR-green — and, on the orchestrator page, executor dispatch,
                 guarded operations and the worktree checklist — plus one file per
                 thing they still point at: PRD / architecture / ADR /
                 design-spec templates, CI + release pipelines, red-check
                 and CI-fallback rules, reviewer
                 prompt, where files go (where-it-goes.md — not a
                 router or classifier), out-of-repo writes, in-repo document
                 admission, repo CLAUDE.md admission
docs/            DevStandard's own PRD, architecture doc, and decision log
_source/         the research this design stands on
```

DevStandard was built with its own rules. Its `docs/` holds a real PRD, architecture doc, and an ADR log recording why every major call went the way it did — including the ones that got overturned (0001 → 0007, 0002 → 0016, 0003 → 0008, 0004 → 0014, 0005 → 0015, and the rebuild's own supersessions: 0038/0039 → 0045 → 0056 → 0063, 0006/0008 → 0047, 0014 → 0048). That log is the best demo of what the method produces.

## License

MIT.
