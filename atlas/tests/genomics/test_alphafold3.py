#!/usr/bin/env python3
"""
Test script for AlphaFold 3 Protein Structure Service
Validates protein structure prediction, binding site analysis, and interaction modeling
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.alphafold3_service import AlphaFold3ProteinStructureService


async def test_structure_prediction():
    """
    Test protein structure prediction functionality
    """
    print("🧬 Test 1: Protein Structure Prediction")
    print("-" * 50)
    
    try:
        service = AlphaFold3ProteinStructureService()
        
        # Test with a small protein sequence
        test_sequence = "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
        
        print(f"📝 Test sequence: {test_sequence[:30]}... ({len(test_sequence)} residues)")
        print("🔄 Predicting structure...")
        
        result = await service.predict_protein_structure(test_sequence)
        
        if result.get('success'):
            data = result['data']
            structure = data['structure']
            quality = data['quality_assessment']
            
            print("✅ Structure prediction successful")
            print(f"🆔 Structure ID: {structure['structure_id']}")
            print(f"🎯 Overall confidence: {structure['prediction_confidence']:.3f}")
            print(f"📊 High confidence residues: {quality['high_confidence_residues']}")
            print(f"📊 Medium confidence residues: {quality['medium_confidence_residues']}")
            print(f"📊 Low confidence residues: {quality['low_confidence_residues']}")
            
            return structure['structure_id']
        else:
            print(f"❌ Structure prediction failed: {result.get('error')}")
            return None
            
    except Exception as e:
        print(f"❌ Structure prediction test failed: {e}")
        return None


async def test_binding_site_analysis(structure_id: str):
    """
    Test binding site analysis functionality
    """
    print("\n🔍 Test 2: Binding Site Analysis")
    print("-" * 50)
    
    try:
        service = AlphaFold3ProteinStructureService()
        
        print(f"🆔 Analyzing structure: {structure_id}")
        print("🔄 Detecting binding sites...")
        
        result = await service.analyze_binding_sites(structure_id)
        
        if result.get('success'):
            data = result['data']
            sites = data['binding_sites']
            summary = data['analysis_summary']
            
            print("✅ Binding site analysis successful")
            print(f"🎯 Total sites found: {summary['total_sites_found']}")
            print(f"🏆 High confidence sites: {summary['high_confidence_sites']}")
            print(f"💊 Druggable sites: {summary['druggable_sites']}")
            
            print("\n📋 Binding sites details:")
            for i, site in enumerate(sites[:3]):  # Show top 3 sites
                print(f"  Site {i+1}: {site['site_id']}")
                print(f"    Confidence: {site['confidence']:.3f}")
                print(f"    Volume: {site['cavity_volume']:.1f} Ų")
                print(f"    Druggability: {site['druggability_score']:.3f}")
            
            return True
        else:
            print(f"❌ Binding site analysis failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Binding site analysis test failed: {e}")
        return False


async def test_protein_interaction():
    """
    Test protein-protein interaction prediction
    """
    print("\n🤝 Test 3: Protein-Protein Interaction")
    print("-" * 50)
    
    try:
        service = AlphaFold3ProteinStructureService()
        
        # Two test protein sequences
        seq_a = "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
        seq_b = "MSIIGATRLQNDKSDTYSAGPCYAGGCSAFTPRGTCGKDWDLGEQTCASGFCTSQPLCARIKKT"
        
        print(f"🧬 Protein A: {seq_a[:25]}... ({len(seq_a)} residues)")
        print(f"🧬 Protein B: {seq_b[:25]}... ({len(seq_b)} residues)")
        print("🔄 Predicting interaction...")
        
        result = await service.predict_protein_interaction(seq_a, seq_b)
        
        if result.get('success'):
            data = result['data']
            interaction = data['interaction']
            quality = data['prediction_quality']
            
            print("✅ Protein interaction prediction successful")
            print(f"🎯 Interaction confidence: {interaction['interaction_confidence']:.3f}")
            print(f"📊 Confidence level: {quality['confidence_level']}")
            print(f"🔗 Interaction type: {interaction['interaction_type']}")
            print(f"🧩 Interface residues: {quality['interface_size']}")
            
            return True
        else:
            print(f"❌ Protein interaction prediction failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Protein interaction test failed: {e}")
        return False


async def test_quality_metrics(structure_id: str):
    """
    Test structure quality assessment
    """
    print("\n📊 Test 4: Structure Quality Metrics")
    print("-" * 50)
    
    try:
        service = AlphaFold3ProteinStructureService()
        
        print(f"🆔 Assessing quality for: {structure_id}")
        
        result = await service.get_structure_quality_metrics(structure_id)
        
        if result.get('success'):
            metrics = result['data']
            
            print("✅ Quality assessment successful")
            print(f"🎯 Overall confidence: {metrics['overall_confidence']:.3f}")
            print(f"📈 pLDDT mean: {metrics['plddt_distribution']['mean']:.2f}")
            print(f"📊 pLDDT range: {metrics['plddt_distribution']['min']:.1f} - {metrics['plddt_distribution']['max']:.1f}")
            
            regions = metrics['confidence_regions']
            print(f"\n🌈 Confidence regions:")
            print(f"  Very high (>90): {regions['very_high']} residues")
            print(f"  High (80-90): {regions['high']} residues") 
            print(f"  Medium (60-80): {regions['medium']} residues")
            print(f"  Low (<60): {regions['low']} residues")
            
            assessment = metrics['structural_assessment']
            print(f"\n🔬 Structural assessment:")
            print(f"  Reliable domains: {assessment['reliable_domains']*100:.1f}%")
            print(f"  Disorder regions: {assessment['disorder_regions']*100:.1f}%")
            
            return True
        else:
            print(f"❌ Quality assessment failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Quality metrics test failed: {e}")
        return False


async def test_validation_errors():
    """
    Test input validation and error handling
    """
    print("\n⚠️  Test 5: Input Validation")
    print("-" * 50)
    
    try:
        service = AlphaFold3ProteinStructureService()
        
        # Test invalid sequences
        test_cases = [
            ("", "Empty sequence"),
            ("INVALID", "Too short sequence"), 
            ("MKTVRQXRLKSIVRILERSKEPVSG", "Invalid amino acid (X)"),
            ("M" * 3000, "Sequence too long")
        ]
        
        validation_passed = 0
        
        for test_seq, description in test_cases:
            result = await service.predict_protein_structure(test_seq)
            if not result.get('success'):
                print(f"✅ {description}: Correctly rejected")
                validation_passed += 1
            else:
                print(f"❌ {description}: Should have been rejected")
        
        print(f"\n📊 Validation tests: {validation_passed}/{len(test_cases)} passed")
        return validation_passed == len(test_cases)
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return False


async def test_health_check():
    """
    Test service health check
    """
    print("\n🏥 Test 6: Service Health Check")
    print("-" * 50)
    
    try:
        service = AlphaFold3ProteinStructureService()
        
        health_result = await service.health_check()
        
        status = health_result.get('service_status', 'unknown')
        print(f"🏥 Service status: {status}")
        print(f"📦 Service version: {health_result.get('version', 'unknown')}")
        print(f"🔗 API status: {health_result.get('api_status', 'unknown')}")
        print(f"💾 Cache entries: {health_result.get('cache_entries', 0)}")
        
        features = health_result.get('supported_features', [])
        print(f"⚙️  Supported features: {', '.join(features)}")
        
        return status == 'healthy'
        
    except Exception as e:
        print(f"❌ Health check test failed: {e}")
        return False


async def main():
    """
    Run all AlphaFold 3 service tests
    """
    print("=" * 70)
    print("🧬 AlphaFold 3 Protein Structure Service Test Suite")
    print("=" * 70)
    print(f"⏰ Test started at: {datetime.now().isoformat()}")
    print()
    
    try:
        # Test 1: Structure prediction
        structure_id = await test_structure_prediction()
        test1_passed = structure_id is not None
        
        # Test 2: Binding site analysis (requires structure_id)
        test2_passed = False
        if structure_id:
            test2_passed = await test_binding_site_analysis(structure_id)
        else:
            print("\n⚠️  Skipping binding site analysis (no structure ID)")
        
        # Test 3: Protein interaction
        test3_passed = await test_protein_interaction()
        
        # Test 4: Quality metrics (requires structure_id)
        test4_passed = False
        if structure_id:
            test4_passed = await test_quality_metrics(structure_id)
        else:
            print("\n⚠️  Skipping quality metrics (no structure ID)")
        
        # Test 5: Input validation
        test5_passed = await test_validation_errors()
        
        # Test 6: Health check
        test6_passed = await test_health_check()
        
        # Summary
        tests_passed = sum([test1_passed, test2_passed, test3_passed, 
                           test4_passed, test5_passed, test6_passed])
        total_tests = 6
        
        print("\n" + "=" * 70)
        print("📊 Test Results Summary")
        print("=" * 70)
        print(f"✅ Structure Prediction: {'PASSED' if test1_passed else 'FAILED'}")
        print(f"✅ Binding Site Analysis: {'PASSED' if test2_passed else 'FAILED'}")
        print(f"✅ Protein Interaction: {'PASSED' if test3_passed else 'FAILED'}")
        print(f"✅ Quality Metrics: {'PASSED' if test4_passed else 'FAILED'}")
        print(f"✅ Input Validation: {'PASSED' if test5_passed else 'FAILED'}")
        print(f"✅ Health Check: {'PASSED' if test6_passed else 'FAILED'}")
        print(f"\n🎯 Overall: {tests_passed}/{total_tests} tests passed")
        
        if tests_passed == total_tests:
            print("🎉 All AlphaFold 3 service tests passed!")
            print("🔬 Protein structure prediction service is ready for use")
            print("💊 Drug discovery and structural biology capabilities validated")
            return True
        else:
            print("❌ Some tests failed. Please check the implementation.")
            return False
            
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
