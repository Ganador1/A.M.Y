#!/usr/bin/env python3
"""
Test: A.M.Y genera un paper usando su ciclo cognitivo completo,
con herramientas Atlas + literatura real.
"""
import sys, os, json, asyncio, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "atlas"))

from core.heartbeat import Heartbeat
from core.global_workspace import GlobalWorkspace
from core.world_model import WorldModel
from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory
from memory.procedural import ProceduralMemory
from cognition.goal_stack import GoalStack
from cognition.curiosity import CuriosityModule
from cognition.reflection import ReflectionModule
from skills.library import SkillLibrary
from senses.web_sensor import WebSensor
from senses.time_sensor import TimeSensor
from communication.breakthrough_detector import BreakthroughDetector
from communication.report_generator import ReportGenerator

TEST_CONFIG = {
    "heartbeat": {
        "base_interval_seconds": 1.0,
        "focused_interval_seconds": 0.5,
        "idle_interval_seconds": 5.0,
        "max_cycles_before_reflection": 10,
        "adaptive_interval": False,
    },
    "mission": {
        "goal": "Verify hydrogen energy levels using quantum mechanics tools",
        "description": "Use Atlas quantum_energy_levels tool to verify Rydberg formula",
    },
    "memory": {
        "episodic_db": ":memory:",
        "semantic_db": ":memory:",
        "procedural_db": ":memory:",
    },
    "llm": {
        "provider": "ollama",
        "model": "gemini-3-flash-preview:cloud",
        "temperature": 0.7,
    },
    "curiosity": {
        "surprise_threshold": 0.7,
    },
    "communication": {
        "breakthrough_threshold": 0.9,
    },
    "skills": {
        "library_path": ":memory:",
    },
    "research": {},
}


class MockReasoningEngine:
    """Mock que simula el ciclo de razonamiento de A.M.Y."""
    
    def __init__(self):
        self.step = 0
        self.thoughts = [
            {
                "observation": "Hydrogen energy levels follow the Rydberg formula",
                "thought": "I should verify the Rydberg formula computationally",
                "hypothesis": "Hydrogen energy levels match E_n = -13.6/n^2 eV",
                "action_type": "run_scientific_tool",
                "action_details": {
                    "tool_name": "quantum_energy_levels",
                    "tool_input": "hydrogen:3",
                    "domain": "physics",
                },
                "new_facts": [
                    {"subject": "hydrogen_n3", "predicate": "energy", "object": "-1.5111 eV", "confidence": 1.0}
                ],
                "content": "Verifying hydrogen n=3 energy level",
                "surprise_assessment": 0.3,
                "progress_toward_goal": 0.3,
            },
            {
                "observation": "n=3 level confirmed at -1.5111 eV",
                "thought": "Now check n=5 and n=10 for scaling verification",
                "hypothesis": "Energy scales as 1/n^2 for all n",
                "action_type": "run_scientific_tool",
                "action_details": {
                    "tool_name": "quantum_energy_levels",
                    "tool_input": "hydrogen:5",
                    "domain": "physics",
                },
                "new_facts": [
                    {"subject": "hydrogen_n5", "predicate": "energy", "object": "-0.5440 eV", "confidence": 1.0}
                ],
                "content": "Verifying hydrogen n=5 energy level",
                "surprise_assessment": 0.2,
                "progress_toward_goal": 0.6,
            },
            {
                "observation": "Both n=3 and n=5 match Rydberg formula",
                "thought": "I have enough data to write a paper",
                "hypothesis": "The Rydberg formula is verified for n=1..10",
                "action_type": "write_paper",
                "action_details": {
                    "paper_topic": "Computational Verification of Hydrogen Energy Levels and the Rydberg Formula",
                    "domain": "physics",
                },
                "new_facts": [
                    {"subject": "rydberg_formula", "predicate": "verified_for_n", "object": "1_to_10", "confidence": 1.0}
                ],
                "content": "Writing paper on hydrogen energy level verification",
                "surprise_assessment": 0.1,
                "progress_toward_goal": 1.0,
            },
        ]
    
    async def reason(self, **kwargs):
        if self.step < len(self.thoughts):
            thought = self.thoughts[self.step]
            self.step += 1
            return thought
        return {"action_type": "think_more", "content": "Analysis complete"}
    
    async def generate_experiment_code(self, **kwargs):
        return "print('mock experiment')"


async def main():
    print("=" * 70)
    print("  A.M.Y GENERATES PAPER WITH REAL LITERATURE")
    print("=" * 70)
    
    # Initialize A.M.Y cognitive architecture
    print("\n[1/5] Initializing A.M.Y cognitive architecture...")
    episodic = EpisodicMemory(TEST_CONFIG["memory"])
    semantic = SemanticMemory(TEST_CONFIG["memory"])
    procedural = ProceduralMemory(TEST_CONFIG["memory"])
    world_model = WorldModel(semantic_memory=semantic, episodic_memory=episodic)
    goal_stack = GoalStack(TEST_CONFIG["mission"])
    curiosity = CuriosityModule(TEST_CONFIG["curiosity"])
    reflection = ReflectionModule(episodic_memory=episodic, semantic_memory=semantic)
    reasoning = MockReasoningEngine()
    reflection.reasoning_engine = reasoning
    workspace = GlobalWorkspace()
    skill_library = SkillLibrary(TEST_CONFIG["skills"])
    web_sensor = WebSensor(TEST_CONFIG["research"])
    time_sensor = TimeSensor()
    breakthrough = BreakthroughDetector(TEST_CONFIG["communication"])
    report_gen = ReportGenerator(TEST_CONFIG["communication"])
    
    heartbeat = Heartbeat(
        config=TEST_CONFIG["heartbeat"],
        world_model=world_model,
        goal_stack=goal_stack,
        curiosity=curiosity,
        reflection=reflection,
        reasoning=reasoning,
        workspace=workspace,
        episodic_memory=episodic,
        semantic_memory=semantic,
        procedural_memory=procedural,
        skill_library=skill_library,
        web_sensor=web_sensor,
        time_sensor=time_sensor,
        breakthrough_detector=breakthrough,
        report_generator=report_gen,
    )
    print("  ✅ Cognitive architecture initialized")
    
    # Run 2 tool executions + 1 paper write
    print("\n[2/5] Executing Atlas tools via A.M.Y heartbeat...")
    for cycle in range(3):
        print(f"\n  --- Cycle {cycle + 1} ---")
        await heartbeat._perceive()
        focus = await heartbeat._attend([])
        thought = await heartbeat._think(focus)
        action_result = await heartbeat._act(thought)
        await heartbeat._learn(thought, action_result)
        
        action_type = action_result.get("type", "unknown")
        if action_type == "run_scientific_tool":
            tool_name = action_result.get("tool_name", "unknown")
            success = action_result.get("success", False)
            icon = "✅" if success else "❌"
            result_preview = str(action_result.get("result", ""))[:80]
            print(f"  {icon} {tool_name}: {result_preview}")
        elif action_type == "write_paper":
            result = action_result.get("result", {})
            if "error" not in result:
                md_path = result.get("markdown_path", "N/A")
                word_count = result.get("word_count", 0)
                print(f"  ✅ Paper written: {md_path}")
                print(f"     Words: {word_count}")
                
                # Show the paper content
                if md_path and os.path.exists(md_path):
                    with open(md_path) as f:
                        content = f.read()
                    print(f"\n{'=' * 70}")
                    print("  PAPER CONTENT")
                    print(f"{'=' * 70}")
                    print(content[:2000])
                    print("...")
            else:
                print(f"  ❌ Paper error: {result.get('error')}")
    
    # Verify
    print(f"\n{'=' * 70}")
    print("  VERIFICATION")
    print(f"{'=' * 70}")
    
    tool_history = getattr(heartbeat, "_tool_results_history", [])
    print(f"  Tools executed: {len(tool_history)}")
    for tr in tool_history:
        print(f"    - {tr['tool_name']}: {str(tr['result'])[:60]}")
    
    papers = [f for f in os.listdir("papers") if f.endswith(".md") and "Hydrogen" in f or "Rydberg" in f]
    print(f"  Papers found: {len(papers)}")
    for p in sorted(papers, reverse=True)[:3]:
        size = os.path.getsize(os.path.join("papers", p))
        print(f"    - {p} ({size} bytes)")
    
    print(f"\n{'=' * 70}")
    print("  DONE")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    asyncio.run(main())
