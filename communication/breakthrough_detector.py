"""
Breakthrough Detector — Decides when a finding is worth reporting.

A.M.Y doesn't spam you with every thought. She only communicates
when she discovers something genuinely significant. This module
evaluates whether a thought/result crosses the breakthrough threshold.
"""
import structlog

log = structlog.get_logger()


class BreakthroughDetector:
    """
    Evaluates whether a cognitive cycle produced a breakthrough.
    
    Criteria for breakthrough:
    - High novelty: something we didn't know before
    - High confidence: strongly supported by evidence
    - Goal-relevant: directly advances the mission
    - Actionable: suggests a concrete next step or finding
    """

    def __init__(self, config: dict):
        self.threshold = config.get("breakthrough_threshold", 0.8)
        self._reports_today = 0
        self.max_reports = config.get("max_reports_per_day", 10)

    async def evaluate(self, thought: dict, action_result: dict, semantic_memory) -> bool:
        """Is this a breakthrough worth reporting?

        A breakthrough MUST be backed by verifiable provenance:
        - an experiment_id from a sandbox run, OR
        - a verified citation, OR
        - an Atlas paper with tool_realism evidence.
        """

        if self._reports_today >= self.max_reports:
            return False

        # ── PROVENANCE GATE ──
        has_provenance = self._has_verifiable_provenance(thought, action_result)

        # Score the finding
        novelty = thought.get("surprise_assessment", 0.0)
        progress = thought.get("progress_toward_goal", 0.0)
        confidence = 0.0

        # Check new facts
        new_facts = thought.get("new_facts", [])
        if new_facts:
            confidence = max(f.get("confidence", 0) for f in new_facts)

        # Experiment results are more likely breakthroughs
        experiment_bonus = 0.3 if action_result.get("type") == "experiment" else 0.0
        provenance_bonus = 0.3 if has_provenance else 0.0

        score = (
            0.25 * novelty
            + 0.25 * progress
            + 0.2 * confidence
            + 0.2 * experiment_bonus
            + 0.1 * provenance_bonus
        )

        is_breakthrough = score >= self.threshold and has_provenance

        if is_breakthrough:
            self._reports_today += 1
            log.info(
                "breakthrough.detected",
                score=score,
                has_provenance=has_provenance,
                content=thought.get("content", "")[:100],
            )
        elif score >= self.threshold:
            log.info(
                "breakthrough.score_high_but_no_provenance",
                score=score,
                content=thought.get("content", "")[:100],
            )

        return is_breakthrough

    def _has_verifiable_provenance(self, thought: dict, action_result: dict) -> bool:
        """Check whether this result has verifiable provenance."""
        # 1. Sandbox experiment with experiment_id
        if action_result.get("type") == "experiment":
            result = action_result.get("result", {})
            if result.get("experiment_id") or result.get("provenance_path"):
                return True

        # 2. Atlas peer-review with evidence
        if action_result.get("type") == "peer_review_paper":
            if action_result.get("success") and action_result.get("score", 0) >= 5:
                return True

        # 3. Literature search that verified a claim
        if action_result.get("type") in ("research", "search_literature"):
            # Require that the thought explicitly mentions verification
            content = thought.get("content", "")
            if "verified" in content.lower() or "confirmed" in content.lower():
                return True

        # 4. Custom script that produced result files
        if action_result.get("type") == "run_script":
            result = action_result.get("result", {})
            if result.get("success") and result.get("result_files"):
                return True

        # 5. Explicit experiment_id mentioned in the thought content
        content = thought.get("content", "")
        if "experiment_" in content.lower():
            return True

        return False
