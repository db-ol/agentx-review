# Anonymization notice

This review copy contains identity redactions and the explicit endpoint restrictions described below. Use it through the anonymous artifact link provided with the paper.

## Identity substitutions

This review copy derives from the product source revision used in the experiments. Product names, identifying contributor names, email addresses, personal host labels and selected account or message identifiers in documentation and regression fixtures have been replaced consistently. Product identifiers also occur in paths, environment variables and prompt strings, so this copy is not byte identical to the experimental source.

All original source modules, test files and installation manifests remain present. No replacement execution driver has been introduced. Permissions, policy rules and model choices have not been redesigned. No paper experiment archives or reported results have been rewritten by this source anonymization.

The recording indicator's product display name was replaced with a string of the same byte length and its local ad hoc signature was renewed. This is a display identity change, not a rewrite of executable instructions.

## Dependency provenance

The voice dependency retains its package name, version and locked Git commit. Its download locator now uses the dependency project's own upstream repository. The exact locked commit was fetched successfully from both the former source and the upstream source before this change. The dependency implementation and third party license notices have not been replaced or removed.

## Explicit endpoint restrictions

The following are redaction placeholders, not operational services.

| Placeholder | Purpose | Consequence |
| --- | --- | --- |
| `agentx-cloud.example.invalid` | Product cloud and Station gateway | Requires an authorized service configuration. The placeholder does not provide a cloud service. |
| `agentx-cloud-legacy.example.invalid` | Legacy cloud origin and redirect comparison | The host distinction is retained, but the placeholder is not reachable. |
| `agentx.example.invalid` | Product website | Display reference only. |
| `media.example.invalid/redacted-for-review` | Identifying demonstrations and community invitation | Original identifying destination is withheld. Generic third party media APIs are retained. |
| `REDACTED_OWNER/agentx` and related repository placeholders | Original source links, issue operations and repository maintenance | Do not execute these as working clone or maintenance targets. Download the review archive from the anonymous artifact page. Repository maintenance needs an explicitly configured authorized destination. |

Code implementing these integrations is retained. Their original public endpoints are not part of this candidate. Do not infer that the integrations work unchanged with the placeholder values. Never send credentials to a replacement service unless its operator and authorization are independently verified.

The corresponding host derived expected values in a regression test were updated to match the redacted origins. The production key derivation algorithm was not changed.

## Evidence and verification boundaries

The two documentation screenshots have opaque masks over identifying names, avatars and room identifiers. They are distributed as PNG files without ancillary metadata. Pixels outside the masks were checked against the decoded original images and are unchanged. The original screenshots and mask coordinates are retained privately for verification.

Both versions passed syntax checks for 1227 Python files. Of 86 selected test files, 84 passed in this review copy and 2 passed their executed checks with some tool dependent subchecks skipped. Tests requiring a local HTTP server were checked separately. These are selected regression checks, not the complete product test suite.

Private records retain the original source correspondence, per file differences, identity mappings and test logs. They are not included in the public review directory. No full application installation, live cloud integration test or paper experiment rerun is claimed for this candidate.

Necessary third party library names and license notices are retained. Anonymous review does not guarantee that public source code cannot be recognized by comparison with public repositories.
