"""Reflection Agent — structured self-review of a draft paper.

Pattern from Google AI Co-Scientist + Sakana AI Scientist v2.
The agent acts as an independent peer reviewer with a fixed rubric:
- Claims tracing: every numerical claim must trace to provenance.
- Limitations: must be explicit.
- Falsifiability: each hypothesis must have a testable criterion.
- Alternative explanations: must be considered.

This module is deterministic (regex + provenance lookup) so the A/B test
is reproducible. An LLM-backed variant can be plugged in via judge_llm=...
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class ReflectionResult:
    pass_overall: bool
    score: float                       # 0-100
    issues: list[dict] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    annotations: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def _extract_experiment_ids(md: str) -> list[str]:
    return list(dict.fromkeys(
        re.findall(r"([a-z][a-z0-9_]+_\d{8}_\d{6}(?:_[a-z0-9]+)?)", md)
    ))


def _load_provenance_text(experiment_ids: list[str], experiments_dir: Path) -> str:
    text = ""
    for eid in experiment_ids:
        prov_path = experiments_dir / eid / "provenance.json"
        if prov_path.exists():
            try:
                text += json.loads(prov_path.read_text(encoding="utf-8")).get("output_preview", "")
            except Exception:
                continue
    return text


def reflect(
    md: str,
    experiments_dir: Path | None = None,
) -> ReflectionResult:
    """Run structured self-review on paper markdown.

    Returns a ReflectionResult with score 0-100 and concrete issues.
    Issues are dicts: {"severity": "high|medium|low", "section": "...",
                       "message": "...", "suggestion": "..."}
    """
    experiments_dir = experiments_dir or (Path(__file__).resolve().parent.parent /
                                          "data" / "experiments")
    issues: list[dict] = []
    score = 100.0

    # 1. Numerical-claim grounding
    exp_ids = _extract_experiment_ids(md)
    prov_text = _load_provenance_text(exp_ids, experiments_dir)
    discussion = re.search(r"##\s*Discussion(.+?)(?=##|\Z)", md, flags=re.DOTALL | re.IGNORECASE)
    if discussion:
        numbers = re.findall(r"-?\d+\.\d+", discussion.group(1))
        def _grounded(n: str) -> bool:
            if n in prov_text:
                return True
            return bool(re.search(re.escape(n) + r"\d*", prov_text))
        unsupported = [n for n in numbers if not _grounded(n)]
        if unsupported:
            issues.append({
                "severity": "high",
                "section": "Discussion",
                "message": f"{len(unsupported)} of {len(numbers)} numerical claims in Discussion not found in provenance.",
                "suggestion": "Either remove the unsupported numbers or add the experiment that produced them.",
            })
            score -= 15 * (len(unsupported) / max(1, len(numbers)))

    # 2. Explicit limitations
    md_lower = md.lower()
    limitation_markers = [
        "limitation", "does not claim", "calibration control", "verification control",
        "without asserting novelty", "before being classified",
    ]
    if not any(m in md_lower for m in limitation_markers):
        issues.append({
            "severity": "high",
            "section": "Discussion / Conclusion",
            "message": "Paper does not explicitly state what it does NOT claim.",
            "suggestion": "Add a sentence like 'This study does not claim X because Y was not measured.'",
        })
        score -= 12

    # 3. Falsifiability of hypotheses
    test_block = re.search(r"(?:##|\*\*)\s*Testable Predictions?\s*(?:\*\*)?\s*\n(.+?)(?=##|\Z)", md, flags=re.DOTALL | re.IGNORECASE)
    if test_block:
        hypotheses = re.findall(r"H\d+\.\s+(.+?)(?=H\d+\.|\Z)", test_block.group(1), flags=re.DOTALL)
        weak = [h for h in hypotheses
                if not re.search(r"testable via|test via|measur|compar against", h.lower())]
        if weak:
            issues.append({
                "severity": "medium",
                "section": "Testable Predictions",
                "message": f"{len(weak)} hypothesis/-es lack an explicit test procedure.",
                "suggestion": "For each H, add 'Testable via: <concrete experiment>'.",
            })
            score -= 5 * len(weak)
    else:
        issues.append({
            "severity": "medium",
            "section": "After Discussion",
            "message": "No 'Testable Predictions' section found.",
            "suggestion": "Add 1-3 falsifiable predictions with explicit test procedures.",
        })
        score -= 10

    # 4. Citation freshness
    refs = re.findall(r"^\[\d+\]\s+(.+)", md, flags=re.MULTILINE)
    if refs:
        unverified = sum(1 for r in refs if "[unverified]" in r.lower())
        if unverified > 0:
            issues.append({
                "severity": "high",
                "section": "References",
                "message": f"{unverified} unverified citation(s).",
                "suggestion": "Replace with verifiable references or remove the claim that needs them.",
            })
            score -= 4 * unverified

    # 5. Statistical reporting (only flag if Statistics-ish content)
    has_stats_topic = any(w in md_lower for w in ["correlation", "distribution", "mean", "variance", "regression"])
    has_stats_reporting = any(m in md_lower for m in ["p-value", "confidence interval", "effect size", "n=", "std:"])
    if has_stats_topic and not has_stats_reporting:
        issues.append({
            "severity": "medium",
            "section": "Results / Discussion",
            "message": "Statistical content present but no p-value, CI, or effect size reported.",
            "suggestion": "Report p-values, confidence intervals, or effect sizes for each statistical comparison.",
        })
        score -= 6

    # 6. Alternative explanations
    if "alternative" not in md_lower and "could also" not in md_lower:
        issues.append({
            "severity": "low",
            "section": "Discussion",
            "message": "No alternative explanation discussed.",
            "suggestion": "Add a paragraph: 'Alternative explanations include X; we cannot rule this out because Y.'",
        })
        score -= 3

    score = max(0.0, min(100.0, score))

    suggestions = [iss["suggestion"] for iss in issues if iss["severity"] in ("high", "medium")]

    annotations = {
        "n_issues": len(issues),
        "n_high": sum(1 for i in issues if i["severity"] == "high"),
        "n_medium": sum(1 for i in issues if i["severity"] == "medium"),
        "n_low": sum(1 for i in issues if i["severity"] == "low"),
        "experiment_ids": exp_ids,
    }

    return ReflectionResult(
        pass_overall=(score >= 70 and annotations["n_high"] == 0),
        score=round(score, 2),
        issues=issues,
        suggestions=suggestions,
        annotations=annotations,
    )


def annotate_draft(md: str, result: ReflectionResult) -> str:
    """Insert a structured self-review block into the draft for transparency."""
    if not result.issues and result.pass_overall:
        block = "<!-- Reflection: passed (no issues). -->\n\n"
    else:
        lines = ["<!-- Reflection result", f"  score: {result.score}/100",
                 f"  pass: {result.pass_overall}",
                 f"  high: {result.annotations['n_high']}, medium: {result.annotations['n_medium']}, low: {result.annotations['n_low']}",
                 "-->\n"]
        if result.suggestions:
            lines.append("\n## Self-Review (Reflection Agent)\n")
            lines.append(f"Internal review score: **{result.score}/100**\n")
            lines.append("\n**Action items raised by self-review:**\n")
            for iss in result.issues:
                lines.append(f"- *[{iss['severity']}]* **{iss['section']}**: {iss['message']} → {iss['suggestion']}")
            lines.append("")
        block = "\n".join(lines) + "\n"
    return block + md


if __name__ == "__main__":
    # Self-test on a baseline paper
    import sys
    paper = sys.argv[1] if len(sys.argv) > 1 else None
    if not paper:
        from pathlib import Path
        candidates = sorted(Path("experiments/ab_test/baseline/papers").glob("*.md"))
        if not candidates:
            print("No paper to test on.")
            sys.exit(0)
        paper = str(candidates[0])
    md = Path(paper).read_text(encoding="utf-8")
    result = reflect(md)
    print(f"Paper: {paper}")
    print(f"Score: {result.score}/100  Pass: {result.pass_overall}")
    print(f"Issues:")
    for iss in result.issues:
        print(f"  [{iss['severity']}] {iss['section']}: {iss['message']}")
        print(f"    → {iss['suggestion']}")
