"""
Skill Library — Reusable capabilities that grow over time.

Based on Voyager's skill library pattern:
- Each skill is executable code indexed by semantic description
- Skills compose (complex skills call simpler ones)
- New skills are learned from successful experiments
- Skills are retrieved by similarity when facing new problems
"""
import json
import time
from pathlib import Path

import structlog

log = structlog.get_logger()


class SkillLibrary:
    """
    A.M.Y's growing repertoire of abilities.
    
    Unlike Voyager (which only stores code), A.M.Y also stores:
    - The context in which the skill was learned
    - Success/failure rates
    - Dependencies on other skills
    """

    def __init__(self, config: dict):
        self.path = Path(config.get("library_path", "./data/skill_library"))
        self.path.mkdir(parents=True, exist_ok=True)
        self.max_retrieval = config.get("max_retrieval", 5)
        self.skills: dict[str, dict] = {}
        self._load()

    def _load(self):
        index_file = self.path / "index.json"
        if index_file.exists():
            try:
                with open(index_file, "r") as f:
                    self.skills = json.load(f)
            except (json.JSONDecodeError, KeyError):
                self.skills = {}

    def _save(self):
        index_file = self.path / "index.json"
        with open(index_file, "w") as f:
            json.dump(self.skills, f, indent=2)

    async def register_skill(self, name: str, description: str, code: str):
        """Register a new skill in the library."""
        # Save code to its own file
        code_file = self.path / f"{name}.py"
        with open(code_file, "w") as f:
            f.write(code)

        self.skills[name] = {
            "description": description,
            "code_file": str(code_file),
            "created_at": time.time(),
            "times_used": 0,
            "success_count": 0,
            "failure_count": 0,
        }
        self._save()
        log.info("skill_library.registered", name=name)

    async def retrieve(self, query: str) -> list[dict]:
        """
        Retrieve skills relevant to a query.
        Simple keyword matching for now — embeddings later.
        """
        query_words = set(query.lower().split())
        scored = []

        for name, skill in self.skills.items():
            desc_words = set(skill["description"].lower().split())
            name_words = set(name.lower().replace("_", " ").split())
            overlap = len(query_words & (desc_words | name_words))
            if overlap > 0:
                scored.append((overlap, {"name": name, **skill}))

        scored.sort(key=lambda x: -x[0])
        return [s[1] for s in scored[: self.max_retrieval]]

    async def list_skills(self) -> list[dict]:
        return [{"name": k, **v} for k, v in self.skills.items()]

    async def record_usage(self, name: str, success: bool):
        """Track skill usage and success rate."""
        if name in self.skills:
            self.skills[name]["times_used"] += 1
            if success:
                self.skills[name]["success_count"] += 1
            else:
                self.skills[name]["failure_count"] += 1
            self._save()
