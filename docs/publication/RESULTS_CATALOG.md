# Results catalog

Editorial review for the 1.1.0rc1 candidate, 20 September 2026. “Publishable” here means an appropriate format and claim scope have been identified; it does not mean external peer review or worldwide priority has been established.

| Item | Defensible result | Publication decision | Remaining work |
|---|---|---|---|
| Minimum autocorrelation, C6.6 | Exact witness gives C ≥ 0.40863826; stronger than the pinned Russell witness | Priority mathematical note and reproducibility package | External mathematical review, broader priority search, complete search-lineage deposit |
| Receipt memory, failure recovery, parser and typed closure | Implemented changes with regression tests and native calibration evidence | Software release and engineering evaluation | Longer runs, unseen tasks, more independent replications |
| Multimodel calibration | 20 sessions, 51 checked measurements; failures retained across four versions | Bounded evaluation report | Controlled replicates before ranking models |
| H₂ RHF/STO-3G | Numerical consistency at specified geometries, corrupted-energy controls rejected | Verification example | Independent integral engine for stronger independence claims |
| SSH solver behavior / certificates | Numerical diagnostics and finite spectral checks | Reproduction or methods appendix | Prior-art comparison; no new physical-mechanism claim |
| Singer / difference-basis obstructions | Negative results inside specified finite search families | Optional negative-results dataset | Exact scope, checker and relation to prior MILP exclusions |
| Unit-distance graphs | Local constructions and comparisons to supplied incumbents | Benchmark or search dataset | No new global record demonstrated in this release |
| Lean fluid proofs | Reproduction/checking of supplied formal developments | Reproducibility appendix | Resolve incomplete replay paths; preserve upstream credit; no AMY Millennium solution claim |
| Chang manuscript algebra | Historical diagnostic affected by later author revisions | Historical audit only | Do not advertise as a current new correction |
| Jacobian and power-modulus work | Reproductions or classical mathematics | Educational/validation examples | No novelty claim |

## Autocorrelation claim

For nonnegative integrable functions, define

`C = sup_f min_{0≤t≤1} ∫ f(x)f(x+t) dx / (∫ f(x) dx)²`.

The selected witness proves the exact lower bound

`25472093474917464906152750403804195198286625 / 62334087449348808708328853738083398757238922`.

Its decimal is approximately 0.40863826707362133. The public headline **C ≥ 0.40863826** rounds down. It improves the pinned Russell value `2378625/5958277`; this is a comparison with a specific witness, not a guaranteed current world record. Verification instructions and the mathematical argument are in [the evidence package](../../release_evidence/autocorrelation/README.md).

On 20 September, the [Russell repository](https://github.com/techno-optimist/minimum-autocorrelation-bound) still displayed its 0.39921356… witness. The primary problem is [Barnard–Steinerberger, arXiv:1903.08731](https://arxiv.org/abs/1903.08731). This bounded source check does not establish exhaustive priority. Preserve credit to Russell's construction and the known step-function reduction.

## Attribution

Human direction and review: Ganador1. Implementation and repair assistance: Codex. Native AMY selected requests within operator-defined laboratories; deterministic optimizers and checkers performed the mathematical computation. The compact witness package proves existence, not the full chronology of invention. No model is credited with independently inventing the supplied algorithms.

## Historical packages

The existing `zenodo_deposits/` tree contains older proposed bundles, including a weaker autocorrelation value. Do not upload those archives as the current release or treat their filenames as proof of publication. Original archives remain intact; this catalog supersedes their editorial classification without rewriting their contents.
