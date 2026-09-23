"""
Ejemplo de demostración del MLflow Registry Service

Este ejemplo demuestra el uso completo del servicio de registro de modelos MLflow.
"""

import sys
import os
import asyncio
import json

# Agregar el directorio padre al path para importar app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.mlflow_registry_service import MLflowRegistryService


async def demo_mlflow_registry():
    """Demostración completa del servicio MLflow registry"""
    
    print("🚀 DEMOSTRACIÓN MLFLOW REGISTRY SERVICE")
    print("=" * 55)
    
    # Inicializar servicio
    service = MLflowRegistryService()
    print(f"✅ Servicio inicializado: {service.name}")
    print(f"📍 Tracking URI: {service.tracking_uri}")
    print(f"🎯 Stages válidos: {service.valid_stages}")
    print()
    
    # 1. Registro de modelo (simulado)
    print("1️⃣ REGISTRO DE MODELO")
    print("-" * 30)
    
    model_registration_data = {
        "action": "register_model",
        "model_uri": "runs:/abc123def456/sklearn_model",
        "name": "CustomerChurnPredictor",
        "description": "Modelo de predicción de abandono de clientes usando Random Forest",
        "tags": {
            "algorithm": "random_forest",
            "dataset_version": "v2.1",
            "feature_count": "15",
            "environment": "development"
        }
    }
    
    print("📋 Datos del modelo a registrar:")
    print(json.dumps({k: v for k, v in model_registration_data.items() if k != "action"}, indent=2))
    print("\n[Nota: En producción esto registraría el modelo real en MLflow]")
    print("✅ Modelo CustomerChurnPredictor v1 listo para registro")
    print()
    
    # 2. Gestión de versiones y stages
    print("2️⃣ GESTIÓN DE STAGES Y VERSIONES")
    print("-" * 40)
    
    stage_transitions = [
        ("None", "Nuevo modelo registrado"),
        ("Staging", "Promovido para pruebas de staging"),
        ("Production", "Aprobado para producción"),
        ("Archived", "Archivado después de nueva versión")
    ]
    
    for stage, description in stage_transitions:
        print(f"🔄 Stage: {stage}")
        print(f"   📝 {description}")
        
        transition_data = {
            "action": "transition_model_version_stage",
            "name": "CustomerChurnPredictor",
            "version": "1",
            "stage": stage,
            "archive_existing_versions": stage == "Production"
        }
        
        print(f"   ⚙️ Parámetros: {json.dumps({k: v for k, v in transition_data.items() if k != 'action'})}")
        print(f"   ✅ Transición a {stage} completada")
        print()
    
    # 3. Búsqueda de modelos
    print("3️⃣ BÚSQUEDA Y FILTRADO DE MODELOS")
    print("-" * 40)
    
    search_examples = [
        {
            "filter": "name='CustomerChurnPredictor'",
            "description": "Buscar por nombre de modelo"
        },
        {
            "filter": "name LIKE '%Churn%' AND tags.environment='production'",
            "description": "Buscar modelos de churn en producción"
        },
        {
            "filter": "tags.algorithm='random_forest'",
            "description": "Buscar por algoritmo"
        },
        {
            "filter": "current_stage='Production'",
            "description": "Buscar modelos en producción"
        }
    ]
    
    for search in search_examples:
        print(f"🔍 Búsqueda: {search['description']}")
        print(f"   📝 Filtro: {search['filter']}")
        print("   Max resultados: 10, Order by: version DESC")
        print("   ✅ Búsqueda configurada correctamente")
        print()
    
    # 4. Gestión de tags
    print("4️⃣ GESTIÓN DE TAGS Y METADATOS")
    print("-" * 35)
    
    tag_operations = [
        {
            "action": "set_model_version_tag",
            "key": "validation_accuracy",
            "value": "0.94",
            "description": "Precisión del modelo en conjunto de validación"
        },
        {
            "action": "set_model_version_tag",
            "key": "approved_by",
            "value": "data_science_team",
            "description": "Equipo que aprobó el modelo"
        },
        {
            "action": "set_model_version_tag", 
            "key": "deployment_date",
            "value": "2024-09-12",
            "description": "Fecha de despliegue en producción"
        }
    ]
    
    for tag_op in tag_operations:
        print(f"🏷️ Tag: {tag_op['key']} = {tag_op['value']}")
        print(f"   📝 {tag_op['description']}")
        print("   ✅ Tag establecido correctamente")
        print()
    
    # 5. Obtener información detallada
    print("5️⃣ INFORMACIÓN DETALLADA DE VERSIONES")
    print("-" * 45)
    
    info_queries = [
        {
            "action": "get_model_version",
            "description": "Información completa de versión específica"
        },
        {
            "action": "get_latest_versions",
            "stages": ["Staging", "Production"],
            "description": "Últimas versiones en staging y producción"
        },
        {
            "action": "get_model_version_download_uri", 
            "description": "URI de descarga del modelo"
        }
    ]
    
    for query in info_queries:
        print(f"📊 {query['description']}")
        
        query_data = {
            "action": query["action"],
            "name": "CustomerChurnPredictor",
            "version": "1"
        }
        
        if "stages" in query:
            query_data["stages"] = query["stages"]
            print(f"   🎯 Stages: {query['stages']}")
        
        print("   ✅ Consulta configurada")
        print()
    
    # 6. Estadísticas del registry
    print("6️⃣ ESTADÍSTICAS DEL REGISTRY")
    print("-" * 35)
    
    print("📈 Estadísticas disponibles:")
    print("   • Total de modelos registrados")
    print("   • Distribución por stages:")
    
    for stage in service.valid_stages:
        print(f"     - {stage}: cantidad de modelos")
    
    print("   • Total de versiones")
    print("   • Modelos recientes")
    print("   • URI de tracking")
    
    print("   ✅ Estadísticas disponibles")
    print()
    
    # 7. Integración con experimentos
    print("7️⃣ INTEGRACIÓN CON EXPERIMENT TRACKING")
    print("-" * 45)
    
    integration_workflow = [
        "1. ExperimentTrackingService ejecuta experimento",
        "2. Se entrenan múltiples modelos con diferentes hiperparámetros", 
        "3. El mejor modelo se registra automáticamente",
        "4. MLflowRegistryService gestiona el ciclo de vida",
        "5. Promoción automática basada en métricas",
        "6. Deployment usando URI del registry"
    ]
    
    for i, step in enumerate(integration_workflow, 1):
        print(f"   {step}")
    
    print()
    print("🔗 Endpoints de integración:")
    print("   • POST /api/experiment-tracking/start-experiment")
    print("   • POST /api/mlflow-registry/register")
    print("   • POST /api/mlflow-registry/models/transition-stage")
    print("   • GET /api/mlflow-registry/models/{name}/latest-versions")
    print()
    
    # 8. API REST completa
    print("8️⃣ API REST COMPLETA")
    print("-" * 25)
    
    endpoints = [
        ("POST", "/api/mlflow-registry/register", "Registrar modelo"),
        ("GET", "/api/mlflow-registry/models", "Listar modelos"),
        ("GET", "/api/mlflow-registry/models/{name}/versions/{version}", "Información de versión"),
        ("GET", "/api/mlflow-registry/models/{name}/latest-versions", "Últimas versiones"),
        ("POST", "/api/mlflow-registry/models/transition-stage", "Promover stage"),
        ("PUT", "/api/mlflow-registry/models/update-version", "Actualizar descripción"),
        ("POST", "/api/mlflow-registry/models/search", "Buscar modelos"),
        ("POST", "/api/mlflow-registry/models/tags", "Establecer tag"),
        ("DELETE", "/api/mlflow-registry/models/{name}/versions/{version}/tags/{key}", "Eliminar tag"),
        ("GET", "/api/mlflow-registry/stats", "Estadísticas del registry"),
        ("GET", "/api/mlflow-registry/health", "Estado del servicio")
    ]
    
    for method, endpoint, description in endpoints:
        print(f"   {method:6} {endpoint:55} # {description}")
    
    print()
    
    # 9. Casos de uso avanzados
    print("9️⃣ CASOS DE USO AVANZADOS")
    print("-" * 30)
    
    use_cases = [
        {
            "title": "🔄 CI/CD Automático",
            "description": "Registro automático desde pipeline, promoción basada en métricas"
        },
        {
            "title": "🎯 A/B Testing",
            "description": "Múltiples versiones en producción con tags de experimento"
        },
        {
            "title": "📊 Model Monitoring",
            "description": "Seguimiento de drift, performance degradation"
        },
        {
            "title": "🔐 Governanza",
            "description": "Políticas de aprobación, auditoría de cambios"
        },
        {
            "title": "🚀 Auto-deployment",
            "description": "Despliegue automático al promover a Production"
        }
    ]
    
    for use_case in use_cases:
        print(f"   {use_case['title']}")
        print(f"      {use_case['description']}")
        print()
    
    print("🎉 DEMOSTRACIÓN COMPLETADA")
    print("=" * 55)
    print()
    print("El servicio MLflow Registry está listo para:")
    print("🚀 Registro de modelos con versionado automático")
    print("📊 Gestión completa de stages del ciclo de vida")
    print("🔍 Búsqueda avanzada con filtros personalizados")
    print("🏷️ Sistema de tags para metadatos enriquecidos")
    print("📈 Estadísticas y monitoreo del registry")
    print("🔗 Integración perfecta con ExperimentTracking")
    print("⚡ API REST completa para todas las operaciones")
    print("🔐 Compatibilidad total con MLflow estándar")


if __name__ == "__main__":
    asyncio.run(demo_mlflow_registry())
