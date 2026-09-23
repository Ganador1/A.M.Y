# Mathematical discovery components

`cognition.math_discovery` provides campaign storage, research-job scheduling, claim review gates and adapters for computational verification. These are Python building blocks for a coordinator: creating a campaign does not start an autonomous search or establish a mathematical result.

## Included APIs

| Component | Purpose |
|---|---|
| `CampaignStore` | Create a campaign directory, retain its problem and protocol, and store content-addressed artifacts |
| `CampaignLedger`, `Claim`, `ClaimStatus` | Record candidate statements and enforce review-state transitions |
| `CampaignProvenance` | Record model/tool interactions and check manifests, hash chains and referenced artifacts |
| `ResearchJob`, `CampaignScheduler`, `MathematicalWorker` | Schedule dependent jobs and execute model roles through a supplied `ModelBroker` |
| `DiscoveryGatekeeper`, `ReviewEvidence` | Evaluate explicit evidence before changing a claim's status |
| `ExactComputationRunner`, `Z3Runner`, `LeanRunner` | Run finite checks, satisfiability checks or formal compilation with retained execution records |
| `AdaptiveFrontier` and task-specific evaluators | Track candidate lineage and scores for exploration, review and repair |

The package also includes difference-basis construction and evaluation helpers, unit-distance replication evaluation, and a universal-power-modulus benchmark. These supply specific search or replication methods; their presence does not establish a new theorem or a new record.

## Create and inspect a campaign

Run this example from the repository root after installing AMY. It uses a temporary directory and makes no model calls:

```python
from tempfile import TemporaryDirectory

from cognition.math_discovery import (
    CampaignLedger,
    CampaignProvenance,
    CampaignStore,
    Claim,
)

with TemporaryDirectory() as directory:
    store = CampaignStore.create(
        directory,
        "example-001",
        problem="Check whether n * (n + 1) is even for every integer n.",
        protocol={"max_concurrency": 1, "budget": {"calls": 0}},
    )
    ledger = CampaignLedger(store)
    claim = Claim(
        statement="For every integer n, n * (n + 1) is even.",
        domain="number_theory",
        created_by_job="example-proposer",
    )
    ledger.create_claim(claim)

    report = CampaignProvenance(store).verify()
    assert report["integrity_verified"] is True
    assert report["truth_verified"] is False
    assert ledger.claims()[claim.claim_id].truth_verified is False
```

The example records a statement and checks the retained record. It supplies no proof. For persistent work, choose your own campaign directory and a new campaign ID; creating an existing ID raises an error. Reopen it with `CampaignStore(directory, campaign_id)`.

## Jobs, roles and review gates

A coordinator constructs `ResearchJob` objects, supplies a worker and submits dependent jobs to `CampaignScheduler`. The scheduler reconstructs state from the event log and supports bounded retries. This mathematical scheduler currently accepts **one to three slots** through `max_slots`; it has its own limit even when an account or another AMY campaign supports higher concurrency.

Model availability, context limits, generation budgets and transport concurrency depend on the supplied jobs and client configuration. The role policies control which dependency artifacts enter a prompt. Blind exploration and independent rederivation restrict prior artifacts at prompt construction; this is not operating-system isolation.

Claims progress through explicit computational, literature, adversarial, independent-rederivation and formal-verification gates. A claim cannot promote itself or skip required transitions. A formal-verification transition requires a supported method and retained execution evidence; a model's assertion that a proof succeeded is insufficient. A refutation requires a retained counterexample. `UNKNOWN`, tool failure and a missing dependency must remain distinct from a proven or disproven statement.

The coordinator must invoke the required verification adapters and attach their outputs. The mathematical model worker does not automatically turn every suggested tool call into a completed formal verification.

## Verification scope

Exact enumeration checks the specified finite domain. Z3 checks the encoded problem under its configured limits. Lean checks the supplied formal statement and toolchain; its assumptions and statement must correspond to the intended mathematics. The adapters distinguish `PROVEN`, `DISPROVEN`, `UNKNOWN` and `ERROR` and retain evidence for the executed check.

Generated Python uses the configured Docker execution path. Lean defaults to container isolation and requires an appropriate toolchain/image; optional solvers and formal systems are not installed merely by importing this package.

SHA-256 chains detect inconsistencies in retained records. They do not authenticate the original author or time, prevent replacement by an older complete history, prove novelty, or establish mathematical truth. Heuristic frontier scores and model reviews help prioritize work but cannot replace formal or exact verification.

For runnable evidence packages and their commands, see [reproducibility](../../docs/REPRODUCIBILITY.md). For the distinction between integrity, numerical checks and mathematical claims, see [evidence](../../docs/EVIDENCE.md).
