"""
Knowledge Graph Service - Servicio centralizado para gestión del grafo de conocimiento científico

Este servicio actúa como coordinador central para todas las operaciones del knowledge graph,
integrando y orquestando las capacidades existentes de literatura search y research cycle manager.

Author: AXIOM Development Team
Date: September 12, 2025
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import joinedload

from app.services.base_service import BaseService
# Import database models when available; provide lightweight stand-ins to keep tests isolated
try:
    from app.models.database_models import KnowledgeNode, KnowledgeRelation
except Exception:
    class KnowledgeNode:  # lightweight placeholder
        pass
    class KnowledgeRelation:  # lightweight placeholder
        pass

from app.core.database import get_db_session
from app.exceptions.domain.biology import BiologyError
from app.types.knowledge_graph_service_types import (
    ProcessRequestResult,
    CreateKnowledgeNodeResult,
    GetKnowledgeNodeResult,
    SearchKnowledgeNodesResult,
    CreateKnowledgeRelationResult,
    GetSubgraphResult,
    GetGraphStatisticsResult,
    ValidateCausalRelationResult,
    DetectContradictionsResult,
    SuggestExperimentsResult,
    CaptureExperimentalConditionsResult,
    FindSimilarExperimentsResult,
)

# Configure logging
logger = logging.getLogger(__name__)


class KnowledgeGraphService(BaseService):
    """
    Servicio centralizado para gestión del knowledge graph científico.
    
    Proporciona funcionalidades completas para:
    - Gestión CRUD de nodos y relaciones
    - Búsqueda avanzada en el grafo
    - Análisis de conectividad y centralidad
    - Visualización de subgrafos
    """
    
    def __init__(self):
        super().__init__(name="KnowledgeGraph")
        self.version = "1.0.0"
        self.description = "Servicio centralizado para gestión del grafo de conocimiento científico"
        
        # Configuración del servicio
        self.max_search_results = 100
        self.max_subgraph_depth = 5
        
        # Tipos de nodos válidos (ampliados con tipos experimentales)
        self.valid_node_types = [
            "hypothesis", "concept", "method", "result", "paper", 
            "material", "technique", "domain", "researcher", "dataset",
            # Nuevos tipos para condiciones experimentales
            "experimental_condition", "parameter", "instrument", "reagent",
            "protocol", "measurement", "environment", "treatment"
        ]
        
        # Tipos de relaciones válidos (ampliados con relaciones causales científicas)
        self.valid_relation_types = [
            # Relaciones básicas
            "supports", "contradicts", "derives_from", "tests", "measures",
            "produces", "refines", "validates", "references", "extends",
            "requires", "enables", "conflicts_with", "similar_to",
            
            # Relaciones causales específicas para ciencia
            "causes", "inhibits", "activates", "regulates", "binds_to",
            "catalyzes", "modulates", "potentiates", "antagonizes", "synergizes_with",
            "upregulates", "downregulates", "induces", "represses", "mediates",
            
            # Relaciones experimentales
            "measured_in", "observed_in", "validated_by", "reproduced_in",
            "depends_on", "correlates_with", "associated_with", "predicts",
            
            # Relaciones de dominio
            "applies_to", "specializes_in", "cross_domain", "interdisciplinary"
        ]

        # Predicados bidireccionales adicionales
        self.bidirectional_predicates = {
            "similar_to", "related_to", "correlates_with", "associated_with",
            "synergizes_with", "cross_domain", "interdisciplinary"
        }

        # Predicados causales con direccionalidad específica
        self.causal_predicates = {
            "causes", "inhibits", "activates", "regulates", "binds_to",
            "catalyzes", "modulates", "potentiates", "antagonizes",
            "upregulates", "downregulates", "induces", "represses", "mediates"
        }

        # Predicados experimentales
        self.experimental_predicates = {
            "measured_in", "observed_in", "validated_by", "reproduced_in",
            "depends_on", "predicts"
        }
        
        # Tipos de condiciones experimentales comunes
        self.experimental_condition_types = {
            "temperature": "°C",
            "pressure": "atm", 
            "ph": "",
            "concentration": "M",
            "time": "min",
            "humidity": "%",
            "wavelength": "nm",
            "voltage": "V",
            "current": "A",
            "flow_rate": "mL/min"
        }

        # Mapeo de instrumentos a parámetros medibles
        self.instrument_parameters = {
            "nmr_spectrometer": ["frequency", "solvent", "temperature", "scan_count"],
            "mass_spectrometer": ["ionization_mode", "resolution", "mass_range"],
            "plate_reader": ["wavelength", "gain", "read_time"],
            "microscope": ["magnification", "resolution", "exposure_time"]
        }
        
        logger.info(f"✅ {self.name} initialized - Central knowledge graph coordinator")

    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Process knowledge graph requests"""
        try:
            action = request_data.get("action", "")
            
            # Node operations
            if action == "create_node":
                return await self.create_knowledge_node(request_data)
            elif action == "get_node":
                return await self.get_knowledge_node(request_data)
            elif action == "search_nodes":
                return await self.search_knowledge_nodes(request_data)
            
            # Relation operations
            elif action == "create_relation":
                return await self.create_knowledge_relation(request_data)
            
            # Graph analysis operations
            elif action == "get_subgraph":
                return await self.get_subgraph(request_data)
            elif action == "get_statistics":
                return await self.get_graph_statistics(request_data)
            
            # New advanced operations
            elif action == "detect_contradictions":
                return await self.detect_contradictions(request_data.get("node_id"), request_data.get("max_depth", 2))
            elif action == "suggest_experiments":
                return await self.suggest_experiments(request_data.get("node_id"), request_data.get("max_suggestions", 5))
            elif action == "capture_experimental_conditions":
                return await self.capture_experimental_conditions(request_data)
            elif action == "find_similar_experiments":
                return await self.find_similar_experiments(
                    request_data.get("conditions", {}),
                    request_data.get("domain", "general"),
                    request_data.get("max_results", 5)
                )
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": [
                        "create_node", "get_node", "search_nodes",
                        "create_relation", "get_subgraph", "get_statistics"
                    ]
                }

        except BiologyError as e:
            return self.handle_error(e, "process_request")

    # === NODE OPERATIONS ===

    async def create_knowledge_node(self, request_data: CreateKnowledgeNodeResult) -> CreateKnowledgeNodeResult:
        """Create a new knowledge node in the graph"""
        try:
            name = request_data.get("name", "").strip()
            concept_type = request_data.get("type", "concept").strip()
            domain = request_data.get("domain", "general").strip()
            properties = request_data.get("properties", {})
            confidence_score = request_data.get("confidence_score", 0.8)
            source_papers = request_data.get("source_papers", [])
            created_by = request_data.get("created_by")

            if not name:
                return {"success": False, "error": "Node name is required"}
                
            if concept_type not in self.valid_node_types:
                return {"success": False, "error": f"Invalid node type. Valid types: {self.valid_node_types}"}

            session = get_db_session()
            try:
                existing = session.query(KnowledgeNode).filter(
                    and_(KnowledgeNode.name == name, KnowledgeNode.domain == domain)
                ).first()
                
                if existing:
                    return {"success": False, "error": f"Node '{name}' already exists in domain '{domain}'"}

                new_node = KnowledgeNode(
                    name=name,
                    concept_type=concept_type,
                    domain=domain,
                    properties=properties,
                    confidence_score=confidence_score,
                    source_papers=source_papers,
                    created_by=created_by,
                    is_validated=False,
                    validation_count=0
                )

                session.add(new_node)
                session.commit()
                session.refresh(new_node)

                logger.info(f"🆕 Created knowledge node: '{name}' ({concept_type}) in domain '{domain}'")

                return {
                    "success": True,
                    "node_id": new_node.id,
                    "node": {
                        "id": new_node.id,
                        "name": new_node.name,
                        "type": new_node.concept_type,
                        "domain": new_node.domain,
                        "confidence_score": new_node.confidence_score,
                        "is_validated": new_node.is_validated
                    }
                }
            finally:
                session.close()

        except BiologyError as e:
            return self.handle_error(e, "create_knowledge_node")

    async def get_knowledge_node(self, request_data: GetKnowledgeNodeResult) -> GetKnowledgeNodeResult:
        """Get detailed information about a knowledge node"""
        try:
            node_id = request_data.get("node_id")
            include_relations = request_data.get("include_relations", True)

            if not node_id:
                return {"success": False, "error": "node_id is required"}

            session = get_db_session()
            try:
                query = session.query(KnowledgeNode)
                if include_relations:
                    query = query.options(
                        joinedload(KnowledgeNode.outgoing_relations),
                        joinedload(KnowledgeNode.incoming_relations)
                    )
                
                node = query.filter(KnowledgeNode.id == node_id).first()
                
                if not node:
                    return {"success": False, "error": f"Node with id {node_id} not found"}

                node_data = {
                    "id": node.id,
                    "name": node.name,
                    "type": node.concept_type,
                    "domain": node.domain,
                    "properties": node.properties or {},
                    "confidence_score": node.confidence_score,
                    "source_papers": node.source_papers or [],
                    "created_by": node.created_by,
                    "is_validated": node.is_validated,
                    "validation_count": node.validation_count
                }

                if include_relations:
                    outgoing = []
                    for rel in node.outgoing_relations:
                        outgoing.append({
                            "relation_id": rel.id,
                            "predicate": rel.predicate,
                            "target_id": rel.object_id,
                            "target_name": rel.object.name if rel.object else "Unknown",
                            "strength": rel.strength
                        })
                    
                    incoming = []
                    for rel in node.incoming_relations:
                        incoming.append({
                            "relation_id": rel.id,
                            "predicate": rel.predicate,
                            "source_id": rel.subject_id,
                            "source_name": rel.subject.name if rel.subject else "Unknown",
                            "strength": rel.strength
                        })

                    node_data["outgoing_relations"] = outgoing
                    node_data["incoming_relations"] = incoming

                return {
                    "success": True,
                    "node": node_data
                }
            finally:
                session.close()

        except BiologyError as e:
            return self.handle_error(e, "get_knowledge_node")

    async def search_knowledge_nodes(self, request_data: SearchKnowledgeNodesResult) -> SearchKnowledgeNodesResult:
        """Search knowledge nodes with advanced filters"""
        try:
            query_text = request_data.get("query", "").strip()
            domain_filter = request_data.get("domain")
            type_filter = request_data.get("type")
            min_confidence = request_data.get("min_confidence", 0.0)
            validated_only = request_data.get("validated_only", False)
            limit = min(request_data.get("limit", 50), self.max_search_results)
            offset = request_data.get("offset", 0)

            session = get_db_session()
            try:
                query = session.query(KnowledgeNode)
                
                conditions = []
                
                if query_text:
                    conditions.append(KnowledgeNode.name.ilike(f"%{query_text}%"))
                
                if domain_filter:
                    conditions.append(KnowledgeNode.domain == domain_filter)
                
                if type_filter and type_filter in self.valid_node_types:
                    conditions.append(KnowledgeNode.concept_type == type_filter)
                
                if min_confidence > 0:
                    conditions.append(KnowledgeNode.confidence_score >= min_confidence)
                
                if validated_only:
                    conditions.append(KnowledgeNode.is_validated)

                if conditions:
                    query = query.filter(and_(*conditions))

                query = query.order_by(
                    desc(KnowledgeNode.confidence_score),
                    desc(KnowledgeNode.validation_count),
                    KnowledgeNode.name
                )

                total_count = query.count()
                nodes = query.offset(offset).limit(limit).all()

                results = []
                for node in nodes:
                    results.append({
                        "id": node.id,
                        "name": node.name,
                        "type": node.concept_type,
                        "domain": node.domain,
                        "confidence_score": node.confidence_score,
                        "is_validated": node.is_validated,
                        "validation_count": node.validation_count
                    })

                return {
                    "success": True,
                    "nodes": results,
                    "total_count": total_count,
                    "returned_count": len(results),
                    "offset": offset,
                    "limit": limit,
                    "has_more": (offset + len(results)) < total_count
                }
            finally:
                session.close()

        except BiologyError as e:
            return self.handle_error(e, "search_knowledge_nodes")

    # === RELATION OPERATIONS ===

    async def create_knowledge_relation(self, request_data: CreateKnowledgeRelationResult) -> CreateKnowledgeRelationResult:
        """Create a new relation between knowledge nodes"""
        try:
            subject_id = request_data.get("subject_id")
            object_id = request_data.get("object_id")
            predicate = request_data.get("predicate", "").strip()
            strength = request_data.get("strength", 1.0)
            context = request_data.get("context", {})
            evidence_papers = request_data.get("evidence_papers", [])
            created_by = request_data.get("created_by")

            if not subject_id or not object_id:
                return {"success": False, "error": "Both subject_id and object_id are required"}
                
            if not predicate:
                return {"success": False, "error": "Predicate is required"}
                
            if predicate not in self.valid_relation_types:
                return {"success": False, "error": f"Invalid predicate. Valid types: {self.valid_relation_types}"}

            if not (0.0 <= strength <= 1.0):
                return {"success": False, "error": "Strength must be between 0.0 and 1.0"}

            session = get_db_session()
            try:
                subject_node = session.query(KnowledgeNode).filter(KnowledgeNode.id == subject_id).first()
                object_node = session.query(KnowledgeNode).filter(KnowledgeNode.id == object_id).first()
                
                if not subject_node:
                    return {"success": False, "error": f"Subject node with id {subject_id} not found"}
                
                if not object_node:
                    return {"success": False, "error": f"Object node with id {object_id} not found"}

                existing_relation = session.query(KnowledgeRelation).filter(
                    and_(
                        KnowledgeRelation.subject_id == subject_id,
                        KnowledgeRelation.object_id == object_id,
                        KnowledgeRelation.predicate == predicate
                    )
                ).first()
                
                if existing_relation:
                    return {
                        "success": False, 
                        "error": f"Relation '{predicate}' between nodes {subject_id} and {object_id} already exists"
                    }

                new_relation = KnowledgeRelation(
                    subject_id=subject_id,
                    object_id=object_id,
                    predicate=predicate,
                    strength=strength,
                    context=context,
                    evidence_papers=evidence_papers,
                    created_by=created_by,
                    is_bidirectional=self._is_bidirectional_predicate(predicate),
                    validation_status="pending"
                )

                session.add(new_relation)
                session.commit()
                session.refresh(new_relation)

                logger.info(f"🔗 Created relation: {subject_node.name} --[{predicate}]--> {object_node.name}")

                return {
                    "success": True,
                    "relation_id": new_relation.id,
                    "relation": {
                        "id": new_relation.id,
                        "subject_id": new_relation.subject_id,
                        "subject_name": subject_node.name,
                        "predicate": new_relation.predicate,
                        "object_id": new_relation.object_id,
                        "object_name": object_node.name,
                        "strength": new_relation.strength,
                        "is_bidirectional": new_relation.is_bidirectional
                    }
                }
            finally:
                session.close()

        except BiologyError as e:
            return self.handle_error(e, "create_knowledge_relation")

    # === GRAPH ANALYSIS OPERATIONS ===

    async def get_subgraph(self, request_data: GetSubgraphResult) -> GetSubgraphResult:
        """Get a subgraph starting from a root node"""
        try:
            root_node_id = request_data.get("root_node_id")
            max_depth = min(request_data.get("max_depth", 2), self.max_subgraph_depth)
            include_relation_types = request_data.get("include_relation_types", self.valid_relation_types)
            min_strength = request_data.get("min_strength", 0.1)

            if not root_node_id:
                return {"success": False, "error": "root_node_id is required"}

            session = get_db_session()
            try:
                root_node = session.query(KnowledgeNode).filter(KnowledgeNode.id == root_node_id).first()
                if not root_node:
                    return {"success": False, "error": f"Root node with id {root_node_id} not found"}

                visited_nodes = set()
                visited_relations = set()
                nodes_data = {}
                relations_data = []
                
                queue = [(root_node_id, 0)]
                visited_nodes.add(root_node_id)

                while queue:
                    current_node_id, current_depth = queue.pop(0)
                    
                    current_node = session.query(KnowledgeNode).filter(
                        KnowledgeNode.id == current_node_id
                    ).first()
                    
                    if current_node:
                        nodes_data[current_node_id] = {
                            "id": current_node.id,
                            "name": current_node.name,
                            "type": current_node.concept_type,
                            "domain": current_node.domain,
                            "confidence_score": current_node.confidence_score,
                            "depth": current_depth
                        }

                    if current_depth < max_depth:
                        outgoing_relations = session.query(KnowledgeRelation).filter(
                            and_(
                                KnowledgeRelation.subject_id == current_node_id,
                                KnowledgeRelation.predicate.in_(include_relation_types),
                                KnowledgeRelation.strength >= min_strength
                            )
                        ).all()

                        for relation in outgoing_relations:
                            if relation.id not in visited_relations:
                                visited_relations.add(relation.id)
                                
                                relations_data.append({
                                    "id": relation.id,
                                    "source": relation.subject_id,
                                    "target": relation.object_id,
                                    "predicate": relation.predicate,
                                    "strength": relation.strength,
                                    "is_bidirectional": relation.is_bidirectional
                                })

                                if relation.object_id not in visited_nodes:
                                    visited_nodes.add(relation.object_id)
                                    queue.append((relation.object_id, current_depth + 1))

                subgraph_metrics = {
                    "total_nodes": len(nodes_data),
                    "total_relations": len(relations_data),
                    "max_depth_reached": max((node["depth"] for node in nodes_data.values())) if nodes_data else 0,
                    "avg_node_confidence": sum(node["confidence_score"] for node in nodes_data.values()) / len(nodes_data) if nodes_data else 0,
                    "avg_relation_strength": sum(rel["strength"] for rel in relations_data) / len(relations_data) if relations_data else 0
                }

                return {
                    "success": True,
                    "subgraph": {
                        "root_node_id": root_node_id,
                        "root_node_name": root_node.name,
                        "max_depth": max_depth,
                        "nodes": list(nodes_data.values()),
                        "relations": relations_data,
                        "metrics": subgraph_metrics
                    }
                }
            finally:
                session.close()

        except BiologyError as e:
            return self.handle_error(e, "get_subgraph")

    async def get_graph_statistics(self, request_data: GetGraphStatisticsResult) -> GetGraphStatisticsResult:
        """Get comprehensive statistics about the knowledge graph"""
        try:
            session = get_db_session()
            try:
                total_nodes = session.query(KnowledgeNode).count()
                validated_nodes = session.query(KnowledgeNode).filter(
                    KnowledgeNode.is_validated
                ).count()
                
                total_relations = session.query(KnowledgeRelation).count()
                
                # Simple statistics calculation
                avg_confidence = session.query(func.avg(KnowledgeNode.confidence_score)).scalar() or 0.0
                min_confidence = session.query(func.min(KnowledgeNode.confidence_score)).scalar() or 0.0
                max_confidence = session.query(func.max(KnowledgeNode.confidence_score)).scalar() or 0.0

                basic_stats = {
                    "total_nodes": total_nodes,
                    "validated_nodes": validated_nodes,
                    "validation_percentage": (validated_nodes / total_nodes * 100) if total_nodes > 0 else 0,
                    "total_relations": total_relations,
                    "avg_confidence_score": float(avg_confidence),
                    "min_confidence_score": float(min_confidence),
                    "max_confidence_score": float(max_confidence),
                    "graph_density": (total_relations / (total_nodes * (total_nodes - 1))) if total_nodes > 1 else 0
                }

                return {
                    "success": True,
                    "statistics": basic_stats,
                    "generated_at": datetime.utcnow().isoformat()
                }
            finally:
                session.close()

        except BiologyError as e:
            return self.handle_error(e, "get_graph_statistics")

    # === HELPER METHODS ===

    def _is_bidirectional_predicate(self, predicate: str) -> bool:
        """Determine if a predicate should be treated as bidirectional"""
        return predicate in self.bidirectional_predicates

    def _validate_causal_relation(self, subject_type: str, predicate: str, object_type: str) -> ValidateCausalRelationResult:
        """Validar consistencia semántica de relaciones causales"""
        validation = {
            "is_valid": True,
            "warnings": [],
            "suggestions": []
        }
        
        # Validaciones específicas para relaciones causales
        if predicate in self.causal_predicates:
            # Las relaciones causales generalmente requieren nodos de tipo concepto/hypothesis
            if subject_type not in ["concept", "hypothesis", "method"]:
                validation["warnings"].append(f"Subject type '{subject_type}' may not be appropriate for causal predicate '{predicate}'")
            
            if object_type not in ["concept", "hypothesis", "result"]:
                validation["warnings"].append(f"Object type '{object_type}' may not be appropriate for causal predicate '{predicate}'")
        
        # Validaciones para relaciones experimentales
        elif predicate in self.experimental_predicates:
            if object_type not in ["method", "technique", "dataset", "result"]:
                validation["warnings"].append(f"Object type '{object_type}' may not be appropriate for experimental predicate '{predicate}'")
        
        return validation

    async def detect_contradictions(self, node_id: int, max_depth: int = 2) -> DetectContradictionsResult:
        """Detectar relaciones contradictorias para un nodo específico"""
        try:
            session = get_db_session()
            try:
                # Obtener subgrafos de soporte y contradicción
                support_subgraph = await self.get_subgraph({
                    "action": "get_subgraph",
                    "root_node_id": node_id,
                    "max_depth": max_depth,
                    "include_relation_types": ["supports", "validates", "causes", "activates"]
                })
                
                contradiction_subgraph = await self.get_subgraph({
                    "action": "get_subgraph", 
                    "root_node_id": node_id,
                    "max_depth": max_depth,
                    "include_relation_types": ["contradicts", "inhibits", "conflicts_with", "antagonizes"]
                })
                
                contradictions = []
                
                # Buscar nodos que aparecen en ambos subgrafos (potenciales contradicciones)
                if support_subgraph["success"] and contradiction_subgraph["success"]:
                    support_nodes = {node["id"] for node in support_subgraph["subgraph"]["nodes"]}
                    contradiction_nodes = {node["id"] for node in contradiction_subgraph["subgraph"]["nodes"]}
                    
                    conflicting_nodes = support_nodes.intersection(contradiction_nodes)
                    
                    for node_id in conflicting_nodes:
                        contradictions.append({
                            "node_id": node_id,
                            "evidence_types": ["support", "contradiction"],
                            "confidence": 0.7,  # Placeholder - calcular basado en fuerza de relaciones
                            "suggestion": "Investigar evidencia contradictoria mediante experimentos controlados"
                        })
                
                return {
                    "success": True,
                    "contradictions": contradictions,
                    "total_contradictions": len(contradictions),
                    "analysis_depth": max_depth
                }
                
            finally:
                session.close()
        except BiologyError as e:
            return self.handle_error(e, "detect_contradictions")

    async def suggest_experiments(self, node_id: int, max_suggestions: int = 5) -> SuggestExperimentsResult:
        """Sugerir experimentos para resolver gaps de conocimiento o contradicciones"""
        try:
            session = get_db_session()
            try:
                node = session.query(KnowledgeNode).filter(KnowledgeNode.id == node_id).first()
                if not node:
                    return {"success": False, "error": f"Node {node_id} not found"}
                
                suggestions = []
                
                # Analizar el nodo para determinar tipo de experimento sugerido
                node_type = node.concept_type
                domain = node.domain
                
                # Sugerencias basadas en tipo de nodo
                if node_type == "hypothesis":
                    suggestions.extend(self._suggest_hypothesis_experiments(node, domain))
                elif node_type == "concept":
                    suggestions.extend(self._suggest_concept_experiments(node, domain))
                elif node_type == "result":
                    suggestions.extend(self._suggest_result_experiments(node, domain))
                
                # Limitar número de sugerencias
                suggestions = suggestions[:max_suggestions]
                
                return {
                    "success": True,
                    "suggestions": suggestions,
                    "total_suggestions": len(suggestions),
                    "node_id": node_id,
                    "node_type": node_type,
                    "domain": domain
                }
                
            finally:
                session.close()
        except BiologyError as e:
            return self.handle_error(e, "suggest_experiments")

    def _suggest_hypothesis_experiments(self, node, domain: str) -> List[Dict[str, Any]]:
        """Sugerir experimentos para validar hipótesis"""
        suggestions = []
        
        # Mapeo de dominios a tipos de experimentos
        domain_experiments = {
            "biology": [
                {"type": "molecular_docking", "tool": "AutoDock Vina", "description": "Validar unión molecular"},
                {"type": "gene_expression", "tool": "scanpy", "description": "Medir expresión génica"},
                {"type": "protein_folding", "tool": "ESMFold", "description": "Predecir estructura proteica"}
            ],
            "chemistry": [
                {"type": "reaction_prediction", "tool": "RDKit", "description": "Predecir outcome de reacción"},
                {"type": "property_calculation", "tool": "RDKit", "description": "Calcular propiedades moleculares"},
                {"type": "retrosynthesis", "tool": "ASKCOS", "description": "Planificar síntesis"}
            ],
            "materials": [
                {"type": "molecular_dynamics", "tool": "OpenMM", "description": "Simular dinámica molecular"},
                {"type": "property_prediction", "tool": "ML models", "description": "Predecir propiedades materiales"}
            ]
        }
        
        # Sugerencias específicas del dominio
        for exp in domain_experiments.get(domain, []):
            suggestions.append({
                "experiment_type": exp["type"],
                "suggested_tool": exp["tool"],
                "description": f"{exp['description']} para validar hipótesis '{node.name}'",
                "priority": "high",
                "estimated_duration": "2-4 hours",
                "confidence_impact": 0.3  # Impacto esperado en score de confianza
            })
        
        return suggestions

    def _suggest_concept_experiments(self, node, domain: str) -> List[Dict[str, Any]]:
        """Sugerir experimentos para explorar conceptos"""
        return [
            {
                "experiment_type": "literature_review",
                "suggested_tool": "LiteratureSearchService", 
                "description": f"Revisar literatura sobre concepto '{node.name}'",
                "priority": "medium",
                "estimated_duration": "1-2 hours",
                "confidence_impact": 0.1
            }
        ]

    def _suggest_result_experiments(self, node, domain: str) -> List[Dict[str, Any]]:
        """Sugerir experimentos para replicar/validar resultados"""
        return [
            {
                "experiment_type": "replication",
                "suggested_tool": "ActiveReproducibilityEngine",
                "description": f"Replicar resultado '{node.name}' con variaciones controladas",
                "priority": "high", 
                "estimated_duration": "3-6 hours",
                "confidence_impact": 0.4
            }
        ]

    async def capture_experimental_conditions(self, experiment_data: CaptureExperimentalConditionsResult) -> CaptureExperimentalConditionsResult:
        """Capturar condiciones experimentales como nodos especializados en el KG"""
        try:
            session = get_db_session()
            try:
                experiment_id = experiment_data.get("experiment_id", f"exp_{datetime.now().timestamp()}")
                conditions = experiment_data.get("conditions", {})
                instrument = experiment_data.get("instrument")
                protocol = experiment_data.get("protocol")
                
                created_nodes = []
                
                # Crear nodo principal del experimento
                experiment_node = await self.create_knowledge_node({
                    "action": "create_node",
                    "name": f"Experiment {experiment_id}",
                    "type": "method",
                    "domain": experiment_data.get("domain", "general"),
                    "properties": {
                        "experiment_id": experiment_id,
                        "purpose": experiment_data.get("purpose", ""),
                        "hypothesis_tested": experiment_data.get("hypothesis_tested"),
                        "timestamp": datetime.now().isoformat()
                    }
                })
                
                if experiment_node["success"]:
                    created_nodes.append(experiment_node["node_id"])
                
                # Capturar condiciones individuales
                for param_name, param_value in conditions.items():
                    if param_name in self.experimental_condition_types:
                        unit = self.experimental_condition_types[param_name]
                        condition_node = await self.create_knowledge_node({
                            "action": "create_node",
                            "name": f"{param_name}: {param_value}{unit}",
                            "type": "parameter",
                            "domain": experiment_data.get("domain", "general"),
                            "properties": {
                                "parameter_name": param_name,
                                "value": param_value,
                                "unit": unit,
                                "experiment_id": experiment_id
                            }
                        })
                        
                        if condition_node["success"]:
                            created_nodes.append(condition_node["node_id"])
                            # Relacionar condición con experimento
                            await self.create_knowledge_relation({
                                "action": "create_relation",
                                "subject_id": experiment_node["node_id"],
                                "object_id": condition_node["node_id"],
                                "predicate": "uses_parameter",
                                "strength": 1.0,
                                "context": {"role": "experimental_condition"}
                            })
                
                # Capturar información del instrumento si está disponible
                if instrument:
                    instrument_node = await self.create_knowledge_node({
                        "action": "create_node",
                        "name": f"Instrument: {instrument}",
                        "type": "instrument",
                        "domain": experiment_data.get("domain", "general"),
                        "properties": {
                            "instrument_type": instrument,
                            "experiment_id": experiment_id,
                            "capabilities": self.instrument_parameters.get(instrument, [])
                        }
                    })
                    
                    if instrument_node["success"]:
                        created_nodes.append(instrument_node["node_id"])
                        await self.create_knowledge_relation({
                            "action": "create_relation",
                            "subject_id": experiment_node["node_id"],
                            "object_id": instrument_node["node_id"],
                            "predicate": "uses_instrument",
                            "strength": 1.0
                        })
                
                return {
                    "success": True,
                    "experiment_id": experiment_id,
                    "created_nodes": created_nodes,
                    "total_conditions_captured": len(conditions),
                    "message": f"Captured {len(conditions)} experimental conditions for experiment {experiment_id}"
                }
                
            finally:
                session.close()
        except BiologyError as e:
            return self.handle_error(e, "capture_experimental_conditions")

    async def find_similar_experiments(self, conditions: FindSimilarExperimentsResult, domain: str, max_results: int = 5) -> FindSimilarExperimentsResult:
        """Encontrar experimentos similares basados en condiciones"""
        try:
            session = get_db_session()
            try:
                # Buscar nodos de parámetros que coincidan con las condiciones
                matching_nodes = []
                
                for param_name, param_value in conditions.items():
                    if param_name in self.experimental_condition_types:
                        search_query = f"{param_name}: {param_value}"
                        param_nodes = await self.search_knowledge_nodes({
                            "action": "search_nodes",
                            "query": search_query,
                            "type": "parameter",
                            "domain": domain,
                            "limit": 10
                        })
                        
                        if param_nodes["success"]:
                            matching_nodes.extend(param_nodes["nodes"])
                
                # Agrupar por experimento y calcular similitud
                experiment_similarity = {}
                
                for node in matching_nodes:
                    # Obtener el experimento padre de este parámetro
                    experiment_relations = await self.get_knowledge_node({
                        "action": "get_node",
                        "node_id": node["id"],
                        "include_relations": True
                    })
                    
                    if experiment_relations["success"]:
                        for rel in experiment_relations["node"].get("incoming_relations", []):
                            if rel["predicate"] == "uses_parameter":
                                experiment_id = rel["source_id"]
                                if experiment_id not in experiment_similarity:
                                    experiment_similarity[experiment_id] = 0
                                experiment_similarity[experiment_id] += 1
                
                # Ordenar por similitud y limitar resultados
                sorted_experiments = sorted(experiment_similarity.items(), key=lambda x: x[1], reverse=True)
                results = []
                
                for exp_id, similarity_score in sorted_experiments[:max_results]:
                    exp_node = await self.get_knowledge_node({
                        "action": "get_node",
                        "node_id": exp_id
                    })
                    
                    if exp_node["success"]:
                        results.append({
                            "experiment_id": exp_id,
                            "similarity_score": similarity_score / len(conditions),
                            "experiment_name": exp_node["node"]["name"],
                            "domain": exp_node["node"]["domain"]
                        })
                
                return {
                    "success": True,
                    "similar_experiments": results,
                    "total_found": len(results),
                    "search_conditions": conditions
                }
                
            finally:
                session.close()
        except BiologyError as e:
            return self.handle_error(e, "find_similar_experiments")


# Singleton instance for global access
_knowledge_graph_service_instance = None


def get_knowledge_graph_service() -> KnowledgeGraphService:
    """
    Obtiene la instancia singleton del servicio de knowledge graph
    
    Returns:
        KnowledgeGraphService: Instancia del servicio
    """
    global _knowledge_graph_service_instance
    
    if _knowledge_graph_service_instance is None:
        _knowledge_graph_service_instance = KnowledgeGraphService()
    
    return _knowledge_graph_service_instance
