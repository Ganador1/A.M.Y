


          
Perfecto. He leído tu análisis en “analisis gp5hig.md” y lo he fusionado con mi evaluación previa para producir un roadmap detallado y accionable, alineado con la arquitectura actual del proyecto y tus prioridades estratégicas.

A continuación te entrego:
- Un complemento del análisis (qué añade y cómo converge con lo previo).
- Un roadmap faseado y priorizado con tareas concretas, criterios de aceptación, dependencias y riesgos.
- Un mapeo de cambios a componentes específicos del repo.
- Métricas/KPIs y quick wins para los próximos 7 días.

Si quieres, al final puedo guardar este roadmap como un documento Markdown dentro del repositorio.

Complemento del análisis (convergencias y añadidos clave)
- Convergencia fuerte:
  - Arquitectura modular y madura con cadena de middlewares robusta, MLflow para tracking, publicaciones con integridad verificable y sandbox para ejecuciones controladas.
  - Cobertura de dominios científicos y servicios avanzados (plausibilidad, scheduler, orquestador, multi‑agente, GPU).
  - Observabilidad y testeo amplio, aunque con espacios por completar.
- Aportes/énfasis añadidos del documento:
  - Necesidad de API coherente y versionada (/api/v1), estandarización de contratos y pruebas de compatibilidad.
  - Reproducibilidad de datasets/artefactos: estandarizar manifest y forzar DVC donde corresponda.
  - CI/CD con gates (lint, seguridad, pruebas, migraciones) y defensa operativa (SLO/SLI con alertas).
  - Endurecimiento del sandbox con aislamiento a nivel contenedor/microVM y políticas de recursos.
  - Gobernanza/documentación: completar docs clave, TOC e índice navegable por release.
  - Scheduler “policy‑aware” y GPU “cost‑aware”, más integración con Multi‑Agente y KG para cerrar el loop científico.

Roadmap fusionado y priorizado (12–16 semanas + continuo)
Visión: Convertir AXIOM META 4 en un laboratorio autónomo multidominio que produce ciencia reproducible a escala, con seguridad de clase producción, observabilidad distribuida, gobernanza abierta y rigor metodológico.

Principios:
- Seguridad y observabilidad primero.
- Contratos y reproducibilidad como gates (no “nice‑to‑have”).
- Automatización: todo lo crítico se prueba y despliega con pipeline.
- Métricas y SLOs que guían decisiones.

Fase 0 (Semanas 0–2): Fundamentos de producción (alto impacto/urgencia)
Objetivo: Cerrar brechas críticas de seguridad, observabilidad básica distribuida, cohesión de API y pipeline CI mínimo.

Epics y tareas
- Seguridad (AuthN/Z + hardening)
  - Implementar OAuth2/JWT con scopes por router (RBAC/ABAC por endpoint). Criterio: 100% endpoints protegidos con esquema documentado.
  - Endurecer cabeceras de seguridad (CSP estricta, HSTS, X‑Content‑Type‑Options, Referrer‑Policy). Criterio: scan sin findings críticos.
  - Validación homogénea de payloads con Pydantic v2 en todos los endpoints, tamaños máximos por ruta, rate limits por categoría.
- Observabilidad (OTel base)
  - Instrumentación OpenTelemetry (traces/metrics/logs) en FastAPI y clientes http internos; propagación de trace_id end‑to‑end. Criterio: 100% requests con trace_id y trazas visibles.
  - Export a Prometheus y collector/tempo/loki (según tu stack); dashboard base de latencia p50/p95/p99, tasa de errores y saturación.
- API coherente
  - Versionar API en /api/v1, unificar prefijos/tags y publicar OpenAPI validada; generar JSONSchema por contrato. Criterio: contratos versionados + docs consistentes.
- CI mínimo (GitHub Actions/GitLab CI)
  - Jobs: lint (flake8/ruff), unit+integration, cobertura con gate, seguridad (bandit, pip‑audit), build multi‑stage. Criterio: pipeline rojo si falla cualquiera.

Dependencias:
- Ninguna fuerte, salvo definir emisores/validadores de JWT y secreto seguro.

Riesgos:
- Cambios de ruptura en rutas; mitigación: introducir /api/v1 en paralelo y mantener deprecación gradual.

Fase 1 (Semanas 3–6): Rigor científico y reproducibilidad
Objetivo: Cerrar reproducibilidad end‑to‑end y establecer integridad fuerte en artefactos y publicaciones.

Epics y tareas
- Reproducibilidad de datos/artefactos
  - “Artifact Manifest” estándar por modelo y experimento (YAML/JSON) con origen, commit, hyperparams, dataset hash, métricas, CV, firma HMAC/Ed25519, enlace a MLflow. Criterio: 100% modelos en <mcfolder name="models/" path="./models"></mcfolder> con manifest validado.
  - DVC requerido en pipelines de entrenamiento clave; enforcement en CI (rechazar merges sin dvc.lock para experimentos publicados). Criterio: 90% experimentos relevantes con DVC + lock.
- Replicability Checker
  - Re‑ejecución en entorno limpio (contenedor) comparando hashes/métricas con tolerancias; reporte automático. Criterio: ≥90% hash‑match reproducciones.
- Integridad de publicaciones (Merkle + firma)
  - Firmas Ed25519 de paquetes de publicación en <mcfolder name="publications/" path="./publications"></mcfolder>, árbol Merkle con proofs, anclaje opcional (OpenTimestamps). Criterio: verificación automatizada en CI y en un endpoint de integridad.
- Contratos de API y pruebas
  - Generar JSONSchema + contract tests (compatibilidad hacia atrás); Schemathesis o similar para fuzzing de OpenAPI. Criterio: compatibilidad ≥95% en cambios de minor version.

Dependencias:
- Fase 0 para CI y API versionada.

Riesgos:
- Complejidad operativa de DVC con datos grandes; mitigación: seleccionar pipelines críticos primero y storage remoto eficiente.

Fase 2 (Semanas 7–10): Orquestación inteligente y coste (scheduler/policies/GPU)
Objetivo: Llevar el orquestador y scheduler a políticas multi‑objetivo con coste y riesgo, y endurecer el sandbox.

Epics y tareas
- Policy‑aware scheduling
  - Incorporar plausibilidad, riesgo/ética, costo GPU y prioridad científica a la función de costo del scheduler. Criterio: colas por prioridad, “admission control” con cuotas por tenant/proyecto.
  - Deadline scheduling y SLOs por job; timeouts y reintentos diferenciados por criticidad.
- GPU cost‑aware allocation
  - Perfiles por job (mem/vRAM/tiempo) y asignación acorde; auto‑escalado por demanda; preferencia spot/preemptible donde aplique. Criterio: reducción de coste medio por experimento con SLOs estables.
- Sandbox endurecido
  - Aislamiento con gVisor/Firecracker o contenedores rootless; seccomp/apparmor; montajes read‑only; límites cgroup por job. Criterio: pruebas de escape negativas; auditoría de permisos mínima.

Dependencias:
- Métricas/trazas (Fase 0) para observar efecto de políticas.

Riesgos:
- Overhead de aislamiento; mitigación: perfiles configurables según criticidad del job.

Fase 3 (Semanas 11–16): Laboratorio autónomo multidominio (loop cerrado)
Objetivo: Integrar Multi‑Agente y KG con orquestación para cerrar el ciclo científico completo y publicar automáticamente.

Epics y tareas
- Integración Multi‑Agente + KG
  - Hipótesis → evaluación de plausibilidad → scheduler → sandbox → validación → publicación → realimentación de conocimiento (KG) y prompts. Criterio: 3 workflows multidominio/mes end‑to‑end.
- Peer‑review automatizado
  - Agente revisor independiente con criterios estadísticos/UQ y checklist de reproducibilidad; gate antes de promover a “producción científica”. Criterio: 100% publicaciones con peer‑review automatizado.
- “Publication‑ready outputs”
  - Plantillas LaTeX + anexos reproducibles (datos, código, hashes, proofs). Criterio: paquete listo para arXiv/Zenodo con DOI opcional.

Continuo (operaciones y excelencia)
- SLO/SLI/Alerting: latencia p99, tasa de éxito, integridad (≥0.95), reproducibilidad (≥0.9), costo por experimento. Alertas y runbooks.
- Auditorías periódicas (seguridad, ética, bias), rotación de claves y gestión de secretos, backups/DR.
- Gobernanza abierta y documentación versionada con TOC e índice por release.

Mapa de cambios a componentes del repo
- API, seguridad, middlewares
  - <mcfile name="main.py" path="./main.py"></mcfile>: montaje de /api/v1, registro de middlewares de seguridad/OTel y routers.
  - <mcfolder name="app/middleware/" path="./app/middleware/"></mcfolder> y <mcfile name="middleware.py" path="./app/middleware.py"></mcfile>: CSP, HSTS, TraceIdMiddleware, size limits, rate limits por ruta.
  - <mcfile name="security.py" path="./app/security.py"></mcfile>: OAuth2/JWT, scopes, RBAC/ABAC.
  - <mcfolder name="app/routers/" path="./app/routers/"></mcfolder> (ej. <mcfile name="pde.py" path="./app/routers/pde.py"></mcfile>): versionado de rutas y validación Pydantic v2.
- Observabilidad
  - <mcfile name="metrics.py" path="./app/metrics.py"></mcfile>, <mcfile name="monitoring.py" path="./app/monitoring.py"></mcfile>, <mcfolder name="monitoring/" path="./monitoring/"></mcfolder>: instrumentación OTel, export, dashboards.
- Datos/ML y reproducibilidad
  - <mcfile name="pipeline_v4.py" path="./pipeline_v4.py"></mcfile> y <mcfile name="weak_label_v4.py" path="./weak_label_v4.py"></mcfile>: integración DVC, logging enriquecido, manifest y registro MLflow coherente.
  - <mcfolder name="mlruns/" path="./mlruns/"></mcfolder> + <mcfolder name="models/" path="./models"></mcfolder>: generación/validación de manifests.
  - <mcfolder name="publications/" path="./publications"></mcfolder>: Merkle tree, firma Ed25519, proofs y verificación.
- Orquestación y sandbox
  - <mcfolder name="app/services/" path="./app/services/"></mcfolder> (scheduler/orchestrator): políticas de costo multi‑objetivo, deadlines, colas/prioridades, cuotas.
  - <mcfolder name="app/services/sandbox/" path="./app/services/sandbox/"></mcfolder> o módulo equivalente: aislamiento con gVisor/Firecracker, límites cgroup.
- Documentación y CI/CD
  - <mcfolder name="docs/" path="./docs/"></mcfolder>: INDEX.md/TOC, completar “licencias” y “gobernanza”.
  - <mcfolder name=".github/workflows/" path="./.github/workflows/"></mcfolder>: pipelines CI con gates y artefactos.
  - <mcfile name="README.md" path="./README.md"></mcfile>: dividir en guías temáticas; mantener un README delgado y navegable.

Criterios de aceptación por fase (resumen)
- Fase 0:
  - 100% endpoints bajo /api/v1 con auth y validación homogénea; CSP/HSTS activas.
  - Trazas OTel visibles con propagación de trace_id; dashboard base operativo.
  - CI en rojo si falla lint, tests, seguridad o build.
- Fase 1:
  - 100% modelos con manifest validado; ≥90% pipelines relevantes con DVC.
  - Replicability Checker con ≥90% hash‑match; publicaciones con firma y Merkle verificados en CI.
  - Contract tests activos; compatibilidad hacia atrás ≥95%.
- Fase 2:
  - Scheduler con políticas multi‑objetivo y cuotas por tenant; SLO por job.
  - Asignación GPU cost‑aware con reducción de coste y SLOs estables.
  - Sandbox endurecido con pruebas de escape negativas.
- Fase 3:
  - ≥3 workflows multidominio/mes completados E2E con peer‑review automatizado.
  - “Publication‑ready outputs” generados automáticamente para paquetes prioritarios.

KPIs y SLO/SLI
- Seguridad: 0 findings críticos en bandit/pip‑audit; 100% endpoints con auth.
- Reproducibilidad: ≥90% de experimentos con bundle completo y hash verificado.
- Observabilidad: 100% requests con trace_id; p99 < SLO acordado; MTTR < 30 min.
- Coste: reducción ≥20% en coste medio por experimento con estabilidad de SLOs.
- Ciencia: ≥3 workflows multidominio/mes con publicación validada.

Quick wins (próximos 7 días)
- API/Seguridad
  - Introducir /api/v1 en <mcfile name="main.py" path="./main.py"></mcfile> y mantener alias temporal para rutas antiguas (deprecación).
  - Añadir CSP estricta y HSTS en <mcfile name="middleware.py" path="./app/middleware.py"></mcfile>.
  - Añadir OAuth2/JWT básico en <mcfile name="security.py" path="./app/security.py"></mcfile> y proteger 2–3 routers críticos (p.ej., plausibility, scheduler).
- Observabilidad
  - Integrar OTel FastAPI + httpx y export a Prometheus; propagar trace_id a logs en <mcfile name="metrics.py" path="./app/metrics.py"></mcfile>.
  - Dashboard inicial: latencias p50/p95/p99, error rate, cache hit ratio.
- CI
  - Workflow base en <mcfolder name=".github/workflows/" path="./.github/workflows/"></mcfolder>: setup Python, cache deps, ruff/flake8, pytest con cobertura y gates, bandit, pip‑audit, build de imagen.
- Reproducibilidad
  - Definir schema del “Artifact Manifest” y crear validador CLI en <mcfolder name="scripts/" path="./scripts/"></mcfolder>; aplicar a 1–2 modelos en <mcfolder name="models/" path="./models"></mcfolder> para prueba piloto.

Riesgos y mitigaciones
- Cambios de ruptura en API: mantener periodo de compatibilidad con alias, comunicar deprecaciones en <mcfile name="README.md" path="./README.md"></mcfile> y en /docs.
- Fricción con DVC/almacenamiento: empezar por pipelines críticos y definir storage remoto eficiente.
- Overhead de OTel y sandbox endurecido: activar por perfil/entorno, ajustar sampling y límites.

## Progreso Agente Low (Seguimiento Iterativo)

Estado inicial (Semana 0) – Todos los entregables en planificación.

Entregables Fase 0 bajo ownership del Agente Low:

- CI mínima: workflow con lint (ruff), tests (pytest + coverage), seguridad (bandit, pip-audit) y build base.
- Documentación base estructurada: `docs/INDEX.md` (TOC + estados), completar borradores de licencia y gobernanza.
- Validador de manifiestos de modelos/datasets (`scripts/validate_manifests.py`).
- Guía de contribución específica del rol low (`docs/LOW_AGENT_CONTRIBUTING.md`).
- Integración de validación de manifiestos en CI (gate suave al inicio: warning → luego error obligatorio).

Métrica de avance (se actualizará en cada iteración):

| Entregable | Estado | ETA | Notas |
|------------|--------|-----|-------|
| CI mínima | done | ✅ | Workflow inicial operativo (ruff, tests, seguridad, build) |
| INDEX.md + TOC | done | ✅ | Índice creado con estados y TOC base |
| Licencia & Gobernanza (esqueletos) | done | ✅ | Documentos draft añadidos |
| Validador manifiestos | done | ✅ | Script con salida JSON y hashes |
| LOW_AGENT_CONTRIBUTING.md | done | ✅ | Guía con checklist y estándares |
| Validación manifiestos en CI | done | ✅ | Paso añadido (no bloqueante) |
| manifest.schema.json | done | ✅ | Esquema draft (versión inicial) |
| Manifest ejemplo (plausibility_v4_rf) | done | ✅ | Validado contra schema |
| Manifests adicionales (logreg, rf_regularized) | done | ✅ | Total 3 manifests válidos |
| Script firma Ed25519 (`sign_manifest.py`) | done | ✅ | Generación clave + firma determinística |
| Script verificación firmas (`verify_manifest_signatures.py`) | done | ✅ | Reporte JSON con estado por manifest |
| Job verificación firmas en CI | done | ✅ | No bloqueante, publica artefacto |
| Dependencia cryptography añadida | done | ✅ | Alineada con requirements.audit.txt |
| Activar gate estricto manifests | pending | TBD | Condición: 2 runs consecutivas sin errores (alcanzado), próximo commit activará fail-on-error |
| Activar gate firmas (bloqueante) | pending | TBD | Condición: ≥1 firma válida por manifest y claves públicas versionadas |

Próximos pasos inmediatos (Agente Low - actualización):

1. Activar modo bloqueante del validador de manifests (cambiar paso CI: remover `|| true` y/o añadir `--fail-on-error`).
2. Añadir almacenamiento de claves públicas en `keys/public/` + `keys/README.md` (solo públicas; privadas fuera del repo).
3. Ejecutar firma sobre los 3 manifests actuales y commitear firmas (añadir sección `signatures`).
4. Activar gate de firmas (warning → bloqueante) tras verificar consistencia en 2 pipelines consecutivos.
5. Extender schema para validar estructura de `signatures[*]` (alg, sig, public_key_fingerprint, optional ts).
6. Documentar flujo de rotación de claves y verificación local en `docs/REPRODUCIBILITY_INTEGRITY.md` (nuevo).
7. Preparar diseño preliminar Merkle tree para lote de publicaciones (borrador técnico).

Condiciones de activación gates:

- Gate manifests (estructura + hashes): INMINENTE (criterio cumplido).
- Gate firmas: tras 3 manifests firmados + 2 ejecuciones CI consecutivas sin fallos de verificación.


Próxima actualización: tras habilitar gate bloqueante de manifests y firmar los 3 manifests actuales.
