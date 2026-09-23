"""Goal focus through real planning, memory, workspace and reasoning methods.

Only the model/transport boundary is replaced. No model requests are sent;
the recorded fixture responses are not native AMY decisions or discoveries.
Unused action/report sensors are disabled, since these tests never call ACT.
"""
import copy
from dataclasses import asdict, dataclass
import json
import socket

import pytest

from cognition.curiosity import CuriosityModule
from cognition.goal_stack import GoalStack, GoalStatus
from cognition.reasoning import ReasoningEngine, REASONING_SYSTEM_PROMPT
from cognition.reflection import ReflectionModule
from core.execution_evidence import EvidenceRun, verify_run
from core.global_workspace import GlobalWorkspace
from core.heartbeat import Heartbeat
from core.world_model import WorldModel
from memory.episodic import EpisodicMemory
from memory.procedural import ProceduralMemory
from memory.semantic import SemanticMemory


MISSION = "ROOT CONTRACT: test finite models; report limitations honestly."


class FixtureModelTransport:
    """Explicit model-boundary double; no network, private inference or science."""

    def __init__(self):
        self.calls = []
        self.reply = {"action_type": "think_more", "content": "EXPLICIT TEST FIXTURE", "new_facts": []}

    async def chat(self, **kwargs):
        self.calls.append(copy.deepcopy(kwargs))
        return {"done": True, "done_reason": "stop", "message": {"content": json.dumps(self.reply)}}


@dataclass
class Harness:
    heartbeat: Heartbeat
    transport: FixtureModelTransport
    evidence: EvidenceRun

    def last_context(self):
        # Observe the real ReasoningEngine span; do not replace reason(),
        # receipt_context(), workspace, memory, or Heartbeat methods.
        events = [json.loads(line) for line in self.evidence.events_path.read_text().splitlines()]
        begin = next(event for event in reversed(events) if event["kind"] == "reasoning.decision.begin")
        payload = json.loads((self.evidence.path / begin["payload"]["path"]).read_text())
        return payload["input"]["context"]


@pytest.fixture(autouse=True)
def reject_real_network(monkeypatch):
    def deny(*args, **kwargs):
        raise AssertionError("goal-focus fixtures must never use real network transport")
    monkeypatch.setattr(socket, "getaddrinfo", deny)
    monkeypatch.setattr(socket.socket, "connect", deny)
    monkeypatch.setattr(socket.socket, "connect_ex", deny)


@pytest.fixture
def harness(tmp_path, monkeypatch):
    transport = FixtureModelTransport()
    monkeypatch.setattr("cognition.reasoning.OllamaCloudClient", lambda config: transport)
    # Credential bootstrap belongs to the disabled transport boundary.
    monkeypatch.setattr("core.ollama_client._load_env", lambda: None)
    reasoning = ReasoningEngine({"reasoner": {"model": "fixture-no-network"}, "fast": {"model": "fixture-no-network"}})
    episodic = EpisodicMemory({"episodic_log_path": str(tmp_path / "episodes.jsonl")})
    semantic = SemanticMemory({"knowledge_graph_path": str(tmp_path / "knowledge.json")})
    procedural = ProceduralMemory({"vector_db_path": str(tmp_path / "procedural")})
    reflection = ReflectionModule(episodic, semantic)
    reflection.reasoning_engine = reasoning
    heartbeat = Heartbeat(
        config={"base_interval_seconds": 1, "max_cycles": 120},
        world_model=WorldModel(semantic, episodic), goal_stack=GoalStack({}),
        curiosity=CuriosityModule({}), reflection=reflection, reasoning=reasoning,
        workspace=GlobalWorkspace(), episodic_memory=episodic,
        semantic_memory=semantic, procedural_memory=procedural,
        skill_library=None, web_sensor=None, time_sensor=None,
        breakthrough_detector=None, report_generator=None,
    )
    evidence = EvidenceRun(tmp_path / "evidence", metadata={"origin": "hermetic_test", "real_model_calls": 0})
    with evidence.activate():
        yield Harness(heartbeat, transport, evidence)
    seal = evidence.seal()
    assert verify_run(evidence.path, expected_root=seal["root_sha256"])["integrity_verified"] is True


async def start(harness, children=0):
    heartbeat = harness.heartbeat
    stack = heartbeat.goal_stack
    await stack.set_mission(MISSION)
    heartbeat._sync_current_goal_from_mission()
    heartbeat.ctx.cycle_number = 1
    ids = [await stack.push_subgoal(stack.mission_id, f"Pending fixture objective {index}", .7)
           for index in range(children)]
    return stack, ids


async def test_frontier_uses_child_and_grandchild_priorities_without_completing_root():
    stack = GoalStack({})
    await stack.set_mission(MISSION)
    assert (await stack.get_attention_candidate())["id"] == stack.mission_id
    parent = await stack.push_subgoal(stack.mission_id, "Parent fixture objective", .9)
    grandchild = await stack.push_subgoal(parent, "Executable grandchild fixture", .2)
    sibling = await stack.push_subgoal(stack.mission_id, "Higher-priority executable sibling", .5)
    # Priority applies to executable frontier nodes, not their higher-priority ancestors.
    assert (await stack.get_attention_candidate())["id"] == sibling
    await stack.complete_goal(sibling, "Explicit fixture transition")
    assert (await stack.get_attention_candidate())["id"] == grandchild
    await stack.complete_goal(grandchild, "Explicit fixture transition")
    assert (await stack.get_attention_candidate())["id"] == parent
    await stack.complete_goal(parent, "Explicit fixture transition")
    assert (await stack.get_attention_candidate())["id"] == stack.mission_id
    assert stack.goals[stack.mission_id].status is GoalStatus.ACTIVE
    assert stack.goals[stack.mission_id].description == MISSION


async def test_equal_priority_siblings_rotate_without_mutating_goals():
    stack = GoalStack({})
    await stack.set_mission(MISSION)
    peers = [await stack.push_subgoal(stack.mission_id, f"Equal-priority fixture {i}", .7) for i in range(3)]
    await stack.push_subgoal(stack.mission_id, "Lower-priority fixture", .2)
    before = {key: asdict(goal) for key, goal in stack.goals.items()}
    turns = [(await stack.get_attention_candidate())["id"] for _ in range(6)]
    assert set(turns[:3]) == set(turns[3:]) == set(peers)
    assert all(turns.count(goal_id) == 2 for goal_id in peers)
    assert {key: asdict(goal) for key, goal in stack.goals.items()} == before


async def test_old_mission_branch_cannot_reenter_attention_or_prompt(harness):
    stack, old_children = await start(harness, children=1)
    old_root = stack.mission_id
    old_child = old_children[0]
    next_mission = "CURRENT ROOT CONTRACT: separate mission."
    await stack.set_mission(next_mission)
    # Match Heartbeat's mission rollover, which updates stack and context
    # together. _sync_current_goal_from_mission only initializes an empty ctx.
    harness.heartbeat.ctx.current_goal = next_mission
    current = await stack.push_subgoal(stack.mission_id, "Current executable objective", .6)
    # Adversarial persisted state: old root and child are active and outrank current goals.
    for goal_id in (old_root, old_child):
        stack.goals[goal_id].status = GoalStatus.ACTIVE
        stack.goals[goal_id].priority = 2
    heartbeat = harness.heartbeat
    focus = await heartbeat._attend([])
    assert focus["goal_id"] == current
    await heartbeat._think(focus)
    context = harness.last_context()
    assert context["active_sub_goals"] == [stack.goals[current].description]
    assert context["active_sub_goal_window"]["visible_ids"] == [current]
    assert context["current_goal"] == stack.goals[stack.mission_id].description
    wire_prompt = harness.transport.calls[-1]["messages"][1]["content"]
    assert stack.goals[old_child].description not in wire_prompt
    assert MISSION not in wire_prompt


@pytest.mark.parametrize("status", [GoalStatus.COMPLETED, GoalStatus.FAILED, GoalStatus.DEFERRED, GoalStatus.BLOCKED])
async def test_ancestor_status_filters_both_focus_and_real_reasoning_context(harness, status):
    stack, parents = await start(harness, children=1)
    parent = parents[0]
    child = await stack.push_subgoal(parent, "Nested active fixture objective", .7)
    if status is GoalStatus.BLOCKED:
        await stack.report_impasse(parent, "Waiting for active child, not a verified conclusion")
    else:
        stack.goals[parent].status = status
    focus = await harness.heartbeat._attend([])
    expected = [child] if status is GoalStatus.BLOCKED else []
    assert focus["goal_id"] == (child if expected else stack.mission_id)
    await harness.heartbeat._think(focus)
    context = harness.last_context()
    assert context["active_sub_goal_window"]["visible_ids"] == expected
    assert context["active_sub_goals"] == [stack.goals[key].description for key in expected]
    assert stack.goals[parent].status is status
    assert stack.goals[child].status is GoalStatus.ACTIVE


async def test_five_goal_window_keeps_focus_id_and_eventually_shows_omitted_goals(harness):
    stack, ids = await start(harness, children=8)
    focused = ids[-1]
    stack.goals[focused].priority = .9
    initial = {key: asdict(goal) for key, goal in stack.goals.items()}
    shown = set()
    for cycle in range(1, 8):
        heartbeat = harness.heartbeat
        heartbeat.ctx.cycle_number = cycle
        focus = await heartbeat._attend([])
        assert focus["goal_id"] == focused
        assert heartbeat.workspace.get_recent_focus_history(1)[0]["goal_id"] == focused
        thought = await heartbeat._think(focus)
        assert thought["action_type"] == "think_more" and thought["cycle"] == cycle
        context = harness.last_context()
        visible = context["active_sub_goal_window"]["visible_ids"]
        assert len(visible) == 5 and len(set(visible)) == 5 and focused in visible
        assert context["active_sub_goals"] == [stack.goals[key].description for key in visible]
        assert context["active_sub_goal_count"] == 8
        assert context["active_sub_goal_window"]["omitted_count"] == 3
        assert context["current_goal"] == MISSION
        messages = harness.transport.calls[-1]["messages"]
        assert messages[0]["content"] == REASONING_SYSTEM_PROMPT
        assert "Showing 5 of 8 pending goals" in messages[1]["content"]
        assert MISSION in messages[1]["content"]
        shown.update(visible)
    assert shown == set(ids)
    assert {key: asdict(goal) for key, goal in stack.goals.items()} == initial
    assert len(harness.transport.calls) == 7


async def test_curiosity_may_win_without_inventing_a_goal_id_or_changing_mission(harness):
    stack, ids = await start(harness, children=8)
    heartbeat = harness.heartbeat
    heartbeat.ctx.surprise_level = 1
    heartbeat.ctx.cycle_number = 2
    focus = await heartbeat._attend([])
    assert focus["source"] == "curiosity" and "goal_id" not in focus
    assert heartbeat.workspace.get_recent_focus_history(1)[0] == focus
    await heartbeat._think(focus)
    context = harness.last_context()
    assert context["active_sub_goal_window"]["visible_ids"] == ids[1:6]
    assert context["active_sub_goal_window"]["omitted_count"] == 3
    assert context["current_goal"] == MISSION
    assert all(stack.goals[key].status is GoalStatus.ACTIVE for key in ids)


@pytest.mark.parametrize("nullable_field", ["loop_description", "diagnosis"])
async def test_null_reflection_metadata_keeps_complete_plan_through_real_reflect(harness, nullable_field):
    stack, _ = await start(harness)
    heartbeat = harness.heartbeat
    await heartbeat.episodic_memory.record("thought", "Explicit fixture episode; no scientific result")
    plan = ["Compare two declared finite fixture models", "Check an independent fixture limiting case"]
    response = {"loop_detected": False, "loop_description": "Fixture description", "diagnosis": "Fixture diagnosis",
                "new_subgoals": plan, "insights": [], "knowledge_gaps": [], "successful_strategies": []}
    response[nullable_field] = None
    harness.transport.reply = response
    await heartbeat.reflection.reflect(heartbeat.world_model, stack)
    current = await stack.get_current_active_goals()
    children = [goal for goal in current if goal["depth"] > 0]
    assert [goal["description"] for goal in children] == plan
    assert len(harness.transport.calls) == 1
    assert harness.transport.calls[0]["format_json"] is True
    assert stack.goals[stack.mission_id].description == MISSION
    assert stack.goals[stack.mission_id].status is GoalStatus.ACTIVE
    assert heartbeat.semantic_memory.facts == {} and heartbeat.semantic_memory.claims == {}
