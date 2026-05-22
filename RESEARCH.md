# A.M.Y — Research Papers & Scientific Foundations

## Core Theoretical Frameworks

### 1. Active Inference & Free Energy Principle (Karl Friston)
- **Paper**: Friston, K. (2010). "The free-energy principle: a unified brain theory?" *Nature Reviews Neuroscience*, 11(2), 127-138.
- **Book**: Parr, T., Pezzulo, G., & Friston, K. J. (2022). *Active Inference: The Free Energy Principle in Mind, Brain, and Behavior*. MIT Press.
- **Implementation**: `pymdp` — https://github.com/infer-actively/pymdp (Python/JAX, MIT License)
- **Key Insight**: Todo sistema que persiste minimiza su energía libre variacional. La percepción actualiza el modelo interno; la acción cambia el mundo para que coincida con las predicciones. La **curiosidad** emerge como "valor epistémico" — el agente busca reducir su propia incertidumbre.
- **Relevancia para A.M.Y**: El motor central. A.M.Y mantiene un modelo generativo del mundo y continuamente minimiza la divergencia entre lo que predice y lo que observa, mediante dos rutas: actualizar su modelo (aprender) o actuar sobre el mundo (experimentar).

### 2. Global Workspace Theory (Bernard Baars / Stanislas Dehaene)
- **Paper**: Baars, B. J. (1988). *A Cognitive Theory of Consciousness*. Cambridge UP.
- **Paper**: Dehaene, S., Kerszberg, M., & Changeux, J. P. (1998). "A neuronal model of a global workspace in effortful cognitive tasks." *PNAS*, 95(24), 14529-14534.
- **Implementation**: LIDA (Learning Intelligent Distribution Agent) — Stan Franklin, U. of Memphis
- **Key Insight**: El cerebro tiene muchos módulos especializados procesando en paralelo. Solo un contenido a la vez gana la "competición por la atención" y se retransmite (broadcast) a todos los demás módulos. Esto crea una integración funcional de información.
- **Relevancia para A.M.Y**: La arquitectura de atención. Múltiples módulos (percepción, memoria, razonamiento, curiosidad) compiten por el "foco de pensamiento". El ganador difunde su contenido a todos los demás, coordinando la actividad cognitiva.

### 3. SOAR Cognitive Architecture
- **Paper**: Laird, J. E., Newell, A., & Rosenbloom, P. S. (1987). "SOAR: An architecture for general intelligence." *Artificial Intelligence*, 33(1), 1-64.
- **Book**: Laird, J. E. (2012). *The Soar Cognitive Architecture*. MIT Press.
- **Implementation**: https://soar.eecs.umich.edu/ (C/C++, BSD License)
- **Key Insight**: Ciclo de proponer→evaluar→seleccionar→aplicar operadores (~50ms). Cuando el conocimiento es insuficiente, surge un "impasse" que genera automáticamente un subespacio de resolución (recursión). El "chunking" compila razonamiento deliberativo en comportamiento automático.
- **Relevancia para A.M.Y**: El ciclo operativo y la recursión. Cuando A.M.Y encuentra un problema que no puede resolver, automáticamente descompone en sub-problemas. Con el tiempo, las soluciones deliberativas se compilan en skills automáticas.

## Autonomous Agent Research

### 4. Voyager: Open-Ended Lifelong Learning
- **Paper**: Wang, G. et al. (2023). "Voyager: An Open-Ended Embodied Agent with Large Language Models." *arXiv:2305.16291*.
- **Code**: https://github.com/MineDojo/Voyager (MIT License)
- **Key Components**:
  - **Automatic Curriculum**: GPT-4 genera la siguiente tarea basándose en el estado actual del agente
  - **Skill Library**: Skills como código ejecutable indexado por embeddings semánticos
  - **Iterative Prompting**: Feedback del entorno + errores de ejecución + auto-verificación
- **Relevancia para A.M.Y**: El patrón de skill library y automatic curriculum. A.M.Y acumula habilidades como código ejecutable y genera su propio plan de estudio basado en lo que ya sabe.

### 5. ReAct: Synergizing Reasoning and Acting
- **Paper**: Yao, S. et al. (2022). "ReAct: Synergizing Reasoning and Acting in Language Models." *ICLR 2023*. arXiv:2210.03629.
- **Code**: https://react-lm.github.io/
- **Key Insight**: Intercalar razonamiento (traces de pensamiento) con acciones (queries a APIs, búsquedas). El razonamiento guía las acciones; las acciones alimentan el razonamiento.
- **Relevancia para A.M.Y**: El patrón de interleaving entre pensamiento y acción en cada step del heartbeat.

### 6. LATM: LLMs As Tool Makers
- **Paper**: Cai, T. et al. (2023). "Large Language Models as Tool Makers." *arXiv:2305.17126*.
- **Key Insight**: Los LLMs pueden crear sus propias herramientas reusables. Un modelo "tool maker" genera funciones; un modelo "tool user" las aplica. Las herramientas se cachean para uso futuro.
- **Relevancia para A.M.Y**: A.M.Y puede crear sus propias herramientas de análisis y experimentación, almacenarlas en su skill library, y reutilizarlas.

### 7. ResearchAgent: Iterative Research Idea Generation
- **Paper**: Baek, J. et al. (2024). "ResearchAgent: Iterative Research Idea Generation over Scientific Literature with Large Language Models." *NAACL 2025*. arXiv:2404.07738.
- **Key Insight**: El agente genera ideas de investigación, luego múltiples "reviewing agents" internos las critican, y se refinan iterativamente. Conecta papers a través de un grafo académico y entidades compartidas.
- **Relevancia para A.M.Y**: El módulo de reflexión. A.M.Y tiene "voces internas" que critican y refinan sus propias hipótesis antes de experimentar.

## Intrinsic Motivation & Curiosity

### 8. Curiosity-Driven Exploration (ICM)
- **Paper**: Pathak, D. et al. (2017). "Curiosity-driven Exploration by Self-Supervised Prediction." *ICML 2017*. arXiv:1705.05363.
- **Code**: https://pathak22.github.io/noreward-rl/
- **Key Insight**: La curiosidad = error de predicción del agente al predecir consecuencias de sus acciones, en un feature space aprendido (no píxeles crudos). Ignora factores incontrolables del entorno.

### 9. Large-Scale Study of Curiosity-Driven Learning
- **Paper**: Burda, Y. et al. (2018). "Large-Scale Study of Curiosity-Driven Learning." *arXiv:1808.04355*.
- **Key Insight**: La curiosidad sola (sin recompensa externa) logra rendimiento sorprendente en 54+ entornos. Pero falla en entornos estocásticos ("problema de la TV ruidosa"). Random Network Distillation (RND) es más robusto.

### 10. Autotelic Agents
- **Paper**: Colas, C., Karch, T., Sigaud, O., & Oudeyer, P. Y. (2022). "Autotelic Agents with Intrinsically Motivated Goal-Conditioned Reinforcement Learning."
- **Key Insight**: Agentes que generan, seleccionan y resuelven sus propios problemas. Marco del Developmental RL. Repertorio abierto de habilidades que crece incrementalmente.

## Never-Ending Learning

### 11. NELL (Never-Ending Language Learning)
- **Paper**: Mitchell, T. et al. (2018). "Never-Ending Learning." *Communications of the ACM*, 61(5), 103-115.
- **Institución**: Carnegie Mellon University (DARPA + Google)
- **Key Insight**: Sistema corriendo 24/7 desde 2010, leyendo la web y construyendo una base de 120M+ creencias. Auto-corrección parcial. Problemas: acumulación de errores, solo 3% de creencias de alta confianza.
- **Lección para A.M.Y**: Necesitamos mecanismos robustos de calibración de confianza, "olvido activo" de creencias erróneas, y revisión bayesiana continua.

## Related World Models & Dreaming

### 12. World Models (Ha & Schmidhuber)
- **Paper**: Ha, D. & Schmidhuber, J. (2018). "World Models." *arXiv:1803.10122*.
- **Key Insight**: El agente aprende un modelo comprimido del mundo (VAE + RNN) y puede "soñar" — planificar en su imaginación sin interactuar con el entorno real. Entrenamiento dentro del sueño transfiere al mundo real.
- **Relevancia para A.M.Y**: El módulo de "consolidación" de memoria. Cuando A.M.Y no tiene datos nuevos, puede "soñar" — simular escenarios en su world model para descubrir patrones.

### 13. Generative Agents (Stanford)
- **Paper**: Park, J. S. et al. (2023). "Generative Agents: Interactive Simulacra of Human Behavior." *arXiv:2304.03442*.
- **Key Insight**: 25 agentes con reloj interno, observan, guardan recuerdos, reflexionan (consolidan memorias en insights de alto nivel), y planifican sin input externo.
- **Relevancia para A.M.Y**: El patrón de reflexión. A.M.Y reflexiona sobre sus memorias para extraer insights de alto nivel que guían su investigación.

---

## Frameworks & Libraries de Referencia

| Biblioteca | Uso | URL |
|-----------|-----|-----|
| `pymdp` | Active Inference (POMDP) | https://github.com/infer-actively/pymdp |
| `stable-baselines3` | RL para módulos de bajo nivel | https://github.com/DLR-RM/stable-baselines3 |
| `chromadb` | Vector DB para skill library/memory | https://github.com/chroma-core/chroma |
| `networkx` | Knowledge Graph | https://networkx.org/ |
| `langchain` / `litellm` | Abstracción LLM | https://github.com/BerriAI/litellm |
| `docker` SDK | Sandbox para ejecutar experimentos | https://docker-py.readthedocs.io/ |
