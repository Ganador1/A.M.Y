# A.M.Y. Mathematical Discovery Runtime

This package is the auditable state layer for Mathematical Discovery Mode. It does
not decide whether a theorem is true; it records what was proposed, which gates were
passed, and the exact artifacts used as evidence.

## Implemented guarantees

- Every `OllamaCloudClient` in one AMY process shares a transport gate capped at the
  configured `llm.max_concurrency` (three by default).
- `ModelBroker` adds a priority queue and three schedulable workers above that hard
  gate.
- Campaign directories are assembled in a temporary sibling and atomically renamed
  into place.
- `ledger.jsonl` and `events.jsonl` are append-only SHA-256 chains with monotonic
  sequence numbers.
- Problem and protocol bytes are committed by the campaign manifest.
- Prompts, raw/normalized responses, stdin, stdout and stderr are retained as
  content-addressed artifacts.
- Claims cannot skip gates, promote themselves, or return from a terminal state.
- The dependency scheduler runs at most three jobs, dynamically fills free slots,
  retries bounded failures, cancels blocked descendants and reconstructs state from
  the event chain after a restart.
- Blind roles (`explorer` and `independent_rederiver`) receive no prior artifacts;
  synthesis and review roles receive only explicitly authorized dependency outputs.
- Mathematical verdicts and scheduler authority are separate: any role may report a
  refutation, but only roles with `may_refute_branch` can cancel a branch.
- Discovery jobs default to DeepSeek V4 Flash's 1,000,000-token context window and
  a 16,384-token generation budget. Retries preserve temperature and thinking mode;
  they never trade reasoning quality for easier JSON recovery.
- Formal verification requires an explicit method (`lean`, `z3`, or
  `exact_computation`) and evidence hashes.
- Exact finite enumeration, Z3 UNSAT checks and Lean compilation share explicit
  `PROVEN`/`DISPROVEN`/`UNKNOWN`/`ERROR` results and retain the actual executed input.
- A `DISPROVEN` gate decision requires a retained counterexample. Bare tool labels
  cannot terminate a claim, and corroborating counterexample artifacts are combined.
- Generated Python runs in fail-closed Docker isolation. Lean also defaults to a
  no-network, read-only container and refuses host execution unless explicitly opted in.
- Chain, manifest and artifact verification fail closed after modification,
  deletion, reordering or partial writes.

## Deliberate limitations

- The concurrency ceiling is process-wide, not machine-wide. Running two independent
  AMY OS processes could make six calls; production discovery campaigns must use one
  coordinator process.
- SHA-256 detects changed retained bytes. It does not authenticate who created them,
  prevent rollback to an older complete campaign, establish novelty, or prove a
  mathematical statement.
- `truth_verified` is never inferred by the provenance verifier. It appears on a
  claim only after the formal-verification transition and remains scoped to the exact
  formal statement and toolchain artifact.
- Role isolation is enforced at prompt construction, not by an OS sandbox. The
  discovery worker does not yet autonomously schedule the mathematical tool adapters;
  the current campaign coordinator invokes them as explicit gate jobs.

## Real calibration matrix

The first paired calibration uses nearby statements to test both directions:

- `n^5 ≡ n (mod 60)` is deliberately false and must terminate as `refuted` with
  smallest counterexample `n = 2`.
- `n^5 ≡ n (mod 30)` is true and must survive independent derivation, exact residue
  enumeration, Z3, adversarial review and a universal Lean proof.

Matrix v2 adds an undefined symbol that must remain inconclusive, a real-domain
counterexample that defeats integer intuition, and a real one-millisecond Z3 timeout
that must remain `UNKNOWN`. The machine-readable auditor is
`scripts/run/audit_math_matrix.py`.

Retained reports:

- `output/math-discovery-real-pilots-2026-08-12.md`
- `output/math-discovery-matrix-v2-2026-08-12.md`
- `output/math-discovery-matrix-v2-results.json`

## Long unattended search

`scripts/run/run_overnight_math_search.py` runs a checkpoint after every six-job
round, reconstructs interrupted scheduler state, retries transient provider failures
with bounded exponential waits, and pauses before new rounds when resource thresholds
are unsafe. Its process lock prevents two coordinators from writing the same campaign.

The first long campaign studies the greatest universal modulus of `n^k - n`. It uses
five fresh roles plus synthesis per round, with blind explorer/rederiver roles kept
separate from exact observations and prior outputs. Generated proof text is retained
but never executed unattended. Final claims can advance only to computational support;
formal truth and expert review remain separate gates.

## Adaptive candidate frontier

`scripts/run/run_adaptive_math_search.py` replaces fixed repeated rounds with an
event-sourced search frontier. Three deliberately different proposal directions run
at a time. Candidates retain parent IDs, source artifact hashes, methodological
families, referee obligations, repair depth and task-specific score components.

Each generation performs hostile review after proposal, removes near-duplicate
claim/proof pairs, selects elites with a quality/diversity objective, and spends the
next calls on directed repairs, adversarial mutations, or a blind representation
reset when family entropy collapses. A lineage receives at most three focused
repairs. Search stops on independently reviewed high-scoring consensus, a measured
score plateau, or the explicit generation budget. Mutable runtime snapshots are only
convenience views; the append-only event chain remains the reconstruction source of
truth.

The universal-power-modulus evaluator is a hidden-oracle rediscovery benchmark, not
a novelty detector. For open-ended problems the structural evaluator can rank proof
quality, but its score and LLM referee verdicts are heuristic and cannot promote a
claim to formally verified truth.

## Minimal use

```python
from cognition.math_discovery import CampaignLedger, CampaignStore, Claim

store = CampaignStore.create(
    "campaigns",
    "prime-gap-pilot-001",
    problem="Precisely stated candidate problem",
    protocol={"max_concurrency": 3, "budget": {"calls": 90}},
)
ledger = CampaignLedger(store)
ledger.create_claim(
    Claim(
        statement="Falsifiable statement",
        domain="number_theory",
        created_by_job="explorer-001",
    )
)
```
