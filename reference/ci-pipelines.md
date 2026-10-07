# CI, the release pipeline, and keeping them current

Read this at project start, after the skeleton exists. Two robots, generated once — then they age with GitHub, not with the project:

- **CI** — for pushes and PRs, use the CI template below and `reference/orchestrator.md`'s Branch protection section.
- **Release (CD)** — every project must ANSWER the release question: *what does "shipping" mean here?* A service → deploy; a tool/library → publish a package; a plugin → publish to its marketplace/repo. Default trigger: **a version tag** — use the release template below; the human decides when to tag. Fully-automatic release-on-merge is a per-project opt-in, not the default.

Adapt the templates to the project's language/toolchain (swap the test command and the release steps). Keep each file minimal — these are gates, not build systems.

## CI template (`.github/workflows/ci.yml`)

```yaml
name: CI
permissions:
  contents: read
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 2
      - name: Bind this checkout to the advertised PR merge result
        if: github.event_name == 'pull_request'
        env:
          EXPECTED_BASE: ${{ github.event.pull_request.base.sha }}
          EXPECTED_HEAD: ${{ github.event.pull_request.head.sha }}
        run: |
          test "$(git rev-parse HEAD^1)" = "$EXPECTED_BASE"
          test "$(git rev-parse HEAD^2)" = "$EXPECTED_HEAD"
      # <language setup step here, e.g. actions/setup-node / setup-python>
      - name: Install
        run: <install command>
      - name: Test
        run: <test command>

  merged-result:
    name: merged-result / ${{ github.event.pull_request.base.sha }} / ${{ github.event.pull_request.head.sha }}
    if: github.event_name == 'pull_request'
    needs: test
    runs-on: ubuntu-latest
    steps:
      - run: echo "this exact merge of base and head passed the test job"
```

The CI token only needs to read the code; a job that must write (like the release template) escalates its own permissions per-job.

When generating CI for guarded integration, copy the `merged-result` job and checkout-binding
step exactly as the template gives them. The machine contract is `scripts/hard_edges.py`'s
`MERGED_RESULT` and `merge_check`; use `reference/orchestrator.md`'s Guarded operations section
for invocation.

Third-party (non-`actions/*`) actions: pin to a full commit SHA, not a tag — a tag can be rewritten under you (the 2025 tj-actions compromise; SHA-pinned repos were immune). First-party `actions/*` at a version tag is fine. A SHA never updates itself — that is exactly what the Dependabot file below keeps current.

Artifacts: upload one only when a later step or a person actually consumes it, and always set `retention-days:` — the default keeps every copy for 90 days, and on a private repo the 500 MB storage quota fills in days of routine pushes, after which uploads start failing. CI output is not an archive: actual release deliverables ship through the release pipeline; a report worth retaining goes where `reference/where-it-goes.md` sends it rather than being published merely to keep it, and any build can be reproduced from its commit.

Minutes are the other finite quota, and the one that stops everything: on a private repo an exhausted monthly balance runs *no* workflow at all — CI, release and Dependabot alike — so the merge gate goes absent rather than red (a public repo's standard runners are free, so this cannot happen there). Treat exhaustion as a pipeline-spend bug before an allowance problem; the usual causes are cheap to fix — a job triggering on every push to every branch when `pull_request` alone would do, a matrix kept wide out of habit, no dependency cache so every run re-downloads the world, no `paths:` filter so a docs typo rebuilds everything, no `concurrency:` group canceling superseded branch runs, and the default 6-hour `timeout-minutes` letting a hung job burn an afternoon. Fix the spend, and tell the human the balance is out — topping it up, or making the repo public, is theirs. The check-2 fallback (`reference/ci-cannot-run.md`) is what you do meanwhile, never the answer.

The minimal template above includes none of these controls; add the language setup action's `cache:` input, job-level `timeout-minutes:`, `on: pull_request: paths:`, `strategy: matrix:`, and a top-level `concurrency:` group.

A self-hosted runner is the other way out, and it is not a degradation: the merge gates are unchanged and only the compute moves to a machine you own (a one-line `runs-on:` change), so no minutes are charged. Standing one up is the human's call, like topping up and going public. **Register it ephemeral — one job, then it deregisters and exits — never persistent.** A persistent runner hands every job the last one's workspace, and that was measured in this method's own repository: a marker file written by one job was still there in the next, and the probe that should have caught it reported success, because a `run:` block's exit status is its last command's. Green on a machine's accumulated state is a weaker claim than the one check 2 makes.

Three costs decide whether to reach for it at all. The machine has to be up when a PR lands — a run queued behind an offline one is not an outage and not a fallback trigger, and a job still `queued` past five minutes with no runner registering means the loop that starts them is down, which is the human's to restart. It must **never** be used on a public repo: a fork's pull request would run on your hardware, automatically for a repeat contributor and one approval click away for a first-timer. And the machine holds no secret it does not need — the image carries the toolchain, and whatever a job needs arrives through the workflow's own `secrets:` and lives only for that job, which ephemeral makes enforceable and persistent leaves a promise. When the constraint is minutes rather than a platform that is down, reach for this before the check-2 fallback (`reference/ci-cannot-run.md`).

At founding, apply branch protection last with `guard protection --apply --check test`;
`reference/prd.md` owns the setup order. For expected settings, plan limits and provisioning,
use `scripts/guard protection --help` and `reference/orchestrator.md`'s Branch protection section.

Protection changes only who enforces the ceremony, not the ceremony itself. Use your role page's two-checks paragraph for review and CI, including its bare-version-bump exception; protection does not invent further exceptions. Required status protection makes GitHub enforce the CI portion and nothing else — what it leaves open, and the role guards and reviewed-head merge route that cover it, are in `reference/orchestrator.md`'s Guarded operations section.

## Pipeline pin upkeep (`.github/dependabot.yml`, generated in the same setup step)

The pipeline's own parts — the `uses:` pins in these workflows — rot on GitHub's clock, not the project's: actions age out of support and a SHA pin never updates itself. Generate this file in the same setup step; a bot then opens PRs bumping those pins as new versions land, and each rides the normal two checks like any other change. This keeps the pipeline's own actions current only — the project's own dependencies stay out of the method's scope (that ruling stands, now narrowed to say so explicitly).

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

## Release template (`.github/workflows/release.yml`)

```yaml
name: Release
on:
  push:
    tags: ['v*']

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      # <language setup + install + build steps>
      - name: Test
        run: <test command>          # green tests gate the release too
      - name: Publish
        run: <publish/deploy step>   # gh release create / npm publish / deploy ...
```

If the project genuinely has no release form yet, generate CI only and record the open release question in the PRD's constraints — don't invent ceremony.

Both files land in the target repo under `.github/workflows/`.

The same setup step also generates the repo-root `CLAUDE.md`, when the project has anything to put in it — `reference/repo-claude-md.md` (that file stays the operational memory on every harness). The same founding commit also seeds the in-repo worktree root into `.gitignore` (`/.claude/worktrees/`) — the line every later worktree creation checks for (`reference/orchestrator.md`'s Worktree lifecycle section, Birth).

## When CI goes red with no change of yours

A green run means the code passed today, not that the pipeline is current. GitHub ends-of-life the runtimes its actions run on, on its own cutoff dates — so a pipeline with zero project changes can go from green to red, usually after months of deprecation-warning annotations inside still-green runs. If a gate goes red mid-task with no relevant change of yours, suspect a vendor deprecation before your own code; when a task already touches a workflow file, bump any `uses:` the run flags as deprecated in the same diff.

For protection provisioning/checks, use `reference/orchestrator.md`'s Branch protection section;
see `scripts/guard`'s `main` for the payload.
