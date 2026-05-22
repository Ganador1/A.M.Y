#!/usr/bin/env python3
"""
Test script for Advanced Evidence Synthesis Service
Validates comprehensive evidence synthesis functionality

Usage:
    python test_evidence_synthesis.py [--verbose]
"""

import asyncio
import sys
import argparse
import traceback
from datetime import datetime, timezone as tz
from typing import Dict, Any

# Add the project root to Python path
sys.path.append('.')

from app.services.evidence_synthesis_service import (
    AdvancedEvidenceSynthesisService,
    EvidenceSource,
    EvidenceType,
    ConfidenceLevel
)

UTC = tz.utc

class EvidenceSynthesisTestSuite:
    """Test suite for Advanced Evidence Synthesis Service"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.service = None
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        if self.verbose or level in ["ERROR", "SUCCESS"]:
            print(f"[{timestamp}] {level}: {message}")
    
    async def setup_service(self) -> Dict[str, Any]:
        """Initialize the evidence synthesis service"""
        self.log("🔧 Initializing Evidence Synthesis Service...")
        
        test_results = {
            "test_name": "service_initialization",
            "initialization": False,
            "domain_expertise": False,
            "conflict_strategies": False,
            "errors": []
        }
        
        try:
            self.service = AdvancedEvidenceSynthesisService(cache_size=50)
            test_results["initialization"] = True
            self.log("✅ Service initialized successfully")
            
            # Check domain expertise
            if hasattr(self.service, 'domain_expertise') and self.service.domain_expertise:
                test_results["domain_expertise"] = True
                domains_count = len(self.service.domain_expertise)
                self.log(f"✅ Domain expertise loaded: {domains_count} domains")
            
            # Check conflict resolution strategies
            if hasattr(self.service, 'conflict_resolution_strategies') and self.service.conflict_resolution_strategies:
                test_results["conflict_strategies"] = True
                strategies_count = len(self.service.conflict_resolution_strategies)
                self.log(f"✅ Conflict resolution strategies: {strategies_count} methods")
            
        except Exception as e:
            test_results["errors"].append(f"Service initialization error: {str(e)}")
            self.log(f"❌ Service initialization failed: {e}", "ERROR")
        
        return test_results
    
    async def test_evidence_clustering(self) -> Dict[str, Any]:
        """Test evidence clustering functionality"""
        self.log("🔍 Testing evidence clustering...")
        
        test_results = {
            "test_name": "evidence_clustering",
            "basic_clustering": False,
            "similarity_calculation": False,
            "topic_extraction": False,
            "errors": []
        }
        
        try:
            # Create test evidence sources
            evidence_sources = [
                EvidenceSource(
                    id="ev1",
                    title="CRISPR gene therapy for sickle cell disease",
                    content="Clinical trial results show promising outcomes for CRISPR-based gene therapy in treating sickle cell disease patients.",
                    evidence_type=EvidenceType.CLINICAL_TRIAL,
                    confidence_score=0.85,
                    reliability_score=0.90,
                    publication_date=datetime(2023, 6, 15, tzinfo=UTC),
                    domain="medicine",
                    authors=["Smith J", "Johnson A"],
                    citations=45,
                    tags=["CRISPR", "gene therapy", "sickle cell"]
                ),
                EvidenceSource(
                    id="ev2",
                    title="CRISPR delivery mechanisms in genetic diseases",
                    content="Review of various CRISPR delivery systems including viral vectors and lipid nanoparticles for genetic disease treatment.",
                    evidence_type=EvidenceType.LITERATURE_REVIEW,
                    confidence_score=0.75,
                    reliability_score=0.80,
                    publication_date=datetime(2023, 8, 20, tzinfo=UTC),
                    domain="biology",
                    authors=["Brown M", "Davis K"],
                    citations=32,
                    tags=["CRISPR", "delivery", "vectors"]
                ),
                EvidenceSource(
                    id="ev3",
                    title="Graphene nanocomposite electrical properties",
                    content="Experimental analysis of electrical conductivity in graphene-polymer nanocomposites for electronics applications.",
                    evidence_type=EvidenceType.EXPERIMENTAL,
                    confidence_score=0.90,
                    reliability_score=0.85,
                    publication_date=datetime(2023, 5, 10, tzinfo=UTC),
                    domain="materials_science",
                    authors=["Wilson R", "Taylor S"],
                    citations=28,
                    tags=["graphene", "conductivity", "nanocomposite"]
                )
            ]
            
            # Test clustering
            clusters = await self.service._cluster_evidence(evidence_sources, threshold=0.5, max_clusters=5)
            
            if clusters:
                test_results["basic_clustering"] = True
                self.log(f"✅ Basic clustering successful: {len(clusters)} clusters created")
                
                # Test topic extraction
                if all(cluster.topic for cluster in clusters):
                    test_results["topic_extraction"] = True
                    topics = [cluster.topic for cluster in clusters]
                    self.log(f"✅ Topic extraction successful: {topics}")
            
            # Test similarity calculation
            sim_score = self.service._calculate_semantic_similarity(evidence_sources[0], evidence_sources[1])
            if 0.0 <= sim_score <= 1.0:
                test_results["similarity_calculation"] = True
                self.log(f"✅ Similarity calculation successful: {sim_score:.3f}")
            
        except Exception as e:
            test_results["errors"].append(f"Evidence clustering error: {str(e)}")
            self.log(f"❌ Evidence clustering failed: {e}", "ERROR")
        
        return test_results
    
    async def test_cluster_analysis(self) -> Dict[str, Any]:
        """Test cluster analysis functionality"""
        self.log("📊 Testing cluster analysis...")
        
        test_results = {
            "test_name": "cluster_analysis",
            "consensus_calculation": False,
            "conflict_detection": False,
            "findings_extraction": False,
            "errors": []
        }
        
        try:
            # Create test evidence cluster
            from app.services.evidence_synthesis_service import EvidenceCluster
            
            evidence_sources = [
                EvidenceSource(
                    id="ev1",
                    title="High-confidence study on protein folding",
                    content="Detailed analysis shows protein folding mechanisms with high accuracy.",
                    evidence_type=EvidenceType.EXPERIMENTAL,
                    confidence_score=0.90,
                    reliability_score=0.85,
                    publication_date=datetime(2023, 6, 15, tzinfo=UTC),
                    domain="biology",
                    authors=["Expert A"],
                    tags=["protein", "folding"]
                ),
                EvidenceSource(
                    id="ev2", 
                    title="Medium-confidence protein study",
                    content="Additional research on protein structures with moderate confidence.",
                    evidence_type=EvidenceType.OBSERVATIONAL,
                    confidence_score=0.65,
                    reliability_score=0.70,
                    publication_date=datetime(2023, 7, 20, tzinfo=UTC),
                    domain="biology",
                    authors=["Expert B"],
                    tags=["protein", "structure"]
                )
            ]
            
            test_cluster = EvidenceCluster(
                id="test_cluster",
                topic="Protein Research",
                evidence_sources=evidence_sources,
                consensus_level=0.0,  # Will be calculated
                conflict_level=0.0,   # Will be calculated
                main_findings=[],     # Will be filled
                conflicting_points=[], # Will be filled
                confidence_distribution={}  # Will be calculated
            )
            
            # Analyze cluster
            analyzed_cluster = await self.service._analyze_evidence_cluster(test_cluster)
            
            # Check consensus calculation
            if 0.0 <= analyzed_cluster.consensus_level <= 1.0:
                test_results["consensus_calculation"] = True
                self.log(f"✅ Consensus calculation successful: {analyzed_cluster.consensus_level:.3f}")
            
            # Check conflict detection
            if 0.0 <= analyzed_cluster.conflict_level <= 1.0:
                test_results["conflict_detection"] = True
                self.log(f"✅ Conflict detection successful: {analyzed_cluster.conflict_level:.3f}")
            
            # Check findings extraction
            if analyzed_cluster.main_findings:
                test_results["findings_extraction"] = True
                findings_count = len(analyzed_cluster.main_findings)
                self.log(f"✅ Findings extraction successful: {findings_count} findings")
            
        except Exception as e:
            test_results["errors"].append(f"Cluster analysis error: {str(e)}")
            self.log(f"❌ Cluster analysis failed: {e}", "ERROR")
        
        return test_results
    
    async def test_full_synthesis(self) -> Dict[str, Any]:
        """Test complete evidence synthesis pipeline"""
        self.log("🧠 Testing full evidence synthesis...")
        
        test_results = {
            "test_name": "full_synthesis",
            "synthesis_completion": False,
            "cross_domain_detection": False,
            "conflict_resolution": False,
            "conclusions_generation": False,
            "methodology_assessment": False,
            "errors": []
        }
        
        try:
            # Create comprehensive test evidence
            evidence_sources = [
                # Medicine domain
                EvidenceSource(
                    id="med1",
                    title="Clinical efficacy of targeted cancer therapy",
                    content="Phase III clinical trial demonstrates significant improvement in patient outcomes using targeted molecular therapy for cancer treatment.",
                    evidence_type=EvidenceType.CLINICAL_TRIAL,
                    confidence_score=0.90,
                    reliability_score=0.95,
                    publication_date=datetime(2023, 4, 15, tzinfo=UTC),
                    domain="medicine",
                    authors=["Dr. Smith", "Dr. Johnson"],
                    citations=67,
                    peer_reviewed=True,
                    methodology_score=0.85,
                    sample_size=450,
                    statistical_power=0.90,
                    tags=["cancer", "therapy", "clinical trial"]
                ),
                # Biology domain  
                EvidenceSource(
                    id="bio1",
                    title="Molecular mechanisms of targeted therapy resistance",
                    content="Laboratory studies reveal cellular mechanisms underlying resistance to targeted molecular therapies in cancer cells.",
                    evidence_type=EvidenceType.EXPERIMENTAL,
                    confidence_score=0.85,
                    reliability_score=0.80,
                    publication_date=datetime(2023, 6, 10, tzinfo=UTC),
                    domain="biology",
                    authors=["Dr. Brown", "Dr. Davis"],
                    citations=43,
                    peer_reviewed=True,
                    methodology_score=0.80,
                    sample_size=None,
                    tags=["molecular", "resistance", "cancer"]
                ),
                # Computational study
                EvidenceSource(
                    id="comp1",
                    title="Computational prediction of therapy effectiveness",
                    content="Machine learning models predict patient response to targeted therapies based on genetic markers and clinical data.",
                    evidence_type=EvidenceType.COMPUTATIONAL,
                    confidence_score=0.75,
                    reliability_score=0.85,
                    publication_date=datetime(2023, 8, 5, tzinfo=UTC),
                    domain="computer_science",
                    authors=["Dr. Wilson", "Dr. Taylor"],
                    citations=29,
                    peer_reviewed=True,
                    methodology_score=0.75,
                    tags=["prediction", "machine learning", "therapy"]
                )
            ]
            
            # Perform full synthesis
            result = await self.service.synthesize_evidence(
                evidence_sources=evidence_sources,
                query="Effectiveness and mechanisms of targeted cancer therapy",
                synthesis_parameters={
                    "min_confidence": 0.3,
                    "cluster_threshold": 0.6,
                    "max_clusters": 10
                }
            )
            
            # Check synthesis completion
            if result and hasattr(result, 'id'):
                test_results["synthesis_completion"] = True
                self.log(f"✅ Synthesis completed: {result.id}")
                
                # Check cross-domain connections
                if hasattr(result, 'cross_domain_connections') and result.cross_domain_connections:
                    test_results["cross_domain_detection"] = True
                    connections_count = len(result.cross_domain_connections)
                    self.log(f"✅ Cross-domain connections detected: {connections_count}")
                
                # Check conflict resolutions
                if hasattr(result, 'conflict_resolutions'):
                    test_results["conflict_resolution"] = True
                    resolutions_count = len(result.conflict_resolutions)
                    self.log(f"✅ Conflict resolutions: {resolutions_count}")
                
                # Check conclusions generation
                if hasattr(result, 'main_conclusions') and result.main_conclusions:
                    test_results["conclusions_generation"] = True
                    conclusions_count = len(result.main_conclusions)
                    self.log(f"✅ Main conclusions generated: {conclusions_count}")
                
                # Check methodology assessment
                if hasattr(result, 'methodology_assessment') and result.methodology_assessment:
                    test_results["methodology_assessment"] = True
                    overall_score = result.methodology_assessment.get('overall_score', 0)
                    self.log(f"✅ Methodology assessment: {overall_score:.3f}")
            
        except Exception as e:
            test_results["errors"].append(f"Full synthesis error: {str(e)}")
            self.log(f"❌ Full synthesis failed: {e}", "ERROR")
        
        return test_results
    
    async def test_service_health(self) -> Dict[str, Any]:
        """Test service health and status functionality"""
        self.log("🔍 Testing service health...")
        
        test_results = {
            "test_name": "service_health",
            "health_check": False,
            "cache_status": False,
            "configuration": False,
            "errors": []
        }
        
        try:
            # Test health status
            health_status = await self.service.get_synthesis_health_status()
            
            if health_status and "service_name" in health_status:
                test_results["health_check"] = True
                status = health_status.get('status', 'unknown')
                self.log(f"✅ Health check successful: {status}")
            
            # Test cache information
            if hasattr(self.service, 'synthesis_cache'):
                test_results["cache_status"] = True
                cache_size = len(self.service.synthesis_cache)
                max_size = self.service.cache_size
                self.log(f"✅ Cache status: {cache_size}/{max_size}")
            
            # Test configuration info
            if health_status and "supported_domains" in health_status:
                test_results["configuration"] = True
                domains_count = len(health_status["supported_domains"])
                self.log(f"✅ Configuration loaded: {domains_count} domains supported")
            
        except Exception as e:
            test_results["errors"].append(f"Service health error: {str(e)}")
            self.log(f"❌ Service health check failed: {e}", "ERROR")
        
        return test_results
    
    def print_test_summary(self, all_results: Dict[str, Dict[str, Any]]):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🚀 ADVANCED EVIDENCE SYNTHESIS - TEST RESULTS SUMMARY")
        print("="*80)
        
        total_tests = 0
        total_passed = 0
        
        for test_category, test_results in all_results.items():
            print(f"\n📋 {test_results['test_name'].replace('_', ' ').title()}:")
            print("-" * 50)
            
            # Count tests for this category
            category_tests = [k for k in test_results.keys() if k not in ['test_name', 'errors']]
            category_passed = sum(1 for k in category_tests if test_results[k])
            
            total_tests += len(category_tests)
            total_passed += category_passed
            
            # Print individual test results
            for test_name in category_tests:
                status = "✅ PASS" if test_results[test_name] else "❌ FAIL"
                print(f"  {test_name.replace('_', ' '):<25} {status}")
            
            # Print errors if any
            if test_results['errors']:
                print(f"\n  🔍 Errors encountered:")
                for error in test_results['errors'][:2]:  # Show first 2 errors
                    print(f"    • {error}")
                if len(test_results['errors']) > 2:
                    print(f"    ... and {len(test_results['errors']) - 2} more errors")
            
            # Category summary
            success_rate = (category_passed / len(category_tests)) * 100 if category_tests else 0
            print(f"\n  📊 Category Summary: {category_passed}/{len(category_tests)} tests passed ({success_rate:.1f}%)")
        
        # Overall summary
        print("\n" + "="*80)
        overall_success_rate = (total_passed / total_tests) * 100 if total_tests else 0
        print(f"🎯 OVERALL RESULTS: {total_passed}/{total_tests} tests passed ({overall_success_rate:.1f}%)")
        
        if overall_success_rate >= 90:
            print("🎉 EXCELLENT: Evidence synthesis system working perfectly!")
        elif overall_success_rate >= 75:
            print("✅ GOOD: Evidence synthesis system functioning well")
        elif overall_success_rate >= 60:
            print("⚠️  PARTIAL: Some evidence synthesis features need attention")
        else:
            print("❌ CRITICAL: Major issues with evidence synthesis system")
        
        print("="*80)
        
        return overall_success_rate
    
    async def run_all_tests(self) -> Dict[str, Dict[str, Any]]:
        """Run all evidence synthesis tests"""
        self.log("🔬 Starting Advanced Evidence Synthesis Test Suite...")
        
        results = {}
        
        # Test sequence
        test_functions = [
            ("service_setup", self.setup_service),
            ("evidence_clustering", self.test_evidence_clustering),
            ("cluster_analysis", self.test_cluster_analysis),
            ("full_synthesis", self.test_full_synthesis),
            ("service_health", self.test_service_health)
        ]
        
        for test_name, test_func in test_functions:
            try:
                self.log(f"Running {test_name}...")
                results[test_name] = await test_func()
            except Exception as e:
                self.log(f"Critical error in {test_name}: {e}", "ERROR")
                results[test_name] = {
                    "test_name": test_name,
                    "errors": [f"Critical test failure: {str(e)}"]
                }
        
        return results

async def main():
    """Main test execution"""
    parser = argparse.ArgumentParser(description="Test Advanced Evidence Synthesis Service")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Initialize test suite
    test_suite = EvidenceSynthesisTestSuite(verbose=args.verbose)
    
    try:
        # Run all tests
        results = await test_suite.run_all_tests()
        
        # Print summary and determine exit code
        success_rate = test_suite.print_test_summary(results)
        
        if success_rate >= 80:
            sys.exit(0)  # Success
        elif success_rate >= 60:
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
