"""
A.M.Y — Autonomous Mind Yield
Entry point: starts the cognitive heartbeat and never stops.
"""
__version__ = "1.0.0"

import asyncio
import signal
import sys
from pathlib import Path

import yaml
import structlog

from core.heartbeat import Heartbeat
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
from communication.breakthrough_detector import BreakthroughDetector
from communication.report_generator import ReportGenerator
from senses.web_sensor import WebSensor
from senses.time_sensor import TimeSensor

log = structlog.get_logger()


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


class AMY:
    """
    The Autonomous Mind.
    Once started, she pursues her mission autonomously — thinking,
    researching, experimenting, learning — and only communicates
    through breakthroughs.
    """

    def __init__(self, config: dict):
        self.config = config
        self.running = False

        # --- Memory Systems ---
        self.episodic_memory = EpisodicMemory(config["memory"])
        self.semantic_memory = SemanticMemory(config["memory"])
        self.procedural_memory = ProceduralMemory(config["memory"])

        # --- World Model (Active Inference) ---
        self.world_model = WorldModel(
            semantic_memory=self.semantic_memory,
            episodic_memory=self.episodic_memory,
        )

        # --- Cognition ---
        self.goal_stack = GoalStack(config["mission"])
        self.curiosity = CuriosityModule(config["curiosity"])
        self.reflection = ReflectionModule(
            episodic_memory=self.episodic_memory,
            semantic_memory=self.semantic_memory,
        )
        self.reasoning = ReasoningEngine(config["llm"])

        # Give reflection access to the reasoning engine for LLM-powered metacognition
        self.reflection.reasoning_engine = self.reasoning

        # --- Global Workspace (Attention Bus) ---
        self.workspace = GlobalWorkspace()

        # --- Skills (optionally with embedding-backed retrieval) ---
        skill_index = None
        skills_cfg = config.get("skills", {})
        if skills_cfg.get("use_embedding_recall", False):
            from memory.semantic_index import SemanticIndex
            embed_model = skills_cfg.get("embedding_model", "embeddinggemma")

            async def _embed_one(text: str):
                vecs = await self.reasoning.client.embed(embed_model, text)
                return vecs[0] if vecs else []

            skill_index = SemanticIndex(_embed_one, name="amy_skills")
            log.info("amy.skill_embedding_recall_enabled", model=embed_model)
        self.skill_library = SkillLibrary(skills_cfg, semantic_index=skill_index)

        # --- Senses ---
        self.web_sensor = WebSensor(config.get("research", {}))
        self.time_sensor = TimeSensor()

        # --- Communication ---
        self.breakthrough_detector = BreakthroughDetector(
            config["communication"]
        )
        self.report_generator = ReportGenerator(config["communication"])

        # --- Heartbeat ---
        heartbeat_config = dict(config["heartbeat"])
        heartbeat_config["sandbox"] = config.get("sandbox", {})
        heartbeat_config["atlas_quality_gate"] = config.get("atlas_quality_gate", {})

        self.heartbeat = Heartbeat(
            config=heartbeat_config,
            world_model=self.world_model,
            goal_stack=self.goal_stack,
            curiosity=self.curiosity,
            reflection=self.reflection,
            reasoning=self.reasoning,
            workspace=self.workspace,
            episodic_memory=self.episodic_memory,
            semantic_memory=self.semantic_memory,
            procedural_memory=self.procedural_memory,
            skill_library=self.skill_library,
            web_sensor=self.web_sensor,
            time_sensor=self.time_sensor,
            breakthrough_detector=self.breakthrough_detector,
            report_generator=self.report_generator,
        )

    async def start(self):
        """Start the autonomous mind. She never stops until you tell her to."""
        self.running = True
        mission = self.config["mission"]
        log.info(
            "amy.awakening",
            goal=mission["goal"],
            description=mission.get("description", ""),
        )

        # Initialize goal stack with mission
        await self.goal_stack.set_mission(
            goal=mission["goal"],
            description=mission.get("description", ""),
        )

        # Start the heartbeat — the infinite loop of cognition
        log.info("amy.heartbeat.starting")
        await self.heartbeat.run()

    async def stop(self):
        """Gracefully stop the mind (consolidate memory first)."""
        log.info("amy.shutting_down")
        self.running = False
        await self.heartbeat.stop()
        await self.reflection.consolidate_before_shutdown()
        # Flush the debounced knowledge graph so changes since the last
        # interval save are not lost on shutdown.
        try:
            await self.semantic_memory.flush()
        except Exception as exc:
            log.warning("amy.semantic_flush_failed", error=str(exc))
        # Release the Ollama HTTP client (was leaked — close() was never called).
        try:
            await self.reasoning.close()
        except Exception as exc:
            log.warning("amy.reasoning_close_failed", error=str(exc))
        log.info("amy.shutdown_complete")


async def main():
    config = load_config()

    # Override goal from command line if provided
    import argparse
    parser = argparse.ArgumentParser(description="A.M.Y — Autonomous Mind Yield")
    parser.add_argument("--goal", type=str, help="The mission goal")
    parser.add_argument("--config", type=str, default="config.yaml", help="Config file path")
    args = parser.parse_args()

    if args.config != "config.yaml":
        config = load_config(args.config)
    if args.goal:
        config["mission"]["goal"] = args.goal

    amy = AMY(config)

    # Handle graceful shutdown
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(amy.stop()))

    try:
        await amy.start()
    except KeyboardInterrupt:
        await amy.stop()


def _cli():
    """Synchronous entry point for `amy` console script."""
    asyncio.run(main())


if __name__ == "__main__":
    _cli()
