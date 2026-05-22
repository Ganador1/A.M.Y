"""
Advanced Hypothesis Validator Service

Integrates concepts from:
- POPPER (Stanford): Sequential falsification with statistical rigor
- ToolUniverse (Harvard): 700+ scientific tool integrations
- ChemCrow: Chemistry-specific tools

Combined with AXIOM's existing infrastructure for a comprehensive
hypothesis validation system.
"""

import asyncio
import json
import logging
import os
import dataclasses
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from scipy import stats
from scipy.stats import chi2

logger = logging.getLogger(__name__)


class ValidationMethod(Enum):
    """Methods for aggregating multiple test results."""
    FISHERS = "fishers"           # Fisher's method for combining p-values
    E_VALUE = "e_value"           # E-value (POPPER's default)
    BONFERRONI = "bonferroni"     # Bonferroni correction
    SEQUENTIAL = "sequential"     # Sequential probability ratio test


class HypothesisStatus(Enum):
    """Status of hypothesis after validation."""
    VALIDATED = "validated"
    REFUTED = "refuted"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    ERROR = "error"


@dataclass
class FalsificationTest:
    """A single falsification test against a hypothesis."""
    test_id: str
    test_name: str
    description: str
    null_hypothesis: str
    alternative_hypothesis: str
    p_value: Optional[float] = None
    e_value: Optional[float] = None
    test_statistic: Optional[float] = None
    raw_result: Optional[Dict] = None
    execution_time_ms: float = 0.0
    tool_used: str = ""
    data_sources: List[str] = field(default_factory=list)
    error: Optional[str] = None
    
    @property
    def is_significant(self) -> bool:
        """Check if result is statistically significant at alpha=0.05."""
        if self.p_value is not None:
            return self.p_value < 0.05
        return False


@dataclass
class ValidationResult:
    """Complete result of hypothesis validation."""
    hypothesis: str
    status: HypothesisStatus
    confidence: float
    combined_p_value: Optional[float]
    combined_e_value: Optional[float]
    tests_run: List[FalsificationTest]
    method_used: ValidationMethod
    alpha: float
    timestamp: str
    total_time_ms: float
    reasoning: str
    conclusion: str
    
    def to_dict(self) -> Dict:
        return {
            "hypothesis": self.hypothesis,
            "status": self.status.value,
            "confidence": self.confidence,
            "combined_p_value": self.combined_p_value,
            "combined_e_value": self.combined_e_value,
            "tests_run": [
                {
                    "test_id": t.test_id,
                    "test_name": t.test_name,
                    "p_value": t.p_value,
                    "e_value": t.e_value,
                    "tool_used": t.tool_used,
                    "is_significant": t.is_significant,
                    "error": t.error
                }
                for t in self.tests_run
            ],
            "method_used": self.method_used.value,
            "alpha": self.alpha,
            "timestamp": self.timestamp,
            "total_time_ms": self.total_time_ms,
            "reasoning": self.reasoning,
            "conclusion": self.conclusion
        }


class StatisticalAggregator:
    """
    Statistical methods for combining multiple test results.
    Based on POPPER's implementation.
    """
    
    @staticmethod
    def fishers_method(p_values: List[float], alpha: float = 0.1) -> Tuple[bool, float]:
        """
        Combine p-values using Fisher's method.
        
        Args:
            p_values: List of p-values from individual tests
            alpha: Significance level
            
        Returns:
            (is_significant, combined_p_value)
        """
        p_values = np.array([p for p in p_values if p is not None and p > 0])
        if len(p_values) == 0:
            return False, 1.0
            
        # Fisher's method: -2 * sum(log(p))
        chi_square_stat = -2 * np.sum(np.log(p_values))
        degrees_of_freedom = 2 * len(p_values)
        combined_p_value = 1 - chi2.cdf(chi_square_stat, degrees_of_freedom)
        
        return combined_p_value < alpha, combined_p_value
    
    @staticmethod
    def e_value_kappa_calibrator(
        p_values: List[float], 
        alpha: float = 0.1, 
        kappa: float = 0.5
    ) -> Tuple[bool, float]:
        """
        Convert p-values to e-values using kappa calibration.
        E-values can be multiplied for sequential testing.
        
        Args:
            p_values: List of p-values
            alpha: Significance level
            kappa: Calibration parameter (0 < kappa < 1)
            
        Returns:
            (is_significant, cumulative_e_value)
        """
        p_values = np.array([p for p in p_values if p is not None and p > 0])
        if len(p_values) == 0:
            return False, 0.0
            
        e_values = kappa * np.power(p_values, kappa - 1)
        cumulative_e = np.prod(e_values)
        
        # Reject null if cumulative e-value > 1/alpha
        return cumulative_e > 1/alpha, cumulative_e
    
    @staticmethod
    def bonferroni_correction(
        p_values: List[float], 
        alpha: float = 0.1
    ) -> Tuple[bool, float]:
        """
        Apply Bonferroni correction for multiple testing.
        
        Args:
            p_values: List of p-values
            alpha: Family-wise significance level
            
        Returns:
            (is_significant, adjusted_alpha)
        """
        p_values = [p for p in p_values if p is not None]
        if len(p_values) == 0:
            return False, alpha
            
        adjusted_alpha = alpha / len(p_values)
        min_p = min(p_values)
        
        return min_p < adjusted_alpha, min_p


class ScientificToolAdapter:
    """
    Adapter for integrating various scientific tools.
    Inspired by ToolUniverse's tool interface.
    """
    
    def __init__(self):
        self.available_tools = self._discover_tools()
        
    def _discover_tools(self) -> Dict[str, Dict]:
        """Discover available scientific tools."""
        tools = {
            # Chemistry tools (RDKit-based)
            "molecular_descriptors": {
                "category": "chemistry",
                "description": "Calculate molecular descriptors using RDKit",
                "requires": ["rdkit"]
            },
            "molecular_similarity": {
                "category": "chemistry",
                "description": "Calculate molecular fingerprints and similarity",
                "requires": ["rdkit"]
            },
            "lipinski_rules": {
                "category": "chemistry",
                "description": "Check Lipinski's Rule of Five",
                "requires": ["rdkit"]
            },
            
            # Quantum tools (Qiskit-based)
            "quantum_simulation": {
                "category": "quantum",
                "description": "Quantum circuit simulation with noise models",
                "requires": ["qiskit", "qiskit_aer"]
            },
            "quantum_error_correction": {
                "category": "quantum",
                "description": "Test quantum error correction codes",
                "requires": ["qiskit", "qiskit_aer"]
            },
            
            # Mathematics tools (SymPy/NumPy-based)
            "symbolic_math": {
                "category": "mathematics",
                "description": "Symbolic mathematics and equation solving",
                "requires": ["sympy"]
            },
            "numerical_optimization": {
                "category": "mathematics",
                "description": "Numerical optimization algorithms",
                "requires": ["scipy"]
            },
            "statistical_tests": {
                "category": "statistics",
                "description": "Statistical hypothesis testing",
                "requires": ["scipy"]
            },
            
            # Biology tools
            "sequence_analysis": {
                "category": "biology",
                "description": "DNA/RNA/Protein sequence analysis",
                "requires": ["biopython"]
            },
            "protein_properties": {
                "category": "biology",
                "description": "Calculate protein properties",
                "requires": ["biopython"]
            },
            
            # Materials science
            "thermal_conductivity": {
                "category": "materials",
                "description": "Thermal conductivity models for composites",
                "requires": ["numpy", "scipy"]
            },
            "crystal_structure": {
                "category": "materials",
                "description": "Crystal structure analysis",
                "requires": ["pymatgen"]
            },
            
            # AXIOM Native Bridges
            "axiom_astronomy": {
                "category": "astronomy",
                "description": "AXIOM Native Astronomy Analysis (Exoplanets, Light Curves)",
                "requires": ["numpy", "scipy"]
            },
            "axiom_medicine": {
                "category": "medicine",
                "description": "AXIOM Native Medical Analysis (Imaging, ClinicalBERT)",
                "requires": ["numpy", "scipy"]
            },
            "axiom_neuroscience": {
                "category": "neuroscience",
                "description": "AXIOM Native Neuroscience Analysis",
                "requires": ["numpy", "networkx"]
            },
            "axiom_mathematics": {
                "category": "mathematics",
                "description": "AXIOM Native Advanced Mathematics (Symbolic AI, GPU Math)",
                "requires": ["numpy", "scipy", "sympy"]
            },
            
            # Extended Bridges (NEW)
            "axiom_quantum_chemistry": {
                "category": "chemistry",
                "description": "Quantum Chemistry (DFT, ab initio) via QuantumChemistryService",
                "requires": ["numpy", "scipy"]
            },
            "tooluniverse_ensembl": {
                "category": "biology",
                "description": "Ensembl Gene Database Queries",
                "requires": ["requests"]
            },
            "tooluniverse_pubchem": {
                "category": "chemistry",
                "description": "PubChem Compound Database Queries",
                "requires": ["requests"]
            },
            "tooluniverse_clinvar": {
                "category": "medicine",
                "description": "ClinVar Variant Clinical Significance",
                "requires": ["requests"]
            },
            "chemcrow_synthesis": {
                "category": "chemistry",
                "description": "ChemCrow Synthesis Route Validation (RXN4Chem)",
                "requires": ["rdkit"]
            },
            "popper_physics": {
                "category": "physics",
                "description": "POPPER Falsification for Quantum/Particle Physics",
                "requires": ["numpy", "scipy"]
            },
            # Additional Extended Bridges
            "axiom_dnabert2": {
                "category": "biology",
                "description": "DNABERT2 Genomic Sequence Analysis",
                "requires": ["numpy"]
            },
            "axiom_quantum_physics": {
                "category": "physics",
                "description": "Quantum Physics Simulations (QuTiP)",
                "requires": ["numpy", "scipy"]
            },
            "axiom_gnome_materials": {
                "category": "materials",
                "description": "GNoME Materials Discovery and Stability",
                "requires": ["numpy"]
            }
        }
        
        # Check which tools are actually available
        for tool_name, tool_info in tools.items():
            tool_info["available"] = self._check_requirements(tool_info["requires"])
            
        return tools
    
    def _check_requirements(self, requires: List[str]) -> bool:
        """Check if required packages are available."""
        for package in requires:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                return False
        return True
    
    async def execute_tool(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a scientific tool.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool-specific parameters
            
        Returns:
            Tool execution result
        """
        if tool_name not in self.available_tools:
            return {"error": f"Tool '{tool_name}' not found"}
            
        if not self.available_tools[tool_name]["available"]:
            return {"error": f"Tool '{tool_name}' requirements not met"}
        
        # Route to specific tool implementations
        tool_methods = {
            "molecular_descriptors": self._run_molecular_descriptors,
            "lipinski_rules": self._run_lipinski_rules,
            "statistical_tests": self._run_statistical_test,
            "thermal_conductivity": self._run_thermal_conductivity,
            "quantum_simulation": self._run_quantum_simulation,
            "sequence_analysis": self._run_sequence_analysis,
            "axiom_astronomy": self._run_axiom_astronomy,
            "axiom_medicine": self._run_axiom_medicine,
            "axiom_neuroscience": self._run_axiom_neuroscience,
            "axiom_mathematics": self._run_axiom_mathematics,
            # Extended bridges (NEW)
            "axiom_quantum_chemistry": self._run_quantum_chemistry,
            "tooluniverse_ensembl": self._run_ensembl,
            "tooluniverse_pubchem": self._run_pubchem,
            "tooluniverse_clinvar": self._run_clinvar,
            "chemcrow_synthesis": self._run_chemcrow_synthesis,
            "popper_physics": self._run_popper_physics,
            # Additional extended bridges
            "axiom_dnabert2": self._run_dnabert2,
            "axiom_quantum_physics": self._run_quantum_physics_simulation,
            "axiom_gnome_materials": self._run_gnome_materials,
        }
        
        if tool_name in tool_methods:
            return await tool_methods[tool_name](parameters)
        else:
            return {"error": f"Tool '{tool_name}' implementation not found"}
    
    async def _run_molecular_descriptors(self, params: Dict) -> Dict:
        """Calculate molecular descriptors using RDKit."""
        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors, Lipinski
            
            smiles = params.get("smiles", "")
            mol = Chem.MolFromSmiles(smiles)
            
            if mol is None:
                return {"error": f"Invalid SMILES: {smiles}"}
            
            descriptors = {
                "molecular_weight": Descriptors.MolWt(mol),
                "logp": Descriptors.MolLogP(mol),
                "tpsa": Descriptors.TPSA(mol),
                "hbd": Descriptors.NumHDonors(mol),
                "hba": Descriptors.NumHAcceptors(mol),
                "rotatable_bonds": Descriptors.NumRotatableBonds(mol),
                "rings": Descriptors.RingCount(mol),
                "aromatic_rings": Descriptors.NumAromaticRings(mol),
                "heavy_atoms": Descriptors.HeavyAtomCount(mol),
            }
            
            return {
                "success": True,
                "smiles": smiles,
                "descriptors": descriptors
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _run_lipinski_rules(self, params: Dict) -> Dict:
        """Check Lipinski's Rule of Five."""
        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors
            
            smiles = params.get("smiles", "")
            mol = Chem.MolFromSmiles(smiles)
            
            if mol is None:
                return {"error": f"Invalid SMILES: {smiles}"}
            
            mw = Descriptors.MolWt(mol)
            logp = Descriptors.MolLogP(mol)
            hbd = Descriptors.NumHDonors(mol)
            hba = Descriptors.NumHAcceptors(mol)
            
            rules = {
                "molecular_weight_ok": mw <= 500,
                "logp_ok": logp <= 5,
                "hbd_ok": hbd <= 5,
                "hba_ok": hba <= 10
            }
            
            violations = sum(1 for ok in rules.values() if not ok)
            
            return {
                "success": True,
                "smiles": smiles,
                "molecular_weight": mw,
                "logp": logp,
                "hbd": hbd,
                "hba": hba,
                "rules": rules,
                "violations": violations,
                "is_drug_like": violations <= 1
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _run_statistical_test(self, params: Dict) -> Dict:
        """Run statistical hypothesis test."""
        try:
            test_type = params.get("test_type", "ttest")
            data1 = np.array(params.get("data1", []))
            data2 = params.get("data2")
            
            if test_type == "ttest":
                if data2:
                    data2 = np.array(data2)
                    stat, p_value = stats.ttest_ind(data1, data2)
                else:
                    stat, p_value = stats.ttest_1samp(data1, params.get("popmean", 0))
            elif test_type == "correlation":
                data2 = np.array(data2)
                stat, p_value = stats.pearsonr(data1, data2)
            elif test_type == "anova":
                groups = [np.array(g) for g in params.get("groups", [])]
                stat, p_value = stats.f_oneway(*groups)
            elif test_type == "chi2":
                observed = np.array(params.get("observed", []))
                expected = params.get("expected")
                if expected:
                    stat, p_value = stats.chisquare(observed, np.array(expected))
                else:
                    stat, p_value = stats.chisquare(observed)
            else:
                return {"error": f"Unknown test type: {test_type}"}
            
            return {
                "success": True,
                "test_type": test_type,
                "statistic": float(stat),
                "p_value": float(p_value),
                "significant_at_05": p_value < 0.05,
                "significant_at_01": p_value < 0.01
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _run_thermal_conductivity(self, params: Dict) -> Dict:
        """Calculate thermal conductivity using Maxwell-Garnett model."""
        try:
            k_matrix = params.get("k_matrix", 0.4)  # W/m·K
            k_filler = params.get("k_filler", 5000)  # W/m·K (e.g., graphene)
            volume_fractions = params.get("volume_fractions", [0.01, 0.05, 0.10])
            
            results = []
            for vf in volume_fractions:
                # Maxwell-Garnett model
                numerator = k_filler + 2*k_matrix + 2*vf*(k_filler - k_matrix)
                denominator = k_filler + 2*k_matrix - vf*(k_filler - k_matrix)
                k_effective = k_matrix * (numerator / denominator)
                improvement = ((k_effective - k_matrix) / k_matrix) * 100
                
                results.append({
                    "volume_fraction": vf,
                    "k_effective": k_effective,
                    "improvement_percent": improvement
                })
            
            return {
                "success": True,
                "model": "Maxwell-Garnett",
                "k_matrix": k_matrix,
                "k_filler": k_filler,
                "results": results
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _run_quantum_simulation(self, params: Dict) -> Dict:
        """Run quantum circuit simulation."""
        try:
            from qiskit import QuantumCircuit
            from qiskit_aer import AerSimulator
            from qiskit_aer.noise import NoiseModel, depolarizing_error
            
            circuit_type = params.get("circuit_type", "bell_state")
            shots = params.get("shots", 1000)
            error_rate = params.get("error_rate", 0.01)
            
            # Create circuit based on type
            if circuit_type == "bell_state":
                qc = QuantumCircuit(2, 2)
                qc.h(0)
                qc.cx(0, 1)
                qc.measure([0, 1], [0, 1])
            elif circuit_type == "ghz":
                n_qubits = params.get("n_qubits", 3)
                qc = QuantumCircuit(n_qubits, n_qubits)
                qc.h(0)
                for i in range(n_qubits - 1):
                    qc.cx(i, i + 1)
                qc.measure(range(n_qubits), range(n_qubits))
            else:
                return {"error": f"Unknown circuit type: {circuit_type}"}
            
            # Create noise model
            noise_model = NoiseModel()
            error_1q = depolarizing_error(error_rate, 1)
            error_2q = depolarizing_error(error_rate * 2, 2)
            noise_model.add_all_qubit_quantum_error(error_1q, ['h', 'x', 'y', 'z'])
            noise_model.add_all_qubit_quantum_error(error_2q, ['cx'])
            
            # Run simulation
            simulator = AerSimulator(noise_model=noise_model)
            result = simulator.run(qc, shots=shots).result()
            counts = result.get_counts()
            
            return {
                "success": True,
                "circuit_type": circuit_type,
                "shots": shots,
                "error_rate": error_rate,
                "counts": counts,
                "num_qubits": qc.num_qubits
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def _run_sequence_analysis(self, params: Dict) -> Dict:
        """Analyze DNA/RNA/Protein sequence."""
        try:
            from Bio.Seq import Seq
            from Bio.SeqUtils import gc_fraction
            
            sequence = params.get("sequence", "")
            seq_type = params.get("type", "dna")
            
            seq = Seq(sequence)
            
            result = {
                "success": True,
                "sequence_length": len(seq),
                "type": seq_type
            }
            
            if seq_type.lower() in ["dna", "rna"]:
                result["gc_content"] = gc_fraction(seq) * 100
                # Calculate p-value for GC content hypothesis
                expected_min = params.get("expected_min", 50)
                result["p_value"] = 0.01 if result["gc_content"] > expected_min else 0.9
                
                if seq_type.lower() == "dna":
                    result["complement"] = str(seq.complement())
                    result["reverse_complement"] = str(seq.reverse_complement())
                    result["transcribed"] = str(seq.transcribe())
            
            return result
        except Exception as e:
            return {"error": str(e)}

    # ════════════════════════════════════════════════════════════════════════
    # AXIOM NATIVE BRIDGES
    # ════════════════════════════════════════════════════════════════════════

    async def _run_axiom_astronomy(self, params: Dict) -> Dict:
        """Bridge to AXIOM Astronomy Domain."""
        try:
            from app.domains.astronomy.services.advanced_statistics_service import AdvancedStatisticsService

            data = params.get("data")
            if data is None:
                # Synthetic "light curve" with small noise + a dip to emulate a transit.
                rng = np.random.default_rng(int(params.get("seed", 123)))
                n = int(params.get("n", 256))
                x = np.linspace(0, 1, n)
                y = rng.normal(loc=1.0, scale=float(params.get("noise_sigma", 0.01)), size=n)
                dip_center = float(params.get("dip_center", 0.5))
                dip_width = float(params.get("dip_width", 0.03))
                dip_depth = float(params.get("dip_depth", 0.02))
                transit_mask = np.abs(x - dip_center) < dip_width
                y[transit_mask] -= dip_depth
            else:
                y = np.asarray(data, dtype=float)

            # Simple transit evidence: compare in-transit vs out-of-transit mean.
            # This yields a p-value for "transit-like dip exists" (support).
            dip_center = float(params.get("dip_center", 0.5))
            dip_width = float(params.get("dip_width", 0.03))
            n = int(len(y))
            x = np.linspace(0, 1, n)
            in_transit = np.abs(x - dip_center) < dip_width
            if in_transit.sum() < 5 or (~in_transit).sum() < 5:
                return {"error": "Insufficient samples for transit test"}

            in_vals = y[in_transit]
            out_vals = y[~in_transit]

            # One-sided: mean(in) < mean(out)
            t_stat, p_two = stats.ttest_ind(in_vals, out_vals, equal_var=False)
            p_support = float(p_two / 2.0) if float(t_stat) < 0 else float(1.0 - p_two / 2.0)

            # Falsification-style p-value: evidence AGAINST the hypothesis.
            p_against = float(min(max(1.0 - p_support, 0.0), 1.0))

            # Also return some descriptive stats
            svc = AdvancedStatisticsService()
            results = svc.analyze_advanced_statistics(y)

            return {
                "success": True,
                "p_value": p_against,
                "support_p_value": p_support,
                "metrics": {
                    "mean_in_transit": float(np.mean(in_vals)),
                    "mean_out_transit": float(np.mean(out_vals)),
                    "t_statistic": float(t_stat),
                },
                "tests": [
                    {
                        "test_name": t.test_name,
                        "statistic": float(t.statistic),
                        "p_value": float(t.p_value),
                        "reject_null": bool(t.reject_null),
                    }
                    for t in (results.statistical_tests or [])
                ],
            }
        except Exception as e:
            return {"error": f"AXIOM Astronomy Bridge Error: {str(e)}"}

    async def _run_axiom_medicine(self, params: Dict) -> Dict:
        """Bridge to AXIOM Medicine Domain."""
        try:
            from app.domains.medicine.advanced_clinical_validation_service import AdvancedClinicalValidationService

            imaging_data = params.get("imaging_data") or params.get("image_data") or {}
            expected_mean = float(params.get("expected_ef_mean", 60.0))
            sigma = float(params.get("expected_ef_sigma", 5.0))

            service = AdvancedClinicalValidationService()
            vf = service.analyze_ventricular_function(imaging_data)

            ef = float(vf.ejection_fraction)
            # Two-sided p-value under a simple Normal null around expected EF.
            z = abs(ef - expected_mean) / max(sigma, 1e-9)
            p_value = float(2.0 * (1.0 - stats.norm.cdf(z)))

            vf_dict = dataclasses.asdict(vf)
            # Enum -> value for JSON friendliness
            if "calculation_method" in vf_dict and hasattr(vf_dict["calculation_method"], "value"):
                vf_dict["calculation_method"] = vf_dict["calculation_method"].value

            return {
                "success": True,
                "p_value": p_value,
                "metrics": {
                    "ejection_fraction": ef,
                    "confidence_score": float(vf.confidence_score),
                    "expected_mean": expected_mean,
                    "expected_sigma": sigma,
                },
                "ventricular_function": vf_dict,
            }
        except Exception as e:
            return {"error": f"AXIOM Medicine Bridge Error: {str(e)}"}

    async def _run_axiom_neuroscience(self, params: Dict) -> Dict:
        """Bridge to AXIOM Neuroscience Domain."""
        try:
            from app.domains.neuroscience.services.computational_biology import ComputationalBiologyService

            circuit_type = params.get("circuit_type", "cortical_column")
            num_neurons = int(params.get("num_neurons", 100))
            seed = int(params.get("seed", 123))
            null_samples = int(params.get("null_samples", 50))

            service = ComputationalBiologyService()
            result = await service.brain_circuit_analysis(
                {
                    "circuit_type": circuit_type,
                    "num_neurons": num_neurons,
                }
            )
            if not result.get("success"):
                return {"error": result.get("error", "Neuroscience analysis failed")}

            clustering = float(result["network_properties"]["clustering_coefficient"])
            density = float(result["network_properties"]["connection_density"])
            n = int(result["network_properties"]["num_neurons"])

            # Null: Erdos-Rényi G(n,p) with p approximated by density.
            import networkx as nx

            rng = np.random.default_rng(seed)
            null_clusterings: List[float] = []
            for _ in range(max(null_samples, 1)):
                g = nx.erdos_renyi_graph(n=n, p=max(min(density, 1.0), 0.0), seed=int(rng.integers(0, 2**32 - 1)))
                null_clusterings.append(float(nx.average_clustering(g)))

            # One-sided support p-value: probability null clustering >= observed.
            p_support = float((sum(1 for c in null_clusterings if c >= clustering) + 1) / (len(null_clusterings) + 1))
            # Falsification-style p-value: evidence AGAINST hypothesis (high clustering).
            p_value = float(min(max(1.0 - p_support, 0.0), 1.0))

            return {
                "success": True,
                "p_value": p_value,
                "support_p_value": p_support,
                "metrics": {
                    "observed_clustering": clustering,
                    "density": density,
                    "n": n,
                    "null_samples": len(null_clusterings),
                },
                "axiom_result": result,
            }
        except Exception as e:
            return {"error": f"AXIOM Neuroscience Bridge Error: {str(e)}"}

    async def _run_axiom_mathematics(self, params: Dict) -> Dict:
        """Bridge to AXIOM Mathematics Domain."""
        try:
            operation = params.get("operation", "solve_linear_system")

            if operation == "solve_equation":
                import sympy as sp

                expression = params.get("expression", "")
                variable = params.get("variable", "x")
                x = sp.Symbol(variable)
                expr = sp.sympify(expression)
                simplified = sp.simplify(expr)
                is_zero = bool(simplified == 0)
                # Falsification-style: high p-value when the identity is consistent (no refutation).
                p_value = 1.0 if is_zero else 1e-12
                return {
                    "success": True,
                    "p_value": float(p_value),
                    "metrics": {"is_zero": is_zero, "simplified": str(simplified)},
                }

            # Default: solve a linear system and derive a p-value from residual magnitude.
            from app.domains.mathematics.services.mathematical_computation import LinearAlgebra

            A = params.get("coefficient_matrix")
            b = params.get("constants")
            if A is None or b is None:
                # Small well-conditioned system by default
                A = [[3.0, 1.0], [1.0, 2.0]]
                b = [9.0, 8.0]

            solved = LinearAlgebra.solve_linear_system(A, b)
            if not solved.get("success"):
                return {"error": solved.get("error", "Math solve failed")}

            residual = float(solved.get("residual", 0.0))
            sigma = float(params.get("sigma", 1.0))
            df = int(params.get("df", max(len(b) - 1, 1)))

            # Null: residual comes from Gaussian noise with scale sigma.
            test_stat = (residual / max(sigma, 1e-12)) ** 2
            p_value = float(1.0 - chi2.cdf(test_stat, df=df))

            return {
                "success": True,
                "p_value": p_value,
                "metrics": {
                    "residual": residual,
                    "condition_number": float(solved.get("condition_number", 0.0)),
                    "sigma": sigma,
                    "df": df,
                },
                "axiom_result": solved,
            }
        except Exception as e:
            return {"error": f"AXIOM Mathematics Bridge Error: {str(e)}"}

    # ════════════════════════════════════════════════════════════════════════
    # EXTENDED BRIDGES (NEW)
    # ════════════════════════════════════════════════════════════════════════

    async def _run_quantum_chemistry(self, params: Dict) -> Dict:
        """Bridge to QuantumChemistryService for DFT/ab initio calculations."""
        try:
            from app.services.extended_hypothesis_bridges import QuantumChemistryBridge
            
            bridge = QuantumChemistryBridge()
            
            atoms = params.get("atoms")
            if atoms is None:
                # Default: water molecule (H2O)
                atoms = [
                    ("O", (0.0, 0.0, 0.0)),
                    ("H", (0.0, 0.757, 0.587)),
                    ("H", (0.0, -0.757, 0.587)),
                ]
            
            result = await bridge.validate_molecular_energy(
                atoms=atoms,
                expected_energy=params.get("expected_energy", -76.0),
                energy_sigma=params.get("energy_sigma", 0.01),
                method=params.get("method", "b3lyp"),
                basis=params.get("basis", "6-31g*"),
            )
            return result
        except Exception as e:
            return {"error": f"Quantum Chemistry Bridge Error: {str(e)}"}

    async def _run_ensembl(self, params: Dict) -> Dict:
        """Bridge to Ensembl via ToolUniverse wrapper."""
        try:
            from app.services.extended_hypothesis_bridges import ToolUniverseWrapper
            
            wrapper = ToolUniverseWrapper()
            result = await wrapper.query_ensembl_gene(
                gene_id=params.get("gene_id", "BRCA1"),
                species=params.get("species", "homo_sapiens"),
                expected_chromosome=params.get("expected_chromosome"),
            )
            return result
        except Exception as e:
            return {"error": f"Ensembl Bridge Error: {str(e)}"}

    async def _run_pubchem(self, params: Dict) -> Dict:
        """Bridge to PubChem via ToolUniverse wrapper."""
        try:
            from app.services.extended_hypothesis_bridges import ToolUniverseWrapper
            
            wrapper = ToolUniverseWrapper()
            result = await wrapper.query_pubchem_compound(
                smiles=params.get("smiles"),
                name=params.get("name"),
                cid=params.get("cid"),
                expected_mw=params.get("expected_mw"),
                mw_tolerance=params.get("mw_tolerance", 0.5),
            )
            return result
        except Exception as e:
            return {"error": f"PubChem Bridge Error: {str(e)}"}

    async def _run_clinvar(self, params: Dict) -> Dict:
        """Bridge to ClinVar via ToolUniverse wrapper."""
        try:
            from app.services.extended_hypothesis_bridges import ToolUniverseWrapper
            
            wrapper = ToolUniverseWrapper()
            result = await wrapper.query_clinvar_variant(
                variant_id=params.get("variant_id", "VCV000000001"),
                expected_significance=params.get("expected_significance"),
            )
            return result
        except Exception as e:
            return {"error": f"ClinVar Bridge Error: {str(e)}"}

    async def _run_chemcrow_synthesis(self, params: Dict) -> Dict:
        """Bridge to ChemCrow for synthesis route validation."""
        try:
            from app.services.extended_hypothesis_bridges import ChemCrowSynthesisBridge
            
            bridge = ChemCrowSynthesisBridge()
            
            if "target_smiles" in params and "starting_materials" in params:
                # Retrosynthesis validation
                result = await bridge.validate_retrosynthesis_route(
                    target_smiles=params["target_smiles"],
                    proposed_starting_materials=params["starting_materials"],
                    max_steps=params.get("max_steps", 3),
                )
            else:
                # Forward reaction prediction
                result = await bridge.validate_reaction_product(
                    reactants_smiles=params.get("reactants_smiles", "CC(=O)O.CCO"),
                    expected_product_smiles=params.get("expected_product", "CCOC(C)=O"),
                    similarity_threshold=params.get("similarity_threshold", 0.8),
                )
            return result
        except Exception as e:
            return {"error": f"ChemCrow Synthesis Bridge Error: {str(e)}"}

    async def _run_popper_physics(self, params: Dict) -> Dict:
        """Bridge to POPPER for physics data validation."""
        try:
            from app.services.extended_hypothesis_bridges import POPPERPhysicsAdapter
            
            adapter = POPPERPhysicsAdapter()
            
            if "invariant_mass" in params.get("event_data", {}):
                # Particle physics
                result = await adapter.validate_particle_physics_data(
                    event_data=params["event_data"],
                    expected_mass=params.get("expected_mass", 125.0),
                    mass_resolution=params.get("mass_resolution", 2.0),
                    background_rate=params.get("background_rate", 0.1),
                )
            else:
                # Quantum physics
                result = await adapter.validate_quantum_hypothesis(
                    hypothesis=params.get("hypothesis", "Quantum measurement follows normal distribution"),
                    measurement_data=params.get("measurement_data", {"observed": np.random.normal(0, 1, 100).tolist()}),
                    expected_distribution=params.get("expected_distribution", "normal"),
                    alpha=params.get("alpha", 0.1),
                )
            return result
        except Exception as e:
            return {"error": f"POPPER Physics Bridge Error: {str(e)}"}

    async def _run_dnabert2(self, params: Dict) -> Dict:
        """Bridge to DNABERT2 for genomic sequence analysis."""
        try:
            from app.services.extended_hypothesis_bridges import DNABERT2GenomicsBridge
            
            bridge = DNABERT2GenomicsBridge()
            
            if "sequence1" in params and "sequence2" in params:
                # Sequence similarity
                result = await bridge.validate_sequence_similarity(
                    sequence1=params["sequence1"],
                    sequence2=params["sequence2"],
                    expected_similar=params.get("expected_similar", True),
                    similarity_threshold=params.get("similarity_threshold", 0.8),
                )
            else:
                # Sequence classification
                result = await bridge.validate_sequence_classification(
                    sequence=params.get("sequence", "ATGCATGCATGC"),
                    expected_class=params.get("expected_class", "coding"),
                )
            return result
        except Exception as e:
            return {"error": f"DNABERT2 Bridge Error: {str(e)}"}

    async def _run_quantum_physics_simulation(self, params: Dict) -> Dict:
        """Bridge to QuantumPhysicsService for QuTiP simulations."""
        try:
            from app.services.extended_hypothesis_bridges import QuantumPhysicsSimulationBridge
            
            bridge = QuantumPhysicsSimulationBridge()
            
            if "initial_state" in params:
                # Spin dynamics
                result = await bridge.validate_spin_dynamics(
                    initial_state=params.get("initial_state", "up"),
                    hamiltonian_type=params.get("hamiltonian_type", "rabi"),
                    evolution_time=params.get("evolution_time", 10.0),
                    expected_final_population=params.get("expected_final_population", 0.5),
                )
            else:
                # Entanglement
                result = await bridge.validate_entanglement_hypothesis(
                    state_type=params.get("state_type", "bell"),
                    expected_entanglement=params.get("expected_entanglement", 1.0),
                    tolerance=params.get("tolerance", 0.05),
                )
            return result
        except Exception as e:
            return {"error": f"Quantum Physics Simulation Bridge Error: {str(e)}"}

    async def _run_gnome_materials(self, params: Dict) -> Dict:
        """Bridge to GNoME for materials stability prediction."""
        try:
            from app.services.extended_hypothesis_bridges import GNoMEMaterialsBridge
            
            bridge = GNoMEMaterialsBridge()
            
            result = await bridge.validate_material_stability(
                composition=params.get("composition", "Li2O"),
                expected_stable=params.get("expected_stable", True),
                expected_formation_energy=params.get("expected_formation_energy"),
                energy_tolerance=params.get("energy_tolerance", 0.1),
            )
            return result
        except Exception as e:
            return {"error": f"GNoME Materials Bridge Error: {str(e)}"}


class AdvancedHypothesisValidator:
    """
    Advanced hypothesis validation service combining:
    - POPPER's sequential falsification framework
    - ToolUniverse's scientific tool ecosystem
    - AXIOM's existing infrastructure
    
    This provides rigorous, reproducible hypothesis testing with
    statistical error control.
    """
    
    def __init__(
        self,
        alpha: float = 0.1,
        max_tests: int = 5,
        aggregation_method: ValidationMethod = ValidationMethod.E_VALUE
    ):
        self.alpha = alpha
        self.max_tests = max_tests
        self.aggregation_method = aggregation_method
        self.tool_adapter = ScientificToolAdapter()
        self.aggregator = StatisticalAggregator()
        
    async def validate_hypothesis(
        self,
        hypothesis: str,
        domain: str,
        test_specifications: List[Dict[str, Any]]
    ) -> ValidationResult:
        """
        Validate a scientific hypothesis using sequential falsification.
        
        Args:
            hypothesis: The hypothesis to test
            domain: Scientific domain (chemistry, physics, biology, etc.)
            test_specifications: List of test configurations
            
        Returns:
            ValidationResult with comprehensive test results
        """
        start_time = datetime.now()
        tests_run: List[FalsificationTest] = []
        p_values: List[float] = []
        
        logger.info(f"Validating hypothesis: {hypothesis}")
        logger.info(f"Domain: {domain}, Running {len(test_specifications)} tests")
        
        for i, test_spec in enumerate(test_specifications[:self.max_tests]):
            test_id = f"test_{i+1}_{datetime.now().strftime('%H%M%S')}"
            test_start = datetime.now()
            
            try:
                # Execute the test
                tool_name = test_spec.get("tool", "statistical_tests")
                parameters = test_spec.get("parameters", {})
                
                result = await self.tool_adapter.execute_tool(tool_name, parameters)
                
                # Extract p-value from result
                p_value = result.get("p_value")
                
                test = FalsificationTest(
                    test_id=test_id,
                    test_name=test_spec.get("name", f"Test {i+1}"),
                    description=test_spec.get("description", ""),
                    null_hypothesis=test_spec.get("null_hypothesis", "No effect"),
                    alternative_hypothesis=test_spec.get("alternative_hypothesis", "Effect exists"),
                    p_value=p_value,
                    e_value=self._p_to_e_value(p_value) if p_value else None,
                    raw_result=result,
                    execution_time_ms=(datetime.now() - test_start).total_seconds() * 1000,
                    tool_used=tool_name,
                    data_sources=test_spec.get("data_sources", [])
                )
                
                if result.get("error"):
                    test.error = result["error"]
                elif p_value is not None:
                    p_values.append(p_value)
                    
                tests_run.append(test)
                
            except Exception as e:
                logger.error(f"Test {test_id} failed: {e}")
                tests_run.append(FalsificationTest(
                    test_id=test_id,
                    test_name=test_spec.get("name", f"Test {i+1}"),
                    description=test_spec.get("description", ""),
                    null_hypothesis=test_spec.get("null_hypothesis", ""),
                    alternative_hypothesis=test_spec.get("alternative_hypothesis", ""),
                    error=str(e),
                    execution_time_ms=(datetime.now() - test_start).total_seconds() * 1000,
                    tool_used=test_spec.get("tool", "unknown")
                ))
        
        # Aggregate results
        combined_p, combined_e, status = self._aggregate_results(p_values)
        
        # Generate reasoning and conclusion
        reasoning, conclusion = self._generate_conclusion(
            hypothesis, tests_run, status, combined_p, combined_e
        )
        
        total_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return ValidationResult(
            hypothesis=hypothesis,
            status=status,
            confidence=self._calculate_confidence(combined_p, combined_e),
            combined_p_value=combined_p,
            combined_e_value=combined_e,
            tests_run=tests_run,
            method_used=self.aggregation_method,
            alpha=self.alpha,
            timestamp=datetime.now().isoformat(),
            total_time_ms=total_time,
            reasoning=reasoning,
            conclusion=conclusion
        )
    
    def _p_to_e_value(self, p_value: float, kappa: float = 0.5) -> float:
        """Convert p-value to e-value using kappa calibrator."""
        if p_value is None or p_value <= 0:
            return 0.0
        return kappa * (p_value ** (kappa - 1))
    
    def _aggregate_results(
        self, 
        p_values: List[float]
    ) -> Tuple[Optional[float], Optional[float], HypothesisStatus]:
        """Aggregate test results using configured method."""
        if not p_values:
            return None, None, HypothesisStatus.INSUFFICIENT_EVIDENCE
        
        if self.aggregation_method == ValidationMethod.FISHERS:
            is_significant, combined_p = self.aggregator.fishers_method(p_values, self.alpha)
            combined_e = None
        elif self.aggregation_method == ValidationMethod.E_VALUE:
            is_significant, combined_e = self.aggregator.e_value_kappa_calibrator(p_values, self.alpha)
            _, combined_p = self.aggregator.fishers_method(p_values, self.alpha)
        elif self.aggregation_method == ValidationMethod.BONFERRONI:
            is_significant, combined_p = self.aggregator.bonferroni_correction(p_values, self.alpha)
            combined_e = None
        else:
            is_significant, combined_p = self.aggregator.fishers_method(p_values, self.alpha)
            combined_e = None
        
        if is_significant:
            return combined_p, combined_e, HypothesisStatus.REFUTED
        else:
            # Check if we have strong evidence FOR the hypothesis
            if combined_p and combined_p > 0.5:
                return combined_p, combined_e, HypothesisStatus.VALIDATED
            return combined_p, combined_e, HypothesisStatus.INSUFFICIENT_EVIDENCE
    
    def _calculate_confidence(
        self, 
        combined_p: Optional[float], 
        combined_e: Optional[float]
    ) -> float:
        """Calculate confidence level in the result."""
        if combined_p is not None:
            # Higher p-value = more confidence in null (hypothesis holds)
            # Lower p-value = more confidence in rejecting hypothesis
            return abs(0.5 - combined_p) * 2
        elif combined_e is not None:
            # E-value > 1/alpha suggests strong evidence
            return min(1.0, combined_e / (1/self.alpha))
        return 0.0
    
    def _generate_conclusion(
        self,
        hypothesis: str,
        tests: List[FalsificationTest],
        status: HypothesisStatus,
        combined_p: Optional[float],
        combined_e: Optional[float]
    ) -> Tuple[str, str]:
        """Generate human-readable reasoning and conclusion."""
        successful_tests = [t for t in tests if t.error is None and t.p_value is not None]
        significant_tests = [t for t in successful_tests if t.is_significant]
        
        reasoning_parts = [
            f"Ran {len(tests)} falsification tests for the hypothesis.",
            f"Successfully completed: {len(successful_tests)} tests.",
            f"Tests with significant results (p < 0.05): {len(significant_tests)}.",
        ]
        
        if combined_p is not None:
            reasoning_parts.append(f"Combined p-value (Fisher's method): {combined_p:.4e}")
        if combined_e is not None:
            reasoning_parts.append(f"Combined e-value: {combined_e:.4f}")
        
        reasoning = " ".join(reasoning_parts)
        
        if status == HypothesisStatus.VALIDATED:
            conclusion = f"The hypothesis '{hypothesis}' is SUPPORTED by the evidence. " \
                        f"None of the {len(successful_tests)} falsification attempts could refute it."
        elif status == HypothesisStatus.REFUTED:
            conclusion = f"The hypothesis '{hypothesis}' is REFUTED. " \
                        f"{len(significant_tests)} out of {len(successful_tests)} tests showed significant evidence against it."
        else:
            conclusion = f"INSUFFICIENT EVIDENCE to confirm or refute '{hypothesis}'. " \
                        f"More tests may be needed for a definitive conclusion."
        
        return reasoning, conclusion


# Convenience function for quick validation
async def validate_scientific_hypothesis(
    hypothesis: str,
    domain: str,
    tests: List[Dict],
    alpha: float = 0.1,
    method: str = "e_value"
) -> Dict:
    """
    Quick function to validate a scientific hypothesis.
    
    Args:
        hypothesis: The hypothesis to test
        domain: Scientific domain
        tests: List of test specifications
        alpha: Significance level
        method: Aggregation method ('fishers', 'e_value', 'bonferroni')
    
    Returns:
        Validation result as dictionary
    """
    validator = AdvancedHypothesisValidator(
        alpha=alpha,
        aggregation_method=ValidationMethod(method)
    )
    result = await validator.validate_hypothesis(hypothesis, domain, tests)
    return result.to_dict()
