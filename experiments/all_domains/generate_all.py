"""Generate one paper per Atlas domain, end-to-end.

Strategy per domain:
- Pick a meaningful research topic.
- Pick 4-6 tool calls with diverse (tool, input) combinations.
- Skip service_* tools that require JSON payloads we can't easily synthesize.
- Skip evidence_corroborate_* (slow, returns diagnostic text).
- Use the real PaperGenerator (Reflection + Ranking already wired).
"""
import asyncio
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from core.atlas_tools import AtlasTools
from communication.paper_generator import PaperGenerator


OUT_DIR = REPO_ROOT / "experiments" / "all_domains" / "papers"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPERIMENTS_DIR = REPO_ROOT / "data" / "experiments"
EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)


# ── Per-domain plans — concrete topics with diverse (tool, input) pairs ────────
PLANS = [
    # Hard sciences
    {
        "domain": "astronomy",
        "topic": "Cosmological Distances and Stellar Spectroscopy",
        "title": "Computational Cosmology: Distance-Redshift Relations and Stellar Blackbody Spectra",
        "tool_calls": [
            ("astropy_cosmology", "luminosity_distance:0.1", "Nearby SN Ia distance"),
            ("astropy_cosmology", "luminosity_distance:1.0", "z=1.0 SN Ia distance"),
            ("astropy_cosmology", "comoving_distance:6.0", "Quasar comoving distance"),
            ("astropy_cosmology", "age:0", "Universe age at z=0"),
            ("astropy_blackbody", "5778", "Solar photosphere spectrum"),
            ("astropy_blackbody", "10000", "B-type star spectrum"),
            ("astropy_constants", "M_sun", "Solar mass reference"),
            ("astropy_constants", "G", "Gravitational constant"),
        ],
    },
    {
        "domain": "physics",
        "topic": "Hydrogen Atom Spectroscopy and Quantum Limits",
        "title": "Verification of Rydberg Scaling and Quantum Mechanical Calculations",
        "tool_calls": [
            ("quantum_energy_levels", "hydrogen:1", "Lyman level"),
            ("quantum_energy_levels", "hydrogen:2", "Balmer level"),
            ("quantum_energy_levels", "hydrogen:3", "Paschen level"),
            ("quantum_energy_levels", "hydrogen:5", "n=5 level"),
            ("quantum_circuit", "bell:2", "Bell-state preparation"),
            ("astropy_constants", "h", "Planck constant"),
            ("calculus_engine", "limit:exp(-x)/x:x->inf", "Decay limit"),
        ],
    },
    {
        "domain": "chemistry",
        "topic": "Molecular Energetics from Empirical Constants to Ab Initio",
        "title": "Cross-Level Comparison: IUPAC vs Hartree-Fock vs DFT vs EMT",
        "tool_calls": [
            ("molecular_weight_calc", "H2O", "Water (IUPAC)"),
            ("molecular_weight_calc", "C2H6O", "Ethanol (IUPAC)"),
            ("bond_energy_analyzer", "O-H", "O-H BDE"),
            ("bond_energy_analyzer", "C-C", "C-C BDE"),
            ("pyscf_hf_energy", "H 0 0 0; H 0 0 0.74", "H2 HF/sto-3g"),
            ("pyscf_dft_energy", "H 0 0 0; H 0 0 0.74", "H2 B3LYP/sto-3g"),
            ("ase_optimize", "H2O", "Water EMT geometry"),
            ("ase_optimize", "CH4", "Methane EMT geometry"),
        ],
    },
    {
        "domain": "biology",
        "topic": "Sequence Composition and Protein Biophysics",
        "title": "Quantitative Properties of DNA Sequences and Protein Sequences",
        "tool_calls": [
            ("dna_analyzer", "ATCGATCGATCGATCG", "AT/GC balanced sequence"),
            ("dna_analyzer", "GC:GCGCGCGCGC", "GC-rich oligonucleotide"),
            ("dna_analyzer", "ATATATATATATAT", "AT-rich oligonucleotide"),
            ("protein_properties", "MKVLWAALLVTFLAGCQA", "Signal peptide"),
            ("protein_properties", "GVKKDGKIVHHNGNVKKLPFPELHFGEFKEMHNIKYWGKLD", "Short folded peptide"),
        ],
    },
    {
        "domain": "mathematics",
        "topic": "Prime Distribution and Algebraic Verification",
        "title": "Computational Studies of Prime Counting and Twin Prime Density",
        "tool_calls": [
            ("prime_gap_analysis", "1000", "Primes up to 10³"),
            ("prime_gap_analysis", "10000", "Primes up to 10⁴"),
            ("prime_gap_analysis", "100000", "Primes up to 10⁵"),
            ("number_theory_advanced", "goldbach:100", "Goldbach for n ≤ 100"),
            ("number_theory_advanced", "twin_primes:10000", "Twin primes ≤ 10⁴"),
            ("sympy_prime_analysis", "prime_count:10000", "π(10⁴)"),
            ("sympy_prime_analysis", "nth_prime:1000", "1000th prime"),
            ("sympy_solve_equation", "x**3 - x", "Cubic roots"),
        ],
    },
    {
        "domain": "statistics",
        "topic": "Sampling, Correlation, and Hypothesis Testing",
        "title": "Statistical Routines: Distribution Sampling and Effect-Size Inference",
        "tool_calls": [
            ("numpy_statistics", "summary:[1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0,10.0]", "Discrete 1..10"),
            ("numpy_distribution", "normal:1000,0,1", "Standard normal n=1000"),
            ("numpy_distribution", "normal:10000,100,15", "IQ-like distribution"),
            ("numpy_correlation", "correlation:[1,2,3,4,5]:[2,4,6,8,10]", "Perfect linear r=1"),
            ("numpy_correlation", "correlation:[1,2,3,4,5,6,7,8]:[1,2,1,2,1,2,1,2]", "Zero-correlation control"),
            ("hypothesis_tester", "ttest:[1,2,3,4,5]:[3,4,5,6,7]", "Shifted-means t-test"),
            ("hypothesis_tester", "ttest:[1,2,3,4,5]:[1,2,3,4,5]", "Null t-test"),
        ],
    },
    # Materials science
    {
        "domain": "materials_science",
        "topic": "Crystal Structures and Lattice Properties",
        "title": "Structural Verification of Reference Crystals",
        "tool_calls": [
            ("pymatgen_structure", "Si", "Silicon diamond"),
            ("pymatgen_structure", "NaCl", "Rocksalt NaCl"),
            ("pymatgen_structure", "TiO2", "Rutile TiO2"),
            ("pymatgen_structure", "Cu", "FCC Copper"),
        ],
    },
    # Number theory (own domain in Atlas)
    {
        "domain": "number_theory",
        "topic": "Bounded Verification of Number-Theoretic Conjectures",
        "title": "Empirical Tests of Goldbach and Twin-Prime Conjectures",
        "tool_calls": [
            ("number_theory_advanced", "goldbach:50", "Goldbach 4 ≤ n ≤ 50"),
            ("number_theory_advanced", "goldbach:200", "Goldbach 4 ≤ n ≤ 200"),
            ("number_theory_advanced", "twin_primes:100", "Twin primes ≤ 100"),
            ("number_theory_advanced", "twin_primes:1000", "Twin primes ≤ 1000"),
            ("number_theory_advanced", "twin_primes:10000", "Twin primes ≤ 10⁴"),
            ("prime_gap_analysis", "10000", "Prime gap statistics"),
        ],
    },
]


def _save_provenance(domain, tool, tool_input, output, description, counter):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_in = hashlib.md5(tool_input.encode()).hexdigest()[:6]
    eid = f"{domain}_{tool}_{timestamp}_{safe_in}{counter}"
    exp_dir = EXPERIMENTS_DIR / eid
    exp_dir.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256(output.encode()).hexdigest()
    rec = {
        "experiment_id": eid,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": {"name": tool, "input": tool_input, "output_hash": h,
                 "output_length": len(output), "success": True},
        "output_preview": output[:2000],
        "domain": domain,
        "extra": {"description": description},
    }
    (exp_dir / "provenance.json").write_text(json.dumps(rec, indent=2))
    (exp_dir / "output.txt").write_text(output)
    return eid


async def run_plan(at, gen, plan):
    domain = plan["domain"]
    print(f"\n=== {domain.upper():30s} | {plan['topic']}")
    tool_results = []
    experiment_ids = []
    for i, (tool, tool_input, desc) in enumerate(plan["tool_calls"]):
        try:
            out = await at.run_scientific_tool(tool, tool_input, domain=domain)
            out_str = str(out)
            if any(m in out_str[:50].lower() for m in ("error:", "unknown ", "not found")):
                print(f"  [skip]  {tool}({tool_input[:25]}) → {out_str[:50]}")
                continue
            eid = _save_provenance(domain, tool, tool_input, out_str, desc, i)
            experiment_ids.append(eid)
            tool_results.append({
                "tool": tool, "input": tool_input, "result": out_str,
                "description": desc, "success": True, "experiment_id": eid,
            })
            print(f"  [ok]    {tool}({tool_input[:25]:25s}) → {out_str[:60].replace(chr(10), ' | ')}")
        except Exception as exc:
            print(f"  [err]   {tool}({tool_input[:25]}): {exc}")
            continue

    if len(tool_results) < 2:
        print(f"  Too few results, skipping paper.")
        return None

    title = plan["title"]
    abstract = (
        f"Computational study of {plan['topic'].lower()} executing "
        f"{len(tool_results)} distinct tool invocations from the AXIOM Atlas platform. "
        f"Each output is paired with a SHA-256 provenance hash; this manuscript reports "
        f"verification controls and falsifiable predictions rather than novel claims."
    )

    sections = [
        {"heading": "Introduction",
         "content": f"This work investigates {plan['topic'].lower()} using a reproducible computational pipeline."},
        {"heading": "Methods",
         "content": f"We executed {len(tool_results)} tool invocations spanning "
                    f"{len(set(r['tool'] for r in tool_results))} distinct Atlas tools."},
        {"heading": "Results",
         "content": "\n\n".join(
             f"### {r['description']}\n**Tool:** `{r['tool']}`\n**Input:** `{r['input']}`\n\n"
             f"**Output:**\n```\n{r['result'][:500]}\n```"
             for r in tool_results
         )},
        {"heading": "Discussion", "content": "TBD"},
        {"heading": "Conclusion", "content": "TBD"},
    ]

    result = await gen.generate_paper(
        title=title, abstract=abstract, sections=sections,
        references=None, knowledge_facts=None,
        experiment_ids=experiment_ids, domain=domain,
        tool_results=tool_results,
    )
    if not result:
        return None
    md_path = Path(result["markdown_path"])
    if md_path.exists():
        out_path = OUT_DIR / md_path.name
        out_path.write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"  → {out_path.name}  ({result['publication_status']})")
        return out_path
    return None


async def main():
    at = AtlasTools()
    gen = PaperGenerator(enhance=True)
    print(f"Generating {len(PLANS)} papers (one per domain) into {OUT_DIR}")
    for plan in PLANS:
        await run_plan(at, gen, plan)
    n = len(list(OUT_DIR.glob("*.md")))
    print(f"\nDone: {n} papers in {OUT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
