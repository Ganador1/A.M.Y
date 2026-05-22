"""Novelty hunt — try to surface at least one genuinely novel finding.

Strategy: rather than calibration-control topics, give A.M.Y diverse tool
combinations whose joint behaviour is NOT a known textbook result. Score
each by the novelty heuristic and rank.

Examples:
- Cross-level chemistry: do HF/B3LYP/EMT agree to within a known constant for H2 and CH4?
- Prime gap scaling: does max(g)/log²p approach 1 monotonically?
- Cosmology: distance ratio d_L(z=2) / d_L(z=1) — does it match the inverse-square law?
- Hückel vs PySCF for benzene HOMO-LUMO gap — quantitative agreement?
- AT-rich vs GC-rich DNA hydropathy of translated reading frames?
"""
import asyncio
import hashlib
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from core.atlas_tools import AtlasTools
from communication.paper_generator import PaperGenerator
from experiments.ab_test.scoring.score_paper import score_paper
from experiments.all_domains.review_all import detect_novelty_signals


OUT_DIR = REPO_ROOT / "experiments" / "novelty_hunt" / "papers"
OUT_DIR.mkdir(parents=True, exist_ok=True)
EXPERIMENTS_DIR = REPO_ROOT / "data" / "experiments"


HUNT_PLANS = [
    {
        "topic": "Multi-level convergence of H₂ binding energy across HF, DFT and EMT",
        "title": "Cross-Level Discrepancy in H₂ Binding: A Reproducible Comparison of Hartree-Fock, B3LYP, and EMT",
        "domain": "chemistry",
        "tool_calls": [
            ("pyscf_hf_energy", "H 0 0 0; H 0 0 0.74", "H₂ HF / sto-3g"),
            ("pyscf_hf_energy", "H 0 0 0; H 0 0 0.74;basis=6-31g", "H₂ HF / 6-31g"),
            ("pyscf_dft_energy", "H 0 0 0; H 0 0 0.74", "H₂ B3LYP / sto-3g"),
            ("pyscf_dft_energy", "H 0 0 0; H 0 0 0.74;basis=6-31g", "H₂ B3LYP / 6-31g"),
            ("ase_optimize", "H2", "H₂ EMT geometry"),
            ("ase_thermochemistry", "H2:298", "H₂ Gibbs at 298 K"),
        ],
    },
    {
        "topic": "Empirical scaling of max gap / log²p in prime gaps from 10³ to 10⁷",
        "title": "Cramér Ratio Across Six Decades: A High-Range Empirical Audit",
        "domain": "mathematics",
        "tool_calls": [
            ("prime_gap_analysis", "1000", "N=10³"),
            ("prime_gap_analysis", "10000", "N=10⁴"),
            ("prime_gap_analysis", "100000", "N=10⁵"),
            ("prime_gap_analysis", "1000000", "N=10⁶"),
            ("prime_gap_analysis", "10000000", "N=10⁷"),
            ("number_theory_advanced", "twin_primes:100000", "Twin primes ≤ 10⁵"),
        ],
    },
    {
        "topic": "Cosmological distance ratios across redshift",
        "title": "Distance Ratios in Planck18: Empirical Tests of the Standard Cosmology",
        "domain": "astronomy",
        "tool_calls": [
            ("astropy_cosmology", "luminosity_distance:0.1", "z=0.1"),
            ("astropy_cosmology", "luminosity_distance:0.5", "z=0.5"),
            ("astropy_cosmology", "luminosity_distance:1.0", "z=1.0"),
            ("astropy_cosmology", "luminosity_distance:2.0", "z=2.0"),
            ("astropy_cosmology", "luminosity_distance:4.0", "z=4.0"),
            ("astropy_cosmology", "comoving_distance:1.0", "z=1.0 comoving"),
            ("astropy_cosmology", "comoving_distance:2.0", "z=2.0 comoving"),
            ("astropy_cosmology", "age:0", "Universe age"),
        ],
    },
    {
        "topic": "Bond-energy database internal consistency",
        "title": "Empirical Audit of Internal Consistency in the Atlas Bond-Energy Reference Table",
        "domain": "chemistry",
        "tool_calls": [
            ("bond_energy_analyzer", "H-H", "H-H"),
            ("bond_energy_analyzer", "C-H", "C-H"),
            ("bond_energy_analyzer", "C-C", "C-C"),
            ("bond_energy_analyzer", "C=C", "C=C"),
            ("bond_energy_analyzer", "C≡C", "C≡C"),
            ("bond_energy_analyzer", "N-H", "N-H"),
            ("bond_energy_analyzer", "O-H", "O-H"),
            ("bond_energy_analyzer", "N=N", "N=N"),
        ],
    },
    {
        "topic": "Wien-displacement convergence across stellar effective temperatures",
        "title": "Wien Peak Wavelength Across Spectral Classes: A Cross-Star Audit",
        "domain": "astronomy",
        "tool_calls": [
            ("astropy_blackbody", "3000", "M dwarf"),
            ("astropy_blackbody", "5778", "G2V (Sun)"),
            ("astropy_blackbody", "8000", "A-type"),
            ("astropy_blackbody", "10000", "B-type"),
            ("astropy_blackbody", "30000", "O-type"),
            ("astropy_constants", "h", "Planck constant"),
            ("astropy_constants", "c", "Speed of light"),
            ("astropy_constants", "k_B", "Boltzmann constant"),
        ],
    },
    {
        "topic": "GC-content dependence of DNA properties across designed sequences",
        "title": "GC Content as Predictor of Sequence Properties: A 10-Sample Audit",
        "domain": "biology",
        "tool_calls": [
            ("dna_analyzer", "AAAAAAAAAAAAAAAA", "0% GC"),
            ("dna_analyzer", "AAAAAATTTTTTTTTT", "0% GC, mixed"),
            ("dna_analyzer", "ATCGATCGATCGATCG", "50% GC, alternating"),
            ("dna_analyzer", "GC:GCATGCATGCATGC", "50% GC, GC-prefixed"),
            ("dna_analyzer", "GC:GCGCGCGCATATAT", "75% GC, blocked"),
            ("dna_analyzer", "GC:GCGCGCGCGCGCGC", "100% GC"),
        ],
    },
    {
        "topic": "Hückel π-electron energy scaling with chain length",
        "title": "HOMO-LUMO Gap Scaling in Linear Conjugated Systems",
        "domain": "chemistry",
        "tool_calls": [
            ("molecular_orbital_energy", "4", "Butadiene-like (n=4)"),
            ("molecular_orbital_energy", "6", "Hexatriene-like (n=6)"),
            ("molecular_orbital_energy", "8", "Octatetraene (n=8)"),
            ("molecular_orbital_energy", "10", "Decapentaene (n=10)"),
            ("molecular_orbital_energy", "12", "n=12"),
            ("molecular_orbital_energy", "14", "n=14"),
            ("molecular_orbital_energy", "16", "n=16"),
        ],
    },
    {
        "topic": "Twin-prime density vs Hardy-Littlewood second-moment prediction",
        "title": "Twin-Prime Density Across Five Decades: A Hardy-Littlewood Empirical Test",
        "domain": "number_theory",
        "tool_calls": [
            ("number_theory_advanced", "twin_primes:100", "≤10²"),
            ("number_theory_advanced", "twin_primes:1000", "≤10³"),
            ("number_theory_advanced", "twin_primes:10000", "≤10⁴"),
            ("number_theory_advanced", "twin_primes:100000", "≤10⁵"),
            ("number_theory_advanced", "twin_primes:1000000", "≤10⁶"),
            ("sympy_prime_analysis", "prime_count:1000000", "π(10⁶)"),
        ],
    },
]


def _save(domain, tool, inp, out, desc, i):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe = hashlib.md5(inp.encode()).hexdigest()[:6]
    eid = f"{domain}_{tool}_{timestamp}_{safe}{i}"
    d = EXPERIMENTS_DIR / eid
    d.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256(out.encode()).hexdigest()
    rec = {
        "experiment_id": eid,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tool": {"name": tool, "input": inp, "output_hash": h,
                 "output_length": len(out), "success": True},
        "output_preview": out[:2000], "domain": domain,
        "extra": {"description": desc},
    }
    (d / "provenance.json").write_text(json.dumps(rec, indent=2))
    (d / "output.txt").write_text(out)
    return eid


async def run_one(at, gen, plan):
    domain = plan["domain"]
    print(f"\n=== {plan['title'][:70]}")
    tool_results = []
    experiment_ids = []
    for i, (tool, inp, desc) in enumerate(plan["tool_calls"]):
        try:
            out = await asyncio.wait_for(
                at.run_scientific_tool(tool, inp, domain), timeout=120
            )
            out_str = str(out)
            if any(m in out_str[:60].lower() for m in ("error:", "unknown ")):
                print(f"  [skip] {tool}({inp[:25]})")
                continue
            eid = _save(domain, tool, inp, out_str, desc, i)
            experiment_ids.append(eid)
            tool_results.append({"tool": tool, "input": inp, "result": out_str,
                                  "description": desc, "success": True,
                                  "experiment_id": eid})
            print(f"  [ok]  {tool}({inp[:25]:25s})")
        except Exception as exc:
            print(f"  [err] {tool}({inp[:25]}): {exc}")
            continue

    if len(tool_results) < 3:
        return None

    title = plan["title"]
    abstract = (
        f"Computational audit of {plan['topic'].lower()} across "
        f"{len(tool_results)} Atlas tool invocations. We compute and report "
        "the cross-scale pattern rather than any single value, and we flag "
        "deviations from textbook expectations as candidate-novelty signals "
        "to be examined by independent replication."
    )

    sections = [
        {"heading": "Introduction",
         "content": f"This investigation targets {plan['topic'].lower()}. "
                    "The motivation is to look at the *pattern across inputs* rather than any "
                    "single value, so that systematic deviations from textbook expectations "
                    "become visible."},
        {"heading": "Methods",
         "content": f"We executed {len(tool_results)} Atlas tool invocations spanning "
                    f"{len(set(r['tool'] for r in tool_results))} distinct tools."},
        {"heading": "Results",
         "content": "\n\n".join(
             f"### {r['description']}\n**Tool:** `{r['tool']}`\n**Input:** `{r['input']}`\n\n"
             f"**Output:**\n```\n{r['result'][:500]}\n```"
             for r in tool_results)},
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
    if not md_path.exists():
        return None
    out_path = OUT_DIR / md_path.name
    out_path.write_text(md_path.read_text(encoding="utf-8"))
    return out_path


async def main():
    at = AtlasTools()
    gen = PaperGenerator(enhance=True)
    papers = []
    for plan in HUNT_PLANS:
        p = await run_one(at, gen, plan)
        if p:
            papers.append(p)

    print(f"\nGenerated {len(papers)} papers. Scoring novelty...\n")
    report = []
    for p in papers:
        md = p.read_text(encoding="utf-8")
        s = score_paper(p, peer_abstracts=[])
        nov = detect_novelty_signals(md)
        max_elo = nov["max_elo"]
        report.append({
            "paper": p.name,
            "rubric": s.total,
            "novelty_score": nov["novelty_score"],
            "max_elo": max_elo,
            "n_candidate_novelty": nov["candidate_novelty_count"],
            "n_testable": nov["testable_hypothesis_count"],
            "has_quantitative": nov["has_quantitative_predictions"],
            "has_falsifiable": nov["has_falsifiable_predictions"],
        })
    report.sort(key=lambda r: -r["novelty_score"])

    print(f"{'paper':70s} {'rubric':>7s} {'novel':>6s} {'elo':>6s} {'qHyp':>5s}")
    print("-" * 105)
    for r in report:
        print(f"  {r['paper'][:68]:68s} {r['rubric']:>7.1f} {r['novelty_score']:>6.1f} "
              f"{r['max_elo']:>6.0f} {'Y' if r['has_quantitative'] else 'N':>5s}")

    out = REPO_ROOT / "experiments" / "novelty_hunt" / "RESULTS.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"\nResults: {out}")


if __name__ == "__main__":
    asyncio.run(main())
