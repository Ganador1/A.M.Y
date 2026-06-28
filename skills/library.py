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

    def __init__(self, config: dict, semantic_index=None):
        # ":memory:" means an ephemeral, non-persistent library (used by tests).
        # SkillLibrary is directory-backed, not SQLite, so a literal ":memory:"
        # path would otherwise create a junk ":memory:/" directory on disk.
        raw_path = config.get("library_path", "./data/skill_library")
        self._ephemeral = raw_path == ":memory:"
        self.path = None if self._ephemeral else Path(raw_path)
        if self.path is not None:
            self.path.mkdir(parents=True, exist_ok=True)
        self.max_retrieval = config.get("max_retrieval", 5)
        # Optional embedding-backed retrieval (matches by meaning, not just
        # exact tokens). When None, retrieve() uses keyword matching as before.
        self.semantic_index = semantic_index
        self.skills: dict[str, dict] = {}
        self._load()

    def _load(self):
        if self._ephemeral:
            return
        index_file = self.path / "index.json"
        if index_file.exists():
            try:
                with open(index_file, "r") as f:
                    self.skills = json.load(f)
            except (json.JSONDecodeError, KeyError):
                self.skills = {}

    def _save(self):
        if self._ephemeral:
            return
        index_file = self.path / "index.json"
        with open(index_file, "w") as f:
            json.dump(self.skills, f, indent=2)

    async def register_skill(self, name: str, description: str, code: str):
        """Register a new skill in the library."""
        if self._ephemeral:
            code_file = f"<memory>/{name}.py"
        else:
            # Save code to its own file
            code_file = self.path / f"{name}.py"
            with open(code_file, "w") as f:
                f.write(code)

        # Preserve learned usage stats when re-registering an existing skill
        # (e.g. consolidation re-extracting the same experiment). Overwriting
        # them would silently discard the skill's success/failure history.
        existing = self.skills.get(name)
        self.skills[name] = {
            "description": description,
            "code_file": str(code_file),
            "code": code if self._ephemeral else None,
            "created_at": existing["created_at"] if existing else time.time(),
            "updated_at": time.time(),
            "times_used": existing.get("times_used", 0) if existing else 0,
            "success_count": existing.get("success_count", 0) if existing else 0,
            "failure_count": existing.get("failure_count", 0) if existing else 0,
        }
        self._save()
        # Index for semantic retrieval (best-effort; fail-soft).
        if self.semantic_index is not None:
            await self.semantic_index.add(
                doc_id=name,
                text=f"{name.replace('_', ' ')}. {description}",
                metadata={"name": name},
            )
        log.info("skill_library.registered", name=name, updated=existing is not None)

    async def retrieve(self, query: str) -> list[dict]:
        """Retrieve skills relevant to a query.

        Uses the embedding index (matches by meaning) when one is configured and
        returns hits; otherwise — and on any index miss/failure — falls back to
        keyword overlap so recall never depends on the network being up.
        """
        if self.semantic_index is not None:
            hits = await self.semantic_index.query(query, n_results=self.max_retrieval)
            results = []
            for h in hits:
                name = (h.get("metadata") or {}).get("name") or h.get("id")
                if name in self.skills:
                    results.append({"name": name, **self.skills[name]})
            if results:
                return results
            # else: fall through to keyword matching

        return self._keyword_retrieve(query)

    def _keyword_retrieve(self, query: str) -> list[dict]:
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
        if name not in self.skills:
            # Don't silently drop the reward signal — surface the mismatch.
            log.warning("skill_library.record_usage_unknown_skill", name=name)
            return
        self.skills[name]["times_used"] += 1
        if success:
            self.skills[name]["success_count"] += 1
        else:
            self.skills[name]["failure_count"] += 1
        self._save()
