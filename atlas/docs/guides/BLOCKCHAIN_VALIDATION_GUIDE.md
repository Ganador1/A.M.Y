# AXIOM META 4 - Blockchain Validation & Integrity Assurance Guide

## 1. Propósito
Garantizar integridad, trazabilidad y autenticidad criptográfica de resultados científicos (especialmente PINN y workflows avanzados) mediante:
- Validación distribuida (simulada) estilo blockchain
- Hashing determinístico de resultados y metadatos
- Auditoría de integridad multicapa (local + estadística + blockchain + continua)
- Verificación externa vía API segura

## 2. Componentes Clave
| Componente | Archivo | Rol | Output Principal |
|------------|---------|-----|------------------|
| BlockchainValidationService | `app/blockchain_validation.py` | Valida y registra resultados con consenso y PoW ligero | Bloques + pruebas de validación |
| IntegrityVerificationService | `app/integrity_verification.py` | Verifica integridad local y distribuida | Registros y auditorías |
| Security Auditor | `app/security.py` | Registra eventos de seguridad | Eventos estructurados |
| PINN Result Hashing | `create_pinn_result_hash` | Generación de huellas criptográficas | SHA-256 reproducible |

## 3. Flujo de Validación (Resumen)
1. Servicio científico genera resultado PINN / modelo avanzado
2. Se solicita validación: `/api/blockchain/validate`
3. Se crea `PINNResult` + hash determinístico
4. Nodos validadores (simulados) generan firmas + PoW -> `ValidationBlock`
5. Resultado puede verificarse externamente con hash/proof -> `/api/blockchain/verify`
6. IntegrityVerificationService ejecuta auditoría adicional (estadística + blockchain opcional)
7. Monitoreo continuo detecta anomalías y genera alertas

```
+-------------------+     +---------------------+     +-----------------------+
| Scientific Result | --> | BlockchainValidation| --> | Validation Block Store|
+-------------------+     +---------------------+     +-----------+-----------+
          |                            |                           |
          v                            v                           v
  Integrity Verification -----> Auditorías -----> Continuous Monitoring
```

## 4. Modelo de Datos Principal
### PINNResult
```json
{
  "result_id": "uuid",
  "model_type": "pinn",
  "pde_type": "heat",
  "input_parameters": {...},
  "output_data": {"solution": [...], "error": 0.001},
  "confidence_score": 0.95,
  "execution_time": 1.23,
  "timestamp": "ISO8601",
  "node_id": "validator-node",
  "version": "1.0"
}
```
### ValidationBlock
- previous_hash, consensus_hash, validator_nodes, signatures, nonce, difficulty

### IntegrityRecord
- Métodos: basic | statistical | comprehensive | blockchain
- Campos críticos: `integrity_status` (valid|warning|compromised), `confidence_score`

## 5. Endpoints Disponibles
| Endpoint | Método | Descripción | Auth |
|----------|--------|-------------|------|
| `/api/blockchain/validate` | POST | Inicia validación blockchain | Bearer |
| `/api/blockchain/verify` | POST | Verifica hash contra cadena | Bearer |
| `/api/blockchain/stats` | GET | Métricas de consenso y red | Bearer |
| `/api/blockchain/blocks` | GET | Últimos bloques | Bearer |
| `/api/integrity/verify` | POST | Verificación local/distribuida | Bearer |
| `/api/integrity/audit` | POST | Auditoría completa | Bearer |
| `/api/integrity/stats` | GET | Métricas de integridad | Bearer |
| `/api/integrity/records/{id}` | GET | Historial verificación | Bearer |

## 6. Ejemplos de Uso
### Validar un resultado PINN
```bash
curl -X POST http://localhost:8001/api/blockchain/validate \
 -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
 -d '{
  "result_id":"res_123",
  "model_data": {
    "model_type":"pinn",
    "pde_type":"heat",
    "input_parameters": {"alpha":0.01},
    "output_data": {"solution":[0.1,0.2,0.3], "error":0.001},
    "confidence_score":0.95,
    "execution_time":1.2
  },
  "validator_count":3
 }'
```
### Verificar integridad (comprehensive)
```bash
curl -X POST http://localhost:8001/api/integrity/verify \
 -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
 -d '{"result_id":"res_123","verification_method":"comprehensive","include_metadata":true}'
```

## 7. Estrategia de Integridad Multicapa
| Capa | Método | Objetivo | Riesgo Mitigado |
|------|--------|----------|-----------------|
| Hash Determinístico | SHA-256 | Trazabilidad | Manipulación local |
| Validación Distribuida | Firmas + PoW ligero | Consenso | Alteración no autorizada |
| Verificación Estadística | Monotonicidad, rangos | Coherencia física | Resultados espurios |
| Auditorías Programadas | `/audit` | Revisión histórica | Degradación progresiva |
| Monitoreo Continuo | Tarea asíncrona | Detección temprana | Compromisos silenciosos |

## 8. Modelo de Amenazas (Resumen)
| Amenaza | Vía | Mitigación Actual | Futuro |
|---------|-----|------------------|--------|
| Alteración de resultados | Almacenamiento local | Hash + revalidación | Ledger externo opcional |
| Firmas falsas | Simulación local | Clave RSA central | Rotación + PKI distribuida |
| Reorganización cadena | Reescritura PoW | Dificultad + timestamp | Anchor externo periódico |
| Ataques replay | Reuso de hash | Timestamp + result_id | Nonces externos |

## 9. Métricas Clave
- `total_blocks`, `total_validations`, `active_validators`
- `integrity_rate`, `compromised_records`
- `consensus_threshold`, `current_difficulty`

## 10. Integración con Otros Servicios
| Servicio | Uso | Beneficio |
|----------|-----|-----------|
| Scientific AI (PINN) | Validar soluciones PDE | Confianza reproducible |
| Monitoring | Alertas en compromisos | Respuesta temprana |
| Security Auditor | Eventos firmados | Trazabilidad forense |
| Distributed Scaling | Replicar validadores | Resiliencia |

## 11. Roadmap Evolutivo
| Fase | Mejora | Estado |
|------|--------|--------|
| 1 | PoW Ligero + Firmas | Implementado |
| 2 | Registro Merkle por bloque | Pendiente |
| 3 | Validadores remotos reales | Pendiente |
| 4 | Anclaje en blockchain pública (opcional) | Evaluación |
| 5 | Pruebas formales de consistencia | Pendiente |

## 12. Buenas Prácticas
- Usar `result_id` estable y semántico cuando sea posible
- Validar antes de publicar resultados críticos
- Programar auditorías periódicas (cron / scheduler)
- Monitorear `integrity_rate` < 0.9 => investigación inmediata

## 13. Resumen Ejecutivo
Este módulo establece la columna vertebral de confianza de AXIOM META 4: asegura que cada resultado científico es verificable, trazable y resistente a manipulación. Sienta bases para futura federación, compliance regulatoria y auditoría externa.

---
**Estado**: Activo | **Madurez**: Intermedia (PoC robusto) | **Prioridad Próxima**: Merkle + validadores distribuidos.
