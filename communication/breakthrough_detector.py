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

        A candidate notification requires a successful retained execution.
        Its score is heuristic and does not certify a scientific discovery.
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

        # This is a candidate notification gate, never a novelty/truth proof.
        is_breakthrough = score >= self.threshold and has_provenance
        from core.execution_evidence import record_event
        record_event("breakthrough.assessment", {
            "candidate_report": is_breakthrough, "heuristic_score": score,
            "provenance": provenance_assessment(action_result),
            "scientific_truth_verified": False, "novelty_verified": False,
        })

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
        """Check retained bytes, not words, peer scores or caller assertions."""
        return provenance_assessment(action_result)["integrity_verified"]


def provenance_assessment(action_result: dict) -> dict:
    """Bind a candidate to a successful retained execution and its journal.

    A real computation can still implement the wrong scientific model. Neither
    this check nor the model's confidence establishes scientific truth/novelty.
    """
    import hashlib
    import json
    from pathlib import Path
    from core.provenance import get_provenance_manager

    assessment = {"integrity_verified": False, "scientific_truth_verified": False,
                  "novelty_verified": False, "reason": "no bound execution receipt"}
    try:
        kind = action_result.get("type")
        result = action_result.get("result")
        execution = result if kind in ("experiment", "run_script") and isinstance(result, dict) else action_result
        experiment_id = execution.get("experiment_id")
        if not experiment_id or execution.get("success") is not True:
            return assessment
        manager = get_provenance_manager()
        verified = manager.verify_experiment_id(experiment_id)
        if not verified["integrity_verified"]:
            return assessment
        record = verified["record"]
        if record["tool"]["success"] is not True:
            return assessment
        output = (Path(verified["path"]).parent / "output.txt").read_bytes()
        if kind == "run_scientific_tool":
            bound = (isinstance(result, str)
                     and hashlib.sha256(result.encode()).hexdigest() == record["tool"]["output_hash"]
                     and action_result.get("tool_name") == record["tool"]["name"])
        elif kind in ("experiment", "run_script"):
            retained = json.loads(output)
            bound = (retained.get("experiment_id") == experiment_id
                     and all(retained.get(key) == execution.get(key) for key in
                             ("success", "stdout", "stderr", "return_code", "result_files")))
        else:
            bound = False
        journal = manager.verify_journal()
        entries = [json.loads(line) for line in manager.journal_path.read_bytes().splitlines() if line.strip()]
        memberships = [entry for entry in entries if entry.get("experiment_id") == experiment_id
                       and entry.get("record_hash") == record["integrity"]["record_hash"]
                       and entry.get("sequence") == record["integrity"]["journal_sequence"]]
        if not bound or not journal["integrity_verified"] or len(memberships) != 1:
            return assessment
        assessment.update(integrity_verified=True, experiment_id=experiment_id,
                          record_hash=record["integrity"]["record_hash"],
                          output_sha256=record["tool"]["output_hash"],
                          journal_head=journal["head_hash"],
                          reason="retained output matches a successful journaled execution")
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        pass
    return assessment
