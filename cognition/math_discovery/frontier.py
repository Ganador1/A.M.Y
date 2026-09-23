"""Adaptive, provenance-backed frontier for mathematical discovery.

The frontier deliberately separates model proposals from deterministic scoring.
Every mutation, review, score, duplicate decision and stop decision is appended to
the campaign event chain, so a coordinator can reconstruct the search after a
crash without trusting a mutable snapshot.
"""

from __future__ import annotations

import ast
import math
import re
import unicodedata
from dataclasses import asdict, dataclass
from typing import Any, Protocol

from cognition.math_discovery.storage import (
    CampaignStore,
    canonical_json_bytes,
    sha256_bytes,
)


_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def normalized_tokens(text: str | None) -> frozenset[str]:
    """Return a small, deterministic lexical fingerprint for novelty checks."""

    normalized = unicodedata.normalize("NFKD", text or "").lower()
    normalized = normalized.replace("−", "-").replace("∏", " product ")
    return frozenset(_TOKEN_RE.findall(normalized))


def jaccard_similarity(left: str | None, right: str | None) -> float:
    left_tokens = normalized_tokens(left)
    right_tokens = normalized_tokens(right)
    if not left_tokens and not right_tokens:
        return 1.0
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def claim_agreement(left: str | None, right: str | None) -> float:
    """Symmetric containment score for concise vs. expanded equivalent claims."""

    left_tokens = normalized_tokens(left)
    right_tokens = normalized_tokens(right)
    if not left_tokens and not right_tokens:
        return 1.0
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / min(len(left_tokens), len(right_tokens))


def candidate_similarity(
    left: "FrontierCandidate", right: "FrontierCandidate"
) -> float:
    claim = jaccard_similarity(left.claim, right.claim)
    proof = jaccard_similarity(left.proof_outline, right.proof_outline)
    return 0.65 * claim + 0.35 * proof


_METHOD_MARKERS: dict[str, tuple[str, ...]] = {
    "finite_field_group": (
        "primitive root",
        "finite field",
        "fermat",
        "cyclic",
        "multiplicative order",
        "group",
    ),
    "valuation_prime_power": (
        "p-adic",
        "valuation",
        "prime power",
        "squarefree",
        "p^2",
        "v_p",
    ),
    "computational_falsification": (
        "counterexample",
        "brute force",
        "exhaustive",
        "residue table",
        "computation",
        "z3",
    ),
    "polynomial_arithmetic": (
        "polynomial",
        "integer-valued",
        "carmichael",
        "gcd",
        "divisibility",
    ),
    "formal_decomposition": (
        "lean",
        "formal",
        "lemma dag",
        "theorem prover",
        "induction",
    ),
}


def method_family(parsed: dict[str, Any]) -> str:
    text = " ".join(
        str(parsed.get(key) or "")
        for key in ("candidate_claim", "proof_outline", "summary", "lemmas", "tests")
    ).lower()
    counts = {
        family: sum(text.count(marker) for marker in markers)
        for family, markers in _METHOD_MARKERS.items()
    }
    best = max(counts.values(), default=0)
    if best == 0:
        return "unclassified"
    winners = sorted(family for family, count in counts.items() if count == best)
    return winners[0] if len(winners) == 1 else "mixed"


def normalized_family_entropy(candidates: list["FrontierCandidate"]) -> float:
    """Shannon entropy in [0, 1], normalized by the observed population size."""

    if len(candidates) < 2:
        return 0.0
    counts: dict[str, int] = {}
    for candidate in candidates:
        counts[candidate.family] = counts.get(candidate.family, 0) + 1
    entropy = -sum(
        (count / len(candidates)) * math.log(count / len(candidates))
        for count in counts.values()
    )
    maximum = math.log(len(candidates))
    return entropy / maximum if maximum else 0.0


@dataclass(frozen=True)
class CandidateScore:
    objective: float
    rigor: float
    review: float
    novelty: float
    total: float
    evaluator: str
    evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("objective", "rigor", "review", "novelty", "total"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between zero and one")

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["evidence"] = list(self.evidence)
        return value

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "CandidateScore":
        payload = dict(value)
        payload["evidence"] = tuple(payload.get("evidence", ()))
        return cls(**payload)


@dataclass
class FrontierCandidate:
    candidate_id: str
    generation: int
    branch_id: str
    direction_id: str
    source_job_id: str
    artifact_hash: str
    claim: str
    proof_outline: str
    verdict: str
    family: str
    parent_candidate_ids: tuple[str, ...] = ()
    gaps: tuple[str, ...] = ()
    tests: tuple[str, ...] = ()
    repair_count: int = 0
    review_job_id: str | None = None
    review_verdict: str | None = None
    obligations: tuple[str, ...] = ()
    score: CandidateScore | None = None
    status: str = "active"
    duplicate_of: str | None = None

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        for key in ("parent_candidate_ids", "gaps", "tests", "obligations"):
            value[key] = list(value[key])
        value["score"] = self.score.to_dict() if self.score else None
        return value

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "FrontierCandidate":
        payload = dict(value)
        for key in ("parent_candidate_ids", "gaps", "tests", "obligations"):
            payload[key] = tuple(payload.get(key, ()))
        if payload.get("score") is not None:
            payload["score"] = CandidateScore.from_dict(payload["score"])
        return cls(**payload)


def candidate_from_result(
    *,
    generation: int,
    branch_id: str,
    direction_id: str,
    source_job_id: str,
    result: dict[str, Any],
    parent_candidate_ids: tuple[str, ...] = (),
    repair_count: int = 0,
) -> FrontierCandidate:
    parsed = result.get("parsed", {})
    artifact_hash = str(result.get("output_artifact", {}).get("sha256") or "")
    if not artifact_hash:
        raise ValueError("candidate result has no retained output artifact")
    identity = sha256_bytes(
        canonical_json_bytes(
            {
                "artifact_hash": artifact_hash,
                "generation": generation,
                "source_job_id": source_job_id,
            }
        )
    )
    return FrontierCandidate(
        candidate_id=f"cand_{identity[:24]}",
        generation=generation,
        branch_id=branch_id,
        direction_id=direction_id,
        source_job_id=source_job_id,
        artifact_hash=artifact_hash,
        claim=str(parsed.get("candidate_claim") or "").strip(),
        proof_outline=str(parsed.get("proof_outline") or "").strip(),
        verdict=str(parsed.get("verdict") or "inconclusive"),
        family=method_family(parsed),
        parent_candidate_ids=parent_candidate_ids,
        gaps=tuple(str(item) for item in parsed.get("gaps", ()) if str(item).strip()),
        tests=tuple(str(item) for item in parsed.get("tests", ()) if str(item).strip()),
        repair_count=repair_count,
    )


def obligations_from_review(review: dict[str, Any]) -> tuple[str, ...]:
    obligations = [
        str(item).strip() for item in review.get("gaps", ()) if str(item).strip()
    ]
    verdict = str(review.get("verdict") or "inconclusive")
    if verdict != "supported" and not obligations:
        summary = str(review.get("summary") or "review did not support the candidate")
        obligations.append(summary.strip())
    return tuple(dict.fromkeys(obligations))


class CandidateEvaluator(Protocol):
    name: str

    def evaluate(
        self,
        candidate: FrontierCandidate,
        *,
        review: dict[str, Any] | None,
        novelty: float,
    ) -> CandidateScore: ...


class StructuralEvaluator:
    """Generic evaluator for problems without a task-specific executable oracle."""

    name = "structural-v1"

    def evaluate(
        self,
        candidate: FrontierCandidate,
        *,
        review: dict[str, Any] | None,
        novelty: float,
    ) -> CandidateScore:
        evidence: list[str] = []
        objective = 0.0
        if candidate.claim:
            objective += 0.55
            evidence.append("nonempty precise candidate claim")
        if candidate.verdict == "supported":
            objective += 0.25
            evidence.append("proposer marks claim supported")
        if candidate.tests:
            objective += 0.20
            evidence.append("candidate includes falsifiable tests")

        rigor = 0.0
        if candidate.proof_outline:
            rigor += 0.55
        if len(candidate.proof_outline) >= 400:
            rigor += 0.20
        if not candidate.gaps:
            rigor += 0.25

        review_score = 0.0
        if review is not None:
            if review.get("verdict") == "supported":
                review_score += 0.6
            if not obligations_from_review(review):
                review_score += 0.4
        total = 0.35 * objective + 0.30 * rigor + 0.25 * review_score + 0.10 * novelty
        if candidate.verdict == "refuted" or (review or {}).get("verdict") == "refuted":
            total = min(total, 0.30)
        return CandidateScore(
            objective=_clamp(objective),
            rigor=_clamp(rigor),
            review=_clamp(review_score),
            novelty=_clamp(novelty),
            total=_clamp(total),
            evaluator=self.name,
            evidence=tuple(evidence),
        )


class UniversalPowerModulusEvaluator:
    """Hidden-oracle evaluator for the universal-modulus rediscovery benchmark."""

    name = "universal-power-modulus-v1"

    @staticmethod
    def _text(candidate: FrontierCandidate) -> str:
        return (
            " ".join((candidate.claim, candidate.proof_outline, *candidate.tests))
            .lower()
            .replace("−", "-")
            .replace("∏", " product ")
        )

    def evaluate(
        self,
        candidate: FrontierCandidate,
        *,
        review: dict[str, Any] | None,
        novelty: float,
    ) -> CandidateScore:
        text = self._text(candidate)
        compact = re.sub(r"\s+", "", text)
        formula_checks = (
            "prime" in text,
            "product" in text or "\\prod" in text,
            "p-1" in compact,
            "k-1" in compact,
            "divid" in text or "|" in text or "\\mid" in text,
        )
        objective = sum(formula_checks) / len(formula_checks)

        obligations = {
            "existence_finiteness": "finite" in text
            or "p <= k" in text
            or "p≤k" in text,
            "prime_power_exclusion": any(
                marker in text
                for marker in ("squarefree", "p^2", "prime power", "valuation", "v_p")
            ),
            "necessity": "necess" in text
            and any(marker in text for marker in ("primitive root", "order", "cyclic")),
            "sufficiency": "fermat" in text
            and any(
                marker in text
                for marker in ("sufficien", "converse", "crt", "chinese remainder")
            ),
            "maximality": any(
                marker in text
                for marker in (
                    "maximal",
                    "greatest",
                    "every valid modulus",
                    "m divides",
                )
            ),
            "coprime_combination": "crt" in text or "chinese remainder" in text,
        }
        rigor = sum(obligations.values()) / len(obligations)
        if candidate.gaps:
            rigor *= max(0.5, 1.0 - 0.12 * len(candidate.gaps))

        review_score = 0.0
        if review is not None:
            review_obligations = obligations_from_review(review)
            if review.get("verdict") == "supported" and not review_obligations:
                review_score = 1.0
            elif not review_obligations:
                review_score = 0.35
        total = 0.40 * objective + 0.30 * rigor + 0.20 * review_score + 0.10 * novelty
        if candidate.verdict == "refuted" or (review or {}).get("verdict") == "refuted":
            total = min(total, 0.30)
        evidence = [name for name, passed in obligations.items() if passed]
        evidence.append(f"formula_markers={sum(formula_checks)}/{len(formula_checks)}")
        return CandidateScore(
            objective=_clamp(objective),
            rigor=_clamp(rigor),
            review=_clamp(review_score),
            novelty=_clamp(novelty),
            total=_clamp(total),
            evaluator=self.name,
            evidence=tuple(evidence),
        )


class UnitDistanceReplicationEvaluator:
    """Hidden published-route coverage evaluator for the unit-distance result.

    This is not a proof checker. It measures whether a blind candidate reaches the
    exact negative theorem and closes the key obligations in the published route.
    An alternative valid proof could therefore be underestimated and must be
    escalated to expert review rather than discarded automatically.
    """

    name = "unit-distance-replication-v1"

    @staticmethod
    def _text(candidate: FrontierCandidate) -> str:
        return (
            " ".join((candidate.claim, candidate.proof_outline, *candidate.tests))
            .lower()
            .replace("−", "-")
            .replace("δ", "delta")
            .replace("ν", "nu")
            .replace("∞", "infinity")
        )

    def evaluate(
        self,
        candidate: FrontierCandidate,
        *,
        review: dict[str, Any] | None,
        novelty: float,
    ) -> CandidateScore:
        text = self._text(candidate)
        compact = re.sub(r"\s+", "", text)
        resolution_checks = {
            "negative_resolution": any(
                marker in text
                for marker in (
                    "disprove",
                    "refute",
                    "no such constants",
                    "conjecture is false",
                    "negative resolution",
                )
            ),
            "fixed_positive_exponent": (
                "delta" in text
                and any(marker in text for marker in ("fixed", "absolute", "> 0", ">0"))
            ),
            "infinitely_many_sizes": any(
                marker in text for marker in ("infinitely many", "infinite sequence")
            )
            or re.search(r"\bn_?j\b", text) is not None,
            "polynomial_superlinear_bound": (
                ("n^(1+" in compact or "n^{1+" in compact or "1+delta" in compact)
                and any(marker in text for marker in ("unit distance", "nu(", "ν("))
            ),
        }
        objective = sum(resolution_checks.values()) / len(resolution_checks)
        if candidate.verdict != "supported" or not candidate.claim:
            # Mentioning the vocabulary of a resolution is not proposing one.
            # Retain partial diagnostic signal without promoting an analysis.
            objective *= 0.25

        obligations = {
            "counterexample_family": any(
                marker in text
                for marker in ("construction", "point set", "point-set", "family")
            ),
            "growing_degree_number_fields": (
                "number field" in text
                and any(
                    marker in text
                    for marker in ("growing degree", "degree tends", "high-dimensional")
                )
            ),
            "bounded_root_discriminant": (
                "root discriminant" in text
                and any(marker in text for marker in ("bounded", "constant", "uniform"))
            ),
            "infinite_unramified_tower": (
                any(
                    marker in text
                    for marker in ("unramified tower", "class field tower")
                )
                and any(
                    marker in text
                    for marker in ("golod", "shafarevich", "pro-3", "pro-p")
                )
            ),
            "prescribed_split_primes": (
                "split completely" in text
                and any(
                    marker in text
                    for marker in ("frobenius", "chebotarev", "prescribed prime")
                )
            ),
            "many_norm_one_elements": (
                any(
                    marker in text
                    for marker in ("norm-one", "norm one", "u c(u)", "u*c(u)")
                )
                and any(
                    marker in text
                    for marker in (
                        "every embedding",
                        "all embeddings",
                        "absolute value 1",
                        "modulus 1",
                    )
                )
            ),
            "exponential_count_survives_class_group": (
                any(marker in text for marker in ("class group", "class-group"))
                and any(
                    marker in text
                    for marker in ("exponential", "pigeonhole", "class number")
                )
            ),
            "minkowski_lattice_projection": (
                "minkowski" in text
                and "lattice" in text
                and any(
                    marker in text for marker in ("project", "coordinate", "injective")
                )
            ),
            "unit_pair_counting": (
                any(
                    marker in text
                    for marker in (
                        "unit segment",
                        "unit-distance pair",
                        "unit distance pair",
                    )
                )
                and any(
                    marker in text
                    for marker in ("average", "count", "multiplicity", "at most twice")
                )
            ),
            "parameter_closure": (
                "delta" in text
                and any(
                    marker in text
                    for marker in (
                        "log log",
                        "for every c",
                        "arbitrary c",
                        "sufficiently large",
                    )
                )
            ),
        }
        rigor = sum(obligations.values()) / len(obligations)
        if candidate.gaps:
            rigor *= max(0.35, 1.0 - 0.10 * len(candidate.gaps))

        review_score = 0.0
        if review is not None:
            review_obligations = obligations_from_review(review)
            if review.get("verdict") == "supported" and not review_obligations:
                review_score = 1.0
            elif not review_obligations:
                review_score = 0.35
        # Lexical novelty is useful for frontier diversity, but it is not
        # mathematical evidence and must not raise a unit-distance claim's score.
        total = 0.35 * objective + 0.40 * rigor + 0.25 * review_score
        if candidate.verdict == "refuted" or (review or {}).get("verdict") == "refuted":
            total = min(total, 0.25)
        elif candidate.verdict != "supported":
            total = min(total, 0.30)
        evidence = [name for name, passed in obligations.items() if passed]
        evidence.extend(name for name, passed in resolution_checks.items() if passed)
        return CandidateScore(
            objective=_clamp(objective),
            rigor=_clamp(rigor),
            review=_clamp(review_score),
            novelty=_clamp(novelty),
            total=_clamp(total),
            evaluator=self.name,
            evidence=tuple(evidence),
        )


def evaluate_difference_basis(values: list[int]) -> dict[str, Any]:
    """Exactly evaluate a finite difference basis using integer arithmetic."""

    if not values or len(values) > 2000:
        return {"valid": False, "reason": "basis size must be in [1, 2000]"}
    if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        return {"valid": False, "reason": "basis elements must be integers"}
    basis = sorted(set(values))
    if basis[0] < 0:
        return {"valid": False, "reason": "basis elements must be nonnegative"}
    differences = {
        basis[j] - basis[i]
        for i in range(len(basis))
        for j in range(i + 1, len(basis))
    }
    first_missing = next(
        value for value in range(1, (max(differences) if differences else 0) + 2)
        if value not in differences
    )
    covered = first_missing - 1
    if covered < 1:
        return {"valid": False, "reason": "difference 1 is not covered"}
    ratio = len(basis) ** 2 / covered
    return {
        "valid": True,
        "basis": basis,
        "size": len(basis),
        "covered_through": covered,
        "ratio": ratio,
    }


_INTEGER_LIST_RE = re.compile(r"\[(?:\s*-?\d+\s*,?\s*)+\]")
_NAMED_INTEGER_LIST_RE = re.compile(
    r"\b(?P<name>A|B|basis|combined_set)\s*=\s*"
    r"(?P<value>\[(?:\s*-?\d+\s*,?\s*)+\])",
    re.IGNORECASE,
)
_MODULUS_RE = re.compile(r"\b(?:m|modulus)\s*=\s*(\d+)\b", re.IGNORECASE)


def difference_basis_constructions(text: str) -> list[list[int]]:
    """Extract explicit bases and safe ``{a*m+b}`` product constructions."""

    constructions: list[list[int]] = []
    named: dict[str, list[int]] = {}
    for match in _NAMED_INTEGER_LIST_RE.finditer(text):
        value = ast.literal_eval(match.group("value"))
        if isinstance(value, list):
            named[match.group("name").lower()] = value
            constructions.append(value)
    for match in _INTEGER_LIST_RE.finditer(text):
        value = ast.literal_eval(match.group(0))
        if isinstance(value, list) and value not in constructions:
            constructions.append(value)
    modulus_match = _MODULUS_RE.search(text)
    if "a" in named and "b" in named and modulus_match:
        modulus = int(modulus_match.group(1))
        constructions.append(
            sorted({a * modulus + b for a in named["a"] for b in named["b"]})
        )
    return constructions


def best_difference_basis_evaluation(
    candidate: FrontierCandidate,
) -> dict[str, Any] | None:
    """Return the candidate's strongest exact explicit construction, if any."""

    text = "\n".join((candidate.claim, candidate.proof_outline, *candidate.tests))
    evaluated = [
        evaluate_difference_basis(values)
        for values in difference_basis_constructions(text)
    ]
    valid = [result for result in evaluated if result.get("valid")]
    return min(valid, key=lambda result: result["ratio"]) if valid else None


def difference_basis_semantic_fingerprint(
    candidate: FrontierCandidate,
) -> str | None:
    """Hash the normalized best basis instead of its surrounding prose."""

    best = best_difference_basis_evaluation(candidate)
    if best is None:
        return None
    return sha256_bytes(canonical_json_bytes(best["basis"]))


class DifferenceBasisReplicationEvaluator:
    """Exact construction evaluator for AlphaEvolve difference-basis replication."""

    name = "difference-basis-replication-v1"
    baseline_ratio = 8.0 / 3.0
    published_ratio = 129600.0 / 49109.0

    def evaluate(
        self,
        candidate: FrontierCandidate,
        *,
        review: dict[str, Any] | None,
        novelty: float,
    ) -> CandidateScore:
        best = best_difference_basis_evaluation(candidate)
        if best is None:
            return CandidateScore(
                objective=0.0,
                rigor=0.0,
                review=0.0,
                novelty=_clamp(novelty),
                total=_clamp(0.05 * novelty),
                evaluator=self.name,
                evidence=("no valid explicit integer difference basis parsed",),
            )

        best_ratio = float(best["ratio"])
        replication_span = self.baseline_ratio - self.published_ratio
        if best_ratio >= self.published_ratio:
            # Reserve the top five percent for genuine progress beyond the
            # replicated published construction.  Previously the score
            # saturated at the incumbent and could not rank marginal gains.
            objective = 0.95 * _clamp(
                (self.baseline_ratio - best_ratio) / replication_span
            )
        else:
            sixty_four_step_ratio = 129600.0 / (49109.0 + 64.0)
            strict_gain_span = self.published_ratio - sixty_four_step_ratio
            objective = 0.95 + 0.05 * _clamp(
                (self.published_ratio - best_ratio) / strict_gain_span
            )
        review_verdict = str((review or {}).get("verdict") or "inconclusive")
        review_gaps = tuple((review or {}).get("gaps") or ())
        review_score = (
            1.0
            if review_verdict == "supported" and not review_gaps
            else 0.35
            if review_verdict == "inconclusive"
            else 0.0
        )
        strict_improvement = bool(
            int(best["covered_through"]) > 49109
            and float(best["ratio"]) < self.published_ratio
        )
        basis_fingerprint = sha256_bytes(canonical_json_bytes(best["basis"]))
        total = (
            0.75 * objective
            + 0.15
            + 0.05 * review_score
            + 0.05 * novelty
        )
        evidence = (
            "exact integer verification passed",
            f"basis_size={best['size']}",
            f"covered_through={best['covered_through']}",
            f"ratio={best['ratio']:.15g}",
            f"published_ratio={self.published_ratio:.15g}",
            f"basis_sha256={basis_fingerprint}",
            f"strict_improvement={str(strict_improvement).lower()}",
        )
        return CandidateScore(
            objective=objective,
            rigor=1.0,
            review=_clamp(review_score),
            novelty=_clamp(novelty),
            total=_clamp(total),
            evaluator=self.name,
            evidence=evidence,
        )


class AdaptiveFrontier:
    """Event-sourced candidate frontier and selection policy."""

    def __init__(self, store: CampaignStore, *, actor: str = "adaptive_frontier"):
        self.store = store
        self.actor = actor

    def candidates(self) -> dict[str, FrontierCandidate]:
        candidates: dict[str, FrontierCandidate] = {}
        for event in self.store.event_log.records():
            event_type = event.get("event_type")
            payload = event.get("payload", {})
            if event_type == "frontier_candidate_added":
                candidate = FrontierCandidate.from_dict(payload["candidate"])
                candidates[candidate.candidate_id] = candidate
            elif event_type == "frontier_candidate_reviewed":
                candidate = candidates[payload["candidate_id"]]
                candidate.review_job_id = payload["review_job_id"]
                candidate.review_verdict = payload["review_verdict"]
                candidate.obligations = tuple(payload.get("obligations", ()))
            elif event_type == "frontier_candidate_scored":
                candidates[payload["candidate_id"]].score = CandidateScore.from_dict(
                    payload["score"]
                )
            elif event_type == "frontier_candidate_status":
                candidate = candidates[payload["candidate_id"]]
                candidate.status = payload["status"]
                candidate.duplicate_of = payload.get("duplicate_of")
        return candidates

    def add(self, candidate: FrontierCandidate) -> bool:
        if candidate.candidate_id in self.candidates():
            return False
        self.store.event_log.append(
            "frontier_candidate_added",
            {"candidate": candidate.to_dict()},
            actor=self.actor,
        )
        return True

    def record_review(
        self,
        candidate_id: str,
        *,
        review_job_id: str,
        review: dict[str, Any],
    ) -> None:
        candidate = self.candidates()[candidate_id]
        obligations = obligations_from_review(review)
        if candidate.review_job_id == review_job_id:
            return
        self.store.event_log.append(
            "frontier_candidate_reviewed",
            {
                "candidate_id": candidate_id,
                "review_job_id": review_job_id,
                "review_verdict": str(review.get("verdict") or "inconclusive"),
                "obligations": list(obligations),
            },
            actor=self.actor,
        )

    def score(
        self,
        candidate_id: str,
        evaluator: CandidateEvaluator,
        *,
        review: dict[str, Any] | None,
    ) -> CandidateScore:
        candidates = self.candidates()
        candidate = candidates[candidate_id]
        peers = [item for key, item in candidates.items() if key != candidate_id]
        novelty = 1.0 - max(
            (candidate_similarity(candidate, peer) for peer in peers),
            default=0.0,
        )
        score = evaluator.evaluate(candidate, review=review, novelty=novelty)
        self.store.event_log.append(
            "frontier_candidate_scored",
            {"candidate_id": candidate_id, "score": score.to_dict()},
            actor=self.actor,
        )
        return score

    def mark_duplicates(self, *, generation: int) -> list[tuple[str, str]]:
        candidates = self.candidates()
        current = sorted(
            (item for item in candidates.values() if item.generation == generation),
            key=lambda item: (
                -(item.score.total if item.score else 0.0),
                item.candidate_id,
            ),
        )
        kept: list[FrontierCandidate] = [
            item
            for item in candidates.values()
            if item.generation < generation and item.status != "duplicate"
        ]
        duplicates: list[tuple[str, str]] = []
        for candidate in current:
            semantic_fingerprint = difference_basis_semantic_fingerprint(candidate)
            duplicate = next(
                (
                    prior
                    for prior in kept
                    if (
                        semantic_fingerprint is not None
                        and semantic_fingerprint
                        == difference_basis_semantic_fingerprint(prior)
                    )
                    or (
                        jaccard_similarity(candidate.claim, prior.claim) >= 0.96
                        and jaccard_similarity(
                            candidate.proof_outline, prior.proof_outline
                        )
                        >= 0.88
                    )
                ),
                None,
            )
            if duplicate is None:
                kept.append(candidate)
                continue
            self.set_status(
                candidate.candidate_id,
                "duplicate",
                duplicate_of=duplicate.candidate_id,
            )
            duplicates.append((candidate.candidate_id, duplicate.candidate_id))
        return duplicates

    def set_status(
        self,
        candidate_id: str,
        status: str,
        *,
        duplicate_of: str | None = None,
    ) -> None:
        candidate = self.candidates()[candidate_id]
        if candidate.status == status and candidate.duplicate_of == duplicate_of:
            return
        self.store.event_log.append(
            "frontier_candidate_status",
            {
                "candidate_id": candidate_id,
                "status": status,
                "duplicate_of": duplicate_of,
            },
            actor=self.actor,
        )

    def select_elites(
        self, *, limit: int = 3, preserve_lineages: bool = False
    ) -> list[FrontierCandidate]:
        pool = [
            candidate
            for candidate in self.candidates().values()
            if candidate.score is not None
            and candidate.status not in {"duplicate", "refuted", "discarded"}
            and candidate.verdict != "refuted"
        ]
        selected: list[FrontierCandidate] = []

        if preserve_lineages:
            candidates = self.candidates()

            def root_id(candidate: FrontierCandidate) -> str:
                current = candidate
                seen = {current.candidate_id}
                while current.parent_candidate_ids:
                    parent_id = current.parent_candidate_ids[0]
                    if parent_id in seen or parent_id not in candidates:
                        break
                    seen.add(parent_id)
                    current = candidates[parent_id]
                return current.candidate_id

            lineages: dict[str, list[FrontierCandidate]] = {}
            for candidate in pool:
                lineages.setdefault(root_id(candidate), []).append(candidate)
            reserved = [
                max(
                    members,
                    key=lambda item: (item.score.total, item.candidate_id),
                )
                for members in lineages.values()
            ]
            reserved.sort(
                key=lambda item: (item.score.total, item.candidate_id), reverse=True
            )
            selected.extend(reserved[:limit])
            pool = [item for item in pool if item not in selected]

        while pool and len(selected) < limit:

            def utility(candidate: FrontierCandidate) -> tuple[float, str]:
                diversity = 1.0 - max(
                    (candidate_similarity(candidate, elite) for elite in selected),
                    default=0.0,
                )
                return (
                    0.82 * candidate.score.total + 0.18 * diversity,
                    candidate.candidate_id,
                )

            winner = max(pool, key=utility)
            selected.append(winner)
            pool.remove(winner)
        return selected

    def generation_completed(self, generation: int) -> bool:
        return any(
            event.get("event_type") == "frontier_generation_completed"
            and event.get("payload", {}).get("generation") == generation
            for event in self.store.event_log.records()
        )

    def complete_generation(self, generation: int) -> dict[str, Any]:
        if self.generation_completed(generation):
            return next(
                event["payload"]
                for event in reversed(self.store.event_log.records())
                if event.get("event_type") == "frontier_generation_completed"
                and event.get("payload", {}).get("generation") == generation
            )
        current = [
            item for item in self.candidates().values() if item.generation == generation
        ]
        active = [
            item
            for item in current
            if item.status not in {"duplicate", "refuted", "discarded"}
        ]
        payload = {
            "generation": generation,
            "candidate_ids": [item.candidate_id for item in current],
            "active_candidate_ids": [item.candidate_id for item in active],
            "best_score": max(
                (item.score.total for item in active if item.score is not None),
                default=0.0,
            ),
            "family_entropy": normalized_family_entropy(active),
            "families": sorted({item.family for item in active}),
        }
        self.store.event_log.append(
            "frontier_generation_completed", payload, actor=self.actor
        )
        return payload

    def generation_history(self) -> list[dict[str, Any]]:
        return [
            event["payload"]
            for event in self.store.event_log.records()
            if event.get("event_type") == "frontier_generation_completed"
        ]

    def stop_decision(
        self,
        *,
        patience: int = 3,
        min_delta: float = 0.015,
        success_score: float = 0.84,
    ) -> dict[str, Any]:
        history = self.generation_history()
        candidates = list(self.candidates().values())
        qualified = [
            item
            for item in candidates
            if item.score is not None
            and item.status != "duplicate"
            and item.score.total >= success_score
            and item.score.objective >= 0.95
            and item.score.rigor >= 0.80
            and item.review_verdict == "supported"
            and not item.obligations
        ]
        for index, left in enumerate(qualified):
            for right in qualified[index + 1 :]:
                if (
                    left.direction_id != right.direction_id
                    and claim_agreement(left.claim, right.claim) >= 0.85
                ):
                    return {
                        "stop": True,
                        "reason": "independent_high_score_consensus",
                        "candidate_ids": [left.candidate_id, right.candidate_id],
                    }
        if len(history) >= patience + 1:
            window = history[-(patience + 1) :]
            baseline = float(window[0].get("best_score", 0.0))
            later_best = max(float(item.get("best_score", 0.0)) for item in window[1:])
            if later_best - baseline < min_delta:
                return {
                    "stop": True,
                    "reason": "score_plateau",
                    "generations": [item["generation"] for item in window],
                    "improvement": later_best - baseline,
                }
        return {"stop": False, "reason": "continue"}
