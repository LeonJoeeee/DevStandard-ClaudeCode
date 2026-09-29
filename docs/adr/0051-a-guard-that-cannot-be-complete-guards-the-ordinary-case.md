# 0051 — A guard that cannot be complete guards the ordinary case

Status: Accepted (2026-09-10). Amends 0046 (role hooks). Amended by 0052 (2026-09-10). Amended (2026-09-11). Amended by 0055 (2026-09-11). Amended by 0056 (2026-09-11). Amended (2026-09-12). Amended by 0062 (2026-09-20). Amended (2026-09-20). Amended by 0063 (2026-09-29).

## Context

The role hook is what stands between a role and an operation it must never perform. Between
2026-09-05 and 2026-09-10 it grew to meet each new spelling a review round found: a closed lexical
shell grammar with separators, redirections, wrappers and reserved words; a ten-family refusal table
for the syntax that grammar could not model; a second text scan for the orchestrator when the
grammar gave up; a per-tool-call read of `.github/devstandard-guards.json` from the **remote**
default branch through four GitHub API calls; a bounded retry layer for the transport failures that
read produced on a flapping network; and a head-bound authorization record for every irreversible
orchestrator command.

That machinery cost seven review rounds and three releases over 2026-09-09/10. It refused a worker's
`cd <worktree> && git push --force-with-lease`, a `for` loop over `echo`, a `$(printf …)` inside a
`--jq` argument and a multi-line `python3 -c` — ordinary research and delivery commands, none of
them dangerous. It turned a dropped network connection into a refusal a worker was told to retry.
And it never claimed to be complete: ADR 0046's own limitation sentence says this implementation
"does not claim an arbitrary-shell capability boundary," and the shipped page said in as many words
that an interpreter script or an obfuscated spelling passes it. Each round added weight to a fence
whose gate was documented as open.

The human ruled on 2026-09-10: 实在控制不住那就算了，出问题就出问题吧 — a guard that cannot be
complete should guard only the ordinary case, with a rule simple enough to hold in one's head, and
the residual should be accepted rather than chased.

## Decision

**The hook does one thing.** It reads the command's raw text — quotes, here-doc bodies and
substitution bodies included, with no parsing and no grammar — and refuses when that text carries
one of its role's words. A word matches where it begins at a non-identifier position and is not
continued by a hyphen; a rule of several words matches only where those words stand together.
**Unparseable syntax is never a reason to refuse, for any role.**

- **worker:** `merge`, `tag`, `release`, `--force`, `branch -D`, `branch --delete`, `push --delete`,
  `worktree remove`; a recursive `rm` whose targets are not under `/tmp/`; and `push` only where the
  same command also names the default branch. Everything else is admitted, its own task-branch push
  and any composition around it included.
- **reviewer:** read-only — `push`, `merge`, `tag`, `release`, `delete`, `rm`, and a `gh` command's
  `-X`, `--method`, `-f`, `-F`, `--input`. The reviewer agent definition keeps its tool surface.
- **orchestrator:** `gh pr merge` and `git merge`, refused with the reason naming the sole admitted
  entry `<plugin>/scripts/guard merge`; a `push` naming the default branch; and `tag`/`release`
  unless default-branch policy relays a standing release delegation.

**The policy is local.** `.github/devstandard-guards.json` is read once per hook process from the
local `origin/main` ref with `git show`, never over the network inside a tool call and never from
the working tree. A missing ref, a missing file, a directory outside any repository or unparseable
JSON all mean the built-in defaults. **Nothing in the hook refuses because a read failed**, so the
transport-failure vocabulary, the retry layer and the distinct "policy read that could not happen"
reason all go with it.

**One record survives.** `guard merge` still requires the human's head-bound
`devstandard-authorization-v1` comment for an architecture-level merge, and is now its only reader.
Deleting a merged branch or worktree is routine teardown and is admitted with no record. `guard
protection --apply` is not gated by the hook at all; it stays the human's or the main session's by
role instruction and by who holds admin credentials.

**Every refusal is a reminder, not a wall** (the same day's ruling): a worker that reaches for
`merge` has usually forgotten which lane it is in rather than defected, and the harness feeds the
refusal text back to the model as the tool result. One template per role, stated once in code,
fills in the word the caller actually wrote, what the role does instead, the one page and section
to read, and — because a textual scan will sometimes hit a `grep`, a commit message or an issue
body that merely spells a word — how to re-spell so the word is absent (put the text in a file and
pass the file; search with a pattern that does not spell it). That detour is legitimate and the
pages say so; passing a refused *operation* under another spelling is not.

**The residual is named and accepted.** Obfuscation, an interpreter script, a forged local ref and
an operation read from runtime data are outside this hook and no rule will be added for them. What
carries the guarantee is the rest of the guard: `guard merge`'s reviewed-head verification, rebase
proof and GitHub reads; branch protection; and the per-role OS sandbox. **A review finding of that
class is a Note, not a defect** — and that clause is the operative half of this decision, because
without it the next round rebuilds the table.

The alternative rejected is the one the last six days took: extend recognition to each newly found
spelling. It converges on a complete shell parser, which the hook is not, cannot become in a
PreToolUse handler, and would still lose to `bash -c "$(curl …)"`.

## What this supersedes

These changes are removed here rather than layered under, and are named so the record shows what
was undone: **#240**, admitting routine worker commands by extending the grammar; **#248**, quoted
literal patterns in the role hooks; **#302's hook half only** — the no-repository refusal shape,
while its seeded policy file, its CI template and its founding-push admission all stay, the last of
them restated in this decision; **#312**, the orchestrator's second, unparsed text scan with
`UNPARSED_INDICATORS`, unnecessary once nothing is parsed; **#320**, the `cd <lane worktree> &&`
composition rule, for the same reason; and **#321**, `PolicyUnreadable`, the bounded transport
retry and the unresolvable-remote shape, all consequences of the remote read this decision replaces
with a local one.

The guard side is untouched: **#223**'s `guard merge`, **#231**, **#233**, **#255**, **#262**,
**#283**, **#289**, **#290** and **#307** keep their behaviour, their own GitHub reads and their
own tests. What changed for the authorization record is the number of its readers — `guard merge`
is now the only one — not the record, its shape, or the merge path it gates.

## Consequences

Refusals are cheaper and more legible: a refusal names a word the caller actually wrote, and every
ordinary command a role runs is admitted. Three behaviours narrow — a worker no longer gets a
recognized-operation exception for `--force-if-includes` alone, a target's `command_patterns` are
now per-role words rather than per-kind regexes, and a repository whose default branch is not `main`
runs on built-in defaults. Three widen: a reviewer's non-`gh` read commands are no longer checked
against an allowlist, an orchestrator's destructive commands outside its three rules are admitted,
and `guard protection --apply` is admitted for every role. Both directions ship in one minor version.

`.github/test-hard-edges.py` keeps a sweep so a regression in the word list still shows, over each
role's words in the bare, quoted, here-doc, substitution and `cd … &&` positions and both tool-input
formats, plus a fixture that decides identically with every network call failing. The adversarial
grammar sweep is deleted rather than weakened, and its sixteen CI shards become two: the suite that
took minutes now runs in seconds. No probe asserts a refusal for an obfuscated construction, because
such a probe would encode a boundary this hook does not claim.

**This ADR decides what the method ships**, not only how this repository operates: every seeded
project's role hook behaves this way.

**Amendment (2026-09-10, see 0052):** the Decision's *"The policy is local"* paragraph is retired,
not relocated. `.github/devstandard-guards.json` is deleted, and with it every rule that existed to
read it: `settings_for`, `POLICY_PATH`, `policy_words`, `command_patterns`, `default_branches`,
`standing_delegation` and the founding carve-out. **Nothing in the hook reads anything** — the word
lists are in the source, and the default branch is `main` or `master` by name. That paragraph's
guarantee holds a fortiori: a read that does not exist cannot fail.

Two clauses of the Decision's role lists change with it. The orchestrator's *"`tag`/`release` unless
default-branch policy relays a standing release delegation"* is deleted: releasing is `core.md`'s
rule and the human's call, not a word list's. The orchestrator's *"a `push` naming the default
branch"* is deleted too, so the founding push needs no exception. **What survives unchanged is this
ADR's operative half** — the raw-text scan, the boundary rule, one word list per role, unparseable
syntax never a reason to refuse, every refusal written as a reminder, and *a review finding of the
residual class is a Note*. The Consequences' *"a target's `command_patterns` are now per-role words"*
is overtaken: a target adds no words at all. `reference/hard-edges.md` carries the operative
wording.

**Amendment (2026-09-11, issue #334):** the per-role tool allowlists are deleted, and with them
the Decision's reviewer clause *"The reviewer agent definition keeps its tool surface"* as a
statement about the hook. `READ_TOOLS`, `WORKER_TOOLS`, `REVIEWER_TOOLS`, the two `tool not in`
checks and the orchestrator's tool-name regex are gone: **the hook judges a command's raw text by
its role's word list and never a tool name**, so every tool call that is not a shell command is
admitted for every role.

The allowlist was the *enumerate what is allowed* shape this ADR rejected for commands and left
standing for tool names, and it forbade useful work rather than a wrong act: a worker could not
spawn the read-only helper review `reference/worker.md` requires, because `Agent`, `Task` and
Codex's `spawn_agent` all sat outside `WORKER_TOOLS`. It guarded nothing the word lists do not.

**The rule of shape behind the removal**, in the human's words (2026-09-11): a hard limit — a
hook, a guard, a tool denial — is reserved for the very serious or the fully forbidden, and is
always a blacklist of the few acts, never an allowlist of what is permitted
("尽可能使用黑名单而非白名单"). So no allowlist survives anywhere: the agent definitions drop
their `tools` lists as well, and `agents/reviewer.md` and `agents/helper.md` name only what they
forbid — `disallowedTools: Write, Edit, NotebookEdit` — while `agents/worker.md` forbids nothing
and inherits the session's whole tool set. Read-only stays check 1's property, carried by that
denial, by the reviewer's `gh` write-flag filter (always a command rule, and unchanged), and, where
Codex is the executor, by the per-role sandbox.

The residual widens by two named cases, accepted under this ADR's own rule rather than answered
with a new one. A subagent runs under the hook its own definition declares, or the spawning
session's where it declares none, so a role that deliberately spawns a general-purpose agent can
reach a command its own role refuses — the deliberate-evasion class. And with no tool lists, every
role reaches every MCP tool the host session has attached, including ones that act outside the
repository; the hook reads commands, not tool calls, so it cannot see them, and the remedy is to
not attach such a server to a session that runs workers rather than to write a list. The
reviewed-head verification in `guard merge` plus branch protection still carry the
guarantee. `reference/hard-edges.md` carries the operative wording.

**Amendment (2026-09-11, see 0055):** `agents/helper.md` no longer exists. The block above names the
helper twice — once as the file, once as the review. In the list of what a definition forbids, read
it as: `agents/reviewer.md` names only what it forbids — `disallowedTools: Write, Edit,
NotebookEdit` — and `agents/worker.md` forbids nothing.
In the allowlist's cost, *"a worker could not spawn the read-only helper review `reference/worker.md`
requires"* records what was true on 2026-09-11 and stays as history: since 0055 that page requires no
such review, because the method governs the GitHub-collaboration layer and nothing below a role.
**This ADR's own decision is untouched** — the hook judges a command's raw text by its role's word
list and never a tool name, and a worker still reaches `Agent` to spawn subagents of its own; what
changed is only that the method no longer names one of them.

**Amendment (2026-09-11, see 0056):** 0056 adds native Codex workers and explicit Claude CLI workers.
The per-role OS sandbox clauses apply to Codex CLI; the new worker paths retain host/tool
permissions and must use the assigned worktree. Gating review uses a qualified read-only
implementation. Unclassified native child events carrying `agent_id` use the worker word list after
explicit role, recognized agent type and process-marker bindings. The command-only word lists,
blacklist shape and accepted residual remain; `reference/hard-edges.md` owns the operative boundary.

**Amendment (2026-09-12, issue #351):** the Decision's *"It reads the command's raw text — quotes,
here-doc bodies and substitution bodies included"* now reads: it reads the command's own text, with
**here-document bodies and quoted-string contents removed** and substitution bodies still read. And
*"A word matches where it begins at a non-identifier position and is not continued by a hyphen"*
gains its second boundary: a word also ends where the text continues neither an identifier nor a
hyphenated word, so `merge` no longer reads `merged` or `--merged`, `tag` no longer `--tags`, and
`rm` no longer `rmdir`. A `gh` write flag keeps the older boundary, because an option and the value
written onto it are one word to the shell: `-X` still reads `-XPOST`. Everything else in the
Decision stands, the word lists unchanged. The 2026-09-11 blocks above restate *"a command's raw
text"* twice; they take the same correction, and what they were saying — **never a tool name** — is
untouched.

Reading text that is never a command was this ADR's own failure mode in reverse. It refused a
Codex worker writing a draft test with `cat > t.py <<'EOF'` because a local `threading.Event` was
named `release`; it refused an orchestrator filing an issue whose `--body` prose named a lifecycle
command; it refused a `git branch --merged` and a `grep` for `merged-result`. Two lanes and three
orchestrator rounds went to it. A here-document body or a quoted commit message is never the
forgotten `git merge main` this hook exists to remind someone of, so refusing it reminds nobody of
anything — the reminder rule above is what the old reading contradicted, not merely a cost it paid.
The fix removes text from what the scan reads and narrows a match to whole words; it adds no word,
no configuration and no grammar. Removal is one-directional — the quote characters and the line
structure stay, so nothing removed can join two fragments into a word nobody wrote — with one
place where it could have bitten: the `/tmp/` cleanup exemption reads targets rather than words, so
that rule reads them from the command as written too, and `rm -rf "/tmp/x"` stays admitted.

**The residual widens by three named cases**, accepted under this ADR's own rule rather than
answered with a new one: an interpreter given its script as a quoted argument (`sh -c "git merge
main"`) or as a here-document (`bash <<EOF`); a word quoted as its own argument to the command that
runs it (`git "merge" main`, `git push "--force" origin task/x`); and a spelling that puts a
guarded word inside a longer one (`git push origin --tags`). The first two are the
interpreter/obfuscation class this ADR already accepts — writing a command that way is a deliberate
act, never the forgotten lane a refusal exists to remind someone of — and `.github/test-hard-edges.py`
records all three as behaviour. **A review finding of that class is a
Note.** `reference/hard-edges.md` carries the operative wording; the sweep positions named in the
Consequences below are history of what #323 built, and the suite now requires the quoted and
here-doc positions to admit what the bare, substitution and composed positions refuse.

**Amendment (2026-09-20, see 0062):** the Decision's three role lists are replaced by three rules —
**worker:** `merge`; **reviewer:** a `gh` command's `-X`, `--method`, `-f`, `-F`, `--input`;
**orchestrator:** `gh pr merge`. The worker's `push` naming the default branch survives beside them
for the window before branch protection is applied. Every other word in those bullets is deleted:
the worker's `tag`, `release`, `--force`, `branch -D`, `branch --delete`, `push --delete` and
`worktree remove`; the recursive-`rm` rule and its `/tmp/` carve-out; and the reviewer's whole
`push`, `merge`, `tag`, `release`, `delete`, `rm` list. So is the fourth part of the refusal text —
*"how to re-spell so the word is absent"* — which existed to route around refusals these three do
not make; a refusal now names the word, what the role does instead, and the one page.

**This ADR's operative half is what did the removing.** *A guard that cannot be complete guards the
ordinary case* was applied to its own lists: a word earns its place only where the act it names is
irreversible and no other layer stops it. Each deleted word failed that bar in both directions at
once — `tag` refused a reversible local `git tag` while admitting `git push --tags`, `release`
refused `cargo build --release`, `--force` stranded a worker on its own briefed lease-protected push
(#236), and the reviewer's list admitted `gh pr comment`, `gh pr review --approve` and `gh pr edit`,
so it never carried the independence its name claimed. The *"residual is named and accepted"* clause
governs what widens, unchanged: read-only is `agents/reviewer.md`'s writer denial and the Codex
`-s read-only` sandbox, and a recursive `rm` in a disposable worktree whose branch is already pushed
is the lane's own business. `reference/orchestrator.md`'s Guarded operations section carries the
operative wording.

**Amendment (2026-09-20, issue #433):** each block above that routes the operative wording to
`reference/hard-edges.md` names a page that does not exist; `reference/orchestrator.md`'s Guarded
operations section carries it, as the 0062 block above already says.

**Amendment (2026-09-20, issue #437):** the hook fails open. Its top-level handler turned every
exception into `deny: guard refused: …`, so one defect below the decision — or one malformed host
event — denied every tool call in every lane at once, which is #338's shape surviving the remote
read that motivated it. It now admits the call and writes one line to stderr naming the error. The
Decision's *"Nothing in the hook refuses because a read failed"* becomes the whole error path's
rule: **nothing in the hook refuses because the hook broke.** Only the word rules refuse, and they
are unchanged. The residual this widens is named like every other: a guard whose own code is broken
guards nothing until someone fixes it, and denying everything meanwhile is not a stricter fence —
it is an outage, on the side of the layers this ADR says carry the real guarantee.

**Amendment (2026-09-29, see 0063):** 0063 removes native Codex workers. The role hook keeps the
fallback that gives a child event carrying `agent_id` but no agent type the worker list, because
removing it could only loosen the guard for an untyped child event. The Codex CLI sandbox clauses
and Claude CLI workers' host/tool permissions are unchanged; `reference/orchestrator.md`'s Guarded
operations section owns the operative boundary.
