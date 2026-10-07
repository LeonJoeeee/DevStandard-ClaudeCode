#!/usr/bin/env python3
"""Qualify the dispatched Codex CLI executor against a local Responses fixture, without model usage.

Requires Python 3.11+ and Codex CLI 0.153.4+. No user configuration, trust record,
marketplace, HOME, or CODEX_HOME is changed. Existing rules remain in force.
The model output is deterministic probes and final text; writes stay in disposable fixtures.

Codex no longer hosts the method (#459, ADR 0063); what it still does is run a worker or a
read-only gating review that a Claude Code orchestrator dispatches. So every case here runs the
executor exactly as `scripts/dispatch --implementation codex` does: the fixed role hook from
`scripts/hard_edges.py`'s `codex_hook_config`, trusted for one invocation, the dispatched brief on
stdin, and the MCP admission each purpose gets.
"""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import runpy
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import time


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
sys.dont_write_bytecode = True
from hard_edges import codex_hook_config  # noqa: E402 -- the dispatcher's own hook settings
# What no dispatched executor may be handed: a DevStandard startup context. The executor runs only
# the fixed role hook, so the orchestrator page cannot reach it by any handler.
STARTUP_CONTEXT = 'DevStandard operating context'
ALLOW = 'DEVSTANDARD_RUNTIME_ALLOWED_342'
DENY = 'DEVSTANDARD_RUNTIME_EXECUTED_342'
MCP_TOKEN = 'DEVSTANDARD_MCP_TOOL_RAN_358'
MCP_SERVER_NAME = 'probe'
MCP_TOOL_NAME = 'devstandard_probe'
MCP_BINDING = 'mcp__' + MCP_SERVER_NAME + '__' + MCP_TOOL_NAME
# The exact setting scripts/dispatch appends per host MCP server. Held here as well so this
# case fails if the dispatcher stops emitting it, not only if the CLI stops honouring it.
MCP_APPROVAL = 'mcp_servers.{name}.default_tools_approval_mode="approve"'
MCP_SERVER = '''import json, sys
from pathlib import Path
LOG = Path(sys.argv[1])
TOOL = {'name': %r, 'description': 'Return one fixed token. No side effects.',
        'inputSchema': {'type': 'object', 'properties': {}, 'additionalProperties': False}}
RESULTS = {'initialize': {'protocolVersion': '2025-06-18', 'capabilities': {'tools': {}},
                          'serverInfo': {'name': 'devstandard-probe', 'version': '1.0.0'}},
           'tools/list': {'tools': [TOOL]},
           'tools/call': {'content': [{'type': 'text', 'text': %r}], 'isError': False},
           'ping': {}}
for line in sys.stdin:
    if not line.strip():
        continue
    message = json.loads(line)
    with LOG.open('a') as record:
        record.write(json.dumps({'method': message.get('method')}) + '\\n')
    if 'id' not in message:
        continue
    result = RESULTS.get(message.get('method'))
    answer = ({'jsonrpc': '2.0', 'id': message['id'], 'result': result} if result is not None else
              {'jsonrpc': '2.0', 'id': message['id'],
               'error': {'code': -32601, 'message': 'unsupported'}})
    sys.stdout.write(json.dumps(answer) + '\\n')
    sys.stdout.flush()
''' % (MCP_TOOL_NAME, MCP_TOKEN)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def toml(value):
    """Encode the small JSON-compatible inline TOML config used by this fixture."""
    if isinstance(value, dict):
        return '{' + ','.join(json.dumps(key) + '=' + toml(item)
                              for key, item in value.items()) + '}'
    if isinstance(value, list):
        return '[' + ','.join(toml(item) for item in value) + ']'
    return json.dumps(value)


def inventory(fixture):
    """Refuse external hook layers before granting this invocation's hook trust.

    User config is ignored and plugins are disabled by supported CLI overrides.
    Standalone hook files and managed system config are not overridden that way.
    Conservative refusal is preferable to executing an unrelated user's hook.
    """
    codex_home = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    candidates = [codex_home / 'hooks.json', codex_home / 'requirements.toml',
                  Path('/etc/codex/config.toml'),
                  Path('/etc/codex/requirements.toml')]
    for parent in (fixture, *fixture.parents):
        candidates += [parent / '.codex/hooks.json', parent / '.codex/config.toml']
    found = sorted({str(path) for path in candidates if path.exists()})
    require(not found, 'runtime isolation unavailable: external hook/config layers: '
            + ', '.join(found))
    return {'external_hook_layers': [], 'user_config': 'ignored',
            'plugins': 'disabled for this invocation', 'execpolicy_rules': 'preserved'}


class ResponsesFixture:
    def __init__(self, forbidden, allowed_command=None):
        self.forbidden = forbidden
        self.allowed_command = allowed_command
        self.history_reads = 0
        self.requests = []
        self.errors = []
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def do_GET(self):
                if self.path == '/history':
                    outer.history_reads += 1
                    body = b'NETWORK_HISTORY_READ_478'
                    self.send_response(200)
                    self.send_header('Content-Length', str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
                # Custom providers are queried for model metadata before the first turn.
                # An empty catalog deliberately selects Codex's fallback metadata.
                if self.path.split('?', 1)[0] != '/v1/models':
                    outer.errors.append('unexpected local endpoint: ' + self.path)
                    self.send_error(404)
                    return
                if self.headers.get('Authorization'):
                    outer.errors.append('fixture unexpectedly received authentication')
                    self.send_error(403)
                    return
                body = b'{"models":[]}'
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self):
                try:
                    require(self.path.rstrip('/') == '/v1/responses',
                            'unexpected local endpoint: ' + self.path)
                    require(not self.headers.get('Authorization'),
                            'fixture unexpectedly received authentication')
                    require(self.headers.get('Content-Encoding', 'identity') == 'identity',
                            'request compression must be disabled for the fixture')
                    body = self.rfile.read(int(self.headers['Content-Length']))
                    request = json.loads(body)
                    outer.requests.append(request)
                    require(len(outer.requests) <= 3, 'unexpected extra model continuation')
                    item = outer.response_item(request, len(outer.requests) - 1)
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/event-stream')
                    self.send_header('Connection', 'close')
                    self.end_headers()
                    response = {'id': 'resp_devstandard_' + str(len(outer.requests)),
                                'object': 'response', 'status': 'completed', 'output': [item],
                                'usage': {'input_tokens': 1, 'output_tokens': 1,
                                          'total_tokens': 2}}
                    for event in [
                        {'type': 'response.created', 'response': dict(response, status='in_progress', output=[])},
                        {'type': 'response.output_item.added', 'output_index': 0, 'item': item},
                        {'type': 'response.output_item.done', 'output_index': 0, 'item': item},
                        {'type': 'response.completed', 'response': response},
                    ]:
                        self.wfile.write(('data: ' + json.dumps(event) + '\n\n').encode())
                    self.wfile.flush()
                except Exception as error:
                    outer.errors.append(str(error))
                    self.send_error(500, 'fixture refused request')

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *_args):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def response_item(self, request, index):
        if index == 2:
            return {'type': 'message', 'id': 'msg_fixture', 'role': 'assistant',
                    'status': 'completed', 'content': [{'type': 'output_text',
                    'text': 'DevStandard runtime fixture complete.', 'annotations': []}]}
        tools = {tool.get('name'): tool for tool in request.get('tools', [])}
        require('exec_command' in tools, 'Codex did not expose the expected unified exec tool')
        # The refused probe stays a harmless `printf`, with the guarded word as an unquoted
        # operand. It used to sit inside the quoted format string; since #351 the hook does
        # not read quoted text, so the word has to stand in the command itself for this
        # probe to exercise a refusal (`reference/orchestrator.md`, The role hook).
        command = ((self.allowed_command or 'printf ' + shlex.quote(ALLOW + '\n')) if index == 0 else
                   'printf ' + shlex.quote(DENY + '\n') + ' ' + self.forbidden)
        return {'type': 'function_call', 'id': 'fc_' + str(index),
                'call_id': 'call_' + str(index), 'name': 'exec_command',
                'arguments': json.dumps({'cmd': command, 'login': False,
                                         'max_output_tokens': 1000 if self.allowed_command else 100})}


class McpFixture(ResponsesFixture):
    """Two turns: call the single tool the local stdio MCP server offers, then finish.

    Codex offers that tool in one of two shapes, and this case exercises whichever the host
    actually produces rather than configuring one into existence. Without code mode the server
    arrives as its own `mcp__<server>` namespace. With code mode — the default a dispatched
    child runs under — only `exec` is offered and MCP tools live on the JavaScript `tools`
    object as `mcp__<server>__<tool>`, so a flip in that default cannot quietly leave this case
    exercising no MCP call at all.
    """

    def __init__(self, prefer=None):
        super().__init__('gh pr merge')  # No shell probe runs in this case.
        self.prefer, self.shape = prefer, None

    @staticmethod
    def catalog(request):
        supplied = list(request.get('tools', []))
        for item in request.get('input', []):
            if item.get('type') == 'additional_tools':
                supplied.extend(item.get('tools', []))
        found = {}
        for tool in supplied:
            if tool.get('type') == 'namespace':
                for member in tool.get('tools', []):
                    found[member['name']] = tool['name']
            elif tool.get('name'):
                found[tool['name']] = None
        return found

    def response_item(self, request, index):
        if index:
            return {'type': 'message', 'id': 'msg_mcp', 'role': 'assistant', 'status': 'completed',
                    'content': [{'type': 'output_text', 'text': 'MCP fixture complete.',
                                 'annotations': []}]}
        item, self.shape = mcp_call_item(request, 'fc_mcp', 'call_mcp', self.prefer)
        return item


def mcp_call_item(request, item_id, call_id, prefer=None):
    """Build the one MCP tool call in whichever shape the host actually offers this turn.

    Returns the response item and the label naming that shape. It decides nothing `McpFixture`
    did not already decide, and asserts nothing.
    """
    catalog = McpFixture.catalog(request)
    direct = None if prefer == 'code-mode' else next(
        (name for name, space in catalog.items()
         if space and str(space).startswith('mcp__')), None)
    if direct:
        return ({'type': 'function_call', 'id': item_id, 'call_id': call_id,
                 'namespace': catalog[direct], 'name': direct, 'arguments': '{}'},
                'mcp namespace tool')
    require('exec' in catalog, 'Codex offered neither an MCP namespace nor code mode: '
            + repr(sorted(catalog)))
    # Caught and reported as text, so a denied call reaches the model as a result to
    # assert on rather than as an opaque script failure.
    script = ('try { text(JSON.stringify(await tools.' + MCP_BINDING + '({}))); } '
              "catch (error) { text('MCP_CALL_ERROR ' + String(error)); }")
    item = {'type': 'custom_tool_call', 'id': item_id, 'call_id': call_id,
            'name': 'exec', 'input': script}
    if catalog['exec']:
        item['namespace'] = catalog['exec']
    return item, 'code-mode tools.' + MCP_BINDING


def run_mcp_case(binary, name, *, sandbox, admit, prefer=None, logs=None):
    """#358: a dispatched Codex child could see its host's MCP tools and never call one.

    `codex exec` is non-interactive, so its approval policy is `never`, and `never` auto-rejects
    every MCP tool call — indistinguishably from an unreachable server. The `admit=False` case is
    that defect, kept as the control: it is what CI was green on. The rest are the fix — one per
    purpose, proving the admission composes with each sandbox mode rather than trading it away, and
    one pinning the code-mode call shape a dispatched child runs under.
    This is also the guard for the next `@openai/codex` pin bump, which is half its value: the
    behaviour already moved once between 0.149.1 and 0.153.4.
    """
    require(MCP_APPROVAL in (ROOT / 'scripts/dispatch').read_text(),
            'scripts/dispatch no longer emits the qualified MCP approval setting')
    with tempfile.TemporaryDirectory(prefix='devstandard-mcp-') as scratch:
        scratch = Path(scratch).resolve()
        project = scratch / 'project'
        project.mkdir()
        inventory(project)
        subprocess.run(['git', 'init', '--quiet', str(project)], check=True, capture_output=True)
        # A run that configures an MCP server persists a project trust entry, which
        # `--ignore-user-config` does not prevent: that flag governs reading, not writing.
        # This case therefore gets its own CODEX_HOME, so it changes no user state — the
        # promise this file's docstring makes.
        codex_home = scratch / 'codex-home'
        codex_home.mkdir()
        server = scratch / 'mcp-server.py'
        server.write_text(MCP_SERVER)
        log = scratch / 'mcp-calls.jsonl'
        with McpFixture(prefer) as fixture:
            settings = {
                'model_provider': 'devstandard-fixture',
                'model_providers.devstandard-fixture': {
                    'name': 'Local deterministic DevStandard fixture',
                    'base_url': 'http://127.0.0.1:' + str(fixture.server.server_port) + '/v1',
                    'wire_api': 'responses', 'requires_openai_auth': False,
                    'supports_websockets': False, 'request_max_retries': 0,
                    'stream_max_retries': 0, 'stream_idle_timeout_ms': 5000},
                'features.hooks': False, 'features.plugins': False,
                'features.apps': False, 'features.remote_plugin': False,
                'features.enable_request_compression': False,
                # Code mode decides which shape the MCP tool arrives in, and a dispatched child
                # runs under whichever the host defaults to, so neither shape is assumed: cases
                # leave it alone, and one case pins it on to cover that arm deliberately.
                'features.shell_snapshot': False,
                'features.multi_agent': False, 'features.skip_host_skill_discovery': True,
                'web_search': 'disabled', 'check_for_update_on_startup': False,
                # The policy axis is not the lever: `exec` ignores every value it is given.
                'approval_policy': 'never', 'analytics.enabled': False,
                # Local, deterministic, offline: one tool returning one fixed token.
                'mcp_servers.' + MCP_SERVER_NAME: {
                    'command': sys.executable, 'args': [str(server), str(log)],
                    'startup_timeout_sec': 30, 'tool_timeout_sec': 30},
            }
            if prefer == 'code-mode':
                settings['features.code_mode'] = True
            command = [binary, 'exec', '--ignore-user-config', '--ephemeral', '--json',
                       '-s', sandbox, '-C', str(project), '-m', 'devstandard-fixture']
            for key, value in settings.items():
                command += ['-c', key + '=' + toml(value)]
            if admit:
                command += ['-c', MCP_APPROVAL.format(name=MCP_SERVER_NAME)]
            command.append('Call the one MCP probe tool the fixture offers, then finish.')
            env = dict(os.environ, CODEX_HOME=str(codex_home))
            for key in ('DEVSTANDARD_ROLE', 'PLUGIN_DATA', 'CLAUDE_PLUGIN_DATA',
                        'PLUGIN_ROOT', 'CLAUDE_PLUGIN_ROOT', 'OPENAI_API_KEY'):
                env.pop(key, None)
            started = time.monotonic()
            result = subprocess.run(command, env=env, stdin=subprocess.DEVNULL,
                                    capture_output=True, text=True, timeout=90)
        methods = [json.loads(line)['method'] for line in log.read_text().splitlines()] \
            if log.exists() else []
        # Code mode returns the same call as a custom_tool_call_output, so read both forms.
        answer = str({item['call_id']: item.get('output', '')
                      for item in fixture.requests[-1].get('input', [])
                      if item.get('type') in ('function_call_output', 'custom_tool_call_output')}
                     .get('call_mcp', '<missing>'))
        diagnostic = json.dumps({'server_methods': methods, 'tool_result': answer[-1500:],
                                 'stderr_tail': result.stderr[-2000:]})
        if logs:
            (logs / (name + '.events.jsonl')).write_text(result.stdout)
            (logs / (name + '.mcp.json')).write_text(diagnostic + '\n')
        require(result.returncode == 0, name + ': Codex failed: ' + result.stderr[-2000:])
        require(not fixture.errors, name + ': ' + repr(fixture.errors))
        # The server's own method log and the model's tool result are independent witnesses:
        # neither alone separates "the call was refused" from "the server never answered".
        require('tools/list' in methods, name + ': the MCP server was never listed; ' + diagnostic)
        if admit:
            require('tools/call' in methods, name + ': no call reached the server; ' + diagnostic)
            require(MCP_TOKEN in answer, name + ': the tool result never reached the model; '
                    + diagnostic)
        else:
            require('tools/call' not in methods, name + ': control case called the server; '
                    + diagnostic)
            require('approval policy is never' in answer,
                    name + ': control case was refused for another reason; ' + diagnostic)
        summary = {'case': name, 'status': 'pass', 'sandbox': sandbox,
                   'codex_home': 'scratch', 'user_state': 'unchanged',
                   'mcp_approval': 'per-server approve' if admit else 'none (control)',
                   'call_shape': fixture.shape, 'server_methods': methods,
                   'seconds': round(time.monotonic() - started, 2)}
        if logs:
            (logs / (name + '.summary.json')).write_text(json.dumps(summary, indent=2) + '\n')
        return summary


def tool_results(request):
    return {item['call_id']: item.get('output', '') for item in request.get('input', [])
            if item.get('type') == 'function_call_output'}


def fixture_settings(port, *, enabled=True):
    """The `codex exec` settings every shell-hook case shares: an isolated local provider."""
    return {
        'model_provider': 'devstandard-fixture',
        'model_providers.devstandard-fixture': {
            'name': 'Local deterministic DevStandard fixture',
            'base_url': 'http://127.0.0.1:' + str(port) + '/v1',
            'wire_api': 'responses', 'requires_openai_auth': False,
            'supports_websockets': False, 'request_max_retries': 0,
            'stream_max_retries': 0, 'stream_idle_timeout_ms': 5000},
        'features.hooks': enabled, 'features.plugins': False,
        'features.apps': False, 'features.remote_plugin': False,
        'features.enable_request_compression': False,
        'features.shell_snapshot': False, 'features.code_mode': False,
        'features.multi_agent': False, 'features.skip_host_skill_discovery': True,
        'web_search': 'disabled', 'check_for_update_on_startup': False,
        'approval_policy': 'never', 'analytics.enabled': False,
    }


def run_case(binary, fixture, name, *, role, trusted=False, enabled=True, logs=None,
             prompt=None, carries=None):
    """One dispatched executor run through the shipped role hook.

    `trusted` adds the dispatcher's `--dangerously-bypass-hook-trust`; without it, or with hooks
    disabled, the hook must not run at all — which is also what shows the bypass never persisted
    trust into a later invocation. `prompt` replaces the fixture's probe instruction with a
    dispatched worker's real one, and `carries` is the (source paths, resolved text) that prompt
    is supposed to deliver — the prompt, not a hook, is what brings a Codex worker its role pages.
    """
    # Each role's own surviving rule since #425: the reviewer's is a `gh api` write flag,
    # and no single word is refused for more than one role any more.
    forbidden = {'worker': 'merge', 'reviewer': 'gh api -X'}[role]
    with ResponsesFixture(forbidden) as server:
        settings = fixture_settings(server.server.server_port, enabled=enabled)
        command = [binary, 'exec', '--ignore-user-config', '--ephemeral', '--json',
                   '-s', 'workspace-write' if role == 'reviewer' else 'read-only',
                   '-C', str(fixture), '-m', 'devstandard-fixture']
        if role == 'reviewer':
            command += ['-c', 'sandbox_workspace_write.network_access=true']
        for key, value in settings.items():
            command += ['-c', key + '=' + toml(value)]
        # The dispatcher's own hook settings, verbatim: the fixed role hook and its role.
        for setting in codex_hook_config(ROOT, role).splitlines():
            command += ['-c', setting]
        if trusted:
            command.append('--dangerously-bypass-hook-trust')
        # The dispatcher's own transport since #454: `-` is the CLI's documented "read the prompt
        # from stdin", and a brief as long as a real issue record cannot be an argv element at
        # all. Probing it here is what keeps "the model saw these exact bytes" a statement about
        # the shipped path rather than about a shape only this test builds.
        instructions = (prompt
                        or 'Run the two harmless local printf probes supplied by the fixture, then finish.')
        command.append('-')
        env = dict(os.environ)
        for key in ('DEVSTANDARD_ROLE', 'PLUGIN_DATA', 'CLAUDE_PLUGIN_DATA',
                    'PLUGIN_ROOT', 'CLAUDE_PLUGIN_ROOT', 'OPENAI_API_KEY'):
            env.pop(key, None)
        env['DEVSTANDARD_ROLE'] = role  # set on the supervisor by the dispatcher, and inherited
        started = time.monotonic()
        result = subprocess.run(command, env=env, input=instructions,
                                capture_output=True, text=True, timeout=45)
        if logs:
            (logs / (name + '.events.jsonl')).write_text(result.stdout)
            (logs / (name + '.stderr.log')).write_text(result.stderr)
        require(result.returncode == 0, name + ': Codex failed: ' + result.stderr[-2000:])
        require(not server.errors, name + ': ' + repr(server.errors))
        require(len(server.requests) == 3,
                name + ': expected two tool calls and final request, got ' + str(len(server.requests))
                + '; ' + result.stderr[-1000:])
        active = trusted and enabled
        actual = '\n'.join(text_fragments(server.requests[0].get('input', [])))
        require(STARTUP_CONTEXT not in actual,
                name + ': a DevStandard startup context reached a dispatched executor')
        if carries:
            # #396's other half: a dispatched Codex CLI worker's role page is carried by the
            # prompt, not by a hook, so what it owes is the page's exact bytes in the host's own
            # request — once, undivided.
            carried_sources, carried_text = carries
            found = actual.count(carried_text)
            require(found == 1, name + ': the dispatched ' + ' + '.join(carried_sources)
                    + ' reached the model ' + str(found)
                    + ' times, want exactly one byte-identical copy')
            if logs:
                (logs / (name + '.role-delivery.json')).write_text(json.dumps(
                    {'artifact': list(carried_sources),
                     'page_bytes': [len((ROOT / path).read_bytes()) for path in carried_sources],
                     'resolved_page_bytes': len(carried_text.encode()),
                     'carrier': "scripts/dispatch brief on the codex exec child's stdin",
                     'arrived_byte_identical_in_request': True}, indent=2) + '\n')
        outputs = tool_results(server.requests[2])
        events = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
        commands = [event['item'] for event in events if event.get('type') == 'item.completed'
                    and event.get('item', {}).get('type') == 'command_execution']
        # An admitted tool can still fail before its process starts (for example,
        # Linux sandbox setup). Keep that cause in CI output even without --log-dir.
        # These are only the fixture's fixed printf results, never full model requests.
        allow_diagnostic = json.dumps({
            'tool_output': str(outputs.get('call_0', '<missing call_0 result>'))[-2500:],
            'command_events': [{key: item.get(key) for key in
                               ('status', 'exit_code', 'command', 'aggregated_output')}
                              for item in commands],
            'stderr_tail': result.stderr[-3000:],
        })
        require(ALLOW in str(outputs.get('call_0', '')),
                name + ': admitted shell did not execute; ' + allow_diagnostic)
        require(any(item.get('aggregated_output') == ALLOW + '\n'
                    and item.get('exit_code') == 0 for item in commands),
                name + ': no successful printf execution in Codex events; ' + allow_diagnostic)
        blocked = str(outputs.get('call_1', ''))
        if active:
            require('role refuses' in blocked, name + ': no hook refusal reached model: ' + blocked[:500])
            # Codex quotes the refused command in its feedback; execution events are
            # the independent witness that the printf itself never ran.
            require(not any(DENY in item.get('command', '') for item in commands),
                    name + ': denied printf executed')
            require(role + ' role refuses' in blocked,
                    name + ': wrong guard role: ' + blocked[:500])
        else:
            require(DENY in blocked, name + ': inactive hook branch did not execute harmless probe')
            # The guarded word is an ignored operand now, so the format alone is the output.
            require(any(item.get('aggregated_output') == DENY + '\n'
                        and item.get('exit_code') == 0 for item in commands),
                    name + ': inactive hook branch has no successful printf event')
        summary = {'case': name, 'status': 'pass', 'role': role,
                   'hook_source': 'scripts/hard_edges.py codex_hook_config',
                   'guard': 'denied' if active else 'inactive',
                   'requests': len(server.requests), 'seconds': round(time.monotonic() - started, 2)}
        if logs:
            (logs / (name + '.summary.json')).write_text(json.dumps(summary, indent=2) + '\n')
        return summary


def dispatch_reviewer(binary, logs):
    """Real dispatch, copy, CLI, sandbox, hook and cleanup; only model/GitHub are fixtures.

    A lane that has moved since the pin plus a write/fetch/network command catches accidental
    lane execution, shared Git metadata, a protected copy gitdir or a network-disabled sandbox.
    """
    case = runpy.run_path(str(ROOT / '.github/test-dispatch.py'))['DispatchTest']()
    case.setUp()
    record = None
    try:
        (case.project / 'evidence.txt').write_text('pinned evidence')
        case.git('add', '.'); case.git('commit', '-m', 'pinned evidence')
        pin = case.git('rev-parse', 'HEAD')
        branch, lane = case.hand_made_lane()
        case.call('--adopt', '--branch', branch, '--worktree', str(lane), '--base', 'origin/main')
        (lane / 'evidence.txt').write_text('later evidence')
        case.git('-C', str(lane), 'add', '.'); case.git('-C', str(lane), 'commit', '-m', 'later')
        refs = case.git('show-ref')
        with ResponsesFixture('gh api -X') as fixture:
            probe = ("from pathlib import Path; import urllib.request; "
                     "print(urllib.request.urlopen('http://127.0.0.1:"
                     + str(fixture.server.server_port) + "/history',timeout=5).read().decode()); "
                     "Path('evidence.txt').write_text('reviewer experiment'); "
                     "print('COPY_WRITE_478')")
            fixture.allowed_command = ('printf ' + shlex.quote(ALLOW + '\n')
                + ' && git rev-parse HEAD && git fetch --no-tags ' + shlex.quote(str(lane)) + ' ' + pin
                + ' && python3 -c ' + shlex.quote(probe))
            settings = fixture_settings(fixture.server.server_port)
            overrides = [arg for key, value in settings.items() for arg in ('-c', key + '=' + toml(value))]
            case.tool('codex', 'import json,os,sys\n'
                + "if sys.argv[1:3]==['mcp','list']: print('[]'); raise SystemExit(0)\n"
                + 'args=sys.argv[1:]; args[args.index("-m")+1]="devstandard-fixture"\n'
                + 'os.execv(' + repr(binary) + ',[' + repr(binary)
                + ',args[0],"--ignore-user-config","--ephemeral",*args[1:],*'
                + repr(overrides) + '])\n')
            case.env.pop('OPENAI_API_KEY', None)
            record = case.call('--purpose', 'reviewer', '--implementation', 'codex',
                               '--packet', str(case.review_packet(head=pin)), '--wait')
            require(record['executor_exit'] == 0, 'dispatched reviewer CLI failed: ' + Path(record['log']).read_text())
            require(not fixture.errors and len(fixture.requests) == 3, 'reviewer fixture protocol failed')
            actual = '\n'.join(text_fragments(fixture.requests[0].get('input', [])))
            brief = Path(record['brief']).read_text()
            require(actual.count(brief.strip()) == 1, 'complete reviewer brief did not arrive once')
            outputs = tool_results(fixture.requests[2])
            allowed = str(outputs.get('call_0', ''))
            require(pin in allowed and 'COPY_WRITE_478' in allowed and fixture.history_reads == 1
                    and 'NETWORK_HISTORY_READ_478' in allowed,
                    'reviewer could not read pin, fetch, write and reach network: ' + allowed[-2500:])
            require('reviewer role refuses' in str(outputs.get('call_1', '')), 'reviewer write-flag hook missing')
            require('never comments' in actual and 'never pushes' in actual, 'remote prohibition not delivered')
            require(case.git('-C', str(lane), 'status', '--porcelain', '-uall') == '', 'review dirtied lane')
            require(case.git('show-ref') == refs, 'review altered lane refs')
            require((lane / 'evidence.txt').read_text() == 'later evidence', 'review altered lane file')
            require(not Path(record['review_checkout']).parent.exists(), 'review copy survived completion')
            if logs:
                for key in ('brief', 'output', 'log', 'completion'):
                    shutil.copy2(record[key], logs / ('dispatch-reviewer.' + Path(record[key]).name))
                (logs / 'dispatch-reviewer.requests.json').write_text(json.dumps(fixture.requests, indent=2))
            return {'case': 'dispatch-reviewer', 'status': 'pass', 'pinned_head': pin,
                    'sandbox': 'workspace-write', 'network': 'HTTP history read',
                    'git_fetch': 'executed in independent metadata', 'copy_write': 'executed',
                    'lane_status': 'empty', 'copy_cleanup': 'removed', 'remote_rule': 'delivered',
                    'guard': 'reviewer gh api write flags denied'}
    finally:
        case.doCleanups()


def dispatched_worker_prompt(worktree):
    """The prompt `scripts/dispatch --implementation codex` hands `codex exec`.

    The dispatcher reads `reference/worker.md` unchanged — the page carries no template slot
    since #402 — then appends the marked worker-facing section of `reference/harness-codex.md`,
    because a Codex CLI worker has no carrier that survives a lost packet (ADR 0061). It writes the
    result as the lane's brief and hands it to `codex exec -` on stdin; `.github/test-dispatch.py`
    asserts the child's stdin carries it.
    This rebuilds the same shape so the real CLI can be asked what this test owes: do those exact
    bytes reach the model?
    """
    page = (ROOT / 'reference/worker.md').read_text()
    codex_page = (ROOT / 'reference/harness-codex.md').read_text()
    mechanics = codex_page.split('<!-- BEGIN CODEX WORKER MECHANICS -->\n', 1)[1] \
                          .split('<!-- END CODEX WORKER MECHANICS -->\n', 1)[0].strip('\n')
    require(mechanics, 'reference/harness-codex.md carries no worker-facing section')
    carried = page + '\n' + mechanics + '\n'
    packet = ('\n\n# Task packet\nIssue: https://github.com/o/r/issues/396\n'
              'Branch: task/396-runtime-fixture\nWorktree: ' + str(worktree) + '\n'
              'Named base: origin/main\nRole references resolve from: ' + str(ROOT) + '\n\n'
              'Run the two harmless local printf probes supplied by the fixture, then finish.\n')
    return carried, carried + packet


def text_fragments(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from text_fragments(item)
    elif isinstance(value, list):
        for item in value:
            yield from text_fragments(item)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log-dir', type=Path, help='Save concise Codex events and assertion summaries')
    parser.add_argument('--case', choices=['disabled', 'untrusted-before', 'worker',
                                         'untrusted-after', 'reviewer', 'worker-brief',
                                         'mcp-refused-without-the-setting', 'mcp-reviewer',
                                         'mcp-worker', 'mcp-worker-code-mode', 'dispatch-reviewer'])
    args = parser.parse_args()
    binary = shutil.which('codex')
    require(binary, 'Codex CLI is required; install the CI-pinned version before this test')
    version = subprocess.check_output([binary, '--version'], text=True).strip()
    match = re.fullmatch(r'codex-cli (\d+)\.(\d+)\.(\d+)', version)
    require(match and tuple(map(int, match.groups())) >= (0, 153, 4),
            'runtime fixture requires Codex CLI 0.153.4 or newer: ' + version)
    if args.log_dir:
        args.log_dir.mkdir(parents=True, exist_ok=True)
    # The trust cases run in this order on purpose: the guard is inactive with hooks disabled and
    # before any trusted invocation, active under the dispatcher's one-invocation bypass, and
    # inactive again afterwards — the bypass persists no trust.
    cases = [('disabled', {'role': 'worker', 'enabled': False}),
             ('untrusted-before', {'role': 'worker'}),
             ('worker', {'role': 'worker', 'trusted': True}),
             ('untrusted-after', {'role': 'worker'}),
             ('reviewer', {'role': 'reviewer', 'trusted': True})]
    with tempfile.TemporaryDirectory(prefix='devstandard-runtime-') as scratch:
        fixture = Path(scratch).resolve()
        isolation = inventory(fixture)
        subprocess.run(['git', 'init', '--quiet', str(fixture)], check=True, capture_output=True)
        results = [run_case(binary, fixture, name, logs=args.log_dir, **options)
                   for name, options in cases if args.case is None or args.case == name]
        # The standing dispatched path: `--implementation codex` passes the brief, which opens
        # with the resolved worker page and the Codex harness's worker section under it, as the
        # prompt. No startup hook runs in a dispatched child, so the prompt is the only carrier of
        # either and must be exact.
        if args.case is None or args.case == 'worker-brief':
            carried, prompt = dispatched_worker_prompt(fixture)
            results.append(run_case(binary, fixture, 'worker-brief', trusted=True, role='worker',
                                    prompt=prompt,
                                    carries=(('reference/worker.md',
                                              'reference/harness-codex.md'), carried),
                                    logs=args.log_dir))
    # Reviewer admission must compose with its writable copy sandbox (#478).
    mcp_cases = [('mcp-refused-without-the-setting', 'workspace-write', False, None),
                 ('mcp-reviewer', 'workspace-write', True, None),
                 ('mcp-worker', 'workspace-write', True, None),
                 # Code mode reaches an MCP tool through `exec`'s JavaScript rather than through
                 # the tool's own namespace, and a dispatched child on a default host runs in
                 # that arm, so it gets a case instead of being left to the host's default.
                 ('mcp-worker-code-mode', 'workspace-write', True, 'code-mode')]
    results += [run_mcp_case(binary, name, sandbox=sandbox, admit=admit, prefer=prefer,
                             logs=args.log_dir)
                for name, sandbox, admit, prefer in mcp_cases
                if args.case is None or args.case == name]
    if args.case is None or args.case == 'dispatch-reviewer':
        results.append(dispatch_reviewer(binary, args.log_dir))
    print(json.dumps({'codex': version, 'isolation': isolation, 'results': results,
                      'not_exercised': ['a remote PR lifecycle', 'production authentication']},
                     ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (AssertionError, OSError, subprocess.SubprocessError) as error:
        print(json.dumps({'status': 'fail', 'error': str(error)}))
        raise SystemExit(1)
