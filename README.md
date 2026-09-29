# AgentX review snapshot

This artifact contains an anonymized source snapshot for the AgentX deployment
evaluated in PAPriv. It is based on the recorded experiment revision, not a
current upstream release. The private provenance record maps the original
revision and each transformed file to this review copy.

## Scope

The validated surface is the Python chat bridge and its local admission,
permission tier, configuration, and response handling helpers. Additional source
is retained for inspection. This is not a complete desktop or voice application
distribution. Do not run `start.sh` or general installation scripts to reproduce
the paper.

Development history, CI metadata, promotional material, selected binary assets,
and the root Node installation manifests are omitted. The voice dependency that
identified an author repository is not distributed here. Placeholder URLs under
`example.invalid` are not download locations or operational service endpoints.
See `REVIEW-SCOPE.md` before attempting execution.

## Local checks

Use Python 3.13. The following commands do not call hosted models or start chat
clients. Install dependencies in a dedicated environment.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-review.txt
.venv/bin/python review/verify.py
.venv/bin/python review/check.py
```

The check script runs selected upstream tests and parses the included Python
source. It reports skipped and missing checks separately from passed checks.
The final preparation checks passed in a newly created environment installed
from `requirements-review.txt`. See `VALIDATION.md` for the scope and results.

## PAPriv integration

Obtain the separate PAPriv review artifact and install its dependencies.
Using that environment's Python interpreter, run:

```sh
python review/check_papriv.py --papriv /absolute/path/to/papriv
```

This test gives the product bridge PAPriv's actual generated access files for
all three tier conditions. It checks admission, tier lookup, and rulebook
selection. It does not send a gateway message or ask a model to answer.

For a future live experiment, `AGENTX_REPO` must name a disposable copy of this
snapshot, not a personal installation. PAPriv supplies its recorded enrollment
launcher and core invocation driver. Preserve the experimental configuration
and reset protocol when using those components. No live experiment was rerun
while preparing these artifacts.

## License

The copyright holder name in `LICENSE` is anonymized for review with permission
communicated by the submitting author. The MIT permission and warranty text is
unchanged. Model and library identifiers needed to understand or run the code
remain technical identifiers, not statements of authorship.
