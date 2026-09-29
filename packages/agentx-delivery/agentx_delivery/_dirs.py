"""Filesystem interface for the agentx-delivery transport client: it needs exactly
a TASK_DIR (incoming tasks land here), a RESULT_DIR (results read + posted back),
and a STATE_DIR (inflight/rooms ledgers). No 'workspace' concept, no agentx deps.

Resolution (per dir): explicit env → injected resolver → default under
~/.agentx-delivery/. AgentX injects its own (workspace/tasks, /results, /state) via
set_dirs(); any other agent just sets the env vars (or takes the defaults)."""
import os
from pathlib import Path

_DEFAULT_BASE = Path.home() / ".agentx-delivery"
_injected = None  # dict(task/result/state -> Path) set by internal agentx


def set_dirs(task_dir=None, result_dir=None, state_dir=None):
    """Internal callers (agentx) inject concrete dirs; external uses env/defaults."""
    global _injected
    _injected = {
        "task": Path(task_dir) if task_dir else None,
        "result": Path(result_dir) if result_dir else None,
        "state": Path(state_dir) if state_dir else None,
    }


def _resolve(kind, env_var, default):
    if _injected and _injected.get(kind):
        return _injected[kind]
    v = os.environ.get(env_var)
    return Path(v) if v else default


def task_dir():
    return _resolve("task", "AGENT_CONNECT_TASK_DIR", _DEFAULT_BASE / "task_dir")


def result_dir():
    return _resolve("result", "AGENT_CONNECT_RESULT_DIR", _DEFAULT_BASE / "result_dir")


def state_dir():
    return _resolve("state", "AGENT_CONNECT_STATE_DIR", _DEFAULT_BASE / "state")
