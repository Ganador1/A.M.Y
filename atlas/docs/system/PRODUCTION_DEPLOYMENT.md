# Guía de Despliegue en Producción

## Objetivo
Procedimiento estandarizado para desplegar la plataforma con reproducibilidad, observabilidad e integridad asegurada.

## Requisitos Previos
| Requisito | Versión / Nota |
|-----------|----------------|
| Python | 3.13.x |
| GPU (opcional) | CUDA 11+ |
| Docker | >=24 |
| docker-compose | >=2 |
| Storage | SSD recomendado |

## Modos de Despliegue
| Modo | Uso | Pros | Contras |
|------|-----|-----|---------|
| Local Virtualenv | Desarrollo | Simplicidad | No aislado |
| Docker Single | Demo / QA | Reproducible | Latencia inicial |
| Docker Compose | Producción base | Servicios separados | Orquestación manual |
| Kubernetes (plan) | Escala horizontal | Auto-recovery | Complejidad |

## Pasos (Docker Compose)
1. Construir imagen: `docker-compose build`
2. Lanzar servicios: `docker-compose up -d`
3. Verificar salud: endpoint `/health`
4. Revisar logs: `docker-compose logs -f app`
5. Registrar artefactos críticos (integridad)

## Variables de Entorno (Ejemplo)
| Variable | Propósito | Ejemplo |
|----------|-----------|---------|
| APP_ENV | Entorno | production |
| LOG_LEVEL | Nivel log | INFO |
| ENABLE_GPU | Aceleración | true |
| INTEGRITY_BATCH_SIZE | Artefactos por Merkle | 10 |
| METRICS_PORT | Exposición métricas | 9090 |

## Observabilidad
- Logs estructurados JSON opcional (plan)
- Métricas: export HTTP (añadir endpoint `/metrics` futuro)
- Alertas: integridad + fallo adaptativo + latencia p95

## Seguridad
| Área | Práctica |
|------|----------|
| Dependencias | `pip-audit` en CI |
| Código | `bandit` periódico |
| Integridad | Hash + chain root |
| Acceso | Control de red (reverse proxy) |

## Backup & Recuperación
| Artefacto | Estrategia |
|-----------|-----------|
| Modelos | Snapshot versión + hash |
| Configuraciones | Git + copia cifrada |
| Logs Integridad | Rotación + compresión |
| Reportes | Almacenamiento replicado |

## Flujo de Release
1. Rama feature → PR + tests + auditorías
2. Tag semántico: vMAJOR.MINOR.PATCH
3. Build imagen con tag
4. Escaneo seguridad (dependencias + estático)
5. Deploy progresivo (QA → staging → prod)

## Checklist Pre-Producción
- [ ] Tests críticos verdes
- [ ] Análisis seguridad sin críticos
- [ ] Hashes verificados
- [ ] Métricas de base recogidas
- [ ] Documentación actualizada

## Escalado
| Dimensión | Técnica |
|----------|---------|
| CPU-bound | Multiproceso / distribución |
| GPU | Managers + batching |
| IO | Async + colas (plan) |

## Roadmap Producción
| Fase | Entrega |
|------|---------|
| Q4 2025 | Export métricas estándar |
| Q1 2026 | Soporte Kubernetes nativo |
| Q1 2026 | Circuit breakers |
| Q2 2026 | Autoscaling predictivo |

---
Versión inicial lista.
