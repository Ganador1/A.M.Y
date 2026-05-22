"""Ranking Agent — Elo tournament for hypothesis selection.

Pattern from Google AI Co-Scientist (arXiv:2503.08979 ecosystem):
Generate N candidate hypotheses, run a pairwise Elo tournament where each
match is judged on (novelty, falsifiability, effect size, reproducibility),
and return the ranked list. The top hypothesis is the one A.M.Y commits
to deeper investigation.

Design choices:
- Deterministic given (hypotheses, judge function) — no LLM stochasticity
  in the tournament itself; the judge can be an LLM but should be seeded.
- O(N²) matches: fine for N ≤ 20 candidate hypotheses.
- K-factor decays with match count (FIDE-style) so early matches matter more.

Two judges are provided:
- `heuristic_judge`: deterministic, fast, no API calls. Default.
- `llm_judge`: async, uses OllamaCloudClient to do pairwise comparison with
  a structured prompt. Use via `run_tournament_async(..., judge=llm_judge)`.
"""
from __future__ import annotations

import asyncio
import json
import math
import os
import random
from dataclasses import dataclass, field, asdict
from typing import Callable


@dataclass
class HypothesisRecord:
    hypothesis: str
    domain: str = ""
    novelty_status: str = ""
    confidence: float = 0.5
    elo: float = 1500.0
    wins: int = 0
    losses: int = 0
    draws: int = 0
    matches: int = 0
    extra: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


def heuristic_judge(a: HypothesisRecord, b: HypothesisRecord) -> float:
    """Default deterministic judge — returns score in [0,1] favoring `a`.

    Uses cheap proxies: longer hypothesis = more specific (slight bonus),
    higher self-reported confidence wins, novelty_status ranking wins.

    Replace with an LLM-backed judge in production.
    """
    novelty_rank = {
        "candidate_novelty": 4,
        "testable_hypothesis": 3,
        "finite_computational_observation": 2,
        "observation": 1,
        "known_control": 0,
    }
    a_novelty = novelty_rank.get(a.novelty_status, 1)
    b_novelty = novelty_rank.get(b.novelty_status, 1)

    a_specificity = min(1.0, len(a.hypothesis) / 200.0)
    b_specificity = min(1.0, len(b.hypothesis) / 200.0)

    # Falsifiability proxy: presence of "test", "measur", "compar"
    def falsifiability_score(text: str) -> float:
        text = text.lower()
        markers = ["test", "measur", "compar", "predict", "falsif", "replicat"]
        return min(1.0, sum(0.2 for m in markers if m in text))

    a_falsif = falsifiability_score(a.hypothesis)
    b_falsif = falsifiability_score(b.hypothesis)

    a_score = (a_novelty * 0.4) + (a.confidence * 0.2) + (a_specificity * 0.2) + (a_falsif * 0.2)
    b_score = (b_novelty * 0.4) + (b.confidence * 0.2) + (b_specificity * 0.2) + (b_falsif * 0.2)

    total = a_score + b_score
    if total == 0:
        return 0.5
    return a_score / total


def expected_score(rating_a: float, rating_b: float) -> float:
    return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))


def _k_factor(matches: int) -> float:
    """K-factor decays with experience (FIDE-style)."""
    if matches < 5:
        return 40.0
    if matches < 15:
        return 20.0
    return 10.0


def run_tournament(
    hypotheses: list[dict] | list[HypothesisRecord],
    judge: Callable[[HypothesisRecord, HypothesisRecord], float] = heuristic_judge,
    rounds: int = 1,
    seed: int = 42,
) -> list[HypothesisRecord]:
    """Run an Elo tournament among hypotheses.

    Args:
        hypotheses: list of hypothesis dicts (with 'hypothesis', 'novelty_status', 'confidence')
                    or HypothesisRecord objects.
        judge: function(a, b) → score in [0,1] favoring a.
        rounds: how many round-robin passes (more rounds = more stable ratings).
        seed: pairing order randomness seed.

    Returns:
        hypotheses sorted by Elo descending.
    """
    records: list[HypothesisRecord] = []
    for h in hypotheses:
        if isinstance(h, HypothesisRecord):
            records.append(h)
        else:
            records.append(HypothesisRecord(
                hypothesis=h.get("hypothesis", h.get("text", "")),
                domain=h.get("domain", ""),
                novelty_status=h.get("novelty_status", ""),
                confidence=float(h.get("confidence", 0.5)),
                extra={k: v for k, v in h.items() if k not in
                       ("hypothesis", "text", "domain", "novelty_status", "confidence")},
            ))

    rng = random.Random(seed)
    n = len(records)
    if n < 2:
        return records

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for _ in range(rounds):
        rng.shuffle(pairs)
        for i, j in pairs:
            a, b = records[i], records[j]
            s_a = judge(a, b)
            e_a = expected_score(a.elo, b.elo)
            k = (_k_factor(a.matches) + _k_factor(b.matches)) / 2.0
            delta = k * (s_a - e_a)
            a.elo += delta
            b.elo -= delta
            a.matches += 1
            b.matches += 1
            if s_a > 0.55:
                a.wins += 1
                b.losses += 1
            elif s_a < 0.45:
                a.losses += 1
                b.wins += 1
            else:
                a.draws += 1
                b.draws += 1

    records.sort(key=lambda r: r.elo, reverse=True)
    return records


def select_top_k(hypotheses: list[dict], k: int = 3, seed: int = 42) -> list[dict]:
    """Convenience wrapper: run tournament, return top-K as dicts (with elo)."""
    ranked = run_tournament(hypotheses, rounds=2, seed=seed)
    out = []
    for r in ranked[:k]:
        d = {
            "hypothesis": r.hypothesis,
            "domain": r.domain,
            "novelty_status": r.novelty_status,
            "confidence": r.confidence,
            "elo": round(r.elo, 1),
            "tournament_record": f"{r.wins}W-{r.losses}L-{r.draws}D",
        }
        d.update(r.extra)
        out.append(d)
    return out


# ── LLM-backed judge ──────────────────────────────────────────────────────────

LLM_JUDGE_PROMPT = """You are an impartial scientific reviewer. You will be shown two candidate hypotheses generated from the same computational experiments. Judge which is the better hypothesis to investigate further.

Criteria (in priority order):
1. Falsifiability — the hypothesis specifies a concrete test or measurement.
2. Specificity — names quantities, ranges, thresholds, not vague claims.
3. Novelty — is this a candidate discovery, or is it a known control / textbook result?
4. Effect size — would the experiment, if successful, change scientific understanding meaningfully?
5. Reproducibility — could an independent researcher run the test?

Output strictly a JSON object: {"winner": "A" or "B", "rationale": "<one-sentence reason>", "score_a": <0-1>, "score_b": <0-1>}.

Hypothesis A:
{hyp_a}

Hypothesis B:
{hyp_b}
"""


async def llm_judge(
    a: "HypothesisRecord",
    b: "HypothesisRecord",
    client=None,
    model: str | None = None,
) -> float:
    """Async pairwise judge backed by an LLM (Ollama Cloud).

    Returns a score in [0,1] favoring `a`. Falls back to heuristic_judge
    on any LLM error so the tournament always completes.

    `client` is an OllamaCloudClient; if None, a new one is created from env.
    """
    if client is None:
        try:
            from core.ollama_client import OllamaCloudClient
            client = OllamaCloudClient()
        except Exception:
            return heuristic_judge(a, b)

    if model is None:
        model = os.getenv("AMY_RANKING_MODEL")
        if not model:
            try:
                import yaml
                cfg_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
                with open(cfg_path) as f:
                    cfg = yaml.safe_load(f)
                model = cfg.get("llm", {}).get("reasoner", {}).get("model", "qwen3:32b")
            except Exception:
                model = "qwen3:32b"

    prompt = LLM_JUDGE_PROMPT.format(hyp_a=a.hypothesis, hyp_b=b.hypothesis)
    messages = [{"role": "user", "content": prompt}]
    try:
        resp = await asyncio.wait_for(
            client.chat(model=model, messages=messages, temperature=0.0,
                        max_tokens=400, format_json=True),
            timeout=30.0,
        )
        content = resp.get("message", {}).get("content", "")
        # Strip code fences if any
        content = content.strip()
        if content.startswith("```"):
            content = content.strip("`").lstrip("json").strip()
        data = json.loads(content)
        # Honour score_a/score_b if present, else infer from winner
        sa = data.get("score_a")
        sb = data.get("score_b")
        if isinstance(sa, (int, float)) and isinstance(sb, (int, float)) and (sa + sb) > 0:
            return float(sa) / float(sa + sb)
        winner = str(data.get("winner", "")).upper()
        if winner == "A":
            return 1.0
        if winner == "B":
            return 0.0
        return 0.5
    except Exception:
        return heuristic_judge(a, b)


async def run_tournament_async(
    hypotheses,
    judge_async=None,
    rounds: int = 1,
    seed: int = 42,
    client=None,
    model: str | None = None,
) -> list:
    """Async tournament that supports an LLM-backed pairwise judge.

    When `judge_async` is None, defaults to `llm_judge` bound to the given
    client/model. Each match calls `judge_async(a, b)` and updates Elo.
    """
    if judge_async is None:
        async def _bound(a, b):
            return await llm_judge(a, b, client=client, model=model)
        judge_async = _bound

    records: list[HypothesisRecord] = []
    for h in hypotheses:
        if isinstance(h, HypothesisRecord):
            records.append(h)
        else:
            records.append(HypothesisRecord(
                hypothesis=h.get("hypothesis", h.get("text", "")),
                domain=h.get("domain", ""),
                novelty_status=h.get("novelty_status", ""),
                confidence=float(h.get("confidence", 0.5)),
                extra={k: v for k, v in h.items() if k not in
                       ("hypothesis", "text", "domain", "novelty_status", "confidence")},
            ))

    import random as _random
    rng = _random.Random(seed)
    n = len(records)
    if n < 2:
        return records

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for _ in range(rounds):
        rng.shuffle(pairs)
        for i, j in pairs:
            a, b = records[i], records[j]
            s_a = await judge_async(a, b)
            e_a = expected_score(a.elo, b.elo)
            k = (_k_factor(a.matches) + _k_factor(b.matches)) / 2.0
            delta = k * (s_a - e_a)
            a.elo += delta
            b.elo -= delta
            a.matches += 1
            b.matches += 1
            if s_a > 0.55:
                a.wins += 1
                b.losses += 1
            elif s_a < 0.45:
                a.losses += 1
                b.wins += 1
            else:
                a.draws += 1
                b.draws += 1

    records.sort(key=lambda r: r.elo, reverse=True)
    return records


if __name__ == "__main__":
    # Self-test
    samples = [
        {"hypothesis": "The data is consistent with theory.",
         "novelty_status": "known_control", "confidence": 0.9},
        {"hypothesis": "Testable: when basis set is enlarged from sto-3g to 6-31g, HOMO-LUMO gap of H2 should decrease by ≥10%; this can be measured directly and compared against literature.",
         "novelty_status": "candidate_novelty", "confidence": 0.7},
        {"hypothesis": "Stellar mass distribution follows IMF.",
         "novelty_status": "observation", "confidence": 0.6},
        {"hypothesis": "Falsifiable prediction: prime gaps around 10^9 should test the Cramer-Granville conjecture by measuring max gap / (log p)^2 across 100 samples and comparing to expected 1.0±0.2.",
         "novelty_status": "testable_hypothesis", "confidence": 0.65},
    ]
    ranked = run_tournament(samples, rounds=3)
    print(f"Tournament with {len(samples)} hypotheses, 3 rounds:")
    print()
    for i, r in enumerate(ranked, 1):
        print(f"  #{i}  Elo={r.elo:.0f}  ({r.wins}W-{r.losses}L-{r.draws}D)  [{r.novelty_status}]")
        print(f"      {r.hypothesis[:90]}")
        print()
