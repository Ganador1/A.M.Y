#!/usr/bin/env python3
"""
Test script for AdvancedConsistencyCheckerService improvements
"""

import sys
import os
import asyncio

async def test_consistency_checker_improvements():
    """Test the improved ConsistencyCheckerService"""
    print("🔍 Testing Advanced Consistency Checker Service Improvements")
    print("=" * 65)
    
    try:
        # Import the improved service directly
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'services'))
        from consistency_checker_service_improved import AdvancedConsistencyCheckerService
        
        # Create service instance
        service = AdvancedConsistencyCheckerService()
        
        print(f"✅ Service created successfully")
        print(f"📊 Version: {service.version}")
        print(f"🔧 Advanced config: {len(service.advanced_config)} parameters")
        
        # Test 1: Basic Consistency Check (Legacy Interface)
        print("\n📋 Testing Basic Consistency Check...")
        
        test_text_1 = """
        The study shows that exercise increases cardiovascular health. 
        Physical activity reduces the risk of heart disease. 
        However, exercise has no effect on heart health according to recent findings.
        We recommend daily physical activity for optimal wellness.
        """
        
        basic_result = service.check(test_text_1, required_terms=["exercise", "health", "missing_term"])
        print(f"✅ Basic check completed")
        print(f"   Overall score: {basic_result['score']}")
        print(f"   Issues found: {basic_result['issue_count']}")
        print(f"   Analysis type: {basic_result['analysis_type']}")
        
        for issue in basic_result['issues']:
            print(f"     - {issue['type']}: {issue.get('term', issue.get('patterns', str(issue)))}")
        
        # Test 2: Comprehensive Analysis
        print("\n🧠 Testing Comprehensive Analysis...")
        
        test_text_2 = """
        Climate change is a significant global challenge that requires immediate action.
        Rising temperatures have been observed worldwide over the past century.
        However, some regions show no evidence of temperature increase.
        The scientific consensus is clear that human activities are the primary cause.
        We must implement renewable energy solutions to reduce carbon emissions.
        Solar and wind power are becoming increasingly cost-effective.
        Therefore, transitioning to clean energy is both necessary and economically viable.
        """
        
        comprehensive_result = await service.comprehensive_check(
            test_text_2, 
            required_terms=["climate change", "renewable energy", "biodiversity"],
            context="Scientific report on climate action"
        )
        
        print(f"✅ Comprehensive analysis completed")
        print(f"   Overall score: {comprehensive_result.overall_score:.3f}")
        print(f"   Inconsistency issues: {len(comprehensive_result.inconsistency_issues)}")
        print(f"   Logical relations: {len(comprehensive_result.logical_relations)}")
        print(f"   Semantic gaps: {len(comprehensive_result.semantic_gaps)}")
        
        # Show inconsistency issues
        if comprehensive_result.inconsistency_issues:
            print(f"   Inconsistency Issues:")
            for issue in comprehensive_result.inconsistency_issues:
                print(f"     - {issue.issue_type} ({issue.severity}): {issue.description}")
                print(f"       Confidence: {issue.confidence:.3f}")
                if issue.suggestion:
                    print(f"       Suggestion: {issue.suggestion}")
        
        # Show logical relations
        if comprehensive_result.logical_relations:
            print(f"   Logical Relations:")
            for relation in comprehensive_result.logical_relations[:3]:  # Show first 3
                print(f"     - {relation.relation.capitalize()} (confidence: {relation.confidence:.3f})")
                print(f"       Premise: {relation.premise[:80]}...")
                print(f"       Hypothesis: {relation.hypothesis[:80]}...")
                print(f"       Reasoning: {relation.reasoning}")
        
        # Show semantic gaps
        if comprehensive_result.semantic_gaps:
            print(f"   Semantic Gaps:")
            for gap in comprehensive_result.semantic_gaps:
                print(f"     - Missing: {gap.missing_concept} (importance: {gap.importance:.2f})")
                print(f"       Context: {gap.context}")
                if gap.suggestions:
                    print(f"       Suggestions: {', '.join(gap.suggestions[:2])}")
        
        # Show coherence metrics
        coherence_metrics = comprehensive_result.coherence_metrics
        if coherence_metrics:
            print(f"   Coherence Metrics:")
            for metric, value in coherence_metrics.items():
                print(f"     - {metric.replace('_', ' ').title()}: {value:.3f}")
        
        # Show recommendations
        print(f"   Recommendations ({len(comprehensive_result.recommendations)}):")
        for rec in comprehensive_result.recommendations:
            print(f"     {rec}")
        
        # Show text statistics
        text_stats = comprehensive_result.text_statistics
        if text_stats and 'error' not in text_stats:
            print(f"   Text Statistics:")
            print(f"     - Words: {text_stats.get('word_count', 0)}")
            print(f"     - Sentences: {text_stats.get('sentence_count', 0)}")
            print(f"     - Avg sentence length: {text_stats.get('average_sentence_length', 0):.1f} words")
            print(f"     - Unique word ratio: {text_stats.get('unique_word_ratio', 0):.3f}")
        
        # Test 3: Contradiction Detection
        print("\n⚠️ Testing Contradiction Detection...")
        
        contradictory_text = """
        The new medication is completely safe for all patients.
        Clinical trials show no adverse effects in any participants.
        However, the drug is dangerous and causes severe side effects.
        All patients experienced significant improvement.
        No patients showed any improvement in their condition.
        The treatment is both effective and ineffective simultaneously.
        """
        
        contradiction_result = await service.comprehensive_check(contradictory_text)
        
        print(f"✅ Contradiction detection completed")
        print(f"   Overall score: {contradiction_result.overall_score:.3f}")
        print(f"   Issues found: {len(contradiction_result.inconsistency_issues)}")
        
        # Count contradiction types
        contradiction_count = len([
            issue for issue in contradiction_result.inconsistency_issues 
            if issue.issue_type == "logical_contradiction"
        ])
        
        logical_contradictions = len([
            rel for rel in contradiction_result.logical_relations 
            if rel.relation == "contradiction"
        ])
        
        print(f"   Logical contradictions found: {logical_contradictions}")
        print(f"   Contradiction issues: {contradiction_count}")
        
        # Show detected contradictions
        for relation in contradiction_result.logical_relations:
            if relation.relation == "contradiction":
                print(f"   Detected contradiction:")
                print(f"     - Premise: {relation.premise[:80]}...")
                print(f"     - Hypothesis: {relation.hypothesis[:80]}...")
                print(f"     - Confidence: {relation.confidence:.3f}")
                print(f"     - Reasoning: {relation.reasoning}")
        
        # Test 4: Argument Structure Analysis
        print("\n📊 Testing Argument Structure Analysis...")
        
        argument_text = """
        We claim that artificial intelligence will revolutionize healthcare.
        Studies show that AI algorithms can diagnose diseases with 95% accuracy.
        Research demonstrates significant improvements in patient outcomes.
        The evidence clearly supports widespread AI adoption in medical practice.
        Therefore, we conclude that AI is the future of medicine.
        However, some argue that AI lacks the human touch necessary for patient care.
        """
        
        argument_result = await service.comprehensive_check(argument_text)
        
        print(f"✅ Argument structure analysis completed")
        print(f"   Overall score: {argument_result.overall_score:.3f}")
        
        # Show argument-related issues
        argument_issues = [
            issue for issue in argument_result.inconsistency_issues 
            if "argument" in issue.issue_type or "conclusion" in issue.issue_type
        ]
        
        if argument_issues:
            print(f"   Argument structure issues:")
            for issue in argument_issues:
                print(f"     - {issue.description}")
                print(f"       Severity: {issue.severity}, Confidence: {issue.confidence:.3f}")
        else:
            print(f"   No significant argument structure issues detected")
        
        # Test 5: Short Text Analysis
        print("\n📝 Testing Short Text Analysis...")
        
        short_text = "AI is good."
        short_result = await service.comprehensive_check(short_text)
        
        print(f"✅ Short text analysis completed")
        print(f"   Overall score: {short_result.overall_score:.3f}")
        print(f"   Recommendations: {short_result.recommendations}")
        
        # Test 6: Performance Test
        print("\n⚡ Testing Performance...")
        
        medium_text = """
        Artificial intelligence represents one of the most significant technological advances of the 21st century.
        Machine learning algorithms are increasingly being deployed across various industries.
        Natural language processing enables computers to understand human communication.
        Computer vision allows machines to interpret visual information.
        Deep learning networks can identify complex patterns in large datasets.
        However, AI systems often lack transparency in their decision-making processes.
        The black box nature of neural networks raises concerns about accountability.
        Ethical considerations are paramount when developing AI applications.
        Privacy and security issues must be addressed in AI implementations.
        Bias in training data can lead to unfair outcomes in AI systems.
        """ * 3  # Make it longer
        
        import time
        start_time = time.time()
        
        performance_result = await service.comprehensive_check(
            medium_text, 
            required_terms=["AI", "machine learning", "ethics", "transparency"]
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"✅ Performance test completed")
        print(f"   Processing time: {processing_time:.2f} seconds")
        print(f"   Text length: {len(medium_text)} characters")
        print(f"   Words per second: {len(medium_text.split()) / processing_time:.0f}")
        print(f"   Overall score: {performance_result.overall_score:.3f}")
        print(f"   Total analysis results:")
        print(f"     - Issues: {len(performance_result.inconsistency_issues)}")
        print(f"     - Relations: {len(performance_result.logical_relations)}")
        print(f"     - Gaps: {len(performance_result.semantic_gaps)}")
        
        print("\n🎉 Advanced Consistency Checker Service Test Complete!")
        print("=" * 65)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to run async test"""
    return asyncio.run(test_consistency_checker_improvements())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
