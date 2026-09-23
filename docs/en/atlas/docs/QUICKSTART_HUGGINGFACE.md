> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="-quick-start-modelos-hugging-face-cloud-en-sistema-multi-agente"></a>
# 🚀 Quick Start: Hugging Face Cloud Models in Multi-Agent System

**Use specialized 70B parameter models without a local GPU!**

---

<a id="-inicio-rápido-5-minutos"></a>
## ⚡ Quick Start (5 minutes)

<a id="1-instalar-dependencia"></a>
### 1. Install Dependency

```bash
<a id="activar-entorno-virtual"></a>
# Activar entorno virtual
source venv-new/bin/activate

<a id="instalar-httpx-requerido"></a>
# Instalar httpx (requerido)
pip install httpx
```

<a id="2-opcional-configurar-api-key"></a>
### 2. (Optional) Configure API Key

```bash
<a id="obtener-en-httpshuggingfacecosettingstokens"></a>
# Obtener en: https://huggingface.co/settings/tokens
export HUGGINGFACE_API_KEY=hf_...

<a id="o-agregar-al-env"></a>
# O agregar al .env
echo "HUGGINGFACE_API_KEY=hf_..." >> .env
```

> **Note:** API key is optional. Public models work without it, but with rate limits.

<a id="3-iniciar-servidor"></a>
### 3. Start Server

```bash
uvicorn main_refactored:app --reload
```

<a id="4-probar-integración"></a>
### 4. Test Integration

```bash
<a id="test-de-conexión"></a>
# Test de conexión
curl -X POST http://localhost:8000/api/huggingface/test-connection
```

---

<a id="-ejemplo-básico"></a>
## 🎯 Basic Example

<a id="python-async"></a>
### Python (Async)

```python
import asyncio
from app.services.huggingface_agent_wrapper import create_agent_wrapper

async def main():
    # Crear agente de hipótesis biológicas
    bio_agent = create_agent_wrapper(
        agent_role="bio_hypothesis",
        provider="huggingface",
        domain="biology"
    )

    # Generar hipótesis
    hypothesis = await bio_agent.generate_async(
        prompt="Generate a hypothesis about CRISPR gene editing efficiency in stem cells",
        max_new_tokens=800,
        temperature=0.65
    )

    print(f"Hipótesis generada:\n{hypothesis}")

asyncio.run(main())
```

<a id="http-request"></a>
### HTTP Request

```bash
curl -X POST http://localhost:8000/api/huggingface/generate-for-agent \
  -H "Content-Type: application/json" \
  -d '{
    "agent_role": "bio_hypothesis",
    "prompt": "Generate a hypothesis about protein folding mechanisms",
    "domain": "biology",
    "max_new_tokens": 800,
    "temperature": 0.65
  }'
```

---

<a id="-modelos-por-rol-de-agente"></a>
## 🤖 Models by Agent Role

| Role | Model | Specialization |
|-----|--------|----------------|
| **orchestrator** | Meta-Llama-3.1-70B | Strategic planning |
| **bio_hypothesis** | microsoft/biogpt | Biological hypotheses (15M PubMed papers) |
| **physchem_coder** | Qwen2.5-Coder-32B | Scientific code |
| **reviewer** | Meta-Llama-3.1-70B | Critical review |
| **publisher** | Mixtral-8x7B | Scientific reports |
| **scientific_reasoner** | facebook/galactica-30b | Scientific reasoning (48M papers) |

---

<a id="-workflow-multi-agente-completo"></a>
## 🔄 Complete Multi-Agent Workflow

```python
import asyncio
from app.services.huggingface_agent_wrapper import create_agent_wrapper

async def research_workflow():
    research_goal = "Investigate CRISPR efficiency in hematopoietic stem cells"

    # 1. Planificación
    orchestrator = create_agent_wrapper("orchestrator", "huggingface")
    plan = await orchestrator.generate_async(
        f"Create research plan for: {research_goal}",
        max_new_tokens=512
    )

    # 2. Hipótesis
    bio_hyp = create_agent_wrapper("bio_hypothesis", "huggingface", domain="biology")
    hypothesis = await bio_hyp.generate_async(
        f"Generate testable hypothesis for: {research_goal}",
        max_new_tokens=640
    )

    # 3. Diseño Experimental
    coder = create_agent_wrapper("physchem_coder", "huggingface")
    design = await coder.generate_async(
        f"Design computational pipeline for: {hypothesis[:300]}",
        max_new_tokens=700
    )

    # 4. Revisión
    reviewer = create_agent_wrapper("reviewer", "huggingface")
    review = await reviewer.generate_async(
        f"Review hypothesis and plan: {hypothesis[:200]} | {design[:200]}",
        max_new_tokens=480
    )

    # 5. Reporte
    publisher = create_agent_wrapper("publisher", "huggingface")
    report = await publisher.generate_async(
        f"Write report: {hypothesis[:200]} | {review[:200]}",
        max_new_tokens=700
    )

    return {
        "plan": plan,
        "hypothesis": hypothesis,
        "design": design,
        "review": review,
        "report": report
    }

<a id="ejecutar"></a>
# Ejecutar
results = asyncio.run(research_workflow())
print(results)
```

---

<a id="-sistema-híbrido-cloud--local"></a>
## 🔀 Hybrid System (Cloud + Local)

```python
from app.services.huggingface_agent_wrapper import HybridAgentWrapper

<a id="intenta-hugging-face-primero-fallback-a-ollama-si-falla"></a>
# Intenta Hugging Face primero, fallback a Ollama si falla
hybrid_agent = HybridAgentWrapper(
    agent_role="reviewer",
    hf_model_id="meta-llama/Meta-Llama-3.1-70B-Instruct",
    ollama_model="qwen:7b",
    prefer_cloud=True  # Preferir cloud
)

review = hybrid_agent.generate(
    prompt="Review this hypothesis critically...",
    max_new_tokens=480
)
```

---

<a id="-endpoints-api"></a>
## 📊 API Endpoints

<a id="generar-con-modelo-específico"></a>
### Generate with Specific Model
```bash
POST /api/huggingface/generate
```

<a id="generar-por-rol-de-agente"></a>
### Generate by Agent Role
```bash
POST /api/huggingface/generate-for-agent
```

<a id="listar-modelos"></a>
### List Models
```bash
GET /api/huggingface/models
GET /api/huggingface/models/by-agent/{role}
GET /api/huggingface/models/by-domain/{domain}
```

<a id="métricas"></a>
### Metrics
```bash
GET /api/huggingface/metrics
GET /api/huggingface/status
```

<a id="utilidades"></a>
### Utilities
```bash
POST /api/huggingface/clear-cache
POST /api/huggingface/test-connection
```

---

<a id="-ejecutar-demo-completo"></a>
## 🧪 Run Full Demo

```bash
<a id="demo-con-todos-los-ejemplos"></a>
# Demo con todos los ejemplos
python examples/huggingface_multiagent_demo.py

<a id="tests-de-integración"></a>
# Tests de integración
pytest tests/integration/test_huggingface_multiagent.py -v
```

---

<a id="-personalización"></a>
## 🎨 Customization

<a id="cambiar-modelo-por-rol"></a>
### Change Model by Role

```python
from app.services.llm_providers.huggingface_provider import huggingface_provider

<a id="editar-mapa-de-modelos"></a>
# Editar mapa de modelos
huggingface_provider.AGENT_MODEL_MAP["bio_hypothesis"] = "tu-modelo-custom"
```

<a id="ajustar-parámetros"></a>
### Adjust Parameters

```python
agent = create_agent_wrapper("orchestrator", "huggingface")

result = await agent.generate_async(
    prompt="...",
    max_new_tokens=1024,    # Más tokens
    temperature=0.5         # Menos creativo
)
```

---

<a id="-troubleshooting-rápido"></a>
## 🐛 Quick Troubleshooting

<a id="error-httpx-not-found"></a>
### Error: httpx not found
```bash
pip install httpx
```

<a id="error-rate-limit-exceeded"></a>
### Error: Rate limit exceeded
```bash
<a id="esperar-1-minuto-o-configurar-api-key"></a>
# Esperar 1 minuto o configurar API key
export HUGGINGFACE_API_KEY=hf_...
```

<a id="error-model-loading-timeout"></a>
### Error: Model loading timeout
```bash
<a id="usar-modelo-más-ligero"></a>
# Usar modelo más ligero
model_id = "gpt2"  # Para pruebas
```

---

<a id="-recursos"></a>
## 📚 Resources

- **Complete Guide:** docs/HUGGINGFACE_MULTIAGENT_GUIDE.md (`docs/HUGGINGFACE_MULTIAGENT_GUIDE.md`; resource not included)
- **Configuration:** config/agents_enhanced.yaml (`config/agents_enhanced.yaml`; resource not included)
- **Examples:** examples/huggingface_multiagent_demo.py (`examples/huggingface_multiagent_demo.py`; resource not included)
- **Tests:** tests/integration/test_huggingface_multiagent.py (`tests/integration/test_huggingface_multiagent.py`; resource not included)

---

<a id="-checklist"></a>
## ✅ Checklist

- [ ] Installed `httpx`
- [ ] API key configured (optional)
- [ ] Server started
- [ ] Connection test successful
- [ ] Basic example tested
- [ ] Multi-agent workflow executed

---

<a id="-ventajas-vs-ollama-local"></a>
## 🎯 Advantages vs Local Ollama

| Feature | Hugging Face Cloud | Local Ollama |
|---------------|-------------------|--------------|
| **Model size** | Up to 70B+ ✅ | Up to 13B |
| **Specialization** | Scientific models ✅ | General |
| **No GPU** | ✅ | ❌ Requires GPU |
| **Free** | ✅ (public) | ✅ |
| **Offline** | ❌ | ✅ |

---

**Ready to use! 🚀**

```bash
<a id="comando-único-para-empezar"></a>
# Comando único para empezar
uvicorn main_refactored:app --reload && \
  open http://localhost:8000/docs#/Hugging%20Face
```

