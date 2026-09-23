# Results and reproducible examples

AMY combines software capabilities, empirical evaluations and mathematical certificates. These are different kinds of evidence. The examples below are included so a reader can inspect the inputs and run the checks.

## Exact minimum-autocorrelation witness

The supplied nonnegative rational step function proves **C ≥ 0.40863826** for the minimum-autocorrelation functional. Its exact ratio is

`25472093474917464906152750403804195198286625 / 62334087449348808708328853738083398757238922`.

The certificate uses 960 rational cells. The verifier checks 740 nodes/endpoints and 739 midpoints, and rejects an inflated declared ratio and an altered height. See the [mathematical note](research/AUTOCORRELATION.md) and [self-contained evidence](../release_evidence/autocorrelation/README.md).

The ratio exceeds the pinned Russell witness `2378625/5958277`. This is a comparison with that specific construction. Worldwide priority and global optimality are not established. The finite step-function reduction is known mathematics.

## Native model calibration

Twenty sessions across five cloud models tested two bounded tasks: AR1 early-warning benchmarks and H2 RHF/STO-3G calculations. Four successive protocol/software batches retained 51 successful measurements, 14 quantitative closures and six sessions without a passing closure. The failed batches are part of the evaluation.

The [numerical package](../release_evidence/runtime/README.md) replays 23 AR1 measurements, checks 28 H2 certificates and retains one failed request. H2 checking uses the supplied integrals; it does not independently regenerate them. The public numerical package does not contain all raw model conversations and does not independently reproduce aggregate session-closure counts.

These small, versioned calibration studies test tool use, memory, input contracts and session closure. They are not a broad ranking of models or proof of unrestricted autonomy. [Reproduction instructions](REPRODUCIBILITY.md) cover both offline checking and a fresh bounded campaign.

## Software improvements

Persistent receipts, mission-scoped memory, stricter response parsing, bounded recovery and validated session closure are implemented and covered by the public regression suite. The source includes the tests and direct validation dependency pins. Use the check attached to the exact Git commit when assessing CI results.

## Other research areas

SSH calculations and solver diagnostics, finite Singer/difference-basis exclusions, unit-distance graph constructions and replays of supplied formal fluid proofs were explored during development. These are reproductions, bounded negative results or engineering diagnostics. This release does not establish new global records in those areas or a solution to a Millennium Prize Problem. They are not bundled as new discoveries.

## Attribution

Ganador1 directed and reviewed the project. Codex assisted with implementation and repairs. Native AMY sessions selected requests inside operator-defined laboratories; deterministic optimizers and checkers performed the computations. The compact certificates establish the stated mathematical or numerical claims, not the full historical chronology of invention. See [evidence scope](EVIDENCE.md).
