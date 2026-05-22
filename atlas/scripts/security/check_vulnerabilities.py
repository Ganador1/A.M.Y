#!/usr/bin/env python3
"""
Vulnerability Checker - Verificar vulnerabilidades de seguridad
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional


class VulnerabilityChecker:
    """Verificador de vulnerabilidades de seguridad"""
    
    def __init__(self):
        self.critical_issues = []
        self.high_issues = []
        self.medium_issues = []
        self.low_issues = []
    
    def check_bandit_report(self, bandit_file: str) -> Dict[str, Any]:
        """Verificar reporte de Bandit"""
        if not Path(bandit_file).exists():
            return {"error": "Bandit report file not found"}
        
        try:
            with open(bandit_file, 'r') as f:
                bandit_data = json.load(f)
            
            results = bandit_data.get('results', [])
            
            # Clasificar por severidad
            for result in results:
                severity = result.get('issue_severity', 'UNKNOWN')
                confidence = result.get('issue_confidence', 'UNKNOWN')
                
                issue = {
                    'tool': 'bandit',
                    'severity': severity,
                    'confidence': confidence,
                    'issue_text': result.get('issue_text', ''),
                    'filename': result.get('filename', ''),
                    'line_number': result.get('line_number', 0),
                    'test_id': result.get('test_id', '')
                }
                
                if severity == 'HIGH':
                    self.high_issues.append(issue)
                elif severity == 'MEDIUM':
                    self.medium_issues.append(issue)
                else:
                    self.low_issues.append(issue)
            
            return {
                'total_issues': len(results),
                'high_issues': len([r for r in results if r.get('issue_severity') == 'HIGH']),
                'medium_issues': len([r for r in results if r.get('issue_severity') == 'MEDIUM']),
                'low_issues': len([r for r in results if r.get('issue_severity') == 'LOW'])
            }
            
        except Exception as e:
            return {"error": f"Error parsing Bandit report: {e}"}
    
    def check_safety_report(self, safety_file: str) -> Dict[str, Any]:
        """Verificar reporte de Safety"""
        if not Path(safety_file).exists():
            return {"error": "Safety report file not found"}
        
        try:
            with open(safety_file, 'r') as f:
                safety_data = json.load(f)
            
            # Clasificar vulnerabilidades
            for vuln in safety_data:
                severity = self._classify_safety_severity(vuln)
                
                issue = {
                    'tool': 'safety',
                    'severity': severity,
                    'package': vuln.get('package', ''),
                    'vulnerability_id': vuln.get('vulnerability_id', ''),
                    'advisory': vuln.get('advisory', ''),
                    'specs': vuln.get('specs', '')
                }
                
                if severity == 'CRITICAL':
                    self.critical_issues.append(issue)
                elif severity == 'HIGH':
                    self.high_issues.append(issue)
                elif severity == 'MEDIUM':
                    self.medium_issues.append(issue)
                else:
                    self.low_issues.append(issue)
            
            return {
                'total_vulnerabilities': len(safety_data),
                'critical_vulnerabilities': len([v for v in safety_data if self._classify_safety_severity(v) == 'CRITICAL']),
                'high_vulnerabilities': len([v for v in safety_data if self._classify_safety_severity(v) == 'HIGH']),
                'medium_vulnerabilities': len([v for v in safety_data if self._classify_safety_severity(v) == 'MEDIUM']),
                'low_vulnerabilities': len([v for v in safety_data if self._classify_safety_severity(v) == 'LOW'])
            }
            
        except Exception as e:
            return {"error": f"Error parsing Safety report: {e}"}
    
    def check_trivy_report(self, trivy_file: str) -> Dict[str, Any]:
        """Verificar reporte de Trivy"""
        if not Path(trivy_file).exists():
            return {"error": "Trivy report file not found"}
        
        try:
            with open(trivy_file, 'r') as f:
                trivy_data = json.load(f)
            
            # Trivy SARIF format
            runs = trivy_data.get('runs', [])
            total_vulnerabilities = 0
            critical_vulnerabilities = 0
            high_vulnerabilities = 0
            medium_vulnerabilities = 0
            low_vulnerabilities = 0
            
            for run in runs:
                results = run.get('results', [])
                for result in results:
                    total_vulnerabilities += 1
                    
                    # Obtener severidad
                    severity = result.get('level', 'UNKNOWN')
                    if severity == 'error':
                        severity = 'CRITICAL'
                    elif severity == 'warning':
                        severity = 'HIGH'
                    elif severity == 'note':
                        severity = 'MEDIUM'
                    else:
                        severity = 'LOW'
                    
                    issue = {
                        'tool': 'trivy',
                        'severity': severity,
                        'rule_id': result.get('ruleId', ''),
                        'message': result.get('message', {}).get('text', ''),
                        'locations': result.get('locations', [])
                    }
                    
                    if severity == 'CRITICAL':
                        self.critical_issues.append(issue)
                        critical_vulnerabilities += 1
                    elif severity == 'HIGH':
                        self.high_issues.append(issue)
                        high_vulnerabilities += 1
                    elif severity == 'MEDIUM':
                        self.medium_issues.append(issue)
                        medium_vulnerabilities += 1
                    else:
                        self.low_issues.append(issue)
                        low_vulnerabilities += 1
            
            return {
                'total_vulnerabilities': total_vulnerabilities,
                'critical_vulnerabilities': critical_vulnerabilities,
                'high_vulnerabilities': high_vulnerabilities,
                'medium_vulnerabilities': medium_vulnerabilities,
                'low_vulnerabilities': low_vulnerabilities
            }
            
        except Exception as e:
            return {"error": f"Error parsing Trivy report: {e}"}
    
    def _classify_safety_severity(self, vuln: Dict[str, Any]) -> str:
        """Clasificar severidad de vulnerabilidad de Safety"""
        # Clasificación basada en CVE y advisory
        advisory = vuln.get('advisory', '').lower()
        vulnerability_id = vuln.get('vulnerability_id', '').lower()
        
        # Palabras clave para clasificación
        critical_keywords = ['remote code execution', 'rce', 'arbitrary code execution', 'privilege escalation']
        high_keywords = ['sql injection', 'xss', 'csrf', 'authentication bypass', 'information disclosure']
        medium_keywords = ['denial of service', 'dos', 'memory leak', 'buffer overflow']
        
        # Verificar keywords críticos
        for keyword in critical_keywords:
            if keyword in advisory or keyword in vulnerability_id:
                return 'CRITICAL'
        
        # Verificar keywords de alto riesgo
        for keyword in high_keywords:
            if keyword in advisory or keyword in vulnerability_id:
                return 'HIGH'
        
        # Verificar keywords de riesgo medio
        for keyword in medium_keywords:
            if keyword in advisory or keyword in vulnerability_id:
                return 'MEDIUM'
        
        # Por defecto, clasificar como bajo riesgo
        return 'LOW'
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generar reporte resumen de vulnerabilidades"""
        return {
            'summary': {
                'critical_issues': len(self.critical_issues),
                'high_issues': len(self.high_issues),
                'medium_issues': len(self.medium_issues),
                'low_issues': len(self.low_issues),
                'total_issues': len(self.critical_issues) + len(self.high_issues) + len(self.medium_issues) + len(self.low_issues)
            },
            'critical_issues': self.critical_issues[:10],  # Top 10
            'high_issues': self.high_issues[:10],  # Top 10
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generar recomendaciones basadas en vulnerabilidades encontradas"""
        recommendations = []
        
        if self.critical_issues:
            recommendations.append("🚨 CRÍTICO: Se encontraron vulnerabilidades críticas que requieren atención inmediata")
            recommendations.append("   - Actualizar dependencias vulnerables")
            recommendations.append("   - Revisar y corregir código con vulnerabilidades de seguridad")
        
        if self.high_issues:
            recommendations.append("⚠️ ALTO: Se encontraron vulnerabilidades de alto riesgo")
            recommendations.append("   - Priorizar la corrección de estas vulnerabilidades")
            recommendations.append("   - Considerar implementar medidas de mitigación temporales")
        
        if self.medium_issues:
            recommendations.append("🟡 MEDIO: Se encontraron vulnerabilidades de riesgo medio")
            recommendations.append("   - Planificar la corrección en el próximo ciclo de desarrollo")
            recommendations.append("   - Monitorear estas vulnerabilidades")
        
        if not self.critical_issues and not self.high_issues:
            recommendations.append("✅ No se encontraron vulnerabilidades críticas o de alto riesgo")
            recommendations.append("   - Continuar con el monitoreo regular de seguridad")
        
        return recommendations
    
    def should_fail_build(self, fail_on_critical: bool = True, fail_on_high: bool = False) -> bool:
        """Determinar si el build debe fallar basado en vulnerabilidades"""
        if fail_on_critical and self.critical_issues:
            return True
        if fail_on_high and self.high_issues:
            return True
        return False


def main():
    """Función principal del script"""
    parser = argparse.ArgumentParser(description="Verificar vulnerabilidades de seguridad")
    parser.add_argument("--bandit", type=str, help="Archivo de reporte de Bandit")
    parser.add_argument("--safety", type=str, help="Archivo de reporte de Safety")
    parser.add_argument("--trivy", type=str, help="Archivo de reporte de Trivy")
    parser.add_argument("--fail-on-critical", action="store_true", help="Fallar si hay vulnerabilidades críticas")
    parser.add_argument("--fail-on-high", action="store_true", help="Fallar si hay vulnerabilidades de alto riesgo")
    parser.add_argument("--output", type=str, help="Archivo de salida para el reporte")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="Formato de salida")
    
    args = parser.parse_args()
    
    checker = VulnerabilityChecker()
    
    # Verificar reportes disponibles
    bandit_result = {}
    safety_result = {}
    trivy_result = {}
    
    if args.bandit:
        bandit_result = checker.check_bandit_report(args.bandit)
        if "error" in bandit_result:
            print(f"⚠️ Warning: {bandit_result['error']}")
    
    if args.safety:
        safety_result = checker.check_safety_report(args.safety)
        if "error" in safety_result:
            print(f"⚠️ Warning: {safety_result['error']}")
    
    if args.trivy:
        trivy_result = checker.check_trivy_report(args.trivy)
        if "error" in trivy_result:
            print(f"⚠️ Warning: {trivy_result['error']}")
    
    # Generar reporte resumen
    summary = checker.generate_summary_report()
    
    # Mostrar resultados
    if args.format == "json":
        output = json.dumps(summary, indent=2, ensure_ascii=False)
    else:
        output = generate_text_report(summary, bandit_result, safety_result, trivy_result)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Reporte guardado en: {args.output}")
    else:
        print(output)
    
    # Determinar si el build debe fallar
    should_fail = checker.should_fail_build(args.fail_on_critical, args.fail_on_high)
    
    if should_fail:
        print("\n❌ BUILD FAILED: Vulnerabilidades de seguridad encontradas")
        sys.exit(1)
    else:
        print("\n✅ Security check passed")
        sys.exit(0)


def generate_text_report(summary: Dict[str, Any], bandit_result: Dict[str, Any], 
                        safety_result: Dict[str, Any], trivy_result: Dict[str, Any]) -> str:
    """Generar reporte en formato texto"""
    report = []
    report.append("🔒 SECURITY VULNERABILITY REPORT")
    report.append("=" * 50)
    report.append("")
    
    # Resumen
    summary_data = summary['summary']
    report.append("📊 RESUMEN:")
    report.append(f"   Vulnerabilidades Críticas: {summary_data['critical_issues']}")
    report.append(f"   Vulnerabilidades Altas: {summary_data['high_issues']}")
    report.append(f"   Vulnerabilidades Medias: {summary_data['medium_issues']}")
    report.append(f"   Vulnerabilidades Bajas: {summary_data['low_issues']}")
    report.append(f"   Total: {summary_data['total_issues']}")
    report.append("")
    
    # Resultados por herramienta
    if bandit_result and "error" not in bandit_result:
        report.append("🐍 BANDIT (Python Security Linter):")
        report.append(f"   Total Issues: {bandit_result.get('total_issues', 0)}")
        report.append(f"   High: {bandit_result.get('high_issues', 0)}")
        report.append(f"   Medium: {bandit_result.get('medium_issues', 0)}")
        report.append(f"   Low: {bandit_result.get('low_issues', 0)}")
        report.append("")
    
    if safety_result and "error" not in safety_result:
        report.append("🛡️ SAFETY (Dependency Check):")
        report.append(f"   Total Vulnerabilities: {safety_result.get('total_vulnerabilities', 0)}")
        report.append(f"   Critical: {safety_result.get('critical_vulnerabilities', 0)}")
        report.append(f"   High: {safety_result.get('high_vulnerabilities', 0)}")
        report.append(f"   Medium: {safety_result.get('medium_vulnerabilities', 0)}")
        report.append(f"   Low: {safety_result.get('low_vulnerabilities', 0)}")
        report.append("")
    
    if trivy_result and "error" not in trivy_result:
        report.append("🔍 TRIVY (Container Security):")
        report.append(f"   Total Vulnerabilities: {trivy_result.get('total_vulnerabilities', 0)}")
        report.append(f"   Critical: {trivy_result.get('critical_vulnerabilities', 0)}")
        report.append(f"   High: {trivy_result.get('high_vulnerabilities', 0)}")
        report.append(f"   Medium: {trivy_result.get('medium_vulnerabilities', 0)}")
        report.append(f"   Low: {trivy_result.get('low_vulnerabilities', 0)}")
        report.append("")
    
    # Vulnerabilidades críticas
    if summary['critical_issues']:
        report.append("🚨 VULNERABILIDADES CRÍTICAS:")
        for issue in summary['critical_issues'][:5]:  # Top 5
            report.append(f"   - {issue['tool'].upper()}: {issue.get('issue_text', issue.get('message', 'N/A'))}")
        report.append("")
    
    # Vulnerabilidades altas
    if summary['high_issues']:
        report.append("⚠️ VULNERABILIDADES ALTAS:")
        for issue in summary['high_issues'][:5]:  # Top 5
            report.append(f"   - {issue['tool'].upper()}: {issue.get('issue_text', issue.get('message', 'N/A'))}")
        report.append("")
    
    # Recomendaciones
    report.append("💡 RECOMENDACIONES:")
    for rec in summary['recommendations']:
        report.append(f"   {rec}")
    report.append("")
    
    return "\n".join(report)


if __name__ == "__main__":
    main()
