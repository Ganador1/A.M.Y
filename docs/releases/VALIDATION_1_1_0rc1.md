# Local validation — 1.1.0rc1

Prepared on 20 September 2026. This records local checks, not a remote CI result or a signed release approval.

| Check | Result | Scope |
|---|---|---|
| Selected regression suite | 523 passed, 1 skipped | Parser, receipts, execution evidence, closure, tool contracts, release hygiene and safety gates |
| Skipped test | Live literature API test | Requires RUN_LIVE_LITERATURE=1; no live-network coverage claimed |
| Atlas subprocess and tool subset | 116 passed in an earlier overlapping subset | Includes a separate-laboratory-root process test; do not add this count to 523 |
| Autocorrelation witness | Exact ratio verified; two corruptions rejected | 960 cells, 740 nodes, 739 midpoint checks, continuous-shift proof argument |
| Release metadata | Versions aligned, local links and witness hashes checked | No fictional DOI or published-release date |
| Distribution | Wheel and source archive constructed | AMY runtime; separate Atlas installation required |
| Installed-runtime smoke | Imports 1.1.0rc1 and displays CLI help outside checkout | Uses local installed dependencies, not a clean cross-platform installation |

Three warnings concern unavailable PySCF OpenMP support. These do not make the numerical audit fail; this machine did not test OpenMP parallelism.

## Failures retained and corrected

An old science-gate fixture constructed Heartbeat without its receipt store and expected failed experiments to disappear from episodic memory. The fixture now initializes the store and checks that failure is retained as failure without updating the world model. Production evidence gates were not weakened.

The standalone Atlas check still expected nine QFT gates for three qubits. Under its documented abstract-gate convention the count is three Hadamard gates, three controlled-phase gates and one reversal SWAP, totaling seven. The check now verifies the components as well as the total. It is an analytic structural check, not a live quantum-circuit experiment.

An installed runtime could select an external Atlas directory while the worker assumed an adjacent directory. The parent now passes its resolved root and the worker honors it. A real subprocess test against a temporary separate laboratory covers this path.

## Outstanding gates

The working tree contains substantial pre-existing changes and untracked research source. Review and commit the intended source set before tagging; the preparation task does not certify every legacy file. Run remote CI from that exact revision. No GitHub release, tag, external attestation, research submission or DOI deposit was created.

The primary release documentation is English. 205 historical Atlas manuals now have English derivatives; original research records retain their language; see [language status](TRANSLATION_STATUS.md). Do not describe this candidate as a complete repository-wide translation.

Detailed build logs, failing and passing test logs, package hashes and language inventory are retained locally under output/release-prep-20260920/.

## Privacy and numerical replay update — 23 September 2026

The public source snapshot excludes Git history and private trajectories. Maintainer attribution uses Ganador1. Privacy substitutions create explicit derivatives; their hashes do not authenticate the original chronology. See [reproduction guide](REPRODUCING.md) and [translation status](TRANSLATION_STATUS.md). The runtime evidence now includes 23 deterministic AR(1) replays, 28 H2 certificate checks and one retained failed request.

The 23 September focused working-tree regression passed 40 tests (three PySCF OpenMP warnings). Public-copy tests initially exposed two omitted auxiliary files (the release-hygiene workflow and Kubernetes secret example); these were added to the export selection. Numerical checks also passed from the public copy. Final archive-level results are recorded in PUBLIC_VALIDATION.json in the distribution directory.

## Legacy Atlas source repairs

A full syntax scan found 18 pre-existing malformed modules: imports inserted into multiline imports, damaged settings lookups, misplaced exception colons, a missing try block, and a corrupted middleware setup. These were repaired. Middleware registration and invalid configuration rejection have focused tests. Syntax validity does not establish runtime correctness of all optional Atlas services. The full ASGI application and optional telemetry/ML integrations remain outside this release smoke test. Archive owner metadata is cleared to avoid exposing the build account.
