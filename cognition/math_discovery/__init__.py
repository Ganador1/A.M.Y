"""Auditable campaign primitives for A.M.Y Mathematical Discovery Mode."""

from cognition.math_discovery.ledger import CampaignLedger
from cognition.math_discovery.models import (
    Claim,
    ClaimStatus,
    JobResult,
    JobStatus,
    ResearchJob,
    ResearchRole,
)
from cognition.math_discovery.provenance import CampaignProvenance
from cognition.math_discovery.storage import CampaignStore
from cognition.math_discovery.scheduler import CampaignScheduler
from cognition.math_discovery.gates import (
    DiscoveryGatekeeper,
    GateDecision,
    ReviewEvidence,
)
from cognition.math_discovery.formalization import (
    FormalizationReport,
    assess_formalization,
)
from cognition.math_discovery.rederivation import (
    BlindDerivation,
    RederivationReport,
    compare_blind_derivations,
)
from cognition.math_discovery.worker import MathematicalWorker
from cognition.math_discovery.program_frontier import (
    DifferenceBasisProgramRunner,
    ConstructProgramCompiler,
    DifferenceBasisLocalEvolution,
    PopulationMember,
    affine_residues,
    exact_difference_basis_metrics,
    layered_difference_basis,
    singer_residue_set,
    ProgramEvaluation,
    extract_construct_program,
    validate_construct_program,
)
from cognition.math_discovery.frontier import (
    AdaptiveFrontier,
    CandidateScore,
    DifferenceBasisReplicationEvaluator,
    FrontierCandidate,
    StructuralEvaluator,
    UniversalPowerModulusEvaluator,
    UnitDistanceReplicationEvaluator,
    candidate_from_result,
    candidate_similarity,
    claim_agreement,
    jaccard_similarity,
    normalized_family_entropy,
    obligations_from_review,
    difference_basis_constructions,
    evaluate_difference_basis,
)
from cognition.math_discovery.tools import (
    ExactComputationRunner,
    FiniteEnumerationSpec,
    LeanRunner,
    ToolResult,
    VerificationStatus,
    Z3Runner,
)

__all__ = [
    "CampaignLedger",
    "CampaignProvenance",
    "CampaignStore",
    "CampaignScheduler",
    "DiscoveryGatekeeper",
    "GateDecision",
    "ReviewEvidence",
    "FormalizationReport",
    "assess_formalization",
    "BlindDerivation",
    "RederivationReport",
    "compare_blind_derivations",
    "Claim",
    "ClaimStatus",
    "JobResult",
    "JobStatus",
    "ResearchJob",
    "ResearchRole",
    "MathematicalWorker",
    "DifferenceBasisProgramRunner",
    "ConstructProgramCompiler",
    "DifferenceBasisLocalEvolution",
    "PopulationMember",
    "affine_residues",
    "exact_difference_basis_metrics",
    "layered_difference_basis",
    "singer_residue_set",
    "ProgramEvaluation",
    "extract_construct_program",
    "validate_construct_program",
    "AdaptiveFrontier",
    "CandidateScore",
    "DifferenceBasisReplicationEvaluator",
    "FrontierCandidate",
    "StructuralEvaluator",
    "UniversalPowerModulusEvaluator",
    "UnitDistanceReplicationEvaluator",
    "candidate_from_result",
    "candidate_similarity",
    "claim_agreement",
    "jaccard_similarity",
    "normalized_family_entropy",
    "obligations_from_review",
    "difference_basis_constructions",
    "evaluate_difference_basis",
    "ExactComputationRunner",
    "FiniteEnumerationSpec",
    "LeanRunner",
    "ToolResult",
    "VerificationStatus",
    "Z3Runner",
]
