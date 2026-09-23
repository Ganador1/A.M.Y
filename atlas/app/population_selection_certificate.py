"""Exact, bounded diploid viability-selection tool for the native AMY loop."""
from __future__ import annotations

import copy
import json
from fractions import Fraction

from .population_selection_verifier import (
    LIMITATIONS, MAX_CERTIFICATE_BYTES, MAX_RATIONAL_BITS, MODEL, SCHEMA,
    SCOPE, SOURCE, parse_population_selection_input, verify_population_selection_certificate,
)


def _encode(value: Fraction) -> str:
    if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > MAX_RATIONAL_BITS:
        raise ValueError("rational arithmetic precision limit exceeded; request fewer generations")
    return str(value)


def produce_population_selection_certificate(request) -> dict:
    """Compute all requested steps exactly, or fail without a partial certificate.

    p_t is the allele A frequency in zygotes before selection. Adult genotype
    frequencies generally are not Hardy-Weinberg; random mating restores that
    form in the next zygotes. Viability weights are relative, not probabilities.
    """
    parameters = parse_population_selection_input(request)
    p = p0 = Fraction(parameters["p0"])
    wAA, wAa, waa = (Fraction(parameters[key]) for key in ("wAA", "wAa", "waa"))
    states, steps = [], []
    for generation in range(parameters["generations"] + 1):
        q = 1 - p
        zygotes = {"AA": p*p, "Aa": 2*p*q, "aa": q*q}
        states.append({"generation": generation, "p_A": _encode(p), "q_a": _encode(q),
                       "zygote_frequencies": {k: _encode(v) for k, v in zygotes.items()}})
        if generation == parameters["generations"]:
            break
        mean = p*p*wAA + 2*p*q*wAa + q*q*waa
        if mean <= 0:
            raise ValueError(f"zero mean viability at generation {generation}; next generation undefined")
        # Direct marginal-fitness recurrence; the verifier instead uses integer
        # genotype weights and a separate count of Mendelian allele copies.
        next_p = (p*p*wAA + p*q*wAa) / mean
        steps.append({"generation": generation, "mean_fitness": _encode(mean),
                      "adult_genotype_frequencies": {
                          "AA": _encode(zygotes["AA"]*wAA/mean),
                          "Aa": _encode(zygotes["Aa"]*wAa/mean),
                          "aa": _encode(zygotes["aa"]*waa/mean)},
                      "p_next": _encode(next_p)})
        p = next_p
        # Bound output incrementally; rational doubling must not silently
        # truncate the requested trajectory or exceed the native tool budget.
        if len(json.dumps([states, steps]).encode()) > MAX_CERTIFICATE_BYTES - 8192:
            raise ValueError("trajectory exceeds certificate byte budget; request fewer generations")
    cert = {
        "schema": SCHEMA,
        "status": "computed_exact_model_trajectory",
        "claim": SCOPE,
        "summary": {"generations": parameters["generations"], "p_initial": _encode(p0),
                    "p_final": _encode(p), "delta_p": _encode(p-p0), "scope": SCOPE},
        "model": copy.deepcopy(MODEL),
        "input": parameters,
        "trajectory": states,
        "transitions": steps,
        "arithmetic": {"kind": "exact_rational", "representation": "canonical_fraction_strings",
                       "max_rational_bits": MAX_RATIONAL_BITS},
        "sources": [SOURCE],
        "limitations": list(LIMITATIONS),
    }
    audit = verify_population_selection_certificate(cert, expected_input=parameters)
    if not audit["valid"]:
        raise ValueError("independent verifier rejected computed trajectory: " + "; ".join(audit["failures"]))
    cert["verification"] = audit
    if len(json.dumps(cert, allow_nan=False).encode()) > MAX_CERTIFICATE_BYTES:
        raise ValueError("certificate byte limit exceeded")
    return cert


def population_selection_certificate_tool(query: str) -> str:
    """Native JSON input/output wrapper, with structured errors and no I/O."""
    try:
        return json.dumps(produce_population_selection_certificate(query), allow_nan=False, separators=(",", ":"))
    except (ValueError, TypeError, OverflowError, RecursionError) as exc:
        return json.dumps({"schema": SCHEMA, "status": "error", "error": str(exc),
                           "input_format": '{"p0":"1/4","wAA":"1","wAa":"1/2","waa":"1/4","generations":4}'})


TOOL_DESCRIPTOR = {
    "name": "population_selection_certificate",
    "domain": "biology",
    "description": (
        "Compute an exact rational finite diploid viability-selection trajectory. "
        "Choose p0 in [0,1], nonnegative relative weights wAA,wAa,waa (not all zero), "
        "and integer generations 0..64. Use integer or decimal/rational strings, no float literals. "
        "Returns every zygote state and adult-selection stage, with an independent integer "
        "allele-count audit. Limits: 64-bit inputs, 4096-bit rational fields, 256 KiB output; "
        "reduce generations if a limit is reached. Infinite randomly mating population, "
        "one locus, constant viability, Mendelian segregation, no mutation/migration/drift. "
        "Exact model-instance result only; no empirical, asymptotic, universal or novelty claim."
    ),
    "function": population_selection_certificate_tool,
    "input_format": '{"p0":"1/4","wAA":"1","wAa":"1/2","waa":"1/4","generations":4}',
    "output_format": "JSON exact rational states, selection stages, explicit assumptions and independent audit",
    "evidence_grade": "real_local",
}
