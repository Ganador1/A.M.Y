"""
Procedural Memory — Learned skills and strategies.

Like the cerebellum/basal ganglia: stores "how to do things".
Combined with SOAR's chunking: when A.M.Y figures out how to
do something through deliberation, it gets compiled into a
reusable skill.
"""
import json
import time
from pathlib import Path

import structlog

log = structlog.get_logger()


class ProceduralMemory:
    def __init__(self, config: dict):
        self.path = Path(config.get("vector_db_path", "./data")) / "procedural_memory.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.skills: dict[str, dict] = {}
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                with open(self.path, "r") as f:
                    self.skills = json.load(f)
            except (json.JSONDecodeError, KeyError):
                self.skills = {}

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self.skills, f, indent=2)

    async def store_skill(self, name: str, description: str, code: str, success_rate: float = 1.0):
        """Store a learned skill."""
        self.skills[name] = {
            "description": description,
            "code": code,
            "success_rate": success_rate,
            "times_used": 0,
            "created_at": time.time(),
            "last_used": None,
        }
        self._save()
        log.info("procedural_memory.skill_stored", name=name)

    async def get_skill(self, name: str) -> dict | None:
        return self.skills.get(name)

    async def use_skill(self, name: str) -> dict | None:
        """Mark a skill as used and return it."""
        skill = self.skills.get(name)
        if skill:
            skill["times_used"] += 1
            skill["last_used"] = time.time()
            self._save()
        return skill

    async def list_skills(self) -> list[dict]:
        return [
            {"name": k, **v}
            for k, v in self.skills.items()
        ]
