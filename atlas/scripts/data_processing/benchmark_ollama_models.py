#!/usr/bin/env python3
"""Benchmark de modelos Ollama para clasificación de plausibilidad científica.

Prueba varios modelos con un conjunto pequeño de papers y evalúa cuál 
produce mejores clasificaciones basado en criterios científicos.
"""

import json
import requests
import time
from pathlib import Path
from typing import Dict, List, Any

# Test cases con ejemplos claros de plausible/implausible
TEST_CASES = [
    {
        "paper_id": "plausible_1",
        "domain": "materials_science", 
        "title": "Enhanced Thermal Conductivity in Graphene-Copper Nanocomposites",
        "abstract": "This study investigates the thermal conductivity enhancement in copper matrix composites reinforced with graphene nanoplatelets. We synthesize nanocomposites using powder metallurgy and characterize thermal properties using laser flash analysis. Results show 35% improvement in thermal conductivity at 2 wt% graphene loading, attributed to efficient heat transfer pathways and strong interfacial bonding.",
        "expected_plausible": True,
        "reasoning": "Factible, metodología clara, resultados razonables"
    },
    {
        "paper_id": "implausible_1", 
        "domain": "physics",
        "title": "Room Temperature Nuclear Fusion Using Kitchen Salt",
        "abstract": "We demonstrate nuclear fusion at room temperature using ordinary table salt (NaCl) and a standard microwave oven. By heating salt for 30 seconds at maximum power, we observe deuterium-tritium fusion reactions producing helium nuclei and neutrons. Energy output exceeds input by factor of 10,000. This revolutionary method could solve world energy crisis.",
        "expected_plausible": False,
        "reasoning": "Viola leyes físicas fundamentales, claims extraordinarios sin evidencia"
    },
    {
        "paper_id": "plausible_2",
        "domain": "biochemistry",
        "title": "CRISPR-Cas9 Mediated Knockout of BRCA1 in Breast Cancer Cell Lines",
        "abstract": "We employed CRISPR-Cas9 genome editing to generate BRCA1 knockout variants in MCF-7 breast cancer cells. Guide RNAs targeting exon 5 were designed and validated. Successful knockouts were confirmed by PCR and Western blot. BRCA1-deficient cells showed increased sensitivity to PARP inhibitors, consistent with synthetic lethality principles.",
        "expected_plausible": True,
        "reasoning": "Metodología establecida, objetivos claros, resultados esperados"
    },
    {
        "paper_id": "implausible_2",
        "domain": "medicine", 
        "title": "Telepathic Communication Enhances Surgical Precision",
        "abstract": "We trained 50 surgeons in telepathic communication techniques and measured surgical precision during complex procedures. Surgeons who achieved telepathic connection with patients showed 95% reduction in complications. Brain wave synchronization between surgeon and patient correlates with improved outcomes. Traditional medical training is obsolete.",
        "expected_plausible": False,
        "reasoning": "No base científica, metodología imposible, claims infundados"
    },
    {
        "paper_id": "borderline_1",
        "domain": "neuroscience",
        "title": "Novel Brain-Computer Interface Using Quantum Entanglement",
        "abstract": "We propose a brain-computer interface leveraging quantum entanglement between neural microtubules and silicon quantum dots. Preliminary experiments show correlation between conscious thought patterns and quantum state measurements. While current resolution is limited, this approach could enable direct neural control of quantum computers.",
        "expected_plausible": False,  # Borderline pero muy especulativo
        "reasoning": "Muy especulativo, mechanisms no establecidos, pero no imposible"
    }
]

MODELS_TO_TEST = [
    "qwen:7b",
    "llama3:8b", 
    "mistral:7b",
    "codellama:7b"
]

def call_ollama(model: str, prompt: str, base_url: str = "http://localhost:11434") -> str:
    """Llamar a Ollama con un modelo específico."""
    url = f"{base_url}/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "top_p": 0.9,
            "num_predict": 500
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=180)
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"ERROR: {str(e)}"

def create_evaluation_prompt(test_case: Dict) -> str:
    """Crear prompt de evaluación con ejemplos."""
    
    examples = """
**EXAMPLES OF EVALUATION:**

PLAUSIBLE Example:
Title: "Machine Learning for Drug Discovery Using Molecular Fingerprints"
- Uses established computational methods
- Builds on existing research
- Feasible with current technology
- Reasonable scope and claims

IMPLAUSIBLE Example:  
Title: "Time Travel Using Household Items"
- Violates fundamental physics laws
- No scientific basis
- Impossible with any known technology
- Extraordinary claims without evidence

**YOUR TASK:**
"""
    
    prompt = f"""You are a scientific peer reviewer evaluating research hypotheses.

{examples}

Evaluate this hypothesis:

Domain: {test_case['domain']}
Title: {test_case['title']}
Abstract: {test_case['abstract']}

Provide your assessment as JSON:
{{
  "validity_score": [0-10],
  "feasibility_score": [0-10], 
  "novelty_score": [0-10],
  "overall_plausible": true/false,
  "confidence": [0.0-1.0],
  "reasoning": "brief explanation"
}}

Focus on:
1. Scientific validity (does it follow known principles?)
2. Technical feasibility (can this actually be done?)
3. Reasonable scope (not too ambitious or trivial?)

Be strict but fair. Extraordinary claims require extraordinary evidence."""

    return prompt

def evaluate_model_on_test_case(model: str, test_case: Dict) -> Dict:
    """Evaluar un modelo en un caso de test."""
    
    prompt = create_evaluation_prompt(test_case)
    
    print(f"  Testing {test_case['paper_id']} (expected: {'✅' if test_case['expected_plausible'] else '❌'})")
    
    start_time = time.time()
    response = call_ollama(model, prompt)
    duration = time.time() - start_time
    
    if response.startswith("ERROR:"):
        return {
            "error": response,
            "duration": duration,
            "correct": False
        }
    
    # Extract JSON
    try:
        if '```json' in response:
            json_str = response.split('```json')[1].split('```')[0].strip()
        elif '{' in response and '}' in response:
            start = response.find('{')
            end = response.rfind('}') + 1
            json_str = response[start:end]
        else:
            raise ValueError("No JSON found")
        
        result = json.loads(json_str)
        
        predicted_plausible = result.get('overall_plausible', True)
        is_correct = predicted_plausible == test_case['expected_plausible']
        
        return {
            "prediction": predicted_plausible,
            "expected": test_case['expected_plausible'], 
            "correct": is_correct,
            "confidence": result.get('confidence', 0.0),
            "reasoning": result.get('reasoning', ''),
            "duration": duration,
            "raw_response": response
        }
        
    except Exception as e:
        return {
            "error": f"JSON parsing failed: {e}",
            "raw_response": response,
            "duration": duration,
            "correct": False
        }

def benchmark_models():
    """Ejecutar benchmark completo."""
    
    print("🧪 BENCHMARK DE MODELOS OLLAMA PARA CLASIFICACIÓN CIENTÍFICA")
    print("=" * 70)
    
    results = {}
    
    for model in MODELS_TO_TEST:
        print(f"\n🤖 Evaluando modelo: {model}")
        print("-" * 50)
        
        model_results = {
            'test_cases': {},
            'summary': {
                'total_correct': 0,
                'total_tests': len(TEST_CASES),
                'accuracy': 0.0,
                'avg_duration': 0.0,
                'total_errors': 0
            }
        }
        
        total_duration = 0
        
        for test_case in TEST_CASES:
            result = evaluate_model_on_test_case(model, test_case)
            model_results['test_cases'][test_case['paper_id']] = result
            
            if result['correct']:
                model_results['summary']['total_correct'] += 1
                print(f"    ✅ Correcto ({result['duration']:.1f}s)")
            elif 'error' in result:
                model_results['summary']['total_errors'] += 1
                print(f"    ❌ Error: {result['error'][:50]}...")
            else:
                print(f"    ❌ Incorrecto - Predijo: {'plausible' if result['prediction'] else 'implausible'}")
            
            total_duration += result['duration']
        
        # Calcular estadísticas
        model_results['summary']['accuracy'] = model_results['summary']['total_correct'] / len(TEST_CASES)
        model_results['summary']['avg_duration'] = total_duration / len(TEST_CASES)
        
        results[model] = model_results
        
        print(f"  📊 Precisión: {model_results['summary']['accuracy']:.1%}")
        print(f"  ⏱️  Tiempo promedio: {model_results['summary']['avg_duration']:.1f}s")
    
    # Mostrar resultados finales
    print(f"\n🏆 RESULTADOS FINALES")
    print("=" * 70)
    
    best_model = None
    best_score = -1
    
    for model, data in results.items():
        summary = data['summary']
        # Score combinado: precisión es más importante que velocidad
        score = summary['accuracy'] * 0.8 + (1.0 / (1.0 + summary['avg_duration'] / 10)) * 0.2
        
        print(f"{model:15} | Precisión: {summary['accuracy']:>6.1%} | "
              f"Tiempo: {summary['avg_duration']:>5.1f}s | Score: {score:.3f}")
        
        if score > best_score:
            best_score = score
            best_model = model
    
    print(f"\n🥇 GANADOR: {best_model} (score: {best_score:.3f})")
    
    # Guardar resultados detallados
    output_file = Path("data/model_benchmark_results.json")
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'results': results,
            'winner': best_model,
            'test_cases_used': TEST_CASES
        }, f, indent=2, ensure_ascii=False)
    
    print(f"📁 Resultados guardados en: {output_file}")
    
    return best_model

if __name__ == '__main__':
    best_model = benchmark_models()
    print(f"\n✨ Usar modelo '{best_model}' para clasificación a gran escala")
