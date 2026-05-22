# Plan: Cross-Validation Matrix

## Objetivo
Crear una matriz NxN dinámica que cuantifique compatibilidad y validación cruzada entre dominios científicos (filas y columnas = dominios/servicios principales).

## Motivación
- Elevar rigor científico combinando resultados de distintos métodos
- Detectar contradicciones inter-dominio
- Priorizar experimentos con mayor valor marginal

## Estructura de Datos (Propuesta)
```json
{
  "domains": ["plasma", "materials", "clinical", "genomics", ...],
  "matrix": {
    "plasma|materials": {"compatibility": 0.82, "evidence": 5, "last_updated": "2025-09-09T12:00:00Z", "rationale": "Thermal gradients ↔ phase stability"},
    "clinical|genomics": {"compatibility": 0.74, "evidence": 3, "rationale": "Mutation-load ↔ phenotype metrics"}
  },
  "version": "cv_matrix.v1"
}
```

## Cálculo Compatibilidad
| Factor | Peso | Fuente |
|--------|------|--------|
| Coincidencia entidades (variables compartidas) | 0.25 | Ontología (futuro) |
| Coherencia numérica (correlaciones esperadas) | 0.25 | Análisis estadístico |
| Evidencia previa (n experimentos consistentes) | 0.20 | validation_history |
| Robustez cruzada (estabilidad resultados) | 0.15 | robustness_metrics |
| Incertidumbre convergente (UQ overlap) | 0.15 | UQ service |

Score final = Σ (factor_normalizado * peso).

## Pipeline de Actualización
1. Registrar ejecución workflow multi-dominio
2. Extraer variables comunes + métricas
3. Calcular correlaciones / divergencias
4. Integrar robustez y UQ
5. Actualizar celda matriz + timestamp
6. Emitir evento `cross_validation.updated`

## Endpoints Planeados
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | /cv/matrix | Recupera matriz completa |
| GET | /cv/matrix/cell?src=A&dst=B | Detalle par dominios |
| POST | /cv/matrix/recompute | Fuerza recomputación global |
| GET | /cv/matrix/stats | Métricas agregadas |

## Métricas Clave
| Métrica | Objetivo |
|---------|----------|
| cobertura_dominios | ≥ 80% pares activos |
| contradicciones_detectadas | < 5% pares | 
| tiempo_actualización | < 2s celda |
| latencia_consulta | < 150ms |

## Integraciones
- Hypothesis Core: snapshot de compatibilidad
- Publication Pipeline: sección de validación cruzada
- Knowledge Graph: entidades compartidas
- Integrity: hash de versión matriz

## Roadmap Incremental
| Fase | Descripción | Entrega |
|------|-------------|---------|
| F1 | Esquema + endpoints lectura dummy | Semana 1 |
| F2 | Cálculo correlaciones básicas | Semana 2 |
| F3 | Integración UQ + robustez | Semana 3 |
| F4 | Eventos + hashing integridad | Semana 4 |

## Riesgos
| Riesgo | Mitigación |
|--------|-----------|
| Sparsidad inicial | Bootstrapping con pares críticos|
| Coste computacional | Cache incremental |
| Inconsistencias datos | Validadores tipados |

---
Primer blueprint. Siguiente: definir modelo persistencia y prototipo endpoints.
