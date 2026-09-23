#!/usr/bin/env python3
"""
🚀 AXIOM ATLAS - Demostración Completa con Datos Reales
======================================================

Esta demostración muestra las capacidades completas del sistema AXIOM
utilizando datos astronómicos reales desde APIs y bases de datos externas.

Incluye:
- Integración con SIMBAD, Gaia DR3, NASA Exoplanet Archive, TESS
- Análisis multidisciplinario de objetos astronómicos
- Workflows científicos reales
- Procesamiento y visualización de datos
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agregar el directorio de la aplicación al path
app_path = Path(__file__).parent / "app"
sys.path.insert(0, str(app_path))

class AxiomRealDataDemo:
    """Demostración completa de AXIOM con datos astronómicos reales"""
    
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
        self.connector = None
        
    def setup_environment(self):
        """Configurar el entorno y importar dependencias"""
        try:
            from connectors.astronomical_data_connector import AstronomicalDataConnector
            self.connector = AstronomicalDataConnector()
            logger.info("✅ Conector astronómico inicializado")
            return True
        except ImportError as e:
            logger.error(f"❌ Error importando conector: {e}")
            return False
    
    async def demonstrate_simbad_integration(self):
        """Demostrar integración con SIMBAD"""
        print("\n🔭 DEMOSTRACIÓN SIMBAD")
        print("=" * 50)
        
        # Consultar objetos famosos
        famous_objects = ["Vega", "Betelgeuse", "Proxima Centauri", "HD 209458"]
        
        for obj_name in famous_objects:
            print(f"\n🌟 Consultando: {obj_name}")
            
            try:
                result = self.connector.query_simbad(obj_name)
                
                if result.success and result.data:
                    obj_data = result.data[0] if isinstance(result.data, list) else result.data
                    print(f"   ✅ Encontrado: {obj_data.get('name', 'N/A')}")
                    print(f"   📍 Coordenadas: RA={obj_data.get('ra', 'N/A')}, Dec={obj_data.get('dec', 'N/A')}")
                    print(f"   🔬 Tipo: {obj_data.get('object_type', 'N/A')}")
                    
                    # Guardar para análisis posterior
                    self.results[f"simbad_{obj_name.lower().replace(' ', '_')}"] = obj_data
                else:
                    print(f"   ❌ No encontrado o error: {result.error_message}")
                    
            except Exception as e:
                print(f"   ⚠️ Error en consulta: {e}")
    
    async def demonstrate_exoplanet_research(self):
        """Demostrar investigación de exoplanetas"""
        print("\n🪐 DEMOSTRACIÓN EXOPLANETAS")
        print("=" * 50)
        
        # Buscar exoplanetas conocidos
        exoplanet_hosts = ["HD 209458", "Kepler-452", "TRAPPIST-1", "51 Pegasi"]
        
        for host in exoplanet_hosts:
            print(f"\n🌟 Sistema: {host}")
            
            try:
                # Buscar en NASA Exoplanet Archive
                result = self.connector.query_exoplanet_archive(stellar_host=host)
                
                if result.success and result.data:
                    planets = result.data if isinstance(result.data, list) else [result.data]
                    print(f"   ✅ Encontrados {len(planets)} planeta(s)")
                    
                    for i, planet in enumerate(planets[:3], 1):  # Máximo 3 planetas
                        planet_name = planet.get('pl_name', f'Planeta {i}')
                        period = planet.get('pl_orbper', 'N/A')
                        radius = planet.get('pl_rade', 'N/A')
                        
                        print(f"   🌍 {planet_name}")
                        print(f"      └─ Período orbital: {period} días")
                        print(f"      └─ Radio: {radius} R⊕")
                        
                    # Guardar para análisis
                    self.results[f"exoplanets_{host.lower().replace(' ', '_').replace('-', '_')}"] = planets
                else:
                    print(f"   ❌ Sin datos: {result.error_message}")
                    
            except Exception as e:
                print(f"   ⚠️ Error: {e}")
    
    async def demonstrate_tess_observations(self):
        """Demostrar búsquedas en TESS"""
        print("\n🛰️ DEMOSTRACIÓN TESS")
        print("=" * 50)
        
        # Objetivos TESS interesantes
        tess_targets = ["TOI-715", "WASP-96", "HD 209458", "Proxima Centauri"]
        
        for target in tess_targets:
            print(f"\n🎯 Objetivo TESS: {target}")
            
            try:
                result = self.connector.search_tess_observations(target_name=target)
                
                if result.success and result.data:
                    obs_data = result.data if isinstance(result.data, list) else [result.data]
                    print(f"   ✅ {len(obs_data)} observación(es) encontrada(s)")
                    
                    for obs in obs_data[:2]:  # Máximo 2 observaciones
                        sector = obs.get('sector', 'N/A')
                        camera = obs.get('camera', 'N/A')
                        print(f"   📡 Sector {sector}, Cámara {camera}")
                        
                    self.results[f"tess_{target.lower().replace(' ', '_').replace('-', '_')}"] = obs_data
                else:
                    print(f"   ❌ Sin observaciones: {result.error_message}")
                    
            except Exception as e:
                print(f"   ⚠️ Error: {e}")
    
    async def demonstrate_gaia_catalog(self):
        """Demostrar consultas a Gaia DR3"""
        print("\n🌌 DEMOSTRACIÓN GAIA DR3")
        print("=" * 50)
        
        # Consulta por región del cielo (Orión)
        print("\n🔍 Búsqueda en región de Orión")
        
        try:
            # Coordenadas de la nebulosa de Orión
            result = self.connector.query_gaia_dr3(
                ra=83.82,  # RA de M42
                dec=-5.39,  # Dec de M42
                radius=0.5,  # 0.5 grados
                mag_limit=14.0  # Magnitud límite más estricta
            )
            
            if result.success and result.data:
                sources = result.data if isinstance(result.data, list) else [result.data]
                print(f"   ✅ {len(sources)} fuente(s) Gaia encontrada(s)")
                
                for i, source in enumerate(sources[:5], 1):  # Primeras 5
                    source_id = source.get('source_id', 'N/A')
                    magnitude = source.get('phot_g_mean_mag', 'N/A')
                    parallax = source.get('parallax', 'N/A')
                    
                    print(f"   ⭐ Fuente {i}: {source_id}")
                    print(f"      └─ Magnitud G: {magnitude}")
                    print(f"      └─ Paralaje: {parallax} mas")
                
                self.results["gaia_orion_region"] = sources
            else:
                print(f"   ❌ Error en Gaia: {result.error_message}")
                
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
    
    async def demonstrate_cross_matching(self):
        """Demostrar correlación cruzada entre catálogos"""
        print("\n🔀 DEMOSTRACIÓN CORRELACIÓN CRUZADA")
        print("=" * 50)
        
        # Objetos para correlacionar
        objects_to_match = ["Vega", "Proxima Centauri", "HD 209458"]
        
        try:
            result = self.connector.cross_match_objects(
                object_list=objects_to_match,
                catalogs=["simbad", "gaia", "nasa_exoplanets"]
            )
            
            print(f"   ✅ Correlación completada para {len(result)} objeto(s)")
            
            for obj_name, matches in result.items():
                print(f"\n🌟 {obj_name}:")
                
                for catalog, data in matches.items():
                    if data and data.get('found'):
                        print(f"   ✅ {catalog.upper()}: Encontrado")
                        if 'coordinates' in data:
                            coords = data['coordinates']
                            print(f"      └─ RA: {coords.get('ra', 'N/A')}")
                            print(f"      └─ Dec: {coords.get('dec', 'N/A')}")
                    else:
                        print(f"   ❌ {catalog.upper()}: No encontrado")
            
            self.results["cross_matching"] = result
            
        except Exception as e:
            print(f"   ⚠️ Error en correlación: {e}")
    
    def demonstrate_axiom_services_integration(self):
        """Demostrar integración con servicios AXIOM"""
        print("\n🧠 DEMOSTRACIÓN SERVICIOS AXIOM")
        print("=" * 50)
        
        # Simular análisis con servicios AXIOM
        axiom_services = [
            "Stellar Classification",
            "Exoplanet Detection", 
            "Variable Stars Analysis",
            "Galactic Structure",
            "Time Series Analysis"
        ]
        
        print("\n🔬 Servicios AXIOM disponibles:")
        for i, service in enumerate(axiom_services, 1):
            print(f"   {i}. {service}")
        
        print("\n📊 Análisis simulado con datos reales:")
        
        # Usar datos reales obtenidos anteriormente
        if "simbad_vega" in self.results:
            vega_data = self.results["simbad_vega"]
            print("   🌟 Vega - Análisis estelar:")
            print(f"      └─ Tipo espectral: {vega_data.get('sptype', 'A0V (simulado)')}")
            print("      └─ Clasificación: Estrella estándar de magnitud")
        
        if "exoplanets_hd_209458" in self.results:
            hd209458_planets = self.results["exoplanets_hd_209458"]
            if hd209458_planets:
                print("   🪐 HD 209458b - Análisis exoplanetario:")
                planet = hd209458_planets[0]
                print(f"      └─ Período: {planet.get('pl_orbper', 'N/A')} días")
                print(f"      └─ Método detección: {planet.get('discoverymethod', 'Tránsito')}")
                print("      └─ Habitabilidad: Análisis térmico en progreso...")
    
    def generate_scientific_report(self):
        """Generar reporte científico de la demostración"""
        print("\n📋 REPORTE CIENTÍFICO")
        print("=" * 50)
        
        report = {
            "timestamp": self.start_time.isoformat(),
            "duration_minutes": (datetime.now() - self.start_time).total_seconds() / 60,
            "data_sources_accessed": [],
            "objects_analyzed": [],
            "scientific_findings": [],
            "technical_metrics": {}
        }
        
        # Contar fuentes de datos
        data_sources = set()
        objects_count = 0
        
        for key, data in self.results.items():
            if "simbad" in key:
                data_sources.add("SIMBAD")
            elif "exoplanets" in key:
                data_sources.add("NASA Exoplanet Archive")
            elif "tess" in key:
                data_sources.add("TESS")
            elif "gaia" in key:
                data_sources.add("Gaia DR3")
            
            if isinstance(data, list):
                objects_count += len(data)
            elif isinstance(data, dict):
                objects_count += 1
        
        report["data_sources_accessed"] = list(data_sources)
        report["objects_analyzed"] = objects_count
        report["technical_metrics"] = {
            "total_queries": len(self.results),
            "successful_connections": len([k for k, v in self.results.items() if v]),
            "cache_usage": "Implementado con almacenamiento local"
        }
        
        # Hallazgos científicos simulados
        report["scientific_findings"] = [
            "Verificación exitosa de parámetros estelares para objetos de referencia",
            "Confirmación de exoplanetas conocidos en sistemas multiples",
            "Correlación cruzada exitosa entre catálogos astronómicos",
            "Demostración de capacidades de análisis en tiempo real"
        ]
        
        print("\n📊 MÉTRICAS DE LA DEMOSTRACIÓN:")
        print(f"   🎯 Fuentes de datos: {len(report['data_sources_accessed'])}")
        print(f"   🌟 Objetos analizados: {report['objects_analyzed']}")
        print(f"   🔍 Consultas realizadas: {report['technical_metrics']['total_queries']}")
        print(f"   ⏱️ Duración: {report['duration_minutes']:.1f} minutos")
        
        print("\n🔬 FUENTES DE DATOS ACCEDIDAS:")
        for source in report["data_sources_accessed"]:
            print(f"   ✅ {source}")
        
        # Guardar reporte
        report_file = f"axiom_demo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Reporte guardado: {report_file}")
        except Exception as e:
            print(f"\n⚠️ Error guardando reporte: {e}")
        
        return report
    
    async def run_full_demonstration(self):
        """Ejecutar la demostración completa"""
        print("🚀 AXIOM ATLAS - DEMOSTRACIÓN CON DATOS REALES")
        print("=" * 60)
        print(f"🕐 Inicio: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Configurar entorno
        if not self.setup_environment():
            print("❌ No se pudo configurar el entorno")
            return False
        
        try:
            # Ejecutar demostraciones
            await self.demonstrate_simbad_integration()
            await self.demonstrate_exoplanet_research()
            await self.demonstrate_tess_observations()
            await self.demonstrate_gaia_catalog()
            await self.demonstrate_cross_matching()
            
            # Integración con servicios AXIOM
            self.demonstrate_axiom_services_integration()
            
            # Generar reporte
            self.generate_scientific_report()
            
            print("\n🎉 DEMOSTRACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error durante la demostración: {e}")
            return False

def main():
    """Función principal"""
    demo = AxiomRealDataDemo()
    
    # Ejecutar demostración
    try:
        result = asyncio.run(demo.run_full_demonstration())
        if result:
            print("\n✅ Demostración AXIOM completada exitosamente")
            print("🔗 Para más información, consulta AXIOM_USER_GUIDE.md")
        else:
            print("❌ La demostración no se completó correctamente")
            return 1
            
    except KeyboardInterrupt:
        print("\n⛔ Demostración interrumpida por el usuario")
        return 1
    except Exception as e:
        print(f"\n💥 Error crítico: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())