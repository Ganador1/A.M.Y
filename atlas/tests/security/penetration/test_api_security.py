"""
Security penetration testing for API endpoints and authentication.

Propósito:
    Simular ataques de penetración contra endpoints de API para identificar
    vulnerabilidades de seguridad comunes como injection, authentication bypass,
    rate limiting, input validation, y authorization flaws.

Coverage:
    - SQL injection attempts on database-connected endpoints
    - NoSQL injection for document databases
    - Authentication bypass attempts
    - Authorization escalation testing
    - Rate limiting validation
    - Input validation and sanitization testing
    - CORS policy validation
    - Header security validation
    - Session management security
    - API versioning security
"""

import pytest
import asyncio
import aiohttp
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from unittest.mock import patch, MagicMock
import base64


@dataclass
class SecurityTestResult:
    """Container for security test results."""
    test_name: str
    endpoint: str
    attack_type: str
    payload: str
    status_code: int
    response_time_ms: float
    vulnerability_detected: bool
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    recommendation: str


@dataclass
class PenetrationTestSuite:
    """Container for penetration test suite results."""
    total_tests: int
    vulnerabilities_found: int
    critical_vulnerabilities: int
    high_vulnerabilities: int
    medium_vulnerabilities: int
    low_vulnerabilities: int
    test_results: List[SecurityTestResult]


class APISecurityTester:
    """Security penetration tester for API endpoints."""

    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self.base_url = base_url
        self.session = None
        self.results: List[SecurityTestResult] = []

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def test_sql_injection(self, endpoint: str, params: Dict[str, str]) -> List[SecurityTestResult]:
        """Test for SQL injection vulnerabilities."""
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "admin'--",
            "admin' /*",
            "' OR 1=1 --",
            "' OR 'a'='a",
            "') OR ('1'='1",
            "' OR 1=1#",
            "'; EXEC sp_configure 'show advanced options', 1 --"
        ]

        results = []
        for payload in sql_payloads:
            for param_name in params.keys():
                test_params = params.copy()
                test_params[param_name] = payload

                result = await self._make_security_request(
                    endpoint=endpoint,
                    method="GET",
                    params=test_params,
                    attack_type="SQL_INJECTION",
                    payload=payload
                )
                results.append(result)

        return results

    async def test_nosql_injection(self, endpoint: str, json_data: Dict[str, Any]) -> List[SecurityTestResult]:
        """Test for NoSQL injection vulnerabilities."""
        nosql_payloads = [
            {"$ne": None},
            {"$gt": ""},
            {"$regex": ".*"},
            {"$where": "this.username == 'admin'"},
            {"$expr": {"$eq": ["$username", "admin"]}},
            {"$or": [{"username": "admin"}, {"role": "admin"}]},
            {"username": {"$in": ["admin", "root", "administrator"]}},
            {"$text": {"$search": "admin"}},
            {"$nor": [{"username": "guest"}]},
            {"password": {"$exists": False}}
        ]

        results = []
        for payload in nosql_payloads:
            for field_name in json_data.keys():
                test_data = json_data.copy()
                test_data[field_name] = payload

                result = await self._make_security_request(
                    endpoint=endpoint,
                    method="POST",
                    json_data=test_data,
                    attack_type="NOSQL_INJECTION",
                    payload=str(payload)
                )
                results.append(result)

        return results

    async def test_authentication_bypass(self, endpoint: str) -> List[SecurityTestResult]:
        """Test authentication bypass attempts."""
        bypass_attempts = [
            # Header manipulation
            {"headers": {"X-Forwarded-User": "admin"}},
            {"headers": {"X-Remote-User": "administrator"}},
            {"headers": {"X-User-ID": "1"}},
            {"headers": {"Authorization": "Bearer fake_token"}},
            {"headers": {"Authorization": "Basic " + base64.b64encode(b"admin:admin").decode()}},

            # Parameter manipulation
            {"params": {"user": "admin", "bypass": "true"}},
            {"params": {"role": "admin"}},
            {"params": {"uid": "0"}},
            {"params": {"admin": "1"}},

            # JSON payload manipulation
            {"json_data": {"user": "admin", "authenticated": True}},
            {"json_data": {"role": "administrator"}},
            {"json_data": {"permissions": ["admin", "read", "write"]}},
        ]

        results = []
        for attempt in bypass_attempts:
            result = await self._make_security_request(
                endpoint=endpoint,
                method="GET",
                headers=attempt.get("headers"),
                params=attempt.get("params"),
                json_data=attempt.get("json_data"),
                attack_type="AUTH_BYPASS",
                payload=str(attempt)
            )
            results.append(result)

        return results

    async def test_authorization_escalation(self, endpoint: str, user_token: str) -> List[SecurityTestResult]:
        """Test authorization escalation vulnerabilities."""
        escalation_attempts = [
            # Role elevation
            {"params": {"role": "admin"}},
            {"params": {"privilege": "administrator"}},
            {"params": {"level": "99"}},
            {"params": {"user_type": "superuser"}},

            # ID manipulation
            {"params": {"user_id": "1"}},  # Try admin user
            {"params": {"account_id": "0"}},  # Try system account
            {"params": {"org_id": "1"}},  # Try different organization

            # Header manipulation with token
            {"headers": {"Authorization": f"Bearer {user_token}", "X-Admin": "true"}},
            {"headers": {"Authorization": f"Bearer {user_token}", "X-Role": "admin"}},
            {"headers": {"Authorization": f"Bearer {user_token}", "X-Elevation": "1"}},
        ]

        results = []
        for attempt in escalation_attempts:
            result = await self._make_security_request(
                endpoint=endpoint,
                method="GET",
                headers=attempt.get("headers"),
                params=attempt.get("params"),
                attack_type="AUTHZ_ESCALATION",
                payload=str(attempt)
            )
            results.append(result)

        return results

    async def test_rate_limiting(self, endpoint: str, requests_per_second: int = 10) -> SecurityTestResult:
        """Test rate limiting effectiveness."""
        start_time = time.time()
        success_count = 0
        rate_limited_count = 0

        # Send rapid requests
        tasks = []
        for _ in range(requests_per_second * 5):  # Send 5 seconds worth of requests rapidly
            task = self._make_simple_request(endpoint)
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for response in responses:
            if isinstance(response, Exception):
                continue

            if hasattr(response, 'status'):
                if response.status < 400:
                    success_count += 1
                elif response.status == 429:  # Too Many Requests
                    rate_limited_count += 1

        end_time = time.time()
        total_time = (end_time - start_time) * 1000

        # Analyze results
        vulnerability_detected = rate_limited_count == 0  # No rate limiting detected
        severity = "HIGH" if vulnerability_detected else "LOW"

        return SecurityTestResult(
            test_name="rate_limiting_test",
            endpoint=endpoint,
            attack_type="RATE_LIMITING",
            payload=f"{requests_per_second * 5} requests in {total_time:.2f}ms",
            status_code=200 if success_count > 0 else 429,
            response_time_ms=total_time,
            vulnerability_detected=vulnerability_detected,
            severity=severity,
            description=f"Sent {len(tasks)} rapid requests. Success: {success_count}, Rate limited: {rate_limited_count}",
            recommendation="Implement rate limiting with appropriate thresholds" if vulnerability_detected else "Rate limiting is properly configured"
        )

    async def test_input_validation(self, endpoint: str, params: Dict[str, str]) -> List[SecurityTestResult]:
        """Test input validation and sanitization."""
        malicious_inputs = [
            # XSS payloads
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//",

            # Path traversal
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",

            # Command injection
            "; ls -la",
            "| cat /etc/passwd",
            "`whoami`",
            "$(id)",

            # Buffer overflow attempts
            "A" * 1000,
            "A" * 10000,
            "\x00" * 100,

            # Format string attacks
            "%s%s%s%s",
            "%n%n%n%n",
            "%{1000000}x",

            # LDAP injection
            "*)(uid=*",
            "admin)(&(|(password=*)(password=*))",

            # XML/XXE
            "<?xml version='1.0'?><!DOCTYPE foo [<!ELEMENT foo ANY ><!ENTITY xxe SYSTEM 'file:///etc/passwd' >]><foo>&xxe;</foo>",
        ]

        results = []
        for payload in malicious_inputs:
            for param_name in params.keys():
                test_params = params.copy()
                test_params[param_name] = payload

                result = await self._make_security_request(
                    endpoint=endpoint,
                    method="GET",
                    params=test_params,
                    attack_type="INPUT_VALIDATION",
                    payload=payload
                )
                results.append(result)

        return results

    async def test_cors_policy(self, endpoint: str) -> List[SecurityTestResult]:
        """Test CORS policy configuration."""
        malicious_origins = [
            "http://evil.com",
            "https://attacker.evil",
            "null",
            "*",
            "http://localhost:3000",  # Development origin
            "file://",
            "data:",
            "javascript:"
        ]

        results = []
        for origin in malicious_origins:
            headers = {
                "Origin": origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }

            result = await self._make_security_request(
                endpoint=endpoint,
                method="OPTIONS",
                headers=headers,
                attack_type="CORS_POLICY",
                payload=f"Origin: {origin}"
            )
            results.append(result)

        return results

    async def test_header_security(self, endpoint: str) -> SecurityTestResult:
        """Test security headers presence and configuration."""
        result = await self._make_simple_request(endpoint)

        if isinstance(result, Exception):
            return SecurityTestResult(
                test_name="header_security_test",
                endpoint=endpoint,
                attack_type="HEADER_SECURITY",
                payload="Security headers check",
                status_code=0,
                response_time_ms=0,
                vulnerability_detected=True,
                severity="HIGH",
                description="Failed to connect to endpoint",
                recommendation="Ensure endpoint is accessible for security testing"
            )

        headers = result.headers
        missing_headers = []
        weak_headers = []

        # Check for security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": ["DENY", "SAMEORIGIN"],
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=",
            "Content-Security-Policy": None,  # Should exist
            "Referrer-Policy": ["strict-origin-when-cross-origin", "no-referrer", "same-origin"],
            "Permissions-Policy": None,  # Should exist
        }

        for header, expected_value in security_headers.items():
            header_value = headers.get(header)

            if not header_value:
                missing_headers.append(header)
            elif expected_value and isinstance(expected_value, list):
                if not any(exp in header_value for exp in expected_value):
                    weak_headers.append(f"{header}: {header_value}")
            elif expected_value and isinstance(expected_value, str):
                if expected_value not in header_value:
                    weak_headers.append(f"{header}: {header_value}")

        vulnerability_detected = len(missing_headers) > 0 or len(weak_headers) > 0
        severity = "HIGH" if len(missing_headers) > 2 else "MEDIUM" if len(missing_headers) > 0 else "LOW"

        description = f"Missing headers: {missing_headers}. Weak headers: {weak_headers}"
        recommendation = "Implement proper security headers configuration"

        return SecurityTestResult(
            test_name="header_security_test",
            endpoint=endpoint,
            attack_type="HEADER_SECURITY",
            payload="Security headers analysis",
            status_code=result.status,
            response_time_ms=0,
            vulnerability_detected=vulnerability_detected,
            severity=severity,
            description=description,
            recommendation=recommendation
        )

    async def _make_security_request(
        self,
        endpoint: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        attack_type: str = "",
        payload: str = ""
    ) -> SecurityTestResult:
        """Make a security-focused HTTP request and analyze the response."""
        if not self.session:
            return SecurityTestResult(
                test_name=f"{attack_type.lower()}_test",
                endpoint=endpoint,
                attack_type=attack_type,
                payload=payload,
                status_code=0,
                response_time_ms=0,
                vulnerability_detected=True,
                severity="HIGH",
                description="Session not initialized",
                recommendation="Initialize HTTP session before testing"
            )

        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            async with self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000

                # Analyze response for vulnerabilities
                vulnerability_detected = await self._analyze_response_for_vulnerabilities(
                    response, attack_type, payload
                )

                severity = self._determine_severity(response.status, attack_type, vulnerability_detected)

                return SecurityTestResult(
                    test_name=f"{attack_type.lower()}_test",
                    endpoint=endpoint,
                    attack_type=attack_type,
                    payload=payload,
                    status_code=response.status,
                    response_time_ms=response_time_ms,
                    vulnerability_detected=vulnerability_detected,
                    severity=severity,
                    description=f"Response status: {response.status}",
                    recommendation=self._get_recommendation(attack_type, vulnerability_detected)
                )

        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000

            return SecurityTestResult(
                test_name=f"{attack_type.lower()}_test",
                endpoint=endpoint,
                attack_type=attack_type,
                payload=payload,
                status_code=0,
                response_time_ms=response_time_ms,
                vulnerability_detected=True,
                severity="HIGH",
                description=f"Request failed: {str(e)}",
                recommendation="Investigate request handling and error responses"
            )

    async def _make_simple_request(self, endpoint: str):
        """Make a simple HTTP request for basic testing."""
        if not self.session:
            return Exception("Session not initialized")

        url = f"{self.base_url}{endpoint}"
        try:
            return await self.session.get(url, timeout=aiohttp.ClientTimeout(total=5))
        except Exception as e:
            return e

    async def _analyze_response_for_vulnerabilities(
        self,
        response: aiohttp.ClientResponse,
        attack_type: str,
        payload: str
    ) -> bool:
        """Analyze HTTP response for vulnerability indicators."""
        try:
            response_text = await response.text()
        except Exception:
            response_text = ""

        # SQL Injection indicators
        if attack_type == "SQL_INJECTION":
            sql_error_indicators = [
                "sql syntax",
                "mysql_fetch",
                "ora-00921",
                "microsoft jet database",
                "odbc sql server driver",
                "postgresql",
                "warning: mysql",
                "valid mysql result",
                "unknown column",
                "table doesn't exist"
            ]
            return any(indicator in response_text.lower() for indicator in sql_error_indicators)

        # NoSQL Injection indicators
        elif attack_type == "NOSQL_INJECTION":
            nosql_indicators = [
                "mongodb",
                "bsonobject",
                "collection.find",
                "invalid bson",
                "mongo",
                "document"
            ]
            return any(indicator in response_text.lower() for indicator in nosql_indicators)

        # Authentication bypass indicators
        elif attack_type == "AUTH_BYPASS":
            # Successful bypass usually returns 200 instead of 401/403
            return response.status == 200

        # Authorization escalation indicators
        elif attack_type == "AUTHZ_ESCALATION":
            # Successful escalation usually returns 200 instead of 403
            return response.status == 200

        # Input validation indicators
        elif attack_type == "INPUT_VALIDATION":
            validation_indicators = [
                "<script>",
                "alert(",
                "/etc/passwd",
                "root:",
                "administrator",
                "system error",
                "exception",
                "stack trace"
            ]
            return any(indicator in response_text.lower() for indicator in validation_indicators)

        # CORS policy indicators
        elif attack_type == "CORS_POLICY":
            cors_headers = response.headers
            # Overly permissive CORS
            origin_header = cors_headers.get("Access-Control-Allow-Origin", "")
            return origin_header == "*" or "evil" in origin_header

        return False

    def _determine_severity(self, status_code: int, attack_type: str, vulnerability_detected: bool) -> str:
        """Determine severity based on response and vulnerability type."""
        if not vulnerability_detected:
            return "LOW"

        critical_attacks = ["SQL_INJECTION", "AUTH_BYPASS", "AUTHZ_ESCALATION"]
        high_attacks = ["NOSQL_INJECTION", "INPUT_VALIDATION"]
        medium_attacks = ["CORS_POLICY", "HEADER_SECURITY"]

        if attack_type in critical_attacks:
            return "CRITICAL"
        elif attack_type in high_attacks:
            return "HIGH"
        elif attack_type in medium_attacks:
            return "MEDIUM"
        else:
            return "LOW"

    def _get_recommendation(self, attack_type: str, vulnerability_detected: bool) -> str:
        """Get security recommendation based on attack type."""
        if not vulnerability_detected:
            return "Security control is properly configured"

        recommendations = {
            "SQL_INJECTION": "Use parameterized queries and input validation",
            "NOSQL_INJECTION": "Implement proper input sanitization and use schema validation",
            "AUTH_BYPASS": "Strengthen authentication mechanisms and token validation",
            "AUTHZ_ESCALATION": "Implement proper authorization checks and principle of least privilege",
            "RATE_LIMITING": "Implement rate limiting with appropriate thresholds",
            "INPUT_VALIDATION": "Implement comprehensive input validation and sanitization",
            "CORS_POLICY": "Configure restrictive CORS policy with specific origins",
            "HEADER_SECURITY": "Implement proper security headers configuration"
        }

        return recommendations.get(attack_type, "Review security configuration for this endpoint")


class TestAPISecurityPenetration:
    """Penetration testing suite for API security."""

    @pytest.mark.security
    @pytest.mark.slow
    async def test_comprehensive_api_penetration_testing(self) -> None:
        """Run comprehensive penetration testing against API endpoints."""

        # Define test endpoints based on AXIOM ATLAS API structure
        test_endpoints = [
            {
                "path": "/api/v1/health",
                "method": "GET",
                "auth_required": False,
                "params": {},
                "json_data": {}
            },
            {
                "path": "/api/v1/auth/login",
                "method": "POST",
                "auth_required": False,
                "params": {},
                "json_data": {"username": "test", "password": "test"}
            },
            {
                "path": "/api/v1/scientific/hypothesis/generate",
                "method": "POST",
                "auth_required": True,
                "params": {"domain": "biology"},
                "json_data": {"research_area": "genetics", "complexity": "intermediate"}
            },
            {
                "path": "/api/v1/quantum/circuits/simulate",
                "method": "POST",
                "auth_required": True,
                "params": {},
                "json_data": {"circuit_type": "grover", "qubits": 3}
            },
            {
                "path": "/api/v1/biology/protein/analyze",
                "method": "POST",
                "auth_required": True,
                "params": {},
                "json_data": {"sequence": "ACGTACGT", "analysis_type": "structure"}
            }
        ]

        all_results = []

        # Mock the HTTP server for testing
        with patch('aiohttp.ClientSession') as mock_session:
            # Setup mock responses
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.headers = {
                "Content-Type": "application/json",
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY"
            }
            async def mock_text():
                return '{"status": "ok"}'

            mock_response.text = mock_text

            mock_session_instance = MagicMock()
            mock_session_instance.request.return_value.__aenter__.return_value = mock_response
            mock_session_instance.get.return_value = mock_response
            mock_session.return_value = mock_session_instance

            async with APISecurityTester() as tester:
                tester.session = mock_session_instance

                for endpoint_config in test_endpoints:
                    endpoint = endpoint_config["path"]
                    params = endpoint_config["params"]
                    json_data = endpoint_config["json_data"]

                    print(f"\n🔍 Testing endpoint: {endpoint}")

                    # SQL Injection tests
                    if params:
                        sql_results = await tester.test_sql_injection(endpoint, params)
                        all_results.extend(sql_results)

                    # NoSQL Injection tests
                    if json_data:
                        nosql_results = await tester.test_nosql_injection(endpoint, json_data)
                        all_results.extend(nosql_results)

                    # Authentication bypass tests
                    auth_results = await tester.test_authentication_bypass(endpoint)
                    all_results.extend(auth_results)

                    # Authorization escalation tests (if auth required)
                    if endpoint_config["auth_required"]:
                        fake_token = "fake_user_token_12345"
                        authz_results = await tester.test_authorization_escalation(endpoint, fake_token)
                        all_results.extend(authz_results)

                    # Rate limiting tests
                    rate_result = await tester.test_rate_limiting(endpoint, requests_per_second=20)
                    all_results.append(rate_result)

                    # Input validation tests
                    if params:
                        input_results = await tester.test_input_validation(endpoint, params)
                        all_results.extend(input_results)

                    # CORS policy tests
                    cors_results = await tester.test_cors_policy(endpoint)
                    all_results.extend(cors_results)

                    # Header security tests
                    header_result = await tester.test_header_security(endpoint)
                    all_results.append(header_result)

        # Analyze and report results
        test_suite = self._analyze_penetration_results(all_results)
        self._print_security_report(test_suite)

        # Security assertions
        assert test_suite.critical_vulnerabilities == 0, f"Found {test_suite.critical_vulnerabilities} critical vulnerabilities"
        assert test_suite.high_vulnerabilities <= 5, f"Found {test_suite.high_vulnerabilities} high-severity vulnerabilities (max 5 allowed)"
        assert test_suite.vulnerabilities_found / test_suite.total_tests < 0.3, f"Vulnerability rate too high: {test_suite.vulnerabilities_found/test_suite.total_tests:.2%}"

    def _analyze_penetration_results(self, results: List[SecurityTestResult]) -> PenetrationTestSuite:
        """Analyze penetration test results and categorize vulnerabilities."""
        total_tests = len(results)
        vulnerabilities_found = sum(1 for r in results if r.vulnerability_detected)

        critical_vulnerabilities = sum(1 for r in results if r.vulnerability_detected and r.severity == "CRITICAL")
        high_vulnerabilities = sum(1 for r in results if r.vulnerability_detected and r.severity == "HIGH")
        medium_vulnerabilities = sum(1 for r in results if r.vulnerability_detected and r.severity == "MEDIUM")
        low_vulnerabilities = sum(1 for r in results if r.vulnerability_detected and r.severity == "LOW")

        return PenetrationTestSuite(
            total_tests=total_tests,
            vulnerabilities_found=vulnerabilities_found,
            critical_vulnerabilities=critical_vulnerabilities,
            high_vulnerabilities=high_vulnerabilities,
            medium_vulnerabilities=medium_vulnerabilities,
            low_vulnerabilities=low_vulnerabilities,
            test_results=results
        )

    def _print_security_report(self, test_suite: PenetrationTestSuite) -> None:
        """Print comprehensive security penetration test report."""
        print("\n" + "="*80)
        print("🔒 API SECURITY PENETRATION TEST REPORT")
        print("="*80)

        print("\n📊 SUMMARY:")
        print(f"  Total Tests: {test_suite.total_tests}")
        print(f"  Vulnerabilities Found: {test_suite.vulnerabilities_found}")
        print(f"  Vulnerability Rate: {test_suite.vulnerabilities_found/test_suite.total_tests:.2%}")

        print("\n⚠️  SEVERITY BREAKDOWN:")
        print(f"  🔴 Critical: {test_suite.critical_vulnerabilities}")
        print(f"  🟠 High: {test_suite.high_vulnerabilities}")
        print(f"  🟡 Medium: {test_suite.medium_vulnerabilities}")
        print(f"  🔵 Low: {test_suite.low_vulnerabilities}")

        # Group results by attack type for detailed reporting
        attack_types = {}
        for result in test_suite.test_results:
            if result.attack_type not in attack_types:
                attack_types[result.attack_type] = []
            attack_types[result.attack_type].append(result)

        print("\n🎯 VULNERABILITY DETAILS BY ATTACK TYPE:")
        for attack_type, results in attack_types.items():
            vulnerabilities = [r for r in results if r.vulnerability_detected]
            if vulnerabilities:
                print(f"\n  {attack_type}:")
                for vuln in vulnerabilities[:3]:  # Show first 3 vulnerabilities
                    print(f"    🚨 {vuln.endpoint} - {vuln.severity}")
                    print(f"       Payload: {vuln.payload[:50]}...")
                    print(f"       Recommendation: {vuln.recommendation}")
                if len(vulnerabilities) > 3:
                    print(f"    ... and {len(vulnerabilities) - 3} more vulnerabilities")

        print("\n✅ SECURITY POSTURE:")
        if test_suite.critical_vulnerabilities == 0 and test_suite.high_vulnerabilities <= 2:
            print("  🟢 GOOD - Low security risk detected")
        elif test_suite.critical_vulnerabilities == 0 and test_suite.high_vulnerabilities <= 5:
            print("  🟡 MODERATE - Some security issues need attention")
        else:
            print("  🔴 POOR - Critical security vulnerabilities detected")

        print("="*80)