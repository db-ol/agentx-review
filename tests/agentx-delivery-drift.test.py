#!/usr/bin/env python3
"""CI guard: every module the package bundles from src/ must stay in sync with it.

The bundled set is `MAP` in tools/sync_from_src.py — 14 modules today, including
outbox.py and outbox_adapter.py. Only what is NOT in MAP is package-canonical and
intentionally divergent (remote_gateway_bridge, _dirs, send_allowlist). This
docstring used to name three modules, which read as "outbox is not covered" long
after MAP had grown; the guard's actual scope is MAP, not this sentence.

This lives under tests/ so the repo's test discovery
(`find tests -name '*.test.py'`, package.json) actually runs it — the package's
own `tools/test_no_drift.py` was outside every discovery path (Codex #2082 P2).

Run: python3 tests/agentx-delivery-drift.test.py
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SYNC = REPO / "packages" / "agentx-delivery" / "tools" / "sync_from_src.py"


def test_agentx_delivery_bundled_utils_in_sync_with_src():
    assert SYNC.exists(), f"missing {SYNC}"
    r = subprocess.run([sys.executable, str(SYNC), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, (
        "agentx-delivery bundled utils drifted from src/. "
        "Run: python3 packages/agentx-delivery/tools/sync_from_src.py\n"
        + (r.stdout or "") + (r.stderr or "")
    )


if __name__ == "__main__":
    test_agentx_delivery_bundled_utils_in_sync_with_src()
    print("PASS — agentx-delivery bundled utils in sync with src/")
