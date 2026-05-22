# Ética, Seguridad y Uso Responsable

Este proyecto incluye módulos de cómputo científico, simulación, criptografía y ejecución de procesos que pueden conllevar riesgos técnicos, legales o de seguridad si se usan incorrectamente. Este documento centraliza advertencias, buenas prácticas y limitaciones.

## Principios de uso responsable
- Cumple leyes y licencias aplicables (software, datos, exportación, cifrado).
- No uses el sistema para dañar, vulnerar privacidad o eludir controles.
- Informa a usuarios finales de limitaciones, sesgos y márgenes de error.
- Protege credenciales, claves y datos sensibles.
- Respeta límites de recursos (CPU/GPU/memoria) para evitar abuso o costes inesperados.

## Áreas de riesgo y advertencias

### 1) Criptografía y claves (app/routers/cryptography, diagnose_rsa.py)
- No generes, almacenes ni transmita claves privadas en texto plano.
- Evita usar tamaños de clave inseguros o RNG no criptográfico.
- Cumple normativas de exportación y regulaciones locales sobre cifrado.
- Usa librerías revisadas; evita implementar algoritmos criptográficos desde cero.

### 2) Endpoints y red (FastAPI, requests/httpx, scripts de test)
- Expón el servidor solo en redes confiables y con autenticación (JWT/API keys).
- Valida y sanea la entrada; limita tasas y añade control de acceso por rol.
- Nunca registres secretos o PII en logs. Revisa `server.log` y configuraciones.

### 3) Ejecución de código/Procesos (subprocess, eval/exec en PDE)
- `eval/exec` es peligroso. En `pde_service.py` está limitado, pero debe evitarse con entrada de usuarios.
- No ejecutes comandos de sistema con entrada no confiable. Usa listas de argumentos y timeouts.
- Aísla procesos intensivos (containers) y establece límites de recursos.

### 4) Base de datos y ficheros (SQLAlchemy, sqlite3, open())
- Usa consultas parametrizadas; no construyas SQL con cadenas.
- Encripta datos sensibles en reposo y en tránsito. Gestiona migraciones de forma segura.
- Controla permisos de archivos. No guardes PII sin base legal.

### 5) GPU/DFT/Simulaciones (GPAW, ASE, DeepXDE, PyTorch)
- Alto consumo energético/coste: configura límites (tamaño de malla, k-points, pasos).
- Respeta licencias y citas de código y datos científicos.
- No uses resultados sin validación para decisiones críticas.

### 6) Servicios Médicos Avanzados (Strain Analysis, Multiscale Models, Advanced Clinical Validation)
- **ADVERTENCIA CRÍTICA**: Estos servicios procesan datos médicos sensibles. Cumple HIPAA/GDPR y obtén consentimiento informado.
- **Limitaciones Clínicas**: Resultados son herramientas de apoyo, no reemplazan juicio médico profesional.
- **Validación Requerida**: Valida algoritmos contra estándares clínicos antes de uso diagnóstico.
- **Privacidad**: Anonimiza datos antes del procesamiento. No almacenes imágenes médicas sin encriptación.
- **Responsabilidad**: Documenta limitaciones, márgenes de error y casos donde el algoritmo puede fallar.
- **Consentimiento**: Obtén aprobación ética para uso de datos médicos en investigación.
- **Transparencia**: Explica algoritmos a usuarios clínicos y pacientes cuando corresponda.

### 7) Servicios Científicos Avanzados (Plasma Physics, Additive Manufacturing)
- **Riesgos de Seguridad**: Simulaciones de plasma pueden modelar procesos con aplicaciones duales (médicas/militares).
- **Licencias de Exportación**: Verifica regulaciones ITAR/EAR para algoritmos de física de plasmas.
- **Validación Científica**: Resultados requieren validación experimental antes de publicación o aplicación.
- **Recursos Computacionales**: Procesos intensivos pueden afectar disponibilidad del sistema.
- **Propiedad Intelectual**: Respeta patentes y derechos de autor en diseños de manufactura aditiva.
- **Impacto Ambiental**: Considera huella energética de simulaciones de alto rendimiento.

### 8) Caché y Redis
- No caches datos sensibles. Define expiración y invalidación correctas.
- Asegura Redis con contraseña/TLS y listas de control de acceso.

## Datos personales y cumplimiento
- Minimiza la recopilación de datos. Define retención y borrado.
- Informa a usuarios sobre uso de datos. Facilita exportación y eliminación.
- Considera GDPR/CCPA u otras normativas según tu jurisdicción.

## Riesgos específicos de IA médica y científica

### Extensión: Biología y Química Computacional (Resumen)
Para detalles ampliados ver `BIO_CHEM_ETHICS_AND_SAFETY.md`.
| Dominio Sensible | Riesgos | Mitigación Base |
|------------------|---------|-----------------|
| Genómica | Re-identificación, privacidad | Anonimización estricta, hashing, gating CRITICAL |
| Redes Metabólicas | Diseño rutas biosintéticas | Firma dual, límites modelo |
| Química Computacional Avanzada | Screening masivo | Límite conformers y tamaño batch |
| Dinámica Molecular | Derivación estructuras sensibles | Control átomos y fuerza campo |
| Biología Sintética | Construcción no autorizada | Bloqueo por defecto + whitelist |
| Bioseguridad / Evaluación | Detección vulnerabilidades | Aislamiento + auditoría reforzada |

### IA en Medicina y Salud
- **Sesgos en Datos**: Los modelos pueden heredar sesgos de datos de entrenamiento (subrepresentación de grupos demográficos).
- **Falsos Positivos/Negativos**: Riesgo de diagnósticos erróneos con consecuencias graves para pacientes.
- **Dependencia Tecnológica**: No reemplaza experiencia clínica; úsalo como herramienta complementaria.
- **Privacidad Genética**: Datos genómicos requieren protección especial bajo leyes de privacidad médica.
- **Equidad en Salud**: Asegura que algoritmos funcionen equitativamente across poblaciones diversas.

### IA en Investigación Científica
- **Reproducibilidad**: Documenta completamente parámetros, datos y versiones para reproducibilidad.
- **Validación Experimental**: Resultados computacionales requieren validación experimental antes de claims científicos.
- **Fraude Científico**: Evita manipulación de resultados o cherry-picking de datos.
- **Colaboración Ética**: Transparencia en colaboraciones público-privadas, especialmente con datos sensibles.
- **Impacto Ambiental**: Simulaciones de alto rendimiento tienen huella energética significativa.

### Gobernanza de IA
- **Auditorías Regulares**: Revisa algoritmos periódicamente por sesgos, precisión y seguridad.
- **Explicabilidad**: Implementa métodos para explicar decisiones de IA (XAI - Explainable AI).
- **Monitoreo Continuo**: Sistema de alertas para degradación del rendimiento o detección de anomalías.
- **Actualización Responsable**: Plan de actualización de modelos con validación completa antes del despliegue.

## Registro y monitoreo
- Registra métricas sin exponer datos sensibles.
- Establece alertas para uso anómalo de recursos o errores repetidos.

## Protocolos de emergencia y respuesta a incidentes

### Incidentes Médicos
- **Fallo de Algoritmo**: Protocolo de fallback a métodos tradicionales si IA falla.
- **Brecha de Datos**: Notificación inmediata a afectados y autoridades regulatorias.
- **Resultado Clínico Adverso**: Documentación completa y análisis root-cause.
- **Tiempo de Respuesta**: Máximo 24 horas para incidentes críticos de salud.

### Incidentes Científicos
- **Error de Simulación**: Verificación cruzada con métodos alternativos.
- **Pérdida de Datos**: Backups redundantes y recuperación de desastres.
- **Contaminación de Datos**: Protocolos de aislamiento y limpieza de datasets.
- **Falla de Validación**: Revisión completa antes de publicación o aplicación.

### Recuperación de Desastres
- **Plan de Continuidad**: Mantenimiento de servicios críticos durante interrupciones.
- **Comunicación**: Canales claros para informar stakeholders sobre incidentes.
- **Lecciones Aprendidas**: Análisis post-incidente y mejora continua de protocolos.

## Versionado y almacenamiento de datos
- No versiones PII/secretos/licencias restrictivas. Usa .gitignore/.dvcignore.
- Configura límites: MAX_VERSION_FILE_BYTES (p.ej. 500MB por archivo) y cuotas de espacio.
- Restringe rutas con STRICT_DATA_PATHS=1 y ALLOWED_DATA_ROOT (por defecto ./data).
- Verifica integridad con checksums (SHA-256) y auditorías de cambios.
- DVC es opcional; protege remotos con credenciales seguras y TLS.

## Limitaciones y descargo de responsabilidad
- El software se provee "tal cual", sin garantías. Úsalo bajo tu propio riesgo.
- Los módulos educativos o de demo no están endurecidos para producción.
- Los resultados científicos pueden variar según parámetros y entorno.

## Checklist rápido antes de producción
- [ ] Variables de entorno seguras (sin secretos en repositorio)
- [ ] HTTPS/TLS en endpoints, autenticación y autorización activas
- [ ] Sanitización de entradas y límites de tasa
- [ ] Logs sin PII ni secretos
- [ ] Políticas de retención de datos
- [ ] Límites de recursos y cuotas configurados

## Referencias
- OWASP Top 10, ASVS
- NIST SP 800-53 / 800-57 (gestión de claves)
- Responsible AI: transparencia, equidad, robustez, privacidad
- FDA Guidance for Medical Device Software
- EU AI Act (Artificial Intelligence Act)
- WHO Guidelines for Digital Health
- ACM Code of Ethics for Computing
- ASME Standards for Additive Manufacturing
- IEEE Standards for Plasma Physics Simulations

---

## Matriz de Evaluación de Riesgo (Propuesta)
| Nivel | Descripción | Ejemplos | Controles Requeridos |
|-------|-------------|----------|----------------------|
| Bajo | No impacto seguridad / privacidad | Álgebra simbólica, visualizaciones simples | Logging básico |
| Medio | Uso moderado de recursos o datos no sensibles | Optimización numérica, simulaciones pequeñas | Límites de recursos, métricas |
| Alto | Datos sensibles o cómputo intensivo | Imágenes médicas, modelos multiescala | Aislamiento, trazabilidad hash, revisión humana |
| Crítico | Potencial dual-use o impacto clínico directo | Plasma avanzado, análisis clínico automatizado | Revisión ética formal, gating manual, auditoría reforzada |

## Controles Graduales (Escalonamiento)
1. Observación pasiva (solo métricas)
2. Limitación de parámetros (rangos seguros)
3. Sandboxing parcial (recursos acotados)
4. Doble confirmación humana (4-eyes)
5. Gate ético con justificación firmada

## Checklist Dual-Use antes de Ejecución
- ¿El resultado puede ser reutilizado para daño físico, biológico o industrial?
- ¿Existen restricciones de exportación (ITAR/EAR) aplicables?
- ¿Hay alternativa menos riesgosa para el objetivo científico?
- ¿Se documenta la finalidad legítima y los límites de uso?
- ¿El código/experimento incluye referencias de validación y disclaimers?

Si ≥2 respuestas "sí" → elevar a revisión ética antes de continuar.

## Mecanismo de Override Responsable
| Condición | Requisito de Override | Registro |
|-----------|-----------------------|---------|
| Bloqueo automático por riesgo alto | Firma digital de 2 responsables | Hash + timestamp cadena integridad |
| Exceso de recursos | Justificación de necesidad | Métricas antes/después |
| Algoritmo experimental no validado | Plan de validación adjunto | Ticket vinculado |

## Red Teaming Científico (Plan)
| Fase | Objetivo | Frecuencia |
|------|----------|-----------|
| Simulación adversarial | Encontrar parámetros inseguros | Semestral |
| Inyección de datos corruptos | Evaluar robustez validación | Trimestral |
| Auditoría reproducibilidad | Confirmar replicabilidad | Anual |

## Roles Humanos y Responsabilidades
| Rol | Responsabilidad Ética |
|-----|-----------------------|
| Lead Científico | Aprobación final experimentos críticos |
| Oficial de Cumplimiento | Verificar regulaciones y licencias |
| Data Steward | Clasificación y anonimización de datos |
| SecOps | Supervisar seguridad operacional |
| Comité Ético | Revisar casos dual-use y clínicos |

## Respuesta a Incidentes (Extensión)
| Tipo | Tiempo Objetivo (TTR) | Acciones Clave |
|------|----------------------|---------------|
| Brecha de datos sensibles | < 4h contención | Aislar, revocar claves, notificar |
| Uso no autorizado GPU masivo | < 2h | Cortar sesión, analizar logs |
| Fallo cadena integridad | < 6h | Reconstruir Merkle, comparar backups |
| Modelo clínico deriva | < 24h | Desplegar versión previa estable |

## Métricas Éticas Operacionales (Adicionales)
| Métrica | Fórmula | Umbral | Acción |
|---------|---------|--------|--------|
| risk_event_rate | eventos_riesgo / ejecuciones | < 1% | Revisar reglas si > |
| override_ratio | overrides / bloqueos | < 30% | Auditar motivos |
| dual_use_flags | flags aprobados / total flags | N/A | Monitoreo tendencia |
| reproducibility_gap | |resultado_ref - resultado_actual| | < tolerancia definida | Ajustar pipeline |

## Integración con Otros Documentos
- Ver `ETHICS_COMPLIANCE_PLAN.md` para roadmap de bias y gating.
- Ver `INTEGRITY_PIPELINE_UNIFICATION.md` para encadenado de hashes y auditoría.

## Ejemplo de Uso Práctico (Ethics Gate)
```python
from app.ethics_gate import EthicsGate, ExperimentRequest

gate = EthicsGate()
req = ExperimentRequest(
	domain="medical_imaging",
	description="Segmentación de estudios anonimizada para validación",
	resources={"gpu_hours": 3, "memory_gb": 48},
	data_sensitivity="high",
	declared_intent="Mejorar precisión diagnóstica",
	justification="Validación prospectiva controlada con comité aprobado",
	justification_signature="usuarioX|2025-09-09"
)
decision = gate.evaluate(req)
if not decision.allowed:
	raise RuntimeError(f"Bloqueado: {decision.reason} (nivel {decision.level})")
```
El hash `decision.hash_record` puede concatenarse en el pipeline de integridad para cadena auditable.

### Política YAML y Configuración Dinámica
Puedes ajustar umbrales, dominios y niveles que requieren firma creando un archivo YAML (por defecto ruta en `ETHICS_POLICY_PATH` o pasándolo como argumento al constructor):

```yaml
thresholds:
	low: 3      # <3 => LOW
	medium: 7   # 3-6 => MEDIUM, 7-10 => HIGH
	high: 11    # >=11 => CRITICAL
domain_weights:
	medical_imaging: 5
	clinical_validation: 6
	plasma_physics: 4
signature_levels: ["HIGH", "CRITICAL"]
```

Ejemplo con política explícita y dry-run:
```python
gate = EthicsGate(policy_path="config/ethics_policy.yaml")
preview = gate.evaluate(req, dry_run=True)  # No persiste en log ni ancla
print(preview.level, preview.risk_score)
```

### Métricas Expuestas (Prometheus opcional)
Si `prometheus_client` está instalado se registran (labels: level, allowed):
- ethics_risk_events_total{level,allowed}
- ethics_overrides_total{level}
- ethics_malicious_block_total
- ethics_high_pending (Gauge)
Integra un endpoint estándar (`/metrics`) en FastAPI para exponerlas.

### Firma Digital y Cadena de Integridad
Si `cryptography` (Ed25519) está disponible se genera una clave efímera:
```python
pub = gate.export_public_key()
sig = gate.sign_chain()          # Firma hash agregado actual
assert gate.verify_chain_signature(sig)
```
Se recomienda persistir la clave privada externamente (HSM/archivo seguro) para continuidad de auditoría.

### Anclaje Merkle (Hook)
`evaluate(..., auto_anchor=True)` dispara `_try_anchor_chain()` que invoca `anchor_hook(chain_hash)` si se configuró. Integra aquí tu servicio de:
- Blockchain / notarización externa
- Registro Merkle batched
- Esquema de transparencia o third-party attest ledger

### Buenas Prácticas de Uso del Gate
- Usa `dry_run=True` en UI para mostrar al usuario por qué sería bloqueado.
- Exige longitud mínima de justificación (≥15 chars por defecto) en overrides.
- Supervisa `override_ratio` (ver sección Métricas Éticas Operacionales) para detectar abuso de firmas.
- Versiona la política YAML y aplica control de cambios / revisión.
- Implementa rotación controlada de claves Ed25519 si firmas se publican externamente.

## Roadmap Ético Ampliado
| Fase | Entrega | Métrica de Éxito |
|------|---------|------------------|
| Q4 2025 | Implementar matriz riesgo dinámica | Cobertura ≥ 90% de ejecuciones clasificadas |
| Q1 2026 | Ethics Gate configurable YAML | <5% falsos bloqueos |
| Q1 2026 | Red teaming automatizado parcial | ≥3 hallazgos accionables |
| Q2 2026 | Reporte ético generado automáticamente | Publicación mensual consistente |

## Consideraciones Ambientales
- Monitor energético (kWh/job) planificado.
- Penalización a configuraciones con >p95 consumo.
- Recomendación de lotes fuera de horas pico.

## Declaración de Limitación Adicional
Este marco mitiga riesgos pero no garantiza eliminación total de abuso. Requiere supervisión humana continua y revisión periódica de métricas y políticas.

