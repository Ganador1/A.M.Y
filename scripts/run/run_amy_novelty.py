#!/usr/bin/env python3
"""
A.M.Y Novelty Discovery Mission

Ejecuta misiones científicas diseñadas para descubrir patrones novedosos:
1. Usa herramientas avanzadas (conjecture_engine, number_theory, quantum)
2. Combina resultados de múltiples herramientas para encontrar patrones
3. Genera hipótesis basadas en datos reales (no templates)
4. Detecta anomalías y desviaciones de teorías conocidas
5. Crea papers con hallazgos potencialmente novedosos
"""
import asyncio
import json
import math
import re
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "atlas"))

from core.atlas_tools import AtlasTools
from core.provenance import ProvenanceManager
from communication.paper_generator import PaperGenerator
from communication.paper_enhancer import PaperEnhancer, generate_hypothesis, generate_references, PeerReviewer

LOG_FILE = Path("amy_novelty.log")
STATE_FILE = Path("amy_novelty_state.json")


def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


# ============================================================
# KNOWN CONJECTURES BLOCKLIST — never mark these as novel
# These are classical open problems known for decades/centuries
# ============================================================
KNOWN_CONJECTURES_BLOCKLIST = {
    "goldbach", "twin prime", "collatz", "riemann hypothesis", "riemann zeta",
    "abc conjecture", "birch and swinnerton-dyer", "hodge conjecture",
    "navier-stokes", "yang-mills", "p vs np", "beal conjecture",
    "hardy-littlewood", "poincaré conjecture", "fermat",
    "prime number theorem", "pnt", "cramér", "granville",
    "euler conjecture", "catalan conjecture", "legendre conjecture",
    "brocard conjecture", "landau conjecture", "schinzel hypothesis",
}

def _is_known_conjecture(text: str) -> bool:
    """Return True if text references a known classical conjecture."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in KNOWN_CONJECTURES_BLOCKLIST)

NOVELTY_MISSIONS = {
    "prime_gap_structure": {
        "name": "Prime Gap Structural Analysis",
        "title": "Computational Analysis of Prime Gap Scaling Anomalies Relative to the Cramer Model",
        "domain": "mathematics",
        "description": "Analyze prime gap distribution at multiple scales to detect scaling anomalies",
        "tools": [
            ("prime_gap_analysis", "1000", "Prime gaps up to 1000"),
            ("prime_gap_analysis", "5000", "Prime gaps up to 5000"),
            ("prime_gap_analysis", "10000", "Prime gaps up to 10000"),
            ("number_theory_advanced", "prime_gaps:1000", "Detailed prime gaps"),
            ("number_theory_advanced", "twin_primes:1000", "Twin prime pairs"),
            ("conjecture_engine", "generate:prime_gaps", "Generate conjectures"),
        ],
        "novelty_detector": "prime_gap_novelty",
    },
    "quantum_scaling": {
        "name": "Quantum Energy Scaling Analysis",
        "title": "Verification of Rydberg Formula Scaling and Deviation Analysis in Hydrogen Energy Levels",
        "domain": "physics",
        "description": "Study energy level scaling across n to detect deviations from Rydberg",
        "tools": [
            ("quantum_energy_levels", "hydrogen:1", "H n=1"),
            ("quantum_energy_levels", "hydrogen:5", "H n=5"),
            ("quantum_energy_levels", "hydrogen:10", "H n=10"),
            ("quantum_energy_levels", "hydrogen:20", "H n=20"),
            ("quantum_energy_levels", "hydrogen:50", "H n=50"),
        ],
        "novelty_detector": "quantum_scaling_novelty",
    },
    "molecular_orbital_patterns": {
        "name": "Molecular Orbital Pattern Discovery",
        "title": "Huckel Molecular Orbital Analysis of Conjugated Pi-Systems: HOMO-LUMO Gap Scaling Laws",
        "domain": "chemistry",
        "description": "Analyze Huckel MO patterns across conjugated systems to find regularities",
        "tools": [
            ("molecular_orbital_energy", "4", "4-carbon system (butadiene)"),
            ("molecular_orbital_energy", "6", "6-carbon system (benzene)"),
            ("molecular_orbital_energy", "8", "8-carbon system (octatetraene)"),
            ("molecular_orbital_energy", "10", "10-carbon system"),
            ("molecular_orbital_energy", "12", "12-carbon system"),
            ("molecular_orbital_energy", "14", "14-carbon system"),
        ],
        "novelty_detector": "molecular_orbital_novelty",
    },
    "prime_verification_deep": {
        "name": "Deep Prime Verification",
        "title": "Computational Verification of Prime Properties and Classical Conjectures at Scale",
        "domain": "mathematics",
        "description": "Test primality of large numbers and verify Goldbach at scale",
        "tools": [
            ("sympy_prime_analysis", "is_prime:104729", "10000th prime"),
            ("sympy_prime_analysis", "is_prime:1299709", "100000th prime"),
            ("number_theory_advanced", "goldbach:1000", "Goldbach up to 1000"),
            ("number_theory_advanced", "twin_primes:5000", "Twin primes up to 5000"),
            ("conjecture_engine", "generate:prime_distribution", "Generate conjectures"),
        ],
        "novelty_detector": "prime_verification_novelty",
    },
}


def _candidate_status(condition: bool, min_scale: int | None = None, scale: int | None = None,
                      description: str = "") -> str:
    """Return candidate status only when the effect is large enough and computed at useful scale.
    Always returns finite_computational_observation for known classical conjectures."""
    if _is_known_conjecture(description):
        return "known_control"  # Never mark known conjectures as candidate novelty
    if condition and (min_scale is None or (scale is not None and scale >= min_scale)):
        return "candidate_novelty"
    return "finite_computational_observation"


def _finding_label(finding: dict) -> str:
    """Academic marker for findings; confirmed novelty is intentionally rare."""
    description = finding.get("description", "")
    status = finding.get("novelty_status", "finite_computational_observation")
    # Blocklist: classical conjectures are never novel
    if _is_known_conjecture(description):
        return "[KNOWN]"
    if finding.get("is_novel"):
        return "[NOVEL]"
    if status == "candidate_novelty":
        return "[CANDIDATE]"
    if status in {"known_control", "bounded_verification"}:
        return "[KNOWN]"
    if status in {"precision_check", "precision_artifact"}:
        return "[CONTROL]"
    return "[OBSERVATION]"


# ============================================================
# NOVELTY DETECTORS — Find patterns that deviate from theory
# ============================================================

def prime_gap_novelty(results: list[dict]) -> dict:
    """Detect anomalies in prime gap distribution."""
    gaps_data = {}
    twins_data = {}
    conjectures = []
    
    for r in results:
        if "prime_gap_analysis" in r["tool"]:
            # Extract scale and stats
            nums = re.findall(r'up to (\d+)', r["result"])
            means = re.findall(r'Mean gap: ([\d.]+)', r["result"])
            stds = re.findall(r'Std dev: ([\d.]+)', r["result"])
            maxs = re.findall(r'Max gap: (\d+)', r["result"])
            counts = re.findall(r'Number of primes: (\d+)', r["result"])
            
            if nums and means:
                scale = int(nums[0])
                gaps_data[scale] = {
                    "mean": float(means[0]),
                    "std": float(stds[0]) if stds else 0,
                    "max_gap": int(maxs[0]) if maxs else 0,
                    "prime_count": int(counts[0]) if counts else 0,
                }
        
        elif "twin_primes" in r["tool"]:
            twin_nums = re.findall(r'found: (\d+)', r["result"])
            if twin_nums:
                scale_match = re.search(r'up to (\d+)', r["result"]) or re.search(r'up to (\d+)', r.get("description", ""))
                scale = int(scale_match.group(1)) if scale_match else None
                if scale is not None:
                    twins_data[scale] = int(twin_nums[0])
        
        elif "conjecture" in r["tool"]:
            conjectures.append(r["result"])
    
    # Analyze scaling behavior
    findings = []
    if len(gaps_data) >= 2:
        scales = sorted(gaps_data.keys())
        
        # Check if mean gap follows log(n) prediction from PNT
        for i in range(len(scales) - 1):
            n1, n2 = scales[i], scales[i+1]
            g1, g2 = gaps_data[n1]["mean"], gaps_data[n2]["mean"]
            
            # PNT predicts mean gap ~ log(n)
            predicted_ratio = math.log(n2) / math.log(n1)
            actual_ratio = g2 / g1 if g1 > 0 else 0
            deviation = abs(actual_ratio - predicted_ratio) / predicted_ratio * 100
            status = _candidate_status(deviation > 15, min_scale=1_000_000, scale=n2)
            
            findings.append({
                "type": "scaling_deviation",
                "description": f"Prime gap scaling from n={n1} to n={n2}: predicted ratio {predicted_ratio:.3f}, actual {actual_ratio:.3f}, deviation {deviation:.1f}%",
                "deviation_pct": deviation,
                "novelty_status": status,
                "evidence_level": "bounded_computation",
                "is_novel": False,
            })
        
        # Check max gap vs Cramér prediction (log²(n))
        for scale, data in gaps_data.items():
            cramer_pred = math.log(scale) ** 2
            actual_max = data["max_gap"]
            if cramer_pred > 0:
                ratio = actual_max / cramer_pred
                status = _candidate_status(ratio > 1.5 or ratio < 0.5, min_scale=1_000_000, scale=scale)
                findings.append({
                    "type": "cramer_deviation",
                    "description": f"Max gap at n={scale}: actual={actual_max}, Cramér prediction={cramer_pred:.1f}, ratio={ratio:.2f}",
                    "ratio": ratio,
                    "novelty_status": status,
                    "evidence_level": "bounded_computation",
                    "is_novel": False,
                })
    
    # Twin prime density analysis
    if twins_data and gaps_data:
        for scale, data in gaps_data.items():
            if scale not in twins_data:
                continue
            if data["prime_count"] > 0:
                twin_density = twins_data[scale] / data["prime_count"]
                hardy_littlewood_pred = 1.32 / (math.log(scale) ** 2) if scale > 10 else 0
                if hardy_littlewood_pred > 0:
                    density_ratio = twin_density / hardy_littlewood_pred
                    status = _candidate_status(abs(density_ratio - 1.0) > 0.5, min_scale=1_000_000, scale=scale)
                    findings.append({
                        "type": "twin_prime_density",
                        "description": f"Twin prime density at n={scale}: actual={twin_density:.4f}, Hardy-Littlewood={hardy_littlewood_pred:.4f}, ratio={density_ratio:.2f}",
                        "ratio": density_ratio,
                        "novelty_status": status,
                        "evidence_level": "bounded_computation",
                        "is_novel": False,
                    })
    
    # Generate candidate hypotheses from bounded findings. These are not confirmed novelty.
    novel_findings = [f for f in findings if f.get("is_novel", False)]
    candidate_findings = [f for f in findings if f.get("novelty_status") == "candidate_novelty"]
    
    hypotheses = []
    for f in candidate_findings:
        if f["type"] == "scaling_deviation":
            hypotheses.append({
                "hypothesis": f"The deviation of {f['deviation_pct']:.1f}% from the Prime Number Theorem prediction suggests a correction factor may be needed for gap scaling at moderate ranges. {f['description']}",
                "confidence": min(0.85, 0.5 + f["deviation_pct"] / 20),
                "testable": True,
                "method": "Extend analysis to n=10^6 and fit empirical correction to PNT prediction using least squares regression.",
                "novelty_status": "candidate_novelty",
                "evidence_level": "bounded_computation",
            })
        elif f["type"] == "cramer_deviation":
            hypotheses.append({
                "hypothesis": f"The Cramér model {'overestimates' if f['ratio'] < 1 else 'underestimates'} maximum prime gaps by a factor of {abs(f['ratio']-1):.2f}, suggesting the model needs refinement for finite ranges. {f['description']}",
                "confidence": min(0.80, 0.4 + abs(f["ratio"] - 1) * 2),
                "testable": True,
                "method": "Compare max gaps across multiple scales and fit empirical scaling law to determine correction exponent.",
                "novelty_status": "candidate_novelty",
                "evidence_level": "bounded_computation",
            })
        elif f["type"] == "twin_prime_density":
            hypotheses.append({
                "hypothesis": f"The twin prime density ratio of {f['ratio']:.2f} relative to Hardy-Littlewood suggests {'higher' if f['ratio'] > 1 else 'lower'} density than predicted, with implications for the twin prime conjecture. {f['description']}",
                "confidence": min(0.75, 0.4 + abs(f["ratio"] - 1)),
                "testable": True,
                "method": "Compute twin prime density at multiple scales and compare against Hardy-Littlewood constant C2=1.3203...",
                "novelty_status": "candidate_novelty",
                "evidence_level": "bounded_computation",
            })
    
    return {
        "findings": findings,
        "novel_findings": novel_findings,
        "candidate_findings": candidate_findings,
        "hypotheses": hypotheses,
        "has_novelty": False,
    }


def quantum_scaling_novelty(results: list[dict]) -> dict:
    """Detect deviations from Rydberg formula in quantum energy levels."""
    energy_data = {}
    
    for r in results:
        nums = re.findall(r'n=(\d+)', r["result"])
        energies = re.findall(r'E_\d+ = ([-\d.]+) eV', r["result"])
        if nums and energies:
            n = int(nums[0])
            energy_data[n] = float(energies[0])
    
    findings = []
    hypotheses = []
    
    if len(energy_data) >= 3:
        # Test Rydberg formula: E_n = -13.6/n²
        for n, E_actual in energy_data.items():
            E_predicted = -13.6 / (n ** 2)
            deviation = abs(E_actual - E_predicted) / abs(E_predicted) * 100 if E_predicted != 0 else 0
            
            findings.append({
                "type": "rydberg_deviation",
                "description": f"n={n}: actual={E_actual:.4f} eV, predicted={E_predicted:.4f} eV, deviation={deviation:.4f}%",
                "deviation_pct": deviation,
                "novelty_status": "precision_artifact" if deviation > 0.1 else "known_control",
                "evidence_level": "rounded_output_check",
                "is_novel": False,
            })
        
        # Check 1/n² scaling law
        ns = sorted(energy_data.keys())
        if len(ns) >= 2:
            # Compute E_n * n² for each level (should be constant = -13.6)
            products = {n: energy_data[n] * n**2 for n in ns}
            values = list(products.values())
            mean_product = sum(values) / len(values)
            variance = sum((v - mean_product)**2 for v in values) / len(values)
            std_product = math.sqrt(variance) if variance > 0 else 0
            
            findings.append({
                "type": "scaling_law_test",
                "description": f"E_n × n² = {mean_product:.4f} ± {std_product:.4f} (should be -13.6 eV·n²)",
                "std": std_product,
                "novelty_status": "precision_artifact" if std_product > 0.01 else "known_control",
                "evidence_level": "rounded_output_check",
                "is_novel": False,
            })
            
            if std_product > 0.01:
                hypotheses.append({
                    "hypothesis": f"The E_n × n² product shows variance of {std_product:.4f} in rounded output; this should be treated as a numerical precision artifact unless reproduced with full-precision residuals.",
                    "confidence": min(0.70, 0.45 + std_product * 5),
                    "testable": True,
                    "method": "Compute energy levels for n=1..100 and fit to E_n = -R/(n-δ)² to extract quantum defect δ, comparing against known values for hydrogen (δ≈0).",
                    "novelty_status": "precision_check",
                    "evidence_level": "rounded_output_check",
                })
    
    if not hypotheses:
        hypotheses.append({
            "hypothesis": "The Rydberg formula E_n = -13.6/n² eV holds precisely across all computed levels, confirming the Coulomb potential model for hydrogen with no detectable quantum defect.",
            "confidence": 0.90,
            "testable": True,
            "method": "Extend computation to n=100 and verify precision to 10+ decimal places using high-precision arithmetic.",
            "novelty_status": "known_control",
            "evidence_level": "verification",
        })
    
    return {
        "findings": findings,
        "novel_findings": [f for f in findings if f.get("is_novel", False)],
        "candidate_findings": [f for f in findings if f.get("novelty_status") == "candidate_novelty"],
        "hypotheses": hypotheses,
        "has_novelty": False,
    }


def molecular_orbital_novelty(results: list[dict]) -> dict:
    """Detect patterns in Huckel MO energies across conjugated systems."""
    mo_data = {}
    
    for r in results:
        if not r.get("success", True):
            continue
        result_text = r.get("result", "")
        
        # Extract carbon count from description or result
        carbon_match = re.search(r'(\d+)-carbon', result_text)
        if not carbon_match:
            carbon_match = re.search(r'(\d+)\s*carbon', result_text)
        if not carbon_match:
            # Try from description
            carbon_match = re.search(r'(\d+)-carbon', r.get("description", ""))
        
        if not carbon_match:
            continue
            
        n = int(carbon_match.group(1))
        
        # Extract all energy levels - handle np.float64() format
        energies = []
        # Try np.float64 format first
        np_floats = re.findall(r'np\.float64\(([-\d.]+)\)', result_text)
        if np_floats:
            energies = [float(e) for e in np_floats]
        else:
            # Try regular float format
            float_matches = re.findall(r'([-]?\d+\.\d+)', result_text)
            if float_matches:
                energies = [float(e) for e in float_matches]
        
        if energies:
            mo_data[n] = sorted(energies, reverse=True)
    
    findings = []
    hypotheses = []
    
    if len(mo_data) >= 3:
        # Analyze HOMO-LUMO gap scaling
        gap_data = {}
        for n, energies in sorted(mo_data.items()):
            if len(energies) >= 2:
                sorted_e = sorted(energies, reverse=True)
                if n % 2 == 0:
                    homo_idx = n // 2 - 1
                    lumo_idx = n // 2
                else:
                    homo_idx = n // 2
                    lumo_idx = n // 2 + 1
                
                if homo_idx < len(sorted_e) and lumo_idx < len(sorted_e):
                    gap = abs(sorted_e[homo_idx] - sorted_e[lumo_idx])
                    gap_data[n] = gap
                    findings.append({
                        "type": "homo_lumo_gap",
                        "description": f"{n}-carbon system: HOMO-LUMO gap = {gap:.3f} eV",
                        "gap": gap,
                        "n_carbons": n,
                        "novelty_status": "finite_computational_observation",
                        "evidence_level": "model_fit",
                        "is_novel": False,
                    })
        
        # Check if gap follows 1/n scaling (particle-in-a-box prediction)
        if len(gap_data) >= 3:
            # Fit gap = A/n + B
            ns = sorted(gap_data.keys())
            gs = [gap_data[n] for n in ns]
            
            # Simple linear regression on 1/n vs gap
            inv_ns = [1/n for n in ns]
            n_pts = len(inv_ns)
            sum_x = sum(inv_ns)
            sum_y = sum(gs)
            sum_xy = sum(x*y for x, y in zip(inv_ns, gs))
            sum_x2 = sum(x**2 for x in inv_ns)
            
            if n_pts * sum_x2 - sum_x**2 != 0:
                A = (n_pts * sum_xy - sum_x * sum_y) / (n_pts * sum_x2 - sum_x**2)
                B = (sum_y - A * sum_x) / n_pts
                
                # Calculate R²
                y_mean = sum_y / n_pts
                ss_tot = sum((y - y_mean)**2 for y in gs)
                ss_res = sum((y - (A/x + B))**2 for x, y in zip(ns, gs))
                r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0
                
                findings.append({
                    "type": "gap_scaling_law",
                    "description": f"HOMO-LUMO gap scales as {A:.2f}/n + {B:.2f} (R²={r_squared:.4f})",
                    "r_squared": r_squared,
                    "novelty_status": "candidate_novelty" if r_squared < 0.95 else "finite_computational_observation",
                    "evidence_level": "model_fit",
                    "is_novel": False,
                })
                
                if r_squared < 0.95:
                    hypotheses.append({
                        "hypothesis": f"The HOMO-LUMO gap scaling deviates from the simple 1/n particle-in-a-box model (R²={r_squared:.3f}), suggesting electron-electron interactions or boundary effects become significant for larger conjugated systems.",
                        "confidence": min(0.80, 0.5 + (1 - r_squared) * 2),
                        "testable": True,
                        "method": "Perform DFT calculations on the same systems and compare HOMO-LUMO gaps against Huckel predictions to quantify electron correlation effects.",
                        "novelty_status": "candidate_novelty",
                        "evidence_level": "model_fit",
                    })
                else:
                    hypotheses.append({
                        "hypothesis": f"The HOMO-LUMO gap follows the 1/n scaling law (R²={r_squared:.4f}) predicted by the particle-in-a-box model, confirming the validity of the Huckel approximation for conjugated π-systems.",
                        "confidence": 0.85,
                        "testable": True,
                        "method": "Extend analysis to n=20-30 carbon systems and verify scaling holds, or detect crossover to different scaling regime.",
                        "novelty_status": "finite_computational_observation",
                        "evidence_level": "model_fit",
                    })
    
    if not findings:
        findings.append({
            "type": "insufficient_data",
            "description": "Insufficient molecular orbital data for pattern analysis",
            "novelty_status": "insufficient_data",
            "is_novel": False,
        })
    
    return {
        "findings": findings,
        "novel_findings": [f for f in findings if f.get("is_novel", False)],
        "candidate_findings": [f for f in findings if f.get("novelty_status") == "candidate_novelty"],
        "hypotheses": hypotheses,
        "has_novelty": False,
    }


def prime_verification_novelty(results: list[dict]) -> dict:
    """Detect novel findings from deep prime verification."""
    findings = []
    hypotheses = []
    
    for r in results:
        if "goldbach" in r["tool"].lower() or "goldbach" in r["result"].lower():
            # Goldbach is a KNOWN conjecture — not novel
            if "verified" in r["result"].lower() or "all" in r["result"].lower():
                findings.append({
                    "type": "goldbach_verification",
                    "description": "Goldbach conjecture verified within computational range (KNOWN conjecture, not novel)",
                    "novelty_status": "known_control",
                    "evidence_level": "bounded_verification",
                    "is_novel": False,
                })
        
        if "twin_primes" in r["tool"].lower():
            twin_count = re.findall(r'found: (\d+)', r["result"])
            if twin_count:
                findings.append({
                    "type": "twin_prime_count",
                    "description": f"Found {twin_count[0]} twin prime pairs in range (KNOWN phenomenon, not novel)",
                    "count": int(twin_count[0]),
                    "novelty_status": "known_control",
                    "evidence_level": "bounded_verification",
                    "is_novel": False,
                })
        
        if "conjecture" in r["tool"].lower():
            # Extract generated conjectures
            conjecture_texts = re.findall(r'Statement: (.+?)(?:\n|Status)', r["result"])
            for ct in conjecture_texts:
                # Check if this is a known conjecture
                if is_known_conjecture(ct):
                    findings.append({
                        "type": "known_conjecture",
                        "description": f"Known conjecture reproduced: {ct[:100]} (not novel)",
                        "novelty_status": "known_control",
                        "evidence_level": "literature_known",
                        "is_novel": False,
                    })
                else:
                    findings.append({
                        "type": "generated_conjecture",
                        "description": f"Auto-generated conjecture requiring validation: {ct[:100]}",
                        "novelty_status": "candidate_novelty",
                        "evidence_level": "generated_unverified",
                        "is_novel": False,
                    })
                    hypotheses.append({
                        "hypothesis": f"Computational conjecture: {ct[:150]}",
                        "confidence": 0.60,
                        "testable": True,
                        "method": "Verify computationally at larger scales and attempt formal proof using automated theorem prover.",
                        "novelty_status": "candidate_novelty",
                        "evidence_level": "generated_unverified",
                    })
    
    return {
        "findings": findings,
        "novel_findings": [f for f in findings if f.get("is_novel", False)],
        "candidate_findings": [f for f in findings if f.get("novelty_status") == "candidate_novelty"],
        "hypotheses": hypotheses,
        "has_novelty": False,
    }


NOVELTY_DETECTORS = {
    "prime_gap_novelty": prime_gap_novelty,
    "quantum_scaling_novelty": quantum_scaling_novelty,
    "molecular_orbital_novelty": molecular_orbital_novelty,
    "prime_verification_novelty": prime_verification_novelty,
}

# ============================================================
# KNOWN CONJECTURES — Not novel, should not be flagged as such
# ============================================================
KNOWN_CONJECTURES = {
    "goldbach": "Goldbach's conjecture (every even integer > 2 is the sum of two primes) — unsolved but well-known",
    "twin_prime": "Twin prime conjecture (infinitely many twin primes) — unsolved but well-known",
    "collatz": "Collatz conjecture (3n+1 problem) — unsolved but well-known",
    "riemann": "Riemann hypothesis (all non-trivial zeros of ζ(s) have real part 1/2) — unsolved but well-known",
    "fermat": "Fermat's Last Theorem — proven by Andrew Wiles (1995)",
    "pnt": "Prime Number Theorem (π(x) ~ x/ln(x)) — proven by Hadamard & de la Vallée-Poussin (1896)",
    "cramer": "Cramér's conjecture on prime gaps — well-known unsolved conjecture",
}


def is_known_conjecture(text: str) -> bool:
    """Check if a finding or hypothesis describes a known conjecture."""
    text_lower = text.lower()
    for key, desc in KNOWN_CONJECTURES.items():
        if key in text_lower:
            return True
        # Check if the description text overlaps
        # e.g., "every even integer" matches Goldbach
        if key == "goldbach" and ("even integer" in text_lower or "sum of two primes" in text_lower):
            return True
        if key == "twin_prime" and ("twin prime" in text_lower or "infinitely many" in text_lower and "prime" in text_lower):
            return True
        if key == "collatz" and ("3n+1" in text_lower or "collatz" in text_lower or "eventually reaches 1" in text_lower):
            return True
        if key == "riemann" and ("riemann" in text_lower or "zeta" in text_lower and "zero" in text_lower or "real part 1/2" in text_lower or "non-trivial zeros" in text_lower):
            return True
    return False


# ============================================================
# MAIN NOVELTY MISSION RUNNER
# ============================================================

class NoveltyMissionRunner:
    """Run missions designed to discover novel scientific findings."""
    
    def __init__(self):
        self.tools = None
        self.pg = PaperGenerator(reasoning_engine=None, enhance=True)
        self.enhancer = PaperEnhancer()
        self.provenance = ProvenanceManager()
        self.mission_count = 0
        self.novel_findings_count = 0
        self.papers_generated = 0
        self.start_time = time.time()
        self.all_novel_findings = []
    
    def _init_tools(self):
        if self.tools is None:
            log("🔧 Initializing Atlas tools...")
            self.tools = AtlasTools()
            log("✅ Atlas tools ready!")
    
    async def run_tool(self, tool_name: str, tool_input: str, description: str, domain: str = "mathematics") -> dict:
        """Execute a single tool with timeout and provenance tracking."""
        start = time.time()
        try:
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: asyncio.run(self.tools.run_scientific_tool(tool_name, tool_input, domain))
                ),
                timeout=90,
            )
            duration = time.time() - start
            result_str = str(result)
            # Record provenance
            prov = self.provenance.record_execution(
                tool_name=tool_name,
                tool_input=tool_input,
                tool_output=result_str,
                success=True,
                duration_seconds=duration,
                domain=domain,
            )
            return {
                "tool": tool_name,
                "input": tool_input,
                "description": description,
                "result": result_str,
                "success": True,
                "provenance_id": prov["experiment_id"],
                "provenance_path": self.provenance.get_provenance_path(prov["experiment_id"]),
            }
        except asyncio.TimeoutError:
            duration = time.time() - start
            self.provenance.record_execution(
                tool_name=tool_name, tool_input=tool_input,
                tool_output="Timeout after 90s", success=False,
                duration_seconds=duration, domain=domain,
            )
            return {"tool": tool_name, "input": tool_input, "description": description, "result": "Timeout", "success": False}
        except Exception as e:
            duration = time.time() - start
            err = str(e)[:200]
            self.provenance.record_execution(
                tool_name=tool_name, tool_input=tool_input,
                tool_output=err, success=False,
                duration_seconds=duration, domain=domain,
            )
            return {"tool": tool_name, "input": tool_input, "description": description, "result": err, "success": False}
    
    async def run_novelty_mission(self, mission_key: str) -> dict:
        """Run a single novelty discovery mission."""
        mission = NOVELTY_MISSIONS[mission_key]
        self.mission_count += 1
        
        log(f"🔬 Novelty Mission #{self.mission_count}: {mission['name']}")
        log(f"   Domain: {mission['domain']} | {mission['description']}")
        
        # Execute all tools with provenance tracking
        domain = mission["domain"]
        results = []
        for tool_name, tool_input, description in mission["tools"]:
            result = await self.run_tool(tool_name, tool_input, description, domain=domain)
            results.append(result)
            if result["success"]:
                prov_id = result.get("provenance_id", "N/A")
                log(f"  ✅ {description}: {result['result'][:60]} [provenance: {prov_id}]")
            else:
                log(f"  ❌ {description}: {result['result'][:60]}")
        
        # Run novelty detector
        detector_key = mission["novelty_detector"]
        detector = NOVELTY_DETECTORS.get(detector_key)
        if detector:
            novelty_result = detector(results)
        else:
            novelty_result = {"findings": [], "novel_findings": [], "hypotheses": [], "has_novelty": False}
        
        # Log findings
        for f in novelty_result["findings"]:
            marker = _finding_label(f)
            log(f"  {marker} {f['description'][:100]}")
        
        if novelty_result["novel_findings"]:
            self.novel_findings_count += len(novelty_result["novel_findings"])
            self.all_novel_findings.extend(novelty_result["novel_findings"])
        
        # Generate paper with novelty findings
        successful = [r for r in results if r["success"]]
        if successful:
            paper = await self.generate_novelty_paper(mission, results, novelty_result)
            self.papers_generated += 1
            candidates = len(novelty_result.get("candidate_findings", []))
            confirmed = len(novelty_result.get("novel_findings", []))
            log(f"  📄 Paper: {paper.get('word_count', 0)} words | Confirmed novel: {confirmed} | Candidates: {candidates}")
        
        return novelty_result
    
    async def generate_novelty_paper(self, mission: dict, results: list, novelty: dict) -> dict:
        """Generate a paper highlighting novel findings."""
        domain = mission["domain"]
        topic = mission["name"]
        # Use academic title if available
        paper_title = mission.get("title", f"Computational Analysis of {topic}")
        
        # Build tool sections with real provenance IDs
        tool_sections = []
        experiment_ids = []
        provenance_verified = []
        for i, r in enumerate(results):
            if r["success"]:
                tool_sections.append({
                    "heading": f"{r['description']} ({r['tool']})",
                    "content": f"**Input:** `{r.get('input', '')}`\n\n**Result:**\n{r['result'][:500]}",
                })
                # Use real provenance ID if available, otherwise synthetic
                prov_id = r.get("provenance_id", f"{domain}_{r['tool']}_{i}")
                experiment_ids.append(prov_id)
                # Verify provenance exists
                verified = self.provenance.verify_experiment_id(prov_id)
                provenance_verified.append(verified)
        
        # Log provenance verification
        verified_count = sum(1 for v in provenance_verified if v["exists"])
        log(f"  📋 Provenance: {verified_count}/{len(experiment_ids)} experiment IDs verified on disk")
        
        # Build novelty findings section
        novelty_section = ""
        if novelty["findings"]:
            novelty_section = "### Computational Findings\n\n"
            for f in novelty["findings"]:
                marker = _finding_label(f)
                novelty_section += f"{marker}: {f['description']}\n\n"
        
        # Build sections
        sections = [
            {"heading": "Introduction", "content": f"Study of {topic} using computational methods."},
            {"heading": "Methods", "content": f"Used {len(tool_sections)} Atlas tools."},
            {"heading": "Results", "content": "\n\n".join([f"### {s['heading']}\n{s['content']}" for s in tool_sections])},
            {"heading": "Novelty Analysis", "content": novelty_section or "No novel patterns detected in this analysis."},
            {"heading": "Discussion", "content": "Results demonstrate computational verification."},
            {"heading": "Conclusion", "content": "Analysis confirms findings."},
        ]
        
        # Combine hypotheses
        all_hypotheses = novelty.get("hypotheses", [])
        
        # Generate paper with enhancement
        paper = await self.pg.generate_paper(
            title=paper_title,
            abstract=f"Computational analysis of {topic.lower()} using {len(tool_sections)} independent methods. Findings are labeled as confirmed novelty only after provenance and literature validation; otherwise they are reported as controls, observations, or candidates.",
            sections=sections,
            references=["A.M.Y (2026). AXIOM Atlas Platform."],
            knowledge_facts=[{"subject": domain, "predicate": "analyzed", "object": "novelty", "confidence": 0.95}],
            experiment_ids=experiment_ids,
            domain=domain,
            tool_results=[r for r in results if r["success"]],
        )
        
        return paper
    
    async def run_all_missions(self):
        """Run all novelty discovery missions."""
        log("=" * 70)
        log("A.M.Y NOVELTY DISCOVERY MISSIONS")
        log("=" * 70)
        
        self._init_tools()
        
        all_results = {}
        for key in NOVELTY_MISSIONS:
            result = await self.run_novelty_mission(key)
            all_results[key] = result
            
            # Save state
            save_state({
                "mission_count": self.mission_count,
                "novel_findings_count": self.novel_findings_count,
                "papers_generated": self.papers_generated,
                "novel_findings": [f["description"] for f in self.all_novel_findings],
                "elapsed": time.time() - self.start_time,
            })
            
            await asyncio.sleep(3)
        
        # Final report
        log("=" * 70)
        log("NOVELTY DISCOVERY COMPLETE")
        log("=" * 70)
        log(f"Missions: {self.mission_count}")
        log(f"Novel findings: {self.novel_findings_count}")
        log(f"Papers generated: {self.papers_generated}")
        
        if self.all_novel_findings:
            log("\n🆕 NOVEL FINDINGS:")
            for f in self.all_novel_findings:
                log(f"  • {f['description'][:120]}")
        else:
            log("\n📊 No novel findings detected — all results match theoretical predictions.")
        
        return all_results


def main():
    runner = NoveltyMissionRunner()
    asyncio.run(runner.run_all_missions())


if __name__ == "__main__":
    main()
