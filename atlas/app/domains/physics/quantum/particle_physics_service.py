"""
Enhanced Particle Physics Service for AXIOM Meta/Atlas
- Análisis de datos de física de partículas usando ROOT, uproot, awkward
- Procesamiento de eventos de colisionadores (LHC, etc.)
- Reconstrucción de partículas y análisis estadístico avanzado
- Integración con pipeline de descubrimiento científico Atlas
"""

from __future__ import annotations
import aiofiles

import asyncio
import os
import tempfile
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import json

from app.services.base_service import BaseService
from app.exceptions.domain.physics import ParticlePhysicsError

# ROOT/uproot availability checks
ROOT_AVAILABLE = None
UPROOT_AVAILABLE = None
AWKWARD_AVAILABLE = None

def _check_root_stack():
    """Check if ROOT analysis stack is available"""
    global ROOT_AVAILABLE, UPROOT_AVAILABLE, AWKWARD_AVAILABLE
    
    if ROOT_AVAILABLE is None:
        try:
            import ROOT  # noqa: F401
            ROOT_AVAILABLE = True
        except ImportError:
            ROOT_AVAILABLE = False
    
    if UPROOT_AVAILABLE is None:
        try:
            import uproot  # noqa: F401
            UPROOT_AVAILABLE = True
        except ImportError:
            UPROOT_AVAILABLE = False
    
    if AWKWARD_AVAILABLE is None:
        try:
            import awkward as ak  # noqa: F401
            AWKWARD_AVAILABLE = True
        except ImportError:
            AWKWARD_AVAILABLE = False
    
    return ROOT_AVAILABLE or UPROOT_AVAILABLE


@dataclass
class ParticleEvent:
    """Evento de partículas con cinemática completa"""
    event_id: int
    particles: List[Dict[str, float]]
    metadata: Dict[str, Any]
    
    def missing_et(self) -> Tuple[float, float]:
        """Calcula energía transversal perdida"""
        met_x = -sum(p.get("px", 0.0) for p in self.particles)
        met_y = -sum(p.get("py", 0.0) for p in self.particles)
        return met_x, met_y
    
    def total_energy(self) -> float:
        """Energía total del evento"""
        return sum(p.get("e", 0.0) for p in self.particles)


@dataclass
class JetAnalysisResult:
    """Resultado de análisis de jets"""
    jets: List[Dict[str, float]]
    jet_algorithm: str
    r_parameter: float
    n_jets: int
    leading_jet_pt: float
    jet_mass_spectrum: List[float]


@dataclass
class ResonanceSearch:
    """Búsqueda de resonancias en espectro de masa invariante"""
    mass_spectrum: np.ndarray
    bins: np.ndarray
    peak_candidates: List[Dict[str, float]]
    background_estimate: Optional[np.ndarray] = None
    significance: Optional[List[float]] = None


class ParticlePhysicsService(BaseService):
    """
    Servicio avanzado de física de partículas con ROOT/uproot
    """
    
    def __init__(self) -> None:
        super().__init__("ParticlePhysicsService")
        self.root_available = _check_root_stack()
        self.temp_dir = tempfile.mkdtemp(prefix="particle_physics_")
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Configuraciones estándar
        self.jet_algorithms = {
            "antikt": {"R": 0.4, "description": "Anti-kT algorithm"},
            "kt": {"R": 0.6, "description": "kT algorithm"},
            "cambridge": {"R": 0.8, "description": "Cambridge/Aachen"}
        }
        
        # Masas de partículas conocidas (GeV)
        self.particle_masses = {
            "electron": 0.000511, "muon": 0.105658, "tau": 1.77686,
            "pion_charged": 0.13957, "pion_neutral": 0.13498,
            "kaon_charged": 0.49367, "kaon_neutral": 0.49761,
            "proton": 0.93827, "neutron": 0.93957,
            "w_boson": 80.379, "z_boson": 91.188, "higgs": 125.18
        }
        
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

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa requests de análisis de física de partículas"""
        self.log_request(request_data)
        try:
            operation = request_data.get("operation", "info")
            
            if operation == "info":
                return {
                    "capabilities": [
                        "advanced_event_analysis", "jet_reconstruction", 
                        "invariant_mass_analysis", "resonance_search",
                        "particle_identification", "kinematic_fitting",
                        "monte_carlo_analysis", "root_file_processing"
                    ],
                    "root_available": self.root_available,
                    "supported_formats": ["ROOT", "HDF5", "Parquet", "JSON"]
                }
            
            elif operation == "event_analysis":
                events = request_data.get("events", [])
                return await self.analyze_events(events)
                
            elif operation == "jet_reconstruction":
                particles = request_data.get("particles", [])
                algorithm = request_data.get("algorithm", "antikt")
                return await self.reconstruct_jets(particles, algorithm)
                
            elif operation == "invariant_mass":
                particles = request_data.get("particles", [])
                particle_types = request_data.get("particle_types", [])
                return await self.calculate_invariant_mass_spectrum(particles, particle_types)
                
            elif operation == "resonance_search":
                mass_data = request_data.get("mass_spectrum", [])
                return await self.search_resonances(mass_data)
                
            elif operation == "particle_id":
                tracks = request_data.get("tracks", [])
                return await self.identify_particles(tracks)
                
            elif operation == "monte_carlo_analysis":
                mc_events = request_data.get("mc_events", [])
                return await self.analyze_monte_carlo(mc_events)
                
            elif operation == "process_root_file":
                file_path = request_data.get("file_path", "")
                tree_name = request_data.get("tree_name", "Events")
                return await self.process_root_file(file_path, tree_name)
                
            else:
                return {"error": f"Unknown operation: {operation}"}
            
        except ParticlePhysicsError as e:
            return self.handle_error(e, "process_request")
        except Exception as e:
            return self.handle_error(e, "process_request")

    # --- Advanced Event Analysis ---
    async def analyze_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Análisis avanzado de eventos de partículas
        """
        try:
            if not events:
                return {"error": "No events provided"}
            
            analyzed_events = []
            summary_stats = {
                "total_events": len(events),
                "total_particles": 0,
                "average_multiplicity": 0.0,
                "missing_et_distribution": [],
                "energy_distribution": []
            }
            
            for i, event_data in enumerate(events):
                particles = event_data.get("particles", [])
                event = ParticleEvent(
                    event_id=i,
                    particles=particles,
                    metadata=event_data.get("metadata", {})
                )
                
                # Análisis del evento individual
                met_x, met_y = event.missing_et()
                met_magnitude = np.sqrt(met_x**2 + met_y**2)
                total_energy = event.total_energy()
                
                event_analysis = {
                    "event_id": i,
                    "n_particles": len(particles),
                    "missing_et": {
                        "magnitude": met_magnitude,
                        "x": met_x,
                        "y": met_y
                    },
                    "total_energy": total_energy,
                    "particle_multiplicities": self._count_particle_types(particles),
                    "kinematic_variables": await self._calculate_event_kinematics(particles)
                }
                
                analyzed_events.append(event_analysis)
                
                # Actualizar estadísticas
                summary_stats["total_particles"] += len(particles)
                summary_stats["missing_et_distribution"].append(met_magnitude)
                summary_stats["energy_distribution"].append(total_energy)
            
            summary_stats["average_multiplicity"] = (
                summary_stats["total_particles"] / len(events)
            )
            
            return {
                "success": True,
                "events": analyzed_events,
                "summary": summary_stats,
                "analysis_method": "advanced_kinematics"
            }
            
        except QuantumError as e:
            return {"error": f"Event analysis failed: {str(e)}"}

    async def reconstruct_jets(self, particles: List[Dict[str, float]], 
                             algorithm: str = "antikt") -> JetAnalysisResult:
        """
        Reconstrucción de jets usando algoritmos estándar
        """
        try:
            if not particles:
                return JetAnalysisResult(
                    jets=[], jet_algorithm=algorithm, r_parameter=0.4,
                    n_jets=0, leading_jet_pt=0.0, jet_mass_spectrum=[]
                )
            
            r_param = self.jet_algorithms.get(algorithm, {"R": 0.4})["R"]
            
            # Implementación simplificada de clustering de jets
            if self.root_available and AWKWARD_AVAILABLE:
                jets = await self._cluster_jets_with_fastjet(particles, algorithm, r_param)
            else:
                jets = await self._cluster_jets_simple(particles, r_param)
            
            # Ordenar jets por pT
            jets.sort(key=lambda j: j.get("pt", 0), reverse=True)
            
            # Análisis de jets
            jet_masses = [j.get("mass", 0.0) for j in jets]
            leading_pt = jets[0].get("pt", 0.0) if jets else 0.0
            
            return JetAnalysisResult(
                jets=jets,
                jet_algorithm=algorithm,
                r_parameter=r_param,
                n_jets=len(jets),
                leading_jet_pt=leading_pt,
                jet_mass_spectrum=jet_masses
            )
            
        except QuantumError as e:
            # Return empty result on error
            return JetAnalysisResult(
                jets=[], jet_algorithm=algorithm, r_parameter=0.4,
                n_jets=0, leading_jet_pt=0.0, jet_mass_spectrum=[]
            )

    async def calculate_invariant_mass_spectrum(self, particles: List[Dict[str, float]], 
                                              particle_types: List[str]) -> Dict[str, Any]:
        """
        Calcula espectro de masa invariante para combinaciones de partículas
        """
        try:
            if len(particles) < 2:
                return {"error": "Need at least 2 particles for invariant mass"}
            
            # Filtrar partículas por tipo si se especifica
            filtered_particles = particles
            if particle_types:
                filtered_particles = [
                    p for p in particles 
                    if p.get("type", "") in particle_types
                ]
            
            invariant_masses = []
            combinations = []
            
            # Calcular masa invariante para todas las combinaciones
            for i in range(len(filtered_particles)):
                for j in range(i+1, len(filtered_particles)):
                    p1, p2 = filtered_particles[i], filtered_particles[j]
                    
                    # Vectores 4-momentum
                    e1, px1, py1, pz1 = p1.get("e", 0), p1.get("px", 0), p1.get("py", 0), p1.get("pz", 0)
                    e2, px2, py2, pz2 = p2.get("e", 0), p2.get("px", 0), p2.get("py", 0), p2.get("pz", 0)
                    
                    # Masa invariante: sqrt((E1+E2)^2 - (p1+p2)^2)
                    e_total = e1 + e2
                    px_total = px1 + px2
                    py_total = py1 + py2
                    pz_total = pz1 + pz2
                    p_total_sq = px_total**2 + py_total**2 + pz_total**2
                    
                    inv_mass_sq = e_total**2 - p_total_sq
                    inv_mass = np.sqrt(max(0, inv_mass_sq))  # Evitar negativos por errores numéricos
                    
                    invariant_masses.append(inv_mass)
                    combinations.append({
                        "particles": [i, j],
                        "invariant_mass": inv_mass,
                        "particle_types": [p1.get("type", "unknown"), p2.get("type", "unknown")]
                    })
            
            # Crear histograma
            if invariant_masses:
                hist, bins = np.histogram(invariant_masses, bins=50, range=(0, max(invariant_masses)))
                bin_centers = (bins[:-1] + bins[1:]) / 2
            else:
                hist, bins, bin_centers = [], [], []
            
            return {
                "success": True,
                "invariant_masses": invariant_masses,
                "combinations": combinations,
                "histogram": {
                    "counts": hist.tolist() if len(hist) > 0 else [],
                    "bins": bins.tolist() if len(bins) > 0 else [],
                    "bin_centers": bin_centers.tolist() if len(bin_centers) > 0 else []
                },
                "statistics": {
                    "n_combinations": len(combinations),
                    "mean_mass": np.mean(invariant_masses) if invariant_masses else 0,
                    "std_mass": np.std(invariant_masses) if invariant_masses else 0,
                    "min_mass": min(invariant_masses) if invariant_masses else 0,
                    "max_mass": max(invariant_masses) if invariant_masses else 0
                }
            }
            
        except QuantumError as e:
            return {"error": f"Invariant mass calculation failed: {str(e)}"}

    async def search_resonances(self, mass_spectrum: List[float]) -> ResonanceSearch:
        """
        Busca picos/resonancias en espectro de masa
        """
        try:
            if len(mass_spectrum) < 10:
                return ResonanceSearch(
                    mass_spectrum=np.array(mass_spectrum),
                    bins=np.array([]),
                    peak_candidates=[]
                )
            
            # Crear histograma
            hist, bins = np.histogram(mass_spectrum, bins=50)
            bin_centers = (bins[:-1] + bins[1:]) / 2
            
            # Búsqueda simple de picos
            peak_candidates = []
            
            # Suavizar para reducir ruido
            if len(hist) > 5:
                smoothed = np.convolve(hist, np.ones(3)/3, mode='same')
                
                # Encontrar máximos locales
                for i in range(1, len(smoothed)-1):
                    if (smoothed[i] > smoothed[i-1] and 
                        smoothed[i] > smoothed[i+1] and 
                        smoothed[i] > np.mean(smoothed) + 2*np.std(smoothed)):
                        
                        peak_candidates.append({
                            "mass": float(bin_centers[i]),
                            "counts": float(smoothed[i]),
                            "significance": float((smoothed[i] - np.mean(smoothed)) / np.std(smoothed)),
                            "bin_index": i
                        })
            
            # Ordenar por significancia
            peak_candidates.sort(key=lambda p: p["significance"], reverse=True)
            
            return ResonanceSearch(
                mass_spectrum=np.array(mass_spectrum),
                bins=bins,
                peak_candidates=peak_candidates[:5],  # Top 5 peaks
                background_estimate=np.ones_like(hist) * np.mean(hist),
                significance=[p["significance"] for p in peak_candidates[:5]]
            )
            
        except QuantumError as e:
            return ResonanceSearch(
                mass_spectrum=np.array(mass_spectrum),
                bins=np.array([]),
                peak_candidates=[],
            )

    # --- ROOT File Processing ---
    async def process_root_file(self, file_path: str, tree_name: str = "Events") -> Dict[str, Any]:
        """
        Procesa archivos ROOT usando uproot
        """
        if not UPROOT_AVAILABLE:
            return {"error": "uproot not available. Install: pip install uproot"}
        
        try:
            import uproot
            import awkward as ak
            
            # Abrir archivo ROOT
            if not os.path.exists(file_path):
                return {"error": f"File not found: {file_path}"}
            
            with uproot.aiofiles.aiofiles.open(file_path) as file:
                if tree_name not in file:
                    available_trees = list(file.keys())
                    return {
                        "error": f"Tree '{tree_name}' not found",
                        "available_trees": available_trees
                    }
                
                tree = file[tree_name]
                
                # Información básica del árbol
                branches = list(tree.keys())
                n_entries = tree.num_entries
                
                # Leer algunas ramas principales (limitado para evitar memoria excesiva)
                max_entries = min(n_entries, 1000)  # Límite de seguridad
                
                data_summary = {
                    "file_path": file_path,
                    "tree_name": tree_name,
                    "n_entries": n_entries,
                    "n_branches": len(branches),
                    "branches": branches[:20],  # Primeras 20 ramas
                    "entries_processed": max_entries
                }
                
                # Si hay ramas de partículas típicas, procesarlas
                particle_branches = [b for b in branches if any(
                    keyword in b.lower() for keyword in 
                    ["pt", "eta", "phi", "energy", "px", "py", "pz"]
                )]
                
                if particle_branches:
                    # Leer datos de partículas
                    particle_data = tree.arrays(
                        particle_branches[:10],  # Primeras 10 ramas de partículas
                        entry_stop=max_entries,
                        library="ak"
                    )
                    
                    # Análisis básico
                    analysis_results = await self._analyze_root_data(particle_data)
                    data_summary["particle_analysis"] = analysis_results
                
                return {
                    "success": True,
                    "data_summary": data_summary,
                    "processing_method": "uproot_awkward"
                }
                
        except QuantumError as e:
            return {"error": f"ROOT file processing failed: {str(e)}"}

    # --- Helper Methods ---
    def _count_particle_types(self, particles: List[Dict[str, float]]) -> Dict[str, int]:
        """Cuenta tipos de partículas en un evento"""
        counts = {}
        for particle in particles:
            ptype = particle.get("type", "unknown")
            counts[ptype] = counts.get(ptype, 0) + 1
        return counts

    async def _calculate_event_kinematics(self, particles: List[Dict[str, float]]) -> Dict[str, float]:
        """Calcula variables cinemáticas del evento"""
        if not particles:
            return {}
        
        # Momentum transversal total
        total_pt = sum(p.get("pt", 0.0) for p in particles)
        
        # Pseudorapidity central
        eta_values = [p.get("eta", 0.0) for p in particles if "eta" in p]
        central_eta = np.mean(eta_values) if eta_values else 0.0
        
        # Multiplicidad charged/neutral
        charged_mult = len([p for p in particles if p.get("charge", 0) != 0])
        neutral_mult = len(particles) - charged_mult
        
        return {
            "total_pt": total_pt,
            "central_eta": central_eta,
            "charged_multiplicity": charged_mult,
            "neutral_multiplicity": neutral_mult,
            "total_multiplicity": len(particles)
        }

    async def _cluster_jets_simple(self, particles: List[Dict[str, float]], r_param: float) -> List[Dict[str, float]]:
        """Algoritmo simple de clustering de jets (fallback)"""
        jets = []
        remaining_particles = particles.copy()
        
        while remaining_particles:
            # Encontrar partícula con mayor pT
            seed = max(remaining_particles, key=lambda p: p.get("pt", 0))
            remaining_particles.remove(seed)
            
            # Cluster con partículas cercanas
            jet_particles = [seed]
            seed_eta, seed_phi = seed.get("eta", 0), seed.get("phi", 0)
            
            to_remove = []
            for particle in remaining_particles:
                eta, phi = particle.get("eta", 0), particle.get("phi", 0)
                delta_eta = eta - seed_eta
                delta_phi = phi - seed_phi
                
                # Ajustar delta_phi para periodicidad
                while delta_phi > np.pi:
                    delta_phi -= 2*np.pi
                while delta_phi < -np.pi:
                    delta_phi += 2*np.pi
                
                delta_r = np.sqrt(delta_eta**2 + delta_phi**2)
                
                if delta_r < r_param:
                    jet_particles.append(particle)
                    to_remove.append(particle)
            
            # Remover partículas agrupadas
            for p in to_remove:
                remaining_particles.remove(p)
            
            # Calcular propiedades del jet
            if len(jet_particles) >= 1:  # Mínimo 1 partícula
                jet_pt = sum(p.get("pt", 0) for p in jet_particles)
                jet_px = sum(p.get("px", 0) for p in jet_particles)
                jet_py = sum(p.get("py", 0) for p in jet_particles)
                jet_pz = sum(p.get("pz", 0) for p in jet_particles)
                jet_e = sum(p.get("e", 0) for p in jet_particles)
                
                # Masa del jet
                jet_mass_sq = jet_e**2 - (jet_px**2 + jet_py**2 + jet_pz**2)
                jet_mass = np.sqrt(max(0, jet_mass_sq))
                
                jets.append({
                    "pt": jet_pt,
                    "px": jet_px,
                    "py": jet_py, 
                    "pz": jet_pz,
                    "e": jet_e,
                    "mass": jet_mass,
                    "n_constituents": len(jet_particles)
                })
        
        return jets

    async def _cluster_jets_with_fastjet(self, particles: List[Dict[str, float]], 
                                       algorithm: str, r_param: float) -> List[Dict[str, float]]:
        """Clustering con FastJet (requiere ROOT/pyjet)"""
        # Placeholder para implementación con FastJet
        # En producción usaría pyjet o bindings de FastJet
        return await self._cluster_jets_simple(particles, r_param)

    async def _analyze_root_data(self, particle_data) -> Dict[str, Any]:
        """Analiza datos de partículas de archivo ROOT"""
        try:
            import awkward as ak
            
            analysis = {}
            
            # Estadísticas básicas por branch
            for branch_name, branch_data in particle_data.items():
                if ak.count(branch_data) > 0:
                    flattened = ak.flatten(branch_data)
                    
                    if len(flattened) > 0:
                        analysis[branch_name] = {
                            "count": int(ak.count(flattened)),
                            "mean": float(ak.mean(flattened)),
                            "std": float(ak.std(flattened)),
                            "min": float(ak.min(flattened)),
                            "max": float(ak.max(flattened))
                        }
            
            return analysis
            
        except QuantumError as e:
            return {"error": f"ROOT data analysis failed: {str(e)}"}

    # --- Placeholder methods para funcionalidades adicionales ---
    async def identify_particles(self, tracks: List[Dict[str, float]]) -> Dict[str, Any]:
        """Identificación de partículas (placeholder)"""
        return {
            "success": True,
            "identified_particles": [],
            "method": "placeholder_pid",
            "note": "Particle identification algorithms not yet implemented"
        }

    async def analyze_monte_carlo(self, mc_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Análisis Monte Carlo (placeholder)"""
        return {
            "success": True,
            "mc_analysis": {},
            "method": "placeholder_mc",
            "note": "Monte Carlo analysis not yet implemented"
        }
