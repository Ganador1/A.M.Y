"""
Particle Physics Jet Analysis Service - AXIOM Advanced
======================================================

Servicio especializado para análisis de jets en física de partículas con
algoritmos de clustering, reconstrucción de masa invariante y análisis
de eventos de colisiones de alta energía.

Características:
- Jet clustering con algoritmos anti-kT, kT y Cambridge/Aachen
- Cálculo de masa invariante de sistemas de partículas
- Análisis de estructura de jets (jet shapes, subjets)
- Identificación de jets de quarks pesados (b-tagging simulation)
- Análisis de missing transverse energy (MET)
- Reconstrucción de partículas resonantes (W, Z, Higgs)

Algoritmos implementados:
- Anti-kT jet clustering (aproximación)
- kT jet clustering
- Análisis de masa invariante di-jet y multi-jet
- Análisis de QCD vs electroweak jets
- Simulación de background QCD

Autor: AXIOM Research Team
Fecha: Septiembre 2025
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import matplotlib.pyplot as plt
import io
import base64

from app.services.base_service import BaseService
from app.exceptions.domain.physics import QuantumError

logger = logging.getLogger(__name__)

# Constantes físicas
C_LIGHT = 2.998e8  # m/s
PROTON_MASS = 0.938272  # GeV/c²
ELECTRON_MASS = 0.000511  # GeV/c²

# Masas de partículas conocidas (GeV/c²)
PARTICLE_MASSES = {
    'W_boson': 80.379,
    'Z_boson': 91.188,
    'higgs': 125.10,
    'top_quark': 173.0,
    'bottom_quark': 4.18,
    'charm_quark': 1.27,
    'tau_lepton': 1.777
}


@dataclass
class ParticleCandidate:
    """Candidato de partícula en el detector"""
    px: float  # Momento en x (GeV/c)
    py: float  # Momento en y (GeV/c)
    pz: float  # Momento en z (GeV/c)
    energy: float  # Energía (GeV)
    
    # Propiedades derivadas
    pt: Optional[float] = None  # Momento transverso
    eta: Optional[float] = None  # Pseudorapidez
    phi: Optional[float] = None  # Ángulo azimutal
    mass: Optional[float] = None  # Masa invariante
    
    # Identificación
    particle_type: str = "unknown"  # electron, muon, photon, jet, etc.
    charge: Optional[int] = None
    
    # Calidad
    isolation: float = 1.0
    detector_response: float = 1.0


@dataclass
class JetCandidate:
    """Candidato de jet reconstruido"""
    constituents: List[ParticleCandidate]
    
    # Cinemática del jet
    px: float
    py: float
    pz: float
    energy: float
    pt: float
    eta: float
    phi: float
    mass: float
    
    # Propiedades del jet
    n_constituents: int
    jet_area: float = 0.0
    
    # B-tagging (simulado)
    btag_score: float = 0.0
    is_btagged: bool = False
    
    # Identificación de sabor
    flavor_truth: Optional[str] = None  # Para simulación
    jet_quality: float = 1.0


@dataclass
class EventAnalysis:
    """Análisis completo de un evento"""
    jets: List[JetCandidate]
    leptons: List[ParticleCandidate]
    photons: List[ParticleCandidate]
    
    # Variables globales del evento
    missing_et: Tuple[float, float]  # (MET_x, MET_y)
    scalar_ht: float  # Suma escalar de pT de jets
    vector_ht: Tuple[float, float]  # Suma vectorial
    
    # Masas invariantes candidatas
    invariant_masses: Dict[str, List[float]]
    
    # Clasificación del evento
    event_type: str = "unknown"
    signal_significance: float = 0.0


class ParticlePhysicsJetService(BaseService):
    """
    Servicio de análisis de jets en física de partículas
    """
    
    def __init__(self):
        super().__init__("ParticlePhysicsJets")
        
        # Configuración de jet clustering
        self.jet_config = {
            'algorithm': 'anti_kt',
            'R_parameter': 0.4,  # Radio del jet
            'pt_min': 20.0,  # GeV
            'eta_max': 2.5,
            'ghost_area': 0.01  # Para área de jet
        }
        
        # Configuración de b-tagging
        self.btag_config = {
            'working_point': 'medium',
            'efficiency_b': 0.70,
            'misid_rate_c': 0.20,
            'misid_rate_light': 0.01
        }
        
        logger.info("⚛️ ParticlePhysicsJetService inicializado")
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process particle physics jet analysis request
        
        Args:
            request_data: Request containing particle data and analysis parameters
            
        Returns:
            Analysis results
        """
        try:
            self.log_request(request_data)
            
            # Validate input
            validation = self.validate_scientific_input(request_data)
            if not validation["valid"]:
                return self.handle_error(ValueError(validation["error"]), "input_validation")
            
            # Extract parameters
            operation = request_data.get("operation", "jet_analysis")
            particles = request_data.get("particles", [])
            event_id = request_data.get("event_id", "unknown")
            clustering_algorithm = request_data.get("clustering_algorithm", "anti_kt")
            jet_radius = request_data.get("jet_radius", 0.4)
            
            # Route to appropriate analysis method
            if operation == "jet_analysis":
                result = await self.analyze_jet_event(
                    particles=particles,
                    event_id=event_id,
                    clustering_algorithm=clustering_algorithm,
                    jet_radius=jet_radius
                )
            elif operation == "invariant_mass":
                result = await self.calculate_invariant_mass(
                    particles=particles,
                    particle_selection=request_data.get("particle_selection")
                )
            elif operation == "new_physics_search":
                result = await self.search_new_physics_signatures(
                    events=request_data.get("events", [particles]),
                    background_model=request_data.get("background_model", "qcd_multijet")
                )
            else:
                return self.handle_error(ValueError(f"Unknown operation: {operation}"), "operation_routing")
            
            # Format output
            response = self.format_scientific_output(result)
            self.log_response(response)
            
            return response
            
        except QuantumError as e:
            return self.handle_error(e, "process_request")
    
    async def analyze_jet_event(
        self,
        particles: List[Dict[str, float]],
        event_id: str = "unknown",
        clustering_algorithm: str = "anti_kt",
        jet_radius: float = 0.4
    ) -> Dict[str, Any]:
        """
        Análisis completo de jets en un evento
        
        Args:
            particles: Lista de partículas con [px, py, pz, E, type]
            event_id: Identificador del evento
            clustering_algorithm: Algoritmo de clustering
            jet_radius: Radio del jet
            
        Returns:
            Análisis completo del evento con jets
        """
        try:
            logger.info(f"⚛️ Analizando evento con jets: {event_id}")
            
            # Preparar candidatos de partículas
            particle_candidates = self._prepare_particle_candidates(particles)
            
            # Jet clustering
            jets = await self._perform_jet_clustering(
                particle_candidates, clustering_algorithm, jet_radius
            )
            
            # Separar leptons y photons
            leptons = [p for p in particle_candidates if p.particle_type in ['electron', 'muon']]
            photons = [p for p in particle_candidates if p.particle_type == 'photon']
            
            # Calcular variables globales
            global_vars = self._calculate_global_variables(jets, leptons, photons)
            
            # Análisis de masa invariante
            mass_analysis = await self._analyze_invariant_masses(jets, leptons, photons)
            
            # B-tagging simulation
            btagged_jets = self._simulate_btag(jets)
            
            # Clasificación del evento
            event_classification = await self._classify_event_type(jets, leptons, global_vars)
            
            # Análisis de estructura de jets
            jet_structure = await self._analyze_jet_structure(jets)
            
            return {
                "event_id": event_id,
                "jet_analysis": {
                    "n_jets": len(jets),
                    "algorithm": clustering_algorithm,
                    "radius_parameter": jet_radius,
                    "jets": [self._jet_to_dict(jet) for jet in jets],
                    "leading_jet_pt": max([j.pt for j in jets]) if jets else 0.0,
                    "second_jet_pt": sorted([j.pt for j in jets], reverse=True)[1] if len(jets) > 1 else 0.0
                },
                "global_variables": {
                    "missing_et": {
                        "met": np.sqrt(global_vars['missing_et'][0]**2 + global_vars['missing_et'][1]**2),
                        "met_phi": np.arctan2(global_vars['missing_et'][1], global_vars['missing_et'][0])
                    },
                    "scalar_ht": global_vars['scalar_ht'],
                    "n_leptons": len(leptons),
                    "n_photons": len(photons)
                },
                "invariant_mass_analysis": mass_analysis,
                "btag_analysis": {
                    "n_btagged_jets": len(btagged_jets),
                    "btag_working_point": self.btag_config['working_point'],
                    "btagged_jets": [self._jet_to_dict(jet) for jet in btagged_jets]
                },
                "event_classification": event_classification,
                "jet_structure": jet_structure,
                "physics_interpretation": await self._interpret_physics(
                    jets, leptons, mass_analysis, event_classification
                )
            }
            
        except QuantumError as e:
            logger.error(f"❌ Error en análisis de jets: {str(e)}")
            raise
    
    async def calculate_invariant_mass(
        self,
        particles: List[Dict[str, float]],
        particle_selection: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Cálculo de masa invariante para sistema de partículas
        
        Args:
            particles: Lista de partículas [px, py, pz, E]
            particle_selection: Criterios de selección
            
        Returns:
            Análisis de masa invariante
        """
        try:
            logger.info("📊 Calculando masa invariante")
            
            # Preparar partículas
            particle_candidates = self._prepare_particle_candidates(particles)
            
            # Aplicar selección si se especifica
            if particle_selection:
                particle_candidates = self._apply_particle_selection(
                    particle_candidates, particle_selection
                )
            
            # Calcular masa invariante total
            total_mass = self._calculate_system_invariant_mass(particle_candidates)
            
            # Análisis de combinaciones
            combinations_analysis = await self._analyze_particle_combinations(particle_candidates)
            
            # Análisis de distribución de masa
            mass_distribution = self._analyze_mass_distribution(combinations_analysis)
            
            # Búsqueda de resonancias
            resonance_search = await self._search_resonances(combinations_analysis)
            
            return {
                "total_system": {
                    "invariant_mass_gev": total_mass,
                    "n_particles": len(particle_candidates),
                    "total_energy": sum(p.energy for p in particle_candidates),
                    "total_momentum": self._calculate_total_momentum(particle_candidates)
                },
                "combinations_analysis": combinations_analysis,
                "mass_distribution": mass_distribution,
                "resonance_candidates": resonance_search,
                "known_particle_matches": self._match_known_particles(total_mass, combinations_analysis)
            }
            
        except QuantumError as e:
            logger.error(f"❌ Error calculando masa invariante: {str(e)}")
            raise
    
    async def search_new_physics_signatures(
        self,
        events: List[List[Dict[str, float]]],
        background_model: str = "qcd_multijet"
    ) -> Dict[str, Any]:
        """
        Búsqueda de señales de nueva física
        
        Args:
            events: Lista de eventos (cada evento es lista de partículas)
            background_model: Modelo de background
            
        Returns:
            Análisis de búsqueda de nueva física
        """
        try:
            logger.info(f"🔍 Buscando nueva física en {len(events)} eventos")
            
            # Analizar cada evento
            event_analyses = []
            for i, event_particles in enumerate(events):
                analysis = await self.analyze_jet_event(
                    event_particles, f"event_{i}", "anti_kt", 0.4
                )
                event_analyses.append(analysis)
            
            # Construir distribuciones
            distributions = self._build_kinematic_distributions(event_analyses)
            
            # Modelo de background
            background_expectation = self._model_background(
                len(events), background_model, distributions
            )
            
            # Búsqueda de excesos
            excess_analysis = self._search_for_excesses(distributions, background_expectation)
            
            # Análisis estadístico
            statistical_analysis = await self._perform_statistical_analysis(
                distributions, background_expectation
            )
            
            # Interpretación de nueva física
            new_physics_interpretation = await self._interpret_new_physics_signals(
                excess_analysis, statistical_analysis
            )
            
            return {
                "search_summary": {
                    "n_events_analyzed": len(events),
                    "background_model": background_model,
                    "search_channels": list(distributions.keys())
                },
                "kinematic_distributions": distributions,
                "background_expectation": background_expectation,
                "excess_analysis": excess_analysis,
                "statistical_significance": statistical_analysis,
                "new_physics_interpretation": new_physics_interpretation,
                "recommendations": self._generate_analysis_recommendations(
                    excess_analysis, statistical_analysis
                )
            }
            
        except QuantumError as e:
            logger.error(f"❌ Error en búsqueda de nueva física: {str(e)}")
            raise
    
    # ========== MÉTODOS DE JET CLUSTERING ==========
    
    def _prepare_particle_candidates(
        self,
        particles: List[Dict[str, float]]
    ) -> List[ParticleCandidate]:
        """Prepara candidatos de partículas"""
        
        candidates = []
        
        for particle in particles:
            px = particle.get('px', 0.0)
            py = particle.get('py', 0.0)
            pz = particle.get('pz', 0.0)
            energy = particle.get('energy', particle.get('E', 0.0))
            
            # Calcular propiedades derivadas
            pt = np.sqrt(px**2 + py**2)
            p = np.sqrt(px**2 + py**2 + pz**2)
            
            if p > 0:
                eta = 0.5 * np.log((p + pz) / (p - pz)) if p != pz else 0.0
            else:
                eta = 0.0
            
            phi = np.arctan2(py, px)
            
            # Masa invariante
            mass_sq = energy**2 - p**2
            mass = np.sqrt(max(0, mass_sq))
            
            candidate = ParticleCandidate(
                px=px, py=py, pz=pz, energy=energy,
                pt=pt, eta=eta, phi=phi, mass=mass,
                particle_type=particle.get('type', 'unknown')
            )
            
            candidates.append(candidate)
        
        return candidates
    
    async def _perform_jet_clustering(
        self,
        particles: List[ParticleCandidate],
        algorithm: str,
        radius: float
    ) -> List[JetCandidate]:
        """Realiza clustering de jets"""
        
        if algorithm == "anti_kt":
            return self._cluster_anti_kt(particles, radius)
        elif algorithm == "kt":
            return self._cluster_kt(particles, radius)
        elif algorithm == "cambridge_aachen":
            return self._cluster_cambridge_aachen(particles, radius)
        else:
            # Algoritmo por defecto
            return self._cluster_anti_kt(particles, radius)
    
    def _cluster_anti_kt(
        self,
        particles: List[ParticleCandidate],
        radius: float
    ) -> List[JetCandidate]:
        """Clustering anti-kT (implementación simplificada)"""
        
        # Filtrar partículas por pT mínimo
        valid_particles = [
            p for p in particles 
            if p.pt > self.jet_config['pt_min'] and abs(p.eta) < self.jet_config['eta_max']
        ]
        
        if not valid_particles:
            return []
        
        jets = []
        remaining_particles = valid_particles.copy()
        
        while remaining_particles:
            # Encontrar partícula con mayor pT (seed del jet)
            seed = max(remaining_particles, key=lambda p: p.pt)
            remaining_particles.remove(seed)
            
            # Construir jet alrededor del seed
            jet_constituents = [seed]
            
            # Agregar partículas dentro del radio
            to_remove = []
            for particle in remaining_particles:
                distance = self._calculate_delta_r(seed, particle)
                if distance < radius:
                    jet_constituents.append(particle)
                    to_remove.append(particle)
            
            # Remover partículas agregadas al jet
            for particle in to_remove:
                remaining_particles.remove(particle)
            
            # Crear candidato de jet
            jet = self._create_jet_candidate(jet_constituents)
            
            # Aplicar cortes de calidad
            if jet.pt > self.jet_config['pt_min'] and abs(jet.eta) < self.jet_config['eta_max']:
                jets.append(jet)
        
        # Ordenar jets por pT
        jets.sort(key=lambda j: j.pt, reverse=True)
        
        return jets
    
    def _cluster_kt(
        self,
        particles: List[ParticleCandidate],
        radius: float
    ) -> List[JetCandidate]:
        """Clustering kT (simplificado)"""
        
        # Implementación similar al anti-kT pero con diferentes métricas de distancia
        valid_particles = [
            p for p in particles 
            if p.pt > self.jet_config['pt_min'] and abs(p.eta) < self.jet_config['eta_max']
        ]
        
        jets = []
        clusters = [[p] for p in valid_particles]  # Cada partícula inicia como cluster
        
        while len(clusters) > 1:
            min_distance = float('inf')
            merge_i, merge_j = -1, -1
            
            # Encontrar par más cercano para merge
            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    # Distancia kT entre clusters
                    dist = self._calculate_kt_distance(clusters[i], clusters[j], radius)
                    if dist < min_distance:
                        min_distance = dist
                        merge_i, merge_j = i, j
            
            # Merger clusters si están dentro del radio
            if min_distance < radius**2:
                merged_cluster = clusters[merge_i] + clusters[merge_j]
                clusters = [c for k, c in enumerate(clusters) if k not in [merge_i, merge_j]]
                clusters.append(merged_cluster)
            else:
                break
        
        # Convertir clusters a jets
        for cluster in clusters:
            jet = self._create_jet_candidate(cluster)
            if jet.pt > self.jet_config['pt_min']:
                jets.append(jet)
        
        jets.sort(key=lambda j: j.pt, reverse=True)
        return jets
    
    def _cluster_cambridge_aachen(
        self,
        particles: List[ParticleCandidate],
        radius: float
    ) -> List[JetCandidate]:
        """Clustering Cambridge/Aachen (simplificado)"""
        
        # Similar al kT pero con métricas de distancia diferentes
        return self._cluster_kt(particles, radius)  # Implementación simplificada
    
    def _calculate_delta_r(
        self,
        p1: ParticleCandidate,
        p2: ParticleCandidate
    ) -> float:
        """Calcula distancia ΔR entre dos partículas"""
        
        delta_eta = p1.eta - p2.eta
        delta_phi = p1.phi - p2.phi
        
        # Normalizar delta_phi al rango [-π, π]
        while delta_phi > np.pi:
            delta_phi -= 2 * np.pi
        while delta_phi < -np.pi:
            delta_phi += 2 * np.pi
        
        return np.sqrt(delta_eta**2 + delta_phi**2)
    
    def _calculate_kt_distance(
        self,
        cluster1: List[ParticleCandidate],
        cluster2: List[ParticleCandidate],
        radius: float
    ) -> float:
        """Calcula distancia kT entre clusters"""
        
        # Representantes de los clusters (suma de momentos)
        p1_total = self._sum_four_momenta(cluster1)
        p2_total = self._sum_four_momenta(cluster2)
        
        # Distancia angular
        delta_r = self._calculate_delta_r_from_momenta(p1_total, p2_total)
        
        # Distancia kT
        min_pt = min(p1_total['pt'], p2_total['pt'])
        kt_distance = min_pt**2 * (delta_r / radius)**2
        
        return kt_distance
    
    def _sum_four_momenta(self, particles: List[ParticleCandidate]) -> Dict[str, float]:
        """Suma cuadrimomentos de una lista de partículas"""
        
        px_total = sum(p.px for p in particles)
        py_total = sum(p.py for p in particles)
        pz_total = sum(p.pz for p in particles)
        e_total = sum(p.energy for p in particles)
        
        pt_total = np.sqrt(px_total**2 + py_total**2)
        p_total = np.sqrt(px_total**2 + py_total**2 + pz_total**2)
        
        eta_total = 0.5 * np.log((p_total + pz_total) / (p_total - pz_total)) if p_total != pz_total else 0.0
        phi_total = np.arctan2(py_total, px_total)
        
        return {
            'px': px_total, 'py': py_total, 'pz': pz_total, 'energy': e_total,
            'pt': pt_total, 'eta': eta_total, 'phi': phi_total
        }
    
    def _calculate_delta_r_from_momenta(
        self,
        p1: Dict[str, float],
        p2: Dict[str, float]
    ) -> float:
        """Calcula ΔR entre dos cuadrimomentos"""
        
        delta_eta = p1['eta'] - p2['eta']
        delta_phi = p1['phi'] - p2['phi']
        
        while delta_phi > np.pi:
            delta_phi -= 2 * np.pi
        while delta_phi < -np.pi:
            delta_phi += 2 * np.pi
        
        return np.sqrt(delta_eta**2 + delta_phi**2)
    
    def _create_jet_candidate(self, constituents: List[ParticleCandidate]) -> JetCandidate:
        """Crea candidato de jet a partir de constituyentes"""
        
        # Sumar cuadrimomentos
        total_momentum = self._sum_four_momenta(constituents)
        
        # Calcular masa invariante
        mass_sq = (total_momentum['energy']**2 - 
                  total_momentum['px']**2 - 
                  total_momentum['py']**2 - 
                  total_momentum['pz']**2)
        mass = np.sqrt(max(0, mass_sq))
        
        # Simular b-tagging score
        btag_score = self._simulate_btag_score(constituents)
        is_btagged = btag_score > 0.5  # Working point medium
        
        return JetCandidate(
            constituents=constituents,
            px=total_momentum['px'],
            py=total_momentum['py'],
            pz=total_momentum['pz'],
            energy=total_momentum['energy'],
            pt=total_momentum['pt'],
            eta=total_momentum['eta'],
            phi=total_momentum['phi'],
            mass=mass,
            n_constituents=len(constituents),
            btag_score=btag_score,
            is_btagged=is_btagged
        )
    
    # ========== MÉTODOS DE ANÁLISIS ==========
    
    def _calculate_global_variables(
        self,
        jets: List[JetCandidate],
        leptons: List[ParticleCandidate],
        photons: List[ParticleCandidate]
    ) -> Dict[str, Any]:
        """Calcula variables globales del evento"""
        
        # Missing ET (simplificado - suma vectorial negativa)
        total_px = sum(j.px for j in jets) + sum(l.px for l in leptons) + sum(ph.px for ph in photons)
        total_py = sum(j.py for j in jets) + sum(l.py for l in leptons) + sum(ph.py for ph in photons)
        
        missing_et = (-total_px, -total_py)
        
        # Scalar HT (suma de pT de jets)
        scalar_ht = sum(j.pt for j in jets)
        
        # Vector HT
        vector_ht_x = sum(j.px for j in jets)
        vector_ht_y = sum(j.py for j in jets)
        
        return {
            'missing_et': missing_et,
            'scalar_ht': scalar_ht,
            'vector_ht': (vector_ht_x, vector_ht_y)
        }
    
    async def _analyze_invariant_masses(
        self,
        jets: List[JetCandidate],
        leptons: List[ParticleCandidate],
        photons: List[ParticleCandidate]
    ) -> Dict[str, Any]:
        """Análisis de masas invariantes candidatas"""
        
        mass_candidates = {}
        
        # Di-jet masses
        if len(jets) >= 2:
            dijet_masses = []
            for i in range(len(jets)):
                for j in range(i + 1, len(jets)):
                    mass = self._calculate_dijet_mass(jets[i], jets[j])
                    dijet_masses.append(mass)
            mass_candidates['dijet'] = dijet_masses
        
        # Multi-jet masses
        if len(jets) >= 3:
            trijet_masses = []
            for i in range(len(jets)):
                for j in range(i + 1, len(jets)):
                    for k in range(j + 1, len(jets)):
                        mass = self._calculate_multijet_mass([jets[i], jets[j], jets[k]])
                        trijet_masses.append(mass)
            mass_candidates['trijet'] = trijet_masses
        
        # Lepton-jet masses (para busquedas de leptoquarks, etc.)
        if leptons and jets:
            lepton_jet_masses = []
            for lepton in leptons:
                for jet in jets:
                    mass = self._calculate_lepton_jet_mass(lepton, jet)
                    lepton_jet_masses.append(mass)
            mass_candidates['lepton_jet'] = lepton_jet_masses
        
        # Di-lepton masses (Z, Higgs candidates)
        if len(leptons) >= 2:
            dilepton_masses = []
            for i in range(len(leptons)):
                for j in range(i + 1, len(leptons)):
                    mass = self._calculate_dilepton_mass(leptons[i], leptons[j])
                    dilepton_masses.append(mass)
            mass_candidates['dilepton'] = dilepton_masses
        
        return mass_candidates
    
    def _calculate_dijet_mass(self, jet1: JetCandidate, jet2: JetCandidate) -> float:
        """Calcula masa invariante di-jet"""
        
        px_total = jet1.px + jet2.px
        py_total = jet1.py + jet2.py
        pz_total = jet1.pz + jet2.pz
        e_total = jet1.energy + jet2.energy
        
        mass_sq = e_total**2 - px_total**2 - py_total**2 - pz_total**2
        return np.sqrt(max(0, mass_sq))
    
    def _calculate_multijet_mass(self, jets: List[JetCandidate]) -> float:
        """Calcula masa invariante multi-jet"""
        
        px_total = sum(j.px for j in jets)
        py_total = sum(j.py for j in jets)
        pz_total = sum(j.pz for j in jets)
        e_total = sum(j.energy for j in jets)
        
        mass_sq = e_total**2 - px_total**2 - py_total**2 - pz_total**2
        return np.sqrt(max(0, mass_sq))
    
    def _calculate_lepton_jet_mass(
        self,
        lepton: ParticleCandidate,
        jet: JetCandidate
    ) -> float:
        """Calcula masa invariante lepton-jet"""
        
        px_total = lepton.px + jet.px
        py_total = lepton.py + jet.py
        pz_total = lepton.pz + jet.pz
        e_total = lepton.energy + jet.energy
        
        mass_sq = e_total**2 - px_total**2 - py_total**2 - pz_total**2
        return np.sqrt(max(0, mass_sq))
    
    def _calculate_dilepton_mass(
        self,
        lepton1: ParticleCandidate,
        lepton2: ParticleCandidate
    ) -> float:
        """Calcula masa invariante di-lepton"""
        
        px_total = lepton1.px + lepton2.px
        py_total = lepton1.py + lepton2.py
        pz_total = lepton1.pz + lepton2.pz
        e_total = lepton1.energy + lepton2.energy
        
        mass_sq = e_total**2 - px_total**2 - py_total**2 - pz_total**2
        return np.sqrt(max(0, mass_sq))
    
    def _calculate_system_invariant_mass(
        self,
        particles: List[ParticleCandidate]
    ) -> float:
        """Calcula masa invariante del sistema completo"""
        
        px_total = sum(p.px for p in particles)
        py_total = sum(p.py for p in particles)
        pz_total = sum(p.pz for p in particles)
        e_total = sum(p.energy for p in particles)
        
        mass_sq = e_total**2 - px_total**2 - py_total**2 - pz_total**2
        return np.sqrt(max(0, mass_sq))
    
    def _calculate_total_momentum(self, particles: List[ParticleCandidate]) -> Dict[str, float]:
        """Calcula momento total del sistema"""
        
        px_total = sum(p.px for p in particles)
        py_total = sum(p.py for p in particles)
        pz_total = sum(p.pz for p in particles)
        
        p_total = np.sqrt(px_total**2 + py_total**2 + pz_total**2)
        pt_total = np.sqrt(px_total**2 + py_total**2)
        
        return {
            'px': px_total,
            'py': py_total,
            'pz': pz_total,
            'p_total': p_total,
            'pt_total': pt_total
        }
    
    # ========== MÉTODOS AUXILIARES ==========
    
    def _simulate_btag_score(self, constituents: List[ParticleCandidate]) -> float:
        """Simula score de b-tagging"""
        
        # Simulación simple basada en propiedades del jet
        base_score = 0.1
        
        # Más constituyentes -> mayor probabilidad de b-jet
        n_factor = len(constituents) / 20.0
        
        # Score aleatorio con sesgo basado en número de constituyentes
        random_component = np.random.random()
        
        score = base_score + n_factor * 0.3 + random_component * 0.6
        
        return min(1.0, score)
    
    def _simulate_btag(self, jets: List[JetCandidate]) -> List[JetCandidate]:
        """Simula b-tagging y retorna jets b-tagged"""
        
        btagged = []
        
        for jet in jets:
            # Aplicar eficiencia de b-tagging
            if jet.btag_score > 0.5:  # Working point
                btagged.append(jet)
        
        return btagged
    
    def _jet_to_dict(self, jet: JetCandidate) -> Dict[str, Any]:
        """Convierte jet a diccionario"""
        
        return {
            'pt': jet.pt,
            'eta': jet.eta,
            'phi': jet.phi,
            'mass': jet.mass,
            'energy': jet.energy,
            'n_constituents': jet.n_constituents,
            'btag_score': jet.btag_score,
            'is_btagged': jet.is_btagged
        }
    
    async def _classify_event_type(
        self,
        jets: List[JetCandidate],
        leptons: List[ParticleCandidate],
        global_vars: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Clasifica el tipo de evento"""
        
        n_jets = len(jets)
        n_leptons = len(leptons)
        scalar_ht = global_vars['scalar_ht']
        met = np.sqrt(global_vars['missing_et'][0]**2 + global_vars['missing_et'][1]**2)
        
        # Clasificación simple
        if n_jets >= 4 and n_leptons == 0 and scalar_ht > 500:
            event_type = "Multijet_QCD"
            confidence = 0.8
        elif n_jets >= 2 and n_leptons >= 1 and met > 50:
            event_type = "W_plus_jets"
            confidence = 0.7
        elif n_jets >= 2 and n_leptons >= 2:
            event_type = "Dilepton_ttbar"
            confidence = 0.6
        elif n_jets == 0 and n_leptons >= 2:
            event_type = "Drell_Yan"
            confidence = 0.9
        else:
            event_type = "Unknown"
            confidence = 0.3
        
        return {
            'event_type': event_type,
            'confidence': confidence,
            'classification_features': {
                'n_jets': n_jets,
                'n_leptons': n_leptons,
                'scalar_ht': scalar_ht,
                'missing_et': met
            }
        }
    
    async def _analyze_jet_structure(self, jets: List[JetCandidate]) -> Dict[str, Any]:
        """Analiza estructura interna de jets"""
        
        if not jets:
            return {}
        
        # Análisis del jet líder
        leading_jet = jets[0]
        
        # Jet shapes (simplificado)
        jet_shapes = {
            'girth': self._calculate_jet_girth(leading_jet),
            'broadening': self._calculate_jet_broadening(leading_jet),
            'mass_ratio': leading_jet.mass / leading_jet.pt if leading_jet.pt > 0 else 0
        }
        
        return {
            'leading_jet_analysis': jet_shapes,
            'average_jet_mass': np.mean([j.mass for j in jets]),
            'jet_mass_distribution': [j.mass for j in jets]
        }
    
    def _calculate_jet_girth(self, jet: JetCandidate) -> float:
        """Calcula girth del jet (medida de ancho)"""
        
        if not jet.constituents or jet.pt == 0:
            return 0.0
        
        girth = 0.0
        for constituent in jet.constituents:
            dr = self._calculate_delta_r_from_momenta(
                {'eta': jet.eta, 'phi': jet.phi},
                {'eta': constituent.eta, 'phi': constituent.phi}
            )
            girth += constituent.pt * dr
        
        return girth / jet.pt
    
    def _calculate_jet_broadening(self, jet: JetCandidate) -> float:
        """Calcula broadening del jet"""
        
        if not jet.constituents:
            return 0.0
        
        # Simplificado: dispersión angular de constituyentes
        eta_values = [c.eta for c in jet.constituents]
        phi_values = [c.phi for c in jet.constituents]
        
        if len(eta_values) > 1:
            broadening = np.std(eta_values) + np.std(phi_values)
        else:
            broadening = 0.0
        
        return broadening
    
    async def _interpret_physics(
        self,
        jets: List[JetCandidate],
        leptons: List[ParticleCandidate],
        mass_analysis: Dict[str, Any],
        event_classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Interpretación física del evento"""
        
        interpretations = []
        
        # Buscar resonancias conocidas
        if 'dijet' in mass_analysis:
            dijet_masses = mass_analysis['dijet']
            for mass in dijet_masses:
                if 70 < mass < 90:
                    interpretations.append({
                        'particle': 'W_boson_candidate',
                        'mass': mass,
                        'confidence': 0.7
                    })
                elif 85 < mass < 97:
                    interpretations.append({
                        'particle': 'Z_boson_candidate',
                        'mass': mass,
                        'confidence': 0.8
                    })
                elif 120 < mass < 130:
                    interpretations.append({
                        'particle': 'Higgs_candidate',
                        'mass': mass,
                        'confidence': 0.6
                    })
        
        # Interpretación basada en clasificación de evento
        physics_process = "Unknown"
        if event_classification['event_type'] == "Multijet_QCD":
            physics_process = "QCD multijet production"
        elif event_classification['event_type'] == "W_plus_jets":
            physics_process = "W boson + jets production"
        elif event_classification['event_type'] == "Dilepton_ttbar":
            physics_process = "Top quark pair production"
        
        return {
            'physics_process': physics_process,
            'resonance_candidates': interpretations,
            'topology': f"{len(jets)} jets + {len(leptons)} leptons",
            'physics_significance': event_classification.get('confidence', 0.0)
        }
    
    # ========== MÉTODOS DE NUEVA FÍSICA ==========
    
    async def _analyze_particle_combinations(
        self,
        particles: List[ParticleCandidate]
    ) -> Dict[str, List[float]]:
        """Analiza todas las combinaciones de partículas"""
        
        combinations = {
            'all_pairs': [],
            'all_triplets': [],
            'all_quadruplets': []
        }
        
        n = len(particles)
        
        # Pares
        for i in range(n):
            for j in range(i + 1, n):
                mass = self._calculate_dilepton_mass(particles[i], particles[j])
                combinations['all_pairs'].append(mass)
        
        # Triplets
        for i in range(n):
            for j in range(i + 1, n):
                for k in range(j + 1, n):
                    total_momentum = self._sum_four_momenta([particles[i], particles[j], particles[k]])
                    mass_sq = (total_momentum['energy']**2 - 
                              total_momentum['px']**2 - 
                              total_momentum['py']**2 - 
                              total_momentum['pz']**2)
                    mass = np.sqrt(max(0, mass_sq))
                    combinations['all_triplets'].append(mass)
        
        return combinations
    
    def _analyze_mass_distribution(
        self,
        combinations: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        """Analiza distribución de masas"""
        
        distribution_analysis = {}
        
        for combo_type, masses in combinations.items():
            if masses:
                distribution_analysis[combo_type] = {
                    'mean': np.mean(masses),
                    'std': np.std(masses),
                    'min': np.min(masses),
                    'max': np.max(masses),
                    'n_combinations': len(masses)
                }
        
        return distribution_analysis
    
    async def _search_resonances(
        self,
        combinations: Dict[str, List[float]]
    ) -> List[Dict[str, Any]]:
        """Busca resonancias en las distribuciones de masa"""
        
        resonance_candidates = []
        
        for combo_type, masses in combinations.items():
            if not masses:
                continue
            
            # Buscar picos en la distribución
            hist, bin_edges = np.histogram(masses, bins=50)
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
            
            # Encontrar picos locales
            peak_indices = []
            for i in range(1, len(hist) - 1):
                if hist[i] > hist[i-1] and hist[i] > hist[i+1] and hist[i] > 2:
                    peak_indices.append(i)
            
            # Evaluar picos como posibles resonancias
            for peak_idx in peak_indices:
                peak_mass = bin_centers[peak_idx]
                peak_height = hist[peak_idx]
                
                # Calcular significancia del pico
                background_level = np.median(hist)
                significance = (peak_height - background_level) / np.sqrt(background_level + 1)
                
                if significance > 2.0:  # 2-sigma threshold
                    resonance_candidates.append({
                        'combination_type': combo_type,
                        'mass_gev': peak_mass,
                        'significance': significance,
                        'peak_height': peak_height,
                        'background_level': background_level
                    })
        
        return resonance_candidates
    
    def _match_known_particles(
        self,
        total_mass: float,
        combinations: Dict[str, List[float]]
    ) -> List[Dict[str, Any]]:
        """Busca coincidencias con partículas conocidas"""
        
        matches = []
        
        # Buscar en masa total
        for particle_name, known_mass in PARTICLE_MASSES.items():
            if abs(total_mass - known_mass) < 5.0:  # 5 GeV tolerance
                matches.append({
                    'particle': particle_name,
                    'known_mass': known_mass,
                    'measured_mass': total_mass,
                    'mass_difference': abs(total_mass - known_mass),
                    'combination_type': 'total_system'
                })
        
        # Buscar en combinaciones
        for combo_type, masses in combinations.items():
            for mass in masses:
                for particle_name, known_mass in PARTICLE_MASSES.items():
                    if abs(mass - known_mass) < 3.0:  # 3 GeV tolerance for combinations
                        matches.append({
                            'particle': particle_name,
                            'known_mass': known_mass,
                            'measured_mass': mass,
                            'mass_difference': abs(mass - known_mass),
                            'combination_type': combo_type
                        })
        
        return matches
    
    def _apply_particle_selection(
        self,
        particles: List[ParticleCandidate],
        selection: Dict[str, Any]
    ) -> List[ParticleCandidate]:
        """Aplica criterios de selección a las partículas"""
        
        selected = []
        
        for particle in particles:
            passes_selection = True
            
            # Filtros de pT
            if 'pt_min' in selection and particle.pt < selection['pt_min']:
                passes_selection = False
            if 'pt_max' in selection and particle.pt > selection['pt_max']:
                passes_selection = False
            
            # Filtros de eta
            if 'eta_max' in selection and abs(particle.eta) > selection['eta_max']:
                passes_selection = False
            
            # Filtros de tipo de partícula
            if 'particle_types' in selection and particle.particle_type not in selection['particle_types']:
                passes_selection = False
            
            if passes_selection:
                selected.append(particle)
        
        return selected
    
    def _build_kinematic_distributions(
        self,
        event_analyses: List[Dict[str, Any]]
    ) -> Dict[str, List[float]]:
        """Construye distribuciones cinemáticas"""
        
        distributions = {
            'leading_jet_pt': [],
            'missing_et': [],
            'scalar_ht': [],
            'n_jets': [],
            'n_leptons': []
        }
        
        for analysis in event_analyses:
            jet_analysis = analysis.get('jet_analysis', {})
            global_vars = analysis.get('global_variables', {})
            
            distributions['leading_jet_pt'].append(jet_analysis.get('leading_jet_pt', 0))
            distributions['missing_et'].append(global_vars.get('missing_et', {}).get('met', 0))
            distributions['scalar_ht'].append(global_vars.get('scalar_ht', 0))
            distributions['n_jets'].append(jet_analysis.get('n_jets', 0))
            distributions['n_leptons'].append(global_vars.get('n_leptons', 0))
        
        return distributions
    
    def _model_background(
        self,
        n_events: int,
        background_model: str,
        distributions: Dict[str, List[float]]
    ) -> Dict[str, Any]:
        """Modela background esperado"""
        
        # Modelo simplificado de background QCD
        background = {
            'model_type': background_model,
            'total_expected_events': n_events * 0.9,  # 90% background
            'uncertainties': {
                'statistical': np.sqrt(n_events * 0.9),
                'systematic': n_events * 0.9 * 0.1  # 10% systematic
            }
        }
        
        return background
    
    def _search_for_excesses(
        self,
        distributions: Dict[str, List[float]],
        background: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Busca excesos sobre el background"""
        
        excesses = {}
        
        for dist_name, values in distributions.items():
            if not values:
                continue
            
            # Análisis simple de exceso en cola alta
            high_tail = [v for v in values if v > np.percentile(values, 95)]
            
            expected_high_tail = len(values) * 0.05  # 5% esperado
            observed_high_tail = len(high_tail)
            
            excess = observed_high_tail - expected_high_tail
            significance = excess / np.sqrt(expected_high_tail + 1)
            
            excesses[dist_name] = {
                'observed': observed_high_tail,
                'expected': expected_high_tail,
                'excess': excess,
                'significance': significance
            }
        
        return excesses
    
    async def _perform_statistical_analysis(
        self,
        distributions: Dict[str, List[float]],
        background: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Realiza análisis estadístico"""
        
        # Análisis estadístico simplificado
        total_observed = sum(len(values) for values in distributions.values() if values)
        total_expected = background['total_expected_events']
        
        # Test de Poisson simple
        if total_expected > 0:
            z_score = (total_observed - total_expected) / np.sqrt(total_expected)
        else:
            z_score = 0
        
        return {
            'total_observed': total_observed,
            'total_expected': total_expected,
            'z_score': z_score,
            'p_value': 2 * (1 - scipy.stats.norm.cdf(abs(z_score))) if 'scipy.stats' in dir() else 0.5,
            'significance_sigma': abs(z_score)
        }
    
    async def _interpret_new_physics_signals(
        self,
        excess_analysis: Dict[str, Any],
        statistical_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Interpreta señales de nueva física"""
        
        interpretations = []
        
        # Buscar excesos significativos
        for variable, excess_info in excess_analysis.items():
            if excess_info['significance'] > 2.0:
                interpretations.append({
                    'variable': variable,
                    'signal_type': 'High-tail excess',
                    'significance': excess_info['significance'],
                    'possible_interpretation': self._interpret_excess_variable(variable)
                })
        
        overall_significance = statistical_analysis.get('significance_sigma', 0)
        
        return {
            'individual_excesses': interpretations,
            'overall_significance': overall_significance,
            'new_physics_probability': min(1.0, overall_significance / 5.0),  # Rough estimate
            'recommended_follow_up': self._recommend_follow_up(interpretations, overall_significance)
        }
    
    def _interpret_excess_variable(self, variable: str) -> str:
        """Interpreta exceso en variable específica"""
        
        interpretations = {
            'leading_jet_pt': 'High-energy jets may indicate heavy particle production',
            'missing_et': 'Large MET could suggest dark matter or neutrino production',
            'scalar_ht': 'High HT may indicate new heavy particles or extra dimensions',
            'n_jets': 'Excess jets could suggest cascade decays or new interactions'
        }
        
        return interpretations.get(variable, 'Unknown new physics signature')
    
    def _recommend_follow_up(
        self,
        interpretations: List[Dict[str, Any]],
        overall_significance: float
    ) -> List[str]:
        """Recomienda análisis de seguimiento"""
        
        recommendations = []
        
        if overall_significance > 3.0:
            recommendations.append("Increase statistics with larger dataset")
            recommendations.append("Perform detailed systematic uncertainty studies")
        
        if any(i['variable'] == 'missing_et' for i in interpretations):
            recommendations.append("Search for dark matter candidates")
            recommendations.append("Analyze missing energy topology")
        
        if any(i['variable'] == 'leading_jet_pt' for i in interpretations):
            recommendations.append("Search for heavy resonances in dijet spectrum")
            recommendations.append("Analyze jet substructure")
        
        if not recommendations:
            recommendations.append("Continue monitoring with standard model predictions")
        
        return recommendations
    
    def _generate_analysis_recommendations(
        self,
        excess_analysis: Dict[str, Any],
        statistical_analysis: Dict[str, Any]
    ) -> List[str]:
        """Genera recomendaciones de análisis"""
        
        recommendations = []
        
        significance = statistical_analysis.get('significance_sigma', 0)
        
        if significance > 5.0:
            recommendations.append("🎉 Potential discovery! Publish results immediately")
        elif significance > 3.0:
            recommendations.append("Strong evidence - increase statistics and reduce systematics")
        elif significance > 2.0:
            recommendations.append("Interesting excess - continue investigation")
        else:
            recommendations.append("No significant deviation from Standard Model")
        
        # Recomendaciones específicas por variable
        for variable, excess in excess_analysis.items():
            if excess['significance'] > 2.0:
                recommendations.append(f"Focus analysis on {variable} distribution")
        
        return recommendations


# Instancia global del servicio
particle_physics_jet_service = ParticlePhysicsJetService()
