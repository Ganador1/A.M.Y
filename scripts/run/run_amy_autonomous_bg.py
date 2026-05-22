#!/usr/bin/env python3
"""
A.M.Y Autonomous Mission Runner — Background Edition

Ejecuta misiones científicas autónomas y guarda logs en archivo.
Uso: nohup python run_amy_autonomous_bg.py --duration 3600 > amy_autonomous.log 2>&1 &

Para ver progreso en tiempo real:
  tail -f amy_autonomous.log
"""
import argparse
import asyncio
import json
import random
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "atlas"))

from core.atlas_tools import AtlasTools
from core.provenance import ProvenanceManager
from communication.paper_generator import PaperGenerator
from communication.paper_enhancer import PaperEnhancer


# Misiones por dominio
MISSIONS = {
    "mathematics": {
        "topic": "Mathematical Analysis",
        "tools": [
            ("sympy_solve_equation", "x**2 - 4 = 0", "Equation solving"),
            ("sympy_derivative", "x**3, x", "Derivative calculation"),
            ("sympy_integrate", "x**2, x", "Integral calculation"),
            ("prime_gap_analysis", "1000", "Prime gap distribution"),
            ("number_theory_advanced", "goldbach:100", "Goldbach conjecture"),
        ],
    },
    "chemistry": {
        "topic": "Molecular Structure Analysis",
        "tools": [
            ("molecular_weight_calc", "C6H12O6", "Glucose molecular weight"),
            ("molecular_weight_calc", "H2O", "Water molecular weight"),
            ("bond_energy_analyzer", "C-C", "Carbon bond energy"),
        ],
    },
    "physics": {
        "topic": "Quantum Energy Analysis",
        "tools": [
            ("quantum_energy_levels", "hydrogen:3", "Hydrogen n=3"),
            ("quantum_energy_levels", "hydrogen:5", "Hydrogen n=5"),
        ],
    },
    "biology": {
        "topic": "DNA Sequence Analysis",
        "tools": [
            ("dna_analyzer", "ATCGATCGATCGATCGATCG", "DNA composition"),
            ("protein_properties", "MVLSPADKTNVKAAWGKVGA", "Protein analysis"),
        ],
    },
    "statistics": {
        "topic": "Statistical Analysis",
        "tools": [
            ("numpy_statistics", "summary:[1,2,3,4,5,6,7,8,9,10]", "Basic statistics"),
            ("numpy_distribution", "normal:1000,0,1", "Normal distribution"),
        ],
    },
}

LOG_FILE = Path("amy_autonomous.log")
STATE_FILE = Path("amy_autonomous_state.json")


def log(message: str):
    """Log to file and stdout."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def save_state(state: dict):
    """Save current state to JSON file."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


class AutonomousAMY:
    """A.M.Y running autonomously in background."""
    
    def __init__(self, duration_seconds: int = 3600, fixed_domain: str = None):
        self.duration = duration_seconds
        self.fixed_domain = fixed_domain
        self.tools = None
        self.pg = PaperGenerator(reasoning_engine=None, enhance=True)
        self.enhancer = PaperEnhancer()
        self.provenance = ProvenanceManager()
        self.mission_count = 0
        self.tool_count = 0
        self.paper_count = 0
        self.start_time = time.time()
        self.errors = []
        
    def _init_tools(self):
        """Initialize Atlas tools (takes time on first call)."""
        if self.tools is None:
            log("🔧 Initializing Atlas tools (first time, may take 30-60s)...")
            self.tools = AtlasTools()
            log("✅ Atlas tools ready!")
        
    def should_continue(self) -> bool:
        elapsed = time.time() - self.start_time
        return elapsed < self.duration
    
    async def run_single_tool(self, tool_name: str, tool_input: str, description: str, domain: str = "mathematics") -> dict:
        """Run a single tool with timeout and provenance tracking."""
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
            result_str = str(result)[:400]
            # Record provenance
            prov = self.provenance.record_execution(
                tool_name=tool_name, tool_input=tool_input,
                tool_output=str(result), success=True,
                duration_seconds=duration, domain=domain,
            )
            return {
                "tool": tool_name, "description": description,
                "result": result_str, "success": True,
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
            return {"tool": tool_name, "description": description, "result": "Timeout after 90s", "success": False}
        except Exception as e:
            duration = time.time() - start
            self.provenance.record_execution(
                tool_name=tool_name, tool_input=tool_input,
                tool_output=str(e)[:200], success=False,
                duration_seconds=duration, domain=domain,
            )
            return {"tool": tool_name, "description": description, "result": str(e)[:200], "success": False}
    
    async def run_mission(self) -> dict:
        """Run one complete mission."""
        self.mission_count += 1
        
        # Select domain
        if self.fixed_domain:
            domain = self.fixed_domain
        else:
            domain = random.choice(list(MISSIONS.keys()))
        
        mission = MISSIONS[domain]
        log(f"🚀 Mission #{self.mission_count}: {domain.upper()} - {mission['topic']}")
        
        # Select 2-3 tools
        num_tools = random.randint(2, min(3, len(mission['tools'])))
        selected_tools = random.sample(mission['tools'], num_tools)
        
        # Execute tools one by one with provenance tracking
        results = []
        for tool_name, tool_input, description in selected_tools:
            result = await self.run_single_tool(tool_name, tool_input, description, domain=domain)
            results.append(result)
            if result["success"]:
                self.tool_count += 1
                prov_id = result.get("provenance_id", "N/A")
                log(f"  ✅ {description}: {result['result'][:50]} [prov: {prov_id}]")
            else:
                log(f"  ❌ {description}: {result['result'][:60]}")
        
        # Generate paper if we have results
        successful = [r for r in results if r["success"]]
        if len(successful) >= 1:
            try:
                paper = await self.generate_paper(domain, mission['topic'], successful)
                self.paper_count += 1
                log(f"  📄 Paper generated: {paper.get('word_count', 0)} words")
            except Exception as e:
                log(f"  ⚠️  Paper generation failed: {e}")
                self.errors.append(str(e))
        
        # Save state
        save_state({
            "mission_count": self.mission_count,
            "tool_count": self.tool_count,
            "paper_count": self.paper_count,
            "elapsed_seconds": time.time() - self.start_time,
            "duration_seconds": self.duration,
            "last_mission": domain,
            "errors": self.errors[-5:],
        })
        
        return {
            "domain": domain,
            "tools_executed": len(successful),
            "tools_failed": len([r for r in results if not r["success"]]),
        }
    
    async def generate_paper(self, domain: str, topic: str, results: list) -> dict:
        """Generate a paper from results with real provenance IDs."""
        tool_sections = []
        experiment_ids = []
        provenance_verified = []
        
        for i, r in enumerate(results):
            tool_sections.append({
                "heading": f"{r['description']} ({r['tool']})",
                "content": f"**Input:** `{r['tool']}`\n\n**Result:**\n{r['result'][:500]}",
            })
            # Use real provenance ID if available
            prov_id = r.get("provenance_id", f"{domain}_{r['tool']}_{i}")
            experiment_ids.append(prov_id)
            verified = self.provenance.verify_experiment_id(prov_id)
            provenance_verified.append(verified)
        
        # Log provenance verification
        verified_count = sum(1 for v in provenance_verified if v["exists"])
        log(f"  📋 Provenance: {verified_count}/{len(experiment_ids)} experiment IDs verified")
        
        sections = [
            {"heading": "Introduction", "content": f"Study of {topic} using computational methods."},
            {"heading": "Methods", "content": f"Used {len(tool_sections)} Atlas tools."},
            {"heading": "Results", "content": "\n\n".join([f"### {s['heading']}\n{s['content']}" for s in tool_sections])},
            {"heading": "Discussion", "content": "Results demonstrate computational verification."},
            {"heading": "Conclusion", "content": "Analysis confirms findings."},
        ]
        
        return await self.pg.generate_paper(
            title=f"Computational Analysis of {topic}",
            abstract=f"Analysis of {topic} using {len(tool_sections)} computational tools.",
            sections=sections,
            references=["A.M.Y (2026). AXIOM Atlas Platform."],
            knowledge_facts=[{"subject": domain, "predicate": "analyzed", "object": "Atlas", "confidence": 0.95}],
            experiment_ids=experiment_ids,
            domain=domain,
            tool_results=results,
        )
    
    async def run(self):
        """Main autonomous loop."""
        log("=" * 70)
        log("A.M.Y AUTONOMOUS MISSION STARTED")
        log(f"Duration: {self.duration} seconds ({self.duration/60:.0f} minutes)")
        log(f"Domain: {self.fixed_domain or 'ALL (random)'}")
        log("=" * 70)
        
        # Initialize tools
        self._init_tools()
        
        while self.should_continue():
            try:
                await self.run_mission()
                
                # Stats
                elapsed = time.time() - self.start_time
                remaining = self.duration - elapsed
                log(f"📊 Stats: {self.mission_count} missions, {self.tool_count} tools, {self.paper_count} papers")
                log(f"⏱️  Remaining: {remaining/60:.0f} minutes")
                
                # Wait between missions
                if self.should_continue():
                    wait_time = random.randint(3, 8)
                    log(f"😴 Sleeping {wait_time}s before next mission...")
                    await asyncio.sleep(wait_time)
                    
            except Exception as e:
                log(f"💥 Error in mission: {e}")
                self.errors.append(str(e))
                await asyncio.sleep(10)
        
        # Final report
        log("=" * 70)
        log("A.M.Y AUTONOMOUS MISSION COMPLETED")
        log("=" * 70)
        log(f"Total missions: {self.mission_count}")
        log(f"Total tools executed: {self.tool_count}")
        log(f"Total papers generated: {self.paper_count}")
        log(f"Duration: {(time.time() - self.start_time)/60:.1f} minutes")
        if self.errors:
            log(f"Errors encountered: {len(self.errors)}")


def main():
    parser = argparse.ArgumentParser(description="Run A.M.Y autonomously in background")
    parser.add_argument("--duration", type=int, default=3600, help="Duration in seconds (default: 3600 = 1 hour)")
    parser.add_argument("--domain", type=str, default=None, help="Fixed domain (default: random)")
    args = parser.parse_args()
    
    # Clear old log
    if LOG_FILE.exists():
        LOG_FILE.unlink()
    
    amy = AutonomousAMY(duration_seconds=args.duration, fixed_domain=args.domain)
    asyncio.run(amy.run())


if __name__ == "__main__":
    main()
