"""
Computational Chemistry Service for AXIOM
Integrates RDKit, Biopython, and PySCF for molecular modeling and quantum chemistry

Ethics & Safety (importante):
- Uso responsable: no usar estos resultados para diseño de fármacos, toxicidad o decisiones clínicas sin validación humana experta y protocolos regulatorios.
- Datos sensibles: no subir PII ni secuencias biológicas confidenciales. Anonimiza y cumple con normativa aplicable.
- Recursos y licencias: RDKit (conda-forge) y PySCF pueden requerir entornos específicos (Conda) y recursos elevados. Comprueba licencias y límites de uso.
- Validación científica: las propiedades y cálculos (HF/DFT básicos) son orientativos; no sustituyen verificación con métodos/paquetes de referencia y benchmarks.
- Seguridad operacional: limita tamaño de moléculas, número de conformeros y parámetros de cálculo para evitar DoS involuntario.

Consulta la guía central: ETHICS_AND_SAFETY.md
"""

import logging
from typing import Dict, Any
from app.services.base_service import BaseService
from app.compliance.ethics_gate import EthicsGate, ExperimentRequest  # Integración ética
from app.exceptions.domain.chemistry import ChemistryError

logger = logging.getLogger(__name__)

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors
    import rdkit
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    logger.warning("RDKit not available")

try:
    # Biopython components are imported narrowly when needed
    from Bio.Seq import Seq
    # from Bio.SeqRecord import SeqRecord  # not used directly
    import Bio
    BIOPYTHON_AVAILABLE = True
except ImportError:
    BIOPYTHON_AVAILABLE = False
    logger.warning("Biopython not available")

try:
    import pyscf
    from pyscf import gto, scf
    PYSCF_AVAILABLE = True
except ImportError:
    PYSCF_AVAILABLE = False
    logger.warning("PySCF not available")

# New advanced chemistry dependencies (importación dinámica dentro de métodos)
try:
    import pymatgen  # noqa: F401  (usado dinámicamente)
    PYMATGEN_AVAILABLE = True
except ImportError:
    PYMATGEN_AVAILABLE = False
    logger.warning("Pymatgen not available - pip install pymatgen")

try:
    import cobra  # noqa: F401
    COBRAPY_AVAILABLE = True
except ImportError:
    COBRAPY_AVAILABLE = False
    logger.warning("COBRApy not available - pip install cobra")

try:
    import openmm  # noqa: F401
    OPENMM_AVAILABLE = True
except ImportError:
    OPENMM_AVAILABLE = False
    logger.warning("OpenMM not available - conda install -c conda-forge openmm")


class ComputationalChemistryService(BaseService):
    """Service for computational chemistry operations"""

    def __init__(self):
        super().__init__("ComputationalChemistryService")
        self.rdkit_available = RDKIT_AVAILABLE
        self.biopython_available = BIOPYTHON_AVAILABLE
        self.pyscf_available = PYSCF_AVAILABLE
        self.pymatgen_available = PYMATGEN_AVAILABLE
        self.cobrapy_available = COBRAPY_AVAILABLE
        self.openmm_available = OPENMM_AVAILABLE
        # Ethics Gate instancia (política YAML opcional)
        self.ethics_gate = EthicsGate(policy_path="config/ethics_policy.yaml")

    def _ethics_check(self, operation: str, request_data: Dict[str, Any]) -> None:
        """Evalúa operaciones sensibles antes de ejecutar.
        Lanza PermissionError si bloqueado.
        """
        sensitive_map = {
            "quantum_chemistry": "quantum_chemistry",
            "metabolic_network_analysis": "metabolic_networks",
            "molecular_dynamics_setup": "molecular_dynamics",
            "analyze_crystal_structure": "materials_screening",
            "materials_screening": "materials_screening",
            # Secuencias pueden ser genómicas/proteína
            "analyze_sequence": request_data.get("sequence_domain", "genomics"),
        }
        if operation not in sensitive_map:
            return
        domain = sensitive_map[operation]
        req = ExperimentRequest(
            domain=domain,
            description=f"Chem/Bio operation {operation}",
            resources={
                "gpu_hours": request_data.get("gpu_hours", 0),
                "memory_gb": request_data.get("memory_gb", 0)
            },
            data_sensitivity=request_data.get("data_sensitivity", "none"),
            declared_intent=request_data.get("intent", "uso científico legítimo"),
            justification=request_data.get("justification"),
            justification_signature=request_data.get("justification_signature")
        )
        decision = self.ethics_gate.evaluate(req, auto_anchor=True)
        if not decision.allowed:
            raise PermissionError(f"EthicsGate bloqueó {operation}: {decision.reason} (nivel {decision.level})")

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a computational chemistry request"""
        try:
            operation = request_data.get("operation", "")
            self.log_request(request_data)

            # Chequeo ético previo (no para operaciones triviales)
            try:
                self._ethics_check(operation, request_data)
            except PermissionError as e:
                return {"error": str(e), "ethics_block": True}

            if operation == "analyze_molecule":
                result = self.analyze_molecule(request_data.get("smiles", ""))
            elif operation == "generate_conformers":
                result = self.generate_conformers(
                    request_data.get("smiles", ""),
                    request_data.get("num_conformers", 10)
                )
            elif operation == "analyze_sequence":
                result = self.analyze_sequence(
                    request_data.get("sequence", ""),
                    request_data.get("sequence_type", "dna")
                )
            elif operation == "quantum_chemistry":
                result = self.quantum_chemistry_calculation(request_data)
            # New advanced operations for Meta 4
            elif operation == "analyze_crystal_structure":
                result = await self.analyze_crystal_structure(request_data)
            elif operation == "metabolic_network_analysis":
                result = await self.metabolic_network_analysis(request_data)
            elif operation == "molecular_dynamics_setup":
                result = await self.molecular_dynamics_setup(request_data)
            elif operation == "materials_screening":
                result = await self.materials_screening(request_data)
            elif operation == "service_info":
                result = self.get_service_info()
            else:
                result = {"error": f"Unknown operation: {operation}"}

            self.log_response(result)
            return result

        except ChemistryError as e:
            return self.handle_error(e, "process_request")

    def get_service_info(self) -> Dict[str, Any]:
        """Get information about available chemistry libraries"""
        return {
            "rdkit": {
                "available": self.rdkit_available,
                "version": rdkit.__version__ if self.rdkit_available else None,
                "capabilities": [
                    "Molecular structure manipulation",
                    "Descriptor calculation",
                    "Molecular visualization",
                    "Substructure searching",
                    "Conformer generation"
                ]
            },
            "biopython": {
                "available": self.biopython_available,
                "version": Bio.__version__ if self.biopython_available else None,
                "capabilities": [
                    "Sequence analysis",
                    "Sequence alignment",
                    "Phylogenetic analysis",
                    "Protein structure analysis"
                ]
            },
            "pyscf": {
                "available": self.pyscf_available,
                "version": pyscf.__version__ if self.pyscf_available else None,
                "capabilities": [
                    "Quantum chemistry calculations",
                    "Hartree-Fock theory",
                    "Density functional theory",
                    "Molecular orbital analysis"
                ]
            },
            "pymatgen": {
                "available": self.pymatgen_available,
                "version": None,  # Will be available when imported
                "capabilities": [
                    "Crystal structure analysis",
                    "Phase diagram construction",
                    "Materials property prediction",
                    "High-throughput screening"
                ]
            },
            "cobrapy": {
                "available": self.cobrapy_available,
                "version": None,
                "capabilities": [
                    "Metabolic network analysis",
                    "Flux balance analysis",
                    "Essential gene identification",
                    "Systems biology modeling"
                ]
            },
            "openmm": {
                "available": self.openmm_available,
                "version": None,
                "capabilities": [
                    "Molecular dynamics setup",
                    "Force field applications",
                    "Energy minimization",
                    "MD simulation preparation"
                ]
            }
        }

    def analyze_molecule(self, smiles: str) -> Dict[str, Any]:
        """Analyze molecular properties using RDKit"""
        if not self.rdkit_available:
            return {"error": "RDKit not available"}

        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return {"error": "Invalid SMILES string"}

            # Calculate molecular descriptors
            descriptors = {
                "molecular_weight": Descriptors.ExactMolWt(mol),
                "logp": Descriptors.MolLogP(mol),
                "tpsa": Descriptors.TPSA(mol),
                "hbd": Descriptors.NumHDonors(mol),
                "hba": Descriptors.NumHAcceptors(mol),
                "rotatable_bonds": Descriptors.NumRotatableBonds(mol),
                "rings": Descriptors.RingCount(mol),
                "heavy_atoms": mol.GetNumHeavyAtoms(),
                "formula": Chem.rdMolDescriptors.CalcMolFormula(mol)
            }

            return {
                "smiles": smiles,
                "descriptors": descriptors,
                "num_atoms": mol.GetNumAtoms(),
                "num_bonds": mol.GetNumBonds()
            }

        except ChemistryError as e:
            return {"error": f"Analysis failed: {str(e)}"}

    def generate_conformers(self, smiles: str, num_conformers: int = 10) -> Dict[str, Any]:
        """Generate molecular conformers"""
        if not self.rdkit_available:
            return {"error": "RDKit not available"}

        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return {"error": "Invalid SMILES string"}

            # Add hydrogens
            mol = Chem.AddHs(mol)

            # Generate conformers
            AllChem.EmbedMultipleConfs(mol, numConfs=num_conformers, randomSeed=42)
            AllChem.MMFFOptimizeMoleculeConfs(mol)

            conformers = []
            for i in range(num_conformers):
                conf = mol.GetConformer(i)
                energy = AllChem.MMFFGetMoleculeForceField(mol, confId=i).CalcEnergy()
                conformers.append({
                    "conformer_id": i,
                    "energy": energy,
                    "coordinates": conf.GetPositions().tolist()
                })

            return {
                "smiles": smiles,
                "num_conformers": num_conformers,
                "conformers": conformers
            }

        except ChemistryError as e:
            return {"error": f"Conformer generation failed: {str(e)}"}

    def analyze_sequence(self, sequence: str, sequence_type: str = "dna") -> Dict[str, Any]:
        """Analyze biological sequence using Biopython"""
        if not self.biopython_available:
            return {"error": "Biopython not available"}

        try:
            if sequence_type.lower() == "dna":
                seq = Seq(sequence)
                complement = seq.complement()
                reverse_complement = seq.reverse_complement()
                gc_content = (sequence.count('G') + sequence.count('C')) / len(sequence) * 100

                return {
                    "sequence": sequence,
                    "type": "DNA",
                    "length": len(sequence),
                    "gc_content": gc_content,
                    "complement": str(complement),
                    "reverse_complement": str(reverse_complement),
                    "molecular_weight": sum(self._nucleotide_weight(nt) for nt in sequence)
                }

            elif sequence_type.lower() == "protein":
                seq = Seq(sequence)
                molecular_weight = sum(self._amino_acid_weight(aa) for aa in sequence)

                return {
                    "sequence": sequence,
                    "type": "Protein",
                    "length": len(sequence),
                    "molecular_weight": molecular_weight,
                    "hydrophobic_residues": sum(1 for aa in sequence if aa in 'AILMFWYV'),
                    "charged_residues": sum(1 for aa in sequence if aa in 'DEKRH')
                }

            else:
                return {"error": f"Unsupported sequence type: {sequence_type}"}

        except ChemistryError as e:
            return {"error": f"Sequence analysis failed: {str(e)}"}

    def quantum_chemistry_calculation(self, molecule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform quantum chemistry calculation using PySCF"""
        if not self.pyscf_available:
            return {"error": "PySCF not available"}

        try:
            # Create molecule object
            mol = gto.Mole()
            mol.atom = molecule_data.get("atom", "H 0 0 0; H 0 0 0.74")
            mol.basis = molecule_data.get("basis", "sto-3g")
            mol.build()

            # Perform Hartree-Fock calculation
            mf = scf.RHF(mol)
            energy = mf.kernel()

            # Get molecular orbitals
            orbitals = mf.mo_energy.tolist() if hasattr(mf, 'mo_energy') else []

            return {
                "method": "Hartree-Fock",
                "basis": mol.basis,
                "energy": energy,
                "num_electrons": mol.nelec[0] + mol.nelec[1],
                "num_basis_functions": mol.nao,
                "molecular_orbitals": orbitals[:10]  # First 10 orbitals
            }

        except ChemistryError as e:
            return {"error": f"Quantum calculation failed: {str(e)}"}

    def _nucleotide_weight(self, nucleotide: str) -> float:
        """Get molecular weight of nucleotide"""
        weights = {'A': 313.2, 'T': 304.2, 'C': 289.2, 'G': 329.2}
        return weights.get(nucleotide.upper(), 0)

    def _amino_acid_weight(self, amino_acid: str) -> float:
        """Get molecular weight of amino acid"""
        weights = {
            'A': 89.1, 'R': 174.2, 'N': 132.1, 'D': 133.1,
            'C': 121.2, 'Q': 146.2, 'E': 147.1, 'G': 75.1,
            'H': 155.2, 'I': 131.2, 'L': 131.2, 'K': 146.2,
            'M': 149.2, 'F': 165.2, 'P': 115.1, 'S': 105.1,
            'T': 119.1, 'W': 204.2, 'Y': 181.2, 'V': 117.1
        }
        return weights.get(amino_acid.upper(), 0)

    # === New Meta 4 Methods: Advanced Chemistry ===
    
    async def analyze_crystal_structure(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze crystal structure using Pymatgen - Materials Chemistry"""
        if not self.pymatgen_available:
            return {
                "error": "Pymatgen not available", 
                "install_command": "pip install pymatgen"
            }
        
        try:
            # Import here to avoid errors if not available
            from pymatgen.core import Structure, Lattice
            from pymatgen.analysis.structure_analyzer import SpacegroupAnalyzer
            
            structure_data = request_data.get("structure_data")
            if not structure_data:
                # Create a default silicon structure for demonstration
                lattice = Lattice.cubic(5.43)  # Silicon lattice parameter
                species = ["Si", "Si"]
                coords = [[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]]
                structure = Structure(lattice, species, coords)
            elif isinstance(structure_data, dict):
                # Build structure from dict format
                lattice_data = structure_data.get("lattice", {})
                species = structure_data.get("species", ["Si", "Si"])
                coords = structure_data.get("coords", [[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]])
                
                # Create lattice
                if "a" in lattice_data and "b" in lattice_data and "c" in lattice_data:
                    lattice = Lattice.from_parameters(
                        lattice_data["a"], lattice_data["b"], lattice_data["c"],
                        lattice_data.get("alpha", 90), 
                        lattice_data.get("beta", 90),
                        lattice_data.get("gamma", 90)
                    )
                else:
                    lattice = Lattice.cubic(5.43)  # Default
                
                structure = Structure(lattice, species, coords)
            else:
                return {"error": "Invalid structure format - use dict with lattice, species, coords"}
            
            # Analyze structure
            analyzer = SpacegroupAnalyzer(structure)
            
            result = {
                "success": True,
                "analysis": {
                    "formula": structure.formula,
                    "num_atoms": len(structure),
                    "volume": structure.volume,
                    "density": structure.density,
                    "lattice_parameters": {
                        "a": structure.lattice.a,
                        "b": structure.lattice.b, 
                        "c": structure.lattice.c,
                        "alpha": structure.lattice.alpha,
                        "beta": structure.lattice.beta,
                        "gamma": structure.lattice.gamma
                    },
                    "crystal_system": analyzer.get_crystal_system(),
                    "space_group": analyzer.get_space_group_symbol(),
                    "space_group_number": analyzer.get_space_group_number(),
                    "point_group": analyzer.get_point_group_symbol()
                }
            }
            
            return result
            
        except ChemistryError as e:
            return {"error": f"Crystal structure analysis failed: {str(e)}"}
    
    async def metabolic_network_analysis(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze metabolic networks using COBRApy - Systems Biology"""
        if not self.cobrapy_available:
            return {
                "error": "COBRApy not available",
                "install_command": "pip install cobra"
            }
        
        try:
            # Import here to avoid errors if not available
            import cobra
            
            model_data = request_data.get("model")
            analysis_type = request_data.get("analysis_type", "flux_balance")
            
            if not model_data:
                # Use a test model for demonstration
                model = cobra.io.load_model('textbook')
            elif isinstance(model_data, str):
                # Try to load from BiGG models database or create test model
                try:
                    if model_data == "test_model":
                        model = cobra.io.load_model('textbook')
                    else:
                        model = cobra.io.load_model(model_data)
                except ChemistryError as e:
                    # Fall back to test model
                    model = cobra.io.load_model('textbook')
                    logger.warning(f"Could not load {model_data}, using textbook model: {e}")
            else:
                return {"error": "Invalid model format - use model name or 'test_model'"}
            
            result = {
                "success": True,
                "model_info": {
                    "id": model.id,
                    "name": getattr(model, 'name', 'Test Model'),
                    "num_reactions": len(model.reactions),
                    "num_metabolites": len(model.metabolites),
                    "num_genes": len(model.genes)
                }
            }
            
            if analysis_type == "flux_balance" or analysis_type == "fba":
                # Perform flux balance analysis
                solution = model.optimize()
                result["analysis"] = {
                    "type": "Flux Balance Analysis",
                    "objective_value": float(solution.objective_value) if solution.objective_value else 0.0,
                    "status": str(solution.status),
                    "fluxes": {
                        rxn.id: float(solution.fluxes.get(rxn.id, 0.0))
                        for rxn in list(model.reactions)[:10] if rxn.id in solution.fluxes
                    }
                }
                
            elif analysis_type == "essential_genes":
                # Find essential genes
                essential_genes = []
                try:
                    for gene in list(model.genes)[:5]:  # Limit for performance
                        with model:
                            gene.knock_out()
                            ko_solution = model.optimize()
                            if ko_solution.objective_value < 0.01:
                                essential_genes.append(gene.id)
                except ChemistryError as e:
                    logger.warning(f"Gene essentiality analysis failed: {e}")
                
                result["analysis"] = {
                    "type": "Essential Gene Analysis", 
                    "essential_genes": essential_genes,
                    "num_essential": len(essential_genes)
                }
            
            return result
            
        except ChemistryError as e:
            return {"error": f"Metabolic network analysis failed: {str(e)}"}
    
    async def molecular_dynamics_setup(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Setup molecular dynamics simulations with OpenMM integration"""
        if not self.openmm_available:
            return {
                "error": "OpenMM not available",
                "install_command": "conda install -c conda-forge openmm"
            }
        
        try:
            # Import here to avoid errors if not available
            from openmm import app, unit
            import openmm
            
            pdb_data = request_data.get("pdb_structure")
            forcefield_name = request_data.get("forcefield", "amber14-all.xml")
            temperature = request_data.get("temperature", 300.0) * unit.kelvin
            
            if not pdb_data:
                return {"error": "PDB structure required"}
            
            # Create temporary PDB file
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pdb', delete=False) as f:
                f.write(pdb_data)
                pdb_file = f.name
            
            try:
                # Load PDB
                pdb = app.PDBFile(pdb_file)
                
                # Create forcefield
                forcefield = app.ForceField(forcefield_name)
                
                # Create system
                system = forcefield.createSystem(
                    pdb.topology,
                    nonbondedMethod=app.PME,
                    nonbondedCutoff=1.0*unit.nanometer,
                    constraints=app.HBonds
                )
                
                # Setup integrator
                integrator = openmm.LangevinIntegrator(
                    temperature,
                    1.0/unit.picosecond,
                    2.0*unit.femtoseconds
                )
                
                # Create simulation
                simulation = app.Simulation(pdb.topology, system, integrator)
                simulation.context.setPositions(pdb.positions)
                
                # Energy minimization
                simulation.minimizeEnergy()
                
                # Get system properties
                state = simulation.context.getState(getEnergy=True)
                potential_energy = state.getPotentialEnergy()
                
                result = {
                    "success": True,
                    "setup": {
                        "num_atoms": pdb.topology.getNumAtoms(),
                        "num_residues": pdb.topology.getNumResidues(),
                        "forcefield": forcefield_name,
                        "temperature": temperature.value_in_unit(unit.kelvin),
                        "potential_energy": potential_energy.value_in_unit(unit.kilojoules_per_mole)
                    },
                    "simulation_ready": True,
                    "note": "System minimized and ready for MD simulation"
                }
                
                return result
                
            finally:
                # Clean up temporary file
                os.unlink(pdb_file)
                
        except ChemistryError as e:
            return {"error": f"Molecular dynamics setup failed: {str(e)}"}
    
    async def materials_screening(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """High-throughput materials screening using Pymatgen"""
        if not self.pymatgen_available:
            return {
                "error": "Pymatgen not available",
                "install_command": "pip install pymatgen"
            }
        
        try:
            # Import here to avoid errors
            from pymatgen.core import Structure, Element
            from pymatgen.analysis.structure_analyzer import SpacegroupAnalyzer
            
            materials_list = request_data.get("materials", [])
            screening_criteria = request_data.get("criteria", ["stability", "bandgap"])
            
            if not materials_list:
                return {"error": "Materials list required"}
            
            results = []
            
            for material_data in materials_list[:10]:  # Limit to 10 for performance
                try:
                    # Create structure
                    if isinstance(material_data, dict):
                        structure = Structure.from_dict(material_data)
                    else:
                        continue
                    
                    analyzer = SpacegroupAnalyzer(structure)
                    
                    # Basic analysis
                    analysis = {
                        "formula": structure.formula,
                        "volume": structure.volume,
                        "density": structure.density,
                        "crystal_system": analyzer.get_crystal_system(),
                        "space_group": analyzer.get_space_group_symbol()
                    }
                    
                    # Add screening criteria
                    if "stability" in screening_criteria:
                        # Simple formation energy estimate (would need more sophisticated methods in practice)
                        elements = structure.composition.elements
                        formation_energy = sum([Element(el).X for el in elements]) * -0.1  # Rough estimate
                        analysis["formation_energy_estimate"] = formation_energy
                    
                    if "bandgap" in screening_criteria:
                        # Bandgap estimation based on composition (very rough)
                        elements = structure.composition.elements
                        avg_electronegativity = sum([Element(el).X for el in elements]) / len(elements)
                        bandgap_estimate = max(0, avg_electronegativity - 1.5)  # Very rough
                        analysis["bandgap_estimate"] = bandgap_estimate
                    
                    results.append({
                        "material": structure.formula,
                        "analysis": analysis,
                        "promising": analysis.get("formation_energy_estimate", 0) < -0.5
                    })
                    
                except ChemistryError as e:
                    results.append({
                        "material": str(material_data),
                        "error": str(e)
                    })
            
            # Sort by most promising
            promising_materials = [r for r in results if r.get("promising", False)]
            
            return {
                "success": True,
                "screening_results": {
                    "total_screened": len(results),
                    "promising_candidates": len(promising_materials),
                    "results": results,
                    "top_candidates": promising_materials[:5]
                },
                "note": "This is a simplified screening - use advanced DFT for accurate results"
            }
            
        except ChemistryError as e:
            return {"error": f"Materials screening failed: {str(e)}"}
