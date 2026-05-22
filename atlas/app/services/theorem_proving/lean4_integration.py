"""
Lean4 Integration (stub seguro)
- Detecta entorno de Lean/elan y expone API async consistente
- Si está disponible, intenta verificación ejecutando `lean` con archivo temporal
- Incluye validación, diagnóstico y instalación asistida
"""

from __future__ import annotations
import aiofiles

import asyncio
import os
import platform
import re
import shutil
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List
from app.types.lean4 import SystemInfo, BinaryChecks, Diagnosis
from app.config import settings


def _detect_lean() -> DetectLeanResult:
    # Resolver ELAN_HOME con fallback robusto
    env_elan = os.getenv("ELAN_HOME")
    settings_elan = getattr(settings, "ELAN_HOME", None)
    elan_home = os.path.expanduser(env_elan or settings_elan or "~/.elan")

    # Construir rutas por defecto basadas en ELAN_HOME
    default_lean_bin = os.path.join(elan_home, "bin", "lean")
    default_lake_bin = os.path.join(elan_home, "bin", "lake")

    # Permitir override directo LEAN_BIN
    env_lean_bin = os.getenv("LEAN_BIN")
    settings_lean_bin = getattr(settings, "LEAN_BIN", None)
    lean_bin = env_lean_bin or settings_lean_bin or default_lean_bin
    lake_bin = default_lake_bin

    available = bool(lean_bin) and os.path.exists(lean_bin)
    return {
        "available": available,
        "elan_home": elan_home,
        "lean_bin": lean_bin,
        "lake_bin": lake_bin,
    }


class Lean4Service:
    def __init__(self) -> None:
        self.env = _detect_lean()
        self.default_timeout = int(os.getenv("LEAN_TIMEOUT_MS", getattr(settings, "lean_timeout_ms", "15000")))
        self.logger = logging.getLogger(__name__)
        
        # Configuración extendida para validación y diagnóstico
        self.diagnostics = {}
        # Order matters: prioritize type_error over syntax_error to avoid overlap
        self.error_patterns = {
            'type_error': r'type mismatch',
            'syntax_error': r'expected.*got',
            'undefined_symbol': r'unknown identifier',
            'import_error': r'could not resolve import',
            'timeout_error': r'(timeout|interrupted)',
            'memory_error': r'out of memory'
        }

    async def prove_theorem(self, statement: str, context: Optional[ProveTheoremResult] = None, timeout_ms: Optional[int] = None) -> ProveTheoremResult:
        if not self.env["available"]:
            return {
                "proven": None,
                "status": "UNKNOWN",
                "reason": "Lean4 no disponible en el entorno",
            }
        # Ejecutar lean con un archivo temporal minimal
        src = self._build_lean_source(statement, context)
        try:
            with tempfile.TemporaryDirectory() as td:
                src_path = os.path.join(td, "Main.lean")
                with aiofiles.aiofiles.open(src_path, "w", encoding="utf-8") as f:
                    f.write(src)
                proc = await asyncio.create_subprocess_exec(
                    self.env["lean_bin"], src_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                try:
                    to = (timeout_ms if timeout_ms is not None else self.default_timeout) / 1000.0
                    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=to)
                except asyncio.TimeoutError:
                    proc.kill()
                    return {"proven": None, "status": "UNKNOWN", "reason": "timeout"}
                out = (stdout or b"").decode()
                err = (stderr or b"").decode()
                success = proc.returncode == 0
                return {
                    "proven": success,
                    "status": "PROVEN" if success else "UNKNOWN",
                    "stdout": out[:2000],
                    "stderr": err[:2000],
                }
        except Exception as e:
            return {"proven": None, "status": "ERROR", "reason": str(e)}

    def _build_lean_source(self, statement: str, context: Optional[Dict[str, Any]]) -> str:
        header = """
import Mathlib
from app.config import settings
from app.types.lean4_integration_types import (
    DetectLeanResult,
    ProveTheoremResult,
    VerifyAtlasHypothesisResult,
    ValidateConfigurationResult,
    GetToolchainInfoResult,
    CheckMathlibStatusResult,
    CheckWorkspaceSetupResult,
    TestBasicCompilationResult,
)
set_option maxHeartbeats 200000
"""
        body = statement.strip()
        if not body:
            body = "theorem triv : True := by trivial"
        return header + "\n" + body + "\n"

    async def verify_atlas_hypothesis(self, hypothesis: VerifyAtlasHypothesisResult) -> VerifyAtlasHypothesisResult:
        stmt = hypothesis.get("formula") or hypothesis.get("statement") or ""
        result = await self.prove_theorem(stmt)
        return {
            "hypothesis_id": hypothesis.get("id", "unknown"),
            "formal_proof": result,
            "verified": bool(result.get("proven")),
            "confidence": 0.0 if result.get("proven") is not True else 0.98,
            "counterexample": None,
        }
    
    async def validate_configuration(self) -> ValidateConfigurationResult:
        """Validación completa de configuración Lean4"""
        try:
            self.logger.info("🔍 Validando configuración de Lean4")
            
            validation_results = {
                'timestamp': asyncio.get_event_loop().time(),
                'system_info': await self._get_system_info(),
                'binary_checks': await self._check_binaries(),
                'toolchain_info': await self._get_toolchain_info(),
                'mathlib_status': await self._check_mathlib_status(),
                'workspace_check': await self._check_workspace_setup(),
                'compilation_test': await self._test_basic_compilation(),
                'overall_status': 'unknown'
            }
            
            # Determinar estado general
            binary_available = validation_results['binary_checks'].get('lean', {}).get('available', False)
            compilation_success = validation_results['compilation_test'].get('success', False)
            
            if binary_available and compilation_success:
                validation_results['overall_status'] = 'healthy'
            elif binary_available:
                validation_results['overall_status'] = 'partial'
            else:
                validation_results['overall_status'] = 'broken'
            
            # Generar recomendaciones
            validation_results['recommendations'] = self._generate_recommendations(validation_results)
            
            self.diagnostics = validation_results
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Error validating Lean4 configuration: {str(e)}")
            return {
                'overall_status': 'error',
                'error': str(e),
                'recommendations': ['Verificar instalación de Lean4', 'Ejecutar diagnóstico completo']
            }
    
    async def _get_system_info(self) -> SystemInfo:
        """Información del sistema"""
        return {
            'os': platform.system(),
            'architecture': platform.machine(),
            'python_version': platform.python_version(),
            'shell': os.getenv('SHELL', getattr(settings, 'shell', 'unknown')),
            'home_dir': str(Path.home()),
            'current_dir': str(Path.cwd()),
            'elan_home': self.env.get('elan_home', 'unknown')
        }
    
    async def _check_binaries(self) -> BinaryChecks:
        """Verificación de binarios Lean4"""
        binaries = {}
        
        # Verificar lean
        lean_bin = self.env.get('lean_bin')
        if lean_bin and os.path.exists(lean_bin):
            binaries['lean'] = {
                'available': True,
                'path': lean_bin,
                'executable': os.access(lean_bin, os.X_OK)
            }
        else:
            binaries['lean'] = {
                'available': False,
                'path': lean_bin,
                'error': 'Binary not found'
            }
        
        # Verificar lake
        lake_bin = self.env.get('lake_bin')
        if lake_bin and os.path.exists(lake_bin):
            binaries['lake'] = {
                'available': True,
                'path': lake_bin,
                'executable': os.access(lake_bin, os.X_OK)
            }
        else:
            binaries['lake'] = {
                'available': False,
                'path': lake_bin,
                'error': 'Binary not found'
            }
        
        # Verificar elan
        elan_bin = os.path.join(self.env.get('elan_home', ''), 'bin', 'elan')
        if os.path.exists(elan_bin):
            binaries['elan'] = {
                'available': True,
                'path': elan_bin,
                'executable': os.access(elan_bin, os.X_OK)
            }
        else:
            binaries['elan'] = {
                'available': False,
                'path': elan_bin,
                'error': 'Binary not found'
            }
        
        return binaries
    
    async def _get_toolchain_info(self) -> GetToolchainInfoResult:
        """Información del toolchain Lean4"""
        elan_bin = os.path.join(self.env.get('elan_home', ''), 'bin', 'elan')
        
        if not os.path.exists(elan_bin):
            return {'error': 'elan not available'}
        
        try:
            # Obtener información del toolchain
            proc = await asyncio.create_subprocess_exec(
                elan_bin, 'show',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            return {
                'elan_available': True,
                'toolchain_info': stdout.decode().strip() if proc.returncode == 0 else None,
                'error': stderr.decode() if stderr else None
            }
            
        except Exception as e:
            return {'error': str(e), 'elan_available': False}
    
    async def _check_mathlib_status(self) -> CheckMathlibStatusResult:
        """Estado de mathlib4"""
        try:
            mathlib_paths = [
                Path(self.env.get('elan_home', '')) / 'toolchains',
                Path.home() / 'mathlib4',
                Path.cwd() / 'mathlib4'
            ]
            
            mathlib_info = {
                'found_paths': [],
                'cache_available': False,
                'version': None
            }
            
            for path in mathlib_paths:
                if path.exists():
                    # Buscar archivos de mathlib
                    mathlib_files = list(path.rglob('*Mathlib*'))
                    if mathlib_files:
                        mathlib_info['found_paths'].append(str(path))
            
            # Verificar cache de mathlib
            cache_path = Path.home() / '.cache' / 'mathlib4'
            if cache_path.exists():
                mathlib_info['cache_available'] = True
                mathlib_info['cache_path'] = str(cache_path)
            
            return mathlib_info
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _check_workspace_setup(self) -> CheckWorkspaceSetupResult:
        """Verificación de workspace"""
        current_dir = Path.cwd()
        
        workspace_info = {
            'current_directory': str(current_dir),
            'is_lean_project': False,
            'lakefile_exists': False,
            'lean_toolchain_exists': False,
            'build_directory_exists': False
        }
        
        # Verificar archivos del proyecto Lean
        lakefile = current_dir / 'lakefile.lean'
        toolchain_file = current_dir / 'lean-toolchain'
        build_dir = current_dir / 'build'
        
        workspace_info['lakefile_exists'] = lakefile.exists()
        workspace_info['lean_toolchain_exists'] = toolchain_file.exists()
        workspace_info['build_directory_exists'] = build_dir.exists()
        workspace_info['is_lean_project'] = lakefile.exists() or toolchain_file.exists()
        
        # Leer contenido del lean-toolchain si existe
        if toolchain_file.exists():
            try:
                workspace_info['toolchain_version'] = toolchain_file.read_text().strip()
            except Exception:
                workspace_info['toolchain_version'] = 'unknown'
        
        return workspace_info
    
    async def _test_basic_compilation(self) -> TestBasicCompilationResult:
        """Test básico de compilación"""
        if not self.env.get('available', False):
            return {'success': False, 'error': 'lean binary not available'}
        
        try:
            # Crear archivo Lean temporal para test
            test_code = '''-- Test básico de Lean 4
def hello : String := "Hello from Lean 4!"

#check hello
#eval hello
'''
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.lean', delete=False) as f:
                f.write(test_code)
                temp_file = f.name
            
            try:
                # Intentar compilar el archivo
                proc = await asyncio.create_subprocess_exec(
                    self.env['lean_bin'], temp_file,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()
                
                return {
                    'success': proc.returncode == 0,
                    'stdout': stdout.decode()[:500],
                    'stderr': stderr.decode()[:500],
                    'returncode': proc.returncode
                }
                
            finally:
                # Limpiar archivo temporal
                os.unlink(temp_file)
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_recommendations(self, validation_results: Dict[str, Any]) -> List[str]:
        """Genera recomendaciones basadas en validación"""
        recommendations = []
        
        # Verificar binarios
        binaries = validation_results.get('binary_checks', {})
        if not binaries.get('lean', {}).get('available', False):
            recommendations.append("❌ Instalar Lean 4: curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh")
        
        if not binaries.get('elan', {}).get('available', False):
            recommendations.append("❌ Instalar elan (Lean toolchain manager)")
        
        if not binaries.get('lake', {}).get('available', False):
            recommendations.append("⚠️ Lake no disponible - verificar instalación de Lean 4")
        
        # Verificar mathlib
        mathlib_status = validation_results.get('mathlib_status', {})
        if not mathlib_status.get('found_paths', []):
            recommendations.append("📚 Considerar instalar mathlib4 para acceso a biblioteca matemática")
        
        # Verificar workspace
        workspace = validation_results.get('workspace_check', {})
        if not workspace.get('is_lean_project', False):
            recommendations.append("📁 Crear proyecto Lean: lake new <nombre_proyecto>")
        
        # Verificar compilación
        compilation = validation_results.get('compilation_test', {})
        if not compilation.get('success', False):
            recommendations.append("🚨 Compilación fallida - revisar configuración de Lean")
        
        # Estado general
        overall_status = validation_results.get('overall_status', 'unknown')
        if overall_status == 'healthy':
            recommendations.append("✅ Configuración Lean4 está funcionando correctamente")
        elif overall_status == 'partial':
            recommendations.append("⚠️ Configuración Lean4 funcional pero con problemas menores")
        elif overall_status == 'broken':
            recommendations.append("❌ Configuración Lean4 requiere reparación")
        
        return recommendations if recommendations else ["✅ No hay recomendaciones específicas"]
    
    async def diagnose_error(self, error_message: str, context: Optional[str] = None) -> Diagnosis:
        """Diagnóstica errores específicos de Lean4"""
        try:
            diagnosis = {
                'error_message': error_message,
                'context': context,
                'error_type': 'unknown',
                'suggestions': [],
                'severity': 'medium'
            }
            
            # Clasificar tipo de error
            for error_type, pattern in self.error_patterns.items():
                if re.search(pattern, error_message, re.IGNORECASE):
                    diagnosis['error_type'] = error_type
                    break
            
            # Generar sugerencias específicas
            diagnosis['suggestions'] = self._get_error_suggestions(diagnosis['error_type'], error_message)
            
            # Determinar severidad
            if diagnosis['error_type'] in ['syntax_error', 'type_error']:
                diagnosis['severity'] = 'low'
            elif diagnosis['error_type'] in ['undefined_symbol', 'import_error']:
                diagnosis['severity'] = 'medium'
            elif diagnosis['error_type'] in ['timeout_error', 'memory_error']:
                diagnosis['severity'] = 'high'
            
            return diagnosis
            
        except Exception as e:
            return {
                'error': str(e),
                'suggestions': ['Verificar sintaxis básica', 'Consultar documentación Lean4']
            }
    
    def _get_error_suggestions(self, error_type: str, error_message: str) -> List[str]:
        """Genera sugerencias específicas por tipo de error"""
        suggestions = {
            'syntax_error': [
                "Verificar paréntesis y llaves balanceados",
                "Revisar sintaxis de declaraciones",
                "Consultar guía de sintaxis Lean4"
            ],
            'type_error': [
                "Verificar tipos de argumentos",
                "Usar #check para inspeccionar tipos",
                "Revisar definiciones de tipos"
            ],
            'undefined_symbol': [
                "Verificar imports necesarios",
                "Revisar ortografía de identificadores",
                "Usar #check para verificar disponibilidad"
            ],
            'import_error': [
                "Verificar que el módulo existe",
                "Revisar configuración de lakefile.lean",
                "Verificar instalación de mathlib si es necesario"
            ],
            'timeout_error': [
                "Simplificar expresiones complejas",
                "Usar #set_option maxHeartbeats para incrementar límite",
                "Dividir pruebas en pasos más pequeños"
            ],
            'memory_error': [
                "Reducir tamaño del problema",
                "Incrementar memoria disponible",
                "Optimizar definiciones recursivas"
            ]
        }
        
        return suggestions.get(error_type, [
            "Revisar documentación oficial de Lean4",
            "Consultar comunidad Lean4",
            "Verificar configuración del sistema"
        ])

