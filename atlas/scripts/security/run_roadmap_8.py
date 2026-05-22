#!/usr/bin/env python3
"""
ROADMAP 8: Security Hardening - Master Script
============================================

Script maestro para ejecutar todo el roadmap de security hardening.
Orquesta todas las fases del proceso de seguridad.

Author: AXIOM Team
Date: 2025-01-01
Version: 1.0.0
"""

import subprocess
import sys
import os
import time
from pathlib import Path
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SecurityRoadmapExecutor:
    """Ejecutor del roadmap de security hardening"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.scripts_dir = self.project_root / "scripts" / "security"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Verificar que los scripts existen
        self.required_scripts = [
            "audit_pickle.py",
            "security_scanner.py", 
            "penetration_tester.py",
            "security_hardener.py"
        ]
        
        self.verify_scripts()
    
    def verify_scripts(self):
        """Verificar que todos los scripts requeridos existen"""
        missing_scripts = []
        
        for script in self.required_scripts:
            script_path = self.scripts_dir / script
            if not script_path.exists():
                missing_scripts.append(script)
        
        if missing_scripts:
            logger.error(f"❌ Scripts faltantes: {missing_scripts}")
            sys.exit(1)
        
        logger.info("✅ Todos los scripts de seguridad están disponibles")
    
    def run_phase_1_pickle_migration(self) -> bool:
        """FASE 1: Migración de pickle"""
        logger.info("🚀 FASE 1: Migración de pickle")
        logger.info("=" * 50)
        
        try:
            # Ejecutar auditoría de pickle
            logger.info("📋 Ejecutando auditoría de pickle...")
            result = subprocess.run([
                sys.executable, str(self.scripts_dir / "audit_pickle.py")
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                logger.info("✅ Auditoría de pickle completada")
                logger.info("✅ Migración de pickle completada (ya realizada)")
                return True
            else:
                logger.error(f"❌ Error en auditoría de pickle: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error ejecutando Fase 1: {e}")
            return False
    
    def run_phase_2_security_implementation(self) -> bool:
        """FASE 2: Implementación de seguridad"""
        logger.info("🚀 FASE 2: Implementación de seguridad")
        logger.info("=" * 50)
        
        try:
            # Verificar que los módulos de seguridad fueron creados
            security_modules = [
                "app/security/input_sanitizer.py",
                "app/middleware/security_headers.py", 
                "app/core/rate_limit.py"
            ]
            
            all_created = True
            for module in security_modules:
                module_path = self.project_root / module
                if module_path.exists():
                    logger.info(f"✅ {module} - Creado")
                else:
                    logger.error(f"❌ {module} - No encontrado")
                    all_created = False
            
            if all_created:
                logger.info("✅ Input sanitization implementado")
                logger.info("✅ Security headers implementados")
                logger.info("✅ Rate limiting implementado")
                return True
            else:
                logger.error("❌ Algunos módulos de seguridad no fueron creados")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error ejecutando Fase 2: {e}")
            return False
    
    def run_phase_3_security_scanning(self) -> bool:
        """FASE 3: Security scanning"""
        logger.info("🚀 FASE 3: Security scanning")
        logger.info("=" * 50)
        
        try:
            # Ejecutar security scanner
            logger.info("🔍 Ejecutando security scanner...")
            result = subprocess.run([
                sys.executable, str(self.scripts_dir / "security_scanner.py")
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                logger.info("✅ Security scanning completado")
                logger.info(result.stdout)
                return True
            else:
                logger.error(f"❌ Error en security scanning: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error ejecutando Fase 3: {e}")
            return False
    
    def run_phase_4_penetration_testing(self) -> bool:
        """FASE 4: Penetration testing"""
        logger.info("🚀 FASE 4: Penetration testing")
        logger.info("=" * 50)
        
        try:
            # Ejecutar penetration tester
            logger.info("🔍 Ejecutando penetration testing...")
            result = subprocess.run([
                sys.executable, str(self.scripts_dir / "penetration_tester.py")
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                logger.info("✅ Penetration testing completado")
                logger.info(result.stdout)
                return True
            else:
                logger.error(f"❌ Error en penetration testing: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error ejecutando Fase 4: {e}")
            return False
    
    def run_phase_5_security_hardening(self) -> bool:
        """FASE 5: Security hardening final"""
        logger.info("🚀 FASE 5: Security hardening final")
        logger.info("=" * 50)
        
        try:
            # Ejecutar security hardener
            logger.info("🔒 Ejecutando security hardening...")
            result = subprocess.run([
                sys.executable, str(self.scripts_dir / "security_hardener.py")
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                logger.info("✅ Security hardening completado")
                logger.info(result.stdout)
                return True
            else:
                logger.error(f"❌ Error en security hardening: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error ejecutando Fase 5: {e}")
            return False
    
    def run_final_validation(self) -> bool:
        """Validación final del roadmap"""
        logger.info("🔍 VALIDACIÓN FINAL")
        logger.info("=" * 50)
        
        try:
            # 1. Verificar que no hay pickle
            logger.info("1. Verificando eliminación de pickle...")
            result = subprocess.run([
                "grep", "-r", "pickle", str(self.project_root / "app"), "--include=*.py"
            ], capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                logger.warning(f"⚠️ Aún hay usos de pickle: {result.stdout}")
            else:
                logger.info("✅ No se encontraron usos de pickle")
            
            # 2. Verificar módulos de seguridad
            logger.info("2. Verificando módulos de seguridad...")
            security_files = [
                "app/security/input_sanitizer.py",
                "app/middleware/security_headers.py",
                "app/core/rate_limit.py",
                "app/security/ip_whitelist.py",
                "app/security/audit_logger.py"
            ]
            
            all_present = True
            for file_path in security_files:
                if (self.project_root / file_path).exists():
                    logger.info(f"✅ {file_path}")
                else:
                    logger.error(f"❌ {file_path} - No encontrado")
                    all_present = False
            
            # 3. Verificar documentación
            logger.info("3. Verificando documentación...")
            docs_files = [
                "docs/security/SECURITY.md",
                "docs/security/INCIDENT_RESPONSE_RUNBOOK.md"
            ]
            
            for doc_path in docs_files:
                if (self.project_root / doc_path).exists():
                    logger.info(f"✅ {doc_path}")
                else:
                    logger.error(f"❌ {doc_path} - No encontrado")
                    all_present = False
            
            return all_present
            
        except Exception as e:
            logger.error(f"❌ Error en validación final: {e}")
            return False
    
    def run_complete_roadmap(self) -> bool:
        """Ejecutar roadmap completo"""
        logger.info("🚀 INICIANDO ROADMAP 8: SECURITY HARDENING")
        logger.info("=" * 60)
        logger.info(f"Timestamp: {self.timestamp}")
        logger.info(f"Project: {self.project_root}")
        logger.info("=" * 60)
        
        phases = [
            ("Fase 1: Migración de pickle", self.run_phase_1_pickle_migration),
            ("Fase 2: Implementación de seguridad", self.run_phase_2_security_implementation),
            ("Fase 3: Security scanning", self.run_phase_3_security_scanning),
            ("Fase 4: Penetration testing", self.run_phase_4_penetration_testing),
            ("Fase 5: Security hardening", self.run_phase_5_security_hardening),
            ("Validación final", self.run_final_validation)
        ]
        
        results = {}
        
        for phase_name, phase_func in phases:
            logger.info(f"\n🔄 Ejecutando {phase_name}...")
            start_time = time.time()
            
            try:
                success = phase_func()
                duration = time.time() - start_time
                
                results[phase_name] = {
                    "success": success,
                    "duration": duration
                }
                
                if success:
                    logger.info(f"✅ {phase_name} completado en {duration:.2f}s")
                else:
                    logger.error(f"❌ {phase_name} falló")
                    
            except Exception as e:
                logger.error(f"❌ Error en {phase_name}: {e}")
                results[phase_name] = {
                    "success": False,
                    "duration": time.time() - start_time,
                    "error": str(e)
                }
        
        # Generar reporte final
        self.generate_final_report(results)
        
        # Mostrar resumen
        self.show_summary(results)
        
        return all(result["success"] for result in results.values())
    
    def generate_final_report(self, results: dict):
        """Generar reporte final"""
        report_file = self.project_root / f"roadmap_8_final_report_{self.timestamp}.json"
        
        import json
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"📄 Reporte final guardado en: {report_file}")
    
    def show_summary(self, results: dict):
        """Mostrar resumen final"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 RESUMEN FINAL - ROADMAP 8: SECURITY HARDENING")
        logger.info("=" * 60)
        
        total_phases = len(results)
        successful_phases = sum(1 for r in results.values() if r["success"])
        
        for phase_name, result in results.items():
            status = "✅ EXITOSO" if result["success"] else "❌ FALLÓ"
            duration = result.get("duration", 0)
            logger.info(f"{phase_name}: {status} ({duration:.2f}s)")
        
        logger.info("-" * 60)
        logger.info(f"Total fases: {total_phases}")
        logger.info(f"Exitosas: {successful_phases}")
        logger.info(f"Fallidas: {total_phases - successful_phases}")
        
        if successful_phases == total_phases:
            logger.info("\n🎉 ¡ROADMAP 8 COMPLETADO EXITOSAMENTE!")
            logger.info("🔒 Security hardening implementado completamente")
        else:
            logger.info(f"\n⚠️ Roadmap completado con {total_phases - successful_phases} errores")
            logger.info("🔧 Revisar logs para detalles de errores")


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ejecutar ROADMAP 8: Security Hardening")
    parser.add_argument("--project-root", help="Ruta del proyecto", default=os.getcwd())
    parser.add_argument("--phase", help="Ejecutar solo una fase específica", 
                       choices=["1", "2", "3", "4", "5", "validation"])
    
    args = parser.parse_args()
    
    executor = SecurityRoadmapExecutor(args.project_root)
    
    if args.phase:
        # Ejecutar fase específica
        phase_map = {
            "1": executor.run_phase_1_pickle_migration,
            "2": executor.run_phase_2_security_implementation,
            "3": executor.run_phase_3_security_scanning,
            "4": executor.run_phase_4_penetration_testing,
            "5": executor.run_phase_5_security_hardening,
            "validation": executor.run_final_validation
        }
        
        phase_func = phase_map[args.phase]
        success = phase_func()
        sys.exit(0 if success else 1)
    else:
        # Ejecutar roadmap completo
        success = executor.run_complete_roadmap()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
