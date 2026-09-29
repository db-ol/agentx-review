# Review scope and transformations

## Relationship to the study

The source revision matches the product version recorded for the baseline,
all team, and all other settings in the main study. The original source and
experiment archives remain unchanged. The product source is distinct from
the PAPriv enrollment and the archived experiment responses.

Anonymization changes product names, environment variable prefixes, module and
file names, hostnames, participant identifiers in fixtures, and identifying
links. Required third party model and library names remain. A source syntax
repair was necessary after redacting a video URL embedded in a formatted string.
No change was intended to the admission or tier policy.
Two ambiguous token literals in test fixtures were replaced with explicitly
synthetic values. This does not replace or alter experiment responses.

The renamed prompts are not byte identical to those used in the original model
calls. Local tests do not establish that hosted models will respond identically
after these transformations. Published counts must be recomputed from the
archived responses in the PAPriv artifact, not inferred from this source copy.

## Included and omitted material

Included source covers the chat bridge, policy modules, state and delivery
helpers, sandbox invocation helpers, and tests. Other source and reference
instructions are retained to make dependencies inspectable.

The original root README, development history, contribution and review process
documents, CI configuration, hooks for Git operations, and personal override
example are not included. Runtime `AGENTS.md` and `CLAUDE.md` are retained with
identity substitutions because they can influence the core's context.

The root Node manifests and lockfile are omitted because the optional voice
installation depends on a repository that identifies an author. The remaining
voice and desktop source is for inspection only. Neither that application nor
its dependency installation is validated by the review checks.

Two runtime screenshots, two package logos, and a compiled recording indicator
are omitted. The associated multimedia and recording paths are outside the
validated chat surface. References to omitted material in historical or runtime
documentation do not imply that it is included or supported here.

No personal workspace, login file, experiment archive, or Git history is part
of this snapshot. Synthetic credentials already present in test fixtures are
not operational credentials. Do not supply personal account credentials to
unreviewed auxiliary scripts.

## Validation boundaries

`review/check.py` runs selected tests for tiers, collaborator dispatch, file
send authorization, sandbox rulebooks, fallback handling, access persistence,
configuration, and history reading. It also parses all included Python files.

`review/check_papriv.py` checks the local configuration contract between the
two review artifacts. It validates three access maps, each admitting twelve
participants, with tier counts of 1/7/4, 1/11/0, and 1/0/11 for owner/team/other.
It uses the product's actual access loaders and rulebook selector.

These checks do not validate a live transport round trip, the full upstream
test suite, isolation against every information path, or new hosted model
responses. They do not turn an anonymized snapshot into a complete application
release or guarantee that its origin cannot be inferred from public source.

## Review integrity

`RELEASE-MANIFEST.json` covers the distributed files. `review/verify.py` checks
their sizes and SHA256 hashes and rejects unexpected source files. Generated
caches, dedicated virtual environments, and the local runtime workspace are
excluded from this inventory. Do not distribute those directories.
