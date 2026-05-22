"""Stub consistency checker service."""
import re


class ConsistencyCheckerService:
    def check(self, text: str, required_terms: list[str] | None = None):
        issues = []
        required_terms = required_terms or []

        for term in required_terms:
            if term.lower() not in text.lower():
                issues.append({"type": "missing_term", "term": term})

        # Simple contradiction heuristic
        contradiction_patterns = [
            (r"no evidence.*?strong evidence", "contradiction_evidence"),
            (r"no effect.*?strong effect", "contradiction_effect"),
        ]
        for pattern, issue_type in contradiction_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append({"type": issue_type})

        score = max(0.0, 1.0 - len(issues) * 0.2)
        return {"score": score, "issue_count": len(issues), "issues": issues}


consistency_checker_service = ConsistencyCheckerService()
