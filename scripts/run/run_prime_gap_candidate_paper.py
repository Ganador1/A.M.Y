#!/usr/bin/env python3
"""Generate a provenance-gated prime-gap residual diagnostics paper.

This script is intentionally conservative: it produces a candidate
computational observation with explicit literature boundaries, not a proof and
not a certified novelty claim.
"""
from __future__ import annotations

import hashlib
import json
import math
import time
from datetime import datetime
from pathlib import Path

import numpy as np

from core.provenance import ProvenanceManager


LIMITS = [100_000, 300_000, 1_000_000, 3_000_000, 10_000_000]
TAIL_THRESHOLDS = [1.0, 2.0, 3.0, 4.0]
PAPERS_DIR = Path("papers")


def sieve_primes(limit: int) -> np.ndarray:
    """Return all primes up to limit using a vectorized Eratosthenes sieve."""
    if limit < 2:
        return np.array([], dtype=np.int64)

    sieve = np.ones(limit + 1, dtype=bool)
    sieve[:2] = False
    max_factor = int(math.isqrt(limit))
    for n in range(2, max_factor + 1):
        if sieve[n]:
            sieve[n * n : limit + 1 : n] = False
    return np.flatnonzero(sieve).astype(np.int64)


def ks_distance_to_exp1(values: np.ndarray) -> float:
    """Kolmogorov distance between empirical CDF and Exp(1) CDF."""
    values = np.sort(values.astype(float))
    n = values.size
    if n == 0:
        return float("nan")
    theoretical = 1.0 - np.exp(-values)
    empirical_right = np.arange(1, n + 1, dtype=float) / n
    empirical_left = np.arange(0, n, dtype=float) / n
    return float(max(np.max(empirical_right - theoretical), np.max(theoretical - empirical_left)))


def linear_fit(x: list[float], y: list[float]) -> dict:
    """Fit y = slope*x + intercept and return coefficients plus R2."""
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    slope, intercept = np.polyfit(x_arr, y_arr, 1)
    pred = slope * x_arr + intercept
    ss_res = float(np.sum((y_arr - pred) ** 2))
    ss_tot = float(np.sum((y_arr - np.mean(y_arr)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot else 1.0
    return {
        "slope": float(slope),
        "intercept": float(intercept),
        "r_squared": float(r2),
    }


def summarize_prefix(limit: int, primes: np.ndarray, gaps: np.ndarray) -> dict:
    """Compute prefix statistics for gaps with left endpoint <= limit."""
    left_primes = primes[:-1]
    mask = left_primes <= limit
    selected_gaps = gaps[mask]
    selected_left = left_primes[mask]
    log_left = np.log(selected_left.astype(float))
    normalized = selected_gaps.astype(float) / log_left
    max_idx = int(np.argmax(selected_gaps))
    max_gap = int(selected_gaps[max_idx])
    max_gap_after = int(selected_left[max_idx])
    max_ratio = max_gap / (math.log(limit) ** 2)

    tail_ratios = {}
    for threshold in TAIL_THRESHOLDS:
        empirical = float(np.mean(normalized >= threshold))
        expected = math.exp(-threshold)
        tail_ratios[str(threshold)] = {
            "empirical": empirical,
            "exp1_expected": expected,
            "ratio": empirical / expected if expected else float("nan"),
        }

    residues = {}
    for residue in [0, 2, 4]:
        residues[str(residue)] = float(np.mean((selected_gaps % 6) == residue))

    return {
        "limit": limit,
        "prime_count": int(np.searchsorted(primes, limit, side="right")),
        "gap_count": int(selected_gaps.size),
        "mean_gap": float(np.mean(selected_gaps)),
        "mean_log_left_prime": float(np.mean(log_left)),
        "mean_normalized_gap": float(np.mean(normalized)),
        "variance_normalized_gap": float(np.var(normalized)),
        "ks_distance_exp1": ks_distance_to_exp1(normalized),
        "max_gap": max_gap,
        "max_gap_after_prime": max_gap_after,
        "max_gap_over_log_squared": float(max_ratio),
        "tail_ratios": tail_ratios,
        "gap_mod_6_frequencies": residues,
    }


def summarize_slab(lo: int, hi: int, primes: np.ndarray, gaps: np.ndarray) -> dict:
    """Compute local-window statistics for gaps with left endpoint in (lo, hi]."""
    left_primes = primes[:-1]
    mask = (left_primes > lo) & (left_primes <= hi)
    selected_gaps = gaps[mask]
    selected_left = left_primes[mask]
    log_left = np.log(selected_left.astype(float))
    normalized = selected_gaps.astype(float) / log_left
    return {
        "interval": [lo, hi],
        "gap_count": int(selected_gaps.size),
        "mean_normalized_gap": float(np.mean(normalized)),
        "ks_distance_exp1": ks_distance_to_exp1(normalized),
        "tail_ratio_ge_3": float(np.mean(normalized >= 3.0) / math.exp(-3.0)),
    }


def build_analysis() -> dict:
    """Run the computation and return a serializable analysis record."""
    max_limit = max(LIMITS)
    primes = sieve_primes(max_limit + 10_000)
    gaps = np.diff(primes)

    prefix_stats = [summarize_prefix(limit, primes, gaps) for limit in LIMITS]
    slab_stats = []
    previous = 10_000
    for limit in LIMITS:
        slab_stats.append(summarize_slab(previous, limit, primes, gaps))
        previous = limit

    inv_logs = [1.0 / math.log(item["limit"]) for item in prefix_stats]
    ks_values = [item["ks_distance_exp1"] for item in prefix_stats]
    tail3_values = [item["tail_ratios"]["3.0"]["ratio"] for item in prefix_stats]

    return {
        "experiment": "prime_gap_finite_range_residual_diagnostics",
        "limits": LIMITS,
        "max_limit": max_limit,
        "sieve": "vectorized Eratosthenes",
        "normalization": "gap / log(left_prime)",
        "baseline_distribution": "Exp(1), corresponding to local Cramer-style independent spacing",
        "prefix_statistics": prefix_stats,
        "slab_statistics": slab_stats,
        "fits": {
            "ks_distance_vs_inverse_log_limit": linear_fit(inv_logs, ks_values),
            "tail_ratio_ge_3_vs_inverse_log_limit": linear_fit(inv_logs, tail3_values),
        },
        "claim_status": {
            "primary_claim": "candidate_methodological_observation",
            "novelty_certified": False,
            "reason": (
                "The result is a reproducible residual diagnostic and finite-range pattern. "
                "It is not a theorem and is not certified as absent from the prime-gap literature."
            ),
        },
    }


def table_prefix(stats: list[dict]) -> str:
    lines = [
        "| N | primes <= N | mean gap | mean g/log(p) | KS vs Exp(1) | max gap | max/log^2(N) | tail ratio g/log(p)>=3 |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in stats:
        lines.append(
            "| {limit} | {prime_count} | {mean_gap:.4f} | {mean_normalized_gap:.4f} | "
            "{ks_distance_exp1:.4f} | {max_gap} | {max_gap_over_log_squared:.4f} | {tail3:.4f} |".format(
                tail3=row["tail_ratios"]["3.0"]["ratio"],
                **row,
            )
        )
    return "\n".join(lines)


def table_slabs(stats: list[dict]) -> str:
    lines = [
        "| Interval | gaps | mean g/log(p) | KS vs Exp(1) | tail ratio g/log(p)>=3 |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in stats:
        lo, hi = row["interval"]
        lines.append(
            f"| ({lo}, {hi}] | {row['gap_count']} | {row['mean_normalized_gap']:.4f} | "
            f"{row['ks_distance_exp1']:.4f} | {row['tail_ratio_ge_3']:.4f} |"
        )
    return "\n".join(lines)


def build_paper(analysis: dict, experiment_id: str, output_hash: str, script_hash: str) -> str:
    now = datetime.now().strftime("%B %d, %Y")
    prefix = analysis["prefix_statistics"]
    slabs = analysis["slab_statistics"]
    ks_fit = analysis["fits"]["ks_distance_vs_inverse_log_limit"]
    tail_fit = analysis["fits"]["tail_ratio_ge_3_vs_inverse_log_limit"]
    final = prefix[-1]

    return f"""# A Provenance-Gated Finite-Range Diagnostic for Normalized Prime-Gap Residuals

**Authors:** A.M.Y Computational Research System [1]
**Affiliation:** [1] AXIOM Atlas Platform, Autonomous Computational Research
**Date:** {now}
**Classification:** MSC 11A41 (Prime numbers), MSC 11N05 (Distribution of primes), MSC 11Y11 (Primality)
**Keywords:** prime gaps, Cramer model, finite-range diagnostics, computational number theory, provenance

---

## Abstract

We report a reproducible computational diagnostic for finite-range residuals in normalized prime gaps. Consecutive prime gaps with left endpoint p <= 10^7 were generated by a vectorized Eratosthenes sieve and normalized as g/log(p). The empirical distribution was compared with an Exp(1) baseline, which is the local independent-spacing approximation associated with Cramer-style models. The largest prefix, N=10^7, contains {final['prime_count']} primes and {final['gap_count']} gaps; it has mean normalized gap {final['mean_normalized_gap']:.4f}, Kolmogorov distance {final['ks_distance_exp1']:.4f} from Exp(1), and maximum-gap ratio max(g)/log^2(N) = {final['max_gap_over_log_squared']:.4f}. Across the tested prefixes, the Kolmogorov distance is well fit by a linear function of 1/log(N) with R^2={ks_fit['r_squared']:.4f}. This is presented as a candidate methodological observation: a compact, provenance-linked residual benchmark for detecting finite-range bias, not as a proof and not as a certified new theorem.

## Introduction

Prime gaps are a standard test case for separating computational evidence from mathematical proof. Cramer introduced an independent probabilistic model for primes [1], Granville refined this perspective by emphasizing residue-class structure [2], and recent work develops more sophisticated probabilistic models for large prime gaps [3]. Large empirical computations have already tested prime-gap and Goldbach-related formulas at scales far beyond this experiment [4]. Therefore, a small-to-moderate computation cannot honestly claim to refute or improve the known theory by itself.

The purpose of this study is narrower. We ask whether A.M.Y/Atlas can produce a fully provenance-gated finite-range diagnostic that states its claim boundaries explicitly. The candidate contribution is the workflow and residual summary: for each prefix N, compute normalized gaps g/log(p), compare their empirical distribution with Exp(1), track tail ratios, and fit the residual decay against 1/log(N). The result is useful as a regression benchmark for autonomous science generation because it rewards reproducibility and penalizes over-claiming.

## Methods

Primes were generated up to 10^7 using a vectorized sieve of Eratosthenes. For consecutive primes p_i and p_(i+1), the gap was defined as g_i = p_(i+1) - p_i and the normalized gap as x_i = g_i/log(p_i). For each prefix N in {LIMITS}, gaps with p_i <= N were summarized by mean gap, mean normalized gap, variance, maximum gap, maximum-gap ratio max(g)/log^2(N), and the Kolmogorov distance between the empirical CDF of x_i and the Exp(1) CDF.

Tail behavior was summarized by empirical ratios P(x_i >= t)/exp(-t) for t in {TAIL_THRESHOLDS}. To separate cumulative-prefix effects from local-window behavior, the same diagnostics were computed on slabs (10^4, 10^5], (10^5, 3*10^5], (3*10^5, 10^6], (10^6, 3*10^6], and (3*10^6, 10^7]. Finally, two ordinary least-squares trend fits were performed: Kolmogorov distance versus 1/log(N), and the t=3 tail ratio versus 1/log(N).

All outputs were serialized to JSON before paper generation. The provenance record stores the command output hash, the input description, execution environment, and script hash.

## Results

### Prefix Diagnostics

{table_prefix(prefix)}

### Local Slab Diagnostics

{table_slabs(slabs)}

### Residual Trend Fits

The prefix Kolmogorov distance fit against 1/log(N) has slope {ks_fit['slope']:.4f}, intercept {ks_fit['intercept']:.4f}, and R^2={ks_fit['r_squared']:.4f}. The tail-ratio fit for x >= 3 has slope {tail_fit['slope']:.4f}, intercept {tail_fit['intercept']:.4f}, and R^2={tail_fit['r_squared']:.4f}. These fits are descriptive only; they should not be extrapolated as asymptotic laws without larger-scale computation and theoretical support.

## Discussion

The diagnostics show a consistent finite-range residual between normalized prime gaps and the Exp(1) independent-spacing baseline. This is expected in broad terms because Cramer-style independence suppresses important arithmetic structure, while Granville-type and sieve-based models account for residue-class constraints [2,3]. The value of the present result is not the statement that such structure exists; that is already known. The value is the provenance-gated benchmark: every numerical claim in the table is tied to a single hashed execution record, and the paper labels the observation as candidate methodology rather than confirmed novelty.

The result also exposes an important limitation for A.M.Y/Atlas. A system can compute true statements and still produce bad science if it upgrades finite-range deviations into novelty claims. This paper therefore treats the residual trend as a falsable diagnostic: it should be rerun at 10^8 and beyond, compared against Granville/sieve-inspired null models, and checked against published maximal-gap datasets before any stronger claim is made.

## Conclusion

This study produced a reproducible finite-range prime-gap residual diagnostic up to N=10^7. The main scientific output is a candidate methodological observation: normalized gap residuals can be summarized as a compact provenance-linked benchmark for testing autonomous paper generation and for screening over-claims. No theorem is claimed, and no prime-gap novelty is certified. A publishable mathematical claim would require larger computation, comparison to established maximal-gap datasets, and a literature review deep enough to rule out prior equivalent diagnostics.

## Acknowledgments

The authors acknowledge the AXIOM Atlas computational platform for providing the research environment and provenance tooling used in this study.

## Data Availability

All computational data supporting this study are available in the local experiment record. The record contains full input metadata, complete JSON output, execution environment, and SHA-256 output hash:

- {experiment_id}: `data/experiments/{experiment_id}/provenance.json` (output SHA-256: `{output_hash}`)

The exact script used to generate the experiment is `run_prime_gap_candidate_paper.py`; script SHA-256: `{script_hash}`.

## References

[1] Cramer, H. 1936. On the order of magnitude of the difference between consecutive prime numbers. Acta Arithmetica 2, 23-46.
[2] Granville, A. 1995. Harald Cramer and the distribution of prime numbers. Scandinavian Actuarial Journal 1995(1), 12-28.
[3] Banks, W., Ford, K., and Tao, T. 2023. Large prime gaps and probabilistic models. Inventiones Mathematicae 233, 1471-1518. doi: 10.1007/s00222-023-01199-0
[4] Oliveira e Silva, T., Herzog, S., and Pardi, S. 2014. Empirical verification of the even Goldbach conjecture and computation of prime gaps up to 4*10^18. Mathematics of Computation 83(288), 2033-2060. doi: 10.1090/S0025-5718-2013-02787-1
[5] Kourbatov, A. 2014. The distribution of maximal prime gaps in Cramer's probabilistic model of primes. International Journal of Statistics and Probability 3(2), 18-29. doi: 10.48550/arXiv.1401.6959
[6] Kourbatov, A. 2019. Predicting maximal gaps in sets of primes. Mathematics 7(5), 400. doi: 10.48550/arXiv.1901.03785

## Supplementary Material

### Novelty Screen

Status: candidate methodological observation. The paper does not claim a new theorem, a disproof of Cramer's conjecture, or a new maximal-gap law. The candidate contribution is the provenance-gated residual diagnostic and the explicit downgrade of finite-range deviations to validation targets.

### Reproduction Command

```bash
.venv/bin/python run_prime_gap_candidate_paper.py
```
"""


def main() -> None:
    start = time.time()
    script_path = Path(__file__)
    script_hash = hashlib.sha256(script_path.read_bytes()).hexdigest()

    analysis = build_analysis()
    output = json.dumps(analysis, indent=2, sort_keys=True)
    duration = time.time() - start

    provenance = ProvenanceManager()
    record = provenance.record_execution(
        tool_name="prime_gap_finite_range_residual_diagnostics",
        tool_input=json.dumps({"limits": LIMITS, "normalization": "gap/log(left_prime)"}, sort_keys=True),
        tool_output=output,
        success=True,
        duration_seconds=duration,
        domain="mathematics",
        extra={
            "script": str(script_path),
            "script_sha256": script_hash,
            "claim_status": analysis["claim_status"],
        },
    )

    experiment_id = record["experiment_id"]
    exp_dir = Path("data/experiments") / experiment_id
    (exp_dir / "analysis.json").write_text(output, encoding="utf-8")

    output_hash = record["tool"]["output_hash"]
    paper = build_paper(analysis, experiment_id, output_hash, script_hash)
    PAPERS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    paper_path = PAPERS_DIR / f"Prime_Gap_Residual_Diagnostics_{timestamp}.md"
    paper_path.write_text(paper, encoding="utf-8")

    print(json.dumps({
        "paper": str(paper_path),
        "experiment_id": experiment_id,
        "provenance": str(exp_dir / "provenance.json"),
        "duration_seconds": round(duration, 3),
        "script_sha256": script_hash,
    }, indent=2))


if __name__ == "__main__":
    main()
