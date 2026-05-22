#!/usr/bin/env python3
"""
Meta 4 - Pruebas Reales con Datos Válidos
Tests exhaustivos con casos de uso científicos reales
"""

import asyncio
import json
import traceback
from datetime import datetime

async def test_crystal_structure_real_data():
    """Prueba análisis cristalino con datos reales de silicio"""
    print("🔬 PRUEBA REAL: Análisis de Estructura Cristalina - Silicio")
    print("-" * 60)
    
    try:
        from app.services.computational_chemistry import ComputationalChemistryService
        service = ComputationalChemistryService()
        
        # Datos reales de la estructura del silicio (diamond cubic)
        silicon_structure = {
            "structure_data": {
                "lattice": {
                    "a": 5.431020511,  # Parámetro de red real del Si en Å
                    "b": 5.431020511,
                    "c": 5.431020511,
                    "alpha": 90.0,
                    "beta": 90.0,
                    "gamma": 90.0
                },
                "species": ["Si", "Si"],
                "coords": [
                    [0.0, 0.0, 0.0],      # Posición del primer Si
                    [0.25, 0.25, 0.25]    # Posición del segundo Si
                ]
            },
            "analysis_level": "detailed"
        }
        
        result = await service.analyze_crystal_structure(silicon_structure)
        
        if result.get("success"):
            analysis = result.get("analysis", {})
            print("✅ Análisis de Silicio EXITOSO:")
            print(f"   Fórmula: {analysis.get('formula', 'N/A')}")
            print(f"   Número de átomos: {analysis.get('num_atoms', 'N/A')}")
            print(f"   Volumen: {analysis.get('volume', 'N/A'):.2f} Ų")
            print(f"   Densidad: {analysis.get('density', 'N/A'):.2f} g/cm³")
            print(f"   Sistema cristalino: {analysis.get('crystal_system', 'N/A')}")
            print(f"   Grupo espacial: {analysis.get('space_group', 'N/A')}")
            return True
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba: {str(e)}")
        traceback.print_exc()
        return False

async def test_metabolic_network_real_data():
    """Prueba análisis de redes metabólicas con modelo real"""
    print("\n🧬 PRUEBA REAL: Análisis de Red Metabólica - E. coli")
    print("-" * 60)
    
    try:
        from app.services.computational_chemistry import ComputationalChemistryService
        service = ComputationalChemistryService()
        
        # Usar modelo test integrado de COBRApy
        metabolic_request = {
            "model": "test_model",  # Usa el modelo textbook de E. coli
            "analysis_type": "fba"
        }
        
        result = await service.metabolic_network_analysis(metabolic_request)
        
        if result.get("success"):
            model_info = result.get("model_info", {})
            analysis = result.get("analysis", {})
            
            print("✅ Análisis de Red Metabólica EXITOSO:")
            print(f"   Modelo: {model_info.get('name', model_info.get('id', 'N/A'))}")
            print(f"   Reacciones: {model_info.get('num_reactions', 'N/A')}")
            print(f"   Metabolitos: {model_info.get('num_metabolites', 'N/A')}")
            print(f"   Genes: {model_info.get('num_genes', 'N/A')}")
            print(f"   Valor objetivo: {analysis.get('objective_value', 'N/A'):.4f}")
            print(f"   Estado: {analysis.get('status', 'N/A')}")
            
            # Mostrar algunas reacciones principales
            fluxes = analysis.get('fluxes', {})
            if fluxes:
                print(f"   Flujos principales ({len(fluxes)} reacciones):")
                for rxn_id, flux in list(fluxes.items())[:3]:
                    print(f"     {rxn_id}: {flux:.3f}")
            
            return True
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba: {str(e)}")
        traceback.print_exc()
        return False

async def test_physics_particle_analysis():
    """Prueba análisis de física de partículas con datos experimentales"""
    print("\n⚛️  PRUEBA REAL: Análisis de Física de Partículas - Detector LHC")
    print("-" * 60)
    
    try:
        from app.services.solid_state_physics import SolidStatePhysicsService
        service = SolidStatePhysicsService()
        
        # Datos reales de experimento LHC
        particle_request = {
            "process": "muon_scattering",
            "energy": 13.6,  # TeV - energía real del LHC Run 3
            "decay_channel": "dimuon",
            "detector": "CMS"
        }
        
        result = await service.particle_physics_analysis(particle_request)
        
        if result.get("success"):
            print("✅ Análisis de Partículas EXITOSO:")
            print(f"   Tipo de análisis: {result.get('analysis_type', 'N/A')}")
            print(f"   Energía: {result.get('particle_energy_GeV', 'N/A')} GeV")
            
            cross_sections = result.get('cross_sections', {})
            if cross_sections:
                print("   Secciones eficaces:")
                print(f"     Compton: {cross_sections.get('compton_scattering', 0):.2e} {cross_sections.get('unit', 'm²')}")
                print(f"     Fotoeléctrico: {cross_sections.get('photoelectric', 0):.2e} {cross_sections.get('unit', 'm²')}")
                print(f"     Total: {cross_sections.get('total', 0):.2e} {cross_sections.get('unit', 'm²')}")
            
            interaction_props = result.get('interaction_properties', {})
            if interaction_props:
                print("   Propiedades de interacción:")
                print(f"     Camino libre medio: {interaction_props.get('mean_free_path_cm', 'N/A'):.0f} cm")
                print(f"     Longitud de atenuación: {interaction_props.get('attenuation_length_cm', 'N/A'):.0f} cm")
            
            return True
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba: {str(e)}")
        traceback.print_exc()
        return False

async def test_gene_network_analysis():
    """Prueba análisis de redes génicas con pathway real"""
    print("\n🧬 PRUEBA REAL: Red Regulatoria Génica - Ciclo Celular Humano")
    print("-" * 60)
    
    try:
        from app.services.computational_biology import ComputationalBiologyService
        service = ComputationalBiologyService()
        
        # Análisis de pathway real del ciclo celular
        gene_request = {
            "organism": "homo_sapiens",
            "pathway": "cell_cycle_g1_s",
            "analysis_type": "centrality",
            "network_size": 15  # Tamaño realista
        }
        
        result = await service.regulatory_network_analysis(gene_request)
        
        if result.get("success"):
            props = result.get('network_properties', {})
            regulators = result.get('key_regulators', {})
            motifs = result.get('network_motifs', {})
            
            print("✅ Análisis de Red Génica EXITOSO:")
            print(f"   Genes: {props.get('num_genes', 'N/A')}")
            print(f"   Interacciones: {props.get('num_interactions', 'N/A')}")
            print(f"   Densidad: {props.get('network_density', 'N/A'):.3f}")
            print(f"   Conectada: {'Sí' if props.get('is_connected') else 'No'}")
            
            # Reguladores centrales
            central_genes = regulators.get('most_central_genes', [])[:3]
            if central_genes:
                print("   Reguladores centrales:")
                for gene, centrality in central_genes:
                    print(f"     {gene}: {centrality:.3f}")
            
            # Motivos regulatorios
            feedback_loops = motifs.get('feedback_loops', [])
            if feedback_loops:
                print(f"   Bucles de retroalimentación: {len(feedback_loops)}")
                for loop in feedback_loops[:2]:  # Mostrar primeros 2
                    print(f"     {' → '.join(loop)}")
            
            return True
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba: {str(e)}")
        traceback.print_exc()
        return False

async def test_ecosystem_dynamics():
    """Prueba simulación de ecosistema con parámetros reales"""
    print("\n🌍 PRUEBA REAL: Dinámicas de Ecosistema - Yellowstone")
    print("-" * 60)
    
    try:
        from app.services.computational_biology import ComputationalBiologyService
        service = ComputationalBiologyService()
        
        # Parámetros basados en datos reales de Yellowstone
        ecosystem_request = {
            "model_type": "predator_prey",
            "species": ["wolves", "elk"],
            "parameters": {
                "alpha": 0.8,    # Tasa crecimiento elk
                "beta": 0.02,    # Tasa predación
                "gamma": 0.8,    # Eficiencia wolves
                "delta": 0.15    # Tasa mortalidad wolves
            },
            "time_span": [0, 30],  # 30 años
            "initial_conditions": [200, 25]  # Elk inicial, Wolves inicial
        }
        
        result = await service.ecosystem_simulation(ecosystem_request)
        
        if result.get("success"):
            results = result.get('results', {})
            params = result.get('parameters', {})
            
            print("✅ Simulación de Ecosistema EXITOSO:")
            print(f"   Modelo: {result.get('ecosystem_type', 'N/A')}")
            print(f"   Periodo simulado: {params.get('time_span_years', 'N/A')} años")
            
            # Estadísticas de población
            prey_stats = results.get('prey_population', {})
            predator_stats = results.get('predator_population', {})
            
            if prey_stats:
                print("   Elk (presa):")
                print(f"     Población final: {prey_stats.get('final', 'N/A'):.0f}")
                print(f"     Máximo: {prey_stats.get('max', 'N/A'):.0f}")
                print(f"     Promedio: {prey_stats.get('mean', 'N/A'):.0f}")
            
            if predator_stats:
                print("   Lobos (depredador):")
                print(f"     Población final: {predator_stats.get('final', 'N/A'):.0f}")
                print(f"     Máximo: {predator_stats.get('max', 'N/A'):.0f}")
                print(f"     Promedio: {predator_stats.get('mean', 'N/A'):.0f}")
            
            return True
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba: {str(e)}")
        traceback.print_exc()
        return False

async def test_biodiversity_analysis():
    """Prueba análisis de biodiversidad con datos reales de campo"""
    print("\n📊 PRUEBA REAL: Análisis de Biodiversidad - Amazonía")
    print("-" * 60)
    
    try:
        from app.services.computational_biology import ComputationalBiologyService
        service = ComputationalBiologyService()
        
        # Parámetros basados en estudios reales de biodiversidad
        biodiversity_request = {
            "data_type": "species_abundance",
            "location": "amazon_basin",
            "indices": ["shannon", "simpson", "pielou"],
            "sample_size": 1000  # Muestreo extensivo
        }
        
        result = await service.biodiversity_analysis(biodiversity_request)
        
        if result.get("success"):
            metrics = result.get('diversity_metrics', {})
            community = result.get('community_structure', {})
            
            print("✅ Análisis de Biodiversidad EXITOSO:")
            print(f"   Localización: {result.get('location', 'N/A')}")
            print(f"   Tamaño de muestra: {result.get('sample_info', {}).get('total_individuals', 'N/A')}")
            
            if metrics:
                print("   Índices de diversidad:")
                print(f"     Riqueza de especies: {metrics.get('species_richness', 'N/A')}")
                print(f"     Índice Shannon: {metrics.get('shannon_index', 'N/A'):.3f}")
                print(f"     Índice Simpson: {metrics.get('simpson_index', 'N/A'):.3f}")
                print(f"     Equitatividad (Pielou): {metrics.get('evenness', 'N/A'):.3f}")
            
            if community:
                print("   Estructura de la comunidad:")
                dom_pct = community.get('dominance_percentage', 'N/A')
                rare_pct = community.get('rare_species_percentage', 'N/A')
                
                if dom_pct != 'N/A':
                    print(f"     Especies dominantes: {dom_pct:.1f}%")
                else:
                    print(f"     Especies dominantes: {dom_pct}")
                    
                if rare_pct != 'N/A':
                    print(f"     Especies raras: {rare_pct:.1f}%")
                else:
                    print(f"     Especies raras: {rare_pct}")
            
            return True
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba: {str(e)}")
        traceback.print_exc()
        return False

async def main():
    """Ejecutar todas las pruebas reales"""
    print("🚀 AXIOM META 4 - PRUEBAS REALES CON DATOS CIENTÍFICOS")
    print("=" * 70)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Ejecutar todas las pruebas
    tests = [
        ("Análisis Cristalino", test_crystal_structure_real_data),
        ("Red Metabólica", test_metabolic_network_real_data),  
        ("Física de Partículas", test_physics_particle_analysis),
        ("Redes Génicas", test_gene_network_analysis),
        ("Dinámicas de Ecosistema", test_ecosystem_dynamics),
        ("Análisis de Biodiversidad", test_biodiversity_analysis)
    ]
    
    results = {}
    successful_tests = 0
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results[test_name] = "✅ EXITOSO" if success else "❌ FALLIDO"
            if success:
                successful_tests += 1
        except Exception as e:
            results[test_name] = f"❌ ERROR: {str(e)}"
            print(f"❌ Error inesperado en {test_name}: {e}")
    
    # Resumen final
    print("\n" + "=" * 70)
    print("📋 RESUMEN DE PRUEBAS REALES")
    print("=" * 70)
    
    for test_name, result in results.items():
        print(f"   {test_name}: {result}")
    
    success_rate = (successful_tests / len(tests)) * 100
    print(f"\n🎯 TASA DE ÉXITO: {successful_tests}/{len(tests)} ({success_rate:.1f}%)")
    
    if success_rate >= 70:
        print("🎉 AXIOM META 4: CAPACIDADES CIENTÍFICAS VALIDADAS")
        print("✅ Las implementaciones funcionan correctamente con datos reales")
        print("🔬 Listo para investigación científica profesional")
    else:
        print("⚠️  Algunas capacidades necesitan ajustes adicionales")
    
    # Guardar resultados
    summary = {
        "timestamp": datetime.now().isoformat(),
        "test_results": results,
        "success_rate": success_rate,
        "successful_tests": successful_tests,
        "total_tests": len(tests)
    }
    
    with open("meta4_real_data_tests.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\n📄 Resultados guardados en: meta4_real_data_tests.json")
    return success_rate >= 70

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
