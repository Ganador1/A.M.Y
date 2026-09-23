"""
GNOME Materials Discovery Service (placeholder ligero)
Emula sugerencias de materiales y propiedades objetivo con heurísticas simples
y datos básicos (sin modelo GNOME real).
"""

from __future__ import annotations

from typing import Dict, Any, List
from dataclasses import dataclass

from app.services.base_service import BaseService
from app.core.bootstrap_logging import logger
from app.exceptions.domain.chemistry import ChemistryError


@dataclass
class Candidate:
    """
    Material candidate with predicted properties.
    
    Attributes:
        formula: Chemical formula of the material
        score: Relevance score for the target application
        predicted_properties: Dictionary of predicted material properties
    """
    formula: str
    score: float
    predicted_properties: Dict[str, float]


MATERIAL_DB = [
    # Batteries (Li-ion, Solid State)
    ("LiFePO4", {"conductivity": 1.5, "stability": 0.92, "capacity": 160, "type": "battery"}),
    ("LiCoO2", {"conductivity": 2.1, "stability": 0.85, "capacity": 150, "type": "battery"}),
    ("LiNiMnCoO2", {"conductivity": 2.8, "stability": 0.88, "capacity": 180, "type": "battery"}),
    ("Li7La3Zr2O12", {"conductivity": 5.0, "stability": 0.95, "capacity": 0, "type": "battery_electrolyte"}),
    
    # Solar Cells (Perovskites, Silicon, Thin Film)
    ("MAPbI3", {"band_gap": 1.55, "efficiency": 0.22, "stability": 0.4, "type": "solar"}),
    ("FAPbI3", {"band_gap": 1.48, "efficiency": 0.24, "stability": 0.5, "type": "solar"}),
    ("GaAs", {"band_gap": 1.42, "efficiency": 0.29, "stability": 0.99, "type": "solar"}),
    ("CdTe", {"band_gap": 1.45, "efficiency": 0.22, "stability": 0.95, "type": "solar"}),
    ("CIGS", {"band_gap": 1.15, "efficiency": 0.23, "stability": 0.90, "type": "solar"}),
    
    # Semiconductors / Electronics
    ("SiC", {"thermal_conductivity": 120, "hardness": 9.5, "band_gap": 2.3, "type": "semiconductor"}),
    ("GaN", {"thermal_conductivity": 130, "band_gap": 3.4, "mobility": 2000, "type": "semiconductor"}),
    
    # Ceramics / Structural
    ("Al2O3", {"thermal_conductivity": 30, "hardness": 9.0, "stability": 0.99, "type": "ceramic"}),
    ("ZrO2", {"thermal_conductivity": 2.0, "hardness": 8.5, "toughness": 8.0, "type": "ceramic"}),

    # Superconductors
    ("YBCO", {"critical_temp": 92.0, "coherence_length": 1.5, "type": "superconductor"}),
    ("MgB2", {"critical_temp": 39.0, "coherence_length": 5.0, "type": "superconductor"}),
]


class GNOMEMaterialsService(BaseService):
    def __init__(self):
        super().__init__("GNOMEMaterials")
        logger.info("✅ GNOMEMaterialsService initialized (expanded database)")

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if (action := request_data.get("action", "")) == "suggest_candidates":
                return self.suggest_candidates(request_data)
            if action == "predict_properties":
                return self.predict_properties(request_data)
            if action == "search_materials": # Support direct search action
                return {"success": True, "candidates": await self.search_materials(
                    request_data.get("application", ""),
                    request_data.get("max_results", 10),
                    request_data.get("filters", {})
                )}
            return {"success": False, "error": f"Unknown action: {action}", "available_actions": ["suggest_candidates", "predict_properties", "search_materials"]}
        except ChemistryError as e:
            return self.handle_error(e, "process_request")

    async def search_materials(self, application: str, max_results: int = 10, filters: Dict = None) -> List[Dict[str, Any]]:
        """Helper method for direct internal calls"""
        # Filters are currently unused in this mock implementation but kept for interface compatibility
        _ = filters 
        req = {"target": application, "top_n": max_results}
        res = self.suggest_candidates(req)
        return res.get("candidates", [])

    def suggest_candidates(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            target = (request_data.get("target") or "").lower()
            top_n = int(request_data.get("top_n", 3))
            
            # Map common terms to types
            target_type = "unknown"
            if "solar" in target or "photovoltaic" in target:
                target_type = "solar"
            elif "battery" in target or "storage" in target or "lithium" in target:
                target_type = "battery"
            elif "semiconductor" in target or "chip" in target:
                target_type = "semiconductor"
            elif "superconductor" in target:
                target_type = "superconductor"
            elif "ceramic" in target or "structural" in target:
                target_type = "ceramic"

            scored: List[Candidate] = []
            for formula, props in MATERIAL_DB:
                score = 0.0
                mat_type = props.get("type", "")
                
                # 1. Type matching (High priority)
                if target_type != "unknown" and mat_type == target_type:
                    score += 0.8
                elif target_type == "unknown":
                    score += 0.1 # Give everyone a small chance if target is vague

                # 2. Property matching
                for k, _ in props.items():
                    if k in target: # e.g. "high conductivity"
                        score += 0.3
                
                # 3. Random noise for variety (simulating discovery)
                import random
                score += random.uniform(0, 0.1)

                if score > 0.2: # Threshold to avoid totally irrelevant stuff
                    scored.append(Candidate(formula=formula, score=round(score, 3), predicted_properties=props))
            
            scored.sort(key=lambda c: c.score, reverse=True)
            out = [c.__dict__ for c in scored[:top_n]]
            return {"success": True, "target": target, "candidates": out, "count": len(out)}
        except ChemistryError as e:
            return self.handle_error(e, "suggest_candidates")

    def predict_properties(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            formula = request_data.get("formula")
            if not formula:
                return {"success": False, "error": "formula is required"}
            for f, props in MATERIAL_DB:
                if f.lower() == formula.lower():
                    return {"success": True, "formula": f, "predicted_properties": props}
            # Predicción ingenua si no está en DB
            return {"success": True, "formula": formula, "predicted_properties": {"stability": 0.5}}
        except ChemistryError as e:
            return self.handle_error(e, "predict_properties")
