> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="guía-cómo-usar-modelos-científicos-especializados"></a>
# Guide: How to Use Specialized Scientific Models

<a id="-situación-actual"></a>
## 📊 Current Situation

Specialized scientific models like **BioGPT-Large** and **Galactica** are NOT available in HuggingFace's **free Serverless Inference API**.

<a id="modelos-no-disponibles-en-api-gratuita"></a>
### Models NOT Available in Free API:
- ❌ `microsoft/BioGPT-Large` - Specialized in biomedicine
- ❌ `facebook/galactica-30b` - Specialized in general science
- ❌ `facebook/galactica-6.7b` - General science (small version)
- ❌ `mistralai/Mathstral-7B-v0.1` - Specialized mathematics
- ❌ `deepseek-ai/deepseek-coder-33b-instruct` - Advanced code
- ❌ `Qwen/Qwen2.5-Math-72B-Instruct` - Advanced mathematics

<a id="por-qué-no-están-disponibles"></a>
### Why Are They Not Available?

1. **Too large**: Models with 30B+ parameters require powerful GPUs
2. **No provider**: No Inference API provider has deployed them
3. **Restrictive licenses**: Some have non-commercial licenses (CC BY-NC)
4. **Costs**: HuggingFace cannot offer them for free due to computational cost

---

<a id="-3-opciones-para-usar-modelos-especializados"></a>
## 🔧 3 Options to Use Specialized Models

<a id="opción-1-dedicated-inference-endpoints-recomendado-para-producción"></a>
### **Option 1: Dedicated Inference Endpoints** (Recommended for Production)

<a id="qué-es"></a>
#### What is it?
HuggingFace offers **Dedicated Inference Endpoints**: dedicated servers where you can deploy ANY model from the Hub.

<a id="ventajas"></a>
#### Advantages:
- ✅ **Any model**: BioGPT, Galactica, etc.
- ✅ **Managed infrastructure**: HuggingFace handles everything (Kubernetes, CUDA, etc.)
- ✅ **Autoscaling**: Scales automatically based on demand
- ✅ **Scale-to-zero**: You don't pay when you're not using it
- ✅ **Compatible API**: Same API we already use
- ✅ **Multiple GPUs**: From T4 to A100

<a id="desventajas"></a>
#### Disadvantages:
- 💰 **Cost**: Requires payment (from $0.60/hour for T4 GPU)
- 💳 **Card**: You need to add a credit card

<a id="costos-aproximados"></a>
#### Approximate Costs:

| GPU | Price/Hour | Example Model | GPU RAM |
|-----|-------------|----------------|---------|
| **CPU** | $0.032/hr | Small models | - |
| **NVIDIA T4** | $0.60/hr | BioGPT-Large, Galactica-6.7b | 16 GB |
| **NVIDIA A10G** | $1.30/hr | Galactica-30b | 24 GB |
| **NVIDIA A100** | $4.50/hr | 70B+ models | 40 GB |

**Cost Example:**
- BioGPT-Large on T4 GPU: ~$0.60/hour
- If you use it 100 hours/month: $60/month
- With scale-to-zero (only when used): it can be $10-20/month

<a id="cómo-configurar"></a>
#### How to Configure:

1. **Go to HuggingFace Inference Endpoints:**
   ```
   https://huggingface.co/inference-endpoints/dedicated
   ```

2. **Create Endpoint:**
   - Click "Create Endpoint"
   - Select model: `microsoft/BioGPT-Large`
   - Select GPU: T4 (enough for BioGPT-Large)
   - Configure autoscaling
   - Enable scale-to-zero

3. **Get Endpoint URL:**
   ```
   https://xxxxx.us-east-1.aws.endpoints.huggingface.cloud
   ```

4. **Update the Code:**
   ```python
   # In app/services/llm_providers/huggingface_provider.py

   # To use dedicated endpoint:
   DEDICATED_ENDPOINTS = {
       "bio_hypothesis": {
           "url": "https://xxxxx.aws.endpoints.huggingface.cloud",
           "model": "microsoft/BioGPT-Large"
       }
   }
   ```

---

<a id="opción-2-deployment-local-gratis-pero-requiere-hardware"></a>
### **Option 2: Local Deployment** (Free but Requires Hardware)

<a id="qué-es-1"></a>
#### What is it?
Download and run the models on your own computer or server.

<a id="ventajas-1"></a>
#### Advantages:
- ✅ **Free**: You don't pay HuggingFace
- ✅ **Total control**: Your data doesn't leave your infrastructure
- ✅ **No rate limits**: Use as much as you want
- ✅ **Offline**: You don't need internet once downloaded

<a id="desventajas-1"></a>
#### Disadvantages:
- ❌ **Requires powerful GPU**: Minimum 16GB VRAM for large models
- ❌ **Complex setup**: You need to configure CUDA, PyTorch, etc.
- ❌ **Maintenance**: You manage updates and debugging

<a id="requisitos-de-hardware"></a>
#### Hardware Requirements:

| Model | Minimum GPU RAM | Recommended GPU | Disk Space |
|--------|----------------|-----------------|---------------|
| BioGPT-Large | 6 GB | RTX 3060 (12GB) | 2 GB |
| Galactica-6.7b | 14 GB | RTX 3090 (24GB) | 14 GB |
| Galactica-30b | 60 GB | A100 (80GB) | 60 GB |

<a id="cómo-configurar-1"></a>
#### How to Configure:

1. **Install Dependencies:**
   ```bash
   pip install transformers accelerate bitsandbytes torch
   ```

2. **Download and Run Model:**
   ```python
   from transformers import AutoTokenizer, AutoModelForCausalLM

   # Load BioGPT-Large
   tokenizer = AutoTokenizer.from_pretrained("microsoft/BioGPT-Large")
   model = AutoModelForCausalLM.from_pretrained(
       "microsoft/BioGPT-Large",
       device_map="auto",  # Automatically distributes across GPUs
       load_in_8bit=True   # Quantization to save memory
   )

   # Generate text
   inputs = tokenizer("Generate a hypothesis about cell division:", return_tensors="pt")
   outputs = model.generate(**inputs, max_new_tokens=100)
   text = tokenizer.decode(outputs[0])
   ```

3. **Create Local API with FastAPI:**
   ```python
   # local_biogpt_server.py
   from fastapi import FastAPI
   from pydantic import BaseModel

   app = FastAPI()

   # Load model on startup
   model = AutoModelForCausalLM.from_pretrained("microsoft/BioGPT-Large")
   tokenizer = AutoTokenizer.from_pretrained("microsoft/BioGPT-Large")

   class GenerateRequest(BaseModel):
       prompt: str
       max_tokens: int = 100

   @app.post("/generate")
   def generate(request: GenerateRequest):
       inputs = tokenizer(request.prompt, return_tensors="pt")
       outputs = model.generate(**inputs, max_new_tokens=request.max_tokens)
       return {"text": tokenizer.decode(outputs[0])}

   # Run: uvicorn local_biogpt_server:app --port 8001
   ```

4. **Update AXIOM ATLAS to use local server:**
   ```python
   # In HuggingFaceProvider, add:
   LOCAL_ENDPOINTS = {
       "bio_hypothesis": "http://localhost:8001/generate"
   }
   ```

---

<a id="opción-3-usar-ollama-gratis-y-más-fácil"></a>
### **Option 3: Use Ollama** (Free and Easier)

<a id="qué-es-2"></a>
#### What is it?
Ollama allows you to run large models locally in a VERY simple way.

<a id="ventajas-2"></a>
#### Advantages:
- ✅ **Super easy**: A single command to download and run
- ✅ **Free**: All local
- ✅ **Compatible API**: OpenAI-compatible API
- ✅ **Optimized**: Automatic quantization

<a id="desventajas-2"></a>
#### Disadvantages:
- ❌ **Limited models**: It doesn't have BioGPT or Galactica in its official catalog
- ❌ **Requires GPU**: Minimum 8GB VRAM

<a id="modelos-científicos-en-ollama"></a>
#### Scientific Models in Ollama:

Although it doesn't have BioGPT, it has excellent scientific models:

```bash
<a id="modelos-disponibles-en-ollama"></a>
# Modelos disponibles en Ollama
ollama pull llama3.1:70b      # Modelo general muy potente
ollama pull qwen2.5:72b       # Excelente para matemáticas
ollama pull codellama:34b     # Código científico
ollama pull deepseek-coder    # Alternativa a Qwen Coder
```

<a id="tu-proyecto-ya-tiene-soporte-para-ollama"></a>
#### Your project ALREADY has support for Ollama:
- See: `app/services/ollama_service.py`
- See: `app/services/huggingface_agent_wrapper.py` (HybridAgentWrapper)

---

<a id="-recomendación-por-caso-de-uso"></a>
## 🎯 Recommendation by Use Case

<a id="para-desarrollotesting"></a>
### For Development/Testing:
✅ **Use models available in Serverless API** (current)
- Llama-3.1-70B for biology/medicine (very capable)
- Qwen2.5-Math-7B for mathematics
- Qwen2.5-Coder-32B for code

<a id="para-producción-con-presupuesto"></a>
### For Production with Budget:
✅ **HuggingFace Dedicated Endpoints**
- BioGPT-Large on T4 GPU (~$20-40/month with scale-to-zero)
- Galactica-6.7b on T4 GPU (~$30-50/month)
- Total control, managed infrastructure

<a id="para-producción-sin-presupuesto-pero-con-gpu"></a>
### For Production without Budget but with GPU:
✅ **Local Deployment**
- Server with dedicated GPU
- BioGPT-Large + Galactica locally
- Cost: $0/month (only electricity + hardware)

<a id="para-prototipado-rápido"></a>
### For Rapid Prototyping:
✅ **Ollama Local**
- Easy to configure
- Good scientific models (Llama, Qwen)
- Already integrated into the project

---

<a id="-plan-de-acción-sugerido"></a>
## 📝 Suggested Action Plan

<a id="fase-1-actual-gratis-"></a>
### Phase 1: Current (Free) ✅
```yaml
Estatus: IMPLEMENTADO
Modelos: Llama-3.1-70B, Qwen2.5-Coder-32B, Mixtral-8x22B
Costo: $0/mes (free tier de HuggingFace)
Calidad: Excelente (70B-176B parámetros)
```

<a id="fase-2-agregar-ollama-local-gratis"></a>
### Phase 2: Add Ollama Local (Free)
```yaml
Estatus: CÓDIGO YA EXISTE
Acción: Instalar Ollama + configurar modelos
Modelos: llama3.1:70b, qwen2.5:72b, codellama:34b
Costo: $0/mes
Requiere: GPU con 16GB+ VRAM
```

<a id="fase-3-dedicated-endpoints-cuando-necesites-biogpt"></a>
### Phase 3: Dedicated Endpoints (When you need BioGPT)
```yaml
Estatus: PENDIENTE
Acción: Crear endpoint para BioGPT-Large
Costo: ~$30/mes (con scale-to-zero)
Requiere: Tarjeta de crédito
Beneficio: Modelo especializado en biomedicina
```

<a id="fase-4-local-deployment-para-control-total"></a>
### Phase 4: Local Deployment (For total control)
```yaml
Estatus: FUTURO
Acción: Servidor con GPUs para modelos grandes
Costo: Hardware inicial + electricidad
Beneficio: Control total, datos privados, sin límites
```

---

<a id="-comparación-de-opciones"></a>
## 🔍 Comparison of Options

| Feature | Serverless API | Dedicated Endpoint | Local | Ollama |
|----------------|----------------|-------------------|-------|--------|
| **Cost** | Free* | $0.60-4.50/hr | Hardware | Free |
| **Setup** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **BioGPT** | ❌ | ✅ | ✅ | ❌ |
| **Galactica** | ❌ | ✅ | ✅ | ❌ |
| **Llama-70B** | ✅ | ✅ | ✅** | ✅ |
| **Privacy** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Scalability** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **Maintenance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |

*Free with rate limits
**Requires powerful GPU

---

<a id="-conclusión"></a>
## 💡 Conclusion

**For most AXIOM ATLAS use cases, the current configuration is EXCELLENT:**

1. **Llama-3.1-70B** is a very capable model and can handle biology/medicine tasks
2. **Qwen2.5-Math-7B** is specialized in mathematics and physics
3. **Qwen2.5-Coder-32B** is excellent for scientific code
4. **Mixtral-8x22B** is one of the largest models available for free

**You only need specialized models (BioGPT, Galactica) if:**
- You need VERY specific biomedical vocabulary
- You work with very technical scientific jargon
- You need exact citations and references from papers

**Recommendation:** Start with the current configuration (free, powerful, works). If you encounter specific limitations, then consider Dedicated Endpoints for specialized models.

---

<a id="-referencias"></a>
## 📚 References

- [HuggingFace Dedicated Endpoints](https://huggingface.co/inference-endpoints/dedicated)
- [BioGPT Model Card](https://huggingface.co/microsoft/BioGPT-Large)
- [Galactica Model Card](https://huggingface.co/facebook/galactica-30b)
- [Ollama](https://ollama.ai/)
- [Pricing Calculator](https://huggingface.co/pricing#inference-endpoints)
