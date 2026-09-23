"""Extended scientific tools for Atlas — AstroPy, PySCF, ASE, PyMatGen, BioPython.

Designed to be loaded after the legacy registry: each tool is a small wrapper
that returns a plain string so the Atlas worker → A.M.Y protocol stays simple.

Every tool follows the same contract:
- input: a single colon-delimited string (parsed inside the wrapper)
- output: human-readable text (LLM-friendly)
- on error: returns a helpful "Error: ..." string with the expected format
"""
from __future__ import annotations


# ── AstroPy: real astronomy calculations ──────────────────────────────────────

def astropy_constants(query: str) -> str:
    """Look up a fundamental physics constant.
    Format: 'name' (e.g. 'G', 'c', 'h', 'k_B', 'M_sun', 'R_earth').
    """
    from astropy import constants as const
    from astropy import units as u

    name = query.strip()
    try:
        c = getattr(const, name)
        return (f"Constant {name}: {c.value:.6e} {c.unit}\n"
                f"Reference: {c.reference}\n"
                f"Uncertainty: {c.uncertainty:.3e}")
    except AttributeError:
        examples = "G, c, h, hbar, k_B, e, m_e, m_p, M_sun, R_sun, L_sun, M_earth, R_earth, au, pc, ly"
        return f"Error: Unknown constant '{name}'. Examples: {examples}"


def astropy_unit_convert(query: str) -> str:
    """Convert between astronomical units.
    Format: 'value:from_unit:to_unit' (e.g. '1:pc:lyr', '5000:K:eV').
    """
    from astropy import units as u
    import math

    parts = query.split(":")
    if len(parts) != 3:
        return "Error: Format should be 'value:from_unit:to_unit'. Example: '1:pc:lyr'"
    try:
        value = float(parts[0])
        if not math.isfinite(value):
            raise ValueError("unit conversion requires a finite value")
        from_u = u.Unit(parts[1].strip())
        to_u = u.Unit(parts[2].strip())
        result = (value * from_u).to(to_u, equivalencies=u.spectral() + u.temperature_energy())
        if not math.isfinite(float(result.value)):
            raise ValueError("converted value is non-finite")
        return f"{value} {from_u} = {result.value:.6g} {to_u}"
    except Exception as e:
        return f"Error: {e}. Examples: '1:pc:lyr', '5000:K:eV', '1:au:km'"


def astropy_cosmology(query: str) -> str:
    """Compute cosmological distances using Planck18.
    Format: 'operation:redshift' where operation ∈ {luminosity_distance, comoving_distance,
    angular_diameter_distance, lookback_time, age}. Example: 'luminosity_distance:1.0'.
    """
    from astropy.cosmology import Planck18 as cosmo
    import astropy.units as u

    parts = query.split(":")
    if len(parts) != 2:
        return ("Error: Format 'operation:redshift'. Operations: luminosity_distance, "
                "comoving_distance, angular_diameter_distance, lookback_time, age")
    op, z_str = parts[0].strip(), parts[1].strip()
    try:
        z = float(z_str)
        if op == "luminosity_distance":
            r = cosmo.luminosity_distance(z)
        elif op == "comoving_distance":
            r = cosmo.comoving_distance(z)
        elif op == "angular_diameter_distance":
            r = cosmo.angular_diameter_distance(z)
        elif op == "lookback_time":
            r = cosmo.lookback_time(z)
        elif op == "age":
            r = cosmo.age(z)
        else:
            return f"Error: Unknown operation '{op}'. See docstring."
        return (f"Planck18 cosmology, {op} at z={z}:\n"
                f"  {r:.4f}\n"
                f"  H_0 = {cosmo.H0:.3f}, Omega_m = {cosmo.Om0:.4f}, Omega_L = {cosmo.Ode0:.4f}")
    except Exception as e:
        return f"Error: {e}"


def astropy_blackbody(query: str) -> str:
    """Planck blackbody spectrum and Stefan-Boltzmann luminosity.
    Format: 'temperature_K' (e.g. '5778' for Sun).
    """
    from astropy.modeling.physical_models import BlackBody
    from astropy import units as u
    from astropy import constants as const
    import numpy as np

    try:
        T = float(query.strip()) * u.K
        bb = BlackBody(temperature=T)
        peak_wave = (2.898e-3 / T.value) * u.m
        peak_freq = (5.879e10 * T.value) * u.Hz
        luminosity_per_area = (const.sigma_sb * T**4).to(u.W / u.m**2)
        return (f"Blackbody spectrum at T = {T}:\n"
                f"  Wien peak wavelength: {peak_wave.to(u.nm):.2f}\n"
                f"  Wien peak frequency: {peak_freq.to(u.THz):.2f}\n"
                f"  Stefan-Boltzmann emittance: {luminosity_per_area:.4e}")
    except Exception as e:
        return f"Error: {e}. Expected a number (temperature in Kelvin)."


# ── Millennium Prize Problems Certificates ────────────────────────────────────

def riemann_zeta_certificate(query: str) -> str:
    from .millennium_tools import riemann_zeta_certificate as rzc
    return rzc(query)


def bsd_elliptic_certificate(query: str) -> str:
    from .millennium_tools import bsd_elliptic_certificate as bec
    return bec(query)


def p_vs_np_complexity_certificate(query: str) -> str:
    from .millennium_tools import p_vs_np_complexity_certificate as pvc
    return pvc(query)


def yang_mills_lattice_certificate(query: str) -> str:
    from .millennium_tools import yang_mills_lattice_certificate as ymc
    return ymc(query)


def hodge_variety_certificate(query: str) -> str:
    from .millennium_tools import hodge_variety_certificate as hvc
    return hvc(query)


def lean4_prove_certificate(query: str) -> str:
    from .millennium_tools import lean4_prove_certificate as l4c
    return l4c(query)


# ── PySCF: real quantum chemistry ─────────────────────────────────────────────

def h2_rhf_certificate(query: str) -> str:
    """Return the full H2 RHF/STO-3G calculation and its independent NumPy audit."""
    from .h2_rhf_certificate import h2_rhf_certificate_tool
    return h2_rhf_certificate_tool(query)


def pyscf_hf_energy(query: str) -> str:
    """Run Hartree-Fock SCF on a small molecule.
    Format: 'atoms;basis' where atoms is 'H 0 0 0;H 0 0 0.74' and basis is e.g. 'sto-3g', '6-31g'.
    Default basis: sto-3g. Example: 'H 0 0 0;H 0 0 0.74'.
    """
    try:
        from pyscf import gto, scf
    except ImportError:
        return "Error: PySCF not available in this environment."

    parts = query.split(";basis=")
    atoms_str = parts[0].strip()
    basis = parts[1].strip() if len(parts) > 1 else "sto-3g"

    try:
        mol = gto.Mole()
        mol.atom = atoms_str
        mol.basis = basis
        mol.verbose = 0
        mol.build()
        mf = scf.RHF(mol)
        mf.verbose = 0
        e = mf.kernel()
        homo = mf.mo_energy[mol.nelectron // 2 - 1]
        lumo = mf.mo_energy[mol.nelectron // 2]
        return (f"PySCF Hartree-Fock RHF result:\n"
                f"  Atoms: {atoms_str}\n"
                f"  Basis: {basis}\n"
                f"  Total energy: {e:.8f} Ha\n"
                f"  HOMO: {homo:.4f} Ha\n"
                f"  LUMO: {lumo:.4f} Ha\n"
                f"  HOMO-LUMO gap: {(lumo-homo)*27.211386:.4f} eV")
    except Exception as exc:
        return ("Error: " + str(exc) +
                ". Format: 'atom1 x y z; atom2 x y z;basis=sto-3g'. "
                "Example: 'H 0 0 0; H 0 0 0.74'.")


def _polyene_atom_string(n_carbons: int) -> str:
    """Build a simple planar all-trans C_n H_(n+2) geometry for small polyenes."""
    if n_carbons < 4 or n_carbons % 2 != 0:
        raise ValueError("polyene controls require an even carbon count >= 4")
    x = 0.0
    carbon_x = [x]
    for idx in range(n_carbons - 1):
        x += 1.34 if idx % 2 == 0 else 1.46
        carbon_x.append(x)

    atoms = [f"C {x_pos:.3f} 0.000 0.000" for x_pos in carbon_x]
    c_h = 1.09
    for idx, x_pos in enumerate(carbon_x):
        if idx in (0, n_carbons - 1):
            atoms.append(f"H {x_pos:.3f} {c_h:.3f} 0.000")
            atoms.append(f"H {x_pos:.3f} {-c_h:.3f} 0.000")
        else:
            y_pos = c_h if idx % 2 else -c_h
            atoms.append(f"H {x_pos:.3f} {y_pos:.3f} 0.000")
    return "; ".join(atoms)


def pyscf_polyene_hf_gap(query: str) -> str:
    """Run RHF/STO-3G controls for generated linear polyenes.
    Format: '4,6;basis=sto-3g'. Keep n small; this is an independent quantum-chemistry
    sanity check, not a high-quality geometry optimization.
    """
    try:
        from pyscf import gto, scf
    except ImportError:
        return "Error: PySCF not available in this environment."

    parts = query.split(";basis=")
    counts_text = parts[0].strip()
    basis = parts[1].strip() if len(parts) > 1 else "sto-3g"
    try:
        counts = [int(part.strip()) for part in counts_text.replace(" ", "").split(",") if part.strip()]
        if not counts:
            return "Error: Provide carbon counts, e.g. '4,6;basis=sto-3g'"
        invalid = [n for n in counts if n < 4 or n % 2 != 0]
        if invalid:
            return f"Error: PySCF polyene controls require even carbon counts >= 4. Invalid: {invalid}"

        rows = []
        gaps = []
        for n_carbons in counts:
            atoms_str = _polyene_atom_string(n_carbons)
            mol = gto.Mole()
            mol.atom = atoms_str
            mol.basis = basis
            mol.verbose = 0
            mol.build()
            mf = scf.RHF(mol)
            mf.verbose = 0
            energy = float(mf.kernel())
            homo = float(mf.mo_energy[mol.nelectron // 2 - 1])
            lumo = float(mf.mo_energy[mol.nelectron // 2])
            gap_ev = (lumo - homo) * 27.211386
            gaps.append(gap_ev)
            rows.append(
                f"    n={n_carbons}: formula=C{n_carbons}H{n_carbons + 2}; "
                f"total_energy={energy:.8f} Ha; HOMO={homo:.6f} Ha; "
                f"LUMO={lumo:.6f} Ha; HF_gap={gap_ev:.4f} eV; converged={mf.converged}"
            )

        trend = "decreases" if len(gaps) >= 2 and gaps[-1] < gaps[0] else "not_monotone"
        return (
            "PySCF polyene RHF/STO-3G HOMO-LUMO gap controls:\n"
            "  Geometry: rough planar all-trans C_n H_(n+2), alternating C-C distances 1.34/1.46 A, C-H=1.09 A.\n"
            f"  Basis: {basis}\n"
            f"  Carbon counts: {counts}\n"
            "  Observations:\n"
            + "\n".join(rows)
            + "\n"
            f"  HF trend over tested counts: {trend}\n"
            "  Interpretation: RHF/STO-3G orbital gaps are method-dependent and not optical gaps, "
            "but they provide an independent ab initio control on the sign of the length trend."
        )
    except Exception as exc:
        return f"Error: {exc}. Format: '4,6;basis=sto-3g'."


def pyscf_dft_energy(query: str) -> str:
    """Run DFT (B3LYP) on a small molecule.
    Format: same as pyscf_hf_energy. Example: 'O 0 0 0;H 0 0 0.96;H 0.93 0 -0.24'.
    """
    try:
        from pyscf import gto, dft
    except ImportError:
        return "Error: PySCF not available."

    parts = query.split(";basis=")
    atoms_str = parts[0].strip()
    basis = parts[1].strip() if len(parts) > 1 else "sto-3g"

    try:
        mol = gto.Mole()
        mol.atom = atoms_str
        mol.basis = basis
        mol.verbose = 0
        mol.build()
        mf = dft.RKS(mol)
        mf.xc = "b3lyp"
        mf.verbose = 0
        e = mf.kernel()
        return (f"PySCF DFT (B3LYP) result:\n"
                f"  Atoms: {atoms_str}\n"
                f"  Basis: {basis}\n"
                f"  Total energy: {e:.8f} Ha\n"
                f"  Converged: {mf.converged}")
    except Exception as exc:
        return ("Error: " + str(exc) +
                ". Format: 'atom1 x y z; atom2 x y z'. Example: 'O 0 0 0; H 0 0 0.96; H 0.93 0 -0.24'.")


# ── ASE: atomistic simulations ────────────────────────────────────────────────

def ase_optimize(query: str) -> str:
    """Optimize molecular geometry with EMT potential.
    Format: 'molecule_name' from ASE's collection (e.g. 'H2', 'CH4', 'H2O', 'N2', 'CO2').
    """
    try:
        from ase.build import molecule
        from ase.calculators.emt import EMT
        from ase.optimize import BFGS
        import io
    except ImportError:
        return "Error: ASE not available."

    try:
        atoms = molecule(query.strip())
        atoms.calc = EMT()
        e0 = atoms.get_potential_energy()
        # Capture optimizer log
        opt = BFGS(atoms, logfile=None)
        opt.run(fmax=0.05)
        e1 = atoms.get_potential_energy()
        symbols = atoms.get_chemical_symbols()
        positions = atoms.get_positions()
        pos_str = "\n".join(f"  {s}: ({p[0]:.4f}, {p[1]:.4f}, {p[2]:.4f})"
                            for s, p in zip(symbols, positions))
        return (f"ASE EMT geometry optimization of {query}:\n"
                f"  Initial energy: {e0:.6f} eV\n"
                f"  Final energy:   {e1:.6f} eV\n"
                f"  Energy drop:    {(e0-e1):.6f} eV\n"
                f"Optimized positions (Å):\n{pos_str}")
    except Exception as exc:
        return (f"Error: {exc}. "
                f"Try one of: H2, N2, O2, H2O, CO2, CH4, NH3, C2H6, C6H6.")


def ase_thermochemistry(query: str) -> str:
    """Compute ideal-gas thermochemistry for a small molecule (vibrations from EMT).
    Format: 'molecule_name:temperature_K' (e.g. 'H2O:298').
    """
    import math
    import os
    import tempfile

    parts = query.split(":")
    if len(parts) > 2 or not parts[0].strip():
        return "Error: expected 'molecule_name:positive_temperature_K'."
    name = parts[0].strip()
    try:
        T = float(parts[1]) if len(parts) > 1 else 298.15
    except (ValueError, TypeError):
        return "Error: temperature must be a finite positive number in kelvin."
    if not math.isfinite(T) or T <= 0:
        return "Error: temperature must be a finite positive number in kelvin."

    try:
        # ASE's vibration imports require real matplotlib.axes/projections.
        # Loading pyplot while repository stubs are excluded also prevents the
        # local mpl_toolkits stub from shadowing its installed counterpart.
        from .core.real_matplotlib import get_real_pyplot
        get_real_pyplot()
        from ase.build import molecule
        from ase.calculators.emt import EMT
        from ase.vibrations import Vibrations
        from ase.thermochemistry import IdealGasThermo
    except ImportError as exc:
        return f"Error: ASE thermochemistry import failed ({type(exc).__name__}: {exc})."
    except Exception as exc:
        return f"Error: ASE thermochemistry dependency initialization failed ({type(exc).__name__}: {exc})."

    try:
        with tempfile.TemporaryDirectory() as tmp:
            atoms = molecule(name)
            atoms.calc = EMT()
            e_pot = atoms.get_potential_energy()
            # An absolute cache prefix keeps all vibration files inside the
            # temporary directory without changing process-global cwd.
            vib = Vibrations(atoms, name=os.path.join(tmp, "vibrations"))
            vib.run()
            vib_energies = vib.get_energies()
            geometry = "nonlinear" if len(atoms) > 2 else "linear"
            thermo = IdealGasThermo(vib_energies=vib_energies,
                                    geometry=geometry,
                                    potentialenergy=e_pot, atoms=atoms,
                                    symmetrynumber=1, spin=0)
            G = thermo.get_gibbs_energy(temperature=T, pressure=101325, verbose=False)
            if not math.isfinite(float(e_pot)) or not math.isfinite(float(G)):
                return "Error: ASE thermochemistry returned a non-finite energy."
            return (f"ASE thermochemistry for {name} at T={T} K (EMT level):\n"
                    f"  Potential energy: {e_pot:.6f} eV\n"
                    f"  Gibbs free energy: {G:.6f} eV\n"
                    f"  Assumptions: fixed ASE database geometry (not optimized); "
                    f"ideal gas; geometry={geometry} (atom-count heuristic); "
                    f"pressure=101325 Pa; symmetrynumber=1; spin=0.\n"
                    f"  Scope: EMT model calculation, not empirical thermochemistry; "
                    f"geometry, symmetry and spin assumptions are not validated for arbitrary molecules.")
    except Exception as exc:
        return (f"Error: {exc}. "
                f"Try 'H2O:298', 'CH4:500', 'N2:1000'.")


# ── PyMatGen: real materials science ──────────────────────────────────────────

def pymatgen_structure(query: str) -> str:
    """Get crystal-structure properties for common materials.
    Format: 'material' (e.g. 'Si', 'NaCl', 'TiO2'). Reports the cell convention.
    Fixed illustrative lattice parameters, not an optimization or measurement.
    """
    try:
        from pymatgen.core import Lattice, Structure, Composition
    except ImportError:
        return "Error: PyMatGen not available."

    name = query.strip()
    try:
        templates = {
            "Si": ("diamond", 5.431, ["Si", "Si"], [[0,0,0],[0.25,0.25,0.25]]),
            "NaCl": ("rocksalt", 5.640, ["Na","Cl"], [[0,0,0],[0.5,0.5,0.5]]),
            "TiO2": ("rutile", 4.594, ["Ti","Ti","O","O","O","O"],
                     [[0,0,0],[0.5,0.5,0.5],[0.305,0.305,0],[0.695,0.695,0],
                      [0.195,0.805,0.5],[0.805,0.195,0.5]]),
            "Cu": ("fcc", 3.615, ["Cu","Cu","Cu","Cu"],
                   [[0,0,0],[0.5,0.5,0],[0.5,0,0.5],[0,0.5,0.5]]),
        }
        if name not in templates:
            return f"Error: Unknown material '{name}'. Available: {', '.join(templates)}."
        kind, a, species, coords = templates[name]
        if name in {"Si", "NaCl"}:
            # Two atoms belong to an fcc primitive cell, volume a^3/4,
            # rather than a conventional cube (which has eight atoms).
            # AFLOW A_cF8_227_a-001 and AB_cF8_225_a_b-001.
            lat = Lattice([[0, a/2, a/2], [a/2, 0, a/2], [a/2, a/2, 0]])
            cell = "fcc primitive (a labels the conventional cubic lattice constant)"
        elif name == "TiO2":
            # Rutile is tP6 with independent a,c parameters, not cubic.
            # AFLOW A2B_tP6_136_f_a-001; c is an explicit model parameter.
            lat = Lattice.tetragonal(a, 2.958)
            cell = "tetragonal primitive; c = 2.9580 Å (fixed model parameter)"
        else:
            lat = Lattice.cubic(a)
            cell = "fcc conventional cubic"
        struct = Structure(lat, species, coords)
        comp = Composition.from_dict({s: species.count(s) for s in set(species)})
        return (f"PyMatGen structure of {name} ({kind}):\n"
                f"  Composition: {comp.formula} (reduced: {comp.reduced_formula})\n"
                f"  Lattice constant: a = {a:.4f} Å\n"
                f"  Cell: {cell}\n"
                f"  Volume: {struct.volume:.4f} Å³\n"
                f"  Number of sites: {struct.num_sites}\n"
                f"  Density: {struct.density:.4f} g/cm³\n"
                "  Fixed prototype model; not a measured or optimized structure.")
    except Exception as exc:
        return f"Error: {exc}"


# ── Tool descriptor list — Atlas registry consumes this ───────────────────────

EXTENDED_TOOLS = [
    {
        "name": "astropy_constants",
        "domain": "physics",
        "description": "Look up fundamental physical/astronomical constants (G, c, h, M_sun, etc) with CODATA reference and uncertainty.",
        "function": astropy_constants,
        "input_format": "constant_name (e.g. 'G', 'c', 'M_sun')",
        "output_format": "value, unit, reference, uncertainty",
        "evidence_grade": "real_local",
    },
    {
        "name": "astropy_unit_convert",
        "domain": "physics",
        "description": "Convert between astronomical units (parsec↔light-year, eV↔Kelvin, AU↔km, etc).",
        "function": astropy_unit_convert,
        "input_format": "value:from_unit:to_unit",
        "output_format": "converted_value with unit",
        "evidence_grade": "real_local",
    },
    {
        "name": "astropy_cosmology",
        "domain": "astronomy",
        "description": "Compute cosmological distances and ages at redshift z using Planck18 parameters.",
        "function": astropy_cosmology,
        "input_format": "operation:redshift",
        "output_format": "distance/time with H_0, Omega_m, Omega_L context",
        "evidence_grade": "real_local",
    },
    {
        "name": "astropy_blackbody",
        "domain": "astronomy",
        "description": "Planck blackbody peak wavelength, peak frequency, and Stefan-Boltzmann emittance at given temperature.",
        "function": astropy_blackbody,
        "input_format": "temperature_K (e.g. '5778' for Sun)",
        "output_format": "Wien peaks + Stefan-Boltzmann emittance",
        "evidence_grade": "real_local",
    },
    {
        "name": "h2_rhf_certificate",
        "domain": "chemistry",
        "description": (
            "Compute fixed neutral-singlet H2 RHF/STO-3G at an explicit distance, "
            "including full AO integrals, density, orbitals, convergence and an independent "
            "NumPy energy/normalization/idempotence/residual/bonding-orbital audit. "
            "JSON input exactly one distance_angstrom or distance_bohr; allowed range "
            "0.3..4 angstrom. Output JSON <=48 KiB. Shared PySCF/libcint integrals; "
            "numerical consistency only, not an exact physical energy, interval bound or novelty claim."
        ),
        "function": h2_rhf_certificate,
        "input_format": '{"distance_angstrom":"0.74"} OR {"distance_bohr":"1.4"}',
        "output_format": "JSON calculation, metadata, integrals, SCF state and independent audit",
        "evidence_grade": "real_local",
    },
    {
        "name": "pyscf_hf_energy",
        "domain": "chemistry",
        "description": "Compute Hartree-Fock total energy, HOMO/LUMO, and HOMO-LUMO gap for a molecule. Real ab initio quantum chemistry.",
        "function": pyscf_hf_energy,
        "input_format": "'atom1 x y z; atom2 x y z;basis=sto-3g'",
        "output_format": "total energy (Ha), HOMO, LUMO, gap (eV)",
        "evidence_grade": "real_local",
    },
    {
        "name": "pyscf_polyene_hf_gap",
        "domain": "chemistry",
        "description": "Generate small linear polyene geometries and compute RHF/STO-3G HOMO-LUMO gaps. Input: '4,6;basis=sto-3g'.",
        "function": pyscf_polyene_hf_gap,
        "input_format": "comma-separated even carbon counts plus optional ;basis=sto-3g",
        "output_format": "per-polyene total energy, HOMO, LUMO, gap (eV), convergence",
        "evidence_grade": "real_local",
    },
    {
        "name": "pyscf_dft_energy",
        "domain": "chemistry",
        "description": "Compute B3LYP DFT total energy for a molecule. More accurate than HF for chemistry.",
        "function": pyscf_dft_energy,
        "input_format": "'atom1 x y z; atom2 x y z;basis=sto-3g'",
        "output_format": "total energy (Ha) + convergence",
        "evidence_grade": "real_local",
    },
    {
        "name": "ase_optimize",
        "domain": "chemistry",
        "description": "Optimize molecular geometry with EMT potential. Returns final positions and energy drop.",
        "function": ase_optimize,
        "input_format": "molecule_name from ASE collection (H2, H2O, CH4, ...)",
        "output_format": "initial/final energy + optimized positions",
        "evidence_grade": "real_local",
    },
    {
        "name": "ase_thermochemistry",
        "domain": "chemistry",
        "description": "Compute ideal-gas Gibbs free energy at given temperature using EMT vibrations.",
        "function": ase_thermochemistry,
        "input_format": "molecule_name:temperature_K",
        "output_format": "potential energy + Gibbs free energy",
        "evidence_grade": "real_local",
    },
    {
        "name": "pymatgen_structure",
        "domain": "materials_science",
        "description": "Get crystal-structure properties (composition, lattice, volume, density) for common materials.",
        "function": pymatgen_structure,
        "input_format": "material_name (Si, NaCl, TiO2, Cu)",
        "output_format": "composition, lattice constant, volume, density",
        "evidence_grade": "real_local",
    },
    {
        "name": "riemann_zeta_certificate",
        "domain": "mathematics",
        "description": "Certified numerical and analytical probe for the Riemann Hypothesis. Evaluate zeta zeros on critical line, sample Z(t), test Li's criterion lambda_n > 0, or probe off-line values. Input JSON string.",
        "function": riemann_zeta_certificate,
        "input_format": '{"zeros_index": [1, 2]} OR {"li_criterion_n": 5} OR {"sample_line": {"t_start": 10, "t_end": 30}}',
        "output_format": "JSON with exact zeros, critical line alignment, Li coefficient, and SHA-256 certificate",
        "evidence_grade": "real_local",
    },
    {
        "name": "bsd_elliptic_certificate",
        "domain": "mathematics",
        "description": "Certified arithmetic analysis of elliptic curves E/Q: y^2 = x^3 + Ax + B for Birch and Swinnerton-Dyer conjecture. Computes discriminant, j-invariant, bad primes, torsion subgroup, Frobenius traces a_p, and real period. Input JSON string.",
        "function": bsd_elliptic_certificate,
        "input_format": '{"A": -1, "B": 0, "primes_limit": 50}',
        "output_format": "JSON invariants, torsion structure, partial BSD Euler product, and certificate hash",
        "evidence_grade": "real_local",
    },
    {
        "name": "p_vs_np_complexity_certificate",
        "domain": "mathematics",
        "description": "Certified Boolean complexity analyzer for P versus NP. Exact DPLL solver with decision tree metrics, random 3-SAT phase transition generation, polynomial-time certificate verification, and theoretical barriers. Input JSON string.",
        "function": p_vs_np_complexity_certificate,
        "input_format": '{"random_3sat": {"n_vars": 16, "alpha": 4.26, "seed": 42}} OR {"clauses": [[1, -2], [-1, 2]]}',
        "output_format": "JSON SAT/UNSAT status, decision tree nodes explored, poly-time verification, barrier notes",
        "evidence_grade": "real_local",
    },
    {
        "name": "yang_mills_lattice_certificate",
        "domain": "physics",
        "description": "Certified non-perturbative SU(2) Euclidean lattice gauge theory probe for Yang-Mills Mass Gap. Wilson plaquette action, Creutz ratios, string tension sigma, and glueball mass gap Delta > 0. Input JSON string.",
        "function": yang_mills_lattice_certificate,
        "input_format": '{"lattice_size": [4, 4, 4, 4], "beta": 2.3, "n_sweeps": 50, "thermalization": 15}',
        "output_format": "JSON average plaquette, Wilson loops, string tension, estimated mass gap Delta, and certificate hash",
        "evidence_grade": "real_local",
    },
    {
        "name": "hodge_variety_certificate",
        "domain": "mathematics",
        "description": "Certified complex algebraic geometry probe for the Hodge Conjecture. Computes Hodge diamond, Betti numbers, rational Hodge classes, Lefschetz (1,1) verification, and Shioda character conditions for Fermat varieties and Calabi-Yau/K3 manifolds. Input JSON string.",
        "function": hodge_variety_certificate,
        "input_format": '{"variety_type": "k3_surface"} OR {"variety_type": "fermat_hypersurface", "dimension": 2, "degree": 4}',
        "output_format": "JSON Hodge diamond, Betti numbers, Euler char, rational Hodge class dimensions, and status",
        "evidence_grade": "real_local",
    },
    {
        "name": "lean4_prove_certificate",
        "domain": "mathematics",
        "description": (
            "Formal interactive theorem prover using the Lean 4 kernel. Formulates lemmas, "
            "verifies type theory proofs, and checks mathematical hypotheses for the Millennium Problems "
            "(RH, BSD, P vs NP, Yang-Mills, Hodge). Rejects unproven goals and 'sorry'. "
            "Input JSON: {'theorem_name': str, 'lean_code': str}."
        ),
        "function": lean4_prove_certificate,
        "input_format": '{"theorem_name": "mod24_residues", "lean_code": "theorem res : ∀ r : Fin 24, ... := by decide"}',
        "output_format": "JSON proof status, verified_by_lean_kernel, AST errors/diagnostics, and certificate hash",
        "evidence_grade": "real_local",
    },
]


def register_extended_tools(registry):
    """Register all extended tools into an Atlas DynamicToolRegistry."""
    try:
        from app.run_agent_with_tools_legacy import ToolDescriptor
    except ImportError:
        try:
            from run_agent_with_tools import ToolDescriptor
        except ImportError:
            return 0

    from .population_selection_certificate import TOOL_DESCRIPTOR
    count = 0
    for spec in [*EXTENDED_TOOLS, TOOL_DESCRIPTOR]:
        registry.register_tool(ToolDescriptor(
            name=spec["name"],
            domain=spec["domain"],
            description=spec["description"],
            function=spec["function"],
            input_format=spec["input_format"],
            output_format=spec["output_format"],
            evidence_grade=spec.get("evidence_grade", "heuristic")
        ))
        count += 1
    return count
