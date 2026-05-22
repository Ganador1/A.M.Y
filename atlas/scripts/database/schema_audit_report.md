# Reporte de Auditoría de Schema Drift - ROADMAP 6
# Fecha: 2025-09-30

## Estado Actual
- **Migraciones existentes:** 2 archivos
  - 2025_09_01_2147-f905ab334d30_initial_migration_create_all_axiom_.py
  - 2025_09_02_1010-0b1c2d3e4f56_add_workflows_v1_1.py

- **Archivos de modelos:** 19 archivos identificados
  - database_models.py (18 tablas principales)
  - workflow_persistence_models.py (3 tablas de workflows)
  - hypothesis_models.py (1 tabla identificada)
  - protgpt2_models.py (7 tablas identificadas)
  - experiment_scheduler_models.py (1 tabla identificada)
  - plausibility_models.py (1 tabla identificada)

## Problemas Identificados
1. **Schema Drift Detectado:** El script de autogeneración no detectó cambios, posiblemente porque no todos los modelos están registrados en env.py
2. **Modelos No Incluidos:** Muchos archivos de modelos no están siendo incluidos en las migraciones
3. **Falta de Sincronización:** Hay 19 archivos de modelos pero solo 2 migraciones

## Modelos Identificados por Archivo

### database_models.py (18 tablas):
- users, user_sessions, calculations, cached_results, system_metrics
- error_logs, api_request_logs, scientific_datasets, knowledge_nodes
- knowledge_relations, scientific_concepts, cross_domain_mappings
- evaluation_records, decision_ledger_entries, claim_records
- paper_quality_metrics, peer_review_records, claim_relations

### workflow_persistence_models.py (3 tablas):
- workflows, workflow_steps, workflow_step_executions

### hypothesis_models.py (1 tabla):
- hypothesis (identificada pero no revisada completamente)

### Otros archivos con tablas identificadas:
- protgpt2_models.py (7 tablas)
- experiment_scheduler_models.py (1 tabla)
- plausibility_models.py (1 tabla)

## Próximos Pasos
1. Actualizar env.py de Alembic para incluir todos los modelos
2. Generar nueva migración comprehensiva
3. Aplicar migración en ambiente de desarrollo
4. Verificar integridad de datos
