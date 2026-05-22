"""
A.M.Y Multi-Domain Exploration v2 — CORRECTED
Usa herramientas reales de Atlas (no solo literature_search)
"""
import asyncio, json, sys, time, re, hashlib
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from core.atlas_tools import AtlasTools
from core.ollama_client import OllamaCloudClient
import yaml

with open("config.yaml") as f:
    CONFIG = yaml.safe_load(f)

MODEL = CONFIG["llm"]["reasoner"]["model"]
PAPERS_DIR = Path("papers")
PAPERS_DIR.mkdir(exist_ok=True)

# ── Domains with REAL Atlas tools ────────────────────────────────────────────
DOMAINS = [
    {
        "name": "astronomy",
        "tools": [
            ("literature_search", "JWST early universe galaxy formation unexpected findings 2024"),
            ("literature_search", "exoplanet atmosphere characterization JWST 2024"),
            ("service_astronomicalmlservice", "analyze galaxy formation data"),
        ],
    },
    {
        "name": "biology",
        "tools": [
            ("literature_search", "CRISPR prime editing clinical trials 2024 2025"),
            ("literature_search", "AAV vector engineering gene therapy 2024"),
            ("service_genomicsservice", "analyze CRISPR editing efficiency"),
            ("service_dnabert2genomicsservice", "analyze gene sequence"),
        ],
    },
    {
        "name": "chemistry",
        "tools": [
            ("literature_search", "CO2 capture metal organic frameworks 2024"),
            ("literature_search", "green ammonia synthesis electrocatalysis 2024"),
            ("molecular_weight_calc", "CO2"),
            ("molecular_weight_calc", "NH3"),
            ("service_computationalchemistryservice", "analyze CO2 reduction"),
        ],
    },
    {
        "name": "climate_science",
        "tools": [
            ("literature_search", "climate tipping points cascading risks 2024"),
            ("literature_search", "extreme weather attribution climate change 2024"),
            ("service_climateevidenceservice", "analyze tipping point evidence"),
        ],
    },
    {
        "name": "engineering",
        "tools": [
            ("literature_search", "AI-driven topology optimization additive manufacturing 2024"),
            ("literature_search", "digital twin structural health monitoring 2024"),
            ("service_additivemanufacturingservice", "analyze manufacturing process"),
        ],
    },
    {
        "name": "neuroscience",
        "tools": [
            ("literature_search", "consciousness global workspace theory neuroscience 2024"),
            ("literature_search", "transformer models brain predictive coding 2024"),
            ("service_neurosciencelightservice", "analyze consciousness theories"),
        ],
    },
    {
        "name": "physics",
        "tools": [
            ("literature_search", "room temperature superconductor evidence 2024 2025"),
            ("literature_search", "skyrmion pinning mechanisms 2024"),
            ("service_solidstatephysicsservice", "analyze skyrmion dynamics"),
            ("service_quantumphysicsservice", "analyze quantum effects"),
        ],
    },
]

SYSTEM_PROMPT = """You are A.M.Y (Autonomous Mind Yield), an autonomous scientific AI.
For each domain, you receive literature search results AND computational tool outputs.
Write a short scientific paper (~1000-1500 words) integrating BOTH.

Rules:
- Pick a SPECIFIC, narrow topic supported by the data
- INTEGRATE computational results with literature findings
- Label observations as "candidate findings" where appropriate
- Include real citations from literature results
- Format: Abstract, Introduction, Methods, Results, Discussion, References
- Be honest about limitations
- Every claim must be traceable to either literature or tool outputs"""

PAPER_PROMPT = """Domain: {domain}
Literature search results:
{literature_results}

Computational tool outputs:
{tool_results}

Write a short scientific paper (~1000-1500 words) on a specific topic within {domain}.
INTEGRATE the computational results with the literature findings.
Choose the most interesting and well-supported topic.

Format as Markdown with:
# Title (specific and descriptive)
## Abstract (100-150 words)
## Introduction
## Methods (literature search + computational tools used)
## Results (integrate literature AND computational findings)
## Discussion (implications, limitations)
## References (real citations from literature, format: [N] Author. Year. Title. Venue.)

Be a scientist: honest, precise, humble about what is known vs. speculated."""


async def explore_domain(atlas: AtlasTools, llm: OllamaCloudClient, domain_info: dict):
    domain = domain_info["name"]
    print(f"\n{'='*60}")
    print(f"Exploring: {domain.upper()}")
    print(f"{'='*60}")

    literature_results = []
    tool_results = []

    for tool_name, tool_input in domain_info["tools"]:
        is_lit = "literature" in tool_name
        label = "LIT" if is_lit else "TOOL"
        print(f"  [{label}] {tool_name}('{str(tool_input)[:60]}...')")
        try:
            result = await asyncio.wait_for(
                atlas.run_scientific_tool(tool_name, str(tool_input), domain=domain),
                timeout=60,
            )
            result_str = str(result)[:1500]
            if is_lit:
                literature_results.append({"query": tool_input, "result": result_str})
            else:
                tool_results.append({"tool": tool_name, "input": tool_input, "output": result_str})
            print(f"    -> {result_str[:80]}...")
        except asyncio.TimeoutError:
            print(f"    TIMEOUT")
            if is_lit:
                literature_results.append({"query": tool_input, "error": "timeout"})
            else:
                tool_results.append({"tool": tool_name, "input": tool_input, "error": "timeout"})
        except Exception as e:
            print(f"    ERROR: {e}")
            if is_lit:
                literature_results.append({"query": tool_input, "error": str(e)})
            else:
                tool_results.append({"tool": tool_name, "input": tool_input, "error": str(e)})

    # Generate paper
    print(f"  Generating paper...")
    lit_text = json.dumps(literature_results, indent=2, default=str)[:3000]
    tool_text = json.dumps(tool_results, indent=2, default=str)[:2000]

    try:
        resp = await asyncio.wait_for(
            llm.chat(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": PAPER_PROMPT.format(
                        domain=domain,
                        literature_results=lit_text,
                        tool_results=tool_text,
                    )},
                ],
                temperature=0.3,
                max_tokens=3000,
            ),
            timeout=60.0,
        )
        paper_text = ""
        if isinstance(resp, dict):
            msg = resp.get("message", {})
            paper_text = msg.get("content", "") if isinstance(msg, dict) else str(msg)
        else:
            paper_text = str(resp)
    except asyncio.TimeoutError:
        paper_text = f"# {domain.title()} Exploration\n\nPaper generation timed out.\n"
    except Exception as e:
        paper_text = f"# {domain.title()} Exploration\n\nError: {e}\n"

    if not paper_text or len(paper_text) < 100:
        paper_text = f"# {domain.title()} Exploration\n\nInsufficient data to generate paper.\n\nLiterature: {len(literature_results)} results\nTools: {len(tool_results)} results\n"

    # Save
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"AMY_{domain.replace('_','-')}_v2_{timestamp}.md"
    filepath = PAPERS_DIR / filename

    provenance = f"""

---
## Provenance
- Domain: {domain}
- Generated: {datetime.now(timezone.utc).isoformat()}
- Literature searches: {sum(1 for t,_ in domain_info['tools'] if 'literature' in t)}
- Computational tools: {sum(1 for t,_ in domain_info['tools'] if 'literature' not in t)}
- Model: {MODEL}
"""
    filepath.write_text(paper_text + provenance, encoding="utf-8")
    print(f"  Paper saved: {filename} ({len(paper_text)} chars)")

    return {"domain": domain, "paper_file": str(filepath), "paper_preview": paper_text[:300]}


async def main():
    print("A.M.Y Multi-Domain Exploration v2 — WITH REAL TOOLS")
    print("=" * 60)

    atlas = AtlasTools()
    llm = OllamaCloudClient(CONFIG["llm"])

    results = []
    for domain_info in DOMAINS:
        result = await explore_domain(atlas, llm, domain_info)
        results.append(result)

    print(f"\n\n{'='*60}")
    print("EXPLORATION COMPLETE")
    print(f"{'='*60}")
    for r in results:
        print(f"  {r['domain']}: {Path(r['paper_file']).name}")

    summary_path = PAPERS_DIR / f"multi_domain_v2_summary_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    summary_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nSummary: {summary_path}")


if __name__ == "__main__":
    asyncio.run(main())
