#!/usr/bin/env python3
"""
Clasificador LLM mejorado que guarda respuestas completas y métricas de confianza
para posterior entrenamiento ML con confidence scores.
"""

import json
import time
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import argparse

class EnhancedOllamaClassifier:
    """Clasificador con logging completo de respuestas y confidence metrics."""
    
    def __init__(self, model: str = "mistral:7b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.total_processed = 0
        self.total_errors = 0
        self.confidence_distribution = []
        
        # Enhanced evaluation prompt with more examples
        self.evaluation_prompt = """You are a scientific hypothesis evaluator with expertise across multiple domains. 
Your task is to assess the scientific plausibility of research hypotheses.

**EXAMPLES FOR CALIBRATION:**

PLAUSIBLE Examples:
1. "Enhanced Thermal Conductivity in Graphene-Copper Nanocomposites" 
   - Uses established materials science principles
   - Methodology is feasible (powder metallurgy, laser flash analysis)
   - Results are reasonable (35% improvement at 2 wt%)
   → PLAUSIBLE ✅

2. "Correlation Between Vitamin D Levels and COVID-19 Severity"
   - Based on known immunological mechanisms
   - Uses standard clinical measurements
   - Statistical approach is appropriate
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

3. "Water-Powered Car Engine Using Consciousness Energy"
   - Pseudoscientific mechanism (consciousness as energy)
   - Violates thermodynamics and chemistry
   - No reproducible methodology
   → IMPLAUSIBLE ❌

**ASSESSMENT CRITERIA:**
- **Validity**: Does it follow established scientific principles?
- **Feasibility**: Is the methodology technically possible?
- **Novelty**: Is it genuinely innovative vs breakthrough claims?
- **Evidence**: Are results reasonable for the claimed methodology?

**NOW EVALUATE THIS HYPOTHESIS:**

Domain: {domain}
Title: {title}
Abstract: {abstract}

**PROVIDE YOUR ASSESSMENT AS VALID JSON:**
{{
  "validity_score": X.XX,
  "feasibility_score": Y.YY, 
  "novelty_score": Z.ZZ,
  "reasoning": "Detailed explanation focusing on why plausible/implausible with specific scientific justification",
  "overall_plausible": true/false,
  "confidence": 0.XX,
  "red_flags": ["list", "of", "concerning", "aspects"],
  "strengths": ["list", "of", "positive", "aspects"]
}}

IMPORTANT: Be thorough but decisive. Consider fundamental scientific principles and be appropriately skeptical of extraordinary claims without extraordinary evidence."""

    def call_ollama(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call Ollama API with enhanced error handling."""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "num_predict": 700,
                "stop": ["Human:", "Assistant:"]
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=180)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            return None
    
    def parse_llm_response(self, raw_response: str) -> Optional[Dict[str, Any]]:
        """Parse LLM response with robust JSON extraction."""
        try:
            # Clean response
            cleaned = raw_response.replace('\n', ' ').replace('\r', ' ')
            cleaned = ''.join(char for char in cleaned if ord(char) >= 32 or char in '\n\r\t')
            
            # Find JSON block
            if '{' in cleaned and '}' in cleaned:
                start = cleaned.find('{')
                end = cleaned.rfind('}') + 1
                json_str = cleaned[start:end]
            else:
                return None
            
            # Parse JSON
            result = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['validity_score', 'feasibility_score', 'novelty_score', 
                             'reasoning', 'overall_plausible', 'confidence']
            
            for field in required_fields:
                if field not in result:
                    print(f"⚠️ Missing required field: {field}")
                    return None
            
            # Normalize scores to 0-1 range
            for score_field in ['validity_score', 'feasibility_score', 'novelty_score', 'confidence']:
                if isinstance(result[score_field], (int, float)):
                    result[score_field] = max(0.0, min(1.0, float(result[score_field])))
                else:
                    result[score_field] = 0.5  # Default fallback
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse error: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ Parse error: {str(e)}")
            return None
    
    def classify_paper(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """Classify single paper with complete logging."""
        
        title = paper.get('title', '')[:200]  # Limit title length
        abstract = paper.get('abstract', '')[:1000]  # Limit abstract length
        domain = paper.get('expected_domain', paper.get('source', 'unknown'))
        
        if not title or not abstract:
            return {
                'paper_id': paper.get('paper_id', 'unknown'),
                'classification_error': 'Missing title or abstract',
                'timestamp': datetime.now().isoformat()
            }
        
        # Format prompt
        prompt = self.evaluation_prompt.format(
            domain=domain,
            title=title,
            abstract=abstract
        )
        
        # Call LLM
        start_time = time.time()
        llm_response = self.call_ollama(prompt)
        duration = time.time() - start_time
        
        if not llm_response:
            self.total_errors += 1
            return {
                'paper_id': paper.get('paper_id', 'unknown'),
                'classification_error': 'LLM API call failed',
                'timestamp': datetime.now().isoformat(),
                'duration': duration
            }
        
        # Parse response
        parsed_result = self.parse_llm_response(llm_response.get('response', ''))
        
        if not parsed_result:
            self.total_errors += 1
            return {
                'paper_id': paper.get('paper_id', 'unknown'),
                'classification_error': 'Failed to parse LLM response',
                'raw_response': llm_response.get('response', '')[:500],
                'timestamp': datetime.now().isoformat(),
                'duration': duration
            }
        
        # Successful classification
        self.total_processed += 1
        confidence = parsed_result.get('confidence', 0.5)
        self.confidence_distribution.append(confidence)
        
        # Build comprehensive result
        result = {
            # Paper metadata
            'paper_id': paper.get('paper_id', 'unknown'),
            'title': title,
            'abstract': abstract[:500] + ('...' if len(abstract) > 500 else ''),
            'domain': domain,
            'source': paper.get('source', 'unknown'),
            'year': paper.get('year'),
            
            # Classification results
            'plausible': parsed_result['overall_plausible'],
            'confidence': confidence,
            'validity_score': parsed_result['validity_score'],
            'feasibility_score': parsed_result['feasibility_score'],
            'novelty_score': parsed_result['novelty_score'],
            'reasoning': parsed_result['reasoning'],
            'red_flags': parsed_result.get('red_flags', []),
            'strengths': parsed_result.get('strengths', []),
            
            # Technical metadata
            'model_used': self.model,
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': duration,
            'llm_response_length': len(llm_response.get('response', '')),
        }
        
        return result
    
    def classify_dataset(self, input_file: str, output_file: str, max_papers: Optional[int] = None) -> Dict[str, Any]:
        """Classify entire dataset with progress tracking."""
        
        input_path = Path(input_file)
        output_path = Path(output_file)
        log_path = output_path.with_suffix('.log')
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Load papers
        papers = []
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    papers.append(json.loads(line))
        
        if max_papers:
            papers = papers[:max_papers]
        
        total_papers = len(papers)
        
        print(f"🤖 CLASIFICACIÓN MASIVA CON {self.model.upper()}")
        print(f"📊 Papers a procesar: {total_papers}")
        print(f"⏰ Tiempo estimado: {total_papers * 12 / 3600:.1f} horas")
        print(f"📁 Resultados: {output_file}")
        print(f"📝 Log: {log_path}")
        print("=" * 60)
        
        start_time = time.time()
        results = []
        
        # Create output directory
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Process papers
        for i, paper in enumerate(papers):
            print(f"[{i+1:4d}/{total_papers}] ", end="")
            
            try:
                result = self.classify_paper(paper)
                results.append(result)
                
                if 'classification_error' in result:
                    print(f"❌ Error: {result['classification_error']}")
                else:
                    is_plausible = result['plausible']
                    confidence = result['confidence']
                    symbol = "✅" if is_plausible else "❌"
                    print(f"{symbol} {result['title'][:50]}... (conf: {confidence:.2f})")
                
                # Save intermediate results every 10 papers
                if (i + 1) % 10 == 0:
                    self.save_intermediate_results(results, output_path, i + 1)
                    self.log_progress(log_path, i + 1, total_papers)
                
            except KeyboardInterrupt:
                print("\n🛑 Proceso interrumpido por usuario")
                break
            except Exception as e:
                error_result = {
                    'paper_id': paper.get('paper_id', f'paper_{i+1}'),
                    'classification_error': f'Unexpected error: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                }
                results.append(error_result)
                print(f"❌ Unexpected error: {str(e)}")
        
        # Save final results
        self.save_final_results(results, output_path)
        
        # Generate summary statistics
        summary = self.generate_summary_stats(results, time.time() - start_time)
        
        summary_path = output_path.with_suffix('.summary.json')
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎯 CLASIFICACIÓN COMPLETADA")
        print(f"📊 Estadísticas:")
        print(f"   Procesados exitosamente: {self.total_processed}")
        print(f"   Errores: {self.total_errors}")
        total_attempts = self.total_processed + self.total_errors
        success_rate = (self.total_processed / total_attempts * 100) if total_attempts > 0 else 0
        print(f"   Tasa de éxito: {success_rate:.1f}%")
        if self.confidence_distribution:
            print(f"   Confianza promedio: {sum(self.confidence_distribution)/len(self.confidence_distribution):.3f}")
        print(f"📁 Resumen guardado: {summary_path}")
        
        return summary
    
    def save_intermediate_results(self, results: List[Dict[str, Any]], output_path: Path, count: int):
        """Save intermediate results."""
        backup_path = output_path.with_name(f"{output_path.stem}_backup_{count}{output_path.suffix}")
        self.save_results_to_file(results, backup_path)
    
    def save_final_results(self, results: List[Dict[str, Any]], output_path: Path):
        """Save final results."""
        self.save_results_to_file(results, output_path)
    
    def save_results_to_file(self, results: List[Dict[str, Any]], file_path: Path):
        """Save results to JSONL file."""
        with open(file_path, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')
    
    def log_progress(self, log_path: Path, current: int, total: int):
        """Log progress to file."""
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now().isoformat()} - Progress: {current}/{total} ({current/total*100:.1f}%)\n")
    
    def generate_summary_stats(self, results: List[Dict[str, Any]], total_time: float) -> Dict[str, Any]:
        """Generate comprehensive summary statistics."""
        
        successful = [r for r in results if 'classification_error' not in r]
        errors = [r for r in results if 'classification_error' in r]
        
        if not successful:
            return {
                'total_papers': len(results),
                'successful_classifications': 0,
                'errors': len(errors),
                'error_rate': 1.0,
                'total_time_minutes': total_time / 60,
            }
        
        plausible = [r for r in successful if r.get('plausible', False)]
        implausible = [r for r in successful if not r.get('plausible', True)]
        
        # Confidence statistics
        confidences = [r.get('confidence', 0.5) for r in successful]
        
        # Score statistics
        validity_scores = [r.get('validity_score', 0.5) for r in successful]
        feasibility_scores = [r.get('feasibility_score', 0.5) for r in successful]
        novelty_scores = [r.get('novelty_score', 0.5) for r in successful]
        
        return {
            'total_papers': len(results),
            'successful_classifications': len(successful),
            'errors': len(errors),
            'error_rate': len(errors) / len(results) if results else 0,
            
            'plausibility_distribution': {
                'plausible': len(plausible),
                'implausible': len(implausible),
                'plausible_rate': len(plausible) / len(successful) if successful else 0
            },
            
            'confidence_stats': {
                'mean': sum(confidences) / len(confidences) if confidences else 0,
                'min': min(confidences) if confidences else 0,
                'max': max(confidences) if confidences else 0,
                'distribution': {
                    'high_conf_0.8+': len([c for c in confidences if c >= 0.8]),
                    'medium_conf_0.5-0.8': len([c for c in confidences if 0.5 <= c < 0.8]),
                    'low_conf_<0.5': len([c for c in confidences if c < 0.5])
                }
            },
            
            'score_averages': {
                'validity': sum(validity_scores) / len(validity_scores) if validity_scores else 0,
                'feasibility': sum(feasibility_scores) / len(feasibility_scores) if feasibility_scores else 0,
                'novelty': sum(novelty_scores) / len(novelty_scores) if novelty_scores else 0
            },
            
            'performance_metrics': {
                'total_time_minutes': total_time / 60,
                'avg_time_per_paper': total_time / len(results) if results else 0,
                'papers_per_hour': len(results) / (total_time / 3600) if total_time > 0 else 0
            },
            
            'model_info': {
                'model_name': self.model,
                'classification_timestamp': datetime.now().isoformat()
            }
        }

def main():
    parser = argparse.ArgumentParser(description="Enhanced LLM classifier with full logging")
    parser.add_argument('--input', type=str, 
                       default='data/plausibility_training_v4_candidates.jsonl',
                       help='Input dataset file')
    parser.add_argument('--output', type=str,
                       default='data/llm_classifications_complete.jsonl', 
                       help='Output classifications file')
    parser.add_argument('--model', type=str, default='mistral:7b',
                       help='Ollama model to use')
    parser.add_argument('--max-papers', type=int, default=None,
                       help='Maximum papers to process (for testing)')
    parser.add_argument('--ollama-url', type=str, default='http://localhost:11434',
                       help='Ollama base URL')
    
    args = parser.parse_args()
    
    classifier = EnhancedOllamaClassifier(
        model=args.model,
        base_url=args.ollama_url
    )
    
    try:
        summary = classifier.classify_dataset(
            input_file=args.input,
            output_file=args.output,
            max_papers=args.max_papers
        )
        
        print(f"\n🎉 Clasificación completada exitosamente!")
        print(f"📊 {summary['successful_classifications']} papers clasificados")
        print(f"⚡ {summary['plausibility_distribution']['plausible_rate']:.1%} clasificados como plausibles")
        print(f"🎯 Confianza promedio: {summary['confidence_stats']['mean']:.3f}")
        
    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
