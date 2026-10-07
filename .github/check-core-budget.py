"""Delivery gate: every shipped artifact arrives whole through its declared handlers.

The name is the #205 measurement's; what it checks is ADR 0059's shape. There is no shared
core page and no size budget on a role page any more: a page larger than one hook output is
emitted across as many ordered handler calls as `hooks/hooks.json` declares, and the parts
concatenate to the file's exact bytes. What is still capped is one part's complete context,
and the failure this gate exists to catch is the hook degrading to an instructed read —
runtime behaviour, never a permitted CI state.

That cap is Claude Code's fixed persistence boundary (#415), the only host since #459 (ADR
0063): a handler names the orchestrator page, its part and the declared total, and nothing else.

The gate drives the shipped handler commands themselves, so a page that outgrows its declared
handlers fails here rather than losing its tail in a session.
"""

import json
import os
from pathlib import Path
import re
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ROLE_PAGES = ('reference/orchestrator.md', 'reference/worker.md')
ARTIFACT, PAGE = 'orchestrator', 'reference/orchestrator.md'

hook_source = (ROOT / 'hooks/session-start').read_text()
CAP = int(re.search(r'^CLAUDE_CAP_BYTES=(\d+)$', hook_source, re.M)[1])

for page in ROLE_PAGES:
    assert (ROOT / page).is_file(), f'missing role page: {page}'
assert not (ROOT / 'core.md').exists(), 'core.md was deleted; a role page carries the workflow now'

# The declared handlers, read from what ships: part index and declared total, per call.
groups = json.loads((ROOT / 'hooks/hooks.json').read_text())['hooks']['SessionStart']
calls = []
for group in groups:
    for handler in group['hooks']:
        words = shlex.split(handler['command'])
        assert len(words) == 4 and words[1] == ARTIFACT, (
            f'a SessionStart handler must name the orchestrator part and total and nothing '
            f'else: {words}')
        calls.append((int(words[2]), int(words[3])))
totals = {total for _, total in calls}
assert totals == {len(calls)}, (
    f'{len(calls)} declared handlers but they announce {sorted(totals)} parts')
assert sorted(index for index, _ in calls) == list(range(1, len(calls) + 1)), (
    f'declared part numbers are not 1..{len(calls)}')

env = {k: v for k, v in os.environ.items()
       if k not in ('PLUGIN_DATA', 'CLAUDE_PLUGIN_DATA', 'DEVSTANDARD_ROLE')}
env['CLAUDE_PLUGIN_DATA'] = 'test'

sizes = []
payload = ''
for index, total in sorted(calls):
    emitted = json.loads(subprocess.check_output(
        [str(ROOT / 'hooks/session-start'), ARTIFACT, str(index), str(total)],
        input=b'{"source":"startup"}', env=env, cwd='/tmp', timeout=60))
    context = emitted.get('hookSpecificOutput', {}).get('additionalContext', '')
    assert len(context.encode()) <= CAP, f'{PAGE} part {index}: context exceeds the cap'
    # A page carries the words "IN FULL" itself, so the degraded mode is read from the hook's own
    # system message, which only that branch writes.
    assert 'requires an IN FULL read' not in emitted.get('systemMessage', ''), (
        f'{PAGE} part {index}: the hook fell back to the instructed read — the page needs more '
        f'than the {len(calls)} handlers hooks.json declares, or carries a line longer than one '
        'part. Runtime behaviour, never a permitted CI state.')
    if context:
        head, blank, body = context.partition('\n\n')
        assert blank, f'{PAGE} part {index}: emitted context carries no part header'
        sizes.append(len(context.encode()))
        payload += body
page_bytes = (ROOT / PAGE).read_bytes()
assert payload.encode() == page_bytes, f'{PAGE}: the delivered parts do not reconstruct the page'
shape = 'one part' if len(sizes) == 1 else f'{len(sizes)} of {len(calls)} declared parts'
print(f'{PAGE}: {len(page_bytes)} bytes arrive whole in {shape}, contexts {sizes} (cap {CAP})')
print('One page per role, delivered whole; no instructed-read fallback in any shipped artifact')
