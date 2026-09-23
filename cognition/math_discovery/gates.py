"""Evidence-backed campaign gates layered above the append-only claim ledger."""
from __future__ import annotations

from dataclasses import dataclass

from cognition.math_discovery.formalization import FormalizationReport
from cognition.math_discovery.ledger import CampaignLedger, claim_statement_sha256
from cognition.math_discovery.models import ClaimStatus
from cognition.math_discovery.rederivation import RederivationReport
from cognition.math_discovery.storage import CampaignStore
from cognition.math_discovery.tools.models import ToolResult, VerificationStatus


@dataclass(frozen=True)
class ReviewEvidence:
    job_id: str
    artifact_hash: str
    verdict: str
    gaps: tuple[str, ...] = ()
    counterexample: object = None
    counterexample_verified: bool = False


@dataclass(frozen=True)
class GateDecision:
    passed: bool
    target_status: ClaimStatus | None
    reason: str
    evidence_hashes: tuple[str, ...]
    gaps: tuple[str, ...] = ()
    verification_event_hash: str | None = None
    exact_statement_sha256: str | None = None


class DiscoveryGatekeeper:
    def __init__(self, store: CampaignStore):
        self.store = store
        self.ledger = CampaignLedger(store)

    def computational(self, results: tuple[ToolResult, ...]) -> GateDecision:
        verified_counterexamples = [
            item
            for item in results
            if item.status is VerificationStatus.DISPROVEN
            and item.counterexample is not None
            and item.evidence_hashes
        ]
        if verified_counterexamples:
            tools = ", ".join(item.tool_name for item in verified_counterexamples)
            evidence = tuple(
                dict.fromkeys(
                    digest
                    for item in verified_counterexamples
                    for digest in item.evidence_hashes
                )
            )
            return GateDecision(
                True,
                ClaimStatus.REFUTED,
                f"verified counterexample retained by: {tools}",
                evidence,
            )
        incomplete_refutations = [
            item.tool_name
            for item in results
            if item.status is VerificationStatus.DISPROVEN
        ]
        if incomplete_refutations:
            return GateDecision(
                False,
                None,
                "a tool reported DISPROVEN without a retained counterexample",
                (),
                tuple(f"missing counterexample: {name}" for name in incomplete_refutations),
            )
        proven = [item for item in results if item.status is VerificationStatus.PROVEN]
        if not proven:
            gaps = tuple(f"{item.tool_name}: {item.status.value}" for item in results)
            return GateDecision(False, None, "no exact tool produced support", (), gaps)
        evidence = tuple(dict.fromkeys(h for item in proven for h in item.evidence_hashes))
        return GateDecision(
            True,
            ClaimStatus.COMPUTATIONALLY_SUPPORTED,
            "at least one exact, scoped tool obligation returned PROVEN",
            evidence,
        )

    def literature(self, evidence_hashes: tuple[str, ...]) -> GateDecision:
        return self._simple(
            ClaimStatus.LITERATURE_CHECKED,
            evidence_hashes,
            "literature map retained; this gate does not assert novelty",
        )

    def adversarial(self, reviews: tuple[ReviewEvidence, ...]) -> GateDecision:
        refutation = next(
            (
                review for review in reviews
                if review.verdict == "refuted" and review.counterexample_verified
            ),
            None,
        )
        if refutation:
            return GateDecision(
                True,
                ClaimStatus.REFUTED,
                f"verified adversarial counterexample from {refutation.job_id}",
                (refutation.artifact_hash,),
            )
        gaps = tuple(dict.fromkeys(gap for review in reviews for gap in review.gaps))
        supporting = [review for review in reviews if review.verdict == "supported"]
        if gaps or not supporting:
            return GateDecision(False, None, "adversarial review did not clear all gaps", (), gaps)
        return self._simple(
            ClaimStatus.ADVERSARIALLY_SURVIVED,
            tuple(review.artifact_hash for review in supporting),
            "independent adversarial review retained no unresolved objection",
        )

    def rederivation(self, report: RederivationReport) -> GateDecision:
        if not report.passed:
            return GateDecision(
                False, None, "blind rederivations did not recover the mechanism",
                report.evidence_hashes, report.gaps,
            )
        return self._simple(
            ClaimStatus.INDEPENDENTLY_REDERIVED,
            report.evidence_hashes,
            f"two blind derivations aligned (score={report.overlap_score:.3f})",
        )

    def formalization(
        self, report: FormalizationReport, *, verification_event_hash: str | None = None,
    ) -> GateDecision:
        if not report.fully_verified or report.verification_method is None:
            return GateDecision(
                False,
                None,
                f"formal coverage is {report.coverage:.1%}",
                report.evidence_hashes,
                report.gaps,
            )
        if verification_event_hash is None:
            return GateDecision(False, None, "formal gate requires a retained execution receipt",
                                report.evidence_hashes)
        try:
            matches = [event for event in self.store.event_log.records()
                       if event.get("event_hash") == verification_event_hash]
            if len(matches) != 1:
                raise ValueError("formal execution receipt is missing or ambiguous")
            payload = matches[0]["payload"]
            binding = payload["metadata"]["verification_binding"]
            claim = self.ledger.claims()[binding["claim_id"]]
            if report.exact_statement_sha256 != claim_statement_sha256(claim):
                raise ValueError("formal report statement differs from the claim")
            self.ledger.require_formal_receipt(
                claim, reviewer_job_id=payload["job_id"],
                evidence_hashes=report.evidence_hashes,
                verification_method=report.verification_method,
                verification_event_hash=verification_event_hash,
            )
            actual_axioms = tuple(payload["metadata"].get("reported_axioms", ()))
            if report.reported_axioms != actual_axioms:
                raise ValueError("formal report axiom scope differs from the checker receipt")
        except (KeyError, TypeError, ValueError, OSError, AttributeError) as exc:
            return GateDecision(False, None, f"formal receipt rejected: {exc}",
                                report.evidence_hashes, (str(exc),))
        return GateDecision(
            True,
            ClaimStatus.FORMALLY_VERIFIED,
            f"claim-bound checker receipt retained; axioms={list(report.reported_axioms)}; "
            "scope=declared_formal_input; trust=local_runner; authenticated=False",
            report.evidence_hashes,
            verification_event_hash=verification_event_hash,
            exact_statement_sha256=report.exact_statement_sha256,
        )

    def apply(
        self,
        claim_id: str,
        decision: GateDecision,
        *,
        reviewer_job_id: str,
        verification_method: str | None = None,
        verification_event_hash: str | None = None,
    ) -> dict:
        if not decision.passed or decision.target_status is None:
            raise ValueError("cannot apply a blocked gate decision")
        self._require_retained_artifacts(decision.evidence_hashes)
        receipt = verification_event_hash or decision.verification_event_hash
        if (verification_event_hash is not None and decision.verification_event_hash is not None
                and verification_event_hash != decision.verification_event_hash):
            raise ValueError("formal decision and execution receipt differ")
        if decision.exact_statement_sha256 is not None:
            claim = self.ledger.claims()[claim_id]
            if claim_statement_sha256(claim) != decision.exact_statement_sha256:
                raise ValueError("formal decision and claim statement differ")
        return self.ledger.transition(
            claim_id,
            decision.target_status,
            reviewer_job_id=reviewer_job_id,
            evidence_hashes=list(decision.evidence_hashes),
            reason=decision.reason,
            verification_method=verification_method,
            verification_event_hash=receipt,
        )

    @staticmethod
    def _simple(
        status: ClaimStatus,
        evidence_hashes: tuple[str, ...],
        reason: str,
    ) -> GateDecision:
        if not evidence_hashes:
            return GateDecision(False, None, "gate has no retained evidence", ())
        return GateDecision(True, status, reason, tuple(dict.fromkeys(evidence_hashes)))

    def _require_retained_artifacts(self, hashes: tuple[str, ...]) -> None:
        if not hashes:
            raise ValueError("gate requires retained evidence")
        for digest in hashes:
            self.store.artifacts.read_by_hash(digest)
