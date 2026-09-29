# DevStandard — Collaboration-model architecture

> Shared baseline for all parallel work. Read before any task. Changing anything here = touching
> the core: public merge + human approval + an ADR.

This document defines the supplementary harness required by the three target workflows in PRD §4. It
does not repeat those workflows or the working rules held by their role pages. It defines the
roles, context boundaries, delivery paths, enforcement points, and concurrency behavior from which
the rebuild is implemented. Every structure named here is traced to a PRD §1 pain point or a PRD §2
reuse decision in the closing table.

Delivery and enforcement statements use two labels. **Verified** means the behavior was measured or
the artifact was inspected, and names its source. **Unverified** means the architecture requires the
behavior but the rebuild has not demonstrated it. A design requirement is not treated as a fact
about a native harness. Unless a paragraph or evidence cell says **Verified**, mechanisms described
here are **Unverified** target requirements.

## 1. Scope and configuration

The supported configuration is one Claude Code orchestrator with N dispatched executors. A
dispatched executor has one of two purposes, worker or reviewer. Implementations are Claude-native
subagents, Codex CLI processes and Claude CLI workers. A conflict resolver is a
worker assigned a conflict task, not a third role. This is the smallest configuration that removes scheduling from the human while
retaining the GitHub flow and native isolation mechanisms (PRD §1.1, §2.1, §2.2).

DevStandard is a supplementary harness. The host owns its sessions, hooks, native subagents,
tools, models and permissions; a dispatched Codex CLI process also owns its sandbox. Claude CLI
workers use host/tool permissions and the assigned worktree. DevStandard supplies the
missing collaboration protocol: role context, dispatch, acceptance, and the transitions between
GitHub artifacts. It replaces neither the native harness nor the Codex CLI's (PRD §1.1, §1.5).

**It governs one layer: the collaboration with GitHub — issue, lane, PR, review, merge — and
nothing below a role.** What a dispatched role spawns beneath itself to finish its own task touches
none of those artifacts, so this design neither names nor requires any such subagent; what it
requires of a lane is that one accountable author hands back one PR (ADR 0055). The gating reviews
above a role — merge check 1 and the pre-code design challenge, both commissioned by the
orchestrator and published on the PR — are inside this layer and unaffected.

ADR 0063 makes Claude Code the only main session on the human's ruling
([issue #459](https://github.com/LeonJoeeee/devstandard/issues/459)), superseding ADR 0056's Codex
host restoration: as a main session Codex follows its own harness rather than the method. Codex
remains a dispatched executor — the `codex` CLI for a worker or an independent read-only gating
reviewer — and `reference/harness-codex.md` owns its mechanics. Workers retain their internal
delegation under ADR 0055. Separate live-session lanes, Codex custom agent configuration and
workflow panels are not required (PRD §1.6).

**Verified — repository source:** the plugin ships the Claude manifest and marketplace, a
SessionStart script delivering the orchestrator page, and the dispatcher. Codex CLI briefs deliver
the worker role source plus the Codex worker section. Dispatch installs only the fixed role hook,
bound to the child's role; a DevStandard startup hook left from a pre-2.0 Codex install still runs
under the invocation-wide trust bypass, and their `DEVSTANDARD_ROLE` silences it. Codex executor qualification, and the record of
the removed host, are under **Codex qualification (2026-09-11, #342; host removed 2026-09-29, #459)**
below.

The durable coordination state is GitHub: issues declare work, branches and worktrees isolate it,
PRs deliver it, review records acceptance, and CI plus branch protection gate integration. Native
task handles, process identifiers, and output files are transient observations, not a second state
machine (PRD §2.1, §2.2).

## 2. Roles and context sets

### Orchestrator

The orchestrator converses with the human, completes an issue with the settled result and reason
after the human confirms the handover,
partitions concurrent work, dispatches executors, observes delivery, assembles acceptance reviews,
merges accepted work, and performs cleanup and delegated release. Its context set contains:

- the workflow contract and the three events that wait on the human;
- open-issue, open-PR, CI, branch, and worktree state needed to run the main loop;
- the dispatch, acceptance, merge, cleanup, and reporting triggers with pointers to their operative
  procedures;
- requirements-clarification skill bindings used while discussing direction with the human; and
- the rule that implementation craft and a worker's task-local procedure are not loaded into the
  orchestrator set.

This set keeps the main conversation responsive and stops the human from becoming the scheduler
(PRD §1.1). It delivers assumed working conventions to every new orchestrator session (PRD §1.5)
without mixing in the worker set described below.

### Dispatched executor: purpose × implementation

There is one dispatched-executor construct. Purpose determines its context and authority;
implementation determines how that context is delivered.

| Purpose | Claude-native | Codex CLI | Claude CLI | Result |
|---|---|---|---|---|
| Worker | `devstandard:worker`'s body is `reference/worker.md` followed by `reference/harness-claude.md`, concatenated byte for byte, so the harness carries the contract and this harness's mechanics as the subagent's system prompt with no read (ADR 0060, ADR 0061); its frontmatter fixes the skill and hook bindings, and dispatch supplies the issue, lane and explicit purpose-routed model/effort. | Dispatch supplies the shared role plus `reference/harness-codex.md`'s worker-facing section, the task, explicit settings and a sandbox granting the worktree plus required linked-worktree git metadata. | Explicit worker process with the same role/task and assigned worktree, using host/tool permissions and noninteractive `acceptEdits`, without a sandbox bypass. | A green PR linked to the issue, rebased on current `main`, with final-state evidence. |
| Reviewer | `devstandard:reviewer` fixes the judging role, empty skills and denial of built-in writers; dispatch explicitly supplies purpose-routed model/effort. The packet supplies the review instance. | Dispatch supplies the judging contract and packet, explicit settings and an OS read-only sandbox. | Refused before mutation: no qualified per-child read-only sandbox. | A verdict naming the reviewer and reviewed head, published whole on the PR. |

The Claude carriers are the whole shipped set of agent definitions, `agents/worker.md` and
`agents/reviewer.md`. `agents/worker.md` is hand-authored frontmatter plus a body generated from two
hand-written sources — `reference/worker.md` then `reference/harness-claude.md`, concatenated byte
for byte with nothing between them; `.github/check-agents.py` asserts that exact body and
regenerates it under `--write`. The body is the only carrier that delivers the Claude harness page
to a Claude worker at all (ADR 0061). A role's own subagents
are not a third one: they sit below the governed layer (§1), so v0.45.0's `devstandard:helper`
definition and the pre-handback review it was required for are removed (ADR 0055).

The routing rule is ADR 0040 as amended by 0063: dispatch defaults to a Claude-native subagent,
and the human's instruction — for one dispatch, or standing until their next — selects Codex
CLI execution instead. A native receipt requires the actual Agent tool; a prepared receipt is not a
launched worker. The choice
changes delivery, not purpose or obligations. Explicit binding prevents invented working conventions
(PRD §1.5); role-based skill bindings reuse the superpowers library at the step where its craft is needed (PRD §2.3).

### Worker context set

The worker set consists of the static role plus one dynamic task packet.

The static role binds the worker to PRD §4 Workflow 3: one issue, branch, and worktree; write
authority only in that lane; evidence and attribution duties; the NEVER and escalation boundaries;
and the execution-skill triggers, including test-driven development and systematic debugging. The
task packet supplies the freshly fetched whole issue — body and ordered non-record comments
verbatim — with named base, branch, worktree, required inputs, and expected output. It carries no
merge, release, or orchestration procedure. This separates execution from integration and makes a
worker's claim inspectable rather than trusted (PRD §1.2, §1.5, §2.3).

### Reviewer context set

Reviewer is the read-only purpose of the dispatched-executor family. Its static set is the judging
contract from issue #183 and PR #188: Goal verdict first, the two-check Floor second, and Notes last.
Only the Goal verdict and Floor decide readiness; Notes neither block nor trigger another review
round. The reviewer has no craft skills because it reads and rules rather than builds (PRD §1.4).

An ordinary review packet contains the issue's goal, bounds, and done-check; the PR description as
the fulfillment claim; explicit review-base and head SHAs; the convention base; the accepted-spec
blob or `NONE`; the architecture-level flag; the CI-configuration paths the diff touches, so a green
run the diff configured cannot vouch for it; the in-repo-write predicate; an assembly report naming
what it pinned and what it could not; and the published CI-fallback comment only when the fallback
has been declared. Beside those slots it carries the complete issue body as
quoted evidence, the three contract sections still deciding the verdict
(`reference/code-review-prompt.md`). The reviewer sees no orchestrator history and treats
supplied claims as unverified (PRD §1.2, §1.4).

### Resolver

A resolver is a worker whose issue-sized assignment is to rebase a delivered branch that conflicts
with current `main`. It receives the ordinary worker set plus the delivered PR, old and new bases,
the conflicting paths, and the original issue contract. It may change only that lane, reruns the
original done-check on the resolved final state, republishes evidence, and returns the new head for
fresh review. It never receives merge authority (PRD §1.2, §2.2).

## 3. Context delivery

Static role content has one operative source per role: the orchestrator role reference, the worker
role reference, and `reference/code-review-prompt.md` for the reviewer. The worker's is a contract
only; the mechanics of its host come from one page per executor family, `reference/harness-claude.md`
or `reference/harness-codex.md`'s worker-facing section, and a worker is delivered its own and never
the other's (ADR 0061). Agent definitions and
dispatch prompts are delivery carriers, not independently edited copies. Each role page is
self-contained: it carries the shared workflow contract, triggers and pointers together with that
role's own operations, so a role reads one page and never the other role's (ADR 0059) — plus, for a
worker, its own harness page, which is delivered with the contract rather than read from a pointer. This
arrangement addresses convention loss without rebuilding another incident-driven rules layer
(PRD §1.5, §1.6).

Rebuild 5's implementation sources are `reference/orchestrator.md` and `reference/worker.md`.
**The one-release compatibility pointer was removed 2026-09-07 (#206, #269)**, so no compatibility
pointer resolves beside them; a dispatched worker also holds its own harness page, delivered with
the contract rather than resolved from a pointer (ADR 0061). The hook-cap measurement, per-artifact carrier qualification
and source-rule dispositions are recorded in `docs/specs/2026-09-06-core-md-rule-ledger.md`. That
implementation evidence qualifies the dated delivery requirements below; it does not requalify the
unrelated executor/enforcement claims.

Under the human's [delivery ruling](https://github.com/LeonJoeeee/devstandard/issues/179#issuecomment-5550401101),
direct context injection is the default delivery for every static context set. The concrete
mechanism for each artifact is inline injection; an artifact larger than one hook output is emitted
across as many ordered handler calls as `hooks/hooks.json` declares, and the parts concatenate to
the file's exact bytes, so a role page's size is no longer a design constraint (ADR 0059). How large
one output may be is the **host's** answer — Claude Code's fixed persistence boundary — and a page
the whole-page cap admits is never split (human ruling,
[issue #415](https://github.com/LeonJoeeee/devstandard/issues/415)). The calls
are ordered and their arrival is not — a host appends each part as its handler process finishes — so
each part carries its number and is reassembled by number, never by position (#396); part 1 carries
the full preamble and every later part one line, because the concatenation and trigger rules are
stated once. An
instructed read survives only as the visible degraded mode for a page the declared handlers cannot
carry, which CI refuses for any shipped artifact. **Verified — repository source:**
`hooks/session-start` and `.github/check-core-budget.py` implement the per-part cap recorded in the
rule ledger above and the reconstruction the parts owe. **Verified — real CLI:**
`.github/test-claude-runtime.py` takes each delivered part out of the host's own model request,
reassembles by part number and compares the result to the file's bytes (#396). The two mechanisms
have an identical caching profile, so the choice is about reliability, not caching cost
([measurement and caching record](https://github.com/LeonJoeeee/devstandard/issues/179#issuecomment-5550375489);
PRD §1.5, §5). The cap governs our own carrier choice alone and binds one part, not one page.

**Per source:** startup and clear deliver the orchestrator page; compaction delivers no role page at
all, because a Claude Agent child's compaction fires the main-session SessionStart carrying the root
session's `session_id` and `transcript_path` and no agent identity at all, so that source cannot
tell a dispatched worker from an orchestrator (measured on Claude Code 2.1.270,
[issue #375](https://github.com/LeonJoeeee/devstandard/issues/375)) — a short role-neutral notice
asks an orchestrator for the page there, and tells a dispatched role not to read it. CLI
workers/reviewers receive the role in their brief and suppress orchestrator startup delivery. A
Codex environment running the hook is an unsupported one and gets a visible warning instead of the
method (ADR 0063) (PRD §1.5, §1.6).

| Context and executor | Delivery path | Evidence state |
|---|---|---|
| Orchestrator static set | Claude Code's SessionStart hook delivers the orchestrator's self-contained page under the rule above: inline, in as many ordered parts as the host's cap needs — one part where that cap admits the whole page. It supplies the workflow entry point, and the same trigger repeats after a context clear; after compaction the role-neutral notice takes its place — per the source rule above. | **Verified — repository source:** `hooks/hooks.json`, `hooks/session-start`, and the local CI hook gates show one output per delivered part — every part within the host's measured cap, the parts reconstructing the file byte for byte, and the IN FULL read only when the declared handlers cannot carry the page — on the unchanged matchers, the compact source delivering the notice and not the role page, and the delivery gate failing a page its handlers do not cover (#258, #375, #396; ADR 0049, ADR 0059). Native startup is qualified below; persistent UI lifecycle behavior remains **Unverified**. |
| Claude-native worker static set | The `devstandard:worker` agent definition supplies model settings and execution-skill bindings in its frontmatter, and the worker role itself as its body: that body is `reference/worker.md` followed by `reference/harness-claude.md`, concatenated byte for byte, so the harness loads both pages as the subagent's system prompt (#402, ADR 0060; #409, ADR 0061). | **Verified — [issue #187](https://github.com/LeonJoeeee/devstandard/issues/187) and [issue #179's enforcement-tier ruling](https://github.com/LeonJoeeee/devstandard/issues/179#issuecomment-5488257766):** the recorded native-subagent probe found that a subagent receives neither the session hook nor the method automatically **at spawn**, where SubagentStart carries neither — which is why the definition, not a hook, is the carrier. **Verified — [issue #375](https://github.com/LeonJoeeee/devstandard/issues/375):** its *compaction* does reach the main-session SessionStart, identifying no agent, which is why that source no longer delivers the orchestrator page (per the source rule above). The current agent definition is qualified below. **Verified — real CLI:** since #402 the definition's body is the role source itself, and `.github/test-claude-runtime.py` asserts each page of that body — and since #409 their exact concatenation — arrives byte-identical, exactly once, in the host request for the CLI worker and the native Agent child; no model read stands between the pages and the worker. |
| Claude-native worker task | The dispatcher validates the lane, then prepares the Agent receipt with base, inputs and output duty. The caller invokes the actual host tool and records its handle. | **Verified — repository source:** `scripts/dispatch` validates fields and publishes the prepared receipt; `.github/test-dispatch.py` covers refusal and lane records. Native runtime qualification is reported separately. |
| Claude-native reviewer static set | The `devstandard:reviewer` agent definition fixes the read-only purpose, judging contract under the delivery rule above, empty skill set, denial of the built-in writers, and model. | **Verified — [issue #179](https://github.com/LeonJoeeee/devstandard/issues/179#issuecomment-5501782986) and [issue #183](https://github.com/LeonJoeeee/devstandard/issues/183#issuecomment-5496822719) role rulings:** reviewer is a worker-family purpose with a separate set and read-only posture. The current definition and writer denial are qualified below; a model reading the complete judging contract remains **Unverified**. |
| Codex CLI worker or reviewer static set | The fixed dispatcher expands the appropriate role reference into the prompt, without depending on Codex agent definitions. It passes explicit model, effort, working directory and sandbox, installs only the fixed role hook, and sets the child role marker that hook reads. | **Verified — historical probe:** [issue #187](https://github.com/LeonJoeeee/devstandard/issues/187) and [issue #179](https://github.com/LeonJoeeee/devstandard/issues/179#issuecomment-5501782986) established dispatch-brief delivery for their tested CLI. **Verified — real CLI:** the role hook under the dispatcher's own settings and the brief arriving byte-identical are qualified under **Codex qualification** below. |
| Claude CLI worker | `scripts/dispatch --implementation claude-cli` launches `--agent devstandard:worker`, so the definition body carries the role and stdin carries the task packet alone; it selects purpose-routed model/effort or explicit overrides and sets the assigned cwd plus child role marker. It uses noninteractive `acceptEdits`, preserving normal authentication and settings. | **Verified — repository source:** dispatch emits a real process receipt with JSON Lines output, logs and completion. Required-action permission denials must be reported as blocked; no OS sandbox or reviewer support is claimed. Runtime qualification is recorded separately below. |
| CLI worker lifetime | A Python supervisor starts a new OS session on macOS/Linux and ignores SIGHUP. The selected CLI remains foreground inside it, with output captured in session scratch; each CLI reads its whole brief on stdin, the only transport a packet the size of an issue record fits. Default review publication uses the same lifetime principle. In tool PID namespaces, explicit `--wait` retains the originating invocation through CLI completion and synchronous review publication. No external `setsid` or `nohup` is required. | **Verified — historical probe:** [issue #187](https://github.com/LeonJoeeee/devstandard/issues/187) and [issue #179](https://github.com/LeonJoeeee/devstandard/issues/179#issuecomment-5501782986) established the detached-session requirement. Replacement supervision and publication are qualified under **Codex qualification** below. |
| Review instance, either implementation | The review-packet assembler reads current GitHub state, resolves exact SHAs, takes the current reviewer contract, and fills every ordinary-packet slot before dispatch. It refuses a partial packet or a review before the PR is green. | **Verified — [issue #183](https://github.com/LeonJoeeee/devstandard/issues/183) and [PR #188](https://github.com/LeonJoeeee/devstandard/pull/188):** the judging protocol changed while this architecture work was being dispatched, demonstrating that a copied earlier packet can stale under the dispatcher. **Verified — repository source:** `scripts/review-packet` implements current-source assembly, green-head admission and refusal of incomplete slots; `.github/test-review-packet.py` covers these transitions. |

The dispatcher records implementation, purpose, issue, branch, worktree and either process identity
or prepared native status on the issue. For native execution the caller adds the actual returned
handle; the shell dispatcher cannot invent or observe it. That lane record is the observable marker for the
dispatched wait. While a lane is running, native-handle, supervisor-lock, and captured-output checks
feed short event handlers or a dispatched monitor lane; Claude's background subagents notify, and a
CLI run is watched through its completion marker or held with `--wait`
(`reference/orchestrator.md`'s Dispatching to an executor section).
Completion is never inferred from those signals: it is established only by the durable PR,
evidence, verdict, and CI state. A restarted orchestrator reconstructs work from open issues and
PRs; absence of a PR remains "running or lost," not "done" (PRD §1.1, §1.2, §2.1).

**Unverified:** native-subagent status delivery, detached-process observation after orchestrator
restart, and issue-record creation have not been tested as one recovery path.

## 4. Workflow edges and enforcement tiers

The tiers describe how a rule binds:

- **Hard:** a native mechanism refuses an invalid action. Use it for catastrophic and mechanically
  decidable boundaries.
- **Structural:** the harness puts required context or a fixed transition at the act site. The agent
  can still disobey, but omission is not left to memory.
- **Soft:** the role instructions require judgment. Use it only where the decision cannot be made
  mechanically.

The workflow comes first; tiers are assigned to its edges, not used to invent additional workflow.
The worker-side rows below point to PRD §4 Workflow 3 and assign mechanisms to its boundary; they do
not restate the worker's execution.

### Workflow 1: one task

| Step or edge from PRD §4 | Tier and native mechanism | Evidence state |
|---|---|---|
| Discussion → confirmed, complete ① issue | **Structural:** the orchestrator set provides the issue fields and the requirements-skill trigger. **Soft:** the human confirms the settled result and reason; the orchestrator completes its scope and done-check afterward. | **Verified — repository source:** `reference/orchestrator.md` supplies the ready-at-dispatch definition, fields and triggers; native startup delivery is qualified below. The use of a skill here is reuse under PRD §2.3, not a claim that a skill can judge completeness. |
| ① issue → ② dispatch / Workflow 3 receipt | **Hard:** the fixed dispatch script refuses a missing issue, named base, branch, or worktree, and a reviewer dispatch whose goal, bounds or done-check is unfilled. **Structural:** the injected worker set points to Workflow 3's specification check. **Soft:** the orchestrator writes the issue contract and cuts scope, and the worker returns a missing or vague field before starting (#427). | **Verified — repository source:** `scripts/dispatch` validates fields and selects the requested implementation; `.github/test-dispatch.py` covers its refusals. This edge exists to prevent evidence-free work and missing conventions (PRD §1.2, §1.5). |
| ② dispatch → Workflow 3 isolated lane | **Hard:** Codex CLI sandboxes restrict filesystem writes; Codex gating reviewers are read-only. **Structural:** a dedicated worktree separates working trees, while the selected role set and task packet bind the worker to Workflow 3 through the agent definition or dispatch prompt. **Soft:** a worker with required shared-git-metadata access still obeys its named-branch boundary. | **Verified — [issue #187](https://github.com/LeonJoeeee/devstandard/issues/187) and [issue #179's delivery finding](https://github.com/LeonJoeeee/devstandard/issues/179#issuecomment-5488257766):** the tested native subagents lacked SessionStart method delivery at spawn; a Claude Agent child's compaction does reach it, identifying no agent (#375, per the source rule above). **Verified — repository source:** dispatch sets Codex CLI sandbox arguments and lane identity; Claude definitions declare tool restrictions. Live qualification is scoped below. Reuses PRD §2.2. |
| ③ Workflow 3 execution → green delivered PR | **Hard:** Codex CLI sandbox grants scope its process writes, and review assembly refuses acceptance until the current PR checks report green. **Structural:** the worker set binds Workflow 3's act-site obligations to the lane. **Soft:** implementation choices and the truth of non-mechanical evidence remain worker judgment subject to review. | **Verified — repository source:** worker carriers deliver the role itself — the agent definition body on both Claude paths, the dispatch brief on the Codex CLI path — and review-packet enforces green-head admission. **Unverified:** the complete live execution-to-handback path. GitHub, CI, and worktrees are reused under PRD §2.1 and §2.2; acceptance addresses PRD §1.2. |
| Delivered green PR → ④ acceptance | **Hard:** the assembler refuses an ordinary review while the current PR head is red or unreported; Codex CLI review is OS read-only and Claude review denies built-in writers. **Structural:** the assembler supplies a complete, current, clean-context packet and the Goal/Floor/Notes output shape. **Soft:** the reviewer judges goal fulfillment and the Floor evidence. | **Verified — [issue #183](https://github.com/LeonJoeeee/devstandard/issues/183) and [PR #188](https://github.com/LeonJoeeee/devstandard/pull/188):** the goal-centric contract and empty-by-design skill set are recorded, and PR #188's CI is green. **Verified — repository source:** `scripts/review-packet` implements green-head admission and packet assembly; `scripts/dispatch` selects the review sandbox. Live role enforcement is qualified separately below. This edge addresses PRD §1.2 and §1.4. |
| ④ accepted head → ⑤ merge and cleanup | **Hard:** branch protection rejects direct main writes; the merge guard requires a Goal Yes/Floor Pass verdict or the permitted orchestrator merge-as-is ruling after both Floor checks pass. If `main` moves after acceptance, the only path without a fresh verdict is a conflict-free rebase for which the comparison script proves every PR-changed path byte-identical — chapter 5's manifest version-line exemption apart — and CI passes on the merged result; both hard layers pass → merge, while either failure falls back to full review and a resolver where needed. **Structural:** the guard records the acceptance anchor and comparison proof; architecture-level status travels in the issue, PR, and review packet. **Soft:** the orchestrator classifies architecture-level work and waits for the human's decision. | **Verified — [issue #179's option-A ruling](https://github.com/LeonJoeeee/devstandard/issues/179#issuecomment-5550436875):** the human fixed the two-layer path. **Verified — repository source:** `scripts/guard`, `scripts/hard_edges.py` and `.github/test-hard-edges.py` implement and constructively probe these checks. Target-repository protection still requires actual evidence. The hard mechanisms are reused under PRD §2.1 and §2.2. |
| ⑤ merged result → ⑥ delegated release | **Structural:** the orchestrator set requires the human's authorization or the project's standing delegation before releasing, and the one-line report after. **Soft:** the human decides a new delegation or major-release sign-off. | **Unverified:** delivery of the release rule to a fresh orchestrator. Since ADR 0052 this edge has **no hard tier**: the hook does not recognize `tag` or `release`, and no record is looked up. Releasing is judged against PRD §1.3 by the role's page, and that is the ruling, not a gap to close. |

### Workflow 2: orchestrator events

The event-handler paragraph under [PRD §4 Workflow 2](./PRD.md#4-the-solution-the-target-workflows),
tracked in [issue #194](https://github.com/LeonJoeeee/devstandard/issues/194), is the authority for
the loop's semantics rather than this table. The architectural consequence is that every event
handler must be short, and any long wait is a dispatched lane plus an observable marker
([human ruling](https://github.com/LeonJoeeee/devstandard/issues/179#issuecomment-5550436875)).

| Event from PRD §4 | Tier and native mechanism | Evidence state |
|---|---|---|
| The human speaks | **Soft:** the orchestrator discusses or adjusts direction. **Structural:** its role set presents the issue-creation and requirements-skill triggers. | **Verified — repository source:** `reference/orchestrator.md` supplies these triggers; host delivery is qualified below. Addresses PRD §1.1 and reuses §2.3. |
| An irreversible action is needed | **Hard:** role hooks reject their listed command words, and the orchestrator's PreToolUse hook refuses `gh pr merge`, routing merges through `guard merge`; GitHub's branch protection rejects a direct push to a protected default branch. **Soft:** the orchestrator identifies every irreversible action the hook's word list does not reach — which since ADR 0051 is deliberately most of them, teardown of a merged lane included, since ADR 0052 the founding push and the release as well, and since ADR 0062 everything outside the three rules. | **Verified — repository source:** role hooks implement the word lists; live host enforcement is scoped below. Addresses PRD §1.3. |
| Architecture direction or a major release is ready | **Structural:** the orchestrator set keeps direction and major-release authority with the human, and the review packet routes architecture-level review one tier higher; architecture integration has no separate sign-off after that direction is settled. **Soft:** the orchestrator classifies the change and the human decides direction or publication. | **Verified — repository source:** `reference/orchestrator.md` supplies the authority boundary and its Dispatching to an executor section supplies review routing. Addresses the irreversible-control concern in PRD §1.3. |
| Ready-at-dispatch issues await | **Hard:** the dispatcher enforces one branch/worktree per task. **Structural:** it creates and records N lanes. **Soft:** the orchestrator applies its ready definition and cuts scopes to reduce overlap. | **Verified — repository source:** `reference/orchestrator.md` defines the dispatch moment; `scripts/dispatch` publishes lane records and `.github/test-dispatch.py` covers its admission and refusal transitions. GitHub and worktrees are reused under PRD §2.1 and §2.2 to address PRD §1.1. |
| A worker delivers | **Structural:** the orchestrator observes the PR and external state, validates the fulfillment packet, and starts acceptance only when required checks for the current head are green. A red or unreported PR remains on the worker side of the handback edge. **Soft:** a worker report remains a claim until review establishes it. | **Verified — repository source:** `scripts/review-packet` enforces green-head admission. **Unverified:** autonomous observer behavior as a complete live loop. The durable source is GitHub under PRD §2.1; the distrust boundary addresses PRD §1.2. |
| A verdict returns | **Structural:** Goal Yes/Floor Pass advances the reviewed head toward merge; if its base later moves, it enters the two-layer light-review path. Goal No returns only the stated goal grounds to the orchestrator for its per-PR continuation decision. A Floor check 1 failure—an evidence-free completion claim—returns to the worker for real evidence, and the failed review counts as a round. A Floor check 2 failure—an unauthorized irreversible action or out-of-scope work—stops the lane and escalates to the human at the irreversibles touchpoint, with no fix round. A conflict dispatches a resolver. **Hard:** merge waits on exact-head acceptance or a prior acceptance anchor plus both content-unchanged-rebase layers; any failed layer falls back to full review and a resolver where needed. **Soft:** the verdict, the permitted orchestrator ruling, and whether another goal-fix round is useful are judgments. | **Verified — [issue #183](https://github.com/LeonJoeeee/devstandard/issues/183) and [PR #188](https://github.com/LeonJoeeee/devstandard/pull/188):** Goal/Floor/Notes semantics. **Verified — [issue #179's round ruling](https://github.com/LeonJoeeee/devstandard/issues/179#issuecomment-5525395030) and [option-A ruling](https://github.com/LeonJoeeee/devstandard/issues/179#issuecomment-5550436875):** the human fixed the continuation, cap, and base-move paths. **Verified — repository source:** review-packet round accounting, guard rebase proof and dispatch continuation implement the mechanical transitions. **Unverified:** the complete autonomous verdict-to-resolution loop. Addresses PRD §1.2, §1.3, and §1.4. |
| Main goes red | **Structural:** the orchestrator set stops new dispatch and presents revert-first recovery and the relevant procedure. **Soft:** it decides whether an obvious minutes-long fix-forward is safer than revert. | **Verified — repository source:** `reference/orchestrator.md` supplies the event rule. CI is reused under PRD §2.1; preventing concurrent work on a bad base supports PRD §1.1. |
| Idle | **Structural:** the main-loop trigger queries open issues, PRs, checks, and worktree records and reports progress. **Soft:** the orchestrator decides whether a leftover needs cleanup or escalation. | **Verified — repository source:** `reference/orchestrator.md` supplies the idle trigger. **Unverified:** sustained autonomous idle handling. Reuses GitHub state under PRD §2.1 to address PRD §1.1. |

### Workflow 3: worker execution

[PRD §4 Workflow 3](./PRD.md#4-the-solution-the-target-workflows) is the authority for the steps; this table assigns their enforcement mechanisms.

| Step or edge from PRD §4 Workflow 3 | Tier and native mechanism | Evidence state |
|---|---|---|
| Receipt → specification check | **Hard:** the fixed dispatch script refuses an unfilled named base, branch, or worktree. **Soft:** the worker judges a missing, placeholder or vague goal, bounds or done-check and returns an underspecified task rather than starting; since #427 that judgment is the only check on the worker path. | **Verified — repository source:** dispatch validates the lane and the worker role begins with the specification check. Host delivery qualification is separate below. |
| Taking position → baseline snapshot | **Hard:** Codex CLI sandbox grants constrain its process writes. **Structural:** the dedicated worktree separates the lane. The role set requires the baseline snapshot, and the dispatcher records the lane on the issue. | **Verified — [issue #179's lifetime finding](https://github.com/LeonJoeeee/devstandard/issues/179#issuecomment-5501782986):** detached Codex execution survives its invoking session. **Unverified:** worktree/sandbox enforcement, baseline delivery, and issue recording as a complete lane path; the lifetime probe does not verify them. |
| Implementation | **Structural:** the agent definition or dispatch prompt binds execution skills, including TDD and systematic debugging. **Hard:** Codex CLI sandbox grants limit its process write scope. **Soft:** implementation choices and the named-branch boundary remain judgment where shared git metadata access is required. | **Verified — [issue #179's delivery probe](https://github.com/LeonJoeeee/devstandard/issues/179#issuecomment-5488257766) and [role-matrix ruling](https://github.com/LeonJoeeee/devstandard/issues/179#issuecomment-5501782986):** the tested native subagents lacked SessionStart method delivery at spawn — a Claude Agent child's compaction does reach it, identifying no agent (#375, per the source rule above) — and Codex CLI's role rode its brief. **Verified — repository source:** role pages and Claude definitions bind skills; dispatch selects Codex CLI sandbox arguments. **Unverified:** uncoached skill use and named-branch adherence. |
| The four stop events | **Hard:** the worker role hook refuses command text carrying its short word list, decided from source alone. It does not remove every way to perform an irreversible operation. **Soft:** recognizing core-architecture work, a wrong or unreachable done-check, or a direction call requires worker judgment. **Structural:** the role set fixes the escalation channel (output file / issue comment) and requires the lane to stop and wait. | **Verified — repository source:** the worker role defines the stop triggers and `scripts/hard_edges.py` implements the word list. **Unverified:** uncoached escalation behavior; live hook probes are scoped below. The open enforcement boundary below still applies. |
| Rebase onto current main → own conflicts | **Structural:** the role set assigns rebasing and conflict resolution to the worker. **Hard:** the merge guard rejects a head not based on current main; a moved base after acceptance uses the content-unchanged-rebase path in chapter 5 or full review. | **Verified — [issue #179's option-A ruling](https://github.com/LeonJoeeee/devstandard/issues/179#issuecomment-5550436875):** the two-layer rebase path is settled. **Verified — repository source:** the worker role assigns rebase ownership; guard and comparison machinery implement the current-base and unchanged-content checks. Live recovery as one sequence remains unverified. |
| Final-state done-check → evidence | **Structural:** the role set requires the done-check on the final state with commands, exit codes, and output. **Hard:** CI reruns the mechanical assertions. **Soft:** the truth of non-mechanical evidence is judged by Floor check 1. | **Verified — repository source:** `reference/worker.md` requires final-state evidence and `.github/workflows/ci.yml` carries mechanical assertions. **Verified — [PR #188](https://github.com/LeonJoeeee/devstandard/pull/188):** the Floor evidence contract. **Unverified:** the complete live evidence-to-acceptance path. |
| Opening the PR → fulfillment claim | **Structural:** the PR template restates the goal and carries the evidence. **Hard:** branch protection forbids direct main writes. | **Unverified:** rebuilt template delivery and branch-protection configuration. |
| Driving CI green | **Hard:** the observer and assembler refuse a red or unreported current head at acceptance. **Soft:** the worker classifies own-red versus not-own-red and escalates the latter. | **Verified — repository source:** review assembly enforces green-head admission and the worker role supplies red-check classification and escalation. Uncoached compliance remains unverified. |
| Handback → worktree left in place | **Hard:** the worker role hook refuses its listed merge command words. **Structural:** the lane record and handback message return the PR and evidence to the orchestrator, retaining the worktree for removal at merge. | **Verified — repository source:** the role hook, dispatch lane record and cleanup preconditions exist. **Unverified:** the complete live handback/cleanup transition. |
| Returned for a goal fix | **Structural:** a continuation brief carries the named goal gap into the same branch, worktree, and PR; the lane persists and the executor is disposable. **Hard:** per-PR round accounting records and reports every returned round. | **Verified — [issue #179's round ruling](https://github.com/LeonJoeeee/devstandard/issues/179#issuecomment-5525395030):** same-lane continuation is settled; issue #434 replaced the cap with a reported warning. **Verified — repository source:** `scripts/dispatch` preserves the lane on continuation and `scripts/review-packet` enforces round accounting. Each returned native handle is recorded on the issue, which is the evidence a prior handle finished. |

**open:** the architecture never claimed zero unauthorized irreversible actions, and since ADR 0051
it does not attempt to. A hook that reads command text is not complete enforcement — obfuscation, an
interpreter script and an operation built from runtime data all pass it — so the role hook guards the
ordinary case and the layers that carry the guarantee are `guard merge`'s reviewed-head verification,
branch protection and, for Codex CLI, the OS sandbox. Claude-native and Claude CLI workers retain
host/tool permissions: their assigned-worktree and named-branch boundaries are structural role obligations.
A CLI worker's shared git metadata access also does not enforce its named-branch boundary.

These assignments answer the five engineering sub-problems from PRD §5. Delivery is role-specific
and has one source per context set; CLI lifetime uses detached supervision or an explicitly retained
originating tool invocation;
asymmetry is explicit in the implementation columns; enforcement is selected per workflow edge; and
observability uses external state while treating self-report as a claim.

## 5. Concurrency and review convergence

N-way dispatch is N issue/branch/worktree lanes under one orchestrator. The orchestrator cuts scope
to reduce overlap between concurrently writable path sets; it never reduces concurrency, and every
issue meeting `reference/orchestrator.md`'s ready-at-dispatch definition is dispatched at once. Worktrees separate lanes; Codex CLI sandboxes constrain its
writes, while other workers obey their assigned-worktree contract. GitHub provides the queue and
durable return path (PRD §1.1, §2.1, §2.2).

**open:** the human has not set the observation target for N in PRD §6. The architecture therefore
defines N-way behavior without claiming a supported lane count.

Before handback, the worker owns rebasing and conflict resolution under PRD §4 Workflow 3. After a
green PR is handed back, the orchestrator never repairs a new conflict in its own worktree; it
dispatches a resolver worker into the affected lane. The resolver preserves the issue goal, reruns
final evidence, drives the new head green, and returns it for review. The
[live case recorded on issue #179](https://github.com/LeonJoeeee/devstandard/issues/179#issuecomment-5488090376)
verifies the cost: with two concurrent PRs, merging #177 caused #171 to conflict in
`reference/external-agent.md`; detection consumed review round 5, resolution used an
orchestrator-dispatched worker, and the changed head required round 6. That observation supports
scope cutting and resolver dispatch; it does not prove that every conflict has the same cost.

The review dose is one goal-centric round by default. Notes do not trigger another review round.
Whether to dispatch each next goal-fix round is the orchestrator's per-PR decision, judged only from
the verdict's stated goal gaps. Each returned verdict consumes a review round,
including a verdict that fails Floor check 1. The count is reported, and warned about past **7
rounds** per PR, but nothing refuses on it: the stop signal is findings of the same shape round
after round, which the reviewer reports as non-convergence. The
[human ruling](https://github.com/LeonJoeeee/devstandard/issues/179#issuecomment-5525395030) set 7
as a provisional cap tuned from observed effect; issue #434 (2026-09-20) turned it into the warning,
no record of it ever firing having appeared.

The lane persists and the worker is disposable. A goal-fix round sends a continuation brief into
the same branch, worktree, and PR, carrying only the blocking goal gaps, the PR, and the issue. A
native executor may continue through the same handle with `--resume` or through a fresh one; both
CLI implementations use a fresh process. A native handle is the caller's own and the dispatcher
observes none, so the handle recorded on the issue is the evidence its child finished; only a live
or unknown CLI run blocks reuse.

A Floor check 1 failure for an evidence-free completion claim returns to that lane for real evidence;
the failed review has already consumed a round. A Floor check 2 failure for an unauthorized
irreversible action or out-of-scope work stops the lane and escalates to the human at the
irreversibles touchpoint; it receives no fix round. A conflict after review invalidates the reviewed
head and dispatches a resolver; the resolver's changed head enters full review.

When another round would be pointless — most clearly when the findings keep their shape round
after round — the orchestrator rules first:
merge as-is when the goal is met within bounds and dispose of remaining Notes under
`reference/code-review-prompt.md`'s three options and leave-on-PR default; return the issue for
rewriting; abandon it; or change route. The ruling reaches the human only when it is
directional (abandon or change route) or meets `reference/orchestrator.md`'s handover-interrupt
grounds; that page's ready-at-dispatch and interrupt rules govern rather than a counted set of
touchpoints. Otherwise the orchestrator decides and reports the ruling in one line. A
merge-as-is ruling may settle an unresolved Goal No; it cannot waive either Floor check (PRD §1.4).

Before the option-A implementation, the rule re-reviewed every rebased head because its SHA changed. Applied to N ready PRs, each
merge can invalidate the other N−1 reviews even when the changed paths are disjoint. The issue #179
case demonstrates the conflict branch of this cascade at N=2; the general quadratic cost is an
inference, not a measurement.

Under the
[human's option-A ruling](https://github.com/LeonJoeeee/devstandard/issues/179#issuecomment-5550436875),
a reviewed PR whose base moves is neither merged blind nor sent immediately through another full
review. It receives a light review in two ordered, hard layers. The
[industry survey on issue #179](https://github.com/LeonJoeeee/devstandard/issues/179#issuecomment-5525494302)
found no mature system that adds a human or model interaction gate keyed on textual identity; CI on
the merged result is treated as the empirical answer, and the PRD's no-preventive-construction
boundary applies.

1. **Mechanical, hard:** a script proves that the rebase was conflict-free and every path changed by
   the PR is byte-identical before and after it. **One exemption, added 2026-09-07 (#242, #256)**
   because the human's ruling puts the version bump on the change PR: both release manifest
   version lines read as no difference when their old and new versions each agree, and where that
   exemption is what admits the comparison the new head must declare a bump against the reviewed
   head whose value, read as a dotted numeric release, sorts above both the reviewed head's and the
   replay's — so a lane cannot rebase past a merged bump and set the manifests back. The same
   exemption governs the replay that feeds the comparison: a conflict confined to those version lines
   resolves to the new base's value and the replay continues (#274). Every other byte or mode
   difference, and every conflict reaching any other path or line, still refuses.
   The same synchronized version-only predicate covers the bare-bump review waiver; a stale or
   mismatched version and non-version changes require ordinary review.
2. **Integration, hard:** CI is green on the merged result.

Both layers pass → merge. Any failure falls back to full review and dispatches a resolver where
needed (PRD §1.2, §1.4, §2.1, §2.2).

## 6. Rebuild outputs

The original rebuild opened the following implementation work after architecture approval. The
shipped source and remaining runtime qualification are recorded below; this is not a new task list:

1. Add the Claude-native worker and reviewer agent definitions, including their purpose-specific
   tools, model settings, context pointers, and worker-only skill bindings (PRD §1.5, §2.3).
2. Build the fixed dispatcher for both executor implementations: issue-field validation, worktree
   creation, implementation selection, sandbox arguments, detached Codex supervision, attribution,
   issue-side lane record, same-lane continuation dispatch that supports either a continuing or
   disposable executor, and cleanup (PRD §1.1, §1.4, §1.5, §2.2).
3. Build current-source acceptance assembly and publication: exact SHAs; green-head admission;
   complete ordinary packets from the current reviewer contract, reporting an unfilled slot to the
   reviewer rather than withholding the packet; whole-verdict return; and per-PR round accounting
   with the orchestrator-first ruling path (PRD §1.2, §1.4).
4. Split the orchestrator and worker context into two role references, evolving the existing worker
   brief, and reduce `core.md` to the shared workflow contract, triggers, and pointers. Bind
   superpowers once per role. Set `core.md`'s size budget from the hook's inline cap once that cap is
   re-measured against the rebuilt draft. Issue #200 removed Codex host delivery during this rebuild;
   ADR 0056 restored it using these shared artifacts, and ADR 0063 removed it again, with workers
   receiving their role through dispatch throughout. ADR 0059 later folded that shared page back into each role page and deleted it, so the
   size budget named here no longer exists (PRD §1.5, §1.6, §2.3).
5. Implement and probe the hard edges: the role hook's per-role word lists, the reviewed-head
   merge guard, the two-layer content-unchanged-rebase path (comparison script and CI on the
   merged result), branch-protection settings, PreToolUse authorization guards, and recovery
   behavior (PRD §1.2, §1.3, §2.1, §2.2).
6. Audit every current `reference/` page as keep, merge, move-to-role, or drop. Build a rule ledger
   that gives every retained clause its role, act site, enforcement tier, and PRD trace; a drop needs
   the human's approval. This ledger is implementation evidence, not a new shipped rules page (PRD
   §1.6).
7. Write the superseding and amending ADRs indicated below when their implementation lands. ADR
   bodies remain immutable; only status lines and dated amendment blocks change (PRD §1.5).

ADR 0056 extended these shipped mechanisms with a Codex host and native Codex worker receipts; ADR
0063 removed both and kept the Codex CLI executor. Neither reopens the original rebuild.

## 7. ADR dispositions and traceability

This table finalizes the preliminary inventory on issue #179 against the approved PRD and the later
human rulings. It records what the rebuild must do and names the ADRs as their implementation lands.

**Reconciled 2026-09-07 (#207).** Every row below now names the ADR that carries its disposition,
and the dated amendment blocks are appended on the ADRs the rebuild overtook. ADR bodies were not
rewritten; a row whose disposition needs no ADR says so.

| Disposition | ADRs | Reason |
|---|---|---|
| Already superseded; history only | 0001–0005 | Later ADRs already replaced the initial package, superpowers, execution, lifecycle, and fixed-session forms. No rebuild action, and no ADR needed. |
| Stands as foundation | 0000, 0009, 0012, 0013, 0017, 0018, 0020, 0022, 0023, 0025, 0026, 0031, 0033, 0034, 0037, 0041, 0042 | ADR discipline; GitHub collaboration; worktree lifecycle; task-level design and document admission; operational memory; red-main recovery; universal PR/review/CI; record language; CI fallback; PR ownership; reference sizing; verdict publication; placement; and clean handback remain required by this architecture. Unchanged by the rebuild, so no ADR needed. |
| Superseded by the rebuild | 0006, 0008 → 0047; 0014 → 0048 | The native Workflow tool is no longer the whole harness because fixed dispatch and packet machinery are required, and direct in-session work is no longer the default beyond one- or two-line changes and research (0047); the full/light/mini setup fork is removed and weight is a bound on each issue (0048). The reusable parts of each decision — run sizing, rationing, and "the agent never guesses scope" — are restated by the superseding ADR. |
| Superseded by 0045 (issue #200), then 0045 superseded by 0056, then 0056 by 0063 | 0038, 0039, 0045, 0056 | Rebuild 0 removed Codex host delivery. ADR 0056 restored the host with shared roles, native workers and independent read-only CLI gating review; ADR 0063 removes it again on the human's ruling (#459), keeping Codex as a dispatched CLI executor. The older role-marker and adoption designs remain history. |
| Amended for role delivery | 0007, 0015, 0016, 0019 → 0049; 0015, 0036, 0040 → 0047; 0024 dated block; 0024, 0040 → 0050 | Static context is now one delivered artifact per role, injected by default with the carrier chosen from a measured size and a CI gate that fails an over-cap artifact (0049). The dispatch-first rule and the retirement of the ladder's rung vocabulary ride 0047. ADR 0050 supersedes 0024's cap and 0040's restatement; as amended 2026-09-19 (#406) the worker and the reviewer are anchored rather than routed by kind of work, and `reference/orchestrator.md`'s Model and effort section carries those two rows, the arbitration setting and the one-off subagents' — nested helpers included. ADR 0045 reconciled the Codex host removal earlier. |
| Amended for acceptance and concurrency | 0011, 0035 | Already carried: the goal-centric contract by 0044, and the two-layer light review by 0046. Added 2026-09-07 as dated blocks on 0011, 0035 and 0046: the manifest version-line exemption to the byte-identical clause (#242, #256). Resolver dispatch needs no block here — it leaves both gates and the reviewed-diff rule as written; the live statement it overtook is 0015's, which its 0047 block carries. |
| Repository operations; unaffected | 0010, 0021, 0027–0030, 0032, 0043 | Rename history, this repository's pipeline upkeep, wording sweeps, translation and changelog policy, repo-only placement, and page-audit rules do not define the target collaboration model. No ADR needed. |
| Reviewer-contract ADR | 0044 | It records the approved Goal/Floor/Notes contract from PR #188; this architecture does not duplicate or supersede it. No ADR needed. |
| Written by the rebuild | 0045, 0046, 0047, 0048, 0049 | Codex host removal; the guarded merge and content-unchanged rebase; the shipped collaboration machinery with dispatch as the default; weight as a per-issue bound; and per-artifact injected role context. Each rode the PR that implemented its decision, except 0047–0049, which reconcile decisions already landed across Rebuild 0–6. |
| Host restoration and removal after the rebuild | 0056, 0063 | 0056 added Codex packaging and a bounded host adapter around the existing collaboration machinery; 0063 removes them and keeps the Codex CLI executor. Both preserve the role split, guards, review contract and historical ADR bodies. |

### Structure traceability

| Named structure | PRD source | Why it exists |
|---|---|---|
| Supplementary harness on Claude Code, dispatching Codex as an executor | §1.1, §1.5 | Native sessions do not supply the collaboration protocol or assumed team conventions. |
| Claude Code as the only orchestrator | §1.6, §5 | As a main session Codex follows its own harness rather than the method (ADR 0063); it executes when dispatched, and gating review runs in its independent read-only CLI. |
| GitHub as durable coordination state | §2.1 | Reuses issues, PRs, review, and CI rather than inventing an agent state machine. |
| Orchestrator context set | §1.1, §1.5 | Removes human scheduling and delivers main-loop conventions to a fresh session. |
| Dispatched-executor purpose × implementation matrix | §1.1, §1.5 | Enables parallel execution while carrying the same role contract through asymmetric native harnesses. |
| Worker context set and worker role reference | §1.2, §1.5, §2.3 | Makes completion evidence-bearing, supplies conventions, and binds execution craft. |
| Reviewer context set and ordinary packet | §1.2, §1.4 | Distrusts completion claims and stops peripheral review drift through a clean, current judging packet. |
| Resolver as a worker purpose | §1.2, §2.2 | Keeps conflict changes isolated and re-verifiable without granting merge authority. |
| SessionStart delivery of the orchestrator set | §1.5 | Ensures a fresh orchestrator receives the conventions it otherwise lacks. |
| Codex CLI executor page | §1.5, §5 | Maps the Codex CLI's mechanics for the dispatching session without copying the method, and carries the worker-facing section a Codex worker is handed. |
| Direct-injection default and measured per-artifact carrier choice | §1.5, §5 | Makes static context delivery reliable: the carrier for each artifact follows its measured size against the re-measured hook cap, and since ADR 0049 an artifact that does not fit is a failed gate rather than a silently degraded delivery. |
| Claude worker/reviewer agent definitions | §1.5, §2.3 | Carry fixed role, tool, model, and role-bound skill settings, because a dispatched child's role never arrives from the session hook: none fires at spawn, and the one its compaction fires names no agent (per the source rule above). |
| Fixed cross-implementation dispatcher and same-lane continuation | §1.1, §1.4, §1.5, §2.2 | Creates N isolated lanes, keeps fix state in the lane rather than the executor, and closes the Claude/Codex delivery asymmetry. |
| CLI supervisor and explicit tool-lifetime wait | §1.1 | Detached supervision survives SIGHUP; `--wait` retains the originating tool where an enclosing PID namespace would otherwise tear down. Review waiting includes synchronous publication. |
| Current-source ordinary review-packet assembler | §1.2, §1.4 | Delivers a complete, non-stale fulfillment claim to a clean reviewer. |
| Hard / structural / soft enforcement tiers | §1.2, §1.3, §1.5 | Mechanizes evidence and safety boundaries while retaining judgment only where required. |
| Workflow 3 edge tiers | §1.2, §1.3, §1.5, §2.2 | Assign evidence, stop, and isolation mechanisms to every worker-execution step without duplicating the PRD workflow. |
| Worktrees, OS sandboxes, branch protection, and CI-green-before-review order | §1.2, §2.1, §2.2 | Reuses native isolation and integration enforcement while ensuring the reviewer judges a green PR and merge requires both gates. |
| Reviewed-head merge guard | §1.2, §2.1 | Prevents an acceptance verdict for one head from authorizing a different merge unless both hard layers prove the rebased content unchanged — chapter 5's manifest version-line exemption apart — and the merged result green. |
| PreToolUse role hook | §1.3 | Refuses the ordinary spelling of the operations a role must never perform, cheaply enough to hold in one's head, without refusing ordinary work, and with nothing to configure: since ADR 0052 the words are in its source and it reads no file, no ref and no network, and since ADR 0051's 2026-09-11 amendment it judges a command's own text and never a tool name — no allowlist anywhere, with what a role may reach left to the agent definition's denials and the sandbox that already carried it. Since ADR 0062 it refuses three things — a worker's `merge`, the orchestrator's `gh pr merge`, a reviewer's `gh api` write flags — plus the worker default-branch push that branch protection takes over, because a word that named a reversible act bought its refusals with false ones. |
| GitHub-first lane observability | §1.1, §1.2, §2.1 | Lets the orchestrator reconstruct state without trusting a worker's self-report. |
| Scope cutting and N-way lanes | §1.1, §2.2 | Provide parallel throughput while reducing writable overlap. |
| Per-PR round decision, reported round count, and orchestrator-first ruling | §1.1, §1.4 | Bounds revision without making the human schedule ordinary continuation decisions. |
| Same-lane goal repair and the two Floor-failure transitions | §1.2, §1.3, §1.4, §2.2 | Returns an evidence-free claim for proof while stopping unauthorized irreversible or out-of-scope work instead of treating it as a normal fix. |
| Resolver full review and two-layer content-unchanged-rebase light review | §1.2, §1.4, §2.1, §2.2 | Reviews changed conflict resolutions fully while checking byte identity — chapter 5's manifest version-line exemption apart — and merged-result integration for an unchanged PR. |
| Rule ledger and reference-corpus disposition | §1.6 | Prevent silent loss while deleting every clause that lacks a PRD reason. |

Decisions and their reasons: `docs/adr/`.

### Hard-edge implementation evidence (#204)

`scripts/guard` implements the reviewed-head/current-base check and the two-layer rebase path;
`scripts/dispatch` carries role hooks and lane admission. Constructed negative
probes live in `.github/test-hard-edges.py` and `.github/test-dispatch.py`. The live protection
fixture refused while main passed, as recorded on #204. ADR 0046 records the interfaces;
`reference/orchestrator.md`'s Guarded operations section owns their operation. **The match/authorization defaults settled on
2026-09-06 (#204, #223) no longer exist**: the human signed off on the architecture-level change and
delegated three proposed defaults to the main session, which shipped them in a configuration file —
and ADR 0052 deleted that file with every rule that read it on 2026-09-10. Live executor hook
enforcement remains **Unverified**, assigned to the main session by #204's second continuation
ruling. Neither command matching nor classic status protection alone proves zero unauthorized
operations or a complete PR-only capability boundary.

**One rule per role (2026-09-10, #323).** The machinery above — a closed shell grammar, a
ten-family refusal table, a per-tool-call policy read from the remote default branch, an
authorization record for every irreversible orchestrator command, and a retry layer for the network
faults that read caused — cost seven review rounds and three releases over 2026-09-09/10 and still
refused ordinary research commands. On the human's ruling the hook reads command text instead of
parsing it and decides on a short word list per role, and no read failure can produce a refusal.
Each refusal is written as a reminder rather than a wall — the
word, what the role does instead, its page, and how to re-spell a benign command — because a
textual scan will sometimes hit one. The residual is accepted rather than chased. ADR 0051 records
the ruling, `reference/orchestrator.md`'s Guarded operations section owns the operative wording, and the rows above are written to
it.

**No configuration file (2026-09-10, #326).** The same day's second ruling finished the first one.
The chain that produced a policy file ran: a hook to stop a subagent writing to GitHub → a file so
the hook knew who the human was and what to require → rules for reading the file → an issue about
where the file lives; each layer solved the previous layer's problem. **The hook stays and
everything that existed only to feed it goes.** The word lists are in the source, the default
branch is `main` or `master` by name, `guard merge` keeps its own GitHub reads, derives the
repository owner from the repository's API record and judges CI by its own read of the head's
checks, with no name list to configure; `guard protection --apply` takes its check names from the
command line. The founding admission below is now the absence of a rule rather than a carve-out,
and the authorization record, the authorization issue and the standing-release entry are retired. ADR 0052
records the ruling and the chain it undoes.

**Founding admission (2026-09-07, #293; retired 2026-09-10, #326).** Proven policy absence once
narrowed what the guard granted and then also admitted one operation, because an authorization
record could not precede the policy file that named its issue. **The admission has no code left.**
Its protection half was dropped on 2026-09-10 (#323) with the remote reads; its policy half went
the same day with the file (#326), because the orchestrator's word list no longer carries `push`
at all. GitHub's own branch protection is what rejects a push to a protected branch, which is the
layer that check belongs to. `reference/orchestrator.md`'s Guarded operations section owns the wording and its limits; ADR 0046's
2026-09-07 and 2026-09-10 blocks record the admission, its narrowing and its retirement.

**Three rules (2026-09-20, #425).** The #379 audit read every word in the lists against one bar:
does it name an act that is irreversible *and* that no other layer stops? Three cleared it — a
worker's `merge`, the orchestrator's `gh pr merge`, a reviewer's `gh api` write flags — and every
other word was refusing reversible work while admitting the spelling that mattered. `tag` refused a
local `git tag` and admitted `git push --tags`; `release` refused `cargo build --release` in every
target project; `--force` stranded a worker on the lease-protected push its own brief required
(#236); the reviewer's whole list admitted `gh pr comment`, `gh pr review --approve` and
`gh pr edit`, so it carried no independence at all. The recursive-`rm` rule with its `/tmp/`
carve-out, and the re-spelling detour every refusal carried, go with them: the detour existed to
route around refusals these three do not make. **What widens is named rather than chased** — a
reviewer's shell reaches GitHub writes outside `gh api`, and a worker's recursive `rm` reaches any
target — because read-only is `agents/reviewer.md`'s writer denial and the Codex `-s read-only`
sandbox, and the lane is a disposable worktree whose branch is already pushed. ADR 0062 records the
ruling, and `reference/orchestrator.md`'s Guarded operations section owns the operative wording.

### Rebuild implementation evidence (2026-09-07, #207)

Rebuild 0 through 6 landed the mechanisms this document specifies. `scripts/dispatch` validates the
issue contract, creates and records the lane, selects the executor implementation, and detaches a
Codex process (#202, #213). `scripts/review-packet` assembles current-source packets, refuses a red
or unreported head, publishes the whole verdict, and accounts rounds against the cap (#203, #222).
`scripts/guard` with `scripts/hard_edges.py` implements the reviewed-head merge and the two-layer
rebase proof (#204, #223). `hooks/session-start` delivers one artifact per role (#205, #235), and
`agents/worker.md` and `agents/reviewer.md` carry the Claude-native roles (#201, #208). Their
constructed tests live in `.github/`. ADRs 0047 and 0049 record the decisions behind the shipped
machinery and the delivery split; 0048 records weight as a per-issue bound.

**Source labels reconciled 2026-09-11 (#342).** The original 2026-09-07 qualification (#279) told
readers to reinterpret absent-mechanism cells using this implementation record. The cells now name
the shipped source directly. Constructed tests qualify the mechanism they reach, not unrelated
behavior. What constructed tests leave **Unverified** includes live enforcement of role hooks and
sandbox by the harness (separately qualified below),
native-subagent status delivery, detached-process observation after an orchestrator restart, and
the complete recovery path exercised as one sequence. A passing constructed probe is not a proof
about the harness.

### Codex qualification (2026-09-11, #342; host removed 2026-09-29, #459)

**Host removed (2026-09-29, #459, ADR 0063).** The installed-plugin, native-spawn and native
follow-up paragraphs below qualified the Codex host and are history: `.github/test-codex-install.py`
and `.github/test-codex-native.py` are deleted. `.github/test-codex-runtime.py` now runs only the
dispatched executor, through `scripts/hard_edges.py`'s `codex_hook_config` exactly as the dispatcher
passes it: the role guard inactive with hooks disabled and before and after the one-invocation trust
bypass, active for worker and reviewer under it; the dispatched worker brief arriving byte-identical
in the model request; and MCP admission per sandbox mode. It passed on the CI-pinned Codex CLI 0.156.1
on Linux for #459, and it gates the Codex CI job on macOS and Ubuntu.

**Verified — native Codex CLI 0.153.4 on macOS and Ubuntu 24.04:** `.github/test-codex-install.py` and
`.github/test-codex-runtime.py` exercised a temporary native plugin installation, its cache and
skill discovery, and actual native hook handlers with the plugin's own environment. A deterministic
local Responses service drove disabled hooks, untrusted hooks before and after an invocation-wide
trust bypass, and invocation-trusted main, worker and reviewer runs. The main request contained the
complete core, orchestrator and adapter artifacts. Assigned workers/reviewers received no
orchestrator startup context, and their actual tool hooks enforced their role. These were installed
plugin hooks, not inline-hook or environment doubles; the trust bypass did not persist trust.

**Verified — installed Codex plugin on macOS:** `.github/test-codex-native.py`, called before
installer cleanup, passed both native spawn protocols against the actual cached dispatcher and
hooks. The full emitted worker brief and explicit model/effort reached a fresh child; it inherited
developer instructions and permissions, used the assigned worktree explicitly, ran an allowed
command, and refused the worker's forbidden command. Its real `agent_id` selected worker rules
without a process role marker. Native wait returned completion. This proves native dispatch and
hook behavior with a deterministic provider, not independent child sandboxing or a remote PR lifecycle.

**Verified — native follow-up to a finished child, Codex CLI 0.153.4 on Ubuntu 24.04 (#352):** a
one-off live probe, not a CI gate, using the same shape as the suite above — real CLI, real native
spawn/wait/follow-up, deterministic local provider. On both protocols a child that had reached a
final status accepted a follow-up (v1 `send_input`, v2 `followup_task`) and its next request carried
the earlier task, tool call, tool output and final message alongside the new message; the verdict
was read from the CLI's own request bytes, not the fixture's claim. Commands and output are on
[issue #352](https://github.com/LeonJoeeee/devstandard/issues/352). This qualifies one CLI version
on one host and says nothing about resuming across separate `codex exec` invocations: the handle
lives in the spawning session's agent tree.

**Verified — Claude Code 2.1.268 on macOS and the original Linux SSH development server:**
`.github/test-claude-runtime.py` exercised the candidate through session-only plugin loading and a
local deterministic Messages service. Main startup delivered full core/orchestrator context without
the Codex adapter. Direct worker/reviewer sessions, with and without the CLI role marker, and actual
background Agent workers/reviewers received their shipped role definition without orchestrator context. Allowed shell
commands ran and each role's forbidden command was refused; reviewer tool catalogs excluded
`Write` and `Edit`. A worker process's inherited role did not override its named reviewer child.
The `--dispatch-cli` case also exercised the real dispatcher and detached supervisor into Claude:
the full resolved brief arrived through stdin, the assigned cwd and explicit model/effort were
used, and structured output retained permission denials alongside completion. GitHub I/O and provider
responses were fixtures; test-only invocation controls excluded unrelated configuration and tools.
This left the existing installation unchanged. It does not establish a native Claude model acting on
the role/contract it receives, production authentication/model behavior, or a remote PR lifecycle.

**Verified — real macOS/Linux processes with controlled GitHub/model boundaries:** the dispatch and
review-packet integration suites passed Python session detachment, SIGHUP survival, completion and
publication checks. Those fixtures establish process behavior, not a complete remote worker/PR
lifecycle or uncoached model adherence to the method.

Linux CI installs the distribution Bubblewrap package and its scoped AppArmor profile under
[Codex's prerequisites](https://learn.chatgpt.com/docs/sandboxing#prerequisites); the real runtime
probes retain the read-only sandbox and existing command rules. Captured qualification runs are
linked from [PR #343](https://github.com/LeonJoeeee/devstandard/pull/343).

**Unverified:** persistent UI resume, clear and compaction behavior; matcher-fixture coverage does
not qualify those UI transitions. These limits belong to this
restored-host path and do not rewrite the older rebuild's evidence or qualify unrelated recovery
claims above.

**CLI lifetime correction (2026-09-11, #342 continuation).** A real Linux Codex workspace-write tool
could publish a detached launch then lose its supervisor when the tool PID namespace ended.
Python session detachment does not prevent that teardown. Explicit CLI `dispatch --wait` retains
the originating execution until the actual child exit is atomically recorded; `review-packet start
--wait` also publishes the whole verdict synchronously. Default detached behavior remains.

A supervisor inherits a pre-acquired advisory lock in existing run scratch, avoiding a publication
readiness race; its CLI child does not inherit ownership. Later callers use this lock, never a
namespace-local PID, to distinguish active supervision from lost/unknown execution. Valid completion
records a CLI exit, not task acceptance. Missing completion and a free/missing lock block reuse;
explicit exact-run reconciliation records the caller's authoritative originating-host absence claim,
not an automated verification of that inspection. It changes the original issue run to `reconciled-lost`, without fabricating an exit. Lost reviews release
only after reading that exact reconciliation, as failed attempts with no verdict round. The existing
single-orchestrator contract remains; no global journal or distributed comment lock is added.
`reference/orchestrator.md`'s Dispatching to an executor section owns recovery and retention through lane cleanup. These mechanisms do
not change authentication, hook trust, runtime-directory grants or nested sandbox capability.
