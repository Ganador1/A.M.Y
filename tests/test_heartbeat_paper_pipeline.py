#!/usr/bin/env python3
"""Regression tests for A.M.Y heartbeat tool provenance and paper fallback."""

from __future__ import annotations

import json

from communication import paper_generator
from communication.paper_generator import PaperGenerator
from core import provenance
from core.heartbeat import Heartbeat


class FakeAtlasTools:
    async def run_scientific_tool(self, tool_name: str, tool_input: str, domain: str) -> str:
        assert tool_name == "sympy_prime_analysis"
        assert tool_input == "is_prime:97"
        assert domain == "mathematics"
        return "97 is prime: True"


class FakeMemory:
    def __init__(self):
        self.events = []

    async def record(self, **kwargs):
        self.events.append(kwargs)


class FakeWorldModel:
    def __init__(self):
        self.observations = []

    async def update_with_observations(self, observations):
        self.observations.extend(observations)


async def test_heartbeat_scientific_tool_execution_records_real_provenance(monkeypatch, tmp_path):
    manager = provenance.ProvenanceManager(base_dir=tmp_path)
    monkeypatch.setattr(provenance, "_provenance", manager)

    heartbeat = Heartbeat.__new__(Heartbeat)
    heartbeat._atlas_tools = FakeAtlasTools()
    heartbeat._tool_results_history = []
    heartbeat.episodic_memory = FakeMemory()
    heartbeat.world_model = FakeWorldModel()

    result = await heartbeat._act_run_scientific_tool(
        {
            "action_type": "run_scientific_tool",
            "action_details": {
                "tool_name": "sympy_prime_analysis",
                "tool_input": "is_prime:97",
                "domain": "mathematics",
            },
        }
    )

    assert result["success"] is True
    assert result["experiment_id"]
    record_path = tmp_path / result["experiment_id"] / "provenance.json"
    output_path = tmp_path / result["experiment_id"] / "output.txt"
    assert record_path.exists()
    assert output_path.read_text(encoding="utf-8") == "97 is prime: True"

    record = json.loads(record_path.read_text(encoding="utf-8"))
    assert record["tool"]["output_hash"]
    assert heartbeat._tool_results_history[-1]["experiment_id"] == result["experiment_id"]
    assert heartbeat.episodic_memory.events[-1]["metadata"]["experiment_id"] == result["experiment_id"]


async def test_paper_generator_offline_fallback_publishes_with_real_provenance(monkeypatch, tmp_path):
    experiments_dir = tmp_path / "experiments"
    papers_dir = tmp_path / "papers"
    papers_dir.mkdir(parents=True)
    monkeypatch.setattr(paper_generator, "EXPERIMENTS_DIR", experiments_dir)
    monkeypatch.setattr(paper_generator, "PAPERS_DIR", papers_dir)
    monkeypatch.setattr(paper_generator, "REJECTED_PAPERS_DIR", papers_dir / "rejected")

    manager = provenance.ProvenanceManager(base_dir=experiments_dir)
    record = manager.record_execution(
        tool_name="quantum_energy_levels",
        tool_input="hydrogen:3",
        tool_output="Hydrogen atom energy level n=3:\n  E_3 = -1.5111 eV",
        success=True,
        duration_seconds=0.1,
        domain="physics",
    )

    result = await PaperGenerator(reasoning_engine=object(), enhance=False).generate_from_llm(
        topic="Computational Verification of Hydrogen Energy Levels",
        knowledge_facts=[],
        recent_thoughts=["Hydrogen n=3 and n=5 follow the Rydberg scaling relation."],
        breakthrough_content="A calibration run reproduced expected hydrogen energy levels.",
        tool_sections=[
            {
                "heading": "Computational Verification",
                "content": "**quantum_energy_levels**\n- Input: `hydrogen:3`\n- Result: E_3 = -1.5111 eV",
            }
        ],
        experiment_ids=[record["experiment_id"]],
        literature_papers=[],
    )

    assert result["publication_status"] == "published"
    paper_text = (papers_dir / result["markdown_path"].split("/")[-1]).read_text(encoding="utf-8")
    assert "# Computational Verification of Hydrogen Energy Levels" in paper_text
    assert record["experiment_id"] in paper_text
    assert record["tool"]["output_hash"] in paper_text
