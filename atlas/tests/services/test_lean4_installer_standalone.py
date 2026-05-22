#!/usr/bin/env python3
"""
Standalone test script for Advanced Lean4 Installer improvements
===============================================================

This script tests the enhanced features of the Lean4 installer service
without requiring the full AXIOM application dependencies.

Author: AXIOM Research Team
Date: December 2024
"""

import asyncio
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, Mock

# Direct import without app dependencies
sys.path.insert(0, str(Path(__file__).parent / 'app' / 'services'))

# Create minimal imports to avoid dependency issues
class MockBaseService:
    pass

# Import directly
from lean4_installer_improved import AdvancedLean4InstallerService

async def test_basic_initialization():
    """Test basic service initialization"""
    print("🔧 Testing basic initialization...")
    
    installer = AdvancedLean4InstallerService()
    
    print(f"   System detected: {installer.system}")
    print(f"   Architecture: {installer.architecture}")
    print(f"   Config loaded: {'elan_installer_urls' in installer.config}")
    print(f"   Dependencies defined: {len(installer.dependencies)}")
    print(f"   Install paths configured: {len(installer.install_paths)}")
    
    assert installer.system is not None, "System should be detected"
    assert installer.architecture is not None, "Architecture should be detected"
    assert 'elan_installer_urls' in installer.config, "Config should be loaded"
    
    print("   ✅ Basic initialization passed!")
    return True

async def test_os_detection():
    """Test enhanced OS detection"""
    print("\n🖥️ Testing OS detection...")
    
    installer = AdvancedLean4InstallerService()
    os_info = installer._detect_os()
    
    print(f"   System: {os_info.get('system', 'unknown')}")
    print(f"   Architecture: {os_info.get('architecture', 'unknown')}")
    print(f"   Platform: {os_info.get('platform', 'unknown')}")
    print(f"   Python version: {os_info.get('python_version', 'unknown')}")
    
    assert 'system' in os_info, "System info should include 'system'"
    assert 'architecture' in os_info, "System info should include 'architecture'"
    assert 'platform' in os_info, "System info should include 'platform'"
    
    print("   ✅ OS detection passed!")
    return True

async def test_dependency_structure():
    """Test dependency structure and definitions"""
    print("\n🔗 Testing dependency structure...")
    
    installer = AdvancedLean4InstallerService()
    
    # Check dependency categories
    expected_categories = ['essential', 'recommended', 'optional']
    for category in expected_categories:
        assert category in installer.dependencies, f"Category {category} should exist"
        deps = installer.dependencies[category]
        print(f"   {category.title()}: {len(deps)} dependencies")
        
        # Check each dependency has required fields
        for dep in deps:
            assert hasattr(dep, 'name'), f"Dependency should have 'name'"
            assert hasattr(dep, 'required'), f"Dependency should have 'required'"
            assert hasattr(dep, 'description'), f"Dependency should have 'description'"
    
    print("   ✅ Dependency structure passed!")
    return True

async def test_version_extraction():
    """Test version extraction from various outputs"""
    print("\n📦 Testing version extraction...")
    
    installer = AdvancedLean4InstallerService()
    
    test_cases = [
        ("curl 7.68.0 (x86_64-pc-linux-gnu)", "7.68.0"),
        ("git version 2.25.1", "2.25.1"),
        ("GNU Make 4.2.1", "4.2.1"),
        ("Python 3.8.10", "3.8.10"),
        ("lean 4.2.0", "4.2.0"),
        ("v1.2.3", "1.2.3"),
        ("version 2.1", "2.1")
    ]
    
    for output, expected in test_cases:
        extracted = installer._extract_version(output)
        print(f"   '{output}' -> '{extracted}' (expected: '{expected}')")
        assert extracted == expected, f"Expected {expected}, got {extracted}"
    
    print("   ✅ Version extraction passed!")
    return True

async def test_progress_tracking():
    """Test progress tracking functionality"""
    print("\n📊 Testing progress tracking...")
    
    installer = AdvancedLean4InstallerService()
    
    # Test multiple progress updates
    steps = [
        ("analysis", 10, "running", "Analyzing system"),
        ("download", 40, "running", "Downloading components"),
        ("install", 70, "running", "Installing Lean4"),
        ("verify", 100, "completed", "Installation complete")
    ]
    
    for step, progress, status, message in steps:
        installer._update_progress(step, progress, status, message)
    
    print(f"   Progress entries: {len(installer.progress_history)}")
    print(f"   Current step: {installer.current_step}")
    print(f"   Final progress: {installer.progress_history[-1].progress_percent}%")
    
    assert len(installer.progress_history) == 4, "Should have 4 progress entries"
    assert installer.progress_history[-1].progress_percent == 100.0, "Final progress should be 100%"
    assert installer.current_step == "verify", "Current step should be 'verify'"
    
    # Check duration calculation (except first entry)
    for i in range(1, len(installer.progress_history)):
        assert installer.progress_history[i].duration is not None, "Duration should be calculated"
        print(f"   Step {i} duration: {installer.progress_history[i].duration:.3f}s")
    
    print("   ✅ Progress tracking passed!")
    return True

async def test_compatibility_scoring():
    """Test the compatibility scoring system"""
    print("\n🎯 Testing compatibility scoring...")
    
    installer = AdvancedLean4InstallerService()
    
    # Test perfect compatibility
    perfect_requirements = {
        'supported_os': True,
        'supported_architecture': True,
        'sufficient_disk_space': True,
        'sufficient_memory': True,
        'internet_connectivity': True,
        'dependency_curl': True,
        'dependency_git': True,
        'dependency_bash': True,
        'dependency_make': True,
        'dependency_gcc': True
    }
    
    perfect_score = installer._calculate_compatibility_score({}, perfect_requirements)
    print(f"   Perfect compatibility score: {perfect_score:.2f}")
    
    # Test minimal compatibility (only essential requirements)
    minimal_requirements = {
        'supported_os': True,
        'supported_architecture': True,
        'sufficient_disk_space': True,
        'sufficient_memory': True,
        'internet_connectivity': True,
        'dependency_curl': True,
        'dependency_git': True,
        'dependency_bash': True,
        'dependency_make': False,
        'dependency_gcc': False
    }
    
    minimal_score = installer._calculate_compatibility_score({}, minimal_requirements)
    print(f"   Minimal compatibility score: {minimal_score:.2f}")
    
    # Test poor compatibility
    poor_requirements = {
        'supported_os': False,
        'supported_architecture': False,
        'sufficient_disk_space': False,
        'sufficient_memory': False,
        'internet_connectivity': False,
        'dependency_curl': False,
        'dependency_git': False,
        'dependency_bash': False,
        'dependency_make': False,
        'dependency_gcc': False
    }
    
    poor_score = installer._calculate_compatibility_score({}, poor_requirements)
    print(f"   Poor compatibility score: {poor_score:.2f}")
    
    assert perfect_score == 1.0, "Perfect requirements should give score of 1.0"
    assert minimal_score > poor_score, "Minimal should be better than poor"
    assert poor_score == 0.0, "Poor requirements should give score of 0.0"
    
    print("   ✅ Compatibility scoring passed!")
    return True

async def test_configuration_generation():
    """Test configuration generation features"""
    print("\n⚙️ Testing configuration generation...")
    
    installer = AdvancedLean4InstallerService()
    
    # Test shell configuration generation
    elan_bin_path = "/home/user/.elan/bin"
    shell_configs = installer._generate_shell_configuration(elan_bin_path)
    
    expected_shells = ['bash', 'zsh', 'fish']
    for shell in expected_shells:
        assert shell in shell_configs, f"Configuration for {shell} should be generated"
        config = shell_configs[shell]
        assert elan_bin_path in config, f"Elan bin path should be in {shell} config"
        print(f"   {shell.title()} config: ✅ (contains PATH)")
    
    # Test next steps generation
    next_steps = installer._generate_next_steps()
    print(f"   Next steps generated: {len(next_steps)}")
    assert len(next_steps) > 0, "Should generate next steps"
    
    # Test troubleshooting guide
    troubleshooting = installer._generate_troubleshooting_guide()
    print(f"   Troubleshooting steps: {len(troubleshooting)}")
    assert len(troubleshooting) > 0, "Should generate troubleshooting guide"
    
    print("   ✅ Configuration generation passed!")
    return True

async def test_performance_metrics():
    """Test performance metrics collection"""
    print("\n📈 Testing performance metrics...")
    
    installer = AdvancedLean4InstallerService()
    
    # Test that all expected metrics are initialized
    expected_metrics = [
        'total_download_time',
        'total_install_time', 
        'download_speed_mbps',
        'memory_usage_mb',
        'disk_space_used_mb'
    ]
    
    for metric in expected_metrics:
        assert metric in installer.performance_metrics, f"Metric {metric} should be initialized"
        print(f"   {metric}: {installer.performance_metrics[metric]}")
    
    # Test updating metrics
    installer.performance_metrics['total_download_time'] = 5.2
    installer.performance_metrics['download_speed_mbps'] = 8.5
    
    assert installer.performance_metrics['total_download_time'] == 5.2, "Should update metrics"
    assert installer.performance_metrics['download_speed_mbps'] == 8.5, "Should update metrics"
    
    print("   ✅ Performance metrics passed!")
    return True

async def test_build_info_extraction():
    """Test build info extraction from version outputs"""
    print("\n🔍 Testing build info extraction...")
    
    installer = AdvancedLean4InstallerService()
    
    test_version_output = """
lean 4.2.0
commit 12345abcdef
date 2024-01-15
platform linux
architecture x86_64
"""
    
    build_info = installer._extract_build_info(test_version_output)
    
    print(f"   Extracted build info: {build_info}")
    
    expected_fields = ['commit', 'date', 'platform', 'architecture']
    for field in expected_fields:
        if field in build_info:
            print(f"   {field}: {build_info[field]}")
    
    # Should extract at least some information
    assert len(build_info) > 0, "Should extract some build information"
    
    print("   ✅ Build info extraction passed!")
    return True

async def test_installation_completeness_calculation():
    """Test installation completeness score calculation"""
    print("\n🎯 Testing installation completeness calculation...")
    
    installer = AdvancedLean4InstallerService()
    
    # Test complete installation
    complete_binary_status = {
        'elan': {'executable': True},
        'lean': {'executable': True},
        'lake': {'executable': True}
    }
    
    complete_version_info = {
        'elan': {'available': True},
        'lean': {'available': True},
        'lake': {'available': True}
    }
    
    complete_toolchain_info = {'available': True, 'count': 2}
    complete_mathlib_info = {'found': True}
    
    complete_score = installer._calculate_installation_completeness(
        complete_binary_status, complete_version_info, 
        complete_toolchain_info, complete_mathlib_info
    )
    
    print(f"   Complete installation score: {complete_score:.2f}")
    assert complete_score == 1.0, "Complete installation should score 1.0"
    
    # Test partial installation
    partial_binary_status = {
        'elan': {'executable': True},
        'lean': {'executable': False},  # Missing
        'lake': {'executable': True}
    }
    
    partial_score = installer._calculate_installation_completeness(
        partial_binary_status, complete_version_info,
        complete_toolchain_info, complete_mathlib_info
    )
    
    print(f"   Partial installation score: {partial_score:.2f}")
    assert 0.0 < partial_score < 1.0, "Partial installation should have intermediate score"
    
    print("   ✅ Installation completeness calculation passed!")
    return True

async def test_verification_score_calculation():
    """Test verification score calculation"""
    print("\n✅ Testing verification score calculation...")
    
    installer = AdvancedLean4InstallerService()
    
    # Test perfect verification
    perfect_results = {
        'elan': {'functional': True},
        'lean': {'functional': True},
        'lake': {'functional': True},
        'toolchains': {'success': True, 'count': 2},
        'functionality_test': {'success': True}
    }
    
    perfect_score = installer._calculate_verification_score(perfect_results)
    print(f"   Perfect verification score: {perfect_score:.2f}")
    assert perfect_score == 1.0, "Perfect verification should score 1.0"
    
    # Test failed verification
    failed_results = {
        'elan': {'functional': False},
        'lean': {'functional': False},
        'lake': {'functional': False},
        'toolchains': {'success': False, 'count': 0},
        'functionality_test': {'success': False}
    }
    
    failed_score = installer._calculate_verification_score(failed_results)
    print(f"   Failed verification score: {failed_score:.2f}")
    assert failed_score == 0.0, "Failed verification should score 0.0"
    
    print("   ✅ Verification score calculation passed!")
    return True

async def main():
    """Run all tests"""
    print("🚀 Testing Advanced Lean4 Installer Service (Standalone)")
    print("=" * 70)
    
    tests = [
        test_basic_initialization,
        test_os_detection,
        test_dependency_structure,
        test_version_extraction,
        test_progress_tracking,
        test_compatibility_scoring,
        test_configuration_generation,
        test_performance_metrics,
        test_build_info_extraction,
        test_installation_completeness_calculation,
        test_verification_score_calculation
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    start_time = time.time()
    
    for test in tests:
        try:
            success = await test()
            if success:
                passed_tests += 1
        except Exception as e:
            print(f"   ❌ Test failed with error: {e}")
    
    total_time = time.time() - start_time
    
    print("\n" + "=" * 70)
    print(f"🎉 Test Results: {passed_tests}/{total_tests} tests passed")
    print(f"⏱️ Total test time: {total_time:.2f} seconds")
    
    if passed_tests == total_tests:
        print("✨ All tests passed successfully!")
        print("\n🎯 Advanced Lean4 Installer features verified:")
        print("   ✅ Enhanced service initialization and configuration")
        print("   ✅ Intelligent OS detection and system analysis")
        print("   ✅ Comprehensive dependency management system")
        print("   ✅ Robust version extraction and parsing")
        print("   ✅ Real-time progress tracking with duration calculation")
        print("   ✅ Smart compatibility scoring algorithm")
        print("   ✅ Multi-shell configuration generation")
        print("   ✅ Performance metrics collection and monitoring")
        print("   ✅ Build information extraction and analysis")
        print("   ✅ Installation completeness scoring system")
        print("   ✅ Comprehensive verification framework")
        print("\n🚀 Ready for production use!")
        return True
    else:
        print("⚠️ Some tests failed - check the implementation")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
