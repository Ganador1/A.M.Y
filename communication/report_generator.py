"""
Report Generator — Creates human-readable reports of breakthroughs.
"""
import json
import time
import uuid
from datetime import datetime
from pathlib import Path

import structlog

log = structlog.get_logger()


class ReportGenerator:
    def __init__(self, config: dict):
        self.report_path = Path(config.get("report_path", "./reports"))
        self.report_path.mkdir(parents=True, exist_ok=True)
        self.method = config.get("method", "file")

    async def generate(self, thought: dict, action_result: dict, context: dict) -> str:
        """Generate and deliver a breakthrough report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cycle = context.get("cycle", 0)
        goal = context.get("goal", "")

        from core.execution_evidence import current_evidence, record_bytes, record_event
        from communication.breakthrough_detector import provenance_assessment
        run = current_evidence()
        assessment = provenance_assessment(action_result)
        attribution = (f"Recorded runtime: {run.run_id}; see decision and action receipts for attribution."
                       if run else "No native runtime trace attached; autonomous attribution is not established.")
        report = f"""# A.M.Y Candidate Finding Report
**Time**: {timestamp}
**Cycle**: {cycle}
**Mission**: {goal}
**Attribution**: {attribution}
**Status**: Candidate for review. Scientific truth and novelty are not certified by this report.

## Finding
{thought.get('content', 'No content')}

## Hypothesis
{thought.get('hypothesis', 'None')}

## Agent's observation (not independently established by this text)
{thought.get('observation', 'No observation recorded')}

## Reasoning
{thought.get('thought', 'No reasoning recorded')}

## Action Taken
Type: {action_result.get('type', 'unknown')}

## New Knowledge
"""
        for fact in thought.get("new_facts", []):
            report += f"- **{fact.get('subject', '')}** {fact.get('predicate', '')} {fact.get('object', '')} (confidence: {fact.get('confidence', 0):.0%})\n"

        report += "\n## Retained execution assessment\n```json\n" + json.dumps(assessment, ensure_ascii=False, indent=2) + "\n```\n"
        report += "\n## Actual action result\n```json\n" + json.dumps(action_result, ensure_ascii=False, indent=2) + "\n```\n"
        report += "\nModel confidence is an estimate, not a proof. Tool-specific certificates state their own scope and assumptions.\n"

        # Deliver the report
        if self.method == "file":
            filename = f"report_{cycle}_{int(time.time())}_{uuid.uuid4().hex[:12]}.md"
            filepath = self.report_path / filename
            with open(filepath, "w") as f:
                f.write(report)
            log.info("report.saved", path=str(filepath))

        retained = record_bytes("candidate_report.md", report.encode("utf-8"), "text/markdown")
        record_event("report.created", {"report": retained, "assessment": assessment,
                                         "delivery": self.method, "cycle": cycle})

        return report
