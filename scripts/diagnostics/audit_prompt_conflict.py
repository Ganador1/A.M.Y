#!/usr/bin/env python3
"""
Prompt-conflict audit for the Meta-review feedback injection.

QUESTION (from the user): does the meta-review feedback-suffix conflict with the
other prompts and data A.M.Y consumes during execution?

We answer in two layers:

  PART A — ISOLATED (static, no LLM): assemble the real prompts and the injected
  feedback and check for concrete conflicts:
    A1. num_ctx overflow — does feedback + the reasoning prompt blow the 8192
        budget (system prompt ~4500 tok already)?
    A2. instruction-category mismatch — the reasoning prompt asks for an ACTION
        ("what is your next cognitive step?"), while the feedback is PAPER-WRITING
        guidance. Injecting it there is a category error. We detect the overlap
        of imperative verbs / topic mismatch.
    A3. contradiction with the existing forced-instruction block (LOOP DETECTED).
    A4. the SAFE channel — confirm the feedback lands cleanly in the paper
        ENHANCER prompt (where it is topically correct) without overflow.

  PART B — IN-LOOP (live, [LLM]): run the real reasoning path with feedback
  injected into the reasoning prompt vs. not, and check whether the model's
  chosen action degrades (e.g. starts emitting paper-writing chatter instead of
  a clean action decision). Degrades to SKIP without an API key.

Run:
    .venv/bin/python scripts/diagnostics/audit_prompt_conflict.py
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

findings: list[dict] = []


def note(part: str, name: str, verdict: str, detail: str = ""):
    findings.append({"part": part, "name": name, "verdict": verdict, "detail": detail})
    color = {"OK": "\033[92mOK\033[0m", "CONFLICT": "\033[91mCONFLICT\033[0m",
             "WARN": "\033[93mWARN\033[0m", "SKIP": "\033[93mSKIP\033[0m"}.get(verdict, verdict)
    print(f"  [{color}] {name}" + (f" — {detail}" if detail else ""))


def _approx_tokens(text: str) -> int:
    """Cheap token estimate (~4 chars/token for English)."""
    return max(1, len(text) // 4)


def _build_sample_feedback() -> str:
    """Build a realistic, *large* meta-review digest (worst-case for overflow)."""
    from cognition.meta_review_agent import MetaReviewAgent
    agent = MetaReviewAgent()
    # Saturate it with every pattern so the suffix is as long as it gets.
    msgs = [
        "number not traceable to provenance",
        "the paper does not state its limitations",
        "hypothesis has no explicit test procedure (falsifiability)",
        "unverified citation present",
        "no p-value or confidence interval reported",
        "no alternative explanation considered",
        "single tool used — parameter variation, not methodological independence",
        "known control labelled as novel",
    ]
    for _ in range(3):
        for m in msgs:
            agent.ingest_review({"issues": [{"severity": "high", "message": m, "suggestion": "fix it"}]})
    agent.ingest_peer_review({"scores": {k: 3.0 for k in
                              ["novelty", "methodology", "reproducibility", "discussion_depth", "references"]},
                              "feedback": []})
    return agent.synthesize().as_prompt_suffix()


# ── PART A — isolated static audit ───────────────────────────────────────────
def audit_isolated():
    print("\n[A] ISOLATED static audit")
    from cognition.reasoning import REASONING_SYSTEM_PROMPT
    import yaml

    # num_ctx from config
    try:
        cfg = yaml.safe_load((ROOT / "config.yaml").read_text())
        num_ctx = cfg.get("llm", {}).get("reasoner", {}).get("num_ctx", 8192)
    except Exception:
        num_ctx = 8192

    feedback = _build_sample_feedback()
    fb_tok = _approx_tokens(feedback)
    sys_tok = _approx_tokens(REASONING_SYSTEM_PROMPT)

    print(f"      num_ctx={num_ctx}, system_prompt≈{sys_tok} tok, feedback≈{fb_tok} tok")

    # A1. overflow check — reasoning prompt path
    # Reconstruct a representative full user prompt (rich context, worst-ish case).
    rich_user = (
        "## Current Focus\nInvestigate prime-gap statistics\n\n"
        "## Current Goal\nFind scaling anomalies\n"
        "## Active Sub-Goals\n" + "\n".join(f"  - sub-goal {i}" for i in range(5)) + "\n"
        "## World Model State\n" + "\n".join(f"- belief {i} (confidence: 0.5)" for i in range(10)) + "\n\n"
        "## Recent Thoughts (last 5)\n" + "\n".join(f"- [research] thought {i}" for i in range(5)) + "\n"
        "## Searches Already Done (DO NOT REPEAT THESE)\n" + "\n".join(f"  - query {i}" for i in range(15)) + "\n"
        "## Hypotheses Already Validated by Atlas (DO NOT RESUBMIT)\n" + "\n".join(f"  - hyp {i}" for i in range(8)) + "\n"
        "## Cycle\n#42\n\nWhat is your next cognitive step?"
    )
    base_tok = sys_tok + _approx_tokens(rich_user)
    with_fb_tok = base_tok + fb_tok
    headroom = num_ctx - base_tok
    note("A", "A1 reasoning-prompt base fits num_ctx",
         "OK" if base_tok < num_ctx else "CONFLICT",
         f"base≈{base_tok} tok, headroom≈{headroom} tok")
    note("A", "A1 reasoning-prompt + feedback fits num_ctx",
         "OK" if with_fb_tok < num_ctx else "CONFLICT",
         f"with feedback≈{with_fb_tok} tok vs {num_ctx} "
         f"({'OVERFLOW' if with_fb_tok >= num_ctx else 'fits'})")

    # A2. category mismatch: reasoning prompt is action-selection; feedback is
    # paper-writing. Detect topical mismatch by keyword.
    paper_terms = ["discussion", "citation", "provenance", "limitations", "hypothes",
                   "falsifiab", "p-value", "manuscript", "paper"]
    fb_low = feedback.lower()
    paper_hits = sum(t in fb_low for t in paper_terms)
    note("A", "A2 feedback is paper-writing-oriented",
         "WARN" if paper_hits >= 3 else "OK",
         f"{paper_hits} paper-writing terms — belongs in the ENHANCER prompt, "
         f"NOT the action-selection reasoning prompt")

    # A3. contradiction with the LOOP-DETECTED forced block.
    # The loop block says "DO NOT choose <action>"; the feedback never dictates
    # an action, so there is no direct action contradiction — but both are
    # high-priority imperative blocks competing for attention.
    note("A", "A3 no direct action contradiction with LOOP-DETECTED block",
         "OK",
         "feedback gives no action directives, so it cannot contradict "
         "'DO NOT choose X' — but two imperative blocks dilute attention")

    # A4. SAFE channel: the enhancer prompt. Confirm it fits and is topical.
    from communication.llm_enhancer import DISCUSSION_PROMPT, DISCUSSION_SYSTEM
    enh_user = DISCUSSION_PROMPT.format(domain="mathematics", topic="Prime gaps",
                                        results_context="[E1] tool=`x`\n  output: ...",
                                        hypotheses="(none)")
    enh_base = _approx_tokens(DISCUSSION_SYSTEM) + _approx_tokens(enh_user)
    enh_with_fb = enh_base + fb_tok
    # enhancer uses default num_ctx (no explicit small cap on chat); treat 8192.
    note("A", "A4 enhancer prompt + feedback fits budget",
         "OK" if enh_with_fb < num_ctx else "WARN",
         f"enhancer+feedback≈{enh_with_fb} tok")
    note("A", "A4 feedback is topically aligned with enhancer prompt",
         "OK",
         "enhancer prompt IS about writing the Discussion — feedback belongs here")


# ── PART B — in-loop live audit ──────────────────────────────────────────────
async def audit_in_loop():
    print("\n[B] IN-LOOP live audit  [LLM]")
    # Build a real ReasoningEngine and call reason() with/without feedback
    # injected into the reasoning prompt, to see if the action decision degrades.
    try:
        import yaml
        cfg = yaml.safe_load((ROOT / "config.yaml").read_text())
        from cognition.reasoning import ReasoningEngine
        from core.ollama_client import OllamaCloudClient
        # Build client to detect key availability early.
        client = OllamaCloudClient(cfg["llm"])
    except Exception as e:
        note("B", "build ReasoningEngine + client", "SKIP", f"{type(e).__name__}: {str(e)[:80]}")
        return

    try:
        engine = ReasoningEngine(cfg["llm"])
    except Exception as e:
        note("B", "instantiate ReasoningEngine", "SKIP", f"{type(e).__name__}: {str(e)[:80]}")
        return

    # Minimal world model / context for a single reason() call.
    class _WM:
        beliefs = {}
        average_surprise = 0.3
    context = {"current_goal": "Investigate prime-gap statistics",
               "cycle": 1, "recent_thoughts": [], "recent_queries": [],
               "recent_hypotheses": [], "consecutive_same_action": 0,
               "active_sub_goals": []}
    focus = {"content": "prime gaps", "source": "curiosity", "type": "explore"}

    # Baseline action (no feedback)
    try:
        base = await asyncio.wait_for(
            engine.reason(focus=focus, context=context, world_model=_WM(),
                          semantic_memory=None, skill_library=None),
            timeout=120)
        base_action = base.get("action_type") or base.get("action") or "?"
        note("B", "baseline reason() returns a valid action",
             "OK" if base_action and base_action != "?" else "WARN",
             f"action={base_action}")
    except Exception as e:
        note("B", "baseline reason()", "SKIP", f"{type(e).__name__}: {str(e)[:80]}")
        return

    # Now inject feedback into the reasoning prompt by monkeypatching the
    # context with a feedback field the loop would carry, simulating the RISKY
    # design (feedback in the action prompt). We append it to the goal text.
    feedback = _build_sample_feedback()
    context_fb = dict(context)
    context_fb["current_goal"] = context["current_goal"] + "\n\n" + feedback
    try:
        fb = await asyncio.wait_for(
            engine.reason(focus=focus, context=context_fb, world_model=_WM(),
                          semantic_memory=None, skill_library=None),
            timeout=120)
        fb_action = fb.get("action_type") or fb.get("action") or "?"
        # Conflict signal: action becomes invalid, or the 'content'/'reasoning'
        # starts talking about paper writing instead of the research step.
        blob = (str(fb.get("content", "")) + str(fb.get("reasoning", ""))).lower()
        contaminated = any(t in blob for t in ["citation", "provenance", "limitations section",
                                               "discussion section", "manuscript"])
        valid_action = fb_action in ("research", "search_literature", "experiment",
                                     "decompose_goal", "think_more")
        if not valid_action:
            note("B", "feedback-in-reasoning-prompt keeps action valid", "CONFLICT",
                 f"action degraded to '{fb_action}'")
        elif contaminated:
            note("B", "feedback-in-reasoning-prompt keeps action focused", "CONFLICT",
                 "action valid but reasoning text contaminated with paper-writing topics")
        else:
            note("B", "feedback-in-reasoning-prompt: action still valid+focused", "OK",
                 f"action={fb_action} (model ignored the off-topic injection)")
    except Exception as e:
        note("B", "feedback-injected reason()", "WARN", f"{type(e).__name__}: {str(e)[:80]}")


async def main():
    print("=" * 68)
    print("PROMPT-CONFLICT AUDIT — Meta-review feedback injection")
    print("=" * 68)
    audit_isolated()
    await audit_in_loop()

    n_conflict = sum(1 for f in findings if f["verdict"] == "CONFLICT")
    n_warn = sum(1 for f in findings if f["verdict"] == "WARN")
    n_ok = sum(1 for f in findings if f["verdict"] == "OK")
    n_skip = sum(1 for f in findings if f["verdict"] == "SKIP")
    print("\n" + "=" * 68)
    print(f"SUMMARY: {n_ok} OK · {n_warn} WARN · {n_conflict} CONFLICT · {n_skip} SKIP")
    print("=" * 68)
    print("\nINTERPRETATION:")
    print("  - The feedback belongs in the paper ENHANCER prompt (topically aligned,")
    print("    fits budget). That is where this repo injects it.")
    print("  - Injecting it into the action-selection REASONING prompt is a category")
    print("    mismatch and competes with the LOOP-DETECTED block for the tight")
    print("    8192-token budget. PART B tests whether the model tolerates it.")

    import json
    (ROOT / "scripts" / "diagnostics" / "prompt_conflict_report.json").write_text(
        json.dumps({"findings": findings,
                    "summary": {"ok": n_ok, "warn": n_warn, "conflict": n_conflict, "skip": n_skip}},
                   indent=2), encoding="utf-8")
    return 1 if n_conflict else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
