"""Aging receipts and repeated model claims must not become unsupported facts."""
import copy
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from cognition.reasoning import ReasoningEngine
from core.experiment_context import compact_receipt, receipt_context
from core.heartbeat import Heartbeat
from core.world_model import WorldModel
from memory.semantic import SemanticMemory


def result(n, verified=True, bound=True):
    return {"experiment_id": f"actual-{n}", "tool_name": "h2_rhf_certificate",
            "result": f"raw-{n}", "assessment": {
                "certificate_verified": verified, "input_bound": bound,
                "verified_summary": {"energy_hartree": -1.2 + n/100,
                                     "scope": "numerical model only"}}}


def heartbeat():
    deps = dict.fromkeys(("world_model", "goal_stack", "curiosity", "reflection", "reasoning", "workspace",
                         "episodic_memory", "semantic_memory", "procedural_memory", "skill_library", "web_sensor",
                         "time_sensor", "breakthrough_detector", "report_generator"))
    return Heartbeat(config={"base_interval_seconds": 0}, **deps)


@pytest.mark.parametrize("verified,bound", [(False, True), (True, False), (1, True), (True, 1)])
def test_index_does_not_promote_unchecked_summaries(verified, bound):
    receipt = compact_receipt(result(0, verified, bound))
    assert receipt["certificate_verified"] is False
    assert "verified_summary" not in receipt


def test_receipts_are_detached_and_have_raw_hash():
    import hashlib
    original = result(0)
    receipt = compact_receipt(original)
    original["assessment"]["verified_summary"]["energy_hartree"] = 999
    assert receipt["verified_summary"]["energy_hartree"] == -1.2
    assert receipt["raw_output_sha256"] == hashlib.sha256(b"raw-0").hexdigest()
    visible = receipt_context({"actual-0": receipt})
    visible["visible_receipts"][0]["verified_summary"]["energy_hartree"] = 222
    assert receipt["verified_summary"]["energy_hartree"] == -1.2


async def test_real_think_preserves_oldest_id_after_raw_history_eviction():
    hb = heartbeat()
    for n in range(25):
        value = result(n)
        hb._tool_results_history.append(value)
        hb._experiment_receipts[value["experiment_id"]] = compact_receipt(value)
    assert all(r["experiment_id"] != "actual-0" for r in hb._tool_results_history)
    from cognition.goal_stack import GoalStack
    hb.goal_stack = GoalStack({})
    hb.reasoning = SimpleNamespace(reason=AsyncMock(return_value={"content": "CI test"}))
    await hb._think({})
    context = hb.reasoning.reason.call_args.kwargs["context"]
    assert len(context["recent_tool_results"]) == 3
    engine = ReasoningEngine.__new__(ReasoningEngine)
    engine.config = {"tool_observation_mode": "certified_summary"}
    prompt = engine._build_reasoning_prompt({}, context, None)[1]["content"]
    assert '"experiment_id": "actual-0"' in prompt and '"energy_hartree": -1.2' in prompt
    assert '"omitted_receipts": 0' in prompt


def test_context_overflow_is_explicit_and_index_remains_complete():
    index = {f"actual-{n}": compact_receipt(result(n)) for n in range(70)}
    before = copy.deepcopy(index)
    visible = receipt_context(index)
    assert len(visible["visible_receipts"]) == 64
    assert visible["omitted_receipts"] == 6 and visible["total_receipts"] == 70
    assert receipt_context(index, character_budget=1)["omitted_receipts"] == 70
    assert index == before


def test_control_arm_omits_only_index_from_prompt():
    engine = ReasoningEngine.__new__(ReasoningEngine)
    engine.config = {"experiment_receipt_context": False}
    context = {"experiment_receipt_index": receipt_context({"actual-0": compact_receipt(result(0))})}
    assert "actual-0" not in engine._build_reasoning_prompt({}, context, None)[1]["content"]
    engine.config["experiment_receipt_context"] = True
    assert "actual-0" in engine._build_reasoning_prompt({}, context, None)[1]["content"]


def test_native_ablation_has_same_missions_and_isolated_memories(tmp_path):
    from scripts.run.run_receipt_memory_validation import make_validation_plan, prepare_validation
    plan = make_validation_plan()
    assert len(plan["rows"]) == 12 and len({r["id"] for r in plan["rows"]}) == 12
    assert {r["memory_profile"] for r in plan["rows"]} == {"index_visible", "recent_only"}
    configs = [prepare_validation(tmp_path, plan, r)[1] for r in plan["rows"][:2]]
    assert configs[0]["mission"] == configs[1]["mission"]
    assert configs[0]["llm"]["experiment_receipt_context"] is True
    assert configs[1]["llm"]["experiment_receipt_context"] is False
    assert configs[0]["memory"]["mission_memory_root"] != configs[1]["memory"]["mission_memory_root"]
    assert all(c["evidence"]["enabled"] and c["heartbeat"]["require_tool_certificate"] for c in configs)


async def test_model_claims_are_retained_without_promoting_or_updating_facts(tmp_path):
    path = tmp_path/"graph.json"
    sm = SemanticMemory({"knowledge_graph_path": str(path)})
    await sm.add_fact("legacy", "is", "preserved", .8, "old")
    kwargs = dict(subject="claim", predicate="is", obj="true", model_confidence=.99,
                  experiment_ids=["real-1", "invented"], known_experiment_ids=["real-1"])
    for i in range(30):
        await sm.add_claim(**kwargs, source=f"cycle_{i}")
    await sm.flush()
    loaded = SemanticMemory({"knowledge_graph_path": str(path)})
    assert list(loaded.facts) == ["legacy|is|preserved"]
    claim, = loaded.claims.values()
    assert claim["verification_status"] == "unverified_model_claim"
    assert claim["times_reported"] == 30 and len(claim["observations"]) == 25
    assert claim["interpretation_verified"] is False and "confidence" not in claim
    assert claim["observations"][-1]["known_experiment_ids"] == ["real-1"]
    assert len(await loaded.get_high_confidence()) == 1


@pytest.mark.parametrize("confidence", [float("nan"), float("inf"), -1, 2, True, "certain"])
async def test_invalid_model_confidence_remains_unknown(tmp_path, confidence):
    sm = SemanticMemory({"knowledge_graph_path": str(tmp_path/"graph.json")})
    claim = await sm.add_claim("a", "b", "c", model_confidence=confidence)
    assert claim["observations"][0]["model_confidence"] is None
    json.dumps(claim, allow_nan=False)


async def test_native_learning_cannot_launder_repetition_into_world_model_confirmation(tmp_path):
    hb = heartbeat()
    hb.semantic_memory = SemanticMemory({"knowledge_graph_path": str(tmp_path/"graph.json")})
    hb.episodic_memory = SimpleNamespace(record=AsyncMock())
    hb.curiosity = SimpleNamespace(update=AsyncMock())
    hb.world_model = WorldModel(hb.semantic_memory, hb.episodic_memory)
    hb._experiment_receipts = {"actual-0": compact_receipt(result(0))}
    thought = {"content": "claim", "new_facts": [{"subject": "an experiment", "predicate": "proves",
               "object": "a universal law", "confidence": .99, "experiment_ids": ["actual-0", "invented"]}]}
    for _ in range(5):
        await hb._learn(thought, {"type": "think_more", "success": True})
    assert not hb.semantic_memory.facts and not hb.world_model.beliefs
    claim, = hb.semantic_memory.claims.values()
    assert claim["times_reported"] == 5 and claim["interpretation_verified"] is False
    assert claim["observations"][0]["known_experiment_ids"] == ["actual-0"]
