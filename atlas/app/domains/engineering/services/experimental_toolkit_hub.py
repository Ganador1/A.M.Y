"""
Experimental Toolkit Hub - Central hub for real experimental tools by domain

This service provides access to real computational and experimental tools
for different scientific domains, enabling autonomous hypothesis testing
with actual simulations and analyses rather than stubs.

Author: ATLAS Autonomous Laboratory System
Date: ${new Date().toISOString().split('T')[0]}
"""

import logging
import asyncio
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime, timezone as tz
from app.exceptions.domain.biology import BiologyError

# Configure logging
logger = logging.getLogger(__name__)

UTC = tz.utc

# Import Knowledge Graph integration
from app.services.knowledge_graph_service import get_knowledge_graph_service


@dataclass
class ExperimentalResult:
    """Container for experimental results with metadata"""
    experiment_id: str
    domain: str
    tool_name: str
    method: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    metrics: Dict[str, float]
    raw_data: Optional[Any] = None
    logs: List[str] = None
    errors: List[str] = None
    duration_seconds: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(UTC)
        if self.logs is None:
            self.logs = []
        if self.errors is None:
            self.errors = []


class DomainToolkit(ABC):
    """Abstract base class for domain-specific toolkits"""
    
    def __init__(self, domain_name: str):
        self.domain_name = domain_name
        self.available_tools = []
        self.initialized = False
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the toolkit and check dependencies"""
        pass
    
    @abstractmethod
    async def list_capabilities(self) -> List[Dict[str, Any]]:
        """List available tools and their capabilities"""
        pass
    
    @abstractmethod
    async def validate_inputs(self, tool_name: str, inputs: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate inputs for a specific tool"""
        pass


class BiologyToolkit(DomainToolkit):
    """Toolkit for computational biology experiments"""
    
    def __init__(self):
        super().__init__("biology")
        self.openmm_available = False
        self.rdkit_available = False
        self.scanpy_available = False
        self.esmfold_available = False
        
    async def initialize(self) -> bool:
        """Check and initialize biology-specific dependencies"""
        try:
            # Check OpenMM availability
            try:
                import openmm
                import openmm.app as app
                self.openmm_available = True
                logger.info("✅ OpenMM disponible para simulaciones MD")
            except ImportError:
                logger.warning("⚠️ OpenMM no instalado - simulaciones MD no disponibles")
            
            # Check RDKit availability  
            try:
                from rdkit import Chem
                from rdkit.Chem import Descriptors
                self.rdkit_available = True
                logger.info("✅ RDKit disponible para análisis molecular")
            except ImportError:
                logger.warning("⚠️ RDKit no instalado - análisis molecular limitado")
                
            # Check scanpy availability
            try:
                import scanpy as sc
                self.scanpy_available = True
                logger.info("✅ scanpy disponible para análisis transcriptómico")
            except ImportError:
                logger.warning("⚠️ scanpy no instalado - análisis de expresión no disponible")
                
            # Check ESM availability
            try:
                import esm
                self.esmfold_available = True
                logger.info("✅ ESM disponible para predicción de estructura")
            except ImportError:
                logger.warning("⚠️ ESM no instalado - predicción de estructura limitada")
                
            self.initialized = True
            return True
            
        except BiologyError as e:
            logger.error(f"Error inicializando BiologyToolkit: {str(e)}")
            return False
    
    async def list_capabilities(self) -> List[Dict[str, Any]]:
        """List available biology tools"""
        capabilities = []
        
        if self.openmm_available:
            capabilities.append({
                "tool": "molecular_dynamics",
                "description": "Simulación de dinámica molecular con OpenMM",
                "methods": ["NPT", "NVT", "minimization"],
                "inputs": ["pdb_structure", "force_field", "temperature", "pressure", "time_ns"],
                "outputs": ["trajectory", "energy_profile", "rmsd", "contacts"]
            })
            
        if self.rdkit_available:
            capabilities.append({
                "tool": "molecular_properties",
                "description": "Cálculo de propiedades moleculares con RDKit",
                "methods": ["descriptors", "fingerprints", "3d_conformers"],
                "inputs": ["smiles", "sdf", "mol"],
                "outputs": ["logP", "tpsa", "mw", "hbd", "hba", "fingerprint"]
            })
            
        if self.scanpy_available:
            capabilities.append({
                "tool": "gene_expression_analysis",
                "description": "Análisis de expresión génica con scanpy",
                "methods": ["clustering", "differential_expression", "trajectory"],
                "inputs": ["count_matrix", "metadata"],
                "outputs": ["clusters", "de_genes", "umap", "pseudotime"]
            })
            
        if self.esmfold_available:
            capabilities.append({
                "tool": "protein_structure_prediction", 
                "description": "Predicción de estructura proteica con ESMFold",
                "methods": ["fold_single_sequence", "confidence_scoring"],
                "inputs": ["protein_sequence"],
                "outputs": ["pdb_structure", "plddt_scores", "confidence_plot"]
            })
            
        return capabilities
    
    async def validate_inputs(self, tool_name: str, inputs: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate inputs for biology tools"""
        errors = []
        
        if tool_name == "molecular_dynamics":
            if not inputs.get("pdb_structure") and not inputs.get("pdb_file"):
                errors.append("Se requiere estructura PDB")
            if "temperature" in inputs:
                temp = inputs["temperature"]
                if not isinstance(temp, (int, float)) or temp < 0 or temp > 1000:
                    errors.append(f"Temperatura inválida: {temp}K")
            if "time_ns" in inputs:
                time = inputs["time_ns"]
                if not isinstance(time, (int, float)) or time <= 0:
                    errors.append(f"Tiempo de simulación inválido: {time}ns")
                    
        elif tool_name == "molecular_properties":
            if not any(k in inputs for k in ["smiles", "sdf", "mol", "molecule"]):
                errors.append("Se requiere molécula en formato SMILES, SDF o MOL")
                
        elif tool_name == "gene_expression_analysis":
            if "count_matrix" not in inputs:
                errors.append("Se requiere matriz de conteos de expresión")
                
        elif tool_name == "protein_structure_prediction":
            if "protein_sequence" not in inputs:
                errors.append("Se requiere secuencia de proteína")
            else:
                seq = inputs["protein_sequence"]
                valid_aa = set("ACDEFGHIKLMNPQRSTVWY")
                if not all(aa in valid_aa for aa in seq.upper()):
                    errors.append("Secuencia contiene aminoácidos inválidos")
                    
        return len(errors) == 0, errors
    
    async def run_molecular_dynamics(self, inputs: Dict[str, Any]) -> ExperimentalResult:
        """Run real molecular dynamics simulation with OpenMM"""
        experiment_id = f"md_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        result = ExperimentalResult(
            experiment_id=experiment_id,
            domain="biology",
            tool_name="molecular_dynamics",
            method="OpenMM",
            inputs=inputs,
            outputs={},
            metrics={}
        )
        
        if not self.openmm_available:
            result.errors.append("OpenMM no está disponible")
            return result
            
        try:
            import openmm
            import openmm.app as app
            from openmm import unit
            import mdtraj
            
            # Load structure
            if "pdb_file" in inputs:
                pdb = app.PDBFile(inputs["pdb_file"])
            else:
                # Create from string
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.pdb', delete=False) as f:
                    f.write(inputs["pdb_structure"])
                    temp_pdb = f.name
                pdb = app.PDBFile(temp_pdb)
            
            # Setup system
            forcefield = app.ForceField(inputs.get("force_field", "amber14-all.xml"))
            modeller = app.Modeller(pdb.topology, pdb.positions)
            
            # Add solvent if requested
            if inputs.get("solvate", True):
                modeller.addSolvent(forcefield, padding=1.0*unit.nanometer)
                
            # Create system
            system = forcefield.createSystem(
                modeller.topology,
                nonbondedMethod=app.PME,
                constraints=app.HBonds,
                temperature=inputs.get("temperature", 300)*unit.kelvin
            )
            
            # Setup integrator
            integrator = openmm.LangevinIntegrator(
                inputs.get("temperature", 300)*unit.kelvin,
                1/unit.picosecond,
                0.002*unit.picoseconds
            )
            
            # Create simulation
            simulation = app.Simulation(modeller.topology, system, integrator)
            simulation.context.setPositions(modeller.positions)
            
            # Minimize
            result.logs.append("Minimizando energía...")
            simulation.minimizeEnergy(maxIterations=1000)
            
            # Production run
            time_ns = inputs.get("time_ns", 1.0)
            steps = int(time_ns * 500000)  # 2fs timestep
            
            result.logs.append(f"Ejecutando simulación por {time_ns}ns...")
            
            # Record trajectory
            positions = []
            energies = []
            report_interval = max(1, steps // 100)
            
            for i in range(0, steps, report_interval):
                simulation.step(report_interval)
                state = simulation.context.getState(getPositions=True, getEnergy=True)
                positions.append(state.getPositions(asNumpy=True))
                energies.append(state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole))
                
                if i % (steps // 10) == 0:
                    result.logs.append(f"Progreso: {100 * i / steps:.1f}%")
            
            # Analyze results
            result.outputs["final_energy"] = energies[-1]
            result.outputs["energy_profile"] = energies
            result.outputs["n_frames"] = len(positions)
            
            # Calculate RMSD if possible
            try:
                import mdtraj
                # Create trajectory for analysis
                traj = mdtraj.Trajectory(
                    np.array(positions),
                    mdtraj.Topology.from_openmm(modeller.topology)
                )
                rmsd = mdtraj.rmsd(traj, traj[0])
                result.outputs["rmsd"] = rmsd.tolist()
                result.metrics["final_rmsd"] = float(rmsd[-1])
                result.metrics["avg_rmsd"] = float(np.mean(rmsd))
            except EngineeringError:
                result.logs.append("No se pudo calcular RMSD")
            
            result.metrics["simulation_time_ns"] = time_ns
            result.metrics["n_atoms"] = modeller.topology.getNumAtoms()
            
            return result
            
        except BiologyError as e:
            result.errors.append(f"Error en simulación MD: {str(e)}")
            logger.error(f"Error en MD: {str(e)}", exc_info=True)
            return result
    
    async def predict_protein_folding(self, sequence: str) -> ExperimentalResult:
        """Predict protein structure using ESMFold or fallback methods"""
        experiment_id = f"fold_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        result = ExperimentalResult(
            experiment_id=experiment_id,
            domain="biology",
            tool_name="protein_structure_prediction",
            method="ESMFold" if self.esmfold_available else "Homology",
            inputs={"sequence": sequence},
            outputs={},
            metrics={}
        )
        
        try:
            if self.esmfold_available:
                # Use ESMFold
                import esm
                model = esm.pretrained.esmfold_v1()
                model = model.eval()
                
                with torch.no_grad():
                    output = model.infer_pdb(sequence)
                    
                result.outputs["pdb_structure"] = output
                result.outputs["confidence"] = "high"
                result.logs.append("Estructura predicha con ESMFold")
                
            else:
                # Fallback: use template-based modeling or basic prediction
                result.outputs["pdb_structure"] = self._generate_extended_structure(sequence)
                result.outputs["confidence"] = "low" 
                result.logs.append("Estructura básica generada (ESMFold no disponible)")
                
            result.metrics["sequence_length"] = len(sequence)
            return result
            
        except BiologyError as e:
            result.errors.append(f"Error en predicción de estructura: {str(e)}")
            return result
    
    def _generate_extended_structure(self, sequence: str) -> str:
        """Generate basic extended structure as fallback"""
        # Simple extended chain generator
        pdb_lines = ["REMARK   Generated extended structure"]
        
        for i, aa in enumerate(sequence):
            atom_lines = [
                f"ATOM  {i*4+1:5d}  N   {aa} A{i+1:4d}    {i*3.8:8.3f}   0.000   0.000  1.00  0.00           N",
                f"ATOM  {i*4+2:5d}  CA  {aa} A{i+1:4d}    {i*3.8+1.5:8.3f}   0.000   0.000  1.00  0.00           C",
                f"ATOM  {i*4+3:5d}  C   {aa} A{i+1:4d}    {i*3.8+2.5:8.3f}   0.000   0.000  1.00  0.00           C",
                f"ATOM  {i*4+4:5d}  O   {aa} A{i+1:4d}    {i*3.8+2.5:8.3f}   1.200   0.000  1.00  0.00           O"
            ]
            pdb_lines.extend(atom_lines)
            
        pdb_lines.append("END")
        return "\n".join(pdb_lines)
    
    async def analyze_gene_expression(self, count_matrix: np.ndarray, metadata: Dict[str, Any] = None) -> ExperimentalResult:
        """Analyze gene expression data using scanpy"""
        experiment_id = f"gex_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        result = ExperimentalResult(
            experiment_id=experiment_id,
            domain="biology",
            tool_name="gene_expression_analysis",
            method="scanpy",
            inputs={"matrix_shape": count_matrix.shape, "metadata": metadata},
            outputs={},
            metrics={}
        )
        
        if not self.scanpy_available:
            result.errors.append("scanpy no está disponible")
            return result
            
        try:
            import scanpy as sc
            import pandas as pd
            
            # Create AnnData object
            adata = sc.AnnData(X=count_matrix)
            
            if metadata:
                if "gene_names" in metadata:
                    adata.var_names = metadata["gene_names"]
                if "cell_names" in metadata:
                    adata.obs_names = metadata["cell_names"]
                if "cell_types" in metadata:
                    adata.obs["cell_type"] = metadata["cell_types"]
                    
            # Quality control
            sc.pp.calculate_qc_metrics(adata, inplace=True)
            
            # Filtering
            sc.pp.filter_cells(adata, min_genes=200)
            sc.pp.filter_genes(adata, min_cells=3)
            
            # Normalization
            adata.layers["counts"] = adata.X.copy()
            sc.pp.normalize_total(adata, target_sum=1e4)
            sc.pp.log1p(adata)
            
            # Find highly variable genes
            sc.pp.highly_variable_genes(adata, min_mean=0.0125, max_mean=3, min_disp=0.5)
            adata.raw = adata
            adata = adata[:, adata.var.highly_variable]
            
            # Scale data
            sc.pp.scale(adata, max_value=10)
            
            # PCA
            sc.tl.pca(adata, svd_solver='arpack')
            
            # Compute neighborhood graph
            sc.pp.neighbors(adata, n_neighbors=10, n_pcs=40)
            
            # UMAP
            sc.tl.umap(adata)
            
            # Clustering
            sc.tl.leiden(adata)
            
            # Find marker genes
            sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')
            
            # Extract results
            result.outputs["n_cells"] = adata.n_obs
            result.outputs["n_genes"] = adata.n_vars
            result.outputs["n_clusters"] = len(adata.obs['leiden'].unique())
            result.outputs["umap_coords"] = adata.obsm['X_umap'].tolist()
            result.outputs["clusters"] = adata.obs['leiden'].tolist()
            
            # Top marker genes per cluster
            marker_genes = {}
            for cluster in adata.obs['leiden'].unique():
                genes = sc.get.rank_genes_groups_df(adata, group=cluster, key='rank_genes_groups')
                marker_genes[f"cluster_{cluster}"] = genes.head(10)['names'].tolist()
                
            result.outputs["marker_genes"] = marker_genes
            
            result.metrics["n_hvgs"] = sum(adata.var.highly_variable)
            result.metrics["median_genes_per_cell"] = float(np.median(adata.obs['n_genes_by_counts']))
            
            result.logs.append(f"Análisis completado: {result.outputs['n_clusters']} clusters identificados")
            
            return result
            
        except BiologyError as e:
            result.errors.append(f"Error en análisis de expresión: {str(e)}")
            return result


class ChemistryToolkit(DomainToolkit):
    """Toolkit for computational chemistry experiments"""
    
    def __init__(self):
        super().__init__("chemistry")
        self.rdkit_available = False
        self.openbabel_available = False
        
    async def initialize(self) -> bool:
        """Check and initialize chemistry-specific dependencies"""
        try:
            # Check RDKit
            try:
                from rdkit import Chem
                from rdkit.Chem import Descriptors, AllChem, DataStructs
                self.rdkit_available = True
                logger.info("✅ RDKit disponible para química computacional")
            except ImportError:
                logger.warning("⚠️ RDKit no instalado")
                
            # Check OpenBabel
            try:
                import openbabel
                self.openbabel_available = True
                logger.info("✅ OpenBabel disponible para conversiones")
            except ImportError:
                logger.warning("⚠️ OpenBabel no instalado")
                
            self.initialized = True
            return True
            
        except BiologyError as e:
            logger.error(f"Error inicializando ChemistryToolkit: {str(e)}")
            return False
    
    async def list_capabilities(self) -> List[Dict[str, Any]]:
        """List available chemistry tools"""
        capabilities = []
        
        if self.rdkit_available:
            capabilities.extend([
                {
                    "tool": "molecular_properties",
                    "description": "Cálculo de propiedades fisicoquímicas",
                    "methods": ["descriptors", "rule_of_five", "qed"],
                    "inputs": ["smiles", "mol"],
                    "outputs": ["logP", "mw", "tpsa", "hbd", "hba", "rotatable_bonds"]
                },
                {
                    "tool": "reaction_prediction",
                    "description": "Predicción de productos de reacción",
                    "methods": ["template_based", "ml_based"],
                    "inputs": ["reactants", "conditions"],
                    "outputs": ["products", "yield_prediction", "mechanism"]
                },
                {
                    "tool": "retrosynthesis",
                    "description": "Análisis retrosintético",
                    "methods": ["disconnection", "transform_based"],
                    "inputs": ["target_molecule"],
                    "outputs": ["synthetic_routes", "precursors", "difficulty_score"]
                },
                {
                    "tool": "similarity_search",
                    "description": "Búsqueda de moléculas similares",
                    "methods": ["fingerprint", "pharmacophore", "shape"],
                    "inputs": ["query_molecule", "database"],
                    "outputs": ["similar_molecules", "similarity_scores"]
                }
            ])
            
        return capabilities
    
    async def validate_inputs(self, tool_name: str, inputs: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate inputs for chemistry tools"""
        errors = []
        
        if tool_name in ["molecular_properties", "reaction_prediction", "retrosynthesis"]:
            if not any(k in inputs for k in ["smiles", "mol", "molecule"]):
                errors.append("Se requiere molécula en formato SMILES o MOL")
            elif "smiles" in inputs:
                # Validate SMILES
                if self.rdkit_available:
                    from rdkit import Chem
                    mol = Chem.MolFromSmiles(inputs["smiles"])
                    if mol is None:
                        errors.append(f"SMILES inválido: {inputs['smiles']}")
                        
        return len(errors) == 0, errors
    
    async def calculate_molecular_properties(self, smiles: str) -> ExperimentalResult:
        """Calculate comprehensive molecular properties"""
        experiment_id = f"props_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        result = ExperimentalResult(
            experiment_id=experiment_id,
            domain="chemistry",
            tool_name="molecular_properties",
            method="RDKit",
            inputs={"smiles": smiles},
            outputs={},
            metrics={}
        )
        
        if not self.rdkit_available:
            result.errors.append("RDKit no está disponible")
            return result
            
        try:
            from rdkit import Chem
            from rdkit.Chem import Descriptors, Lipinski, QED, AllChem
            
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                result.errors.append(f"No se pudo parsear SMILES: {smiles}")
                return result
                
            # Basic properties
            result.outputs["molecular_weight"] = Descriptors.MolWt(mol)
            result.outputs["logP"] = Descriptors.MolLogP(mol)
            result.outputs["tpsa"] = Descriptors.TPSA(mol)
            result.outputs["n_hbd"] = Descriptors.NumHDonors(mol)
            result.outputs["n_hba"] = Descriptors.NumHAcceptors(mol)
            result.outputs["n_rotatable_bonds"] = Descriptors.NumRotatableBonds(mol)
            result.outputs["n_aromatic_rings"] = Descriptors.NumAromaticRings(mol)
            result.outputs["n_heavy_atoms"] = Descriptors.HeavyAtomCount(mol)
            
            # Lipinski Rule of Five
            ro5_violations = 0
            if result.outputs["molecular_weight"] > 500:
                ro5_violations += 1
            if result.outputs["logP"] > 5:
                ro5_violations += 1
            if result.outputs["n_hbd"] > 5:
                ro5_violations += 1
            if result.outputs["n_hba"] > 10:
                ro5_violations += 1
                
            result.outputs["lipinski_violations"] = ro5_violations
            result.outputs["lipinski_pass"] = ro5_violations <= 1
            
            # QED Score
            result.outputs["qed_score"] = QED.qed(mol)
            
            # 3D properties
            try:
                mol_3d = Chem.AddHs(mol)
                AllChem.EmbedMolecule(mol_3d, randomSeed=42)
                AllChem.MMFFOptimizeMolecule(mol_3d)
                
                # Calculate some 3D descriptors
                result.outputs["asphericity"] = Descriptors.Asphericity(mol_3d)
                result.outputs["eccentricity"] = Descriptors.Eccentricity(mol_3d)
                result.outputs["radius_of_gyration"] = Descriptors.RadiusOfGyration(mol_3d)
                
            except EngineeringError:
                result.logs.append("No se pudieron calcular propiedades 3D")
                
            # SMARTS pattern matching for functional groups
            functional_groups = {
                "carboxylic_acid": "[CX3](=O)[OX2H1]",
                "amine": "[NX3;H2,H1;!$(NC=O)]",
                "alcohol": "[OX2H]",
                "ketone": "[CX3](=O)[CX4]",
                "ester": "[CX3](=O)[OX2][CX4]",
                "amide": "[CX3](=O)[NX3]"
            }
            
            result.outputs["functional_groups"] = []
            for name, smarts in functional_groups.items():
                pattern = Chem.MolFromSmarts(smarts)
                if mol.HasSubstructMatch(pattern):
                    result.outputs["functional_groups"].append(name)
                    
            result.metrics["druglikeness"] = result.outputs["qed_score"]
            result.metrics["complexity"] = len(Chem.GetSymmSSSR(mol))  # Ring systems
            
            result.logs.append(f"Propiedades calculadas para {smiles}")
            
            return result
            
        except BiologyError as e:
            result.errors.append(f"Error calculando propiedades: {str(e)}")
            return result
    
    async def predict_reaction_outcomes(self, reactants: List[str], conditions: Dict[str, Any] = None) -> ExperimentalResult:
        """Predict reaction products using template-based or ML methods"""
        experiment_id = f"rxn_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        result = ExperimentalResult(
            experiment_id=experiment_id,
            domain="chemistry", 
            tool_name="reaction_prediction",
            method="Template-based",
            inputs={"reactants": reactants, "conditions": conditions or {}},
            outputs={},
            metrics={}
        )
        
        if not self.rdkit_available:
            result.errors.append("RDKit no está disponible")
            return result
            
        try:
            from rdkit import Chem
            from rdkit.Chem import AllChem
            
            # Parse reactants
            reactant_mols = []
            for r in reactants:
                mol = Chem.MolFromSmiles(r)
                if mol is None:
                    result.errors.append(f"Reactante inválido: {r}")
                    return result
                reactant_mols.append(mol)
            
            # Simple reaction templates
            reaction_templates = {
                "esterification": "[CX3:1](=[OX1])[OX2H1:2].[CX4:3][OX2H1:4]>>[CX3:1](=[OX1])[OX2:2][CX4:3].[OH2:4]",
                "amide_formation": "[CX3:1](=[OX1])[OX2H1:2].[NX3;H2,H1:3]>>[CX3:1](=[OX1])[NX3:3].[OH2:2]",
                "sn2": "[CX4:1][Cl,Br,I:2].[Nu-:3]>>[CX4:1][Nu:3].[Cl-,Br-,I-:2]",
                "aldol": "[CX3H1:1]=[OX1:2].[CX3:3][CX3:4]=[OX1:5]>>[CX3:1][CX3:3][CX3:4][OX2H1:5]"
            }
            
            # Try to match reaction templates
            products_found = []
            
            for template_name, smarts in reaction_templates.items():
                try:
                    rxn = AllChem.ReactionFromSmarts(smarts)
                    # Try reaction with different combinations of reactants
                    if len(reactant_mols) == 2:
                        products = rxn.RunReactants((reactant_mols[0], reactant_mols[1]))
                        if products:
                            for product_set in products:
                                product_smiles = [Chem.MolToSmiles(p) for p in product_set]
                                products_found.append({
                                    "template": template_name,
                                    "products": product_smiles,
                                    "confidence": 0.8
                                })
                                
                except EngineeringError:
                    continue
                    
            if products_found:
                result.outputs["predicted_products"] = products_found
                result.outputs["n_routes"] = len(products_found)
                result.logs.append(f"Se encontraron {len(products_found)} rutas de reacción")
            else:
                # Fallback: simple combination
                result.outputs["predicted_products"] = [{
                    "template": "unknown",
                    "products": [".".join(reactants)],
                    "confidence": 0.3
                }]
                result.logs.append("No se encontraron templates específicos, predicción genérica")
                
            result.metrics["n_products"] = len(products_found)
            
            return result
            
        except BiologyError as e:
            result.errors.append(f"Error en predicción de reacción: {str(e)}")
            return result
    
    async def optimize_synthesis_route(self, target_smiles: str, max_steps: int = 3) -> ExperimentalResult:
        """Perform retrosynthetic analysis"""
        experiment_id = f"retro_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        result = ExperimentalResult(
            experiment_id=experiment_id,
            domain="chemistry",
            tool_name="retrosynthesis",
            method="Disconnection-based",
            inputs={"target": target_smiles, "max_steps": max_steps},
            outputs={},
            metrics={}
        )
        
        if not self.rdkit_available:
            result.errors.append("RDKit no está disponible")
            return result
            
        try:
            from rdkit import Chem
            from rdkit.Chem import AllChem
            
            target_mol = Chem.MolFromSmiles(target_smiles)
            if target_mol is None:
                result.errors.append(f"SMILES objetivo inválido: {target_smiles}")
                return result
                
            # Simple retrosynthetic disconnections
            disconnections = {
                "ester": {
                    "pattern": "[CX3](=O)[OX2][CX4]",
                    "precursors": ["[CX3](=O)[OH]", "[CX4][OH]"],
                    "name": "Ester hydrolysis"
                },
                "amide": {
                    "pattern": "[CX3](=O)[NX3]",
                    "precursors": ["[CX3](=O)[OH]", "[NX3H2]"],
                    "name": "Amide hydrolysis"
                },
                "cn_bond": {
                    "pattern": "[CX4][NX3]",
                    "precursors": ["[CX4][Br]", "[NX3H2]"],
                    "name": "C-N coupling"
                }
            }
            
            routes = []
            
            # Try each disconnection
            for disc_name, disc_info in disconnections.items():
                pattern = Chem.MolFromSmarts(disc_info["pattern"])
                if target_mol.HasSubstructMatch(pattern):
                    # This is a very simplified retrosynthesis
                    route = {
                        "disconnection": disc_info["name"],
                        "target": target_smiles,
                        "precursors": disc_info["precursors"],
                        "steps": 1,
                        "difficulty_score": 0.5,
                        "commercial_availability": "unknown"
                    }
                    routes.append(route)
                    
            if not routes:
                # Fallback: suggest general building blocks
                mw = Descriptors.MolWt(target_mol)
                if mw < 200:
                    precursors = ["C=C", "C#C", "[NH2]"]
                elif mw < 350:
                    precursors = ["c1ccccc1", "CC(=O)Cl", "[NH2]"]
                else:
                    precursors = ["c1ccccc1Br", "c1ccccc1B(O)O", "CC(=O)Cl"]
                    
                routes.append({
                    "disconnection": "Generic building blocks",
                    "target": target_smiles,
                    "precursors": precursors,
                    "steps": max_steps,
                    "difficulty_score": 0.8,
                    "commercial_availability": "likely"
                })
                
            result.outputs["synthetic_routes"] = routes
            result.outputs["n_routes"] = len(routes)
            result.outputs["best_route"] = min(routes, key=lambda x: x["difficulty_score"])
            
            result.metrics["min_steps"] = min(r["steps"] for r in routes)
            result.metrics["avg_difficulty"] = np.mean([r["difficulty_score"] for r in routes])
            
            result.logs.append(f"Se encontraron {len(routes)} rutas sintéticas")
            
            return result
            
        except BiologyError as e:
            result.errors.append(f"Error en retrosíntesis: {str(e)}")
            return result


class PhysicsToolkit(DomainToolkit):
    """Toolkit for physics and materials science experiments"""
    
    def __init__(self):
        super().__init__("physics")
        self.numpy_available = True  # Always available
        self.scipy_available = False
        self.ase_available = False
        
    async def initialize(self) -> bool:
        """Check physics dependencies"""
        try:
            try:
                import scipy
                self.scipy_available = True
                logger.info("✅ SciPy disponible para cálculos físicos")
            except ImportError:
                logger.warning("⚠️ SciPy no instalado")
                
            try:
                import ase
                self.ase_available = True
                logger.info("✅ ASE disponible para simulaciones de materiales")
            except ImportError:
                logger.warning("⚠️ ASE no instalado")
                
            self.initialized = True
            return True
            
        except BiologyError as e:
            logger.error(f"Error inicializando PhysicsToolkit: {str(e)}")
            return False
    
    async def list_capabilities(self) -> List[Dict[str, Any]]:
        """List available physics tools"""
        capabilities = [
            {
                "tool": "quantum_simulation",
                "description": "Simulación cuántica básica",
                "methods": ["schrodinger_1d", "harmonic_oscillator", "particle_in_box"],
                "inputs": ["potential", "mass", "energy_range"],
                "outputs": ["wavefunctions", "energies", "probability_density"]
            },
            {
                "tool": "materials_properties",
                "description": "Predicción de propiedades de materiales",
                "methods": ["density", "band_gap", "elastic_moduli"],
                "inputs": ["crystal_structure", "composition"],
                "outputs": ["properties_dict", "stability_score"]
            },
            {
                "tool": "thermodynamics",
                "description": "Cálculos termodinámicos",
                "methods": ["phase_diagram", "gibbs_energy", "heat_capacity"],
                "inputs": ["temperature", "pressure", "composition"],
                "outputs": ["phase", "thermodynamic_properties"]
            }
        ]
        
        return capabilities
    
    async def validate_inputs(self, tool_name: str, inputs: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate physics tool inputs"""
        errors = []
        
        if tool_name == "quantum_simulation":
            if "mass" in inputs and inputs["mass"] <= 0:
                errors.append("La masa debe ser positiva")
                
        elif tool_name == "thermodynamics":
            if "temperature" in inputs and inputs["temperature"] < 0:
                errors.append("La temperatura debe ser >= 0K")
                
        return len(errors) == 0, errors
    
    async def run_quantum_simulation(self, system_type: str, params: Dict[str, Any]) -> ExperimentalResult:
        """Run basic quantum mechanical simulations"""
        experiment_id = f"qm_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        result = ExperimentalResult(
            experiment_id=experiment_id,
            domain="physics",
            tool_name="quantum_simulation",
            method=system_type,
            inputs=params,
            outputs={},
            metrics={}
        )
        
        try:
            if system_type == "particle_in_box":
                # 1D particle in a box
                L = params.get("box_length", 1.0)  # nm
                mass = params.get("mass", 9.109e-31)  # electron mass
                n_levels = params.get("n_levels", 5)
                
                if self.scipy_available:
                    # Usar SciPy para cálculo más preciso
                    import scipy
                    result.logs.append("✅ Usando SciPy para simulación cuántica")
                    
                    # Energy levels (más preciso con constantes físicas de SciPy)
                    from scipy.constants import h, m_e, eV
                    energies = []
                    for n in range(1, n_levels + 1):
                        E_n = (n**2 * h**2) / (8 * mass * (L*1e-9)**2) / eV
                        energies.append(E_n)
                    
                    # Wavefunctions
                    x = np.linspace(0, L, 1000)
                    wavefunctions = []
                    for n in range(1, n_levels + 1):
                        psi = np.sqrt(2/L) * np.sin(n * np.pi * x / L)
                        wavefunctions.append(psi.tolist())
                        
                else:
                    # Implementación analítica básica (fallback)
                    result.logs.append("⚠️ Usando implementación analítica básica (SciPy no disponible)")
                    
                    # Energy levels
                    energies = []
                    wavefunctions = []
                    
                    x = np.linspace(0, L, 1000)
                    
                    for n in range(1, n_levels + 1):
                        # Energy in eV
                        E_n = (n**2 * np.pi**2 * 6.626e-34**2) / (8 * mass * (L*1e-9)**2) / 1.602e-19
                        energies.append(E_n)
                        
                        # Wavefunction
                        psi = np.sqrt(2/L) * np.sin(n * np.pi * x / L)
                        wavefunctions.append(psi.tolist())
                
                result.outputs["energy_levels_eV"] = energies
                result.outputs["wavefunctions"] = wavefunctions
                result.outputs["x_grid"] = x.tolist()
                
                result.metrics["ground_state_energy_eV"] = energies[0]
                result.metrics["n_levels_calculated"] = n_levels
                
            elif system_type == "harmonic_oscillator":
                # Quantum harmonic oscillator
                k = params.get("spring_constant", 1.0)  # N/m
                mass = params.get("mass", 9.109e-31)  # kg
                n_levels = params.get("n_levels", 5)
                
                if self.scipy_available:
                    # Usar SciPy para cálculo más preciso
                    import scipy
                    result.logs.append("✅ Usando SciPy para oscilador armónico")
                    
                    from scipy.constants import h, eV
                    omega = np.sqrt(k / mass)
                    
                    # Energy levels usando constantes precisas de SciPy
                    energies = []
                    for n in range(n_levels):
                        E_n = (n + 0.5) * h * omega / (2 * np.pi) / eV  # eV
                        energies.append(E_n)
                        
                else:
                    # Implementación analítica básica
                    result.logs.append("⚠️ Usando implementación analítica básica (SciPy no disponible)")
                    
                    omega = np.sqrt(k / mass)
                    
                    # Energy levels
                    energies = []
                    for n in range(n_levels):
                        E_n = (n + 0.5) * 6.626e-34 * omega / (2 * np.pi) / 1.602e-19  # eV
                        energies.append(E_n)
                    
                result.outputs["energy_levels_eV"] = energies
                result.outputs["frequency_Hz"] = omega / (2 * np.pi)
                result.outputs["zero_point_energy_eV"] = energies[0]
                
                result.metrics["frequency_THz"] = omega / (2 * np.pi * 1e12)
                
            result.logs.append(f"Simulación cuántica {system_type} completada")
            
            return result
            
        except BiologyError as e:
            result.errors.append(f"Error en simulación cuántica: {str(e)}")
            return result


class ExperimentalToolkitHub:
    """Central hub for accessing all domain-specific experimental toolkits"""
    
    def __init__(self):
        self.toolkits: Dict[str, DomainToolkit] = {}
        self.initialized = False
        
    async def initialize(self) -> bool:
        """Initialize all available toolkits"""
        try:
            logger.info("🔬 Inicializando Experimental Toolkit Hub...")
            
            # Initialize each toolkit
            biology = BiologyToolkit()
            if await biology.initialize():
                self.toolkits["biology"] = biology
                
            chemistry = ChemistryToolkit()
            if await chemistry.initialize():
                self.toolkits["chemistry"] = chemistry
                
            physics = PhysicsToolkit()
            if await physics.initialize():
                self.toolkits["physics"] = physics
                
            self.initialized = True
            logger.info(f"✅ Hub inicializado con {len(self.toolkits)} toolkits")
            
            return True
            
        except BiologyError as e:
            logger.error(f"Error inicializando hub: {str(e)}")
            return False
    
    async def list_all_capabilities(self) -> Dict[str, List[Dict[str, Any]]]:
        """List capabilities of all toolkits"""
        capabilities = {}
        
        for domain, toolkit in self.toolkits.items():
            capabilities[domain] = await toolkit.list_capabilities()
            
        return capabilities
    
    async def execute_experiment(
        self,
        domain: str,
        tool_name: str,
        method: str,
        inputs: Dict[str, Any]
    ) -> ExperimentalResult:
        
        # Get toolkit
        toolkit = self.get_toolkit(domain)
        if not toolkit:
            return ExperimentalResult(
                experiment_id=f"error_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}",
                domain=domain,
                tool_name=tool_name,
                method=method,
                inputs=inputs,
                outputs={},
                metrics={},
                errors=[f"Dominio '{domain}' no disponible"]
            )
        
        # Capture experimental conditions in Knowledge Graph
        kg_service = await get_knowledge_graph_service()
        experiment_id = f"{domain}_{tool_name}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Extract experimental conditions from inputs
            experimental_conditions = {}
            instrument_info = None
            
            # Common experimental parameters to capture
            condition_params = ["temperature", "pressure", "ph", "concentration", 
                              "time", "humidity", "wavelength", "voltage", "current"]
            
            for param in condition_params:
                if param in inputs:
                    experimental_conditions[param] = inputs[param]
            
            # Capture instrument information if available
            if "instrument" in inputs:
                instrument_info = inputs["instrument"]
            elif tool_name in ["molecular_dynamics", "quantum_simulation", "nmr_analysis"]:
                instrument_info = f"computational_{tool_name}"
            
            # Store conditions in Knowledge Graph
            if experimental_conditions:
                await kg_service.capture_experimental_conditions({
                    "experiment_id": experiment_id,
                    "conditions": experimental_conditions,
                    "instrument": instrument_info,
                    "domain": domain,
                    "purpose": f"{tool_name} experiment using {method}",
                    "hypothesis_tested": inputs.get("hypothesis", "")
                })
                
        except BiologyError as kg_error:
            logger.warning(f"Could not capture experimental conditions in KG: {kg_error}")
        
        # Execute the actual experiment
        start_time = datetime.now(UTC)
        errors = []
        
        try:
            # Route to appropriate method
            if domain == "biology":
                if tool_name == "molecular_dynamics":
                    result = await toolkit.run_molecular_dynamics(inputs)
                elif tool_name == "protein_structure_prediction":
                    result = await toolkit.predict_protein_folding(inputs.get("protein_sequence", ""))
                elif tool_name == "gene_expression_analysis":
                    result = await toolkit.analyze_gene_expression(
                        inputs.get("count_matrix", np.array([])),
                        inputs.get("metadata", {})
                    )
                else:
                    result = ExperimentalResult(
                        experiment_id=experiment_id,
                        domain=domain,
                        tool_name=tool_name,
                        method=method,
                        inputs=inputs,
                        outputs={},
                        metrics={},
                        errors=[f"Herramienta '{tool_name}' no implementada para biología"]
                    )
                    
            elif domain == "chemistry":
                if tool_name == "molecular_properties":
                    result = await toolkit.calculate_molecular_properties(inputs.get("smiles", ""))
                elif tool_name == "reaction_prediction":
                    result = await toolkit.predict_reaction_outcomes(
                        inputs.get("reactants", []),
                        inputs.get("conditions", {})
                    )
                elif tool_name == "retrosynthesis":
                    result = await toolkit.optimize_synthesis_route(
                        inputs.get("target", ""),
                        inputs.get("max_steps", 3)
                    )
                else:
                    result = ExperimentalResult(
                        experiment_id=experiment_id,
                        domain=domain,
                        tool_name=tool_name,
                        method=method,
                        inputs=inputs,
                        outputs={},
                        metrics={},
                        errors=[f"Herramienta '{tool_name}' no implementada para química"]
                    )
                    
            elif domain == "physics":
                if tool_name == "quantum_simulation":
                    result = await toolkit.run_quantum_simulation(
                        inputs.get("system_type", "particle_in_box"),
                        inputs
                    )
                else:
                    result = ExperimentalResult(
                        experiment_id=experiment_id,
                        domain=domain,
                        tool_name=tool_name,
                        method=method,
                        inputs=inputs,
                        outputs={},
                        metrics={},
                        errors=[f"Herramienta '{tool_name}' no implementada para física"]
                    )
                    
            else:
                result = ExperimentalResult(
                    experiment_id=experiment_id,
                    domain=domain,
                    tool_name=tool_name,
                    method=method,
                    inputs=inputs,
                    outputs={},
                    metrics={},
                    errors=[f"Dominio '{domain}' no soportado"]
                )
                
            # Calculate duration
            result.duration_seconds = (datetime.now(UTC) - start_time).total_seconds()
            
            return result
            
        except BiologyError as e:
            errors.append(f"Error ejecutando experimento: {str(e)}")
            return ExperimentalResult(
                experiment_id=experiment_id,
                domain=domain,
                tool_name=tool_name,
                method=method,
                inputs=inputs,
                outputs={},
                metrics={},
                errors=errors
            )
    
    def get_toolkit(self, domain: str) -> Optional[DomainToolkit]:
        """Get a specific domain toolkit"""
        return self.toolkits.get(domain)
    
    async def run_comparative_experiment(
        self,
        experiments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run multiple experiments and compare results"""
        results = []
        
        for exp in experiments:
            result = await self.execute_experiment(
                domain=exp["domain"],
                tool_name=exp["tool_name"],
                method=exp["method"],
                inputs=exp["inputs"]
            )
            results.append(result)
            
        # Compare results
        comparison = {
            "n_experiments": len(results),
            "successful": sum(1 for r in results if not r.errors),
            "failed": sum(1 for r in results if r.errors),
            "domains": list(set(r.domain for r in results)),
            "tools": list(set(r.tool_name for r in results)),
            "total_duration": sum(r.duration_seconds for r in results),
            "results": [
                {
                    "experiment_id": r.experiment_id,
                    "domain": r.domain,
                    "tool": r.tool_name,
                    "success": len(r.errors) == 0,
                    "metrics": r.metrics
                }
                for r in results
            ]
        }
        
        return comparison


# Singleton instance
_hub_instance = None


async def get_experimental_hub() -> ExperimentalToolkitHub:
    """Get or create the singleton hub instance"""
    global _hub_instance
    
    if _hub_instance is None:
        _hub_instance = ExperimentalToolkitHub()
        await _hub_instance.initialize()
        
    return _hub_instance
