# Extended candidate validation — 23 September 2026

Maintainer: Ganador1. This candidate uses a new public branch without ancestors from the original development history. The original repository branches and private evidence are preserved separately; this does not erase information previously published elsewhere in the repository.

## Results

| Check | Result | Scope |
|---|---|---|
| Development suite excluding network-marked tests | 2,177 passed; 32 skipped; 9 deselected | Local Python 3.14; includes private research harnesses not all included in the public snapshot |
| Public-source regression | 233 passed | The complete selected test set included in the public candidate |
| Fresh-environment public regression | 233 passed | New virtual environment, freshly installed declared dependencies; no borrowed packages |
| Real HTTP middleware | Passed on both tested Atlas/Python environments | Headers, host rejection, size limit, allowed and rejected CORS requests |
| Installed runtime | Passed | Portable configuration loads outside checkout and requires Docker for generated code |
| Exact witness | Passed | C ≥ 0.40863826, with two corruptions rejected |
| Retained numerical calibration | Passed | 23 AR1 replays, 28 H2 checks, one retained failed request |
| Static correctness | Passed | AMY runtime syntax and undefined-name gate |
| Peer-review diagnostic | Completed in 30 seconds | Timeout handling only; no successful model review or scientific result is inferred |

Warnings concern unavailable PySCF OpenMP parallelism and Starlette's deprecated HTTPX adapter. Neither was silently suppressed in the retained logs. Optional integrations and platform-specific skipped tests are not certified by these counts.

## Corrections found by wider testing

- Starlette's MutableHeaders does not implement pop; response-header removal now uses membership and deletion. Real requests cover the previously crashing path.
- The middleware honors ATLAS_ALLOWED_HOSTS and ATLAS_CORS_ORIGINS while retaining fallback names.
- The public profile now requires Docker isolation for generated code. The operator's local configuration is separate.
- Older fixture objects created with __new__ lacked required receipt stores and operating-contract fields. Tests now initialize the real supporting objects and retain failed experiments as failures.
- A model-profile test still expected the retired three-agent configuration. It now checks the explicit portable release profile rather than the operator's mutable settings.
- Public-source selection now includes the receipt-memory calibration harness and broader regression coverage.

## Reproduction and Git boundary

Follow [REPRODUCING.md](REPRODUCING.md). The direct validation dependencies are pinned in scripts/release/requirements-validation.txt; this is not a complete transitive lock. Public CI repeats the selected tests and numerical verification on Linux. Local results do not imply that a remote CI run has passed; inspect the check attached to the exact public commit.

The public branch is codex/public-release-1.1.0rc1. Its initial commit uses only Ganador1 attribution and contains the curated source manifest. Creating it does not merge, rewrite, or anonymize main or any older branch. Raw research trajectories and credentials are excluded. Public derivatives cannot establish the entire historical search chronology or worldwide priority.

The final file-name hygiene gate excluded three legacy security snapshot JSON files from the export before any push. Both archive scanning and export selection now reject secret-snapshot names even if a content scan finds no known credential. Earlier local candidate packages are superseded and must not be uploaded.
