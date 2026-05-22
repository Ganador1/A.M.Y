#!/usr/bin/env python3
"""Regression tests for audit, provenance, and novelty hardening.

Run with:
    .venv/bin/python test_scientific_hardening.py
"""
import hashlib
import asyncio
import json
import shutil
from pathlib import Path

import audit_papers
from communication.paper_enhancer import DOMAIN_INSIGHTS, PeerReviewer, PaperEnhancer, generate_hypothesis
from communication.paper_generator import PaperGenerator
from communication.citation_verifier import CitationVerifier
from core.atlas_tools import assess_tool_output
from core.provenance import ProvenanceManager
from run_amy_novelty import (
    molecular_orbital_novelty,
    prime_gap_novelty,
    quantum_scaling_novelty,
)


TMP_DIR = Path("data/experiments/test_audit_tmp")
TMP_PAPER = Path("papers/test_modern_provenance_audit.md")


def _reset_tmp():
    shutil.rmtree(TMP_DIR, ignore_errors=True)
    TMP_PAPER.unlink(missing_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)


def test_audit_recognizes_modern_provenance_paths_and_hashes():
    _reset_tmp()
    exp_id = "test_audit_tmp"
    exp_dir = TMP_DIR
    exp_dir.mkdir(parents=True, exist_ok=True)
    output = "Prime gaps up to 1000\nMean gap: 5.9581\nMax gap: 20\n"
    (exp_dir / "output.txt").write_text(output, encoding="utf-8")
    output_hash = hashlib.sha256(output.encode("utf-8")).hexdigest()
    (exp_dir / "provenance.json").write_text(
        json.dumps(
            {
                "experiment_id": exp_id,
                "tool": {
                    "name": "prime_gap_analysis",
                    "input": "1000",
                    "output_hash": output_hash,
                    "success": True,
                },
                "domain": "mathematics",
                "provenance_version": "1.0",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    TMP_PAPER.write_text(
        "\n".join(
            [
                "# Test Paper",
                "",
                "## Results",
                "Mean gap: 5.9581.",
                "",
                "## Data Availability",
                f"- {exp_id}: `{exp_dir}/provenance.json` (output SHA-256: `{output_hash}`)",
                "",
                "## References",
                "[1] Cramer, H. (1936). On the order of magnitude of the difference between consecutive primes.",
            ]
        ),
        encoding="utf-8",
    )

    result = audit_papers.audit_paper(TMP_PAPER)

    assert result["experiment_ids"] == [exp_id]
    assert result["provenance_ok"] is True
    assert result["cited_hash_ok"] is True
    assert result["provenance_hash_ok"] is True
    assert result["references_count"] == 1
    assert result["overall_score"] >= 85


def test_audit_rejects_mismatched_paper_cited_hash():
    _reset_tmp()
    exp_id = "test_audit_tmp"
    output = "Prime gaps up to 1000\nMean gap: 5.9581\nMax gap: 20\n"
    (TMP_DIR / "output.txt").write_text(output, encoding="utf-8")
    output_hash = hashlib.sha256(output.encode("utf-8")).hexdigest()
    (TMP_DIR / "provenance.json").write_text(
        json.dumps(
            {
                "experiment_id": exp_id,
                "tool": {
                    "name": "prime_gap_analysis",
                    "input": "1000",
                    "output_hash": output_hash,
                    "success": True,
                },
                "domain": "mathematics",
                "provenance_version": "1.0",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    fake_hash = "0" * 64
    TMP_PAPER.write_text(
        "\n".join(
            [
                "# Test Paper",
                "",
                "## Data Availability",
                f"- {exp_id}: `{TMP_DIR}/provenance.json` (output SHA-256: `{fake_hash}`)",
            ]
        ),
        encoding="utf-8",
    )

    result = audit_papers.audit_paper(TMP_PAPER)

    assert result["cited_hash_ok"] is False
    assert result["provenance_hash_ok"] is False
    assert result["cited_hash_details"][exp_id]["status"] == "mismatch"


def test_audit_verifies_all_modern_provenance_hashes_not_just_first_two():
    _reset_tmp()
    exp_ids = ["test_audit_tmp_a", "test_audit_tmp_b", "test_audit_tmp_c"]
    lines = ["# Test Paper", "", "## Data Availability"]
    for exp_id in exp_ids:
        exp_dir = Path("data/experiments") / exp_id
        shutil.rmtree(exp_dir, ignore_errors=True)
        exp_dir.mkdir(parents=True, exist_ok=True)
        output = f"output for {exp_id}"
        (exp_dir / "output.txt").write_text(output, encoding="utf-8")
        output_hash = hashlib.sha256(output.encode("utf-8")).hexdigest()
        (exp_dir / "provenance.json").write_text(
            json.dumps(
                {
                    "experiment_id": exp_id,
                    "tool": {
                        "name": "test_tool",
                        "input": exp_id,
                        "output_hash": output_hash,
                        "success": True,
                    },
                    "domain": "mathematics",
                    "provenance_version": "1.0",
                }
            ),
            encoding="utf-8",
        )
        lines.append(
            f"- {exp_id}: `data/experiments/{exp_id}/provenance.json` "
            f"(output SHA-256: `{output_hash}`)"
        )

    (Path("data/experiments") / exp_ids[2] / "output.txt").write_text(
        "tampered output",
        encoding="utf-8",
    )
    TMP_PAPER.write_text("\n".join(lines), encoding="utf-8")

    try:
        result = audit_papers.audit_paper(TMP_PAPER)

        assert set(result["reproducibility"]) == set(exp_ids)
        assert result["reproducibility"][exp_ids[2]]["output_hash_ok"] is False
        assert result["provenance_hash_ok"] is False
    finally:
        for exp_id in exp_ids:
            shutil.rmtree(Path("data/experiments") / exp_id, ignore_errors=True)


def test_paper_generator_cites_real_full_provenance_output_hash():
    _reset_tmp()
    exp_id = "test_audit_tmp"
    output = "tool output"
    output_hash = hashlib.sha256(output.encode("utf-8")).hexdigest()
    (TMP_DIR / "output.txt").write_text(output, encoding="utf-8")
    (TMP_DIR / "provenance.json").write_text(
        json.dumps(
            {
                "experiment_id": exp_id,
                "tool": {
                    "name": "test_tool",
                    "input": "x",
                    "output_hash": output_hash,
                    "success": True,
                },
                "domain": "mathematics",
                "provenance_version": "1.0",
            }
        ),
        encoding="utf-8",
    )

    markdown = PaperGenerator(enhance=False)._build_markdown(
        "Test Paper",
        "Abstract.",
        [{"heading": "Methods", "content": "Method."}],
        [],
        [],
        [exp_id],
    )

    assert f"output SHA-256: `{output_hash}`" in markdown
    assert "0/10" not in markdown


def test_paper_generator_rejects_publication_when_provenance_hash_is_missing():
    title = "Test Missing Provenance Gate"

    result = asyncio.run(
        PaperGenerator(enhance=False).generate_paper(
            title=title,
            abstract="Abstract.",
            sections=[{"heading": "Methods", "content": "Method."}],
            references=[],
            knowledge_facts=[],
            experiment_ids=["missing_experiment_for_gate"],
        )
    )

    path = Path(result["markdown_path"])
    try:
        assert result["publication_status"] == "rejected"
        assert "missing provenance output hash" in result["rejection_reasons"]
        assert path.parent.name == "rejected"
        assert result["pdf_path"] is None
    finally:
        path.unlink(missing_ok=True)


def test_paper_generator_prepublication_gate_rejects_plain_unusable_output():
    gate = PaperGenerator(enhance=False)._prepublication_gate(
        "## Results\nMolecular weight of He: 0.000 g/mol\nComposition:",
        [],
    )

    assert gate["passed"] is False
    assert "unusable tool output in manuscript" in gate["reasons"]


def test_audit_does_not_treat_sha256_chunks_as_experiment_ids():
    text = (
        "- exp_real: `data/experiments/exp_real/provenance.json`\n"
        "Script SHA-256: `5a690e0368d1c633957dda6eed8e5845c4e0807a4302cdeb3ae751f62862e3d5`"
    )

    assert audit_papers.extract_experiment_ids(text) == ["exp_real"]


def test_citation_verifier_strips_trailing_doi_punctuation():
    citations = CitationVerifier().extract_citations(
        "A sentence citation (doi: 10.1038/s41586-026-10265-5)."
    )

    assert citations == [{"type": "doi", "raw": "10.1038/s41586-026-10265-5"}]


def test_unknown_operation_output_is_not_scientific_evidence():
    assessment = assess_tool_output("Unknown operation: derivative. Available: limit, taylor")

    assert assessment["usable"] is False
    assert "unknown operation" in assessment["markers"]


def test_zero_molecular_weight_output_is_not_scientific_evidence():
    assessment = assess_tool_output("Molecular weight of He: 0.000 g/mol\nComposition:")

    assert assessment["usable"] is False
    assert "zero molecular weight" in assessment["markers"]


def test_provenance_manager_does_not_overwrite_same_second_tool_runs():
    _reset_tmp()
    manager = ProvenanceManager(base_dir=TMP_DIR)

    first = manager.record_execution(
        tool_name="quantum_energy_levels",
        tool_input="hydrogen:1",
        tool_output="E1",
        success=True,
        duration_seconds=0.1,
        domain="physics",
        experiment_id="physics_quantum_energy_levels_collision",
    )
    second = manager.record_execution(
        tool_name="quantum_energy_levels",
        tool_input="hydrogen:2",
        tool_output="E2",
        success=True,
        duration_seconds=0.1,
        domain="physics",
        experiment_id="physics_quantum_energy_levels_collision",
    )

    assert first["experiment_id"] == "physics_quantum_energy_levels_collision"
    assert second["experiment_id"] == "physics_quantum_energy_levels_collision_2"
    assert (TMP_DIR / first["experiment_id"] / "output.txt").read_text(encoding="utf-8") == "E1"
    assert (TMP_DIR / second["experiment_id"] / "output.txt").read_text(encoding="utf-8") == "E2"


def test_audit_flags_zero_failure_claim_with_failed_tool_output():
    text = "\n".join(
        [
            "# Test Paper",
            "All results are real experimental outputs with zero tool failures.",
            "## Results",
            "```",
            "Unknown operation: derivative. Available: limit, taylor",
            "```",
        ]
    )

    result = audit_papers.detect_operational_output_issues(text)

    assert result["zero_failure_claim"] is True
    assert result["unusable_output_blocks"]
    assert "claims_zero_failures_but_contains_unusable_tool_output" in result["contradictions"]


def test_audit_flags_zero_molecular_weight_in_plain_result_text():
    text = "\n".join(
        [
            "# Test Paper",
            "## Results",
            "Molecular weight of He: 0.000 g/mol",
            "Composition:",
        ]
    )

    result = audit_papers.detect_operational_output_issues(text)

    assert result["unusable_output_blocks"]
    assert "zero molecular weight" in result["unusable_output_blocks"][0]["markers"]


def test_audit_score_is_capped_when_operational_integrity_fails():
    score = audit_papers._score(
        {"safe": True},
        {"total": 1, "all_verified": True},
        {"exp": True},
        {"exp": {"output_hash_ok": True, "reproducible": True}},
        [],
        {"exp": {"ok": True}},
        {
            "ok": False,
            "unusable_output_blocks": [{"markers": ["zero molecular weight"]}],
            "contradictions": [],
        },
    )

    assert score <= 60


def test_math_prime_verification_does_not_emit_prime_gap_hypothesis():
    hypotheses = generate_hypothesis(
        "mathematics",
        [
            {
                "tool": "sympy_prime_analysis",
                "input": "is_prime:104729",
                "result": "104729 is prime: True",
                "success": True,
            }
        ],
    )

    joined = " ".join(h["hypothesis"].lower() for h in hypotheses)
    assert "prime gap distribution" not in joined
    assert all(h.get("novelty_status") != "candidate_novelty" for h in hypotheses)


def test_molecular_orbital_hypothesis_matches_homo_lumo_not_stoichiometry():
    hypotheses = generate_hypothesis(
        "chemistry",
        [
            {
                "tool": "molecular_orbital_energy",
                "input": "14",
                "result": "HOMO-LUMO gap: 1.045 eV\nDelocalization energy: -42.834 eV",
                "success": True,
            }
        ],
    )

    joined = " ".join(h["hypothesis"].lower() for h in hypotheses)
    assert "homo-lumo" in joined
    assert "stoichiometric" not in joined
    assert "reaction yields" not in joined


def test_quantum_rounded_rydberg_results_are_observations_not_novelty():
    hypotheses = generate_hypothesis(
        "physics",
        [
            {
                "tool": "quantum_energy_levels",
                "input": "hydrogen:50",
                "result": "Energy level n=50: -0.0054 eV",
                "success": True,
            }
        ],
    )

    assert all(h.get("novelty_status") != "candidate_novelty" for h in hypotheses)


def test_conclusion_does_not_call_known_controls_novel():
    from communication.paper_enhancer import PaperEnhancer

    enhancer = PaperEnhancer()
    conclusion = enhancer._build_conclusion(
        "mathematics",
        "Prime Verification",
        [
            {
                "hypothesis": "The bounded verification reproduces known conjectural structures.",
                "confidence": 0.5,
                "method": "Increase bounds.",
                "novelty_status": "known_control",
            }
        ],
        [{"tool": "sympy_prime_analysis", "result": "104729 is prime: True"}],
    )

    assert "novel hypotheses" not in conclusion.lower()
    assert "known controls" in conclusion.lower() or "verification controls" in conclusion.lower()


def test_peer_review_novelty_does_not_reward_known_controls():
    review = PeerReviewer().review_paper(
        "mathematics",
        "Prime Verification",
        [{"tool": "sympy_prime_analysis", "result": "104729 is prime: True", "success": True}],
        [{"heading": "Discussion", "content": "A detailed discussion with enough words to avoid a discussion-depth penalty. " * 4}],
        [
            {
                "hypothesis": "Known primality verification control.",
                "confidence": 0.5,
                "method": "Repeat primality checks.",
                "novelty_status": "known_control",
            }
        ],
        ["Hardy, G.H. & Wright, E.M. (2008). An Introduction to the Theory of Numbers."],
        experiment_ids=[],
    )

    assert review["scores"]["novelty"] <= 4.0
    assert any("known" in item.lower() or "control" in item.lower() for item in review["feedback"])


def test_discussion_does_not_add_prime_gap_implication_without_gap_tool():
    enhancer = PaperEnhancer()
    discussion = enhancer._build_discussion(
        "mathematics",
        [
            {"tool": "sympy_prime_analysis", "description": "10000th prime", "result": "104729 is prime: True"},
            {"tool": "number_theory_advanced", "description": "Goldbach up to 1000", "result": "Goldbach verified for all even n <= 1000"},
        ],
        DOMAIN_INSIGHTS["mathematics"],
    )

    assert "Cramér" not in discussion
    assert "prime spacing" not in discussion


def test_discussion_prefers_exact_prime_gap_pattern_over_fuzzy_sympy_match():
    enhancer = PaperEnhancer()
    discussion = enhancer._build_discussion(
        "mathematics",
        [
            {
                "tool": "prime_gap_analysis",
                "description": "Prime gaps up to 1000",
                "result": "Prime gap analysis up to 1000:\nMean gap: 5.9581",
            }
        ],
        DOMAIN_INSIGHTS["mathematics"],
    )

    assert "distribution of prime gaps" in discussion.lower()
    assert "primality checks" not in discussion.lower()


def test_peer_review_reproducibility_uses_real_experiment_ids_without_rendered_data_section():
    _reset_tmp()
    exp_id = "test_audit_tmp"
    output = "tool output"
    (TMP_DIR / "output.txt").write_text(output, encoding="utf-8")
    (TMP_DIR / "provenance.json").write_text(
        json.dumps(
            {
                "experiment_id": exp_id,
                "tool": {
                    "name": "test_tool",
                    "input": "x",
                    "output_hash": hashlib.sha256(output.encode("utf-8")).hexdigest(),
                    "success": True,
                },
                "domain": "mathematics",
                "provenance_version": "1.0",
            }
        ),
        encoding="utf-8",
    )

    review = PeerReviewer().review_paper(
        "mathematics",
        "Reproducibility Gate",
        [{"tool": "test_tool", "result": "value = 1.23", "success": True}],
        [{"heading": "Methods", "content": "A method section before data availability rendering."}],
        [],
        ["Reference A", "Reference B", "Reference C"],
        experiment_ids=[exp_id],
    )

    assert review["scores"]["reproducibility"] == 9.0


def test_enhance_paper_builds_hypotheses_before_discussion():
    enhancer = PaperEnhancer()

    enhanced = asyncio.run(
        enhancer.enhance_paper(
            domain="mathematics",
            topic="Prime Gap Test",
            results=[
                {
                    "tool": "prime_gap_analysis",
                    "description": "Prime gaps up to 1000",
                    "result": "Prime gap analysis up to 1000:\nMean gap: 5.9581",
                    "success": True,
                }
            ],
            sections=[
                {"heading": "Introduction", "content": "Intro"},
                {"heading": "Methods", "content": "Methods"},
                {"heading": "Results", "content": "Results"},
                {"heading": "Discussion", "content": "Discussion"},
                {"heading": "Conclusion", "content": "Conclusion"},
            ],
            experiment_ids=[],
        )
    )

    assert enhanced["hypotheses"]
    discussion = next(s for s in enhanced["sections"] if s["heading"] == "Discussion")
    assert "prime gaps" in discussion["content"].lower()
    assert all("review" not in s["heading"].lower() for s in enhanced["sections"])
    assert enhanced["peer_review"]["overall_score"] >= 0


def test_enhancer_uses_astronomy_domain_instead_of_mathematics_fallback():
    enhancer = PaperEnhancer()

    enhanced = asyncio.run(
        enhancer.enhance_paper(
            domain="astronomy",
            topic="Stellar Physics",
            results=[
                {
                    "tool": "quantum_energy_levels",
                    "description": "Hydrogen n=2",
                    "result": "Hydrogen atom energy level n=2: E_2 = -3.4000 eV",
                    "success": True,
                },
                {
                    "tool": "numpy_correlation",
                    "description": "Temperature-luminosity correlation",
                    "result": "Pearson correlation coefficient: 0.951847",
                    "success": True,
                },
            ],
            sections=[
                {"heading": "Introduction", "content": "Intro"},
                {"heading": "Methods", "content": "Methods"},
                {"heading": "Results", "content": "Results"},
                {"heading": "Discussion", "content": "Discussion"},
                {"heading": "Conclusion", "content": "Conclusion"},
            ],
            experiment_ids=[],
        )
    )

    combined = " ".join(
        [enhanced["abstract"]]
        + [s["content"] for s in enhanced["sections"]]
        + enhanced["references"]
    ).lower()
    assert "mathematics research" not in combined
    assert "prime numbers" not in combined
    assert "stellar" in combined or "astrophysics" in combined


def test_prime_gap_detector_does_not_call_small_finite_cramer_gap_novel():
    result = prime_gap_novelty(
        [
            {
                "tool": "prime_gap_analysis",
                "input": "1000",
                "result": "Prime gaps up to 1000:\nMean gap: 5.95\nStd dev: 4.3\nMax gap: 20\nNumber of primes: 168",
                "success": True,
            },
            {
                "tool": "prime_gap_analysis",
                "input": "5000",
                "result": "Prime gaps up to 5000:\nMean gap: 7.85\nStd dev: 5.9\nMax gap: 34\nNumber of primes: 669",
                "success": True,
            },
            {
                "tool": "prime_gap_analysis",
                "input": "10000",
                "result": "Prime gaps up to 10000:\nMean gap: 8.80\nStd dev: 6.5\nMax gap: 36\nNumber of primes: 1229",
                "success": True,
            },
        ]
    )

    assert result["has_novelty"] is False
    assert result["novel_findings"] == []
    assert all(f.get("is_novel") is False for f in result["findings"])


def test_quantum_detector_treats_rounded_high_n_deviation_as_precision_control():
    result = quantum_scaling_novelty(
        [
            {"tool": "quantum_energy_levels", "input": "hydrogen:1", "result": "Energy level n=1: E_1 = -13.6000 eV", "success": True},
            {"tool": "quantum_energy_levels", "input": "hydrogen:10", "result": "Energy level n=10: E_10 = -0.1360 eV", "success": True},
            {"tool": "quantum_energy_levels", "input": "hydrogen:50", "result": "Energy level n=50: E_50 = -0.0054 eV", "success": True},
        ]
    )

    assert result["has_novelty"] is False
    assert result["novel_findings"] == []
    assert any(f.get("novelty_status") == "precision_artifact" for f in result["findings"])


def test_molecular_orbital_detector_reports_gap_fit_as_observation_or_candidate():
    result = molecular_orbital_novelty(
        [
            {"tool": "molecular_orbital_energy", "description": "4-carbon system", "result": "4-carbon system\nEnergies: [-1.0, -0.4, 0.4, 1.0]", "success": True},
            {"tool": "molecular_orbital_energy", "description": "6-carbon system", "result": "6-carbon system\nEnergies: [-1.2, -0.7, -0.2, 0.2, 0.7, 1.2]", "success": True},
            {"tool": "molecular_orbital_energy", "description": "8-carbon system", "result": "8-carbon system\nEnergies: [-1.4, -0.9, -0.5, -0.1, 0.1, 0.5, 0.9, 1.4]", "success": True},
        ]
    )

    assert result["has_novelty"] is False
    assert all(f.get("is_novel") is False for f in result["findings"])
    assert any(f.get("novelty_status") in {"finite_computational_observation", "candidate_novelty"} for f in result["findings"])


def main():
    tests = [
        test_audit_recognizes_modern_provenance_paths_and_hashes,
        test_audit_rejects_mismatched_paper_cited_hash,
        test_audit_verifies_all_modern_provenance_hashes_not_just_first_two,
        test_paper_generator_cites_real_full_provenance_output_hash,
        test_paper_generator_rejects_publication_when_provenance_hash_is_missing,
        test_paper_generator_prepublication_gate_rejects_plain_unusable_output,
        test_audit_does_not_treat_sha256_chunks_as_experiment_ids,
        test_citation_verifier_strips_trailing_doi_punctuation,
        test_unknown_operation_output_is_not_scientific_evidence,
        test_zero_molecular_weight_output_is_not_scientific_evidence,
        test_provenance_manager_does_not_overwrite_same_second_tool_runs,
        test_audit_flags_zero_failure_claim_with_failed_tool_output,
        test_audit_flags_zero_molecular_weight_in_plain_result_text,
        test_audit_score_is_capped_when_operational_integrity_fails,
        test_math_prime_verification_does_not_emit_prime_gap_hypothesis,
        test_molecular_orbital_hypothesis_matches_homo_lumo_not_stoichiometry,
        test_quantum_rounded_rydberg_results_are_observations_not_novelty,
        test_conclusion_does_not_call_known_controls_novel,
        test_peer_review_novelty_does_not_reward_known_controls,
        test_discussion_does_not_add_prime_gap_implication_without_gap_tool,
        test_discussion_prefers_exact_prime_gap_pattern_over_fuzzy_sympy_match,
        test_peer_review_reproducibility_uses_real_experiment_ids_without_rendered_data_section,
        test_enhance_paper_builds_hypotheses_before_discussion,
        test_enhancer_uses_astronomy_domain_instead_of_mathematics_fallback,
        test_prime_gap_detector_does_not_call_small_finite_cramer_gap_novel,
        test_quantum_detector_treats_rounded_high_n_deviation_as_precision_control,
        test_molecular_orbital_detector_reports_gap_fit_as_observation_or_candidate,
    ]
    try:
        for test in tests:
            test()
            print(f"PASS {test.__name__}")
    finally:
        shutil.rmtree(TMP_DIR, ignore_errors=True)
        TMP_PAPER.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
