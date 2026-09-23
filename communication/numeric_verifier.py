"""
Numeric Verifier — Detect and flag unverified numerical claims in papers.

Scientific papers must not contain invented statistics. This module:
1. Extracts numerical claims (p-values, hazard ratios, confidence intervals, etc.)
2. Checks whether each claim is backed by a provenance entry (experiment_id or dataset)
3. Flags unverified numbers with [SIMULATED — REQUIRES VALIDATION]
"""
import re
from pathlib import Path

import structlog

log = structlog.get_logger()

# Patterns for common numeric claims in biomedical/quantitative papers
NUMERIC_PATTERNS = [
    # p-values
    re.compile(r"p\s*[<>=]\s*0?\.\d+", re.IGNORECASE),
    # Hazard / Odds ratios with CI
    re.compile(r"(?:HR|OR|RR)\s*[=\s]+\d+\.?\d*\s*\(\s*95%\s*CI\s+[^)]+\)", re.IGNORECASE),
    # Median overall survival
    re.compile(r"median\s+(?:overall\s+)?survival\s+(?:of\s+)?\d+\.?\d*\s*(?:months|years?)", re.IGNORECASE),
    # Confidence intervals alone
    re.compile(r"95%\s*CI\s+\d+\.?\d*\s*[-–]\s*\d+\.?\d*", re.IGNORECASE),
    # Percentages with clinical context
    re.compile(r"\d+\.?\d*%\s+(?:response\s+rate|survival|mortality|efficacy|toxicity)", re.IGNORECASE),
]

EXPERIMENTS_DIR = Path("data/experiments")
DATASETS_DIR = Path("data/datasets")


class NumericVerifier:
    """Flag numerical claims that lack experimental provenance."""

    def extract_numeric_claims(self, text: str) -> list[str]:
        """Extract candidate numeric strings from paper text."""
        found = []
        seen = set()
        for pattern in NUMERIC_PATTERNS:
            for match in pattern.finditer(text):
                raw = match.group(0)
                if raw not in seen:
                    seen.add(raw)
                    found.append(raw)
        return found

    def has_provenance(self) -> bool:
        """Check whether any experiments or datasets exist in the provenance store."""
        experiments_exist = EXPERIMENTS_DIR.exists() and any(EXPERIMENTS_DIR.iterdir())
        datasets_exist = DATASETS_DIR.exists() and any(DATASETS_DIR.iterdir())
        return experiments_exist or datasets_exist

    def verify_text(self, text: str, experiment_ids: list[str] | None = None) -> dict:
        """
        Check numeric claims in text.
        If the paper does not explicitly cite experiment_ids or dataset URLs,
        ALL numeric claims are flagged as simulated.
        """
        claims = self.extract_numeric_claims(text)
        if not claims:
            return {"claims": [], "flagged": [], "safe": True}

        flagged = []
        safe = True

        # If experiment_ids are provided, we consider those as valid provenance.
        # Otherwise we look for explicit experiment_id mentions in the text.
        has_explicit_provenance = bool(experiment_ids)

        for claim in claims:
            idx = text.find(claim)
            if idx == -1:
                continue

            context = text[max(0, idx - 200):idx + len(claim) + 200]

            # Already marked
            if "[SIMULATED" in context:
                continue

            # Explicit experiment_id in local context
            if "experiment_" in context:
                continue

            # Explicit dataset URL in local context
            if "http" in context and ("dataset" in context.lower() or "data" in context.lower()):
                continue

            if not has_explicit_provenance:
                flagged.append(claim)
                safe = False
            else:
                # With explicit provenance, still flag high-risk clinical stats
                # unless they mention the experiment or a trial
                lower_claim = claim.lower()
                if "median overall survival" in lower_claim or "hr=" in lower_claim or "or=" in lower_claim:
                    if "clinical trial" not in context.lower():
                        flagged.append(claim)
                        safe = False

        return {"claims": claims, "flagged": flagged, "safe": safe}

    def mark_flagged(self, text: str, flagged: list[str]) -> str:
        """Append [SIMULATED — REQUIRES VALIDATION] to flagged numeric claims."""
        for claim in flagged:
            # Insert marker right after the claim if not already present
            idx = text.find(claim)
            if idx == -1:
                continue
            end = idx + len(claim)
            # Check if already marked in the immediate vicinity
            snippet = text[end:end + 50]
            if "[SIMULATED" not in snippet:
                text = text[:end] + " [SIMULATED — REQUIRES VALIDATION]" + text[end:]
        return text
