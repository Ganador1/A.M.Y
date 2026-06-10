export const meta = {
  name: 'amy-learning-ablation',
  description: 'Exhaustive weights-vs-feedback ablation for A.M.Y, with adversarial verification of the conclusion',
  phases: [
    { title: 'Run cells', detail: 'fan out (arm × topic × seed) ablation cells in parallel' },
    { title: 'Aggregate', detail: 'pool RAW per-seed values → seed-paired Δ + cycle-0 balance check' },
    { title: 'Adversarial verify', detail: 'independent skeptics attack the conclusion' },
    { title: 'Synthesize', detail: 'final cited findings report' },
  ],
}

// Each agent runs ONE (arm, topic, seed-batch) cell so cells run concurrently.
// Sharding seeds into batches keeps each cell short enough to finish inside the
// per-agent timeout AND raises n_cells_contributing (the adversarial verifiers
// flagged n_cells=3 as too low — pseudo-replication). Seeds are i.i.d. LLM
// samples (the harness does not vary inputs by seed integer; variation comes
// from the model's own sampling at temperature 0.3), so batching is valid: each
// batch is an independent set of draws.
const ARMS = ['none', 'feedback', 'weights', 'both']
const TOPICS = [0, 1, 2]              // indices into TOPICS in run_ablation.py
const SEEDS = (args && args.seeds) ? args.seeds : 4
const CYCLES = (args && args.cycles) ? args.cycles : 4
// Seeds-per-cell: keep each cell to a few-minute job. Defaults to ceil(SEEDS/5)
// so a big run shards into ~5 batches/arm/topic, overridable via args.batch.
const BATCH = (args && args.batch) ? args.batch : Math.max(1, Math.ceil(SEEDS / 5))
const N_BATCHES = Math.ceil(SEEDS / BATCH)

log(`Ablation grid: ${ARMS.length} arms × ${TOPICS.length} topics × ${SEEDS} seeds `
  + `(sharded into ${N_BATCHES} batches of ≤${BATCH}), ${CYCLES} cycles/cell`)

const cells = []
for (const arm of ARMS) {
  for (const topic of TOPICS) {
    let remaining = SEEDS
    let batchIdx = 0
    while (remaining > 0) {
      const seedsThisCell = Math.min(BATCH, remaining)
      cells.push({ arm, topic, batchIdx, seeds: seedsThisCell })
      remaining -= seedsThisCell
      batchIdx++
    }
  }
}

const CELL_SCHEMA = {
  type: 'object',
  required: ['arm', 'topic_index', 'first_mean', 'last_mean', 'improvement', 'n',
             'raw_first_values', 'raw_last_values', 'raw_improvements'],
  properties: {
    arm: { type: 'string' },
    topic_index: { type: 'number' },
    metric: { type: 'string' },
    first_mean: { type: ['number', 'null'] },
    last_mean: { type: ['number', 'null'] },
    improvement: { type: ['number', 'null'] },
    n: { type: 'number' },
    // RAW per-seed values are what make true seed-level variance recoverable.
    // We pool these across cells in aggregation; aggregating over per-cell
    // MEANS (only 2-3 numbers/arm) collapses the real noise.
    raw_first_values: { type: 'array', items: { type: 'number' } },
    raw_last_values: { type: 'array', items: { type: 'number' } },
    raw_improvements: { type: 'array', items: { type: 'number' } }, // per-seed Δ = last − first
    notes: { type: 'string' },
  },
}

phase('Run cells')
const cellResults = await parallel(cells.map((cell) => async () => {
  const prompt = `You are running ONE cell of a learning-ablation experiment for the A.M.Y project at "/Volumes/Ganador disk/A.M.Y".

Run EXACTLY this command. It generates real papers via the LLM enhancer and scores ONLY the Discussion section with the sensitive Discussion-only judge (discussion_total, 0-100). It runs ONLY arm "${cell.arm}" on ONLY topic index ${cell.topic}, across ${cell.seeds} seeds (this is batch ${cell.batchIdx}) and ${CYCLES} cycles:

  cd "/Volumes/Ganador disk/A.M.Y" && AMY_USE_LLM_ENHANCER=1 .venv/bin/python experiments/learning_ablation/run_ablation.py --arms ${cell.arm} --topic-index ${cell.topic} --seeds ${cell.seeds} --cycles ${CYCLES} --metric discussion_total

The script prints ONE line per seed, carrying BOTH the first- and last-cycle score and the seed-paired Δ:
  ${cell.arm}  | <domain> | seed N | first discussion_total=F last discussion_total=L delta=D (refl ...)
and a SUMMARY table with a row:
  ${cell.arm}   first(mean±std)   last(mean±std)   Δ

IMPORTANT:
- Parse the per-seed STDOUT lines (do NOT rely on the shared RESULTS.json — parallel cells overwrite it). Every raw value you report must come from these per-seed lines, NOT from the SUMMARY means.
- The per-seed Δ (delta=D) is what controls for each arm's own baseline; collect it for EVERY seed, in order, so the three raw arrays are aligned element-by-element (raw_first_values[i], raw_last_values[i], raw_improvements[i] all refer to the same seed i).
- This batch is ${cell.seeds} seeds × ${CYCLES} cycles = ${cell.seeds * CYCLES * 2} LLM paper-generations (first+last cycle counted). Allow up to ~20 minutes; LLM endpoint is shared across parallel cells.
- If the whole run errors, capture the error in notes and report n=0 with null means and empty raw arrays. If SOME seeds produced lines, report those.

Report for arm "${cell.arm}", topic_index ${cell.topic} (batch ${cell.batchIdx}):
- first_mean, last_mean, improvement (Δ = last − first) — the means over THIS batch's seeds;
- n (= number of seeds in this batch that produced a score);
- raw_first_values  = the per-seed "first discussion_total=F" values, in order;
- raw_last_values   = the per-seed "last discussion_total=L" values, in order;
- raw_improvements  = the per-seed "delta=D" values, in order (last−first PER SEED).`
  const r = await agent(prompt, {
    label: `cell:${cell.arm}/t${cell.topic}/b${cell.batchIdx}`,
    phase: 'Run cells',
    schema: CELL_SCHEMA,
  })
  return r
}))

const valid = cellResults.filter(Boolean)
log(`Collected ${valid.length}/${cells.length} cells`)

phase('Aggregate')
// Pure aggregation in JS (no agent needed) — group by arm.
//
// CRITICAL: we pool the RAW per-seed values across cells and compute every
// mean/std over those raw values — NOT over per-cell means. Aggregating over
// per-cell means averages 2-3 numbers per arm and collapses the real
// seed-level variance (e.g. the on-disk `both` cell has per-seed Δ
// [+0.43,+1.0,+2.0,−3.0], raw std ≈ 1.88, but the mean-of-means std is ~0).
// The reported std must reflect true noise, so the headline can be judged
// against it honestly.
const byArm = {}
for (const c of valid) {
  if (!byArm[c.arm]) byArm[c.arm] = { rawFirst: [], rawLast: [], rawImp: [], n: 0 }
  const rf = Array.isArray(c.raw_first_values) ? c.raw_first_values : []
  const rl = Array.isArray(c.raw_last_values) ? c.raw_last_values : []
  let ri = Array.isArray(c.raw_improvements) ? c.raw_improvements : []
  // Reconstruct per-seed Δ if the cell omitted it but gave aligned first/last.
  if (ri.length === 0 && rf.length && rf.length === rl.length) {
    ri = rl.map((l, i) => l - rf[i])
  }
  byArm[c.arm].rawFirst.push(...rf.filter((v) => typeof v === 'number'))
  byArm[c.arm].rawLast.push(...rl.filter((v) => typeof v === 'number'))
  byArm[c.arm].rawImp.push(...ri.filter((v) => typeof v === 'number'))
  byArm[c.arm].n += (c.n || 0)
}
const mean = (xs) => xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : null
// Population std (÷n) over RAW per-seed values — the honest seed-level noise.
// (÷n matches run_ablation.py's _stats; the point of the fix is pooling RAW
// per-seed values instead of 2-3 per-cell MEANS, not the n-vs-n−1 convention.)
const std = (xs) => {
  if (xs.length < 2) return null
  const m = mean(xs)
  return Math.sqrt(xs.reduce((a, b) => a + (b - m) ** 2, 0) / xs.length)
}
const round = (x, k = 3) => (typeof x === 'number' ? Number(x.toFixed(k)) : x)
const aggregate = {}
for (const [arm, d] of Object.entries(byArm)) {
  const impMean = mean(d.rawImp)
  const impStd = std(d.rawImp)
  aggregate[arm] = {
    // Lead with Δ: the within-cell, seed-paired improvement controls for each
    // arm's own cycle-0 baseline. This is the cross-arm comparison metric.
    mean_improvement: round(impMean),
    improvement_std: round(impStd),         // std over RAW per-seed Δ (true noise)
    // |Δ| judged against one seed-level std → is the effect distinguishable?
    delta_within_one_std: (typeof impMean === 'number' && typeof impStd === 'number')
      ? Math.abs(impMean) <= impStd : null,
    last_mean: round(mean(d.rawLast)), last_std: round(std(d.rawLast)),
    first_mean: round(mean(d.rawFirst)), first_std: round(std(d.rawFirst)),
    n_seeds: d.rawImp.length, n_cells_contributing: valid.filter((c) => c.arm === arm).length,
    total_runs: d.n,
  }
}

// ── Cycle-0 randomization / balance check ────────────────────────────────────
// Cycle 0 has NO learning applied yet, so first-cycle means SHOULD be equal
// across arms. If they are not, any last-cycle comparison is confounded (the
// arms did not start level) and the seed-paired Δ is the ONLY trustworthy
// cross-arm metric. We report the cross-arm spread in cycle-0 means and a
// crude one-way-ANOVA F (between-arm variance / pooled within-arm variance);
// F near or below 1 ⇒ cycle-0 means are statistically indistinguishable.
const cycle0 = (() => {
  const arms = Object.entries(byArm).filter(([, d]) => d.rawFirst.length >= 2)
  const armMeans = arms.map(([arm, d]) => ({ arm, m: mean(d.rawFirst), n: d.rawFirst.length, vals: d.rawFirst }))
  const means = armMeans.map((a) => a.m)
  if (means.length < 2) return { checkable: false, note: 'need ≥2 arms with ≥2 seeds each' }
  const grand = mean(armMeans.flatMap((a) => a.vals))
  const k = armMeans.length
  const N = armMeans.reduce((s, a) => s + a.n, 0)
  // Between-group SS (df = k−1) and within-group SS (df = N−k).
  const ssBetween = armMeans.reduce((s, a) => s + a.n * (a.m - grand) ** 2, 0)
  const ssWithin = armMeans.reduce((s, a) => s + a.vals.reduce((t, v) => t + (v - a.m) ** 2, 0), 0)
  const dfB = k - 1, dfW = N - k
  const msBetween = dfB > 0 ? ssBetween / dfB : null
  const msWithin = dfW > 0 ? ssWithin / dfW : null
  const F = (msBetween != null && msWithin) ? msBetween / msWithin : null
  return {
    checkable: true,
    arm_first_means: Object.fromEntries(armMeans.map((a) => [a.arm, round(a.m)])),
    max_gap: round(Math.max(...means) - Math.min(...means)),
    F: round(F, 2), df_between: dfB, df_within: dfW,
    // No p-value table here; F≲1 means between-arm spread is within within-arm
    // noise ⇒ cycle-0 means are statistically indistinguishable (arms start level).
    arms_start_level: (typeof F === 'number') ? F <= 2.0 : null,
  }
})()

log('Aggregate per arm (Δ-led): ' + JSON.stringify(aggregate))
log('Cycle-0 balance check: ' + JSON.stringify(cycle0))

phase('Adversarial verify')
// Three independent skeptics each try to REFUTE the headline conclusion.
//
// Rank arms by the seed-paired Δ (NOT last_mean — last_mean is confounded by
// unequal cycle-0 baselines). Decide up front whether the spread between arms
// is even distinguishable from seed-level noise: if EVERY arm's |Δ| sits
// inside one seed-level std, the honest verdict is "indistinguishable from
// noise" and no arm ranking is trustworthy.
const ranking = Object.entries(aggregate)
  .filter(([, a]) => typeof a.mean_improvement === 'number')
  .sort((x, y) => y[1].mean_improvement - x[1].mean_improvement)
  .map(([arm, a]) => ({ arm, delta: a.mean_improvement, delta_std: a.improvement_std }))
const allWithinNoise = ranking.length > 0 &&
  Object.values(aggregate).every((a) => a.delta_within_one_std !== false)
const noiseVerdict = allWithinNoise
  ? 'INDISTINGUISHABLE FROM NOISE: every arm\'s |Δ| is within one seed-level std, so no arm can be ranked above another with this data.'
  : 'At least one arm\'s |Δ| exceeds one seed-level std; a tentative ranking may be defensible but is still weak.'
const headlinePayload = {
  primary_metric: 'mean_improvement (Δ = last − first, seed-paired, controls for cycle-0 baseline)',
  ranking_by_delta: ranking,
  noise_verdict: noiseVerdict,
  cycle0_balance_check: cycle0,
  per_arm: aggregate,
}
const headline = JSON.stringify(headlinePayload, null, 2)
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
  'statistical significance — the cross-arm metric is the seed-paired Δ, and its std is computed over RAW per-seed values (true noise). Is any arm\'s Δ distinguishable from any other\'s, given that every |Δ| is within ~1 seed-level std? Default to claim_survives=false if the effects are within noise.',
  'confound — does the analysis correctly AVOID last_mean as the cross-arm metric? Cycle-0 means differ across arms (no learning applied yet, so they SHOULD be equal); a last-cycle gap would be confounded. Check the cycle0_balance_check: do the arms start level, and does leading with the seed-paired Δ actually control for the unequal baselines?',
  'causal validity — does each arm have a REAL causal path to the metric? feedback only affects the Discussion via the LLM enhancer; weights affect a per-arm belief store. If a mechanism has no causal path, its "no effect" result is uninformative, not evidence.',
]
const verdicts = await parallel(lenses.map((lens, i) => async () => {
  const v = await agent(
    `You are an adversarial reviewer of an A.M.Y learning-ablation experiment. The headline is reported below. The cross-arm comparison metric is the within-cell, seed-paired Δ (= last − first), which controls for each arm's own cycle-0 baseline; last_mean is NOT used because cycle-0 means are unequal across arms and would confound it. Std values are computed over RAW per-seed values, so they reflect true seed-level noise.\n\n${headline}\n\nThe tentative conclusion under test is: "${noiseVerdict} Ranked by seed-paired Δ, the order is ${ranking.map(r => `${r.arm} (Δ=${r.delta})`).join(' > ')}, but because every |Δ| is within one seed-level std this ordering is NOT a reliable signal — the mechanisms are statistically indistinguishable on this rubric with the current seeds."\n\nAttack this conclusion specifically through the lens of ${lens}\n\nBe rigorous and skeptical. The conclusion SURVIVES (claim_survives=true) only if it is honestly calibrated — i.e. it does NOT over-claim a winner that the noise cannot support, AND it does not use last_mean as the cross-arm metric. Report claim_survives with a confidence 0-1 and your reasoning. Name the single biggest threat to validity.`,
    { label: `verify:lens${i + 1}`, phase: 'Adversarial verify', schema: VERDICT_SCHEMA }
  )
  return { lens, ...v }
}))
const survived = verdicts.filter(Boolean).filter(v => v.claim_survives).length
const totalV = verdicts.filter(Boolean).length
log(`Adversarial verification: ${survived}/${totalV} lenses say the conclusion survives`)

phase('Synthesize')
const report = await agent(
  `Write a concise, honest findings report (Markdown) for the A.M.Y "weights vs feedback" learning ablation.

Results payload. The metric is the **Discussion-only judge** (discussion_total, 0-100) — it scores ONLY the Discussion section on grounding/limitations/alternatives/calibration/depth, the dimensions the learning mechanisms can actually move (unlike the full rubric, where ~65/100 pts are fixed by setup). READ THE SHAPE CAREFULLY:
- "primary_metric" / "ranking_by_delta": the cross-arm comparison metric is the within-cell, seed-paired Δ = last − first. It controls for each arm's own cycle-0 baseline. DO NOT rank arms by last_mean.
- "cycle0_balance_check": cycle 0 has NO learning applied yet, so first-cycle means SHOULD be equal across arms. This is the randomization check. If the arms do NOT start level, a last-cycle comparison is confounded.
- per-arm std (improvement_std, last_std, first_std) is computed over RAW per-seed values, so it reflects true seed-level noise — NOT the std of 2-3 per-cell means.
- "noise_verdict": the precomputed honest verdict on whether the arms are even distinguishable.

${headline}

Adversarial verification verdicts (${survived}/${totalV} say the conclusion survives):
${JSON.stringify(verdicts.filter(Boolean), null, 2)}

Context the reader needs:
- Arms: none (control), feedback (Co-Scientist meta-review digest injected into the paper Discussion prompt), weights (world-model belief-confidence re-estimation from accumulated evidence — what Google's Co-Scientist explicitly does NOT do), both.
- The Co-Scientist paper (arXiv:2502.18864) claims learning "without back-propagation" via the meta-review feedback loop. This experiment tests whether adding a weight-update mechanism changes outcomes.
- A separate prompt-conflict audit found: the feedback fits the context budget (no overflow), is correctly scoped to the enhancer prompt (not the action-selection reasoning prompt), and even when deliberately misplaced into the reasoning prompt the model still returned a valid focused action (no hard conflict).

MANDATORY framing rules (the whole point of this report):
- LEAD with the seed-paired Δ ranking AND the cycle-0 balance check. The very first thing the reader sees must be: do the arms start level (cycle-0 check), and what does Δ say.
- Explicitly state the cycle-0 finding: quote the per-arm first-cycle means and the max gap, and say whether the arms start level. If they do NOT start level, state plainly that last-cycle/last_mean comparisons are confounded and are therefore NOT used.
- If "noise_verdict" says indistinguishable (every arm's |Δ| within one seed-level std), the Headline MUST say the mechanisms are "indistinguishable from noise" on this rubric with the current seeds, and MUST NOT crown a winner. You may report the Δ ordering, but frame it explicitly as not a reliable signal.
- Never present last_mean as evidence for or against a mechanism.

Write these sections:
1. **Headline** — 2-3 sentences led by the seed-paired Δ and the cycle-0 balance result. If within noise, say "indistinguishable from noise" outright.
2. **Do the arms start level? (cycle-0 randomization check)** — per-arm first-cycle means, max gap, the F / "arms_start_level" flag, and the consequence (whether last-cycle numbers can be trusted at all).
3. **Per-arm table** — Δ (mean ± seed-level std) FIRST, then first→last cycle means ± std, n_seeds. Make the seed-level std visible so |Δ| can be eyeballed against it.
4. **Is it significant?** — judge each arm's |Δ| against one seed-level std. Be explicit that |Δ| values inside one std are within noise. Reflect the adversarial verdicts and the noise_verdict.
5. **Does the Co-Scientist "no backprop" claim hold for A.M.Y?** — interpret ONLY what the Δ + noise verdict licenses: did weight-update add value over feedback-only, or is the data too thin to say? What does that imply about the paper's design choice?
6. **Prompt-conflict conclusion** — does the feedback conflict with A.M.Y's other prompts/data? (summarize the audit).
7. **Recommendation** — concrete next step (e.g. how many more seeds to get |Δ| outside one std? keep/drop a mechanism? where feedback belongs).

Be calibrated: with these seed counts the honest answer is most likely "indistinguishable from noise." Say so plainly. Do not overstate.`,
  { label: 'synthesize', phase: 'Synthesize' }
)

return {
  primary_metric: 'mean_improvement (seed-paired Δ = last − first)',
  ranking_by_delta: ranking,
  noise_verdict: noiseVerdict,
  cycle0_balance_check: cycle0,
  aggregate,
  adversarial: { survived, total: totalV, verdicts: verdicts.filter(Boolean) },
  report,
  cells_collected: valid.length,
  cells_total: cells.length,
}
