"""Autonomous research agent entrypoint.

This module exists as the stable import target for:
- tests (e.g. `from run_agent_with_tools import autonomous_research_agent`)
- scripts (benchmarks, demos)

Implementation currently lives in `app/run_agent_with_tools_legacy.py`.
"""

from app.run_agent_with_tools_legacy import DynamicToolRegistry, ToolDescriptor, autonomous_research_agent

__all__ = [
    "DynamicToolRegistry",
    "ToolDescriptor",
    "autonomous_research_agent",
]
