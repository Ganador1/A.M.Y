"""
Misión autónoma: A.M.Y explora los límites del análisis de prime gaps.

A.M.Y tiene acceso a prime_gap_hpc y decide iterativamente hasta qué escala
empujar basándose en sus propios resultados. En cada ronda:
  1. Ejecuta prime_gap_hpc a la escala actual
  2. Interpreta los resultados con su LLM
  3. Decide si seguir subiendo, explorar variantes, o detenerse
  4. Al finalizar, genera un paper con sus propias observaciones

Sin límite de escala ni de rondas — A.M.Y decide absolutamente todo.
"""
import asyncio
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))

from core.atlas_tools import AtlasTools
from core.ollama_client import OllamaCloudClient as OllamaClient

PAPERS_DIR = Path(__file__).parent / "papers"
PAPERS_DIR.mkdir(exist_ok=True)

# Load config
with open(Path(__file__).parent / "config.yaml") as f:
    CONFIG = yaml.safe_load(f)

MODEL = CONFIG.get("reasoner", {}).get("model", "glm-5.1")

# ── A.M.Y's system prompt for this mission ───────────────────────────────────
SYSTEM_PROMPT = """You are A.M.Y (Autonomous Mind Yield), an autonomous scientific AI.
You are currently running a mathematical exploration mission: studying the distribution
of normalized prime gaps x_i = g_i / log(p_i) across increasing scales using the
prime_gap_hpc computational tool.

Your mission has NO externally imposed limit. You decide when you have gathered
enough evidence to write a meaningful scientific paper. You can push to 10^9, 10^10,
10^11 or beyond if you judge it worthwhile.

Scientific constraints you must respect:
- Be honest about what is and is not proven
- Finite-range computation is not a theorem
- Label all claims as "candidate observations" or "empirical findings"
- Every numerical result must come from actual tool output (no fabrication)
- The paper must cite real references (Cramér 1936, Granville 1995, Banks-Ford-Tao 2023,
  Oliveira e Silva et al. 2014, Kourbatov 2014/2019)

When interpreting results, consider:
- Is the KS-vs-1/log(N) OLS fit stable? Is R² converging?
- Is the intercept b stabilizing (suggesting an asymptotic residual)?
- Are maximal gap ratios consistent with Kourbatov's database?
- What does the tail ratio trend imply about convergence speed?
- Is there anything surprising worth noting?"""

DECISION_PROMPT = """You just ran prime_gap_hpc at scale N={N}.
Here are the results (truncated to key statistics):

{results_summary}

ACCUMULATED DATA across all runs so far:
{history_summary}

Now decide:
1. Should you run a LARGER scale? If yes, suggest the next N (e.g. 3e9, 1e10, 3e10, 1e11...).
   Reason: is the intercept still changing? Is R² improving? Are there surprises?
2. Should you run a VARIANT analysis? (e.g. different threshold t, or analyze only
   specific slab windows to zoom into a region)
3. Or is the data SUFFICIENT to write a strong paper? What would the key claims be?

Respond in JSON:
{{
  "decision": "continue" | "variant" | "write",
  "next_N": <float or null>,
  "variant_query": "<tool input if variant>" or null,
  "reasoning": "<2-3 sentences explaining the choice>",
  "key_observations": ["<obs1>", "<obs2>", ...]
}}"""

PAPER_PROMPT = """You have completed the following prime gap explorations:

{full_history}

Write a complete scientific paper in Markdown. Requirements:
- Title that reflects the actual scale reached and key finding
- Abstract: 150-200 words, includes all key quantitative results
- Introduction: context (Cramér, Granville, Banks-Ford-Tao), prior work, this paper's goal
- Methods: prime_gap_hpc tool, primesieve, streaming float32, OLS methodology
- Results: ALL tables from all runs, OLS fits across all scales, maximal gap records
- Discussion: what the intercept estimate means, comparison with Granville's prediction,
  convergence speed of tail ratio, limitations
- Conclusion: honest assessment of what was learned vs what remains unproven
- References: [1] Cramér 1936, [2] Granville 1995, [3] Banks-Ford-Tao 2023 doi:10.1007/s00222-023-01199-0,
  [4] Oliveira e Silva et al. 2014 doi:10.1090/S0025-5718-2013-02787-1,
  [5] Kourbatov 2014 doi:10.48550/arXiv.1401.6959, [6] Kourbatov 2019 doi:10.48550/arXiv.1901.03785
- Novelty Screen section: honest self-assessment
- Provenance section: all N values tested, wall times, tool SHA-256

The paper should reflect YOUR own scientific reasoning — what patterns you noticed,
what surprised you, what the data actually implies. Be a scientist, not a reporter."""


async def llm_chat(llm: OllamaClient, prompt: str, system: str = "",
                   temperature: float = 0.3, max_tokens: int = 2000,
                   timeout_seconds: float = 25.0) -> str:
    """Helper: call Ollama chat and return the message text. Timeout fallback."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    try:
        resp = await asyncio.wait_for(
            llm.chat(
                model=MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            ),
            timeout=timeout_seconds,
        )
        if isinstance(resp, dict):
            msg = resp.get("message", resp.get("response", ""))
            if isinstance(msg, dict):
                return msg.get("content", str(msg))
            return str(msg)
        return str(resp)
    except asyncio.TimeoutError:
        print(f"  [LLM timeout — pushing to next scale]")
        return '{"decision": "continue", "next_N": null, "reasoning": "LLM timeout, pushing to next scale", "key_observations": []}'
    except Exception as e:
        print(f"  [LLM error: {e} — pushing to next scale]")
        return '{"decision": "continue", "next_N": null, "reasoning": f"LLM error: {e}", "key_observations": []}'


async def parse_llm_decision(llm_text: str, current_N: float) -> dict:
    """Extract JSON decision from LLM response. Fallback: continue to next scale."""
    if not llm_text or not llm_text.strip():
        return {"decision": "continue", "next_N": current_N * 3, "reasoning": "LLM no response, pushing to next scale", "key_observations": []}
    try:
        m = re.search(r'\{.*\}', llm_text, re.DOTALL)
        if m:
            return json.loads(m.group())
    except Exception:
        pass
    text_lower = llm_text.lower()
    if "write" in text_lower and "paper" in text_lower:
        return {"decision": "write", "next_N": None, "reasoning": llm_text[:200], "key_observations": []}
    if "continue" in text_lower or "larger" in text_lower or "push" in text_lower:
        m2 = re.search(r'(\d+(?:\.\d+)?)\s*[eE]\s*(\d+)', llm_text)
        if m2:
            next_n = float(f"{m2.group(1)}e{m2.group(2)}")
            return {"decision": "continue", "next_N": next_n, "reasoning": llm_text[:200], "key_observations": []}
    # Default: push to next scale
    return {"decision": "continue", "next_N": current_N * 3, "reasoning": "Default: pushing to next scale", "key_observations": []}


def summarize_results(tool_output: str, max_chars: int = 2000) -> str:
    """Extract key statistics from tool output, discarding raw JSON."""
    lines = tool_output.split('\n')
    summary_lines = []
    in_json = False
    for line in lines:
        if 'JSON_DATA:' in line:
            in_json = True
            continue
        if in_json:
            continue
        summary_lines.append(line)
    summary = '\n'.join(summary_lines)
    return summary[:max_chars]


def build_history_summary(history: list) -> str:
    if not history:
        return "(no prior runs)"
    parts = []
    for run in history:
        ols = run.get("ols_ks", {})
        parts.append(
            f"N={run['N_limit']:,}: KS={run.get('ks_last', '?'):.6f}  "
            f"OLS_intercept={ols.get('intercept', '?'):.4f}  R²={ols.get('r2', '?'):.4f}  "
            f"max_gap={run.get('max_gap', '?')}  wall={run.get('wall_time', '?'):.1f}s"
        )
    return '\n'.join(parts)


def extract_json_data(tool_output: str) -> dict:
    """Parse the JSON_DATA section of tool output."""
    try:
        m = re.search(r'JSON_DATA:\s*(\{.*\})', tool_output, re.DOTALL)
        if m:
            return json.loads(m.group(1))
    except Exception:
        pass
    return {}


async def run_amy_prime_push():
    print("=" * 70)
    print("A.M.Y Prime Gap Autonomous Mission — No External Limit")
    print("A.M.Y decides scale, variants, and when to write the paper.")
    print("=" * 70)
    print()

    atlas = AtlasTools()
    llm   = OllamaClient(CONFIG["llm"])

    history = []
    all_tool_outputs = []

    # Starting scale — A.M.Y begins at 3e8 (already has 10^7 and 10^8 data)
    current_N = 3e8
    round_num = 0

    while True:
        round_num += 1
        N_str = f"{current_N:.2g}"
        print(f"\n{'─'*60}")
        print(f"Round {round_num}: Calling prime_gap_hpc({N_str})")
        print(f"{'─'*60}")

        t0 = time.perf_counter()
        tool_output = await atlas.run_scientific_tool(
            "prime_gap_hpc", N_str, domain="mathematics"
        )
        elapsed = time.perf_counter() - t0
        print(f"Tool finished in {elapsed:.1f}s")

        if tool_output.startswith("Blocked") or "Error" in tool_output[:50]:
            print(f"Tool returned error: {tool_output[:200]}")
            break

        all_tool_outputs.append({"N": int(current_N), "output": tool_output, "wall": elapsed})

        jdata = extract_json_data(tool_output)
        prefixes = jdata.get("prefixes", [])
        last_prefix = prefixes[-1] if prefixes else {}
        ols_ks = jdata.get("ols_ks", {})

        run_summary = {
            "N_limit":    int(current_N),
            "ks_last":    last_prefix.get("ks_exp1", float("nan")),
            "mean_norm":  last_prefix.get("mean_norm", float("nan")),
            "max_gap":    last_prefix.get("max_gap", 0),
            "max_gap_ratio": last_prefix.get("max_gap_ratio", 0),
            "ols_ks":     ols_ks,
            "wall_time":  elapsed,
        }
        history.append(run_summary)

        print(f"  KS={run_summary['ks_last']:.6f}  intercept={ols_ks.get('intercept', '?'):.4f}  "
              f"R²={ols_ks.get('r2', '?'):.4f}  max_gap={run_summary['max_gap']}")

        summary = summarize_results(tool_output)
        print("\n--- Tool summary ---")
        for line in summary.split('\n')[:25]:
            print(line)

        # ── Ask A.M.Y what to do next ─────────────────────────────────────
        print(f"\n[A.M.Y reasoning about round {round_num}...]")
        decision_text = await llm_chat(
            llm,
            prompt=DECISION_PROMPT.format(
                N=f"{int(current_N):,}",
                results_summary=summary,
                history_summary=build_history_summary(history),
            ),
            system=SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=1500,
        )
        print(f"A.M.Y:\n{decision_text[:800]}\n")

        decision = await parse_llm_decision(decision_text, current_N)
        print(f"Decision: {decision.get('decision')}  next_N={decision.get('next_N')}")
        print(f"Reasoning: {decision.get('reasoning', '')[:300]}")

        if decision.get("key_observations"):
            print("Key observations:")
            for obs in decision["key_observations"]:
                print(f"  • {obs}")

        if decision["decision"] == "write":
            print("\nA.M.Y decides the data is sufficient — writing paper...")
            break
        elif decision["decision"] == "variant":
            variant_q = decision.get("variant_query") or f"{current_N:.2g}"
            print(f"\nRunning variant analysis: {variant_q}")
            t0v = time.perf_counter()
            vout = await atlas.run_scientific_tool("prime_gap_hpc", variant_q, domain="mathematics")
            all_tool_outputs.append({"N": "variant", "output": vout, "wall": time.perf_counter() - t0v})
            next_n = decision.get("next_N")
            if next_n and float(next_n) > current_N:
                current_N = float(next_n)
        else:  # continue
            next_n = decision.get("next_N")
            if next_n and float(next_n) > current_N:
                current_N = float(next_n)
            else:
                # A.M.Y didn't give a clear next_N — push by 3x
                current_N = current_N * 3
                print(f"No next_N given — A.M.Y pushes to {current_N:.2g}")

    # ── Paper generation ─────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("A.M.Y is writing the paper...")
    print("=" * 70)

    full_history_text = ""
    for entry in all_tool_outputs:
        N_label = entry["N"] if isinstance(entry["N"], str) else f"{entry['N']:,}"
        out = entry["output"]
        summary = summarize_results(out, max_chars=3000)
        full_history_text += f"\n\n### Run N={N_label} (wall={entry['wall']:.1f}s)\n{summary}\n"

    paper_text = await llm_chat(
        llm,
        prompt=PAPER_PROMPT.format(full_history=full_history_text),
        system=SYSTEM_PROMPT,
        temperature=0.2,
        max_tokens=6000,
    )

    # ── Save paper ───────────────────────────────────────────────────────────
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    max_N_reached = max((e["N"] for e in all_tool_outputs if isinstance(e["N"], int)), default=0)
    paper_filename = f"Prime_Gap_AMY_Autonomous_{max_N_reached:.0e}_{timestamp}.md"
    paper_path = PAPERS_DIR / paper_filename

    tool_sha = hashlib.sha256(
        Path("atlas/app/run_agent_with_tools_legacy.py").read_bytes()
    ).hexdigest()
    provenance = f"""

---

## Provenance (auto-generated)

| Key | Value |
|---|---|
| Tool | `prime_gap_hpc` |
| Tool source SHA-256 | `{tool_sha}` |
| Scales tested | {', '.join(str(e['N']) for e in all_tool_outputs)} |
| Total wall time | {sum(e['wall'] for e in all_tool_outputs):.1f}s |
| Generated | {datetime.now(timezone.utc).isoformat()} |
| Safety gate | `core/safety_kernel.py` |

### Reproduction
```bash
cd "/Volumes/Ganador disk/A.M.Y" && source .venv/bin/activate && python run_amy_prime_push.py
```
"""
    paper_path.write_text(paper_text + provenance, encoding="utf-8")
    print(f"\nPaper saved: {paper_path}")
    print(f"\nFirst 500 chars:\n{paper_text[:500]}")

    state_path = PAPERS_DIR / f"prime_push_state_{timestamp}.json"
    state = {
        "history": history,
        "max_N": max_N_reached,
        "paper_file": str(paper_path),
    }
    state_path.write_text(json.dumps(state, indent=2, default=str))
    print(f"State saved: {state_path}")

    return paper_path


if __name__ == "__main__":
    asyncio.run(run_amy_prime_push())
