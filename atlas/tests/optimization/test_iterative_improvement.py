#!/usr/bin/env python3
"""
Test script for Iterative Improvement Pipeline
Validates continuous learning and optimization capabilities

Usage:
    python test_iterative_improvement.py [--verbose]
"""

import asyncio
import sys
import argparse
import traceback
from datetime import datetime
from typing import Dict, Any

# Add project root to path
sys.path.append('.')

from app.services.iterative_improvement_service import (
    IterativeImprovementPipeline,
    AnalysisType, 
    FeedbackType
)


class IterativeImprovementTestSuite:
    """Test suite for iterative improvement pipeline"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.service = None
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if self.verbose or level in ["ERROR", "SUCCESS"]:
            print(f"[{timestamp}] {level}: {message}")
    
    async def setup_service(self) -> bool:
        """Initialize the improvement pipeline service"""
        try:
            self.log("🔧 Initializing Iterative Improvement Pipeline...")
            self.service = IterativeImprovementPipeline()
            self.log("✅ Service initialized successfully")
            return True
        except Exception as e:
            self.log(f"❌ Failed to initialize service: {e}", "ERROR")
            return False
    
    async def test_feedback_recording(self) -> Dict[str, Any]:
        """Test feedback recording functionality"""
        self.log("📊 Testing feedback recording...")
        
        test_results = {
            "test_name": "feedback_recording",
            "basic_feedback": False,
            "multiple_feedback_types": False,
            "parameter_tracking": False,
            "errors": []
        }
        
        try:
            # Test basic feedback recording
            feedback_id = await self.service.record_feedback(
                analysis_type=AnalysisType.LITERATURE_SEARCH,
                feedback_type=FeedbackType.ACCURACY_SCORE,
                value=0.85,
                parameters={"query_terms": "machine learning", "max_results": 100},
                context={"domain": "computer_science"},
                source="test_suite"
            )
            
            if feedback_id:
                test_results["basic_feedback"] = True
                self.log(f"✅ Basic feedback recorded: {feedback_id}")
            
            # Test multiple feedback types
            feedback_types_tested = [
                (FeedbackType.COMPLETION_TIME, 2.5),
                (FeedbackType.COHERENCE_SCORE, 0.9),
                (FeedbackType.RELEVANCE_SCORE, 0.8),
                (FeedbackType.SCIENTIFIC_VALIDITY, 0.75)
            ]
            
            for fb_type, value in feedback_types_tested:
                await self.service.record_feedback(
                    analysis_type=AnalysisType.EVIDENCE_SYNTHESIS,
                    feedback_type=fb_type,
                    value=value,
                    parameters={"synthesis_method": "weighted", "sources": 5},
                    source="test_suite"
                )
            
            test_results["multiple_feedback_types"] = True
            self.log("✅ Multiple feedback types recorded")
            
            # Test parameter tracking with varying values
            for i in range(10):
                accuracy = 0.6 + (i * 0.04)  # 0.6 to 0.96
                await self.service.record_feedback(
                    analysis_type=AnalysisType.MODEL_PREDICTION,
                    feedback_type=FeedbackType.ACCURACY_SCORE,
                    value=accuracy,
                    parameters={
                        "model_complexity": i + 1,
                        "training_data_size": 1000 + (i * 100),
                        "regularization": 0.01 * (i + 1)
                    },
                    source="test_suite"
                )
            
            test_results["parameter_tracking"] = True
            self.log("✅ Parameter tracking test completed")
            
        except Exception as e:
            test_results["errors"].append(f"Feedback recording error: {str(e)}")
            self.log(f"❌ Feedback recording failed: {e}", "ERROR")
        
        return test_results
    
    async def test_metrics_calculation(self) -> Dict[str, Any]:
        """Test performance metrics calculation"""
        self.log("📈 Testing metrics calculation...")
        
        test_results = {
            "test_name": "metrics_calculation",
            "basic_metrics": False,
            "trend_calculation": False,
            "multiple_analysis_types": False,
            "errors": []
        }
        
        try:
            # Get metrics for specific analysis type
            metrics = await self.service.get_performance_metrics(AnalysisType.MODEL_PREDICTION)
            
            if metrics and "data" in metrics:
                test_results["basic_metrics"] = True
                self.log(f"✅ Basic metrics calculated: {metrics['data'].get('metrics', {}).get('total_analyses', 0)} analyses")
            
            # Check trend calculation
            if metrics.get("data", {}).get("metrics", {}).get("improvement_trend") is not None:
                test_results["trend_calculation"] = True
                trend = metrics["data"]["metrics"]["improvement_trend"]
                self.log(f"✅ Improvement trend calculated: {trend:.3f}")
            
            # Get metrics for all analysis types
            all_metrics = await self.service.get_performance_metrics()
            
            if all_metrics and "all_metrics" in all_metrics:
                test_results["multiple_analysis_types"] = True
                types_count = len(all_metrics["all_metrics"])
                self.log(f"✅ All metrics retrieved: {types_count} analysis types")
            
        except Exception as e:
            test_results["errors"].append(f"Metrics calculation error: {str(e)}")
            self.log(f"❌ Metrics calculation failed: {e}", "ERROR")
        
        return test_results
    
    async def test_optimization_recommendations(self) -> Dict[str, Any]:
        """Test optimization recommendation generation"""
        self.log("🎯 Testing optimization recommendations...")
        
        test_results = {
            "test_name": "optimization_recommendations",
            "recommendation_generation": False,
            "parameter_analysis": False,
            "confidence_scoring": False,
            "errors": []
        }
        
        try:
            # Add more feedback data to enable recommendations
            high_performance_params = [
                {"complexity": 8, "data_size": 1500, "reg": 0.05},
                {"complexity": 9, "data_size": 1600, "reg": 0.06},
                {"complexity": 10, "data_size": 1700, "reg": 0.07}
            ]
            
            low_performance_params = [
                {"complexity": 2, "data_size": 500, "reg": 0.01},
                {"complexity": 3, "data_size": 600, "reg": 0.02},
                {"complexity": 4, "data_size": 700, "reg": 0.03}
            ]
            
            # Record high performance feedback
            for params in high_performance_params:
                await self.service.record_feedback(
                    analysis_type=AnalysisType.HYPOTHESIS_GENERATION,
                    feedback_type=FeedbackType.ACCURACY_SCORE,
                    value=0.9,
                    parameters=params,
                    source="test_optimization"
                )
            
            # Record low performance feedback
            for params in low_performance_params:
                await self.service.record_feedback(
                    analysis_type=AnalysisType.HYPOTHESIS_GENERATION,
                    feedback_type=FeedbackType.ACCURACY_SCORE,
                    value=0.5,
                    parameters=params,
                    source="test_optimization"
                )
            
            # Get optimization recommendations
            recommendations = await self.service.get_optimization_recommendations(
                AnalysisType.HYPOTHESIS_GENERATION
            )
            
            if recommendations and "recommendations" in recommendations:
                rec_list = recommendations["recommendations"]
                if rec_list:
                    test_results["recommendation_generation"] = True
                    self.log(f"✅ Generated {len(rec_list)} recommendations")
                    
                    # Check parameter analysis
                    if any("complexity" in rec["parameter"] for rec in rec_list):
                        test_results["parameter_analysis"] = True
                        self.log("✅ Parameter analysis successful")
                    
                    # Check confidence scoring
                    if all("confidence" in rec for rec in rec_list):
                        test_results["confidence_scoring"] = True
                        avg_confidence = sum(rec["confidence"] for rec in rec_list) / len(rec_list)
                        self.log(f"✅ Confidence scoring: avg={avg_confidence:.3f}")
            
        except Exception as e:
            test_results["errors"].append(f"Optimization recommendations error: {str(e)}")
            self.log(f"❌ Optimization recommendations failed: {e}", "ERROR")
        
        return test_results
    
    async def test_improvement_simulation(self) -> Dict[str, Any]:
        """Test improvement impact simulation"""
        self.log("🧪 Testing improvement simulation...")
        
        test_results = {
            "test_name": "improvement_simulation",
            "basic_simulation": False,
            "impact_estimation": False,
            "confidence_calculation": False,
            "errors": []
        }
        
        try:
            # Simulate parameter changes
            parameter_changes = {
                "complexity": 8.5,
                "data_size": 1550,
                "reg": 0.055
            }
            
            simulation = await self.service.simulate_improvement_impact(
                analysis_type=AnalysisType.HYPOTHESIS_GENERATION,
                parameter_changes=parameter_changes
            )
            
            if simulation and "estimated_improvement" in simulation:
                test_results["basic_simulation"] = True
                self.log("✅ Basic simulation completed")
                
                # Check impact estimation
                if simulation["estimated_improvement"] != 0:
                    test_results["impact_estimation"] = True
                    improvement = simulation["estimated_improvement"]
                    self.log(f"✅ Impact estimation: {improvement:.3f}")
                
                # Check confidence calculation
                if "confidence" in simulation:
                    test_results["confidence_calculation"] = True
                    confidence = simulation["confidence"]
                    self.log(f"✅ Confidence calculation: {confidence:.3f}")
            
        except Exception as e:
            test_results["errors"].append(f"Improvement simulation error: {str(e)}")
            self.log(f"❌ Improvement simulation failed: {e}", "ERROR")
        
        return test_results
    
    async def test_learning_insights(self) -> Dict[str, Any]:
        """Test learning insights generation"""
        self.log("🧠 Testing learning insights...")
        
        test_results = {
            "test_name": "learning_insights",
            "insights_generation": False,
            "trend_analysis": False,
            "cross_type_analysis": False,
            "errors": []
        }
        
        try:
            insights = await self.service.get_learning_insights()
            
            if insights and "insights_by_type" in insights:
                test_results["insights_generation"] = True
                self.log("✅ Learning insights generated")
                
                # Check trend analysis
                if "overall_trends" in insights:
                    test_results["trend_analysis"] = True
                    trends = insights["overall_trends"]
                    self.log(f"✅ Trend analysis: {len(trends)} trends identified")
                
                # Check cross-type analysis
                if len(insights["insights_by_type"]) > 1:
                    test_results["cross_type_analysis"] = True
                    types_count = len(insights["insights_by_type"])
                    self.log(f"✅ Cross-type analysis: {types_count} types analyzed")
            
        except Exception as e:
            test_results["errors"].append(f"Learning insights error: {str(e)}")
            self.log(f"❌ Learning insights failed: {e}", "ERROR")
        
        return test_results
    
    async def test_service_health(self) -> Dict[str, Any]:
        """Test service health monitoring"""
        self.log("🔍 Testing service health...")
        
        test_results = {
            "test_name": "service_health",
            "health_check": False,
            "data_availability": False,
            "configuration_info": False,
            "errors": []
        }
        
        try:
            health = await self.service.get_service_health()
            
            if health and "status" in health:
                test_results["health_check"] = True
                status = health["status"]
                self.log(f"✅ Health check: {status}")
                
                # Check data availability info
                if "feedback_entries" in health:
                    test_results["data_availability"] = True
                    entries = health["feedback_entries"]
                    self.log(f"✅ Data availability: {entries} feedback entries")
                
                # Check configuration info
                if "feedback_window_days" in health:
                    test_results["configuration_info"] = True
                    window = health["feedback_window_days"]
                    self.log(f"✅ Configuration info: {window} days window")
            
        except Exception as e:
            test_results["errors"].append(f"Service health error: {str(e)}")
            self.log(f"❌ Service health check failed: {e}", "ERROR")
        
        return test_results
    
    def print_test_summary(self, all_results: list):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🚀 ITERATIVE IMPROVEMENT PIPELINE - TEST RESULTS SUMMARY")
        print("="*80)
        
        total_tests = 0
        total_passed = 0
        
        for test_result in all_results:
            test_name = test_result.get("test_name", "unknown")
            print(f"\n📋 {test_name.replace('_', ' ').title()}:")
            print("-" * 50)
            
            # Count tests for this category
            test_keys = [k for k in test_result.keys() if k not in ['test_name', 'errors']]
            passed_count = sum(1 for k in test_keys if test_result[k])
            
            total_tests += len(test_keys)
            total_passed += passed_count
            
            # Print individual test results
            for test_key in test_keys:
                status = "✅ PASS" if test_result[test_key] else "❌ FAIL"
                print(f"  {test_key.replace('_', ' '):<25} {status}")
            
            # Print errors if any
            if test_result.get("errors"):
                print("  🔍 Errors:")
                for error in test_result["errors"][:2]:  # Show first 2 errors
                    print(f"    • {error}")
            
            # Category summary
            success_rate = (passed_count / len(test_keys)) * 100 if test_keys else 0
            print(f"\n  📊 Category Summary: {passed_count}/{len(test_keys)} tests passed ({success_rate:.1f}%)")
        
        # Overall summary
        print("\n" + "="*80)
        overall_success_rate = (total_passed / total_tests) * 100 if total_tests else 0
        print(f"🎯 OVERALL RESULTS: {total_passed}/{total_tests} tests passed ({overall_success_rate:.1f}%)")
        
        if overall_success_rate >= 85:
            print("🎉 EXCELLENT: Iterative improvement pipeline working perfectly!")
        elif overall_success_rate >= 70:
            print("✅ GOOD: Most pipeline features working correctly")
        elif overall_success_rate >= 50:
            print("⚠️  PARTIAL: Some pipeline features need attention")
        else:
            print("❌ CRITICAL: Major issues with improvement pipeline")
        
        print("="*80)
        
        return overall_success_rate >= 70
    
    async def run_all_tests(self) -> bool:
        """Run all improvement pipeline tests"""
        self.log("🔬 Starting Iterative Improvement Pipeline Test Suite...")
        
        if not await self.setup_service():
            return False
        
        # Run all tests
        test_results = []
        
        try:
            test_results.append(await self.test_feedback_recording())
            test_results.append(await self.test_metrics_calculation())
            test_results.append(await self.test_optimization_recommendations())
            test_results.append(await self.test_improvement_simulation())
            test_results.append(await self.test_learning_insights())
            test_results.append(await self.test_service_health())
            
            # Print summary
            success = self.print_test_summary(test_results)
            return success
            
        except Exception as e:
            self.log(f"❌ Test suite execution failed: {e}", "ERROR")
            return False


async def main():
    """Main test execution"""
    parser = argparse.ArgumentParser(description="Test iterative improvement pipeline")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Initialize test suite
    test_suite = IterativeImprovementTestSuite(verbose=args.verbose)
    
    try:
        # Run tests
        success = await test_suite.run_all_tests()
        
        # Set exit code
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: Test execution failed: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main())
