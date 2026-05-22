#!/usr/bin/env python3
"""
🔬 AXIOM META 4 - Evaluación Científica Comprehensiva
Sistema de pruebas exhaustivas para modelos LLM científicos con datos reales
"""

import json
import time
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import traceback
import requests
import subprocess
from pathlib import Path
from importlib import util as _importlib_util

# Configurar logging detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive_evaluation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveScientificEvaluator:
    """Evaluador comprehensivo de modelos científicos"""
    
    def __init__(self):
        # Lista completa histórica (puede ampliarse si se desactiva single_model_mode)
        full_model_list = [
            "falcon3:1b",
            "falcon3:3b",
            "deepseek-r1:1.5b",
            "qwen2.5:1.5b"
        ]
        # Bandera para restringir a mejor modelo identificado
        self.single_model_mode = True
        self.preferred_model = "deepseek-r1:1.5b"
        self.models_to_test = [self.preferred_model] if self.single_model_mode else full_model_list
        
        self.scientific_domains = [
            "mathematics",
            "physics", 
            "chemistry",
            "biology",
            "engineering",
            "materials_science",
            "medical_imaging",
            "plasma_physics",
            "computational_science"
        ]
        
        self.evaluation_results = {}
        self.ollama_base_url = "http://localhost:11434"
        # Directorio para logs detallados de LLM
        self.llm_log_dir = Path("logs/llm")
        try:
            self.llm_log_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            # Si falla la creación del directorio, continuamos sin interrumpir la evaluación
            pass

    def log_llm_interaction(self, *, model: str, category: str, prompt: str, response: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Guarda cada interacción LLM (prompt/respuesta completos) para auditoría reproducible."""
        try:
            log_item: Dict[str, Any] = {
                "timestamp": datetime.now().isoformat(),
                "model": model,
                "category": category,
                "prompt": prompt,
                "response": response,
                "response_length": len(response or ""),
            }
            if extra:
                log_item.update({"extra": extra})
            # Un archivo JSONL por día
            daily = self.llm_log_dir / f"llm_interactions_{datetime.now().strftime('%Y%m%d')}.jsonl"
            with open(daily, "a", encoding="utf-8") as fp:
                fp.write(json.dumps(log_item, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.debug(f"No se pudo registrar interacción LLM: {e}")
        
    def check_ollama_health(self) -> bool:
        """Verificar que Ollama esté funcionando"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama no está disponible: {e}")
            return False
    
    def test_model_basic_reasoning(self, model: str) -> Dict[str, Any]:
        """Test básico de razonamiento científico"""
        logger.info(f"🧠 Testing basic reasoning for {model}")
        
        test_questions = [
            {
                "question": "What is the relationship between pressure and volume in an ideal gas at constant temperature?",
                "expected_concepts": ["boyle", "law", "inverse", "pressure", "volume"],
                "domain": "physics"
            },
            {
                "question": "Explain the molecular basis of enzyme specificity",
                "expected_concepts": ["active", "site", "substrate", "lock", "key", "binding"],
                "domain": "biology"
            },
            {
                "question": "What factors affect the thermal conductivity of crystalline materials?",
                "expected_concepts": ["phonon", "structure", "defect", "crystal", "temperature"],
                "domain": "materials_science"
            }
        ]
        
        results = []
        for test in test_questions:
            try:
                response = requests.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": test["question"],
                        "stream": False
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    answer = response.json().get("response", "")
                    # Log completo de interacción
                    self.log_llm_interaction(model=model, category="basic_reasoning", prompt=test["question"], response=answer,
                                              extra={"domain": test["domain"]})
                    
                    # Evaluar calidad de respuesta
                    concept_matches = sum(1 for concept in test["expected_concepts"] 
                                        if concept.lower() in answer.lower())
                    
                    score = concept_matches / len(test["expected_concepts"])
                    
                    results.append({
                        "prompt": test["question"],
                        "question": test["question"],
                        "answer": answer,
                        "domain": test["domain"],
                        "concept_score": score,
                        "concept_matches": concept_matches,
                        "total_concepts": len(test["expected_concepts"])
                    })
                else:
                    logger.error(f"Error calling {model}: {response.status_code}")
                    results.append({
                        "question": test["question"],
                        "error": f"HTTP {response.status_code}",
                        "concept_score": 0.0
                    })
                    
            except Exception as e:
                logger.error(f"Exception testing {model}: {e}")
                results.append({
                    "question": test["question"],
                    "error": str(e),
                    "concept_score": 0.0
                })
        
        avg_score = sum(r.get("concept_score", 0) for r in results) / len(results)
        
        return {
            "model": model,
            "average_reasoning_score": avg_score,
            "detailed_results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def test_model_hypothesis_generation(self, model: str) -> Dict[str, Any]:
        """Test de generación de hipótesis científicas"""
        logger.info(f"🔬 Testing hypothesis generation for {model}")
        research_contexts = [
            {
                "field": "materials_science",
                "context": "Recent advances in 2D materials have shown unusual thermal properties in graphene derivatives.",
                "prompt": "Generate a research hypothesis about thermal conductivity enhancement in 2D materials"
            },
            {
                "field": "biology",
                "context": "CRISPR gene editing shows varying efficiency across different cell types.",
                "prompt": "Generate a research hypothesis about factors affecting CRISPR efficiency"
            },
            {
                "field": "physics",
                "context": "Quantum dots exhibit size-dependent optical properties in semiconductor nanocrystals.",
                "prompt": "Generate a research hypothesis about quantum confinement effects in nanostructures"
            }
        ]

        results: list[Dict[str, Any]] = []
        for context in research_contexts:
            try:
                full_prompt = (
                    f"Context: {context['context']}\n\n"
                    f"Task: {context['prompt']}\n\n"
                    "Generate a clear, testable scientific hypothesis with methodology outline."
                )

                response = requests.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": full_prompt,
                        "stream": False,
                    },
                    timeout=120,
                )

                if response.status_code == 200:
                    hypothesis = response.json().get("response", "")
                    # Log completo de interacción
                    self.log_llm_interaction(
                        model=model,
                        category="hypothesis_generation",
                        prompt=full_prompt,
                        response=hypothesis,
                        extra={"field": context["field"]},
                    )

                    # Evaluar calidad de hipótesis
                    h_low = hypothesis.lower()
                    quality_metrics = {
                        "has_prediction": any(word in h_low for word in [
                            "hypothesis",
                            "predict",
                            "expect",
                            "should",
                            "will",
                        ]),
                        "has_methodology": any(word in h_low for word in [
                            "measure",
                            "test",
                            "experiment",
                            "analyze",
                            "method",
                        ]),
                        "has_variables": any(word in h_low for word in [
                            "variable",
                            "parameter",
                            "factor",
                            "control",
                        ]),
                        "is_specific": len(hypothesis.split()) > 50,  # Minimum detail level
                        "field_relevant": context["field"].replace("_", " ") in h_low,
                    }

                    quality_score = sum(1 if v else 0 for v in quality_metrics.values()) / len(quality_metrics)

                    results.append(
                        {
                            "prompt": full_prompt,
                            "field": context["field"],
                            "context": context["context"],
                            "hypothesis": hypothesis,
                            "quality_score": quality_score,
                            "quality_metrics": quality_metrics,
                        }
                    )
                else:
                    logger.error(
                        f"Error in hypothesis generation for {model}: {response.status_code}"
                    )
                    results.append(
                        {
                            "field": context["field"],
                            "error": f"HTTP {response.status_code}",
                            "quality_score": 0.0,
                        }
                    )

            except Exception as e:
                logger.error(f"Exception in hypothesis generation for {model}: {e}")
                results.append(
                    {
                        "field": context["field"],
                        "error": str(e),
                        "quality_score": 0.0,
                    }
                )

        avg_quality = sum(r.get("quality_score", 0) for r in results) / len(results) if results else 0.0

        return {
            "model": model,
            "average_hypothesis_quality": avg_quality,
            "detailed_hypotheses": results,
            "timestamp": datetime.now().isoformat(),
        }
    
    def run_axiom_e2e_with_model(self, model: str) -> Dict[str, Any]:
        """Ejecutar test E2E completo con modelo específico"""
        logger.info(f"🚀 Running full AXIOM E2E test with {model}")
        
        # Configurar el modelo en config
        original_config = self.backup_config()
        
        try:
            # Actualizar configuración para usar el modelo específico
            self.update_config_for_model(model)
            
            # Ejecutar E2E test
            start_time = time.time()
            
            result = subprocess.run([
                sys.executable, "test_axiom_meta4_e2e_real_data.py"
            ], capture_output=True, text=True, timeout=900)  # 15 min timeout
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                # Intentar parsear los resultados del E2E
                try:
                    if os.path.exists("e2e_test_results.json"):
                        with open("e2e_test_results.json", "r") as f:
                            e2e_results = json.load(f)
                    else:
                        e2e_results = {"note": "No results file generated"}
                except Exception as parse_error:
                    logger.warning(f"Could not parse E2E results: {parse_error}")
                    e2e_results = {"error": "Could not parse results"}
                
                return {
                    "model": model,
                    "success": True,
                    "execution_time": execution_time,
                    "stdout": result.stdout[-2000:],  # Last 2000 chars
                    "e2e_results": e2e_results,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "model": model,
                    "success": False,
                    "execution_time": execution_time,
                    "error": result.stderr[-1000:],  # Last 1000 chars of error
                    "stdout": result.stdout[-1000:],
                    "timestamp": datetime.now().isoformat()
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"E2E test with {model} timed out")
            return {
                "model": model,
                "success": False,
                "error": "Test timed out after 15 minutes",
                "execution_time": 900,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Exception in E2E test with {model}: {e}")
            return {
                "model": model,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        finally:
            # Restaurar configuración original
            self.restore_config(original_config)
    
    def backup_config(self) -> dict:
        """Hacer backup de la configuración actual"""
        try:
            with open("app/config.py", "r") as f:
                return {"content": f.read()}
        except Exception as e:
            logger.warning(f"Could not backup config: {e}")
            return {}
    
    def restore_config(self, backup: dict):
        """Restaurar configuración desde backup"""
        try:
            if "content" in backup:
                with open("app/config.py", "w") as f:
                    f.write(backup["content"])
        except Exception as e:
            logger.warning(f"Could not restore config: {e}")
    
    def update_config_for_model(self, model: str):
        """Actualizar configuración para usar modelo específico"""
        try:
            with open("app/config.py", "r") as f:
                config_content = f.read()
            
            # Reemplazar la línea del modelo
            lines = config_content.split('\n')
            for i, line in enumerate(lines):
                if 'ollama_model' in line and '=' in line:
                    lines[i] = f'ollama_model = "{model}"'
                    break
            
            with open("app/config.py", "w") as f:
                f.write('\n'.join(lines))
                
            logger.info(f"Updated config to use {model}")
            
        except Exception as e:
            logger.error(f"Could not update config for {model}: {e}")
    
    def run_comprehensive_evaluation(self) -> Dict[str, Any]:
        """Ejecutar evaluación comprehensiva completa"""
        logger.info("🎯 Starting comprehensive scientific evaluation")
        
        if not self.check_ollama_health():
            raise Exception("Ollama is not available - cannot proceed with evaluation")
        
        evaluation_start = time.time()
        results = {
            "evaluation_metadata": {
                "start_time": datetime.now().isoformat(),
                "models_tested": self.models_to_test,
                "domains_covered": self.scientific_domains,
                "test_types": ["basic_reasoning", "hypothesis_generation", "e2e_integration"]
            },
            "model_results": {}
        }
        
        for model in self.models_to_test:
            logger.info(f"\n{'='*60}")
            logger.info(f"🔍 EVALUATING MODEL: {model}")
            logger.info(f"{'='*60}")
            
            model_start = time.time()
            model_results: Dict[str, Any] = {
                "model_name": model,
                "evaluation_start": datetime.now().isoformat()
            }
            
            # Test 1: Razonamiento básico
            try:
                reasoning_results = self.test_model_basic_reasoning(model)
                model_results["basic_reasoning"] = reasoning_results
                logger.info(f"✅ Basic reasoning complete for {model}: {reasoning_results['average_reasoning_score']:.3f}")
            except Exception as e:
                logger.error(f"❌ Basic reasoning failed for {model}: {e}")
                model_results["basic_reasoning"] = {"error": str(e)}
            
            # Test 2: Generación de hipótesis
            try:
                hypothesis_results = self.test_model_hypothesis_generation(model)
                model_results["hypothesis_generation"] = hypothesis_results
                logger.info(f"✅ Hypothesis generation complete for {model}: {hypothesis_results['average_hypothesis_quality']:.3f}")
            except Exception as e:
                logger.error(f"❌ Hypothesis generation failed for {model}: {e}")
                model_results["hypothesis_generation"] = {"error": str(e)}
            
            # Test 3: E2E Integration
            try:
                e2e_results = self.run_axiom_e2e_with_model(model)
                model_results["e2e_integration"] = e2e_results
                if e2e_results["success"]:
                    logger.info(f"✅ E2E integration complete for {model}: {e2e_results['execution_time']:.1f}s")
                else:
                    logger.error(f"❌ E2E integration failed for {model}")
            except Exception as e:
                logger.error(f"❌ E2E integration exception for {model}: {e}")
                model_results["e2e_integration"] = {"error": str(e)}
            
            model_results["evaluation_time"] = time.time() - model_start
            model_results["evaluation_end"] = datetime.now().isoformat()
            
            results["model_results"][model] = model_results
            
            # Guardar resultados parciales
            self.save_partial_results(results)
        
        results["evaluation_metadata"]["total_time"] = time.time() - evaluation_start
        results["evaluation_metadata"]["end_time"] = datetime.now().isoformat()
        
        # Análisis comparativo
        results["comparative_analysis"] = self.generate_comparative_analysis(results)
        
        # Guardar resultados finales
        self.save_final_results(results)

        # Ejecutar validación extendida de hipótesis (harness) si existe
        try:
            harness_path = Path('hypothesis_tool_validation.py')
            if harness_path.exists():
                logger.info("🧪 Running extended hypothesis validation harness")
                # Import dinámico sin ejecutar main en caso de side effects
                spec = _importlib_util.spec_from_file_location("hypothesis_tool_validation", str(harness_path))
                hv_mod = _importlib_util.module_from_spec(spec)  # type: ignore
                assert spec and spec.loader
                spec.loader.exec_module(hv_mod)  # type: ignore
                if hasattr(hv_mod, 'run_batch_validation'):
                    hv_report = hv_mod.run_batch_validation()
                    results['hypothesis_validation_report'] = {
                        'average_score': hv_report['aggregate'].get('average_score'),
                        'falsification_coverage': hv_report['aggregate'].get('falsification_coverage'),
                        'count': hv_report['aggregate'].get('count'),
                        'report_generated': True
                    }
                    # Re-guardar resultados incluyendo resumen de validación
                    self.save_final_results(results)
                else:
                    logger.warning("Harness module lacks run_batch_validation")
            else:
                logger.info("Harness not present; skipping hypothesis validation integration")
        except Exception as e:
            logger.warning(f"Could not execute hypothesis validation harness: {e}")
        
            # Intentar refinamiento si existe módulo
            refine_path = Path('hypothesis_refinement.py')
            if refine_path.exists():
                logger.info("🛠  Running hypothesis refinement module")
                spec_ref = _importlib_util.spec_from_file_location("hypothesis_refinement", str(refine_path))
                ref_mod = _importlib_util.module_from_spec(spec_ref)  # type: ignore
                assert spec_ref and spec_ref.loader
                spec_ref.loader.exec_module(ref_mod)  # type: ignore
                if hasattr(ref_mod, 'build_refinements'):
                    refinements = ref_mod.build_refinements()
                    results['hypothesis_refinements'] = {
                        'count': refinements.get('count'),
                        'refinement_file': next(iter([k for k in refinements.keys() if k == 'timestamp']), None)
                    }
                    self.save_final_results(results)
        return results
    
    def generate_comparative_analysis(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generar análisis comparativo de todos los modelos"""
        logger.info("📊 Generating comparative analysis")
        
        analysis = {
            "ranking": {},
            "domain_performance": {},
            "recommendations": []
        }
        
        # Ranking por métricas
        model_scores = {}
        for model, model_results in results["model_results"].items():
            scores = []
            
            # Puntaje de razonamiento básico
            if "basic_reasoning" in model_results and "average_reasoning_score" in model_results["basic_reasoning"]:
                scores.append(model_results["basic_reasoning"]["average_reasoning_score"])
            
            # Puntaje de generación de hipótesis
            if "hypothesis_generation" in model_results and "average_hypothesis_quality" in model_results["hypothesis_generation"]:
                scores.append(model_results["hypothesis_generation"]["average_hypothesis_quality"])
            
            # Puntaje E2E (éxito/fallo + tiempo)
            if "e2e_integration" in model_results:
                e2e_score = 1.0 if model_results["e2e_integration"].get("success", False) else 0.0
                # Bonus por tiempo rápido (normalizado)
                if e2e_score > 0 and "execution_time" in model_results["e2e_integration"]:
                    time_bonus = max(0, (600 - model_results["e2e_integration"]["execution_time"]) / 600 * 0.2)
                    e2e_score += time_bonus
                scores.append(e2e_score)
            
            model_scores[model] = sum(scores) / len(scores) if scores else 0.0
        
        # Ordenar modelos por puntuación
        sorted_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
        analysis["ranking"]["overall"] = sorted_models
        analysis["ranking"]["scores"] = model_scores
        
        # Recomendaciones
        if sorted_models:
            best_model = sorted_models[0][0]
            best_score = sorted_models[0][1]
            
            analysis["recommendations"].append(f"Best overall model: {best_model} (score: {best_score:.3f})")
            
            # Recomendaciones específicas
            for model, score in sorted_models:
                if score >= 0.8:
                    analysis["recommendations"].append(f"{model}: Excellent for production use")
                elif score >= 0.6:
                    analysis["recommendations"].append(f"{model}: Good for development/testing")
                else:
                    analysis["recommendations"].append(f"{model}: Needs improvement for scientific tasks")
        
        return analysis
    
    def save_partial_results(self, results: Dict[str, Any]):
        """Guardar resultados parciales"""
        try:
            with open("comprehensive_evaluation_partial.json", "w") as f:
                json.dump(results, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save partial results: {e}")
    
    def save_final_results(self, results: Dict[str, Any]):
        """Guardar resultados finales"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Archivo con timestamp
            with open(f"comprehensive_evaluation_{timestamp}.json", "w") as f:
                json.dump(results, f, indent=2)
            
            # Archivo latest
            with open("comprehensive_evaluation_latest.json", "w") as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"✅ Final results saved to comprehensive_evaluation_{timestamp}.json")
            
        except Exception as e:
            logger.error(f"Could not save final results: {e}")

def main():
    """Función principal"""
    print("🔬 AXIOM META 4 - Comprehensive Scientific Evaluation")
    print("=" * 60)
    print("Testing multiple LLM models for scientific reasoning capability")
    print("Models: falcon3:1b, falcon3:3b, deepseek-r1:1.5b, qwen2.5:1.5b")
    print("=" * 60)
    
    evaluator = ComprehensiveScientificEvaluator()
    
    try:
        results = evaluator.run_comprehensive_evaluation()
        
        print("\n🎉 EVALUATION COMPLETE!")
        print("=" * 60)
        
        # Mostrar resumen
        if "comparative_analysis" in results and "ranking" in results["comparative_analysis"]:
            print("\n📊 RANKING FINAL:")
            for i, (model, score) in enumerate(results["comparative_analysis"]["ranking"]["overall"]):
                print(f"{i+1}. {model}: {score:.3f}")
        
        if "comparative_analysis" in results and "recommendations" in results["comparative_analysis"]:
            print("\n💡 RECOMENDACIONES:")
            for rec in results["comparative_analysis"]["recommendations"]:
                print(f"- {rec}")
        
        print("\n📄 Resultados detallados guardados en: comprehensive_evaluation_latest.json")
        
    except Exception as e:
        logger.error(f"❌ Evaluation failed: {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
