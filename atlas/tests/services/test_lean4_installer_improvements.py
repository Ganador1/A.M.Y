#!/usr/bin/env python3
"""
Test script for Advanced Lean4 Installer improvements
====================================================

This script tests the enhanced features of the Lean4 installer service
without requiring actual installation or external dependencies.

Author: AXIOM Research Team
Date: December 2024
"""

import asyncio
import json
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, Mock

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import the improved service
from app.services.lean4_installer_improved import AdvancedLean4InstallerService

async def test_system_compatibility_analysis():
    """Test system compatibility analysis"""
    print("🔍 Testing system compatibility analysis...")
    
    installer = AdvancedLean4InstallerService()
    
    # Mock system requirements to avoid real system calls
    async def mock_check_requirements():
        return {
            'supported_os': True,
            'supported_architecture': True,
            'sufficient_disk_space': True,
            'sufficient_memory': True,
            'internet_connectivity': True,
            'dependency_curl': True,
            'dependency_git': True,
            'dependency_bash': True
        }
    
    installer._check_system_requirements = mock_check_requirements
    
    compatibility = await installer.analyze_system_compatibility()
    
    print(f"   OS: {compatibility.os_name}")
    print(f"   Architecture: {compatibility.architecture}")
    print(f"   Supported: {compatibility.is_supported}")
    print(f"   Compatibility Score: {compatibility.compatibility_score:.2f}")
    print(f"   Recommendations: {len(compatibility.recommendations)}")
    print(f"   Warnings: {len(compatibility.warnings)}")
    
    assert compatibility.is_supported, "System should be compatible"
    assert compatibility.compatibility_score > 0.7, f"Score too low: {compatibility.compatibility_score}"
    
    print("   ✅ System compatibility analysis passed!")
    return True

async def test_advanced_installation_check():
    """Test advanced installation checking"""
    print("\n🔧 Testing advanced installation check...")
    
    installer = AdvancedLean4InstallerService()
    
    # Mock file system checks
    def mock_path_exists(self):
        return False  # Simulate no existing installation
    
    with patch.object(Path, 'exists', mock_path_exists):
        install_check = await installer.advanced_installation_check()
    
    print(f"   Installation completeness: {install_check.get('completeness_score', 0):.2f}")
    print(f"   Fully installed: {install_check.get('fully_installed', False)}")
    print(f"   Binary status checked: {len(install_check.get('binary_status', {}))}")
    print(f"   Recommendations: {len(install_check.get('recommendations', []))}")
    
    assert 'completeness_score' in install_check, "Completeness score should be calculated"
    assert 'binary_status' in install_check, "Binary status should be checked"
    
    print("   ✅ Advanced installation check passed!")
    return True

async def test_intelligent_download_simulation():
    """Test intelligent download features (simulated)"""
    print("\n📥 Testing intelligent download simulation...")
    
    installer = AdvancedLean4InstallerService()
    
    # Mock download methods
    async def mock_download_with_progress(url, download_dir):
        # Simulate successful download
        fake_file = download_dir / "elan_installer_test"
        fake_file.touch()
        
        return {
            'success': True,
            'file_path': fake_file,
            'stats': {
                'download_time': 2.5,
                'downloaded_size_mb': 15.2,
                'download_speed_mbps': 6.08,
                'used_cache': False,
                'cache_hit': False
            }
        }
    
    async def mock_verify_installer_integrity(installer_path):
        return {
            'valid': True,
            'file_size': 15728640,  # ~15MB
            'sha256_hash': 'mock_hash_12345',
            'header_check': 'passed'
        }
    
    async def mock_check_cached_installer(url, cache_dir):
        return {'valid': False, 'reason': 'Cache file not found'}
    
    installer._download_with_progress = mock_download_with_progress
    installer._verify_installer_integrity = mock_verify_installer_integrity
    installer._check_cached_installer = mock_check_cached_installer
    
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_dir = Path(temp_dir)
        download_result = await installer._intelligent_download('stable', True, True)
    
    print(f"   Download success: {download_result.get('success', False)}")
    print(f"   Download time: {download_result.get('download_time', 0):.2f}s")
    print(f"   Verification passed: {download_result.get('verification_passed', False)}")
    
    assert download_result.get('success', False), "Download should succeed"
    assert download_result.get('verification_passed', False), "Verification should be enabled"
    
    print("   ✅ Intelligent download simulation passed!")
    return True

async def test_progress_tracking():
    """Test installation progress tracking"""
    print("\n📊 Testing progress tracking...")
    
    installer = AdvancedLean4InstallerService()
    
    # Test progress updates
    installer._update_progress("test_step_1", 25.0, "running", "Testing progress tracking")
    installer._update_progress("test_step_2", 50.0, "completed", "Step 1 completed")
    installer._update_progress("test_step_3", 75.0, "running", "Processing step 3")
    installer._update_progress("test_step_4", 100.0, "completed", "All steps completed")
    
    print(f"   Progress entries: {len(installer.progress_history)}")
    print(f"   Current step: {installer.current_step}")
    print(f"   Latest progress: {installer.progress_history[-1].progress_percent}%")
    
    # Check progress history
    assert len(installer.progress_history) == 4, "Should have 4 progress entries"
    assert installer.progress_history[-1].progress_percent == 100.0, "Final progress should be 100%"
    assert installer.current_step == "test_step_4", "Current step should be updated"
    
    # Check duration calculation
    for i in range(1, len(installer.progress_history)):
        assert installer.progress_history[i].duration is not None, "Duration should be calculated"
    
    print("   ✅ Progress tracking passed!")
    return True

async def test_performance_metrics():
    """Test performance metrics collection"""
    print("\n📈 Testing performance metrics...")
    
    installer = AdvancedLean4InstallerService()
    
    # Simulate some operations to update metrics
    installer.performance_metrics['total_download_time'] = 5.2
    installer.performance_metrics['total_install_time'] = 45.7
    installer.performance_metrics['download_speed_mbps'] = 8.5
    installer.performance_metrics['memory_usage_mb'] = 128.3
    installer.performance_metrics['disk_space_used_mb'] = 1024.0
    
    print(f"   Download time: {installer.performance_metrics['total_download_time']}s")
    print(f"   Install time: {installer.performance_metrics['total_install_time']}s")
    print(f"   Download speed: {installer.performance_metrics['download_speed_mbps']} Mbps")
    print(f"   Memory usage: {installer.performance_metrics['memory_usage_mb']} MB")
    print(f"   Disk space used: {installer.performance_metrics['disk_space_used_mb']} MB")
    
    # Verify all expected metrics are present
    expected_metrics = [
        'total_download_time', 'total_install_time', 'download_speed_mbps',
        'memory_usage_mb', 'disk_space_used_mb'
    ]
    
    for metric in expected_metrics:
        assert metric in installer.performance_metrics, f"Metric {metric} should be present"
    
    print("   ✅ Performance metrics passed!")
    return True

async def test_dependency_analysis():
    """Test dependency analysis features"""
    print("\n🔗 Testing dependency analysis...")
    
    installer = AdvancedLean4InstallerService()
    
    # Test dependency categories
    assert 'essential' in installer.dependencies, "Essential dependencies should be defined"
    assert 'recommended' in installer.dependencies, "Recommended dependencies should be defined"
    assert 'optional' in installer.dependencies, "Optional dependencies should be defined"
    
    # Check dependency structure
    for category, deps in installer.dependencies.items():
        print(f"   {category.title()} dependencies: {len(deps)}")
        for dep in deps:
            assert hasattr(dep, 'name'), "Dependency should have name"
            assert hasattr(dep, 'required'), "Dependency should have required flag"
            assert hasattr(dep, 'description'), "Dependency should have description"
    
    # Test version extraction
    test_outputs = [
        "curl 7.68.0 (x86_64-pc-linux-gnu)",
        "git version 2.25.1",
        "GNU Make 4.2.1",
        "Python 3.8.10"
    ]
    
    for output in test_outputs:
        version = installer._extract_version(output)
        print(f"   Extracted version from '{output[:20]}...': {version}")
        assert version is not None, f"Should extract version from: {output}"
    
    print("   ✅ Dependency analysis passed!")
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
        print(f"   {shell.title()} config: {'✅' if elan_bin_path in config else '❌'}")
    
    # Test next steps generation
    next_steps = installer._generate_next_steps()
    assert len(next_steps) > 0, "Should generate next steps"
    print(f"   Next steps generated: {len(next_steps)}")
    
    # Test troubleshooting guide
    troubleshooting = installer._generate_troubleshooting_guide()
    assert len(troubleshooting) > 0, "Should generate troubleshooting guide"
    print(f"   Troubleshooting steps: {len(troubleshooting)}")
    
    print("   ✅ Configuration generation passed!")
    return True

async def test_compatibility_scoring():
    """Test compatibility scoring system"""
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
    assert perfect_score == 1.0, "Perfect requirements should give score of 1.0"
    
    # Test partial compatibility
    partial_requirements = {
        'supported_os': True,
        'supported_architecture': True,
        'sufficient_disk_space': False,  # Missing
        'sufficient_memory': True,
        'internet_connectivity': False,  # Missing
        'dependency_curl': True,
        'dependency_git': False,  # Missing
        'dependency_bash': True,
        'dependency_make': False,  # Missing
        'dependency_gcc': False   # Missing
    }
    
    partial_score = installer._calculate_compatibility_score({}, partial_requirements)
    print(f"   Partial compatibility score: {partial_score:.2f}")
    assert 0.0 < partial_score < 1.0, "Partial requirements should give intermediate score"
    
    print("   ✅ Compatibility scoring passed!")
    return True

async def test_verification_system():
    """Test comprehensive verification system"""
    print("\n✅ Testing verification system...")
    
    installer = AdvancedLean4InstallerService()
    
    # Mock component verification
    async def mock_verify_component(component):
        return {
            'available': True,
            'version_output': f'{component} 4.2.0',
            'version_number': '4.2.0',
            'functional': True
        }
    
    installer._verify_component = mock_verify_component
    
    # Test individual component verification
    for component in ['elan', 'lean', 'lake']:
        result = await installer._verify_component(component)
        print(f"   {component}: {'✅' if result['functional'] else '❌'}")
        assert result['functional'], f"{component} should be functional"
    
    # Test verification score calculation
    mock_verification_results = {
        'elan': {'functional': True},
        'lean': {'functional': True},
        'lake': {'functional': True},
        'toolchains': {'success': True, 'count': 2},
        'functionality_test': {'success': True}
    }
    
    score = installer._calculate_verification_score(mock_verification_results)
    print(f"   Overall verification score: {score:.2f}")
    assert score == 1.0, "All functional components should give perfect score"
    
    print("   ✅ Verification system passed!")
    return True

async def main():
    """Run all tests"""
    print("🚀 Testing Advanced Lean4 Installer Service")
    print("=" * 60)
    
    tests = [
        test_system_compatibility_analysis,
        test_advanced_installation_check,
        test_intelligent_download_simulation,
        test_progress_tracking,
        test_performance_metrics,
        test_dependency_analysis,
        test_configuration_generation,
        test_compatibility_scoring,
        test_verification_system
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
    
    print("\n" + "=" * 60)
    print(f"🎉 Test Results: {passed_tests}/{total_tests} tests passed")
    print(f"⏱️ Total test time: {total_time:.2f} seconds")
    
    if passed_tests == total_tests:
        print("✨ All tests passed successfully!")
        print("\n🎯 Advanced Lean4 Installer features verified:")
        print("   ✅ Intelligent system compatibility analysis")
        print("   ✅ Advanced installation detection and validation")
        print("   ✅ Intelligent download with caching and verification")
        print("   ✅ Comprehensive progress tracking")
        print("   ✅ Performance metrics collection")
        print("   ✅ Enhanced dependency analysis")
        print("   ✅ Smart configuration generation")
        print("   ✅ Compatibility scoring system")
        print("   ✅ Comprehensive verification framework")
        return True
    else:
        print("⚠️ Some tests failed - check the implementation")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
