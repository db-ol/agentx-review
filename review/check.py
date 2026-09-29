"""Run selected local checks without starting a product or calling a model."""

import ast
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
TESTS = [
    'discord-bridge-access-tier.test.py',
    'discord-bridge-allowlist.test.py',
    'discord-bridge-collaborator-tier.test.py',
    'discord-bridge-sandbox-runtime-gemini.test.py',
    'discord-bridge-sandbox-fallback-sentinel.test.py',
    'discord-bridge-sandbox-prompt-path.test.py',
    'discord-bridge-access-no-clobber.test.py',
    'discord-read-redaction.test.py',
    'discord-read-reply-context.test.py',
    'discord_config.test.py',
    'discord-bridge-codex-subprocess-argv.test.py',
    'secret-scanner.test.py',
]


def main():
    import discord

    parsed = 0
    syntax_errors = []
    for path in sorted(ROOT.rglob('*.py')):
        if any(part in {'.venv', '__pycache__', 'out'} for part in path.relative_to(ROOT).parts):
            continue
        try:
            ast.parse(path.read_text(), filename=str(path.relative_to(ROOT)))
            parsed += 1
        except SyntaxError as exc:
            syntax_errors.append({'file': str(path.relative_to(ROOT)), 'line': exc.lineno})
    results = []
    with tempfile.TemporaryDirectory(prefix='agentx-review-check-') as temp:
        env = dict(os.environ)
        env['CLAUDE_CONFIG_DIR'] = str(Path(temp) / 'config')
        env['DISCORD_BOT_TOKEN'] = 'local-test-token'
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        for name in TESTS:
            path = ROOT / 'tests' / name
            if not path.is_file():
                results.append({'test': name, 'status': 'missing'})
                continue
            try:
                proc = subprocess.run([sys.executable, str(path)], cwd=ROOT, env=env,
                                      capture_output=True, text=True, timeout=60)
                skipped = 'SKIP' in proc.stdout or 'SKIP' in proc.stderr
                status = 'pass' if proc.returncode == 0 and not skipped else 'skip' if proc.returncode == 0 else 'fail'
                results.append({'test': name, 'status': status, 'exit_code': proc.returncode})
                if status != 'pass':
                    print(proc.stdout[-2500:] + proc.stderr[-2500:], file=sys.stderr)
            except subprocess.TimeoutExpired:
                results.append({'test': name, 'status': 'timeout'})
    print(json.dumps({'python': sys.version.split()[0], 'discord_py': discord.__version__,
                      'parsed_python_files': parsed, 'syntax_errors': syntax_errors,
                      'tests': results}, indent=2))
    return int(bool(syntax_errors) or any(r['status'] != 'pass' for r in results))


if __name__ == '__main__':
    raise SystemExit(main())
