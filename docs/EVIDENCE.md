# What the provenance establishes

| Layer | Available evidence | What it does not establish |
|---|---|---|
| Recorded bytes | SHA-256 artifacts and chained events | Authenticity against an attacker who can rewrite all roots |
| Execution context | Retained configuration, source identities, inputs and outputs | Coverage of uninstrumented code or provider internals |
| Agent attribution | Native decision, action and receipt events | Invention of operator-supplied algorithms |
| Numerical consistency | H₂ and other scoped numerical checks | Exact physical truth or independent integral generation |
| Exact certificates | Rational or finite mathematical recomputation | Global optimality, novelty or priority |
| Build attestation | Workflow integration exists | A signed attestation for every distributed artifact |
| Trusted timestamps / signatures | Infrastructure and verifier code exist | A complete externally authenticated chain for every historical run |

The latest calibration audit checked 20 execution chains and 18 existing experiment journals. Two sessions performed no experiments and had no journal. Frozen files were unchanged within each campaign. These checks do not retroactively certify all historical AMY runs.

## Reproducing a result

Start with [reproducibility instructions](REPRODUCIBILITY.md). A mathematical witness includes its exact claim, input, verifier and deliberate corruptions. The calibration package includes retained requests, numerical results, certificates and a replay script. Each package has a manifest of its public bytes.

The full raw model conversation and historical search chronology are not included in these compact packages. Checks on the supplied numbers do not establish the model's identity or that it invented an operator-supplied algorithm. The [results overview](RESULTS.md) states which conclusions the available evidence supports.

Translations and redacted public derivatives have separate hashes. Original source hashes are retained as references, but a public derivative is not byte-identical to its original. The public software source manifest identifies the shipped files. CI checks the software and evidence at a particular commit; a passing test or an ordinary SHA-256 manifest is not a provider signature, trusted timestamp or universal proof of correctness.
