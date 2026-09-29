"""Verify distributed files against the release manifest."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {'.git', '.venv', '__pycache__', '.pytest_cache', 'workspace', 'out', 'node_modules'}


def inventory():
    result = {}
    for path in sorted(ROOT.rglob('*')):
        name = path.relative_to(ROOT)
        if any(part in IGNORED for part in name.parts) or str(name) == 'RELEASE-MANIFEST.json':
            continue
        if path.is_symlink():
            raise ValueError(f'Unexpected symlink: {name}')
        if not path.is_file():
            continue
        raw = path.read_bytes()
        result[str(name)] = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
    return result


if __name__ == '__main__':
    expected = json.loads((ROOT / 'RELEASE-MANIFEST.json').read_text())['files']
    actual = inventory()
    if actual != expected:
        mismatches = sorted(k for k in expected.keys() | actual.keys() if expected.get(k) != actual.get(k))
        raise SystemExit('Manifest mismatch: ' + ', '.join(mismatches))
    print(f'PASS: {len(actual)} distributed files verified')
