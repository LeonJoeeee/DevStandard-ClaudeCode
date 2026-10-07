"""Check the shipped Claude-native role carriers (issues #201, #334, #339, #402, #409).

`agents/worker.md` is hand-authored frontmatter plus a GENERATED body, because the Claude harness
loads an agent definition's body as the subagent's system prompt, and that is what carries the role
on the explicit `--implementation claude` path without a read (ADR 0060).

**The concatenation rule: the worker's body is the exact bytes of `reference/worker.md` followed by
the exact bytes of `reference/harness-claude.md`, in that order, with nothing between them.** The
shared contract page and the Claude harness page are separate sources (ADR 0061) and separate
reads; the definition body is the one carrier that delivers both to a Claude worker and survives its
compaction. Both stay hand-written; only the body is generated. Run this gate with `--write` to
regenerate it in place; without it the gate only checks, so CI fails on a body that has drifted from
either source.
"""

from pathlib import Path
import re
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
ROLES = {
    "worker": "reference/worker.md",
    "reviewer": "reference/code-review-prompt.md",
}
# The hook role a definition pins in its own frontmatter. The reviewer pins none: it is spawned
# by an orchestrator, whose hook maps the reviewer agent type onto the reviewer role.
HOOK_ROLE = {"worker": "worker"}
HOOK_COMMAND = '"${CLAUDE_PLUGIN_ROOT}/hooks/pre-tool-use" --role '
# Definitions whose body is generated, and the ordered sources it concatenates byte for byte.
# The reviewer is not one: its judging contract is assembled per review by `scripts/review-packet`
# and rides the prompt, so its definition body is hand-written and routes to no second installed
# contract.
GENERATED_BODY = {'worker': ('reference/worker.md', 'reference/harness-claude.md')}

args = sys.argv[1:]
assert set(args) <= {'--write'}, f'usage: check-agents.py [--write], got {args}'


def frontmatter(path):
    """`(b'', yaml bytes, body bytes)` for one definition file, split on its own fences.

    Bytes throughout, because this gate's claim is byte identity and text mode would not carry
    it: `read_text` translates newlines, so a CRLF body would compare equal to an LF source and
    pass a check that says the two are the same bytes (#411).
    """
    parts = path.read_bytes().split(b"---\n", 2)
    assert len(parts) == 3 and parts[0] == b"", f"{path.name}: missing YAML frontmatter"
    return parts


def generated_body(name):
    """The exact bytes the definition's body must be: its sources, in order, joined by nothing."""
    sources = GENERATED_BODY[name]
    for source in sources:
        assert (ROOT / source).is_file(), f"{name}: missing body source {source}"
    return b"".join((ROOT / source).read_bytes() for source in sources)


if '--write' in args:
    for name in GENERATED_BODY:
        path = ROOT / "agents" / f"{name}.md"
        _, header, _ = frontmatter(path)
        path.write_bytes(b"---\n" + header + b"---\n" + generated_body(name))
        print(f"{name}: body regenerated from {' + '.join(GENERATED_BODY[name])}")

binding_source = (ROOT / 'reference/worker.md').read_text().split(
    '<!-- BEGIN WORKER SKILLS -->', 1)[1].split('<!-- END WORKER SKILLS -->', 1)[0]
worker_skills = re.findall(r'`(superpowers:[^`]+)`', binding_source)
assert len(worker_skills) == 3 and len(set(worker_skills)) == 3, 'missing worker bindings'

for name, source in ROLES.items():
    path = ROOT / "agents" / f"{name}.md"
    assert path.is_file(), f"missing agent definition: {path.relative_to(ROOT)}"
    parts = frontmatter(path)
    metadata = yaml.safe_load(parts[1].decode())
    assert isinstance(metadata, dict), f"{name}: frontmatter must be a mapping"
    assert metadata.get("name") == name, f"{name}: use an unscoped role name"
    description = metadata.get("description")
    assert isinstance(description, str) and description.strip(), f"{name}: missing description"
    assert metadata.get("model") == "opus", f"{name}: model must use the opus tier alias"
    if name == "worker":
        claude_effort = re.search(
            r'^\| worker \| `[^`]+` at `[^`]+` \| `[^`]+` at `([^`]+)` \|$',
            (ROOT / 'reference/orchestrator.md').read_text(), re.M)
        assert claude_effort and metadata.get("effort") == claude_effort[1], \
            "worker: effort must match the Claude cell in orchestrator.md's Model and effort table"
    # No tool allowlist anywhere (#334). A definition with no `tools` field inherits the
    # session's whole tool set, MCP servers included — which is how a worker reaches `Agent`
    # to spawn subagents of its own (#339). The reviewer forbids the built-in writers by name
    # and is read-only by contract; the worker forbids nothing.
    assert "tools" not in metadata, f"{name}: must carry no tool allowlist"
    expected_disallowed = None if name == "worker" else "Write, Edit, NotebookEdit"
    assert metadata.get("disallowedTools") == expected_disallowed, \
        f"{name}: disallowedTools must be {expected_disallowed!r}"
    hook_role = HOOK_ROLE.get(name)
    hooks = metadata.get("hooks")
    if hook_role is None:
        assert hooks is None, f"{name}: must pin no role hook of its own"
    else:
        commands = [h["command"] for entry in hooks["PreToolUse"] for h in entry["hooks"]]
        assert commands == [HOOK_COMMAND + hook_role], \
            f"{name}: must pin the {hook_role} role hook, got {commands}"
    expected_skills = worker_skills if name == "worker" else []
    assert metadata.get("skills") == expected_skills, f"{name}: incorrect skill bindings"
    assert (ROOT / source).is_file(), f"{name}: missing role source {source}"
    if name in GENERATED_BODY:
        # The carrier assertion: the harness delivers this body as the system prompt, so a body
        # byte-identical to the concatenated sources IS both pages arriving without a read.
        expected = generated_body(name)
        assert parts[2] == expected, (
            f"{name}: body is not {' + '.join(GENERATED_BODY[name])} concatenated byte for byte; "
            "regenerate with check-agents.py --write")
    # The Claude column of the page's helper table is restated on each Claude carrier, because
    # neither role reads the orchestrator page (#460); a column that moves must move them too.
    helper_models = set(re.findall(
        r'^\| [^|`]+? \| `[^`|]+` at `[^`|]+` \| `([^`|]+)` \|$',
        (ROOT / 'reference/orchestrator.md').read_text(), re.M))
    assert helper_models, "the orchestrator page states no helper table"
    carrier = parts[2].decode()
    missing = sorted(m for m in helper_models if f"`{m}`" not in carrier)
    assert not missing, f"{name}: body must name each Claude helper model, missing {missing}"
    binding = (f"{' + '.join(GENERATED_BODY[name])} concatenated as body"
               if name in GENERATED_BODY else "hand-authored body")
    print(f"{name}: frontmatter, no allowlist, writer denial, skills, opus alias, hook "
          f"and {binding} OK")
