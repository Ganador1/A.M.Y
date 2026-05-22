"""
A.M.Y Multi-Domain Scientific Exploration

For each uncovered domain, A.M.Y:
1. Searches literature for current hot topics
2. Picks the most interesting topic
3. Runs relevant Atlas tools
4. Generates a short paper with real citations

Domains to explore: climate, engineering, neuroscience, astronomy, biology, chemistry, physics
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

# ── Domains to explore ───────────────────────────────────────────────────────
DOMAINS = [
    {
        "name": "climate",
        "literature_query": "climate change extreme weather attribution 2024 2025",
        "tool_queries": [
            ("literature_search", "climate change attribution extreme events 2024"),
            ("literature_search", "climate tipping points latest research"),
        ],
    },
    {
        "name": "engineering",
        "literature_query": "additive manufacturing topology optimization AI 2024 2025",
        "tool_queries": [
            ("literature_search", "AI-driven topology optimization additive manufacturing"),
            ("literature_search", "digital twin engineering structural health monitoring"),
        ],
    },
    {
        "name": "neuroscience",
        "literature_query": "transformer models brain processing predictive coding 2024 2025",
        "tool_queries": [
            ("literature_search", "predictive coding brain transformer models comparison"),
            ("literature_search", "consciousness global workspace theory neuroscience 2024"),
        ],
    },
    {
        "name": "astronomy",
        "literature_query": "JWST early universe galaxies formation 2024 2025",
        "tool_queries": [
            ("literature_search", "JWST early universe galaxy formation unexpected findings"),
            ("literature_search", "exoplanet atmosphere characterization JWST 2024"),
        ],
    },
    {
        "name": "biology",
        "literature_query": "CRISPR prime editing therapeutic applications 2024 2025",
        "tool_queries": [
            ("literature_search", "CRISPR prime editing clinical trials 2024 2025"),
            ("literature_search", "protein structure prediction AlphaFold drug discovery"),
        ],
    },
    {
        "name": "chemistry",
        "literature_query": "green chemistry sustainable catalysis CO2 capture 2024 2025",
        "tool_queries": [
            ("literature_search", "CO2 capture metal organic frameworks 2024"),
            ("literature_search", "green ammonia synthesis electrocatalysis 2024"),
        ],
    },
    {
        "name": "physics",
        "literature_query": "room temperature superconductivity LK-99 replication 2024 2025",
        "tool_queries": [
            ("literature_search", "room temperature superconductor evidence 2024 2025"),
            ("literature_search", "quantum computing error correction breakthrough 2024"),
        ],
    },
]

SYSTEM_PROMPT = """You are A.M.Y (Autonomous Mind Yield), an autonomous scientific AI exploring 
multiple scientific domains. For each domain, you will receive literature search results 
and must decide on a specific, focused topic for a short scientific paper.

Rules:
- Pick a SPECIFIC, narrow topic (not a broad review)
- The topic must be supported by the literature results provided
- Be honest about limitations — label observations as "candidate findings"
- Include real citations from the literature results
- Write in proper scientific paper format (Abstract, Introduction, Methods, Results, Discussion, References)
- Keep it concise (~800-1200 words)
- Every claim must be traceable to either literature results or tool outputs"""

PAPER_PROMPT = """Domain: {domain}
Literature search results:
{literature_results}

Tool execution results:
{tool_results}

Write a short scientific paper (~800-1200 words) on a specific, focused topic within {domain}.
Choose the most interesting and well-supported topic from the literature results.

Format as Markdown with:
# Title (specific and descriptive)
## Abstract (100-150 words)
## Introduction (context and motivation)
## Methods (literature search + tools used)
## Results (key findings from literature and tools)
## Discussion (implications, limitations)
## References (real citations from literature results, format: [N] Author. Year. Title. Venue. DOI/URL)

Be a scientist: honest, precise, and humble about what is known vs. speculated."""


async def explore_domain(atlas: AtlasTools, llm: OllamaCloudClient, domain_info: dict):
    """Explore one scientific domain and generate a paper."""
    domain = domain_info["name"]
    print(f"\n{'='*60}")
    print(f"Exploring: {domain.upper()}")
    print(f"{'='*60}")
    
    # ── Run literature searches ──────────────────────────────────────────
    literature_results = []
    for tool_name, query in domain_info["tool_queries"]:
        print(f"  Running {tool_name}('{query[:60]}...')")
        try:
            result = await atlas.run_scientific_tool(tool_name, query, domain=domain)
            # Extract just the paper list, not the full output
            if "JSON_DATA" in str(result):
                m = re.search(r'JSON_DATA:\s*(\{.*\})', str(result), re.DOTALL)
                if m:
                    data = json.loads(m.group(1))
                    papers = data.get("results", data.get("papers", []))
                    literature_results.append({"query": query, "papers": papers[:6]})
            else:
                literature_results.append({"query": query, "raw": str(result)[:1000]})
        except Exception as e:
            print(f"    Error: {e}")
            literature_results.append({"query": query, "error": str(e)})
    
    # ── Run domain-specific tools if available ───────────────────────────
    tool_results = []
    domain_tools = await atlas.list_tools(domain)
    computational_tools = [t for t in domain_tools if "service_" in t and "evidence" not in t and "literature" not in t]
    
    for tool_name in computational_tools[:2]:  # Max 2 computational tools
        print(f"  Running computational tool: {tool_name}")
        try:
            result = await atlas.run_scientific_tool(tool_name, "analyze", domain=domain)
            tool_results.append({"tool": tool_name, "output": str(result)[:800]})
        except Exception as e:
            tool_results.append({"tool": tool_name, "error": str(e)})
    
    # ── Generate paper via LLM ───────────────────────────────────────────
    print(f"  Generating paper...")
    lit_text = json.dumps(literature_results, indent=2, default=str)[:3000]
    tool_text = json.dumps(tool_results, indent=2, default=str)[:1500]
    
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
                    )}
                ],
                temperature=0.3,
                max_tokens=3000,
            ),
            timeout=45.0,
        )
        paper_text = ""
        if isinstance(resp, dict):
            msg = resp.get("message", {})
            if isinstance(msg, dict):
                paper_text = msg.get("content", "")
            else:
                paper_text = str(msg)
    except asyncio.TimeoutError:
        paper_text = f"# {domain.title()} Exploration\n\nPaper generation timed out. Literature results available in logs.\n"
    except Exception as e:
        paper_text = f"# {domain.title()} Exploration\n\nError generating paper: {e}\n"
    
    # ── Save paper ───────────────────────────────────────────────────────
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"AMY_{domain.title()}_Exploration_{timestamp}.md"
    filepath = PAPERS_DIR / filename
    
    # Add provenance
    provenance = f"""

---
## Provenance
- Domain: {domain}
- Generated: {datetime.now(timezone.utc).isoformat()}
- Tools used: {', '.join(t for t, _ in domain_info['tool_queries'])}
- Model: {MODEL}
"""
    filepath.write_text(paper_text + provenance, encoding="utf-8")
    print(f"  Paper saved: {filename}")
    print(f"  Preview: {paper_text[:200]}...")
    
    return {"domain": domain, "paper_file": str(filepath), "paper_preview": paper_text[:300]}


async def main():
    print("A.M.Y Multi-Domain Scientific Exploration")
    print("=" * 60)
    
    atlas = AtlasTools()
    llm = OllamaCloudClient(CONFIG["llm"])
    
    results = []
    for domain_info in DOMAINS:
        result = await explore_domain(atlas, llm, domain_info)
        results.append(result)
    
    # ── Summary ──────────────────────────────────────────────────────────
    print(f"\n\n{'='*60}")
    print("EXPLORATION COMPLETE")
    print(f"{'='*60}")
    for r in results:
        print(f"  {r['domain']}: {Path(r['paper_file']).name}")
    
    # Save summary
    summary_path = PAPERS_DIR / f"multi_domain_summary_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    summary_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nSummary saved: {summary_path}")


if __name__ == "__main__":
    asyncio.run(main())
