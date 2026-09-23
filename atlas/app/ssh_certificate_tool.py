"""Bounded JSON adapter for exact finite SSH gap certificates.

Rationals in a certificate are [numerator_hex, denominator_hex] pairs. To
verify a saved result offline, decode its ``certificate`` with
``decode_gap_certificate`` and pass it to ``verify_gap_certificate`` from
ssh_spectral_certificate. SHA-256 binds the recorded input; it does not
establish the origin of physical measurements or scientific novelty.
"""
from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
import re

from .ssh_spectral_certificate import (
    certified_gap_squared,
    classify_gap_threshold,
    verify_gap_certificate,
)

_MAX_INPUT_BYTES = 65536
_MAX_OUTPUT_BYTES = 49152
_MAX_RATIONAL_BITS = 128
_ENCODING = "hex_numerator_denominator_pairs"
_SCALAR_FIELDS = ("gap_squared_lower", "gap_squared_upper")
_VECTOR_FIELDS = ("hoppings", "witness")
_RATIONAL_PATTERN = re.compile(r"[+-]?(?:\d+/\d+|(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)")


def _canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha256(value) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate option: {key}")
        result[key] = value
    return result


def _rational(value, name: str, *, allow_zero: bool = False) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ValueError(f"{name} must be an exact rational number or rational string")
    token = str(value).strip()
    if len(token) > 128:
        raise ValueError(f"{name} rational token exceeds 128 characters")
    if _RATIONAL_PATTERN.fullmatch(token) is None:
        raise ValueError(f"{name} must be an integer, decimal or numerator/denominator rational")
    # Bound exponent expansion before Fraction constructs a potentially huge int.
    match = re.search(r"[eE]([+-]?\d+)$", token)
    if match and abs(int(match.group(1))) > 128:
        raise ValueError(f"{name} decimal exponent exceeds 128")
    try:
        rational = Fraction(token)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError(f"{name} must be a finite rational") from exc
    if rational < 0 or (rational == 0 and not allow_zero):
        raise ValueError(f"{name} must be {'non-negative' if allow_zero else 'positive'}")
    if max(rational.numerator.bit_length(), rational.denominator.bit_length()) > _MAX_RATIONAL_BITS:
        raise ValueError(f"{name} numerator and denominator must fit in 128 bits")
    return rational


def _encode_rational(value: Fraction) -> list[str]:
    return [hex(value.numerator), hex(value.denominator)]


def decode_gap_certificate(certificate: dict) -> dict:
    """Decode the exact hex fields of a saved tool certificate for verification."""
    if not isinstance(certificate, dict) or certificate.get("encoding") != _ENCODING:
        raise ValueError("unsupported SSH certificate encoding")

    def decode(pair):
        if not isinstance(pair, list) or len(pair) != 2 or not all(isinstance(x, str) for x in pair):
            raise ValueError("expected [numerator_hex, denominator_hex]")
        return Fraction(int(pair[0], 16), int(pair[1], 16))

    result = {name: certificate[name] for name in ("method", "scope")}
    result.update({name: decode(certificate[name]) for name in _SCALAR_FIELDS})
    result.update({name: [decode(value) for value in certificate[name]] for name in _VECTOR_FIELDS})
    return result


def _approximation(value: Fraction) -> float | None:
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except OverflowError:
        return None


def _serialize_certificate(exact, *, iterations, threshold, strategy_requested="float", strategy_used="float"):
    if not verify_gap_certificate(exact):
        raise ValueError("internal exact certificate verification failed")
    certificate = {
        "encoding": _ENCODING,
        "method": exact["method"],
        "scope": exact["scope"],
        **{name: _encode_rational(exact[name]) for name in _SCALAR_FIELDS},
        **{name: [_encode_rational(value) for value in exact[name]] for name in _VECTOR_FIELDS},
    }
    output = {
        "success": True,
        "tool": "ssh_gap_certificate",
        "schema_version": 1,
        "site_count": len(exact["hoppings"]) + 1,
        "iterations": iterations,
        "certificate": certificate,
        "certificate_sha256": _sha256(certificate),
        "hoppings_sha256": _sha256(certificate["hoppings"]),
        "approximations": {
            "certified": False,
            "warning": "Rounded display only; zero can mean underflow. Use exact squared bounds for decisions.",
            **{name: _approximation(exact[name]) for name in _SCALAR_FIELDS},
        },
        "scope_notes": [
            "Finite open even chain, strictly positive rational hoppings, exactly zero onsite energies.",
            "Gap is the half-filling spectral gap; units are inherited from the supplied hoppings.",
            "No certificate for diagonal disorder, measurement uncertainty, topology or an infinite-system limit.",
            "Applies known Collatz-Wielandt inequalities; does not establish scientific novelty.",
        ],
    }
    if strategy_requested == "auto":
        output["strategy_requested"] = strategy_requested
        output["strategy_used"] = strategy_used
    if threshold is not None:
        output["threshold"] = {
            "value": _encode_rational(threshold),
            "encoding": _ENCODING,
            "quantity": "gap (not gap squared)",
            "verdict": classify_gap_threshold(exact, threshold),
        }
    return _canonical_json(output)


def _candidate_certificates(hoppings, iterations, strategy):
    yield "float", certified_gap_squared(hoppings, iterations=iterations)
    if strategy == "auto":
        from .ssh_column_witness import column_witness_candidates

        for name, witness in column_witness_candidates(hoppings):
            # The witness alone is a lower bound on the full response size.
            # Avoid costly exact sweeps for proposals that cannot fit anyway.
            encoded_witness = _canonical_json([_encode_rational(value) for value in witness])
            if len(encoded_witness.encode("utf-8")) <= _MAX_OUTPUT_BYTES:
                yield name, certified_gap_squared(hoppings, witness=witness)


def ssh_gap_certificate(query: str) -> str:
    """Return lossless JSON, or a concise Atlas-compatible ``Error:`` response."""
    try:
        if not isinstance(query, str) or len(query.encode("utf-8")) > _MAX_INPUT_BYTES:
            raise ValueError("input must be a JSON string of at most 65536 bytes")
        request = json.loads(query, parse_float=str, object_pairs_hook=_unique_object)
        if not isinstance(request, dict):
            raise ValueError("input must be a JSON object")
        unknown = set(request) - {"hoppings", "threshold", "iterations", "strategy"}
        if unknown:
            raise ValueError("unknown options: " + ", ".join(sorted(unknown)))
        raw_hoppings = request.get("hoppings")
        if not isinstance(raw_hoppings, list) or not 3 <= len(raw_hoppings) <= 511 or len(raw_hoppings) % 2 != 1:
            detail = (
                f" Received {len(raw_hoppings)} hoppings, describing {len(raw_hoppings) + 1} sites."
                if isinstance(raw_hoppings, list) else ""
            )
            raise ValueError(
                "hoppings must be an odd-length list with 3 to 511 entries. "
                "For this open even chain, site_count = len(hoppings) + 1."
                + detail
            )
        hoppings = [_rational(value, "hoppings") for value in raw_hoppings]
        iterations = request.get("iterations", 4)
        if isinstance(iterations, bool) or not isinstance(iterations, int) or not 0 <= iterations <= 100:
            raise ValueError("iterations must be an integer in [0, 100]")
        threshold = _rational(request["threshold"], "threshold", allow_zero=True) if "threshold" in request else None
        strategy = request.get("strategy", "float")
        if not isinstance(strategy, str) or strategy not in ("float", "auto"):
            raise ValueError("strategy must be 'float' or 'auto'")

        best_serialized = None
        best_width = None
        for name, exact in _candidate_certificates(hoppings, iterations, strategy):
            serialized = _serialize_certificate(
                exact, iterations=iterations, threshold=threshold,
                strategy_requested=strategy, strategy_used=name,
            )
            if len(serialized.encode("utf-8")) > _MAX_OUTPUT_BYTES:
                continue
            # Relative width is compared exactly; subtracting one would not
            # change its ordering. Each candidate retains its own full witness.
            width = exact["gap_squared_upper"] / exact["gap_squared_lower"]
            if best_width is None or width < best_width:
                best_serialized, best_width = serialized, width
        if best_serialized is None:
            raise ValueError("exact certificate exceeds the 49152-byte Atlas response budget; use fewer or simpler hoppings")
        return best_serialized
    except (ValueError, TypeError, OverflowError, RecursionError) as exc:
        return f"Error: {exc}"[:500]
