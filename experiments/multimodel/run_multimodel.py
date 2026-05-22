"""Multi-model paper-generation A/B/C/...

Same topic, same tool results, varies only the LLM used by the Reasoning /
PaperEnhancer chain. Scores each resulting paper with the rubric and the
Reflection agent, then prints a delta table.

The point is to learn which model A.M.Y should use as its default reasoner.
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from core.atlas_tools import AtlasTools
from communication.paper_generator import PaperGenerator
from experiments.ab_test.scoring.score_paper import score_paper
from cognition.reflection_agent import reflect


MODELS = [
    "glm-5.1",          # current default — biggest GLM
    "glm-4.7",          # smaller / older GLM
    "qwen3-next:80b",   # qwen3 cloud
    "deepseek-v3.2",    # deepseek mid-tier
    "minimax-m2.5",     # minimax latest
    "kimi-k2.5",        # kimi
    "gpt-oss:120b",     # openai oss
]


OUT_DIR = REPO_ROOT / "experiments" / "multimodel" / "papers"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# Same plan A.M.Y used in flagship, but compressed
async def gather_tool_results(at):
    """Pre-compute tool results once — they don't depend on the LLM."""
    results = []
    for tool, inp, desc in [
        ("prime_gap_analysis", "10000", "Primes up to 10⁴"),
        ("prime_gap_analysis", "100000", "Primes up to 10⁵"),
        ("number_theory_advanced", "twin_primes:1000", "Twin primes ≤ 10³"),
        ("sympy_prime_analysis", "prime_count:10000", "π(10⁴)"),
        ("sympy_prime_analysis", "nth_prime:1000", "1000th prime"),
    ]:
        out = await at.run_scientific_tool(tool, inp, "mathematics")
        results.append({"tool": tool, "input": inp, "result": str(out),
                         "description": desc, "success": True})
    return results


async def run_one(model_name, tool_results):
    """Run paper generation with a specific model — patch config.yaml in-process."""
    # Force the LLM-backed ranking judge to use the model under test.
    os.environ["AMY_RANKING_MODEL"] = model_name
    os.environ["AMY_USE_LLM_JUDGE"] = "1"

    # Avoid clashing PaperGenerator instances writing to the same papers/ dir.
    # Use a fresh PaperGenerator per model.
    gen = PaperGenerator(enhance=True)

    sections = [
        {"heading": "Introduction",
         "content": "Computational verification of prime-gap statistics across two decades."},
        {"heading": "Methods",
         "content": f"We executed {len(tool_results)} Atlas tool invocations using "
                    f"a single LLM-backed enhancer ({model_name})."},
        {"heading": "Results",
         "content": "\n\n".join(
             f"### {r['description']}\n**Tool:** `{r['tool']}`\n**Input:** `{r['input']}`\n\n"
             f"**Output:**\n```\n{r['result'][:500]}\n```"
             for r in tool_results)},
        {"heading": "Discussion", "content": "TBD"},
        {"heading": "Conclusion", "content": "TBD"},
    ]

    title = f"Prime Gap Statistics — Model Study ({model_name})"
    abstract = (
        f"Computational study of prime-gap statistics using {len(tool_results)} "
        f"Atlas tool invocations, with paper generation driven by the "
        f"{model_name} model. This is a controlled-condition test of LLM-driven "
        f"scientific writing — same tool outputs, different reasoning model."
    )

    t0 = time.time()
    try:
        result = await asyncio.wait_for(
            gen.generate_paper(
                title=title, abstract=abstract, sections=sections,
                references=None, knowledge_facts=None,
                experiment_ids=[],
                domain="mathematics",
                tool_results=tool_results,
            ),
            timeout=180.0,
        )
        dt = time.time() - t0
    except asyncio.TimeoutError:
        print(f"  [{model_name}] TIMEOUT after 180s")
        return None
    except Exception as exc:
        dt = time.time() - t0
        print(f"  [{model_name}] ERROR after {dt:.1f}s: {type(exc).__name__}: {exc}")
        return None

    if not result:
        return None
    md_path = Path(result["markdown_path"])
    if not md_path.exists():
        return None

    # Copy to multimodel/ for analysis
    safe = model_name.replace(":", "_").replace("/", "_")
    out_path = OUT_DIR / f"{safe}_{md_path.name}"
    out_path.write_text(md_path.read_text())

    md = out_path.read_text()
    score = score_paper(out_path, peer_abstracts=[])
    refl = reflect(md)
    return {
        "model": model_name,
        "duration_s": round(dt, 2),
        "word_count": result.get("word_count", 0),
        "rubric_score": score.total,
        "reflection_score": refl.score,
        "reflection_pass": refl.pass_overall,
        "per_dim": {f: getattr(score, f) for f in [
            'provenance_integrity','tool_diversity','falsifiability',
            'explicit_limitations','numerical_claims_grounded',
            'citation_accuracy','abstract_uniqueness',
            'statistical_rigor','reproducibility_info']},
    }


async def main():
    at = AtlasTools()
    print("Pre-computing tool results (same across all models)...")
    tool_results = await gather_tool_results(at)
    print(f"  Got {len(tool_results)} results.\n")

    print(f"Testing {len(MODELS)} models...")
    summary = []
    for model in MODELS:
        print(f"\n--- {model} ---")
        r = await run_one(model, tool_results)
        if r:
            print(f"  duration={r['duration_s']}s  rubric={r['rubric_score']:.2f}  "
                  f"reflection={r['reflection_score']:.1f}  pass={r['reflection_pass']}")
            summary.append(r)

    summary.sort(key=lambda r: -r["rubric_score"])
    print("\n" + "=" * 80)
    print(f"  {'model':30s} {'time(s)':>9s} {'rubric':>8s} {'reflect':>9s} {'words':>7s}")
    print("=" * 80)
    for r in summary:
        print(f"  {r['model']:30s} {r['duration_s']:>9.1f} {r['rubric_score']:>8.2f} "
              f"{r['reflection_score']:>9.1f} {r['word_count']:>7d}")

    out_file = REPO_ROOT / "experiments" / "multimodel" / "RESULTS.json"
    out_file.write_text(json.dumps(summary, indent=2))
    print(f"\nResults saved to {out_file}")


if __name__ == "__main__":
    asyncio.run(main())
