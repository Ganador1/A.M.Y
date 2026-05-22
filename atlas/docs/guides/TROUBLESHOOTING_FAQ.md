# Troubleshooting & FAQ

## Problemas Comunes
| Síntoma | Causa Probable | Solución |
|---------|----------------|----------|
| Caída rendimiento súbita | Batching subóptimo | Revisar profiler |
| Memoria GPU llena | Tamaño batch alto | Reducir batch / activar surrogate |
| Hash mismatch | Artefacto modificado | Regenerar y auditar cadena |
| Tiempo de respuesta alto | CPU saturada | Habilitar distribución |
| Variabilidad resultados | Semillas no fijadas | Fijar random seeds |

## Preguntas Frecuentes
### ¿Cómo activo métricas avanzadas?
Integrar exportador (plan) o leer logs estructurados.

### ¿Puedo añadir otro optimizador?
Sí, siguiendo patrón Strategy (ver intelligent_optimizer.py).

### ¿Cómo escalo a múltiples GPUs?
Extender distributed_manager con asignación por dispositivo.

### ¿Qué hacer ante verificación fallida?
1. Aislar artefacto
2. Recalcular hash
3. Revisar logs cadena
4. Emitir alerta si persiste

### ¿Cómo reduzco latencia inicial?
Pre-cargar modelos en fase prepare (futuro con adapters).

## Diagnóstico Rápido
| Check | Comando/Acción |
|-------|----------------|
| Versión Python | `python --version` |
| Dependencias inseguras | pip-audit (script tarea) |
| Seguridad código | bandit (script tarea) |
| Integridad cadena | Auditoría plan API |

---
FAQ inicial completo.
