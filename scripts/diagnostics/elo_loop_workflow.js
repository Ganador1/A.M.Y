export const meta = {
  name: 'amy-coscientist-elo-loop',
  description: 'Full Co-Scientist loop v2 (LLM evolution verified live, placebo pool-dynamics control, per-player K): does the Figure-4 Elo rise reproduce?',
  phases: [
    { title: 'Run cells', detail: 'fan out (arm × topic × seed-batch) Elo-loop cells' },
    { title: 'Aggregate', detail: 'pool raw per-run ΔElo; placebo-adjust; llm_share guard' },
    { title: 'Adversarial verify', detail: 'inflation-vs-placebo, circularity (read real pools), significance' },
    { title: 'Synthesize', detail: 'final findings vs the paper\'s Figure 4' },
  ],
}

// v2 changes after the first run was demolished by the verifiers (0/3):
//  - LLM evolution actually runs now (think=false fix; llm_share tracked per run)
//  - placebo arm = same new-entrant cadence with zero quality change → controls
//    the Elo-inflation pump (which placebo PROVED is real: it inflates d_best
//    MORE than real evolution; d_top3 is the discriminating metric)
//  - per-player K (no veteran K-reset farming)
//  - unique run filenames (no collisions); final pools saved for circularity audit
const ARMS = ['none', 'placebo', 'evolution', 'full', 'full_weights']
const TOPICS = [0, 1, 2]
const SEEDS = (args && args.seeds) ? args.seeds : 4
const CYCLES = (args && args.cycles) ? args.cycles : 8
const BATCH = (args && args.batch) ? args.batch : 2
const MIN_LLM_SHARE = 0.7

log(`Elo-loop v2: ${ARMS.length} arms × ${TOPICS.length} topics × ${SEEDS} seeds `
  + `(batches of ${BATCH}), ${CYCLES} cycles. Primary metric: Δtop3 vs placebo.`)

const cells = []
for (const arm of ARMS) {
  for (const topic of TOPICS) {
    let remaining = SEEDS, batchIdx = 0
    while (remaining > 0) {
      const n = Math.min(BATCH, remaining)
      cells.push({ arm, topic, batchIdx, seeds: n })
      remaining -= n
      batchIdx++
    }
  }
}

const CELL_SCHEMA = {
  type: 'object',
  required: ['arm', 'topic_index', 'raw_d_best', 'raw_d_top3', 'raw_llm_share', 'n', 'json_path'],
  properties: {
    arm: { type: 'string' },
    topic_index: { type: 'number' },
    n: { type: 'number' },
    raw_d_best: { type: 'array', items: { type: 'number' } },
    raw_d_top3: { type: 'array', items: { type: 'number' } },
    raw_llm_share: { type: 'array', items: { type: ['number', 'null'] } }, // per-seed llm_share (null for non-LLM arms)
    evolved_won: { type: 'array', items: { type: 'boolean' } },
    json_path: { type: 'string' },
    notes: { type: 'string' },
  },
}

phase('Run cells')
const cellResults = await parallel(cells.map((cell) => async () => {
  const prompt = `You are running ONE cell of the A.M.Y Co-Scientist Elo-loop experiment (v2) at "/Volumes/Ganador disk/A.M.Y".

Run EXACTLY:

  cd "/Volumes/Ganador disk/A.M.Y" && .venv/bin/python experiments/learning_ablation/run_elo_loop.py --arms ${cell.arm} --topic-index ${cell.topic} --seeds ${cell.seeds} --cycles ${CYCLES}

It prints ONE line per seed:
  ${cell.arm}  | <domain> | seed N | best A->B d_best=D top3 C->E d_top3=F evolved_won=G llm_share=H
and ends with "Wrote <json_path>" (the JSON holds full trajectories AND the final hypothesis pool texts).

- Evolution arms (evolution/full/full_weights) make ~${cell.seeds * CYCLES * 2} LLM calls (~2-5s each); allow up to ~12 minutes. none/placebo are instant.
- Parse the per-seed lines in order: raw_d_best (d_best), raw_d_top3 (d_top3), evolved_won (G), raw_llm_share (H; null when H is None).
- Report json_path from the "Wrote ..." line.
- On error: n=0, empty arrays, error in notes.`
  return agent(prompt, {
    label: `cell:${cell.arm}/t${cell.topic}/b${cell.batchIdx}`,
    phase: 'Run cells',
    schema: CELL_SCHEMA,
  })
}))

const valid = cellResults.filter(Boolean)
log(`Collected ${valid.length}/${cells.length} cells`)

phase('Aggregate')
const byArm = {}
for (const c of valid) {
  if (!byArm[c.arm]) byArm[c.arm] = { dBest: [], dTop3: [], evolvedWon: [], llm: [], paths: [], degraded: 0 }
  const shares = c.raw_llm_share || []
  for (let i = 0; i < (c.raw_d_top3 || []).length; i++) {
    const share = shares[i]
    const isLLMArm = ['evolution', 'full', 'full_weights'].includes(c.arm)
    // Degradation guard: exclude runs whose LLM evolution silently fell back.
    if (isLLMArm && (share === null || share === undefined || share < MIN_LLM_SHARE)) {
      byArm[c.arm].degraded++
      continue
    }
    byArm[c.arm].dTop3.push(c.raw_d_top3[i])
    if ((c.raw_d_best || [])[i] !== undefined) byArm[c.arm].dBest.push(c.raw_d_best[i])
    if ((c.evolved_won || [])[i] !== undefined) byArm[c.arm].evolvedWon.push(c.evolved_won[i])
    if (share !== null && share !== undefined) byArm[c.arm].llm.push(share)
  }
  if (c.json_path) byArm[c.arm].paths.push(c.json_path)
}
const mean = (xs) => xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : null
const std = (xs) => {
  if (xs.length < 2) return 0
  const m = mean(xs)
  return Math.sqrt(xs.reduce((a, b) => a + (b - m) ** 2, 0) / xs.length)
}
const r1 = (x) => x === null ? null : Math.round(x * 10) / 10
const aggregate = {}
for (const [arm, d] of Object.entries(byArm)) {
  aggregate[arm] = {
    d_top3_mean: r1(mean(d.dTop3)), d_top3_std: r1(std(d.dTop3)), n: d.dTop3.length,
    d_best_mean: r1(mean(d.dBest)), d_best_std: r1(std(d.dBest)),
    evolved_won_share: d.evolvedWon.length ? r1(d.evolvedWon.filter(Boolean).length / d.evolvedWon.length) : null,
    llm_share_mean: d.llm.length ? r1(mean(d.llm)) : null,
    degraded_runs_excluded: d.degraded,
    run_jsons: [...new Set(d.paths)],
  }
}
// PRIMARY metric: Δtop3 minus the PLACEBO control (same pool dynamics, zero
// quality change). d_best is reported but inflation-confounded by design.
const placeboTop3 = (aggregate.placebo && aggregate.placebo.d_top3_mean) || 0
for (const arm of Object.keys(aggregate)) {
  aggregate[arm].d_top3_minus_placebo = r1((aggregate[arm].d_top3_mean || 0) - placeboTop3)
}
log('Aggregate: ' + JSON.stringify(aggregate))

phase('Adversarial verify')
const headline = JSON.stringify(aggregate, null, 2)
const VERDICT_SCHEMA = {
  type: 'object',
  required: ['claim_survives', 'confidence', 'reasoning'],
  properties: {
    claim_survives: { type: 'boolean' },
    confidence: { type: 'number' },
    reasoning: { type: 'string' },
    biggest_threat: { type: 'string' },
  },
}
const lenses = [
  `Elo inflation — the placebo arm injects clone entrants at the SAME cadence as evolution (same new-entrant/pool-cap dynamics, zero quality change), so d_top3_minus_placebo is the inflation-controlled effect. Per-player K removed the veteran K-reset pump. Verify: does evolution/full exceed placebo on Δtop3 beyond noise (Welch t on the raw per-run values, n in the aggregate)? Also confirm d_best is NOT used as evidence (it is inflation-dominated — placebo inflates d_best more than evolution does).`,
  `Judge-gaming / circularity — the tournament judge is the deterministic heuristic_judge (novelty 40%, confidence 20%, length-specificity 20%, falsifiability keywords 20%) and the LLM evolution prompt demands exactly those features. Open 2-3 of the run JSONs in the aggregate's run_jsons (they now contain "final_pool" with full hypothesis texts, elo, evolver, strategy). READ the top hypotheses in evolution/full pools vs none/placebo pools and judge AS A SCIENTIST: are the LLM-evolved winners genuinely better hypotheses (specific, falsifiable, consistent with the stated evidence) or keyword-stuffed Goodhart artifacts? Quote at least 2 actual hypothesis texts in your reasoning. Also check llm_share_mean ≈ 1.0 (the prior run silently used 0% LLM).`,
  `Statistical significance — using raw per-run Δtop3 (means/stds/n in the aggregate), test the 3 planned contrasts with Welch t and Bonferroni α=0.0167: (1) evolution vs placebo (the engine), (2) full vs evolution (meta-review feedback increment), (3) full_weights vs full (weights increment). Also note per-topic structure if visible (seeds within a topic share the topic; honest clustering caveat).`,
]
const verdicts = await parallel(lenses.map((lens, i) => async () => {
  const v = await agent(
    `You are an adversarial reviewer of A.M.Y's Co-Scientist Elo-loop experiment v2 (repo: "/Volumes/Ganador disk/A.M.Y"; harness experiments/learning_ablation/run_elo_loop.py, evolution agent cognition/evolution_agent.py). It implements arXiv:2502.18864's loop (Evolution §3.3.5, persistent-Elo tournament §3.3.3 with per-player K, meta-review feedback §3.3.6) and measures Δ Elo across ${CYCLES} cycles. PRIMARY metric: Δtop3 (top-3 average Elo), placebo-controlled. The v1 run was rejected 0/3 (silent LLM fallback, pair-averaged-K inflation, filename collisions) — all three issues were fixed and the fixes are visible in the code and in llm_share/final_pool fields.\n\nAggregate:\n\n${headline}\n\nThe tentative conclusion is: "With the LLM Evolution agent actually running, the Co-Scientist loop reproduces the paper's qualitative Figure-4 result on the inflation-controlled metric: evolution arms lift top-3 Elo well beyond the placebo's pool-dynamics drift. The meta-review feedback increment (full vs evolution) and the weights increment (full_weights vs full) are each small or indistinguishable."\n\nAttack through the lens of: ${lens}\n\nThe conclusion SURVIVES only if honestly calibrated. Report claim_survives, confidence 0-1, reasoning, biggest_threat.`,
    { label: `verify:lens${i + 1}`, phase: 'Adversarial verify', schema: VERDICT_SCHEMA }
  )
  return { lens: lens.slice(0, 60), ...v }
}))
const survived = verdicts.filter(Boolean).filter(v => v.claim_survives).length
const totalV = verdicts.filter(Boolean).length
log(`Adversarial: ${survived}/${totalV} survive`)

phase('Synthesize')
const report = await agent(
  `Write a concise, honest findings report (Markdown) for A.M.Y's full Co-Scientist loop experiment v2.

ARC SO FAR (give the reader this context): (1) Early ablations tested meta-review feedback + belief-weights as Discussion-prose modifiers → indistinguishable from noise. (2) Re-reading arXiv:2502.18864 showed Google's improvement is hypothesis Elo over tournament time (Fig 4) driven by the Evolution agent — never implemented in A.M.Y. (3) v1 of this experiment was rejected 0/3 by adversarial verifiers: the LLM evolution had silently fallen back to a deterministic stub on 100% of calls (thinking-model token exhaustion), feedback was causally disconnected in that path, pair-averaged K inflated veteran Elo, and a filename collision corrupted a control file. (4) v2 fixed all of it: think=false (llm_share now tracked, ~1.0), placebo arm (clone entrants, same pool dynamics, zero quality change) as the inflation control, per-player K, unique filenames, final pools saved for audit. The placebo PROVED the inflation critique: it pumps d_best MORE than real evolution; Δtop3 is the discriminating metric.

Aggregate (Δ Elo over ${CYCLES} cycles; primary = d_top3_minus_placebo):
${headline}

Adversarial verdicts (${survived}/${totalV} survive):
${JSON.stringify(verdicts.filter(Boolean), null, 2)}

Sections:
1. **Headline** — with the LLM Evolution agent actually running, does the Figure-4 qualitative result reproduce on the placebo-controlled Δtop3?
2. **Table** — per arm: Δtop3 ± std (n), Δtop3 − placebo, Δbest (flagged inflation-prone), evolved_won_share, llm_share, degraded runs excluded.
3. **The three increments** — evolution-vs-placebo (engine), full-vs-evolution (feedback), full_weights-vs-full (weights — the user's original question). Significance per the verifier.
4. **What v1→v2 taught** — the silent-fallback incident and the placebo lesson (d_best inflation), as methodology lessons.
5. **Answer to the user** — "¿no estamos siguiendo bien algún paso del paper?": the missing step WAS the Evolution agent + Elo metric; state plainly whether implementing it faithfully reproduced Google's qualitative result, and what remains different from Google's setup (auto-evaluated judge, small pools, 3 topics, deterministic heuristic judge vs their LLM debates).
6. **Recommendation.**

Be calibrated; do not overstate.`,
  { label: 'synthesize', phase: 'Synthesize' }
)

return {
  aggregate,
  adversarial: { survived, total: totalV, verdicts: verdicts.filter(Boolean) },
  report,
  cells_collected: valid.length,
  cells_total: cells.length,
}
