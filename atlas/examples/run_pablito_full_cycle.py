"""Run a full autonomous hypothesis cycle with the enhanced ScientificHypothesisAgent (alias: pablito).

Steps:
 1. Generate hypothesis
 2. Start research cycle (auto-advances through phases and tool corroboration)
 3. Fetch final hypothesis + evidence analysis

This is a lightweight integration smoke to demonstrate end-to-end orchestration.
"""
from __future__ import annotations

import asyncio
from pprint import pprint

from app.services.scientific_hypothesis_agent import ScientificHypothesisAgent


async def main():
    agent = ScientificHypothesisAgent(agent_name="pablito")

    print("[1] Generating hypothesis...")
    gen = await agent.process_request({
        "action": "generate_hypothesis",
        "domain": "materials_science",
        "research_question": "How to improve thermal conductivity in LiFePO4 cathode materials?",
        "context_data": {"material": "LiFePO4"}
    })
    if not gen.get("success"):
        print("Generation failed:", gen)
        return
    hyp_id = gen["hypothesis_id"]

    print("[2] Starting research cycle (auto)...")
    cycle = await agent.process_request({"action": "start_research_cycle", "hypothesis_id": hyp_id})
    if not cycle.get("success"):
        print("Cycle start failed:", cycle)
        return

    # Retrieve internal cycle details
    rc = agent.research_cycles.get(cycle.get("cycle_id"))
    print("\n=== Research Cycle Summary ===")
    if rc:
        print("Phase:", rc.current_phase)
        print("Completed:", bool(rc.completed_at))
        print("Results keys:", list(rc.results.keys()))
        print("Tool corroboration aggregate:", rc.results.get("tool_corroboration", {}).get("aggregate"))

    print("\n[3] Evidence analysis...")
    evidence = await agent.process_request({"action": "analyze_evidence", "hypothesis_id": hyp_id})

    print("\n=== Final Hypothesis ===")
    hyp = agent.get_hypothesis({"hypothesis_id": hyp_id})
    pprint(hyp)

    print("\n=== Evidence Analysis ===")
    pprint(evidence)

    print("\nDone.")


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main())
