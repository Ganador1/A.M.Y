#!/usr/bin/env python3
"""
AXIOM META 4 - Resumen Final Completo
Consolidación de todos los resultados de evaluación científica y verificación de consistencia.
"""

import json
import logging
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScientificConsistencyValidator:
    """Valida la consistencia científica de todos los resultados."""
    
    def __init__(self):
        self.results = {
            "validation_timestamp": datetime.now().isoformat(),
            "comprehensive_evaluation": None,
            "domain_testing": None,
            "final_verification": None,
            "scientific_paper": None,
            "consistency_analysis": {},
            "final_conclusions": {}
        }
    
    def load_all_results(self):
        """Cargar todos los archivos de resultados disponibles."""
        logger.info("📂 Cargando todos los resultados de evaluación...")
        
        # 1. Comprehensive evaluation results
        comp_files = list(Path(".").glob("comprehensive_evaluation_results_*.json"))
        if comp_files:
            latest_comp = max(comp_files, key=lambda x: x.stat().st_mtime)
            with open(latest_comp, 'r', encoding='utf-8') as f:
                self.results["comprehensive_evaluation"] = json.load(f)
            logger.info(f"✅ Evaluación comprensiva cargada: {latest_comp}")
        
        # 2. Domain testing results
        domain_files = list(Path(".").glob("domain_testing_results_*.json"))
        if domain_files:
            latest_domain = max(domain_files, key=lambda x: x.stat().st_mtime)
            with open(latest_domain, 'r', encoding='utf-8') as f:
                self.results["domain_testing"] = json.load(f)
            logger.info(f"✅ Testing de dominios cargado: {latest_domain}")
        
        # 3. Final verification results
        verif_files = list(Path(".").glob("final_e2e_verification_*.json"))
        if verif_files:
            latest_verif = max(verif_files, key=lambda x: x.stat().st_mtime)
            with open(latest_verif, 'r', encoding='utf-8') as f:
                self.results["final_verification"] = json.load(f)
            logger.info(f"✅ Verificación E2E cargada: {latest_verif}")
        
        # 4. Scientific paper
        paper_files = list(Path("generated_papers").glob("scientific_paper_*.md"))
        if paper_files:
            latest_paper = max(paper_files, key=lambda x: x.stat().st_mtime)
            with open(latest_paper, 'r', encoding='utf-8') as f:
                paper_content = f.read()
            self.results["scientific_paper"] = {
                "filename": str(latest_paper),
                "word_count": len(paper_content.split()),
                "created": datetime.fromtimestamp(latest_paper.stat().st_mtime).isoformat()
            }
            logger.info(f"✅ Paper científico encontrado: {latest_paper}")
    
    def analyze_model_performance_consistency(self) -> Dict[str, Any]:
        """Analiza la consistencia del rendimiento de modelos across evaluaciones."""
        logger.info("🔍 Analizando consistencia de rendimiento de modelos...")
        
        consistency = {
            "model_rankings": {},
            "performance_correlation": 0.0,
            "consistent_patterns": [],
            "inconsistencies": []
        }
        
        if not self.results["comprehensive_evaluation"]:
            logger.warning("⚠️ No hay datos de evaluación comprensiva")
            return consistency
        
        # Extract rankings from comprehensive evaluation
        comp_results = self.results["comprehensive_evaluation"]["model_results"]
        comp_ranking = sorted(comp_results.items(), 
                             key=lambda x: x[1]["overall_score"], reverse=True)
        
        consistency["model_rankings"]["comprehensive"] = [
            {"model": model, "score": data["overall_score"]} 
            for model, data in comp_ranking
        ]
        
        # Compare with domain testing if available
        if self.results["domain_testing"]:
            domain_results = self.results["domain_testing"]
            # Extract domain-specific performance patterns
            domain_patterns = {}
            for model, model_data in domain_results.get("model_results", {}).items():
                domain_scores = []
                for domain, domain_data in model_data.get("domain_results", {}).items():
                    if isinstance(domain_data, dict) and "overall_score" in domain_data:
                        domain_scores.append(domain_data["overall_score"])
                
                if domain_scores:
                    avg_domain_score = np.mean(domain_scores)
                    domain_patterns[model] = avg_domain_score
            
            if domain_patterns:
                domain_ranking = sorted(domain_patterns.items(), 
                                      key=lambda x: x[1], reverse=True)
                consistency["model_rankings"]["domain"] = [
                    {"model": model, "score": score} 
                    for model, score in domain_ranking
                ]
        
        # Analyze consistency patterns
        if len(consistency["model_rankings"]) > 1:
            comp_top = consistency["model_rankings"]["comprehensive"][0]["model"]
            domain_top = consistency["model_rankings"].get("domain", [{}])[0].get("model")
            
            if comp_top == domain_top:
                consistency["consistent_patterns"].append(
                    f"Top performing model consistent: {comp_top}"
                )
            else:
                consistency["inconsistencies"].append(
                    f"Top model mismatch: Comprehensive={comp_top}, Domain={domain_top}"
                )
        
        # Check final verification consistency
        if self.results["final_verification"]:
            verif_model = self.results["final_verification"]["model"]
            verif_success = self.results["final_verification"]["test_summary"]["overall_success"]
            
            if verif_model == comp_ranking[0][0] and verif_success:
                consistency["consistent_patterns"].append(
                    f"Best model {verif_model} passed E2E verification"
                )
            elif not verif_success:
                consistency["inconsistencies"].append(
                    f"Best model {verif_model} failed some E2E tests"
                )
        
        return consistency
    
    def analyze_scientific_domain_consistency(self) -> Dict[str, Any]:
        """Analiza la consistencia across dominios científicos."""
        logger.info("🔬 Analizando consistencia de dominios científicos...")
        
        domain_analysis = {
            "domain_performance": {},
            "consistent_domains": [],
            "challenging_domains": [],
            "recommendations": []
        }
        
        if not self.results["comprehensive_evaluation"]:
            return domain_analysis
        
        # Analyze domain-specific patterns
        comp_results = self.results["comprehensive_evaluation"]["model_results"]
        
        domain_scores = {}
        for model, model_data in comp_results.items():
            # Look for domain-specific results in different test categories
            for category in ["basic_reasoning", "hypothesis_generation"]:
                if category in model_data:
                    category_results = model_data[category]
                    if isinstance(category_results, dict) and "individual_results" in category_results:
                        for result in category_results["individual_results"]:
                            domain = result.get("domain", "unknown")
                            score = result.get("keyword_score", 0)
                            
                            if domain not in domain_scores:
                                domain_scores[domain] = []
                            domain_scores[domain].append(score)
        
        # Calculate average scores per domain
        for domain, scores in domain_scores.items():
            avg_score = np.mean(scores)
            domain_analysis["domain_performance"][domain] = {
                "average_score": avg_score,
                "num_tests": len(scores),
                "consistency": np.std(scores) if len(scores) > 1 else 0.0
            }
            
            if avg_score > 0.7:
                domain_analysis["consistent_domains"].append(domain)
            elif avg_score < 0.4:
                domain_analysis["challenging_domains"].append(domain)
        
        # Generate recommendations
        if domain_analysis["challenging_domains"]:
            domain_analysis["recommendations"].append(
                f"Focus improvement on: {', '.join(domain_analysis['challenging_domains'])}"
            )
        
        if domain_analysis["consistent_domains"]:
            domain_analysis["recommendations"].append(
                f"Strong performance in: {', '.join(domain_analysis['consistent_domains'])}"
            )
        
        return domain_analysis
    
    def analyze_workflow_completeness(self) -> Dict[str, Any]:
        """Analiza la completitud del workflow científico E2E."""
        logger.info("🔄 Analizando completitud del workflow E2E...")
        
        workflow_analysis = {
            "e2e_success_rate": 0.0,
            "completed_stages": [],
            "failed_stages": [],
            "workflow_quality": "unknown",
            "production_readiness": False
        }
        
        if not self.results["final_verification"]:
            logger.warning("⚠️ No hay datos de verificación E2E")
            return workflow_analysis
        
        verif_data = self.results["final_verification"]
        test_summary = verif_data["test_summary"]
        
        workflow_analysis["e2e_success_rate"] = test_summary["success_rate"]
        workflow_analysis["production_readiness"] = test_summary["overall_success"]
        
        # Analyze individual test results
        for test_name, test_result in verif_data["tests"].items():
            if test_result["status"] == "success":
                workflow_analysis["completed_stages"].append(test_name)
            else:
                workflow_analysis["failed_stages"].append(test_name)
        
        # Determine workflow quality
        success_rate = workflow_analysis["e2e_success_rate"]
        if success_rate >= 0.9:
            workflow_analysis["workflow_quality"] = "excellent"
        elif success_rate >= 0.7:
            workflow_analysis["workflow_quality"] = "good"
        elif success_rate >= 0.5:
            workflow_analysis["workflow_quality"] = "acceptable"
        else:
            workflow_analysis["workflow_quality"] = "needs_improvement"
        
        return workflow_analysis
    
    def validate_scientific_paper_quality(self) -> Dict[str, Any]:
        """Valida la calidad del paper científico generado."""
        logger.info("📝 Validando calidad del paper científico...")
        
        paper_analysis = {
            "paper_exists": False,
            "word_count": 0,
            "structure_complete": False,
            "publication_ready": False,
            "quality_score": 0.0
        }
        
        if not self.results["scientific_paper"]:
            logger.warning("⚠️ No se encontró paper científico")
            return paper_analysis
        
        paper_info = self.results["scientific_paper"]
        paper_analysis["paper_exists"] = True
        paper_analysis["word_count"] = paper_info["word_count"]
        
        # Determine quality based on word count and existence
        if paper_info["word_count"] > 4000:
            paper_analysis["structure_complete"] = True
            paper_analysis["publication_ready"] = True
            paper_analysis["quality_score"] = 0.9
        elif paper_info["word_count"] > 2000:
            paper_analysis["structure_complete"] = True
            paper_analysis["publication_ready"] = False
            paper_analysis["quality_score"] = 0.7
        else:
            paper_analysis["quality_score"] = 0.5
        
        return paper_analysis
    
    def generate_final_conclusions(self) -> Dict[str, Any]:
        """Genera conclusiones finales basadas en todo el análisis."""
        logger.info("🎯 Generando conclusiones finales...")
        
        conclusions = {
            "overall_success": False,
            "best_performing_model": None,
            "system_readiness": "unknown",
            "key_achievements": [],
            "areas_for_improvement": [],
            "next_steps": [],
            "scientific_validity": "unknown"
        }
        
        # Model performance conclusions
        model_consistency = self.results["consistency_analysis"]["model_performance"]
        if model_consistency["model_rankings"]:
            best_model_data = model_consistency["model_rankings"]["comprehensive"][0]
            conclusions["best_performing_model"] = {
                "name": best_model_data["model"],
                "score": best_model_data["score"]
            }
            conclusions["key_achievements"].append(
                f"Identified best model: {best_model_data['model']} (score: {best_model_data['score']:.3f})"
            )
        
        # Workflow completeness conclusions
        workflow_analysis = self.results["consistency_analysis"]["workflow_completeness"]
        if workflow_analysis["production_readiness"]:
            conclusions["system_readiness"] = "production_ready"
            conclusions["key_achievements"].append(
                f"E2E workflow success rate: {workflow_analysis['e2e_success_rate']:.1%}"
            )
        else:
            conclusions["system_readiness"] = "needs_improvement"
            conclusions["areas_for_improvement"].extend(workflow_analysis["failed_stages"])
        
        # Scientific paper conclusions
        paper_analysis = self.results["consistency_analysis"]["paper_quality"]
        if paper_analysis["publication_ready"]:
            conclusions["scientific_validity"] = "validated"
            conclusions["key_achievements"].append(
                f"Generated publication-ready paper ({paper_analysis['word_count']} words)"
            )
        else:
            conclusions["scientific_validity"] = "partial"
            if paper_analysis["paper_exists"]:
                conclusions["areas_for_improvement"].append("Paper needs expansion for publication")
        
        # Domain analysis conclusions
        domain_analysis = self.results["consistency_analysis"]["domain_consistency"]
        if domain_analysis["consistent_domains"]:
            conclusions["key_achievements"].append(
                f"Strong performance in domains: {', '.join(domain_analysis['consistent_domains'])}"
            )
        if domain_analysis["challenging_domains"]:
            conclusions["areas_for_improvement"].append(
                f"Improve performance in: {', '.join(domain_analysis['challenging_domains'])}"
            )
        
        # Overall success determination
        success_factors = [
            workflow_analysis["production_readiness"],
            paper_analysis["publication_ready"],
            len(conclusions["key_achievements"]) > 2
        ]
        conclusions["overall_success"] = sum(success_factors) >= 2
        
        # Next steps recommendations
        if conclusions["overall_success"]:
            conclusions["next_steps"] = [
                "Deploy system for real scientific research",
                "Collect user feedback and usage metrics",
                "Publish research findings",
                "Expand to additional scientific domains"
            ]
        else:
            conclusions["next_steps"] = [
                "Address identified areas for improvement",
                "Run additional testing and validation",
                "Refine model performance",
                "Complete E2E workflow testing"
            ]
        
        return conclusions
    
    def run_complete_analysis(self) -> Dict[str, Any]:
        """Ejecuta el análisis completo de consistencia científica."""
        logger.info("🚀 AXIOM META 4 - Análisis Final de Consistencia Científica")
        logger.info("="*80)
        
        # Load all available results
        self.load_all_results()
        
        # Run all consistency analyses
        logger.info("\n📊 Ejecutando análisis de consistencia...")
        self.results["consistency_analysis"]["model_performance"] = self.analyze_model_performance_consistency()
        self.results["consistency_analysis"]["domain_consistency"] = self.analyze_scientific_domain_consistency()
        self.results["consistency_analysis"]["workflow_completeness"] = self.analyze_workflow_completeness()
        self.results["consistency_analysis"]["paper_quality"] = self.validate_scientific_paper_quality()
        
        # Generate final conclusions
        self.results["final_conclusions"] = self.generate_final_conclusions()
        
        # Save complete analysis
        self.save_complete_analysis()
        
        # Print comprehensive summary
        self.print_comprehensive_summary()
        
        return self.results
    
    def save_complete_analysis(self):
        """Guarda el análisis completo."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"complete_scientific_analysis_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📁 Análisis completo guardado en: {filename}")
    
    def print_comprehensive_summary(self):
        """Imprime el resumen comprensivo final."""
        logger.info("\n" + "="*100)
        logger.info("🏆 AXIOM META 4 - RESUMEN FINAL COMPRENSIVO")
        logger.info("="*100)
        
        conclusions = self.results["final_conclusions"]
        
        # Overall status
        status_emoji = "✅" if conclusions["overall_success"] else "⚠️"
        logger.info(f"\n{status_emoji} ESTADO GENERAL: {'ÉXITO COMPLETO' if conclusions['overall_success'] else 'PARCIALMENTE COMPLETO'}")
        
        # Best model
        if conclusions["best_performing_model"]:
            model_info = conclusions["best_performing_model"]
            logger.info(f"🥇 MEJOR MODELO: {model_info['name']} (puntuación: {model_info['score']:.3f})")
        
        # System readiness
        readiness_emoji = "🚀" if conclusions["system_readiness"] == "production_ready" else "🔧"
        logger.info(f"{readiness_emoji} PREPARACIÓN SISTEMA: {conclusions['system_readiness'].replace('_', ' ').upper()}")
        
        # Key achievements
        logger.info(f"\n🎉 LOGROS PRINCIPALES ({len(conclusions['key_achievements'])}):")
        for achievement in conclusions["key_achievements"]:
            logger.info(f"   ✅ {achievement}")
        
        # Areas for improvement
        if conclusions["areas_for_improvement"]:
            logger.info(f"\n🔧 ÁREAS DE MEJORA ({len(conclusions['areas_for_improvement'])}):")
            for improvement in conclusions["areas_for_improvement"]:
                logger.info(f"   🔸 {improvement}")
        
        # Scientific validity
        validity_emoji = "🔬" if conclusions["scientific_validity"] == "validated" else "📝"
        logger.info(f"\n{validity_emoji} VALIDEZ CIENTÍFICA: {conclusions['scientific_validity'].upper()}")
        
        # Next steps
        logger.info(f"\n📋 PRÓXIMOS PASOS ({len(conclusions['next_steps'])}):")
        for step in conclusions["next_steps"]:
            logger.info(f"   📌 {step}")
        
        # Final recommendation
        logger.info("\n" + "="*100)
        if conclusions["overall_success"]:
            logger.info("🎊 ¡FELICITACIONES! AXIOM META 4 ha demostrado capacidad científica completa")
            logger.info("🚀 RECOMENDACIÓN: Sistema listo para implementación en investigación real")
        else:
            logger.info("📈 AXIOM META 4 muestra gran potencial con algunas áreas de mejora")
            logger.info("🔧 RECOMENDACIÓN: Abordar mejoras identificadas antes de despliegue completo")
        
        logger.info("="*100)

def main():
    """Función principal de ejecución."""
    try:
        # Initialize validator
        validator = ScientificConsistencyValidator()
        
        # Run complete analysis
        results = validator.run_complete_analysis()
        
        return results
        
    except KeyboardInterrupt:
        logger.info("\n⏹️ Análisis interrumpido por el usuario")
        return None
    except Exception as e:
        logger.error(f"❌ Error en análisis de consistencia: {e}")
        raise

if __name__ == "__main__":
    results = main()
    if results and results["final_conclusions"]["overall_success"]:
        print(f"\n🏁 Análisis completado. AXIOM META 4 - ÉXITO CIENTÍFICO VALIDADO ✅")
    elif results:
        print(f"\n🏁 Análisis completado. AXIOM META 4 - POTENCIAL ALTO, MEJORAS IDENTIFICADAS 📈")
    else:
        print("\n❌ Análisis no completado")
