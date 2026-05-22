# Seguridad e Integridad - AXIOM META 4 (MVP Consolidación)

## Objetivos
Unificar controles dispersos (blockchain, verificación de integridad, gating ético) en una capa clara y extensible.

## Componentes Actuales
- `app/blockchain_validation.py`: Validación distribuida (simulada) + firmas.
- `app/integrity_verification.py`: Chequeos locales/comprehensive + registros.
- `app/integrity_core.py`: Nuevo núcleo unificado de artefactos + anclaje opcional blockchain.
- `app/ethics_gate.py`: Heurística ética base + scoring de riesgo.
- `app/risk_assessment.py`: Capa combinada ética + reglas dominio (bio/chem/clinical/materials).
- `app/service_registry.py`: Descubrimiento de servicios para futuras políticas per‑servicio.

## Riesgos Identificados (Primer Barrido)
| Riesgo | Descripción | Mitigación MVP | Futuro |
|--------|-------------|----------------|--------|
| Hashing duplicado | Cálculo de hash en múltiples módulos | Centralizar en `integrity_core` | API hashing estable + versionado | 
| Umbrales fijos | Thresholds hardcoded ética | Política YAML opcional | Sistema de políticas versionadas | 
| Falta de provenance unificado | Artefactos sin lineage | Campo preparado en core (pendiente) | Grafo + DOI interno | 
| Validación blockchain simulada | Firmas locales no distribuidas | Marcado como experimental | Red p2p / firmas reales por nodo | 
| Ausencia de circuit breakers | Servicios intensivos sin aislamiento | Registry base | Scheduler + límites de recursos | 
| Falta de autenticación robusta | Endpoints abiertos (revisar) | Security auditor base | OAuth2 / API Keys rotación | 

## Flujos Clave
1. Registro artefacto -> hashes (data + metadata) -> (opcional) anclaje blockchain asíncrono.
2. Verificación artefacto -> comparación hash + validación blockchain + chequeo integridad básico.
3. Evaluación riesgo experimento -> EthicsGate -> reglas dominio -> resultado unificado.

## Uso Rápido (Código)
```python
from app.integrity_core import integrity_core
rec = integrity_core.register_artifact({"result": [1,2,3]}, artifact_type="result", metadata={"model_type":"pinn"}, blockchain=True)
status = asyncio.run(integrity_core.verify_artifact(rec.artifact_id))
```

## Política de Reporte de Vulnerabilidades
- Enviar informe reproducible (PoC, impacto, versión) a: security@axiom.local (placeholder)
- Tiempo objetivo de primera respuesta: 72h
- Divulgación responsable: se recomienda ventana 90 días

## Roadmap de Hardening
1. Firmas reales por nodo + rotación de claves.
2. Lineage / provenance (parent-child) + DOI interno (`axiom:year:hash`).
3. Circuit breakers + timeouts adaptativos por servicio crítico.
4. Scheduler consciente de prioridad + cuotas GPU/CPU.
5. Políticas éticas dinámicas (YAML firmadas) + auditoría Merkle.
6. Módulo de secretos (KMS) y escaneo de fugas.
7. Integración completa en paquete de publicación (`/publications/{uuid}/`).

## Métricas Iniciales Propuestas
| Métrica | Fuente | Objetivo |
|---------|--------|----------|
| % artefactos con prueba blockchain | integrity_core | >30% fase inicial |
| Tiempo verificación básica | integrity_core | <150ms |
| Riesgos bloqueados (HIGH/CRITICAL) | risk_assessment | 100% sin firma válida |
| Cobertura servicios en registry | service_registry | >80% archivos *_service.py |

## Limitaciones Conocidas
- Blockchain no resistente a ataques (modo simulación).
- No se persiste a almacenamiento externo (memoria en ejecución).
- Sin autenticación de usuarios final implementada en este MVP.

## Contribuir
1. Añadir nueva verificación -> extender `IntegrityCore`.
2. Añadir nuevas reglas riesgo -> modificar `risk_assessment.py`.
3. Documentar cambios de seguridad en este archivo.

---
`Última actualización`: auto-generado fase consolidación inicial.
