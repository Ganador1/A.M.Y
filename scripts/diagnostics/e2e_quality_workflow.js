export const meta = {
  name: 'amy-e2e-quality',
  description: 'E2E: generate fresh A.M.Y papers with new tools, audit Atlas/provenance, score all criteria, head-to-head vs prior versions, adversarially verify',
  phases: [
    { title: 'Generate', detail: 'fresh papers via real Atlas → provenance → enhancer+evolution, per plan' },
    { title: 'Compare + flagship', detail: 'blind head-to-head vs prior versions; generate flagship recreation paper' },
    { title: 'Adversarial verify', detail: 'provenance integrity, criteria-gaming, comparison validity' },
    { title: 'Synthesize', detail: 'quality report vs the 71-83 prior baseline' },
  ],
}

const PLANS = ['prime_gaps', 'hf_chemistry', 'hydrogen_levels', 'statistics', 'biology']

const AUDIT_SCHEMA = {
  type: 'object',
  required: ['plan', 'ok'],
  properties: {
    plan: { type: 'string' },
    ok: { type: 'boolean' },
    rubric_total: { type: ['number', 'null'] },
    discussion_total: { type: ['number', 'null'] },
    reflection_score: { type: ['number', 'null'] },
    reflection_pass: { type: ['boolean', 'null'] },
    n_distinct_tools: { type: ['number', 'null'] },
    n_atlas_tools_run: { type: ['number', 'null'] },
    provenance_integrity: { type: ['string', 'null'] }, // "k/n"
    discussion_stub_replaced: { type: ['boolean', 'null'] },
    worst_dims: { type: 'array', items: { type: 'string' } }, // 2-3 lowest rubric dims
    notes: { type: 'string' },
  },
}

phase('Generate')
// Each plan = one agent: runs real Atlas tools, writes provenance, generates the
// paper through the full enhancer+evolution pipeline, reads back the audit JSON.
const audits = await parallel(PLANS.map((plan) => async () => {
  return agent(
    `Generate ONE A.M.Y paper end-to-end through the REAL pipeline at "/Volumes/Ganador disk/A.M.Y".

Run EXACTLY (all new tools ON):

  cd "/Volumes/Ganador disk/A.M.Y" && AMY_USE_LLM_ENHANCER=1 AMY_USE_EVOLUTION=1 AMY_USE_LLM_JUDGE=1 .venv/bin/python experiments/e2e_v2/gen_e2e_v2.py --plan ${plan}

This calls genuine Atlas scientific tools (PySCF/SymPy/NumPy/etc.), writes SHA-256 provenance, and generates the paper via the LLM enhancer + Co-Scientist evolution agent. It writes experiments/e2e_v2/audits/${plan}.audit.json and prints a one-line summary. Allow up to ~6 minutes.

Then READ experiments/e2e_v2/audits/${plan}.audit.json and report its fields: rubric_total, discussion_total, reflection_score, reflection_pass, n_distinct_tools, n_atlas_tools_run, provenance_integrity, discussion_stub_replaced. From rubric_breakdown, list the 2-3 LOWEST-scoring dimensions as worst_dims (e.g. "explicit_limitations:2.0"). If the run failed, ok=false with the reason in notes.`,
    { label: `gen:${plan}`, phase: 'Generate', schema: AUDIT_SCHEMA }
  )
}))
const okAudits = audits.filter(Boolean).filter(a => a.ok)
const rubrics = okAudits.map(a => a.rubric_total).filter(x => typeof x === 'number')
const meanRubric = rubrics.length ? Math.round(rubrics.reduce((a, b) => a + b, 0) / rubrics.length * 10) / 10 : null
log(`Generated ${okAudits.length}/${PLANS.length} papers, mean rubric ${meanRubric} (prior baseline 71-83)`)

phase('Compare + flagship')
const [comparison, flagship] = await parallel([
  // Blind head-to-head: new papers vs prior-version papers, LLM-judged.
  async () => agent(
    `Run the blind head-to-head comparison of A.M.Y's NEW e2e_v2 papers vs PRIOR-version papers at "/Volumes/Ganador disk/A.M.Y".

  cd "/Volumes/Ganador disk/A.M.Y" && .venv/bin/python experiments/e2e_v2/compare_vs_prior.py --judge llm --n-prior 12

It judges new-vs-prior manuscripts blind (A/B randomized) with an LLM and writes experiments/e2e_v2/compare_vs_prior_llm_*.json. Allow ~8 minutes. Report: the NEW-papers win rate, n_matches, the 95% CI, and whether the CI lower bound is above 0.5 (i.e. new papers significantly better). Quote 1-2 per_match results.`,
    { label: 'compare:vs-prior', phase: 'Compare + flagship' }
  ),
  // Flagship: the "bonito" meta-paper. Provide the real findings; the agent
  // assembles a provenance-anchored manuscript via A.M.Y's own generator.
  async () => agent(
    `Create the FLAGSHIP meta-paper: "A.M.Y reproduces the Google Co-Scientist Evolution loop as its own experiment." Repo: "/Volumes/Ganador disk/A.M.Y".

This paper documents the REAL result we established (read experiments/learning_ablation/FINDINGS.md for the full arc and numbers). Key verified findings to report faithfully:
- The Co-Scientist qualitative claim reproduces once the Evolution agent (cognition/evolution_agent.py) is implemented: in an anchored blind head-to-head judged by an independent LLM, evolution+feedback ("full") hypotheses won 0.727 (95% CI 0.558-0.849) vs no-learning 0.354 and a pool-dynamics placebo 0.258 — full-vs-placebo CIs do NOT overlap; full beats placebo 94:6 in direct duels.
- Belief-weight updates added nothing across three independent tests (Google's "no back-propagation" design choice is empirically supported).
- The methodology arc required FIVE adversarial-verification panels that rejected three flawed analyses (silent LLM fallback from thinking-model token exhaustion, broken placebo, small-pool Elo inflation) before the valid instrument (anchored head-to-head) was reached.

Write it as a proper Markdown manuscript with sections: Abstract, Introduction (the question: does adding weight-updates beat Co-Scientist's feedback-only design?), Methods (the 4-run escalation + adversarial verification protocol), Results (the head-to-head table + the three nulls for weights), Discussion (what reproduced, what didn't, the methodology lessons — honest about n=6-9/duel and judge-overlap caveats), Conclusion. Save it to papers/e2e_v2/FLAGSHIP_coscientist_recreation.md. Then score it: cd "/Volumes/Ganador disk/A.M.Y" && .venv/bin/python experiments/ab_test/scoring/score_discussion.py papers/e2e_v2/FLAGSHIP_coscientist_recreation.md — and report the discussion score, word count, and confirm the file was written. Do NOT fabricate numbers beyond those given above.`,
    { label: 'flagship:recreation', phase: 'Compare + flagship' }
  ),
])

phase('Adversarial verify')
const VERDICT = {
  type: 'object',
  required: ['claim_survives', 'confidence', 'reasoning'],
  properties: {
    claim_survives: { type: 'boolean' },
    confidence: { type: 'number' },
    reasoning: { type: 'string' },
    biggest_threat: { type: 'string' },
  },
}
const claim = `A.M.Y's new pipeline (LLM enhancer + Co-Scientist evolution + working LLM judge) produces papers that (a) genuinely use real Atlas tools with intact SHA-256 provenance, (b) score meaningfully higher than the prior versions (new e2e_v2 mean rubric ${meanRubric} + the corpus longitudinal result e2e_v2_window 67.6 vs pre_hardening 39.6), and (c) win blind head-to-head against prior-version papers. Audits: ${JSON.stringify(okAudits)}. Comparison: ${comparison}`
const lenses = [
  `Provenance & Atlas integrity — open 2 of the e2e_v2 audit JSONs (experiments/e2e_v2/audits/*.audit.json) and 1-2 of the generated papers (papers/e2e_v2/*.md). Verify the Atlas tools listed actually ran (atlas_audit ok=true with real experiment_ids), that provenance_integrity is k/k (every claimed SHA-256 matches the output.txt rehash), and that numbers in the Discussion actually appear in the tool outputs. If any paper's "provenance" is hollow or numbers are ungrounded/fabricated, the claim fails.`,
  `Criteria-gaming — is the rubric/discussion-judge improvement genuine quality or Goodhart farming of the scorers' keywords? The discussion judge rewards limitation/alternative/falsifiability markers and the LLM enhancer is told to include them. READ an actual e2e_v2 Discussion (papers/e2e_v2/*.md) and judge AS A SCIENTIST whether it is genuinely rigorous (honestly rejects weak hypotheses, grounds numbers) or marker-stuffed. Quote ≥2 sentences.`,
  `Comparison validity — is the new-vs-prior head-to-head fair? Check: were prior papers a reasonable sample of the legacy system (not just rejected/worst)? Could the LLM judge favor new papers for superficial reasons (length, formatting) rather than science? Is n_matches enough for the CI claim? Read experiments/e2e_v2/compare_vs_prior_llm_*.json.`,
]
const verdicts = await parallel(lenses.map((lens, i) => async () =>
  agent(
    `You are an adversarial reviewer at "/Volumes/Ganador disk/A.M.Y". Claim under test:\n\n${claim}\n\nAttack through: ${lens}\n\nThe claim SURVIVES only if honestly supported by the artifacts you inspect. Report claim_survives, confidence 0-1, reasoning (cite files/quotes), biggest_threat.`,
    { label: `verify:lens${i + 1}`, phase: 'Adversarial verify', schema: VERDICT }
  )
))
const survived = verdicts.filter(Boolean).filter(v => v.claim_survives).length
const totalV = verdicts.filter(Boolean).length
log(`Adversarial: ${survived}/${totalV} survive`)

phase('Synthesize')
const report = await agent(
  `Write a concise, honest report (Markdown) answering the user's question: "how good are A.M.Y's papers now vs my previous versions, and is the E2E scientific pipeline using Atlas correctly?"

Evidence:
- Per-paper E2E audits (rubric, discussion, reflection, Atlas tools used, provenance integrity, worst dims): ${JSON.stringify(okAudits)}
- New papers mean rubric: ${meanRubric}. Prior-version baseline: showcase 71-83, all_domains ~70.
- Longitudinal corpus (experiments/e2e_v2/corpus_dataset.json, already computed): e2e_v2_window rubric 67.6±5.3 (n=172) vs hardening 50.4 (n=9) vs pre_hardening 39.6±13.5 (n=219). New era roughly doubles the legacy mean AND cuts variance.
- Blind head-to-head vs prior versions: ${comparison}
- Flagship recreation paper: ${flagship}
- Adversarial verification: ${survived}/${totalV} survived. Verdicts: ${JSON.stringify(verdicts.filter(Boolean))}

Sections:
1. **Headline** — are the new papers better, and is the gain real (per the verifiers)?
2. **E2E pipeline health** — is Atlas being used correctly (real tools, intact provenance)? Flag any paper where it isn't.
3. **Quality vs prior versions** — rubric numbers + longitudinal trajectory + head-to-head win rate, honestly caveated.
4. **Remaining weaknesses** — the consistently-low rubric dimensions (e.g. explicit_limitations) and what would raise them.
5. **The flagship paper** — what it is and its score.
6. **The corpus as an asset** — what the longitudinal dataset gives the project.
7. **Recommendation.**

Be calibrated; reflect the adversarial verdicts; do not overstate.`,
  { label: 'synthesize', phase: 'Synthesize' }
)

return {
  generated: okAudits.length, plans: PLANS.length, mean_rubric: meanRubric,
  comparison, flagship,
  adversarial: { survived, total: totalV, verdicts: verdicts.filter(Boolean) },
  report,
}
