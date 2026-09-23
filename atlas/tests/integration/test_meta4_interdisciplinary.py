#!/usr/bin/env python3
"""
Meta 4 - Demostración Avanzada Interdisciplinaria
Prueba integral que combina múltiples dominios científicos
"""

import asyncio
import json
from datetime import datetime

async def interdisciplinary_demo():
    """Demostración que combina química, física y biología"""
    print("🚀 AXIOM META 4 - DEMOSTRACIÓN INTERDISCIPLINARIA")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {}
    
    # Inicializar servicios
    try:
        from app.services.computational_chemistry import ComputationalChemistryService
        from app.services.solid_state_physics import SolidStatePhysicsService
        from app.services.computational_biology import ComputationalBiologyService
        
        chem_service = ComputationalChemistryService()
        phys_service = SolidStatePhysicsService()
        bio_service = ComputationalBiologyService()
        
    except Exception as e:
        print(f"❌ Error inicializando servicios: {e}")
        return False
    
    # 1. ANÁLISIS DE MATERIALES (Química + Física)
    print("\n🔬 FASE 1: ANÁLISIS DE MATERIALES AVANZADOS")
    print("-" * 50)
    
    try:
        
        # Análisis cristalino del grafeno
        graphene_structure = {
            "structure_data": {
                "lattice": {
                    "a": 2.46,  # Parámetro de red del grafeno
                    "b": 2.46,
                    "c": 10.0,  # Separación entre capas
                    "alpha": 90.0,
                    "beta": 90.0,
                    "gamma": 120.0
                },
                "species": ["C", "C"],
                "coords": [[0.0, 0.0, 0.0], [0.333, 0.666, 0.0]]
            },
            "analysis_level": "detailed"
        }
        
        crystal_result = await chem_service.analyze_crystal_structure(graphene_structure)
        
        if crystal_result.get("success"):
            analysis = crystal_result.get("analysis", {})
            results["crystal_analysis"] = {
                "material": "Grafeno",
                "formula": analysis.get("formula", "N/A"),
                "volume": analysis.get("volume", "N/A"),
                "density": analysis.get("density", "N/A"),
                "system": analysis.get("crystal_system", "N/A")
            }
            print(f"✅ Grafeno analizado: {analysis.get('formula', 'N/A')} - {analysis.get('crystal_system', 'N/A')}")
        
        # Análisis de partículas de alta energía
        particle_analysis = {
            "process": "electron_carbon_scattering",
            "energy": 100.0,  # GeV
            "decay_channel": "multiple",
            "detector": "theoretical"
        }
        
        particle_result = await phys_service.particle_physics_analysis(particle_analysis)
        
        if particle_result.get("success"):
            cross_sections = particle_result.get("cross_sections", {})
            results["particle_physics"] = {
                "energy_GeV": particle_result.get("particle_energy_GeV", "N/A"),
                "total_cross_section": cross_sections.get("total", "N/A"),
                "interaction_type": "electron-carbon"
            }
            print(f"✅ Física de partículas: {cross_sections.get('total', 'N/A'):.2e} m² (sección eficaz)")
        
    except Exception as e:
        print(f"❌ Error en análisis de materiales: {e}")
        results["materials_error"] = str(e)
    
    # 2. SISTEMAS BIOLÓGICOS COMPLEJOS
    print("\n🧬 FASE 2: SISTEMAS BIOLÓGICOS COMPLEJOS")
    print("-" * 50)
    
    try:
        
        # Red regulatoria del cáncer
        cancer_network = {
            "organism": "homo_sapiens",
            "pathway": "p53_pathway",
            "analysis_type": "centrality",
            "network_size": 20
        }
        
        network_result = await bio_service.regulatory_network_analysis(cancer_network)
        
        if network_result.get("success"):
            props = network_result.get("network_properties", {})
            regulators = network_result.get("key_regulators", {})
            results["gene_network"] = {
                "pathway": "p53_pathway",
                "genes": props.get("num_genes", "N/A"),
                "interactions": props.get("num_interactions", "N/A"),
                "density": props.get("network_density", "N/A"),
                "key_regulators": [gene for gene, _ in regulators.get("most_central_genes", [])[:3]]
            }
            print(f"✅ Red p53: {props.get('num_genes', 'N/A')} genes, densidad {props.get('network_density', 'N/A'):.3f}")
        
        # Ecosistema marino
        marine_ecosystem = {
            "model_type": "predator_prey",
            "species": ["phytoplankton", "zooplankton"],
            "parameters": {
                "alpha": 1.2,    # Crecimiento fitoplancton
                "beta": 0.6,     # Predación zooplancton
                "gamma": 0.3,    # Eficiencia zooplancton
                "delta": 0.8     # Mortalidad zooplancton
            },
            "time_span": [0, 50],
            "initial_conditions": [1000, 100]
        }
        
        ecosystem_result = await bio_service.ecosystem_simulation(marine_ecosystem)
        
        if ecosystem_result.get("success"):
            eco_results = ecosystem_result.get("results", {})
            prey_stats = eco_results.get("prey_population", {})
            predator_stats = eco_results.get("predator_population", {})
            results["ecosystem"] = {
                "type": "marine",
                "prey_final": prey_stats.get("final", "N/A"),
                "predator_final": predator_stats.get("final", "N/A"),
                "stability": "stable" if abs(prey_stats.get("final", 0) - prey_stats.get("mean", 0)) < 100 else "oscillating"
            }
            print(f"✅ Ecosistema marino: fitoplancton {prey_stats.get('final', 'N/A'):.0f}, zooplancton {predator_stats.get('final', 'N/A'):.0f}")
        
    except Exception as e:
        print(f"❌ Error en sistemas biológicos: {e}")
        results["biology_error"] = str(e)
    
    # 3. INTEGRACIÓN INTERDISCIPLINARIA
    print("\n⚡ FASE 3: SÍNTESIS INTERDISCIPLINARIA")
    print("-" * 50)
    
    try:
        # Análisis metabólico relacionado con materiales
        metabolic_request = {
            "model": "test_model",
            "analysis_type": "fba"
        }
        
        metabolic_result = await chem_service.metabolic_network_analysis(metabolic_request)
        
        if metabolic_result.get("success"):
            model_info = metabolic_result.get("model_info", {})
            analysis = metabolic_result.get("analysis", {})
            results["metabolism"] = {
                "model": model_info.get("id", "N/A"),
                "reactions": model_info.get("num_reactions", "N/A"),
                "objective_value": analysis.get("objective_value", "N/A"),
                "efficiency": "high" if analysis.get("objective_value", 0) > 0.5 else "low"
            }
            print(f"✅ Metabolismo: {model_info.get('num_reactions', 'N/A')} reacciones, eficiencia {analysis.get('objective_value', 'N/A'):.3f}")
        
    except Exception as e:
        print(f"❌ Error en integración: {e}")
        results["integration_error"] = str(e)
    
    # RESUMEN FINAL
    print("\n" + "=" * 60)
    print("🎯 RESUMEN DE DEMOSTRACIÓN INTERDISCIPLINARIA")
    print("=" * 60)
    
    successful_analyses = 0
    total_analyses = 0
    
    if "crystal_analysis" in results:
        print(f"🔬 Análisis Cristalino: {results['crystal_analysis']['material']} - {results['crystal_analysis']['system']}")
        successful_analyses += 1
    total_analyses += 1
    
    if "particle_physics" in results:
        print(f"⚛️  Física de Partículas: {results['particle_physics']['energy_GeV']} GeV - {results['particle_physics']['interaction_type']}")
        successful_analyses += 1
    total_analyses += 1
    
    if "gene_network" in results:
        regulators = ", ".join(results['gene_network']['key_regulators'][:2]) if results['gene_network']['key_regulators'] else "N/A"
        print(f"🧬 Redes Génicas: {results['gene_network']['pathway']} - Reguladores: {regulators}")
        successful_analyses += 1
    total_analyses += 1
    
    if "ecosystem" in results:
        print(f"🌍 Ecosistema: {results['ecosystem']['type']} - Estado: {results['ecosystem']['stability']}")
        successful_analyses += 1
    total_analyses += 1
    
    if "metabolism" in results:
        print(f"🧪 Metabolismo: {results['metabolism']['reactions']} reacciones - {results['metabolism']['efficiency']} efficiency")
        successful_analyses += 1
    total_analyses += 1
    
    success_rate = (successful_analyses / total_analyses) * 100 if total_analyses > 0 else 0
    print(f"\n🎯 TASA DE ÉXITO INTERDISCIPLINARIA: {successful_analyses}/{total_analyses} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 DEMOSTRACIÓN INTERDISCIPLINARIA EXITOSA")
        print("✅ AXIOM META 4 preparado para investigación avanzada")
        print("🔬 Capacidades multi-dominio validadas")
    else:
        print("⚠️  Algunas capacidades interdisciplinarias necesitan optimización")
    
    # Guardar resultados
    final_report = {
        "timestamp": datetime.now().isoformat(),
        "demo_type": "interdisciplinary_advanced",
        "results": results,
        "success_rate": success_rate,
        "successful_analyses": successful_analyses,
        "total_analyses": total_analyses,
        "status": "success" if success_rate >= 80 else "partial"
    }
    
    with open("meta4_interdisciplinary_demo.json", "w") as f:
        json.dump(final_report, f, indent=2)
    
    print("\n📄 Reporte guardado en: meta4_interdisciplinary_demo.json")
    return success_rate >= 80

if __name__ == "__main__":
    success = asyncio.run(interdisciplinary_demo())
    print("\n🚀 AXIOM META 4 - DEMOSTRACIÓN COMPLETADA")
    exit(0 if success else 1)
