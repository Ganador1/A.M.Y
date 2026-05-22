# Guía de Integración: Sistema Multi-Modelo con Loops Autónomos

**Fecha:** 2 de octubre de 2025  
**Versión:** 1.0  
**Estado:** Lista para Implementación

---

## 📋 Resumen Ejecutivo

Esta guía documenta cómo integrar el nuevo **MultiModelHypothesisService** con los loops autónomos existentes (MathematicsLoop, BiologyLoop, ChemistryLoop, etc.) para mejorar dramáticamente la calidad de generación de hipótesis científicas.

### **Mejoras Clave:**
- ✅ **Multi-modelo:** Usa 3-5 modelos en paralelo
- ✅ **Consensus voting:** Valida hipótesis entre modelos
- ✅ **Modelos especializados:** BioGPT, Galactica, etc.
- ✅ **APIs gratuitas:** HuggingFace, Groq, Together AI
- ✅ **Fallback robusto:** Nunca falla completamente

---

## 🏗️ Arquitectura de Integración

### **Flujo Actual (Baseline)**

```
┌─────────────────────┐
│  MathematicsLoop    │
├─────────────────────┤
│ 1. Seed conjectures │
│ 2. Priority scoring │
│ 3. [HEURISTIC       │  ← Mutaciones básicas de texto
│     mutations]      │
│ 4. Validation       │
└─────────────────────┘
```

### **Flujo Mejorado (Multi-Modelo)**

```
┌─────────────────────────────────────────────┐
│          MathematicsLoop Enhanced           │
├─────────────────────────────────────────────┤
│ 1. Seed conjectures                         │
│ 2. Priority scoring                         │
│ 3. [MULTI-MODEL GENERATION] ←─┐            │
│    ├─ Ollama (deepseek-r1)    │            │
│    ├─ Groq (llama3-70b)       │ Parallel   │
│    ├─ HuggingFace (Galactica) │            │
│    └─ Consensus voting         │            │
│ 4. Quality validation                       │
│ 5. Literature grounding                     │
└─────────────────────────────────────────────┘
```

---

## 🔧 Integración Paso a Paso

### **Paso 1: Importar el Servicio**

```python
# En app/autonomous/pipelines/mathematics_loop.py

from app.services.multi_model_hypothesis_service import (
    multi_model_service,
    HypothesisRequest,
    ModelTier,
)
```

### **Paso 2: Reemplazar HypothesisMutator**

**Antes (Heurístico):**
```python
from app.autonomous.generators.hypothesis_mutator import HypothesisMutator

class MathematicsLoop:
    def __init__(self):
        self.mutator = HypothesisMutator()
        # ...
    
    def _run_iteration(self):
        # ...
        mutations = self.mutator.mutate_batch(allocated, max_mutations=5)
```

**Después (Multi-Modelo):**
```python
from app.services.multi_model_hypothesis_service import multi_model_service

class MathematicsLoop:
    def __init__(self):
        # No necesitas mutator, usarás multi_model_service directamente
        # ...
    
    async def _run_iteration(self):
        # ...
        # Generar hipótesis de alta calidad para los top candidatos
        enhanced_hypotheses = await self._generate_enhanced_hypotheses(allocated[:3])
```

### **Paso 3: Implementar Generación Mejorada**

```python
async def _generate_enhanced_hypotheses(
    self,
    candidates: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Generar hipótesis de alta calidad usando multi-modelo"""
    
    enhanced = []
    
    for candidate in candidates:
        conjecture = candidate["conjecture"]
        
        # Crear request para multi-modelo
        request = HypothesisRequest(
            research_question=conjecture.statement,
            domain=conjecture.domain or self.domain,
            context={
                "importance": candidate.get("importance"),
                "novelty": candidate.get("novelty"),
                "literature_frequency": candidate.get("literature_frequency"),
                "mathematical_area": conjecture.domain,
            },
            model_preference=None,  # Auto-selección
        )
        
        try:
            # Generar con consensus voting
            final_hypothesis, consensus = await multi_model_service.generate_hypothesis_with_consensus(
                request=request,
                num_models=3,  # Usar 3 modelos en paralelo
                tier=ModelTier.BALANCED,  # Balance calidad/velocidad
            )
            
            # Enriquecer el candidato con la hipótesis generada
            enriched = {
                **candidate,
                "generated_hypothesis": {
                    "text": final_hypothesis.hypothesis_text,
                    "reasoning": final_hypothesis.reasoning,
                    "confidence": consensus.confidence_score,
                    "predictions": final_hypothesis.testable_predictions,
                    "methodology": final_hypothesis.methodology_suggestions,
                    "literature": final_hypothesis.related_literature,
                },
                "consensus_metrics": {
                    "supporting_models": consensus.supporting_models,
                    "common_predictions": consensus.common_predictions,
                    "unique_insights": consensus.unique_insights,
                    "quality_score": consensus.quality_metrics.get("consensus_score", 0.0),
                },
            }
            
            enhanced.append(enriched)
            
            logger.info(
                f"Generated enhanced hypothesis for {conjecture.id} "
                f"(confidence: {consensus.confidence_score:.2f}, "
                f"models: {len(consensus.supporting_models)})"
            )
            
        except Exception as e:
            logger.warning(
                f"Multi-model generation failed for {conjecture.id}: {e}. "
                "Falling back to basic candidate."
            )
            enhanced.append(candidate)
    
    return enhanced
```

### **Paso 4: Actualizar Métricas de Telemetría**

```python
# En la iteración, registrar métricas del multi-modelo
if enriched_candidates:
    avg_multi_model_confidence = sum(
        c.get("generated_hypothesis", {}).get("confidence", 0)
        for c in enriched_candidates
    ) / len(enriched_candidates)
    
    avg_consensus_score = sum(
        c.get("consensus_metrics", {}).get("quality_score", 0)
        for c in enriched_candidates
    ) / len(enriched_candidates)
    
    self.telemetry.record_iteration(
        domain="mathematics",
        duration_s=duration,
        selected=len(allocated),
        mutations=len(enriched_candidates),  # Ahora son hipótesis generadas
        sketches=len(sketches),
        custom_metrics={
            "multi_model_confidence": avg_multi_model_confidence,
            "consensus_quality": avg_consensus_score,
        },
    )
```

---

## 📊 Ejemplo de Integración Completa

### **MathematicsLoop Mejorado**

```python
"""Mathematics autonomous exploration loop with multi-model hypothesis generation."""
from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Optional

from app.autonomous.core.budget_allocator import BudgetAllocator
from app.autonomous.core.priority_scoring import PriorityScorer
from app.autonomous.core.state_manager import IterationRecord, StateManager
from app.autonomous.core.task_scheduler import TaskScheduler
from app.autonomous.evaluation.novelty_assessor import NoveltyAssessor
from app.autonomous.integration import ToolEvidenceBridge
from app.domains.mathematics.services.mathematical_discovery_engine import (
    MathematicalDiscoveryEngine,
)
from app.services.multi_model_hypothesis_service import (
    multi_model_service,
    HypothesisRequest,
    ModelTier,
)
from app.core.bootstrap_logging import logger


class EnhancedMathematicsLoop:
    """Loop de matemáticas con generación multi-modelo de hipótesis"""
    
    def __init__(
        self,
        state: StateManager | None = None,
        domain: str = "number_theory",
    ):
        self.state = state or StateManager()
        self.scorer = PriorityScorer()
        self.scheduler = TaskScheduler(diversity_quota=5)
        self.budget = BudgetAllocator(total_budget=10.0)
        self.novelty = NoveltyAssessor()
        self.discovery_engine = MathematicalDiscoveryEngine()
        self.tool_evidence = ToolEvidenceBridge(default_domain="mathematics")
        self.domain = domain
        self.iteration = 0
        self._seen_statements: set[str] = set()
    
    async def _generate_enhanced_hypotheses(
        self,
        candidates: List[Dict[str, Any]],
        tier: ModelTier = ModelTier.BALANCED,
    ) -> List[Dict[str, Any]]:
        """Generar hipótesis mejoradas con multi-modelo"""
        
        enhanced = []
        
        for candidate in candidates:
            conjecture = candidate["conjecture"]
            
            request = HypothesisRequest(
                research_question=f"Investigate the following mathematical conjecture: {conjecture.statement}",
                domain=conjecture.domain or self.domain,
                context={
                    "importance": candidate.get("importance"),
                    "novelty": candidate.get("novelty"),
                    "information_gain": candidate.get("information_gain"),
                    "area": self.domain,
                },
            )
            
            try:
                # Generar con consensus
                final_hypothesis, consensus = await multi_model_service.generate_hypothesis_with_consensus(
                    request=request,
                    num_models=3,
                    tier=tier,
                )
                
                enriched = {
                    **candidate,
                    "multi_model_hypothesis": {
                        "text": final_hypothesis.hypothesis_text,
                        "reasoning": final_hypothesis.reasoning,
                        "confidence": consensus.confidence_score,
                        "predictions": final_hypothesis.testable_predictions,
                        "methodology": final_hypothesis.methodology_suggestions,
                        "literature": final_hypothesis.related_literature,
                        "consensus_score": consensus.quality_metrics.get("consensus_score", 0.0),
                        "supporting_models": consensus.supporting_models,
                    },
                }
                
                enhanced.append(enriched)
                
            except Exception as e:
                logger.warning(f"Multi-model failed for {conjecture.id}: {e}")
                enhanced.append(candidate)
        
        return enhanced
    
    async def run_enhanced_iteration(
        self,
        iteration: int,
        limit: int = 5,
        domain: Optional[str] = None,
        use_multi_model: bool = True,
    ) -> Dict[str, Any]:
        """Ejecutar iteración con generación multi-modelo opcional"""
        
        start = time.time()
        self.iteration = iteration
        active_domain = domain or self.domain
        
        # 1. Generar conjeturas semilla
        seed_count = max(limit * 2, 6)
        candidates = self._prepare_candidates(seed_count, active_domain)
        
        # 2. Ranking y scheduling
        ranked = self.scorer.rank(candidates)
        scheduled = self.scheduler.select(ranked, limit=limit)
        allocated = self.budget.allocate(scheduled)
        
        # 3. NUEVO: Generación multi-modelo para top candidatos
        if use_multi_model and allocated:
            top_candidates = allocated[:min(3, len(allocated))]
            
            logger.info(
                f"Generating multi-model hypotheses for top {len(top_candidates)} candidates"
            )
            
            enriched_top = await self._generate_enhanced_hypotheses(
                top_candidates,
                tier=ModelTier.BALANCED,
            )
            
            # Reemplazar top candidates con versiones enriquecidas
            allocated = enriched_top + allocated[len(top_candidates):]
        
        # 4. Evaluación matemática estándar
        # ... (resto del código de evaluación)
        
        # 5. Métricas
        duration = time.time() - start
        
        if use_multi_model:
            avg_mm_confidence = sum(
                c.get("multi_model_hypothesis", {}).get("confidence", 0)
                for c in allocated
                if "multi_model_hypothesis" in c
            ) / max(1, sum(1 for c in allocated if "multi_model_hypothesis" in c))
            
            logger.info(
                f"Multi-model iteration {iteration}: "
                f"avg_confidence={avg_mm_confidence:.2f}, "
                f"duration={duration:.2f}s"
            )
        
        return {
            "success": True,
            "iteration": iteration,
            "duration_s": duration,
            "selected": allocated,
            "multi_model_enabled": use_multi_model,
        }
```

---

## 🧪 Modo de Prueba Comparativo

Para comparar la calidad de hipótesis generadas, implementa un modo de prueba A/B:

```python
async def compare_hypothesis_quality(
    loop: EnhancedMathematicsLoop,
    num_iterations: int = 5,
) -> Dict[str, Any]:
    """Comparar calidad: heurístico vs multi-modelo"""
    
    results = {
        "heuristic": [],
        "multi_model": [],
    }
    
    for i in range(num_iterations):
        # Baseline heurístico
        baseline_result = await loop.run_enhanced_iteration(
            iteration=i * 2,
            limit=5,
            use_multi_model=False,
        )
        results["heuristic"].append(baseline_result)
        
        # Multi-modelo
        enhanced_result = await loop.run_enhanced_iteration(
            iteration=i * 2 + 1,
            limit=5,
            use_multi_model=True,
        )
        results["multi_model"].append(enhanced_result)
    
    # Análisis comparativo
    return {
        "heuristic_avg_time": sum(r["duration_s"] for r in results["heuristic"]) / num_iterations,
        "multi_model_avg_time": sum(r["duration_s"] for r in results["multi_model"]) / num_iterations,
        "quality_improvement": "calculated based on validation metrics",
    }
```

---

## ⚙️ Configuración de Variables de Entorno

Crea un archivo `.env` con tus API keys:

```bash
# Ollama (local, no requiere API key)
OLLAMA_API_URL=http://localhost:11434

# HuggingFace (gratis con límites)
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxxxxxxxxxx

# Groq (gratis, muy rápido)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx

# Together AI (crédito inicial gratis)
TOGETHER_API_KEY=xxxxxxxxxxxxxxxxxxxxx
```

**Obtener API Keys:**
- HuggingFace: https://huggingface.co/settings/tokens
- Groq: https://console.groq.com/keys
- Together AI: https://api.together.xyz/settings/api-keys

---

## 📈 Métricas de Evaluación

El sistema multi-modelo proporciona métricas detalladas:

### **Métricas Básicas:**
- `confidence_score`: Confianza del consensus (0-1)
- `consensus_score`: Acuerdo entre modelos (0-1)
- `num_models`: Modelos que participaron
- `avg_generation_time`: Tiempo promedio por modelo

### **Métricas de Calidad:**
- `common_predictions`: Predicciones validadas por múltiples modelos
- `unique_insights`: Insights aportados por un solo modelo
- `supporting_models`: Lista de modelos que generaron la hipótesis

### **Uso en Loops:**
```python
# Filtrar hipótesis de alta calidad
high_quality = [
    h for h in enhanced_hypotheses
    if h.get("multi_model_hypothesis", {}).get("confidence", 0) > 0.75
    and h.get("multi_model_hypothesis", {}).get("consensus_score", 0) > 0.6
]
```

---

## 🎯 Mejores Prácticas

### **1. Selección de Modelos**

**Para matemáticas:**
```python
tier=ModelTier.QUALITY  # Usa deepseek-r1, Galactica
num_models=3
```

**Para biología:**
```python
tier=ModelTier.BALANCED  # Usa BioGPT + generales
num_models=3
```

**Para exploración rápida:**
```python
tier=ModelTier.FAST  # Usa solo Ollama local
num_models=2
```

### **2. Rate Limiting**

```python
# Entre generaciones consecutivas
await asyncio.sleep(1)  # Respetar rate limits de APIs
```

### **3. Fallback Robusto**

```python
try:
    enhanced = await self._generate_enhanced_hypotheses(candidates)
except Exception as e:
    logger.warning(f"Multi-model failed: {e}. Using heuristic fallback.")
    enhanced = self.mutator.mutate_batch(candidates)  # Fallback
```

---

## 📊 Benchmarks Esperados

### **Calidad de Hipótesis:**
- **Heurístico baseline:** Confidence ~0.5, Testabilidad limitada
- **Multi-modelo (3 modelos):** Confidence ~0.75, Predicciones específicas
- **Multi-modelo (5 modelos):** Confidence ~0.85, Alta fundamentación

### **Tiempos de Respuesta:**
- **Ollama solo (FAST):** 1-3s
- **Multi-modelo BALANCED:** 5-10s
- **Multi-modelo QUALITY:** 10-30s

### **Uso de Recursos:**
- **CPU:** Bajo (mayoría cloud)
- **Memoria:** ~500MB (caching)
- **Red:** ~2-5 MB/hipótesis

---

## 🚀 Próximos Pasos

### **Corto Plazo (1 semana):**
1. ✅ Integrar con `MathematicsLoop`
2. ✅ Integrar con `BiologyLoop`
3. ✅ Ejecutar benchmark comparativo
4. ✅ Ajustar parámetros según resultados

### **Mediano Plazo (1 mes):**
1. Fine-tune modelo base con papers de ArXiv
2. Implementar caché de hipótesis comunes
3. Optimizar consensus algorithm
4. Agregar detección de contradicciones

### **Largo Plazo (3 meses):**
1. Sistema de aprendizaje continuo
2. Validación automática con literature mining
3. Generación de papers completos
4. Integración con herramientas de proof checking

---

## 📝 Ejemplo de Uso Completo

```python
# examples/multi_model_autonomous_demo.py

import asyncio
from app.autonomous.pipelines.mathematics_loop import EnhancedMathematicsLoop

async def main():
    # Crear loop mejorado
    loop = EnhancedMathematicsLoop(domain="number_theory")
    
    # Ejecutar iteración con multi-modelo
    result = await loop.run_enhanced_iteration(
        iteration=1,
        limit=5,
        use_multi_model=True,
    )
    
    # Mostrar resultados
    print(f"✅ Iteration completed in {result['duration_s']:.2f}s")
    
    for candidate in result["selected"]:
        if "multi_model_hypothesis" in candidate:
            mm_hyp = candidate["multi_model_hypothesis"]
            print(f"\n📊 Hypothesis: {mm_hyp['text'][:100]}...")
            print(f"   Confidence: {mm_hyp['confidence']:.2f}")
            print(f"   Models: {', '.join(mm_hyp['supporting_models'])}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## ✅ Checklist de Integración

- [ ] Instalar dependencias: `pip install httpx tabulate`
- [ ] Configurar API keys en `.env`
- [ ] Importar `multi_model_service` en loop
- [ ] Implementar `_generate_enhanced_hypotheses()`
- [ ] Actualizar métricas de telemetría
- [ ] Ejecutar `test_multi_model_autonomous.py`
- [ ] Comparar calidad vs baseline
- [ ] Ajustar parámetros (num_models, tier)
- [ ] Documentar resultados
- [ ] Deploy en producción

---

**Contacto:** Para preguntas o mejoras, abrir issue en el repositorio.

**Licencia:** MIT
