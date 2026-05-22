# Análisis del Sistema Autónomo de Generación de Hipótesis

**Fecha:** 2 de octubre de 2025  
**Estado:** Análisis Completo + Roadmap de Mejoras

---

## 📊 Estado Actual del Sistema

### 1. **Arquitectura Autónoma Existente**

El proyecto ATLAS tiene una arquitectura autónoma robusta en `app/autonomous/`:

#### **Componentes Core:**
- ✅ `BudgetAllocator` - Asignación de recursos computacionales
- ✅ `PriorityScorer` - Ranking de candidatos por importancia
- ✅ `StateManager` - Gestión de estado iterativo
- ✅ `TaskScheduler` - Planificación de tareas con cuota de diversidad
- ✅ `NoveltyAssessor` - Evaluación de novedad científica
- ✅ `HypothesisMutator` - Mutación y variación de hipótesis

#### **Pipelines de Dominio:**
- ✅ `MathematicsLoop` - Exploración autónoma en matemáticas
- ✅ `BiologyLoop` - Descubrimiento en biología estructural
- ✅ `ChemistryLoop` - Búsqueda de materiales
- ✅ `QuantumLoop` - Computación cuántica
- ✅ `ClimateLoop` - Ciencia climática

#### **Generadores de Hipótesis:**
- ⚠️ `HypothesisMutator` - **LIMITADO**: Mutaciones basadas en heurísticas de texto
- ⚠️ `ProofSketchGenerator` - **PLACEHOLDER**: Solo genera esqueletos básicos
- ❌ **FALTA**: Generación real usando LLMs científicos

### 2. **Modelos LLM Actuales**

#### **Ollama Cloud (Implementado)**
```python
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

**Estado:**
- ✅ Integración completa con Ollama
- ✅ Rate limiting implementado
- ✅ Fallback automático
- ⚠️ **NO integrado con pipelines autónomos**

---

## 🔬 Modelos LLM Pre-entrenados con Papers Científicos

### **Modelos Especializados Disponibles**

#### 1. **Galactica (Meta AI)** 🌟
- **Repositorio:** `facebook/galactica-120b` (HuggingFace)
- **Tamaño:** 120B parámetros
- **Entrenamiento:** 48M papers científicos (ArXiv, PubMed, Wikipedia)
- **Especialización:** Matemáticas, química, física, biología
- **Acceso:** HuggingFace Inference API (GRATIS con límites)
- **Ventaja:** Genera LaTeX, referencias, razonamiento científico
- **Problema:** Modelo retirado oficialmente, pero disponible para investigación

#### 2. **BioGPT (Microsoft)** 🧬
- **Repositorio:** `microsoft/biogpt`
- **Tamaño:** 1.5B parámetros
- **Entrenamiento:** 15M artículos biomédicos de PubMed
- **Especialización:** Biología molecular, medicina
- **Acceso:** HuggingFace gratis
- **Ventaja:** Excelente para hipótesis biomédicas

#### 3. **SciBERT (Allen AI)** 📚
- **Repositorio:** `allenai/scibert_scivocab_uncased`
- **Tamaño:** 110M parámetros
- **Entrenamiento:** 1.14M papers de Semantic Scholar
- **Especialización:** Comprensión de texto científico
- **Acceso:** HuggingFace gratis
- **Uso:** Embeddings científicos, clasificación

#### 4. **PubMedGPT (Stanford)** 💊
- **Repositorio:** `stanford-crfm/pubmedgpt`
- **Tamaño:** 2.7B parámetros
- **Entrenamiento:** Abstracts de PubMed
- **Especialización:** Literatura médica
- **Acceso:** HuggingFace gratis

#### 5. **ScholarBERT (Custom)** 📖
- **Repositorio:** Varios fine-tunes de BERT en ArXiv
- **Especialización:** Física, matemáticas
- **Acceso:** HuggingFace gratis

---

## 🆓 APIs Gratuitas de Modelos LLM

### **1. HuggingFace Inference API** ⭐⭐⭐⭐⭐
```python
# GRATIS (con rate limits razonables)
API_URL = "https://api-inference.huggingface.co/models/{model_id}"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

# Modelos científicos disponibles:
- facebook/galactica-120b
- microsoft/biogpt
- allenai/scibert_scivocab_uncased
- EleutherAI/gpt-neox-20b
```

**Límites Gratuitos:**
- ~1000 requests/día
- Rate limit: ~10 req/min
- Timeout: 60s/request

### **2. Together AI** ⭐⭐⭐⭐
```python
# $25 GRATIS al registrarse
API_URL = "https://api.together.xyz/inference"

# Modelos científicos:
- meta-llama/Llama-3-70b-chat
- mistralai/Mixtral-8x7B-Instruct-v0.1
- NousResearch/Nous-Hermes-2-Mixtral-8x7B
```

**Límites:**
- $25 crédito gratis
- ~200K tokens gratis
- Rate limit: 600 req/min

### **3. Replicate** ⭐⭐⭐
```python
# GRATIS (límites generosos)
API_URL = "https://api.replicate.com/v1/predictions"

# Modelos disponibles:
- meta/llama-2-70b-chat
- stability-ai/stable-diffusion (para visualizaciones)
```

**Límites:**
- $0.006/1K tokens
- Crédito inicial gratis

### **4. Groq** ⭐⭐⭐⭐⭐
```python
# GRATIS (muy rápido)
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Modelos:
- llama3-70b-8192
- mixtral-8x7b-32768
```

**Límites:**
- GRATIS para uso moderado
- Extremadamente rápido (LPU acceleration)
- Rate limit: 30 req/min

### **5. Perplexity AI (pplx-api)** ⭐⭐⭐
```python
# $5 GRATIS al registrarse
API_URL = "https://api.perplexity.ai/chat/completions"

# Modelos con búsqueda web integrada:
- pplx-70b-online
- pplx-7b-chat
```

---

## 📋 Datasets para Fine-tuning

### **Papers Científicos**

1. **ArXiv Dataset** (2M+ papers)
   - Fuente: https://www.kaggle.com/Cornell-University/arxiv
   - Formato: JSON con abstract, texto completo
   - Categorías: cs, math, physics, q-bio

2. **PubMed Central Open Access** (3M+ papers)
   - Fuente: https://www.ncbi.nlm.nih.gov/pmc/tools/openftlist/
   - Formato: XML, PDF
   - Especialización: Biomedicina

3. **Semantic Scholar Open Research Corpus** (200M+ papers)
   - Fuente: https://www.semanticscholar.org/product/api
   - API: GRATIS
   - Metadata: Citations, abstracts, full-text

4. **OpenAlex** (240M+ papers)
   - Fuente: https://openalex.org
   - API: GRATIS
   - Sucesor de Microsoft Academic Graph

---

## 🚀 Propuesta de Mejora: Sistema Híbrido Multi-Modelo

### **Arquitectura Propuesta**

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

### **Estrategia de Uso**

#### **Fase 1: Generación Paralela**
- Enviar prompt a 3-5 modelos diferentes
- Usar modelos especializados por dominio
- Timeout: 30s por modelo

#### **Fase 2: Consensus Voting**
- Comparar hipótesis generadas
- Detectar patrones comunes
- Identificar insights únicos

#### **Fase 3: Refinamiento**
- Usar mejor modelo para refinar
- Agregar referencias de literatura
- Validar testabilidad

---

## 🛠️ Plan de Implementación

### **Sprint 1: Multi-Provider Integration (2 días)**
- [ ] Crear `MultiModelHypothesisService`
- [ ] Integrar HuggingFace Inference API
- [ ] Integrar Groq API
- [ ] Integrar Together AI
- [ ] Sistema de fallback robusto

### **Sprint 2: Domain-Specific Models (2 días)**
- [ ] Integrar BioGPT para biología
- [ ] Integrar Galactica para física/matemáticas
- [ ] Crear adaptadores por dominio
- [ ] Benchmark de calidad

### **Sprint 3: Consensus System (1 día)**
- [ ] Implementar voting mechanism
- [ ] Detección de contradicciones
- [ ] Scoring de confianza
- [ ] Agregación de insights

### **Sprint 4: Integration con Autonomous Loops (1 día)**
- [ ] Actualizar `MathematicsLoop` con nuevo servicio
- [ ] Actualizar `BiologyLoop`
- [ ] Actualizar `ChemistryLoop`
- [ ] Tests end-to-end

### **Sprint 5: Fine-tuning Pipeline (3 días)**
- [ ] Descargar datasets (ArXiv, PubMed)
- [ ] Preprocesar papers
- [ ] Fine-tune modelo base (LoRA)
- [ ] Evaluar mejora vs. modelos base

---

## 📊 Benchmark de Modelos

### **Criterios de Evaluación**
1. **Novedad Científica** (0-1)
2. **Testabilidad** (0-1)
3. **Fundamentación Teórica** (0-1)
4. **Especificidad** (0-1)
5. **Viabilidad Experimental** (0-1)

### **Test Cases por Dominio**

#### **Matemáticas:**
- "Encontrar nuevas conjeturas sobre primos"
- "Generalizar el último teorema de Fermat"

#### **Biología:**
- "Mejorar eficiencia de CRISPR"
- "Predecir estructura de proteínas desordenadas"

#### **Química:**
- "Diseñar catalizadores para CO2"
- "Sintetizar superconductores a temperatura ambiente"

---

## 💰 Análisis de Costos

### **Modelo Gratuito (HuggingFace + Groq)**
- Costo: $0/mes
- Límite: ~30K hipótesis/mes
- Latencia: 2-5s

### **Modelo Híbrido (Ollama local + APIs gratuitas)**
- Costo: $0/mes
- Límite: ilimitado (local) + 30K/mes (cloud)
- Latencia: 1-3s

### **Modelo Premium (con Together AI + Replicate)**
- Costo: ~$50/mes
- Límite: ~500K hipótesis/mes
- Latencia: 0.5-2s

---

## 🎯 Recomendaciones Finales

### **Para Empezar Inmediatamente:**
1. ✅ **Groq API** - Más rápido y gratis
2. ✅ **HuggingFace** - Modelos científicos especializados
3. ✅ **Ollama local** - Deepseek-R1 para razonamiento

### **Para Calidad Máxima:**
1. 🌟 **Galactica** via HuggingFace - Mejor para física/matemáticas
2. 🌟 **BioGPT** - Mejor para biología/medicina
3. 🌟 **Deepseek-R1** - Mejor razonamiento general

### **Para Escalabilidad:**
1. 🚀 Fine-tune de Llama-3-70B con papers de ArXiv
2. 🚀 LoRA adapters por dominio científico
3. 🚀 Knowledge distillation a modelos pequeños

---

## 📝 Próximos Pasos

1. **Implementar `MultiModelHypothesisService`**
2. **Crear sistema de benchmark automático**
3. **Integrar con loops autónomos existentes**
4. **Evaluar calidad real de hipótesis generadas**
5. **Preparar pipeline de fine-tuning**

---

**Conclusión:** El proyecto tiene una base sólida autónoma, pero la generación de hipótesis está limitada a heurísticas. Con la integración de múltiples LLMs especializados (especialmente modelos científicos como Galactica y BioGPT) podemos lograr generación de hipótesis de calidad investigativa real, todo usando APIs gratuitas y modelos open source.
