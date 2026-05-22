"""Quality gate for Atlas papers before AMY treats them as accepted science."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from communication.citation_verifier import CitationVerifier
from communication.numeric_verifier import NumericVerifier


HIGH_RISK_DOMAINS = {"medicine", "medical", "clinical", "biology", "biomedical"}


@dataclass
class AtlasQualityDecision:
    passed: bool
    status: str
    marked_content: str
    reasons: list[str] = field(default_factory=list)
    numeric_result: dict[str, Any] = field(default_factory=dict)
    citation_result: dict[str, Any] = field(default_factory=dict)
    experiment_ids: list[str] = field(default_factory=list)
    support_score: float | None = None
    tool_realism_score: float | None = None
    failure_count: int | None = None
    suspicious_references: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "status": self.status,
            "reasons": self.reasons,
            "numeric_result": self.numeric_result,
            "citation_result": self.citation_result,
            "experiment_ids": self.experiment_ids,
            "support_score": self.support_score,
            "tool_realism_score": self.tool_realism_score,
            "failure_count": self.failure_count,
            "suspicious_references": self.suspicious_references,
        }


class AtlasPaperQualityGate:
    """Downgrade plausible Atlas drafts that lack evidence or provenance."""

    def __init__(
        self,
        *,
        min_support_score: float = 0.35,
        min_tool_realism_score: float = 0.60,
        max_failure_count: int = 5,
        verify_citations: bool = True,
    ):
        self.min_support_score = min_support_score
        self.min_tool_realism_score = min_tool_realism_score
        self.max_failure_count = max_failure_count
        self.verify_citations = verify_citations
        self.numeric_verifier = NumericVerifier()
        self.citation_verifier = CitationVerifier()

    def evaluate(
        self,
        *,
        paper_text: str,
        domain: str,
        atlas_result: dict[str, Any],
        experiment_ids: list[str] | None = None,
    ) -> AtlasQualityDecision:
        domain_key = (domain or "").strip().lower()
        high_risk = domain_key in HIGH_RISK_DOMAINS
        reasons: list[str] = []
        marked_content = paper_text

        found_experiment_ids = experiment_ids or self._extract_experiment_ids(paper_text)

        numeric_result = self.numeric_verifier.verify_text(
            marked_content,
            experiment_ids=found_experiment_ids,
        )
        if numeric_result.get("flagged"):
            marked_content = self.numeric_verifier.mark_flagged(
                marked_content,
                numeric_result["flagged"],
            )
            reasons.append("Numeric claims lack explicit experiment or dataset provenance")

        citation_result = self._verify_citations(marked_content)
        if citation_result.get("total", 0) > 0 and not citation_result.get("all_verified", False):
            reasons.append("One or more extracted citations could not be verified")

        if high_risk and citation_result.get("verified", 0) == 0 and not found_experiment_ids:
            reasons.append("High-risk biomedical paper has no verified citation or local experiment")

        suspicious_refs = self._find_suspicious_references(marked_content)
        if suspicious_refs:
            reasons.append("Suspicious or known hallucinated reference detected")

        support_score = self._find_number(atlas_result, "support_score")
        if support_score is not None and support_score < self.min_support_score:
            reasons.append(
                f"Atlas support_score {support_score:.3f} is below {self.min_support_score:.3f}"
            )
        elif high_risk and support_score is None:
            reasons.append("High-risk paper lacks an Atlas support_score")

        tool_realism_score = self._find_number(atlas_result, "tool_realism_score")
        if (
            tool_realism_score is not None
            and tool_realism_score < self.min_tool_realism_score
        ):
            reasons.append(
                f"Atlas tool_realism_score {tool_realism_score:.3f} is below "
                f"{self.min_tool_realism_score:.3f}"
            )

        failure_count = self._find_int(atlas_result, "failure_count")
        if failure_count is not None and failure_count > self.max_failure_count:
            reasons.append(
                f"Atlas reported {failure_count} tool failures, above {self.max_failure_count}"
            )

        score = self._find_number(atlas_result, "score")
        if score is not None and score < 7:
            reasons.append(f"Atlas review score {score:.1f}/10 is below acceptance threshold")

        passed = not reasons
        return AtlasQualityDecision(
            passed=passed,
            status="accepted" if passed else "needs_validation",
            marked_content=marked_content,
            reasons=reasons,
            numeric_result=numeric_result,
            citation_result=citation_result,
            experiment_ids=found_experiment_ids,
            support_score=support_score,
            tool_realism_score=tool_realism_score,
            failure_count=failure_count,
            suspicious_references=suspicious_refs,
        )

    def _verify_citations(self, text: str) -> dict[str, Any]:
        if not self.verify_citations:
            return {
                "total": 0,
                "verified": 0,
                "unverified": [],
                "citations": [],
                "all_verified": False,
            }
        return self.citation_verifier.verify_citations(text)

    def _extract_experiment_ids(self, text: str) -> list[str]:
        pattern = re.compile(r"`?([a-f0-9]{32})`?", re.IGNORECASE)
        seen = set()
        ids = []
        for match in pattern.finditer(text):
            value = match.group(1).lower()
            start = max(0, match.start() - 120)
            end = min(len(text), match.end() + 120)
            context = text[start:end].lower()
            if value not in seen and any(
                key in context
                for key in ("experiment", "provenance", "data availability", "reproduc")
            ):
                seen.add(value)
                ids.append(value)
        return ids

    def _find_suspicious_references(self, text: str) -> list[str]:
        flags = []
        for line in text.splitlines():
            if re.search(r"Wang R\.? et al\.? \(2024\)", line):
                flags.append(line.strip())
            elif "Optimal Biological Ordering Principles" in line:
                flags.append(line.strip())
        return flags

    def _find_number(self, data: Any, key: str) -> float | None:
        value = self._find_value(data, key)
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return None
        return None

    def _find_int(self, data: Any, key: str) -> int | None:
        value = self._find_number(data, key)
        if value is None:
            return None
        return int(value)

    def _find_value(self, data: Any, key: str) -> Any:
        if isinstance(data, dict):
            if key in data:
                return data[key]
            for value in data.values():
                found = self._find_value(value, key)
                if found is not None:
                    return found
        elif isinstance(data, list):
            for item in data:
                found = self._find_value(item, key)
                if found is not None:
                    return found
        return None
