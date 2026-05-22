# Guía: Cómo Usar Modelos Científicos Especializados

## 📊 Situación Actual

Los modelos científicos especializados como **BioGPT-Large** y **Galactica** NO están disponibles en la **Serverless Inference API gratuita** de HuggingFace.

### Modelos NO Disponibles en API Gratuita:
- ❌ `microsoft/BioGPT-Large` - Especializado en biomedicina
- ❌ `facebook/galactica-30b` - Especializado en ciencia general
- ❌ `facebook/galactica-6.7b` - Ciencia general (versión pequeña)
- ❌ `mistralai/Mathstral-7B-v0.1` - Matemáticas especializadas
- ❌ `deepseek-ai/deepseek-coder-33b-instruct` - Código avanzado
- ❌ `Qwen/Qwen2.5-Math-72B-Instruct` - Matemáticas avanzadas

### ¿Por Qué No Están Disponibles?

1. **Demasiado grandes**: Modelos de 30B+ parámetros requieren GPUs potentes
2. **Sin provider**: Ningún proveedor de la Inference API los ha desplegado
3. **Licencias restrictivas**: Algunos tienen licencias no-comerciales (CC BY-NC)
4. **Costos**: HuggingFace no puede ofrecerlos gratis por el costo computacional

---

## 🔧 3 Opciones para Usar Modelos Especializados

### **Opción 1: Dedicated Inference Endpoints** (Recomendado para Producción)

#### ¿Qué es?
HuggingFace ofrece **Dedicated Inference Endpoints**: servidores dedicados donde puedes desplegar CUALQUIER modelo del Hub.

#### Ventajas:
- ✅ **Cualquier modelo**: BioGPT, Galactica, etc.
- ✅ **Infraestructura manejada**: HuggingFace maneja todo (Kubernetes, CUDA, etc.)
- ✅ **Autoscaling**: Escala automáticamente según demanda
- ✅ **Scale-to-zero**: No pagas cuando no lo usas
- ✅ **API compatible**: Misma API que ya usamos
- ✅ **Múltiples GPUs**: Desde T4 hasta A100

#### Desventajas:
- 💰 **Costo**: Requiere pago (desde $0.60/hora para GPU T4)
- 💳 **Tarjeta**: Necesitas agregar tarjeta de crédito

#### Costos Aproximados:

| GPU | Precio/Hora | Modelo Ejemplo | RAM GPU |
|-----|-------------|----------------|---------|
| **CPU** | $0.032/hr | Modelos pequeños | - |
| **NVIDIA T4** | $0.60/hr | BioGPT-Large, Galactica-6.7b | 16 GB |
| **NVIDIA A10G** | $1.30/hr | Galactica-30b | 24 GB |
| **NVIDIA A100** | $4.50/hr | Modelos 70B+ | 40 GB |

**Ejemplo de Costo:**
- BioGPT-Large en GPU T4: ~$0.60/hora
- Si lo usas 100 horas/mes: $60/mes
- Con scale-to-zero (solo cuando se usa): puede ser $10-20/mes

#### Cómo Configurar:

1. **Ir a HuggingFace Inference Endpoints:**
   ```
   https://huggingface.co/inference-endpoints/dedicated
   ```

2. **Crear Endpoint:**
   - Click "Create Endpoint"
   - Seleccionar modelo: `microsoft/BioGPT-Large`
   - Seleccionar GPU: T4 (suficiente para BioGPT-Large)
   - Configurar autoscaling
   - Activar scale-to-zero

3. **Obtener URL del Endpoint:**
   ```
   https://xxxxx.us-east-1.aws.endpoints.huggingface.cloud
   ```

4. **Actualizar el Código:**
   ```python
   # En app/services/llm_providers/huggingface_provider.py

   # Para usar endpoint dedicado:
   DEDICATED_ENDPOINTS = {
       "bio_hypothesis": {
           "url": "https://xxxxx.aws.endpoints.huggingface.cloud",
           "model": "microsoft/BioGPT-Large"
       }
   }
   ```

---

### **Opción 2: Deployment Local** (Gratis pero Requiere Hardware)

#### ¿Qué es?
Descargar y ejecutar los modelos en tu propia computadora o servidor.

#### Ventajas:
- ✅ **Gratis**: No pagas a HuggingFace
- ✅ **Control total**: Tus datos no salen de tu infraestructura
- ✅ **Sin límites de rate**: Usas tanto como quieras
- ✅ **Offline**: No necesitas internet una vez descargado

#### Desventajas:
- ❌ **Requiere GPU potente**: Mínimo 16GB VRAM para modelos grandes
- ❌ **Setup complejo**: Necesitas configurar CUDA, PyTorch, etc.
- ❌ **Mantenimiento**: Tú gestionas actualizaciones y debugging

#### Requisitos de Hardware:

| Modelo | RAM GPU Mínima | GPU Recomendada | Espacio Disco |
|--------|----------------|-----------------|---------------|
| BioGPT-Large | 6 GB | RTX 3060 (12GB) | 2 GB |
| Galactica-6.7b | 14 GB | RTX 3090 (24GB) | 14 GB |
| Galactica-30b | 60 GB | A100 (80GB) | 60 GB |

#### Cómo Configurar:

1. **Instalar Dependencias:**
   ```bash
   pip install transformers accelerate bitsandbytes torch
   ```

2. **Descargar y Ejecutar Modelo:**
   ```python
   from transformers import AutoTokenizer, AutoModelForCausalLM

   # Cargar BioGPT-Large
   tokenizer = AutoTokenizer.from_pretrained("microsoft/BioGPT-Large")
   model = AutoModelForCausalLM.from_pretrained(
       "microsoft/BioGPT-Large",
       device_map="auto",  # Distribuye automáticamente en GPUs
       load_in_8bit=True   # Cuantización para ahorrar memoria
   )

   # Generar texto
   inputs = tokenizer("Generate a hypothesis about cell division:", return_tensors="pt")
   outputs = model.generate(**inputs, max_new_tokens=100)
   text = tokenizer.decode(outputs[0])
   ```

3. **Crear API Local con FastAPI:**
   ```python
   # local_biogpt_server.py
   from fastapi import FastAPI
   from pydantic import BaseModel

   app = FastAPI()

   # Cargar modelo al iniciar
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

   # Ejecutar: uvicorn local_biogpt_server:app --port 8001
   ```

4. **Actualizar AXIOM ATLAS para usar servidor local:**
   ```python
   # En HuggingFaceProvider, agregar:
   LOCAL_ENDPOINTS = {
       "bio_hypothesis": "http://localhost:8001/generate"
   }
   ```

---

### **Opción 3: Usar Ollama** (Gratis y Más Fácil)

#### ¿Qué es?
Ollama permite ejecutar modelos grandes localmente de forma MUY sencilla.

#### Ventajas:
- ✅ **Súper fácil**: Un solo comando para descargar y ejecutar
- ✅ **Gratis**: Todo local
- ✅ **API compatible**: OpenAI-compatible API
- ✅ **Optimizado**: Cuantización automática

#### Desventajas:
- ❌ **Modelos limitados**: No tiene BioGPT o Galactica en su catálogo oficial
- ❌ **Requiere GPU**: Mínimo 8GB VRAM

#### Modelos Científicos en Ollama:

Aunque no tiene BioGPT, tiene modelos científicos excelentes:

```bash
# Modelos disponibles en Ollama
ollama pull llama3.1:70b      # Modelo general muy potente
ollama pull qwen2.5:72b       # Excelente para matemáticas
ollama pull codellama:34b     # Código científico
ollama pull deepseek-coder    # Alternativa a Qwen Coder
```

#### Tu proyecto YA tiene soporte para Ollama:
- Ver: `app/services/ollama_service.py`
- Ver: `app/services/huggingface_agent_wrapper.py` (HybridAgentWrapper)

---

## 🎯 Recomendación por Caso de Uso

### Para Desarrollo/Testing:
✅ **Usa modelos disponibles en Serverless API** (actual)
- Llama-3.1-70B para biología/medicina (muy capaz)
- Qwen2.5-Math-7B para matemáticas
- Qwen2.5-Coder-32B para código

### Para Producción con Presupuesto:
✅ **HuggingFace Dedicated Endpoints**
- BioGPT-Large en GPU T4 (~$20-40/mes con scale-to-zero)
- Galactica-6.7b en GPU T4 (~$30-50/mes)
- Control total, infraestructura manejada

### Para Producción sin Presupuesto pero con GPU:
✅ **Deployment Local**
- Servidor con GPU dedicada
- BioGPT-Large + Galactica localmente
- Costo: $0/mes (solo electricidad + hardware)

### Para Prototipado Rápido:
✅ **Ollama Local**
- Fácil de configurar
- Modelos científicos buenos (Llama, Qwen)
- Ya integrado en el proyecto

---

## 📝 Plan de Acción Sugerido

### Fase 1: Actual (Gratis) ✅
```yaml
Estatus: IMPLEMENTADO
Modelos: Llama-3.1-70B, Qwen2.5-Coder-32B, Mixtral-8x22B
Costo: $0/mes (free tier de HuggingFace)
Calidad: Excelente (70B-176B parámetros)
```

### Fase 2: Agregar Ollama Local (Gratis)
```yaml
Estatus: CÓDIGO YA EXISTE
Acción: Instalar Ollama + configurar modelos
Modelos: llama3.1:70b, qwen2.5:72b, codellama:34b
Costo: $0/mes
Requiere: GPU con 16GB+ VRAM
```

### Fase 3: Dedicated Endpoints (Cuando necesites BioGPT)
```yaml
Estatus: PENDIENTE
Acción: Crear endpoint para BioGPT-Large
Costo: ~$30/mes (con scale-to-zero)
Requiere: Tarjeta de crédito
Beneficio: Modelo especializado en biomedicina
```

### Fase 4: Local Deployment (Para control total)
```yaml
Estatus: FUTURO
Acción: Servidor con GPUs para modelos grandes
Costo: Hardware inicial + electricidad
Beneficio: Control total, datos privados, sin límites
```

---

## 🔍 Comparación de Opciones

| Característica | Serverless API | Dedicated Endpoint | Local | Ollama |
|----------------|----------------|-------------------|-------|--------|
| **Costo** | Gratis* | $0.60-4.50/hr | Hardware | Gratis |
| **Setup** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **BioGPT** | ❌ | ✅ | ✅ | ❌ |
| **Galactica** | ❌ | ✅ | ✅ | ❌ |
| **Llama-70B** | ✅ | ✅ | ✅** | ✅ |
| **Privacidad** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Escalabilidad** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **Mantenimiento** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |

*Gratis con límites de rate
**Requiere GPU potente

---

## 💡 Conclusión

**Para la mayoría de casos de AXIOM ATLAS, la configuración actual es EXCELENTE:**

1. **Llama-3.1-70B** es un modelo muy capaz y puede manejar tareas de biología/medicina
2. **Qwen2.5-Math-7B** es especializado en matemáticas y física
3. **Qwen2.5-Coder-32B** es excelente para código científico
4. **Mixtral-8x22B** es uno de los modelos más grandes disponibles gratis

**Solo necesitas modelos especializados (BioGPT, Galactica) si:**
- Necesitas vocabulario biomédico MUY específico
- Trabajas con jerga científica muy técnica
- Necesitas citas y referencias exactas de papers

**Recomendación:** Empieza con la configuración actual (gratis, potente, funciona). Si encuentras limitaciones específicas, entonces considera Dedicated Endpoints para modelos especializados.

---

## 📚 Referencias

- [HuggingFace Dedicated Endpoints](https://huggingface.co/inference-endpoints/dedicated)
- [BioGPT Model Card](https://huggingface.co/microsoft/BioGPT-Large)
- [Galactica Model Card](https://huggingface.co/facebook/galactica-30b)
- [Ollama](https://ollama.ai/)
- [Pricing Calculator](https://huggingface.co/pricing#inference-endpoints)
