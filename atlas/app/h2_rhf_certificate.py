"""Auditable H2 RHF/STO-3G producer for AMY's native tool chain.

The certificate is a small numerical evidence object, not a rigorous interval
bound, experimental measurement, or exact solution of the physical molecule.
"""
from __future__ import annotations

import json
import math
import platform
import re
from fractions import Fraction

from .h2_rhf_verifier import MAX_CERTIFICATE_BYTES, SCHEMA, verify_h2_rhf_certificate


def _distance_value(value) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError("distance must be a finite decimal/rational string or number")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("distance must be finite")
    text = str(value).strip()
    if len(text) > 64 or not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d{1,2})?|[+-]?\d+/\d+", text):
        raise ValueError("distance must be a short finite decimal or rational")
    try:
        result = Fraction(text)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError("invalid distance") from exc
    if result.numerator.bit_length() > 256 or result.denominator.bit_length() > 256:
        raise ValueError("distance precision exceeds 256 bits")
    return result


def _parse_input(request):
    if isinstance(request, str):
        if len(request.encode()) > 2048:
            raise ValueError("input exceeds 2 KiB")
        def pairs(items):
            output = {}
            for key, value in items:
                if key in output:
                    raise ValueError(f"duplicate input key: {key}")
                output[key] = value
            return output
        request = json.loads(request, object_pairs_hook=pairs)
    if not isinstance(request, dict) or len(request) != 1:
        raise ValueError("provide exactly one distance_angstrom or distance_bohr field")
    key = next(iter(request))
    if key not in {"distance_angstrom", "distance_bohr"}:
        raise ValueError("only distance_angstrom or distance_bohr is supported")
    return key, _distance_value(request[key])


def produce_h2_rhf_certificate(request) -> dict:
    """Compute fixed RHF/STO-3G for a neutral singlet H2, 0.3..4 angstrom."""
    key, value = _parse_input(request)
    # Validate before importing/initializing the scientific backend.
    from .h2_rhf_verifier import BOHR_ANGSTROM
    conversion = Fraction(str(BOHR_ANGSTROM))
    distance_a = value if key == "distance_angstrom" else value*conversion
    if not Fraction(3, 10) <= distance_a <= 4:
        raise ValueError("distance must lie in [0.3, 4] angstrom")
    distance_b = distance_a/conversion

    import numpy as np
    import scipy
    import pyscf
    from pyscf import gto, scf, lib
    from pyscf.data import nist
    if nist.BOHR != BOHR_ANGSTROM:
        raise RuntimeError("PySCF length conversion changed; review certificate schema")

    # Fixed atomic ordering and units. No geometry optimizer or hidden random data.
    with lib.with_omp_threads(1):
        mol = gto.M(atom=[["H", [0., 0., 0.]], ["H", [0., 0., float(distance_b)]]],
                    unit="Bohr", basis="sto-3g", charge=0, spin=0, verbose=0)
        mf = scf.RHF(mol)
        mf.verbose = 0
        mf.chkfile = None
        mf.conv_tol = 1e-12
        mf.conv_tol_grad = 1e-10
        mf.max_cycle = 100
        history = []
        def record_cycle(environment):
            history.append({
                "cycle": int(environment["cycle"])+1,
                "total_energy_hartree": float(environment["e_tot"]),
                "orbital_gradient_norm": float(environment["norm_gorb"]),
                "density_change_norm": float(environment["norm_ddm"]),
            })
        mf.callback = record_cycle
        energy = float(mf.kernel())
        nuclear_energy = float(mol.energy_nuc())
        certificate = {
            "schema": SCHEMA,
            "claim": "Numerical consistency of a fixed H2 RHF/STO-3G calculation",
            # Native AMY memory retains a short prefix; keep the usable result
            # before the complete, independently auditable matrix payload.
            "summary": {"distance_angstrom": float(distance_a),
                        "total_energy_hartree": energy,
                        "scope": "H2 RHF/STO-3G; numerical audit with shared AO integrals"},
            "model": {
                "method": "RHF", "basis": "sto-3g", "charge": 0, "spin": 0,
                "electron_count": int(mol.nelectron), "ao_count": int(mol.nao),
                "integral_convention": "chemist (pq|rs), real AO",
                "geometry_unit": "bohr", "energy_unit": "hartree",
                "assumptions": ["Born-Oppenheimer clamped nuclei", "nonrelativistic Coulomb Hamiltonian",
                                "closed-shell single determinant", "finite Gaussian basis STO-3G"],
            },
            "input": {key: str(value)},
            "geometry": {
                "elements": ["H", "H"], "coordinates_bohr": mol.atom_coords().tolist(),
                "distance_bohr": float(distance_b), "distance_angstrom": float(distance_a),
                "bohr_to_angstrom": BOHR_ANGSTROM,
                "conversion_source": "pyscf.data.nist.BOHR (floating-point convention)",
            },
            "basis_definition": {"hydrogen_shells_pyscf_format": mol._basis["H"],
                                 "ao_labels": mol.ao_labels()},
            "integrals": {
                "engine": "PySCF libcint; supplied integrals, not independently regenerated by verifier",
                "overlap": mol.intor("int1e_ovlp").tolist(),
                "kinetic": mol.intor("int1e_kin").tolist(),
                "nuclear_attraction": mol.intor("int1e_nuc").tolist(),
                "electron_repulsion": mol.intor("int2e", aosym="s1").reshape(2, 2, 2, 2).tolist(),
            },
            "state": {
                "density": mf.make_rdm1().tolist(), "mo_coefficients": mf.mo_coeff.tolist(),
                "mo_energies": mf.mo_energy.tolist(), "mo_occupations": mf.mo_occ.tolist(),
                "nuclear_repulsion_energy": nuclear_energy,
                "electronic_energy": energy-nuclear_energy, "total_energy": energy,
            },
            "scf": {
                "converged": bool(mf.converged), "cycles": int(mf.cycles),
                "max_cycles": mf.max_cycle, "energy_tolerance": mf.conv_tol,
                "gradient_tolerance": mf.conv_tol_grad, "cycle_history": history,
                "initial_guess": "PySCF default minao", "requested_omp_threads": 1,
                "reported_omp_threads": int(lib.num_threads()),
            },
            "versions": {"python": platform.python_version(), "numpy": np.__version__,
                         "scipy": scipy.__version__, "pyscf": pyscf.__version__,
                         "libcint": "separate version not exposed by installed PySCF API"},
            "sources": [
                "https://pyscf.org/user/scf.html",
                "https://pyscf.org/user/gto.html",
                "https://github.com/pyscf/pyscf/tree/v2.11.0",
                "https://www.basissetexchange.org/family_notes/sto/",
                "https://doi.org/10.1063/1.1672392",
                "https://doi.org/10.1063/5.0006074",
            ],
            "limitations": [
                "Floating-point numerical consistency audit; no rigorous interval energy bound.",
                "Both audits share supplied PySCF/libcint AO integrals; a common integral error can survive.",
                "RHF/STO-3G is an approximate molecular model, not the exact physical energy or experiment.",
                "No inference of novelty, chemical accuracy, or global equilibrium geometry is made.",
            ],
        }
    certificate["verification"] = verify_h2_rhf_certificate(certificate)
    certificate["status"] = "verified_numerical_consistency" if certificate["verification"]["valid"] else "verification_failed"
    certificate = {"schema": certificate.pop("schema"),
                   "status": certificate.pop("status"), **certificate}
    if len(json.dumps(certificate, allow_nan=False).encode()) > MAX_CERTIFICATE_BYTES:
        raise ValueError("certificate exceeds 48 KiB")
    return certificate


def h2_rhf_certificate_tool(query: str) -> str:
    """Native tool: JSON in, JSON out, including machine-readable errors."""
    try:
        return json.dumps(produce_h2_rhf_certificate(query), allow_nan=False, separators=(",", ":"))
    except Exception as exc:
        return json.dumps({"schema": SCHEMA, "status": "error", "error": str(exc),
                           "input_format": '{"distance_angstrom":"0.74"} OR {"distance_bohr":"1.4"}'})
