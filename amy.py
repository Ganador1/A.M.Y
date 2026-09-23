"""
A.M.Y — Autonomous Mind Yield
Entry point: starts the cognitive heartbeat and never stops.
"""
__version__ = "1.1.0rc1"

import asyncio
import hashlib
import re
import signal
import sysconfig
import uuid
from datetime import datetime, timezone
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
from evolution.self_retrain import SelfRetrainModule

log = structlog.get_logger()


def load_config(path: str = "config.yaml") -> dict:
    config_path = Path(path)
    if not config_path.exists() and config_path == Path("config.yaml"):
        installed_root = Path(sysconfig.get_path("data")) / "share" / "amy"
        for name in ("config.release.yaml", "config.yaml"):
            installed_default = installed_root / name
            if installed_default.exists():
                config_path = installed_default
                break
    with config_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def scoped_memory_config(config: dict) -> dict:
    """Return memory paths isolated to the active mission when configured.

    Earlier releases reused one knowledge graph and episodic log for every
    mission, allowing unrelated biomedical and mathematics facts to influence
    each other.  Mission scoping leaves legacy files untouched and gives each
    goal a stable directory under ``mission_memory_root``.
    """
    memory = dict(config.get("memory", {}))
    if not memory.get("namespace_by_mission", False):
        return memory

    explicit = str(memory.get("mission_namespace", "")).strip()
    goal = str(config.get("mission", {}).get("goal", "")).strip()
    if explicit:
        namespace = re.sub(r"[^a-z0-9_-]+", "-", explicit.lower()).strip("-")
        if not namespace:
            raise ValueError(
                "memory.mission_namespace must contain at least one "
                "letter or digit"
            )
    else:
        slug = re.sub(r"[^a-z0-9]+", "-", goal.lower()).strip("-")
        digest = hashlib.sha256(goal.encode("utf-8")).hexdigest()[:10]
        namespace = f"{slug[:48] or 'mission'}-{digest}"

    root = (
        Path(memory.get("mission_memory_root", "./data/missions")).expanduser()
        / namespace
    )
    memory["mission_namespace"] = namespace
    memory["knowledge_graph_path"] = str(root / "knowledge_graph.json")
    memory["episodic_log_path"] = str(root / "episodic_memory.jsonl")
    memory["vector_db_path"] = str(root / "vector_db")
    return memory


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
        self._stop_lock = asyncio.Lock()
        self._stopped = False

        # --- Memory Systems ---
        # Scope persistent state to the mission so facts and episodes from an
        # unrelated prior run cannot silently contaminate current reasoning.
        memory_config = scoped_memory_config(config)
        self.episodic_memory = EpisodicMemory(memory_config)
        self.semantic_memory = SemanticMemory(memory_config)
        self.procedural_memory = ProceduralMemory(memory_config)

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

        # --- Self-improvement (belief recalibration + meta-review feedback) ---
        # Previously defined but never wired into the live loop; the heartbeat
        # now drives it during reflection.
        self.self_retrain = SelfRetrainModule(config.get("evolution", {}))

        # --- Heartbeat ---
        heartbeat_config = dict(config["heartbeat"])
        heartbeat_config["sandbox"] = config.get("sandbox", {})
        heartbeat_config["atlas_quality_gate"] = config.get("atlas_quality_gate", {})
        heartbeat_config["atlas"] = config.get("atlas", {})

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
            self_retrain=self.self_retrain,
        )

    async def start(self):
        """Run the native cognitive loop with retained execution evidence."""
        from core.execution_evidence import EvidenceRun, current_evidence, evidence_span, record_event

        if current_evidence() is not None or not self.config.get("evidence", {}).get("enabled", True):
            return await self._start_with_provenance()
        root = Path(self.config.get("evidence", {}).get("root", "data/execution_evidence"))
        run_id = datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ_")+uuid.uuid4().hex[:12]
        source_root = Path(__file__).resolve().parent
        names = ["amy.py", "core/execution_evidence.py", "core/heartbeat.py", "core/ollama_client.py",
                 "core/model_broker.py", "core/atlas_tools.py", "core/atlas_worker.py", "core/provenance.py",
                 "cognition/reasoning.py", "sandbox/executor.py", "skills/code_experiment.py",
                 "communication/breakthrough_detector.py", "communication/report_generator.py",
                 "atlas/app/run_agent_with_tools_legacy.py", "atlas/app/extended_science_tools.py",
                 "atlas/app/h2_rhf_certificate.py", "atlas/app/h2_rhf_verifier.py"]
        # Snapshot the local runtime modules and explicit worker entrypoints.
        sources = {source_root/name for name in names if (source_root/name).is_file()}
        for package in ("core", "cognition", "memory", "skills", "communication", "senses", "evolution"):
            sources.update((source_root/package).glob("*.py"))
        sources.update(Path(name).resolve() for name in self.config.get("evidence", {}).get("additional_sources", []))
        run = EvidenceRun(root/run_id, metadata={"entrypoint": "amy.AMY.start", "config": _evidence_config(self.config),
                                               "attribution": "Native AMY runtime; operator supplies mission/configuration"},
                          source_paths=sorted(sources))
        self.evidence_path = str(run.path)
        status = "completed"
        try:
            with run.activate():
                with evidence_span("amy.lifecycle", {"mission": self.config["mission"]}) as span:
                    try:
                        initial_memory = {"semantic_facts": self.semantic_memory.facts,
                                          "semantic_claims": getattr(self.semantic_memory, "claims", {}),
                                          "experiment_receipts": getattr(self.heartbeat, "_experiment_receipts", {}),
                                          "episodic_tail": await self.episodic_memory.get_recent(n=1000),
                                          "skill_library": self.skill_library.skills}
                        # Fail before any model call if historical receipts cannot be
                        # bound to retained origin manifests and exact local bytes.
                        run.import_inherited_references(initial_memory, origin_root=root)
                        record_event("memory.initial", initial_memory)
                        await self._start_with_provenance()
                    finally:
                        await self.stop()
                    record_event("memory.final", {"semantic_facts": self.semantic_memory.facts,
                                                   "semantic_claims": getattr(self.semantic_memory, "claims", {}),
                                                   "experiment_receipts": getattr(self.heartbeat, "_experiment_receipts", {}),
                                                   "episodic_tail": await self.episodic_memory.get_recent(n=1000),
                                                   "skill_library": self.skill_library.skills})
                    span.result({"cycles": self.heartbeat.ctx.cycle_number, "status": "stopped"})
        except BaseException:
            status = "interrupted"
            raise
        finally:
            seal = run.seal(status=status)
            log.info("amy.evidence_sealed", path=str(run.path), root_sha256=seal["root_sha256"], status=status)

    async def _start_with_provenance(self):
        from core.provenance_epoch import provenance_epoch
        with provenance_epoch(self.config):
            return await self._start_impl()

    async def _start_impl(self):
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
        async with self._stop_lock:
            if self._stopped:
                return
            await self._stop_impl()
            self._stopped = True

    async def _stop_impl(self):
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


def _evidence_config(value):
    """Keep effective scientific parameters while excluding configured secrets."""
    if isinstance(value, dict):
        return {key: ("[credential omitted]" if any(token in str(key).lower() for token in
                    ("api_key", "password", "authorization", "access_token", "private_key", "secret"))
                      else _evidence_config(item)) for key, item in value.items()}
    if isinstance(value, list):
        return [_evidence_config(item) for item in value]
    return value


def _parse_args(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="A.M.Y — Autonomous Mind Yield")
    parser.add_argument("--goal", type=str, help="The mission goal")
    parser.add_argument("--config", type=str, default="config.yaml", help="Config file path")
    return parser.parse_args(argv)


def resolve_config(argv=None) -> dict:
    """Parse args, then load config from the resolved path exactly once.

    Args are parsed BEFORE loading any config: previously load_config() ran
    first and unconditionally opened the default config.yaml, so passing
    --config other.yaml still crashed if config.yaml was absent (and the
    default was loaded twice). The --goal override is applied here too.
    """
    args = _parse_args(argv)
    config = load_config(args.config)
    if args.goal:
        config["mission"]["goal"] = args.goal
    return config


async def main():
    config = resolve_config()

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
