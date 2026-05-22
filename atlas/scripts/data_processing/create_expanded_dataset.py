#!/usr/bin/env python3
"""
Crear dataset expandido con mayor diversidad de dominios, autores y calidad.
Incluye papers de diferentes niveles de calidad para obtener mejor contraste.
"""

import json
import random
import time
from pathlib import Path
from datetime import datetime

# Dominios científicos expandidos
EXPANDED_DOMAINS = [
    "materials_science", "medicine", "physics", "chemistry", "biology",
    "computer_science", "engineering", "neuroscience", "psychology", "geology",
    "astronomy", "environmental_science", "mathematics", "economics",
    "sociology", "anthropology", "linguistics", "archaeology"
]

# Generar hipótesis sintéticas de diferentes niveles de calidad
def generate_diverse_hypotheses():
    """Generar hipótesis con variedad de calidad y dominios."""
    
    # High-quality papers (conservadores, bien fundamentados)
    high_quality = [
        {
            "domain": "materials_science",
            "title": "Enhanced Thermal Conductivity in Graphene-Copper Nanocomposites via Powder Metallurgy",
            "abstract": "We synthesize graphene-copper nanocomposites using powder metallurgy techniques. Thermal conductivity measurements using laser flash analysis show 35% improvement at 2 wt% graphene loading. X-ray diffraction confirms uniform dispersion. Applications in heat sink design are discussed.",
            "authors": "Smith, J.; Wang, L.; Patel, R.",
            "quality_tier": "high"
        },
        {
            "domain": "medicine", 
            "title": "Correlation Between Vitamin D Levels and COVID-19 Severity in Hospitalized Patients",
            "abstract": "Retrospective analysis of 250 hospitalized COVID-19 patients. Serum 25(OH)D levels measured at admission. Patients with severe deficiency (<10 ng/mL) had 2.3x higher ICU admission rate (p<0.01). Results suggest vitamin D supplementation trials warranted.",
            "authors": "Johnson, M.; Lee, S.; Rodriguez, A.",
            "quality_tier": "high"
        },
        {
            "domain": "computer_science",
            "title": "Optimized LSTM Architecture for Time Series Forecasting in Financial Markets",
            "abstract": "We propose bidirectional LSTM with attention mechanism for stock price prediction. Evaluation on S&P 500 data shows 15% improvement in RMSE over baseline RNN. Feature engineering includes technical indicators and sentiment analysis of news data.",
            "authors": "Chen, X.; Williams, D.; Kumar, A.",
            "quality_tier": "high"
        }
    ]
    
    # Medium-quality papers (metodología cuestionable, claims moderados)
    medium_quality = [
        {
            "domain": "psychology",
            "title": "Crystal Healing Effects on Anxiety Levels: A Controlled Study",
            "abstract": "We investigate amethyst crystal therapy on 30 anxiety patients vs 30 controls. Self-reported anxiety scores decreased 40% in crystal group vs 5% in control (p=0.08). While not statistically significant, trend suggests potential therapeutic value of crystals.",
            "authors": "Miller, K.; Thompson, B.",
            "quality_tier": "medium"
        },
        {
            "domain": "medicine",
            "title": "Homeopathic Remedies for Chronic Fatigue: Promising Preliminary Results", 
            "abstract": "Pilot study of 20 chronic fatigue patients treated with individualized homeopathic preparations. Energy levels improved in 70% of patients over 6 months. Larger randomized controlled trials needed to confirm efficacy of homeopathic intervention.",
            "authors": "Davis, P.; Wilson, J.",
            "quality_tier": "medium"
        },
        {
            "domain": "environmental_science",
            "title": "Magnetic Water Treatment for Enhanced Plant Growth in Desert Conditions",
            "abstract": "We expose irrigation water to magnetic fields (0.5 Tesla) before watering tomato plants in arid soil. Treated plants show 25% better growth metrics. Mechanism unclear but may involve molecular water structure changes affecting nutrient uptake.",
            "authors": "Garcia, L.; Ahmed, F.",
            "quality_tier": "medium"
        }
    ]
    
    # Low-quality papers (metodología pobre, claims extraordinarios)
    low_quality = [
        {
            "domain": "physics",
            "title": "Zero-Point Energy Harvesting Using Copper Wire Coils in Vacuum",
            "abstract": "Our device extracts usable energy from quantum vacuum fluctuations using specially wound copper coils. Power output reaches 50 watts continuously without external input. Commercial applications could solve global energy crisis. Patent pending on revolutionary technology.",
            "authors": "Johnson, Q.; Brown, X.",
            "quality_tier": "low"
        },
        {
            "domain": "biology",
            "title": "Telepathic Communication Between House Plants Mediated by Quantum Entanglement",
            "abstract": "We demonstrate information transfer between geranium plants separated by 100 meters. When one plant is damaged, the other shows stress responses within 30 seconds. Quantum entanglement theory explains instantaneous plant-to-plant communication mechanism.",
            "authors": "Green, M.; Leaf, S.",
            "quality_tier": "low"
        },
        {
            "domain": "medicine",
            "title": "Curing Cancer Through Positive Thinking and Chakra Alignment Therapy",
            "abstract": "15 terminal cancer patients achieved complete remission through 8-week positive visualization program combined with chakra energy balancing. No conventional treatment used. Results demonstrate mind-body connection more powerful than chemotherapy or radiation.",
            "authors": "Healer, A.; Crystal, B.",
            "quality_tier": "low"
        },
        {
            "domain": "engineering",
            "title": "Perpetual Motion Generator Using Neodymium Magnet Arrays for Free Energy",
            "abstract": "Our magnetic motor achieves 180% efficiency using precisely arranged neodymium magnets. Device runs continuously for 6 months without external power. Violates thermodynamics laws but practical applications unlimited. Planning commercial production soon.",
            "authors": "Tesla, N.; Edison, T.",
            "quality_tier": "low"
        }
    ]
    
    # Borderline papers (claims ambiciosos pero con algo de base científica)
    borderline_quality = [
        {
            "domain": "neuroscience",
            "title": "Room Temperature Superconducting Neural Interfaces Using Graphene Quantum Dots",
            "abstract": "We achieve zero electrical resistance in neural electrodes at body temperature using quantum dot arrays. Brain signal recording improved 1000x over conventional electrodes. Breakthrough could enable direct brain-computer communication at unprecedented bandwidth.",
            "authors": "Neural, A.; Interface, B.",
            "quality_tier": "borderline"
        },
        {
            "domain": "chemistry", 
            "title": "Cold Fusion Achieved Using Palladium Electrodes and Heavy Water Electrolysis",
            "abstract": "Electrolytic cell produces excess heat (300% of input) and nuclear byproducts consistent with deuterium fusion. Neutron detectors confirm nuclear reactions at room temperature. Reproducibility challenging but results suggest LENR phenomenon is real.",
            "authors": "Fusion, C.; Nuclear, D.",
            "quality_tier": "borderline"
        },
        {
            "domain": "materials_science",
            "title": "Self-Healing Concrete Using Bacterial Spores and Calcium Lactate",
            "abstract": "Concrete embedded with Bacillus spores automatically repairs cracks when water enters. Bacteria precipitate calcium carbonate, sealing cracks up to 2mm width. Laboratory tests show 90% strength recovery after 28 days healing.",
            "authors": "Concrete, S.; Bacteria, L.",
            "quality_tier": "borderline"
        }
    ]
    
    # Combine all categories
    all_papers = []
    
    # Múltiples instancias para generar más variedad
    for _ in range(3):  # 3 variaciones de cada categoría
        all_papers.extend(high_quality)
        all_papers.extend(medium_quality) 
        all_papers.extend(low_quality)
        all_papers.extend(borderline_quality)
    
    # Añadir papers sintéticos adicionales con variaciones
    additional_papers = []
    
    domains_extended = EXPANDED_DOMAINS
    quality_levels = ["high", "medium", "low", "borderline"]
    
    # Generar papers sintéticos adicionales
    synthetic_templates = [
        {
            "template": "Novel {material} for Enhanced {property} in {application}",
            "domain": "materials_science",
            "abstract_template": "We synthesize {material} using {method}. {measurement} shows {improvement}% improvement over baseline. {analysis} confirms {result}. Applications in {field} are promising."
        },
        {
            "template": "{compound} Treatment for {disease}: {trial_type} Study",
            "domain": "medicine", 
            "abstract_template": "We investigate {compound} therapy in {n} {disease} patients. {outcome} improved by {percent}% compared to placebo ({p_value}). {mechanism} may explain therapeutic effects."
        },
        {
            "template": "{algorithm} Algorithm for {task} Using {technique}",
            "domain": "computer_science",
            "abstract_template": "We propose {algorithm} approach for {task}. Evaluation on {dataset} shows {metric} improvement of {percent}%. {feature} provides key advantage over existing methods."
        }
    ]
    
    # Generar más papers variados
    materials = ["graphene", "carbon nanotubes", "perovskite", "quantum dots", "metamaterials"]
    compounds = ["curcumin", "resveratrol", "CBD oil", "stem cells", "monoclonal antibodies"]
    algorithms = ["deep learning", "reinforcement learning", "genetic algorithm", "neural network", "transformer"]
    
    for i in range(50):  # 50 papers sintéticos adicionales
        template = random.choice(synthetic_templates)
        quality = random.choice(quality_levels)
        
        if template["domain"] == "materials_science":
            title = template["template"].format(
                material=random.choice(materials),
                property=random.choice(["conductivity", "strength", "flexibility"]),
                application=random.choice(["electronics", "aerospace", "automotive"])
            )
        elif template["domain"] == "medicine":
            title = template["template"].format(
                compound=random.choice(compounds),
                disease=random.choice(["cancer", "diabetes", "Alzheimer's"]),
                trial_type=random.choice(["Pilot", "Phase II", "Randomized"])
            )
        else:
            title = template["template"].format(
                algorithm=random.choice(algorithms),
                task=random.choice(["classification", "prediction", "optimization"]),
                technique=random.choice(["attention", "adversarial training", "transfer learning"])
            )
        
        additional_papers.append({
            "domain": template["domain"],
            "title": title,
            "abstract": f"Synthetic paper {i+1} for {template['domain']} research with {quality} quality indicators.",
            "authors": f"Author{i}, B.; Coauthor{i}, C.",
            "quality_tier": quality
        })
    
    all_papers.extend(additional_papers)
    
    # Shuffle para mezclar calidades
    random.shuffle(all_papers)
    
    return all_papers

def create_expanded_dataset():
    """Crear dataset expandido y guardarlo."""
    
    print("🚀 Generando dataset expandido con diversidad de calidad...")
    
    papers = generate_diverse_hypotheses()
    
    print(f"📊 Dataset generado:")
    print(f"   Total papers: {len(papers)}")
    
    # Contar por calidad
    quality_counts = {}
    for paper in papers:
        tier = paper.get("quality_tier", "unknown")
        quality_counts[tier] = quality_counts.get(tier, 0) + 1
    
    for tier, count in quality_counts.items():
        print(f"   {tier.capitalize()}: {count} papers")
    
    # Contar por dominio
    domain_counts = {}
    for paper in papers:
        domain = paper["domain"]
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    print(f"\n📚 Por dominio:")
    for domain, count in sorted(domain_counts.items()):
        print(f"   {domain}: {count} papers")
    
    # Guardar dataset
    output_file = Path("data/plausibility_expanded_dataset.jsonl")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, paper in enumerate(papers):
            paper["id"] = f"paper_{i+1:04d}"
            paper["created_at"] = datetime.now().isoformat()
            f.write(json.dumps(paper, ensure_ascii=False) + '\n')
    
    print(f"\n📁 Dataset guardado en: {output_file}")
    print(f"💡 Listo para clasificación con Mistral (estimado: {len(papers) * 12 / 3600:.1f} horas)")
    
    return output_file, len(papers)

if __name__ == '__main__':
    create_expanded_dataset()
