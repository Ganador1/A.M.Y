#!/usr/bin/env python3
"""
Simplified test script for specialized scientific models integration
Tests basic functionality without heavy model loading

Usage:
    python test_specialized_models_simple.py
"""

import asyncio
import sys
import traceback
from datetime import datetime
from typing import Dict, Any

def log_message(message: str, level: str = "INFO"):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def test_service_imports():
    """Test that all specialized services can be imported"""
    results = {
        "biogpt": False,
        "clinicalbert": False, 
        "matscibert": False,
        "scibert": False,
        "errors": []
    }
    
    # Test BioGPT import
    try:
        from app.services.biogpt_service import BioGPTService
        results["biogpt"] = True
        log_message("✅ BioGPT service import successful")
    except Exception as e:
        results["errors"].append(f"BioGPT import failed: {str(e)}")
        log_message(f"❌ BioGPT service import failed: {e}", "ERROR")
    
    # Test ClinicalBERT import  
    try:
        from app.services.clinicalbert_service import ClinicalBERTService
        results["clinicalbert"] = True
        log_message("✅ ClinicalBERT service import successful")
    except Exception as e:
        results["errors"].append(f"ClinicalBERT import failed: {str(e)}")
        log_message(f"❌ ClinicalBERT service import failed: {e}", "ERROR")
    
    # Test MatSciBERT import
    try:
        from app.services.matscibert_service import MatSciBERTService  
        results["matscibert"] = True
        log_message("✅ MatSciBERT service import successful")
    except Exception as e:
        results["errors"].append(f"MatSciBERT import failed: {str(e)}")
        log_message(f"❌ MatSciBERT service import failed: {e}", "ERROR")
    
    # Test SciBERT import
    try:
        from app.services.scibert_service import SciBERTService
        results["scibert"] = True  
        log_message("✅ SciBERT service import successful")
    except Exception as e:
        results["errors"].append(f"SciBERT import failed: {str(e)}")
        log_message(f"❌ SciBERT service import failed: {e}", "ERROR")
    
    return results

def test_router_imports():
    """Test that all router modules can be imported"""
    results = {
        "biogpt_router": False,
        "clinicalbert_router": False,
        "matscibert_router": False, 
        "scibert_router": False,
        "errors": []
    }
    
    # Test BioGPT router
    try:
        from app.routers.biogpt import router as biogpt_router
        results["biogpt_router"] = True
        log_message("✅ BioGPT router import successful")
    except Exception as e:
        results["errors"].append(f"BioGPT router import failed: {str(e)}")
        log_message(f"❌ BioGPT router import failed: {e}", "ERROR")
    
    # Test ClinicalBERT router
    try:
        from app.routers.clinicalbert import router as clinicalbert_router  
        results["clinicalbert_router"] = True
        log_message("✅ ClinicalBERT router import successful")
    except Exception as e:
        results["errors"].append(f"ClinicalBERT router import failed: {str(e)}")
        log_message(f"❌ ClinicalBERT router import failed: {e}", "ERROR")
    
    # Test MatSciBERT router
    try:
        from app.routers.matscibert import router as matscibert_router
        results["matscibert_router"] = True
        log_message("✅ MatSciBERT router import successful") 
    except Exception as e:
        results["errors"].append(f"MatSciBERT router import failed: {str(e)}")
        log_message(f"❌ MatSciBERT router import failed: {e}", "ERROR")
        
    # Test SciBERT router  
    try:
        from app.routers.scibert import router as scibert_router
        results["scibert_router"] = True
        log_message("✅ SciBERT router import successful")
    except Exception as e:
        results["errors"].append(f"SciBERT router import failed: {str(e)}")
        log_message(f"❌ SciBERT router import failed: {e}", "ERROR")
    
    return results

def test_main_app_integration():
    """Test that main.py can be imported with new routers"""
    try:
        # Check if main.py can be imported
        import main
        log_message("✅ Main application import successful")
        
        # Check if FastAPI app is properly configured
        if hasattr(main, 'app'):
            log_message("✅ FastAPI app instance found")
            
            # Check registered routes
            routes = [route.path for route in main.app.routes]
            specialized_routes = [r for r in routes if any(prefix in r for prefix in ['/api/biogpt', '/api/clinicalbert', '/api/matscibert', '/api/scibert'])]
            
            if specialized_routes:
                log_message(f"✅ Found {len(specialized_routes)} specialized model routes")
                return True
            else:
                log_message("⚠️  No specialized model routes found", "WARNING")
                return False
        else:
            log_message("❌ FastAPI app instance not found", "ERROR")
            return False
            
    except Exception as e:
        log_message(f"❌ Main application import failed: {e}", "ERROR")
        return False

def test_file_structure():
    """Test that all required files exist"""
    import os
    
    required_files = [
        "app/services/biogpt_service.py",
        "app/services/clinicalbert_service.py", 
        "app/services/matscibert_service.py",
        "app/services/scibert_service.py",
        "app/routers/biogpt.py",
        "app/routers/clinicalbert.py",
        "app/routers/matscibert.py", 
        "app/routers/scibert.py"
    ]
    
    results = {
        "files_exist": 0,
        "total_files": len(required_files),
        "missing_files": []
    }
    
    for file_path in required_files:
        if os.path.exists(file_path):
            results["files_exist"] += 1
            log_message(f"✅ File exists: {file_path}")
        else:
            results["missing_files"].append(file_path)
            log_message(f"❌ File missing: {file_path}", "ERROR")
    
    return results

def print_test_summary(service_results, router_results, main_results, file_results):
    """Print comprehensive test summary"""
    print("\n" + "="*80)
    print("🚀 SPECIALIZED SCIENTIFIC MODELS - INTEGRATION TEST SUMMARY")
    print("="*80)
    
    # Service imports summary
    service_passed = sum(1 for v in service_results.values() if isinstance(v, bool) and v)
    service_total = len([k for k in service_results.keys() if k != 'errors'])
    
    print(f"\n📋 Service Imports: {service_passed}/{service_total} successful")
    for service, success in service_results.items():
        if service != 'errors':
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {service:<20} {status}")
    
    # Router imports summary  
    router_passed = sum(1 for v in router_results.values() if isinstance(v, bool) and v)
    router_total = len([k for k in router_results.keys() if k != 'errors'])
    
    print(f"\n🌐 Router Imports: {router_passed}/{router_total} successful")
    for router, success in router_results.items():
        if router != 'errors':
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {router:<25} {status}")
    
    # File structure summary
    print(f"\n📁 File Structure: {file_results['files_exist']}/{file_results['total_files']} files present")
    if file_results['missing_files']:
        print("  Missing files:")
        for missing_file in file_results['missing_files']:
            print(f"    ❌ {missing_file}")
    
    # Main app integration
    main_status = "✅ PASS" if main_results else "❌ FAIL"
    print(f"\n🚀 Main App Integration: {main_status}")
    
    # Overall summary
    total_checks = service_total + router_total + file_results['total_files'] + 1  # +1 for main app
    total_passed = service_passed + router_passed + file_results['files_exist'] + (1 if main_results else 0)
    
    print("\n" + "="*80)
    overall_success_rate = (total_passed / total_checks) * 100
    print(f"🎯 OVERALL RESULTS: {total_passed}/{total_checks} checks passed ({overall_success_rate:.1f}%)")
    
    if overall_success_rate >= 90:
        print("🎉 EXCELLENT: Specialized models integration highly successful!")
        return 0
    elif overall_success_rate >= 75:  
        print("✅ GOOD: Most specialized models integrated properly")
        return 0
    elif overall_success_rate >= 50:
        print("⚠️  PARTIAL: Some integration issues need attention")
        return 1
    else:
        print("❌ CRITICAL: Major integration problems detected")
        return 2

def main():
    """Main test execution"""
    log_message("🔬 Starting Specialized Scientific Models Integration Test...")
    
    try:
        # Test file structure first
        log_message("📁 Testing file structure...")
        file_results = test_file_structure()
        
        # Test service imports
        log_message("🧬 Testing service imports...")
        service_results = test_service_imports()
        
        # Test router imports
        log_message("🌐 Testing router imports...")
        router_results = test_router_imports()
        
        # Test main app integration
        log_message("🚀 Testing main application integration...")
        main_results = test_main_app_integration()
        
        # Print summary and determine exit code
        exit_code = print_test_summary(service_results, router_results, main_results, file_results)
        
        print("="*80)
        sys.exit(exit_code)
        
    except Exception as e:
        log_message(f"❌ CRITICAL ERROR: Test execution failed: {e}", "ERROR")
        traceback.print_exc()
        sys.exit(3)

if __name__ == "__main__":
    main()
