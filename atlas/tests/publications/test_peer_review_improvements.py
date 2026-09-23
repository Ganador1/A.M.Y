#!/usr/bin/env python3
"""
Test script for PeerReviewService improvements
"""

import sys
import os
import asyncio

# Mock all the problematic modules
class MockLogger:
    def info(self, msg):
        print(f"INFO: {msg}")
    
    def error(self, msg):
        print(f"ERROR: {msg}")
    
    def warning(self, msg):
        print(f"WARNING: {msg}")

# Mock all modules that cause import issues
sys.modules['app.core.bootstrap_logging'] = type('MockModule', (), {'logger': MockLogger()})()

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'services'))

async def test_peer_review_improvements():
    """Test the improved PeerReviewService"""
    print("🧪 Testing PeerReviewService Improvements")
    print("=" * 60)
    
    try:
        # Import the service directly
        from peer_review_service import PeerReviewService
        
        # Create service instance
        service = PeerReviewService()
        
        print(f"✅ Service created successfully")
        print(f"📊 Version: {service.version}")
        print(f"🔧 Advanced config: {len(service.advanced_config)} parameters")
        
        # Test papers for review
        test_papers = [
            {
                "paper_id": "test_001",
                "title": "Machine Learning Approach to Cancer Detection",
                "abstract": "We present a novel machine learning approach for cancer detection using deep neural networks. Our method achieves 95% accuracy on a dataset of 1000 patients (p < 0.001). We used cross-validation and sensitivity analysis to ensure robustness. The study was randomized and double-blind.",
                "authors": ["Dr. Smith", "Dr. Johnson"],
                "journal": "Nature Medicine",
                "year": "2024"
            },
            {
                "paper_id": "test_002", 
                "title": "Statistical Analysis of Gene Expression",
                "abstract": "This study analyzes gene expression patterns in cancer cells. We found significant differences between groups (p = 0.05). The sample size was small (n = 20) but results were promising. Further validation is needed.",
                "authors": ["Dr. Brown"],
                "journal": "Cell Reports",
                "year": "2024"
            },
            {
                "paper_id": "test_003",
                "title": "Questionable Research Practices in Psychology",
                "abstract": "We investigated questionable research practices in psychology. Our exploratory analysis found multiple significant results without correction for multiple comparisons. The methodology had several limitations and potential biases.",
                "authors": ["Dr. Wilson"],
                "journal": "Psychological Science",
                "year": "2024"
            }
        ]
        
        # Test 1: Advanced Peer Review
        print("\n📝 Testing Advanced Peer Review...")
        review_result = await service.review(test_papers)
        if "error" not in review_result:
            print(f"✅ Peer review successful")
            print(f"   Papers reviewed: {review_result['count']}")
            print(f"   Version: {review_result['version']}")
            
            # Show overall statistics
            overall_stats = review_result.get('overall_statistics', {})
            if 'error' not in overall_stats:
                print(f"   Average consensus score: {overall_stats.get('average_consensus_score', 0):.3f}")
                print(f"   Average statistical score: {overall_stats.get('average_statistical_score', 0):.3f}")
                print(f"   Average methodology score: {overall_stats.get('average_methodology_score', 0):.3f}")
                print(f"   Average robustness score: {overall_stats.get('average_robustness_score', 0):.3f}")
                print(f"   Total issues found: {overall_stats.get('total_issues', 0)}")
                print(f"   Critical issues: {overall_stats.get('critical_issues', 0)}")
            
            # Show individual paper results
            for i, paper in enumerate(review_result['papers'][:2]):  # Show first 2 papers
                if 'error' not in paper:
                    print(f"\n   Paper {i+1}: {paper['title']}")
                    quality_metrics = paper.get('quality_metrics', {})
                    print(f"     Consensus score: {quality_metrics.get('consensus_score', 0):.3f}")
                    print(f"     Statistical score: {quality_metrics.get('statistical_score', 0):.3f}")
                    print(f"     Methodology score: {quality_metrics.get('methodology_score', 0):.3f}")
                    print(f"     Robustness score: {quality_metrics.get('robustness_score', 0):.3f}")
                    print(f"     Sentiment: {quality_metrics.get('overall_sentiment', 'unknown')}")
                    print(f"     Total issues: {quality_metrics.get('total_issues', 0)}")
                    print(f"     Critical issues: {quality_metrics.get('critical_issues', 0)}")
                    print(f"     Major issues: {quality_metrics.get('major_issues', 0)}")
                    print(f"     Minor issues: {quality_metrics.get('minor_issues', 0)}")
                    
                    # Show recommendations
                    recommendations = paper.get('recommendations', [])
                    if recommendations:
                        print(f"     Recommendations: {len(recommendations)}")
                        for rec in recommendations[:2]:  # Show first 2 recommendations
                            print(f"       - {rec}")
                    
                    # Show review summary
                    summary = paper.get('review_summary', '')
                    if summary:
                        print(f"     Summary: {summary[:100]}...")
        else:
            print(f"❌ Peer review failed: {review_result['error']}")
        
        # Test 2: Individual Review Components
        print("\n🔍 Testing Individual Review Components...")
        
        # Test statistical review
        print("   Testing Statistical Review...")
        stat_review = await service._review_statistical(test_papers[0])
        if "error" not in stat_review:
            print(f"     ✅ Statistical review successful")
            print(f"     Score: {stat_review['score']}")
            print(f"     Issues: {len(stat_review.get('issues', []))}")
            if stat_review.get('statistical_elements'):
                elements = stat_review['statistical_elements']
                print(f"     P-values found: {len(elements.get('p_values', []))}")
                print(f"     Confidence intervals: {len(elements.get('confidence_intervals', []))}")
                print(f"     Effect sizes: {len(elements.get('effect_sizes', []))}")
        else:
            print(f"     ❌ Statistical review failed: {stat_review['error']}")
        
        # Test methodology review
        print("   Testing Methodology Review...")
        method_review = await service._review_methodology(test_papers[0])
        if "error" not in method_review:
            print(f"     ✅ Methodology review successful")
            print(f"     Score: {method_review['score']}")
            print(f"     Issues: {len(method_review.get('issues', []))}")
            if method_review.get('methodology_analysis'):
                analysis = method_review['methodology_analysis']
                print(f"     Strengths: {len(analysis.get('strengths', []))}")
                print(f"     Weaknesses: {len(analysis.get('weaknesses', []))}")
                print(f"     Missing elements: {len(analysis.get('missing_elements', []))}")
                print(f"     Bias indicators: {len(analysis.get('bias_indicators', []))}")
                print(f"     Reproducibility score: {analysis.get('reproducibility_score', 0):.3f}")
        else:
            print(f"     ❌ Methodology review failed: {method_review['error']}")
        
        # Test robustness review
        print("   Testing Robustness Review...")
        robust_review = await service._review_robustness(test_papers[0])
        if "error" not in robust_review:
            print(f"     ✅ Robustness review successful")
            print(f"     Score: {robust_review['score']}")
            print(f"     Issues: {len(robust_review.get('issues', []))}")
            if robust_review.get('robustness_indicators'):
                indicators = robust_review['robustness_indicators']
                print(f"     Sensitivity analysis: {indicators.get('sensitivity_analysis', False)}")
                print(f"     Cross-validation: {indicators.get('cross_validation', False)}")
                print(f"     Generalization: {indicators.get('generalization', False)}")
                print(f"     Replication: {indicators.get('replication', False)}")
        else:
            print(f"     ❌ Robustness review failed: {robust_review['error']}")
        
        # Test sentiment analysis
        print("   Testing Sentiment Analysis...")
        sentiment = await service._analyze_sentiment(test_papers[0]['title'] + " " + test_papers[0]['abstract'])
        print(f"     ✅ Sentiment analysis successful")
        print(f"     Overall sentiment: {sentiment.overall_sentiment}")
        print(f"     Confidence: {sentiment.confidence:.3f}")
        print(f"     Sentiment scores: {sentiment.sentiment_scores}")
        if sentiment.tone_indicators:
            print(f"     Tone classification: {sentiment.tone_indicators.get('tone_classification', 'unknown')}")
            print(f"     Cautious language: {sentiment.tone_indicators.get('cautious_language', 0)}")
            print(f"     Confident language: {sentiment.tone_indicators.get('confident_language', 0)}")
        
        # Test 3: Health Check
        print("\n🏥 Testing Health Check...")
        health_result = await service.health_check()
        if health_result['service_status'] == 'healthy':
            print(f"✅ Health check successful")
            print(f"   Service status: {health_result['service_status']}")
            print(f"   Model readiness: {health_result['model_readiness']:.1%}")
            print(f"   Capabilities: {len(health_result['capabilities'])}")
            for capability in health_result['capabilities']:
                print(f"     - {capability}")
            
            # Show model capabilities
            model_caps = health_result.get('model_capabilities', {})
            print(f"   Model capabilities:")
            for model, available in model_caps.items():
                status = "✅" if available else "❌"
                print(f"     {status} {model}")
        else:
            print(f"❌ Health check failed: {health_result.get('error', 'Unknown error')}")
        
        print("\n🎉 Peer Review Service Improvements Test Complete!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to run async test"""
    return asyncio.run(test_peer_review_improvements())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
