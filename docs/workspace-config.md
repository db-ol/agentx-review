# Workspace configuration

AgentX keeps **per-user runtime state** (tasks, results, notes, state, logs, etc.) under `<repo>/workspace/`, separate from the tracked code in the rest of the repo. This doc covers how the workspace path is resolved and how to override it.

## The default

```
<repo>/workspace/
```

That's it for a fresh clone — no setup, no env var, no config file. The directory is gitignored except for `.gitkeep`, so user data never sneaks into commits.

## Resolution order (highest wins)

1. **`agentx.config.local.json`** → `workspace.path` — per-clone override. Gitignored.
2. **`agentx.config.json`** → `workspace.path` — tracked default. The repo ships `${REPO_DIR}/workspace`.
3. **Baked-in fallback** — `${REPO_DIR}/workspace`, used if neither config file exists.

**Note:** `$AGENTX_WORKSPACE` is **no longer honored** by the resolver as of PR #1440 (workspace contract v0.3.0). If set, startup emits a one-time stderr deprecation warning + invokes auto-migration via `src/startup.sh`. Migrate to `agentx.config.local.json` to silence the warning.

`${REPO_DIR}` in any config string expands to the directory containing the config file (== git toplevel for a sane checkout).

## The two config files

**`agentx.config.json`** — tracked, shared across all clones. Defines the contract + defaults:

```json
{
  "core": { "runtime": "claude" },
  "workspace": {
    "path": "${REPO_DIR}/workspace"
  },
  "vault": { ... }
}
```

**`agentx.config.local.json`** — gitignored, per-clone overrides. Optional — empty file or missing file both mean "use defaults":

```json
{
  "workspace": {
    "path": "/Volumes/MyExternalSSD/agentx-workspace"
  }
}
```

A sample is shipped as `agentx.config.local.json.example`. Copy + edit, or start from scratch — the loader tolerates any subset of fields.

Keys whose name starts with `_` (e.g. `_comment`) are stripped before validation, so the `.example` file can carry inline documentation without affecting runtime.

## Three common overrides

```json
// 1. Use Codex CLI as the persistent core
{ "core": { "runtime": "codex" } }

// 2. Move workspace outside the repo (e.g. shared between clones)
{ "workspace": { "path": "/Users/you/.agentx/workspace" } }

// 3. Enable vault sync to a private remote
{ "vault": { "enabled": true, "remote_url": "https://vault.example.com/you/workspace.git" } }

// 3b. Pin a host that intentionally runs off a non-main branch (e.g. the
//     dual-run pinned nodes). health-check's live-checkout-branch probe warns
//     when the live checkout drifts off this branch; default is "main".
//     Config (not env) is the durable home — launchd/AgentX.app callers
//     never inherit an interactive shell's exports. AGENTX_EXPECTED_BRANCH
//     remains a per-invocation env override (wins over config).
{ "core": { "expected_branch": "v0.4.0-pre-workspace-revamp" } }

// 3c. Tune when a checkout on the RIGHT branch is nonetheless too stale.
//     Being on `main` is only half of being current — a checkout can sit on
//     main and still execute weeks-old code, which is how merged guards end up
//     not running with nothing to report it. Default 10; deliberately not 1,
//     because main moves several times a day and a probe that fires on every
//     ordinary delta is one the reader learns to skip. Invalid values
//     (non-integer, zero, negative) fall back to 10 rather than crashing the
//     health check or warning on an up-to-date checkout. No env-var override —
//     config is the only home.
{ "core": { "checkout_behind_warn": 25 } }

// 4. Multiple overrides
{
  "workspace": { "path": "/Users/you/.agentx/workspace" },
  "vault": { "enabled": true, "remote_url": "https://vault.example.com/you/workspace.git" }
}
```

## Use the loader, never reinvent the fallback

| Language | API |
|---|---|
| Python | `from agentx_config import resolve_workspace, resolve_vault, resolve_core_runtime, load_config` |
| TypeScript | `import { resolveWorkspace, resolveVault, resolveCoreRuntime, loadConfig } from './agentx_config.js'` |
| Swift | `AgentXConfig.resolveWorkspace()` / `AgentXConfig.loadConfig()` |
| Bash | `WORKSPACE="$(bash scripts/agentx-config.sh workspace)"`; runtime via `core-runtime` |

`src/workspace_default.{py,ts}` (the legacy resolver) now delegates to the loader transparently — existing callers don't need code changes.

## Protection layers

The workspace must never end up in commits. Three layers enforce this:

1. **`.gitignore`** — `workspace/*` with a `!workspace/.gitkeep` exception. Prevents `git add .` from picking up runtime files.
2. **Local pre-commit hook** — `.githooks/pre-commit` refuses any commit whose staged files include `workspace/`-prefixed paths (except `.gitkeep`). Auto-installed by `src/startup.sh`; one-time manual install via `bash scripts/install-git-hooks.sh`.
3. **CI workspace-leak check** — `.github/workflows/workspace-leak-check.yml` mirrors the hook on every PR + push to main. Catches anyone who bypassed the local hook.

Escape hatch for the rare legitimate case (updating `.gitkeep` itself): `git commit --no-verify`.

## CI lint: forbid new direct resolution

`.github/workflows/lint-workspace-resolution.yml` refuses PRs that introduce new code outside the loader reading `$AGENTX_WORKSPACE` directly, hardcoding `~/.agentx/workspace`, or using the historic `Path(__file__).resolve().parent.parent` walk-up. Existing legacy offenders are not flagged (the CI uses `--diff` mode); they're migrated separately.

## Migrating from the old default

Older installs used `~/.agentx/workspace/` as the default. If you have one:

- **Path-only override:** add `{"workspace":{"path":"/Users/you/.agentx/workspace"}}` to `agentx.config.local.json`. Done.
- **Move into the in-repo default:** copy your old workspace contents into `<repo>/workspace/`. The loader will emit a `.env` drift warning if your `.env` still declares `AGENTX_WORKSPACE=` — remove that line once you've migrated.

The M1 milestone will ship a dedicated recovery skill (`bash scripts/agentx-migrate.sh`) for users who want a guided audit + move.

## Related

- `CLAUDE.md` § Workspace contract — the project-wide contract this doc operationalizes
- `docs/agentx-config.schema.json` — JSON Schema for the config file (editor autocomplete + validation)
- `agentx.config.local.json.example` — annotated override sample at the repo root


## Deprecated `$AGENTX_WORKSPACE`, and the repo-root fallback anti-pattern

Relocated from `CLAUDE.md` to keep the always-loaded file under its 40 KiB budget; the operative
rule stays there, the history lives here.

`$AGENTX_WORKSPACE` is no longer honored for workspace resolution as of v0.8 / #1440. If it is set
it is still *detected*, to fire a one-time deprecation warning and trigger one-time auto-migration
via per-source sentinels (PR #1478) — but the resolver ignores its value.

**Historic anti-pattern:** bridges fell back to the script's repo root via
`Path(__file__).resolve().parent.parent`. That polluted `git status`, and when invoked from an
app-bundled `src/` symlink it stranded owner DMs in a `bundle-tasks/` directory while the watcher
polled `workspace-tasks/`. Use the helpers listed in `CLAUDE.md` instead of reinventing the fallback.
