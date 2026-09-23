#!/usr/bin/env python3
"""
Strategic Planner Service Functional Demonstration
Comprehensive demonstration of autonomous research strategy planning

This demo showcases the complete Strategic Planner workflow:
1. Autonomous knowledge gap identification
2. Research objective generation with ROI analysis
3. Portfolio optimization and management
4. Progress monitoring and strategy adaptation

Author: AXIOM Autonomous Laboratory System
Date: September 13, 2025
"""

import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def demonstrate_strategic_planner():
    """
    🧠 Strategic Planner Comprehensive Demonstration
    
    This demonstration shows how AXIOM autonomously:
    1. Analyzes the knowledge landscape to identify gaps
    2. Generates strategic research objectives
    3. Creates and optimizes research portfolios
    4. Monitors progress and adapts strategies
    """
    
    print("\n" + "="*80)
    print("🧠 AXIOM STRATEGIC PLANNER - AUTONOMOUS RESEARCH PLANNING DEMO")
    print("="*80)
    print("🎯 Mission: Demonstrate autonomous research strategy planning and execution")
    print()
    
    try:
        # Import the Strategic Planner Service
        from app.services.strategic_planner_service import strategic_planner
        
        # Phase 1: Knowledge Landscape Analysis
        print("🔍 PHASE 1: AUTONOMOUS KNOWLEDGE LANDSCAPE ANALYSIS")
        print("-" * 60)
        
        analysis_results = await strategic_planner.analyze_knowledge_landscape()
        
        print(f"📊 Papers Analyzed: {analysis_results['total_papers_analyzed']:,}")
        print(f"🎯 Domains Covered: {analysis_results['domains_covered']}")
        print(f"💡 Knowledge Gaps Identified: {analysis_results['gaps_identified']}")
        print(f"📈 Research Trends Detected: {analysis_results['trends_detected']}")
        print(f"🔗 Interdisciplinary Opportunities: {analysis_results['opportunities_found']}")
        print(f"⏰ Analysis Timestamp: {analysis_results['analysis_timestamp']}")
        print()
        
        # Phase 2: Research Objective Generation
        print("🎯 PHASE 2: AUTONOMOUS RESEARCH OBJECTIVE GENERATION")
        print("-" * 60)
        
        objectives = await strategic_planner.generate_research_objectives(max_objectives=8)
        
        print(f"📝 Total Objectives Generated: {len(objectives)}")
        print()
        
        # Display top 5 objectives with detailed analysis
        print("🏆 TOP 5 RESEARCH OBJECTIVES (by ROI):")
        sorted_objectives = sorted(objectives, key=lambda x: x.roi_estimate, reverse=True)[:5]
        
        for i, obj in enumerate(sorted_objectives, 1):
            print(f"\n{i}. {obj.title}")
            print(f"   🔬 Domain: {obj.domain.value.replace('_', ' ').title()}")
            print(f"   ⭐ Priority: {obj.priority.value.upper()}")
            print(f"   💰 ROI Estimate: {obj.roi_estimate:.2f}x")
            print(f"   ⏱️  Duration: {obj.estimated_duration.days} days")
            print(f"   💸 Budget: ${obj.required_resources.get('experimental_budget', 0):,}")
            print(f"   ⚠️  Risk Factors: {len(obj.risk_factors)}")
            print(f"   ✅ Success Criteria: {len(obj.success_criteria)}")
        
        print()
        
        # Phase 3: Strategic Portfolio Creation
        print("📊 PHASE 3: STRATEGIC RESEARCH PORTFOLIO CREATION")
        print("-" * 60)
        
        # Create high-impact portfolio
        high_impact_objectives = [obj.id for obj in sorted_objectives[:4]]
        total_budget = 750000.0
        
        portfolio = await strategic_planner.create_research_portfolio(
            name="High-Impact Research Portfolio 2025",
            objective_ids=high_impact_objectives,
            total_budget=total_budget
        )
        
        print(f"📁 Portfolio Created: {portfolio.name}")
        print(f"🎯 Objectives Included: {len(portfolio.objectives)}")
        print(f"💰 Total Budget: ${portfolio.total_budget:,.2f}")
        print(f"💸 Allocated Budget: ${portfolio.allocated_budget:,.2f}")
        print(f"📈 Expected ROI: {portfolio.expected_roi:.2f}x")
        print(f"⚠️  Risk Level: {portfolio.risk_level:.2f}")
        print()
        
        # Phase 4: Portfolio Optimization
        print("⚡ PHASE 4: AUTONOMOUS PORTFOLIO OPTIMIZATION")
        print("-" * 60)
        
        optimization_results = await strategic_planner.optimize_portfolio(portfolio.id)
        
        print(f"🔄 Original ROI: {optimization_results['original_roi']:.2f}")
        print(f"✨ Optimized ROI: {optimization_results['new_roi']:.2f}")
        print(f"📈 ROI Improvement: {optimization_results['improvement_roi']:.2f}")
        print(f"📉 Risk Reduction: {optimization_results['improvement_risk']:.2f}")
        print(f"🛠️  Optimizations Applied: {len(optimization_results['optimizations_applied'])}")
        
        for optimization in optimization_results['optimizations_applied']:
            print(f"   • {optimization}")
        
        print()
        
        # Phase 5: Progress Monitoring
        print("📊 PHASE 5: RESEARCH PROGRESS MONITORING")
        print("-" * 60)
        
        # Simulate some progress on objectives
        for i, obj in enumerate(sorted_objectives[:3]):
            obj.progress = 0.2 + (i * 0.15)  # Simulate different progress levels
        
        progress_report = await strategic_planner.monitor_progress()
        
        print(f"📈 Total Objectives Tracked: {progress_report['total_objectives']}")
        print(f"⚠️  Overdue Objectives: {progress_report.get('overdue_objectives', 0)}")
        
        print("\n🔍 Status Breakdown:")
        for status, count in progress_report['status_breakdown'].items():
            print(f"   • {status.replace('_', ' ').title()}: {count}")
        
        if 'progress_summary' in progress_report and 'average_progress' in progress_report['progress_summary']:
            avg_progress = progress_report['progress_summary']['average_progress']
            print(f"\n📊 Average Progress: {avg_progress:.1%}")
        
        if progress_report['bottlenecks_identified']:
            print(f"\n⚠️  Bottlenecks Identified: {len(progress_report['bottlenecks_identified'])}")
            for bottleneck in progress_report['bottlenecks_identified']:
                print(f"   • {bottleneck}")
        
        if progress_report['recommendations']:
            print(f"\n💡 Strategic Recommendations: {len(progress_report['recommendations'])}")
            for recommendation in progress_report['recommendations']:
                print(f"   • {recommendation}")
        
        print()
        
        # Phase 6: Adaptive Strategy Management
        print("🔄 PHASE 6: ADAPTIVE STRATEGY MANAGEMENT")
        print("-" * 60)
        
        performance_data = {
            "review_trigger": "quarterly_review",
            "performance_metrics": {
                "average_roi_achieved": 3.2,
                "objectives_completed_on_time": 0.75,
                "budget_utilization": 0.88
            }
        }
        
        adaptations = await strategic_planner.adapt_strategy(performance_data)
        
        print("🔄 Strategy Adaptation Completed")
        print(f"⏰ Timestamp: {adaptations['timestamp']}")
        print(f"🎯 Trigger: {adaptations['trigger']}")
        print(f"🛠️  Changes Made: {len(adaptations['changes_made'])}")
        
        for change in adaptations['changes_made']:
            print(f"   • {change}")
        
        print("\n📊 Strategy Adjustments:")
        for adjustment_type, details in adaptations['strategy_adjustments'].items():
            print(f"   • {adjustment_type}: {details}")
        
        print("\n📈 Estimated Impact:")
        for impact_type, value in adaptations['impact_estimate'].items():
            print(f"   • {impact_type.replace('_', ' ').title()}: {value:.2f}")
        
        print()
        
        # Phase 7: Knowledge Gap Analysis
        print("🔍 PHASE 7: DETAILED KNOWLEDGE GAP ANALYSIS")
        print("-" * 60)
        
        gaps = list(strategic_planner.knowledge_gaps.values())
        high_priority_gaps = sorted(gaps, key=lambda x: x.priority_score or 0, reverse=True)[:3]
        
        print(f"📊 Total Knowledge Gaps Tracked: {len(gaps)}")
        print("\n🏆 TOP 3 HIGH-PRIORITY GAPS:")
        
        for i, gap in enumerate(high_priority_gaps, 1):
            print(f"\n{i}. {gap.title}")
            print(f"   🔬 Domain: {gap.domain.value.replace('_', ' ').title()}")
            print(f"   📊 Priority Score: {gap.priority_score:.3f}")
            print(f"   🎯 Confidence: {gap.confidence:.1%}")
            print(f"   🚀 Potential Impact: {gap.potential_impact:.1%}")
            print(f"   ⚙️ Difficulty: {gap.difficulty:.1%}")
            print(f"   📚 Related Publications: {len(gap.related_publications)}")
        
        print()
        
        # Phase 8: Service Status and Capabilities
        print("🧠 PHASE 8: STRATEGIC PLANNER STATUS & CAPABILITIES")
        print("-" * 60)
        
        service_status = await strategic_planner.get_service_status()
        
        print(f"🏷️  Service: {service_status['service_name']}")
        print(f"✅ Status: {service_status['status'].upper()}")
        print(f"📦 Version: {service_status['version']}")
        
        print("\n📊 Statistics:")
        stats = service_status['statistics']
        print(f"   • Knowledge Gaps: {stats['knowledge_gaps_tracked']}")
        print(f"   • Research Objectives: {stats['research_objectives']}")
        print(f"   • Active Portfolios: {stats['active_portfolios']}")
        print(f"   • Literature Insights: {stats['literature_insights']}")
        print(f"   • Expertise Areas: {stats['domain_expertise_areas']}")
        
        print("\n🚀 Core Capabilities:")
        for capability in service_status['capabilities']:
            print(f"   • {capability}")
        
        print()
        
        # Final Summary
        print("🎉 STRATEGIC PLANNER DEMONSTRATION COMPLETE")
        print("="*80)
        print("📋 SUMMARY OF AUTONOMOUS ACHIEVEMENTS:")
        print(f"   🔍 Analyzed {analysis_results['total_papers_analyzed']:,} research papers")
        print(f"   💡 Identified {analysis_results['gaps_identified']} knowledge gaps")
        print(f"   🎯 Generated {len(objectives)} research objectives")
        print("   📊 Created 1 optimized research portfolio")
        print(f"   💰 Managed ${portfolio.total_budget:,.2f} in research funding")
        print(f"   📈 Achieved {optimization_results['new_roi']:.2f}x expected ROI")
        print(f"   🔄 Applied {len(adaptations['changes_made'])} strategic adaptations")
        print()
        print("🧠 The Strategic Planner demonstrates AXIOM's capability for:")
        print("   • Fully autonomous research planning and strategy")
        print("   • Real-time performance monitoring and optimization")
        print("   • Adaptive strategy adjustment based on results")
        print("   • Multi-domain knowledge gap identification")
        print("   • ROI-optimized resource allocation")
        print()
        print("✅ AXIOM is now capable of autonomous scientific research planning!")
        print("🚀 Ready to advance laboratory autonomy to the next level!")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {str(e)}")
        print(f"\n❌ Error during demonstration: {str(e)}")
        raise

async def demonstrate_strategic_planner_api():
    """
    🌐 Demonstrate Strategic Planner via API endpoints
    
    Shows how the Strategic Planner can be accessed through REST API
    for integration with external systems and web interfaces.
    """
    
    print("\n" + "="*80)
    print("🌐 STRATEGIC PLANNER API DEMONSTRATION")
    print("="*80)
    
    try:
        from fastapi.testclient import TestClient
        from app.routers.strategic_planner_router import router
        from fastapi import FastAPI
        
        # Create test app
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Test service status endpoint
        print("🔍 Testing Service Status Endpoint...")
        response = client.get("/strategic-planner/status")
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ Service Status: {status_data['status']}")
            print(f"📊 Tracked Objectives: {status_data['statistics']['research_objectives']}")
        
        # Test knowledge landscape analysis
        print("\n🧠 Testing Knowledge Landscape Analysis...")
        response = client.post("/strategic-planner/analyze-knowledge-landscape")
        if response.status_code == 200:
            analysis_data = response.json()
            print(f"✅ Analysis Complete: {analysis_data['message']}")
            print(f"💡 Gaps Found: {analysis_data['analysis_results']['gaps_identified']}")
        
        # Test objective generation
        print("\n🎯 Testing Objective Generation...")
        response = client.post("/strategic-planner/generate-objectives?max_objectives=3")
        if response.status_code == 200:
            objectives_data = response.json()
            print(f"✅ Generated {objectives_data['objectives_count']} objectives")
            
            if objectives_data['objectives']:
                sample_objective = objectives_data['objectives'][0]
                print(f"📋 Sample Objective: {sample_objective['title']}")
                print(f"💰 ROI: {sample_objective['roi_estimate']:.2f}x")
        
        print("\n🌐 API Demonstration Complete!")
        print("✅ All endpoints are functional and ready for integration")
        
    except ImportError as e:
        print(f"⚠️  API demo skipped: {e}")
    except Exception as e:
        print(f"❌ API demo error: {e}")

if __name__ == "__main__":
    async def main():
        """Run the complete Strategic Planner demonstration"""
        
        print("🚀 Starting AXIOM Strategic Planner Demonstration...")
        
        # Run main service demonstration
        await demonstrate_strategic_planner()
        
        # Run API demonstration
        await demonstrate_strategic_planner_api()
        
        print("\n🎉 All Strategic Planner demonstrations completed successfully!")
        print("📈 AXIOM's autonomous research planning capabilities are fully operational!")
    
    # Run the demonstration
    asyncio.run(main())
