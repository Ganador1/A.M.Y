#!/usr/bin/env python3
"""
Test script for specialized scientific models integration
Tests BioGPT, ClinicalBERT, MatSciBERT, and SciBERT services

Usage:
    python test_specialized_models.py [--model MODEL_NAME] [--verbose]
"""

import asyncio
import sys
import argparse
import traceback
from datetime import datetime
from typing import Dict, Any

# Add the project root to Python path
sys.path.append('.')

from app.services.biogpt_service import BioGPTService
from app.services.clinicalbert_service import ClinicalBERTService
from app.services.matscibert_service import MatSciBERTService
from app.services.scibert_service import SciBERTService


class SpecializedModelsTestSuite:
    """Test suite for specialized scientific models"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {}
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if self.verbose or level in ["ERROR", "SUCCESS"]:
            print(f"[{timestamp}] {level}: {message}")
    
    async def test_biogpt_service(self) -> Dict[str, Any]:
        """Test BioGPT service functionality"""
        self.log("🧬 Testing BioGPT Service...")
        
        test_results = {
            "service_name": "BioGPT",
            "initialization": False,
            "text_generation": False,
            "summarization": False,
            "question_answering": False,
            "errors": []
        }
        
        try:
            # Initialize service
            service = BioGPTService()
            test_results["initialization"] = True
            self.log("✅ BioGPT service initialized successfully")
            
            # Test text generation
            try:
                generation_prompt = "The role of p53 protein in cancer development"
                result = await service.generate_biomedical_text(
                    prompt=generation_prompt,
                    max_length=200,
                    temperature=0.7
                )
                
                if result.get('success'):
                    test_results["text_generation"] = True
                    self.log(f"✅ Text generation successful: {len(result['data']['generated_text'])} characters")
                else:
                    test_results["errors"].append(f"Generation failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                test_results["errors"].append(f"Text generation error: {str(e)}")
                self.log(f"❌ Text generation failed: {e}", "ERROR")
            
            # Test summarization
            try:
                long_text = """
                Cancer is a group of diseases involving abnormal cell growth with the potential to invade 
                or spread to other parts of the body. These contrast with benign tumors, which do not spread. 
                Possible signs and symptoms include a lump, abnormal bleeding, prolonged cough, unexplained 
                weight loss, and a change in bowel movements. While these symptoms may indicate cancer, 
                they may have other causes. The p53 protein plays a crucial role as a tumor suppressor, 
                regulating the cell cycle and preventing cancer formation through various mechanisms including 
                apoptosis induction when DNA damage is irreparable.
                """
                
                result = await service.summarize_biomedical_text(
                    text=long_text,
                    target_ratio=0.4
                )
                
                if result.get('success'):
                    test_results["summarization"] = True
                    self.log(f"✅ Summarization successful: ratio {result['data']['summary_ratio']:.2f}")
                else:
                    test_results["errors"].append(f"Summarization failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                test_results["errors"].append(f"Summarization error: {str(e)}")
                self.log(f"❌ Summarization failed: {e}", "ERROR")
            
            # Test question answering
            try:
                question = "What is the function of p53 protein?"
                context = "p53 is a tumor suppressor protein that regulates cell cycle and prevents cancer."
                
                result = await service.answer_biomedical_question(
                    question=question,
                    context=context
                )
                
                if result.get('success'):
                    test_results["question_answering"] = True
                    self.log(f"✅ Question answering successful")
                else:
                    test_results["errors"].append(f"Q&A failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                test_results["errors"].append(f"Question answering error: {str(e)}")
                self.log(f"❌ Question answering failed: {e}", "ERROR")
                
        except Exception as e:
            test_results["errors"].append(f"Service initialization error: {str(e)}")
            self.log(f"❌ BioGPT service initialization failed: {e}", "ERROR")
        
        return test_results
    
    async def test_clinicalbert_service(self) -> Dict[str, Any]:
        """Test ClinicalBERT service functionality"""
        self.log("🏥 Testing ClinicalBERT Service...")
        
        test_results = {
            "service_name": "ClinicalBERT",
            "initialization": False,
            "entity_extraction": False,
            "classification": False,
            "similarity": False,
            "errors": []
        }
        
        try:
            # Initialize service
            service = ClinicalBERTService()
            test_results["initialization"] = True
            self.log("✅ ClinicalBERT service initialized successfully")
            
            # Test entity extraction
            try:
                clinical_text = """
                Patient presents with chest pain, elevated cardiac enzymes, and ECG changes 
                consistent with acute myocardial infarction. Treatment with aspirin and 
                beta-blockers initiated. Cardiology consultation recommended.
                """
                
                result = await service.extract_clinical_entities(clinical_text)
                
                if result.get('success'):
                    test_results["entity_extraction"] = True
                    entities_count = result['data']['total_entities']
                    self.log(f"✅ Entity extraction successful: {entities_count} entities found")
                else:
                    test_results["errors"].append(f"Entity extraction failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                test_results["errors"].append(f"Entity extraction error: {str(e)}")
                self.log(f"❌ Entity extraction failed: {e}", "ERROR")
            
            # Test classification
            try:
                result = await service.classify_clinical_text(
                    clinical_text="Patient with acute chest pain and cardiac symptoms",
                    classification_type="specialty"
                )
                
                if result.get('success'):
                    test_results["classification"] = True
                    predicted_class = result['data']['predicted_class']
                    confidence = result['data']['confidence_score']
                    self.log(f"✅ Classification successful: {predicted_class} (confidence: {confidence:.2f})")
                else:
                    test_results["errors"].append(f"Classification failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                test_results["errors"].append(f"Classification error: {str(e)}")
                self.log(f"❌ Classification failed: {e}", "ERROR")
            
            # Test similarity analysis
            try:
                text1 = "Patient with cardiac arrest and chest pain"
                text2 = "Heart attack symptoms including chest discomfort"
                
                result = await service.analyze_clinical_similarity(text1, text2)
                
                if result.get('success'):
                    test_results["similarity"] = True
                    similarity = result['data']['similarity_score']
                    self.log(f"✅ Similarity analysis successful: {similarity:.3f}")
                else:
                    test_results["errors"].append(f"Similarity analysis failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                test_results["errors"].append(f"Similarity analysis error: {str(e)}")
                self.log(f"❌ Similarity analysis failed: {e}", "ERROR")
                
        except Exception as e:
            test_results["errors"].append(f"Service initialization error: {str(e)}")
            self.log(f"❌ ClinicalBERT service initialization failed: {e}", "ERROR")
        
        return test_results
    
    async def test_matscibert_service(self) -> Dict[str, Any]:
        """Test MatSciBERT service functionality"""
        self.log("🔬 Testing MatSciBERT Service...")
        
        test_results = {
            "service_name": "MatSciBERT",
            "initialization": False,
            "materials_analysis": False,
            "similarity": False,
            "property_prediction": False,
            "errors": []
        }
        
        try:
            # Initialize service
            service = MatSciBERTService()
            test_results["initialization"] = True
            self.log("✅ MatSciBERT service initialized successfully")
            
            # Test materials analysis
            try:
                materials_text = """
                We synthesized graphene oxide nanocomposites using chemical vapor deposition 
                at 1000°C. The material exhibits high electrical conductivity and mechanical 
                strength, making it suitable for energy storage applications. XRD analysis 
                confirmed the crystalline structure.
                """
                
                result = await service.analyze_materials_text(materials_text)
                
                if result.get('success'):
                    test_results["materials_analysis"] = True
                    entities_count = len(result['data']['entities'])
                    context = result['data']['research_context']
                    self.log(f"✅ Materials analysis successful: {entities_count} entities, context: {context}")
                else:
                    test_results["errors"].append(f"Materials analysis failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                test_results["errors"].append(f"Materials analysis error: {str(e)}")
                self.log(f"❌ Materials analysis failed: {e}", "ERROR")
            
            # Test similarity calculation
            try:
                text1 = "Graphene-based nanocomposites with high conductivity"
                text2 = "Carbon nanotube materials for electrical applications"
                
                result = await service.calculate_materials_similarity(text1, text2)
                
                if result.get('success'):
                    test_results["similarity"] = True
                    similarity = result['data']['similarity_score']
                    self.log(f"✅ Materials similarity successful: {similarity:.3f}")
                else:
                    test_results["errors"].append(f"Materials similarity failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                test_results["errors"].append(f"Materials similarity error: {str(e)}")
                self.log(f"❌ Materials similarity failed: {e}", "ERROR")
            
            # Test property prediction
            try:
                description = "Silicon carbide ceramic material with high hardness"
                
                result = await service.predict_material_properties(description)
                
                if result.get('success'):
                    test_results["property_prediction"] = True
                    properties_count = len(result['data']['predicted_properties'])
                    self.log(f"✅ Property prediction successful: {properties_count} properties predicted")
                else:
                    test_results["errors"].append(f"Property prediction failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                test_results["errors"].append(f"Property prediction error: {str(e)}")
                self.log(f"❌ Property prediction failed: {e}", "ERROR")
                
        except Exception as e:
            test_results["errors"].append(f"Service initialization error: {str(e)}")
            self.log(f"❌ MatSciBERT service initialization failed: {e}", "ERROR")
        
        return test_results
    
    async def test_scibert_service(self) -> Dict[str, Any]:
        """Test SciBERT service functionality"""
        self.log("📚 Testing SciBERT Service...")
        
        test_results = {
            "service_name": "SciBERT",
            "initialization": False,
            "scientific_analysis": False,
            "research_similarity": False,
            "paper_classification": False,
            "errors": []
        }
        
        try:
            # Initialize service
            service = SciBERTService()
            test_results["initialization"] = True
            self.log("✅ SciBERT service initialized successfully")
            
            # Test scientific text analysis
            try:
                scientific_text = """
                We present a novel machine learning algorithm for protein structure prediction 
                based on deep neural networks. The method achieved 95% accuracy on benchmark 
                datasets and outperformed existing approaches. Experimental validation confirms 
                the theoretical predictions.
                """
                
                result = await service.analyze_scientific_text(scientific_text)
                
                if result.get('success'):
                    test_results["scientific_analysis"] = True
                    domain = result['data']['research_domain']
                    complexity = result['data']['complexity_score']
                    self.log(f"✅ Scientific analysis successful: domain={domain}, complexity={complexity}")
                else:
                    test_results["errors"].append(f"Scientific analysis failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                test_results["errors"].append(f"Scientific analysis error: {str(e)}")
                self.log(f"❌ Scientific analysis failed: {e}", "ERROR")
            
            # Test research similarity
            try:
                text1 = "Deep learning models for biological sequence analysis"
                text2 = "Machine learning approaches to genomic data processing"
                
                result = await service.calculate_research_similarity(text1, text2)
                
                if result.get('success'):
                    test_results["research_similarity"] = True
                    similarity = result['data']['similarity_score']
                    potential = result['data']['interdisciplinary_potential']
                    self.log(f"✅ Research similarity successful: {similarity:.3f}, potential={potential}")
                else:
                    test_results["errors"].append(f"Research similarity failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                test_results["errors"].append(f"Research similarity error: {str(e)}")
                self.log(f"❌ Research similarity failed: {e}", "ERROR")
            
            # Test paper classification
            try:
                abstract = """
                This study presents a comprehensive analysis of quantum computing algorithms 
                for optimization problems. We demonstrate significant performance improvements 
                over classical methods and provide theoretical foundations for the approach.
                """
                title = "Quantum Algorithms for Optimization: Theory and Applications"
                
                result = await service.classify_research_paper(abstract, title)
                
                if result.get('success'):
                    test_results["paper_classification"] = True
                    domain = result['data']['primary_domain']
                    paper_type = result['data']['paper_type']
                    self.log(f"✅ Paper classification successful: {domain}, type={paper_type}")
                else:
                    test_results["errors"].append(f"Paper classification failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                test_results["errors"].append(f"Paper classification error: {str(e)}")
                self.log(f"❌ Paper classification failed: {e}", "ERROR")
                
        except Exception as e:
            test_results["errors"].append(f"Service initialization error: {str(e)}")
            self.log(f"❌ SciBERT service initialization failed: {e}", "ERROR")
        
        return test_results
    
    def print_test_summary(self, results: Dict[str, Any]):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🚀 SPECIALIZED SCIENTIFIC MODELS - TEST RESULTS SUMMARY")
        print("="*80)
        
        total_tests = 0
        total_passed = 0
        
        for service_name, service_results in results.items():
            print(f"\n📋 {service_results['service_name']} Service:")
            print("-" * 50)
            
            # Count tests for this service
            service_tests = [k for k in service_results.keys() if k not in ['service_name', 'errors']]
            service_passed = sum(1 for k in service_tests if service_results[k])
            
            total_tests += len(service_tests)
            total_passed += service_passed
            
            # Print individual test results
            for test_name in service_tests:
                status = "✅ PASS" if service_results[test_name] else "❌ FAIL"
                print(f"  {test_name:<25} {status}")
            
            # Print errors if any
            if service_results['errors']:
                print(f"\n  🔍 Errors encountered:")
                for error in service_results['errors'][:3]:  # Show first 3 errors
                    print(f"    • {error}")
                if len(service_results['errors']) > 3:
                    print(f"    ... and {len(service_results['errors']) - 3} more errors")
            
            # Service summary
            success_rate = (service_passed / len(service_tests)) * 100 if service_tests else 0
            print(f"\n  📊 Service Summary: {service_passed}/{len(service_tests)} tests passed ({success_rate:.1f}%)")
        
        # Overall summary
        print("\n" + "="*80)
        overall_success_rate = (total_passed / total_tests) * 100 if total_tests else 0
        print(f"🎯 OVERALL RESULTS: {total_passed}/{total_tests} tests passed ({overall_success_rate:.1f}%)")
        
        if overall_success_rate >= 80:
            print("🎉 EXCELLENT: Specialized models integration highly successful!")
        elif overall_success_rate >= 60:
            print("✅ GOOD: Most specialized models working properly")
        elif overall_success_rate >= 40:
            print("⚠️  PARTIAL: Some specialized models need attention")
        else:
            print("❌ CRITICAL: Major issues with specialized models integration")
        
        print("="*80)
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all specialized model tests"""
        self.log("🔬 Starting Specialized Scientific Models Test Suite...")
        
        results = {}
        
        # Test each service
        test_functions = [
            ("biogpt", self.test_biogpt_service),
            ("clinicalbert", self.test_clinicalbert_service),
            ("matscibert", self.test_matscibert_service),
            ("scibert", self.test_scibert_service)
        ]
        
        for service_name, test_func in test_functions:
            try:
                self.log(f"Testing {service_name}...")
                results[service_name] = await test_func()
            except Exception as e:
                self.log(f"Critical error testing {service_name}: {e}", "ERROR")
                results[service_name] = {
                    "service_name": service_name,
                    "initialization": False,
                    "errors": [f"Critical test failure: {str(e)}"]
                }
        
        return results
    
    async def run_single_model_test(self, model_name: str) -> Dict[str, Any]:
        """Run test for a single model"""
        model_name = model_name.lower()
        
        test_functions = {
            "biogpt": self.test_biogpt_service,
            "clinicalbert": self.test_clinicalbert_service,
            "matscibert": self.test_matscibert_service,
            "scibert": self.test_scibert_service
        }
        
        if model_name not in test_functions:
            raise ValueError(f"Unknown model: {model_name}. Available: {list(test_functions.keys())}")
        
        self.log(f"🔬 Testing {model_name} service...")
        result = await test_functions[model_name]()
        
        return {model_name: result}


async def main():
    """Main test execution"""
    parser = argparse.ArgumentParser(description="Test specialized scientific models")
    parser.add_argument("--model", choices=["biogpt", "clinicalbert", "matscibert", "scibert"], 
                       help="Test specific model only")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Initialize test suite
    test_suite = SpecializedModelsTestSuite(verbose=args.verbose)
    
    try:
        # Run tests
        if args.model:
            results = await test_suite.run_single_model_test(args.model)
        else:
            results = await test_suite.run_all_tests()
        
        # Print summary
        test_suite.print_test_summary(results)
        
        # Set exit code based on results
        total_tests = sum(len([k for k in r.keys() if k not in ['service_name', 'errors']]) for r in results.values())
        total_passed = sum(sum(1 for k, v in r.items() if k not in ['service_name', 'errors'] and v) for r in results.values())
        
        success_rate = (total_passed / total_tests) * 100 if total_tests else 0
        
        if success_rate >= 80:
            sys.exit(0)  # Success
        elif success_rate >= 50:
            sys.exit(1)  # Partial success
        else:
            sys.exit(2)  # Failure
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: Test suite execution failed: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())
