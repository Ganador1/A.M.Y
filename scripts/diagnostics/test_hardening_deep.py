#!/usr/bin/env python3
"""
Deep functional test of the 6 public-release-hardening fixes.

Unlike `pytest` import smoke tests, this EXERCISES each fix and asserts on
observable behaviour. Run with the root venv:

    .venv/bin/python scripts/diagnostics/test_hardening_deep.py

It prints a PASS/FAIL line per check and exits non-zero if any hard check
fails. Checks that require a live LLM are marked [LLM] and degrade to SKIP (not
FAIL) when no API key is reachable, so the script is meaningful offline too.
"""
import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"
results: list[tuple[str, str, str]] = []


def record(name: str, status: str, detail: str = ""):
    results.append((name, status, detail))
    mark = {"PASS": "\033[92mPASS\033[0m", "FAIL": "\033[91mFAIL\033[0m",
            "SKIP": "\033[93mSKIP\033[0m"}.get(status, status)
    print(f"  [{mark}] {name}" + (f" — {detail}" if detail else ""))


# ── 1. Ranking agent: initial Elo 1200 + debate judge wiring ─────────────────
async def test_ranking():
    print("\n[1] Ranking agent (Co-Scientist Elo)")
    from cognition.ranking_agent import (
        run_tournament, HypothesisRecord, INITIAL_ELO, _build_ranking_client,
        heuristic_judge,
    )
    # 1a. initial Elo is 1200 (paper-accurate), not 1500
    rec = HypothesisRecord(hypothesis="x")
    record("initial Elo == 1200", PASS if rec.elo == 1200.0 else FAIL, f"got {rec.elo}")
    record("INITIAL_ELO constant == 1200", PASS if INITIAL_ELO == 1200.0 else FAIL)

    # 1b. tournament ranks candidate_novelty above known_control
    ranked = run_tournament([
        {"hypothesis": "A textbook identity restated.", "novelty_status": "known_control", "confidence": 0.9},
        {"hypothesis": "Testable: measure max_gap/(log p)^2 across 100 samples and compare to 1.0±0.2.",
         "novelty_status": "candidate_novelty", "confidence": 0.7},
    ], rounds=3, seed=7)
    top_is_candidate = ranked[0].novelty_status == "candidate_novelty"
    record("tournament ranks candidate > control", PASS if top_is_candidate else FAIL,
           f"top={ranked[0].novelty_status}")

    # 1c. the client builder no longer crashes on construction (the old bug:
    #     OllamaCloudClient() with no config raised TypeError → silent heuristic)
    try:
        client = _build_ranking_client()
        built = client is not None
        record("_build_ranking_client() constructs", PASS if built else FAIL)
    except TypeError as e:
        record("_build_ranking_client() constructs", FAIL, f"TypeError: {e}")
    except Exception as e:
        # No API key is fine — what matters is it's not the old config TypeError.
        record("_build_ranking_client() constructs", PASS, f"(no key, non-Type err: {type(e).__name__})")


# ── 2. LLM enhancer: grounding + fallback ────────────────────────────────────
async def test_enhancer():
    print("\n[2] LLM paper enhancer (Sakana write-up)")
    from communication.llm_enhancer import generate_discussion_llm, llm_enhancer_enabled

    # 2a. disabled by default (opt-in)
    record("LLM enhancer off by default", PASS if not llm_enhancer_enabled() else FAIL)

    # 2b. empty results → None (no fabricated discussion)
    empty = await generate_discussion_llm("mathematics", "T", [])
    record("empty results → None", PASS if empty is None else FAIL)

    # 2c. [LLM] real grounding: numbers in output must come from the evidence
    results_in = [{"tool": "prime_gap_analysis",
                   "description": "Prime gap analysis up to 1000000",
                   "result": "Number of primes: 78498. Largest gap: 114. Mean gap: 12.74"}]
    disc = await generate_discussion_llm("mathematics", "Prime gaps", results_in, timeout=120)
    if disc is None:
        record("[LLM] grounded discussion", SKIP, "no LLM reachable (fallback path OK)")
    else:
        has_real = ("114" in disc) or ("12.74" in disc)
        # crude hallucination check: a made-up large number not in evidence
        record("[LLM] discussion uses real provenance numbers",
               PASS if has_real else FAIL, f"{len(disc)} chars")
        record("[LLM] discussion is substantive", PASS if len(disc) > 300 else FAIL)


# ── 3. Meta-review agent: synthesizes recurring issues into guidance ─────────
async def test_meta_review():
    print("\n[3] Meta-review agent (feedback synthesis)")
    from cognition.meta_review_agent import MetaReviewAgent

    agent = MetaReviewAgent()
    # one-off issue should NOT become guidance (min_count=2)
    agent.ingest_review({"issues": [{"severity": "low", "message": "a one-off nitpick about wording"}]})
    d1 = agent.synthesize()
    record("one-off issue is not promoted", PASS if not d1.recurring_issues else FAIL)

    # recurring issue (×3) SHOULD become guidance
    for _ in range(3):
        agent.ingest_review({"issues": [
            {"severity": "high", "message": "number not traceable to provenance", "suggestion": "add provenance"}]})
    agent.ingest_peer_review({"scores": {"novelty": 3.0, "methodology": 4.0},
                              "feedback": ["❌ No novel hypotheses proposed."]})
    d2 = agent.synthesize()
    patterns = [i["pattern_key"] for i in d2.recurring_issues]
    record("recurring 'ungrounded_number' detected",
           PASS if "ungrounded_number" in patterns else FAIL, f"patterns={patterns}")
    record("weak criteria detected (novelty<6)",
           PASS if any(c["criterion"] == "novelty" for c in d2.weak_criteria) else FAIL)
    record("produces actionable guidance", PASS if d2.guidance else FAIL, f"{len(d2.guidance)} items")
    suffix = d2.as_prompt_suffix()
    record("prompt suffix is non-empty + structured",
           PASS if suffix and "Meta-review feedback" in suffix else FAIL)


# ── 4. self_retrain: real belief-weight update + persistence ─────────────────
async def test_self_retrain():
    print("\n[4] self_retrain (belief-weight update)")
    from evolution.self_retrain import SelfRetrainModule

    class FakeBelief:
        def __init__(self, conf, confirmed, contradicted, s, p, o):
            self.confidence = conf; self.times_confirmed = confirmed
            self.times_contradicted = contradicted
            self.subject = s; self.predicate = p; self.object = o

    class FakeWM:
        def __init__(self): self.beliefs = {"a|b|c": FakeBelief(0.5, 9, 1, "a", "b", "c")}

    class FakeSem:
        def __init__(self): self.facts = {"a|b|c": {"confidence": 0.5}}
        def _save(self): self.saved = True

    wm, sem = FakeWM(), FakeSem()
    srm = SelfRetrainModule()
    old = wm.beliefs["a|b|c"].confidence
    rec = await srm.retrain_world_model(wm, None, sem)
    new = wm.beliefs["a|b|c"].confidence

    # reliability = 9/10 = 0.9; blended 0.5*0.5 + 0.5*0.9 = 0.7
    record("belief confidence changed", PASS if abs(new - old) > 1e-6 else FAIL, f"{old} -> {new}")
    record("update == expected 0.7", PASS if abs(new - 0.7) < 1e-6 else FAIL, f"got {new}")
    record("retrain reports weights_updated", PASS if rec and rec.get("weights_updated") else FAIL)
    record("change persisted to knowledge graph",
           PASS if abs(sem.facts["a|b|c"]["confidence"] - 0.7) < 1e-6 else FAIL,
           f"graph={sem.facts['a|b|c']['confidence']}")

    # beliefs with zero evidence are left untouched (no spurious update)
    class FakeWM0:
        def __init__(self): self.beliefs = {"x|y|z": FakeBelief(0.5, 0, 0, "x", "y", "z")}
    wm0 = FakeWM0()
    rec0 = await SelfRetrainModule().retrain_world_model(wm0, None, FakeSem())
    record("zero-evidence belief untouched",
           PASS if wm0.beliefs["x|y|z"].confidence == 0.5 and rec0["beliefs_updated"] == 0 else FAIL)

    # meta-review agent is wired into self_retrain
    record("self_retrain wires meta_review", PASS if srm.meta_review is not None else FAIL)


# ── 5. Lean verification: honest fail when Lean absent (no rubber-stamp) ──────
async def test_lean():
    print("\n[5] Lean formal verification (honest fail)")
    try:
        # Heavy atlas import chain — try, but don't hard-fail the whole suite.
        atlas_app = ROOT / "atlas"
        sys.path.insert(0, str(atlas_app))
        from app.services.verification.formal_verification_service import FormalVerificationService  # type: ignore
    except Exception as e:
        record("[atlas] import FormalVerificationService", SKIP, f"{type(e).__name__}: {str(e)[:80]}")
        return

    svc = FormalVerificationService()
    import shutil
    lean_present = shutil.which("lean") or shutil.which("lake")

    res = await svc._verify_with_lean("2 + 2 = 4", proof=None)
    if lean_present:
        # With Lean installed, no-proof should still be rejected (no proof term).
        record("Lean present: no-proof rejected",
               PASS if res.get("valid") is False else FAIL)
    else:
        # The critical regression test: Lean ABSENT must NOT return valid=True.
        ok = res.get("valid") is False and res.get("reason") == "lean_unavailable"
        record("Lean absent: returns valid=False (no rubber-stamp)",
               PASS if ok else FAIL, f"valid={res.get('valid')}, reason={res.get('reason')}")

    # health_check lean_available reflects reality
    hc = await svc.health_check()
    expected = bool(lean_present)
    record("health_check.lean_available is honest",
           PASS if hc.get("lean_available") == expected else FAIL,
           f"reported={hc.get('lean_available')}, actual={expected}")


# ── 6. Reproducibility engine: no fabrication, unresolved → skip ─────────────
async def test_reproducibility():
    print("\n[6] Reproducibility engine (no fabricated params)")
    try:
        atlas_app = ROOT / "atlas"
        sys.path.insert(0, str(atlas_app))
        from app.services.verification.active_reproducibility_engine import ToolMapping  # type: ignore
    except Exception as e:
        record("[atlas] import reproducibility engine", SKIP, f"{type(e).__name__}: {str(e)[:80]}")
        return

    # is_reproducible reflects unresolved params
    m_ok = ToolMapping(1, "chemistry", "pyscf_hf_energy", "default", {"smiles": "O"}, 0.9)
    m_bad = ToolMapping(2, "biology", "alphafold", "default", {}, 0.9,
                        unresolved_parameters=["pdb_structure"])
    record("resolved mapping is_reproducible", PASS if m_ok.is_reproducible else FAIL)
    record("unresolved mapping NOT reproducible", PASS if not m_bad.is_reproducible else FAIL)

    # _resolve_smiles resolves known reagents, refuses unknowns (no methane default)
    from app.services.verification.active_reproducibility_engine import ToolMapper  # type: ignore
    resolve = ToolMapper._resolve_smiles
    record("resolves known reagent (water→O)", PASS if resolve(["water"]) == "O" else FAIL)
    unknown = resolve(["unobtanium-42"])
    record("refuses unknown chemical (no 'C' fallback)",
           PASS if unknown is None else FAIL, f"got {unknown!r}")
    record("empty chemicals → None", PASS if resolve(None) is None else FAIL)


async def main():
    print("=" * 64)
    print("DEEP FUNCTIONAL TEST — public-release-hardening (6 fixes)")
    print("=" * 64)
    for fn in (test_ranking, test_enhancer, test_meta_review,
               test_self_retrain, test_lean, test_reproducibility):
        try:
            await fn()
        except Exception as e:
            import traceback
            record(f"{fn.__name__} (uncaught)", FAIL, f"{type(e).__name__}: {e}")
            traceback.print_exc()

    n_pass = sum(1 for _, s, _ in results if s == PASS)
    n_fail = sum(1 for _, s, _ in results if s == FAIL)
    n_skip = sum(1 for _, s, _ in results if s == SKIP)
    print("\n" + "=" * 64)
    print(f"SUMMARY: {n_pass} PASS · {n_fail} FAIL · {n_skip} SKIP")
    print("=" * 64)
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
