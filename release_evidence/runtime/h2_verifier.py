"""Independent numerical consistency audit for one closed-shell H2/STO-3G result.

Only NumPy and the standard library are used here. Integrals are supplied by the
producer: this is not an independent integral engine or a rigorous energy bound.
The reported verification object and producer tolerances are never trusted.
"""
from __future__ import annotations

import json
import math
import re
from collections.abc import Mapping
from fractions import Fraction

import numpy as np

MAX_CERTIFICATE_BYTES = 48 * 1024
BOHR_ANGSTROM = 0.52917721092  # PySCF 2.11's explicit conversion, not exact SI.
SCHEMA = "amy.h2_rhf.sto3g.v1"
MATRIX_TOLERANCE = 2e-8
ENERGY_TOLERANCE_HARTREE = 2e-9


def _number(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a JSON number, not bool/string")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _array(value, shape, name):
    def walk(node, dims):
        if not dims:
            return _number(node, name)
        if not isinstance(node, list) or len(node) != dims[0]:
            raise ValueError(f"{name} must have shape {shape}")
        return [walk(item, dims[1:]) for item in node]
    return np.array(walk(value, shape), dtype=float)


def verify_h2_rhf_certificate(certificate: Mapping) -> dict:
    """Recompute RHF identities and the H2 bonding-orbital solution.

    The verifier accepts no tolerance overrides. A successful audit establishes
    consistency to the explicitly reported floating-point tolerances only.
    """
    checks = {}
    failures = []

    def check(name, residual, tolerance=MATRIX_TOLERANCE):
        residual = float(residual)
        passed = math.isfinite(residual) and residual <= tolerance
        checks[name] = {"passed": passed, "residual": residual,
                        "tolerance": tolerance}
        if not passed:
            failures.append(name)

    def maximum(value):
        return float(np.max(np.abs(value)))

    report = {
        "valid": False,
        "audit_kind": "independent_numpy_numerical_consistency",
        "scope": "RHF/STO-3G H2, using supplied PySCF/libcint integrals",
        "rigorous_interval_bound": False,
        "independent_integral_engine": False,
        "checks": checks,
        "failures": failures,
    }
    try:
        if not isinstance(certificate, Mapping):
            raise ValueError("certificate must be a JSON object")
        if len(json.dumps(certificate, allow_nan=False).encode()) > MAX_CERTIFICATE_BYTES:
            raise ValueError("certificate exceeds 48 KiB")
        if certificate["schema"] != SCHEMA:
            raise ValueError("unsupported schema")
        model = certificate["model"]
        if (model["method"] != "RHF" or model["basis"] != "sto-3g"
                or model["integral_convention"] != "chemist (pq|rs), real AO"
                or model["energy_unit"] != "hartree"
                or model["geometry_unit"] != "bohr"):
            raise ValueError("unsupported method, basis, convention or units")
        for field, expected in (("charge", 0), ("spin", 0),
                                ("electron_count", 2), ("ao_count", 2)):
            if type(model[field]) is not int or model[field] != expected:
                raise ValueError(f"invalid {field}")
        geometry = certificate["geometry"]
        if geometry["elements"] != ["H", "H"]:
            raise ValueError("geometry must contain exactly two hydrogen atoms")
        coords = _array(geometry["coordinates_bohr"], (2, 3), "coordinates_bohr")
        distance = _number(geometry["distance_bohr"], "distance_bohr")
        distance_a = _number(geometry["distance_angstrom"], "distance_angstrom")
        conversion = _number(geometry["bohr_to_angstrom"], "bohr_to_angstrom")
        if conversion != BOHR_ANGSTROM:
            raise ValueError("unsupported length conversion")
        if not 0.3 <= distance_a <= 4.0 or distance <= 0:
            raise ValueError("distance outside 0.3..4 angstrom")
        check("geometry_distance", abs(np.linalg.norm(coords[1]-coords[0])-distance), 1e-12)
        check("geometry_units", abs(distance_a-distance*conversion), 1e-12)
        request = certificate["input"]
        if not isinstance(request, dict) or len(request) != 1:
            raise ValueError("input must have exactly one explicit distance")
        input_key = next(iter(request))
        raw_distance = request[input_key]
        if (input_key not in {"distance_angstrom", "distance_bohr"}
                or not isinstance(raw_distance, str) or len(raw_distance) > 64
                or not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d{1,2})?|[+-]?\d+/\d+", raw_distance)):
            raise ValueError("invalid explicit input distance")
        rational_distance = Fraction(raw_distance)
        if input_key == "distance_bohr":
            rational_distance *= Fraction(str(BOHR_ANGSTROM))
        if not Fraction(3, 10) <= rational_distance <= 4:
            raise ValueError("input distance outside scope")
        check("input_geometry_binding", abs(float(rational_distance)-distance_a), 1e-12)

        # Fix the AO definition; integral generation itself remains unaudited.
        shells = certificate["basis_definition"]["hydrogen_shells_pyscf_format"]
        if (not isinstance(shells, list) or len(shells) != 1
                or not isinstance(shells[0], list) or len(shells[0]) != 4
                or type(shells[0][0]) is not int or shells[0][0] != 0):
            raise ValueError("expected one contracted s shell per H")
        primitives = _array(shells[0][1:], (3, 2), "STO-3G primitives")
        expected_primitives = np.array([[3.42525091, .15432897],
                                        [.62391373, .53532814], [.1688554, .44463454]])
        check("STO3G_basis_parameters", maximum(primitives-expected_primitives), 1e-12)

        integrals = certificate["integrals"]
        overlap = _array(integrals["overlap"], (2, 2), "overlap")
        kinetic = _array(integrals["kinetic"], (2, 2), "kinetic")
        nuclear = _array(integrals["nuclear_attraction"], (2, 2), "nuclear_attraction")
        eri = _array(integrals["electron_repulsion"], (2, 2, 2, 2), "electron_repulsion")
        state = certificate["state"]
        density = _array(state["density"], (2, 2), "density")
        coeff = _array(state["mo_coefficients"], (2, 2), "mo_coefficients")
        occupations = _array(state["mo_occupations"], (2,), "mo_occupations")
        orbital_energies = _array(state["mo_energies"], (2,), "mo_energies")
        e_nuc = _number(state["nuclear_repulsion_energy"], "nuclear_repulsion_energy")
        e_total = _number(state["total_energy"], "total_energy")
        e_elec = _number(state["electronic_energy"], "electronic_energy")
        summary = certificate["summary"]
        check("summary_geometry_binding", abs(_number(summary["distance_angstrom"], "summary distance")-distance_a), 1e-12)
        check("summary_energy_binding", abs(_number(summary["total_energy_hartree"], "summary energy")-e_total), ENERGY_TOLERANCE_HARTREE)

        # Metadata is necessary, but never sufficient for numerical acceptance.
        convergence = certificate["scf"]
        if type(convergence["converged"]) is not bool:
            raise ValueError("converged must be boolean")
        if not convergence["converged"]:
            failures.append("producer_did_not_converge")
        if (type(convergence["cycles"]) is not int
                or type(convergence["max_cycles"]) is not int
                or not 0 <= convergence["cycles"] <= convergence["max_cycles"] <= 100):
            raise ValueError("invalid SCF cycle counts")
        for field, ceiling in (("energy_tolerance", 1e-10), ("gradient_tolerance", 1e-8)):
            value = _number(convergence[field], field)
            if not 0 < value <= ceiling:
                raise ValueError(f"invalid {field}")
        history = convergence["cycle_history"]
        if not isinstance(history, list) or len(history) != convergence["cycles"] or not history:
            raise ValueError("missing SCF cycle history")
        for cycle, entry in enumerate(history, 1):
            if type(entry["cycle"]) is not int or entry["cycle"] != cycle:
                raise ValueError("nonconsecutive SCF cycle history")
            _number(entry["total_energy_hartree"], "cycle energy")
            for field in ("orbital_gradient_norm", "density_change_norm"):
                if _number(entry[field], field) < 0:
                    raise ValueError("negative SCF norm")
        check("last_cycle_energy", abs(history[-1]["total_energy_hartree"]-e_total), ENERGY_TOLERANCE_HARTREE)
        check("last_cycle_gradient", history[-1]["orbital_gradient_norm"], 1e-8)
        for field in ("python", "numpy", "scipy", "pyscf"):
            if not isinstance(certificate["versions"][field], str) or not certificate["versions"][field]:
                raise ValueError(f"missing {field} version")

        for name, matrix in (("S", overlap), ("T", kinetic), ("V", nuclear), ("D", density)):
            check(f"{name}_symmetry", maximum(matrix-matrix.T))
        eigen_s = np.linalg.eigvalsh(overlap)
        if eigen_s.min() <= 1e-8:
            raise ValueError("overlap must be well-conditioned positive definite")
        check("S_normalized_diagonal", maximum(np.diag(overlap)-1), 1e-10)
        check("identical_H_core_diagonals", abs((kinetic+nuclear)[0, 0]-(kinetic+nuclear)[1, 1]))
        check("ERI_first_pair_symmetry", maximum(eri-eri.swapaxes(0, 1)))
        check("ERI_second_pair_symmetry", maximum(eri-eri.swapaxes(2, 3)))
        check("ERI_pair_exchange", maximum(eri-eri.transpose(2, 3, 0, 1)))
        check("ERI_H_exchange", maximum(eri-eri[::-1, ::-1, ::-1, ::-1]))
        check("nuclear_repulsion", abs(e_nuc-1/distance), 1e-11)
        check("occupations", maximum(occupations-np.array([2., 0.])), 1e-12)
        if orbital_energies[0] >= orbital_energies[1]:
            failures.append("orbitals_not_ascending")

        # Explicit small-loop contractions, independent of the SCF producer.
        core_h = kinetic+nuclear
        coulomb = np.zeros((2, 2))
        exchange = np.zeros((2, 2))
        for p in range(2):
            for q in range(2):
                for r in range(2):
                    for s in range(2):
                        coulomb[p, q] += density[r, s]*eri[p, q, r, s]
                        exchange[p, q] += density[r, s]*eri[p, r, q, s]
        fock = core_h+coulomb-exchange/2
        energy = float(np.sum(density*core_h) + np.sum(density*coulomb)/2
                       - np.sum(density*exchange)/4 + e_nuc)
        check("energy_contraction", abs(energy-e_total), ENERGY_TOLERANCE_HARTREE)
        check("energy_components", abs(e_elec+e_nuc-e_total), ENERGY_TOLERANCE_HARTREE)
        check("electron_normalization", abs(np.trace(density@overlap)-2))
        check("density_idempotence", maximum(density@overlap@density-2*density))
        check("MO_metric_orthonormality", maximum(coeff.T@overlap@coeff-np.eye(2)))
        check("density_from_MO", maximum(density-(coeff*occupations)@coeff.T))
        check("Fock_commutator", maximum(fock@density@overlap-overlap@density@fock))
        check("MO_eigen_residual", maximum(fock@coeff-(overlap@coeff)*orbital_energies))

        # Distinct oracle: the occupied bonding MO is fixed by H2 symmetry.
        # This reconstructs the RHF energy without solving any SCF equations.
        bonding = np.ones(2)/math.sqrt(2*(1+overlap[0, 1]))
        bonding_density = 2*np.outer(bonding, bonding)
        h_gg = float(bonding@core_h@bonding)
        gggg = sum(bonding[p]*bonding[q]*bonding[r]*bonding[s]*eri[p, q, r, s]
                   for p in range(2) for q in range(2) for r in range(2) for s in range(2))
        symmetry_energy = float(2*h_gg+gggg+1/distance)
        check("bonding_density_oracle", maximum(density-bonding_density))
        check("bonding_energy_oracle", abs(e_total-symmetry_energy), ENERGY_TOLERANCE_HARTREE)
        report["recomputed"] = {
            "total_energy_hartree": energy,
            "bonding_energy_hartree": symmetry_energy,
            "electron_count": float(np.trace(density@overlap)),
            "fock": fock.tolist(),
            "density_bonding": bonding_density.tolist(),
        }
        report["valid"] = not failures
    except (KeyError, TypeError, ValueError, ZeroDivisionError, OverflowError, np.linalg.LinAlgError) as exc:
        failures.append(f"invalid_certificate: {exc}")
    return report
