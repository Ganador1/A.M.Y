"""Independent, exact verifier for a nonnegative step autocorrelation witness.

Only the standard library is used. This module neither imports nor executes
search.py. Its primary oracle sums intersections of intervals by an integer
endpoint sweep; an independent discrete correlation checks every value.

For h_i=z_i/s and t=(k+theta)*d, 0<=theta<=1,
  a(t)=d*((1-theta)*C_k + theta*C_(k+1))/s**2,
  C_k=sum_i z_i*z_(i+k).
Indeed, the overlap of two length-d cells is the triangular function
(d-abs(t-(j-i)*d))_+. Between consecutive grid lags only k and k+1
contribute. Hence a is continuous and piecewise affine, including through
the support endpoint n*d. Its minimum on [0,1] is attained at a grid lag
in that interval or at 1; evaluating just floor(1/d)*d omits a required end.
Half-open interval conventions change only sets of measure zero.

The denominator is the SQUARE of the L1 mass, (d*sum_i h_i)**2, not the L2
norm. This is autocorrelation f(x)*f(x+t), not autoconvolution f(x)*f(t-x).
Spatial scaling changes the functional because the lag interval stays [0,1].
No global record or novelty claim follows from verifying a concrete witness.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction as F
import hashlib
import json
from math import lcm
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
PUBLIC_BASELINE = HERE / "baseline.json"
BASELINE_URL = "https://raw.githubusercontent.com/techno-optimist/minimum-autocorrelation-bound/main/certs/certificate_n480.json"
PINNED_BASELINE_URL = "https://raw.githubusercontent.com/techno-optimist/minimum-autocorrelation-bound/b23f2d386eda9963e33c7531eeeb35c8f54cba37/certs/certificate_n480.json"
DEFINITION_URLS = ["https://arxiv.org/pdf/1903.08731", "https://arxiv.org/html/2511.02864v2"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rational(value, name):
    require(not isinstance(value, bool) and isinstance(value, (int, str, F)),
            f"{name} must be an exact integer or rational string")
    if isinstance(value, str):
        require(len(value) <= 256 and re.fullmatch(r"[+-]?\d+(?:/[+-]?\d+)?", value) is not None,
                f"{name} must be an integer or numerator/denominator string")
    try:
        return F(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"{name} must be a finite rational") from exc


def parse_function(document):
    require(isinstance(document, dict), "certificate must be an object")
    require(document.get("constant") == "C6.6_min_autocorrelation", "wrong mathematical functional")
    functional = document.get("functional", "")
    require(isinstance(functional, str) and functional.startswith("autocorrelation")
            and "f(x)f(x+t)" in functional, "autocorrelation definition must use f(x)f(x+t)")
    n, denominator = document.get("n"), document.get("snap_denom")
    require(isinstance(n, int) and not isinstance(n, bool) and 1 <= n <= 4096,
            "n must be an integer from 1 through 4096")
    require(isinstance(denominator, int) and not isinstance(denominator, bool) and denominator > 0,
            "snap_denom must be a positive integer")
    heights = document.get("heights_over_denom")
    require(isinstance(heights, list) and len(heights) == n, "height count must equal n")
    d = rational(document.get("d"), "d")
    require(d > 0, "cell width must be positive")
    z = []
    for item in heights:
        height = rational(item, "height")
        integer_height = height * denominator
        require(height >= 0 and integer_height.denominator == 1,
                "heights must be nonnegative integer multiples of 1/snap_denom")
        z.append(integer_height.numerator)
    require(sum(z) > 0, "L1 mass must be strictly positive")
    return z, denominator, d


def interval_overlap_integral(z, denominator, d, t):
    """Sum f(x)f(x+t) overlaps using integer endpoints, independently of C_k.

    Cell j from f(x+t) is [j*d-t,(j+1)*d-t). A two-pointer sweep enumerates
    every nonempty cell intersection. Negative shifts are supported as well.
    """
    units = lcm(d.denominator, t.denominator)
    cell = d.numerator * (units // d.denominator)
    shift = t.numerator * (units // t.denominator)
    i = j = 0
    total = 0
    while i < len(z) and j < len(z):
        left_a, right_a = i * cell, (i + 1) * cell
        left_b, right_b = j * cell - shift, (j + 1) * cell - shift
        overlap = min(right_a, right_b) - max(left_a, left_b)
        if overlap > 0:
            total += overlap * z[i] * z[j]
        if right_a <= right_b:
            i += 1
        if right_b <= right_a:
            j += 1
    return F(total, units * denominator**2)


def integer_correlations(z):
    return [sum(z[i] * z[i + k] for i in range(len(z) - k)) for k in range(len(z))] + [0]


def interpolated_correlation(correlations, denominator, d, t):
    lag = abs(t) / d
    k = lag.numerator // lag.denominator
    if k >= len(correlations) - 1:
        return F(0)
    theta = lag - k
    return d * ((1 - theta) * correlations[k] + theta * correlations[k + 1]) / denominator**2


def evaluate_function(z, denominator, d):
    """Verify all knots, t=1, every segment midpoint and symmetry exactly."""
    correlations = integer_correlations(z)
    # Past n*d the correlation is identically zero, so no extra mesh points
    # are needed if the declared support is shorter than the lag interval.
    last_knot = min(len(z), F(1) // d)
    nodes = sorted({k * d for k in range(last_knot + 1)} | {F(1)})
    values = []
    for t in nodes:
        overlap = interval_overlap_integral(z, denominator, d, t)
        require(overlap == interpolated_correlation(correlations, denominator, d, t),
                f"independent node methods disagree at t={t}")
        values.append(overlap)
    midpoint_values = []
    for index, (left, right) in enumerate(zip(nodes, nodes[1:])):
        middle = (left + right) / 2
        overlap = interval_overlap_integral(z, denominator, d, middle)
        require(overlap == (values[index] + values[index + 1]) / 2,
                f"affine interpolation check failed at t={middle}")
        require(overlap == interpolated_correlation(correlations, denominator, d, middle),
                f"independent midpoint methods disagree at t={middle}")
        midpoint_values.append((middle, overlap))
    symmetry_checks = sorted({F(0), min(d, F(1)), F(1, 3), F(1)})
    for t in symmetry_checks:
        require(interval_overlap_integral(z, denominator, d, t)
                == interval_overlap_integral(z, denominator, d, -t),
                f"autocorrelation symmetry failed at t={t}")
    mass = d * F(sum(z), denominator)
    minimum = min(values)
    return {
        "n": len(z), "snap_denom": denominator, "d": d, "support_width": len(z) * d,
        "integer_heights": z, "integer_height_sum": sum(z), "L1": mass,
        "min_autocorrelation": minimum, "exact_ratio": minimum / mass**2,
        "minimizing_nodes": [t for t, value in zip(nodes, values) if value == minimum],
        "endpoint_t1": values[-1], "endpoint_is_minimizer": values[-1] == minimum,
        "nodes_checked": len(nodes), "midpoints_checked": len(midpoint_values),
        "symmetry_checks": len(symmetry_checks),
        "all_nodes": [{"t": t, "autocorrelation": value} for t, value in zip(nodes, values)],
        "all_integer_correlations": correlations,
        "midpoint_checks_sha256": digest(midpoint_values),
    }


def verify_document(document):
    z, denominator, d = parse_function(document)
    result = evaluate_function(z, denominator, d)
    require(rational(document.get("exact_ratio"), "exact_ratio") == result["exact_ratio"],
            "declared exact_ratio disagrees with the recomputed minimum divided by L1 squared")
    for name, computed in (("L1", result["L1"]), ("min_g", result["min_autocorrelation"]),
                           ("W", result["support_width"])):
        if name in document:
            require(rational(document[name], name) == computed, f"declared {name} disagrees with the step function")
    return result


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {key: encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    return value


def digest(value):
    return hashlib.sha256(json.dumps(encode(value), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def negative_controls(document):
    checks = []
    wrong_ratio = copy.deepcopy(document)
    wrong_ratio["exact_ratio"] = str(rational(document["exact_ratio"], "exact_ratio") + 1)
    wrong_height = copy.deepcopy(document)
    wrong_height["heights_over_denom"][0] = str(
        rational(document["heights_over_denom"][0], "height") + F(1, document["snap_denom"]))
    for name, mutation in (("ratio_increased_by_one", wrong_ratio),
                           ("first_height_increased_by_one_grid_unit", wrong_height)):
        try:
            verify_document(mutation)
        except ValueError as exc:
            checks.append({"mutation": name, "rejected": True, "reason": str(exc),
                           "mutated_document_sha256": digest(mutation)})
        else:
            checks.append({"mutation": name, "rejected": False})
    require(all(check["rejected"] for check in checks), "a tampered document passed verification")
    return checks


def provenance_checks(document, baseline_sha256):
    provenance = document.get("provenance", {})
    results = {}
    if "baseline_sha256" in provenance:
        results["baseline_sha256_matches"] = provenance["baseline_sha256"] == baseline_sha256
    for key, filename in (("protocol_sha256", "protocol.json"), ("search_sha256", "search.py")):
        if key in provenance:
            path = HERE / filename
            actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
            results[key + "_matches"] = actual == provenance[key]
    return results


def audit_file(path, output_name, baseline_sha256):
    raw = path.read_bytes()
    document = json.loads(raw)
    result = verify_document(document)
    provenance = provenance_checks(document, baseline_sha256)
    report = {
        "mathematical_validation": "passed",
        "method": "exact interval-overlap sweep at every required knot and t=1, checked against integer correlation; exact midpoint interpolation checks",
        "functional": "min_{0<=t<=1} integral_R f(x)f(x+t) dx / (integral_R f(x) dx)^2",
        "scope": "Nonnegative nonzero integrable uniform step function on R; no symmetry restriction; no support<=1 restriction.",
        "claim_limit": "Verifies this concrete witness and its lower-bound value only; does not establish global optimality, novelty, or a current world record.",
        "input_path": str(path.resolve()), "input_sha256": hashlib.sha256(raw).hexdigest(),
        "input_snapshot": document, "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "public_baseline_url": BASELINE_URL, "pinned_public_baseline_url": PINNED_BASELINE_URL,
        "definition_sources": DEFINITION_URLS, "provenance_checks": provenance,
        "computed": result, "negative_controls": negative_controls(document),
    }
    (HERE / output_name).write_text(json.dumps(encode(report), indent=2, allow_nan=False) + "\n")
    summary = {"input": path.name, "status": "passed", "ratio": str(result["exact_ratio"]),
               "nodes": result["nodes_checked"], "midpoints": result["midpoints_checked"],
               "minimizing_nodes": [str(t) for t in result["minimizing_nodes"]],
               "endpoint_is_minimizer": result["endpoint_is_minimizer"],
               "negative_controls_rejected": 2, "provenance_checks": provenance}
    print(json.dumps(summary), flush=True)
    require(all(provenance.values()), "mathematical witness verified, but a recorded provenance hash mismatches")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, default=PUBLIC_BASELINE)
    args = parser.parse_args()
    baseline_sha256 = hashlib.sha256(args.baseline.read_bytes()).hexdigest()
    audit_file(args.baseline, "baseline_verification.json", baseline_sha256)
    for filename in ("width_only_candidate.json", "candidate.json"):
        path = HERE / filename
        if path.exists():
            audit_file(path, filename.removesuffix(".json") + "_verification.json", baseline_sha256)


if __name__ == "__main__":
    main()
