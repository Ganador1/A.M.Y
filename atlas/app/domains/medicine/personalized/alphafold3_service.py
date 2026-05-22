"""
AlphaFold 3 Protein Structure Service for AXIOM
Advanced protein structure prediction and analysis using real APIs.

Features:
- Protein structure lookup via AlphaFold DB (EBI) — FREE, no API key needed
- De-novo prediction via AlphaFold Server API — requires ALPHAFOLD_API_KEY
- Structure quality assessment from real PDB/CIF data
- Drug binding site prediction and analysis (simulated when no structural tools)
- Protein-protein interaction modeling (simulated when no structural tools)

Ethics & Safety:
- Uso responsable: predicciones computacionales, no sustituyen validación experimental
- Limitaciones: resultados probabilísticos requieren interpretación experta
- Privacidad: no enviar secuencias confidenciales sin autorización
- Citas: reconocer contribuciones de DeepMind AlphaFold
"""

import asyncio
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import hashlib
import time

import httpx
import numpy as np

from app.core.bootstrap_logging import logger
from app.exceptions.domain.medicine import MedicalError

# Optional structural biology tools
try:
    from Bio.PDB import PDBParser, PDBIO, SASA
    HAS_BIOPYTHON = True
except Exception:
    HAS_BIOPYTHON = False

try:
    import rdkit
    from rdkit import Chem
    from rdkit.Chem import Descriptors, AllChem
    HAS_RDKIT = True
except Exception:
    HAS_RDKIT = False


@dataclass
class ProteinStructure:
    """Protein structure prediction result"""
    sequence: str
    structure_id: str
    prediction_confidence: float
    plddt_scores: List[float]
    structure_data: Optional[str]
    prediction_method: str
    created_at: datetime
    source: str = "unknown"
    uniprot_id: Optional[str] = None
    pdb_url: Optional[str] = None
    cif_url: Optional[str] = None


@dataclass
class BindingSiteAnalysis:
    """Protein binding site analysis result"""
    site_id: str
    position: Tuple[float, float, float]
    confidence: float
    cavity_volume: float
    druggability_score: float
    residues_involved: List[str]


@dataclass
class ProteinInteraction:
    """Protein-protein interaction prediction"""
    protein_a: str
    protein_b: str
    interaction_confidence: float
    binding_interface_residues: List[Tuple[str, str]]
    interaction_type: str


class AlphaFold3ProteinStructureService:
    """
    AlphaFold 3 Protein Structure Prediction Service using real APIs.
    """

    def __init__(self):
        """Initialize AlphaFold 3 service"""
        logger.info("Initializing AlphaFold3ProteinStructureService")
        self.service_name = "AlphaFold3ProteinStructureService"
        self.version = "2.0.0"
        self.cache = {}
        self.max_cache_age = timedelta(hours=24)

        self.max_sequence_length = 2700
        self.min_sequence_length = 10
        self.supported_formats = ["fasta", "pdb", "json"]

        # Real API configuration
        self.alphafold_db_url = "https://alphafold.ebi.ac.uk/api/prediction"
        self.alphafold_server_url = os.environ.get("ALPHAFOLD_SERVER_URL", "https://alphafoldserver.com/api/v1")
        self.alphafold_api_key = os.environ.get("ALPHAFOLD_API_KEY", "")
        self.api_timeout = 300

        self._httpx: Optional[httpx.AsyncClient] = None

        logger.info(f"✅ {self.service_name} initialized. BioPython={HAS_BIOPYTHON}, RDKit={HAS_RDKIT}")

    async def _get_client(self) -> httpx.AsyncClient:
        if self._httpx is None or self._httpx.is_closed:
            headers = {}
            if self.alphafold_api_key:
                headers["Authorization"] = f"Bearer {self.alphafold_api_key}"
            self._httpx = httpx.AsyncClient(timeout=self.api_timeout, headers=headers)
        return self._httpx

    def _generate_structure_id(self, sequence: str) -> str:
        sequence_hash = hashlib.sha256(sequence.encode()).hexdigest()
        timestamp = int(time.time())
        return f"af3_{sequence_hash[:12]}_{timestamp}"

    def _is_valid_protein_sequence(self, sequence: str) -> Tuple[bool, str]:
        if not sequence:
            return False, "Empty sequence provided"
        clean_sequence = ''.join(sequence.split()).upper()
        if len(clean_sequence) < self.min_sequence_length:
            return False, f"Sequence too short (minimum {self.min_sequence_length} residues)"
        if len(clean_sequence) > self.max_sequence_length:
            return False, f"Sequence too long (maximum {self.max_sequence_length} residues)"
        valid_amino_acids = set("ACDEFGHIKLMNPQRSTVWY")
        invalid_chars = set(clean_sequence) - valid_amino_acids
        if invalid_chars:
            return False, f"Invalid amino acid codes: {invalid_chars}"
        return True, clean_sequence

    async def _fetch_alphafold_db(self, uniprot_id: str) -> Optional[Dict[str, Any]]:
        """Fetch existing prediction from AlphaFold DB (EBI)."""
        client = await self._get_client()
        url = f"{self.alphafold_db_url}/{uniprot_id}"
        try:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                # EBI returns a list of predictions
                if isinstance(data, list) and len(data) > 0:
                    entry = data[0]
                    return {
                        "success": True,
                        "source": "alphafold_db_ebi",
                        "structure_id": entry.get("entryId", uniprot_id),
                        "uniprot_id": uniprot_id,
                        "confidence": entry.get("confidenceScore", 0.0),
                        "pdb_url": entry.get("pdbUrl"),
                        "cif_url": entry.get("cifUrl"),
                        "sequence": entry.get("sequence"),
                        "plddt_scores": entry.get("plddt", []),
                    }
            elif resp.status_code == 404:
                logger.info("AlphaFold DB: no entry found for %s", uniprot_id)
            else:
                logger.warning("AlphaFold DB returned %s for %s", resp.status_code, uniprot_id)
        except Exception as e:
            logger.warning("AlphaFold DB fetch failed: %s", e)
        return None

    async def _fetch_pdb_text(self, pdb_url: str) -> Optional[str]:
        """Download PDB text from URL."""
        if not pdb_url:
            return None
        client = await self._get_client()
        try:
            resp = await client.get(pdb_url, timeout=60)
            if resp.status_code == 200:
                return resp.text
        except Exception as e:
            logger.warning("Failed to fetch PDB from %s: %s", pdb_url, e)
        return None

    async def _submit_alphafold_server(self, sequence: str) -> Optional[Dict[str, Any]]:
        """Submit sequence to AlphaFold Server API (requires API key)."""
        if not self.alphafold_api_key:
            return None
        client = await self._get_client()
        url = f"{self.alphafold_server_url}/predict"
        payload = {
            "sequence": sequence,
            "model": "alphafold3",
        }
        try:
            resp = await client.post(url, json=payload)
            if resp.status_code in (200, 202):
                data = resp.json()
                return {
                    "success": True,
                    "source": "alphafold_server",
                    "job_id": data.get("job_id"),
                    "structure_id": data.get("structure_id", self._generate_structure_id(sequence)),
                    "confidence": data.get("confidence", 0.0),
                    "plddt_scores": data.get("plddt_scores", []),
                    "pdb_data": data.get("pdb_data"),
                    "status": data.get("status", "submitted"),
                }
            else:
                logger.warning("AlphaFold Server returned %s: %s", resp.status_code, resp.text)
        except Exception as e:
            logger.warning("AlphaFold Server submission failed: %s", e)
        return None

    async def predict_protein_structure(self, sequence: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Predict protein structure using AlphaFold DB lookup or AlphaFold Server API.
        """
        options = options or {}
        try:
            logger.info(f"Starting protein structure prediction for sequence of length {len(sequence)}")
            is_valid, clean_sequence_or_error = self._is_valid_protein_sequence(sequence)
            if not is_valid:
                return {'success': False, 'error': clean_sequence_or_error}
            clean_sequence = clean_sequence_or_error

            cache_key = hashlib.sha256(clean_sequence.encode()).hexdigest()
            if cache_key in self.cache:
                cached = self.cache[cache_key]
                if datetime.now() - cached['timestamp'] < self.max_cache_age:
                    logger.info("Returning cached prediction result")
                    return {'success': True, 'data': cached['data'], 'cached': True}

            uniprot_id = options.get("uniprot_id")
            prediction_result: Optional[Dict[str, Any]] = None

            # 1. Try AlphaFold DB if uniprot_id provided
            if uniprot_id:
                prediction_result = await self._fetch_alphafold_db(uniprot_id)

            # 2. Try AlphaFold Server API if no DB result and API key exists
            if not prediction_result and self.alphafold_api_key:
                prediction_result = await self._submit_alphafold_server(clean_sequence)

            # 3. If still nothing, return informative error
            if not prediction_result:
                return {
                    'success': False,
                    'error': (
                        'No structure found in AlphaFold DB and AlphaFold Server API key not configured. '
                        'Provide uniprot_id in options or set ALPHAFOLD_API_KEY environment variable.'
                    )
                }

            # Fetch PDB data if URL available but no raw data
            pdb_data = prediction_result.get("pdb_data")
            pdb_url = prediction_result.get("pdb_url")
            if not pdb_data and pdb_url:
                pdb_data = await self._fetch_pdb_text(pdb_url)

            plddt = prediction_result.get("plddt_scores", [])
            if not plddt and pdb_data:
                # Try to extract pLDDT from B-factors in PDB
                plddt = self._extract_plddt_from_pdb(pdb_data)

            confidence = prediction_result.get("confidence", 0.0)
            if not confidence and plddt:
                confidence = float(np.mean(plddt))

            structure = ProteinStructure(
                sequence=clean_sequence,
                structure_id=prediction_result.get("structure_id", self._generate_structure_id(clean_sequence)),
                prediction_confidence=confidence,
                plddt_scores=plddt,
                structure_data=pdb_data,
                prediction_method="AlphaFold 3",
                created_at=datetime.now(),
                source=prediction_result.get("source", "unknown"),
                uniprot_id=uniprot_id or prediction_result.get("uniprot_id"),
                pdb_url=pdb_url,
                cif_url=prediction_result.get("cif_url"),
            )

            self.cache[cache_key] = {'data': structure, 'timestamp': datetime.now()}

            return {
                'success': True,
                'data': {
                    'structure': asdict(structure),
                    'quality_assessment': {
                        'overall_confidence': confidence,
                        'high_confidence_residues': sum(1 for s in plddt if s > 80),
                        'medium_confidence_residues': sum(1 for s in plddt if 60 <= s <= 80),
                        'low_confidence_residues': sum(1 for s in plddt if s < 60),
                    },
                    'processing_info': {
                        'sequence_length': len(clean_sequence),
                        'method': "AlphaFold 3",
                        'source': structure.source,
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error in protein structure prediction: {e}")
            return {'success': False, 'error': str(e)}

    def _extract_plddt_from_pdb(self, pdb_text: str) -> List[float]:
        """Extract pLDDT scores from PDB B-factors."""
        scores = []
        for line in pdb_text.splitlines():
            if line.startswith("ATOM  ") and line[12:16].strip() == "CA":
                try:
                    bfactor = float(line[60:66].strip())
                    scores.append(bfactor)
                except ValueError:
                    pass
        return scores

    async def analyze_binding_sites(self, structure_id: str, options: Optional[Dict] = None) -> Dict[str, Any]:
        """Analyze potential binding sites. Falls back to simulation if no structural tools."""
        try:
            logger.info(f"Analyzing binding sites for structure {structure_id}")
            structure = self._find_cached_structure(structure_id)
            if not structure:
                return {'success': False, 'error': f'Structure {structure_id} not found. Run prediction first.'}

            if HAS_BIOPYTHON and structure.structure_data:
                return await self._analyze_binding_sites_real(structure, options)
            else:
                return await self._analyze_binding_sites_simulated(structure, options)
        except Exception as e:
            logger.error(f"Error in binding site analysis: {e}")
            return {'success': False, 'error': str(e)}

    async def _analyze_binding_sites_real(self, structure: ProteinStructure, options: Optional[Dict]) -> Dict[str, Any]:
        """Real binding site analysis using BioPython SASA."""
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(mode="w", suffix=".pdb", delete=False) as f:
                f.write(structure.structure_data or "")
                tmp_path = f.name

            parser = PDBParser(QUIET=True)
            model = parser.get_structure("af3", tmp_path)[0]
            sr = SASA.ShrakeRupley()
            sr.compute(model, level="R")

            # Exposed residues with high SASA are potential binding sites
            exposed = []
            for residue in model.get_residues():
                if residue.id[0] == ' ':
                    sasa = residue.sasa
                    if sasa and sasa > 30.0:
                        exposed.append({
                            "residue": residue.resname,
                            "chain": residue.parent.id,
                            "number": residue.id[1],
                            "sasa": round(sasa, 2),
                        })

            os.unlink(tmp_path)

            # Cluster exposed residues into pockets (naive clustering by sequence proximity)
            pockets = []
            if exposed:
                exposed.sort(key=lambda r: r["number"])
                current = [exposed[0]]
                for res in exposed[1:]:
                    if res["number"] - current[-1]["number"] <= 4:
                        current.append(res)
                    else:
                        pockets.append(current)
                        current = [res]
                pockets.append(current)

            binding_sites = []
            for i, pocket in enumerate(pockets[:5]):
                residues = [f"{r['residue']}{r['number']}" for r in pocket]
                binding_sites.append({
                    "site_id": f"site_{i+1}",
                    "residues_involved": residues,
                    "confidence": round(min(0.5 + len(pocket) * 0.02, 0.95), 2),
                    "cavity_volume": round(len(pocket) * 12.5, 2),
                    "druggability_score": round(min(0.4 + len(pocket) * 0.03, 0.9), 2),
                    "sasa_avg": round(sum(r["sasa"] for r in pocket) / len(pocket), 2),
                })

            return {
                'success': True,
                'data': {
                    'structure_id': structure.structure_id,
                    'binding_sites': binding_sites,
                    'analysis_summary': {
                        'total_sites_found': len(binding_sites),
                        'high_confidence_sites': sum(1 for s in binding_sites if s["confidence"] > 0.8),
                        'druggable_sites': sum(1 for s in binding_sites if s["druggability_score"] > 0.6),
                    },
                    'method': 'biopython_sasa'
                }
            }
        except Exception as e:
            logger.warning("Real binding site analysis failed, falling back to simulation: %s", e)
            return await self._analyze_binding_sites_simulated(structure, options)

    async def _analyze_binding_sites_simulated(self, structure: ProteinStructure, options: Optional[Dict]) -> Dict[str, Any]:
        return {
            'success': False,
            'error': (
                'Binding site simulation disabled. Install BioPython and provide a PDB structure '
                'to enable real binding site analysis using SASA.'
            )
        }

    async def predict_protein_interaction(self, sequence_a: str, sequence_b: str) -> Dict[str, Any]:
        """Predict protein-protein interaction. Currently requires external tools."""
        try:
            valid_a, clean_a = self._is_valid_protein_sequence(sequence_a)
            if not valid_a:
                return {'success': False, 'error': f"Invalid sequence A: {clean_a}"}
            valid_b, clean_b = self._is_valid_protein_sequence(sequence_b)
            if not valid_b:
                return {'success': False, 'error': f"Invalid sequence B: {clean_b}"}

            return {
                'success': False,
                'error': (
                    'Protein-protein interaction prediction requires specialized docking tools '
                    '(e.g., HADDOCK, ClusPro, or AlphaFold-Multimer) not available in this environment. '
                    'Use predict_protein_structure for individual structures first.'
                )
            }
        except Exception as e:
            logger.error(f"Error in protein interaction prediction: {e}")
            return {'success': False, 'error': str(e)}

    async def get_structure_quality_metrics(self, structure_id: str) -> Dict[str, Any]:
        """Get detailed quality metrics for a predicted structure."""
        try:
            structure = self._find_cached_structure(structure_id)
            if not structure:
                return {'success': False, 'error': f'Structure {structure_id} not found in cache.'}

            plddt = structure.plddt_scores or []
            if not plddt and structure.structure_data:
                plddt = self._extract_plddt_from_pdb(structure.structure_data)

            if not plddt:
                return {'success': False, 'error': 'No quality scores available for this structure.'}

            mean_plddt = float(np.mean(plddt))
            metrics = {
                'structure_id': structure_id,
                'overall_confidence': structure.prediction_confidence or mean_plddt,
                'plddt_distribution': {
                    'mean': mean_plddt,
                    'min': float(min(plddt)),
                    'max': float(max(plddt)),
                    'std': float(np.std(plddt)),
                },
                'confidence_regions': {
                    'very_high': sum(1 for s in plddt if s > 90),
                    'high': sum(1 for s in plddt if 80 <= s <= 90),
                    'medium': sum(1 for s in plddt if 60 <= s < 80),
                    'low': sum(1 for s in plddt if s < 60),
                },
                'structural_assessment': {
                    'reliable_domains': sum(1 for s in plddt if s > 80) / len(plddt),
                    'disorder_regions': sum(1 for s in plddt if s < 50) / len(plddt),
                },
                'source': structure.source,
            }
            return {'success': True, 'data': metrics}
        except Exception as e:
            logger.error(f"Error getting structure quality metrics: {e}")
            return {'success': False, 'error': str(e)}

    async def predict_complex(self, chains: List[Dict[str, str]]) -> Dict[str, Any]:
        """Predict multi-chain complex. Requires AlphaFold-Multimer or AlphaFold Server."""
        try:
            if not chains or len(chains) < 2:
                return {'success': False, 'error': 'At least 2 chains required for complex prediction'}
            if len(chains) > 10:
                return {'success': False, 'error': 'Maximum 10 chains supported'}
            for i, chain in enumerate(chains):
                if 'sequence' not in chain or 'type' not in chain:
                    return {'success': False, 'error': f'Chain {i+1} missing sequence or type'}
                ct = chain['type'].lower()
                if ct not in ['protein', 'dna', 'rna']:
                    return {'success': False, 'error': f'Unsupported chain type: {ct}'}
                if ct == 'protein':
                    valid, msg = self._is_valid_protein_sequence(chain['sequence'])
                    if not valid:
                        return {'success': False, 'error': f'Chain {i+1}: {msg}'}

            if self.alphafold_api_key:
                client = await self._get_client()
                url = f"{self.alphafold_server_url}/predict_complex"
                payload = {"chains": chains}
                try:
                    resp = await client.post(url, json=payload)
                    if resp.status_code in (200, 202):
                        data = resp.json()
                        return {
                            'success': True,
                            'data': data,
                            'source': 'alphafold_server',
                        }
                except Exception as e:
                    logger.warning("AlphaFold Server complex prediction failed: %s", e)

            return {
                'success': False,
                'error': (
                    'Complex prediction requires AlphaFold Server API key (ALPHAFOLD_API_KEY) '
                    'or local AlphaFold-Multimer installation.'
                )
            }
        except Exception as e:
            logger.error(f"Error in complex prediction: {e}")
            return {'success': False, 'error': str(e)}

    def _find_cached_structure(self, structure_id: str) -> Optional[ProteinStructure]:
        for cached in self.cache.values():
            data = cached.get('data')
            if isinstance(data, ProteinStructure) and data.structure_id == structure_id:
                return data
        return None
