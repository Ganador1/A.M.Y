"""Loop autónomo de medicina para descubrimiento de fármacos y validación clínica"""
from __future__ import annotations

import asyncio
import random
import time
from typing import Any, Dict, List, Optional

from app.autonomous.core.priority_scoring import PriorityScorer
from app.autonomous.core.state_manager import IterationRecord, StateManager
from app.autonomous.evaluation.empirical_feedback import process_feedback
from app.autonomous.evaluation.novelty_assessor import NoveltyAssessor
from app.autonomous.metrics.telemetry_collector import AutonomousTelemetry
from app.autonomous.models.importance_ranker import ImportanceRanker
from app.autonomous.integration import EvidenceSummary, ToolEvidenceBridge
from app.core.bootstrap_logging import logger

# Advanced medical services
from app.domains.medicine.services.advanced_medical_imaging_service import AdvancedMedicalImagingService
from app.domains.medicine.advanced_clinical_validation_service import AdvancedClinicalValidationService
from app.domains.medicine.services.alphafold3_service import AlphaFold3ProteinStructureService
from app.services.advanced_knowledge_graph_service import AdvancedKnowledgeGraphService
# ⭐ SERVICIOS MÉDICOS ADICIONALES (3 servicios)
from app.domains.medicine.services.personalized_medicine_service import PersonalizedMedicineService
from app.domains.medicine.services.clinicalbert_service import ClinicalBERTService
from app.domains.medicine.services.medical_realtime_service import MedicalRealtimeService


class MedicineLoop:
    """Autonomous research loop for medicine domain focusing on drug discovery and clinical validation"""
    
    def __init__(
        self,
        state: StateManager | None = None,
        telemetry: AutonomousTelemetry | None = None,
    ):
        self.state = state or StateManager()
        self.telemetry = telemetry or AutonomousTelemetry()
        self.priority = PriorityScorer()
        self.novelty = NoveltyAssessor()
        self.importance_ranker = ImportanceRanker(w_freq=0.2, w_dependency=0.2, w_impact=0.6)
        self.iteration = 0
        self.rng = random.Random(777)
        
        # Advanced medical services
        self.medical_imaging_service = AdvancedMedicalImagingService()
        self.clinical_validation_service = AdvancedClinicalValidationService()
        self.alphafold_service = AlphaFold3ProteinStructureService()
        self.knowledge_graph_service = AdvancedKnowledgeGraphService()
        # ⭐ SERVICIOS MÉDICOS ADICIONALES (3 servicios)
        self.personalized_medicine = PersonalizedMedicineService()  # Personalized treatment recommendations
        self.clinical_bert = ClinicalBERTService()  # Clinical NLP and entity extraction
        self.realtime_monitoring = MedicalRealtimeService()  # Real-time patient monitoring
        
        self.tool_evidence = ToolEvidenceBridge(default_domain="medicine")
        # Backwards compatibility for legacy integrations/tests
        self.evidence = self.tool_evidence
        self._last_drug_candidates: Optional[List[Dict[str, Any]]] = None

    @staticmethod
    def _run_coro_sync(coro):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)
        new_loop = asyncio.new_event_loop()
        try:
            return new_loop.run_until_complete(coro)
        finally:
            new_loop.close()

    async def _fetch_drug_candidates_async(self, limit: int = 7) -> List[Dict[str, Any]]:
        """Fetch drug candidates using advanced medical services.
        
        Uses:
        - AlphaFold3Service for protein-ligand predictions
        - AdvancedKnowledgeGraphService for drug-disease knowledge
        - AdvancedClinicalValidationService for clinical viability
        """
        candidates: List[Dict[str, Any]] = []
        
        try:
            # 1. Search knowledge graph for drug-disease relationships
            kg_payload = {
                "action": "query",
                "node_type": "drug",
                "filters": {"status": "candidate", "domain": "medicine"},
                "limit": 10,
            }
            kg_result = await self.knowledge_graph_service.process_request(kg_payload)
            
            if kg_result.get("success"):
                drug_nodes = kg_result.get("nodes", [])
                logger.info(f"Found {len(drug_nodes)} drug candidates in knowledge graph")
                
                for idx, drug_node in enumerate(drug_nodes[:limit]):
                    # Extract drug properties from knowledge graph
                    drug_properties = drug_node.get("properties", {})
                    smiles = drug_properties.get("smiles", f"C1=CC=CC=C1{'O' * self.rng.randint(1, 3)}")  # Fallback SMILES
                    target_protein = drug_properties.get("target_protein", "Unknown")
                    
                    # Calculate metrics from graph centrality
                    centrality = drug_node.get("centrality_score", self.rng.random())
                    connections = drug_node.get("edge_count", self.rng.randint(3, 15))
                    
                    candidates.append({
                        "id": drug_node.get("id", f"drug_kg_{self.iteration}_{idx}"),
                        "smiles": smiles,
                        "target_protein": target_protein,
                        "anomaly_index": float(centrality),
                        "impact_potential": min(1.0, connections / 20.0),
                        "literature_frequency": drug_properties.get("citation_count", self.rng.randint(5, 100)),
                        "dependency_count": connections,
                        "proveability": float(centrality),
                        "novelty": 0.75 if drug_properties.get("status") == "candidate" else 0.50,
                        "information_gain": (centrality + (connections / 20.0)) / 2.0,
                        "estimated_cost": self.rng.random() * 0.3 + 0.1,
                        "source": "knowledge_graph",
                        "kg_cluster": drug_node.get("cluster_id"),
                    })
        except Exception as exc:
            logger.warning(f"Knowledge graph drug search failed: {exc}")
        
        try:
            # 2. Generate protein-ligand predictions with AlphaFold3
            # Use common drug targets
            target_proteins = [
                ("MEVKLSHYSGLFGPMFSFLTPQVKTFCGRIRNNYRWRCKNQNTFLRTTFANVVNVCGNPRCVKPGNFTCAFGTC", "COVID-19 Spike"),  # Short sequence
                ("MKLLAA" * 20, "Kinase Target"),  # ~120 AA
            ]
            
            test_ligands = [
                "CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin
                "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",  # Ibuprofen
                "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine
            ]
            
            for idx, (protein_seq, protein_name) in enumerate(target_proteins[:2]):
                for lig_idx, ligand_smiles in enumerate(test_ligands[:2]):
                    try:
                        # Predict protein-ligand binding
                        binding_result = await self.alphafold_service.predict_protein_ligand(
                            protein_sequence=protein_seq,
                            ligand_smiles=ligand_smiles
                        )
                        
                        if binding_result.get("success"):
                            binding_data = binding_result.get("binding_prediction", {})
                            affinity = binding_data.get("binding_affinity", 0.0)
                            confidence = binding_data.get("confidence_score", 0.5)
                            
                            # Convert binding affinity to impact (stronger binding = higher impact)
                            # Affinity typically in range -12 to -4 (log KD)
                            normalized_affinity = min(1.0, abs(affinity) / 12.0)
                            
                            candidates.append({
                                "id": f"alphafold_{self.iteration}_{idx}_{lig_idx}",
                                "smiles": ligand_smiles,
                                "target_protein": protein_name,
                                "protein_sequence_length": len(protein_seq),
                                "binding_affinity": affinity,
                                "anomaly_index": float(normalized_affinity),
                                "impact_potential": float(confidence),
                                "literature_frequency": self.rng.randint(10, 80),
                                "dependency_count": len(binding_data.get("binding_site", [])),
                                "proveability": float(confidence),
                                "novelty": 0.85,  # AlphaFold predictions are novel
                                "information_gain": (normalized_affinity + confidence) / 2.0,
                                "estimated_cost": 0.25,
                                "source": "alphafold3",
                                "binding_confidence": confidence,
                                "binding_site_residues": binding_data.get("binding_site", [])[:5],  # Top 5 residues
                            })
                    except Exception as ligand_exc:
                        logger.debug(f"Protein-ligand prediction failed for {protein_name}: {ligand_exc}")
                        continue
        except Exception as exc:
            logger.warning(f"AlphaFold3 drug discovery failed: {exc}")
        
        # If we have candidates, return them
        if candidates:
            logger.info(f"Fetched {len(candidates)} drug candidates from medical services")
            self._last_drug_candidates = candidates
            return candidates[:limit]
        
        # Fallback: Synthetic drug candidates
        logger.warning("All medical services failed, using synthetic drug candidates")
        return self._seed_synthetic_drugs(limit)

    def _seed_synthetic_drugs(self, k: int = 7) -> List[Dict[str, Any]]:
        """Fallback: Generate synthetic drug candidates"""
        candidates: List[Dict[str, Any]] = []
        
        for i in range(k):
            binding_affinity = self.rng.uniform(-10.0, -5.0)
            selectivity = self.rng.random()
            
            candidates.append({
                "id": f"synthetic_drug_{self.iteration}_{i}",
                "smiles": f"C1=CC=C{i}C=C1",  # Simplified SMILES
                "target_protein": f"Target_{i % 3}",
                "binding_affinity": binding_affinity,
                "anomaly_index": abs(binding_affinity) / 10.0,
                "impact_potential": selectivity,
                "literature_frequency": self.rng.randint(1, 30),
                "dependency_count": self.rng.randint(1, 5),
                "proveability": self.rng.random(),
                "novelty": self.rng.random(),
                "information_gain": (abs(binding_affinity) / 10.0 + selectivity) / 2.0,
                "estimated_cost": self.rng.random() * 0.4,
                "source": "synthetic",
            })
        
        return candidates

    async def _enrich_candidate_async(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich drug candidate with clinical validation and imaging analysis"""
        enrichment: Dict[str, Any] = {}
        
        # 1. Clinical validation if binding data available
        if "binding_affinity" in candidate:
            try:
                validation_payload = {
                    "action": "validate_drug_candidate",
                    "binding_affinity": candidate["binding_affinity"],
                    "selectivity": candidate.get("impact_potential", 0.5),
                    "target": candidate.get("target_protein", "Unknown"),
                }
                validation_result = await self.clinical_validation_service.process_request(validation_payload)
                
                if validation_result.get("success"):
                    enrichment["clinical_validation"] = validation_result.get("validation", {})
            except Exception as exc:
                logger.debug(f"Clinical validation failed for {candidate.get('id')}: {exc}")
                enrichment["clinical_validation"] = {"error": str(exc)}
        
        # 2. Medical imaging analysis (for structural validation)
        try:
            imaging_payload = {
                "action": "analyze_structure",
                "structure_type": "protein_ligand",
                "candidate_id": candidate.get("id"),
            }
            imaging_result = await self.medical_imaging_service.process_request(imaging_payload)
            
            if imaging_result.get("success"):
                analysis_payload = imaging_result.get("analysis", imaging_result.get("structural_analysis", {}))
                enrichment["structural_analysis"] = analysis_payload
                # Provide alias expected by some callers/tests
                enrichment["medical_imaging"] = analysis_payload
        except Exception as exc:
            logger.debug(f"Medical imaging analysis failed: {exc}")
            enrichment["structural_analysis"] = {"error": str(exc)}
            enrichment.setdefault("medical_imaging", {"error": str(exc)})
        
        return enrichment

    def _build_drug_hypothesis(
        self,
        candidate: Dict[str, Any],
        enrichment: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build hypothesis for drug candidate validation"""
        candidate_id = candidate.get("id", "unknown")
        target = candidate.get("target_protein", "Unknown")
        smiles = candidate.get("smiles", "")
        
        description = (
            f"Validate drug candidate {candidate_id} targeting {target} with "
            f"binding affinity {candidate.get('binding_affinity', 'N/A')} and "
            f"predicted selectivity {candidate.get('impact_potential', 0.0):.2f}"
        )
        
        variables: Dict[str, Any] = {
            "candidate_id": candidate_id,
            "target_protein": target,
            "smiles": smiles,
            "binding_affinity": candidate.get("binding_affinity"),
            "source": candidate.get("source"),
            "enrichment": enrichment,
        }
        
        assumptions = [
            "Protein structure predictions are accurate (AlphaFold3 or experimental)",
            "Binding affinity correlates with therapeutic efficacy",
            "Clinical validation metrics represent real-world outcomes",
        ]
        
        extras = {
            "parameters": {
                "binding_site": candidate.get("binding_site_residues", []),
                "confidence": candidate.get("binding_confidence"),
            },
            "keywords": ["drug_discovery", "protein_ligand", target, "clinical_validation"],
        }
        
        return self.tool_evidence.build_hypothesis(
            title=f"Drug Discovery: {candidate_id} → {target}",
            description=description,
            variables=variables,
            assumptions=assumptions,
            expected_outcome="Determine therapeutic viability and clinical priority",
            extras=extras,
        )

    async def _run_iteration_impl(
        self,
        top_n: int = 4,
        iteration_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        start = time.time()
        self.iteration += 1

        seed_count = max(top_n * 2, 6)
        
        # Fetch drug candidates from medical services
        candidates = await self._fetch_drug_candidates_async(seed_count)

        # Rank by importance and priority
        ranked_importance = self.importance_ranker.rank(candidates)
        scored = self.priority.rank(ranked_importance)
        selected = scored[:top_n]

        if not selected:
            logger.warning("No drug candidates available for iteration %d", self.iteration)
            return {"success": False, "reason": "no_candidates", "processed_count": 0}

        actions: List[str] = []
        outcomes: Dict[str, Any] = {}
        enriched_selected: List[Dict[str, Any]] = []
        novelty_scores: List[float] = []
        support_scores: List[float] = []

        for idx, candidate in enumerate(selected):
            # Novelty assessment
            novelty_res = self.novelty.assess([
                candidate["binding_affinity"] if "binding_affinity" in candidate else candidate["anomaly_index"],
                candidate["impact_potential"],
                candidate["information_gain"],
            ])
            novelty_scores.append(novelty_res["novelty_score"])
            
            # Enrich top 2 candidates
            enrichment = await self._enrich_candidate_async(candidate) if idx < 2 else {}
            
            # Tool evidence corroboration
            evidence_summary: Optional[EvidenceSummary] = None
            summary_data: Optional[Dict[str, Any]] = None
            if self.tool_evidence:
                try:
                    hypothesis = self._build_drug_hypothesis(candidate, enrichment)
                    evidence_summary = await self.tool_evidence.corroborate(hypothesis, domain="medicine")
                    success_flag = False
                    support_score = 0.0

                    if isinstance(evidence_summary, dict):
                        summary_data = evidence_summary
                        support_score = float(summary_data.get("support_score", summary_data.get("confidence", 0.0)))
                        success_flag = summary_data.get("success", True)
                    else:
                        summary_data = evidence_summary.as_dict()
                        support_score = float(getattr(evidence_summary, "support_score", 0.0))
                        success_flag = getattr(evidence_summary, "success", True)

                    if success_flag:
                        candidate["impact_potential"] = min(
                            1.0,
                            float(candidate.get("impact_potential", 0.5)) + support_score * 0.15,
                        )
                    support_scores.append(support_score)
                except Exception as exc:
                    logger.debug(f"Drug hypothesis corroboration failed for {candidate.get('id')}: {exc}")
                    support_scores.append(0.0)
            
            actions.append("drug_validation")
            
            outcome_payload: Dict[str, Any] = {
                "novelty_score": novelty_res["novelty_score"],
                "target_protein": candidate.get("target_protein"),
                "binding_affinity": candidate.get("binding_affinity"),
                "source": candidate.get("source"),
                "enrichment": enrichment or None,
            }
            
            if summary_data is not None:
                outcome_payload["tool_evidence"] = summary_data
            
            outcomes[candidate["id"]] = outcome_payload
            enriched_selected.append({**candidate, "enrichment": enrichment, "novelty": novelty_res})

        # Feedback processing
        feedback_event = {
            "metric_name": "therapeutic_potential",
            "value": len(selected),
            "improved": len(selected) > 0,
            "confidence": 0.68,
        }
        feedback_result = process_feedback(feedback_event)

        # Record iteration
        record = IterationRecord(
            iteration=self.iteration,
            domain="medicine",
            selected_ids=[s["id"] for s in selected],
            actions=actions,
            outcomes={**outcomes, "feedback_adjustment": feedback_result["adjustment"]},
        )
        self.state.add_iteration(record)

        # Calculate metrics
        duration = time.time() - start
        avg_novelty = sum(novelty_scores) / len(novelty_scores) if novelty_scores else 0.0
        avg_support = sum(support_scores) / len(support_scores) if support_scores else 0.0
        avg_affinity = sum(
            abs(c.get("binding_affinity", 0.0)) for c in selected if "binding_affinity" in c
        ) / len([c for c in selected if "binding_affinity" in c]) if any("binding_affinity" in c for c in selected) else 0.0
        
        summary = {
            "iteration": self.iteration,
            "duration_s": duration,
            "selected": len(selected),
            "actions": actions,
            "avg_novelty": avg_novelty,
            "avg_support_score": avg_support,
            "avg_binding_affinity": avg_affinity,
        }

        # Telemetry
        try:
            self.telemetry.record_iteration(
                domain="medicine",
                duration_s=duration,
                selected=len(selected),
                mutations=0,
                sketches=0,
            )
        except Exception as exc:
            logger.warning("Telemetry recording failed (medicine): %s", exc)

        # Metrics
        try:
            from app.monitoring.metrics import metrics
            
            metrics.set_gauge("autonomous_novelty_last", float(avg_novelty))
            metrics.set_gauge("autonomous_feedback_adjustment_last", feedback_result["adjustment"])
            if support_scores:
                metrics.set_gauge("autonomous_support_score_last", avg_support)
            if avg_affinity > 0:
                metrics.set_gauge("medicine_avg_binding_affinity", avg_affinity)
        except (ImportError, AttributeError):
            logger.debug("Could not set medicine gauges")

        logger.info("Medicine loop iteration %d: %s", self.iteration, summary)
        
        return {
            "success": True,
            "summary": summary,
            "selected": enriched_selected,
            "outcomes": outcomes,
            "feedback": feedback_result,
            "avg_support_score": avg_support,
            "avg_binding_affinity": avg_affinity,
            "processed_count": len(selected),
        }

    def run_iteration(
        self,
        top_n: int = 4,
        iteration_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Synchronous wrapper for iteration execution"""
        return self._run_coro_sync(self._run_iteration_impl(top_n=top_n, iteration_data=iteration_data))

    async def run_drug_discovery_iteration(
        self,
        top_n: int = 4,
        iteration_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Async drug discovery iteration"""
        return await self._run_iteration_impl(top_n=top_n, iteration_data=iteration_data)


__all__ = ["MedicineLoop"]
