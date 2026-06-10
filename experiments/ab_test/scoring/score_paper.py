"""Objective scoring rubric for A.M.Y papers.

Designed to be deterministic and reproducible — no LLM judge, no humans.
Each metric is computable from the paper markdown + linked provenance files.

Total: 100 points, 9 dimensions.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from dataclasses import dataclass, asdict


REPO_ROOT = Path(__file__).resolve().parents[3]
EXPERIMENTS_DIR = REPO_ROOT / "data" / "experiments"


@dataclass
class PaperScore:
    paper: str
    domain: str
    provenance_integrity: float        # 0-10
    tool_diversity: float              # 0-10
    falsifiability: float              # 0-15
    explicit_limitations: float        # 0-10
    numerical_claims_grounded: float   # 0-15
    citation_accuracy: float           # 0-10
    abstract_uniqueness: float         # 0-10
    statistical_rigor: float           # 0-10
    reproducibility_info: float        # 0-10
    total: float = 0.0

    def compute_total(self):
        self.total = (
            self.provenance_integrity + self.tool_diversity + self.falsifiability
            + self.explicit_limitations + self.numerical_claims_grounded
            + self.citation_accuracy + self.abstract_uniqueness
            + self.statistical_rigor + self.reproducibility_info
        )
        return self.total


# ── Metric implementations ────────────────────────────────────────────────────

def _extract_experiment_ids(md: str) -> list[str]:
    """Pick experiment IDs referenced anywhere in the manuscript.

    IDs look like: '<domain>_<tool_words>_<YYYYMMDD>_<HHMMSS>' with an optional
    trailing `_<digits>` or `_<hex>` suffix. We are permissive on the suffix
    because different generators use different schemes.
    """
    ids = re.findall(
        r"([a-z][a-z0-9_-]+_\d{8}_\d{6}(?:_[a-z0-9]+)?)",
        md,
    )
    return list(dict.fromkeys(ids))


def score_provenance_integrity(md: str) -> float:
    """10 pts: SHA-256 hashes in paper match the provenance.json files."""
    exp_ids = _extract_experiment_ids(md)
    if not exp_ids:
        return 0.0
    paper_hashes = dict(re.findall(r"- ([a-z][a-z0-9_-]+_\d{8}_\d{6}(?:_[a-z0-9]+)?):[^\n]*?\(output SHA-256:\s*`([a-f0-9]{64})`\)", md))
    if not paper_hashes:
        return 0.0
    matching = 0
    total = 0
    for eid, claimed_hash in paper_hashes.items():
        prov_path = EXPERIMENTS_DIR / eid / "provenance.json"
        if not prov_path.exists():
            continue
        try:
            recorded = json.loads(prov_path.read_text()).get("tool", {}).get("output_hash", "")
            total += 1
            if recorded.lower() == claimed_hash.lower():
                matching += 1
        except Exception:
            continue
    return 10.0 * (matching / total) if total else 0.0


def score_tool_diversity(md: str) -> float:
    """10 pts: rewards both (a) variety of tools and (b) coverage of distinct inputs.

    Pure unique/total ratio is misleading: 3 different cosmology distances at
    z=0.1/1/10 are 3 distinct *measurements*, not redundant calls. We score:
      - tool variety  : unique tools / max(3, unique_tools_expected)  → up to 6 pts
      - input variety : unique (tool,input) pairs / total calls       → up to 4 pts
    """
    tool_blocks = re.findall(
        r"\*\*Tool:\*\*\s*`?([a-z_0-9]+)`?\s*\n\*\*Input:\*\*\s*`?([^`\n]+)`?",
        md,
        flags=re.IGNORECASE,
    )
    if not tool_blocks:
        tools = re.findall(r"\*\*Tool:\*\*\s*`?([a-z_0-9]+)`?", md, flags=re.IGNORECASE)
        if not tools:
            provenance_tools = re.findall(r"\btool:\s*([a-z_0-9-]+)", md, flags=re.IGNORECASE)
            if not provenance_tools:
                for eid in _extract_experiment_ids(md):
                    prov_path = EXPERIMENTS_DIR / eid / "provenance.json"
                    if not prov_path.exists():
                        continue
                    try:
                        tool_name = json.loads(prov_path.read_text()).get("tool", {}).get("name")
                    except Exception:
                        tool_name = None
                    if tool_name:
                        provenance_tools.append(str(tool_name))
            if provenance_tools:
                unique = len(set(provenance_tools))
                return min(6.0, 5.0 + unique)
            if "provenance.json" in md and "data/experiments/" in md:
                return 4.0
            return 0.0
        unique = len(set(tools))
        return min(6.0, 6.0 * unique / max(3, len(tools)))

    tools = [t for t, _ in tool_blocks]
    pairs = list(set(tool_blocks))
    n_total = len(tool_blocks)
    n_unique_tools = len(set(tools))
    n_unique_pairs = len(pairs)

    tool_score = min(6.0, 6.0 * n_unique_tools / max(3, min(n_total, 6)))
    input_score = 4.0 * (n_unique_pairs / n_total)
    return round(tool_score + input_score, 2)


def score_falsifiability(md: str) -> float:
    """15 pts: explicit testable hypotheses with falsification criterion."""
    test_block = re.search(r"(?:#{2,3}|\*\*)\s*Testable Predictions?\s*(?:\*\*)?\s*\n(.+?)(?=#{2,3}|\Z)", md, flags=re.DOTALL | re.IGNORECASE)
    if not test_block:
        return 0.0
    block = test_block.group(1)
    hypotheses = re.findall(r"\*?\*?H\d+\.?\*?\*?\s+(.+?)(?=\*?\*?H\d+\.|\Z)", block, flags=re.DOTALL)
    if not hypotheses:
        hypotheses = re.findall(
            r"(?:^|\n)\s*(?:First|Second|Third|Fourth|Fifth),\s+(.+?)(?=\n\s*(?:First|Second|Third|Fourth|Fifth),|\Z)",
            block,
            flags=re.DOTALL | re.IGNORECASE,
        )
    if not hypotheses:
        return 0.0
    score = 0.0
    for h in hypotheses[:5]:
        h_lower = h.lower()
        pts = 1.0
        if "testable via" in h_lower or "test via" in h_lower or "falsifiable" in h_lower or "testable:" in h_lower:
            pts += 1.0
        if re.search(r"confidence:\s*\d+%", h, flags=re.IGNORECASE) or re.search(r"elo:\s*\d+", h_lower):
            pts += 1.0
        score += pts
    return min(15.0, score)


def score_explicit_limitations(md: str) -> float:
    """10 pts: presence and number of explicit limitations."""
    md_lower = md.lower()
    limitation_markers = [
        "limitation", "does not claim", "does not assert", "not assert",
        "should not be treated", "calibration control", "verification control",
        "without asserting novelty", "before being classified as",
        "must be quantified", "should be compared against",
    ]
    hits = sum(md_lower.count(m) for m in limitation_markers)
    if hits == 0:
        return 0.0
    if hits >= 5:
        return 10.0
    return 2.0 * hits


def score_numerical_claims_grounded(md: str) -> float:
    """15 pts: numbers in the body that appear in linked provenance outputs."""
    exp_ids = _extract_experiment_ids(md)
    if not exp_ids:
        return 0.0
    provenance_text = ""
    for eid in exp_ids:
        prov_path = EXPERIMENTS_DIR / eid / "provenance.json"
        if prov_path.exists():
            try:
                provenance_text += json.loads(prov_path.read_text()).get("output_preview", "")
                output_path = prov_path.parent / "output.txt"
                if output_path.exists():
                    provenance_text += "\n" + output_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                pass
    if not provenance_text:
        return 0.0
    discussion = re.search(r"##\s*Discussion(.+?)(?=##|\Z)", md, flags=re.DOTALL | re.IGNORECASE)
    abstract = re.search(r"##\s*Abstract(.+?)(?=##|\Z)", md, flags=re.DOTALL | re.IGNORECASE)
    text_to_check = (discussion.group(1) if discussion else "") + (abstract.group(1) if abstract else "")
    numbers = re.findall(r"-?\d+\.\d+", text_to_check)
    if not numbers:
        return 7.0
    # A number is grounded if it appears in provenance text, OR if a longer
    # version of it appears (e.g. "5.5" is grounded by "5.5000").
    provenance_numbers = []
    for candidate in re.findall(r"-?\d+\.\d+", provenance_text):
        try:
            provenance_numbers.append(float(candidate))
        except ValueError:
            pass

    def _grounded(n: str) -> bool:
        if n in provenance_text:
            return True
        # Allow truncation: search for n followed by digits or a non-numeric boundary.
        if re.search(re.escape(n) + r"\d*", provenance_text):
            return True
        try:
            value = float(n)
        except ValueError:
            return False
        tolerance = max(5e-4, abs(value) * 1e-3)
        return any(abs(value - recorded) <= tolerance for recorded in provenance_numbers)
    grounded = sum(1 for n in numbers if _grounded(n))
    ratio = grounded / len(numbers)
    return 15.0 * ratio


def score_citation_accuracy(md: str) -> float:
    """10 pts: citations not marked as unverified."""
    refs = re.findall(r"^\[\d+\]\s+(.+)", md, flags=re.MULTILINE)
    if not refs:
        return 5.0
    unverified = sum(1 for r in refs if "unverified" in r.lower() or "[unverified]" in r.lower())
    if len(refs) == 0:
        return 0.0
    return 10.0 * (1 - unverified / len(refs))


def score_abstract_uniqueness(md: str, peer_abstracts: list[str]) -> float:
    """10 pts: lower Jaccard similarity to peer abstracts = higher score."""
    abstract_match = re.search(r"##\s*Abstract\s*(.+?)(?=##)", md, flags=re.DOTALL | re.IGNORECASE)
    if not abstract_match:
        return 0.0
    abstract = abstract_match.group(1).lower()
    tokens = set(re.findall(r"[a-z]{4,}", abstract))
    if not tokens or not peer_abstracts:
        return 10.0
    similarities = []
    for peer in peer_abstracts:
        peer_tokens = set(re.findall(r"[a-z]{4,}", peer.lower()))
        if not peer_tokens:
            continue
        jaccard = len(tokens & peer_tokens) / len(tokens | peer_tokens)
        similarities.append(jaccard)
    if not similarities:
        return 10.0
    avg_similarity = sum(similarities) / len(similarities)
    return 10.0 * (1 - avg_similarity)


def score_statistical_rigor(md: str) -> float:
    """10 pts: presence of statistical reporting (p-value, CI, effect size, n=...)."""
    md_lower = md.lower()
    markers = {
        "p-value": 2.5, "p =": 1.5, "p=": 1.5, "p<": 1.5,
        "confidence interval": 2.5, "95% ci": 2.5, "ci:": 1.0,
        "effect size": 2.5, "cohen's d": 2.0, "cohen dz": 2.0,
        "n=": 1.0, "sample size": 1.0,
        "standard deviation": 1.0, "std:": 1.0,
        "pearson": 1.0, "spearman": 1.0,
        "t-statistic": 1.5, "f-statistic": 1.5,
    }
    score = 0.0
    for marker, pts in markers.items():
        if marker in md_lower:
            score += pts
    return min(10.0, score)


def score_reproducibility_info(md: str) -> float:
    """10 pts: env, seeds, versions, hashes documented."""
    md_lower = md.lower()
    score = 0.0
    if "python" in md_lower and re.search(r"python\s*3\.\d", md_lower):
        score += 2.0
    if "apple silicon" in md_lower or "x86" in md_lower or "platform" in md_lower:
        score += 1.5
    if "sha-256" in md_lower or "sha256" in md_lower:
        score += 2.5
    if "provenance" in md_lower:
        score += 2.0
    if "data availability" in md_lower:
        score += 2.0
    return min(10.0, score)


def score_paper(paper_path: Path, peer_abstracts: list[str] | None = None) -> PaperScore:
    md = paper_path.read_text(encoding="utf-8", errors="ignore")
    domain_match = re.search(r"(machine-learning|astronomy|biology|chemistry|physics|mathematics|statistics|climate|materials|engineering)",
                              md, flags=re.IGNORECASE)
    domain = domain_match.group(1).lower() if domain_match else "unknown"

    score = PaperScore(
        paper=paper_path.name,
        domain=domain,
        provenance_integrity=score_provenance_integrity(md),
        tool_diversity=score_tool_diversity(md),
        falsifiability=score_falsifiability(md),
        explicit_limitations=score_explicit_limitations(md),
        numerical_claims_grounded=score_numerical_claims_grounded(md),
        citation_accuracy=score_citation_accuracy(md),
        abstract_uniqueness=score_abstract_uniqueness(md, peer_abstracts or []),
        statistical_rigor=score_statistical_rigor(md),
        reproducibility_info=score_reproducibility_info(md),
    )
    score.compute_total()
    return score


def score_directory(papers_dir: Path) -> list[PaperScore]:
    paper_files = sorted(papers_dir.glob("*.md"))
    abstracts = []
    for p in paper_files:
        m = re.search(r"##\s*Abstract\s*(.+?)(?=##)", p.read_text(errors="ignore"), flags=re.DOTALL | re.IGNORECASE)
        if m:
            abstracts.append(m.group(1))
    results = []
    for p in paper_files:
        peer_abs = [a for i, a in enumerate(abstracts) if i != paper_files.index(p)]
        results.append(score_paper(p, peer_abs))
    return results


if __name__ == "__main__":
    import sys
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO_ROOT / "papers"
    print(f"Scoring papers in: {target}")
    results = score_directory(target)
    if not results:
        print("No papers found.")
        sys.exit(1)

    print(f"\n{'paper':60s} {'domain':12s} {'total':>6s}")
    print("-" * 80)
    for r in results:
        print(f"{r.paper[:60]:60s} {r.domain[:12]:12s} {r.total:6.2f}")

    avg_total = sum(r.total for r in results) / len(results)
    print("-" * 80)
    print(f"{'AVERAGE':60s} {'':12s} {avg_total:6.2f}")
    print(f"\nBy dimension (averages):")
    for field in ["provenance_integrity", "tool_diversity", "falsifiability",
                  "explicit_limitations", "numerical_claims_grounded",
                  "citation_accuracy", "abstract_uniqueness",
                  "statistical_rigor", "reproducibility_info"]:
        avg = sum(getattr(r, field) for r in results) / len(results)
        print(f"  {field:30s} {avg:5.2f}")
