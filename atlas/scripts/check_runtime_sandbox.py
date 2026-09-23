#!/usr/bin/env python3
"""
Runtime Sandbox Checker - AXIOM ATLAS
Verifica que el entorno de ejecución tiene las protecciones necesarias
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SandboxChecker:
    """Verificador de sandbox de ejecución"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {
            "checks": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "warnings": 0
            }
        }
    
    def check_python_version(self) -> Dict[str, Any]:
        """Verificar versión de Python"""
        logger.info("🐍 Verificando versión de Python...")
        
        version_info = sys.version_info
        is_supported = version_info >= (3, 9)
        
        check = {
            "name": "python_version",
            "status": "passed" if is_supported else "warning",
            "version": f"{version_info.major}.{version_info.minor}.{version_info.micro}",
            "supported": is_supported,
            "message": f"Python {version_info.major}.{version_info.minor} detected"
        }
        
        return check
    
    def check_virtual_environment(self) -> Dict[str, Any]:
        """Verificar que se está usando un entorno virtual"""
        logger.info("📦 Verificando entorno virtual...")
        
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        check = {
            "name": "virtual_environment",
            "status": "passed" if in_venv else "warning",
            "in_venv": in_venv,
            "message": "Virtual environment active" if in_venv 
                      else "Not running in virtual environment (recommended for isolation)"
        }
        
        return check
    
    def check_write_permissions(self) -> Dict[str, Any]:
        """Verificar permisos de escritura limitados"""
        logger.info("🔒 Verificando permisos de escritura...")
        
        # Verificar que no se pueda escribir en directorios del sistema
        system_dirs = ["/usr", "/bin", "/sbin", "/etc"]
        safe = True
        
        for dir_path in system_dirs:
            if os.path.exists(dir_path) and os.access(dir_path, os.W_OK):
                safe = False
                break
        
        check = {
            "name": "write_permissions",
            "status": "passed" if safe else "warning",
            "safe": safe,
            "message": "Limited write permissions" if safe 
                      else "Excessive write permissions detected"
        }
        
        return check
    
    def check_sandbox_executor(self) -> Dict[str, Any]:
        """Verificar que el sandbox executor está disponible"""
        logger.info("⚙️ Verificando Sandbox Executor...")
        
        sandbox_service = Path("app/services/sandbox_executor_service.py")
        sandbox_router = Path("app/routers/sandbox_executor.py")
        
        available = sandbox_service.exists() or sandbox_router.exists()
        
        check = {
            "name": "sandbox_executor",
            "status": "passed" if available else "warning",
            "service_exists": sandbox_service.exists(),
            "router_exists": sandbox_router.exists(),
            "message": "Sandbox executor available" if available 
                      else "Sandbox executor not found (optional for code execution)"
        }
        
        return check
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Ejecutar todas las verificaciones"""
        logger.info("🚀 Ejecutando verificaciones de sandbox...")
        
        checks = [
            self.check_python_version(),
            self.check_virtual_environment(),
            self.check_write_permissions(),
            self.check_sandbox_executor()
        ]
        
        # Compilar resultados
        for check in checks:
            self.results["checks"].append(check)
            self.results["summary"]["total"] += 1
            
            if check["status"] == "passed":
                self.results["summary"]["passed"] += 1
            else:
                self.results["summary"]["warnings"] += 1
        
        return self.results
    
    def print_summary(self):
        """Imprimir resumen"""
        print("\n" + "=" * 50)
        print("🔒 RUNTIME SANDBOX CHECKS")
        print("=" * 50)
        
        for check in self.results["checks"]:
            status_icon = "✅" if check["status"] == "passed" else "⚠️"
            print(f"{status_icon} {check['name']}: {check['message']}")
        
        print("\n" + "-" * 50)
        print(f"Total checks: {self.results['summary']['total']}")
        print(f"✅ Passed: {self.results['summary']['passed']}")
        print(f"⚠️  Warnings: {self.results['summary']['warnings']}")
        print("=" * 50)


def main():
    """Función principal"""
    checker = SandboxChecker()
    results = checker.run_all_checks()
    checker.print_summary()
    
    # No fallar en CI, solo informar
    # El sandbox es una capa adicional de seguridad, no un requisito bloqueante
    logger.info("✅ Sandbox check completed")
    exit(0)


if __name__ == "__main__":
    main()
