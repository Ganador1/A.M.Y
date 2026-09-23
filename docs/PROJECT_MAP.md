# Repository map

## Maintained software

| Location | Purpose |
|---|---|
| `amy.py`, `core/` | Entry point, heartbeat, transport, receipts, execution evidence |
| `cognition/` | Decisions, reflection, goals, mathematical search orchestration |
| `memory/`, `skills/`, `senses/` | Persistent context, reusable tools, inputs |
| `communication/`, `evolution/` | Reporting and bounded adaptation |
| `sandbox/` | Generated-code execution and isolation |
| `atlas/app/` | Scientific laboratory and domain services |
| `tests/`, `benchmarks/` | Regression checks and explicit evaluation protocols |
| `scripts/run/`, `scripts/verify/` | Launchers and offline verification |

## Release and publication

| Location | Purpose |
|---|---|
| `docs/releases/` | Release notes and migration guidance |
| `docs/publication/` | Claim classification, attribution and publication decisions |
| `release_evidence/` | Small, explicitly selected evidence for reviewers |
| `scripts/release/` | Repeatable release validation |
| `CITATION.cff` | Software citation; no DOI until a real deposit exists |

## Research records

`experiments/` contains both harness source and historical runs. `output/` contains audits and generated artifacts. `data/` contains local runtime state. `zenodo_deposits/` contains old proposed deposit packages, not evidence that a deposit was published or approved. Do not upload these trees wholesale.

Original experiment paths and bytes remain in place because hashes and native receipts refer to them. New English publication notes summarize and link selected material; they do not retroactively rewrite recorded prompts, failed results or signed manifests.

The top-level English documentation is the maintained entry point. Legacy Atlas documentation, source comments, research planning notes and original experiment records may remain multilingual; they are not all translated or newly validated by this release. Their existence is not an endorsement of their historical claims.

## Release resources

- [English technical manuals](ENGLISH_MANUALS.md)
- [Reproduction guide](releases/REPRODUCING.md)
