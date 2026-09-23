"""Independent exact audit of a finite diploid viability-selection trajectory.

This module never imports/calls the producer. Its transition oracle clears
fitness denominators and counts A copies among integer-weighted survivors.
It certifies the declared mathematical instance, not biological applicability.
"""
from __future__ import annotations

import json
import math
import re
from fractions import Fraction

SCHEMA = "amy.population_selection.diploid.v1"
MAX_INPUT_BYTES = 2048
MAX_CERTIFICATE_BYTES = 256 * 1024
MAX_INPUT_BITS = 64
MAX_RATIONAL_BITS = 4096
MAX_GENERATIONS = 64
SOURCE = "https://doi.org/10.1534/g3.116.028076"
SCOPE = "Finite exact trajectory of the declared diploid viability-selection model"
MODEL = {
    "name": "single_locus_diploid_viability_selection",
    "alleles": ["A", "a"],
    "genotypes": ["AA", "Aa", "aa"],
    "frequency_unit": "dimensionless",
    "fitness_unit": "dimensionless_relative_viability_weight",
    "time_unit": "discrete_generation",
    "state_stage": "zygotes_before_viability_selection",
    "transition_stages": ["viability_selection", "Mendelian_gametes", "random_mating"],
    "assumptions": [
        "Infinite deterministic population; no genetic drift",
        "One autosomal locus with two alleles; no mutation or migration",
        "Random mating restores Hardy-Weinberg proportions among zygotes",
        "Mendelian segregation; equal fertility of surviving genotypes",
        "Identical genotype viabilities in both sexes, constant across generations",
        "Nonnegative relative viability weights; positive mean for every executed transition",
    ],
}
LIMITATIONS = [
    "Exact arithmetic for this finite model instance, not empirical biological validation",
    "No finite-population stochasticity, frequency-dependent fitness, epistasis or environmental change",
    "No claim of asymptotic convergence, fixation probability, novelty or universal biological truth",
    "No authentication of creator; bind expected_input and the retained execution receipt externally",
]


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _object(value, limit):
    if isinstance(value, str):
        if len(value.encode("utf-8")) > limit:
            raise ValueError("JSON size limit exceeded")
        value = json.loads(value, object_pairs_hook=_pairs)
    if not isinstance(value, dict):
        raise ValueError("expected a JSON object")
    # Also bound already-decoded input, reject cycles, nonfinite numbers and
    # non-JSON types before rational parsing or large arithmetic.
    if len(json.dumps(value, allow_nan=False).encode("utf-8")) > limit:
        raise ValueError("JSON size limit exceeded")
    return value


def _keys(value, names, label):
    if not isinstance(value, dict) or set(value) != set(names):
        raise ValueError(f"{label}: missing or unexpected fields")


def _bounded(value: Fraction, bits=MAX_RATIONAL_BITS):
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > bits:
        raise ValueError("rational arithmetic precision limit exceeded")
    return value


def parse_population_selection_input(request):
    """Parse syntax only; shared with producer, not a dynamics implementation.

    JSON floating-point literals are intentionally rejected. Use decimal or
    rational strings to make the initial values exact and unambiguous.
    """
    request = _object(request, MAX_INPUT_BYTES)
    _keys(request, {"p0", "wAA", "wAa", "waa", "generations"}, "input")
    generation = request["generations"]
    if type(generation) is not int or not 0 <= generation <= MAX_GENERATIONS:
        raise ValueError(f"generations must be an integer in [0, {MAX_GENERATIONS}]")
    out = {"generations": generation}
    for key in ("p0", "wAA", "wAa", "waa"):
        raw = request[key]
        if type(raw) not in (str, int):
            raise ValueError(f"{key}: use an integer or exact decimal/rational string")
        raw = str(raw).strip()
        if len(raw) > 80 or not re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+|[0-9]+/[0-9]+)", raw):
            raise ValueError(f"{key}: invalid exact rational")
        try:
            value = _bounded(Fraction(raw), MAX_INPUT_BITS)
        except ZeroDivisionError as exc:
            raise ValueError(f"{key}: zero denominator") from exc
        if value < 0 or (key == "p0" and value > 1):
            raise ValueError(f"{key}: outside allowed nonnegative range")
        out[key] = str(value)
    if all(Fraction(out[key]) == 0 for key in ("wAA", "wAa", "waa")):
        raise ValueError("at least one viability weight must be positive")
    return out


def _rational(raw):
    # Canonical strings only: this also rejects bool, float, NaN, signed zero,
    # whitespace, nonreduced ratios and alternative spellings in a certificate.
    if type(raw) is not str or len(raw) > 2500:
        raise ValueError("certificate rationals must be bounded canonical strings")
    if not re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:/[1-9][0-9]*)?", raw):
        raise ValueError("invalid certificate rational")
    value = _bounded(Fraction(raw))
    if str(value) != raw:
        raise ValueError("noncanonical certificate rational")
    return value


def _rational_dict(value, names, expected, label):
    _keys(value, names, label)
    actual = [_rational(value[name]) for name in names]
    if actual != list(expected):
        raise ValueError(f"{label}: exact identity failed")


def _report(valid, failures, count=0):
    return {
        "valid": valid,
        "audit_kind": "independent_integer_genotype_allele_count",
        "scope": SCOPE,
        "exact_model_verified": valid,
        "transitions_verified": count,
        "scientific_truth_verified": False,
        "novelty_verified": False,
        "authenticated": False,
        "failures": failures,
    }


def verify_population_selection_certificate(certificate, *, expected_input=None) -> dict:
    """Audit every retained state and transition; ignore no narrative fields.

    expected_input optionally binds the certificate to the request actually
    executed. Without it, a wholly different but consistent instance is valid.
    A self-reported verification object is checked against the recomputed audit.
    """
    try:
        cert = _object(certificate, MAX_CERTIFICATE_BYTES)
        required = {"schema", "status", "claim", "summary", "model", "input",
                    "trajectory", "transitions", "arithmetic", "sources", "limitations"}
        if set(cert) not in (required, required | {"verification"}):
            raise ValueError("certificate: missing or unexpected fields")
        if cert["schema"] != SCHEMA or cert["status"] != "computed_exact_model_trajectory":
            raise ValueError("unsupported certificate schema/status")
        if cert["claim"] != SCOPE or cert["model"] != MODEL:
            raise ValueError("model/claim scope changed")
        if cert["limitations"] != LIMITATIONS or cert["sources"] != [SOURCE]:
            raise ValueError("source or limitation metadata changed")
        if cert["arithmetic"] != {"kind": "exact_rational", "representation": "canonical_fraction_strings",
                                  "max_rational_bits": MAX_RATIONAL_BITS}:
            raise ValueError("arithmetic metadata changed")
        # Strict JSON typing: Python considers True == 1, so also compare the
        # canonical serialization for literal model/arithmetic metadata.
        if json.dumps(cert["arithmetic"], sort_keys=True) != json.dumps(
                {"kind": "exact_rational", "representation": "canonical_fraction_strings",
                 "max_rational_bits": MAX_RATIONAL_BITS}, sort_keys=True):
            raise ValueError("invalid arithmetic metadata type")
        parameters = parse_population_selection_input(cert["input"])
        if cert["input"] != parameters:
            raise ValueError("certificate input is not canonical")
        if expected_input is not None and parameters != parse_population_selection_input(expected_input):
            raise ValueError("certificate does not match expected input")
        generations = parameters["generations"]
        states, steps = cert["trajectory"], cert["transitions"]
        if not isinstance(states, list) or len(states) != generations + 1:
            raise ValueError("trajectory must contain exactly generations+1 states")
        if not isinstance(steps, list) or len(steps) != generations:
            raise ValueError("transitions must contain exactly generations steps")
        weights = [Fraction(parameters[name]) for name in ("wAA", "wAa", "waa")]
        scale = math.lcm(*(value.denominator for value in weights))
        integer_weights = [int(value * scale) for value in weights]
        next_p = Fraction(parameters["p0"])
        for t, state in enumerate(states):
            _keys(state, {"generation", "p_A", "q_a", "zygote_frequencies"}, "state")
            if type(state["generation"]) is not int or state["generation"] != t:
                raise ValueError("state generation/order mismatch")
            p = _rational(state["p_A"])
            q = _rational(state["q_a"])
            if p != next_p or p < 0 or p > 1 or p + q != 1:
                raise ValueError("state frequency or transition binding mismatch")
            # Integer chromosome counts before selection.
            n, d = p.numerator, p.denominator
            zygote_counts = [n*n, 2*n*(d-n), (d-n)*(d-n)]
            _rational_dict(state["zygote_frequencies"], ("AA", "Aa", "aa"),
                           (Fraction(k, d*d) for k in zygote_counts), "zygotes")
            if t == generations:
                break
            step = steps[t]
            _keys(step, {"generation", "mean_fitness", "adult_genotype_frequencies", "p_next"}, "transition")
            if type(step["generation"]) is not int or step["generation"] != t:
                raise ValueError("transition generation/order mismatch")
            survivors = [k*w for k, w in zip(zygote_counts, integer_weights)]
            total = sum(survivors)
            if total <= 0:
                raise ValueError("zero mean viability: next generation undefined")
            if _rational(step["mean_fitness"]) != Fraction(total, scale*d*d):
                raise ValueError("mean fitness identity failed")
            _rational_dict(step["adult_genotype_frequencies"], ("AA", "Aa", "aa"),
                           (Fraction(k, total) for k in survivors), "adult genotypes")
            # Each AA survivor contributes 2 A copies, each Aa contributes 1.
            next_p = Fraction(2*survivors[0] + survivors[1], 2*total)
            if _rational(step["p_next"]) != next_p:
                raise ValueError("Mendelian allele-count identity failed")
        summary = cert["summary"]
        _keys(summary, {"generations", "p_initial", "p_final", "delta_p", "scope"}, "summary")
        if type(summary["generations"]) is not int or summary["generations"] != generations:
            raise ValueError("summary generation mismatch")
        if summary["scope"] != SCOPE:
            raise ValueError("summary scope changed")
        p0 = Fraction(parameters["p0"])
        if [_rational(summary[k]) for k in ("p_initial", "p_final", "delta_p")] != [p0, next_p, next_p-p0]:
            raise ValueError("summary frequency mismatch")
        audit = _report(True, [], generations)
        if "verification" in cert and json.dumps(cert["verification"], sort_keys=True) != json.dumps(audit, sort_keys=True):
            raise ValueError("embedded verification report does not match fresh audit")
        return audit
    except (ValueError, TypeError, KeyError, OverflowError, ZeroDivisionError, RecursionError) as exc:
        return _report(False, [str(exc)])
