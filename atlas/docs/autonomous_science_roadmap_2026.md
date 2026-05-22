# Atlas Autonomous Science Roadmap 2026

## Objective

Turn Atlas from a promising multi-agent research prototype into a reproducible AI-for-science platform that can:

1. generate hypotheses with frontier models,
2. ground them in literature and external scientific tools,
3. run computational validation loops,
4. produce auditable papers and experiment bundles.

## What changed in the landscape

The frontier moved materially in 2024-2026. Atlas should stop behaving like a generic agent stack and start acting like a domain-aware science platform with specialized external model adapters.

### Biology and biomedicine

- **AlphaFold 3** moved from protein structure prediction to interactions across proteins, DNA, RNA, ligands and other biomolecules, with a Google DeepMind / Isomorphic Labs launch on **May 8, 2024** and academic code/weights release noted on **November 11, 2024**.
- **AlphaGenome** was introduced by Google DeepMind on **June 25, 2025** as a unifying DNA-sequence model for regulatory variant-effect prediction and is explicitly described as being **available via API**.
- **ESM3** was announced by EvolutionaryScale on **June 25, 2024** as a multimodal biology model aimed at programming biology and later advanced to a Science publication path.
- **Boltz-2** is now positioned by its official repository as an open biomolecular foundation model that jointly models complex structures and binding affinities, targeting practical early-stage drug discovery.

### Materials and chemistry

- **MatterSim** from Microsoft Research was published on **May 13, 2024** as a deep-learning atomistic model spanning broad elements, temperatures and pressures for in silico materials design.
- **MatterGen** reached Nature publication in **January 2025** as a generative model for inorganic materials design with strong novelty/stability claims and property steering.

### Climate and Earth systems

- **AlphaEarth Foundations** was introduced by Google DeepMind on **July 30, 2025** as a global geospatial embedding model for land and coastal monitoring, with embeddings released in Google Earth Engine.

### Autonomous science systems

- **AI co-scientist** was introduced by Google Research on **February 19, 2025** as a Gemini 2.0 multi-agent scientific collaborator with explicit agent roles for generation, reflection, ranking, evolution, proximity and meta-review.
- **Robin** from FutureHouse was announced on **May 20, 2025** as an end-to-end multi-agent scientific discovery workflow that integrated literature, experiment design and data analysis and produced an AI-generated therapeutic discovery workflow.
- **PaperQA2** and its 2024 paper showed that citation-grounded literature agents can reach or exceed subject-matter experts on literature synthesis tasks. This is directly relevant to Atlas literature and reviewer loops.
- **AlphaEvolve** was announced by Google DeepMind on **May 14, 2025** as a coding/evolutionary agent for algorithm discovery with verified gains in math and compute optimization.

## Recommended Atlas priorities

### Priority A: literature and evidence become first-class

Atlas currently has literature plumbing, but it should move to a modern literature-evidence stack:

- Add a `paperqa2_adapter` for PDF-level question answering, contradiction detection and cited synthesis.
- Extend `ToolEvidenceOrchestratorService` so literature evidence has structured weights, contradiction flags and confidence intervals.
- Store evidence provenance as typed records: `source`, `doi_or_url`, `claim`, `evidence_type`, `confidence`, `contradiction_status`.
- Add a benchmark mode based on LitQA2-style or contradiction-discovery tasks.

### Priority B: specialized biology adapters

Add external adapters instead of trying to force one generic LLM to do all scientific reasoning:

- `alphafold3_adapter`
  - Input: protein / complex specification.
  - Output: structure artifacts, confidence metrics, interaction summaries.
- `alphagenome_adapter`
  - Input: long DNA sequence windows and variants.
  - Output: predicted regulatory effects and mutation impact summaries.
- `esm3_adapter`
  - Input: protein design or sequence optimization tasks.
  - Output: candidate sequences, embeddings, design metadata.
- `boltz_adapter`
  - Input: complex / ligand / binding tasks.
  - Output: structure plus affinity-oriented outputs for ranking.

Use these adapters only behind explicit policy gates and provenance logging.

### Priority C: materials stack upgrade

Atlas already has materials-oriented loops, but they are weak compared with the current ecosystem.

- Add `mattergen_adapter` for candidate generation under target properties.
- Add `mattersim_adapter` for fast post-generation validation under temperature and pressure constraints.
- Chain them into a new `materials_design_loop_v2`:
  1. generate candidates,
  2. simulate stability and properties,
  3. rank by novelty, stability and application constraints,
  4. export a reproducible candidate report.

This is one of the most practical routes to a credible autonomous science demo.

### Priority D: climate and Earth science expansion

Atlas has climate services, but they can be made much more ambitious:

- add `alphaearth_adapter` for large-scale geospatial embeddings,
- add dataset ingestion from Google Earth Engine outputs,
- support land-use change, crop stress, deforestation and water-resource workflows,
- benchmark against historical forecasting / mapping tasks.

### Priority E: autonomous-science control plane

Atlas should adopt patterns that recent systems made explicit:

- from **AI co-scientist**:
  - specialized agents with reviewer/evolver/meta-review roles,
  - iterative proposal refinement instead of one-pass generation;
- from **Robin**:
  - narrow but complete workflows that connect hypothesis, experiment proposal and analysis;
- from **AlphaEvolve**:
  - evaluator-driven search with hard verification for math/code subproblems.

Recommended internal additions:

- `ResearchSupervisor`
- `ExperimentDesigner`
- `EvidenceCritic`
- `ProtocolReviewer`
- `AlgorithmEvolver`
- `ReproducibilityAuditor`

These should be explicit services, not only prompt roles.

## Concrete implementation plan for Atlas

### Phase 1: next 2 weeks

- Make Ollama Cloud the default tested frontier runtime for real pipelines.
- Keep per-role model routing in `config/agents.yaml`.
- Add a reusable smoke runner for integrated pipelines.
- Harden quantum/materials services against modern library versions.
- Add structured artifact export with absolute paper paths and evidence metrics.

### Phase 2: next 4-6 weeks

- Integrate PaperQA2 as the main literature QA and contradiction engine.
- Add MatterGen + MatterSim adapters.
- Add AlphaFold 3 / AlphaGenome / ESM3 adapter scaffolding with feature flags.
- Add benchmark suites for:
  - literature synthesis,
  - materials candidate generation,
  - quantum / algorithm tasks,
  - reproducible paper generation.

### Phase 3: next 2-3 months

- Build domain-specific autonomous loops:
  - `genomics_variant_loop`
  - `protein_design_loop`
  - `materials_discovery_loop`
  - `earth_monitoring_loop`
- Add experiment bundle generation with:
  - config snapshot,
  - literature snapshot,
  - tool call traces,
  - dataset hashes,
  - paper draft,
  - reviewer verdicts.

## Technical architecture changes to add

- New package: `app/services/external_science/`
- New package: `app/services/literature_agents/`
- New package: `app/services/evaluators/`
- New package: `app/services/reproducibility/`
- New config files:
  - `config/external_science.yaml`
  - `config/research_benchmarks.yaml`
  - `config/reproducibility_policy.yaml`

Suggested adapter contract:

```python
class ExternalScienceAdapter(BaseService):
    async def run(self, task: dict[str, Any]) -> dict[str, Any]:
        ...
```

Every adapter output should include:

- `success`
- `provider`
- `model_or_tool`
- `inputs_digest`
- `outputs_digest`
- `citation`
- `confidence`
- `artifacts`

## Highest-value near-term demos

If the goal is to make Atlas visibly credible fast, the best demo sequence is:

1. **Quantum / algorithmic research smoke**
   - low data burden,
   - reproducible,
   - fast local verification.
2. **Materials generation + simulation**
   - highest practical value for AI-for-science storytelling.
3. **Literature-grounded biology ideation**
   - use PaperQA2 + AlphaGenome/ESM3 style adapters where available.
4. **Climate mapping workflow**
   - use geospatial embeddings and evidence-backed reporting.

## Sources

- Google Research, **AI co-scientist**, February 19, 2025:
  [research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist](https://research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist/)
- Google DeepMind / Isomorphic Labs, **AlphaFold 3**, May 8, 2024:
  [blog.google/innovation-and-ai/products/google-deepmind-isomorphic-alphafold-3-ai-model](https://blog.google/innovation-and-ai/products/google-deepmind-isomorphic-alphafold-3-ai-model/)
- Google DeepMind, **AlphaGenome**, June 25, 2025:
  [deepmind.google/blog/alphagenome-ai-for-better-understanding-the-genome](https://deepmind.google/blog/alphagenome-ai-for-better-understanding-the-genome/)
- Google DeepMind, **AlphaEvolve**, May 14, 2025:
  [deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/)
- Google DeepMind, **AlphaEarth Foundations**, July 30, 2025:
  [deepmind.google/blog/alphaearth-foundations-helps-map-our-planet-in-unprecedented-detail](https://deepmind.google/blog/alphaearth-foundations-helps-map-our-planet-in-unprecedented-detail/)
- Microsoft Research, **MatterSim**, May 13, 2024:
  [microsoft.com/en-us/research/blog/mattersim-a-deep-learning-model-for-materials-under-real-world-conditions](https://www.microsoft.com/en-us/research/blog/mattersim-a-deep-learning-model-for-materials-under-real-world-conditions/)
- Microsoft Research / Nature publication page, **MatterGen**, January 2025:
  [microsoft.com/en-us/research/publication/a-generative-model-for-inorganic-materials-design](https://www.microsoft.com/en-us/research/publication/a-generative-model-for-inorganic-materials-design/)
- EvolutionaryScale, **ESM3**, June 25, 2024:
  [evolutionaryscale.ai/blog/esm3-release](https://www.evolutionaryscale.ai/blog/esm3-release)
- Boltz official repository:
  [github.com/jwohlwend/boltz](https://github.com/jwohlwend/boltz)
- FutureHouse, **Robin**, May 20, 2025:
  [futurehouse.org/research-announcements/demonstrating-end-to-end-scientific-discovery-with-robin-a-multi-agent-system](https://www.futurehouse.org/research-announcements/demonstrating-end-to-end-scientific-discovery-with-robin-a-multi-agent-system)
- FutureHouse, **PaperQA2** repository:
  [github.com/Future-House/paper-qa](https://github.com/Future-House/paper-qa)
- PaperQA2 paper, September 2024:
  [arxiv.org/abs/2409.13740](https://arxiv.org/abs/2409.13740)
