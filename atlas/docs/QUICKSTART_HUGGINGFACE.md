# 🚀 Quick Start: Modelos Hugging Face Cloud en Sistema Multi-Agente

**¡Usa modelos especializados de 70B parámetros sin GPU local!**

---

## ⚡ Inicio Rápido (5 minutos)

### 1. Instalar Dependencia

```bash
# Activar entorno virtual
source venv-new/bin/activate

# Instalar httpx (requerido)
pip install httpx
```

### 2. (Opcional) Configurar API Key

```bash
# Obtener en: https://huggingface.co/settings/tokens
export HUGGINGFACE_API_KEY=hf_...

# O agregar al .env
echo "HUGGINGFACE_API_KEY=hf_..." >> .env
```

> **Nota:** API key es opcional. Modelos públicos funcionan sin ella, pero con límites de tasa.

### 3. Iniciar Servidor

```bash
uvicorn main_refactored:app --reload
```

### 4. Probar Integración

```bash
# Test de conexión
curl -X POST http://localhost:8000/api/huggingface/test-connection
```

---

## 🎯 Ejemplo Básico

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

## 🤖 Modelos por Rol de Agente

| Rol | Modelo | Especialización |
|-----|--------|----------------|
| **orchestrator** | Meta-Llama-3.1-70B | Planificación estratégica |
| **bio_hypothesis** | microsoft/biogpt | Hipótesis biológicas (15M papers PubMed) |
| **physchem_coder** | Qwen2.5-Coder-32B | Código científico |
| **reviewer** | Meta-Llama-3.1-70B | Revisión crítica |
| **publisher** | Mixtral-8x7B | Reportes científicos |
| **scientific_reasoner** | facebook/galactica-30b | Razonamiento científico (48M papers) |

---

## 🔄 Workflow Multi-Agente Completo

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

# Ejecutar
results = asyncio.run(research_workflow())
print(results)
```

---

## 🔀 Sistema Híbrido (Cloud + Local)

```python
from app.services.huggingface_agent_wrapper import HybridAgentWrapper

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

## 📊 Endpoints API

### Generar con Modelo Específico
```bash
POST /api/huggingface/generate
```

### Generar por Rol de Agente
```bash
POST /api/huggingface/generate-for-agent
```

### Listar Modelos
```bash
GET /api/huggingface/models
GET /api/huggingface/models/by-agent/{role}
GET /api/huggingface/models/by-domain/{domain}
```

### Métricas
```bash
GET /api/huggingface/metrics
GET /api/huggingface/status
```

### Utilidades
```bash
POST /api/huggingface/clear-cache
POST /api/huggingface/test-connection
```

---

## 🧪 Ejecutar Demo Completo

```bash
# Demo con todos los ejemplos
python examples/huggingface_multiagent_demo.py

# Tests de integración
pytest tests/integration/test_huggingface_multiagent.py -v
```

---

## 🎨 Personalización

### Cambiar Modelo por Rol

```python
from app.services.llm_providers.huggingface_provider import huggingface_provider

# Editar mapa de modelos
huggingface_provider.AGENT_MODEL_MAP["bio_hypothesis"] = "tu-modelo-custom"
```

### Ajustar Parámetros

```python
agent = create_agent_wrapper("orchestrator", "huggingface")

result = await agent.generate_async(
    prompt="...",
    max_new_tokens=1024,    # Más tokens
    temperature=0.5         # Menos creativo
)
```

---

## 🐛 Troubleshooting Rápido

### Error: httpx not found
```bash
pip install httpx
```

### Error: Rate limit exceeded
```bash
# Esperar 1 minuto o configurar API key
export HUGGINGFACE_API_KEY=hf_...
```

### Error: Model loading timeout
```bash
# Usar modelo más ligero
model_id = "gpt2"  # Para pruebas
```

---

## 📚 Recursos

- **Guía Completa:** [docs/HUGGINGFACE_MULTIAGENT_GUIDE.md](docs/HUGGINGFACE_MULTIAGENT_GUIDE.md)
- **Configuración:** [config/agents_enhanced.yaml](config/agents_enhanced.yaml)
- **Ejemplos:** [examples/huggingface_multiagent_demo.py](examples/huggingface_multiagent_demo.py)
- **Tests:** [tests/integration/test_huggingface_multiagent.py](tests/integration/test_huggingface_multiagent.py)

---

## ✅ Checklist

- [ ] Instalado `httpx`
- [ ] API key configurada (opcional)
- [ ] Servidor iniciado
- [ ] Test de conexión exitoso
- [ ] Probado ejemplo básico
- [ ] Ejecutado workflow multi-agente

---

## 🎯 Ventajas vs Ollama Local

| Característica | Hugging Face Cloud | Ollama Local |
|---------------|-------------------|--------------|
| **Tamaño modelos** | Hasta 70B+ ✅ | Hasta 13B |
| **Especialización** | Modelos científicos ✅ | Generales |
| **Sin GPU** | ✅ | ❌ Requiere GPU |
| **Gratis** | ✅ (públicos) | ✅ |
| **Offline** | ❌ | ✅ |

---

**¡Listo para usar! 🚀**

```bash
# Comando único para empezar
uvicorn main_refactored:app --reload && \
  open http://localhost:8000/docs#/Hugging%20Face
```
