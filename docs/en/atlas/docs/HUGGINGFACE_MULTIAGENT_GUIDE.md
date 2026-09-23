> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="-guía-sistema-multi-agente-con-hugging-face-cloud"></a>
# 🤖 Guide: Multi-Agent System with Hugging Face Cloud

Complete guide to using specialized Hugging Face models in the AXIOM Atlas multi-agent system.

---

<a id="-tabla-de-contenidos"></a>
## 📋 Table of Contents

1. [Introduction](#introducción)
2. [Initial Setup](#configuración-inicial)
3. [Available Models](#modelos-disponibles)
4. [Basic Usage](#uso-básico)
5. [Multi-Agent Workflow](#workflow-multi-agente)
6. [API Reference](#api-reference)
7. [Best Practices](#mejores-prácticas)
8. [Troubleshooting](#troubleshooting)

---

<a id="-introducción"></a>
## 🎯 Introduction

<a id="qué-es-esto"></a>
### What is this?

This integration allows using Hugging Face cloud models instead of local models (Ollama) for the AXIOM Atlas multi-agent system.

<a id="-beneficios"></a>
### ✨ Benefits

- **Larger and more specialized models**: up to 405B parameters vs 8B local
- **Specialized scientific knowledge**: Models trained with scientific papers
- **No hardware requirements**: Everything in the cloud
- **Free for public models**: No API key needed
- **Automatic fallback**: If HF fails, use local Ollama

<a id="-modelos-destacados"></a>
### 🚀 Featured Models

| Model | Specialization | Parameters |
|--------|----------------|------------|
| `deepseek-ai/DeepSeek-V3` | MoE 671B (37B active) for reasoning and planning | 671B (37B active) |
| `Qwen/Qwen2.5-72B-Instruct` | Biomedical hypotheses, 128K context | 72B |
| `Qwen/Qwen2.5-Math-72B-Instruct` | Advanced mathematics and theoretical physics | 72B |
| `Qwen/Qwen2.5-Coder-32B-Instruct` | Scientific code and laboratory automation | 32B |
| `meta-llama/Meta-Llama-3.1-405B-Instruct` | Editorial-quality scientific synthesis | 405B |

---

<a id="-configuración-inicial"></a>
## ⚙️ Initial Setup

<a id="1-instalar-dependencias"></a>
### 1. Install Dependencies

```bash
<a id="activar-entorno-virtual"></a>
# Activar entorno virtual
source venv-new/bin/activate

<a id="instalar-httpx-requerido"></a>
# Instalar httpx (requerido)
pip install httpx
```

<a id="2-configurar-api-key-opcional"></a>
### 2. Configure API Key (Optional)

For public models you don't need an API key, but for better performance and no rate limits:

```bash
<a id="obtener-api-key-en-httpshuggingfacecosettingstokens"></a>
# Obtener API key en: https://huggingface.co/settings/tokens
export HUGGINGFACE_API_KEY=hf_...

<a id="o-agregar-al-env"></a>
# O agregar al .env
echo "HUGGINGFACE_API_KEY=hf_..." >> .env
```

<a id="3-verificar-instalación"></a>
### 3. Verify Installation

```bash
<a id="test-de-conexión"></a>
# Test de conexión
curl -X POST http://localhost:8000/api/huggingface/test-connection

<a id="o-usar-python"></a>
# O usar Python
python examples/huggingface_multiagent_demo.py
```

---

<a id="-modelos-disponibles"></a>
## 🔬 Available Models

<a id="por-rol-de-agente"></a>
### By Agent Role

| Role | Assigned Model | Description |
|-----|----------------|-------------|
| **orchestrator** | `deepseek-ai/DeepSeek-V3` | Planner with multi-token deliberation |
| **bio_hypothesis** | `Qwen/Qwen2.5-72B-Instruct` | High-precision biomedical hypotheses |
| **physchem_coder** | `Qwen/Qwen2.5-Coder-32B-Instruct` | Experimental design and scientific code |
| **reviewer** | `deepseek-ai/DeepSeek-V3` | Critical review with reflective reasoning |
| **publisher** | `meta-llama/Meta-Llama-3.1-405B-Instruct` | Premium scientific writing and synthesis |
| **scientific_reasoner** | `Qwen/Qwen2.5-Math-72B-Instruct` | Mathematical proofs and theoretical physics |

<a id="por-dominio-científico"></a>
### By Scientific Domain

| Domain | Main Model | Fallback |
|---------|-----------------|----------|
| **Biology** | `Qwen/Qwen2.5-72B-Instruct` | `meta-llama/Meta-Llama-3.1-70B-Instruct` |
| **Chemistry** | `deepseek-ai/DeepSeek-V3` | `Qwen/Qwen2.5-Math-32B-Instruct` |
| **Physics** | `deepseek-ai/DeepSeek-V3` | `Qwen/Qwen2.5-Math-72B-Instruct` |
| **Mathematics** | `Qwen/Qwen2.5-Math-72B-Instruct` | `deepseek-ai/DeepSeek-V3` |
| **Medicine** | `Qwen/Qwen2.5-72B-Instruct` | `meta-llama/Meta-Llama-3.1-70B-Instruct` |
| **General** | `meta-llama/Meta-Llama-3.1-405B-Instruct` | `deepseek-ai/DeepSeek-V3` |
| **Code** | `Qwen/Qwen2.5-Coder-32B-Instruct` | `DeepSeek-R1-Distill-Qwen-32B` |

---

<a id="-uso-básico"></a>
## 💻 Basic Usage

<a id="generación-simple"></a>
### Simple Generation

```python
from app.services.huggingface_agent_wrapper import HuggingFaceAgentWrapper

<a id="crear-wrapper-para-agente"></a>
# Crear wrapper para agente
bio_agent = HuggingFaceAgentWrapper(
    agent_role="bio_hypothesis",
    domain="biology"
)

<a id="generar-hipótesis"></a>
# Generar hipótesis
hypothesis = await bio_agent.generate_async(
    prompt="Generate a hypothesis about CRISPR gene editing efficiency",
    max_new_tokens=800,
    temperature=0.65
)

print(hypothesis)
```

<a id="usando-factory-function"></a>
### Using Factory Function

```python
from app.services.huggingface_agent_wrapper import create_agent_wrapper

<a id="crear-agente-de-forma-simplificada"></a>
# Crear agente de forma simplificada
orchestrator = create_agent_wrapper(
    agent_role="orchestrator",
    provider="huggingface"
)

plan = await orchestrator.generate_async(
    prompt="Create a research plan for quantum computing applications",
    max_new_tokens=512,
    temperature=0.3
)
```

<a id="sistema-híbrido-hf--ollama-fallback"></a>
### Hybrid System (HF + Ollama Fallback)

```python
from app.services.huggingface_agent_wrapper import HybridAgentWrapper

<a id="crear-agente-híbrido"></a>
# Crear agente híbrido
hybrid_agent = HybridAgentWrapper(
    agent_role="reviewer",
    hf_model_id="meta-llama/Meta-Llama-3.1-405B-Instruct",
    ollama_model="llama3:8b",
    prefer_cloud=True  # Intentar HF primero, Ollama si falla
)

review = hybrid_agent.generate(
    prompt="Review this hypothesis critically...",
    max_new_tokens=480
)
```

---

<a id="-workflow-multi-agente"></a>
## 🔄 Multi-Agent Workflow

<a id="ejemplo-completo-investigación-científica"></a>
### Complete Example: Scientific Research

```python
import asyncio
from app.services.huggingface_agent_wrapper import create_agent_wrapper

async def scientific_research_workflow(research_goal: str):
    """Workflow completo de investigación científica"""

    # 1. ORCHESTRATOR: Planificación
    orchestrator = create_agent_wrapper("orchestrator", "huggingface")
    plan = await orchestrator.generate_async(
        f"Create a research plan for: {research_goal}",
        max_new_tokens=512,
        temperature=0.3
    )
    print(f"📋 Plan: {plan}\n")

    # 2. BIO HYPOTHESIS: Generación de hipótesis
    bio_hyp = create_agent_wrapper("bio_hypothesis", "huggingface", domain="biology")
    hypothesis = await bio_hyp.generate_async(
        f"Generate a testable hypothesis for: {research_goal}",
        max_new_tokens=640,
        temperature=0.65
    )
    print(f"🧬 Hipótesis: {hypothesis}\n")

    # 3. PHYSCHEM CODER: Diseño experimental
    coder = create_agent_wrapper("physchem_coder", "huggingface")
    design = await coder.generate_async(
        f"Design experimental pipeline for hypothesis: {hypothesis[:300]}",
        max_new_tokens=700,
        temperature=0.4
    )
    print(f"🔬 Diseño: {design}\n")

    # 4. REVIEWER: Revisión crítica
    reviewer = create_agent_wrapper("reviewer", "huggingface")
    review = await reviewer.generate_async(
        f"Critically review this hypothesis and plan:\nHypothesis: {hypothesis[:300]}\nPlan: {design[:300]}",
        max_new_tokens=480,
        temperature=0.35
    )
    print(f"✅ Revisión: {review}\n")

    # 5. PUBLISHER: Reporte final
    publisher = create_agent_wrapper("publisher", "huggingface")
    report = await publisher.generate_async(
        f"Write scientific report:\nGoal: {research_goal}\nHypothesis: {hypothesis[:200]}\nReview: {review[:200]}",
        max_new_tokens=700,
        temperature=0.65
    )
    print(f"📄 Reporte: {report}\n")

    return {
        "plan": plan,
        "hypothesis": hypothesis,
        "design": design,
        "review": review,
        "report": report
    }

<a id="ejecutar"></a>
# Ejecutar
research_goal = "Investigate CRISPR efficiency in hematopoietic stem cells"
results = asyncio.run(scientific_research_workflow(research_goal))
```

---

<a id="-api-reference"></a>
## 🌐 API Reference

<a id="endpoints-http"></a>
### HTTP Endpoints

<a id="post-apihuggingfacegenerate"></a>
#### POST `/api/huggingface/generate`
Generation with specific model

```bash
curl -X POST http://localhost:8000/api/huggingface/generate \
    -H "Content-Type: application/json" \
    -d '{
        "model_id": "Qwen/Qwen2.5-72B-Instruct",
        "prompt": "Generate a hypothesis about protein folding",
        "max_new_tokens": 512,
        "temperature": 0.7
    }'
```

<a id="post-apihuggingfacegenerate-for-agent"></a>
#### POST `/api/huggingface/generate-for-agent`
Role-optimized generation

```bash
curl -X POST http://localhost:8000/api/huggingface/generate-for-agent \
  -H "Content-Type: application/json" \
  -d '{
    "agent_role": "bio_hypothesis",
    "prompt": "Generate hypothesis about immunotherapy",
    "domain": "medicine",
    "max_new_tokens": 800,
    "temperature": 0.65
  }'
```

<a id="get-apihuggingfacemodels"></a>
#### GET `/api/huggingface/models`
List all available models

```bash
curl http://localhost:8000/api/huggingface/models
```

<a id="get-apihuggingfacemodelsby-agentrole"></a>
#### GET `/api/huggingface/models/by-agent/{role}`
Recommended model by role

```bash
curl http://localhost:8000/api/huggingface/models/by-agent/bio_hypothesis
```

<a id="get-apihuggingfacemetrics"></a>
#### GET `/api/huggingface/metrics`
Usage metrics

```bash
curl http://localhost:8000/api/huggingface/metrics
```

<a id="python-api"></a>
### Python API

<a id="huggingfaceprovider"></a>
#### HuggingFaceProvider

```python
from app.services.llm_providers.huggingface_provider import huggingface_provider, HFInferenceRequest

<a id="generar-texto"></a>
# Generar texto
request = HFInferenceRequest(
    model_id="Qwen/Qwen2.5-72B-Instruct",
    prompt="Your prompt here",
    max_new_tokens=512,
    temperature=0.7
)

response = await huggingface_provider.generate_text(request)
print(response.generated_text)

<a id="obtener-métricas"></a>
# Obtener métricas
metrics = huggingface_provider.get_metrics()
print(f"Success rate: {metrics['success_rate']}%")
```

<a id="huggingfaceagentwrapper"></a>
#### HuggingFaceAgentWrapper

```python
from app.services.huggingface_agent_wrapper import HuggingFaceAgentWrapper

<a id="crear-wrapper"></a>
# Crear wrapper
wrapper = HuggingFaceAgentWrapper(
    agent_role="orchestrator",
    model_id="deepseek-ai/DeepSeek-V3"  # opcional override
)

<a id="generar-async"></a>
# Generar (async)
result = await wrapper.generate_async(
    prompt="Your prompt",
    max_new_tokens=512,
    temperature=0.7
)

<a id="generar-sync"></a>
# Generar (sync)
result = wrapper.generate(
    prompt="Your prompt",
    max_new_tokens=512
)
```

---

<a id="-mejores-prácticas"></a>
## 🎯 Best Practices

<a id="1-selección-de-temperatura"></a>
### 1. Temperature Selection

```python
<a id="tareas-creativas-hipótesis-ideas"></a>
# Tareas creativas (hipótesis, ideas)
temperature = 0.65 - 0.85

<a id="tareas-analíticas-código-revisión"></a>
# Tareas analíticas (código, revisión)
temperature = 0.3 - 0.5

<a id="tareas-balanceadas-planificación-síntesis"></a>
# Tareas balanceadas (planificación, síntesis)
temperature = 0.5 - 0.7
```

<a id="2-optimización-de-tokens"></a>
### 2. Token Optimization

```python
<a id="hipótesis-compleja"></a>
# Hipótesis compleja
max_new_tokens = 800

<a id="código-o-diseño-experimental"></a>
# Código o diseño experimental
max_new_tokens = 700

<a id="planificación"></a>
# Planificación
max_new_tokens = 512

<a id="revisión-crítica"></a>
# Revisión crítica
max_new_tokens = 480
```

<a id="3-uso-de-caché"></a>
### 3. Using Cache

```python
<a id="el-caché-está-habilitado-por-defecto"></a>
# El caché está habilitado por defecto
<a id="limpiar-caché-manualmente-si-necesitas-forzar-regeneración"></a>
# Limpiar caché manualmente si necesitas forzar regeneración
huggingface_provider.clear_cache()

<a id="o-vía-api"></a>
# O vía API
curl -X POST http://localhost:8000/api/huggingface/clear-cache
```

<a id="4-manejo-de-errores"></a>
### 4. Error Handling

```python
try:
    result = await agent.generate_async(prompt)

    if result.startswith("[ERROR"):
        # Manejar error
        logger.error(f"Generation failed: {result}")
    else:
        # Procesar resultado exitoso
        process_result(result)

except Exception as e:
    logger.exception(f"Unexpected error: {e}")
```

<a id="5-rate-limiting"></a>
### 5. Rate Limiting

The service handles rate limiting automatically, but you can adjust it:

```python
from app.services.llm_providers.huggingface_provider import HuggingFaceProvider

<a id="crear-provider-custom"></a>
# Crear provider custom
provider = HuggingFaceProvider(
    max_requests_per_minute=30  # Reducir si tienes límites
)
```

---

<a id="-troubleshooting"></a>
## 🐛 Troubleshooting

<a id="problema-rate-limit-exceeded"></a>
### Problem: "Rate limit exceeded"

**Solution:**
```python
<a id="reducir-tasa-de-requests"></a>
# Reducir tasa de requests
provider.max_requests_per_minute = 20

<a id="o-esperar-antes-de-siguiente-request"></a>
# O esperar antes de siguiente request
import time
time.sleep(2)
```

<a id="problema-model-loading-timeout"></a>
### Problem: "Model loading timeout"

**Solution:**
```bash
<a id="aumentar-timeout"></a>
# Aumentar timeout
provider = HuggingFaceProvider(timeout=120)

<a id="o-usar-modelo-más-pequeño"></a>
# O usar modelo más pequeño
model_id = "gpt2"  # Modelo ligero para pruebas
```

<a id="problema-api-key-invalid"></a>
### Problem: "API key invalid"

**Solution:**
```bash
<a id="verificar-api-key"></a>
# Verificar API key
echo $HUGGINGFACE_API_KEY

<a id="obtener-nueva-key-en-httpshuggingfacecosettingstokens"></a>
# Obtener nueva key en: https://huggingface.co/settings/tokens

<a id="para-modelos-públicos-api-key-es-opcional"></a>
# Para modelos públicos, API key es opcional
<a id="simplemente-no-configurarla"></a>
# Simplemente no configurarla
```

<a id="problema-httpx-not-available"></a>
### Problem: "HTTPX not available"

**Solution:**
```bash
pip install httpx

<a id="verificar-instalación"></a>
# Verificar instalación
python -c "import httpx; print(httpx.__version__)"
```

<a id="problema-async-loop-already-running"></a>
### Problem: "Async loop already running"

**Solution:**
```python
<a id="usar-generate-síncrono-en-lugar-de-generate_async"></a>
# Usar generate() síncrono en lugar de generate_async()
result = wrapper.generate(prompt)

<a id="o-usar-nest_asyncio"></a>
# O usar nest_asyncio
import nest_asyncio
nest_asyncio.apply()
```

---

<a id="-comparación-hf-vs-ollama"></a>
## 📊 HF vs Ollama Comparison

| Feature | Hugging Face Cloud | Ollama Local |
|---------------|-------------------|--------------|
| **Model size** | Up to 70B+ | Up to 13B typically |
| **Specialization** | Scientific models (BioGPT, Galactica) | General models |
| **Requirements** | Internet, optional API key | Local GPU, RAM |
| **Latency** | Variable (network) | Low (local) |
| **Cost** | Free (public models) | Local hardware |
| **Scalability** | Unlimited | Limited by hardware |
| **Offline** | ❌ | ✅ |

---

<a id="-próximos-pasos"></a>
## 🚀 Next Steps

1. **Run demo:**
   ```bash
   python examples/huggingface_multiagent_demo.py
   ```

2. **Run tests:**
   ```bash
   pytest tests/integration/test_huggingface_multiagent.py -v
   ```

3. **Explore API:**
   ```bash
   # Start server
   uvicorn main_refactored:app --reload

   # Open docs
   open http://localhost:8000/docs
   ```

4. **Customize models:**
   - Edit `app/services/llm_providers/huggingface_provider.py`
   - Update `AGENT_MODEL_MAP` or `SPECIALIZED_MODELS`

---

<a id="-recursos-adicionales"></a>
## 📚 Additional Resources

- [Hugging Face Inference API Docs](https://huggingface.co/docs/api-inference/index)
- [Scientific Models on HF](https://huggingface.co/models?pipeline_tag=text-generation&sort=downloads)
- AXIOM Atlas Multi-Agent Docs (`docs/MULTI_AGENT.md`; resource not included)
- Advanced Configuration (`config/agents_enhanced.yaml`; resource not included)

---

<a id="-checklist-de-integración"></a>
## ✅ Integration Checklist

- [ ] Installed `httpx`
- [ ] Configured `HUGGINGFACE_API_KEY` (optional)
- [ ] Run connection test
- [ ] Tested basic generation
- [ ] Run multi-agent workflow
- [ ] Reviewed usage metrics
- [ ] Configured fallback to Ollama
- [ ] Run integration tests

---

**Ready to use specialized cloud models in your scientific research! 🚀🔬**
