#!/usr/bin/env bash
# Tests for scripts/lint-agentx-home-path.sh — the ~/.agentx/ install-path guard.
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"
LINT="scripts/lint-agentx-home-path.sh"
fail=0
ok()   { echo "ok   - $1"; }
bad()  { echo "FAIL - $1"; fail=1; }

# The pattern the lint uses (kept in sync with the script).
PATTERN='(\$HOME|~|/Users/[^/]+|/home/[^/]+)/\.agentx/|home\(\)[[:space:]]*/[[:space:]]*["'\'']\.agentx'

matches() { printf '%s\n' "$1" | grep -Eq "$PATTERN"; }

# 1. The current tree is clean in all-mode (every existing ~/.agentx use is a
#    resolver-owner / intentional fallback in the ALLOWED list).
if bash "$LINT" >/dev/null 2>&1; then ok "all-mode passes on the current tree"; else bad "all-mode passes on the current tree"; fi

# 2. The pattern CATCHES the real offending forms.
if matches 'WS="$HOME/.agentx/newthing"';           then ok "catches shell \$HOME/.agentx/ literal"; else bad "catches shell \$HOME/.agentx/ literal"; fi
if matches 'x=~/.agentx/repo/x';                      then ok "catches shell ~/.agentx/ literal";      else bad "catches shell ~/.agentx/ literal"; fi
if matches 'p = Path.home() / ".agentx" / "repo"';    then ok "catches python Path.home() / .agentx";  else bad "catches python Path.home() / .agentx"; fi
# ABSOLUTE home paths — the #2048 form the first cut missed (no $HOME/~ prefix).
if matches 'x = "/Users/maintainer-two/.agentx/repo/.env"';  then ok "catches absolute macOS /Users/*/.agentx"; else bad "catches absolute macOS /Users/*/.agentx"; fi
if matches 'D=/home/ubuntu/.agentx/repo/x';           then ok "catches absolute linux /home/*/.agentx"; else bad "catches absolute linux /home/*/.agentx"; fi
# TS/JS quoted literal (the scanner covers .ts/.tsx; the literal contains a matched substring).
if matches 'const repo = "~/.agentx/repo";';          then ok "catches TS quoted ~/.agentx literal";    else bad "catches TS quoted ~/.agentx literal"; fi

# 3. The pattern does NOT catch unrelated / bare mentions.
if matches 'd=~/.claude/skills';                       then bad "ignores a bare ~/.claude path";          else ok "ignores a bare ~/.claude path"; fi
if matches 'echo .agentx-memory-sync';                then bad "ignores .agentx-memory-sync dir name";  else ok "ignores .agentx-memory-sync dir name"; fi

# 4. The lint self-whitelists (its own file carries the literal in examples).
if grep -q 'lint-agentx-home-path\\.sh' "$LINT";      then ok "lint file itself is in the ALLOWED list"; else bad "lint file itself is in the ALLOWED list"; fi

if [[ "$fail" -eq 0 ]]; then echo "PASS"; else echo "SOME TESTS FAILED"; exit 1; fi
