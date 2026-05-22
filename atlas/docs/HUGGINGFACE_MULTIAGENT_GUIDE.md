# 🤖 Guía: Sistema Multi-Agente con Hugging Face Cloud

Guía completa para usar modelos especializados de Hugging Face en el sistema multi-agente de AXIOM Atlas.

---

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Configuración Inicial](#configuración-inicial)
3. [Modelos Disponibles](#modelos-disponibles)
4. [Uso Básico](#uso-básico)
5. [Workflow Multi-Agente](#workflow-multi-agente)
6. [API Reference](#api-reference)
7. [Mejores Prácticas](#mejores-prácticas)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Introducción

### ¿Qué es esto?

Esta integración permite usar modelos cloud de Hugging Face en lugar de modelos locales (Ollama) para el sistema multi-agente de AXIOM Atlas.

### ✨ Beneficios

- **Modelos más grandes y especializados**: hasta 405B parámetros vs 8B locales
- **Conocimiento científico especializado**: Modelos entrenados con papers científicos
- **Sin requisitos de hardware**: Todo en la nube
- **Gratis para modelos públicos**: Sin API key necesaria
- **Fallback automático**: Si falla HF, usa Ollama local

### 🚀 Modelos Destacados

| Modelo | Especialización | Parámetros |
|--------|----------------|------------|
| `deepseek-ai/DeepSeek-V3` | MoE 671B (37B activos) para razonamiento y planificación | 671B (37B activos) |
| `Qwen/Qwen2.5-72B-Instruct` | Hipótesis biomédicas, contexto 128K | 72B |
| `Qwen/Qwen2.5-Math-72B-Instruct` | Matemáticas avanzadas y física teórica | 72B |
| `Qwen/Qwen2.5-Coder-32B-Instruct` | Código científico y automatización de laboratorio | 32B |
| `meta-llama/Meta-Llama-3.1-405B-Instruct` | Síntesis científica de calidad editorial | 405B |

---

## ⚙️ Configuración Inicial

### 1. Instalar Dependencias

```bash
# Activar entorno virtual
source venv-new/bin/activate

# Instalar httpx (requerido)
pip install httpx
```

### 2. Configurar API Key (Opcional)

Para modelos públicos no necesitas API key, pero para mejor rendimiento y sin límites de tasa:

```bash
# Obtener API key en: https://huggingface.co/settings/tokens
export HUGGINGFACE_API_KEY=hf_...

# O agregar al .env
echo "HUGGINGFACE_API_KEY=hf_..." >> .env
```

### 3. Verificar Instalación

```bash
# Test de conexión
curl -X POST http://localhost:8000/api/huggingface/test-connection

# O usar Python
python examples/huggingface_multiagent_demo.py
```

---

## 🔬 Modelos Disponibles

### Por Rol de Agente

| Rol | Modelo Asignado | Descripción |
|-----|----------------|-------------|
| **orchestrator** | `deepseek-ai/DeepSeek-V3` | Planner con deliberación multi-token |
| **bio_hypothesis** | `Qwen/Qwen2.5-72B-Instruct` | Hipótesis biomédicas de alta precisión |
| **physchem_coder** | `Qwen/Qwen2.5-Coder-32B-Instruct` | Diseño experimental y código científico |
| **reviewer** | `deepseek-ai/DeepSeek-V3` | Revisión crítica con razonamiento reflexivo |
| **publisher** | `meta-llama/Meta-Llama-3.1-405B-Instruct` | Redacción y síntesis científica premium |
| **scientific_reasoner** | `Qwen/Qwen2.5-Math-72B-Instruct` | Demostraciones matemáticas y física teórica |

### Por Dominio Científico

| Dominio | Modelo Principal | Fallback |
|---------|-----------------|----------|
| **Biology** | `Qwen/Qwen2.5-72B-Instruct` | `meta-llama/Meta-Llama-3.1-70B-Instruct` |
| **Chemistry** | `deepseek-ai/DeepSeek-V3` | `Qwen/Qwen2.5-Math-32B-Instruct` |
| **Physics** | `deepseek-ai/DeepSeek-V3` | `Qwen/Qwen2.5-Math-72B-Instruct` |
| **Mathematics** | `Qwen/Qwen2.5-Math-72B-Instruct` | `deepseek-ai/DeepSeek-V3` |
| **Medicine** | `Qwen/Qwen2.5-72B-Instruct` | `meta-llama/Meta-Llama-3.1-70B-Instruct` |
| **General** | `meta-llama/Meta-Llama-3.1-405B-Instruct` | `deepseek-ai/DeepSeek-V3` |
| **Code** | `Qwen/Qwen2.5-Coder-32B-Instruct` | `DeepSeek-R1-Distill-Qwen-32B` |

---

## 💻 Uso Básico

### Generación Simple

```python
from app.services.huggingface_agent_wrapper import HuggingFaceAgentWrapper

# Crear wrapper para agente
bio_agent = HuggingFaceAgentWrapper(
    agent_role="bio_hypothesis",
    domain="biology"
)

# Generar hipótesis
hypothesis = await bio_agent.generate_async(
    prompt="Generate a hypothesis about CRISPR gene editing efficiency",
    max_new_tokens=800,
    temperature=0.65
)

print(hypothesis)
```

### Usando Factory Function

```python
from app.services.huggingface_agent_wrapper import create_agent_wrapper

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

### Sistema Híbrido (HF + Ollama Fallback)

```python
from app.services.huggingface_agent_wrapper import HybridAgentWrapper

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

## 🔄 Workflow Multi-Agente

### Ejemplo Completo: Investigación Científica

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

# Ejecutar
research_goal = "Investigate CRISPR efficiency in hematopoietic stem cells"
results = asyncio.run(scientific_research_workflow(research_goal))
```

---

## 🌐 API Reference

### Endpoints HTTP

#### POST `/api/huggingface/generate`
Generación con modelo específico

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

#### POST `/api/huggingface/generate-for-agent`
Generación optimizada por rol

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

#### GET `/api/huggingface/models`
Listar todos los modelos disponibles

```bash
curl http://localhost:8000/api/huggingface/models
```

#### GET `/api/huggingface/models/by-agent/{role}`
Modelo recomendado por rol

```bash
curl http://localhost:8000/api/huggingface/models/by-agent/bio_hypothesis
```

#### GET `/api/huggingface/metrics`
Métricas de uso

```bash
curl http://localhost:8000/api/huggingface/metrics
```

### Python API

#### HuggingFaceProvider

```python
from app.services.llm_providers.huggingface_provider import huggingface_provider, HFInferenceRequest

# Generar texto
request = HFInferenceRequest(
    model_id="Qwen/Qwen2.5-72B-Instruct",
    prompt="Your prompt here",
    max_new_tokens=512,
    temperature=0.7
)

response = await huggingface_provider.generate_text(request)
print(response.generated_text)

# Obtener métricas
metrics = huggingface_provider.get_metrics()
print(f"Success rate: {metrics['success_rate']}%")
```

#### HuggingFaceAgentWrapper

```python
from app.services.huggingface_agent_wrapper import HuggingFaceAgentWrapper

# Crear wrapper
wrapper = HuggingFaceAgentWrapper(
    agent_role="orchestrator",
    model_id="deepseek-ai/DeepSeek-V3"  # opcional override
)

# Generar (async)
result = await wrapper.generate_async(
    prompt="Your prompt",
    max_new_tokens=512,
    temperature=0.7
)

# Generar (sync)
result = wrapper.generate(
    prompt="Your prompt",
    max_new_tokens=512
)
```

---

## 🎯 Mejores Prácticas

### 1. Selección de Temperatura

```python
# Tareas creativas (hipótesis, ideas)
temperature = 0.65 - 0.85

# Tareas analíticas (código, revisión)
temperature = 0.3 - 0.5

# Tareas balanceadas (planificación, síntesis)
temperature = 0.5 - 0.7
```

### 2. Optimización de Tokens

```python
# Hipótesis compleja
max_new_tokens = 800

# Código o diseño experimental
max_new_tokens = 700

# Planificación
max_new_tokens = 512

# Revisión crítica
max_new_tokens = 480
```

### 3. Uso de Caché

```python
# El caché está habilitado por defecto
# Limpiar caché manualmente si necesitas forzar regeneración
huggingface_provider.clear_cache()

# O vía API
curl -X POST http://localhost:8000/api/huggingface/clear-cache
```

### 4. Manejo de Errores

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

### 5. Rate Limiting

El servicio maneja rate limiting automáticamente, pero puedes ajustarlo:

```python
from app.services.llm_providers.huggingface_provider import HuggingFaceProvider

# Crear provider custom
provider = HuggingFaceProvider(
    max_requests_per_minute=30  # Reducir si tienes límites
)
```

---

## 🐛 Troubleshooting

### Problema: "Rate limit exceeded"

**Solución:**
```python
# Reducir tasa de requests
provider.max_requests_per_minute = 20

# O esperar antes de siguiente request
import time
time.sleep(2)
```

### Problema: "Model loading timeout"

**Solución:**
```bash
# Aumentar timeout
provider = HuggingFaceProvider(timeout=120)

# O usar modelo más pequeño
model_id = "gpt2"  # Modelo ligero para pruebas
```

### Problema: "API key invalid"

**Solución:**
```bash
# Verificar API key
echo $HUGGINGFACE_API_KEY

# Obtener nueva key en: https://huggingface.co/settings/tokens

# Para modelos públicos, API key es opcional
# Simplemente no configurarla
```

### Problema: "HTTPX not available"

**Solución:**
```bash
pip install httpx

# Verificar instalación
python -c "import httpx; print(httpx.__version__)"
```

### Problema: "Async loop already running"

**Solución:**
```python
# Usar generate() síncrono en lugar de generate_async()
result = wrapper.generate(prompt)

# O usar nest_asyncio
import nest_asyncio
nest_asyncio.apply()
```

---

## 📊 Comparación HF vs Ollama

| Característica | Hugging Face Cloud | Ollama Local |
|---------------|-------------------|--------------|
| **Tamaño de modelos** | Hasta 70B+ | Hasta 13B típicamente |
| **Especialización** | Modelos científicos (BioGPT, Galactica) | Modelos generales |
| **Requisitos** | Internet, API key opcional | GPU local, RAM |
| **Latencia** | Variable (red) | Baja (local) |
| **Costo** | Gratis (modelos públicos) | Hardware local |
| **Escalabilidad** | Ilimitada | Limitada por hardware |
| **Offline** | ❌ | ✅ |

---

## 🚀 Próximos Pasos

1. **Ejecutar demo:**
   ```bash
   python examples/huggingface_multiagent_demo.py
   ```

2. **Ejecutar tests:**
   ```bash
   pytest tests/integration/test_huggingface_multiagent.py -v
   ```

3. **Explorar API:**
   ```bash
   # Iniciar servidor
   uvicorn main_refactored:app --reload

   # Abrir docs
   open http://localhost:8000/docs
   ```

4. **Personalizar modelos:**
   - Editar `app/services/llm_providers/huggingface_provider.py`
   - Actualizar `AGENT_MODEL_MAP` o `SPECIALIZED_MODELS`

---

## 📚 Recursos Adicionales

- [Hugging Face Inference API Docs](https://huggingface.co/docs/api-inference/index)
- [Modelos Científicos en HF](https://huggingface.co/models?pipeline_tag=text-generation&sort=downloads)
- [AXIOM Atlas Multi-Agent Docs](docs/MULTI_AGENT.md)
- [Configuración Avanzada](config/agents_enhanced.yaml)

---

## ✅ Checklist de Integración

- [ ] Instalado `httpx`
- [ ] Configurado `HUGGINGFACE_API_KEY` (opcional)
- [ ] Ejecutado test de conexión
- [ ] Probado generación básica
- [ ] Ejecutado workflow multi-agente
- [ ] Revisado métricas de uso
- [ ] Configurado fallback a Ollama
- [ ] Ejecutado tests de integración

---

**¡Listo para usar modelos cloud especializados en tu investigación científica! 🚀🔬**
