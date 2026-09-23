#!/usr/bin/env python3
"""
Manual Penetration Testing Script - AXIOM ATLAS
==============================================

Script para realizar penetration testing manual automatizado.
Incluye tests para autenticación, inyección, y lógica de negocio.

Author: AXIOM Team
Date: 2025-01-01
Version: 1.0.0
"""

import requests
import json
import time
import random
import string
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Resultado de un test de penetración"""
    test_name: str
    success: bool
    vulnerability_found: bool
    severity: str  # HIGH, MEDIUM, LOW, INFO
    description: str
    payload: Optional[str] = None
    response_code: Optional[int] = None
    response_time: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


class PenetrationTester:
    """Tester de penetración manual automatizado"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.results: List[TestResult] = []
        
        # Headers por defecto
        self.session.headers.update({
            'User-Agent': 'AXIOM-PenTest/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def run_test(self, test_func, test_name: str) -> TestResult:
        """Ejecutar un test individual"""
        logger.info(f"🔍 Ejecutando test: {test_name}")
        
        try:
            result = test_func()
            self.results.append(result)
            return result
        except Exception as e:
            logger.error(f"❌ Error en test {test_name}: {e}")
            error_result = TestResult(
                test_name=test_name,
                success=False,
                vulnerability_found=False,
                severity="INFO",
                description=f"Test failed with error: {e}"
            )
            self.results.append(error_result)
            return error_result
    
    def test_authentication_bypass(self) -> TestResult:
        """Test de bypass de autenticación"""
        vulnerabilities = []
        
        # Test 1: JWT token manipulation
        try:
            # Intentar acceder a endpoint protegido sin token
            response = self.session.get(f"{self.base_url}/api/protected")
            if response.status_code == 200:
                vulnerabilities.append("Endpoint protegido accesible sin autenticación")
        except:
            pass
        
        # Test 2: JWT token malformado
        try:
            headers = {'Authorization': 'Bearer invalid_token'}
            response = self.session.get(f"{self.base_url}/api/protected", headers=headers)
            if response.status_code == 200:
                vulnerabilities.append("JWT malformado aceptado")
        except:
            pass
        
        # Test 3: SQL injection en login
        sql_payloads = [
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT 1,2,3--",
            "'; DROP TABLE users; --"
        ]
        
        for payload in sql_payloads:
            try:
                data = {"username": payload, "password": "test"}
                response = self.session.post(f"{self.base_url}/api/auth/login", json=data)
                if response.status_code == 200 and "error" not in response.text.lower():
                    vulnerabilities.append(f"SQL injection posible en login: {payload}")
            except:
                pass
        
        severity = "HIGH" if vulnerabilities else "INFO"
        return TestResult(
            test_name="Authentication Bypass",
            success=True,
            vulnerability_found=len(vulnerabilities) > 0,
            severity=severity,
            description=f"Found {len(vulnerabilities)} authentication issues",
            details={"vulnerabilities": vulnerabilities}
        )
    
    def test_sql_injection(self) -> TestResult:
        """Test de inyección SQL"""
        vulnerabilities = []
        
        # Endpoints comunes para SQL injection
        endpoints = [
            "/api/experiments",
            "/api/models", 
            "/api/data",
            "/api/users",
            "/api/reports"
        ]
        
        sql_payloads = [
            "' OR '1'='1",
            "1' UNION SELECT 1,2,3--",
            "'; DROP TABLE experiments; --",
            "' AND 1=1--",
            "' AND 1=2--"
        ]
        
        for endpoint in endpoints:
            for payload in sql_payloads:
                try:
                    # Test en query parameters
                    response = self.session.get(f"{self.base_url}{endpoint}?id={payload}")
                    if self._is_sql_injection_response(response):
                        vulnerabilities.append(f"SQL injection en {endpoint} con payload: {payload}")
                    
                    # Test en POST data
                    data = {"id": payload, "name": "test"}
                    response = self.session.post(f"{self.base_url}{endpoint}", json=data)
                    if self._is_sql_injection_response(response):
                        vulnerabilities.append(f"SQL injection en POST {endpoint} con payload: {payload}")
                        
                except:
                    pass
        
        severity = "HIGH" if vulnerabilities else "INFO"
        return TestResult(
            test_name="SQL Injection",
            success=True,
            vulnerability_found=len(vulnerabilities) > 0,
            severity=severity,
            description=f"Found {len(vulnerabilities)} SQL injection vulnerabilities",
            details={"vulnerabilities": vulnerabilities}
        )
    
    def test_command_injection(self) -> TestResult:
        """Test de inyección de comandos"""
        vulnerabilities = []
        
        # Payloads de command injection
        cmd_payloads = [
            "; ls",
            "| whoami",
            "&& cat /etc/passwd",
            "`id`",
            "$(whoami)",
            "; cat /etc/passwd",
            "| cat /etc/hosts"
        ]
        
        # Endpoints que podrían ejecutar comandos
        endpoints = [
            "/api/experiments/run",
            "/api/models/train",
            "/api/data/process",
            "/api/system/command"
        ]
        
        for endpoint in endpoints:
            for payload in cmd_payloads:
                try:
                    data = {"command": payload, "input": "test"}
                    response = self.session.post(f"{self.base_url}{endpoint}", json=data)
                    
                    if self._is_command_injection_response(response):
                        vulnerabilities.append(f"Command injection en {endpoint} con payload: {payload}")
                        
                except:
                    pass
        
        severity = "HIGH" if vulnerabilities else "INFO"
        return TestResult(
            test_name="Command Injection",
            success=True,
            vulnerability_found=len(vulnerabilities) > 0,
            severity=severity,
            description=f"Found {len(vulnerabilities)} command injection vulnerabilities",
            details={"vulnerabilities": vulnerabilities}
        )
    
    def test_path_traversal(self) -> TestResult:
        """Test de path traversal"""
        vulnerabilities = []
        
        # Payloads de path traversal
        path_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd"
        ]
        
        # Endpoints de archivos
        file_endpoints = [
            "/api/files/download",
            "/api/data/download",
            "/api/models/download",
            "/api/reports/download"
        ]
        
        for endpoint in file_endpoints:
            for payload in path_payloads:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}?file={payload}")
                    
                    if self._is_path_traversal_response(response):
                        vulnerabilities.append(f"Path traversal en {endpoint} con payload: {payload}")
                        
                except:
                    pass
        
        severity = "HIGH" if vulnerabilities else "INFO"
        return TestResult(
            test_name="Path Traversal",
            success=True,
            vulnerability_found=len(vulnerabilities) > 0,
            severity=severity,
            description=f"Found {len(vulnerabilities)} path traversal vulnerabilities",
            details={"vulnerabilities": vulnerabilities}
        )
    
    def test_xss(self) -> TestResult:
        """Test de Cross-Site Scripting (XSS)"""
        vulnerabilities = []
        
        # Payloads XSS
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//"
        ]
        
        # Endpoints que podrían ser vulnerables a XSS
        xss_endpoints = [
            "/api/experiments",
            "/api/comments",
            "/api/feedback",
            "/api/search"
        ]
        
        for endpoint in xss_endpoints:
            for payload in xss_payloads:
                try:
                    # Test en POST data
                    data = {"name": payload, "description": "test"}
                    response = self.session.post(f"{self.base_url}{endpoint}", json=data)
                    
                    if payload in response.text:
                        vulnerabilities.append(f"XSS posible en {endpoint} con payload: {payload}")
                        
                except:
                    pass
        
        severity = "MEDIUM" if vulnerabilities else "INFO"
        return TestResult(
            test_name="Cross-Site Scripting (XSS)",
            success=True,
            vulnerability_found=len(vulnerabilities) > 0,
            severity=severity,
            description=f"Found {len(vulnerabilities)} potential XSS vulnerabilities",
            details={"vulnerabilities": vulnerabilities}
        )
    
    def test_rate_limiting_bypass(self) -> TestResult:
        """Test de bypass de rate limiting"""
        vulnerabilities = []
        
        # Test de rate limiting en endpoint sensible
        sensitive_endpoints = [
            "/api/auth/login",
            "/api/auth/register",
            "/api/experiments/create"
        ]
        
        for endpoint in sensitive_endpoints:
            try:
                # Enviar muchas requests rápidamente
                success_count = 0
                for i in range(100):
                    response = self.session.post(f"{self.base_url}{endpoint}", json={"test": "data"})
                    if response.status_code == 200:
                        success_count += 1
                    time.sleep(0.01)  # Pequeña pausa
                
                if success_count > 50:  # Más del 50% exitosas
                    vulnerabilities.append(f"Rate limiting bypass posible en {endpoint}")
                    
            except:
                pass
        
        severity = "MEDIUM" if vulnerabilities else "INFO"
        return TestResult(
            test_name="Rate Limiting Bypass",
            success=True,
            vulnerability_found=len(vulnerabilities) > 0,
            severity=severity,
            description=f"Found {len(vulnerabilities)} rate limiting bypass issues",
            details={"vulnerabilities": vulnerabilities}
        )
    
    def test_information_disclosure(self) -> TestResult:
        """Test de divulgación de información"""
        vulnerabilities = []
        
        # Endpoints que podrían divulgar información sensible
        info_endpoints = [
            "/api/debug",
            "/api/status",
            "/api/health",
            "/api/metrics",
            "/api/logs",
            "/.env",
            "/config.json",
            "/backup.sql"
        ]
        
        for endpoint in info_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                
                if response.status_code == 200:
                    content = response.text.lower()
                    
                    # Buscar información sensible
                    sensitive_patterns = [
                        "password", "secret", "key", "token", "api_key",
                        "database", "connection", "config", "debug"
                    ]
                    
                    for pattern in sensitive_patterns:
                        if pattern in content:
                            vulnerabilities.append(f"Información sensible expuesta en {endpoint}: {pattern}")
                            break
                            
            except:
                pass
        
        severity = "MEDIUM" if vulnerabilities else "INFO"
        return TestResult(
            test_name="Information Disclosure",
            success=True,
            vulnerability_found=len(vulnerabilities) > 0,
            severity=severity,
            description=f"Found {len(vulnerabilities)} information disclosure issues",
            details={"vulnerabilities": vulnerabilities}
        )
    
    def _is_sql_injection_response(self, response) -> bool:
        """Detectar si la respuesta indica SQL injection"""
        if response.status_code != 200:
            return False
        
        content = response.text.lower()
        sql_errors = [
            "sql syntax", "mysql", "postgresql", "sqlite", "oracle",
            "database error", "sql error", "query failed"
        ]
        
        return any(error in content for error in sql_errors)
    
    def _is_command_injection_response(self, response) -> bool:
        """Detectar si la respuesta indica command injection"""
        if response.status_code != 200:
            return False
        
        content = response.text.lower()
        command_indicators = [
            "uid=", "gid=", "root:", "bin/bash", "bin/sh",
            "command not found", "permission denied"
        ]
        
        return any(indicator in content for indicator in command_indicators)
    
    def _is_path_traversal_response(self, response) -> bool:
        """Detectar si la respuesta indica path traversal"""
        if response.status_code != 200:
            return False
        
        content = response.text.lower()
        path_indicators = [
            "root:", "bin:", "etc/passwd", "windows/system32",
            "permission denied", "no such file"
        ]
        
        return any(indicator in content for indicator in path_indicators)
    
    def run_all_tests(self) -> List[TestResult]:
        """Ejecutar todos los tests de penetración"""
        logger.info("🚀 Iniciando penetration testing completo...")
        
        tests = [
            (self.test_authentication_bypass, "Authentication Bypass"),
            (self.test_sql_injection, "SQL Injection"),
            (self.test_command_injection, "Command Injection"),
            (self.test_path_traversal, "Path Traversal"),
            (self.test_xss, "Cross-Site Scripting"),
            (self.test_rate_limiting_bypass, "Rate Limiting Bypass"),
            (self.test_information_disclosure, "Information Disclosure")
        ]
        
        for test_func, test_name in tests:
            self.run_test(test_func, test_name)
            time.sleep(1)  # Pausa entre tests
        
        return self.results
    
    def generate_report(self) -> str:
        """Generar reporte de penetration testing"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Contar vulnerabilidades por severidad
        high_count = len([r for r in self.results if r.severity == "HIGH"])
        medium_count = len([r for r in self.results if r.severity == "MEDIUM"])
        low_count = len([r for r in self.results if r.severity == "LOW"])
        info_count = len([r for r in self.results if r.severity == "INFO"])
        
        report = f"""
🔒 PENETRATION TESTING REPORT
============================

Timestamp: {timestamp}
Target: {self.base_url}
Total Tests: {len(self.results)}

📊 VULNERABILITY SUMMARY
- HIGH: {high_count}
- MEDIUM: {medium_count}  
- LOW: {low_count}
- INFO: {info_count}

📋 DETAILED RESULTS
"""
        
        for result in self.results:
            status = "🔴 VULNERABLE" if result.vulnerability_found else "✅ SECURE"
            report += f"\n{result.test_name}: {status} ({result.severity})\n"
            report += f"  {result.description}\n"
            
            if result.details and result.details.get("vulnerabilities"):
                for vuln in result.details["vulnerabilities"]:
                    report += f"    - {vuln}\n"
        
        # Guardar reporte
        report_file = f"penetration_test_report_{timestamp}.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"📄 Reporte guardado en: {report_file}")
        return report


def main():
    """Función principal"""
    import sys
    
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    tester = PenetrationTester(base_url)
    results = tester.run_all_tests()
    
    report = tester.generate_report()
    print(report)
    
    # Mostrar resumen
    high_count = len([r for r in results if r.severity == "HIGH"])
    medium_count = len([r for r in results if r.severity == "MEDIUM"])
    
    if high_count > 0:
        print(f"\n⚠️ {high_count} HIGH severity vulnerabilities found!")
    elif medium_count > 0:
        print(f"\n⚠️ {medium_count} MEDIUM severity vulnerabilities found!")
    else:
        print("\n✅ No critical vulnerabilities found!")


if __name__ == "__main__":
    main()
