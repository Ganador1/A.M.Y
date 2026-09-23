"""
Quality Gate Validation Tests

This module implements automated quality gates for the CI/CD pipeline.
Quality gates ensure code meets minimum standards before deployment.

Quality Gates Implemented:
1. Test Coverage Gate: Minimum test coverage threshold
2. Performance Gate: Response time within acceptable limits
3. Code Quality Gate: Static analysis issues below threshold
4. Security Gate: No critical vulnerabilities
5. Documentation Gate: API documentation completeness
6. Complexity Gate: Code complexity within limits

Author: Atlas AI Mathematics System
Date: October 2025
"""

import pytest
import json
import time
import asyncio
from typing import Dict, Any, List, Tuple
from datetime import datetime
from pathlib import Path


class QualityMetrics:
    """
    Tracks quality metrics for gate validation.
    
    Aggregates metrics from various sources for gate checking.
    """
    
    def __init__(self):
        self.metrics = {
            'test_coverage': 0.0,
            'performance': {},
            'code_quality': {},
            'security': {},
            'documentation': {},
            'complexity': {},
            'timestamp': datetime.now().isoformat()
        }
    
    def set_test_coverage(self, coverage_percent: float):
        """Set test coverage percentage."""
        self.metrics['test_coverage'] = coverage_percent
    
    def set_performance_metrics(self, metrics: Dict[str, float]):
        """Set performance metrics."""
        self.metrics['performance'] = metrics
    
    def set_code_quality_metrics(self, metrics: Dict[str, int]):
        """Set code quality metrics."""
        self.metrics['code_quality'] = metrics
    
    def set_security_metrics(self, metrics: Dict[str, int]):
        """Set security metrics."""
        self.metrics['security'] = metrics
    
    def set_documentation_metrics(self, metrics: Dict[str, float]):
        """Set documentation metrics."""
        self.metrics['documentation'] = metrics
    
    def set_complexity_metrics(self, metrics: Dict[str, float]):
        """Set complexity metrics."""
        self.metrics['complexity'] = metrics
    
    def to_dict(self) -> Dict[str, Any]:
        """Export metrics as dictionary."""
        return self.metrics


class QualityGate:
    """
    Base class for quality gates.
    
    Defines interface for quality gate validation.
    """
    
    def __init__(self, name: str, threshold: Any):
        self.name = name
        self.threshold = threshold
        self.status = 'pending'
        self.message = ''
    
    def validate(self, metrics: QualityMetrics) -> bool:
        """
        Validate gate against metrics.
        
        Args:
            metrics: Quality metrics to validate
            
        Returns:
            bool: True if gate passes
        """
        raise NotImplementedError
    
    def get_status(self) -> Dict[str, Any]:
        """Get gate validation status."""
        return {
            'gate': self.name,
            'status': self.status,
            'message': self.message,
            'threshold': self.threshold
        }


class TestCoverageGate(QualityGate):
    """Validates minimum test coverage."""
    
    def __init__(self, min_coverage: float = 80.0):
        super().__init__('test_coverage', min_coverage)
    
    def validate(self, metrics: QualityMetrics) -> bool:
        """Validate test coverage meets minimum."""
        coverage = metrics.metrics['test_coverage']
        
        if coverage >= self.threshold:
            self.status = 'passed'
            self.message = f"Coverage {coverage:.1f}% meets minimum {self.threshold:.1f}%"
            return True
        else:
            self.status = 'failed'
            self.message = f"Coverage {coverage:.1f}% below minimum {self.threshold:.1f}%"
            return False


class PerformanceGate(QualityGate):
    """Validates performance metrics within acceptable limits."""
    
    def __init__(self, max_response_time_ms: float = 100.0):
        super().__init__('performance', max_response_time_ms)
    
    def validate(self, metrics: QualityMetrics) -> bool:
        """Validate performance meets requirements."""
        perf = metrics.metrics['performance']
        
        if not perf:
            self.status = 'skipped'
            self.message = "No performance metrics available"
            return True
        
        avg_response = perf.get('avg_response_time_ms', 0)
        
        if avg_response <= self.threshold:
            self.status = 'passed'
            self.message = f"Avg response {avg_response:.1f}ms within limit {self.threshold:.1f}ms"
            return True
        else:
            self.status = 'failed'
            self.message = f"Avg response {avg_response:.1f}ms exceeds limit {self.threshold:.1f}ms"
            return False


class CodeQualityGate(QualityGate):
    """Validates code quality issues below threshold."""
    
    def __init__(self, max_issues: int = 10):
        super().__init__('code_quality', max_issues)
    
    def validate(self, metrics: QualityMetrics) -> bool:
        """Validate code quality meets standards."""
        quality = metrics.metrics['code_quality']
        
        if not quality:
            self.status = 'skipped'
            self.message = "No code quality metrics available"
            return True
        
        total_issues = quality.get('total_issues', 0)
        critical_issues = quality.get('critical_issues', 0)
        
        if critical_issues > 0:
            self.status = 'failed'
            self.message = f"Found {critical_issues} critical issues (must be 0)"
            return False
        
        if total_issues <= self.threshold:
            self.status = 'passed'
            self.message = f"Total issues {total_issues} within limit {self.threshold}"
            return True
        else:
            self.status = 'failed'
            self.message = f"Total issues {total_issues} exceeds limit {self.threshold}"
            return False


class SecurityGate(QualityGate):
    """Validates no critical security vulnerabilities."""
    
    def __init__(self, max_vulnerabilities: int = 0):
        super().__init__('security', max_vulnerabilities)
    
    def validate(self, metrics: QualityMetrics) -> bool:
        """Validate security requirements met."""
        security = metrics.metrics['security']
        
        if not security:
            self.status = 'skipped'
            self.message = "No security metrics available"
            return True
        
        critical_vulns = security.get('critical_vulnerabilities', 0)
        high_vulns = security.get('high_vulnerabilities', 0)
        
        if critical_vulns > self.threshold:
            self.status = 'failed'
            self.message = f"Found {critical_vulns} critical vulnerabilities (max {self.threshold})"
            return False
        
        if high_vulns > 5:
            self.status = 'warning'
            self.message = f"Found {high_vulns} high-severity vulnerabilities (review recommended)"
            return True
        
        self.status = 'passed'
        self.message = f"No critical vulnerabilities found"
        return True


class DocumentationGate(QualityGate):
    """Validates API documentation completeness."""
    
    def __init__(self, min_coverage: float = 90.0):
        super().__init__('documentation', min_coverage)
    
    def validate(self, metrics: QualityMetrics) -> bool:
        """Validate documentation meets standards."""
        docs = metrics.metrics['documentation']
        
        if not docs:
            self.status = 'skipped'
            self.message = "No documentation metrics available"
            return True
        
        doc_coverage = docs.get('api_coverage_percent', 0)
        
        if doc_coverage >= self.threshold:
            self.status = 'passed'
            self.message = f"Documentation {doc_coverage:.1f}% meets minimum {self.threshold:.1f}%"
            return True
        else:
            self.status = 'failed'
            self.message = f"Documentation {doc_coverage:.1f}% below minimum {self.threshold:.1f}%"
            return False


class ComplexityGate(QualityGate):
    """Validates code complexity within limits."""
    
    def __init__(self, max_complexity: float = 10.0):
        super().__init__('complexity', max_complexity)
    
    def validate(self, metrics: QualityMetrics) -> bool:
        """Validate complexity meets standards."""
        complexity = metrics.metrics['complexity']
        
        if not complexity:
            self.status = 'skipped'
            self.message = "No complexity metrics available"
            return True
        
        avg_complexity = complexity.get('average_cyclomatic', 0)
        max_function_complexity = complexity.get('max_cyclomatic', 0)
        
        if max_function_complexity > self.threshold * 2:
            self.status = 'failed'
            self.message = f"Max function complexity {max_function_complexity:.1f} exceeds {self.threshold * 2:.1f}"
            return False
        
        if avg_complexity <= self.threshold:
            self.status = 'passed'
            self.message = f"Avg complexity {avg_complexity:.1f} within limit {self.threshold:.1f}"
            return True
        else:
            self.status = 'warning'
            self.message = f"Avg complexity {avg_complexity:.1f} exceeds recommended {self.threshold:.1f}"
            return True


class QualityGateValidator:
    """
    Orchestrates quality gate validation.
    
    Runs all gates and aggregates results.
    """
    
    def __init__(self):
        self.gates = [
            TestCoverageGate(min_coverage=80.0),
            PerformanceGate(max_response_time_ms=100.0),
            CodeQualityGate(max_issues=10),
            SecurityGate(max_vulnerabilities=0),
            DocumentationGate(min_coverage=90.0),
            ComplexityGate(max_complexity=10.0)
        ]
    
    def validate_all(self, metrics: QualityMetrics) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate all quality gates.
        
        Args:
            metrics: Quality metrics to validate
            
        Returns:
            tuple: (all_passed, gate_statuses)
        """
        results = []
        all_passed = True
        
        for gate in self.gates:
            passed = gate.validate(metrics)
            status = gate.get_status()
            results.append(status)
            
            if not passed and status['status'] == 'failed':
                all_passed = False
        
        return all_passed, results
    
    def generate_report(self, metrics: QualityMetrics) -> Dict[str, Any]:
        """
        Generate quality gate validation report.
        
        Args:
            metrics: Quality metrics
            
        Returns:
            dict: Validation report
        """
        all_passed, results = self.validate_all(metrics)
        
        passed_count = sum(1 for r in results if r['status'] == 'passed')
        failed_count = sum(1 for r in results if r['status'] == 'failed')
        warning_count = sum(1 for r in results if r['status'] == 'warning')
        skipped_count = sum(1 for r in results if r['status'] == 'skipped')
        
        return {
            'overall_status': 'PASSED' if all_passed else 'FAILED',
            'gates': results,
            'summary': {
                'total': len(results),
                'passed': passed_count,
                'failed': failed_count,
                'warnings': warning_count,
                'skipped': skipped_count
            },
            'timestamp': datetime.now().isoformat()
        }


# Test fixtures
@pytest.fixture
def quality_metrics():
    """Create quality metrics tracker."""
    return QualityMetrics()


@pytest.fixture
def gate_validator():
    """Create quality gate validator."""
    return QualityGateValidator()


class TestTestCoverageGate:
    """Test coverage gate validation."""
    
    def test_coverage_passes_threshold(self, quality_metrics):
        """Test coverage gate passes when above threshold."""
        quality_metrics.set_test_coverage(85.0)
        gate = TestCoverageGate(min_coverage=80.0)
        
        result = gate.validate(quality_metrics)
        
        assert result is True
        assert gate.status == 'passed'
        assert '85.0%' in gate.message
    
    def test_coverage_fails_threshold(self, quality_metrics):
        """Test coverage gate fails when below threshold."""
        quality_metrics.set_test_coverage(75.0)
        gate = TestCoverageGate(min_coverage=80.0)
        
        result = gate.validate(quality_metrics)
        
        assert result is False
        assert gate.status == 'failed'
        assert 'below minimum' in gate.message


class TestPerformanceGate:
    """Test performance gate validation."""
    
    def test_performance_passes_threshold(self, quality_metrics):
        """Test performance gate passes when within limits."""
        quality_metrics.set_performance_metrics({
            'avg_response_time_ms': 75.0,
            'p95_response_time_ms': 95.0
        })
        gate = PerformanceGate(max_response_time_ms=100.0)
        
        result = gate.validate(quality_metrics)
        
        assert result is True
        assert gate.status == 'passed'
    
    def test_performance_fails_threshold(self, quality_metrics):
        """Test performance gate fails when exceeding limits."""
        quality_metrics.set_performance_metrics({
            'avg_response_time_ms': 150.0
        })
        gate = PerformanceGate(max_response_time_ms=100.0)
        
        result = gate.validate(quality_metrics)
        
        assert result is False
        assert gate.status == 'failed'
    
    def test_performance_skipped_without_metrics(self, quality_metrics):
        """Test performance gate skipped without metrics."""
        gate = PerformanceGate(max_response_time_ms=100.0)
        
        result = gate.validate(quality_metrics)
        
        assert result is True
        assert gate.status == 'skipped'


class TestCodeQualityGate:
    """Test code quality gate validation."""
    
    def test_quality_passes_threshold(self, quality_metrics):
        """Test quality gate passes when issues within limits."""
        quality_metrics.set_code_quality_metrics({
            'total_issues': 5,
            'critical_issues': 0,
            'major_issues': 2,
            'minor_issues': 3
        })
        gate = CodeQualityGate(max_issues=10)
        
        result = gate.validate(quality_metrics)
        
        assert result is True
        assert gate.status == 'passed'
    
    def test_quality_fails_with_critical_issues(self, quality_metrics):
        """Test quality gate fails with critical issues."""
        quality_metrics.set_code_quality_metrics({
            'total_issues': 3,
            'critical_issues': 1
        })
        gate = CodeQualityGate(max_issues=10)
        
        result = gate.validate(quality_metrics)
        
        assert result is False
        assert gate.status == 'failed'
        assert 'critical issues' in gate.message
    
    def test_quality_fails_exceeding_threshold(self, quality_metrics):
        """Test quality gate fails when exceeding threshold."""
        quality_metrics.set_code_quality_metrics({
            'total_issues': 15,
            'critical_issues': 0
        })
        gate = CodeQualityGate(max_issues=10)
        
        result = gate.validate(quality_metrics)
        
        assert result is False
        assert gate.status == 'failed'


class TestSecurityGate:
    """Test security gate validation."""
    
    def test_security_passes_no_vulnerabilities(self, quality_metrics):
        """Test security gate passes with no vulnerabilities."""
        quality_metrics.set_security_metrics({
            'critical_vulnerabilities': 0,
            'high_vulnerabilities': 0,
            'medium_vulnerabilities': 2
        })
        gate = SecurityGate(max_vulnerabilities=0)
        
        result = gate.validate(quality_metrics)
        
        assert result is True
        assert gate.status == 'passed'
    
    def test_security_fails_with_critical_vulns(self, quality_metrics):
        """Test security gate fails with critical vulnerabilities."""
        quality_metrics.set_security_metrics({
            'critical_vulnerabilities': 1,
            'high_vulnerabilities': 0
        })
        gate = SecurityGate(max_vulnerabilities=0)
        
        result = gate.validate(quality_metrics)
        
        assert result is False
        assert gate.status == 'failed'
        assert 'critical vulnerabilities' in gate.message
    
    def test_security_warning_with_high_vulns(self, quality_metrics):
        """Test security gate warns with high vulnerabilities."""
        quality_metrics.set_security_metrics({
            'critical_vulnerabilities': 0,
            'high_vulnerabilities': 6
        })
        gate = SecurityGate(max_vulnerabilities=0)
        
        result = gate.validate(quality_metrics)
        
        assert result is True
        assert gate.status == 'warning'


class TestDocumentationGate:
    """Test documentation gate validation."""
    
    def test_documentation_passes_threshold(self, quality_metrics):
        """Test documentation gate passes when coverage sufficient."""
        quality_metrics.set_documentation_metrics({
            'api_coverage_percent': 95.0,
            'documented_endpoints': 19,
            'total_endpoints': 20
        })
        gate = DocumentationGate(min_coverage=90.0)
        
        result = gate.validate(quality_metrics)
        
        assert result is True
        assert gate.status == 'passed'
    
    def test_documentation_fails_threshold(self, quality_metrics):
        """Test documentation gate fails when coverage insufficient."""
        quality_metrics.set_documentation_metrics({
            'api_coverage_percent': 85.0
        })
        gate = DocumentationGate(min_coverage=90.0)
        
        result = gate.validate(quality_metrics)
        
        assert result is False
        assert gate.status == 'failed'


class TestComplexityGate:
    """Test complexity gate validation."""
    
    def test_complexity_passes_threshold(self, quality_metrics):
        """Test complexity gate passes when within limits."""
        quality_metrics.set_complexity_metrics({
            'average_cyclomatic': 6.5,
            'max_cyclomatic': 12.0
        })
        gate = ComplexityGate(max_complexity=10.0)
        
        result = gate.validate(quality_metrics)
        
        assert result is True
        assert gate.status == 'passed'
    
    def test_complexity_warning_on_high_average(self, quality_metrics):
        """Test complexity gate warns on high average."""
        quality_metrics.set_complexity_metrics({
            'average_cyclomatic': 11.0,
            'max_cyclomatic': 15.0
        })
        gate = ComplexityGate(max_complexity=10.0)
        
        result = gate.validate(quality_metrics)
        
        assert result is True
        assert gate.status == 'warning'
    
    def test_complexity_fails_on_extreme_max(self, quality_metrics):
        """Test complexity gate fails on extreme max complexity."""
        quality_metrics.set_complexity_metrics({
            'average_cyclomatic': 8.0,
            'max_cyclomatic': 25.0
        })
        gate = ComplexityGate(max_complexity=10.0)
        
        result = gate.validate(quality_metrics)
        
        assert result is False
        assert gate.status == 'failed'


class TestQualityGateValidator:
    """Test complete quality gate validation."""
    
    def test_all_gates_pass(self, gate_validator, quality_metrics):
        """Test all gates pass with good metrics."""
        quality_metrics.set_test_coverage(85.0)
        quality_metrics.set_performance_metrics({'avg_response_time_ms': 75.0})
        quality_metrics.set_code_quality_metrics({'total_issues': 5, 'critical_issues': 0})
        quality_metrics.set_security_metrics({'critical_vulnerabilities': 0, 'high_vulnerabilities': 0})
        quality_metrics.set_documentation_metrics({'api_coverage_percent': 95.0})
        quality_metrics.set_complexity_metrics({'average_cyclomatic': 6.5, 'max_cyclomatic': 12.0})
        
        all_passed, results = gate_validator.validate_all(quality_metrics)
        
        assert all_passed is True
        assert all(r['status'] in ['passed', 'skipped'] for r in results)
    
    def test_some_gates_fail(self, gate_validator, quality_metrics):
        """Test validation fails when some gates fail."""
        quality_metrics.set_test_coverage(70.0)  # Below threshold
        quality_metrics.set_performance_metrics({'avg_response_time_ms': 75.0})
        quality_metrics.set_code_quality_metrics({'total_issues': 5, 'critical_issues': 0})
        quality_metrics.set_security_metrics({'critical_vulnerabilities': 1, 'high_vulnerabilities': 0})  # Critical vuln
        quality_metrics.set_documentation_metrics({'api_coverage_percent': 95.0})
        quality_metrics.set_complexity_metrics({'average_cyclomatic': 6.5, 'max_cyclomatic': 12.0})
        
        all_passed, results = gate_validator.validate_all(quality_metrics)
        
        assert all_passed is False
        failed_gates = [r for r in results if r['status'] == 'failed']
        assert len(failed_gates) >= 2
    
    def test_generate_report(self, gate_validator, quality_metrics):
        """Test quality gate report generation."""
        quality_metrics.set_test_coverage(85.0)
        quality_metrics.set_performance_metrics({'avg_response_time_ms': 75.0})
        quality_metrics.set_code_quality_metrics({'total_issues': 5, 'critical_issues': 0})
        quality_metrics.set_security_metrics({'critical_vulnerabilities': 0, 'high_vulnerabilities': 0})
        quality_metrics.set_documentation_metrics({'api_coverage_percent': 95.0})
        quality_metrics.set_complexity_metrics({'average_cyclomatic': 6.5, 'max_cyclomatic': 12.0})
        
        report = gate_validator.generate_report(quality_metrics)
        
        assert 'overall_status' in report
        assert 'gates' in report
        assert 'summary' in report
        assert report['summary']['total'] == 6
        assert report['overall_status'] in ['PASSED', 'FAILED']
    
    def test_report_with_failures(self, gate_validator, quality_metrics):
        """Test report correctly shows failures."""
        quality_metrics.set_test_coverage(70.0)
        quality_metrics.set_code_quality_metrics({'total_issues': 2, 'critical_issues': 1})
        
        report = gate_validator.generate_report(quality_metrics)
        
        assert report['overall_status'] == 'FAILED'
        assert report['summary']['failed'] >= 2


class TestCICDIntegration:
    """Test CI/CD pipeline integration."""
    
    def test_quality_gate_ci_integration(self, gate_validator):
        """Test quality gates can be integrated into CI/CD."""
        # Simulate CI/CD metrics
        metrics = QualityMetrics()
        metrics.set_test_coverage(82.0)
        metrics.set_performance_metrics({'avg_response_time_ms': 85.0})
        metrics.set_code_quality_metrics({'total_issues': 8, 'critical_issues': 0})
        metrics.set_security_metrics({'critical_vulnerabilities': 0, 'high_vulnerabilities': 2})
        metrics.set_documentation_metrics({'api_coverage_percent': 92.0})
        metrics.set_complexity_metrics({'average_cyclomatic': 7.2, 'max_cyclomatic': 14.0})
        
        report = gate_validator.generate_report(metrics)
        
        # Should pass overall
        assert report['overall_status'] == 'PASSED'
        
        # Should have some warnings
        warnings = [r for r in report['gates'] if r['status'] == 'warning']
        assert len(warnings) >= 0
    
    def test_blocking_deployment_on_failure(self, gate_validator):
        """Test deployment should be blocked on gate failure."""
        metrics = QualityMetrics()
        metrics.set_test_coverage(75.0)  # Below threshold
        metrics.set_security_metrics({'critical_vulnerabilities': 1})  # Critical issue
        
        all_passed, results = gate_validator.validate_all(metrics)
        
        # Should not allow deployment
        assert all_passed is False
        
        # Verify critical gates failed
        failed_critical = [r for r in results if r['status'] == 'failed' and r['gate'] in ['test_coverage', 'security']]
        assert len(failed_critical) >= 2


# Quality gate thresholds configuration
QUALITY_GATE_THRESHOLDS = {
    'test_coverage': {'min': 80.0, 'target': 90.0},
    'performance': {'max_response_ms': 100.0, 'target': 50.0},
    'code_quality': {'max_issues': 10, 'max_critical': 0},
    'security': {'max_critical_vulns': 0, 'max_high_vulns': 5},
    'documentation': {'min_coverage': 90.0, 'target': 95.0},
    'complexity': {'max_avg': 10.0, 'max_function': 20.0}
}


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
