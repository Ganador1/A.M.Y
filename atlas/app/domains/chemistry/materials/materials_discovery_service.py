"""
Materials Discovery Service for AXIOM Meta/Atlas
- Descubrimiento computacional de materiales usando GNoME y Materials Project
- Predicción de propiedades de materiales
- Diseño de materiales funcionales
- Integración con pipeline científico Atlas
"""

from __future__ import annotations

import asyncio
import os
import tempfile
import numpy as np
import json
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import hashlib
from app.config import settings
from app.exceptions.domain.chemistry import ChemistryError

# Materials libraries availability check
PYMATGEN_AVAILABLE = None
MP_API_AVAILABLE = None
ASE_AVAILABLE = None

def _check_materials_stack():
    """Check if materials science stack is available"""
    global PYMATGEN_AVAILABLE, MP_API_AVAILABLE, ASE_AVAILABLE
    
    if PYMATGEN_AVAILABLE is None:
        try:
            import pymatgen  # noqa: F401
            PYMATGEN_AVAILABLE = True
        except ImportError:
            PYMATGEN_AVAILABLE = False
    
    if MP_API_AVAILABLE is None:
        try:
            from mp_api.client import MPRester  # noqa: F401
            MP_API_AVAILABLE = True
        except ImportError:
            MP_API_AVAILABLE = False
    
    if ASE_AVAILABLE is None:
        try:
            import ase  # noqa: F401
            ASE_AVAILABLE = True
        except ImportError:
            ASE_AVAILABLE = False
    
    return PYMATGEN_AVAILABLE or MP_API_AVAILABLE or ASE_AVAILABLE


@dataclass
class MaterialComposition:
    """Composición química de un material"""
    formula: str
    elements: Dict[str, int]
    total_atoms: int
    charge: int = 0
    
    @classmethod
    def from_formula(cls, formula: str) -> 'MaterialComposition':
        """Crea desde fórmula química"""
        # Implementación básica de parsing (en producción usaría pymatgen)
        elements = {}
        
        # Parser simple para fórmulas como "SiO2", "CaCO3", etc.
        i = 0
        while i < len(formula):
            if formula[i].isupper():
                element = formula[i]
                i += 1
                
                # Agregar lowercase si hay
                while i < len(formula) and formula[i].islower():
                    element += formula[i]
                    i += 1
                
                # Obtener número
                num_str = ""
                while i < len(formula) and formula[i].isdigit():
                    num_str += formula[i]
                    i += 1
                
                count = int(num_str) if num_str else 1
                elements[element] = elements.get(element, 0) + count
            else:
                i += 1
        
        total_atoms = sum(elements.values())
        
        return cls(
            formula=formula,
            elements=elements,
            total_atoms=total_atoms,
            charge=0
        )


@dataclass
class MaterialStructure:
    """Estructura cristalina de un material"""
    lattice_parameters: Dict[str, float]  # a, b, c, alpha, beta, gamma
    space_group: str
    crystal_system: str
    atom_positions: List[Dict[str, Any]]
    volume: float
    density: Optional[float] = None


@dataclass
class MaterialProperties:
    """Propiedades predichas/calculadas de un material"""
    formation_energy: Optional[float] = None  # eV/atom
    band_gap: Optional[float] = None  # eV
    bulk_modulus: Optional[float] = None  # GPa
    shear_modulus: Optional[float] = None  # GPa
    thermal_conductivity: Optional[float] = None  # W/mK
    electrical_conductivity: Optional[float] = None  # S/m
    magnetic_moment: Optional[float] = None  # μB
    stability_score: Optional[float] = None  # 0-1
    synthesis_probability: Optional[float] = None  # 0-1


@dataclass
class MaterialCandidate:
    """Candidato material para aplicación específica"""
    composition: MaterialComposition
    structure: Optional[MaterialStructure] = None
    properties: Optional[MaterialProperties] = None
    suitability_score: float = 0.0
    target_application: str = ""
    discovery_method: str = ""


class MaterialsDiscoveryService:
    """
    Servicio de descubrimiento de materiales con GNoME/Materials Project
    """
    
    def __init__(self, mp_api_key: Optional[str] = None):
        self.materials_available = _check_materials_stack()
        self.temp_dir = tempfile.mkdtemp(prefix="materials_discovery_")
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.mp_api_key = mp_api_key or getattr(settings, "MP_API_KEY", None)
        
        # Configuraciones predefinidas
        self.target_applications = {
            "solar_cell": {
                "band_gap_range": (1.0, 1.8),  # eV
                "stability_min": 0.7,
                "required_properties": ["band_gap", "formation_energy"]
            },
            "battery_cathode": {
                "formation_energy_max": -2.0,  # eV/atom
                "stability_min": 0.8,
                "required_properties": ["formation_energy", "electrical_conductivity"]
            },
            "superconductor": {
                "required_elements": ["Cu", "Y", "Ba"],
                "stability_min": 0.6,
                "required_properties": ["electrical_conductivity"]
            },
            "thermoelectric": {
                "band_gap_range": (0.1, 1.0),
                "thermal_conductivity_max": 10.0,
                "required_properties": ["band_gap", "thermal_conductivity", "electrical_conductivity"]
            }
        }
        
        # Base de datos de materiales conocidos (simulada)
        self.known_materials_db = {}
        self._initialize_materials_db()
        
    def __del__(self):
        """Limpia recursos de forma segura durante shutdown"""
        try:
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=False)
            import shutil
            import os
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            # Capturar todas las excepciones incluyendo ImportError durante shutdown
            pass

    # --- Core Materials Discovery Methods ---
    async def discover_materials_for_application(self, application: str, 
                                               max_candidates: int = 50) -> List[MaterialCandidate]:
        """
        Descubre materiales candidatos para una aplicación específica
        """
        try:
            if application not in self.target_applications:
                available_apps = list(self.target_applications.keys())
                raise ValueError(f"Unknown application. Available: {available_apps}")
            
            app_config = self.target_applications[application]
            candidates = []
            
            # Estrategias de descubrimiento
            strategies = [
                "compositional_substitution",
                "structure_prediction", 
                "database_screening",
                "ml_generation"
            ]
            
            for strategy in strategies:
                strategy_candidates = await self._discover_by_strategy(
                    strategy, application, app_config, max_candidates // len(strategies)
                )
                candidates.extend(strategy_candidates)
            
            # Evaluar candidatos
            evaluated_candidates = []
            for candidate in candidates:
                try:
                    # Predecir propiedades si no están disponibles
                    if candidate.properties is None:
                        candidate.properties = await self._predict_material_properties(candidate)
                    
                    # Calcular score de idoneidad
                    suitability = await self._calculate_suitability_score(
                        candidate, application, app_config
                    )
                    candidate.suitability_score = suitability
                    candidate.target_application = application
                    
                    evaluated_candidates.append(candidate)
                    
                except ChemistryError:
                    # Skip candidates with evaluation errors
                    continue
            
            # Ordenar por idoneidad y retornar top candidates
            evaluated_candidates.sort(key=lambda c: c.suitability_score, reverse=True)
            
            return evaluated_candidates[:max_candidates]
            
        except ChemistryError as e:
            return []

    async def predict_material_properties(self, composition: str) -> MaterialProperties:
        """
        Predice propiedades de un material basado en composición
        """
        try:
            material_comp = MaterialComposition.from_formula(composition)
            
            # Usar Materials Project API si está disponible
            if self.materials_available and MP_API_AVAILABLE and self.mp_api_key:
                return await self._predict_with_materials_project(material_comp)
            else:
                return await self._predict_with_heuristics(material_comp)
                
        except ChemistryError as e:
            # Return default properties on error
            return MaterialProperties(stability_score=0.5)

    async def search_similar_materials(self, target_composition: str, 
                                     similarity_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Busca materiales similares en bases de datos
        """
        try:
            target_comp = MaterialComposition.from_formula(target_composition)
            similar_materials = []
            
            # Buscar en base de datos local
            for formula, material_data in self.known_materials_db.items():
                similarity = await self._calculate_compositional_similarity(
                    target_comp, MaterialComposition.from_formula(formula)
                )
                
                if similarity >= similarity_threshold:
                    similar_materials.append({
                        "formula": formula,
                        "similarity": similarity,
                        "properties": material_data.get("properties", {}),
                        "source": "local_db"
                    })
            
            # Buscar en Materials Project si está disponible
            if self.materials_available and MP_API_AVAILABLE and self.mp_api_key:
                mp_results = await self._search_materials_project(target_comp)
                similar_materials.extend(mp_results)
            
            # Ordenar por similitud
            similar_materials.sort(key=lambda m: m["similarity"], reverse=True)
            
            return similar_materials[:20]  # Top 20 most similar
            
        except ChemistryError as e:
            return []

    async def optimize_composition(self, base_composition: str, 
                                 target_properties: Dict[str, float],
                                 optimization_steps: int = 100) -> Dict[str, Any]:
        """
        Optimiza composición para alcanzar propiedades objetivo
        """
        try:
            base_comp = MaterialComposition.from_formula(base_composition)
            
            # Algoritmo de optimización simple (en producción usaría GA o BO)
            best_composition = base_comp
            best_score = 0.0
            optimization_history = []
            
            for step in range(optimization_steps):
                # Generar variación
                modified_comp = await self._generate_composition_variant(best_composition)
                
                # Predecir propiedades
                properties = await self._predict_material_properties(
                    MaterialCandidate(composition=modified_comp)
                )
                
                # Evaluar qué tan cerca están las propiedades del objetivo
                score = await self._evaluate_property_match(properties, target_properties)
                
                optimization_history.append({
                    "step": step,
                    "composition": modified_comp.formula,
                    "properties": properties.__dict__,
                    "score": score
                })
                
                if score > best_score:
                    best_score = score
                    best_composition = modified_comp
            
            return {
                "success": True,
                "base_composition": base_composition,
                "optimized_composition": best_composition.formula,
                "target_properties": target_properties,
                "achieved_score": best_score,
                "optimization_steps": optimization_steps,
                "history": optimization_history[-10:]  # Últimos 10 pasos
            }
            
        except ChemistryError as e:
            return {
                "success": False,
                "error": f"Composition optimization failed: {str(e)}"
            }

    async def analyze_stability(self, composition: str) -> Dict[str, Any]:
        """
        Analiza estabilidad termodinámica de un material
        """
        try:
            material_comp = MaterialComposition.from_formula(composition)
            
            # Análisis de estabilidad básico
            stability_analysis = {
                "composition": composition,
                "formation_energy_estimate": None,
                "decomposition_products": [],
                "stability_score": 0.5,  # Default neutral
                "analysis_method": "heuristic"
            }
            
            # Predecir energía de formación
            properties = await self._predict_material_properties(
                MaterialCandidate(composition=material_comp)
            )
            
            if properties.formation_energy is not None:
                stability_analysis["formation_energy_estimate"] = properties.formation_energy
                
                # Score basado en energía de formación
                # Más negativo = más estable
                if properties.formation_energy < -2.0:
                    stability_analysis["stability_score"] = 0.9
                elif properties.formation_energy < -1.0:
                    stability_analysis["stability_score"] = 0.7
                elif properties.formation_energy < 0.0:
                    stability_analysis["stability_score"] = 0.6
                else:
                    stability_analysis["stability_score"] = 0.3
            
            # Análisis de productos de descomposición (simplificado)
            possible_products = await self._predict_decomposition_products(material_comp)
            stability_analysis["decomposition_products"] = possible_products
            
            return stability_analysis
            
        except ChemistryError as e:
            return {
                "composition": composition,
                "error": f"Stability analysis failed: {str(e)}",
                "stability_score": 0.0
            }

    # --- Materials Project Integration ---
    async def _predict_with_materials_project(self, composition: MaterialComposition) -> MaterialProperties:
        """Predice propiedades usando Materials Project API"""
        try:
            # Implementación placeholder - en producción usaría MP API real
            from mp_api.client import MPRester
            
            with MPRester(self.mp_api_key) as mpr:
                # Buscar materiales similares
                docs = mpr.summary.search(
                    formula=composition.formula,
                    fields=["formation_energy_per_atom", "band_gap", "density"]
                )
                
                if docs:
                    # Usar el primer resultado
                    doc = docs[0]
                    return MaterialProperties(
                        formation_energy=float(doc.formation_energy_per_atom),
                        band_gap=float(doc.band_gap) if doc.band_gap else None,
                        density=float(doc.density) if doc.density else None,
                        stability_score=0.8  # High confidence for MP data
                    )
            
            # Fallback si no se encuentra
            return await self._predict_with_heuristics(composition)
            
        except ChemistryError:
            return await self._predict_with_heuristics(composition)

    async def _search_materials_project(self, target_comp: MaterialComposition) -> List[Dict[str, Any]]:
        """Busca materiales similares en Materials Project"""
        try:
            # Implementación placeholder
            similar_materials = []
            
            # En producción, buscaría en MP con criterios de similitud
            # Por ahora, retornar lista vacía
            
            return similar_materials
            
        except ChemistryError:
            return []

    # --- Heuristic Prediction Methods ---
    async def _predict_with_heuristics(self, composition: MaterialComposition) -> MaterialProperties:
        """Predice propiedades usando heurísticas basadas en elementos"""
        try:
            properties = MaterialProperties()
            
            # Heurísticas simples basadas en elementos
            elements = list(composition.elements.keys())
            
            # Energía de formación estimada
            if any(elem in ["O", "F", "Cl"] for elem in elements):
                # Óxidos, fluoruros tienden a ser estables
                properties.formation_energy = -1.5 - np.random.exponential(0.5)
            else:
                # Otros compuestos
                properties.formation_energy = -0.5 - np.random.exponential(0.3)
            
            # Band gap estimado
            if any(elem in ["Si", "Ge", "GaAs"] for elem in elements):
                # Semiconductores
                properties.band_gap = np.random.uniform(0.5, 2.0)
            elif any(elem in ["Cu", "Ag", "Au"] for elem in elements):
                # Metales
                properties.band_gap = 0.0
            else:
                # Otros materiales
                properties.band_gap = np.random.uniform(0.1, 4.0)
            
            # Propiedades mecánicas estimadas
            properties.bulk_modulus = np.random.uniform(50, 400)  # GPa
            properties.shear_modulus = properties.bulk_modulus * 0.6
            
            # Score de estabilidad basado en energía de formación
            if properties.formation_energy < -2.0:
                properties.stability_score = 0.9
            elif properties.formation_energy < -1.0:
                properties.stability_score = 0.7
            else:
                properties.stability_score = 0.5
            
            # Probabilidad de síntesis (heurística)
            properties.synthesis_probability = min(0.9, properties.stability_score + 0.1)
            
            return properties
            
        except ChemistryError:
            return MaterialProperties(stability_score=0.5)

    # --- Discovery Strategy Methods ---
    async def _discover_by_strategy(self, strategy: str, application: str, 
                                  config: Dict[str, Any], max_candidates: int) -> List[MaterialCandidate]:
        """Descubre candidatos usando una estrategia específica"""
        candidates = []
        
        try:
            if strategy == "compositional_substitution":
                candidates = await self._discover_by_substitution(application, config, max_candidates)
                
            elif strategy == "structure_prediction":
                candidates = await self._discover_by_structure_prediction(application, config, max_candidates)
                
            elif strategy == "database_screening":
                candidates = await self._discover_by_db_screening(application, config, max_candidates)
                
            elif strategy == "ml_generation":
                candidates = await self._discover_by_ml_generation(application, config, max_candidates)
            
            # Marcar método de descubrimiento
            for candidate in candidates:
                candidate.discovery_method = strategy
                
        except ChemistryError:
            pass
        
        return candidates

    async def _discover_by_substitution(self, application: str, config: Dict[str, Any], 
                                      max_candidates: int) -> List[MaterialCandidate]:
        """Descubrimiento por sustitución elemental"""
        candidates = []
        
        # Materiales base conocidos para cada aplicación
        base_materials = {
            "solar_cell": ["Si", "GaAs", "CdTe", "CIGS"],
            "battery_cathode": ["LiCoO2", "LiFePO4", "LiMn2O4"],
            "superconductor": ["YBa2Cu3O7", "Bi2Sr2Ca2Cu3O10"],
            "thermoelectric": ["Bi2Te3", "PbTe", "SiGe"]
        }
        
        base_list = base_materials.get(application, ["SiO2", "Al2O3"])
        
        for base_formula in base_list:
            try:
                base_comp = MaterialComposition.from_formula(base_formula)
                
                # Generar sustituciones
                for _ in range(max_candidates // len(base_list)):
                    substituted_comp = await self._generate_substitution(base_comp)
                    candidate = MaterialCandidate(composition=substituted_comp)
                    candidates.append(candidate)
                    
            except ChemistryError:
                continue
        
        return candidates[:max_candidates]

    async def _discover_by_structure_prediction(self, application: str, config: Dict[str, Any],
                                              max_candidates: int) -> List[MaterialCandidate]:
        """Descubrimiento por predicción de estructuras"""
        # Placeholder - en producción usaría algoritmos como USPEX, CALYPSO
        candidates = []
        
        for i in range(min(max_candidates, 10)):  # Limitado para simplicidad
            # Generar composición aleatoria
            formula = self._generate_random_composition()
            comp = MaterialComposition.from_formula(formula)
            candidate = MaterialCandidate(composition=comp)
            candidates.append(candidate)
        
        return candidates

    async def _discover_by_db_screening(self, application: str, config: Dict[str, Any],
                                       max_candidates: int) -> List[MaterialCandidate]:
        """Descubrimiento por screening de bases de datos"""
        candidates = []
        
        # Buscar en base de datos local
        for formula, data in list(self.known_materials_db.items())[:max_candidates]:
            comp = MaterialComposition.from_formula(formula)
            candidate = MaterialCandidate(composition=comp)
            candidates.append(candidate)
        
        return candidates

    async def _discover_by_ml_generation(self, application: str, config: Dict[str, Any],
                                        max_candidates: int) -> List[MaterialCandidate]:
        """Descubrimiento usando generación ML (placeholder)"""
        # En producción usaría modelos generativos como VAE, GAN para materiales
        candidates = []
        
        for i in range(min(max_candidates, 5)):  # Muy limitado para placeholder
            formula = f"AB{i+1}O{i+2}"  # Pattern simple
            try:
                comp = MaterialComposition.from_formula(formula)
                candidate = MaterialCandidate(composition=comp)
                candidates.append(candidate)
            except ChemistryError:
                continue
        
        return candidates

    # --- Helper Methods ---
    def _initialize_materials_db(self):
        """Inicializa base de datos de materiales conocidos"""
        # Base de datos simplificada
        known_materials = [
            "Si", "GaAs", "InP", "SiO2", "Al2O3", "TiO2",
            "LiCoO2", "LiFePO4", "NaCoO2", "CaTiO3", "BaTiO3",
            "YBa2Cu3O7", "La2CuO4", "Bi2Sr2CaCu2O8",
            "Bi2Te3", "Sb2Te3", "PbTe", "SnTe", "ZnO", "CdS"
        ]
        
        for formula in known_materials:
            # Generar datos simulados
            self.known_materials_db[formula] = {
                "properties": {
                    "formation_energy": -np.random.exponential(1.0),
                    "band_gap": np.random.uniform(0, 4),
                    "stability_score": np.random.uniform(0.5, 1.0)
                },
                "source": "simulated_db"
            }

    async def _calculate_suitability_score(self, candidate: MaterialCandidate, 
                                         application: str, config: Dict[str, Any]) -> float:
        """Calcula score de idoneidad para una aplicación"""
        if candidate.properties is None:
            return 0.0
        
        score = 0.0
        max_score = 0.0
        
        # Evaluar cada criterio de la aplicación
        if "band_gap_range" in config and candidate.properties.band_gap is not None:
            min_gap, max_gap = config["band_gap_range"]
            if min_gap <= candidate.properties.band_gap <= max_gap:
                score += 1.0
            max_score += 1.0
        
        if "stability_min" in config and candidate.properties.stability_score is not None:
            if candidate.properties.stability_score >= config["stability_min"]:
                score += 1.0
            max_score += 1.0
        
        if "formation_energy_max" in config and candidate.properties.formation_energy is not None:
            if candidate.properties.formation_energy <= config["formation_energy_max"]:
                score += 1.0
            max_score += 1.0
        
        return score / max(max_score, 1.0)

    async def _calculate_compositional_similarity(self, comp1: MaterialComposition, 
                                                comp2: MaterialComposition) -> float:
        """Calcula similitud composicional entre dos materiales"""
        # Similitud basada en elementos comunes
        elements1 = set(comp1.elements.keys())
        elements2 = set(comp2.elements.keys())
        
        if not elements1 and not elements2:
            return 1.0
        
        intersection = elements1.intersection(elements2)
        union = elements1.union(elements2)
        
        jaccard_similarity = len(intersection) / len(union) if union else 0.0
        
        return jaccard_similarity

    async def _generate_composition_variant(self, base_comp: MaterialComposition) -> MaterialComposition:
        """Genera variante de una composición base"""
        # Variación simple: cambiar proporción de elementos
        new_elements = base_comp.elements.copy()
        
        # Seleccionar elemento aleatorio para modificar
        if new_elements:
            element = np.random.choice(list(new_elements.keys()))
            current_count = new_elements[element]
            
            # Cambiar conteo ligeramente
            new_count = max(1, current_count + np.random.choice([-1, 0, 1]))
            new_elements[element] = new_count
        
        # Reconstruir fórmula
        formula_parts = []
        for elem, count in new_elements.items():
            if count == 1:
                formula_parts.append(elem)
            else:
                formula_parts.append(f"{elem}{count}")
        
        new_formula = "".join(formula_parts)
        return MaterialComposition.from_formula(new_formula)

    async def _generate_substitution(self, base_comp: MaterialComposition) -> MaterialComposition:
        """Genera sustitución elemental"""
        # Tabla de sustituciones comunes
        substitutions = {
            "Li": ["Na", "K"], "Na": ["Li", "K"], "K": ["Na", "Li"],
            "Mg": ["Ca", "Sr"], "Ca": ["Mg", "Sr"], "Sr": ["Ca", "Ba"],
            "Al": ["Ga", "In"], "Ga": ["Al", "In"], "In": ["Ga", "Al"],
            "Si": ["Ge", "Sn"], "Ge": ["Si", "Sn"], "Sn": ["Ge", "Pb"],
            "Ti": ["Zr", "Hf"], "Zr": ["Ti", "Hf"], "Hf": ["Ti", "Zr"],
            "Fe": ["Co", "Ni"], "Co": ["Fe", "Ni"], "Ni": ["Co", "Fe"]
        }
        
        new_elements = base_comp.elements.copy()
        
        # Seleccionar elemento para sustituir
        for element in base_comp.elements:
            if element in substitutions and np.random.random() < 0.3:  # 30% probabilidad
                substitute = np.random.choice(substitutions[element])
                count = new_elements.pop(element)
                new_elements[substitute] = count
                break
        
        # Reconstruir fórmula
        formula_parts = []
        for elem, count in new_elements.items():
            if count == 1:
                formula_parts.append(elem)
            else:
                formula_parts.append(f"{elem}{count}")
        
        new_formula = "".join(formula_parts)
        return MaterialComposition.from_formula(new_formula)

    def _generate_random_composition(self) -> str:
        """Genera composición química aleatoria"""
        common_elements = ["Li", "Na", "Mg", "Ca", "Al", "Si", "Ti", "Fe", "Co", "Ni", "Cu", "Zn", "O", "F", "S"]
        
        # Seleccionar 1-3 elementos
        n_elements = np.random.choice([1, 2, 3], p=[0.2, 0.6, 0.2])
        elements = np.random.choice(common_elements, n_elements, replace=False)
        
        formula_parts = []
        for element in elements:
            count = np.random.choice([1, 2, 3, 4], p=[0.4, 0.3, 0.2, 0.1])
            if count == 1:
                formula_parts.append(element)
            else:
                formula_parts.append(f"{element}{count}")
        
        return "".join(formula_parts)

    async def _predict_decomposition_products(self, composition: MaterialComposition) -> List[str]:
        """Predice productos de descomposición (simplificado)"""
        products = []
        
        # Predicciones heurísticas simples
        elements = list(composition.elements.keys())
        
        if "O" in elements:
            # Óxidos tienden a descomponerse en óxidos más simples
            for element in elements:
                if element != "O":
                    products.append(f"{element}O")
                    
        else:
            # Otros compuestos -> elementos puros
            products.extend(elements)
        
        return products

    async def _evaluate_property_match(self, properties: MaterialProperties, 
                                     targets: Dict[str, float]) -> float:
        """Evalúa qué tan bien las propiedades coinciden con objetivos"""
        score = 0.0
        count = 0
        
        for prop_name, target_value in targets.items():
            current_value = getattr(properties, prop_name, None)
            if current_value is not None:
                # Score basado en proximidad (tolerancia 20%)
                tolerance = abs(target_value * 0.2)
                if abs(current_value - target_value) <= tolerance:
                    score += 1.0
                else:
                    # Partial score based on distance
                    distance = abs(current_value - target_value)
                    partial_score = max(0, 1.0 - distance / max(abs(target_value), 1.0))
                    score += partial_score
                count += 1
        
        return score / max(count, 1)

    async def _predict_material_properties(self, candidate: MaterialCandidate) -> MaterialProperties:
        """Wrapper para predicción de propiedades"""
        return await self._predict_with_heuristics(candidate.composition)
