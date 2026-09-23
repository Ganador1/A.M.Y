#!/usr/bin/env python3
"""
Security Scanning Script - AXIOM ATLAS
======================================

Script para ejecutar herramientas de seguridad automatizadas.
Incluye Bandit, Safety, y otras herramientas de análisis de seguridad.

Author: AXIOM Team
Date: 2025-01-01
Version: 1.0.0
"""

import subprocess
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityScanner:
    """Scanner de seguridad automatizado"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.reports_dir = self.project_root / "security_reports"
        self.reports_dir.mkdir(exist_ok=True)
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {}
    
    def run_bandit(self) -> Dict[str, Any]:
        """Ejecutar Bandit para análisis de seguridad de código Python"""
        logger.info("🔍 Ejecutando Bandit security linter...")
        
        try:
            # Ejecutar Bandit
            cmd = [
                "bandit", 
                "-r", str(self.project_root / "app"),
                "-f", "json",
                "-o", str(self.reports_dir / f"bandit_report_{self.timestamp}.json")
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Leer reporte
            report_file = self.reports_dir / f"bandit_report_{self.timestamp}.json"
            if report_file.exists():
                with open(report_file) as f:
                    bandit_data = json.load(f)
            else:
                bandit_data = {"results": [], "errors": []}
            
            # Analizar resultados
            high_issues = [r for r in bandit_data.get("results", []) if r.get("issue_severity") == "HIGH"]
            medium_issues = [r for r in bandit_data.get("results", []) if r.get("issue_severity") == "MEDIUM"]
            low_issues = [r for r in bandit_data.get("results", []) if r.get("issue_severity") == "LOW"]
            
            bandit_result = {
                "success": result.returncode == 0,
                "total_issues": len(bandit_data.get("results", [])),
                "high_issues": len(high_issues),
                "medium_issues": len(medium_issues),
                "low_issues": len(low_issues),
                "errors": bandit_data.get("errors", []),
                "report_file": str(report_file)
            }
            
            logger.info(f"✅ Bandit completado: {bandit_result['total_issues']} issues encontrados")
            return bandit_result
            
        except subprocess.TimeoutExpired:
            logger.error("⏰ Bandit timeout")
            return {"success": False, "error": "Timeout"}
        except FileNotFoundError:
            logger.error("❌ Bandit no encontrado. Instalar con: pip install bandit")
            return {"success": False, "error": "Bandit not installed"}
        except Exception as e:
            logger.error(f"❌ Error ejecutando Bandit: {e}")
            return {"success": False, "error": str(e)}
    
    def run_safety(self) -> Dict[str, Any]:
        """Ejecutar Safety para verificar vulnerabilidades en dependencias"""
        logger.info("🔍 Ejecutando Safety dependency scanner...")
        
        try:
            # Ejecutar Safety
            cmd = [
                "safety", 
                "check",
                "--json",
                "--output", str(self.reports_dir / f"safety_report_{self.timestamp}.json")
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            # Leer reporte
            report_file = self.reports_dir / f"safety_report_{self.timestamp}.json"
            if report_file.exists():
                with open(report_file) as f:
                    safety_data = json.load(f)
            else:
                safety_data = []
            
            # Analizar resultados
            vulnerabilities = []
            for item in safety_data:
                if isinstance(item, dict) and "vulnerabilities" in item:
                    vulnerabilities.extend(item["vulnerabilities"])
            
            safety_result = {
                "success": result.returncode == 0,
                "vulnerabilities_found": len(vulnerabilities),
                "vulnerabilities": vulnerabilities,
                "report_file": str(report_file)
            }
            
            logger.info(f"✅ Safety completado: {safety_result['vulnerabilities_found']} vulnerabilidades encontradas")
            return safety_result
            
        except subprocess.TimeoutExpired:
            logger.error("⏰ Safety timeout")
            return {"success": False, "error": "Timeout"}
        except FileNotFoundError:
            logger.error("❌ Safety no encontrado. Instalar con: pip install safety")
            return {"success": False, "error": "Safety not installed"}
        except Exception as e:
            logger.error(f"❌ Error ejecutando Safety: {e}")
            return {"success": False, "error": str(e)}
    
    def run_semgrep(self) -> Dict[str, Any]:
        """Ejecutar Semgrep para análisis de código estático"""
        logger.info("🔍 Ejecutando Semgrep static analysis...")
        
        try:
            # Ejecutar Semgrep
            cmd = [
                "semgrep",
                "--config=auto",
                "--json",
                "--output", str(self.reports_dir / f"semgrep_report_{self.timestamp}.json"),
                str(self.project_root / "app")
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            # Leer reporte
            report_file = self.reports_dir / f"semgrep_report_{self.timestamp}.json"
            if report_file.exists():
                with open(report_file) as f:
                    semgrep_data = json.load(f)
            else:
                semgrep_data = {"results": []}
            
            # Analizar resultados
            results = semgrep_data.get("results", [])
            high_findings = [r for r in results if r.get("extra", {}).get("severity") == "ERROR"]
            medium_findings = [r for r in results if r.get("extra", {}).get("severity") == "WARNING"]
            
            semgrep_result = {
                "success": result.returncode == 0,
                "total_findings": len(results),
                "high_findings": len(high_findings),
                "medium_findings": len(medium_findings),
                "findings": results,
                "report_file": str(report_file)
            }
            
            logger.info(f"✅ Semgrep completado: {semgrep_result['total_findings']} findings encontrados")
            return semgrep_result
            
        except subprocess.TimeoutExpired:
            logger.error("⏰ Semgrep timeout")
            return {"success": False, "error": "Timeout"}
        except FileNotFoundError:
            logger.error("❌ Semgrep no encontrado. Instalar con: pip install semgrep")
            return {"success": False, "error": "Semgrep not installed"}
        except Exception as e:
            logger.error(f"❌ Error ejecutando Semgrep: {e}")
            return {"success": False, "error": str(e)}
    
    def check_secrets(self) -> Dict[str, Any]:
        """Verificar secretos hardcodeados usando detect-secrets"""
        logger.info("🔍 Ejecutando detect-secrets...")
        
        try:
            # Ejecutar detect-secrets
            cmd = [
                "detect-secrets",
                "scan",
                "--all-files",
                "--baseline", str(self.reports_dir / f"secrets_baseline_{self.timestamp}.json"),
                str(self.project_root)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Leer baseline
            baseline_file = self.reports_dir / f"secrets_baseline_{self.timestamp}.json"
            if baseline_file.exists():
                with open(baseline_file) as f:
                    secrets_data = json.load(f)
            else:
                secrets_data = {"results": {}}
            
            # Contar secretos encontrados
            secrets_count = len(secrets_data.get("results", {}))
            
            secrets_result = {
                "success": result.returncode == 0,
                "secrets_found": secrets_count,
                "baseline_file": str(baseline_file),
                "secrets": secrets_data.get("results", {})
            }
            
            logger.info(f"✅ Detect-secrets completado: {secrets_result['secrets_found']} secretos encontrados")
            return secrets_result
            
        except subprocess.TimeoutExpired:
            logger.error("⏰ Detect-secrets timeout")
            return {"success": False, "error": "Timeout"}
        except FileNotFoundError:
            logger.error("❌ Detect-secrets no encontrado. Instalar con: pip install detect-secrets")
            return {"success": False, "error": "Detect-secrets not installed"}
        except Exception as e:
            logger.error(f"❌ Error ejecutando detect-secrets: {e}")
            return {"success": False, "error": str(e)}
    
    def run_all_scans(self) -> Dict[str, Any]:
        """Ejecutar todos los scans de seguridad"""
        logger.info("🚀 Iniciando security scanning completo...")
        
        # Ejecutar todos los scans
        self.results = {
            "timestamp": self.timestamp,
            "project_root": str(self.project_root),
            "bandit": self.run_bandit(),
            "safety": self.run_safety(),
            "semgrep": self.run_semgrep(),
            "secrets": self.check_secrets()
        }
        
        # Generar reporte consolidado
        self.generate_consolidated_report()
        
        return self.results
    
    def generate_consolidated_report(self):
        """Generar reporte consolidado de seguridad"""
        report_file = self.reports_dir / f"security_report_{self.timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Generar reporte en texto
        text_report = self.reports_dir / f"security_report_{self.timestamp}.txt"
        with open(text_report, 'w') as f:
            f.write("🔒 SECURITY SCANNING REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Timestamp: {self.timestamp}\n")
            f.write(f"Project: {self.project_root}\n\n")
            
            # Bandit results
            f.write("📊 BANDIT RESULTS\n")
            f.write("-" * 20 + "\n")
            bandit = self.results.get("bandit", {})
            f.write(f"Total Issues: {bandit.get('total_issues', 0)}\n")
            f.write(f"High Issues: {bandit.get('high_issues', 0)}\n")
            f.write(f"Medium Issues: {bandit.get('medium_issues', 0)}\n")
            f.write(f"Low Issues: {bandit.get('low_issues', 0)}\n\n")
            
            # Safety results
            f.write("📦 SAFETY RESULTS\n")
            f.write("-" * 20 + "\n")
            safety = self.results.get("safety", {})
            f.write(f"Vulnerabilities: {safety.get('vulnerabilities_found', 0)}\n\n")
            
            # Semgrep results
            f.write("🔍 SEMGREP RESULTS\n")
            f.write("-" * 20 + "\n")
            semgrep = self.results.get("semgrep", {})
            f.write(f"Total Findings: {semgrep.get('total_findings', 0)}\n")
            f.write(f"High Findings: {semgrep.get('high_findings', 0)}\n")
            f.write(f"Medium Findings: {semgrep.get('medium_findings', 0)}\n\n")
            
            # Secrets results
            f.write("🔐 SECRETS SCAN\n")
            f.write("-" * 20 + "\n")
            secrets = self.results.get("secrets", {})
            f.write(f"Secrets Found: {secrets.get('secrets_found', 0)}\n\n")
            
            # Summary
            f.write("📋 SUMMARY\n")
            f.write("-" * 20 + "\n")
            total_issues = (
                bandit.get('high_issues', 0) + 
                safety.get('vulnerabilities_found', 0) + 
                semgrep.get('high_findings', 0) + 
                secrets.get('secrets_found', 0)
            )
            f.write(f"Total Critical Issues: {total_issues}\n")
            
            if total_issues == 0:
                f.write("✅ No critical security issues found!\n")
            else:
                f.write("⚠️ Critical security issues require attention!\n")
        
        logger.info(f"📄 Reporte consolidado generado: {report_file}")
        logger.info(f"📄 Reporte de texto generado: {text_report}")


def main():
    """Función principal"""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()
    
    scanner = SecurityScanner(project_root)
    results = scanner.run_all_scans()
    
    # Mostrar resumen
    print("\n" + "=" * 50)
    print("🔒 SECURITY SCANNING COMPLETED")
    print("=" * 50)
    
    bandit = results.get("bandit", {})
    safety = results.get("safety", {})
    semgrep = results.get("semgrep", {})
    secrets = results.get("secrets", {})
    
    print(f"Bandit Issues: {bandit.get('total_issues', 0)}")
    print(f"Safety Vulnerabilities: {safety.get('vulnerabilities_found', 0)}")
    print(f"Semgrep Findings: {semgrep.get('total_findings', 0)}")
    print(f"Secrets Found: {secrets.get('secrets_found', 0)}")
    
    total_critical = (
        bandit.get('high_issues', 0) + 
        safety.get('vulnerabilities_found', 0) + 
        semgrep.get('high_findings', 0) + 
        secrets.get('secrets_found', 0)
    )
    
    if total_critical == 0:
        print("\n✅ No critical security issues found!")
    else:
        print(f"\n⚠️ {total_critical} critical security issues require attention!")
    
    print(f"\n📄 Reports saved in: {scanner.reports_dir}")


if __name__ == "__main__":
    main()
