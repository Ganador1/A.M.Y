"""
AXIOM Astronomy - Conector de Datos Astronómicos
===============================================

Conector unificado para acceder a principales APIs y bases de datos astronómicas:
- SIMBAD (CDS)
- VizieR (CDS) 
- ESA Gaia Archive
- NASA Exoplanet Archive
- TESS Data Archive
- MAST (Mikulski Archive for Space Telescopes)
- ESO Archive

Proporciona interfaz simplificada y manejo robusto de errores para
acceso programático a datos astronómicos reales.

Autor: AXIOM Development Team
Fecha: Septiembre 2025
Versión: 1.0.0
"""

import requests
import json
import time
import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import warnings
from datetime import datetime, timedelta
import aiofiles
import httpx

# Configurar logging
logger = logging.getLogger(__name__)

# Suprimir warnings de astroquery para logging limpio
warnings.filterwarnings('ignore', module='astroquery')

@dataclass
class QueryResult:
    """Resultado de consulta a API astronómica."""
    service: str
    query: str
    data: Any
    metadata: Dict[str, Any]
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None

@dataclass
class ObjectInfo:
    """Información básica de objeto astronómico."""
    object_id: str
    ra: float
    dec: float
    proper_motion_ra: Optional[float] = None
    proper_motion_dec: Optional[float] = None
    parallax: Optional[float] = None
    magnitude_v: Optional[float] = None
    spectral_type: Optional[str] = None
    source_catalog: str = "unknown"

class AstronomicalDataConnector:
    """
    Conector unificado para APIs y bases de datos astronómicas.
    
    Proporciona acceso simplificado a:
    - Catálogos de objetos (SIMBAD, Gaia)
    - Datos de misiones espaciales (TESS, Kepler, Hubble)
    - Archives especializados (Exoplanetas, Variables)
    - Servicios de queries (VizieR, TAP)
    """
    
    def __init__(self, cache_dir: Optional[str] = None, timeout: int = 30):
        """
        Inicializa el conector de datos astronómicos.
        
        Args:
            cache_dir: Directorio para cache local
            timeout: Timeout para requests HTTP
        """
        self.timeout = timeout
        self.cache_dir = Path(cache_dir or "./axiom_data_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # URLs de servicios principales
        self.service_urls = {
            'simbad_tap': 'https://simbad.u-strasbg.fr/simbad/sim-tap/sync',
            'vizier': 'https://vizier.cds.unistra.fr/viz-bin/votable',
            'gaia_tap': 'https://gea.esac.esa.int/tap-server/tap/sync',
            'nasa_exoplanet': 'https://exoplanetarchive.ipac.caltech.edu/TAP/sync',
            'mast_api': 'https://mast.stsci.edu/api/v0.1/',
            'esa_archive': 'https://archives.esac.esa.int/ehst-sl-server/servlet/data-action',
            'tess_mast': 'https://archive.stsci.edu/tess/'
        }
        
        # Headers por defecto
        self.headers = {
            'User-Agent': 'AXIOM-Astronomy-System/1.0',
            'Accept': 'application/json, text/plain, application/x-votable+xml'
        }
        
        # Cache de sessiones para performance
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Estadísticas de uso
        self.query_stats = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'cached_results': 0
        }
        
        logger.info("AstronomicalDataConnector inicializado")
    
    def _make_request(self, url: str, params: Optional[Dict] = None, method: str = 'GET') -> requests.Response:
        """Hace request HTTP con manejo de errores (sync)."""
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, timeout=self.timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, data=params, timeout=self.timeout)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
            
            response.raise_for_status()
            self.query_stats['successful_queries'] += 1
            return response
            
        except requests.exceptions.RequestException as e:
            self.query_stats['failed_queries'] += 1
            logger.error(f"Error en request a {url}: {e}")
            raise
        finally:
            self.query_stats['total_queries'] += 1
    
    async def _make_request_async(self, url: str, params: Optional[Dict] = None, method: str = 'GET') -> aiohttp.ClientResponse:
        """Hace request HTTP async con manejo de errores."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                if method.upper() == 'GET':
                    response = await session.get(url, params=params)
                elif method.upper() == 'POST':
                    response = await session.post(url, data=params)
                else:
                    raise ValueError(f"Método HTTP no soportado: {method}")
                
                response.raise_for_status()
                self.query_stats['successful_queries'] += 1
                return response
                
        except aiohttp.ClientError as e:
            self.query_stats['failed_queries'] += 1
            logger.error(f"Error en request async a {url}: {e}")
            raise
        finally:
            self.query_stats['total_queries'] += 1
    
    def _cache_key(self, service: str, query: str) -> str:
        """Genera clave de cache para query."""
        import hashlib
        key_string = f"{service}_{query}"
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[QueryResult]:
        """Recupera resultado de cache si está disponible y vigente."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with aiofiles.open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                
                # Verificar si el cache no ha expirado (24 horas)
                cached_time = datetime.fromisoformat(cached_data['timestamp'])
                if datetime.now() - cached_time < timedelta(hours=24):
                    self.query_stats['cached_results'] += 1
                    return QueryResult(**cached_data)
                    
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"Cache corrupto para {cache_key}: {e}")
                cache_file.unlink()  # Eliminar cache corrupto
        
        return None
    
    def _save_to_cache(self, cache_key: str, result: QueryResult):
        """Guarda resultado en cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            # Preparar datos para serialización
            cache_data = {
                'service': result.service,
                'query': result.query,
                'data': result.data if isinstance(result.data, (dict, list)) else str(result.data),
                'metadata': result.metadata,
                'timestamp': result.timestamp.isoformat(),
                'success': result.success,
                'error_message': result.error_message
            }
            
            with aiofiles.open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2, default=str)
                
        except Exception as e:
            logger.warning(f"No se pudo guardar en cache: {e}")
    
    # SIMBAD Queries
    async def query_simbad(self, object_name: str, fields: Optional[List[str]] = None) -> QueryResult:
        """
        Consulta información básica de objeto en SIMBAD.
        
        Args:
            object_name: Nombre del objeto astronómico
            fields: Campos específicos a obtener
            
        Returns:
            QueryResult con información del objeto
        """
        if fields is None:
            fields = ['main_id', 'ra', 'dec', 'pmra', 'pmdec', 'plx', 'mag_V', 'sp_type']
        
        query = f"""
        SELECT {', '.join(fields)}
        FROM basic 
        WHERE main_id = '{object_name}'
        """
        
        return await self._execute_tap_query('simbad', query, self.service_urls['simbad_tap'])
    
    def query_simbad_region(self, ra: float, dec: float, radius: float, mag_limit: float = 15.0) -> QueryResult:
        """
        Consulta objetos en región del cielo en SIMBAD.
        
        Args:
            ra, dec: Coordenadas del centro (grados)
            radius: Radio de búsqueda (grados)
            mag_limit: Límite de magnitud
            
        Returns:
            QueryResult con objetos en la región
        """
        query = f"""
        SELECT main_id, ra, dec, pmra, pmdec, mag_V, sp_type
        FROM basic 
        WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {ra}, {dec}, {radius})) = 1
        AND mag_V < {mag_limit}
        """
        
        return self._execute_tap_query('simbad_region', query, self.service_urls['simbad_tap'])
    
    # Gaia Archive Queries
    def query_gaia_dr3(self, source_id: Optional[str] = None, ra: Optional[float] = None, 
                       dec: Optional[float] = None, radius: Optional[float] = None, 
                       mag_limit: float = 16.0) -> QueryResult:
        """
        Consulta Gaia Data Release 3.
        
        Args:
            source_id: ID específico de fuente Gaia
            ra, dec: Coordenadas para búsqueda regional
            radius: Radio de búsqueda (grados)
            mag_limit: Límite de magnitud G
            
        Returns:
            QueryResult con datos Gaia
        """
        if source_id:
            query = f"""
            SELECT source_id, ra, dec, pmra, pmdec, parallax,
                   phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag,
                   teff_gspphot, logg_gspphot, mh_gspphot,
                   radius_gspphot, lum_gspphot
            FROM gaiadr3.gaia_source 
            WHERE source_id = {source_id}
            """
        elif ra is not None and dec is not None and radius is not None:
            query = f"""
            SELECT source_id, ra, dec, pmra, pmdec, parallax,
                   phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag,
                   teff_gspphot, logg_gspphot, mh_gspphot,
                   radius_gspphot, lum_gspphot
            FROM gaiadr3.gaia_source 
            WHERE CONTAINS(POINT('ICRS', ra, dec), CIRCLE('ICRS', {ra}, {dec}, {radius})) = 1
            AND phot_g_mean_mag < {mag_limit}
            LIMIT 1000
            """
        else:
            raise ValueError("Debe proporcionar source_id o coordenadas (ra, dec, radius)")
        
        return self._execute_tap_query('gaia_dr3', query, self.service_urls['gaia_tap'])
    
    # NASA Exoplanet Archive
    def query_exoplanet_archive(self, planet_name: Optional[str] = None, 
                               stellar_host: Optional[str] = None,
                               min_year: Optional[int] = None) -> QueryResult:
        """
        Consulta NASA Exoplanet Archive.
        
        Args:
            planet_name: Nombre del planeta
            stellar_host: Nombre de la estrella host
            min_year: Año mínimo de descubrimiento
            
        Returns:
            QueryResult con datos de exoplanetas
        """
        conditions = []
        
        if planet_name:
            conditions.append(f"pl_name = '{planet_name}'")
        if stellar_host:
            conditions.append(f"hostname = '{stellar_host}'")
        if min_year:
            conditions.append(f"disc_year >= {min_year}")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
        SELECT pl_name, hostname, pl_orbper, pl_rade, pl_masse, pl_eqt,
               st_teff, st_rad, st_mass, st_met, disc_year, disc_facility
        FROM ps 
        WHERE {where_clause}
        AND default_flag = 1
        """
        
        return self._execute_tap_query('nasa_exoplanet', query, self.service_urls['nasa_exoplanet'])
    
    def get_confirmed_exoplanets(self, discovery_year: int = 2020) -> QueryResult:
        """Obtiene lista de exoplanetas confirmados desde año específico."""
        query = f"""
        SELECT pl_name, hostname, pl_orbper, pl_rade, pl_masse, pl_eqt,
               st_teff, st_rad, st_mass, disc_year, disc_facility
        FROM ps 
        WHERE disc_year >= {discovery_year}
        AND pl_rade IS NOT NULL 
        AND pl_masse IS NOT NULL
        AND default_flag = 1
        ORDER BY disc_year DESC, pl_name
        """
        
        return self._execute_tap_query('confirmed_exoplanets', query, self.service_urls['nasa_exoplanet'])
    
    # TESS Data Access
    def search_tess_observations(self, target_name: Optional[str] = None, 
                                tic_id: Optional[str] = None,
                                ra: Optional[float] = None, 
                                dec: Optional[float] = None) -> QueryResult:
        """
        Busca observaciones TESS para un objetivo.
        
        Args:
            target_name: Nombre del objetivo
            tic_id: TESS Input Catalog ID
            ra, dec: Coordenadas
            
        Returns:
            QueryResult con información de observaciones TESS
        """
        try:
            # Intentar usar astroquery.mast si está disponible
            from astroquery.mast import Observations
            
            if tic_id:
                observations = Observations.query_criteria(
                    project="TESS",
                    obs_id=f"*{tic_id}*"
                )
            elif target_name:
                observations = Observations.query_object(
                    target_name,
                    project="TESS"
                )
            elif ra is not None and dec is not None:
                observations = Observations.query_region(
                    coordinates=f"{ra} {dec}",
                    radius="0.01 deg",
                    project="TESS"
                )
            else:
                raise ValueError("Debe proporcionar target_name, tic_id, o coordenadas")
            
            # Convertir a formato estándar
            data = observations.to_pandas() if hasattr(observations, 'to_pandas') else observations
            
            return QueryResult(
                service='tess_observations',
                query=f"TESS search for {target_name or tic_id or f'{ra},{dec}'}",
                data=data,
                metadata={'total_observations': len(observations)},
                timestamp=datetime.now(),
                success=True
            )
            
        except ImportError:
            logger.warning("astroquery no disponible, usando API directa")
            return self._search_tess_direct(target_name, tic_id, ra, dec)
        except Exception as e:
            logger.error(f"Error buscando observaciones TESS: {e}")
            return QueryResult(
                service='tess_observations',
                query="TESS search failed",
                data=None,
                metadata={},
                timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )
    
    def _search_tess_direct(self, target_name: Optional[str] = None, 
                           tic_id: Optional[str] = None,
                           ra: Optional[float] = None, 
                           dec: Optional[float] = None) -> QueryResult:
        """Búsqueda directa en MAST API para TESS."""
        base_url = "https://mast.stsci.edu/api/v0.1/invoke"
        
        if target_name:
            params = {
                'service': 'Mast.Name.Lookup',
                'params': json.dumps({'input': target_name, 'format': 'json'}),
                'format': 'json'
            }
        else:
            # Para búsquedas por coordenadas o TIC ID
            params = {
                'service': 'Mast.Catalogs.Filtered.Tic',
                'params': json.dumps({
                    'columns': 'ID,ra,dec,pmRA,pmDEC,plx,Tmag,Teff',
                    'filters': [
                        {'paramName': 'Tmag', 'values': [{'min': 0, 'max': 16}]}
                    ]
                }),
                'format': 'json'
            }
        
        try:
            response = self._make_request(base_url, params=params, method='POST')
            data = response.json()
            
            return QueryResult(
                service='tess_direct_search',
                query="Direct TESS search",
                data=data.get('data', []),
                metadata={'status': data.get('status', 'unknown')},
                timestamp=datetime.now(),
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error en búsqueda directa TESS: {e}")
            return QueryResult(
                service='tess_direct_search',
                query="Direct TESS search failed",
                data=None,
                metadata={},
                timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )
    
    # Utilidades generales
    async def _execute_tap_query(self, service_name: str, query: str, tap_url: str) -> QueryResult:
        """Ejecuta query TAP (Table Access Protocol) de forma async."""
        cache_key = self._cache_key(service_name, query)
        
        # Verificar cache primero
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
        
        params = {
            'REQUEST': 'doQuery',
            'LANG': 'ADQL',
            'FORMAT': 'json',
            'QUERY': query
        }
        
        try:
            response = await self._make_request_async(tap_url, params=params, method='POST')
            
            # Parsear respuesta según formato
            if 'json' in response.headers.get('content-type', ''):
                data = await response.json()
            else:
                # Para VOTable o texto plano
                data = await response.text()
            
            result = QueryResult(
                service=service_name,
                query=query,
                data=data,
                metadata={'response_format': response.headers.get('content-type')},
                timestamp=datetime.now(),
                success=True
            )
            
            # Guardar en cache
            self._save_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error ejecutando TAP query en {service_name}: {e}")
            return QueryResult(
                service=service_name,
                query=query,
                data=None,
                metadata={},
                timestamp=datetime.now(),
                success=False,
                error_message=str(e)
            )
    
    async def cross_match_objects(self, object_list: List[str], catalogs: Optional[List[str]] = None) -> Dict[str, Dict]:
        """
        Cross-match de objetos entre múltiples catálogos.
        
        Args:
            object_list: Lista de nombres de objetos
            catalogs: Lista de catálogos a consultar ['simbad', 'gaia', 'exoplanet']
            
        Returns:
            Dict con información consolidada por objeto
        """
        if catalogs is None:
            catalogs = ['simbad', 'gaia']
        
        results = {}
        
        for obj_name in object_list:
            obj_results = {'object_name': obj_name}
            
            # Consultar cada catálogo
            for catalog in catalogs:
                try:
                    if catalog == 'simbad':
                        result = self.query_simbad(obj_name)
                        if result.success and result.data:
                            obj_results['simbad'] = result.data
                    
                    elif catalog == 'gaia':
                        # Primero obtener coordenadas de SIMBAD
                        if 'simbad' in obj_results:
                            simbad_data = obj_results['simbad']
                            if 'data' in simbad_data and simbad_data['data']:
                                coords = simbad_data['data'][0]  # Primer resultado
                                gaia_result = self.query_gaia_dr3(
                                    ra=coords.get('ra'),
                                    dec=coords.get('dec'),
                                    radius=0.01  # 0.01 grados ~ 36 arcsec
                                )
                                if gaia_result.success:
                                    obj_results['gaia'] = gaia_result.data
                    
                    elif catalog == 'exoplanet':
                        exo_result = self.query_exoplanet_archive(stellar_host=obj_name)
                        if exo_result.success and exo_result.data:
                            obj_results['exoplanets'] = exo_result.data
                            
                except Exception as e:
                    logger.warning(f"Error consultando {catalog} para {obj_name}: {e}")
                    obj_results[f'{catalog}_error'] = str(e)
            
            results[obj_name] = obj_results
            
            # Pausa para evitar sobrecargar servicios
            await asyncio.sleep(0.5)
        
        return results
    
    async def get_object_summary(self, object_name: str) -> ObjectInfo:
        """Obtiene resumen consolidado de información de objeto."""
        # Consultar SIMBAD primero
        simbad_result = await self.query_simbad(object_name)
        
        if not simbad_result.success or not simbad_result.data:
            raise ValueError(f"Objeto {object_name} no encontrado en SIMBAD")
        
        # Extraer información básica
        simbad_data = simbad_result.data
        if 'data' in simbad_data and simbad_data['data']:
            obj_data = simbad_data['data'][0]
            
            return ObjectInfo(
                object_id=obj_data.get('main_id', object_name),
                ra=float(obj_data.get('ra', 0)),
                dec=float(obj_data.get('dec', 0)),
                proper_motion_ra=obj_data.get('pmra'),
                proper_motion_dec=obj_data.get('pmdec'),
                parallax=obj_data.get('plx'),
                magnitude_v=obj_data.get('mag_V'),
                spectral_type=obj_data.get('sp_type'),
                source_catalog='simbad'
            )
        else:
            raise ValueError(f"No se pudo extraer información de {object_name}")
    
    def test_services(self) -> Dict[str, bool]:
        """Prueba conectividad a todos los servicios."""
        service_status = {}
        
        test_queries = {
            'simbad': ("SELECT main_id FROM basic WHERE main_id = 'Vega' LIMIT 1", 
                      self.service_urls['simbad_tap']),
            'gaia': ("SELECT source_id FROM gaiadr3.gaia_source LIMIT 1", 
                    self.service_urls['gaia_tap']),
            'nasa_exoplanet': ("SELECT pl_name FROM ps LIMIT 1", 
                              self.service_urls['nasa_exoplanet'])
        }
        
        for service, (query, url) in test_queries.items():
            try:
                result = self._execute_tap_query(f'{service}_test', query, url)
                service_status[service] = result.success
            except Exception as e:
                logger.error(f"Test de {service} falló: {e}")
                service_status[service] = False
        
        return service_status
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Retorna estadísticas de uso del conector."""
        cache_files = len(list(self.cache_dir.glob("*.json")))
        cache_size_mb = sum(f.stat().st_size for f in self.cache_dir.glob("*.json")) / (1024*1024)
        
        return {
            **self.query_stats,
            'cache_files': cache_files,
            'cache_size_mb': round(cache_size_mb, 2),
            'success_rate': (self.query_stats['successful_queries'] / 
                           max(self.query_stats['total_queries'], 1)) * 100
        }
    
    def clear_cache(self, older_than_hours: int = 24):
        """Limpia cache de archivos antiguos."""
        cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
        removed_files = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
            if file_time < cutoff_time:
                cache_file.unlink()
                removed_files += 1
        
        logger.info(f"Cache limpiado: {removed_files} archivos eliminados")
        return removed_files

# Función de demostración
def demonstrate_data_connector():
    """Demuestra las capacidades del conector de datos astronómicos."""
    print("🌟 AXIOM Astronomical Data Connector - Demostración")
    print("=" * 55)
    
    # Inicializar conector
    connector = AstronomicalDataConnector()
    
    # Test de conectividad
    print("\n🔍 Probando conectividad a servicios...")
    service_status = connector.test_services()
    
    for service, status in service_status.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {service.upper()}: {'Conectado' if status else 'Sin conexión'}")
    
    # Ejemplo 1: Consulta SIMBAD
    print("\n🔭 Ejemplo 1: Consulta SIMBAD para Vega")
    try:
        vega_result = connector.query_simbad("Vega")
        if vega_result.success:
            print("   ✅ Consulta exitosa")
            if 'data' in vega_result.data and vega_result.data['data']:
                vega_info = vega_result.data['data'][0]
                print(f"   📍 Coordenadas: RA={vega_info.get('ra', 'N/A')}, DEC={vega_info.get('dec', 'N/A')}")
                print(f"   ⭐ Tipo espectral: {vega_info.get('sp_type', 'N/A')}")
                print(f"   💫 Magnitud V: {vega_info.get('mag_V', 'N/A')}")
        else:
            print(f"   ❌ Error: {vega_result.error_message}")
    except Exception as e:
        print(f"   ❌ Error en consulta SIMBAD: {e}")
    
    # Ejemplo 2: Búsqueda regional en Gaia
    print("\n🌌 Ejemplo 2: Búsqueda regional en Gaia DR3")
    try:
        # Región alrededor de Vega
        gaia_result = connector.query_gaia_dr3(ra=279.23, dec=38.78, radius=0.1, mag_limit=12.0)
        if gaia_result.success:
            print("   ✅ Consulta Gaia exitosa")
            if 'data' in gaia_result.data:
                num_sources = len(gaia_result.data['data']) if gaia_result.data['data'] else 0
                print(f"   🌟 Fuentes encontradas: {num_sources}")
        else:
            print(f"   ❌ Error Gaia: {gaia_result.error_message}")
    except Exception as e:
        print(f"   ❌ Error en consulta Gaia: {e}")
    
    # Ejemplo 3: Exoplanetas recientes
    print("\n🪐 Ejemplo 3: Exoplanetas descubiertos recientemente")
    try:
        exo_result = connector.get_confirmed_exoplanets(discovery_year=2023)
        if exo_result.success and 'data' in exo_result.data:
            planets = exo_result.data['data']
            print(f"   ✅ Encontrados {len(planets)} exoplanetas desde 2023")
            
            # Mostrar algunos ejemplos
            for i, planet in enumerate(planets[:3]):
                print(f"   🌍 {planet.get('pl_name', 'N/A')} "
                      f"(Host: {planet.get('hostname', 'N/A')}, "
                      f"Año: {planet.get('disc_year', 'N/A')})")
        else:
            print(f"   ❌ Error exoplanetas: {exo_result.error_message}")
    except Exception as e:
        print(f"   ❌ Error en consulta exoplanetas: {e}")
    
    # Ejemplo 4: Cross-match de objetos
    print("\n🔄 Ejemplo 4: Cross-match de objetos famosos")
    famous_objects = ["Sirius", "Proxima Centauri", "Betelgeuse"]
    
    try:
        cross_match_results = connector.cross_match_objects(
            famous_objects,
            catalogs=['simbad']  # Solo SIMBAD para demo rápida
        )
        
        print("   ✅ Cross-match completado")
        for obj_name, obj_data in cross_match_results.items():
            print(f"   ⭐ {obj_name}:")
            if 'simbad' in obj_data:
                print("      └─ SIMBAD: ✅ Encontrado")
            if 'simbad_error' in obj_data:
                print("      └─ SIMBAD: ❌ Error")
                
    except Exception as e:
        print(f"   ❌ Error en cross-match: {e}")
    
    # Estadísticas finales
    print("\n📊 Estadísticas de Uso:")
    stats = connector.get_usage_statistics()
    print(f"   • Consultas totales: {stats['total_queries']}")
    print(f"   • Consultas exitosas: {stats['successful_queries']}")
    print(f"   • Tasa de éxito: {stats['success_rate']:.1f}%")
    print(f"   • Resultados en cache: {stats['cached_results']}")
    print(f"   • Archivos de cache: {stats['cache_files']}")
    print(f"   • Tamaño de cache: {stats['cache_size_mb']} MB")
    
    print("\n🎉 Demostración del Conector de Datos completada!")
    print("\n💡 Funcionalidades disponibles:")
    print("   • Consultas a SIMBAD, Gaia DR3, NASA Exoplanet Archive")
    print("   • Búsquedas regionales y por nombre")
    print("   • Cross-matching entre catálogos")
    print("   • Cache inteligente para optimizar performance")
    print("   • Manejo robusto de errores y timeouts")
    print("   • Estadísticas de uso y monitoreo")

if __name__ == "__main__":
    # Ejecutar demostración
    demonstrate_data_connector()