"""Strict-enough parsing for worker outputs while retaining every raw response."""
from __future__ import annotations

import json
import re
from typing import Any


class WorkerOutputError(ValueError):
    pass


WORKER_OUTPUT_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "verdict": {
            "type": "string",
            "enum": ["supported", "refuted", "inconclusive"],
        },
        "summary": {"type": "string"},
        "candidate_claim": {"type": ["string", "null"]},
        "proof_outline": {"type": ["string", "null"]},
        "counterexample": {
            "type": ["object", "array", "string", "number", "boolean", "null"]
        },
        "assumptions": {"type": "array", "items": {"type": "string"}},
        "lemmas": {"type": "array", "items": {"type": "string"}},
        "gaps": {"type": "array", "items": {"type": "string"}},
        "tests": {"type": "array", "items": {"type": "string"}},
        "refutes_branch": {"type": "boolean"},
    },
    "required": [
        "verdict",
        "summary",
        "candidate_claim",
        "proof_outline",
        "counterexample",
        "assumptions",
        "lemmas",
        "gaps",
        "tests",
        "refutes_branch",
    ],
    "additionalProperties": False,
}


def parse_json_object(text: str) -> dict[str, Any]:
    decoder = json.JSONDecoder()
    fenced = re.findall(
        r"```(?:json)?\s*(.*?)```",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    for candidate in fenced + [text]:
        for match in re.finditer(r"\{", candidate):
            try:
                value, _end = decoder.raw_decode(candidate[match.start():])
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                return value
    raise WorkerOutputError("worker response contains no valid JSON object")


def validate_worker_output(value: dict[str, Any]) -> dict[str, Any]:
    verdict = str(value.get("verdict", "")).strip().lower()
    if verdict not in {"supported", "refuted", "inconclusive"}:
        raise WorkerOutputError(
            "verdict must be supported, refuted, or inconclusive"
        )
    summary = str(value.get("summary", "")).strip()
    if not summary:
        raise WorkerOutputError("summary cannot be empty")
    for field in ("assumptions", "lemmas", "gaps", "tests"):
        raw = value.get(field, [])
        if not isinstance(raw, list) or any(not isinstance(item, str) for item in raw):
            raise WorkerOutputError(f"{field} must be an array of strings")
    refutes_branch = value.get("refutes_branch", False)
    if not isinstance(refutes_branch, bool):
        raise WorkerOutputError("refutes_branch must be boolean")
    if refutes_branch and verdict != "refuted":
        raise WorkerOutputError("refutes_branch requires verdict=refuted")
    def optional_text(field: str) -> str | None:
        raw = value.get(field)
        if raw is None:
            return None
        if not isinstance(raw, str):
            raise WorkerOutputError(f"{field} must be a string or null")
        return raw.strip() or None

    normalized = {
        "verdict": verdict,
        "summary": summary,
        "candidate_claim": optional_text("candidate_claim"),
        "proof_outline": optional_text("proof_outline"),
        "counterexample": value.get("counterexample"),
        "assumptions": value.get("assumptions", []),
        "lemmas": value.get("lemmas", []),
        "gaps": value.get("gaps", []),
        "tests": value.get("tests", []),
        "refutes_branch": refutes_branch,
    }
    if verdict == "refuted" and normalized["counterexample"] is None:
        normalized["gaps"].append("No concrete counterexample supplied")
    return normalized
