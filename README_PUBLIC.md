# A.M.Y — Autonomous Mind Yield

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Science: Real](https://img.shields.io/badge/science-real-green.svg)](SCIENCE_MANIFESTO.md)

> **Una mente artificial que nunca duerme.** Piensa, investiga, experimenta, aprende y evoluciona de forma autónoma — con rigor científico real.

---

## ¿Qué es A.M.Y?

A.M.Y no es un chatbot. No es un agente que espera tu pregunta. Es una **mente artificial autónoma** que, una vez le das un objetivo científico, se dedica a ese problema **continuamente**:

- 🔬 **Investiga** literatura científica real (PubMed, arXiv, Semantic Scholar)
- 🧠 **Razona** con arquitectura cognitiva inspirada en Active Inference + Global Workspace Theory
- 🧪 **Experimenta** con código Python ejecutado en sandbox aislado
- 📊 **Analiza** datos con herramientas científicas validadas (84+ de AXIOM Atlas)
- 📝 **Escribe** papers académicos con citas reales
- 🔍 **Se revisa a sí misma** con peer review autónomo
- 🔄 **Aprende** de sus errores y pivota a nuevas direcciones

### Demo: Investigando Gaps Primos

```bash
# A.M.Y investiga autónomamente si los gaps entre primos son normales
python run_amy_debug.py

# Resultado: Rechazo fuerte de normalidad (Shapiro-Wilk p = 2.10e-55)
# La distribución es asimétrica positiva (skewness = 1.81) con colas pesadas
# La exponencial tiene mejor AIC que la normal
```

---

## 🚀 Inicio Rápido

### Requisitos

- Python 3.13+
- macOS (Apple Silicon M4 optimizado) o Linux
- 8GB+ RAM recomendado
- API key de Ollama Cloud (o compatible OpenAI)

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/tuusuario/amy.git
cd amy

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar API keys
cp .env.example .env
# Editar .env con tus keys:
# OLLAMA_CLOUD_API_KEY_1=sk-...
# OLLAMA_CLOUD_API_KEY_2=sk-...  # Opcional, para load balancing

# 5. Verificar instalación
python test_amy_quick.py
```

### Ejecutar A.M.Y

```bash
# Modo debug: 3 ciclos con timeout
python run_amy_debug.py

# Misión completa: hasta 12 ciclos + generación de paper
python run_amy_full_mission.py

# Paper específico
python run_amy_paper.py
```

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                     A.M.Y COGNITIVE CORE                        │
│                                                                 │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  ┌───────────┐ │
│  │ PERCEPCIÓN│  │  WORLD MODEL │  │ GOAL STACK│  │  CURIOSITY│ │
│  │ (senses) │→ │ (free energy)│← │ (SOAR-like)│← │  (ICM/RND)│ │
│  └──────────┘  └──────────────┘  └───────────┘  └───────────┘ │
│        ↓              ↕                ↓               ↓       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │            GLOBAL WORKSPACE (attention bus)              │   │
│  │   Módulos compiten → ganador se broadcast a todos       │   │
│  └─────────────────────────────────────────────────────────┘   │
│        ↓              ↓                ↓               ↓       │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  ┌───────────┐ │
│  │ SKILL    │  │  KNOWLEDGE   │  │ EXPERIMENT│  │  SELF-    │ │
│  │ LIBRARY  │  │  GRAPH       │  │ ENGINE    │  │  RETRAIN  │ │
│  │ (Voyager)│  │  (NELL-like) │  │ (sandbox) │  │  MODULE   │ │
│  └──────────┘  └──────────────┘  └───────────┘  └───────────┘ │
│                          ↓                                     │
│                 ┌─────────────────┐                             │
│                 │  COMMUNICATION  │                             │
│                 │  (solo hallazgos│                             │
│                 │   significativos)│                             │
│                 └─────────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
                    ↕ HEARTBEAT LOOP (nunca se detiene)
```

### Componentes Principales

| Módulo | Archivo | Función |
|--------|---------|---------|
| **Heartbeat** | `core/heartbeat.py` | Ciclo cognitivo infinito |
| **World Model** | `core/world_model.py` | Modelo generativo interno (Active Inference) |
| **Global Workspace** | `core/global_workspace.py` | Bus de atención y broadcast |
| **Reasoning** | `cognition/reasoning.py` | Motor de razonamiento con LLM |
| **Goal Stack** | `cognition/goal_stack.py` | Gestión jerárquica de objetivos (SOAR) |
| **Curiosity** | `cognition/curiosity.py` | Motivación intrínseca (ICM/RND) |
| **Episodic Memory** | `memory/episodic.py` | Memoria de experiencias |
| **Semantic Memory** | `memory/semantic.py` | Grafo de conocimiento |
| **Sandbox** | `sandbox/executor.py` | Ejecución aislada de experimentos |
| **Atlas Tools** | `core/atlas_tools.py` | 84+ herramientas científicas |

---

## 🔬 Ciencia Real

A.M.Y no genera "ciencia de juguete". Sigue principios rigurosos:

### ✅ Falsificación Primero
Antes de aceptar un hallazgo, busca activamente evidencia en contra.

### ✅ Evidencia Real
Toda afirmación numérica viene de experimentos ejecutados o papers reales con DOI.

### ✅ Reproducibilidad
Todo experimento incluye código completo, inputs, outputs y timestamp.

### ✅ Validación con Herramientas
Verifica con SymPy, NumPy, RDKit, BioPython y 84+ herramientas de Atlas.

### ✅ Anti-Bucles
No repite hipótesis ya validadas. Siempre pivota a la siguiente pregunta abierta.

Lee el [Science Manifesto](SCIENCE_MANIFESTO.md) para más detalles.

---

## 🧪 Herramientas Científicas (84+)

A.M.Y se integra con **AXIOM Atlas** para acceso a herramientas reales:

| Dominio | # Herramientas | Ejemplos |
|---------|---------------|----------|
| **Matemáticas** | 19 | `sympy_solve_equation`, `prime_gap_analysis`, `z3_prover` |
| **Física** | 10 | `quantum_energy_levels`, `quantum_circuit`, `plasma_physics` |
| **Química** | 14 | `molecular_weight_calc`, `computational_chemistry`, `xray_crystallography` |
| **Biología** | 7 | `dna_analyzer`, `protein_properties`, `genomics` |
| **Medicina** | 4 | `alpha_fold3`, `clinical_bert`, `medical_imaging` |
| **Estadística** | 5 | `hypothesis_tester`, `correlation_analysis`, `distribution_fitting` |
| **Astronomía** | 2 | `astronomical_ml`, `light_curves` |
| **Neurociencia** | 2 | `neuro_simulation`, `brain_computer_interface` |

---

## 📊 Resultados de Ejemplo

### Prime Gap Analysis (Ejecución Real)

```
Prime gap analysis up to 10,000,000:
  Number of primes: 664,579
  Mean gap: 15.0471
  Std dev: 12.5697
  Max gap: 154
  
Shapiro-Wilk: W=0.857121, p=2.10e-55
  → STRONG REJECTION of normality

Skewness: 1.8147 (Normal=0)
Excess Kurtosis: 4.9110 (Normal=0)
  → Right-skewed, heavy-tailed

AIC comparison:
  Exponential AIC: 4,841,345.51
  Normal AIC: 5,250,472.89
  → Exponential fits better
```

---

## 🧪 Tests

```bash
# Tests rápidos de verificación
python test_amy_quick.py

# Tests unitarios
pytest tests/ -v

# Validación de herramientas Atlas
python test_atlas_tools.py
```

---

## ⚙️ Configuración

Edita `config.yaml`:

```yaml
mission:
  goal: "Tu objetivo científico aquí"
  urgency: medium

llm:
  provider: "ollama_cloud"
  base_url: "https://ollama.com/api"
  reasoner:
    model: "glm-5.1"
    temperature: 0.7
    max_tokens: 4096

hardware:
  device: "mps"  # Apple Silicon
  dtype: "float16"

heartbeat:
  base_interval_seconds: 30
  focused_interval_seconds: 5
  idle_interval_seconds: 120
```

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Lee [CONTRIBUTING.md](CONTRIBUTING.md) para:

- Agregar nuevas herramientas científicas
- Mejorar la arquitectura cognitiva
- Corregir bugs
- Traducir documentación

### Roadmap

- [ ] Soporte para múltiples LLM providers (OpenAI, Anthropic, local)
- [ ] Integración con Jupyter notebooks
- [ ] Dashboard web para monitoreo
- [ ] Soporte para experimentos distribuidos
- [ ] Integración con repositorios de datos (Zenodo, Figshare)

---

## 📚 Documentación

| Documento | Contenido |
|-----------|-----------|
| [README.md](README.md) | Este documento |
| [SCIENCE_MANIFESTO.md](SCIENCE_MANIFESTO.md) | Principios de rigor científico |
| [RESEARCH.md](RESEARCH.md) | Papers y referencias científicas |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Guía de contribución |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Código de conducta |
| [docs/](docs/) | Documentación técnica completa |

---

## 🙏 Agradecimientos

A.M.Y está inspirada en décadas de investigación en:

- **Active Inference** — Karl Friston
- **Global Workspace Theory** — Bernard Baars, Stanislas Dehaene
- **SOAR** — Allen Newell, John Laird, Paul Rosenbloom
- **Curiosity-Driven Learning** — Deepak Pathak et al.
- **Voyager** — Linxi Wang et al. (NVIDIA/Caltech)
- **NELL** — Tom Mitchell et al. (CMU)

---

## 📄 Licencia

MIT License — ver [LICENSE](LICENSE) para detalles.

**Restricciones éticas:**
- ❌ No usar para armas biológicas/químicas
- ❌ No usar para vigilancia masiva
- ✅ Uso académico y comercial permitido con atribución

---

*A.M.Y — Autonomous Mind Yield*
*Una mente que nunca duerme, dedicada a expandir el conocimiento humano.*

**Estado:** Pre-release (v0.9.0)  
**Última actualización:** Abril 2026  
**Autor:** Giovanni Arangio
