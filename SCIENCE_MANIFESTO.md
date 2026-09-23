# A.M.Y Science Principles

These are standards for reviewing AMY results, not guarantees that every historical run met them.

## Separate kinds of evidence

1. A successful process means code ran; it does not prove its output is useful or correct.
2. Hash verification checks retained bytes and record links; it does not prove scientific truth.
3. A numerical audit checks a specified computation within tolerances and assumptions.
4. An exact certificate proves its encoded finite mathematical claim, subject to the checker and proof argument.
5. A novelty claim additionally requires prior-art review, correct attribution, and external scrutiny.

## Make claims falsifiable

State the hypothesis, admissible inputs, controls, stopping rule, uncertainty, and acceptance criterion before a confirmatory experiment. Keep failed attempts and negative results. Label adaptive search as exploratory; repeated trajectories and reused seeds are not independent replications.

## Retain and inspect evidence

Record tool requests, complete returned outputs, source/configuration identities, seeds, model identities as reported, and relevant environment details. Bind reported values to actual experiment IDs. Distinguish facts retrieved from memory from newly measured evidence. Store translations and corrections as new artifacts when changing a historical record would invalidate its hashes.

The implementation supports these practices unevenly across old and new workflows. Inspect the actual run and verifier rather than assuming universal coverage. See [provenance scope](docs/EVIDENCE.md).

## Attribute the work

Separate the human research direction, assistant-written algorithms and repairs, native agent decisions, numerical solvers, mathematical arguments, and independent checking. Give upstream constructions and papers credit. A model choosing parameters for a supplied algorithm did not invent that algorithm.

## Publish proportionately

Publish exact claims at the precision proved. Use downward rounding for displayed lower bounds. Report scope restrictions, shared dependencies between verifiers, and unresolved counterexamples. Internal reflection, Elo rankings, and manuscript rubrics are development tools, not peer review or guarantees against hallucination.

The [results catalog](docs/RESULTS.md) is the current editorial classification. Historical reports can contain stronger claims that this review does not endorse.

## Responsible research

Follow the [use policy](USE_POLICY.md) and retain sandbox and tool guardrails. See [LICENSE](LICENSE) for the software license and [SECURITY.md](SECURITY.md) for reporting. Domain-specific safety, ethical, and experimental review remain the responsibility of the people conducting and publishing research.
