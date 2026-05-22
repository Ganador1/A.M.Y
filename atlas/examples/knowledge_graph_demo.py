"""
Ejemplo funcional completo del Knowledge Graph Service

Demuestra todas las capacidades del servicio centralizado de knowledge graph:
- Creación de nodos de conocimiento
- Establecimiento de relaciones
- Búsqueda avanzada
- Extracción de subgrafos
- Análisis estadístico

Author: AXIOM Development Team
Date: September 12, 2025
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.knowledge_graph_service import KnowledgeGraphService


async def knowledge_graph_demo():
    """
    Demostración completa del Knowledge Graph Service
    """
    print("🌐 === AXIOM Knowledge Graph Service Demo ===")
    print()
    
    # Initialize service
    kg_service = KnowledgeGraphService()
    print(f"✅ Servicio inicializado: {kg_service.name} v{kg_service.version}")
    print(f"📋 Tipos de nodos válidos: {len(kg_service.valid_node_types)}")
    print(f"🔗 Tipos de relaciones válidas: {len(kg_service.valid_relation_types)}")
    print()
    
    # === DEMO 1: CREATE KNOWLEDGE NODES ===
    print("🆕 DEMO 1: Creación de nodos de conocimiento")
    print("-" * 50)
    
    # Create hypothesis node
    hypothesis_request = {
        "action": "create_node",
        "name": "Quantum Entanglement in Superconductors",
        "type": "hypothesis",
        "domain": "quantum_physics",
        "properties": {
            "description": "Hypothesis that quantum entanglement plays a role in high-temperature superconductivity",
            "confidence_level": "medium",
            "experimental_support": "preliminary"
        },
        "confidence_score": 0.7,
        "source_papers": ["arxiv:2023.12345", "doi:10.1038/nature.2023.001"],
        "created_by": None  # Using None since created_by is an integer FK to users table
    }
    
    hypothesis_result = await kg_service.process_request(hypothesis_request)
    if hypothesis_result["success"]:
        hypothesis_id = hypothesis_result["node_id"]
        print(f"✅ Hipótesis creada con ID: {hypothesis_id}")
        print(f"   Nombre: {hypothesis_result['node']['name']}")
        print(f"   Confianza: {hypothesis_result['node']['confidence_score']}")
    else:
        print(f"❌ Error creando hipótesis: {hypothesis_result['error']}")
        hypothesis_id = 1  # Mock for demo continuation
    
    # Create method node
    method_request = {
        "action": "create_node",
        "name": "BCS Theory Analysis",
        "type": "method",
        "domain": "quantum_physics",
        "properties": {
            "description": "Bardeen-Cooper-Schrieffer theory application to superconductor analysis",
            "complexity": "high",
            "computational_requirements": "advanced"
        },
        "confidence_score": 0.9,
        "source_papers": ["doi:10.1103/PhysRev.108.1175"],
        "created_by": None  # Using None since created_by is an integer FK to users table
    }
    
    method_result = await kg_service.process_request(method_request)
    if method_result["success"]:
        method_id = method_result["node_id"]
        print(f"✅ Método creado con ID: {method_id}")
        print(f"   Nombre: {method_result['node']['name']}")
        print(f"   Confianza: {method_result['node']['confidence_score']}")
    else:
        print(f"❌ Error creando método: {method_result['error']}")
        method_id = 2  # Mock for demo continuation
    
    # Create material node
    material_request = {
        "action": "create_node",
        "name": "YBCO Superconductor",
        "type": "material",
        "domain": "materials_science",
        "properties": {
            "description": "Yttrium Barium Copper Oxide high-temperature superconductor",
            "critical_temperature": "93K",
            "crystal_structure": "perovskite"
        },
        "confidence_score": 0.95,
        "source_papers": ["doi:10.1103/PhysRevLett.58.908"],
        "created_by": None  # Using None since created_by is an integer FK to users table
    }
    
    material_result = await kg_service.process_request(material_request)
    if material_result["success"]:
        material_id = material_result["node_id"]
        print(f"✅ Material creado con ID: {material_id}")
        print(f"   Nombre: {material_result['node']['name']}")
    else:
        print(f"❌ Error creando material: {material_result['error']}")
        material_id = 3  # Mock for demo continuation
    
    print()
    
    # === DEMO 2: CREATE KNOWLEDGE RELATIONS ===
    print("🔗 DEMO 2: Establecimiento de relaciones")
    print("-" * 50)
    
    # Relation 1: Hypothesis tests Material
    relation1_request = {
        "action": "create_relation",
        "subject_id": hypothesis_id,
        "object_id": material_id,
        "predicate": "tests",
        "strength": 0.8,
        "context": {
            "experiment_type": "theoretical_analysis",
            "validation_method": "quantum_simulation"
        },
        "evidence_papers": ["arxiv:2023.12346"],
        "created_by": None  # Using None since created_by is an integer FK to users table
    }
    
    relation1_result = await kg_service.process_request(relation1_request)
    if relation1_result["success"]:
        print(f"✅ Relación 1 creada: Hipótesis --[tests]--> Material")
        print(f"   Fuerza: {relation1_result['relation']['strength']}")
    else:
        print(f"❌ Error en relación 1: {relation1_result['error']}")
    
    # Relation 2: Method supports Hypothesis
    relation2_request = {
        "action": "create_relation",
        "subject_id": method_id,
        "object_id": hypothesis_id,
        "predicate": "supports",
        "strength": 0.9,
        "context": {
            "theoretical_framework": "BCS_analysis",
            "validation_status": "strong"
        },
        "evidence_papers": ["doi:10.1103/PhysRev.108.1175"],
        "created_by": None  # Using None since created_by is an integer FK to users table
    }
    
    relation2_result = await kg_service.process_request(relation2_request)
    if relation2_result["success"]:
        print(f"✅ Relación 2 creada: Método --[supports]--> Hipótesis")
        print(f"   Fuerza: {relation2_result['relation']['strength']}")
    else:
        print(f"❌ Error en relación 2: {relation2_result['error']}")
    
    print()
    
    # === DEMO 3: SEARCH KNOWLEDGE NODES ===
    print("🔍 DEMO 3: Búsqueda avanzada de nodos")
    print("-" * 50)
    
    # Search by domain
    search_request = {
        "action": "search_nodes",
        "query": "quantum",
        "domain": "quantum_physics",
        "min_confidence": 0.5,
        "limit": 10,
        "offset": 0
    }
    
    search_result = await kg_service.process_request(search_request)
    if search_result["success"]:
        print(f"✅ Búsqueda completada: {search_result['returned_count']} nodos encontrados")
        for node in search_result["nodes"]:
            print(f"   • {node['name']} ({node['type']}) - Confianza: {node['confidence_score']}")
    else:
        print(f"❌ Error en búsqueda: {search_result['error']}")
    
    print()
    
    # === DEMO 4: GET DETAILED NODE ===
    print("📊 DEMO 4: Información detallada de nodo")
    print("-" * 50)
    
    # Get hypothesis with relations
    node_request = {
        "action": "get_node",
        "node_id": hypothesis_id,
        "include_relations": True
    }
    
    node_result = await kg_service.process_request(node_request)
    if node_result["success"]:
        node_data = node_result["node"]
        print(f"✅ Nodo recuperado: {node_data['name']}")
        print(f"   Tipo: {node_data['type']}")
        print(f"   Dominio: {node_data['domain']}")
        print(f"   Validado: {'Sí' if node_data['is_validated'] else 'No'}")
        print(f"   Relaciones salientes: {len(node_data.get('outgoing_relations', []))}")
        print(f"   Relaciones entrantes: {len(node_data.get('incoming_relations', []))}")
    else:
        print(f"❌ Error recuperando nodo: {node_result['error']}")
    
    print()
    
    # === DEMO 5: EXTRACT SUBGRAPH ===
    print("🌐 DEMO 5: Extracción de subgrafo")
    print("-" * 50)
    
    subgraph_request = {
        "action": "get_subgraph",
        "root_node_id": hypothesis_id,
        "max_depth": 2,
        "min_strength": 0.5,
        "include_relation_types": ["tests", "supports", "validates", "refines"]
    }
    
    subgraph_result = await kg_service.process_request(subgraph_request)
    if subgraph_result["success"]:
        subgraph = subgraph_result["subgraph"]
        print(f"✅ Subgrafo extraído desde: {subgraph['root_node_name']}")
        print(f"   Profundidad máxima: {subgraph['max_depth']}")
        print(f"   Nodos en subgrafo: {subgraph['metrics']['total_nodes']}")
        print(f"   Relaciones en subgrafo: {subgraph['metrics']['total_relations']}")
        print(f"   Confianza promedio: {subgraph['metrics']['avg_node_confidence']:.2f}")
        print(f"   Fuerza promedio relaciones: {subgraph['metrics']['avg_relation_strength']:.2f}")
        
        print("   Nodos:")
        for node in subgraph['nodes']:
            print(f"     • {node['name']} (profundidad: {node['depth']})")
        
        print("   Relaciones:")
        for rel in subgraph['relations']:
            print(f"     • {rel['source']} --[{rel['predicate']}]--> {rel['target']} (fuerza: {rel['strength']})")
    else:
        print(f"❌ Error extrayendo subgrafo: {subgraph_result['error']}")
    
    print()
    
    # === DEMO 6: GRAPH STATISTICS ===
    print("📈 DEMO 6: Estadísticas del grafo")
    print("-" * 50)
    
    stats_request = {
        "action": "get_statistics"
    }
    
    stats_result = await kg_service.process_request(stats_request)
    if stats_result["success"]:
        stats = stats_result["statistics"]
        print(f"✅ Estadísticas del grafo:")
        print(f"   Nodos totales: {stats['total_nodes']}")
        print(f"   Nodos validados: {stats['validated_nodes']}")
        print(f"   Porcentaje validación: {stats['validation_percentage']:.1f}%")
        print(f"   Relaciones totales: {stats['total_relations']}")
        print(f"   Confianza promedio: {stats['avg_confidence_score']:.2f}")
        print(f"   Densidad del grafo: {stats['graph_density']:.4f}")
    else:
        print(f"❌ Error obteniendo estadísticas: {stats_result['error']}")
    
    print()
    print("🎉 === Demo Knowledge Graph Service Completado ===")
    print()
    print("🔬 El Knowledge Graph Service proporciona:")
    print("   • Gestión completa de nodos y relaciones científicas")
    print("   • Búsqueda avanzada con múltiples filtros")
    print("   • Extracción inteligente de subgrafos")
    print("   • Análisis estadístico comprehensivo")
    print("   • Integración con servicios de literatura y research cycle")
    print("   • API REST completa para aplicaciones externas")


if __name__ == "__main__":
    asyncio.run(knowledge_graph_demo())
