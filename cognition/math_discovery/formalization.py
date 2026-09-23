"""Coverage accounting for exact formal statements and their proof obligations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from cognition.math_discovery.tools.models import ToolResult, VerificationStatus


@dataclass(frozen=True)
class FormalizationReport:
    exact_statement_sha256: str
    required_lemmas: tuple[str, ...]
    formalized_lemmas: tuple[str, ...]
    evidence_hashes: tuple[str, ...]
    reported_axioms: tuple[str, ...]
    gaps: tuple[str, ...]
    coverage: float
    fully_verified: bool
    verification_method: str | None


def assess_formalization(
    *,
    exact_statement_sha256: str,
    required_lemmas: tuple[str, ...],
    results: Mapping[str, ToolResult],
) -> FormalizationReport:
    if not required_lemmas:
        raise ValueError("formalization requires at least one named proof obligation")
    if len(set(required_lemmas)) != len(required_lemmas):
        raise ValueError("formalization obligations must have unique names")
    formalized: list[str] = []
    evidence: list[str] = []
    axioms: list[str] = []
    gaps: list[str] = []
    methods: set[str] = set()
    for lemma in required_lemmas:
        result = results.get(lemma)
        if result is None:
            gaps.append(f"missing formal result: {lemma}")
            continue
        if result.status is not VerificationStatus.PROVEN:
            gaps.append(f"{lemma}: {result.status.value} ({result.summary})")
            continue
        if "sorryAx" in (result.metadata.get("reported_axioms") or ()):
            gaps.append(f"{lemma}: forbidden sorryAx dependency")
            continue
        formalized.append(lemma)
        evidence.extend(result.evidence_hashes)
        axioms.extend(result.metadata.get("reported_axioms") or ())
        methods.add(
            "lean" if result.tool_name == "lean_compile"
            else "z3" if result.tool_name == "z3_unsat_check"
            else "exact_computation"
        )
    coverage = len(formalized) / len(required_lemmas)
    fully_verified = coverage == 1.0 and not gaps
    method = next(iter(methods)) if fully_verified and len(methods) == 1 else None
    return FormalizationReport(
        exact_statement_sha256=exact_statement_sha256,
        required_lemmas=required_lemmas,
        formalized_lemmas=tuple(formalized),
        evidence_hashes=tuple(dict.fromkeys(evidence)),
        reported_axioms=tuple(dict.fromkeys(axioms)),
        gaps=tuple(gaps),
        coverage=coverage,
        fully_verified=fully_verified,
        verification_method=method,
    )
