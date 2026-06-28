#!/usr/bin/env python3
"""Hermetic tests for the honesty/provenance fixes from the 2026-06-27 audit.

- The abstract no longer emits a bare decimal lifted from raw tool output
  (which both bypassed the provenance gate and frequently mislabeled a
  runtime/temperature as the named metric).
- The Meta-review agent now classifies the two highest-value Reflection Agent
  messages (ungrounded numbers, missing testable-predictions) instead of
  dropping them as 'other'.
"""
import re

import pytest

from cognition.meta_review_agent import MetaReviewAgent, _classify
from communication.paper_enhancer import PaperEnhancer


# ── Meta-review classification matches the real Reflection Agent wording ──────

def test_classify_ungrounded_number_message():
    msg = "3 of 5 numerical claims in Discussion not found in provenance."
    assert _classify(msg) == "ungrounded_number"


def test_classify_missing_testable_predictions_message():
    assert _classify("No 'Testable Predictions' section found.") == "weak_falsifiability"


def test_classify_lacking_test_procedure_message():
    assert _classify("2 hypothesis/-es lack an explicit test procedure.") == "weak_falsifiability"


def test_classify_unknown_message_is_other():
    assert _classify("something entirely unrelated") == "other"


def test_real_reflection_lessons_propagate_to_digest():
    """End-to-end: the two key lessons must reach the prompt suffix when they
    recur, instead of being silently dropped as 'other'."""
    agent = MetaReviewAgent()
    real_issues = [
        {"severity": "high", "section": "Discussion",
         "message": "3 of 5 numerical claims in Discussion not found in provenance.",
         "suggestion": "x"},
        {"severity": "high", "section": "Testable Predictions",
         "message": "No 'Testable Predictions' section found.", "suggestion": "y"},
    ]
    for _ in range(2):  # recurring across two papers
        agent.ingest_review({"issues": real_issues})
    suffix = agent.synthesize().as_prompt_suffix().lower()
    assert "numerical claim" in suffix or "provenance" in suffix
    assert "testable" in suffix or "test procedure" in suffix or "falsifi" in suffix


# ── Abstract does not surface an unverifiable bare decimal ────────────────────

def _abstract_for(result_str: str, description: str) -> str:
    enh = PaperEnhancer.__new__(PaperEnhancer)
    results = [{"tool": "t", "description": description, "result": result_str, "success": True}]
    return enh._build_abstract("mathematics", "Prime gap distribution", results, [])


def test_abstract_does_not_emit_leading_decimal_as_metric():
    # The first decimal here (0.88) is a runtime, not the correlation (0.73).
    abstract = _abstract_for("runtime=0.88s, n=50 samples, r = 0.73", "Correlation r")
    assert "0.88" not in abstract, "abstract surfaced a misattributed bare decimal"
    # It should instead reference the description and point to Results/provenance.
    assert "Correlation r" in abstract
    assert "provenance" in abstract.lower() or "results" in abstract.lower()


def test_abstract_points_to_provenance_for_values():
    abstract = _abstract_for("Landauer limit at T=310.0K: 2.965e-21 J/bit", "Landauer limit")
    # 310.0 is the temperature, not the limit — must not be asserted as the value.
    assert "310.0" not in abstract
    assert "Landauer limit" in abstract


def test_abstract_qualitative_when_no_numbers():
    abstract = _abstract_for("proof completed; QED", "Symbolic proof")
    assert isinstance(abstract, str) and len(abstract) > 0
