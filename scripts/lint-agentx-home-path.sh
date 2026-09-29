#!/usr/bin/env bash
# AgentX lint: forbid NEW inline `~/.agentx/<...>` install-path literals.
#
# `~/.agentx/` is AgentX's per-user home for install/runtime state
# (`~/.agentx/repo` = the app-bundle clone, `~/.agentx/workspace` = the
# legacy workspace default, `~/.agentx/bin` = staged wrappers, etc.). New
# code MUST NOT hardcode a `~/.agentx/<segment>` path inline — it should
# resolve through the documented helper for whatever it needs:
#
#   • workspace     → scripts/agentx-config.sh workspace   (src/agentx_config.*)
#   • claude home   → scripts/agentx-config.sh claude-home-path
#   • other install → import the constant from the one file that owns it,
#                     don't re-hardcode the literal in a new call site.
#
# WHY (this is the part that stops recurrence, not the red X):
#   Hardcoded `~/.agentx/*` literals have bitten this repo more than once
#   (workspace default #762, later removed in #1440; app-bundle repo path
#   #1785). When the same install-path literal is copied into a new file,
#   a later move/rename/packaging change silently strands whichever copy
#   wasn't updated — an expensive, hard-to-see class of bug. Centralizing
#   the path behind a helper/constant means there's ONE place to change.
#
# Companion to `lint-workspace-resolution.sh` (which specifically guards the
# WORKSPACE resolver) and `lint-claude-home-path.sh` (the ~/.claude home).
# This one is the general `~/.agentx/*` install-home backstop.
#
# The lint flags only lines ADDED in the PR diff (--diff), so existing
# offenders stay un-flagged until deliberately migrated; new ones fail CI.
#
# Allowed files — the resolver/helpers, the one owner of each install
# location, migration/legacy scripts that must reference pre-M0 paths, and
# this lint + its tests:
#   scripts/agentx-config.sh · src/util_paths.py · src/workspace_default.{py,ts}
#   src/startup.sh · scripts/install-git-hooks.sh · scripts/install-session-start-hook.sh
#   src/agent/claude/cli/start-cli.sh · src/health-check.py
#   scripts/sync-memory.sh · scripts/sync-workspace.sh · scripts/agentx-migrate.sh
#   src/migration_safety_helpers.sh · scripts/lint-agentx-home-path.sh
#
# Usage:
#   bash scripts/lint-agentx-home-path.sh          # scan whole tree (show legacy debt)
#   bash scripts/lint-agentx-home-path.sh --diff   # scan only added lines vs BASE_REF (CI)

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

mode="${1:-all}"

# Match the inline install-path literal in shell + python + TS/JS:
#   shell/env : $HOME/.agentx/…   or   ~/.agentx/…   (also os.path.expanduser("~/.agentx/…"))
#   ABSOLUTE  : /Users/<name>/.agentx/…  or  /home/<name>/.agentx/…  — the form
#               that caused #2048 (an absolute home path, no $HOME/~ prefix). This
#               is the one the first cut MISSED; it's the whole point of the guard.
#   python    : Path.home() / ".agentx"   (home() followed by a ".agentx" string)
# Applies to any scanned language — a quoted TS/JS literal like "~/.agentx/x" or
# "/Users/x/.agentx/y" contains one of these substrings and is caught.
PATTERN='(\$HOME|~|/Users/[^/]+|/home/[^/]+)/\.agentx/|home\(\)[[:space:]]*/[[:space:]]*["'\'']\.agentx'

# Allowed files — may legitimately reference the install-home literal because
# they OWN the resolution/install-location, or are migration/legacy scripts
# that must name the pre-M0 paths they migrate from.
# NOTE on the "consumer" entries (report-feedback, telemetry, inline-tools):
# these are NOT resolver-owners — they carry a *deliberate* reference to the
# packaged-app install path (a cross-checkout token probe / a defensive
# fallback after resolve_workspace() / a doc comment). They're allowed because
# the reference is intentional and reviewed; a brand-new file copying the
# literal is what this lint is for.
# src/runtime-api/rundir.py OWNS the runtime run-dir resolution (daemon + CLI
# both import it); its ~/.agentx/run is the documented last-resort fallback
# in that one owner file — exactly the "one place to change" the lint wants.
ALLOWED='^(scripts/agentx-config\.sh|src/util_paths\.py|src/workspace_default\.(py|ts)|src/startup\.sh|scripts/install-git-hooks\.sh|scripts/install-session-start-hook\.sh|src/agent/claude/cli/start-cli\.sh|src/health-check\.py|scripts/sync-memory\.sh|scripts/sync-workspace\.sh|scripts/agentx-migrate\.sh|src/migrate\.sh|src/migration_safety_helpers\.sh|scripts/lint-workspace-resolution\.sh|scripts/lint-agentx-home-path\.sh|scripts/probe-team-sandbox\.sh|skills/report-feedback/report-feedback\.py|src/telemetry\.py|src/runtime-api/rundir\.py|src/inline-tools\.ts|tests/lint-agentx-home-path\.test\.sh|tests/runtime-rundir-resolver\.test\.sh|tests/credential-proxy-refresh\.test\.ts|tests/migration-safety-helpers\.test\.sh|tests/state-paths-adoption\.test\.py|tests/sync-memory-migration\.test\.sh|tests/sync-workspace\.test\.sh|tests/workspace-default\.test\.py|tests/runtime-api-rundir\.test\.py|packages/ag2-sparrow/.*\.py)$'

if [[ "$mode" == "--diff" ]]; then
  base="${BASE_REF:-origin/main}"
  files="$(git diff --name-only --diff-filter=AM "$base"...HEAD -- '*.py' '*.ts' '*.tsx' '*.sh' '*.bash')"
else
  files="$(git ls-files -- '*.py' '*.ts' '*.tsx' '*.sh' '*.bash')"
fi

if [[ -z "$files" ]]; then
  echo "lint-agentx-home-path: nothing to scan (mode=$mode)"
  exit 0
fi

found=0
while IFS= read -r f; do
  [[ -f "$f" ]] || continue
  if [[ "$f" =~ $ALLOWED ]]; then
    continue
  fi
  if [[ "$mode" == "--diff" ]]; then
    added="$(git diff "$base"...HEAD -- "$f" | awk '/^\+[^+]/ {print substr($0, 2)}')"
    matches="$(echo "$added" | grep -E "$PATTERN" || true)"
  else
    matches="$(grep -E "$PATTERN" "$f" || true)"
  fi
  if [[ -n "$matches" ]]; then
    found=1
    echo "lint-agentx-home-path: forbidden inline ~/.agentx/ literal in $f"
    while IFS= read -r line; do
      echo "  $line"
    done <<< "$matches"
  fi
done <<< "$files"

if [[ "$found" -eq 1 ]]; then
  cat >&2 <<'EOF'

ERROR: One or more files hardcode an inline `~/.agentx/<...>` install-path
literal. Copying this literal into a new call site is the class of bug that
stranded config across packaging changes before (#762 workspace, #1785 repo).

Fix: resolve through the helper / import the constant, don't re-hardcode:

  Workspace:
    Before:  WS="$HOME/.agentx/workspace"
    After:   WS="$(bash "$REPO_DIR/scripts/agentx-config.sh" workspace)"

  Claude home:
    Before:  D="$HOME/.agentx/repo/.claude"      # (illustrative)
    After:   D="$(bash "$REPO_DIR/scripts/agentx-config.sh" claude-home-path)"

  Other install paths (e.g. ~/.agentx/repo, ~/.agentx/bin): import the
  constant from the single file that already owns it rather than writing a
  fresh literal — so there's ONE place to change when packaging moves.

If your file legitimately OWNS an install location (a new resolver/installer),
add it to the ALLOWED list in scripts/lint-agentx-home-path.sh with a comment
explaining why. See that script's header for the full rationale.
EOF
  exit 1
fi

echo "lint-agentx-home-path: clean (mode=$mode, scanned $(wc -l <<< "$files" | tr -d ' ') files)"
exit 0
