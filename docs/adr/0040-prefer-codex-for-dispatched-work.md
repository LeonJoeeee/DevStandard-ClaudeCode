# 0040 — Prefer Codex for dispatched work; the standing model and effort are written on the page

Status: Accepted (2026-08-26). Amended by 0045 (2026-09-05). Amended by 0047 (2026-09-07). Amended by 0050 (2026-09-09). Amended (2026-09-11). Amends 0036 (two of its stances are reversed by the human's ruling:
the shipped text now *prefers* the external executor for dispatched work, and the page *names* the
standing model and effort — once, dated; and its admissibility is narrowed to rung 2 — a process
executor takes the subagent's slot, never a separate live session's). Amends 0024 in one detail only — its 0039 block's
"standing effort settings" gain an address — while its cap and tier names still bind every agent
spawned through Claude's harness, and its Rejected (b) (version ids rot silently) is answered here
by dating and single-siting the setting, not by refusing to write it. Amends 0039
(its "standing effort settings" gain an address, and the executor choice it left open is decided) and
0011 (gate 1's "fresh subagent" becomes the property it always meant — a fresh, process-isolated
reviewer — with the read-only Codex run as its executor where installed), 0038 (its Claude-side
"defaults to Codex" sentence becomes the harness-neutral rung-2 rule) and 0034 (its "moves into a
subagent" trigger reads as any out-of-context helper, a process included). Cites 0008 (the
ladder's rungs are unchanged). Amended by 0056 (2026-09-11). Amended by 0063 (2026-09-29). Amended by 0064 (2026-10-04).

*This ADR changes what DevStandard ships — a routing preference and a standing setting on the pages
every seeded project reads — so a reader in a seeded project should take it as method.*

## Context

Until now the pages said *where* an external agent fits (rung 2, same rules as a fresh subagent —
0036), *which* one (Codex, where installed — 0039), and *how* to brief it (like a subagent, with
write access for real work — 0039's #156 correction). They said nothing about **when** to choose it
over a harness-native subagent, and they refused to name a model or effort level: 0036 called naming
another vendor's model ids "the silent-rot failure 0024's Rejected (b) already refused", and
`reference/external-agent.md` said hard-coding them "would rot on their release schedule, not yours".

The human read exactly that summary and ruled (issue #165):

- **Write the classification into the page** — when a subagent, when Codex.
- **Recommend Codex** for dispatched work. Their reasoning: the harness's top tier (Fable) is too
  costly to run as a worker; the next tier down (Opus) is not clearly a match for GPT-5.6 Sol at
  `xhigh`; so for the same work the external executor is the stronger worker for the money.
- **The standing strength is `gpt-5.6-sol` at `xhigh`**, and it goes on the page.

What was measured before the ruling, all on #158/#162 the same day: with the real 0.28.2 install on
codex-cli 0.149.1, an uncoached one-shot Codex session read the method first, then ran the entire
ceremony — issue, branch, PR, a self-spawned read-only reviewer, a posted check-1 verdict, merge only
after review and CI, done-check re-verified. And across #148/#155 the cross-vendor pairing caught
defects each side had missed alone (the `codex-adopt` Critical; the round-4 rebuttal). 0036 had
declined to prefer an external agent because "a second vendor reviews better" was unmeasured then;
it has since been observed, which is not the same as measured, and this ADR rests on the ruling.
The design record is `docs/specs/2026-08-26-when-a-subagent-when-codex.md`; the challenge record is
on #165.

## Decision

1. **`reference/external-agent.md` carries a "When a subagent, when Codex" section** — the one place
   the classification is stated in full. Codex for dispatched implementation and for gating reviews
   and design challenges (gating work always takes the fresh process; a harness-only source it needs
   is folded into the report it receives, within `core.md`'s three artifacts) — the named reason is a
   fresh, process-isolated, read-only run, which holds
   when the main session is itself Codex (0039's topology); a second vendor's judgment is the extra
   a Claude main session gets on top, not the rule's ground; a
   harness-native subagent — always fresh, as the ladder's rung 2 says; a context-inheriting fork is
   never a dispatch — for quick read-only exploration whose result belongs in this context, work
   that needs the harness's own rung-2
   mechanisms (EnterWorktree, this harness's MCP servers — a Workflow need selects rung 3, another
   venue, not a subagent), and a piece small enough that the dispatch
   overhead exceeds it. `core.md` carries the trigger and the pointer, in the ladder's rung 2 and in
   "Who does the work".
2. **Where Codex is installed, dispatched work goes to Codex; a harness-native subagent only where
   the work especially suits one** — the human's own summary of the ruling: "use Codex as much as
   we can, unless the case especially suits a subagent." Not merely the default when going
   external. Nothing else moves: same rung, same rules, one writer per worktree, a worker never
   merges, the clean reviewer, the reviewed diff is the merged diff. **Not a dependency** stands
   exactly as 0036 wrote it — a project without Codex loses nothing, its absence never lowers a bar.
3. **The standing model and effort are written on the page, once, dated:** `gpt-5.6-sol` at
   `model_reasoning_effort=xhigh`, in `reference/external-agent.md`'s routing section, marked as the
   human's standing setting with its date. `reference/harness-codex.md` points at it for a Codex
   session dispatching within its own harness. The dispatch still sets both explicitly on every
   invocation (0036's "set it explicitly" is unchanged); what changes is that the *value* is no
   longer left to each dispatcher's memory or a config file nobody reviews.
4. **0024's cap is untouched** (its only amendment here is the address of the standing setting).
   `opus` remains the cap and default for every agent spawned through
   Claude's harness — a worker's helpers included — because that rule guards a different thing
   (a session's own fan-out), and this ADR only chooses between executors at rung 2.

## Consequences

- The page is now vendor-dated on purpose — the same trade 0024 made for Claude's tiers: a rule that
  binds, in exchange for one line that can go stale. The rot is bounded to that line — the CI gate
  reads the record from the page rather than repeating it — so a model rename or a new standing
  setting is one edit plus its date, and a reader can see how old the
  setting is, which the silent config-file default never offered. That bound is the answer to
  0024's Rejected (b), and the reason 0036's refusal is reversed rather than merely overridden.
- A dispatcher who picks a subagent for work outside the page's subagent list now departs from a
  stated rule and says why in the handback; before, either choice was silent.
- The cost reasoning is the human's and is recorded as theirs. It is not a rule about quota or
  budget — the method still does not ration by price — and if the relative standing of the two
  vendors' models changes, the ruling is revisited, not the mechanism.
- Cost on the pages: `core.md` gains one clause in "Who does the work", a few words at rung 2, and
  its fresh-reviewer line now names the Codex run; the act sites where a review or challenge is
  commissioned (`reference/code-review-prompt.md`, `reference/worker-brief.md`,
  `reference/design-spec.md`, `docs/architecture.md`) carry the Codex trigger and pointer, and the
  reviewer prompt's fence gains a `{REVIEWER_IDENTITY}` opening line;
  `reference/external-agent.md` gains one section and loses the "would rot" sentence;
  `reference/harness-codex.md` gains a pointer.

**Amendment (2026-09-05, see 0045):** The Codex-main-session topology in Decision 1 and the mappings-page route in Decision 3 are retired. Claude Code is the supported orchestrator and Codex is a dispatched CLI executor. The dispatch preference, explicit model/effort, fresh read-only reviewer, and canonical dated setting on `reference/external-agent.md` remain unchanged.

**Amendment (2026-09-07, see 0047):** the "rung 2 only" narrowing in this ADR's Decision reads as the
dispatched-executor slot now that the ladder is retired; a separate live session is still not what a
process executor replaces. The preference itself is unchanged and has become mechanized rather than
remembered — the fixed dispatcher selects the implementation, sets the model and effort explicitly
on every invocation, and records the choice on the issue. The standing setting stays exactly where
this ADR put it: stated once, dated, on `reference/external-agent.md`.

**Amendment (2026-09-09, see 0050):** the human's issue #309 ruling supersedes Decision 4's
restatement of 0024's cap and uniform routing across kinds of work. The two-knob default ladder,
escalation order, downgrade test, review floor and override clause live in
`reference/external-agent.md`, “Route it explicitly”, including Codex-internal helpers.
The executor preference and the single, dated standing dispatch setting remain unchanged.
That setting still has one record; a routing change now also reconciles the table and applicable
role settings/tests, so the Consequences' one-edit cost applies only to the standing record.

**Amendment (2026-09-11, see issue #332):** the human reverses Decision 2's preference. **The
default executor for dispatched work is the host's own subagent**, and their instruction — for one
dispatch, or standing until their next — selects Codex instead; `reference/external-agent.md`,
"When a subagent, when Codex", carries the operative wording, and `scripts/dispatch` and
`scripts/review-packet` default to `claude`. The ground is a week of recorded lane failures on the
Codex path and none of that kind on the Claude path: transport failures stopped five workers
mid-lane (#303), the prescribed helper review never initialized (#308), a skill footer caused a
false stop (#304), and a detached return handler died returning no verdict. The cost reasoning in
Decision 2 is not refuted, and this is the same kind of call it was — the human's, revisited on new
evidence. Nothing else moves: Codex stays fully available as the human's choice, keeping its
sandbox, its explicit model and effort, and the single dated standing setting of Decision 3;
Decision 1's classification stands apart from the sentence that made Codex the default.

**Amendment (2026-09-11, see 0056):** 0056 adds host bindings to the 2026-09-11 default: each host
uses its own native workers; Codex hosts pass `--implementation codex-native` for workers and
`--implementation codex` for independent read-only gating reviews. Explicit CLI execution remains a
separate choice. The dispatcher default stays `claude`; the caller passes its host binding.
`reference/external-agent.md` owns routing, with the dated Codex model/effort setting applied to both
native and CLI implementations.

**Amendment (2026-09-29, see 0063):** 0063 removes `--implementation codex-native` and the per-host
bindings. Dispatch defaults to the Claude-native subagent; `--implementation codex` is the
human-selected CLI executor for workers and read-only gating review, and the Codex model/effort
setting applies to that path alone. `reference/orchestrator.md`'s Dispatching to an executor section
owns routing; `reference/harness-codex.md` maps the CLI executor, not a Codex session dispatching
within its own harness.

**Amendment (2026-10-04, see 0064):** The 2026-09-11 block's reversal of the executor preference is reversed: Codex is the default again
for workers and reviewers, including the independent `scripts/review-packet` default. The human's
instruction still selects another supported executor for one dispatch or standing; the
unavailable-executor rule still preserves gate properties or blocks. The 2026-09-29 block's
Claude-native default is superseded likewise. `reference/external-agent.md`, named by the old
blocks, was removed by 0059; the operative wording now lives in `reference/orchestrator.md`'s
Dispatching to an executor section, with executor mechanics on `reference/harness-codex.md`.
