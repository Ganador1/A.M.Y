"""
Servicio de Química Computacional para AXIOM
Integra RDKit, Biopython y PySCF para análisis molecular y química cuántica
"""

from typing import Dict, Any, List, Optional, Union
import logging
import json
import numpy as np
from app.services.base_service import BaseService, ScientificServiceMixin
from app.exceptions.domain.chemistry import ChemistryError

logger = logging.getLogger(__name__)


class ComputationalChemistryService(BaseService, ScientificServiceMixin):
    """Servicio para análisis de química computacional"""

    def __init__(self):
        super().__init__("computational_chemistry")

    def _initialize_libraries(self) -> None:
        """Inicializar bibliotecas de química computacional"""
        # Verificar disponibilidad sin importar inicialmente
        self._available_libraries = {
            "rdkit": self.check_library_availability("rdkit"),
            "biopython": self.check_library_availability("Bio"),
            "pyscf": self.check_library_availability("pyscf"),
            "numpy": self.check_library_availability("numpy"),
        }
        
        # Solo inicializar las que están disponibles
        if self._available_libraries["numpy"]:
            import numpy as np
            self.np = np
        else:
            self.np = None

    def _lazy_import_rdkit(self):
        """Importación lazy de RDKit para evitar lentitud en inicio"""
        if not hasattr(self, '_rdkit_imported'):
            if self._available_libraries["rdkit"]:
                try:
                    from rdkit import Chem
                    from rdkit.Chem import AllChem, Descriptors
                    self.Chem = Chem
                    self.AllChem = AllChem
                    self.Descriptors = Descriptors
                    self._rdkit_imported = True
                    return True
                except ImportError as e:
                    logger.error(f"Error importing RDKit: {e}")
                    self._available_libraries["rdkit"] = False
                    return False
            return False
        return True

    def _lazy_import_biopython(self):
        """Importación lazy de Biopython"""
        if not hasattr(self, '_biopython_imported'):
            if self._available_libraries["biopython"]:
                try:
                    from Bio.Seq import Seq
                    from Bio import SeqUtils
                    from Bio.SeqUtils import molecular_weight
                    self.Seq = Seq
                    self.SeqUtils = SeqUtils
                    self.molecular_weight = molecular_weight
                    self._biopython_imported = True
                    return True
                except ImportError as e:
                    logger.error(f"Error importing Biopython: {e}")
                    self._available_libraries["biopython"] = False
                    return False
            return False
        return True

    def _lazy_import_pyscf(self):
        """Importación lazy de PySCF"""
        if not hasattr(self, '_pyscf_imported'):
            if self._available_libraries["pyscf"]:
                try:
                    from pyscf import gto, scf
                    self.gto = gto
                    self.scf = scf
                    self._pyscf_imported = True
                    return True
                except ImportError as e:
                    logger.error(f"Error importing PySCF: {e}")
                    self._available_libraries["pyscf"] = False
                    return False
            return False
        return True

import logging
from typing import Dict, Any, List, Optional
from app.services.base_service import BaseService
from app.models import BaseResponse

logger = logging.getLogger(__name__)

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors, Draw
    import rdkit
    RDKIT_AVAILABLE = True
except ImportError:
    RDKIT_AVAILABLE = False
    logger.warning("RDKit not available")

try:
    from Bio import SeqIO, AlignIO
    from Bio.Seq import Seq
    from Bio.SeqRecord import SeqRecord
    import Bio
    BIOPYTHON_AVAILABLE = True
except ImportError:
    BIOPYTHON_AVAILABLE = False
    logger.warning("Biopython not available")

try:
    import pyscf
    from pyscf import gto, scf, dft
    PYSCF_AVAILABLE = True
except ImportError:
    PYSCF_AVAILABLE = False
    logger.warning("PySCF not available")


class ComputationalChemistryService(BaseService):
    """Service for computational chemistry operations"""

    def __init__(self):
        super().__init__()
        self.rdkit_available = RDKIT_AVAILABLE
        self.biopython_available = BIOPYTHON_AVAILABLE
        self.pyscf_available = PYSCF_AVAILABLE

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
                    "molecular_weight": sum([self._nucleotide_weight(nt) for nt in sequence])
                }

            elif sequence_type.lower() == "protein":
                seq = Seq(sequence)
                molecular_weight = sum([self._amino_acid_weight(aa) for aa in sequence])

                return {
                    "sequence": sequence,
                    "type": "Protein",
                    "length": len(sequence),
                    "molecular_weight": molecular_weight,
                    "hydrophobic_residues": sum([1 for aa in sequence if aa in 'AILMFWYV']),
                    "charged_residues": sum([1 for aa in sequence if aa in 'DEKRH'])
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
