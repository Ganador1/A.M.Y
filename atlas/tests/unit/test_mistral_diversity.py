#!/usr/bin/env python3
"""Test de diversidad: crear hipótesis implausibles y probar si Mistral las detecta."""

import json
import requests
import time
from pathlib import Path

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

# Hipótesis de test con diferentes niveles de plausibilidad
TEST_HYPOTHESES = [
    {
        "id": "clearly_plausible",
        "domain": "materials_science",
        "title": "Carbon Fiber Reinforcement in Polymer Composites",
        "abstract": "We investigate the mechanical properties of epoxy resin reinforced with 10-30% carbon fiber. Tensile strength and flexural modulus are measured using ASTM standards. Preliminary results show 40% increase in tensile strength at 20% fiber loading.",
        "expected": True,
        "type": "Claramente plausible"
    },
    {
        "id": "moderately_plausible", 
        "domain": "medicine",
        "title": "Novel Biomarker for Early Alzheimer's Detection in Saliva",
        "abstract": "We propose that tau protein fragments in saliva correlate with early-stage Alzheimer's disease. Using mass spectrometry, we analyze saliva samples from 100 patients and 100 controls. Initial data suggests 3-fold elevation of specific tau isoforms in pre-clinical stages.",
        "expected": True,
        "type": "Moderadamente plausible"
    },
    {
        "id": "borderline_implausible",
        "domain": "physics", 
        "title": "Room Temperature Superconductor Using Graphene Quantum Dots",
        "abstract": "We claim to achieve room temperature superconductivity by arranging graphene quantum dots in specific geometric patterns. Resistance drops to zero at 25°C in our preliminary experiments. This breakthrough could revolutionize energy transmission worldwide.",
        "expected": False,
        "type": "Borderline implausible - claims extraordinarios"
    },
    {
        "id": "clearly_implausible_1",
        "domain": "physics",
        "title": "Perpetual Motion Machine Using Magnetic Levitation",
        "abstract": "Our design uses permanent magnets arranged in a specific configuration to create continuous motion without energy input. The rotating mechanism generates more energy than it consumes, violating conservation of energy. We achieve 150% efficiency in laboratory tests.",
        "expected": False,
        "type": "Claramente implausible - viola termodinámica"
    },
    {
        "id": "clearly_implausible_2",
        "domain": "medicine",
        "title": "Telepathic Brain Implant for Remote Surgery",
        "abstract": "We developed a brain-computer interface that enables surgeons to perform operations through telepathic communication. Neural implants read surgeon's thoughts and transmit them to robotic surgical instruments 1000km away. Success rate is 99% for complex cardiac procedures.",
        "expected": False,
        "type": "Claramente implausible - telepathy pseudocientífica"
    },
    {
        "id": "clearly_implausible_3",
        "domain": "chemistry",
        "title": "Water-Powered Car Engine Using Consciousness Energy",
        "abstract": "Our revolutionary engine splits water molecules using focused human consciousness as the energy source. Meditative thoughts from the driver catalyze H2O decomposition more efficiently than electrolysis. Vehicle range exceeds 500km per liter of water.",
        "expected": False,
        "type": "Claramente implausible - pseudociencia + consciousness"
    }
]

EVALUATION_PROMPT = """You are a scientific hypothesis evaluator with expertise across multiple domains. 
Your task is to assess the scientific plausibility of research hypotheses.

**EXAMPLES FOR CALIBRATION:**

PLAUSIBLE Examples:
1. "Enhanced Thermal Conductivity in Graphene-Copper Nanocomposites" 
   - Uses established materials science principles
   - Methodology is feasible (powder metallurgy, laser flash analysis)
   - Results are reasonable (35% improvement at 2 wt%)
   → PLAUSIBLE ✅

IMPLAUSIBLE Examples:
1. "Room Temperature Nuclear Fusion Using Kitchen Salt"
   - Violates fundamental physics (Coulomb barrier)
   - Claims extraordinary energy output (10,000x) without evidence
   - Methodology impossible with household items
   → IMPLAUSIBLE ❌

2. "Perpetual Motion Machine Using Magnetic Levitation"
   - Violates conservation of energy (thermodynamics)
   - Claims >100% efficiency (impossible)
   - No scientific basis for continuous motion without input
   → IMPLAUSIBLE ❌

**NOW EVALUATE THIS HYPOTHESIS:**

Domain: {domain}
Title: {title}
Abstract: {abstract}

**PROVIDE YOUR ASSESSMENT AS VALID JSON:**
{{
  "validity_score": X,
  "feasibility_score": Y, 
  "novelty_score": Z,
  "reasoning": "Detailed explanation of your assessment focusing on why plausible/implausible",
  "overall_plausible": true/false,
  "confidence": 0.XX
}}

Be thorough but decisive. Consider fundamental scientific principles and be strict about extraordinary claims."""

def test_mistral_diversity():
    print("🧪 TEST DE DIVERSIDAD: ¿Puede Mistral detectar hipótesis implausibles?")
    print("=" * 70)
    
    results = []
    
    for i, hyp in enumerate(TEST_HYPOTHESES):
        print(f"\n[{i+1}/6] Testing: {hyp['type']}")
        print(f"Título: {hyp['title']}")
        print(f"Esperado: {'✅ Plausible' if hyp['expected'] else '❌ Implausible'}")
        
        prompt = EVALUATION_PROMPT.format(
            domain=hyp['domain'],
            title=hyp['title'],
            abstract=hyp['abstract']
        )
        
        start_time = time.time()
        response = call_ollama("mistral:7b", prompt)
        duration = time.time() - start_time
        
        if response.startswith("ERROR:"):
            print(f"❌ Error: {response}")
            results.append({"id": hyp['id'], "error": response})
            continue
        
        # Parse JSON response
        try:
            # Limpiar respuesta
            response_clean = response.replace('\n', ' ').replace('\r', ' ')
            response_clean = ''.join(char for char in response_clean if ord(char) >= 32 or char in '\n\r\t')
            
            if '{' in response_clean and '}' in response_clean:
                start = response_clean.find('{')
                end = response_clean.rfind('}') + 1
                json_str = response_clean[start:end]
            else:
                raise ValueError("No JSON found")
            
            result = json.loads(json_str)
            
            predicted = result.get('overall_plausible', True)
            is_correct = predicted == hyp['expected']
            confidence = result.get('confidence', 0.0)
            reasoning = result.get('reasoning', '')
            
            results.append({
                "id": hyp['id'],
                "expected": hyp['expected'],
                "predicted": predicted,
                "correct": is_correct,
                "confidence": confidence,
                "reasoning": reasoning,
                "duration": duration
            })
            
            if is_correct:
                print(f"✅ CORRECTO - Predijo: {'plausible' if predicted else 'implausible'} (conf: {confidence})")
            else:
                print(f"❌ INCORRECTO - Predijo: {'plausible' if predicted else 'implausible'} (esperado: {'plausible' if hyp['expected'] else 'implausible'})")
                
            print(f"Razonamiento: {reasoning[:100]}...")
            print(f"Tiempo: {duration:.1f}s")
            
        except Exception as e:
            print(f"❌ Error parseando JSON: {e}")
            results.append({"id": hyp['id'], "parse_error": str(e), "raw": response[:200]})
    
    # Resumen final
    print(f"\n🎯 RESUMEN FINAL")
    print("=" * 50)
    
    correct = sum(1 for r in results if r.get('correct', False))
    total = len([r for r in results if 'correct' in r])
    
    if total > 0:
        accuracy = correct / total
        print(f"Precisión: {accuracy:.1%} ({correct}/{total})")
        
        # Análisis por tipo
        plausible_correct = sum(1 for r in results if r.get('correct') and r.get('expected'))
        implausible_correct = sum(1 for r in results if r.get('correct') and not r.get('expected', True))
        
        print(f"Detecta plausibles: {plausible_correct}/{sum(1 for h in TEST_HYPOTHESES if h['expected'])}")
        print(f"Detecta implausibles: {implausible_correct}/{sum(1 for h in TEST_HYPOTHESES if not h['expected'])}")
        
        if implausible_correct == 0:
            print("⚠️  PROBLEMA: No detecta ninguna hipótesis implausible!")
        
    # Guardar resultados
    output_file = Path("data/mistral_diversity_test.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'results': results,
            'test_hypotheses': TEST_HYPOTHESES,
            'summary': {
                'total_correct': correct,
                'total_tests': total,
                'accuracy': accuracy if total > 0 else 0.0
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"📁 Resultados guardados en: {output_file}")
    
    return results

if __name__ == '__main__':
    test_mistral_diversity()
