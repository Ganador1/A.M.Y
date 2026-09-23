#!/usr/bin/env python3
"""Clasificador automático de plausibilidad científica usando LLM.

Basado en research papers recientes sobre automated hypothesis evaluation,
especialmente:
- Yang et al. (2023): "Large language models for automated open-domain scientific hypotheses discovery"
- Gil et al. (2016): "Automated hypothesis testing with large scientific data repositories"
- Callahan (2014): "Semi-automated hypothesis evaluation using semantic technologies"

El enfoque usa GPT/OpenAI para evaluar cada hipótesis en tres dimensiones:
1. Validez científica (soundness)
2. Factibilidad técnica (feasibility) 
3. Novedad/originalidad (novelty)

Luego combina estos scores en una clasificación binaria plausible/implausible.
"""

import json
import time
import argparse
import requests
from pathlib import Path
from typing import Dict, List, Any

# Prompt template basado en research papers + ejemplos de benchmark
EVALUATION_PROMPT = """You are a scientific hypothesis evaluator with expertise across multiple domains. 
Your task is to assess the scientific plausibility of research hypotheses.

**EXAMPLES FOR CALIBRATION:**

PLAUSIBLE Examples:
1. "Enhanced Thermal Conductivity in Graphene-Copper Nanocomposites" 
   - Uses established materials science principles
   - Methodology is feasible (powder metallurgy, laser flash analysis)
   - Results are reasonable (35% improvement at 2 wt%)
   → PLAUSIBLE ✅

2. "CRISPR-Cas9 Mediated Knockout of BRCA1 in Breast Cancer Cell Lines"
   - Well-established genome editing technique
   - Clear experimental design (PCR, Western blot validation)  
   - Expected results (PARP inhibitor sensitivity)
   → PLAUSIBLE ✅

IMPLAUSIBLE Examples:
1. "Room Temperature Nuclear Fusion Using Kitchen Salt"
   - Violates fundamental physics (Coulomb barrier)
   - Claims extraordinary energy output (10,000x) without evidence
   - Methodology impossible with household items
   → IMPLAUSIBLE ❌

2. "Telepathic Communication Enhances Surgical Precision"
   - No scientific basis for telepathy
   - Impossible to measure "brain wave synchronization" meaningfully
   - Claims that contradict established medicine
   → IMPLAUSIBLE ❌

**EVALUATION CRITERIA:**

1. **SCIENTIFIC VALIDITY** (0-10): Does it follow established scientific principles?
   - Are underlying theories sound?
   - Does it contradict known laws of physics/chemistry/biology?
   - Are mechanisms plausible?

2. **TECHNICAL FEASIBILITY** (0-10): Can this realistically be implemented?
   - Are required technologies available?
   - Are resources/scale reasonable?
   - Is methodology clearly described and doable?

3. **SCOPE REASONABLENESS** (0-10): Are claims appropriate?
   - Not too trivial (already known)
   - Not too extraordinary (requires impossible breakthroughs)
   - Builds appropriately on existing knowledge

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

Be thorough but decisive. Consider the domain context and be strict about scientific rigor."""

class OllamaPlausibilityClassifier:
    def __init__(self, model: str = "mistral:7b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.rate_limit_delay = 0.5  # Dar tiempo suficiente para procesamiento de calidad
        
    def _call_ollama(self, prompt: str) -> str:
        """Llamada a Ollama API."""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "num_predict": 500
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()["response"]
        except requests.RequestException as e:
            raise ConnectionError(f"Error conectando con Ollama: {e}")
        except KeyError:
            raise ValueError("Respuesta inválida de Ollama")
        
    def evaluate_hypothesis(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluar una hipótesis usando Ollama."""
        
        prompt = EVALUATION_PROMPT.format(
            domain=record.get('domain', 'Unknown'),
            title=record.get('title', ''),
            abstract=record.get('abstract', '')
        )
        
        try:
            content = self._call_ollama(prompt)
            
            # Limpiar caracteres de control problemáticos
            content = content.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
            content = ''.join(char for char in content if ord(char) >= 32 or char in '\n\r\t')
            
            # Extract JSON from response (multiple strategies)
            json_str = None
            
            if '```json' in content:
                json_str = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                json_str = content.split('```')[1].split('```')[0].strip()
            elif '{' in content and '}' in content:
                # Extract JSON between first { and last }
                start = content.find('{')
                end = content.rfind('}') + 1
                json_str = content[start:end]
            
            if not json_str:
                raise ValueError("No JSON structure found in response")
            
            # Additional cleaning
            json_str = json_str.strip()
            
            result = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['validity_score', 'feasibility_score', 'novelty_score', 'overall_plausible']
            if not all(field in result for field in required_fields):
                raise ValueError(f"Missing required fields in LLM response: {result}")
                
            return result
            
        except Exception as e:
            print(f"Error evaluating hypothesis {record.get('paper_id', 'unknown')}: {e}")
            # Return neutral/skip result
            return {
                'validity_score': 5,
                'feasibility_score': 5,
                'novelty_score': 5,
                'reasoning': f'Evaluation failed: {str(e)}',
                'overall_plausible': True,  # Default to plausible when uncertain
                'confidence': 0.0,
                'error': str(e)
            }

def load_candidates(file_path: Path) -> List[Dict[str, Any]]:
    """Cargar candidatos del archivo JSONL."""
    rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows

def create_manual_labels_from_llm(evaluations: Dict[str, Dict], 
                                 output_path: Path) -> Dict[str, int]:
    """Convertir evaluaciones LLM a formato de labels manuales."""
    
    manual_labels = {}
    
    for paper_id, eval_result in evaluations.items():
        if 'error' in eval_result:
            continue  # Skip failed evaluations
            
        # Convert LLM evaluation to binary label
        is_plausible = eval_result.get('overall_plausible', True)
        manual_labels[paper_id] = 1 if is_plausible else 0
    
    # Create output in same format as manual labeling tool
    output_data = {
        'manual_labels': manual_labels,
        'total_labeled': len(manual_labels),
        'distribution': {
            'plausible': sum(1 for v in manual_labels.values() if v == 1),
            'implausible': sum(1 for v in manual_labels.values() if v == 0)
        },
        'method': 'llm_automated',
        'llm_evaluations': evaluations  # Keep detailed evaluations
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    return manual_labels

def main():
    parser = argparse.ArgumentParser(description='Clasificación automática de plausibilidad científica usando Ollama')
    parser.add_argument('--input', '-i', 
                       default='data/plausibility_training_v4_candidates.jsonl',
                       help='Archivo de candidatos JSONL')
    parser.add_argument('--output', '-o', 
                       default='data/manual_labels_v4_ollama.json',
                       help='Archivo de salida para labels')
    parser.add_argument('--sample', '-n', type=int, default=100,
                       help='Número de registros a evaluar (0 = todos)')
    parser.add_argument('--model', default='mistral:7b',
                       help='Modelo Ollama a usar (mistral:7b recomendado)')
    parser.add_argument('--ollama-url', default='http://localhost:11434',
                       help='URL base de Ollama')
    parser.add_argument('--delay', type=float, default=0.5,
                       help='Segundos de delay entre requests (0.5s para calidad)')
    
    args = parser.parse_args()
    
    # Cargar datos
    candidates = load_candidates(Path(args.input))
    print(f"📖 Cargados {len(candidates)} candidatos de {args.input}")
    
    # Sampling si se especifica
    if args.sample > 0 and len(candidates) > args.sample:
        import random
        random.seed(42)
        candidates = random.sample(candidates, args.sample)
        print(f"🎯 Muestra aleatoria de {args.sample} registros")
    
    # Inicializar clasificador
    classifier = OllamaPlausibilityClassifier(model=args.model, base_url=args.ollama_url)
    classifier.rate_limit_delay = args.delay
    
    print(f"🤖 Iniciando evaluación automática con Ollama: {args.model}")
    print(f"🌐 Ollama URL: {args.ollama_url}")
    print(f"⏱️  Delay entre requests: {args.delay}s")
    print(f"📊 Registros a evaluar: {len(candidates)}")
    
    # Evaluar cada hipótesis
    evaluations = {}
    failed_count = 0
    
    for i, record in enumerate(candidates):
        paper_id = record['paper_id']
        
        print(f"[{i+1}/{len(candidates)}] Evaluando {paper_id[:8]}... ", end='', flush=True)
        
        result = classifier.evaluate_hypothesis(record)
        evaluations[paper_id] = result
        
        if 'error' in result:
            failed_count += 1
            print("❌ FALLÓ")
        else:
            plausible = "✅" if result['overall_plausible'] else "❌"
            confidence = result.get('confidence', 0.0)
            print(f"{plausible} (conf: {confidence:.2f})")
        
        # Rate limiting
        if i < len(candidates) - 1:  # Don't sleep after last request
            time.sleep(classifier.rate_limit_delay)
    
    print("\n🏁 Evaluación completada!")
    print(f"   Exitosos: {len(candidates) - failed_count}")
    print(f"   Fallos: {failed_count}")
    
    # Crear labels manuales
    manual_labels = create_manual_labels_from_llm(evaluations, Path(args.output))
    
    if manual_labels:
        plausible = sum(1 for v in manual_labels.values() if v == 1)
        implausible = len(manual_labels) - plausible
        
        print("\n📊 RESULTADOS:")
        print(f"   Total etiquetados: {len(manual_labels)}")
        print(f"   Plausibles: {plausible} ({plausible/len(manual_labels)*100:.1f}%)")
        print(f"   Implausibles: {implausible} ({implausible/len(manual_labels)*100:.1f}%)")
        print(f"   Guardado en: {args.output}")
    else:
        print("⚠️  No se generaron labels válidos")

if __name__ == '__main__':
    main()
