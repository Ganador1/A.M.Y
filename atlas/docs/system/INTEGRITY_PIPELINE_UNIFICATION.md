# Especificación: Unificación del Pipeline de Integridad

## Objetivo
Consolidar hashing, verificación, trazabilidad y anclaje semiblockchain en un flujo declarativo único.

## Estado Actual
| Componente | Función | Limitación |
|------------|---------|-----------|
| blockchain_validation.py | Simulación consenso / registro | No orquesta otros hashes |
| integrity_verification.py | Verifica artefactos individuales | Aislado del flujo completo |
| metrics.py | Exposición parcial | Métricas dispersas |

## Diseño Propuesto
```
[Evento Artefacto] -> Hasher -> Registro Local -> Batch Merkle Builder -> Anchor Writer -> Verificador Programado -> Alertas
```

## Tipos de Artefacto
| Tipo | Ejemplo Ruta | Campos Hash |
|------|--------------|-------------|
| DATASET | /data/processed/*.parquet | bytes + schema_signature |
| MODEL | /models/*.bin | bytes + hyperparams.json |
| REPORT | /reports/papers/*.md | contenido + metadatos |
| CONFIG | /configs/*.yml | contenido |

## Esquema Registro Local (JSONL)
```
{
  "timestamp": "ISO8601",
  "artifact_type": "MODEL",
  "path": "...",
  "sha256": "...",
  "merkle_root": "...",
  "previous_root": "...",
  "integrity_chain_height": 42
}
```

## Lógica Merkle Simplificada
1. Agrupar hashes nuevos cada N artefactos o T minutos
2. Construir árbol binario (padding último si impar)
3. Guardar root + enlazar con root previo (block-like)

## API Interna (Plan)
| Función | Descripción |
|---------|-------------|
| register_artifact(meta) | Calcula y almacena hash base |
| build_merkle_batch() | Consolida lote pendiente |
| anchor_root(root) | Ancla root (simulado) |
| verify_artifact(path) | Recalcula y compara |
| audit_chain() | Recorre enlaces root previos |

## Métricas
| Métrica | Significado |
|---------|-------------|
| integrity_chain_height | Longitud cadena de roots |
| pending_artifacts | En cola para batch |
| verification_failures | Conteo discrepancias |
| avg_batch_interval_sec | Cadencia real lotes |

## Alertas
| Condición | Acción |
|-----------|--------|
| verification_failures > 0 | Alerta crítica integridad |
| pending_artifacts > umbral | Forzar build lote |
| avg_batch_interval_sec > SLA | Ajustar N o T |

## Roadmap
| Fase | Entrega |
|------|---------|
| 1 | Registro unificado + hashing consistente |
| 2 | Merkle batches + chain linking |
| 3 | API verificación + auditoría completa |
| 4 | Export métricas + alertas |
| 5 | Opcional: anclaje externo (timestamp server) |

## Riesgos y Mitigaciones
| Riesgo | Mitigación |
|--------|-----------|
| Crecimiento log | Rotación + compresión |
| Collisiones improbables | SHA256 + opcional BLAKE3 |
| Lotes retrasados | Timer + umbral cantidad |

---
Especificación inicial completada.
