"""
Advanced Lean4 Installer Service for AXIOM
==========================================

Intelligent and robust service for automatic detection, download, and installation 
of Lean4 with all dependencies across different operating systems.

Enhanced Features:
- Intelligent system detection and compatibility analysis
- Advanced dependency management and validation
- Robust error handling and recovery mechanisms
- Performance monitoring and optimization
- Multi-version support and management
- Advanced caching and offline installation
- Comprehensive diagnostics and troubleshooting
- Security validation and verification
- Progress tracking and detailed reporting
- Rollback and recovery capabilities

Author: AXIOM Research Team
Date: December 2024
Version: 2.0.0-advanced
"""

import asyncio
import hashlib
import json
import logging
import os
import platform
import psutil
import re
import shutil
import subprocess
import shlex
import tempfile
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union
import aiofiles
import httpx

from app.exceptions.base import (
    AtlasDomainError,
    AtlasExternalError,
    AtlasValidationError,
)

from app.exceptions import AtlasInfrastructureError
from app.config import settings
from app.types.lean4_installer_improved_types import (
    CheckDependencyResult,
    AdvancedInstallationCheckResult,
    GetComponentVersionResult,
    ExtractBuildInfoResult,
    CheckInstalledToolchainsResult,
    AdvancedMathlibCheckResult,
    SetupInstallationEnvironmentResult,
    CheckCachedInstallerResult,
    DownloadWithProgressResult,
    VerifyInstallerIntegrityResult,
    ExecuteInstallationResult,
    AnalyzeInstallationOutputResult,
    PostInstallationConfigurationResult,
    ConfigureEnvironmentResult,
    ConfigureLeanVersionResult,
    ConfigureMathlibResult,
    SetupDevelopmentEnvironmentResult,
    CheckVscodeLeanExtensionResult,
    OptimizeInstallationResult,
    CleanupTemporaryFilesResult,
    OptimizeCacheResult,
    ComprehensiveVerificationResult,
    VerifyComponentResult,
    VerifyToolchainsResult,
    TestLeanFunctionalityResult,
    RunPerformanceBenchmarkResult,
    IntelligentUninstallResult,
    CreateInstallationBackupResult,
)

logger = logging.getLogger(__name__)

@dataclass
class InstallationProgress:
    """Track installation progress"""
    step: str
    progress_percent: float
    status: str
    message: str
    timestamp: float
    duration: Optional[float] = None

@dataclass
class SystemCompatibility:
    """System compatibility analysis"""
    os_name: str
    os_version: str
    architecture: str
    is_supported: bool
    compatibility_score: float
    requirements_met: Dict[str, bool]
    recommendations: List[str]
    warnings: List[str]

@dataclass
class DependencyInfo:
    """Dependency information"""
    name: str
    required: bool
    available: bool
    version: Optional[str]
    install_command: Optional[str]
    description: str

class AdvancedLean4InstallerService:
    """Advanced Lean4 installation service with intelligent features"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.architecture = platform.machine().lower()
        self.logger = logging.getLogger(__name__)
        
        # Enhanced configuration
        self.config = {
            'elan_installer_urls': {
                'linux': 'https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh',
                'darwin': 'https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh',
                'windows': 'https://github.com/leanprover/elan/releases/latest/download/elan-init.exe'
            },
            'lean_versions': ['4.0.0', '4.1.0', '4.2.0', 'stable', 'nightly'],
            'default_version': 'stable',
            'timeout_seconds': 300,
            'retry_attempts': 3,
            'chunk_size': 8192,
            'verification_enabled': True
        }
        
        # Installation paths with enhanced structure
        self.install_paths = {
            'linux': {
                'elan': Path.home() / '.elan',
                'cache': Path.home() / '.cache' / 'lean',
                'config': Path.home() / '.config' / 'lean'
            },
            'darwin': {
                'elan': Path.home() / '.elan',
                'cache': Path.home() / 'Library' / 'Caches' / 'lean',
                'config': Path.home() / 'Library' / 'Preferences' / 'lean'
            },
            'windows': {
                'elan': Path.home() / '.elan',
                'cache': Path.home() / 'AppData' / 'Local' / 'lean' / 'cache',
                'config': Path.home() / 'AppData' / 'Roaming' / 'lean'
            }
        }
        
        # Enhanced dependency definitions
        self.dependencies = {
            'essential': [
                DependencyInfo('curl', True, False, None, 'apt-get install curl', 'HTTP client for downloads'),
                DependencyInfo('git', True, False, None, 'apt-get install git', 'Version control system'),
                DependencyInfo('bash', True, False, None, 'Built-in shell', 'Command shell')
            ],
            'recommended': [
                DependencyInfo('make', False, False, None, 'apt-get install build-essential', 'Build automation tool'),
                DependencyInfo('gcc', False, False, None, 'apt-get install gcc', 'C compiler'),
                DependencyInfo('python3', False, False, None, 'apt-get install python3', 'Python interpreter')
            ],
            'optional': [
                DependencyInfo('code', False, False, None, 'snap install code --classic', 'VS Code editor'),
                DependencyInfo('emacs', False, False, None, 'apt-get install emacs', 'Emacs editor'),
                DependencyInfo('vim', False, False, None, 'apt-get install vim', 'Vim editor')
            ]
        }
        
        # Progress tracking
        self.progress_history: List[InstallationProgress] = []
        self.current_step = ""
        
        # Performance metrics
        self.performance_metrics = {
            'total_download_time': 0.0,
            'total_install_time': 0.0,
            'download_speed_mbps': 0.0,
            'memory_usage_mb': 0.0,
            'disk_space_used_mb': 0.0
        }
    
    def _detect_os(self) -> Dict[str, str]:
        """Enhanced OS detection with detailed information"""
        try:
            os_info = {
                'system': self.system,
                'architecture': self.architecture,
                'platform': platform.platform(),
                'processor': platform.processor(),
                'machine': platform.machine(),
                'python_version': platform.python_version(),
                'python_build': platform.python_build()
            }
            
            # Detect OS version
            if self.system == 'linux':
                try:
                    with aiofiles.open('/etc/os-release', 'r') as f:
                        release_info = f.read()
                    os_info['distribution'] = self._parse_os_release(release_info)
                except Exception as e:
                    self.logger.debug(f"Failed to parse /etc/os-release: {e}")
                    os_info['distribution'] = 'unknown'
            elif self.system == 'darwin':
                os_info['macos_version'] = platform.mac_ver()[0]
            elif self.system == 'windows':
                os_info['windows_version'] = platform.win32_ver()[0]
            
            return os_info
            
        except Exception as e:
            self.logger.error(f"Error detecting OS: {e}")
            return {'error': str(e)}
    
    def _parse_os_release(self, release_info: str) -> Dict[str, str]:
        """Parse /etc/os-release file"""
        info = {}
        for line in release_info.split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                info[key.lower()] = value.strip('"')
        return info
    
    async def analyze_system_compatibility(self) -> SystemCompatibility:
        """Comprehensive system compatibility analysis"""
        try:
            os_info = self._detect_os()
            requirements = await self._check_system_requirements()
            
            # Calculate compatibility score
            compatibility_score = self._calculate_compatibility_score(os_info, requirements)
            
            # Generate recommendations
            recommendations = self._generate_compatibility_recommendations(os_info, requirements)
            
            # Check for warnings
            warnings = self._check_compatibility_warnings(os_info, requirements)
            
            return SystemCompatibility(
                os_name=os_info.get('system', 'unknown'),
                os_version=os_info.get('distribution', {}).get('version_id', 'unknown'),
                architecture=os_info.get('architecture', 'unknown'),
                is_supported=compatibility_score > 0.7,
                compatibility_score=compatibility_score,
                requirements_met=requirements,
                recommendations=recommendations,
                warnings=warnings
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing system compatibility: {e}")
            return SystemCompatibility(
                os_name='unknown', os_version='unknown', architecture='unknown',
                is_supported=False, compatibility_score=0.0,
                requirements_met={}, recommendations=[], warnings=[str(e)]
            )
    
    async def _check_system_requirements(self) -> Dict[str, bool]:
        """Check detailed system requirements"""
        requirements = {}
        
        # Check OS support
        supported_systems = ['linux', 'darwin', 'windows']
        requirements['supported_os'] = self.system in supported_systems
        
        # Check architecture
        supported_architectures = ['x86_64', 'amd64', 'arm64', 'aarch64']
        requirements['supported_architecture'] = any(
            arch in self.architecture for arch in supported_architectures
        )
        
        # Check disk space (minimum 1GB free)
        disk_usage = psutil.disk_usage(Path.home())
        free_space_gb = disk_usage.free / (1024**3)
        requirements['sufficient_disk_space'] = free_space_gb >= 1.0
        
        # Check memory (minimum 2GB RAM)
        memory = psutil.virtual_memory()
        total_memory_gb = memory.total / (1024**3)
        requirements['sufficient_memory'] = total_memory_gb >= 2.0
        
        # Check internet connectivity
        requirements['internet_connectivity'] = await self._check_internet_connectivity()
        
        # Check dependencies
        for category in self.dependencies:
            for dep in self.dependencies[category]:
                dep_status = await self._check_dependency(dep.name)
                requirements[f'dependency_{dep.name}'] = dep_status['available']
                
                # Update dependency info
                dep.available = dep_status['available']
                dep.version = dep_status.get('version')
        
        return requirements
    
    def _calculate_compatibility_score(self, os_info: Dict[str, Any], requirements: Dict[str, bool]) -> float:
        """Calculate overall compatibility score"""
        # Weight different requirements
        weights = {
            'supported_os': 0.3,
            'supported_architecture': 0.2,
            'sufficient_disk_space': 0.1,
            'sufficient_memory': 0.1,
            'internet_connectivity': 0.1,
            'dependency_curl': 0.05,
            'dependency_git': 0.05,
            'dependency_bash': 0.05,
            'dependency_make': 0.025,
            'dependency_gcc': 0.025
        }
        
        score = 0.0
        total_weight = 0.0
        
        for req, met in requirements.items():
            if req in weights:
                weight = weights[req]
                score += weight if met else 0
                total_weight += weight
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _generate_compatibility_recommendations(self, os_info: Dict[str, Any], requirements: Dict[str, bool]) -> List[str]:
        """Generate system-specific recommendations"""
        recommendations = []
        
        if not requirements.get('supported_os', True):
            recommendations.append(f"⚠️ Your OS ({self.system}) may not be fully supported")
        
        if not requirements.get('sufficient_disk_space', True):
            recommendations.append("💾 Free up at least 1GB of disk space before installation")
        
        if not requirements.get('sufficient_memory', True):
            recommendations.append("🖥️ Consider upgrading to at least 2GB RAM for optimal performance")
        
        if not requirements.get('internet_connectivity', True):
            recommendations.append("🌐 Ensure stable internet connection for downloading components")
        
        # Dependency-specific recommendations
        missing_essential = []
        for dep in self.dependencies['essential']:
            if not dep.available:
                missing_essential.append(dep.name)
                if dep.install_command:
                    recommendations.append(f"📦 Install {dep.name}: {dep.install_command}")
        
        if missing_essential:
            recommendations.append(f"⚡ Install essential dependencies first: {', '.join(missing_essential)}")
        
        return recommendations
    
    def _check_compatibility_warnings(self, os_info: Dict[str, Any], requirements: Dict[str, bool]) -> List[str]:
        """Check for potential compatibility warnings"""
        warnings = []
        
        # Architecture warnings
        if 'arm' in self.architecture.lower():
            warnings.append("🔄 ARM architecture detected - some features may have limited support")
        
        # OS-specific warnings
        if self.system == 'windows':
            warnings.append("🪟 Windows support is experimental - consider using WSL for better compatibility")
        
        # Memory warnings
        memory = psutil.virtual_memory()
        if memory.total / (1024**3) < 4.0:
            warnings.append("⚠️ Low memory detected - compilation may be slow")
        
        return warnings
    
    async def _check_internet_connectivity(self) -> bool:
        """Check internet connectivity"""
            # Try to connect to GitHub (where elan installer is hosted)
            proc = await asyncio.create_subprocess_exec(
                'curl', '-s', '--max-time', '10', 'https://github.com',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            return proc.returncode == 0
        except Exception as e:
            self.logger.warning(f"Internet connectivity check failed: {e}")
            return False
    
    async def _check_dependency(self, command: str) -> CheckDependencyResult:
        """Enhanced dependency checking with version detection"""
        try:
            # Try different version commands
            version_commands = [
                f"{command} --version",
                f"{command} -v",
                f"{command} version",
                f"which {command}"
            ]
            
            for cmd in version_commands:
                # Split command safely for execution without shell
                cmd_args = shlex.split(cmd)
                proc = await asyncio.create_subprocess_exec(
                    *cmd_args,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()
                
                if proc.returncode == 0:
                    version_output = stdout.decode().strip()
                    version = self._extract_version(version_output)
                    return {
                        'available': True,
                        'version': version,
                        'command_used': cmd,
                        'full_output': version_output
                    }
            
            return {'available': False, 'error': 'Command not found'}
            
        except Exception as e:
            return {'available': False, 'error': str(e)}
    
    def _extract_version(self, output: str) -> Optional[str]:
        """Extract version number from command output"""
        # Common version patterns
        patterns = [
            r'version\s+(\d+\.\d+\.\d+)',
            r'v(\d+\.\d+\.\d+)',
            r'(\d+\.\d+\.\d+)',
            r'(\d+\.\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _update_progress(self, step: str, progress: float, status: str, message: str):
        """Update installation progress"""
        progress_entry = InstallationProgress(
            step=step,
            progress_percent=progress,
            status=status,
            message=message,
            timestamp=time.time()
        )
        
        # Calculate duration if there's a previous step
        if self.progress_history:
            last_progress = self.progress_history[-1]
            progress_entry.duration = progress_entry.timestamp - last_progress.timestamp
        
        self.progress_history.append(progress_entry)
        self.current_step = step
        
        self.logger.info(f"📊 [{progress:.1f}%] {step}: {message}")
    
    async def intelligent_installation(self, 
                                     target_version: str = 'stable',
                                     force_reinstall: bool = False,
                                     enable_caching: bool = True,
                                     parallel_downloads: bool = True) -> Dict[str, Any]:
        """Intelligent Lean4 installation with advanced features"""
        start_time = time.time()
        
        try:
            self._update_progress("analysis", 0, "running", "Analyzing system compatibility")
            
            # Step 1: System compatibility analysis
            compatibility = await self.analyze_system_compatibility()
            
            if not compatibility.is_supported:
                return {
                    'success': False,
                    'error': 'System not compatible with Lean4',
                    'compatibility_analysis': asdict(compatibility),
                    'recommendations': compatibility.recommendations
                }
            
            self._update_progress("analysis", 10, "completed", "System compatibility verified")
            
            # Step 2: Check existing installation
            if not force_reinstall:
                self._update_progress("check", 15, "running", "Checking existing installation")
                existing_install = await self.advanced_installation_check()
                
                if existing_install.get('fully_installed', False):
                    return {
                        'success': True,
                        'message': 'Lean4 already installed and functional',
                        'existing_installation': existing_install,
                        'action': 'skipped',
                        'performance_metrics': self.performance_metrics
                    }
                
                self._update_progress("check", 20, "completed", "Installation check completed")
            
            # Step 3: Pre-installation setup
            self._update_progress("setup", 25, "running", "Setting up installation environment")
            
            setup_result = await self._setup_installation_environment()
            if not setup_result['success']:
                return setup_result
            
            self._update_progress("setup", 35, "completed", "Installation environment ready")
            
            # Step 4: Download components
            self._update_progress("download", 40, "running", "Downloading Lean4 components")
            
            download_result = await self._intelligent_download(target_version, enable_caching, parallel_downloads)
            if not download_result['success']:
                return download_result
            
            self._update_progress("download", 60, "completed", "Download completed successfully")
            
            # Step 5: Installation
            self._update_progress("install", 65, "running", "Installing Lean4")
            
            install_result = await self._execute_installation(download_result['installer_path'])
            if not install_result['success']:
                return install_result
            
            self._update_progress("install", 80, "completed", "Core installation completed")
            
            # Step 6: Post-installation configuration
            self._update_progress("configure", 85, "running", "Configuring Lean4 environment")
            
            config_result = await self._post_installation_configuration(target_version)
            
            self._update_progress("configure", 90, "completed", "Configuration completed")
            
            # Step 7: Verification and optimization
            self._update_progress("verify", 95, "running", "Verifying installation")
            
            verification_result = await self._comprehensive_verification()
            
            self._update_progress("verify", 100, "completed", "Installation verification completed")
            
            # Calculate final metrics
            total_time = time.time() - start_time
            self.performance_metrics['total_install_time'] = total_time
            
            return {
                'success': True,
                'message': 'Lean4 installed successfully with advanced features',
                'target_version': target_version,
                'installation_time': total_time,
                'compatibility_analysis': asdict(compatibility),
                'download_details': download_result,
                'installation_details': install_result,
                'configuration_details': config_result,
                'verification_results': verification_result,
                'performance_metrics': self.performance_metrics,
                'progress_history': [asdict(p) for p in self.progress_history],
                'next_steps': self._generate_next_steps(),
                'troubleshooting_guide': self._generate_troubleshooting_guide()
            }
            
        except AtlasDomainError as e:
            self.logger.error(f"Error during intelligent installation: {e}")
            return {
                'success': False,
                'error': str(e),
                'installation_time': time.time() - start_time,
                'progress_history': [asdict(p) for p in self.progress_history],
                'troubleshooting_guide': self._generate_troubleshooting_guide()
            }
        except AtlasExternalError as e:
            self.logger.error(f"Error during intelligent installation: {e}")
            return {
                'success': False,
                'error': str(e),
                'installation_time': time.time() - start_time,
                'progress_history': [asdict(p) for p in self.progress_history],
                'troubleshooting_guide': self._generate_troubleshooting_guide()
            }
        except AtlasValidationError as e:
            self.logger.error(f"Error during intelligent installation: {e}")
            return {
                'success': False,
                'error': str(e),
                'installation_time': time.time() - start_time,
                'progress_history': [asdict(p) for p in self.progress_history],
                'troubleshooting_guide': self._generate_troubleshooting_guide()
            }
        except AtlasInfrastructureError as e:
            self.logger.error(f"Error during intelligent installation: {e}")
            return {
                'success': False,
                'error': str(e),
                'installation_time': time.time() - start_time,
                'progress_history': [asdict(p) for p in self.progress_history],
                'troubleshooting_guide': self._generate_troubleshooting_guide()
            }
    
    async def advanced_installation_check(self) -> AdvancedInstallationCheckResult:
        """Advanced check of existing Lean4 installation"""
        try:
            install_path = self.install_paths.get(self.system, {}).get('elan', Path.home() / '.elan')
            
            # Check binaries
            binaries = {
                'elan': install_path / 'bin' / 'elan',
                'lean': install_path / 'bin' / 'lean',
                'lake': install_path / 'bin' / 'lake',
                'leanpkg': install_path / 'bin' / 'leanpkg'
            }
            
            binary_status = {}
            for name, path in binaries.items():
                binary_status[name] = {
                    'exists': path.exists(),
                    'executable': path.exists() and os.access(path, os.X_OK),
                    'size_mb': path.stat().st_size / (1024*1024) if path.exists() else 0
                }
            
            # Check versions
            version_info = {}
            for name in binaries:
                if binary_status[name]['exists']:
                    version = await self._get_component_version(name)
                    version_info[name] = version
            
            # Check toolchains
            toolchain_info = await self._check_installed_toolchains()
            
            # Check mathlib
            mathlib_info = await self._advanced_mathlib_check()
            
            # Calculate installation completeness
            completeness_score = self._calculate_installation_completeness(
                binary_status, version_info, toolchain_info, mathlib_info
            )
            
            return {
                'install_path': str(install_path),
                'binary_status': binary_status,
                'version_info': version_info,
                'toolchain_info': toolchain_info,
                'mathlib_info': mathlib_info,
                'completeness_score': completeness_score,
                'fully_installed': completeness_score > 0.8,
                'recommendations': self._generate_installation_recommendations(
                    binary_status, version_info, toolchain_info, mathlib_info
                )
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _get_component_version(self, component: str) -> GetComponentVersionResult:
        """Get detailed version information for a component"""
        try:
            proc = await asyncio.create_subprocess_exec(
                component, "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                version_output = stdout.decode().strip()
                return {
                    'available': True,
                    'version_string': version_output,
                    'version_number': self._extract_version(version_output),
                    'build_info': self._extract_build_info(version_output)
                }
            else:
                return {
                    'available': False,
                    'error': stderr.decode().strip()
                }
                
        except Exception as e:
            return {'available': False, 'error': str(e)}
    
    def _extract_build_info(self, version_output: str) -> ExtractBuildInfoResult:
        """Extract build information from version output"""
        build_info = {}
        
        # Look for common build info patterns
        patterns = {
            'commit': r'commit\s+([a-f0-9]+)',
            'date': r'(\d{4}-\d{2}-\d{2})',
            'platform': r'(linux|darwin|windows)',
            'architecture': r'(x86_64|amd64|arm64|aarch64)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, version_output, re.IGNORECASE)
            if match:
                build_info[key] = match.group(1)
        
        return build_info
    
    async def _check_installed_toolchains(self) -> CheckInstalledToolchainsResult:
        """Check installed Lean toolchains"""
        try:
            proc = await asyncio.create_subprocess_exec(
                "elan", "toolchain", "list",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                toolchains = []
                default_toolchain = None
                
                for line in stdout.decode().split('\n'):
                    line = line.strip()
                    if line:
                        if '(default)' in line:
                            default_toolchain = line.replace('(default)', '').strip()
                            toolchains.append({
                                'name': default_toolchain,
                                'is_default': True
                            })
                        else:
                            toolchains.append({
                                'name': line,
                                'is_default': False
                            })
                
                return {
                    'available': True,
                    'toolchains': toolchains,
                    'default_toolchain': default_toolchain,
                    'count': len(toolchains)
                }
            else:
                return {
                    'available': False,
                    'error': stderr.decode().strip()
                }
                
        except Exception as e:
            return {'available': False, 'error': str(e)}
    
    async def _advanced_mathlib_check(self) -> AdvancedMathlibCheckResult:
        """Advanced mathlib installation check"""
        try:
            # Check multiple possible mathlib locations
            mathlib_locations = [
                Path.home() / '.elan' / 'toolchains',
                Path.home() / 'mathlib4',
                Path('/opt/lean/mathlib4'),
                Path.cwd() / 'mathlib4'
            ]
            
            mathlib_info = {
                'found': False,
                'locations': [],
                'version': None,
                'cache_status': {},
                'size_mb': 0
            }
            
            for location in mathlib_locations:
                if location.exists():
                    # Look for mathlib files
                    mathlib_files = list(location.rglob('*mathlib*'))
                    if mathlib_files:
                        mathlib_info['found'] = True
                        mathlib_info['locations'].append(str(location))
                        
                        # Calculate size
                        total_size = sum(
                            f.stat().st_size for f in mathlib_files 
                            if f.is_file()
                        )
                        mathlib_info['size_mb'] += total_size / (1024*1024)
            
            # Check mathlib cache
            cache_dir = self.install_paths.get(self.system, {}).get('cache')
            if cache_dir and cache_dir.exists():
                cache_files = list(cache_dir.rglob('*'))
                mathlib_info['cache_status'] = {
                    'exists': True,
                    'file_count': len(cache_files),
                    'size_mb': sum(
                        f.stat().st_size for f in cache_files 
                        if f.is_file()
                    ) / (1024*1024)
                }
            
            return mathlib_info
            
        except BiologyError as e:
            return {'error': str(e)}
    
    def _calculate_installation_completeness(self, binary_status: Dict, version_info: Dict, 
                                           toolchain_info: Dict, mathlib_info: Dict) -> float:
        """Calculate overall installation completeness score"""
        score = 0.0
        max_score = 0.0
        
        # Binary completeness (40% of total score)
        essential_binaries = ['elan', 'lean', 'lake']
        for binary in essential_binaries:
            max_score += 0.4 / len(essential_binaries)
            if binary_status.get(binary, {}).get('executable', False):
                score += 0.4 / len(essential_binaries)
        
        # Version availability (20% of total score)
        max_score += 0.2
        available_versions = sum(
            1 for v in version_info.values() 
            if v.get('available', False)
        )
        if available_versions > 0:
            score += 0.2 * (available_versions / len(essential_binaries))
        
        # Toolchain availability (20% of total score)
        max_score += 0.2
        if toolchain_info.get('available', False) and toolchain_info.get('count', 0) > 0:
            score += 0.2
        
        # Mathlib availability (20% of total score)
        max_score += 0.2
        if mathlib_info.get('found', False):
            score += 0.2
        
        return score / max_score if max_score > 0 else 0.0
    
    def _generate_installation_recommendations(self, binary_status: Dict, version_info: Dict,
                                             toolchain_info: Dict, mathlib_info: Dict) -> List[str]:
        """Generate recommendations based on installation status"""
        recommendations = []
        
        # Check for missing binaries
        essential_binaries = ['elan', 'lean', 'lake']
        missing_binaries = [
            name for name in essential_binaries 
            if not binary_status.get(name, {}).get('executable', False)
        ]
        
        if missing_binaries:
            recommendations.append(f"🔧 Missing essential binaries: {', '.join(missing_binaries)}")
        
        # Check for version issues
        unavailable_versions = [
            name for name, info in version_info.items()
            if not info.get('available', False)
        ]
        
        if unavailable_versions:
            recommendations.append(f"⚠️ Version check failed for: {', '.join(unavailable_versions)}")
        
        # Check toolchain
        if not toolchain_info.get('available', False):
            recommendations.append("📦 No Lean toolchains found - run 'elan toolchain install stable'")
        elif toolchain_info.get('count', 0) == 0:
            recommendations.append("📦 Install at least one Lean toolchain")
        
        # Check mathlib
        if not mathlib_info.get('found', False):
            recommendations.append("📚 Consider installing mathlib for mathematical libraries")
        
        return recommendations
    
    async def _setup_installation_environment(self) -> SetupInstallationEnvironmentResult:
        """Setup enhanced installation environment"""
        try:
            # Create installation directories
            paths = self.install_paths.get(self.system, {})
            for path_type, path in paths.items():
                if not path.exists():
                    path.mkdir(parents=True, exist_ok=True)
                    self.logger.info(f"Created directory: {path}")
            
            # Set up temporary directory with sufficient space
            temp_dir = tempfile.mkdtemp(prefix='lean4_install_')
            
            # Check and reserve disk space
            required_space_gb = 2.0  # 2GB minimum
            available_space = psutil.disk_usage(temp_dir).free / (1024**3)
            
            if available_space < required_space_gb:
                return {
                    'success': False,
                    'error': f'Insufficient disk space. Need {required_space_gb}GB, have {available_space:.1f}GB'
                }
            
            return {
                'success': True,
                'temp_directory': temp_dir,
                'available_space_gb': available_space,
                'paths_created': list(str(p) for p in paths.values())
            }
            
        except AtlasDomainError as e:
            return {'success': False, 'error': str(e)}
        except AtlasExternalError as e:
            return {'success': False, 'error': str(e)}
        except AtlasValidationError as e:
            return {'success': False, 'error': str(e)}
        except AtlasInfrastructureError as e:
            return {'success': False, 'error': str(e)}
    
    async def _intelligent_download(self, target_version: str, enable_caching: bool, 
                                   parallel_downloads: bool) -> Dict[str, Any]:
        """Intelligent download with caching and optimization"""
        try:
            download_start = time.time()
            
            # Determine download URLs
            installer_url = self.config['elan_installer_urls'].get(self.system)
            if not installer_url:
                return {
                    'success': False,
                    'error': f'No installer URL for system: {self.system}'
                }
            
            # Setup download location
            cache_dir = self.install_paths.get(self.system, {}).get('cache', Path.home() / '.cache' / 'lean')
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Check cache if enabled
            cached_installer = None
            if enable_caching:
                cached_installer = await self._check_cached_installer(installer_url, cache_dir)
            
            installer_path = None
            download_stats = {}
            
            if cached_installer and cached_installer['valid']:
                self.logger.info("Using cached installer")
                installer_path = cached_installer['path']
                download_stats = {
                    'used_cache': True,
                    'cache_hit': True,
                    'download_time': 0.0,
                    'download_speed_mbps': 0.0
                }
            else:
                # Download installer
                self.logger.info(f"Downloading installer from {installer_url}")
                download_result = await self._download_with_progress(installer_url, cache_dir)
                
                if download_result['success']:
                    installer_path = download_result['file_path']
                    download_stats = download_result['stats']
                else:
                    return download_result
            
            # Verify installer integrity
            if self.config['verification_enabled']:
                verification_result = await self._verify_installer_integrity(installer_path)
                if not verification_result['valid']:
                    return {
                        'success': False,
                        'error': 'Installer integrity verification failed',
                        'verification_details': verification_result
                    }
            
            download_time = time.time() - download_start
            self.performance_metrics['total_download_time'] = download_time
            self.performance_metrics['download_speed_mbps'] = download_stats.get('download_speed_mbps', 0.0)
            
            return {
                'success': True,
                'installer_path': installer_path,
                'download_time': download_time,
                'download_stats': download_stats,
                'verification_passed': self.config['verification_enabled']
            }
            
        except (AtlasDomainError, AtlasExternalError, AtlasValidationError, AtlasInfrastructureError) as e:
            return {'success': False, 'error': str(e)}
    
    async def _check_cached_installer(self, url: str, cache_dir: Path) -> CheckCachedInstallerResult:
        """Check for valid cached installer"""
        try:
            # Generate cache filename based on URL hash
            url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
            cache_file = cache_dir / f"elan_installer_{url_hash}"
            
            if not cache_file.exists():
                return {'valid': False, 'reason': 'Cache file not found'}
            
            # Check file age (consider valid for 7 days)
            file_age = time.time() - cache_file.stat().st_mtime
            if file_age > 7 * 24 * 3600:  # 7 days
                return {'valid': False, 'reason': 'Cache file too old'}
            
            # Basic integrity check
            if cache_file.stat().st_size < 1000:  # Less than 1KB
                return {'valid': False, 'reason': 'Cache file too small'}
            
            return {
                'valid': True,
                'path': cache_file,
                'age_hours': file_age / 3600,
                'size_mb': cache_file.stat().st_size / (1024*1024)
            }
            
        except BiologyError as e:
            return {'valid': False, 'reason': str(e)}
    
    async def _download_with_progress(self, url: str, download_dir: Path) -> DownloadWithProgressResult:
        """Download file with progress tracking and optimization"""
        try:
            # Generate filename
            url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
            filename = f"elan_installer_{url_hash}"
            file_path = download_dir / filename
            
            start_time = time.time()
            total_size = 0
            downloaded_size = 0
            
            # Make request with headers
            import urllib.request
            req = urllib.request.Request(
                url,
                headers={
                    'User-Agent': 'AXIOM-Lean4-Installer/2.0.0',
                    'Accept-Encoding': 'gzip, deflate'
                }
            )
            
            with await httpx.get(req, timeout=self.config['timeout_seconds']) as response:
                # Get total size if available
                content_length = response.headers.get('Content-Length')
                if content_length:
                    total_size = int(content_length)
                
                # Download with progress tracking
                with aiofiles.open(file_path, 'wb') as f:
                    while True:
                        chunk = response.read(self.config['chunk_size'])
                        if not chunk:
                            break
                        
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Update progress
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            self._update_progress(
                                "download", 
                                40 + (progress * 0.2),  # 40-60% range
                                "running", 
                                f"Downloaded {downloaded_size / (1024*1024):.1f}MB / {total_size / (1024*1024):.1f}MB"
                            )
            
            download_time = time.time() - start_time
            download_speed_mbps = (downloaded_size / (1024*1024)) / download_time if download_time > 0 else 0
            
            # Make executable (for Unix systems)
            if self.system in ['linux', 'darwin']:
                file_path.chmod(0o755)
            
            return {
                'success': True,
                'file_path': file_path,
                'stats': {
                    'download_time': download_time,
                    'downloaded_size_mb': downloaded_size / (1024*1024),
                    'download_speed_mbps': download_speed_mbps,
                    'used_cache': False,
                    'cache_hit': False
                }
            }
            
        except BiologyError as e:
            return {'success': False, 'error': str(e)}
    
    async def _verify_installer_integrity(self, installer_path: Path) -> VerifyInstallerIntegrityResult:
        """Verify installer file integrity"""
        try:
            # Basic file checks
            if not installer_path.exists():
                return {'valid': False, 'reason': 'File does not exist'}
            
            file_size = installer_path.stat().st_size
            if file_size < 1000:  # Less than 1KB
                return {'valid': False, 'reason': 'File too small'}
            
            # Check file type (basic heuristics)
            with aiofiles.aiofiles.open(installer_path, 'rb') as f:
                header = f.read(100)
            
            # Shell script should start with shebang
            if self.system in ['linux', 'darwin']:
                if not header.startswith(b'#!/'):
                    return {'valid': False, 'reason': 'Invalid shell script header'}
            
            # Calculate file hash for future verification
            hash_sha256 = hashlib.sha256()
            with aiofiles.open(installer_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            
            return {
                'valid': True,
                'file_size': file_size,
                'sha256_hash': hash_sha256.hexdigest(),
                'header_check': 'passed'
            }
            
        except BiologyError as e:
            return {'valid': False, 'reason': str(e)}
    
    async def _execute_installation(self, installer_path: Path) -> ExecuteInstallationResult:
        """Execute the installation with enhanced monitoring"""
        try:
            install_start = time.time()
            
            # Prepare environment
            env = {**os.environ}
            env['ELAN_INIT_SKIP_PATH_CHECK'] = 'yes'
            env['ELAN_INIT_SKIP_SHELL_MODIFY'] = 'no'
            
            # Prepare command based on OS as list
            if self.system in ['linux', 'darwin']:
                cmd_list = ['bash', str(installer_path), '-y', '--default-toolchain', 'stable']
            else:  # Windows
                cmd_list = [str(installer_path), '-y', '--default-toolchain', 'stable']
            
            # Execute with timeout and monitoring
            proc = await asyncio.create_subprocess_exec(
                *cmd_list,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            # Monitor process with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), 
                    timeout=self.config['timeout_seconds']
                )
            except asyncio.TimeoutError:
                proc.kill()
                return {
                    'success': False,
                    'error': 'Installation timed out',
                    'timeout_seconds': self.config['timeout_seconds']
                }
            
            install_time = time.time() - install_start
            self.performance_metrics['total_install_time'] += install_time
            
            # Analyze output
            stdout_text = stdout.decode()
            stderr_text = stderr.decode()
            
            success = proc.returncode == 0
            
            return {
                'success': success,
                'returncode': proc.returncode,
                'install_time': install_time,
                'stdout': stdout_text,
                'stderr': stderr_text,
                'output_analysis': self._analyze_installation_output(stdout_text, stderr_text)
            }
            
        except (AtlasDomainError, AtlasExternalError, AtlasValidationError, AtlasInfrastructureError) as e:
            return {'success': False, 'error': str(e)}
    
    def _analyze_installation_output(self, stdout: str, stderr: str) -> AnalyzeInstallationOutputResult:
        """Analyze installation output for insights"""
        analysis = {
            'warnings': [],
            'errors': [],
            'success_indicators': [],
            'performance_notes': []
        }
        
        # Look for warning patterns
        warning_patterns = [
            r'warning:.*',
            r'deprecated:.*',
            r'note:.*'
        ]
        
        for pattern in warning_patterns:
            warnings = re.findall(pattern, stdout + stderr, re.IGNORECASE)
            analysis['warnings'].extend(warnings)
        
        # Look for error patterns
        error_patterns = [
            r'error:.*',
            r'failed:.*',
            r'cannot.*'
        ]
        
        for pattern in error_patterns:
            errors = re.findall(pattern, stdout + stderr, re.IGNORECASE)
            analysis['errors'].extend(errors)
        
        # Look for success indicators
        success_patterns = [
            r'successfully.*installed',
            r'installation.*complete',
            r'elan.*installed'
        ]
        
        for pattern in success_patterns:
            successes = re.findall(pattern, stdout + stderr, re.IGNORECASE)
            analysis['success_indicators'].extend(successes)
        
        return analysis
    
    async def _post_installation_configuration(self, target_version: str) -> PostInstallationConfigurationResult:
        """Enhanced post-installation configuration"""
        try:
            config_results = {}
            
            # Configure environment
            env_result = await self._configure_environment()
            config_results['environment'] = env_result
            
            # Install/update to target version
            version_result = await self._configure_lean_version(target_version)
            config_results['version'] = version_result
            
            # Configure mathlib
            mathlib_result = await self._configure_mathlib()
            config_results['mathlib'] = mathlib_result
            
            # Setup development environment
            dev_env_result = await self._setup_development_environment()
            config_results['development_environment'] = dev_env_result
            
            # Optimize installation
            optimization_result = await self._optimize_installation()
            config_results['optimization'] = optimization_result
            
            return {
                'success': True,
                'configuration_steps': config_results,
                'message': 'Post-installation configuration completed'
            }
            
        except BiologyError as e:
            return {'success': False, 'error': str(e)}
    
    async def _configure_environment(self) -> ConfigureEnvironmentResult:
        """Configure environment variables and PATH"""
        try:
            elan_bin = self.install_paths[self.system]['elan'] / 'bin'
            
            # Check current PATH
            current_path = os.getenv("PATH", getattr(settings, "path", ""))
            elan_bin_str = str(elan_bin)
            
            path_configured = elan_bin_str in current_path
            
            # Generate shell configuration
            shell_configs = self._generate_shell_configuration(elan_bin_str)
            
            return {
                'success': True,
                'elan_bin_path': elan_bin_str,
                'path_configured': path_configured,
                'shell_configurations': shell_configs,
                'current_path': current_path
            }
            
        except BiologyError as e:
            return {'success': False, 'error': str(e)}
    
    def _generate_shell_configuration(self, elan_bin_path: str) -> Dict[str, str]:
        """Generate shell configuration for different shells"""
        configs = {}
        
        # Bash configuration
        configs['bash'] = f'''
# Lean4 configuration
export PATH="{elan_bin_path}:$PATH"
'''
        
        # Zsh configuration
        configs['zsh'] = f'''
# Lean4 configuration
export PATH="{elan_bin_path}:$PATH"
'''
        
        # Fish configuration
        configs['fish'] = f'''
# Lean4 configuration
set -gx PATH "{elan_bin_path}" $PATH
'''
        
        return configs
    
    async def _configure_lean_version(self, target_version: str) -> ConfigureLeanVersionResult:
        """Configure specific Lean version"""
        try:
            proc = await asyncio.create_subprocess_exec(
                "elan", "toolchain", "install", target_version,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                return {
                    'success': False,
                    'error': f'Failed to install version {target_version}',
                    'stderr': stderr.decode()
                }
            
            proc = await asyncio.create_subprocess_exec(
                "elan", "default", target_version,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await proc.communicate()
            
            return {
                'success': proc.returncode == 0,
                'target_version': target_version,
                'install_output': stdout.decode(),
                'set_as_default': proc.returncode == 0
            }
            
        except BiologyError as e:
            return {'success': False, 'error': str(e)}
    
    async def _configure_mathlib(self) -> ConfigureMathlibResult:
        """Configure mathlib setup"""
        try:
            # Check if lake is available
            lake_check = await self._check_dependency('lake')
            
            if not lake_check['available']:
                return {
                    'success': False,
                    'error': 'Lake not available for mathlib configuration'
                }
            
            # Create a test project to verify mathlib works
            temp_project = Path(tempfile.mkdtemp()) / 'test_mathlib'
            temp_project.mkdir(parents=True, exist_ok=True)
            
            os.chdir(temp_project)
            
            # Initialize test project
            init_proc = await asyncio.create_subprocess_exec(
                "lake", "new", "test_mathlib", "math",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await init_proc.communicate()
            
            # Clean up test project
            shutil.rmtree(temp_project, ignore_errors=True)
            
            return {
                'success': init_proc.returncode == 0,
                'lake_available': True,
                'test_project_created': init_proc.returncode == 0,
                'note': 'Mathlib will be installed per-project with lake'
            }
            
        except (AtlasDomainError, AtlasExternalError, AtlasValidationError, AtlasInfrastructureError) as e:
            return {'success': False, 'error': str(e)}
    
    async def _setup_development_environment(self) -> SetupDevelopmentEnvironmentResult:
        """Setup development environment optimizations"""
        try:
            optimizations = {}
            
            # Check for VS Code Lean extension
            vscode_check = await self._check_vscode_lean_extension()
            optimizations['vscode_extension'] = vscode_check
            
            # Setup lean configuration directory
            config_dir = self.install_paths[self.system]['config']
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Create basic configuration file
            config_file = config_dir / 'config.json'
            default_config = {
                'version': '2.0.0',
                'auto_update': True,
                'cache_enabled': True,
                'parallel_builds': True,
                'max_memory_mb': 2048
            }
            
            with aiofiles.open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            optimizations['config_file_created'] = True
            optimizations['config_path'] = str(config_file)
            
            return {
                'success': True,
                'optimizations': optimizations
            }
            
        except (AtlasDomainError, AtlasExternalError, AtlasValidationError, AtlasInfrastructureError) as e:
            return {'success': False, 'error': str(e)}
    
    async def _check_vscode_lean_extension(self) -> CheckVscodeLeanExtensionResult:
        """Check for VS Code Lean extension"""
        try:
            # Check if VS Code is installed
            code_check = await self._check_dependency('code')
            
            if not code_check['available']:
                return {
                    'vscode_available': False,
                    'extension_installed': False,
                    'recommendation': 'Install VS Code for better Lean development experience'
                }
            
            # Check for Lean extension
            proc = await asyncio.create_subprocess_exec(
                "code", "--list-extensions",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                extensions = stdout.decode().split('\n')
                lean_extension_installed = any('lean' in ext.lower() for ext in extensions)
                
                return {
                    'vscode_available': True,
                    'extension_installed': lean_extension_installed,
                    'installed_extensions': extensions,
                    'recommendation': 'Install leanprover.lean4 extension' if not lean_extension_installed else 'Lean extension available'
                }
            
            return {
                'vscode_available': True,
                'extension_installed': False,
                'error': stderr.decode()
            }
            
        except BiologyError as e:
            return {'vscode_available': False, 'error': str(e)}
    
    async def _optimize_installation(self) -> OptimizeInstallationResult:
        """Optimize installation for performance"""
        try:
            optimizations = {}
            
            # Clear temporary files
            temp_cleanup = await self._cleanup_temporary_files()
            optimizations['temp_cleanup'] = temp_cleanup
            
            # Optimize cache
            cache_optimization = await self._optimize_cache()
            optimizations['cache_optimization'] = cache_optimization
            
            # Memory optimization
            memory_info = psutil.virtual_memory()
            optimizations['memory_status'] = {
                'total_gb': memory_info.total / (1024**3),
                'available_gb': memory_info.available / (1024**3),
                'percent_used': memory_info.percent
            }
            
            # Disk space analysis
            disk_info = psutil.disk_usage(Path.home())
            optimizations['disk_status'] = {
                'total_gb': disk_info.total / (1024**3),
                'free_gb': disk_info.free / (1024**3),
                'percent_used': (disk_info.used / disk_info.total) * 100
            }
            
            return {
                'success': True,
                'optimizations': optimizations
            }
            
        except (AtlasDomainError, AtlasExternalError, AtlasValidationError, AtlasInfrastructureError) as e:
            return {'success': False, 'error': str(e)}
    
    async def _cleanup_temporary_files(self) -> CleanupTemporaryFilesResult:
        """Clean up temporary files from installation"""
        try:
            temp_dirs = [
                '/tmp',
                tempfile.gettempdir()
            ]
            
            cleaned_files = 0
            freed_space_mb = 0
            
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    for file_path in Path(temp_dir).glob('lean4_install_*'):
                        if file_path.is_file():
                            size_mb = file_path.stat().st_size / (1024*1024)
                            file_path.unlink()
                            cleaned_files += 1
                            freed_space_mb += size_mb
                        elif file_path.is_dir():
                            shutil.rmtree(file_path, ignore_errors=True)
                            cleaned_files += 1
            
            return {
                'success': True,
                'cleaned_files': cleaned_files,
                'freed_space_mb': freed_space_mb
            }
            
        except BiologyError as e:
            return {'success': False, 'error': str(e)}
    
    async def _optimize_cache(self) -> OptimizeCacheResult:
        """Optimize Lean cache"""
        try:
            cache_dir = self.install_paths[self.system]['cache']
            
            if not cache_dir.exists():
                return {'success': True, 'message': 'No cache to optimize'}
            
            # Analyze cache size
            cache_files = list(cache_dir.rglob('*'))
            total_size_mb = sum(
                f.stat().st_size for f in cache_files 
                if f.is_file()
            ) / (1024*1024)
            
            # Remove old cache files (older than 30 days)
            old_files_removed = 0
            current_time = time.time()
            
            for file_path in cache_files:
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > 30 * 24 * 3600:  # 30 days
                        file_path.unlink()
                        old_files_removed += 1
            
            return {
                'success': True,
                'total_cache_size_mb': total_size_mb,
                'cache_files_count': len(cache_files),
                'old_files_removed': old_files_removed
            }
            
        except BiologyError as e:
            return {'success': False, 'error': str(e)}
    
    async def _comprehensive_verification(self) -> ComprehensiveVerificationResult:
        """Comprehensive installation verification"""
        try:
            verification_results = {}
            
            # Component verification
            components = ['elan', 'lean', 'lake']
            for component in components:
                verification_results[component] = await self._verify_component(component)
            
            # Toolchain verification
            toolchain_verification = await self._verify_toolchains()
            verification_results['toolchains'] = toolchain_verification
            
            # Functionality test
            functionality_test = await self._test_lean_functionality()
            verification_results['functionality_test'] = functionality_test
            
            # Performance benchmark
            performance_benchmark = await self._run_performance_benchmark()
            verification_results['performance_benchmark'] = performance_benchmark
            
            # Calculate overall verification score
            verification_score = self._calculate_verification_score(verification_results)
            verification_results['overall_score'] = verification_score
            
            return verification_results
            
        except (AtlasDomainError, AtlasExternalError, AtlasValidationError, AtlasInfrastructureError) as e:
            return {'error': str(e)}
    
    async def _verify_component(self, component: str) -> VerifyComponentResult:
        """Verify individual component"""
        try:
            # Check if component is available
            proc = await asyncio.create_subprocess_exec(
                component, "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                version_output = stdout.decode().strip()
                return {
                    'available': True,
                    'version_output': version_output,
                    'version_number': self._extract_version(version_output),
                    'functional': True
                }
            else:
                return {
                    'available': False,
                    'error': stderr.decode().strip(),
                    'functional': False
                }
                
        except BiologyError as e:
            return {'available': False, 'error': str(e), 'functional': False}
    
    async def _verify_toolchains(self) -> VerifyToolchainsResult:
        """Verify installed toolchains"""
        try:
            # List toolchains
            proc = await asyncio.create_subprocess_exec(
                "elan", "toolchain", "list",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                toolchains = []
                for line in stdout.decode().split('\n'):
                    if line.strip():
                        toolchains.append(line.strip())
                
                return {
                    'success': True,
                    'toolchains': toolchains,
                    'count': len(toolchains),
                    'has_default': any('(default)' in tc for tc in toolchains)
                }
            else:
                return {
                    'success': False,
                    'error': stderr.decode().strip()
                }
                
        except BiologyError as e:
            return {'success': False, 'error': str(e)}
    
    async def _test_lean_functionality(self) -> TestLeanFunctionalityResult:
        """Test basic Lean functionality"""
        try:
            # Create a simple Lean file for testing
            test_content = '''
-- Simple Lean test file
#check Nat
#eval 2 + 2
theorem test_theorem : 2 + 2 = 4 := rfl
'''
            
            # Create temporary test file
            temp_dir = Path(tempfile.mkdtemp())
            test_file = temp_dir / 'test.lean'
            
            with aiofiles.aiofiles.open(test_file, 'w') as f:
                f.write(test_content)
            
            # Test Lean compilation
            proc = await asyncio.create_subprocess_exec(
                "lean", str(test_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=temp_dir
            )
            
            stdout, stderr = await proc.communicate()
            
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            success = proc.returncode == 0
            
            return {
                'success': success,
                'test_file_processed': success,
                'stdout': stdout.decode(),
                'stderr': stderr.decode(),
                'returncode': proc.returncode
            }
            
        except BiologyError as e:
            return {'success': False, 'error': str(e)}
    
    async def _run_performance_benchmark(self) -> RunPerformanceBenchmarkResult:
        """Run basic performance benchmark"""
        try:
            # Measure Lean startup time
            start_time = time.time()
            
            proc = await asyncio.create_subprocess_shell(
                "lean --version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await proc.communicate()
            
            startup_time = time.time() - start_time
            
            # Memory usage
            memory_info = psutil.virtual_memory()
            
            return {
                'startup_time_seconds': startup_time,
                'memory_available_gb': memory_info.available / (1024**3),
                'memory_percent_used': memory_info.percent,
                'performance_rating': 'excellent' if startup_time < 1.0 else 'good' if startup_time < 3.0 else 'slow'
            }
            
        except BiologyError as e:
            return {'error': str(e)}
    
    def _calculate_verification_score(self, verification_results: Dict[str, Any]) -> float:
        """Calculate overall verification score"""
        score = 0.0
        max_score = 0.0
        
        # Component scores (60% of total)
        components = ['elan', 'lean', 'lake']
        for component in components:
            max_score += 0.2  # Each component worth 20%
            if verification_results.get(component, {}).get('functional', False):
                score += 0.2
        
        # Toolchain score (20% of total)
        max_score += 0.2
        toolchain_info = verification_results.get('toolchains', {})
        if toolchain_info.get('success', False) and toolchain_info.get('count', 0) > 0:
            score += 0.2
        
        # Functionality test score (20% of total)
        max_score += 0.2
        if verification_results.get('functionality_test', {}).get('success', False):
            score += 0.2
        
        return score / max_score if max_score > 0 else 0.0
    
    def _generate_next_steps(self) -> List[str]:
        """Generate recommended next steps after installation"""
        return [
            "🔄 Restart your terminal or run: source ~/.bashrc (or ~/.zshrc)",
            "✅ Verify installation: lean --version",
            "📚 Create your first project: lake new my_project",
            "💻 Install VS Code Lean 4 extension for better development experience",
            "📖 Visit the Lean 4 documentation: https://leanprover.github.io/lean4/doc/",
            "🎓 Try the Lean 4 tutorial: https://leanprover.github.io/tutorial/",
            "🏗️ Set up a mathlib project: lake new my_math_project math"
        ]
    
    def _generate_troubleshooting_guide(self) -> List[str]:
        """Generate troubleshooting guide"""
        return [
            "🔍 Check PATH configuration: echo $PATH",
            "🔄 Reload shell configuration: source ~/.bashrc",
            "🧹 Clear cache: rm -rf ~/.elan/toolchains/*/lib/lean/library_cache",
            "🔧 Reinstall with: elan self uninstall && curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh",
            "💾 Check disk space: df -h",
            "🖥️ Check memory: free -h",
            "🌐 Check internet connection: ping github.com",
            "📝 Check logs in: ~/.elan/",
            "❓ Get help: https://leanprover.zulipchat.com/"
        ]
    
    async def intelligent_uninstall(self) -> IntelligentUninstallResult:
        """Intelligent uninstallation with backup options"""
        try:
            self.logger.info("🗑️ Starting intelligent Lean4 uninstallation")
            
            # Analyze current installation
            installation_analysis = await self.advanced_installation_check()
            
            if not installation_analysis.get('fully_installed', False):
                return {
                    'success': True,
                    'message': 'Lean4 is not installed or already partially removed',
                    'action': 'none_required'
                }
            
            # Create backup before uninstalling
            backup_result = await self._create_installation_backup()
            
            # Remove installation
            removal_results = {}
            
            # Remove elan directory
            elan_path = self.install_paths[self.system]['elan']
            if elan_path.exists():
                shutil.rmtree(elan_path)
                removal_results['elan_directory'] = 'removed'
            
            # Remove cache
            cache_path = self.install_paths[self.system]['cache']
            if cache_path.exists():
                shutil.rmtree(cache_path)
                removal_results['cache_directory'] = 'removed'
            
            # Remove configuration
            config_path = self.install_paths[self.system]['config']
            if config_path.exists():
                shutil.rmtree(config_path)
                removal_results['config_directory'] = 'removed'
            
            return {
                'success': True,
                'message': 'Lean4 uninstalled successfully',
                'backup_created': backup_result['success'],
                'backup_location': backup_result.get('backup_path'),
                'removal_results': removal_results,
                'restoration_note': 'Use backup to restore if needed'
            }
            
        except AtlasDomainError as e:
            self.logger.error(f"Error during intelligent uninstallation: {e}")
            return {'success': False, 'error': str(e)}
        except AtlasExternalError as e:
            self.logger.error(f"Error during intelligent uninstallation: {e}")
            return {'success': False, 'error': str(e)}
        except AtlasValidationError as e:
            self.logger.error(f"Error during intelligent uninstallation: {e}")
            return {'success': False, 'error': str(e)}
        except AtlasInfrastructureError as e:
            self.logger.error(f"Error during intelligent uninstallation: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _create_installation_backup(self) -> CreateInstallationBackupResult:
        """Create backup of current installation"""
        try:
            backup_dir = Path.home() / '.lean4_backup' / f"backup_{int(time.time())}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup elan directory
            elan_path = self.install_paths[self.system]['elan']
            if elan_path.exists():
                shutil.copytree(elan_path, backup_dir / 'elan')
            
            # Backup configuration
            config_path = self.install_paths[self.system]['config']
            if config_path.exists():
                shutil.copytree(config_path, backup_dir / 'config')
            
            # Create backup metadata
            backup_metadata = {
                'timestamp': time.time(),
                'system': self.system,
                'architecture': self.architecture,
                'backup_path': str(backup_dir)
            }
            
            with aiofiles.open(backup_dir / 'metadata.json', 'w') as f:
                json.dump(backup_metadata, f, indent=2)
            
            return {
                'success': True,
                'backup_path': str(backup_dir),
                'metadata': backup_metadata
            }
            
        except BiologyError as e:
            return {'success': False, 'error': str(e)}

# Global service instances
lean4_installer = AdvancedLean4InstallerService()
lean4_installer_service = lean4_installer  # Alias for compatibility
