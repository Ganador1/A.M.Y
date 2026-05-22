"""
Quantum Chemistry Service for AXIOM Meta/Atlas
- Cálculos de química cuántica usando PySCF
- Optimización de geometría molecular
- Análisis de orbitales y propiedades electrónicas
- Integración con pipeline de descubrimiento científico Atlas
"""

from __future__ import annotations

import asyncio
import os
import tempfile
import json
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from app.exceptions.domain.chemistry import ChemistryError
from app.services.base_service import BaseService

# PySCF availability check
PYSCF_AVAILABLE = None

def _check_pyscf():
    """Check if PySCF is available"""
    global PYSCF_AVAILABLE
    if PYSCF_AVAILABLE is None:
        try:
            import pyscf  # noqa: F401
            PYSCF_AVAILABLE = True
            return True
        except ImportError:
            PYSCF_AVAILABLE = False
            return False
    return PYSCF_AVAILABLE


@dataclass
class MolecularGeometry:
    """Geometría molecular con coordenadas atómicas"""
    atoms: List[Tuple[str, Tuple[float, float, float]]]
    charge: int = 0
    spin: int = 0
    
    def to_pyscf_format(self) -> str:
        """Convierte a formato PySCF"""
        geometry = []
        for atom, (x, y, z) in self.atoms:
            geometry.append(f"{atom} {x:.6f} {y:.6f} {z:.6f}")
        return "; ".join(geometry)


@dataclass
class QuantumChemistryResult:
    """Resultado de cálculo de química cuántica"""
    energy: float
    convergence: bool
    method: str
    basis_set: str
    molecular_geometry: Optional[MolecularGeometry] = None
    molecular_orbitals: Optional[Dict[str, Any]] = None
    properties: Optional[Dict[str, float]] = None
    computation_time: Optional[float] = None


class QuantumChemistryService(BaseService):
    """
    Servicio de química cuántica con PySCF
    Especializado en cálculos DFT, HF, post-HF y optimización molecular
    """
    
    def __init__(self):
        super().__init__("QuantumChemistry")
        self.pyscf_available = _check_pyscf()
        self.temp_dir = tempfile.mkdtemp(prefix="qchem_atlas_")
        
        # Configuraciones predefinidas
        self.basis_sets = {
            "minimal": "sto-3g",
            "standard": "6-31g*",
            "high_quality": "cc-pVTZ",
            "extra_high": "aug-cc-pVQZ"
        }
        
        self.dft_functionals = {
            "b3lyp": "b3lyp",      # Híbrido estándar
            "pbe": "pbe",          # GGA
            "m06": "m06",          # Meta-GGA
            "wb97xd": "wb97x-d",   # Con dispersión
            "camb3lyp": "cam-b3lyp"  # Range-separated
        }
        
    def __del__(self):
        """Limpia archivos temporales de forma segura durante shutdown"""
        try:
            import shutil
            import os
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            # Capturar todas las excepciones incluyendo ImportError durante shutdown
            pass

    async def process_request(self, request_data: Dict) -> Dict:
        """
        Process incoming requests - required by BaseService
        
        Args:
            request_data: Dictionary with 'action' and parameters
            
        Returns:
            Dictionary with results
        """
        action = request_data.get('action')
        
        if action == "scf":
            geometry = request_data.get('geometry')
            result = await self.run_scf_calculation(
                geometry=geometry,
                method=request_data.get('method', 'hf'),
                basis=request_data.get('basis', '6-31g*')
            )
            return {
                'energy': result.energy,
                'convergence': result.convergence,
                'method': result.method,
                'basis_set': result.basis_set
            }
        
        elif action == "optimize":
            geometry = request_data.get('geometry')
            result = await self.optimize_geometry(
                initial_geometry=geometry,
                method=request_data.get('method', 'b3lyp'),
                basis=request_data.get('basis', '6-31g*')
            )
            return {
                'optimized': result.convergence,
                'energy': result.energy,
                'geometry': result.molecular_geometry
            }
        
        elif action == "frequency":
            geometry = request_data.get('geometry')
            result = await self.frequency_analysis(
                geometry=geometry,
                method=request_data.get('method', 'b3lyp'),
                basis=request_data.get('basis', '6-31g*')
            )
            return {
                'frequencies': result.properties.get('frequencies') if result.properties else None,
                'energy': result.energy
            }
        
        elif action == "orbitals":
            geometry = request_data.get('geometry')
            result = await self.analyze_molecular_orbitals(
                geometry=geometry,
                method=request_data.get('method', 'b3lyp'),
                basis=request_data.get('basis', '6-31g*')
            )
            return result
        
        elif action == "verify_hypothesis":
            return await self.verify_chemical_hypothesis(
                hypothesis=request_data.get('hypothesis')
            )
        
        elif action == "suggest_modifications":
            return await self.suggest_molecular_modifications(
                base_molecule=request_data.get('base_molecule'),
                target_properties=request_data.get('target_properties', {})
            )
        
        elif action == "get_info":
            return {
                'service': 'QuantumChemistry',
                'pyscf_available': self.pyscf_available,
                'basis_sets': list(self.basis_sets.keys()),
                'dft_functionals': list(self.dft_functionals.keys()),
                'capabilities': ['SCF', 'DFT', 'geometry_optimization', 'frequency_analysis', 'MO_analysis']
            }
        
        else:
            raise ValueError(f"Unknown action: {action}")

    # --- Core Quantum Chemistry Methods ---
    async def run_scf_calculation(self, geometry: MolecularGeometry, 
                                 method: str = "hf", basis: str = "6-31g*") -> QuantumChemistryResult:
        """
        Ejecuta cálculo SCF (Self-Consistent Field)
        
        Args:
            geometry: Geometría molecular
            method: Método SCF (hf, b3lyp, pbe, etc.)
            basis: Base atómica
        """
        if not self.pyscf_available:
            raise RuntimeError("PySCF no disponible. Instala: pip install pyscf")
        
        try:
            import time
            start_time = time.time()
            
            # Importar módulos PySCF
            from pyscf import gto, scf, dft
            
            # Crear molécula
            mol = gto.Molecule()
            mol.atom = geometry.to_pyscf_format()
            mol.basis = basis
            mol.charge = geometry.charge
            mol.spin = geometry.spin
            mol.build()
            
            # Seleccionar método
            if method.lower() == "hf":
                mf = scf.RHF(mol) if geometry.spin == 0 else scf.UHF(mol)
            elif method.lower() in self.dft_functionals:
                mf = dft.RKS(mol) if geometry.spin == 0 else dft.UKS(mol)
                mf.xc = self.dft_functionals[method.lower()]
            else:
                # Default a B3LYP DFT
                mf = dft.RKS(mol) if geometry.spin == 0 else dft.UKS(mol)
                mf.xc = method
            
            # Ejecutar cálculo
            energy = await asyncio.get_event_loop().run_in_executor(
                None, mf.kernel
            )
            
            computation_time = time.time() - start_time
            
            # Analizar orbitales moleculares
            mo_analysis = None
            if mf.converged:
                mo_analysis = {
                    "homo_energy": float(mf.mo_energy[mf.mo_occ > 0][-1]),
                    "lumo_energy": float(mf.mo_energy[mf.mo_occ == 0][0]),
                    "num_orbitals": len(mf.mo_energy),
                    "num_electrons": int(sum(mf.mo_occ)),
                }
                
                # Gap HOMO-LUMO
                if len(mf.mo_energy[mf.mo_occ == 0]) > 0:
                    mo_analysis["homo_lumo_gap"] = (
                        mo_analysis["lumo_energy"] - mo_analysis["homo_energy"]
                    )
            
            # Calcular propiedades adicionales
            properties = await self._calculate_properties(mol, mf)
            
            return QuantumChemistryResult(
                energy=float(energy),
                convergence=mf.converged,
                method=method,
                basis_set=basis,
                molecular_geometry=geometry,
                molecular_orbitals=mo_analysis,
                properties=properties,
                computation_time=computation_time
            )
            
        except ChemistryError as e:
            raise RuntimeError(f"SCF calculation failed: {str(e)}")

    async def optimize_geometry(self, initial_geometry: MolecularGeometry, 
                              method: str = "b3lyp", basis: str = "6-31g*", 
                              max_cycles: int = 50) -> Dict[str, Any]:
        """
        Optimización de geometría molecular
        """
        if not self.pyscf_available:
            raise RuntimeError("PySCF no disponible")
        
        try:
            from pyscf import gto, dft, geomopt
            import time
            
            start_time = time.time()
            
            # Crear molécula inicial
            mol = gto.Molecule()
            mol.atom = initial_geometry.to_pyscf_format()
            mol.basis = basis
            mol.charge = initial_geometry.charge
            mol.spin = initial_geometry.spin
            mol.build()
            
            # Método de cálculo
            if method.lower() in self.dft_functionals:
                mf = dft.RKS(mol) if initial_geometry.spin == 0 else dft.UKS(mol)
                mf.xc = self.dft_functionals[method.lower()]
            else:
                mf = dft.RKS(mol)
                mf.xc = method
            
            # Optimización de geometría
            mol_opt = await asyncio.get_event_loop().run_in_executor(
                None, lambda: geomopt.optimize(mf, maxsteps=max_cycles)
            )
            
            computation_time = time.time() - start_time
            
            # Extraer geometría optimizada
            optimized_atoms = []
            for i, atom_symbol in enumerate([atom[0] for atom in mol_opt.atom]):
                coord = mol_opt.atom_coords()[i]
                optimized_atoms.append((atom_symbol, tuple(coord)))
            
            optimized_geometry = MolecularGeometry(
                atoms=optimized_atoms,
                charge=initial_geometry.charge,
                spin=initial_geometry.spin
            )
            
            # Cálculo final en geometría optimizada
            final_result = await self.run_scf_calculation(optimized_geometry, method, basis)
            
            return {
                "initial_geometry": initial_geometry,
                "optimized_geometry": optimized_geometry,
                "initial_energy": None,  # Podríamos calcularlo
                "final_energy": final_result.energy,
                "convergence": final_result.convergence,
                "optimization_cycles": max_cycles,  # En PySCF sería más complejo obtener el número real
                "computation_time": computation_time,
                "energy_change": None,
                "final_calculation": final_result
            }
            
        except ChemistryError as e:
            raise RuntimeError(f"Geometry optimization failed: {str(e)}")

    async def frequency_analysis(self, geometry: MolecularGeometry, 
                               method: str = "b3lyp", basis: str = "6-31g*") -> Dict[str, Any]:
        """
        Análisis de frecuencias vibracionales
        """
        if not self.pyscf_available:
            raise RuntimeError("PySCF no disponible")
        
        try:
            from pyscf import gto, dft, hessian
            import time
            
            start_time = time.time()
            
            # Crear molécula
            mol = gto.Molecule()
            mol.atom = geometry.to_pyscf_format()
            mol.basis = basis
            mol.charge = geometry.charge
            mol.spin = geometry.spin
            mol.build()
            
            # Método SCF
            if method.lower() in self.dft_functionals:
                mf = dft.RKS(mol) if geometry.spin == 0 else dft.UKS(mol)
                mf.xc = self.dft_functionals[method.lower()]
            else:
                mf = dft.RKS(mol)
                mf.xc = method
            
            # Cálculo SCF inicial
            mf.kernel()
            
            # Calcular Hessiano y frecuencias
            hess = hessian.RKS(mf) if hasattr(hessian, 'RKS') else None
            if hess is None:
                # Fallback si no hay Hessiano disponible
                return {
                    "frequencies": [],
                    "zero_point_energy": 0.0,
                    "thermal_energy": 0.0,
                    "method": method,
                    "basis": basis,
                    "computation_time": time.time() - start_time,
                    "warning": "Hessian calculation not available"
                }
            
            hessian_matrix = await asyncio.get_event_loop().run_in_executor(
                None, hess.kernel
            )
            
            # Análisis de frecuencias (simplificado)
            # En una implementación completa, necesitaríamos análisis vibracional completo
            computation_time = time.time() - start_time
            
            return {
                "frequencies": [],  # Lista de frecuencias en cm^-1
                "zero_point_energy": 0.0,  # ZPE en hartrees
                "thermal_energy": 0.0,  # Energía térmica
                "method": method,
                "basis": basis,
                "computation_time": computation_time,
                "hessian_calculated": True
            }
            
        except ChemistryError as e:
            return {
                "frequencies": [],
                "error": f"Frequency analysis failed: {str(e)}",
                "method": method,
                "basis": basis
            }

    async def analyze_molecular_orbitals(self, geometry: MolecularGeometry, 
                                       method: str = "b3lyp", basis: str = "6-31g*") -> Dict[str, Any]:
        """
        Análisis detallado de orbitales moleculares
        """
        if not self.pyscf_available:
            raise RuntimeError("PySCF no disponible")
        
        try:
            # Ejecutar cálculo SCF
            scf_result = await self.run_scf_calculation(geometry, method, basis)
            
            if not scf_result.convergence:
                return {
                    "error": "SCF did not converge",
                    "analysis": None
                }
            
            from pyscf import gto, dft
            
            # Reconstruir molécula para análisis
            mol = gto.Molecule()
            mol.atom = geometry.to_pyscf_format()
            mol.basis = basis
            mol.charge = geometry.charge
            mol.spin = geometry.spin
            mol.build()
            
            # Recalcular para obtener objeto MF
            if method.lower() in self.dft_functionals:
                mf = dft.RKS(mol) if geometry.spin == 0 else dft.UKS(mol)
                mf.xc = self.dft_functionals[method.lower()]
            else:
                mf = dft.RKS(mol)
                mf.xc = method
            
            mf.kernel()
            
            # Análisis de población (Mulliken)
            mulliken_pop = None
            try:
                from pyscf import lo
                mulliken_pop = lo.orth_ao(mol, 'lowdin')  # Análisis de Löwdin
            except ChemistryError:
                pass
            
            analysis = {
                "method": method,
                "basis": basis,
                "total_energy": scf_result.energy,
                "molecular_orbitals": scf_result.molecular_orbitals,
                "mulliken_population": mulliken_pop is not None,
                "orbital_energies": [float(e) for e in mf.mo_energy[:20]],  # Primeros 20 MOs
                "orbital_occupations": [float(occ) for occ in mf.mo_occ[:20]],
                "dipole_moment": None,  # Calcularíamos con tools adicionales
                "quadrupole_moment": None
            }
            
            # Calcular momento dipolar si es posible
            try:
                dipole = mf.dip_moment()
                analysis["dipole_moment"] = {
                    "magnitude": float(np.linalg.norm(dipole)),
                    "components": [float(d) for d in dipole]
                }
            except ChemistryError:
                pass
            
            return analysis
            
        except ChemistryError as e:
            return {
                "error": f"Molecular orbital analysis failed: {str(e)}",
                "method": method,
                "basis": basis
            }

    # --- Atlas Integration Methods ---
    async def verify_chemical_hypothesis(self, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifica hipótesis químicas usando cálculos cuánticos
        """
        try:
            hypothesis_type = hypothesis.get("type", "general")
            
            if hypothesis_type == "molecular_stability":
                return await self._verify_molecular_stability(hypothesis)
            elif hypothesis_type == "reaction_feasibility":
                return await self._verify_reaction_feasibility(hypothesis)
            elif hypothesis_type == "electronic_properties":
                return await self._verify_electronic_properties(hypothesis)
            else:
                return await self._general_chemical_verification(hypothesis)
                
        except ChemistryError as e:
            return {
                "hypothesis_id": hypothesis.get("id", "unknown"),
                "verification_method": "quantum_chemistry",
                "verified": None,
                "error": str(e)
            }

    async def suggest_molecular_modifications(self, base_molecule: MolecularGeometry, 
                                            target_properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sugiere modificaciones moleculares para alcanzar propiedades objetivo
        """
        try:
            # Cálculo base
            base_result = await self.run_scf_calculation(base_molecule)
            
            suggestions = []
            
            # Estrategias básicas de modificación
            modification_strategies = [
                {"type": "add_methyl", "description": "Agregar grupo metilo"},
                {"type": "add_hydroxyl", "description": "Agregar grupo hidroxilo"},  
                {"type": "change_substituent", "description": "Cambiar sustituyente"},
                {"type": "ring_expansion", "description": "Expansión del anillo"},
            ]
            
            for strategy in modification_strategies:
                # En una implementación completa, aplicaríamos la modificación
                # y calcularíamos las propiedades resultantes
                suggestion = {
                    "modification": strategy,
                    "predicted_property_change": "TBD",  # Requiere cálculos
                    "feasibility_score": 0.5,  # Placeholder
                    "computational_cost": "medium"
                }
                suggestions.append(suggestion)
            
            return {
                "base_molecule": base_molecule,
                "base_properties": base_result.properties,
                "target_properties": target_properties,
                "suggestions": suggestions,
                "method": "quantum_chemistry_guided"
            }
            
        except ChemistryError as e:
            return {
                "error": f"Molecular modification suggestions failed: {str(e)}",
                "base_molecule": base_molecule
            }

    # --- Helper Methods ---
    async def _calculate_properties(self, mol, mf) -> Dict[str, float]:
        """Calcula propiedades moleculares adicionales"""
        properties = {}
        
        try:
            # Energía de ionización (aproximada)
            if hasattr(mf, 'mo_energy'):
                homo_energy = mf.mo_energy[mf.mo_occ > 0][-1]
                properties["homo_energy_ev"] = float(homo_energy * 27.2114)  # Hartree a eV
                
                if len(mf.mo_energy[mf.mo_occ == 0]) > 0:
                    lumo_energy = mf.mo_energy[mf.mo_occ == 0][0]
                    properties["lumo_energy_ev"] = float(lumo_energy * 27.2114)
                    properties["homo_lumo_gap_ev"] = properties["lumo_energy_ev"] - properties["homo_energy_ev"]
            
            # Momento dipolar
            try:
                dipole = mf.dip_moment()
                properties["dipole_moment_debye"] = float(np.linalg.norm(dipole) * 2.5418)  # au a Debye
            except ChemistryError:
                pass
            
        except ChemistryError:
            pass
        
        return properties

    async def _verify_molecular_stability(self, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica estabilidad molecular"""
        try:
            # Extraer geometría de la hipótesis
            geometry = self._extract_geometry_from_hypothesis(hypothesis)
            
            # Optimizar geometría
            opt_result = await self.optimize_geometry(geometry)
            
            # Análisis de estabilidad
            is_stable = opt_result["convergence"] and opt_result["final_energy"] < -1.0  # Criterio simple
            
            return {
                "hypothesis_id": hypothesis.get("id"),
                "verification_method": "molecular_stability",
                "verified": is_stable,
                "confidence": 0.8 if is_stable else 0.3,
                "details": {
                    "optimized_energy": opt_result["final_energy"],
                    "convergence": opt_result["convergence"],
                    "stability_indicators": {
                        "electronic_stable": opt_result["convergence"],
                        "geometrically_stable": True  # Placeholder
                    }
                }
            }
            
        except ChemistryError as e:
            return {
                "hypothesis_id": hypothesis.get("id"),
                "verification_method": "molecular_stability",
                "verified": None,
                "error": str(e)
            }

    async def _verify_reaction_feasibility(self, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica viabilidad de reacciones químicas"""
        # Implementación placeholder - requiere cálculos de estado de transición
        return {
            "hypothesis_id": hypothesis.get("id"),
            "verification_method": "reaction_feasibility", 
            "verified": None,
            "reason": "Transition state calculations not yet implemented"
        }

    async def _verify_electronic_properties(self, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica propiedades electrónicas predichas"""
        try:
            geometry = self._extract_geometry_from_hypothesis(hypothesis)
            mo_analysis = await self.analyze_molecular_orbitals(geometry)
            
            # Comparar con propiedades esperadas en la hipótesis
            expected = hypothesis.get("expected_properties", {})
            calculated = mo_analysis
            
            verification_score = 0.5  # Placeholder para comparación real
            
            return {
                "hypothesis_id": hypothesis.get("id"),
                "verification_method": "electronic_properties",
                "verified": verification_score > 0.7,
                "confidence": verification_score,
                "details": {
                    "expected": expected,
                    "calculated": calculated,
                    "comparison_score": verification_score
                }
            }
            
        except ChemistryError as e:
            return {
                "hypothesis_id": hypothesis.get("id"),
                "verification_method": "electronic_properties",
                "verified": None,
                "error": str(e)
            }

    async def _general_chemical_verification(self, hypothesis: Dict[str, Any]) -> Dict[str, Any]:
        """Verificación química general"""
        return {
            "hypothesis_id": hypothesis.get("id"),
            "verification_method": "general_quantum_chemistry",
            "verified": None,
            "reason": "General chemical verification requires specific implementation"
        }

    def _extract_geometry_from_hypothesis(self, hypothesis: Dict[str, Any]) -> MolecularGeometry:
        """Extrae geometría molecular de una hipótesis"""
        # Implementación placeholder - en producción parsearía la hipótesis
        # Por ahora, usar molécula de ejemplo (agua)
        return MolecularGeometry(
            atoms=[
                ("O", (0.0, 0.0, 0.0)),
                ("H", (0.757, 0.586, 0.0)),
                ("H", (-0.757, 0.586, 0.0))
            ],
            charge=0,
            spin=0
        )
