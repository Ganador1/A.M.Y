"""
Structural Database Service
Integración ligera con PDB, UniProt y AlphaFold DB (solo lectura).

ASYNC MIGRATION: Migrado de requests a httpx.AsyncClient para non-blocking I/O.
Ver: ROADMAP_5_PHASE2_2_DETAILED_ANALYSIS.md

PHASE 3.2: Added circuit breakers for external structural database resilience.

Nota: Evita dependencias pesadas; usa httpx async y valida respuestas.
"""

import logging
from typing import Dict, Optional, Any
import httpx

from app.exceptions.infrastructure.database import DatabaseError
from app.services.circuit_breaker_service import CircuitBreaker, CircuitBreakerConfig
from app.types.structural_database_service_types import (
    FetchPdbResult,
    FetchUniprotResult,
    FetchAlphafoldPredictionResult,
    SearchSimilarStructuresResult,
    FetchPdbBatchResult,
    FetchUniprotBatchResult,
    FetchAlphafoldBatchResult,
)

logger = logging.getLogger(__name__)

# Global async HTTP client para structural databases
_structural_http_client: Optional[httpx.AsyncClient] = None

# Global Circuit Breakers for structural databases
_structural_circuit_breakers: Dict[str, CircuitBreaker] = {}

def get_structural_circuit_breaker(name: str) -> CircuitBreaker:
    """Get or create a circuit breaker for a structural database."""
    global _structural_circuit_breakers
    
    if name not in _structural_circuit_breakers:
        # Configuration per database
        configs = {
            "pdb": CircuitBreakerConfig(
                failure_threshold=10,
                recovery_timeout=180,
                timeout=30.0,
                max_concurrent_calls=50,
                failure_rate_threshold=0.6
            ),
            "uniprot": CircuitBreakerConfig(
                failure_threshold=10,
                recovery_timeout=180,
                timeout=30.0,
                max_concurrent_calls=50,
                failure_rate_threshold=0.6
            ),
            "alphafold": CircuitBreakerConfig(
                failure_threshold=8,
                recovery_timeout=240,
                timeout=60.0,
                max_concurrent_calls=30,
                failure_rate_threshold=0.65
            ),
        }
        
        config = configs.get(name, CircuitBreakerConfig())
        _structural_circuit_breakers[name] = CircuitBreaker(name, config)
        logger.info(f"Created structural circuit breaker '{name}'")
    
    return _structural_circuit_breakers[name]

# Global async HTTP client para structural databases
_structural_http_client: Optional[httpx.AsyncClient] = None

def get_structural_http_client() -> httpx.AsyncClient:
    """Get or create the global async HTTP client for structural databases."""
    global _structural_http_client
    if _structural_http_client is None:
        _structural_http_client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
            follow_redirects=True
        )
    return _structural_http_client

async def close_structural_http_client() -> None:
    """Close the global HTTP client. Call this on application shutdown."""
    global _structural_http_client
    if _structural_http_client is not None:
        await _structural_http_client.aclose()
        _structural_http_client = None


class StructuralDatabaseService:
    """
    Servicio de integración con bases estructurales públicas.

    - PDB: descarga PDB plano
    - UniProt: metadatos de proteína
    - AlphaFold DB: predicción PDB y confidencias si existen
    """

    def __init__(self,
                 pdb_base: str = "https://files.rcsb.org/download",
                 uniprot_base: str = "https://rest.uniprot.org/uniprotkb",
                 af_base: str = "https://alphafold.ebi.ac.uk/files"):
        self.pdb_base = pdb_base.rstrip('/')
        self.uniprot_base = uniprot_base.rstrip('/')
        self.af_base = af_base.rstrip('/')

    async def _safe_get(self, url: str, timeout: int = 20) -> Optional[httpx.Response]:
        """Async HTTP GET with error handling."""
        try:
            client = get_structural_http_client()
            resp = await client.get(url, timeout=timeout)
            if resp.status_code == 200:
                return resp
            logger.warning(f"GET {url} -> {resp.status_code}")
            return None
        except (httpx.HTTPError, DatabaseError) as e:
            logger.error(f"Request failed: {url} error={e}")
            return None

    async def fetch_pdb(self, pdb_id: str) -> FetchPdbResult:
        """
        Descarga archivo PDB (async) with circuit breaker protection.
        """
        circuit_breaker = get_structural_circuit_breaker("pdb")
        
        async def _api_call():
            pdb_id_clean = (pdb_id or '').strip().upper()
            if not pdb_id_clean:
                raise DatabaseError("PDB ID vacío")
            
            url = f"{self.pdb_base}/{pdb_id_clean}.pdb"
            resp = await self._safe_get(url)
            
            if not resp:
                raise DatabaseError(f"No encontrado PDB {pdb_id_clean}")
            
            return {"success": True, "pdb_id": pdb_id_clean, "pdb": resp.text, "source_url": url}
        
        try:
            return await circuit_breaker.call(_api_call, operation="fetch_pdb")
        except (DatabaseError, Exception) as e:
            logger.warning(f"PDB fetch failed for {pdb_id}: {e}")
            return {"success": False, "error": str(e)}

    async def fetch_uniprot(self, accession: str) -> FetchUniprotResult:
        """
        Obtiene metadatos UniProt en JSON (async) with circuit breaker protection.
        """
        circuit_breaker = get_structural_circuit_breaker("uniprot")
        
        async def _api_call():
            acc = (accession or '').strip()
            if not acc:
                raise DatabaseError("Accession vacío")
            
            url = f"{self.uniprot_base}/{acc}.json"
            resp = await self._safe_get(url)
            
            if not resp:
                raise DatabaseError(f"UniProt no encontrado {acc}")
            
            try:
                data = resp.json()
                return {"success": True, "accession": acc, "data": data}
            except DatabaseError as e:
                raise DatabaseError(f"JSON inválido: {e}") from e
        
        try:
            return await circuit_breaker.call(_api_call, operation="fetch_uniprot")
        except (DatabaseError, Exception) as e:
            logger.warning(f"UniProt fetch failed for {accession}: {e}")
            return {"success": False, "error": str(e)}

    async def fetch_alphafold_prediction(self, uniprot_id: str) -> FetchAlphafoldPredictionResult:
        """
        Descarga predicción AlphaFold con circuit breaker protection.
        """
        circuit_breaker = get_structural_circuit_breaker("alphafold")
        
        async def _api_call():
            uid = (uniprot_id or '').strip()
            if not uid:
                raise DatabaseError("UniProt ID vacío para AlphaFold")
            
            # Try to fetch AlphaFold prediction model and confidence
            pdb_url = f"{self.af_base}/AF-{uid}-F1-model_v4.pdb"
            conf_url = f"{self.af_base}/AF-{uid}-F1-confidence_v4.json"
            
            pdb_resp = await self._safe_get(pdb_url)
            if not pdb_resp:
                raise DatabaseError(f"AlphaFold prediction no disponible para {uid}")
            
            # Try to fetch confidence data (optional)
            confidence = None
            conf_resp = await self._safe_get(conf_url)
            if conf_resp:
                try:
                    confidence = conf_resp.json()
                except DatabaseError:
                    confidence = None
            
            return {
                "success": True,
                "uniprot_id": uid,
                "pdb": pdb_resp.text,
                "confidence": confidence,
                "source": {
                    "pdb_url": pdb_url,
                    "confidence_url": conf_url
                }
            }
        
        try:
            return await circuit_breaker.call(_api_call, operation="fetch_alphafold")
        except (DatabaseError, Exception) as e:
            logger.warning(f"AlphaFold fetch failed for {uniprot_id}: {e}")
            return {"success": False, "error": str(e)}

    async def search_similar_structures(self, sequence: str, identity_cutoff: float = 0.3, max_results: int = 10) -> SearchSimilarStructuresResult:
        """
        Busca estructuras PDB por similitud de secuencia usando el API de RCSB (async).

        Retorna lista de IDs PDB y scores básicos. Evita dependencias pesadas.
        """
        seq = (sequence or '').strip().upper()
        if not seq or len(seq) < 10:
            return {"success": False, "error": "Secuencia inválida (>=10 aa requeridos)"}

        # Endpoint de búsqueda por secuencia (RCSB Search API v2)
        query = {
            "query": {
                "type": "terminal",
                "service": "sequence",
                "parameters": {
                    "evalue": 1.0,
                    "identity_cutoff": float(identity_cutoff),
                    "target": "pdb_protein_sequence",
                    "value": seq
                }
            },
            "request_options": {
                "scoring_strategy": "sequence",
                "results_content_type": ["experimental"],
                "sort": [{"sort_by": "score", "direction": "desc"}],
                "pager": {"start": 0, "rows": int(max_results)}
            },
            "return_type": "entry"
        }

        try:
            client = get_structural_http_client()
            resp = await client.post("https://search.rcsb.org/rcsbsearch/v2/query?json", json=query, timeout=30)
            if resp.status_code != 200:
                return {"success": False, "error": f"Búsqueda falló: HTTP {resp.status_code}"}
            data = resp.json()
            result_set = data.get('result_set') or []
            hits = []
            for hit in result_set[:max_results]:
                identifier = hit.get('identifier')
                score = (hit.get('services') or [{}])[0].get('nodes', [{}])[0].get('meta', {}).get('score')
                hits.append({"pdb_id": identifier, "score": score})
            return {"success": True, "total": len(result_set), "hits": hits}
        except (httpx.HTTPError, DatabaseError) as e:
            logger.error(f"Fallo en sequence-search RCSB: {e}")
            return {"success": False, "error": str(e)}

    async def fetch_pdb_batch(self, pdb_ids: list[str]) -> FetchPdbBatchResult:
        """
        Fetch multiple PDB structures in parallel using asyncio.gather.

        Args:
            pdb_ids: List of PDB IDs to fetch

        Returns:
            Dictionary mapping PDB IDs to their results

        Example:
            results = await service.fetch_pdb_batch(["1CRN", "2HHB", "3NIR"])
            # Returns: {"1CRN": {...}, "2HHB": {...}, "3NIR": {...}}
        """
        import asyncio
        logger.info(f"Fetching {len(pdb_ids)} PDB structures in parallel")

        # Use asyncio.gather to fetch all PDBs concurrently
        tasks = [self.fetch_pdb(pdb_id) for pdb_id in pdb_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Map results back to PDB IDs
        result_dict = {}
        for pdb_id, result in zip(pdb_ids, results):
            if isinstance(result, Exception):
                result_dict[pdb_id] = {"success": False, "error": str(result)}
            else:
                result_dict[pdb_id] = result

        return result_dict

    async def fetch_uniprot_batch(self, accessions: list[str]) -> FetchUniprotBatchResult:
        """
        Fetch multiple UniProt entries in parallel using asyncio.gather.

        Args:
            accessions: List of UniProt accession IDs

        Returns:
            Dictionary mapping accessions to their results
        """
        import asyncio
        logger.info(f"Fetching {len(accessions)} UniProt entries in parallel")

        tasks = [self.fetch_uniprot(acc) for acc in accessions]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        result_dict = {}
        for accession, result in zip(accessions, results):
            if isinstance(result, Exception):
                result_dict[accession] = {"success": False, "error": str(result)}
            else:
                result_dict[accession] = result

        return result_dict

    async def fetch_alphafold_batch(self, uniprot_ids: list[str]) -> FetchAlphafoldBatchResult:
        """
        Fetch multiple AlphaFold predictions in parallel using asyncio.gather.

        Args:
            uniprot_ids: List of UniProt IDs

        Returns:
            Dictionary mapping UniProt IDs to their AlphaFold results
        """
        import asyncio
        logger.info(f"Fetching {len(uniprot_ids)} AlphaFold predictions in parallel")

        tasks = [self.fetch_alphafold_prediction(uid) for uid in uniprot_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        result_dict = {}
        for uniprot_id, result in zip(uniprot_ids, results):
            if isinstance(result, Exception):
                result_dict[uniprot_id] = {"success": False, "error": str(result)}
            else:
                result_dict[uniprot_id] = result

        return result_dict


