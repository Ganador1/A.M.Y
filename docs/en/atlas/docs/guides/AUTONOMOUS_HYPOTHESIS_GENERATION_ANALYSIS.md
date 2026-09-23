> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="análisis-del-sistema-autónomo-de-generación-de-hipótesis"></a>
# Analysis of the Autonomous Hypothesis Generation System

**Date:** 2 October 2025  
**Status:** Complete Analysis + Improvement Roadmap

---

<a id="-estado-actual-del-sistema"></a>
## 📊 Current State of the System

<a id="1-arquitectura-autónoma-existente"></a>
### 1. **Existing Autonomous Architecture**

The ATLAS project has a robust autonomous architecture in `app/autonomous/`:

<a id="componentes-core"></a>
#### **Core Components:**
- ✅ `BudgetAllocator` - Allocation of computational resources
- ✅ `PriorityScorer` - Ranking of candidates by importance
- ✅ `StateManager` - Iterative state management
- ✅ `TaskScheduler` - Task planning with diversity quota
- ✅ `NoveltyAssessor` - Scientific novelty evaluation
- ✅ `HypothesisMutator` - Hypothesis mutation and variation

<a id="pipelines-de-dominio"></a>
#### **Domain Pipelines:**
- ✅ `MathematicsLoop` - Autonomous exploration in mathematics
- ✅ `BiologyLoop` - Discovery in structural biology
- ✅ `ChemistryLoop` - Materials search
- ✅ `QuantumLoop` - Quantum computing
- ✅ `ClimateLoop` - Climate science

<a id="generadores-de-hipótesis"></a>
#### **Hypothesis Generators:**
- ⚠️ `HypothesisMutator` - **LIMITED**: Mutations based on text heuristics
- ⚠️ `ProofSketchGenerator` - **PLACEHOLDER**: Only generates basic skeletons
- ❌ **MISSING**: Real generation using scientific LLMs

<a id="2-modelos-llm-actuales"></a>
### 2. **Current LLM Models**

<a id="ollama-cloud-implementado"></a>
#### **Ollama Cloud (Implemented)**
```python
<a id="appservicesollama_servicepy"></a>
# app/services/ollama_service.py
DOMAIN_MODEL_MAP = {
    "quantum_computing": "deepseek-r1",
    "mathematics": "deepseek-r1",
    "physics": "deepseek-r1",
    "materials_science": "qwen3",
    "chemistry": "qwen3",
    "biology": "qwen3",
}

AVAILABLE_MODELS = {
    "deepseek-r1": ["deepseek-r1:7b", "deepseek-v3.1:671b-cloud"],
    "qwen3": ["qwen3:72b", "qwen3-coder:480b-cloud"],
    "llama3.1": ["llama3.1:8b-instruct", "llama3.1:405b"],
    "gemma3": ["gemma3:27b", "gemma3-instruct:405b-cloud"]
}
```

**Status:**
- ✅ Complete integration with Ollama
- ✅ Rate limiting implemented
- ✅ Automatic fallback
- ⚠️ **NOT integrated with autonomous pipelines**

---

<a id="-modelos-llm-pre-entrenados-con-papers-científicos"></a>
## 🔬 LLM Models Pre-trained with Scientific Papers

<a id="modelos-especializados-disponibles"></a>
### **Specialized Models Available**

<a id="1-galactica-meta-ai-"></a>
#### 1. **Galactica (Meta AI)** 🌟
- **Repository:** `facebook/galactica-120b` (HuggingFace)
- **Size:** 120B parameters
- **Training:** 48M scientific papers (ArXiv, PubMed, Wikipedia)
- **Specialization:** Mathematics, chemistry, physics, biology
- **Access:** HuggingFace Inference API (FREE with limits)
- **Advantage:** Generates LaTeX, references, scientific reasoning
- **Issue:** Model officially retired, but available for research

<a id="2-biogpt-microsoft-"></a>
#### 2. **BioGPT (Microsoft)** 🧬
- **Repository:** `microsoft/biogpt`
- **Size:** 1.5B parameters
- **Training:** 15M biomedical articles from PubMed
- **Specialization:** Molecular biology, medicine
- **Access:** HuggingFace free
- **Advantage:** Excellent for biomedical hypotheses

<a id="3-scibert-allen-ai-"></a>
#### 3. **SciBERT (Allen AI)** 📚
- **Repository:** `allenai/scibert_scivocab_uncased`
- **Size:** 110M parameters
- **Training:** 1.14M papers from Semantic Scholar
- **Specialization:** Scientific text comprehension
- **Access:** HuggingFace free
- **Use:** Scientific embeddings, classification

<a id="4-pubmedgpt-stanford-"></a>
#### 4. **PubMedGPT (Stanford)** 💊
- **Repository:** `stanford-crfm/pubmedgpt`
- **Size:** 2.7B parameters
- **Training:** PubMed abstracts
- **Specialization:** Medical literature
- **Access:** HuggingFace free

<a id="5-scholarbert-custom-"></a>
#### 5. **ScholarBERT (Custom)** 📖
- **Repository:** Various BERT fine-tunes on ArXiv
- **Specialization:** Physics, mathematics
- **Access:** HuggingFace free

---

<a id="-apis-gratuitas-de-modelos-llm"></a>
## 🆓 Free APIs for LLM Models

<a id="1-huggingface-inference-api-"></a>
### **1. HuggingFace Inference API** ⭐⭐⭐⭐⭐
```python
<a id="gratis-con-rate-limits-razonables"></a>
# GRATIS (con rate limits razonables)
API_URL = "https://api-inference.huggingface.co/models/{model_id}"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

<a id="modelos-científicos-disponibles"></a>
# Modelos científicos disponibles:
- facebook/galactica-120b
- microsoft/biogpt
- allenai/scibert_scivocab_uncased
- EleutherAI/gpt-neox-20b
```

**Free Limits:**
- ~1000 requests/day
- Rate limit: ~10 req/min
- Timeout: 60s/request

<a id="2-together-ai-"></a>
### **2. Together AI** ⭐⭐⭐⭐
```python
<a id="25-gratis-al-registrarse"></a>
# $25 GRATIS al registrarse
API_URL = "https://api.together.xyz/inference"

<a id="modelos-científicos"></a>
# Modelos científicos:
- meta-llama/Llama-3-70b-chat
- mistralai/Mixtral-8x7B-Instruct-v0.1
- NousResearch/Nous-Hermes-2-Mixtral-8x7B
```

**Limits:**
- $25 free credit
- ~200K free tokens
- Rate limit: 600 req/min

<a id="3-replicate-"></a>
### **3. Replicate** ⭐⭐⭐
```python
<a id="gratis-límites-generosos"></a>
# GRATIS (límites generosos)
API_URL = "https://api.replicate.com/v1/predictions"

<a id="modelos-disponibles"></a>
# Modelos disponibles:
- meta/llama-2-70b-chat
- stability-ai/stable-diffusion (para visualizaciones)
```

**Limits:**
- $0.006/1K tokens
- Initial free credit

<a id="4-groq-"></a>
### **4. Groq** ⭐⭐⭐⭐⭐
```python
<a id="gratis-muy-rápido"></a>
# GRATIS (muy rápido)
API_URL = "https://api.groq.com/openai/v1/chat/completions"

<a id="modelos"></a>
# Modelos:
- llama3-70b-8192
- mixtral-8x7b-32768
```

**Limits:**
- FREE for moderate use
- Extremely fast (LPU acceleration)
- Rate limit: 30 req/min

<a id="5-perplexity-ai-pplx-api-"></a>
### **5. Perplexity AI (pplx-api)** ⭐⭐⭐
```python
<a id="5-gratis-al-registrarse"></a>
# $5 GRATIS al registrarse
API_URL = "https://api.perplexity.ai/chat/completions"

<a id="modelos-con-búsqueda-web-integrada"></a>
# Modelos con búsqueda web integrada:
- pplx-70b-online
- pplx-7b-chat
```

---

<a id="-datasets-para-fine-tuning"></a>
## 📋 Datasets for Fine-tuning

<a id="papers-científicos"></a>
### **Scientific Papers**

1. **ArXiv Dataset** (2M+ papers)
   - Source: https://www.kaggle.com/Cornell-University/arxiv
   - Format: JSON with abstract, full text
   - Categories: cs, math, physics, q-bio

2. **PubMed Central Open Access** (3M+ papers)
   - Source: https://www.ncbi.nlm.nih.gov/pmc/tools/openftlist/
   - Format: XML, PDF
   - Specialization: Biomedicine

3. **Semantic Scholar Open Research Corpus** (200M+ papers)
   - Source: https://www.semanticscholar.org/product/api
   - API: FREE
   - Metadata: Citations, abstracts, full-text

4. **OpenAlex** (240M+ papers)
   - Source: https://openalex.org
   - API: FREE
   - Successor to Microsoft Academic Graph

---

<a id="-propuesta-de-mejora-sistema-híbrido-multi-modelo"></a>
## 🚀 Improvement Proposal: Hybrid Multi-Model System

<a id="arquitectura-propuesta"></a>
### **Proposed Architecture**

```
┌─────────────────────────────────────────────────────┐
│         AUTONOMOUS HYPOTHESIS GENERATOR             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────┐  ┌──────────────────┐        │
│  │  MODEL ROUTER   │──│  QUALITY SCORER  │        │
│  └────────┬────────┘  └──────────────────┘        │
│           │                                         │
│  ┌────────▼──────────────────────────┐            │
│  │    MODEL PROVIDERS (Parallel)     │            │
│  ├───────────────────────────────────┤            │
│  │ 1. Ollama (deepseek-r1)           │ ←─ Local  │
│  │ 2. HuggingFace (Galactica)        │ ←─ Cloud  │
│  │ 3. Groq (llama3-70b)              │ ←─ Fast   │
│  │ 4. Together AI (Mixtral)          │ ←─ Smart  │
│  │ 5. BioGPT (specialized)           │ ←─ Domain │
│  └───────────────────────────────────┘            │
│                                                     │
│  ┌─────────────────────────────────┐              │
│  │   CONSENSUS & VALIDATION        │              │
│  │  - Vote aggregation             │              │
│  │  - Confidence scoring           │              │
│  │  - Contradiction detection      │              │
│  └─────────────────────────────────┘              │
│                                                     │
│  ┌─────────────────────────────────┐              │
│  │   HYPOTHESIS REFINEMENT         │              │
│  │  - Iterative improvement        │              │
│  │  - Literature grounding         │              │
│  │  - Testability enhancement      │              │
│  └─────────────────────────────────┘              │
└─────────────────────────────────────────────────────┘
```

<a id="estrategia-de-uso"></a>
### **Usage Strategy**

<a id="fase-1-generación-paralela"></a>
#### **Phase 1: Parallel Generation**
- Send prompt to 3-5 different models
- Use specialized models by domain
- Timeout: 30s per model

<a id="fase-2-consensus-voting"></a>
#### **Phase 2: Consensus Voting**
- Compare generated hypotheses
- Detect common patterns
- Identify unique insights

<a id="fase-3-refinamiento"></a>
#### **Phase 3: Refinement**
- Use best model to refine
- Add literature references
- Validate testability

---

<a id="-plan-de-implementación"></a>
## 🛠️ Implementation Plan

<a id="sprint-1-multi-provider-integration-2-días"></a>
### **Sprint 1: Multi-Provider Integration (2 days)**
- [ ] Create `MultiModelHypothesisService`
- [ ] Integrate HuggingFace Inference API
- [ ] Integrate Groq API
- [ ] Integrate Together AI
- [ ] Robust fallback system

<a id="sprint-2-domain-specific-models-2-días"></a>
### **Sprint 2: Domain-Specific Models (2 days)**
- [ ] Integrate BioGPT for biology
- [ ] Integrate Galactica for physics/mathematics
- [ ] Create adapters per domain
- [ ] Quality benchmark

<a id="sprint-3-consensus-system-1-día"></a>
### **Sprint 3: Consensus System (1 day)**
- [ ] Implement voting mechanism
- [ ] Contradiction detection
- [ ] Confidence scoring
- [ ] Insight aggregation

<a id="sprint-4-integration-con-autonomous-loops-1-día"></a>
### **Sprint 4: Integration with Autonomous Loops (1 day)**
- [ ] Update `MathematicsLoop` with new service
- [ ] Update `BiologyLoop`
- [ ] Update `ChemistryLoop`
- [ ] End-to-end tests

<a id="sprint-5-fine-tuning-pipeline-3-días"></a>
### **Sprint 5: Fine-tuning Pipeline (3 days)**
- [ ] Download datasets (ArXiv, PubMed)
- [ ] Preprocess papers
- [ ] Fine-tune base model (LoRA)
- [ ] Evaluate improvement vs. base models

---

<a id="-benchmark-de-modelos"></a>
## 📊 Model Benchmark

<a id="criterios-de-evaluación"></a>
### **Evaluation Criteria**
1. **Scientific Novelty** (0-1)
2. **Testability** (0-1)
3. **Theoretical Foundation** (0-1)
4. **Specificity** (0-1)
5. **Experimental Feasibility** (0-1)

<a id="test-cases-por-dominio"></a>
### **Test Cases by Domain**

<a id="matemáticas"></a>
#### **Mathematics:**
- "Find new conjectures about primes"
- "Generalize Fermat's Last Theorem"

<a id="biología"></a>
#### **Biology:**
- "Improve CRISPR efficiency"
- "Predict structure of disordered proteins"

<a id="química"></a>
#### **Chemistry:**
- "Design catalysts for CO2"
- "Synthesize room-temperature superconductors"

---

<a id="-análisis-de-costos"></a>
## 💰 Cost Analysis

<a id="modelo-gratuito-huggingface--groq"></a>
### **Free Model (HuggingFace + Groq)**
- Cost: $0/month
- Limit: ~30K hypotheses/month
- Latency: 2-5s

<a id="modelo-híbrido-ollama-local--apis-gratuitas"></a>
### **Hybrid Model (Local Ollama + free APIs)**
- Cost: $0/month
- Limit: unlimited (local) + 30K/month (cloud)
- Latency: 1-3s

<a id="modelo-premium-con-together-ai--replicate"></a>
### **Premium Model (with Together AI + Replicate)**
- Cost: ~$50/month
- Limit: ~500K hypotheses/month
- Latency: 0.5-2s

---

<a id="-recomendaciones-finales"></a>
## 🎯 Final Recommendations

<a id="para-empezar-inmediatamente"></a>
### **To Start Immediately:**
1. ✅ **Groq API** - Fastest and free
2. ✅ **HuggingFace** - Specialized scientific models
3. ✅ **Local Ollama** - Deepseek-R1 for reasoning

<a id="para-calidad-máxima"></a>
### **For Maximum Quality:**
1. 🌟 **Galactica** via HuggingFace - Best for physics/mathematics
2. 🌟 **BioGPT** - Best for biology/medicine
3. 🌟 **Deepseek-R1** - Best general reasoning

<a id="para-escalabilidad"></a>
### **For Scalability:**
1. 🚀 Fine-tune of Llama-3-70B with ArXiv papers
2. 🚀 LoRA adapters per scientific domain
3. 🚀 Knowledge distillation to small models

---

<a id="-próximos-pasos"></a>
## 📝 Next Steps

1. **Implement `MultiModelHypothesisService`**
2. **Create automatic benchmark system**
3. **Integrate with existing autonomous loops**
4. **Evaluate real quality of generated hypotheses**
5. **Prepare fine-tuning pipeline**

---

**Conclusion:** The project has a solid autonomous foundation, but hypothesis generation is limited to heuristics. With the integration of multiple specialized LLMs (especially scientific models like Galactica and BioGPT) we can achieve hypothesis generation of real research quality, all using free APIs and open source models.
