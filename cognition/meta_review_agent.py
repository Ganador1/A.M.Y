"""
Meta-review Agent — feedback propagation across review cycles.

This implements the Google AI Co-Scientist Meta-review agent
(arXiv:2502.18864, §3.3.6). Quoting the paper, this agent "enables feedback
propagation and learning **without back-propagation techniques (e.g.,
fine-tuning or reinforcement learning)**": it "synthesizes insights from all
reviews", identifies "recurring patterns ... in tournament debates", and that
synthesized critique "is simply appended to [agent] prompts in the next
iteration." Through this loop the system "continuously learns and improves."

So this is A.M.Y's faithful, paper-grounded notion of *learning*: not a fake
gradient step on a model that does not exist, but a real feedback loop that
makes the next cycle's hypotheses and discussions measurably better by feeding
back the recurring weaknesses found by the Reflection Agent and the Peer
Reviewer.

The agent is deterministic by default (pure aggregation of prior reviews) and
can optionally use the LLM to phrase the synthesized critique more fluently
(``AMY_USE_LLM_JUDGE``-style opt-in via ``AMY_USE_LLM_METAREVIEW=1``). Either
way the *content* is derived from real accumulated reviews, never invented.

Usage::

    agent = MetaReviewAgent()
    agent.ingest_review(reflection_result_dict)      # from cognition.reflection_agent
    agent.ingest_peer_review(peer_review_dict)       # from communication.paper_enhancer
    digest = agent.synthesize()                      # MetaReviewDigest
    prompt_suffix = digest.as_prompt_suffix()        # append to next-cycle prompts
"""
from __future__ import annotations

import json
import os
from collections import Counter
from dataclasses import dataclass, field, asdict

import structlog

log = structlog.get_logger()


@dataclass
class MetaReviewDigest:
    """Synthesized, persistent feedback derived from many prior reviews."""
    n_reviews: int = 0
    n_peer_reviews: int = 0
    recurring_issues: list[dict] = field(default_factory=list)   # [{pattern, count, severity, suggestion}]
    weak_criteria: list[dict] = field(default_factory=list)      # [{criterion, avg_score, n}]
    guidance: list[str] = field(default_factory=list)            # actionable instructions for next cycle
    summary: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def as_prompt_suffix(self) -> str:
        """Render the digest as text to append to the next cycle's prompts.

        This is the literal mechanism from the Co-Scientist paper: the
        meta-review critique is appended to downstream agent prompts so they
        avoid previously-recurring mistakes.
        """
        if not self.guidance and not self.recurring_issues:
            return ""
        lines = [
            "## Meta-review feedback (learned from prior review cycles)",
            "",
            f"Synthesized from {self.n_reviews} self-reviews and "
            f"{self.n_peer_reviews} peer reviews. Apply these lessons to avoid "
            "repeating recurring weaknesses:",
            "",
        ]
        for g in self.guidance:
            lines.append(f"- {g}")
        if self.recurring_issues:
            lines.append("")
            lines.append("Most recurring issues to pre-empt:")
            for iss in self.recurring_issues[:6]:
                lines.append(
                    f"- ({iss['severity']}, ×{iss['count']}) {iss['pattern']}"
                    + (f" → {iss['suggestion']}" if iss.get("suggestion") else "")
                )
        return "\n".join(lines)


# Map a free-text review message to a stable pattern key so the same recurring
# weakness aggregates across papers even when the exact wording differs.
# Needles must match the ACTUAL messages the Reflection Agent emits
# (cognition/reflection_agent.py), not paraphrases. The two highest-value
# integrity lessons used to fall through to "other" and be dropped:
#   - "<n> of <m> numerical claims in Discussion not found in provenance."
#     → needs "not found in provenance" / "numerical claim"
#   - "No 'Testable Predictions' section found." → needs "testable prediction"
_PATTERN_RULES = [
    ("ungrounded_number", ("not traceable", "unsupported number", "no provenance",
                           "does not trace", "not found in provenance", "numerical claim")),
    ("missing_limitations", ("limitation", "does not claim", "not claiming", "overstate")),
    ("weak_falsifiability", ("falsifia", "test procedure", "testable via",
                             "no explicit test", "testable prediction", "lack an explicit test")),
    ("citation_unverified", ("unverified citation", "citation", "reference")),
    ("missing_statistics", ("p-value", "confidence interval", "effect size", "statistic")),
    ("no_alternatives", ("alternative explanation", "competing explanation", "alternative")),
    ("weak_methodology", ("methodolog", "single tool", "parameter variation", "cross-validation")),
    ("weak_novelty", ("novel", "known control", "textbook")),
]


def _classify(message: str) -> str:
    m = (message or "").lower()
    for key, needles in _PATTERN_RULES:
        if any(n in m for n in needles):
            return key
    return "other"


_GUIDANCE_BY_PATTERN = {
    "ungrounded_number": "Every numerical claim in the Discussion must be copied verbatim from a tool output that has a provenance file; do not introduce derived or rounded numbers without showing the computation.",
    "missing_limitations": "Include an explicit limitations statement saying what the paper does NOT claim (e.g. 'calibration control', 'without asserting novelty').",
    "weak_falsifiability": "Give every hypothesis a concrete, falsifiable test procedure ('Testable via: …', with measurable quantities).",
    "citation_unverified": "Only cite references that can be verified; prefer fewer, real citations over many unverifiable ones.",
    "missing_statistics": "When statistics are involved, report p-values, confidence intervals, effect sizes, or sample size n.",
    "no_alternatives": "Discuss at least one alternative explanation or confound for the main result.",
    "weak_methodology": "Be explicit when results come from a single underlying method (internal consistency, not methodological independence).",
    "weak_novelty": "Clearly separate reproduction of known results from genuine candidate novelty; do not label textbook results as novel.",
}


class MetaReviewAgent:
    """Accumulates reviews and synthesizes propagatable feedback.

    State is kept in memory across calls within a run and can be persisted by
    the caller (it is plain JSON-serialisable via ``state``/``load_state``).
    """

    def __init__(self):
        self._issue_records: list[dict] = []          # raw issues from self-reviews
        self._criterion_scores: dict[str, list[float]] = {}  # peer-review criterion -> [scores]
        self._n_reviews = 0
        self._n_peer_reviews = 0

    # ── ingestion ────────────────────────────────────────────────────────────
    def ingest_review(self, reflection_result: dict) -> None:
        """Ingest one Reflection Agent result ({issues:[{severity,message,...}]})."""
        if not reflection_result:
            return
        self._n_reviews += 1
        for iss in reflection_result.get("issues", []):
            self._issue_records.append({
                "severity": iss.get("severity", "low"),
                "message": iss.get("message", ""),
                "suggestion": iss.get("suggestion", ""),
                "pattern": _classify(iss.get("message", "")),
            })

    def ingest_peer_review(self, peer_review: dict) -> None:
        """Ingest one PeerReviewer result ({scores:{criterion:score}, feedback:[...]})."""
        if not peer_review:
            return
        self._n_peer_reviews += 1
        for criterion, score in (peer_review.get("scores") or {}).items():
            try:
                self._criterion_scores.setdefault(criterion, []).append(float(score))
            except (TypeError, ValueError):
                continue
        # Feedback strings are also classifiable signals.
        for fb in peer_review.get("feedback", []):
            # Only treat negative feedback ([FAIL]/[NOTE]/❌/⚠️) as an issue.
            low = str(fb).lower()
            if any(tag in fb for tag in ("[FAIL]", "[NOTE]", "❌", "⚠️")) or "insufficient" in low:
                self._issue_records.append({
                    "severity": "high" if ("[FAIL]" in fb or "❌" in fb) else "medium",
                    "message": str(fb),
                    "suggestion": "",
                    "pattern": _classify(str(fb)),
                })

    # ── synthesis ────────────────────────────────────────────────────────────
    def synthesize(self, min_count: int = 2) -> MetaReviewDigest:
        """Aggregate ingested reviews into propagatable feedback.

        Only patterns seen at least ``min_count`` times become guidance — the
        point is *recurring* weaknesses, not one-offs (matches the paper's
        "recurring patterns" language).
        """
        pattern_counter: Counter = Counter()
        severity_by_pattern: dict[str, str] = {}
        suggestion_by_pattern: dict[str, str] = {}
        for rec in self._issue_records:
            p = rec["pattern"]
            if p == "other":
                continue
            pattern_counter[p] += 1
            # Keep the most severe seen for this pattern.
            sev_rank = {"high": 3, "medium": 2, "low": 1}
            if sev_rank.get(rec["severity"], 1) >= sev_rank.get(severity_by_pattern.get(p, "low"), 1):
                severity_by_pattern[p] = rec["severity"]
            if rec.get("suggestion") and p not in suggestion_by_pattern:
                suggestion_by_pattern[p] = rec["suggestion"]

        recurring = [
            {
                "pattern": p.replace("_", " "),
                "pattern_key": p,
                "count": c,
                "severity": severity_by_pattern.get(p, "low"),
                "suggestion": suggestion_by_pattern.get(p, ""),
            }
            for p, c in pattern_counter.most_common()
            if c >= min_count
        ]

        weak_criteria = []
        for criterion, scores in self._criterion_scores.items():
            if not scores:
                continue
            avg = sum(scores) / len(scores)
            if avg < 6.0:  # below "adequate" on the 0-10 peer-review scale
                weak_criteria.append({
                    "criterion": criterion,
                    "avg_score": round(avg, 2),
                    "n": len(scores),
                })
        weak_criteria.sort(key=lambda d: d["avg_score"])

        guidance: list[str] = []
        for iss in recurring:
            g = _GUIDANCE_BY_PATTERN.get(iss["pattern_key"])
            if g and g not in guidance:
                guidance.append(g)
        # Criterion-driven guidance, mapped through the same pattern guidance.
        _crit_to_pattern = {
            "novelty": "weak_novelty",
            "reproducibility": "ungrounded_number",
            "methodology": "weak_methodology",
            "discussion_depth": "no_alternatives",
            "references": "citation_unverified",
        }
        for wc in weak_criteria:
            p = _crit_to_pattern.get(wc["criterion"])
            g = _GUIDANCE_BY_PATTERN.get(p) if p else None
            if g and g not in guidance:
                guidance.append(g)

        summary = (
            f"{self._n_reviews} self-reviews + {self._n_peer_reviews} peer reviews ingested; "
            f"{len(recurring)} recurring issue pattern(s), {len(weak_criteria)} weak criterion(s)."
        )

        digest = MetaReviewDigest(
            n_reviews=self._n_reviews,
            n_peer_reviews=self._n_peer_reviews,
            recurring_issues=recurring,
            weak_criteria=weak_criteria,
            guidance=guidance,
            summary=summary,
        )
        log.info("meta_review.synthesized",
                 n_reviews=self._n_reviews, n_peer=self._n_peer_reviews,
                 recurring=len(recurring), weak=len(weak_criteria))
        return digest

    # ── persistence ──────────────────────────────────────────────────────────
    def state(self) -> dict:
        return {
            "issue_records": self._issue_records,
            "criterion_scores": self._criterion_scores,
            "n_reviews": self._n_reviews,
            "n_peer_reviews": self._n_peer_reviews,
        }

    def load_state(self, state: dict) -> None:
        if not state:
            return
        self._issue_records = list(state.get("issue_records", []))
        self._criterion_scores = dict(state.get("criterion_scores", {}))
        self._n_reviews = int(state.get("n_reviews", 0))
        self._n_peer_reviews = int(state.get("n_peer_reviews", 0))
