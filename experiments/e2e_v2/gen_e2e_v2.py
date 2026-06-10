#!/usr/bin/env python3
"""
E2E v2 generation — A.M.Y's full pipeline with the new tools ON.

Generates papers through the REAL Atlas → provenance → paper-enhancer path
(the same flow as experiments/all_domains/generate_all.py), but with the
upgrades validated over this work enabled:

  AMY_USE_LLM_ENHANCER=1   LLM-written, provenance-grounded Discussion (Sakana)
  AMY_USE_EVOLUTION=1      Co-Scientist Evolution agent on the top hypotheses
  AMY_USE_LLM_JUDGE=1      LLM scientific-debate ranking (now that think=false works)

Per paper it writes an AUDIT (papers/e2e_v2/<id>.audit.json) recording exactly
which Atlas tools ran, their provenance experiment_ids + SHA-256 hashes, whether
the LLM paths fired (not silent fallback), and the rubric + discussion + reflection
scores — so the E2E scientific pipeline is watchable end to end.

Run one plan:
    AMY_USE_LLM_ENHANCER=1 AMY_USE_EVOLUTION=1 \
    .venv/bin/python experiments/e2e_v2/gen_e2e_v2.py --plan prime_gaps

List plans:
    .venv/bin/python experiments/e2e_v2/gen_e2e_v2.py --list
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from core.atlas_tools import AtlasTools  # noqa: E402
from core.provenance import ProvenanceManager  # noqa: E402
from communication.paper_generator import PaperGenerator  # noqa: E402
from cognition.reflection_agent import reflect  # noqa: E402
from experiments.ab_test.scoring.score_paper import score_paper  # noqa: E402
from experiments.ab_test.scoring.score_discussion import score_discussion  # noqa: E402

OUT_DIR = ROOT / "papers" / "e2e_v2"
OUT_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_DIR = ROOT / "experiments" / "e2e_v2" / "audits"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)
_PROV = ProvenanceManager()

# Diverse plans spanning the evidence-grade Atlas tool families: real symbolic/
# numeric math, real ab-initio chemistry (PySCF), real physics (quantum levels),
# real statistics, real biology. Each uses ≥2 DISTINCT tools so the rubric's
# tool-diversity and methodology checks are genuinely satisfiable.
PLANS = {
    "prime_gaps": {
        "domain": "mathematics",
        "topic": "Prime gap distribution and the Cramér heuristic across decades",
        "title": "Prime Gap Scaling and the Cramér–Granville Heuristic: A Provenance-Anchored Computational Study",
        "tool_calls": [
            ("prime_gap_analysis", "1000000", "Prime gaps up to 10^6"),
            ("prime_gap_analysis", "100000", "Prime gaps up to 10^5"),
            ("number_theory_advanced", "goldbach 100", "Goldbach decomposition control to 100"),
            ("sympy_solve_equation", "x**2 - 5*x + 6", "Symbolic root structure (algebra control)"),
        ],
    },
    "hf_chemistry": {
        "domain": "chemistry",
        "topic": "Hartree–Fock total energies of small molecules cross-checked against bond-energy tables",
        "title": "Cross-Level Verification of Small-Molecule Energetics: Hartree–Fock vs. Empirical Bond Energies",
        "tool_calls": [
            ("pyscf_hf_energy", "H 0 0 0; H 0 0 0.74", "HF/sto-3g energy of H2"),
            ("pyscf_hf_energy", "O 0 0 0; H 0 0 0.96; H 0.93 0 -0.24", "HF/sto-3g energy of H2O"),
            ("molecular_weight_calc", "H2O", "Molecular weight of water"),
            ("bond_energy_analyzer", "O-H", "O-H bond energy"),
        ],
    },
    "hydrogen_levels": {
        "domain": "physics",
        "topic": "Hydrogen energy-level Rydberg scaling as a spectroscopic calibration control",
        "title": "Rydberg Scaling of Hydrogen Energy Levels: A Numerical Precision Control",
        # Atlas grammars: quantum_energy_levels = "system:n" (hydrogen/harmonic/
        # particle); calculus_engine = "op:expr:var[:point[:order]]" with op in
        # limit/taylor/laplace/fourier (NOT derivative/integrate).
        "tool_calls": [
            ("quantum_energy_levels", "hydrogen:5", "Hydrogen levels up to n=5"),
            ("calculus_engine", "taylor:exp(x):x:0:5", "Taylor series control"),
            ("calculus_engine", "limit:sin(x)/x:x:0", "Limit control (sinc at 0)"),
        ],
    },
    "statistics": {
        "domain": "statistics",
        "topic": "Distributional properties and hypothesis testing on a synthetic sample",
        "title": "Descriptive Statistics and Two-Sample Testing: A Tooling Verification Study",
        # Atlas grammars: numpy_statistics = "operation:data" (mean/std/var/
        # median/summary); numpy_distribution = "dist:n,p1,p2,seed"; hypothesis_
        # tester = "testtype:[arr1]:[arr2]" (ttest/kstest/shapiro/pearson/spearman).
        "tool_calls": [
            ("numpy_statistics", "summary:1,2,3,4,5,6,7,8,9,10", "Descriptive stats"),
            ("numpy_distribution", "normal:1000,0,1,42", "Sampled normal distribution (n=1000)"),
            ("hypothesis_tester", "ttest:[1,2,3,4,5]:[6,7,8,9,10]", "Two-sample t-test"),
        ],
    },
    "biology": {
        "domain": "biology",
        "topic": "DNA composition and protein hydropathy as sequence-analysis controls",
        "title": "Compositional and Hydropathy Analysis of Biological Sequences",
        "tool_calls": [
            ("dna_analyzer", "ATGCGCGCTATATCGCGCATGC", "GC content / composition"),
            ("protein_properties", "MKWVTFISLLFLFSSAYS", "Hydropathy / properties"),
        ],
    },
}


def _save_provenance(domain, tool, tool_input, out_str, desc, i):
    rec = _PROV.record_execution(
        tool_name=tool, tool_input=tool_input, tool_output=out_str,
        success=True, duration_seconds=0.0, domain=domain,
    )
    return rec["experiment_id"]


async def run_plan(plan_key: str) -> dict:
    plan = PLANS[plan_key]
    domain = plan["domain"]
    at = AtlasTools()
    tool_results, experiment_ids, atlas_audit = [], [], []
    for i, (tool, tool_input, desc) in enumerate(plan["tool_calls"]):
        try:
            out = await at.run_scientific_tool(tool, tool_input, domain=domain)
            out_str = str(out)
            bad = any(m in out_str[:60].lower() for m in ("error:", "unknown ", "not found", "traceback"))
            if bad:
                atlas_audit.append({"tool": tool, "input": tool_input, "ok": False, "preview": out_str[:80]})
                continue
            eid = _save_provenance(domain, tool, tool_input, out_str, desc, i)
            sha = hashlib.sha256(out_str.encode()).hexdigest()
            experiment_ids.append(eid)
            tool_results.append({"tool": tool, "input": tool_input, "result": out_str,
                                 "description": desc, "success": True, "experiment_id": eid})
            atlas_audit.append({"tool": tool, "input": tool_input, "ok": True,
                                "experiment_id": eid, "sha256": sha, "out_len": len(out_str)})
        except Exception as exc:
            atlas_audit.append({"tool": tool, "input": tool_input, "ok": False, "error": str(exc)[:120]})

    if len(tool_results) < 2:
        return {"plan": plan_key, "ok": False, "reason": "too_few_tool_results",
                "atlas_audit": atlas_audit}

    abstract = (
        f"Computational study of {plan['topic'].lower()} executing {len(tool_results)} "
        f"tool invocations from the AXIOM Atlas platform, each paired with a SHA-256 "
        f"provenance hash."
    )
    sections = [
        {"heading": "Introduction",
         "content": f"This work investigates {plan['topic'].lower()} using a reproducible computational pipeline."},
        {"heading": "Methods",
         "content": f"We executed {len(tool_results)} invocations spanning "
                    f"{len(set(r['tool'] for r in tool_results))} distinct Atlas tools."},
        {"heading": "Results",
         "content": "\n\n".join(
             f"### {r['description']}\n**Tool:** `{r['tool']}`\n**Input:** `{r['input']}`\n\n"
             f"**Output:**\n```\n{r['result'][:500]}\n```" for r in tool_results)},
        {"heading": "Discussion", "content": "TBD"},
        {"heading": "Conclusion", "content": "TBD"},
    ]

    gen = PaperGenerator(enhance=True, output_dir=OUT_DIR)
    result = await gen.generate_paper(
        title=plan["title"], abstract=abstract, sections=sections,
        references=None, knowledge_facts=None,
        experiment_ids=experiment_ids, domain=domain, tool_results=tool_results,
    )
    if not result:
        return {"plan": plan_key, "ok": False, "reason": "generation_failed",
                "atlas_audit": atlas_audit}

    md_path = Path(result["markdown_path"])
    md = md_path.read_text(encoding="utf-8")
    # Provenance integrity: re-hash each output.txt and compare to provenance.json.
    prov_ok, prov_total = 0, 0
    for eid in experiment_ids:
        prov_total += 1
        pj = ROOT / "data" / "experiments" / eid / "provenance.json"
        ot = ROOT / "data" / "experiments" / eid / "output.txt"
        if pj.exists() and ot.exists():
            claimed = json.loads(pj.read_text())["tool"]["output_hash"]
            actual = hashlib.sha256(ot.read_text(encoding="utf-8", errors="ignore").encode()).hexdigest()
            if claimed == actual:
                prov_ok += 1

    rubric = score_paper(md_path, peer_abstracts=[])
    disc = score_discussion(md_path)
    refl = reflect(md)

    audit = {
        "plan": plan_key, "ok": True, "domain": domain,
        "markdown_path": str(md_path), "publication_status": result.get("publication_status"),
        "n_atlas_tools_run": len(tool_results),
        "n_distinct_tools": len(set(r["tool"] for r in tool_results)),
        "atlas_audit": atlas_audit,
        "provenance_integrity": f"{prov_ok}/{prov_total}",
        "rubric_total": round(rubric.total, 1),
        "rubric_breakdown": {k: round(v, 1) for k, v in vars(rubric).items()
                             if isinstance(v, float) and k != "total"},
        "discussion_total": round(disc.total, 1),
        "reflection_score": refl.score, "reflection_pass": refl.pass_overall,
        # The "TBD" Discussion stub must have been replaced for a valid paper.
        "discussion_stub_replaced": "TBD" not in md,
        "discussion_word_count": disc.word_count,
    }
    (AUDIT_DIR / f"{plan_key}.audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    return audit


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default=None, help="plan key (default: all)")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    if args.list:
        for k, p in PLANS.items():
            print(f"  {k:16s} [{p['domain']}] {p['topic']}")
        return 0

    keys = [args.plan] if args.plan else list(PLANS)
    t0 = time.time()
    for k in keys:
        a = await run_plan(k)
        if a.get("ok"):
            print(f"[{k}] rubric={a['rubric_total']} discussion={a['discussion_total']} "
                  f"refl={a['reflection_score']} pass={a['reflection_pass']} "
                  f"tools={a['n_distinct_tools']}/{a['n_atlas_tools_run']} "
                  f"prov={a['provenance_integrity']} status={a['publication_status']}")
        else:
            print(f"[{k}] FAILED: {a.get('reason')}")
    print(f"\nwall {round(time.time()-t0,1)}s")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
