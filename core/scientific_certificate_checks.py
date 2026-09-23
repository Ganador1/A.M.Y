"""Fail-closed, request-bound checks and compact summaries for native tools.

No scientific backend is imported at module load. Domain verifiers run once
per parsed certificate, inside the existing evidence span; their original
return values are retained without substituting these wrapper decisions.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from fractions import Fraction

_CAPS = {
    "h2_rhf_certificate": 48*1024,
    "ssh_gap_certificate": 48*1024,
    "population_selection_certificate": 256*1024,
    "riemann_zeta_certificate": 64*1024,
    "bsd_elliptic_certificate": 64*1024,
    "p_vs_np_complexity_certificate": 64*1024,
    "yang_mills_lattice_certificate": 64*1024,
    "hodge_variety_certificate": 64*1024,
    "lean4_prove_certificate": 64*1024,
}
_KINDS = {
    "h2_rhf_certificate": "h2_rhf_numerical_consistency",
    "ssh_gap_certificate": "ssh_exact_squared_gap_bounds",
    "population_selection_certificate": "population_selection_exact_trajectory",
    "riemann_zeta_certificate": "riemann_zeta_critical_line_probe",
    "bsd_elliptic_certificate": "bsd_elliptic_curve_invariants",
    "p_vs_np_complexity_certificate": "p_vs_np_dpll_and_barriers",
    "yang_mills_lattice_certificate": "yang_mills_lattice_mass_gap",
    "hodge_variety_certificate": "hodge_diamond_and_cycles",
    "lean4_prove_certificate": "lean4_kernel_formal_verification",
}
_SSH_NOTES = [
    "Finite open even chain, strictly positive rational hoppings, exactly zero onsite energies.",
    "Gap is the half-filling spectral gap; units are inherited from the supplied hoppings.",
    "No certificate for diagonal disorder, measurement uncertainty, topology or an infinite-system limit.",
    "Applies known Collatz-Wielandt inequalities; does not establish scientific novelty.",
]


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha(value):
    return hashlib.sha256(_canonical(value).encode()).hexdigest()


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError(f"nonfinite JSON constant: {value}")


def _parse(value, cap, *, decimal_strings=False):
    if isinstance(value, dict):
        raw = _canonical(value).encode()
    elif isinstance(value, str):
        raw = value.encode("utf-8")
    elif isinstance(value, bytes):
        raw = value
    else:
        raise ValueError("expected JSON string, bytes or object")
    if len(raw) > cap:
        raise ValueError("certificate/input byte limit exceeded")
    kwargs = {"object_pairs_hook": _pairs, "parse_constant": _reject_constant}
    if decimal_strings:
        kwargs["parse_float"] = str
    parsed = json.loads(raw, **kwargs)
    if not isinstance(parsed, dict):
        raise ValueError("expected a JSON object")
    _canonical(parsed)  # 1e999 is parsed as infinity by the normal float parser.
    return parsed, hashlib.sha256(raw).hexdigest()


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _keys(value, keys, name):
    _require(isinstance(value, dict) and set(value) == set(keys), f"{name}: unexpected or missing fields")


def _h2_input(request):
    # Match the producer's decimal interpretation of JSON numeric inputs,
    # then compare exact rationals after the explicitly fixed unit conversion.
    from atlas.app.h2_rhf_verifier import BOHR_ANGSTROM
    req, _ = _parse(request, 2048)
    _require(len(req) == 1, "H2 input requires exactly one explicit distance")
    key = next(iter(req))
    _require(key in {"distance_angstrom", "distance_bohr"}, "unsupported H2 distance unit")
    raw = req[key]
    _require(type(raw) in (str, int, float), "invalid H2 distance type")
    token = str(raw).strip()
    _require(len(token) <= 64 and re.fullmatch(
        r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d{1,2})?|[+-]?\d+/\d+", token),
        "invalid H2 exact input")
    value = Fraction(token)
    _require(max(abs(value.numerator).bit_length(), value.denominator.bit_length()) <= 256,
             "H2 distance precision limit")
    if key == "distance_bohr":
        value *= Fraction(str(BOHR_ANGSTROM))
    _require(Fraction(3,10) <= value <= 4, "H2 distance outside scope")
    return value


def _verify_once(tool_name, certificate, verifier, *args, **kwargs):
    from core.execution_evidence import evidence_span
    with evidence_span("atlas.certificate_verification", {
        "tool_name": tool_name, "certificate": certificate,
    }) as span:
        verification = verifier(*args, **kwargs)
        span.result(verification)
    return verification


def _h2(cert, expected_input, audit):
    from atlas.app.h2_rhf_verifier import SCHEMA, verify_h2_rhf_certificate
    _keys(cert, {"schema", "status", "claim", "summary", "model", "input", "geometry",
                 "basis_definition", "integrals", "state", "scf", "versions", "sources",
                 "limitations", "verification"}, "H2 certificate")
    _require(cert["schema"] == SCHEMA and cert["status"] == "verified_numerical_consistency",
             "unsupported or failed H2 schema/status")
    for field, keys in {
        "model": {"method", "basis", "charge", "spin", "electron_count", "ao_count", "integral_convention", "geometry_unit", "energy_unit", "assumptions"},
        "summary": {"distance_angstrom", "total_energy_hartree", "scope"},
        "geometry": {"elements", "coordinates_bohr", "distance_bohr", "distance_angstrom", "bohr_to_angstrom", "conversion_source"},
        "basis_definition": {"hydrogen_shells_pyscf_format", "ao_labels"},
        "integrals": {"engine", "overlap", "kinetic", "nuclear_attraction", "electron_repulsion"},
        "state": {"density", "mo_coefficients", "mo_energies", "mo_occupations", "nuclear_repulsion_energy", "electronic_energy", "total_energy"},
        "scf": {"converged", "cycles", "max_cycles", "energy_tolerance", "gradient_tolerance", "cycle_history", "initial_guess", "requested_omp_threads", "reported_omp_threads"},
        "versions": {"python", "numpy", "scipy", "pyscf", "libcint"},
    }.items():
        _keys(cert[field], keys, "H2 " + field)
    _require(cert["geometry"]["conversion_source"] == "pyscf.data.nist.BOHR (floating-point convention)", "H2 conversion source changed")
    _require(cert["integrals"]["engine"] == "PySCF libcint; supplied integrals, not independently regenerated by verifier", "H2 integral scope changed")
    _require(cert["basis_definition"]["ao_labels"] == ["0 H 1s    ", "1 H 1s    "], "H2 AO labels changed")
    _require(cert["sources"] == ["https://pyscf.org/user/scf.html", "https://pyscf.org/user/gto.html",
             "https://github.com/pyscf/pyscf/tree/v2.11.0", "https://www.basissetexchange.org/family_notes/sto/",
             "https://doi.org/10.1063/1.1672392", "https://doi.org/10.1063/5.0006074"], "H2 source metadata changed")
    for entry in cert["scf"]["cycle_history"]:
        _keys(entry, {"cycle", "total_energy_hartree", "orbital_gradient_norm", "density_change_norm"}, "H2 SCF cycle")
    embedded = cert["verification"]
    _require(isinstance(embedded, dict) and embedded.get("valid") is True,
             "H2 producer did not declare a boolean successful audit")
    verification = _verify_once("h2_rhf_certificate", cert, verify_h2_rhf_certificate, cert)
    audit["verification"] = verification
    audit["scope"] = verification["scope"]
    _require(verification["valid"] is True, "H2 independent numerical audit failed: " + "; ".join(verification["failures"]))
    # Reject declared scientific/scope signals that the pure numerical checker
    # does not inspect. Neither a self-reported pass nor extra prose is evidence.
    _require(_canonical(embedded) == _canonical(verification), "H2 declared audit differs from fresh numerical audit")
    _require(cert["claim"] == "Numerical consistency of a fixed H2 RHF/STO-3G calculation", "H2 claim scope changed")
    _require(cert["summary"].get("scope") == "H2 RHF/STO-3G; numerical audit with shared AO integrals", "H2 summary scope changed")
    _require(cert["model"].get("assumptions") == ["Born-Oppenheimer clamped nuclei", "nonrelativistic Coulomb Hamiltonian",
             "closed-shell single determinant", "finite Gaussian basis STO-3G"], "H2 assumptions changed")
    _require(cert["limitations"] == [
        "Floating-point numerical consistency audit; no rigorous interval energy bound.",
        "Both audits share supplied PySCF/libcint AO integrals; a common integral error can survive.",
        "RHF/STO-3G is an approximate molecular model, not the exact physical energy or experiment.",
        "No inference of novelty, chemical accuracy, or global equilibrium geometry is made.",
    ], "H2 limitations changed")
    distance = _h2_input(cert["input"])
    if expected_input is not None:
        _require(distance == _h2_input(expected_input), "H2 certificate belongs to a different requested distance")
        audit["input_bound"] = True
    energy, display_distance = cert["state"]["total_energy"], cert["geometry"]["distance_angstrom"]
    return {"distance_angstrom": display_distance, "distance_angstrom_input_exact": str(distance),
            "total_energy_hartree": energy, "energy_float64_hex": float(energy).hex(),
            "scope": audit["scope"], "rigorous_interval_bound": False, "independent_integral_engine": False}


def _hex_fraction(pair, *, bits=65536, allow_zero=False):
    _require(isinstance(pair, list) and len(pair) == 2 and all(type(x) is str for x in pair), "invalid SSH rational pair")
    _require(all(len(x) <= 2+(bits+3)//4 and re.fullmatch(r"0x(?:0|[1-9a-f][0-9a-f]*)", x) for x in pair),
             "SSH rational encoding/precision limit")
    value = Fraction(int(pair[0],16), int(pair[1],16))
    _require(value >= 0 if allow_zero else value > 0, "SSH requires positive rationals")
    _require(pair == [hex(value.numerator), hex(value.denominator)], "SSH rationals must be reduced canonical pairs")
    _require(max(value.numerator.bit_length(),value.denominator.bit_length()) <= bits, "SSH precision limit")
    return value


def _ssh_input(request):
    from atlas.app.ssh_certificate_tool import _rational
    req, _ = _parse(request, 65536, decimal_strings=True)
    _require(set(req) <= {"hoppings", "threshold", "iterations", "strategy"}, "unsupported SSH input fields")
    values = req.get("hoppings")
    _require(isinstance(values,list) and 3 <= len(values) <= 511 and len(values)%2 == 1, "invalid SSH input hopping count")
    hops = [_rational(v, "hoppings") for v in values]
    iterations, strategy = req.get("iterations",4), req.get("strategy","float")
    _require(type(iterations) is int and 0 <= iterations <= 100, "invalid SSH input iterations")
    _require(strategy in ("float", "auto"), "invalid SSH input strategy")
    threshold = _rational(req["threshold"], "threshold", allow_zero=True) if "threshold" in req else None
    return hops, threshold, iterations, strategy


def _ssh(cert, expected_input, audit):
    from atlas.app.ssh_certificate_tool import decode_gap_certificate
    from atlas.app.ssh_spectral_certificate import verify_gap_certificate
    required = {"success", "tool", "schema_version", "site_count", "iterations", "certificate",
                "certificate_sha256", "hoppings_sha256", "approximations", "scope_notes"}
    _require(required <= set(cert) <= required | {"threshold", "strategy_requested", "strategy_used"}, "SSH envelope fields changed")
    _require(cert["success"] is True and cert["tool"] == "ssh_gap_certificate"
             and type(cert["schema_version"]) is int and cert["schema_version"] == 1, "unsupported or failed SSH schema/status")
    encoded = cert["certificate"]
    _keys(encoded, {"encoding", "method", "scope", "gap_squared_lower", "gap_squared_upper", "hoppings", "witness"}, "SSH certificate")
    _require(encoded["encoding"] == "hex_numerator_denominator_pairs", "invalid SSH encoding")
    hops = encoded["hoppings"]
    _require(isinstance(hops,list) and 3 <= len(hops) <= 511 and len(hops)%2 == 1, "invalid SSH hopping count")
    _require(type(cert["site_count"]) is int and cert["site_count"] == len(hops)+1, "SSH declared site count mismatch")
    _require(isinstance(encoded["witness"],list) and len(encoded["witness"]) == (len(hops)+1)//2, "SSH witness dimension mismatch")
    for value in hops:
        _hex_fraction(value, bits=128)
    for value in encoded["witness"]:
        _hex_fraction(value)
    lower, upper = (_hex_fraction(encoded[k]) for k in ("gap_squared_lower", "gap_squared_upper"))
    _require(cert["certificate_sha256"] == _sha(encoded) and cert["hoppings_sha256"] == _sha(hops), "SSH certificate/hoppings hash mismatch")
    _require(cert["scope_notes"] == _SSH_NOTES, "SSH scope notes changed")
    exact = decode_gap_certificate(encoded)
    # Retain the original JSON envelope: Fraction has no implicit JSON encoding.
    verification = _verify_once("ssh_gap_certificate", cert, verify_gap_certificate, exact)
    audit["verification"] = verification
    audit["scope"] = exact["scope"]
    _require(verification is True, "SSH exact witness verification failed")
    iterations = cert["iterations"]
    _require(type(iterations) is int and 0 <= iterations <= 100, "invalid SSH iteration count")
    strategy = "float"
    if "strategy_requested" in cert or "strategy_used" in cert:
        _require(cert.get("strategy_requested") == "auto" and cert.get("strategy_used") in ("float", "column", "balanced_columns"), "invalid SSH strategy metadata")
        strategy = "auto"
    approx = cert["approximations"]
    _keys(approx, {"certified", "warning", "gap_squared_lower", "gap_squared_upper"}, "SSH display")
    _require(approx["certified"] is False and approx["warning"] == "Rounded display only; zero can mean underflow. Use exact squared bounds for decisions.", "SSH display falsely certified")
    for key, exact_bound in (("gap_squared_lower", lower), ("gap_squared_upper", upper)):
        try:
            display = float(exact_bound)
            if not math.isfinite(display): display = None
        except OverflowError:
            display = None
        actual = approx[key]
        _require(actual is None if display is None else type(actual) in (int,float) and actual == display,
                 "SSH rounded display differs from exact bound")
    threshold = None
    if "threshold" in cert:
        entry = cert["threshold"]
        _keys(entry, {"value", "encoding", "quantity", "verdict"}, "SSH threshold")
        _require(entry["encoding"] == "hex_numerator_denominator_pairs" and entry["quantity"] == "gap (not gap squared)", "SSH threshold units/encoding changed")
        threshold = _hex_fraction(entry["value"], bits=128, allow_zero=True)
        verdict = "proven_below_or_equal" if upper <= threshold*threshold else "proven_above" if lower > threshold*threshold else "inconclusive"
        _require(entry["verdict"] == verdict, "SSH threshold verdict false")
    if expected_input is not None:
        expected_hops, expected_threshold, expected_iterations, expected_strategy = _ssh_input(expected_input)
        _require(exact["hoppings"] == expected_hops, "SSH certificate belongs to different ordered hoppings")
        _require(threshold == expected_threshold and iterations == expected_iterations and strategy == expected_strategy,
                 "SSH request threshold/options mismatch")
        audit["input_bound"] = True
    summary = {"site_count": cert["site_count"], "gap_squared_lower": encoded["gap_squared_lower"],
               "gap_squared_upper": encoded["gap_squared_upper"], "encoding": encoded["encoding"],
               "bounds_kind": "exact_rational_squared_gap", "display": dict(approx),
               "scope": audit["scope"], "hoppings_sha256": cert["hoppings_sha256"],
               "hoppings_rational": [str(value) for value in exact["hoppings"]],
               "gap_definition": "E[N/2] - E[N/2-1] = 2*sigma_min(B); ascending eigenvalues, zero-based indices",
               "gap_squared_units": "input_hopping_units_squared"}
    if threshold is not None:
        summary["threshold"] = dict(cert["threshold"])
    return summary


def _population(cert, expected_input, audit):
    from atlas.app.population_selection_verifier import verify_population_selection_certificate, parse_population_selection_input
    # The domain result remains independent of optional external request binding,
    # so an offline replay with only the retained certificate returns it exactly.
    verification = _verify_once("population_selection_certificate", cert, verify_population_selection_certificate, cert)
    audit["verification"] = verification
    audit["scope"] = verification["scope"]
    _require(verification["valid"] is True, "population exact trajectory failed: " + "; ".join(verification["failures"]))
    if expected_input is not None:
        request, _ = _parse(expected_input, 2048)
        _require(parse_population_selection_input(request) == cert["input"], "population certificate belongs to different input")
        audit["input_bound"] = True
    states = [Fraction(row["p_A"]) for row in cert["trajectory"]]
    differences = [b-a for a,b in zip(states, states[1:])]
    trend = ("constant" if all(d == 0 for d in differences) else
             "nondecreasing" if all(d >= 0 for d in differences) else
             "nonincreasing" if all(d <= 0 for d in differences) else "nonmonotone")
    return {"generations": cert["input"]["generations"], "p_initial": str(states[0]),
            "p_final": str(states[-1]), "delta_p": str(states[-1]-states[0]),
            "trajectory_trend": trend, "trend_scope": "executed finite transitions only",
            "scope": audit["scope"], "exact_model_verified": True}


def _riemann(cert, expected_input, audit):
    _require(cert.get("problem") == "Riemann Hypothesis", "invalid problem in certificate")
    _require(cert.get("success") is True, "certificate reported success=False")
    audit["scope"] = "Riemann Hypothesis critical line and Li criterion probe"
    audit["input_bound"] = True
    return {"problem": "Riemann Hypothesis", "critical_line": cert.get("critical_line"),
            "zeros_count": len(cert.get("zeros", [])), "all_on_critical_line": cert.get("all_on_critical_line", True)}


def _bsd(cert, expected_input, audit):
    _require(cert.get("problem") == "Birch and Swinnerton-Dyer Conjecture (BSD)", "invalid problem in certificate")
    _require(cert.get("success") is True, "certificate reported success=False")
    audit["scope"] = "Birch and Swinnerton-Dyer elliptic curve invariants"
    audit["input_bound"] = True
    return {"problem": "BSD", "curve": cert.get("curve_weierstrass"),
            "discriminant": cert.get("discriminant"), "j_invariant": cert.get("j_invariant"),
            "bad_primes": cert.get("bad_reduction_primes")}


def _p_vs_np(cert, expected_input, audit):
    _require(cert.get("problem") == "P versus NP", "invalid problem in certificate")
    _require(cert.get("success") is True, "certificate reported success=False")
    audit["scope"] = "P versus NP DPLL complexity and polynomial verification"
    audit["input_bound"] = True
    return {"problem": "P versus NP", "status": cert.get("solver_metrics", {}).get("status"),
            "nodes_explored": cert.get("solver_metrics", {}).get("nodes_explored")}


def _yang_mills(cert, expected_input, audit):
    _require(cert.get("problem") == "Yang-Mills Existence and Mass Gap", "invalid problem in certificate")
    _require(cert.get("success") is True, "certificate reported success=False")
    audit["scope"] = "SU(2) lattice gauge theory mass gap and Wilson loops"
    audit["input_bound"] = True
    npo = cert.get("non_perturbative_observables", {})
    return {"problem": "Yang-Mills", "average_plaquette": npo.get("average_plaquette"),
            "mass_gap_Delta": npo.get("estimated_glueball_mass_gap_Delta")}


def _hodge(cert, expected_input, audit):
    _require(cert.get("problem") == "Hodge Conjecture", "invalid problem in certificate")
    _require(cert.get("success") is True, "certificate reported success=False")
    audit["scope"] = "Complex projective variety Hodge diamond and algebraic cycles"
    audit["input_bound"] = True
    return {"problem": "Hodge Conjecture", "variety_type": cert.get("variety_specification", {}).get("type"),
            "euler_characteristic": cert.get("euler_characteristic")}


def _lean4(cert, expected_input, audit):
    _require(cert.get("problem") == "Formal Theorem Verification (Lean 4)", "invalid problem in certificate")
    _require(cert.get("success") is True, "certificate reported success=False")
    _require(cert.get("verified_by_lean_kernel") is True, "theorem not verified by Lean 4 kernel")
    _require(cert.get("uses_sorry") is False, "theorem uses unproven sorry/admit")
    _require(cert.get("status") == "PROVEN", f"unexpected status {cert.get('status')}")
    audit["scope"] = "Lean 4 kernel formal theorem verification"
    audit["input_bound"] = True
    return {
        "problem": "Formal Theorem Verification (Lean 4)",
        "theorem_name": cert.get("theorem_name"),
        "proven": cert.get("proven"),
        "status": cert.get("status"),
        "code_hash": cert.get("code_hash"),
    }


def check_scientific_certificate(tool_name, output, *, expected_input=None):
    """Return a strict audit for known tools, or None for an unknown tool.

    `valid` includes envelope/summary/request checks. `verification` is the
    original domain checker result, which can pass even if request binding
    fails. No summary is exposed from an invalid certificate.
    """
    if not isinstance(tool_name, str) or tool_name not in _CAPS:
        return None
    audit = {"valid": False, "scope": "unverified", "certificate_kind": _KINDS[tool_name],
             "errors": [], "input_bound": False, "verification": None, "summary": None,
             "scientific_truth_verified": False, "novelty_verified": False, "authenticated": False}
    try:
        cert, output_hash = _parse(output, _CAPS[tool_name])
        audit["raw_output_sha256"] = output_hash
        audit["certificate_sha256"] = _sha(cert)
        handlers = {
            "h2_rhf_certificate": _h2,
            "ssh_gap_certificate": _ssh,
            "population_selection_certificate": _population,
            "riemann_zeta_certificate": _riemann,
            "bsd_elliptic_certificate": _bsd,
            "p_vs_np_complexity_certificate": _p_vs_np,
            "yang_mills_lattice_certificate": _yang_mills,
            "hodge_variety_certificate": _hodge,
            "lean4_prove_certificate": _lean4,
        }
        # These legacy producers return observations or self-reported proof flags,
        # not independently replayable, request-bound scientific certificates.
        # Keep them visible as unsupported rather than upgrading success=True.
        legacy_unverified = {
            "riemann_zeta_certificate", "bsd_elliptic_certificate",
            "p_vs_np_complexity_certificate", "yang_mills_lattice_certificate",
            "hodge_variety_certificate", "lean4_prove_certificate",
        }
        if tool_name in legacy_unverified:
            audit["scope"] = "Legacy observation; independent request-bound verification unavailable"
            audit["verification_status"] = "unsupported_legacy_certificate"
            raise ValueError("Independent request-bound verifier required; producer flags are not evidence")
        handler = handlers[tool_name]
        summary = handler(cert, expected_input, audit)
        summary.update(certificate_sha256=audit["certificate_sha256"], raw_output_sha256=output_hash)
        audit.update(valid=True, summary=summary)
    except Exception as exc:
        # A missing backend or malformed certificate must not make a native
        # action look scientifically verified. KeyboardInterrupt still escapes.
        audit["errors"].append(f"{type(exc).__name__}: {exc}")
        audit["input_bound"] = False
    return audit
