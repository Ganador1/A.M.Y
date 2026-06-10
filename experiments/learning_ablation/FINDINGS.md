# Learning-mechanism ablation — weights vs. feedback vs. both

**Question.** The Google AI Co-Scientist paper (arXiv:2502.18864, §3.3.6) claims its
Meta-review agent "enables feedback propagation and learning *without*
back-propagation techniques (e.g., fine-tuning or reinforcement learning)." The
user asked, reasonably: is that a sound design choice, or would updating internal
*weights* (here, A.M.Y's world-model belief confidences) add something that
prompt-feedback alone does not? And does the feedback mechanism conflict with the
other prompts/data A.M.Y consumes?

This is the honest write-up across **three escalating runs**: Run 1 (whose headline
**did not survive scrutiny**), Run 2 (confounds fixed, full rubric), and Run 3 (a
sensitive Discussion-only judge at 80 seeds). The bottom line is the same in every
properly-analyzed run — **the mechanisms are statistically indistinguishable** — but
each run rules out a different alternative explanation, so the final null is
*informative*, not a measurement failure. Newest run (Run 3) is reported first.

## Arms

What the between-cycle learning step does:

- `none` — control, no learning between papers.
- `feedback` — Co-Scientist meta-review digest injected into the paper Discussion
  prompt (`AMY_METAREVIEW_FEEDBACK` → `llm_enhancer.generate_discussion_llm`).
- `weights` — world-model belief-confidence re-estimated from accumulated
  confirm/contradict evidence, then injected as a Discussion *calibration* signal
  (`AMY_BELIEF_CONFIDENCE` → enhancer: low reliability ⇒ hedge, high ⇒ state firmly).
- `both` — feedback + weights (what this repo implements).

Each cell ran via `experiments/learning_ablation/run_ablation.py`, orchestrated in
parallel by `scripts/diagnostics/ablation_workflow.js`, with three independent
adversarial verifiers (statistical-significance, confound, causal-validity)
attacking the conclusion before it was allowed to stand.

## Run 1 (4 seeds) — headline REJECTED by the verifiers

The first run suggested "weights helps, feedback hurts." **All 3 verifiers refused
it (0/3 survived)**, correctly, because it had two fatal flaws:

1. **Variance collapse.** Per-arm std was computed over 2–3 per-cell *means*, not the
   raw per-seed values, drastically understating true noise.
2. **Unequal baselines + a phantom arm.** Cycle-0 (pre-learning) means differed by
   ~3.7 pts when they should be equal, confounding any last-cycle comparison; and
   the `weights` arm had **no reader** for its signal, so it was causally identical
   to the control — its "result" was uninformative.

## Fixes applied

- **Aggregate over raw per-seed values** + a cycle-0 one-way-ANOVA balance check
  (`arms_start_level` flag), and lead with the **seed-paired Δ** (last−first),
  never `last_mean`.
- **Gave `weights` a real causal path**: the re-estimated belief confidence now
  modulates the Discussion's stance via the enhancer, mirroring how `feedback`
  flows. Covered by a hermetic regression test
  (`tests/test_scientific_hardening.py::test_learned_belief_confidence_changes_the_discussion_prompt`).

## Run 4 — the missing engine: Co-Scientist Evolution loop + anchored head-to-head

**The re-analysis that unlocked it.** Re-reading the paper (pp. 14–16) showed the
earlier ablations were testing one leg of a three-legged stool with the wrong
ruler: Google's improvement *metric* is hypothesis Elo over tournament time
(Fig. 4, best Elo ~1350→1610) and its *engine* is the **Evolution agent**
(§3.3.5: "iterative improvement capability relies heavily on this agent") plus
tournament selection — neither of which A.M.Y had implemented. The meta-review
feedback we had tested is the amplifier, not the engine.

**What got built:** `cognition/evolution_agent.py` (the paper's five refinement
strategies; children are new entrants at Elo 1200) and
`experiments/learning_ablation/run_elo_loop.py` (persistent-Elo tournament +
meta-review feedback mined from tournament losers + placebo arm).

**Two more adversarial rejections, each catching something real:**
- *v1 (0/3):* the LLM evolution had silently fallen back to a deterministic stub
  on 100% of calls. Root cause: glm-5.1 is a *thinking* model — under
  `format_json` it burned the whole token budget on its hidden trace and
  returned empty content (measured: thinking 9,074 chars, content 7 chars).
  The same bug had silently disabled the ranking agent's LLM judge since its
  creation. Fixed with `think=false` (+ retry + salvage); `llm_share` is now
  tracked per run and the workflow excludes degraded runs.
- *v2 (0/3):* with the LLM verified live (llm_share = 1.0), the verifiers
  rebuilt the loop, validated it to the decimal, and showed the placebo control
  was broken in execution (clone perturbation produced duplicate strings that
  dedup collapsed → ~1 effective entrant vs evolution's 16). With a corrected
  placebo, **zero-quality entrants matched or beat the evolution arms on
  Δtop3** — within-pool Elo gains were rating mechanics (entry-rating
  equilibration; non-zero-sum per-player-K updates), not quality.
  **Level-3 lesson: small-pool self-played Elo tournaments cannot validly
  measure hypothesis improvement.** Google's own paper caveats its
  auto-evaluated Elo; at our scale the caveat is the whole story.

**The valid instrument — anchored head-to-head**
(`run_head_to_head.py`): the top-3 hypotheses each arm actually produced
compete arm-vs-arm in blind pairwise matches (A/B order randomized), judged
independently by the scientific-debate LLM judge. No pools, no Elo, no
mechanics to inflate. 78 matches, Wilson CIs:

| Arm | LLM-judge win rate | 95% CI | heuristic judge |
|---|---|---|---|
| **full** (evolution + feedback) | **0.727** | (0.558, 0.849) | 0.697 |
| evolution | 0.606 | (0.437, 0.753) | 0.697 |
| full_weights | 0.515 | (0.352, 0.675) | 0.667 |
| none | 0.354 | (0.195, 0.553) | 0.208 |
| placebo | 0.258 | (0.139, 0.426) | 0.152 |

Key direct duels (LLM judge): full beats placebo **94:6** (n=9); evolution beats
placebo 83:17; **full beats evolution 72:28** (the meta-review feedback
increment, directionally positive); evolution beats full_weights 61:39 and
full ties full_weights 50:50 (the weights increment, zero-to-negative — the
third independent null for weights).

**Verdict (Run 4).** With the engine actually implemented and an instrument
that mechanics cannot inflate, **the paper's qualitative claim reproduces:
tournament + LLM evolution produces genuinely better hypotheses** (confirmed by
two judges, one independent of the evolved features; full-vs-placebo CIs do not
overlap). The meta-review feedback adds a directionally positive increment on
top. The belief-weight mechanism adds nothing here either — consistent with
Google's design choice to learn *without* weight updates. Caveats: n=6–9 per
direct duel; the LLM judge's criteria overlap with the evolution prompt's
goals (mitigated by judge triangulation and the placebo's clear separation);
3 topics.

---

## Run 3 (80 seeds, Discussion-only judge) — the sensitive-instrument result

Run 2 (below) used the full rubric, where ~65/100 points are fixed by the
experimental setup and cannot be moved by a Discussion-rewriting mechanism. The
verifiers' #3 recommendation was to **fix the instrument**. So Run 3 introduced a
**Discussion-only judge** (`experiments/ab_test/scoring/score_discussion.py`,
0–100) scoring exactly the five dimensions the learning mechanisms touch
(claim-grounding, limitation coverage, alternative explanations, calibration,
reasoning depth), and re-ran at **80 seeds/arm**, sharded into batches so
`n_cells_contributing` rose from 3 to 30/arm (fixing the pseudo-replication
caveat). ~3,840 papers.

| Arm | first | last | seed-paired Δ | Δ std |
|---|---|---|---|---|
| **both** | 73.9 | 90.6 | **+16.7** | 23.4 |
| none | 66.0 | 64.9 | −1.1 | 25.6 |
| feedback | 78.7 | 74.6 | −4.1 | 28.7 |
| weights | 75.2 | 70.3 | −4.9 | 20.2 |

**The sensitive instrument finally detects movement** the full rubric could never
show: `both` (feedback + weights together) rose +16.7 while the others stayed flat
or fell. But the adversarial panel (**3/3 survived**) was unanimous that this is
**still not a rankable signal**, and they are right:

- **Cross-arm ANOVA: F(3,44) = 1.875, p = 0.148** — no omnibus difference.
- **`both` vs control: t = 1.70 (NS)** — the mechanism does not significantly beat
  doing nothing.
- **`both`'s +16.7 is a ceiling / regression-to-mean artifact, not learning:** its
  `last_std` collapses 21.3 → 7.4 (scores bunch against the 100 cap) and the
  implied first→last correlation is ≈ −0.12. It started dispersed and ended
  saturated — that mechanizes Δ.
- The strongest pairwise contrast (`both` vs `weights`, p ≈ 0.03) fails
  Bonferroni correction for 6 comparisons.
- Honest wrinkle the verifiers flagged: the workflow's `|Δ| < 1 std` gate uses
  population std rather than SE = std/√n; under SE, `both`'s isolated one-sample
  t ≈ 2.4 (nominal p ≈ 0.04). But this errs *toward* the null for the stated
  conclusion, and the cross-arm ANOVA + corrected pairwise tests independently
  refuse to rank any arm. So the conclusion holds (if anything it under-claims).

**Cycle-0 balance: arms_start_level = true** (F = 0.84), though the spread widened
to 12.7 pts on this higher-variance metric — the seed-paired Δ design controls for
it (it differences each arm against its own baseline), which is why the ranking by
Δ differs from the confounded ranking by `last_mean`.

**Verdict (Run 3): still INDISTINGUISHABLE FROM NOISE, now with an informative
instrument.** Both causal paths are confirmed real (the `weights` arm demonstrably
moves the Discussion prompt — no longer a phantom), so each arm's null is
*informative, not vacuous*: there genuinely isn't enough signal-to-noise to rank
the mechanisms, even with a metric sensitive enough to register a 16-point swing.

### What Run 3 adds to the answer

The sensitive judge does its job — it registers large Discussion changes the rubric
flattened. The fact that even *it* cannot separate the arms (omnibus p = 0.15 at
n=80, the lone nominal signal being a ceiling artifact) is a **stronger** version of
the Run 2 conclusion: it is no longer "the instrument was dead," it is "with a live
instrument and 80 seeds, the mechanisms still do not produce a rankable,
artifact-free quality gain on the Discussion." Co-Scientist's "no back-prop" bet
remains **consistent with — not proven by** — the data.

Two instrument problems to fix before any further scaling: (a) the Discussion judge
**saturates against 100** (cap the contribution per dimension or widen headroom so
Δ isn't mechanized by ceiling), and (b) ~30–40 seeds/arm would be needed to pull a
genuine ~16-pt effect past a corrected cross-arm test, ~80+ for the few-point
effects among the other arms.

---

## Run 2 (20 seeds × 3 topics × 4 cycles, ~960 papers) — full-rubric result

| Arm | first-cycle mean | seed-paired Δ | Δ std | Δ within 1 std? |
|---|---|---|---|---|
| none | 66.99 | −0.16 | 4.36 | yes |
| weights | 67.34 | −0.53 | 3.06 | yes |
| both | 68.29 | −0.54 | 4.18 | yes |
| feedback | 66.72 | −1.29 | 4.68 | yes |

**Cycle-0 balance: arms_start_level = TRUE** (ANOVA F = 0.28, max gap 1.56 pts).
The confound that ruined Run 1 is gone — arms genuinely started level.

**Both causal paths confirmed firing in the real run:** `belief_avg_conf` moved
0.58 → 0.66 across cycles (weights/both); `feedback_injected_chars` went 0 → 294 →
783 (feedback/both). Neither arm is a phantom.

**Verdict: INDISTINGUISHABLE FROM NOISE — 3/3 verifiers agree the conclusion holds.**
Every arm's |Δ| sits within one seed-level std; no arm's Δ differs from zero
(one-sample |t| ≤ 0.96); the largest cross-arm contrast (none vs feedback) is only
|t| = 0.61 (not significant, even before Bonferroni). The ordering above is **not a
reliable signal** and no arm can be ranked above another with this data.

## Answers to the user's questions

**1. Weights vs. feedback — is there a measurable difference?**
No — not at this scale. With balanced baselines, real causal paths for both
mechanisms, and proper raw-seed variance, the four arms are statistically
indistinguishable. **This neither confirms nor refutes the Co-Scientist "no
back-prop" claim** — it shows that, on the paper rubric, adding a weight-update
mechanism does not produce a *detectable* gain over feedback-only or over no
learning. Critically, this is an **underpowered null, not proven equivalence**: a
true ~1–3 pt effect could exist and be invisible at n=12/arm.

**2. Does the feedback conflict with A.M.Y's other prompts/data?**
No (separate audit, `scripts/diagnostics/audit_prompt_conflict.py`, 7 OK · 1 WARN ·
0 CONFLICT): the digest fits the context budget, is correctly scoped to the
*enhancer* prompt (not the action-selection reasoning prompt), and even when
deliberately misplaced into the reasoning prompt the model still returned a valid,
focused action. Safe to keep enabled where it is.

## Recommendation

1. **Treat Run 2 as underpowered, not a verdict.** Do not drop the weight-update
   mechanism on this evidence — the null is uninformative, not negative.
2. **Power up before re-judging.** Seed-level std is ~3–4.7 pts vs observed |Δ| ≤
   1.3 pts. Detecting a generous ~1.5 pt effect at 80% power would need on the order
   of **~80 seeds/arm**; also increase `n_cells_contributing` beyond 3 so the
   per-seed std isn't under-counting the true SE (pseudo-replication caveat).
3. **Fix the instrument, not just the sample size.** The rubric only sees
   Discussion-prose changes, so ~65/100 points are dead weight for this question.
   Add a metric the mechanisms can actually move (Discussion-specific limitation
   coverage, claim-grounding density, or a held-out judge scoring *only* the
   Discussion). Otherwise more seeds just buy a tighter null.
4. **Keep feedback in the enhancer prompt** — the conflict audit clears it.

## Reproduce

```bash
# one cell, sensitive Discussion-only judge (Run 3 metric)
AMY_USE_LLM_ENHANCER=1 .venv/bin/python experiments/learning_ablation/run_ablation.py \
    --arms none,feedback,weights,both --topic-index 0 --seeds 20 --cycles 4 \
    --metric discussion_total

# score any paper's Discussion in isolation
.venv/bin/python experiments/ab_test/scoring/score_discussion.py papers/<file>.md

# full parallel grid + adversarial verification
# Workflow: scripts/diagnostics/ablation_workflow.js
#   Run 2 (rubric):     args {"seeds":20,"cycles":4}
#   Run 3 (discussion): args {"seeds":80,"cycles":4,"batch":8}  (uses discussion_total)
```

*Run 1: `wf_875f2ccf-e1c` (4 seeds, rubric — 0/3 survived, flawed). Run 2:
`wf_a2880190-207` (20 seeds, rubric — 3/3 survived, calibrated null; ANOVA F ≈
0.28, largest cross-arm |t| = 0.61). Run 3: `wf_b703d251-2b0` (80 seeds,
Discussion-only judge — 3/3 survived; cross-arm ANOVA F = 1.875 p = 0.148;
`both` Δ = +16.7 but a ceiling artifact, last_std 21.3 → 7.4). All three agree:
mechanisms statistically indistinguishable.*
