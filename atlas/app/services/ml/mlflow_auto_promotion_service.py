"""
MLflow Auto Promotion Service - AXIOM META 4

Servicio para promoción automática de modelos basada en métricas y políticas.
Integra con MLflow Registry para gestionar el ciclo de vida de modelos.
"""

import mlflow
from mlflow.tracking import MlflowClient
from mlflow.exceptions import RestException
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import os
import json
import aiofiles
import asyncio

from app.services.base_service import BaseService
from app.services.mlflow_registry_service import MLflowRegistryService
from app.core.bootstrap_logging import logger
from app.config import settings
from app.exceptions.infrastructure.api import APIError


@dataclass
class PromotionPolicy:
    """Política de promoción de modelos"""
    name: str
    description: str
    
    # Criterios de métricas
    min_accuracy: Optional[float] = None
    min_precision: Optional[float] = None
    min_recall: Optional[float] = None
    min_f1_score: Optional[float] = None
    min_roc_auc: Optional[float] = None
    min_pr_auc: Optional[float] = None
    
    # Criterios de calibración
    max_ece: Optional[float] = None  # Expected Calibration Error
    max_brier_score: Optional[float] = None
    min_reliability: Optional[float] = None
    
    # Criterios temporales
    min_age_hours: int = 24  # Tiempo mínimo antes de promoción
    max_age_days: Optional[int] = None  # Tiempo máximo para considerar modelo
    
    # Criterios de estabilidad
    min_cv_runs: int = 3  # Mínimo de runs de validación cruzada
    max_cv_std: Optional[float] = None  # Máxima desviación estándar en CV
    
    # Criterios de comparación
    improvement_threshold: float = 0.01  # Mejora mínima sobre modelo actual
    
    # Configuración de stages
    source_stage: str = "None"  # Stage origen
    target_stage: str = "Staging"  # Stage destino
    
    # Configuración de aprobación
    require_manual_approval: bool = False
    auto_archive_previous: bool = True


@dataclass
class PromotionCandidate:
    """Candidato para promoción"""
    model_name: str
    version: str
    run_id: str
    metrics: Dict[str, float]
    calibration_metrics: Dict[str, float]
    creation_timestamp: int
    current_stage: str
    
    # Evaluación
    meets_criteria: bool = False
    promotion_score: float = 0.0
    reasons: List[str] = field(default_factory=list)
    blocking_issues: List[str] = field(default_factory=list)


class MLflowAutoPromotionService(BaseService):
    """
    Servicio de promoción automática de modelos MLflow
    
    Características:
    - Políticas configurables de promoción
    - Evaluación automática de candidatos
    - Promoción basada en métricas y calibración
    - Integración con pipeline de metadata
    - Logging completo de decisiones
    """

    def __init__(self):
        super().__init__("MLflowAutoPromotion")
        
        # Configurar MLflow
        self.tracking_uri = settings.MLFLOW_TRACKING_URI, "file:./mlruns")
        mlflow.set_tracking_uri(self.tracking_uri)
        
        self.client = MlflowClient(self.tracking_uri)
        self.registry_service = MLflowRegistryService()
        
        # Políticas predefinidas
        self.policies = self._load_default_policies()
        
        logger.info(f"✅ MLflowAutoPromotionService initialized with {len(self.policies)} policies")

    def _load_default_policies(self) -> Dict[str, PromotionPolicy]:
        """Cargar políticas de promoción predefinidas"""
        policies = {}
        
        # Política conservadora para staging
        policies["conservative_staging"] = PromotionPolicy(
            name="conservative_staging",
            description="Política conservadora para promoción a Staging",
            min_accuracy=0.85,
            min_f1_score=0.80,
            min_roc_auc=0.85,
            max_ece=0.15,
            max_brier_score=0.25,
            min_age_hours=6,
            min_cv_runs=3,
            max_cv_std=0.05,
            improvement_threshold=0.02,
            source_stage="None",
            target_stage="Staging",
            require_manual_approval=False,
            auto_archive_previous=True
        )
        
        # Política estricta para producción
        policies["strict_production"] = PromotionPolicy(
            name="strict_production",
            description="Política estricta para promoción a Production",
            min_accuracy=0.90,
            min_precision=0.88,
            min_recall=0.85,
            min_f1_score=0.87,
            min_roc_auc=0.90,
            min_pr_auc=0.85,
            max_ece=0.10,
            max_brier_score=0.20,
            min_reliability=0.85,
            min_age_hours=48,
            min_cv_runs=5,
            max_cv_std=0.03,
            improvement_threshold=0.03,
            source_stage="Staging",
            target_stage="Production",
            require_manual_approval=True,
            auto_archive_previous=False
        )
        
        # Política para modelos de plausibilidad
        policies["plausibility_staging"] = PromotionPolicy(
            name="plausibility_staging",
            description="Política específica para modelos de plausibilidad",
            min_accuracy=0.82,
            min_f1_score=0.78,
            min_roc_auc=0.82,
            min_pr_auc=0.75,
            max_ece=0.12,
            max_brier_score=0.22,
            min_age_hours=12,
            min_cv_runs=3,
            max_cv_std=0.04,
            improvement_threshold=0.015,
            source_stage="None",
            target_stage="Staging",
            require_manual_approval=False,
            auto_archive_previous=True
        )
        
        return policies

    async def evaluate_promotion_candidates(self, policy_name: str = "conservative_staging") -> Dict[str, Any]:
        """
        Evaluar candidatos para promoción según política especificada
        """
        try:
            if policy_name not in self.policies:
                return {
                    "success": False,
                    "error": f"Política no encontrada: {policy_name}",
                    "available_policies": list(self.policies.keys())
                }
            
            policy = self.policies[policy_name]
            
            # Buscar modelos en el stage origen
            search_filter = f"current_stage='{policy.source_stage}'"
            model_versions = self.client.search_model_versions(
                filter_string=search_filter,
                max_results=100,
                order_by=["creation_timestamp DESC"]
            )
            
            candidates = []
            for version in model_versions:
                candidate = await self._evaluate_single_candidate(version, policy)
                candidates.append(candidate)
            
            # Ordenar por score de promoción
            candidates.sort(key=lambda x: x.promotion_score, reverse=True)
            
            # Filtrar candidatos que cumplen criterios
            eligible_candidates = [c for c in candidates if c.meets_criteria]
            
            return {
                "success": True,
                "policy_used": policy_name,
                "total_candidates": len(candidates),
                "eligible_candidates": len(eligible_candidates),
                "candidates": [self._candidate_to_dict(c) for c in candidates[:10]],  # Top 10
                "eligible_for_promotion": [self._candidate_to_dict(c) for c in eligible_candidates]
            }
            
        except APIError as e:
            return self.handle_error(e, "evaluate_promotion_candidates")

    async def _evaluate_single_candidate(self, model_version, policy: PromotionPolicy) -> PromotionCandidate:
        """Evaluar un candidato individual"""
        try:
            # Obtener métricas del run
            run = self.client.get_run(model_version.run_id)
            metrics = run.data.metrics
            
            # Obtener métricas de calibración si están disponibles
            calibration_metrics = {}
            for key, value in metrics.items():
                if any(cal_key in key.lower() for cal_key in ['ece', 'brier', 'calibration', 'reliability']):
                    calibration_metrics[key] = value
            
            candidate = PromotionCandidate(
                model_name=model_version.name,
                version=model_version.version,
                run_id=model_version.run_id,
                metrics=metrics,
                calibration_metrics=calibration_metrics,
                creation_timestamp=model_version.creation_timestamp,
                current_stage=model_version.current_stage
            )
            
            # Evaluar criterios
            score = 0.0
            reasons = []
            blocking_issues = []
            
            # Criterios de métricas básicas
            if policy.min_accuracy and metrics.get('accuracy', 0) >= policy.min_accuracy:
                score += 10
                reasons.append(f"Accuracy: {metrics.get('accuracy', 0):.3f} >= {policy.min_accuracy}")
            elif policy.min_accuracy:
                blocking_issues.append(f"Accuracy insuficiente: {metrics.get('accuracy', 0):.3f} < {policy.min_accuracy}")
            
            if policy.min_f1_score and metrics.get('f1_score', 0) >= policy.min_f1_score:
                score += 10
                reasons.append(f"F1-Score: {metrics.get('f1_score', 0):.3f} >= {policy.min_f1_score}")
            elif policy.min_f1_score:
                blocking_issues.append(f"F1-Score insuficiente: {metrics.get('f1_score', 0):.3f} < {policy.min_f1_score}")
            
            if policy.min_roc_auc and metrics.get('roc_auc', 0) >= policy.min_roc_auc:
                score += 10
                reasons.append(f"ROC-AUC: {metrics.get('roc_auc', 0):.3f} >= {policy.min_roc_auc}")
            elif policy.min_roc_auc:
                blocking_issues.append(f"ROC-AUC insuficiente: {metrics.get('roc_auc', 0):.3f} < {policy.min_roc_auc}")
            
            # Criterios de calibración
            if policy.max_ece:
                ece_value = calibration_metrics.get('ece', metrics.get('ece', 1.0))
                if ece_value <= policy.max_ece:
                    score += 15
                    reasons.append(f"ECE: {ece_value:.3f} <= {policy.max_ece}")
                else:
                    blocking_issues.append(f"ECE demasiado alto: {ece_value:.3f} > {policy.max_ece}")
            
            if policy.max_brier_score:
                brier_value = calibration_metrics.get('brier_score', metrics.get('brier_score', 2.0))
                if brier_value <= policy.max_brier_score:
                    score += 15
                    reasons.append(f"Brier Score: {brier_value:.3f} <= {policy.max_brier_score}")
                else:
                    blocking_issues.append(f"Brier Score demasiado alto: {brier_value:.3f} > {policy.max_brier_score}")
            
            # Criterios temporales
            model_age_hours = (datetime.now().timestamp() - model_version.creation_timestamp / 1000) / 3600
            if model_age_hours >= policy.min_age_hours:
                score += 5
                reasons.append(f"Edad del modelo: {model_age_hours:.1f}h >= {policy.min_age_hours}h")
            else:
                blocking_issues.append(f"Modelo muy reciente: {model_age_hours:.1f}h < {policy.min_age_hours}h")
            
            # Criterios de validación cruzada
            cv_mean = metrics.get('cv_mean', metrics.get('cv_score_mean'))
            cv_std = metrics.get('cv_std', metrics.get('cv_score_std'))
            
            if cv_mean and cv_std:
                if policy.max_cv_std and cv_std <= policy.max_cv_std:
                    score += 10
                    reasons.append(f"CV estabilidad: std={cv_std:.3f} <= {policy.max_cv_std}")
                elif policy.max_cv_std:
                    blocking_issues.append(f"CV inestable: std={cv_std:.3f} > {policy.max_cv_std}")
            
            # Comparación con modelo actual en target stage
            current_production_score = await self._get_current_stage_performance(
                model_version.name, policy.target_stage
            )
            
            if current_production_score:
                primary_metric = metrics.get('accuracy', metrics.get('f1_score', 0))
                improvement = primary_metric - current_production_score
                
                if improvement >= policy.improvement_threshold:
                    score += 20
                    reasons.append(f"Mejora: +{improvement:.3f} >= {policy.improvement_threshold}")
                else:
                    blocking_issues.append(f"Mejora insuficiente: +{improvement:.3f} < {policy.improvement_threshold}")
            else:
                # No hay modelo actual, dar puntos por ser el primero
                score += 10
                reasons.append("Primer modelo para este stage")
            
            # Determinar si cumple criterios
            candidate.meets_criteria = len(blocking_issues) == 0 and score >= 50
            candidate.promotion_score = score
            candidate.reasons = reasons
            candidate.blocking_issues = blocking_issues
            
            return candidate
            
        except APIError as e:
            logger.error(f"Error evaluando candidato {model_version.name} v{model_version.version}: {e}")
            return PromotionCandidate(
                model_name=model_version.name,
                version=model_version.version,
                run_id=model_version.run_id,
                metrics={},
                calibration_metrics={},
                creation_timestamp=model_version.creation_timestamp,
                current_stage=model_version.current_stage,
                meets_criteria=False,
                promotion_score=0.0,
                blocking_issues=[f"Error en evaluación: {str(e)}"]
            )

    async def _get_current_stage_performance(self, model_name: str, stage: str) -> Optional[float]:
        """Obtener performance del modelo actual en un stage"""
        try:
            latest_versions = self.client.get_latest_versions(model_name, stages=[stage])
            if not latest_versions:
                return None
            
            current_version = latest_versions[0]
            run = self.client.get_run(current_version.run_id)
            
            # Buscar métrica primaria
            metrics = run.data.metrics
            return metrics.get('accuracy', metrics.get('f1_score', metrics.get('roc_auc')))
            
        except APIError:
            return None

    async def auto_promote_eligible_models(self, policy_name: str = "conservative_staging", dry_run: bool = True) -> Dict[str, Any]:
        """
        Promocionar automáticamente modelos elegibles
        """
        try:
            # Evaluar candidatos
            evaluation_result = await self.evaluate_promotion_candidates(policy_name)
            
            if not evaluation_result["success"]:
                return evaluation_result
            
            policy = self.policies[policy_name]
            eligible_candidates = evaluation_result["eligible_for_promotion"]
            
            promotions = []
            errors = []
            
            for candidate_dict in eligible_candidates:
                if policy.require_manual_approval and not dry_run:
                    # Crear solicitud de aprobación manual
                    approval_request = {
                        "model_name": candidate_dict["model_name"],
                        "version": candidate_dict["version"],
                        "policy": policy_name,
                        "target_stage": policy.target_stage,
                        "promotion_score": candidate_dict["promotion_score"],
                        "reasons": candidate_dict["reasons"],
                        "created_at": datetime.now().isoformat()
                    }
                    
                    # Guardar solicitud (en producción, esto iría a una cola o base de datos)
                    approval_file = f"approvals/promotion_request_{candidate_dict['model_name']}_v{candidate_dict['version']}.json"
                    os.makedirs("approvals", exist_ok=True)
                    
                    with aiofiles.open(approval_file, 'w') as f:
                        json.dump(approval_request, f, indent=2)
                    
                    promotions.append({
                        "model_name": candidate_dict["model_name"],
                        "version": candidate_dict["version"],
                        "action": "approval_requested",
                        "approval_file": approval_file
                    })
                    
                else:
                    # Promoción automática
                    if not dry_run:
                        try:
                            promotion_result = await self.registry_service.transition_model_version_stage({
                                "name": candidate_dict["model_name"],
                                "version": candidate_dict["version"],
                                "stage": policy.target_stage,
                                "archive_existing_versions": policy.auto_archive_previous
                            })
                            
                            if promotion_result["success"]:
                                promotions.append({
                                    "model_name": candidate_dict["model_name"],
                                    "version": candidate_dict["version"],
                                    "action": "promoted",
                                    "new_stage": policy.target_stage,
                                    "promotion_score": candidate_dict["promotion_score"]
                                })
                                
                                logger.info(f"✅ Auto-promoción: {candidate_dict['model_name']} v{candidate_dict['version']} → {policy.target_stage}")
                            else:
                                errors.append({
                                    "model_name": candidate_dict["model_name"],
                                    "version": candidate_dict["version"],
                                    "error": promotion_result.get("error", "Unknown error")
                                })
                                
                        except APIError as e:
                            errors.append({
                                "model_name": candidate_dict["model_name"],
                                "version": candidate_dict["version"],
                                "error": str(e)
                            })
                    else:
                        promotions.append({
                            "model_name": candidate_dict["model_name"],
                            "version": candidate_dict["version"],
                            "action": "would_promote" if not policy.require_manual_approval else "would_request_approval",
                            "target_stage": policy.target_stage,
                            "promotion_score": candidate_dict["promotion_score"]
                        })
            
            return {
                "success": True,
                "policy_used": policy_name,
                "dry_run": dry_run,
                "eligible_candidates": len(eligible_candidates),
                "promotions": promotions,
                "errors": errors,
                "summary": {
                    "promoted": len([p for p in promotions if p["action"] == "promoted"]),
                    "approval_requested": len([p for p in promotions if p["action"] == "approval_requested"]),
                    "would_promote": len([p for p in promotions if p["action"] == "would_promote"]),
                    "errors": len(errors)
                }
            }
            
        except APIError as e:
            return self.handle_error(e, "auto_promote_eligible_models")

    def _candidate_to_dict(self, candidate: PromotionCandidate) -> Dict[str, Any]:
        """Convertir candidato a diccionario"""
        return {
            "model_name": candidate.model_name,
            "version": candidate.version,
            "run_id": candidate.run_id,
            "current_stage": candidate.current_stage,
            "meets_criteria": candidate.meets_criteria,
            "promotion_score": candidate.promotion_score,
            "reasons": candidate.reasons,
            "blocking_issues": candidate.blocking_issues,
            "metrics": candidate.metrics,
            "calibration_metrics": candidate.calibration_metrics,
            "creation_timestamp": candidate.creation_timestamp
        }

    async def get_promotion_policies(self) -> Dict[str, Any]:
        """Obtener políticas de promoción disponibles"""
        policies_info = {}
        
        for name, policy in self.policies.items():
            policies_info[name] = {
                "name": policy.name,
                "description": policy.description,
                "source_stage": policy.source_stage,
                "target_stage": policy.target_stage,
                "require_manual_approval": policy.require_manual_approval,
                "criteria": {
                    "metrics": {
                        "min_accuracy": policy.min_accuracy,
                        "min_f1_score": policy.min_f1_score,
                        "min_roc_auc": policy.min_roc_auc,
                        "min_pr_auc": policy.min_pr_auc
                    },
                    "calibration": {
                        "max_ece": policy.max_ece,
                        "max_brier_score": policy.max_brier_score,
                        "min_reliability": policy.min_reliability
                    },
                    "temporal": {
                        "min_age_hours": policy.min_age_hours,
                        "max_age_days": policy.max_age_days
                    },
                    "stability": {
                        "min_cv_runs": policy.min_cv_runs,
                        "max_cv_std": policy.max_cv_std
                    },
                    "improvement": {
                        "improvement_threshold": policy.improvement_threshold
                    }
                }
            }
        
        return {
            "success": True,
            "policies": policies_info,
            "total_policies": len(policies_info)
        }