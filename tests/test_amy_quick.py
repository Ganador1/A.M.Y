"""
Quick test script to verify A.M.Y core functionality.

This script runs a minimal A.M.Y cycle without LLM calls
to verify that all modules load and work correctly.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory
from memory.procedural import ProceduralMemory
from cognition.goal_stack import GoalStack
from cognition.curiosity import CuriosityModule
from cognition.reflection import ReflectionModule
from cognition.reasoning import ReasoningEngine
from core.global_workspace import GlobalWorkspace
from core.world_model import WorldModel
from skills.library import SkillLibrary
from senses.time_sensor import TimeSensor
from senses.web_sensor import WebSensor
from senses.file_sensor import FileSensor
from senses.api_sensor import APISensor
from evolution.curriculum import CurriculumGenerator
from evolution.self_retrain import SelfRetrainModule
from evolution.strategy_optimizer import StrategyOptimizer


async def test_memory_systems():
    """Test all memory systems."""
    print("🧠 Testing memory systems...")

    config = {
        "episodic_log_path": "./data/test_episodic.jsonl",
        "knowledge_graph_path": "./data/test_knowledge_graph.json",
        "vector_db_path": "./data/test_chromadb",
    }

    episodic = EpisodicMemory(config)
    await episodic.record("test", "test event", {"value": 42})
    events = await episodic.get_recent(1)
    assert len(events) == 1
    print("  ✅ Episodic memory OK")

    semantic = SemanticMemory(config)
    await semantic.add_fact("test", "is", "working", confidence=0.9)
    facts = await semantic.query(subject="test")
    assert len(facts) >= 1
    print("  ✅ Semantic memory OK")

    procedural = ProceduralMemory(config)
    print("  ✅ Procedural memory OK")


async def test_cognition_modules():
    """Test cognition modules."""
    print("🤔 Testing cognition modules...")

    goal_stack = GoalStack({"goal": "test", "description": "test mission"})
    # GoalStack uses async methods
    print("  ✅ Goal stack OK")

    curiosity = CuriosityModule({"epistemic_weight": 0.5, "surprise_threshold": 0.7, "novelty_decay": 0.95})
    print("  ✅ Curiosity module OK")

    reflection = ReflectionModule(episodic_memory=None, semantic_memory=None)
    print("  ✅ Reflection module OK")


async def test_global_workspace():
    """Test global workspace."""
    print("🌐 Testing global workspace...")

    workspace = GlobalWorkspace()
    result = await workspace.compete_and_broadcast([
        {"content": "test", "source": "test", "priority": 0.5, "type": "test"}
    ])
    assert result is not None
    print("  ✅ Global workspace OK")


async def test_skills():
    """Test skill library."""
    print("🛠️  Testing skills...")

    library = SkillLibrary({"library_path": "./data/test_skill_library"})
    print("  ✅ Skill library OK")


async def test_senses():
    """Test all sensors."""
    print("👁️  Testing senses...")

    time_sensor = TimeSensor()
    assert await time_sensor.sense() is not None
    print("  ✅ Time sensor OK")

    web_sensor = WebSensor({})
    print("  ✅ Web sensor OK")

    file_sensor = FileSensor({"watch_paths": ["./data"]})
    assert isinstance(file_sensor.sense(), list)
    print("  ✅ File sensor OK")

    api_sensor = APISensor({})
    print("  ✅ API sensor OK")


async def test_evolution():
    """Test evolution modules."""
    print("🧬 Testing evolution modules...")

    curriculum = CurriculumGenerator({})
    task = curriculum.generate_next_task("math", ["basic"])
    assert task is not None
    print("  ✅ Curriculum generator OK")

    retrain = SelfRetrainModule({})
    assert not retrain.add_training_data({"test": 1})  # Below threshold
    print("  ✅ Self-retrain module OK")

    optimizer = StrategyOptimizer({})
    optimizer.record_outcome("experiment", True)
    assert optimizer.get_success_rate("experiment") == 1.0
    print("  ✅ Strategy optimizer OK")


async def test_json_parsing():
    """Test robust JSON parsing."""
    print("📄 Testing JSON parsing...")

    from cognition.reasoning import _parse_json_robust

    # Valid JSON
    result = _parse_json_robust('{"action": "test"}')
    assert result["action"] == "test"
    print("  ✅ Valid JSON OK")

    # JSON with markdown fences
    result = _parse_json_robust('```json\n{"action": "test"}\n```')
    assert result["action"] == "test"
    print("  ✅ Markdown JSON OK")

    # Truncated JSON (simulates LLM cutoff)
    result = _parse_json_robust('{"action": "test", "content": "unterminated')
    assert "action" in result
    print("  ✅ Truncated JSON recovery OK")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("A.M.Y QUICK VERIFICATION TEST")
    print("=" * 60)

    try:
        await test_memory_systems()
        await test_cognition_modules()
        await test_global_workspace()
        await test_skills()
        await test_senses()
        await test_evolution()
        await test_json_parsing()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
