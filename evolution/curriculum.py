"""
Curriculum — Automatic curriculum generation for skill learning.

Inspired by Voyager's automatic curriculum, this module generates
a sequence of increasingly difficult tasks for A.M.Y to learn new skills.
"""
import structlog

log = structlog.get_logger()


class CurriculumGenerator:
    """Generates learning curricula for autonomous skill acquisition."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.difficulty_levels = self.config.get("difficulty_levels", 5)
        self.current_level = 0
        self.completed_tasks: list[dict] = []

    def generate_next_task(self, skill_domain: str, current_skills: list[str]) -> dict | None:
        """Generate the next learning task based on current progress."""
        if self.current_level >= self.difficulty_levels:
            log.info("curriculum.complete", domain=skill_domain)
            return None

        task = {
            "level": self.current_level,
            "domain": skill_domain,
            "description": f"Learn {skill_domain} at level {self.current_level + 1}/{self.difficulty_levels}",
            "prerequisites": current_skills,
            "success_criteria": f"Successfully apply {skill_domain} technique in an experiment",
        }

        self.current_level += 1
        log.info("curriculum.task_generated", level=task["level"], domain=skill_domain)
        return task

    def mark_completed(self, task: dict, success: bool = True):
        """Mark a task as completed."""
        self.completed_tasks.append({
            **task,
            "success": success,
        })
        if not success:
            # Retry same level
            self.current_level = task["level"]
            log.info("curriculum.retry", level=task["level"])

    def get_progress(self) -> dict:
        """Return current curriculum progress."""
        return {
            "current_level": self.current_level,
            "total_levels": self.difficulty_levels,
            "completed_tasks": len(self.completed_tasks),
            "success_rate": sum(1 for t in self.completed_tasks if t["success"]) / max(len(self.completed_tasks), 1),
        }
