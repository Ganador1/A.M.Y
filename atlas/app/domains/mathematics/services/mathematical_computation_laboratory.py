"""
AXIOM Mathematical Computation Laboratory
Orquestador principal coordinando todos los componentes de análisis matemático
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path

# Import all mathematical components
from app.mathlab.objects.elliptic_curve_enhanced import EllipticCurve
from app.mathlab.invariants.elliptic_curve_invariants import EllipticCurveInvariantAnalyzer
from app.mathlab.analysis.sequence_analyzer import SequenceAnalyzer, SequenceAnalysisResult
from app.mathlab.analysis.sequence_analyzer import SequenceAnalyzer as RealSequenceAnalyzer  # alias para claridad
from app.mathlab.persistence.conjecture_persistence import (
    ConjecturePersistenceService,
    ConjectureType,
    Evidence
)
from app.exceptions.domain.mathematics import MathematicsError
from app.mathlab.registry.object_registry import (
    MathematicalObjectRegistry,
    MathematicalObjectInterface
)
from app.mathlab.conjectures.ranking_engine import score_conjecture  # Añadido para ranking
from app.mathlab.persistence.conjecture import Conjecture # Añadido para ranking

logger = logging.getLogger(__name__)


@dataclass
class ResearchQuestion:
    """A mathematical research question to investigate"""
    question_id: str
    title: str
    description: str
    question_type: str  # "conjecture", "exploration", "verification", "discovery"
    priority: float = 0.5  # 0.0-1.0
    mathematical_domain: str = "general"
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "open"  # "open", "investigating", "answered", "abandoned"


@dataclass
class AnalysisSession:
    """Mathematical analysis session tracking"""
    session_id: str
    objective: str
    start_time: datetime
    end_time: Optional[datetime] = None
    objects_analyzed: int = 0
    patterns_discovered: int = 0
    conjectures_generated: int = 0
    insights: List[str] = field(default_factory=list)
    computational_time: float = 0.0
    status: str = "active"  # "active", "completed", "paused", "failed"


@dataclass
class MathematicalInsight:
    """A mathematical insight or discovery"""
    insight_type: str  # "pattern", "relationship", "anomaly", "conjecture"
    description: str
    mathematical_objects: List[str]  # Object IDs
    confidence: float
    novelty_score: float
    supporting_evidence: List[Dict[str, Any]]
    potential_applications: List[str] = field(default_factory=list)
    follow_up_questions: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class MathematicalComputationLaboratory:
    """
    AXIOM Mathematical Computation Laboratory

    Orchestrates sophisticated mathematical analysis including:
    - Elliptic curve theory and analysis
    - Sequence pattern recognition and OEIS integration
    - Mathematical conjecture generation and validation
    - Cross-domain mathematical insight discovery
    """

    def __init__(self,
                 database_url: str = "sqlite:///mathematics_lab.db",
                 work_directory: Optional[Path] = None):
        self.lab_id = "mathematics_computation_lab"
        self.version = "2.0.0"
        self.work_directory = work_directory or Path("./mathematics_workspace")
        self.work_directory.mkdir(exist_ok=True)

        # Initialize core components
        self.persistence_service = ConjecturePersistenceService(database_url)
        self.object_registry = MathematicalObjectRegistry()
        self.invariant_analyzer = EllipticCurveInvariantAnalyzer()
        self.sequence_analyzer = None  # Will be created as async context manager
        # Conjecture plugins (ligero): registrar plugin de teoría de números si se usan enteros
        try:
            from app.mathlab.conjectures.number_theory_plugin import NumberTheoryConjecturePlugin
            self.number_theory_plugin = NumberTheoryConjecturePlugin()
            from app.mathlab.conjectures.evidence_ratio import EvidenceRatioEngine
            self.evidence_engine = EvidenceRatioEngine()
        except MathematicsError:
            self.number_theory_plugin = None
            self.evidence_engine = None

        # Research session tracking
        self.current_session: Optional[AnalysisSession] = None
        self.active_questions: List[ResearchQuestion] = []
        self.insights_history: List[MathematicalInsight] = []

        # Configuration
        self.config = {
            "max_computation_time": 300,  # 5 minutes per major operation
            "sequence_analysis_depth": True,  # Enable OEIS integration
            "conjecture_confidence_threshold": 0.6,
            "auto_persist_results": True,
            "max_concurrent_analyses": 3,
            "enable_cross_domain_analysis": True
        }

        # Performance metrics
        self.metrics = {
            "analyses_completed": 0,
            "conjectures_generated": 0,
            "patterns_discovered": 0,
            "computation_time_total": 0.0,
            "success_rate": 0.0,
            "uptime": datetime.now()
        }

        logger.info(f"Mathematical Laboratory initialized - Version {self.version}")

    async def __aenter__(self):
        """Async context manager entry"""
        self.sequence_analyzer = SequenceAnalyzer()
        await self.sequence_analyzer.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.sequence_analyzer:
            await self.sequence_analyzer.__aexit__(exc_type, exc_val, exc_tb)

        if self.current_session and self.current_session.status == "active":
            await self.end_analysis_session()

    async def start_analysis_session(self, objective: str) -> str:
        """Start a new mathematical analysis session"""
        if self.current_session and self.current_session.status == "active":
            logger.warning("Ending previous active session")
            await self.end_analysis_session()

        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.current_session = AnalysisSession(
            session_id=session_id,
            objective=objective,
            start_time=datetime.now()
        )

        # Start database research session
        # Start research session
        _ = self.persistence_service.start_research_session(
            session_name=session_id,
            objective=objective,
            approach="systematic"
        )

        logger.info(f"Started analysis session: {session_id}")
        return session_id

    async def end_analysis_session(self) -> Optional[Dict[str, Any]]:
        """End current analysis session"""
        if not self.current_session:
            return None

        session = self.current_session
        session.end_time = datetime.now()
        session.status = "completed"

        # Calculate session duration
        duration = (session.end_time - session.start_time).total_seconds()
        session.computational_time = duration

        # Collect insights from this session
        session_insights = [
            insight.description for insight in self.insights_history
            if insight.timestamp >= session.start_time
        ]

        # End database session
        self.persistence_service.end_research_session(
            session.session_id,
            insights=session_insights,
            follow_up_questions=[]
        )

        session_summary = {
            "session_id": session.session_id,
            "objective": session.objective,
            "duration_seconds": duration,
            "objects_analyzed": session.objects_analyzed,
            "patterns_discovered": session.patterns_discovered,
            "conjectures_generated": session.conjectures_generated,
            "insights_count": len(session_insights),
            "status": session.status
        }

        logger.info(f"Analysis session completed: {session.session_id}")
        self.current_session = None

        return session_summary

    async def analyze_elliptic_curve(self,
                                   curve: EllipticCurve,
                                   deep_analysis: bool = True) -> Dict[str, Any]:
        """Comprehensive elliptic curve analysis"""
        start_time = datetime.now()

        try:
            logger.info(f"Analyzing elliptic curve: {curve}")

            # Basic validation
            if not curve.is_valid():
                return {
                    "success": False,
                    "error": "Invalid elliptic curve (discriminant is zero)",
                    "curve": str(curve)
                }

            # Register in object registry
            curve_id = self.object_registry.register_object(
                curve,
                tags={"elliptic_curve", "analysis_target"}
            )

            analysis_results = {
                "success": True,
                "curve_id": curve_id,
                "curve": str(curve),
                "basic_properties": curve.get_properties(),
                "analysis_timestamp": start_time.isoformat()
            }

            # Perform invariant analysis
            if deep_analysis:
                invariant_result = await self.invariant_analyzer.analyze_curve(curve)
                if invariant_result:
                    analysis_results["invariant_analysis"] = {
                        "j_invariant": invariant_result.j_invariant,
                        "torsion_structure": invariant_result.torsion_structure.__dict__ if invariant_result.torsion_structure else None,
                        "rank_estimate": invariant_result.rank_data.__dict__ if invariant_result.rank_data else None,
                        "statistical_analysis": invariant_result.statistical_analysis,
                        "reliability_score": invariant_result.reliability_score
                    }

            # Find rational points
            rational_points = curve.find_rational_points(search_bound=100)
            analysis_results["rational_points"] = {
                "count": len(rational_points),
                "points": [{"x": p.x, "y": p.y, "is_infinity": p.is_infinity} for p in rational_points[:10]]
            }

            # Torsion analysis
            torsion_points = curve.find_torsion_points()
            analysis_results["torsion_analysis"] = {
                "torsion_points_count": len(torsion_points),
                "estimated_torsion_order": len([p for p in torsion_points if not p.is_infinity])
            }

            # Store in persistence system if configured
            if self.config["auto_persist_results"]:
                db_object_id = self.persistence_service.store_mathematical_object(
                    object_type="elliptic_curve",
                    name=str(curve),
                    canonical_form=curve.get_canonical_form(),
                    hash_value=curve.compute_hash(),
                    properties=curve.get_properties(),
                    invariants=analysis_results.get("invariant_analysis", {})
                )
                analysis_results["db_object_id"] = db_object_id

            # Generate insights and potential conjectures
            insights = await self._generate_curve_insights(curve, analysis_results)
            analysis_results["insights"] = insights

            # Update session metrics
            if self.current_session:
                self.current_session.objects_analyzed += 1
                self.current_session.patterns_discovered += len(insights)

            computation_time = (datetime.now() - start_time).total_seconds()
            analysis_results["computation_time"] = computation_time
            self.metrics["computation_time_total"] += computation_time
            self.metrics["analyses_completed"] += 1

            logger.info(f"Elliptic curve analysis completed in {computation_time:.2f}s")

            return analysis_results

        except MathematicsError as e:
            logger.error(f"Elliptic curve analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "curve": str(curve),
                "computation_time": (datetime.now() - start_time).total_seconds()
            }

    async def analyze_sequence(self,
                             sequence: List[Union[int, float]],
                             sequence_name: Optional[str] = None) -> Dict[str, Any]:
        """Comprehensive sequence analysis with pattern detection"""
        start_time = datetime.now()

        try:
            logger.info(f"Analyzing sequence: {sequence[:10]}... (length: {len(sequence)})")

            if not self.sequence_analyzer:
                return {
                    "success": False,
                    "error": "Sequence analyzer not initialized (use async context manager)"
                }

            # Perform sequence analysis
            analysis_result = await self.sequence_analyzer.analyze_sequence(
                sequence, deep_analysis=self.config["sequence_analysis_depth"]
            )

            # Create sequence object for registry
            class SequenceObject(MathematicalObjectInterface):
                def __init__(self, seq_data, name=None):
                    self.sequence_data = seq_data
                    self.name = name or f"sequence_{len(seq_data)}_terms"

                def get_canonical_form(self) -> str:
                    return str(self.sequence_data)

                def compute_hash(self) -> str:
                    return f"seq_{hash(tuple(self.sequence_data[:20]))}"  # Hash first 20 terms

                def get_properties(self) -> Dict[str, Any]:
                    return {
                        "length": len(self.sequence_data),
                        "terms": self.sequence_data,
                        "first_term": self.sequence_data[0] if self.sequence_data else None,
                        "last_term": self.sequence_data[-1] if self.sequence_data else None
                    }

                def get_object_type(self) -> str:
                    return "sequence"

            seq_obj = SequenceObject(sequence, sequence_name)
            seq_id = self.object_registry.register_object(
                seq_obj,
                tags={"sequence", "analysis_target"}
            )

            results = {
                "success": True,
                "sequence_id": seq_id,
                "sequence_name": sequence_name or f"sequence_{seq_id[:8]}",
                "sequence_length": len(sequence),
                "analysis_timestamp": start_time.isoformat()
            }

            # Extract analysis results
            results["patterns"] = [
                {
                    "type": pattern.pattern_type,
                    "formula": pattern.formula,
                    "confidence": pattern.confidence,
                    "description": pattern.description,
                    "parameters": pattern.parameters
                }
                for pattern in analysis_result.detected_patterns
            ]

            results["oeis_matches"] = [
                {
                    "sequence_id": match.sequence_id,
                    "name": match.name,
                    "match_confidence": match.match_confidence,
                    "url": match.url
                }
                for match in analysis_result.oeis_matches
            ]

            results["statistical_properties"] = analysis_result.statistical_properties
            results["continuation"] = analysis_result.continuation
            results["novelty_score"] = analysis_result.novelty_score
            results["generating_function"] = analysis_result.generating_function
            results["asymptotic_behavior"] = analysis_result.asymptotic_behavior

            # Store in persistence system
            if self.config["auto_persist_results"]:
                db_object_id = self.persistence_service.store_mathematical_object(
                    object_type="sequence",
                    name=results["sequence_name"],
                    canonical_form=str(sequence),
                    hash_value=seq_obj.compute_hash(),
                    properties=seq_obj.get_properties()
                )

                sequence_db_id = self.persistence_service.store_sequence(
                    object_id=db_object_id,
                    terms=sequence,
                    oeis_id=analysis_result.oeis_matches[0].sequence_id if analysis_result.oeis_matches else None,
                    detected_patterns=[p.__dict__ for p in analysis_result.detected_patterns],
                    statistical_properties=analysis_result.statistical_properties,
                    novelty_score=analysis_result.novelty_score,
                    generating_function=analysis_result.generating_function,
                    asymptotic_behavior=analysis_result.asymptotic_behavior
                )

                results["db_object_id"] = db_object_id
                results["db_sequence_id"] = sequence_db_id

            # Generate insights and conjectures
            insights = await self._generate_sequence_insights(analysis_result, results)
            results["insights"] = insights

            # Update session metrics
            if self.current_session:
                self.current_session.objects_analyzed += 1
                self.current_session.patterns_discovered += len(analysis_result.detected_patterns)

            computation_time = (datetime.now() - start_time).total_seconds()
            results["computation_time"] = computation_time
            self.metrics["computation_time_total"] += computation_time
            self.metrics["analyses_completed"] += 1

            logger.info(f"Sequence analysis completed in {computation_time:.2f}s")

            return results

        except MathematicsError as e:
            logger.error(f"Sequence analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "sequence_preview": sequence[:10] if sequence else [],
                "computation_time": (datetime.now() - start_time).total_seconds()
            }

    async def cross_analyze_objects(self,
                                   object_ids: List[str],
                                   analysis_type: str = "relationships") -> Dict[str, Any]:
        """Cross-analyze multiple mathematical objects for relationships"""
        start_time = datetime.now()

        try:
            if not self.config["enable_cross_domain_analysis"]:
                return {"success": False, "error": "Cross-domain analysis disabled"}

            logger.info(f"Cross-analyzing {len(object_ids)} objects")

            # Get objects from registry
            objects = []
            for obj_id in object_ids:
                obj = self.object_registry.get_object(obj_id)
                if obj:
                    objects.append(obj)

            if len(objects) < 2:
                return {"success": False, "error": "Need at least 2 objects for cross-analysis"}

            results = {
                "success": True,
                "analysis_type": analysis_type,
                "objects_analyzed": len(objects),
                "object_types": [obj.object_type for obj in objects],
                "relationships_found": [],
                "insights": [],
                "analysis_timestamp": start_time.isoformat()
            }

            # Analyze relationships between objects
            for i, obj1 in enumerate(objects):
                for _, obj2 in enumerate(objects[i+1:], i+1):
                    relationship = await self._analyze_object_relationship(obj1, obj2)
                    if relationship:
                        results["relationships_found"].append(relationship)

                        # Create relationship in registry if strong enough
                        if relationship["strength"] > 0.5:
                            self.object_registry.create_relationship(
                                obj1.object_id,
                                obj2.object_id,
                                relationship["type"],
                                strength=relationship["strength"]
                            )

            # Generate cross-domain insights
            if results["relationships_found"]:
                cross_insights = await self._generate_cross_domain_insights(objects, results["relationships_found"])
                results["insights"].extend(cross_insights)

            computation_time = (datetime.now() - start_time).total_seconds()
            results["computation_time"] = computation_time

            return results

        except MathematicsError as e:
            logger.error(f"Cross-analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "computation_time": (datetime.now() - start_time).total_seconds()
            }

    async def generate_conjecture(self,
                                 context: Dict[str, Any],
                                 conjecture_type: ConjectureType = ConjectureType.GENERAL) -> Optional[str]:
        """Generate a mathematical conjecture based on analysis context"""
        try:
            logger.info(f"Generating conjecture of type {conjecture_type}")

            # Extract relevant information from context
            if "insights" not in context or not context["insights"]:
                logger.warning("No insights provided for conjecture generation")
                return None

            insights = context["insights"]
            best_insights = [insight for insight in insights if insight.get("confidence", 0) > self.config["conjecture_confidence_threshold"]]

            if not best_insights:
                logger.info("No high-confidence insights for conjecture generation")
                return None

            # Generate conjecture based on best insight
            primary_insight = best_insights[0]

            conjecture_title = f"{conjecture_type.value.title()} Conjecture - {primary_insight.get('type', 'Unknown')}"

            # Si el contexto indica entero, usar plugin de teoría de números para statement(s)
            conjecture_statement = None
            if self.number_theory_plugin and isinstance(context.get("object_payload"), dict):
                payload = context["object_payload"]
                if payload.get("type") == "integer" and "value" in payload:
                    obj = MathematicalObject(
                        id=context.get("db_object_id", "int_obj"),
                        type="integer",
                        semantic_hash="hash",
                        payload_json=payload,
                    )
                    gen = self.number_theory_plugin.generate(obj)
                    if gen:
                        chosen = gen[0]
                        conjecture_statement = chosen.get("statement")
                        # evidence_ratio si engine disponible
                        if self.evidence_engine:
                            ev = self.evidence_engine.compute(chosen)
                            # anexar info de evidencia a contexto para persistencia
                            context.setdefault("evidence", {})[chosen.get("type", "unknown")] = ev
            if not conjecture_statement:
                conjecture_statement = self._formulate_conjecture_statement(primary_insight, context)

            if not conjecture_statement:
                return None

            # Store conjecture
            conjecture_id = self.persistence_service.store_conjecture(
                title=conjecture_title,
                statement=conjecture_statement,
                conjecture_type=conjecture_type,
                primary_object_id=context.get("db_object_id"),
                confidence=primary_insight.get("confidence", 0.5),
                motivation=f"Generated from analysis revealing: {primary_insight.get('description', 'mathematical pattern')}"
            )

            # Add supporting evidence
            for insight in best_insights:
                evidence = Evidence(
                    type="computational",
                    description=insight.get("description", "Mathematical analysis result"),
                    data=insight,
                    confidence=insight.get("confidence", 0.5),
                    source="mathematics_lab_analysis"
                )
                self.persistence_service.add_evidence(conjecture_id, evidence)

            # Ranking: calcular importance_score
            try:
                payload_for_score = {
                    "statement": conjecture_statement,
                    "evidence_ratio": float((context.get("evidence", {}) or {}).get("goldbach", {}).get("evidence_ratio", 0.0)),
                }
                importance = float(score_conjecture(payload_for_score))
                with self.persistence_service.get_db_session() as db:
                    c = db.query(Conjecture).filter_by(id=conjecture_id).first()
                    if c:
                        c.importance_score = max(0.0, min(1.0, importance))
                        db.commit()
            except MathematicsError:
                pass

            # Update metrics
            self.metrics["conjectures_generated"] += 1
            if self.current_session:
                self.current_session.conjectures_generated += 1

            logger.info(f"Generated conjecture: {conjecture_id}")
            return conjecture_id

        except MathematicsError as e:
            logger.error(f"Conjecture generation failed: {e}")
            return None

    async def get_analysis_summary(self) -> Dict[str, Any]:
        """Get comprehensive analysis summary"""
        # Get registry statistics
        registry_stats = self.object_registry.get_statistics()

        # Get persistence statistics
        db_stats = self.persistence_service.get_statistics()

        # Calculate success rate
        if self.metrics["analyses_completed"] > 0:
            self.metrics["success_rate"] = 1.0  # Simplified - could track failures

        uptime = (datetime.now() - self.metrics["uptime"]).total_seconds()

        summary = {
            "lab_info": {
                "id": self.lab_id,
                "version": self.version,
                "uptime_seconds": uptime
            },
            "performance_metrics": self.metrics,
            "object_registry": registry_stats,
            "database_statistics": db_stats,
            "current_session": self.current_session.__dict__ if self.current_session else None,
            "active_questions": len(self.active_questions),
            "insights_discovered": len(self.insights_history),
            "configuration": self.config
        }

        return summary

    async def analyze_point_cloud_topology(self,
                                           points: List[Dict[str, float]],
                                           epsilon: float = 0.2,
                                           epsilon_range: Optional[tuple] = None,
                                           num_steps: int = 20,
                                           max_dimension: int = 2,
                                           include_images: bool = True,
                                           generate_conjecture_flag: bool = True) -> Dict[str, Any]:
        """Flujo integrado de análisis topológico sobre una nube de puntos 2D.

        Retorna invariantes, persistencia y (opcionalmente) imágenes base64.
        Persiste un objeto topológico e insights básicos.
        """
        from app.services.topology_service import TopologyService
        import time
        start = time.time()
        epsilon_range = epsilon_range or (max(1e-3, 0.5 * epsilon), 3.0 * epsilon)

        # Registrar objeto topológico mínimo en el registro/persistencia
        class PointCloudObject(MathematicalObjectInterface):
            def __init__(self, pts: List[Dict[str, float]]):
                self.pts = pts
                self.object_type = "point_cloud"
                self.object_id = None
                self.properties_dict = {"n_points": len(pts)}

            def get_canonical_form(self) -> str:
                return str([[p.get("x"), p.get("y")] for p in self.pts])

            def compute_hash(self) -> str:
                return f"pc_{hash(tuple((p.get('x'), p.get('y')) for p in self.pts[:50]))}"

            def get_properties(self) -> Dict[str, Any]:
                return {"n_points": len(self.pts)}

            def get_object_type(self) -> str:
                return "point_cloud"

        pc_obj = PointCloudObject(points)
        pc_id = self.object_registry.register_object(pc_obj, tags={"topology", "point_cloud"})

        service = TopologyService()
        inv = await service.calculate_invariants(points=[(p["x"], p["y"]) for p in points], epsilon=epsilon)
        pers = await service.analyze_persistence(points=[(p["x"], p["y"]) for p in points],
                                                epsilon_range=epsilon_range,
                                                num_steps=num_steps,
                                                max_dimension=max_dimension)

        images = None
        if include_images:
            # Reutilizar lógica simple de render del router de reportes
            import io, base64
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            import numpy as np
            images = {}
            # PD
            fig, ax = plt.subplots(figsize=(5, 4), dpi=120)
            for item in pers.get("persistence_diagram", []):
                ax.scatter(float(item.get("birth", 0.0)), float(item.get("death", 0.0)), s=20)
            ax.plot([0, 1], [0, 1], transform=ax.transAxes, ls="--", c="gray", lw=1)
            buf = io.BytesIO(); plt.tight_layout(); fig.savefig(buf, format="png"); plt.close(fig); buf.seek(0)
            images["persistence_diagram_base64"] = base64.b64encode(buf.read()).decode("ascii")
            # Betti
            fig2, ax2 = plt.subplots(figsize=(5, 4), dpi=120)
            for k, v in pers.get("betti_curves", {}).items():
                ax2.plot(pers.get("epsilon_values", []), v, label=f"Betti {k}")
            ax2.legend(); buf2 = io.BytesIO(); plt.tight_layout(); fig2.savefig(buf2, format="png"); plt.close(fig2); buf2.seek(0)
            images["betti_curves_base64"] = base64.b64encode(buf2.read()).decode("ascii")

        # Persistencia de resultados mínimos en DB
        if self.config["auto_persist_results"]:
            db_object_id = self.persistence_service.store_mathematical_object(
                object_type="point_cloud",
                name=f"point_cloud_{pc_id[:8]}",
                canonical_form=pc_obj.get_canonical_form(),
                hash_value=pc_obj.compute_hash(),
                properties=pc_obj.get_properties(),
                invariants=inv,
            )
        else:
            db_object_id = None

        # Insight básico según componentes y ciclos estimados
        simple_insights = []
        comps = (inv or {}).get("components_est") or (inv or {}).get("components")
        if comps is not None:
            simple_insights.append({
                "type": "topology_components",
                "description": f"Se detectan {int(comps)} componentes a ε={epsilon}",
                "confidence": 0.7,
            })
        cycles = (inv or {}).get("cycles_est")
        if cycles is not None and cycles > 0:
            simple_insights.append({
                "type": "topology_cycles",
                "description": f"Se estiman {int(cycles)} ciclos a ε={epsilon}",
                "confidence": 0.7,
            })

        if self.current_session:
            self.current_session.objects_analyzed += 1
            self.current_session.patterns_discovered += len(simple_insights)

        result: Dict[str, Any] = {
            "success": True,
            "object_id": pc_id,
            "db_object_id": db_object_id,
            "invariants": inv,
            "persistence": {
                k: v for k, v in pers.items() if k in {"persistence_diagram", "betti_curves", "epsilon_values", "persistence_entropy"}
            },
            "images": images,
            "insights": simple_insights,
            "computation_time": time.time() - start,
        }

        # Generar y rankear conjetura a partir de insights topológicos (opcional)
        if generate_conjecture_flag and simple_insights:
            try:
                conj_id = await self.generate_conjecture(
                    context={
                        "insights": simple_insights,
                        "db_object_id": db_object_id,
                        "object_payload": {"type": "point_cloud", "n_points": len(points)}
                    },
                    conjecture_type=ConjectureType.GENERAL
                )
                if conj_id:
                    result["conjecture_id"] = conj_id
            except MathematicsError:
                # Conjetura opcional: no bloquear el flujo si falla
                pass

        return result

    async def _generate_curve_insights(self,
                                     curve: EllipticCurve,
                                     analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights from elliptic curve analysis"""
        insights = []

        # Discriminant insight
        discriminant = curve.discriminant()
        if abs(discriminant) < 100:
            insights.append({
                "type": "discriminant_analysis",
                "description": f"Small discriminant ({discriminant}) may indicate special arithmetic properties",
                "confidence": 0.7,
                "data": {"discriminant": discriminant}
            })

        # Rational points insight
        if "rational_points" in analysis:
            point_count = analysis["rational_points"]["count"]
            if point_count == 0:
                insights.append({
                    "type": "rational_points",
                    "description": "No rational points found - curve may have rank 0",
                    "confidence": 0.6,
                    "data": {"point_count": point_count}
                })
            elif point_count > 5:
                insights.append({
                    "type": "rational_points",
                    "description": f"Many rational points ({point_count}) suggest high rank",
                    "confidence": 0.8,
                    "data": {"point_count": point_count}
                })

        # Torsion analysis insight
        if "torsion_analysis" in analysis:
            torsion_order = analysis["torsion_analysis"]["estimated_torsion_order"]
            if torsion_order > 2:
                insights.append({
                    "type": "torsion_structure",
                    "description": f"Non-trivial torsion subgroup of order {torsion_order}",
                    "confidence": 0.75,
                    "data": {"torsion_order": torsion_order}
                })

        return insights

    async def _generate_sequence_insights(self,
                                        analysis: SequenceAnalysisResult,
                                        context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights from sequence analysis"""
        insights = []

        # Pattern confidence insight
        if analysis.detected_patterns:
            best_pattern = analysis.detected_patterns[0]
            if best_pattern.confidence > 0.9:
                insights.append({
                    "type": "pattern_detection",
                    "description": f"Strong {best_pattern.pattern_type} pattern detected with high confidence",
                    "confidence": best_pattern.confidence,
                    "data": {
                        "pattern_type": best_pattern.pattern_type,
                        "formula": best_pattern.formula
                    }
                })

        # OEIS novelty insight
        if not analysis.oeis_matches and analysis.novelty_score > 0.7:
            insights.append({
                "type": "novelty",
                "description": "Sequence not found in OEIS - potentially novel mathematical object",
                "confidence": analysis.novelty_score,
                "data": {"novelty_score": analysis.novelty_score}
            })
        elif analysis.oeis_matches:
            best_match = analysis.oeis_matches[0]
            if best_match.match_confidence > 0.95:
                insights.append({
                    "type": "oeis_identification",
                    "description": f"Sequence identified as OEIS {best_match.sequence_id}: {best_match.name}",
                    "confidence": best_match.match_confidence,
                    "data": {
                        "oeis_id": best_match.sequence_id,
                        "oeis_name": best_match.name
                    }
                })

        # Growth behavior insight
        if analysis.asymptotic_behavior:
            insights.append({
                "type": "asymptotic_behavior",
                "description": f"Sequence exhibits {analysis.asymptotic_behavior} growth",
                "confidence": 0.8,
                "data": {"asymptotic": analysis.asymptotic_behavior}
            })

        return insights

    async def _analyze_object_relationship(self, obj1, obj2) -> Optional[Dict[str, Any]]:
        """Analyze relationship between two mathematical objects"""
        # Simplified relationship analysis
        if obj1.object_type == obj2.object_type:
            return {
                "type": "same_type",
                "strength": 0.6,
                "description": f"Both objects are of type {obj1.object_type}"
            }

        # Check for property similarities
        props1 = obj1.properties_dict
        props2 = obj2.properties_dict

        common_props = set(props1.keys()) & set(props2.keys())
        if common_props:
            similarity = len(common_props) / max(len(props1), len(props2))
            if similarity > 0.3:
                return {
                    "type": "property_similarity",
                    "strength": similarity,
                    "description": f"Objects share {len(common_props)} common properties"
                }

        return None

    async def _generate_cross_domain_insights(self, objects, relationships) -> List[Dict[str, Any]]:
        """Generate insights from cross-domain analysis"""
        insights = []

        if len(relationships) > 1:
            insights.append({
                "type": "cross_domain_connections",
                "description": f"Found {len(relationships)} relationships between mathematical objects",
                "confidence": 0.7,
                "data": {"relationship_count": len(relationships)}
            })

        return insights

    def _formulate_conjecture_statement(self, insight: Dict[str, Any], context: Dict[str, Any]) -> Optional[str]:
        """Formulate a conjecture statement from an insight"""
        insight_type = insight.get("type", "")

        if insight_type == "rational_points":
            point_count = insight["data"]["point_count"]
            if point_count == 0:
                return "This elliptic curve has rank 0 over the rationals"
            elif point_count > 5:
                return f"This elliptic curve has rank ≥ {min(point_count // 3, 5)}"

        elif insight_type == "pattern_detection":
            pattern_type = insight["data"]["pattern_type"]
            formula = insight["data"].get("formula", "")
            return f"The analyzed sequence follows a {pattern_type} pattern with formula: {formula}"

        elif insight_type == "novelty":
            return "This sequence represents a previously unidentified mathematical pattern"

        elif insight_type == "discriminant_analysis":
            discriminant = insight["data"]["discriminant"]
            return f"Elliptic curves with discriminant {discriminant} exhibit special arithmetic properties"

        return None


async def demo_mathematical_laboratory_workflow():
    """Comprehensive demonstration of Mathematical Laboratory capabilities"""
    print("🧮 AXIOM Mathematical Computation Laboratory")
    print("=" * 60)

    async with MathematicalComputationLaboratory() as lab:
        # Start analysis session
        session_id = await lab.start_analysis_session(
            "Comprehensive mathematical analysis demonstration"
        )
        print(f"📊 Started analysis session: {session_id}")

        # Analyze elliptic curve
        print("\n🔵 Analyzing Elliptic Curve...")
        curve = EllipticCurve(a4=1, a6=1)  # y^2 = x^3 + x + 1
        curve_results = await lab.analyze_elliptic_curve(curve, deep_analysis=True)

        if curve_results["success"]:
            print(f"  ✅ Analysis successful: {len(curve_results.get('insights', []))} insights generated")
            print(f"  📈 Rational points found: {curve_results['rational_points']['count']}")
        else:
            print(f"  ❌ Analysis failed: {curve_results.get('error')}")

        # Analyze sequence
        print("\n📊 Analyzing Mathematical Sequence...")
        fibonacci = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        seq_results = await lab.analyze_sequence(fibonacci, "Fibonacci Sequence")

        if seq_results["success"]:
            print(f"  ✅ Analysis successful: {len(seq_results.get('patterns', []))} patterns detected")
            print(f"  🎯 OEIS matches: {len(seq_results.get('oeis_matches', []))}")
            print(f"  💡 Novelty score: {seq_results.get('novelty_score', 0):.2f}")
        else:
            print(f"  ❌ Analysis failed: {seq_results.get('error')}")

        # Cross-analyze objects if both analyses succeeded
        if curve_results.get("success") and seq_results.get("success"):
            print("\n🔗 Cross-analyzing Objects...")
            cross_results = await lab.cross_analyze_objects([
                curve_results["curve_id"],
                seq_results["sequence_id"]
            ])

            if cross_results["success"]:
                print(f"  ✅ Found {len(cross_results['relationships_found'])} relationships")
                print(f"  💭 Generated {len(cross_results['insights'])} cross-domain insights")
            else:
                print(f"  ❌ Cross-analysis failed: {cross_results.get('error')}")

        # Generate conjectures
        print("\n🧠 Generating Mathematical Conjectures...")
        conjectures_generated = 0

        if curve_results.get("success") and curve_results.get("insights"):
            conjecture_id = await lab.generate_conjecture(
                curve_results, ConjectureType.ELLIPTIC_CURVE
            )
            if conjecture_id:
                conjectures_generated += 1
                print(f"  📝 Generated elliptic curve conjecture: {conjecture_id[:8]}...")

        if seq_results.get("success") and seq_results.get("insights"):
            conjecture_id = await lab.generate_conjecture(
                seq_results, ConjectureType.SEQUENCE_PATTERN
            )
            if conjecture_id:
                conjectures_generated += 1
                print(f"  📝 Generated sequence conjecture: {conjecture_id[:8]}...")

        print(f"  🎯 Total conjectures generated: {conjectures_generated}")

        # End session and get summary
        print("\n📋 Analysis Session Summary:")
        session_summary = await lab.end_analysis_session()
        if session_summary:
            print(f"  ⏱️  Duration: {session_summary['duration_seconds']:.1f} seconds")
            print(f"  🔬 Objects analyzed: {session_summary['objects_analyzed']}")
            print(f"  🔍 Patterns discovered: {session_summary['patterns_discovered']}")
            print(f"  🧠 Conjectures generated: {session_summary['conjectures_generated']}")

        # Get overall summary
        print("\n📊 Laboratory Performance Summary:")
        summary = await lab.get_analysis_summary()
        metrics = summary["performance_metrics"]
        print(f"  📈 Total analyses: {metrics['analyses_completed']}")
        print(f"  🧮 Total computation time: {metrics['computation_time_total']:.1f}s")
        print(f"  🧠 Total conjectures: {metrics['conjectures_generated']}")
        print(f"  📚 Database objects: {summary['database_statistics']['mathematical_objects']}")
        print(f"  🔗 Registry objects: {summary['object_registry']['total_objects']}")


if __name__ == "__main__":
    asyncio.run(demo_mathematical_laboratory_workflow())