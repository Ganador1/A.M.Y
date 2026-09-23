# A.M.Y — Research Papers and Scientific Foundations

This English overview identifies architectural inspirations. Similar terminology does not mean AMY implements or experimentally validates every mechanism in the cited work. In particular, its curiosity and belief updates are heuristics, not a trained ICM network or a demonstration of general intelligence.

## Cognitive architectures

- **Active inference:** Friston, K. (2010), “The free-energy principle: a unified brain theory?”, Nature Reviews Neuroscience 11, 127–138; Parr, Pezzulo and Friston (2022), *Active Inference*, MIT Press. Perception and action provide a conceptual model for updating beliefs and choosing informative experiments.
- **Global workspace:** Baars (1988), *A Cognitive Theory of Consciousness*; Dehaene, Kerszberg and Changeux (1998), PNAS 95, 14529–14534. Competition for attention and broadcasting motivate AMY's workspace interface, without a claim about consciousness.
- **SOAR:** Laird, Newell and Rosenbloom (1987), Artificial Intelligence 33, 1–64; Laird (2012), *The Soar Cognitive Architecture*. Proposing, selecting and applying operators motivates goal decomposition and the operating loop. AMY does not implement every SOAR mechanism.

## Tool use and research agents

- **Voyager:** Wang et al. (2023), arXiv:2305.16291. Automatic curricula, executable skill libraries and iterative feedback inform reusable skills and follow-up goals.
- **ReAct:** Yao et al. (2022), arXiv:2210.03629. Interleaving reasoning and actions informs the decision/tool loop.
- **LLMs as Tool Makers:** Cai et al. (2023), arXiv:2305.17126. Reusable generated functions motivate the distinction between creating and applying tools.
- **ResearchAgent:** Baek et al. (2024), arXiv:2404.07738. Iterative idea generation and review motivate reflection. Internal critique does not replace external peer review.

## Curiosity and continual learning

- **ICM:** Pathak et al. (2017), arXiv:1705.05363. Prediction error motivates exploration in learned feature spaces.
- **Curiosity-driven learning:** Burda et al. (2018), arXiv:1808.04355. Stochastic distractions motivate caution when using surprise as a research reward.
- **Autotelic agents:** Colas, Karch, Sigaud and Oudeyer (2022), *Autotelic Agents with Intrinsically Motivated Goal-Conditioned Reinforcement Learning*. Self-generated goals motivate an expanding task repertoire.
- **NELL:** Mitchell et al. (2018), *Never-Ending Learning*, Communications of the ACM 61, 103–115. Continual knowledge acquisition motivates explicit confidence, correction and retirement of unsupported beliefs.

## Memory and world models

- **World Models:** Ha and Schmidhuber (2018), arXiv:1803.10122. Learned simulation motivates hypothetical planning; AMY's world-model abstraction is not an implementation of the full VAE/RNN system.
- **Generative Agents:** Park et al. (2023), arXiv:2304.03442. Observation, memory, reflection and planning inform the organization of agent state.

## Implementation context

NetworkX supports graph memory; optional ChromaDB supports vector retrieval. Scientific backends include NumPy, SciPy, SymPy and domain-specific libraries through Atlas. Dependency availability and evidence grade must be checked for each tool. External frameworks mentioned in historical notes are references, not necessarily installed AMY dependencies.

Current experimental results and their evidence are maintained in [the results catalog](docs/RESULTS.md), separately from these conceptual foundations.
