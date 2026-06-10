"""Discussion-only judge for A.M.Y papers.

WHY THIS EXISTS. The full rubric (`score_paper.py`) spreads 100 points across 9
dimensions, but ~65 of those points (provenance integrity, tool diversity, citation
accuracy, abstract uniqueness, reproducibility info, …) are fixed by the
experimental setup and CANNOT be moved by a learning mechanism that only rewrites
the Discussion section. So for the weights-vs-feedback ablation the full rubric is a
mostly-dead instrument: more seeds just buy a tighter null. (This was the explicit
recommendation of the adversarial verifiers in the learning-ablation experiment.)

This judge scores ONLY the Discussion section, on the five dimensions the learning
mechanisms are actually designed to move:

  1. claim_grounding   (0-25) — fraction of Discussion numbers that trace to a
                                 provenance output. Rewards the `feedback` arm's
                                 "ground every number" guidance.
  2. limitation_cover  (0-20) — explicit limitation / caveat statements. Rewards
                                 the `feedback` arm's "state what you do NOT claim".
  3. alternatives      (0-15) — competing-explanation language. Rewards `feedback`'s
                                 "consider an alternative explanation".
  4. calibration       (0-20) — hedging vs. firmness matched to whether the evidence
                                 is a known control / single-method vs. a candidate
                                 finding. Rewards the `weights` arm's stance
                                 calibration (low confidence ⇒ hedge).
  5. reasoning_depth   (0-20) — substantive multi-paragraph reasoning with explicit
                                 comparison/quantification, not boilerplate.

Total: 100 points, deterministic, no LLM (so it is free and reproducible across the
thousands of papers a high-seed ablation generates). An optional LLM judge can be
layered on later, but the deterministic judge is the primary metric here precisely
because it is cheap enough to run at n=80/arm.

Usage:
    from experiments.ab_test.scoring.score_discussion import score_discussion
    s = score_discussion(Path(md_path))   # -> DiscussionScore (s.total 0-100)
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EXPERIMENTS_DIR = REPO_ROOT / "data" / "experiments"


@dataclass
class DiscussionScore:
    paper: str
    has_discussion: bool
    claim_grounding: float       # 0-25
    limitation_cover: float      # 0-20
    alternatives: float          # 0-15
    calibration: float           # 0-20
    reasoning_depth: float       # 0-20
    total: float = 0.0
    word_count: int = 0

    def compute_total(self) -> float:
        self.total = round(
            self.claim_grounding + self.limitation_cover + self.alternatives
            + self.calibration + self.reasoning_depth, 3
        )
        return self.total

    def to_dict(self) -> dict:
        return asdict(self)


# ── helpers ───────────────────────────────────────────────────────────────────

def _extract_discussion(md: str) -> str:
    """Return the Discussion section text (same anchor the rubric uses).

    Falls back to a "Testable Predictions" / "Implications" tail if a paper put
    the hypotheses there, since those are part of the Discussion in this pipeline.
    """
    m = re.search(r"##\s*Discussion(.+?)(?=\n##\s|\Z)", md, flags=re.DOTALL | re.IGNORECASE)
    return m.group(1) if m else ""


def _extract_experiment_ids(md: str) -> list[str]:
    return list(dict.fromkeys(
        re.findall(r"([a-z][a-z0-9_-]+_\d{8}_\d{6}(?:_[a-z0-9]+)?)", md)
    ))


def _provenance_text(md: str) -> str:
    text = ""
    for eid in _extract_experiment_ids(md):
        prov = EXPERIMENTS_DIR / eid / "provenance.json"
        if prov.exists():
            try:
                text += json.loads(prov.read_text()).get("output_preview", "")
                out = prov.parent / "output.txt"
                if out.exists():
                    text += "\n" + out.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                pass
    return text


# ── dimension scorers ───────────────────────────────────────────────────────

def _score_claim_grounding(disc: str, prov_text: str) -> float:
    """25 pts: fraction of Discussion decimals that trace to provenance."""
    numbers = re.findall(r"-?\d+\.\d+", disc)
    if not numbers:
        # No quantitative claims at all is weak for a computational Discussion.
        return 12.0
    if not prov_text:
        return 6.0
    prov_numbers = []
    for c in re.findall(r"-?\d+\.\d+", prov_text):
        try:
            prov_numbers.append(float(c))
        except ValueError:
            pass

    def grounded(n: str) -> bool:
        if n in prov_text:
            return True
        if re.search(re.escape(n) + r"\d*", prov_text):
            return True
        try:
            v = float(n)
        except ValueError:
            return False
        tol = max(5e-4, abs(v) * 1e-3)
        return any(abs(v - r) <= tol for r in prov_numbers)

    ratio = sum(1 for n in numbers if grounded(n)) / len(numbers)
    return round(25.0 * ratio, 3)


_LIMITATION_MARKERS = [
    "limitation", "does not claim", "do not claim", "not claiming", "cannot conclude",
    "cannot rule out", "caveat", "finite-range", "finite sample", "single method",
    "internal consistency", "not methodological independence", "without asserting",
    "calibration control", "not a novel", "not novel", "should be interpreted with",
    "preliminary", "underpowered", "insufficient to",
]


def _score_limitation_cover(disc: str) -> float:
    """20 pts: explicit limitation / boundary statements.

    Asymptotic (1 - e^(-hits/3.5)) rather than a step table: the old table gave
    20/20 at just 4 marker hits, which bunched good papers against the cap and
    mechanized Δ in the learning ablation (ceiling artifact flagged by the
    adversarial verifiers). Now 4 hits ≈ 13.6, 8 ≈ 17.9 — the top decompresses
    and 20 is an asymptote, not a reachable plateau.
    """
    import math
    low = disc.lower()
    hits = sum(1 for m in _LIMITATION_MARKERS if m in low)
    return round(20.0 * (1.0 - math.exp(-hits / 3.5)), 3)


_ALT_MARKERS = [
    "alternative explanation", "alternatively", "competing explanation",
    "another explanation", "could also be explained", "rather than",
    "as opposed to", "confound", "artifact", "rounding", "floating-point",
    "other interpretation", "may instead", "might instead", "could instead",
]


def _score_alternatives(disc: str) -> float:
    """15 pts: considers competing explanations / confounds (asymptotic)."""
    import math
    low = disc.lower()
    hits = sum(1 for m in _ALT_MARKERS if m in low)
    return round(15.0 * (1.0 - math.exp(-hits / 2.5)), 3)


_HEDGE = ["may ", "might ", "could ", "suggest", "appears", "provisional", "tentative",
          "consistent with", "likely", "possibly", "potential", "would require",
          "pending", "not yet", "remains to be", "candidate"]
_FIRM = ["demonstrates", "proves", "confirms decisively", "establishes that",
         "definitively", "clearly shows that", "we have shown", "is novel",
         "breakthrough", "unprecedented", "first-ever", "conclusively"]
# Signals that the evidence is weak / control-like, so hedging is APPROPRIATE.
_WEAK_EVIDENCE = ["known", "textbook", "reproduc", "control", "single", "finite",
                  "verification", "consistent with", "expected"]


def _score_calibration(disc: str) -> float:
    """20 pts: stance matched to evidence strength.

    A Discussion grounded in known/control/finite results SHOULD hedge and avoid
    overclaiming novelty. We reward hedging, penalise unsupported firm/grandiose
    language, and give a bonus when the text explicitly ties its stance to the
    evidence being a control/known result (which is what the `weights` calibration
    signal nudges).
    """
    low = disc.lower()
    if not low.strip():
        return 0.0
    hedge = sum(low.count(h) for h in _HEDGE)
    firm = sum(low.count(f) for f in _FIRM)
    weak_ev = sum(1 for w in _WEAK_EVIDENCE if w in low)

    import math
    score = 9.0  # neutral baseline
    # Reward appropriate hedging — asymptotic, so it can't be farmed to the cap.
    score += 6.0 * (1.0 - math.exp(-hedge / 5.0))
    # Penalise grandiose/overclaiming language, especially when evidence is weak.
    score -= min(10.0, firm * (3.0 if weak_ev else 1.5))
    # Bonus for explicitly framing results as controls/known when they are.
    if weak_ev and any(p in low for p in ("not a novel", "not novel", "known result",
                                          "reproduc", "control", "internal consistency")):
        score += 2.5
    return round(max(0.0, min(20.0, score)), 3)


def _score_reasoning_depth(disc: str) -> float:
    """20 pts: substantive, structured reasoning rather than boilerplate."""
    if not disc.strip():
        return 0.0
    words = len(disc.split())
    paragraphs = [p for p in re.split(r"\n\s*\n", disc.strip()) if len(p.split()) > 15]
    # Comparison / quantification markers indicate real analysis.
    analysis_markers = ["compared", "relative to", "ratio", "deviation", "versus",
                        "vs.", "whereas", "however", "because", "therefore", "implies",
                        "%", "≈", "within", "exceeds", "below", "above"]
    n_analysis = sum(1 for m in analysis_markers if m.lower() in disc.lower())

    import math
    # Slower saturation across the board so the top of the scale keeps headroom:
    # ~640 words, ~5 substantive paragraphs, ~10 analysis markers to approach max.
    word_score = 8.0 * (1.0 - math.exp(-words / 320.0))
    para_score = 6.0 * (1.0 - math.exp(-len(paragraphs) / 2.5))
    analysis_score = 6.0 * (1.0 - math.exp(-n_analysis / 4.0))
    return round(word_score + para_score + analysis_score, 3)


def score_discussion(paper_path: Path) -> DiscussionScore:
    """Score ONLY the Discussion section of a paper. 0-100."""
    md = Path(paper_path).read_text(encoding="utf-8", errors="ignore")
    disc = _extract_discussion(md)
    prov_text = _provenance_text(md)

    score = DiscussionScore(
        paper=Path(paper_path).name,
        has_discussion=bool(disc.strip()),
        claim_grounding=_score_claim_grounding(disc, prov_text),
        limitation_cover=_score_limitation_cover(disc),
        alternatives=_score_alternatives(disc),
        calibration=_score_calibration(disc),
        reasoning_depth=_score_reasoning_depth(disc),
        word_count=len(disc.split()),
    )
    score.compute_total()
    return score


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        s = score_discussion(Path(p))
        print(f"{s.total:6.2f}  {s.paper}")
        print(f"   grounding={s.claim_grounding} limitations={s.limitation_cover} "
              f"alternatives={s.alternatives} calibration={s.calibration} "
              f"depth={s.reasoning_depth} words={s.word_count}")
