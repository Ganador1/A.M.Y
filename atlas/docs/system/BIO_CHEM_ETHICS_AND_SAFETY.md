# Controles Éticos y de Seguridad para Módulos de Biología y Química

Este anexo complementa `ETHICS_AND_SAFETY.md` enfocándose en dominios de mayor potencial de riesgo dual-use o bioseguridad: biología computacional, genómica, química computacional, dinámica molecular y redes metabólicas.

## 1. Dominios y Riesgos Específicos
| Dominio | Riesgos Principales | Clasificación Base | Ejemplos de Abuso | Medida Mitigación Primaria |
|---------|---------------------|--------------------|-------------------|----------------------------|
| computational_biology | Reconstrucción neural, modelado ecosistemas | Alto | Modelos extrapolados a manipulación ecosistemas | Limitación de escala, revisión humana |
| genomics | Datos sensibles, re-identificación | Muy Alto | Inferir identidad o variantes privadas | Anonimización, hashing irreversible |
| metabolic_networks | Optimización de rutas biosintéticas | Muy Alto | Diseño bioquímico no autorizado | Requerir propósito legítimo firmado |
| neuro_simulation | Modelos masivos recursos | Alto | Uso para entrenamiento esquemas adversarios | Cuotas GPU y validación objetivo |
| computational_chemistry | Propiedades moleculares | Medio-Alto | Triaging moléculas sensibles | Límite de screening automatizado |
| quantum_chemistry | Energías precisión | Alto | Diseño acelerado materiales sensibles | Restricción basis set avanzados |
| molecular_dynamics | Preparar sistemas complejos | Alto | Simulación replicación viral (riesgo) | Taxonomía de exclusión patrones |
| systems_biology | Modelado integral | Muy Alto | Escenarios manipulación multivía | Firma múltiple (4-eyes) |
| synthetic_biology | Diseño constructos | Crítico | Construcción/agente biológico | Bloqueo por defecto + whitelist |
| biosecurity_assessment | Evaluación vulnerabilidades | Crítico | Identificación vectores ataque biológico | Aislamiento + logging reforzado |

## 2. Política YAML (Pesos de Dominio)
Los pesos añadidos en `config/ethics_policy.yaml` elevan más rápido a niveles HIGH/CRITICAL para dominios sensibles. Ajustar bajo gobernanza: cambios requieren aprobación dual (Lead Científico + Oficial Cumplimiento).

## 3. Escalamiento de Controles
| Nivel Riesgo | Requisito Bio/Química | Controles Adicionales |
|--------------|-----------------------|-----------------------|
| LOW | Operaciones analíticas triviales | Logging estándar |
| MEDIUM | Descriptores básicos, alineamientos | Límites parámetros, sampling reducido |
| HIGH | Screening molecular amplio, simulación MD > corto | Firma simple + justificación ≥15 chars |
| CRITICAL | Genómica sensible, synthetic_biology, network design optimizado | Firma dual, posible veto, auditoría diaria |

## 4. Patrón de Integración Ethics Gate
Pseudocódigo recomendado antes de ejecutar tarea sensible:
```python
from app.ethics_gate import EthicsGate, ExperimentRequest

gate = EthicsGate(policy_path="config/ethics_policy.yaml")

req = ExperimentRequest(
    domain="genomics",
    description="Análisis regulatorio de red génica anonimizada",
    resources={"gpu_hours": 2, "memory_gb": 32},
    data_sensitivity="high",
    declared_intent="Investigar regulación epigenética en cohortes públicas",
    justification="Proyecto aprobado IRB #2025-AG-17 con anonimización completa",
    justification_signature="investigadorA|2025-09-09"
)
decision = gate.evaluate(req, auto_anchor=True)
if not decision.allowed:
    raise PermissionError(f"Bloqueado: {decision.reason}")
```

## 5. Límites Operacionales Recomendados
| Parámetro | Sugerencia Hard Limit | Racional |
|-----------|-----------------------|----------|
| num_neurons (Brian2) | ≤ 50k | Evitar abuso recursos / escalado masivo sin revisión |
| genome sequence length análisis | ≤ 3e7 bases por job | Evitar datasets humanos completos no aprobados |
| conformers per molecule | ≤ 100 | Limitar búsqueda intensiva potencial screening masivo |
| quantum basis set | Restringir a sto-3g / 6-31g* en modo estándar | Evitar cálculos de alta precisión no supervisados |
| MD box atoms | ≤ 150k | Control de coste y superficie ataque |
| metabolic reactions (modelo) | ≤ 5000 | Identificar ampliaciones sospechosas |

Superar hard limit → elevar a CRITICAL y exigir doble firma.

## 6. Patrón de Detección de Uso Dual (Heurística)
Indicadores combinados (si ≥2 → elevar HIGH mínimo):
1. Palabras clave: "optimizar ruta biosintética", "constructo sintético", "ensamblaje viral".
2. Solicitud parámetros por encima percentil 95 histórico.
3. Secuencias con longitud > umbral genómico humano parcial.
4. Repetición de jobs similares (screening iterativo) en <24h.
5. Mezcla de dominios (genomics + synthetic_biology) en misma sesión.

## 7. Métricas Adicionales Específicas
| Métrica | Descripción | Acción |
|---------|-------------|--------|
| bio_high_jobs_total | Jobs HIGH/CRITICAL bio/química | Revisar semanal |
| dual_use_flags_total | Detecciones heurísticas | Auditoría inmediata |
| synthetic_blocked_total | Bloqueos synthetic_biology | Confirmar legitimidad |
| md_large_box_attempts | Intentos superar límite átomos | Ajustar política |

## 8. Reglas de Sanitización
- Nunca almacenar secuencias crudas si pertenecen a sujetos identificables.
- Hash SHA-256 + truncado (primeros 12 bytes) para tracking no reversible.
- Remover metadatos geográficos / demográficos antes de análisis.

## 9. Checklist Pre-Ejecución CRÍTICA
- [ ] Justificación ≥ 50 caracteres
- [ ] Firma dual registrada
- [ ] Hash de solicitud anclado
- [ ] Validación IRB / Comité Ético (ID referencia)
- [ ] Parámetros dentro de límites aprobados
- [ ] Plan de eliminación/retención datos

## 10. Futuras Extensiones
| Idea | Beneficio |
|------|-----------|
| Escáner de secuencias prohibidas (BLAST DB restrictiva) | Bloqueo automático patrones sensibles |
| Clasificador ML de riesgo textual | Reducción falsos negativos intención |
| Firma multi-parte (threshold signatures) | Mayor robustez auditoría |
| Registro WORM externo | Evidencia no repudiable |

## 11. Declaración
Las capacidades aquí descritas tienen fines de investigación legítima. Cualquier intento de uso indebido (bioseguridad, síntesis ilícita, explotación regulatoria) debe ser bloqueado y reportado a la autoridad interna de cumplimiento.

## 12. Mejores Prácticas Internacionales (Síntesis)

Basado en lineamientos de organismos regulatorios y científicos líderes, esta sección consolida estándares reconocidos para investigación responsable en biología y química computacional.

### 12.1 Marco NIH (National Institutes of Health) - Estados Unidos
| Principio | Aplicación Bio/Chem Computacional |
|-----------|-----------------------------------|
| Rigor Científico | Validación experimental de resultados computacionales antes de publicación |
| Transparencia | Código y datos abiertos (cuando sea seguro); metodología reproducible |
| Responsabilidad Social | Consideración de impacto dual-use y beneficio social |
| Protección Participantes | Anonimización estricta de datos genómicos/médicos |

### 12.2 WHO/OMS - Ética en Investigación de Salud
| Directriz | Implementación Sugerida |
|-----------|-------------------------|
| Consentimiento Informado | Disclaimer claro sobre limitaciones diagnósticas de modelos |
| Minimización Riesgo | Límites computacionales para evitar sobreinterpretación |
| Justicia Distributiva | Acceso equitativo a herramientas; evitar sesgos algorítmicos |
| Beneficencia | Priorizar aplicaciones terapéuticas vs. comerciales sensibles |

### 12.3 GA4GH (Global Alliance for Genomics and Health)
| Framework | Control Específico |
|-----------|-------------------|
| FAIR Principles | Datos Findable, Accessible, Interoperable, Reusable con metadatos éticos |
| Privacy by Design | Técnicas de privacidad diferencial en análisis poblacionales |
| International Standards | Cumplimiento GDPR/HIPAA según jurisdicción |
| Federated Learning | Evitar centralización de datos sensibles |

### 12.4 OECD - Responsible Innovation
| Pilar | Métrica/Proceso |
|-------|----------------|
| Anticipación | Evaluación prospectiva de riesgos emergentes (ej. edición genómica) |
| Inclusión | Consulta multi-stakeholder para aplicaciones controvertidas |
| Reflexividad | Revisión periódica de políticas ante avances tecnológicos |
| Adaptabilidad | Frameworks flexibles que evolucionan con el campo |

### 12.5 NSABB (National Science Advisory Board for Biosecurity) - Dual Use
| Categoría Dual-Use | Señal de Alerta | Mitigación |
|---------------------|-----------------|------------|
| Información Peligrosa | Metodología exacta para síntesis patogénica | Publicación con omisiones técnicas críticas |
| Tecnología Sensible | Herramientas de diseño automatizado de agentes | Restricción acceso + whitelist institucional |
| Datos de Riesgo | Genomas completos de patógenos | Acceso controlado vía IRB/comités |
| Capacidades Emergentes | IA que acelera diseño de amenazas | Pausa desarrollo hasta marcos regulatorios |

### 12.6 ELIXIR - Infraestructura Datos Biológicos Europa
| Estándar | Aplicación |
|----------|------------|
| Data Stewardship | Planes de gestión de datos con consideraciones éticas |
| Interoperabilidad | APIs seguras que preservan privacidad |
| Training & Outreach | Educación continua en ética de datos biológicos |
| Compliance Monitoring | Auditorías regulares de adherencia a políticas |

### 12.7 Síntesis de Recomendaciones Adoptadas

**Controles Técnicos:**
- Anonimización irreversible (hashing + salt) antes de análisis.
- Límites automáticos de parámetros que puedan revelar información sensible.
- Logging exhaustivo con timestamping para auditoría externa.
- Sandboxing de experimentos de alto riesgo.

**Controles Procedimentales:**
- Revisión ética prospectiva (no solo reactiva) para nuevas capacidades.
- Documentación de limitaciones y disclaimers en todas las salidas.
- Entrenamiento obligatorio del personal en bioseguridad computacional.
- Protocolos de incident response específicos para brechas de datos biológicos.

**Controles de Gobernanza:**
- Comité interdisciplinario (científicos, éticos, legales, seguridad).
- Revisión externa anual por auditor independiente.
- Políticas de whistleblowing para reportar uso indebido.
- Coordinación con autoridades regulatorias nacionales cuando aplicable.

### 12.8 Adaptación al Ethics Gate
Los principios anteriores se mapean a nuestra implementación:
- **Scoring heurístico** incorpora elementos de anticipación (OECD) y categorización dual-use (NSABB).
- **Política YAML** permite adaptabilidad sin recompilación de código.
- **Firma digital** provee no-repudio para decisiones críticas.
- **Anclaje Merkle** facilita auditoría externa (ELIXIR).
- **Métricas** permiten monitoreo continuo de adherencia (WHO).

**Pendiente de Implementación Futura:**
- Federated Learning hooks para análisis sin centralización de datos.
- Privacy-preserving computation (ej. computación homomórfica).
- Integración con IRB/comités éticos institucionales.
- Dashboard de transparencia para stakeholders externos.

## 13. Protección de Proyectos Open Source Bio/Química

### 13.1 El Dilema del Código Abierto en Ciencias de la Vida
Los proyectos de código abierto en biología y química enfrentan el desafío de **promover transparencia científica** mientras **minimizan riesgos de uso dual**. No existe solución perfecta, pero se han desarrollado estrategias de mitigación.

### 13.2 Mecanismos de Protección Establecidos

#### A) **Screening de Contribuidores**
| Estrategia | Implementación | Ejemplos |
|------------|----------------|----------|
| Whitelist institucional | Solo organizaciones académicas/gubernamentales verificadas | BioConductor, NCBI tools |
| Verificación identidad | Requerir ORCID + afiliación institucional | Galaxy Project, ELIXIR |
| Proceso de vetting | Revisión manual de nuevos contribuidores por maintainers | OpenMM, RDKit |

#### B) **Limitación Funcional (Safeguarding)**
| Técnica | Descripción | Aplicación |
|---------|-------------|-----------|
| Parámetros acotados | Hard limits en rangos de entrada | Limitar tamaño genoma, basis sets |
| Módulos separados | Funcionalidad sensible en paquetes aparte | PyMOL vs. PyMOL-PSI |
| Deprecation gradual | Eliminar funciones problemáticas en versiones futuras | Sunset APIs peligrosas |

#### C) **Ofuscación Selectiva**
| Método | Pros | Contras | Uso Recomendado |
|--------|------|---------|-----------------|
| Algoritmos incompletos | Preserva IP crítica | Reduce reproducibilidad | Métodos propietarios validación |
| Datos sintéticos | Evita exposición real | Menor precisión | Demos y tutoriales |
| Abstracciones | Oculta implementación | Limita personalización | APIs nivel alto |

#### D) **Licencias Restrictivas**
| Licencia | Restricciones | Aplicabilidad Bio/Chem |
|----------|---------------|------------------------|
| Academic-only | Solo uso no comercial/educativo | Algoritmos experimentales |
| No-derivatives | Prohibe modificaciones | Software diagnóstico validado |
| Geographical | Restricción por país/región | Cumplimiento ITAR/EAR |
| Field-of-use | Limita dominio aplicación | "Solo investigación básica" |

### 13.3 Estrategias por Tipo de Riesgo

#### **Bioseguridad (Patógenos/Toxinas)**
- **Screening de secuencias**: Comparar contra listas de organismos restringidos (Australia Group, CDC)
- **Fragmentación**: Publicar solo subsecuencias no funcionales
- **Delayed release**: Embargo temporal hasta revisión por biosafety boards
- **Watermarking**: Marcas detectables en secuencias generadas

#### **Química Dual-Use (Explosivos/Venenos)**
- **Descriptor filtering**: Omitir propiedades como toxicidad/energía detonación
- **Synthesis pathway obscuration**: No publicar rutas completas de síntesis
- **Precursor monitoring**: Alertar sobre compuestos en listas de control
- **Collaborative filtering**: Crowd-sourcing de detección de uso malicioso

#### **Propiedad Intelectual Sensible**
- **Clean room implementations**: Reimplementar algoritmos sin código original
- **Differential privacy**: Ruido controlado en resultados de screening
- **Federated approaches**: Modelo distribuido sin centralizar datos
- **Homomorphic computation**: Análisis sin revelar inputs

### 13.4 Casos de Estudio Conocidos

#### **OpenEye OMEGA (Conformer Generation)**
- Licencia académica gratuita con limitaciones comerciales
- API pública pero algoritmos core propietarios
- Límites automáticos en número de conformers para usuarios no verificados

#### **GROMACS/OpenMM (Molecular Dynamics)**
- Código completamente abierto PERO documentación limitada para parámetros avanzados
- Comunidad auto-regula usos problemáticos via mailing lists
- Integración con HPC requiere credenciales institucionales

#### **BioPython (Sequence Analysis)**
- Funciones de búsqueda en bases de datos requieren claves API
- Limitación de tasa automática para prevenir scraping masivo
- Documentación incluye advertencias éticas prominentes

### 13.5 Implementación Sugerida para AXIOM

#### **Nivel 1: Controles Técnicos**
```python
# Ejemplo: Screening automático en computational_chemistry
RESTRICTED_PATTERNS = [
    "(?i).*explosive.*",
    "(?i).*toxin.*synthesis.*",
    "(?i).*bioweapon.*"
]

def screen_description(desc: str) -> bool:
    import re
    for pattern in RESTRICTED_PATTERNS:
        if re.search(pattern, desc):
            return False  # Bloquear
    return True
```

#### **Nivel 2: Restricciones de Acceso**
- **Soft limits**: Usuarios anónimos → funcionalidad básica
- **Verified users**: Afiliación académica → acceso completo
- **Trusted contributors**: Track record → funciones experimentales

#### **Nivel 3: Transparencia Controlada**
- **Audit logs públicos**: Hash de solicitudes (sin contenido)
- **Community reporting**: Mecanismo para reportar uso sospechoso
- **Regular reviews**: Revisión trimestral de patrones de uso

### 13.6 Limitaciones de Protección Open Source

**❌ No Se Puede Prevenir Completamente:**
- Fork malicioso del código
- Ingeniería inversa de algoritmos
- Uso por actores estatales/criminales
- Combinación con otras herramientas para crear capacidades peligrosas

**✅ Sí Se Puede Mitigar:**
- Acceso masivo automatizado
- Uso accidental por investigadores legítimos
- Proliferación a usuarios no sofisticados
- Falta de trazabilidad para auditorías

### 13.7 Recomendaciones Finales

1. **Transparencia gradual**: Funcionalidad básica abierta, avanzada restringida
2. **Community engagement**: Involucrar comunidad en auto-regulación
3. **Legal compliance**: Alineación con regulaciones nacionales/internacionales
4. **Continuous monitoring**: Alertas automáticas para patrones anómalos
5. **Responsible disclosure**: Protocolos para reportar vulnerabilidades encontradas

#### **Para AXIOM Específicamente:**
- Implementar `EthicsGate` como capa de protección mínima
- Considerar licencia dual (open core + enterprise)
- Documentar claramente limitaciones y disclaimers
- Establecer process de community review para nuevas capacidades sensibles
- Colaborar con organizaciones internacionales (GA4GH, OECD) para alineación de estándares

---
Maintainer: Comité Ético AXIOM – Revisión mínima trimestral.
