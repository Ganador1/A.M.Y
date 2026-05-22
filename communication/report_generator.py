"""
Report Generator — Creates human-readable reports of breakthroughs.
"""
import json
import time
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

        report = f"""# A.M.Y Breakthrough Report
**Time**: {timestamp}
**Cycle**: {cycle}
**Mission**: {goal}

## Finding
{thought.get('content', 'No content')}

## Hypothesis
{thought.get('hypothesis', 'None')}

## Evidence
{thought.get('observation', 'No observation recorded')}

## Reasoning
{thought.get('thought', 'No reasoning recorded')}

## Action Taken
Type: {action_result.get('type', 'unknown')}

## New Knowledge
"""
        for fact in thought.get("new_facts", []):
            report += f"- **{fact.get('subject', '')}** {fact.get('predicate', '')} {fact.get('object', '')} (confidence: {fact.get('confidence', 0):.0%})\n"

        report += f"\n---\n*Generated autonomously by A.M.Y at cycle {cycle}*\n"

        # Deliver the report
        if self.method == "file":
            filename = f"report_{cycle}_{int(time.time())}.md"
            filepath = self.report_path / filename
            with open(filepath, "w") as f:
                f.write(report)
            log.info("report.saved", path=str(filepath))

        return report
