"""
Goal Stack — Hierarchical goal management with recursive decomposition.

Inspired by SOAR's universal subgoaling:
- When a goal can't be achieved directly → create sub-goals
- Sub-goals can create sub-sub-goals (recursive)
- When a sub-goal is achieved, its result "chunks" back up
- Goals have priority, deadlines, and dependency tracking
"""
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class GoalStatus(Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"    # Waiting on sub-goal or external info
    COMPLETED = "completed"
    FAILED = "failed"
    DEFERRED = "deferred"  # Pushed down to explore something else


@dataclass
class Goal:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = ""
    parent_id: str | None = None
    status: GoalStatus = GoalStatus.ACTIVE
    priority: float = 0.5  # 0-1
    created_at: float = field(default_factory=time.time)
    completed_at: float | None = None
    depth: int = 0  # 0 = mission, 1 = sub-goal, 2 = sub-sub-goal, ...
    result: str = ""
    sub_goal_ids: list[str] = field(default_factory=list)
    attempts: int = 0
    max_attempts: int = 10


class GoalStack:
    """
    The hierarchical goal system.
    
    A.M.Y always has a mission (top-level goal). This decomposes
    into sub-goals, which may further decompose. Like SOAR,
    when A.M.Y hits an "impasse" (can't progress), she automatically
    creates sub-goals to resolve it.
    
    The stack never empties while the mission is active.
    If all sub-goals complete, new ones are generated based on
    what was learned (curriculum generation, like Voyager).
    """

    def __init__(self, mission_config: dict):
        self.goals: dict[str, Goal] = {}
        self.mission_id: str | None = None

    async def set_mission(self, goal: str, description: str = ""):
        """Set the top-level mission. Replaces any previous mission."""
        # Archive old goals
        for g in self.goals.values():
            if g.status == GoalStatus.ACTIVE:
                g.status = GoalStatus.COMPLETED

        mission = Goal(
            description=goal,
            priority=1.0,
            depth=0,
        )
        self.goals[mission.id] = mission
        self.mission_id = mission.id
        log.info("goal_stack.mission_set", goal=goal, id=mission.id)

    async def push_subgoal(self, parent: str, description: str, priority: float = 0.5) -> str:
        """Create a sub-goal under a parent goal."""
        # Find parent by description if not an ID
        parent_goal = self._find_goal(parent)
        if not parent_goal:
            parent_goal = self.goals.get(self.mission_id)

        subgoal = Goal(
            description=description,
            parent_id=parent_goal.id if parent_goal else None,
            priority=priority,
            depth=(parent_goal.depth + 1) if parent_goal else 1,
        )

        self.goals[subgoal.id] = subgoal

        if parent_goal:
            parent_goal.sub_goal_ids.append(subgoal.id)

        log.info(
            "goal_stack.subgoal_created",
            description=description[:80],
            parent=parent_goal.description[:40] if parent_goal else "none",
            depth=subgoal.depth,
        )
        return subgoal.id

    async def complete_goal(self, goal_id: str, result: str = ""):
        """Mark a goal as completed and propagate up."""
        goal = self.goals.get(goal_id)
        if not goal:
            return

        goal.status = GoalStatus.COMPLETED
        goal.completed_at = time.time()
        goal.result = result

        log.info("goal_stack.goal_completed", description=goal.description[:80])

        # Check if parent's sub-goals are all completed
        if goal.parent_id:
            parent = self.goals.get(goal.parent_id)
            if parent:
                all_sub_done = all(
                    self.goals[sid].status == GoalStatus.COMPLETED
                    for sid in parent.sub_goal_ids
                    if sid in self.goals
                )
                if all_sub_done and parent.status == GoalStatus.BLOCKED:
                    parent.status = GoalStatus.ACTIVE
                    log.info("goal_stack.parent_unblocked", description=parent.description[:80])

    async def get_active_goals(self) -> list[dict]:
        """Get all currently active goals, sorted by priority."""
        active = [
            {
                "id": g.id,
                "description": g.description,
                "priority": g.priority,
                "depth": g.depth,
                "attempts": g.attempts,
            }
            for g in self.goals.values()
            if g.status == GoalStatus.ACTIVE
        ]
        return sorted(active, key=lambda x: (-x["priority"], x["depth"]))

    async def get_attention_candidate(self) -> dict | None:
        """Get the highest priority active goal for the workspace competition."""
        active = await self.get_active_goals()
        if active:
            return active[0]
        return None

    async def report_impasse(self, goal_id: str, reason: str):
        """
        Report that a goal can't be achieved directly.
        This triggers SOAR-like subgoaling — the reasoning engine
        should decompose the goal into sub-steps.
        """
        goal = self.goals.get(goal_id)
        if not goal:
            return

        goal.status = GoalStatus.BLOCKED
        goal.attempts += 1

        log.info(
            "goal_stack.impasse",
            goal=goal.description[:80],
            reason=reason,
            attempts=goal.attempts,
        )

        if goal.attempts >= goal.max_attempts:
            goal.status = GoalStatus.FAILED
            log.warning("goal_stack.goal_failed", goal=goal.description[:80])

    async def generate_next_goals(self) -> list[str]:
        """
        Curriculum generation — when current sub-goals are done,
        generate new ones based on what was learned.
        Like Voyager's automatic curriculum.
        """
        completed = [
            g for g in self.goals.values()
            if g.status == GoalStatus.COMPLETED and g.depth > 0
        ]
        active = [
            g for g in self.goals.values()
            if g.status == GoalStatus.ACTIVE and g.depth > 0
        ]

        # If no active sub-goals, it's time to generate new ones
        if not active and completed:
            return [g.result for g in completed[-5:]]  # Context for generation

        return []

    def _find_goal(self, description_or_id: str) -> Goal | None:
        """Find a goal by ID or description."""
        if description_or_id in self.goals:
            return self.goals[description_or_id]
        for g in self.goals.values():
            if g.description == description_or_id:
                return g
        return None

    def get_goal_tree(self) -> dict:
        """Get the full goal tree for visualization/debugging."""
        if not self.mission_id:
            return {}

        def build_tree(goal_id: str) -> dict:
            goal = self.goals.get(goal_id)
            if not goal:
                return {}
            return {
                "id": goal.id,
                "description": goal.description,
                "status": goal.status.value,
                "priority": goal.priority,
                "children": [build_tree(sid) for sid in goal.sub_goal_ids],
            }

        return build_tree(self.mission_id)
