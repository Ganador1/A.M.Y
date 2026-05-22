# 🧪 AXIOM ATLAS - Ejemplos Prácticos Completos

> **Guías paso a paso para casos de uso reales en investigación científica**

## 📋 Índice de Ejemplos

1. [🧬 Investigación Biomédica](#-investigación-biomédica)
2. [⚛️ Computación Cuántica](#️-computación-cuántica)
3. [⚗️ Química Computacional](#️-química-computacional)
4. [🌌 Astronomía y Astrofísica](#-astronomía-y-astrofísica)
5. [📊 Análisis de Datos Científicos](#-análisis-de-datos-científicos)
6. [🔬 Workflows Complejos](#-workflows-complejos)

---

## 🧬 Investigación Biomédica

### Ejemplo 1: Análisis de Eficacia de Fármacos

**Contexto**: Evaluar la plausibilidad de un nuevo tratamiento para diabetes tipo 2.

```python
import requests
import json

API_BASE = "http://localhost:8000"
headers = {"Content-Type": "application/json"}

# Paso 1: Evaluar hipótesis principal
hypothesis_data = {
    "hypothesis": "La metformina combinada con inhibidores SGLT2 mejora el control glucémico mejor que monoterapia",
    "domain": "endocrinologia",
    "context": {
        "population": "adultos_diabetes_tipo2",
        "intervention": "terapia_combinada",
        "comparison": "monoterapia",
        "outcome": "control_glucemico"
    },
    "evidence_sources": ["pubmed", "cochrane", "clinicaltrials"],
    "confidence_threshold": 0.8
}

response = requests.post(f"{API_BASE}/api/plausibility/evaluate", 
                        json=hypothesis_data, headers=headers)
plausibility_result = response.json()

print(f"🎯 Plausibilidad: {plausibility_result['plausibility_score']:.2f}")
print(f"📊 Confianza: {plausibility_result['confidence']:.2f}")
print(f"📚 Evidencia: {plausibility_result['evidence_summary']}")

# Paso 2: Búsqueda de literatura específica
literature_search = {
    "query": "metformin SGLT2 inhibitor combination diabetes HbA1c",
    "databases": ["pubmed", "cochrane"],
    "filters": {
        "publication_types": ["randomized_controlled_trial", "meta_analysis"],
        "years": [2020, 2024],
        "languages": ["english", "spanish"]
    },
    "max_results": 50,
    "sort_by": "relevance"
}

response = requests.post(f"{API_BASE}/api/literature-search/search",
                        json=literature_search, headers=headers)
literature_result = response.json()

print(f"\n📖 Literatura encontrada: {len(literature_result['papers'])} papers")

# Paso 3: Análisis de biomarcadores
biomarker_analysis = {
    "biomarkers": ["HbA1c", "glucose_fasting", "glucose_postprandial"],
    "intervention_data": literature_result['papers'][:10],
    "analysis_type": "meta_analysis",
    "statistical_method": "random_effects"
}

response = requests.post(f"{API_BASE}/api/biomedical-nlp/biomarker-analysis",
                        json=biomarker_analysis, headers=headers)
biomarker_result = response.json()

print(f"\n🧬 Biomarcadores analizados: {len(biomarker_result['results'])}")

# Paso 4: Evaluación de seguridad
safety_assessment = {
    "drug_combinations": ["metformin_sglt2"],
    "adverse_events": ["hypoglycemia", "urinary_tract_infection", "dehydration"],
    "population": "diabetes_type2",
    "risk_factors": ["age_over_65", "kidney_function"]
}

response = requests.post(f"{API_BASE}/api/safety/drug-interaction-analysis",
                        json=safety_assessment, headers=headers)
safety_result = response.json()

print(f"\n🛡️ Perfil de seguridad: {safety_result['risk_level']}")
print(f"⚠️ Eventos adversos principales: {safety_result['main_adverse_events']}")

# Generar reporte final
final_report = {
    "study_title": "Análisis de Eficacia y Seguridad: Metformina + SGLT2",
    "plausibility": plausibility_result,
    "literature": literature_result,
    "biomarkers": biomarker_result,
    "safety": safety_result,
    "conclusions": "Generadas automáticamente",
    "recommendations": "Generadas automáticamente"
}

print("\n" + "="*50)
print("📋 REPORTE FINAL")
print("="*50)
print(json.dumps(final_report, indent=2, ensure_ascii=False))
```

### Ejemplo 2: Análisis de Secuencias de Proteínas

```python
# Análisis completo de una proteína de interés
protein_data = {
    "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG",
    "protein_name": "Ejemplo_proteina_kinasa",
    "organism": "Homo sapiens",
    "analysis_requests": {
        "structure_prediction": True,
        "function_prediction": True,
        "domain_analysis": True,
        "interaction_prediction": True,
        "drug_target_assessment": True
    }
}

response = requests.post(f"{API_BASE}/api/biomedical-nlp/protein-analysis",
                        json=protein_data, headers=headers)
protein_result = response.json()

print(f"🧬 Proteína analizada: {protein_result['protein_info']['name']}")
print(f"📏 Longitud: {protein_result['sequence_info']['length']} aminoácidos")
print(f"🎯 Dominios encontrados: {len(protein_result['domains'])}")
print(f"💊 Potencial farmacológico: {protein_result['druggability_score']:.2f}")
```

---

## ⚛️ Computación Cuántica

### Ejemplo 1: Optimización de Cartera de Inversiones

**Contexto**: Usar algoritmos cuánticos para optimizar una cartera de inversiones.

```python
# Definir problema de optimización
portfolio_optimization = {
    "assets": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"],
    "expected_returns": [0.12, 0.15, 0.10, 0.13, 0.20],
    "risk_matrix": [
        [0.04, 0.02, 0.01, 0.02, 0.03],
        [0.02, 0.09, 0.02, 0.03, 0.04],
        [0.01, 0.02, 0.03, 0.01, 0.02],
        [0.02, 0.03, 0.01, 0.06, 0.03],
        [0.03, 0.04, 0.02, 0.03, 0.16]
    ],
    "budget": 100000,
    "risk_tolerance": 0.15,
    "algorithm": "qaoa"
}

response = requests.post(f"{API_BASE}/api/quantum-computing/portfolio-optimization",
                        json=portfolio_optimization, headers=headers)
optimization_result = response.json()

print(f"⚛️ Algoritmo usado: {optimization_result['algorithm']}")
print(f"💰 Retorno esperado: {optimization_result['expected_return']:.2%}")
print(f"📊 Riesgo: {optimization_result['portfolio_risk']:.2%}")
print(f"🎯 Distribución óptima:")
for asset, allocation in optimization_result['optimal_allocation'].items():
    print(f"  {asset}: {allocation:.1%}")
```

### Ejemplo 2: Simulación Molecular Cuántica

```python
# Simulación de molécula de agua usando VQE
molecular_simulation = {
    "molecule": "H2O",
    "geometry": [
        ["O", [0.0, 0.0, 0.0]],
        ["H", [0.0, 0.757, 0.587]],
        ["H", [0.0, -0.757, 0.587]]
    ],
    "basis_set": "sto-3g",
    "algorithm": "vqe",
    "ansatz": "UCCSD",
    "optimizer": "COBYLA",
    "max_iterations": 1000
}

response = requests.post(f"{API_BASE}/api/quantum-computing/molecular-simulation",
                        json=molecular_simulation, headers=headers)
simulation_result = response.json()

print(f"🧪 Molécula: {simulation_result['molecule']}")
print(f"⚡ Energía fundamental: {simulation_result['ground_state_energy']:.6f} Hartree")
print(f"🔄 Iteraciones: {simulation_result['iterations']}")
print(f"📊 Precisión: {simulation_result['accuracy']:.2e}")
```

---

## ⚗️ Química Computacional

### Ejemplo 1: Diseño de Fármacos Asistido por IA

**Contexto**: Identificar compuestos prometedores para inhibir una proteína específica.

```python
# Paso 1: Análisis del target proteico
target_analysis = {
    "protein_pdb_id": "1HTM",  # HIV protease
    "binding_site_residues": [25, 27, 29, 30, 48, 50, 53, 54, 81, 82, 84],
    "analysis_type": "binding_site_characterization"
}

response = requests.post(f"{API_BASE}/api/computational-chemistry/target-analysis",
                        json=target_analysis, headers=headers)
target_result = response.json()

print(f"🎯 Proteína objetivo: {target_result['protein_name']}")
print(f"📏 Volumen del sitio activo: {target_result['binding_site_volume']:.1f} Ų")
print(f"💧 Hidrofobicidad: {target_result['hydrophobicity_score']:.2f}")

# Paso 2: Búsqueda virtual de compuestos
virtual_screening = {
    "compound_library": "chembl",
    "target_info": target_result,
    "filters": {
        "molecular_weight": [200, 500],
        "logP": [-2, 5],
        "drug_likeness": True,
        "PAINS_filter": True
    },
    "docking_parameters": {
        "exhaustiveness": 8,
        "num_modes": 10
    },
    "max_compounds": 1000
}

response = requests.post(f"{API_BASE}/api/computational-chemistry/virtual-screening",
                        json=virtual_screening, headers=headers)
screening_result = response.json()

print(f"\n🔍 Compuestos evaluados: {screening_result['total_screened']}")
print(f"⭐ Hits identificados: {len(screening_result['top_hits'])}")

# Paso 3: Análisis ADMET de los mejores candidatos
admet_analysis = {
    "compounds": screening_result['top_hits'][:20],
    "properties": [
        "absorption", "distribution", "metabolism", 
        "excretion", "toxicity", "blood_brain_barrier"
    ],
    "species": "human"
}

response = requests.post(f"{API_BASE}/api/computational-chemistry/admet-prediction",
                        json=admet_analysis, headers=headers)
admet_result = response.json()

print(f"\n💊 Análisis ADMET completado para {len(admet_result['results'])} compuestos")

# Paso 4: Ranking final y recomendaciones
final_ranking = {
    "compounds": screening_result['top_hits'][:20],
    "scoring_weights": {
        "binding_affinity": 0.4,
        "drug_likeness": 0.3,
        "admet_score": 0.3
    },
    "experimental_data": None  # Datos experimentales si están disponibles
}

response = requests.post(f"{API_BASE}/api/computational-chemistry/compound-ranking",
                        json=final_ranking, headers=headers)
ranking_result = response.json()

print(f"\n🏆 RANKING FINAL DE CANDIDATOS:")
for i, compound in enumerate(ranking_result['ranked_compounds'][:5], 1):
    print(f"{i}. {compound['name']} (Score: {compound['final_score']:.3f})")
    print(f"   SMILES: {compound['smiles']}")
    print(f"   Afinidad: {compound['binding_affinity']:.1f} kcal/mol")
    print(f"   Drug-likeness: {compound['drug_likeness']:.2f}")
    print()
```

---

## 🌌 Astronomía y Astrofísica

### Ejemplo 1: Detección y Caracterización de Exoplanetas

```python
# Análisis de curvas de luz para detección de tránsitos
exoplanet_detection = {
    "light_curve_file": "kepler_star_12345.csv",
    "star_properties": {
        "stellar_mass": 1.02,  # masas solares
        "stellar_radius": 1.15,  # radios solares
        "effective_temperature": 5800,  # Kelvin
        "metallicity": 0.1  # [Fe/H]
    },
    "detection_parameters": {
        "min_period": 0.5,  # días
        "max_period": 500,  # días
        "min_transit_depth": 0.0001,  # fracción
        "signal_to_noise_ratio": 7.0
    },
    "methods": ["bls", "tls", "machine_learning"]
}

response = requests.post(f"{API_BASE}/api/astronomy/exoplanet-detection",
                        json=exoplanet_detection, headers=headers)
detection_result = response.json()

print(f"🌌 Estrella analizada: ID {detection_result['star_id']}")
print(f"🪐 Candidatos detectados: {len(detection_result['candidates'])}")

for i, candidate in enumerate(detection_result['candidates'], 1):
    print(f"\n  Candidato {i}:")
    print(f"    Período: {candidate['period']:.2f} días")
    print(f"    Radio planetario: {candidate['planet_radius']:.2f} R⊕")
    print(f"    Temperatura de equilibrio: {candidate['equilibrium_temp']:.0f} K")
    print(f"    Zona habitable: {'Sí' if candidate['habitable_zone'] else 'No'}")
    print(f"    Confianza: {candidate['detection_confidence']:.1%}")

# Análisis de follow-up para el mejor candidato
if detection_result['candidates']:
    best_candidate = detection_result['candidates'][0]
    
    followup_analysis = {
        "candidate": best_candidate,
        "analysis_type": "comprehensive",
        "include_atmosphere": True,
        "include_composition": True,
        "include_habitability": True
    }
    
    response = requests.post(f"{API_BASE}/api/astronomy/exoplanet-characterization",
                            json=followup_analysis, headers=headers)
    characterization_result = response.json()
    
    print(f"\n🔬 ANÁLISIS DETALLADO DEL MEJOR CANDIDATO:")
    print(f"Tipo planetario: {characterization_result['planet_type']}")
    print(f"Composición atmosférica estimada: {characterization_result['atmosphere_composition']}")
    print(f"Índice de similitud a la Tierra: {characterization_result['earth_similarity_index']:.3f}")
```

### Ejemplo 2: Análisis de Variabilidad Estelar

```python
# Análisis de estrellas variables
stellar_variability = {
    "star_data": "variable_star_photometry.csv",
    "observation_period": 365,  # días
    "photometric_bands": ["V", "R", "I"],
    "analysis_methods": [
        "lomb_scargle_periodogram",
        "autocorrelation_function",
        "phase_dispersion_minimization"
    ]
}

response = requests.post(f"{API_BASE}/api/astronomy/stellar-variability",
                        json=stellar_variability, headers=headers)
variability_result = response.json()

print(f"⭐ Análisis de variabilidad completado")
print(f"Tipo de variable: {variability_result['variable_type']}")
print(f"Período principal: {variability_result['primary_period']:.4f} días")
print(f"Amplitud: {variability_result['amplitude']:.3f} mag")
print(f"Características: {', '.join(variability_result['characteristics'])}")
```

---

## 📊 Análisis de Datos Científicos

### Ejemplo 1: Análisis Estadístico de Experimentos

```python
# Análisis completo de un experimento controlado
experimental_analysis = {
    "data_file": "experiment_results.csv",
    "experimental_design": {
        "type": "factorial_2x3",
        "factors": ["temperature", "concentration"],
        "levels": {
            "temperature": [25, 37],
            "concentration": [0.1, 0.5, 1.0]
        },
        "response_variable": "activity",
        "replicates": 5
    },
    "statistical_tests": [
        "anova_two_way",
        "tukey_hsd",
        "linear_regression",
        "residual_analysis"
    ],
    "confidence_level": 0.95,
    "multiple_testing_correction": "bonferroni"
}

response = requests.post(f"{API_BASE}/api/statistics/experimental-analysis",
                        json=experimental_analysis, headers=headers)
stats_result = response.json()

print(f"📊 ANÁLISIS ESTADÍSTICO COMPLETO")
print(f"Diseño: {stats_result['design_type']}")
print(f"N total: {stats_result['sample_size']}")
print(f"\nFactores significativos:")
for factor, p_value in stats_result['significant_factors'].items():
    print(f"  {factor}: p = {p_value:.4f}")

print(f"\nModelo estadístico:")
print(f"  R² = {stats_result['model_r_squared']:.3f}")
print(f"  R² ajustado = {stats_result['adjusted_r_squared']:.3f}")
print(f"  RMSE = {stats_result['rmse']:.3f}")

# Generar gráficos y visualizaciones
visualization_request = {
    "analysis_results": stats_result,
    "plot_types": [
        "interaction_plot",
        "residuals_vs_fitted",
        "qq_plot",
        "boxplot_by_factors"
    ],
    "output_format": "png",
    "resolution": 300
}

response = requests.post(f"{API_BASE}/api/visualization/statistical-plots",
                        json=visualization_request, headers=headers)
viz_result = response.json()

print(f"\n📈 Visualizaciones generadas: {len(viz_result['plot_files'])}")
```

---

## 🔬 Workflows Complejos

### Ejemplo 1: Pipeline Completo de Descubrimiento de Fármacos

```python
# Workflow integrado que combina múltiples servicios
drug_discovery_workflow = {
    "workflow_name": "drug_discovery_pipeline",
    "target_protein": "EGFR",
    "disease_indication": "cancer",
    "steps": [
        {
            "step_id": "literature_review",
            "service": "literature_search",
            "parameters": {
                "query": "EGFR inhibitor cancer therapy",
                "databases": ["pubmed", "chembl"],
                "max_results": 200
            },
            "outputs": ["literature_data"]
        },
        {
            "step_id": "target_analysis",
            "service": "computational_chemistry",
            "parameters": {
                "protein_id": "1M17",
                "analysis_type": "binding_site"
            },
            "depends_on": ["literature_review"],
            "outputs": ["target_structure"]
        },
        {
            "step_id": "virtual_screening",
            "service": "computational_chemistry",
            "parameters": {
                "library": "chembl",
                "target": "target_structure",
                "max_compounds": 10000
            },
            "depends_on": ["target_analysis"],
            "outputs": ["hit_compounds"]
        },
        {
            "step_id": "admet_prediction",
            "service": "computational_chemistry",
            "parameters": {
                "compounds": "hit_compounds",
                "properties": ["absorption", "toxicity"]
            },
            "depends_on": ["virtual_screening"],
            "outputs": ["admet_data"]
        },
        {
            "step_id": "final_ranking",
            "service": "machine_learning",
            "parameters": {
                "data_sources": ["hit_compounds", "admet_data"],
                "ranking_criteria": ["binding_affinity", "drug_likeness"]
            },
            "depends_on": ["admet_prediction"],
            "outputs": ["final_candidates"]
        }
    ],
    "execution_mode": "parallel_when_possible",
    "notifications": {
        "email": "researcher@university.edu",
        "slack_webhook": "https://hooks.slack.com/...",
        "notify_on": ["completion", "error", "milestone"]
    }
}

# Ejecutar workflow
response = requests.post(f"{API_BASE}/api/workflows/execute",
                        json=drug_discovery_workflow, headers=headers)
workflow_result = response.json()

workflow_id = workflow_result['workflow_id']
print(f"🔬 Workflow iniciado: {workflow_id}")
print(f"⏱️ Tiempo estimado: {workflow_result['estimated_duration']} minutos")

# Monitorear progreso
import time
while True:
    response = requests.get(f"{API_BASE}/api/workflows/{workflow_id}/status")
    status = response.json()
    
    print(f"\r📊 Progreso: {status['progress']:.1f}% | Estado: {status['current_step']}", end="")
    
    if status['status'] in ['completed', 'failed']:
        break
    time.sleep(30)

# Obtener resultados finales
response = requests.get(f"{API_BASE}/api/workflows/{workflow_id}/results")
final_results = response.json()

print(f"\n\n🎉 WORKFLOW COMPLETADO")
print(f"Duración total: {final_results['total_duration']} minutos")
print(f"Candidatos finales identificados: {len(final_results['final_candidates'])}")

# Mostrar top 3 candidatos
for i, candidate in enumerate(final_results['final_candidates'][:3], 1):
    print(f"\n🏆 Candidato #{i}:")
    print(f"   Nombre: {candidate['compound_name']}")
    print(f"   SMILES: {candidate['smiles']}")
    print(f"   Score: {candidate['final_score']:.3f}")
    print(f"   Afinidad prevista: {candidate['binding_affinity']:.1f} kcal/mol")
    print(f"   Toxicidad: {candidate['toxicity_risk']}")
```

### Ejemplo 2: Análisis Multi-Ómico Integrado

```python
# Pipeline de análisis integrativo
multiomics_workflow = {
    "study_name": "cancer_biomarker_discovery",
    "data_types": ["genomics", "transcriptomics", "proteomics", "metabolomics"],
    "patient_groups": ["control", "early_stage", "advanced"],
    "analysis_steps": [
        {
            "step": "quality_control",
            "parameters": {
                "missing_data_threshold": 0.2,
                "outlier_detection": True,
                "normalization": "quantile"
            }
        },
        {
            "step": "differential_analysis",
            "parameters": {
                "method": "limma",
                "fdr_threshold": 0.05,
                "fold_change_threshold": 1.5
            }
        },
        {
            "step": "pathway_analysis",
            "parameters": {
                "databases": ["kegg", "reactome", "go"],
                "enrichment_method": "gsea"
            }
        },
        {
            "step": "integration_analysis",
            "parameters": {
                "method": "mofa",
                "factors": 10,
                "convergence_mode": "fast"
            }
        },
        {
            "step": "biomarker_identification",
            "parameters": {
                "ml_methods": ["random_forest", "svm", "elastic_net"],
                "cross_validation": 10,
                "feature_selection": True
            }
        }
    ]
}

response = requests.post(f"{API_BASE}/api/omics/integrated-analysis",
                        json=multiomics_workflow, headers=headers)
omics_result = response.json()

print(f"🧬 Análisis multi-ómico completado")
print(f"Biomarcadores identificados: {len(omics_result['biomarkers'])}")
print(f"Vías biológicas alteradas: {len(omics_result['altered_pathways'])}")
print(f"Precisión del modelo: {omics_result['model_accuracy']:.2%}")
```

---

## 🎯 Consejos para Optimización

### 💡 **Mejores Prácticas**

1. **Paralelización**: Usa workflows para ejecutar análisis independientes en paralelo
2. **Cache**: Activa el cache para análisis repetitivos
3. **Batch Processing**: Procesa múltiples muestras en lotes
4. **Monitoreo**: Usa webhooks para notificaciones de progreso

### ⚡ **Optimización de Rendimiento**

```python
# Configuración optimizada para análisis grandes
performance_config = {
    "parallel_workers": 8,
    "cache_enabled": True,
    "batch_size": 100,
    "memory_limit": "16GB",
    "use_gpu": True
}

# Aplicar configuración
response = requests.post(f"{API_BASE}/api/system/configure",
                        json=performance_config, headers=headers)
```

### 🔍 **Debugging y Troubleshooting**

```python
# Obtener logs detallados de un análisis
debug_request = {
    "job_id": "12345",
    "log_level": "DEBUG",
    "include_system_info": True
}

response = requests.get(f"{API_BASE}/api/system/logs",
                       params=debug_request, headers=headers)
logs = response.json()

print("🐛 Información de debug:")
for log_entry in logs['entries']:
    print(f"[{log_entry['timestamp']}] {log_entry['level']}: {log_entry['message']}")
```

---

*¿Necesitas ayuda con algún ejemplo específico? Consulta la [documentación completa](README.md) o abre un [issue en GitHub](https://github.com/your-repo/axiom-atlas/issues).*
