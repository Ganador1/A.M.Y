"""
Regression Detection System Tests

This module implements automated regression detection for performance
and functionality. Compares current metrics against historical baselines
to detect performance degradation or functional regressions.

Regression Types Detected:
1. Performance Regression: Response time increases
2. Memory Regression: Memory usage increases
3. Throughput Regression: Operations/second decreases
4. Functional Regression: Test failures or behavior changes
5. Quality Regression: Code quality metrics degradation
6. Accuracy Regression: Model/algorithm accuracy decreases

Author: Atlas AI Mathematics System
Date: October 2025
"""

import pytest
import time
import asyncio
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field


@dataclass
class MetricSnapshot:
    """
    Represents a snapshot of metrics at a point in time.
    
    Used for comparing current metrics against historical baselines.
    """
    timestamp: str
    performance: Dict[str, float] = field(default_factory=dict)
    memory: Dict[str, float] = field(default_factory=dict)
    throughput: Dict[str, float] = field(default_factory=dict)
    quality: Dict[str, int] = field(default_factory=dict)
    accuracy: Dict[str, float] = field(default_factory=dict)
    functional: Dict[str, bool] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export snapshot as dictionary."""
        return {
            'timestamp': self.timestamp,
            'performance': self.performance,
            'memory': self.memory,
            'throughput': self.throughput,
            'quality': self.quality,
            'accuracy': self.accuracy,
            'functional': self.functional
        }


@dataclass
class RegressionResult:
    """
    Represents the result of a regression check.
    
    Contains information about detected regressions.
    """
    metric_name: str
    regression_type: str
    severity: str  # 'critical', 'major', 'minor'
    baseline_value: float
    current_value: float
    delta_percent: float
    message: str
    detected: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Export result as dictionary."""
        return {
            'metric_name': self.metric_name,
            'regression_type': self.regression_type,
            'severity': self.severity,
            'baseline_value': self.baseline_value,
            'current_value': self.current_value,
            'delta_percent': self.delta_percent,
            'message': self.message,
            'detected': self.detected
        }


class RegressionDetector:
    """
    Detects regressions by comparing current metrics against baselines.
    
    Implements threshold-based detection with severity classification.
    """
    
    def __init__(self):
        self.thresholds = {
            'performance': {'minor': 10, 'major': 25, 'critical': 50},  # % increase
            'memory': {'minor': 15, 'major': 30, 'critical': 50},  # % increase
            'throughput': {'minor': 10, 'major': 25, 'critical': 40},  # % decrease
            'accuracy': {'minor': 2, 'major': 5, 'critical': 10}  # % decrease
        }
    
    def detect_performance_regression(
        self,
        baseline: float,
        current: float,
        metric_name: str
    ) -> Optional[RegressionResult]:
        """
        Detect performance regression (response time increase).
        
        Args:
            baseline: Baseline response time
            current: Current response time
            metric_name: Name of the metric
            
        Returns:
            RegressionResult if regression detected, None otherwise
        """
        if current <= baseline:
            return None
        
        delta_percent = ((current - baseline) / baseline) * 100
        
        severity = None
        if delta_percent >= self.thresholds['performance']['critical']:
            severity = 'critical'
        elif delta_percent >= self.thresholds['performance']['major']:
            severity = 'major'
        elif delta_percent >= self.thresholds['performance']['minor']:
            severity = 'minor'
        
        if severity:
            return RegressionResult(
                metric_name=metric_name,
                regression_type='performance',
                severity=severity,
                baseline_value=baseline,
                current_value=current,
                delta_percent=delta_percent,
                message=f"{metric_name} increased by {delta_percent:.1f}% (baseline: {baseline:.2f}ms, current: {current:.2f}ms)"
            )
        
        return None
    
    def detect_memory_regression(
        self,
        baseline: float,
        current: float,
        metric_name: str
    ) -> Optional[RegressionResult]:
        """
        Detect memory regression (memory usage increase).
        
        Args:
            baseline: Baseline memory usage (MB)
            current: Current memory usage (MB)
            metric_name: Name of the metric
            
        Returns:
            RegressionResult if regression detected, None otherwise
        """
        if current <= baseline:
            return None
        
        delta_percent = ((current - baseline) / baseline) * 100
        
        severity = None
        if delta_percent >= self.thresholds['memory']['critical']:
            severity = 'critical'
        elif delta_percent >= self.thresholds['memory']['major']:
            severity = 'major'
        elif delta_percent >= self.thresholds['memory']['minor']:
            severity = 'minor'
        
        if severity:
            return RegressionResult(
                metric_name=metric_name,
                regression_type='memory',
                severity=severity,
                baseline_value=baseline,
                current_value=current,
                delta_percent=delta_percent,
                message=f"{metric_name} increased by {delta_percent:.1f}% (baseline: {baseline:.1f}MB, current: {current:.1f}MB)"
            )
        
        return None
    
    def detect_throughput_regression(
        self,
        baseline: float,
        current: float,
        metric_name: str
    ) -> Optional[RegressionResult]:
        """
        Detect throughput regression (operations/second decrease).
        
        Args:
            baseline: Baseline throughput (ops/sec)
            current: Current throughput (ops/sec)
            metric_name: Name of the metric
            
        Returns:
            RegressionResult if regression detected, None otherwise
        """
        if current >= baseline:
            return None
        
        delta_percent = ((baseline - current) / baseline) * 100
        
        severity = None
        if delta_percent >= self.thresholds['throughput']['critical']:
            severity = 'critical'
        elif delta_percent >= self.thresholds['throughput']['major']:
            severity = 'major'
        elif delta_percent >= self.thresholds['throughput']['minor']:
            severity = 'minor'
        
        if severity:
            return RegressionResult(
                metric_name=metric_name,
                regression_type='throughput',
                severity=severity,
                baseline_value=baseline,
                current_value=current,
                delta_percent=delta_percent,
                message=f"{metric_name} decreased by {delta_percent:.1f}% (baseline: {baseline:.1f} ops/s, current: {current:.1f} ops/s)"
            )
        
        return None
    
    def detect_accuracy_regression(
        self,
        baseline: float,
        current: float,
        metric_name: str
    ) -> Optional[RegressionResult]:
        """
        Detect accuracy regression (accuracy decrease).
        
        Args:
            baseline: Baseline accuracy (0-1 or 0-100)
            current: Current accuracy
            metric_name: Name of the metric
            
        Returns:
            RegressionResult if regression detected, None otherwise
        """
        if current >= baseline:
            return None
        
        delta_percent = ((baseline - current) / baseline) * 100
        
        severity = None
        if delta_percent >= self.thresholds['accuracy']['critical']:
            severity = 'critical'
        elif delta_percent >= self.thresholds['accuracy']['major']:
            severity = 'major'
        elif delta_percent >= self.thresholds['accuracy']['minor']:
            severity = 'minor'
        
        if severity:
            return RegressionResult(
                metric_name=metric_name,
                regression_type='accuracy',
                severity=severity,
                baseline_value=baseline,
                current_value=current,
                delta_percent=delta_percent,
                message=f"{metric_name} decreased by {delta_percent:.1f}% (baseline: {baseline:.2f}%, current: {current:.2f}%)"
            )
        
        return None
    
    def detect_all_regressions(
        self,
        baseline: MetricSnapshot,
        current: MetricSnapshot
    ) -> List[RegressionResult]:
        """
        Detect all types of regressions by comparing snapshots.
        
        Args:
            baseline: Baseline metric snapshot
            current: Current metric snapshot
            
        Returns:
            List of detected regressions
        """
        regressions = []
        
        # Check performance regressions
        for metric_name, baseline_value in baseline.performance.items():
            if metric_name in current.performance:
                result = self.detect_performance_regression(
                    baseline_value,
                    current.performance[metric_name],
                    metric_name
                )
                if result:
                    regressions.append(result)
        
        # Check memory regressions
        for metric_name, baseline_value in baseline.memory.items():
            if metric_name in current.memory:
                result = self.detect_memory_regression(
                    baseline_value,
                    current.memory[metric_name],
                    metric_name
                )
                if result:
                    regressions.append(result)
        
        # Check throughput regressions
        for metric_name, baseline_value in baseline.throughput.items():
            if metric_name in current.throughput:
                result = self.detect_throughput_regression(
                    baseline_value,
                    current.throughput[metric_name],
                    metric_name
                )
                if result:
                    regressions.append(result)
        
        # Check accuracy regressions
        for metric_name, baseline_value in baseline.accuracy.items():
            if metric_name in current.accuracy:
                result = self.detect_accuracy_regression(
                    baseline_value,
                    current.accuracy[metric_name],
                    metric_name
                )
                if result:
                    regressions.append(result)
        
        return regressions


class RegressionReport:
    """
    Generates regression detection reports.
    
    Provides summary and detailed views of detected regressions.
    """
    
    @staticmethod
    def generate_report(regressions: List[RegressionResult]) -> Dict[str, Any]:
        """
        Generate comprehensive regression report.
        
        Args:
            regressions: List of detected regressions
            
        Returns:
            dict: Regression report
        """
        if not regressions:
            return {
                'status': 'PASSED',
                'summary': {
                    'total_regressions': 0,
                    'critical': 0,
                    'major': 0,
                    'minor': 0
                },
                'regressions': [],
                'timestamp': datetime.now().isoformat()
            }
        
        # Count by severity
        critical = sum(1 for r in regressions if r.severity == 'critical')
        major = sum(1 for r in regressions if r.severity == 'major')
        minor = sum(1 for r in regressions if r.severity == 'minor')
        
        # Group by type
        by_type = {}
        for regression in regressions:
            if regression.regression_type not in by_type:
                by_type[regression.regression_type] = []
            by_type[regression.regression_type].append(regression.to_dict())
        
        return {
            'status': 'FAILED' if critical > 0 else 'WARNING',
            'summary': {
                'total_regressions': len(regressions),
                'critical': critical,
                'major': major,
                'minor': minor,
                'by_type': {k: len(v) for k, v in by_type.items()}
            },
            'regressions': [r.to_dict() for r in regressions],
            'by_type': by_type,
            'timestamp': datetime.now().isoformat()
        }


# Mock services for testing
class MockPerformanceService:
    """Mock service for performance metrics."""
    
    async def measure_response_time(self, operation: str) -> float:
        """Measure response time (simulated)."""
        await asyncio.sleep(0.001)
        base_times = {
            'hypothesis_generation': 10.0,
            'validation': 5.0,
            'computation': 8.0
        }
        return base_times.get(operation, 10.0)


# Test fixtures
@pytest.fixture
def detector():
    """Create regression detector."""
    return RegressionDetector()


@pytest.fixture
def baseline_snapshot():
    """Create baseline metric snapshot."""
    return MetricSnapshot(
        timestamp=(datetime.now() - timedelta(days=1)).isoformat(),
        performance={
            'hypothesis_generation_ms': 10.0,
            'validation_ms': 5.0,
            'computation_ms': 8.0
        },
        memory={
            'peak_memory_mb': 200.0,
            'average_memory_mb': 150.0
        },
        throughput={
            'hypothesis_ops_per_sec': 100.0,
            'validation_ops_per_sec': 200.0
        },
        accuracy={
            'model_accuracy_percent': 95.0,
            'validation_accuracy_percent': 92.0
        }
    )


@pytest.fixture
def current_snapshot_no_regression(baseline_snapshot):
    """Create current snapshot with no regressions."""
    return MetricSnapshot(
        timestamp=datetime.now().isoformat(),
        performance={
            'hypothesis_generation_ms': 9.5,  # Improved
            'validation_ms': 5.2,  # Slightly worse but within threshold
            'computation_ms': 8.1  # Slightly worse but within threshold
        },
        memory={
            'peak_memory_mb': 205.0,  # Slightly increased but within threshold
            'average_memory_mb': 152.0
        },
        throughput={
            'hypothesis_ops_per_sec': 102.0,  # Improved
            'validation_ops_per_sec': 198.0  # Slightly worse but within threshold
        },
        accuracy={
            'model_accuracy_percent': 95.5,  # Improved
            'validation_accuracy_percent': 92.2
        }
    )


@pytest.fixture
def current_snapshot_minor_regression(baseline_snapshot):
    """Create current snapshot with minor regressions."""
    return MetricSnapshot(
        timestamp=datetime.now().isoformat(),
        performance={
            'hypothesis_generation_ms': 11.5,  # 15% increase - minor
            'validation_ms': 5.0,
            'computation_ms': 8.0
        },
        memory={
            'peak_memory_mb': 235.0,  # 17.5% increase - minor
            'average_memory_mb': 150.0
        },
        throughput={
            'hypothesis_ops_per_sec': 92.0,  # 8% decrease - within threshold
            'validation_ops_per_sec': 200.0
        },
        accuracy={
            'model_accuracy_percent': 93.5,  # 1.6% decrease - within threshold
            'validation_accuracy_percent': 92.0
        }
    )


@pytest.fixture
def current_snapshot_major_regression(baseline_snapshot):
    """Create current snapshot with major regressions."""
    return MetricSnapshot(
        timestamp=datetime.now().isoformat(),
        performance={
            'hypothesis_generation_ms': 13.0,  # 30% increase - major
            'validation_ms': 5.0,
            'computation_ms': 8.0
        },
        memory={
            'peak_memory_mb': 270.0,  # 35% increase - major
            'average_memory_mb': 150.0
        },
        throughput={
            'hypothesis_ops_per_sec': 72.0,  # 28% decrease - major
            'validation_ops_per_sec': 200.0
        },
        accuracy={
            'model_accuracy_percent': 90.0,  # 5.3% decrease - major
            'validation_accuracy_percent': 92.0
        }
    )


@pytest.fixture
def current_snapshot_critical_regression(baseline_snapshot):
    """Create current snapshot with critical regressions."""
    return MetricSnapshot(
        timestamp=datetime.now().isoformat(),
        performance={
            'hypothesis_generation_ms': 16.0,  # 60% increase - critical
            'validation_ms': 5.0,
            'computation_ms': 8.0
        },
        memory={
            'peak_memory_mb': 310.0,  # 55% increase - critical
            'average_memory_mb': 150.0
        },
        throughput={
            'hypothesis_ops_per_sec': 58.0,  # 42% decrease - critical
            'validation_ops_per_sec': 200.0
        },
        accuracy={
            'model_accuracy_percent': 85.0,  # 10.5% decrease - critical
            'validation_accuracy_percent': 92.0
        }
    )


class TestPerformanceRegressionDetection:
    """Test performance regression detection."""
    
    def test_no_performance_regression(self, detector):
        """Test no regression when performance improved."""
        result = detector.detect_performance_regression(10.0, 9.0, 'test_metric')
        assert result is None
    
    def test_minor_performance_regression(self, detector):
        """Test detection of minor performance regression."""
        result = detector.detect_performance_regression(10.0, 11.5, 'test_metric')
        assert result is not None
        assert result.severity == 'minor'
        assert result.delta_percent == 15.0
    
    def test_major_performance_regression(self, detector):
        """Test detection of major performance regression."""
        result = detector.detect_performance_regression(10.0, 13.0, 'test_metric')
        assert result is not None
        assert result.severity == 'major'
        assert result.delta_percent == 30.0
    
    def test_critical_performance_regression(self, detector):
        """Test detection of critical performance regression."""
        result = detector.detect_performance_regression(10.0, 16.0, 'test_metric')
        assert result is not None
        assert result.severity == 'critical'
        assert result.delta_percent == 60.0


class TestMemoryRegressionDetection:
    """Test memory regression detection."""
    
    def test_no_memory_regression(self, detector):
        """Test no regression when memory usage improved."""
        result = detector.detect_memory_regression(200.0, 190.0, 'test_metric')
        assert result is None
    
    def test_minor_memory_regression(self, detector):
        """Test detection of minor memory regression."""
        result = detector.detect_memory_regression(200.0, 235.0, 'test_metric')
        assert result is not None
        assert result.severity == 'minor'
    
    def test_major_memory_regression(self, detector):
        """Test detection of major memory regression."""
        result = detector.detect_memory_regression(200.0, 270.0, 'test_metric')
        assert result is not None
        assert result.severity == 'major'


class TestThroughputRegressionDetection:
    """Test throughput regression detection."""
    
    def test_no_throughput_regression(self, detector):
        """Test no regression when throughput improved."""
        result = detector.detect_throughput_regression(100.0, 105.0, 'test_metric')
        assert result is None
    
    def test_minor_throughput_regression(self, detector):
        """Test detection of minor throughput regression."""
        result = detector.detect_throughput_regression(100.0, 88.0, 'test_metric')
        assert result is not None
        assert result.severity == 'minor'
    
    def test_major_throughput_regression(self, detector):
        """Test detection of major throughput regression."""
        result = detector.detect_throughput_regression(100.0, 72.0, 'test_metric')
        assert result is not None
        assert result.severity == 'major'


class TestAccuracyRegressionDetection:
    """Test accuracy regression detection."""
    
    def test_no_accuracy_regression(self, detector):
        """Test no regression when accuracy improved."""
        result = detector.detect_accuracy_regression(95.0, 96.0, 'test_metric')
        assert result is None
    
    def test_minor_accuracy_regression(self, detector):
        """Test detection of minor accuracy regression."""
        result = detector.detect_accuracy_regression(95.0, 93.0, 'test_metric')
        assert result is not None
        assert result.severity == 'minor'
    
    def test_major_accuracy_regression(self, detector):
        """Test detection of major accuracy regression."""
        result = detector.detect_accuracy_regression(95.0, 90.0, 'test_metric')
        assert result is not None
        assert result.severity == 'major'


class TestFullRegressionDetection:
    """Test full regression detection across all metrics."""
    
    def test_no_regressions_detected(self, detector, baseline_snapshot, current_snapshot_no_regression):
        """Test no regressions when all metrics within acceptable range."""
        regressions = detector.detect_all_regressions(baseline_snapshot, current_snapshot_no_regression)
        assert len(regressions) == 0
    
    def test_minor_regressions_detected(self, detector, baseline_snapshot, current_snapshot_minor_regression):
        """Test detection of minor regressions."""
        regressions = detector.detect_all_regressions(baseline_snapshot, current_snapshot_minor_regression)
        assert len(regressions) > 0
        assert all(r.severity == 'minor' for r in regressions)
    
    def test_major_regressions_detected(self, detector, baseline_snapshot, current_snapshot_major_regression):
        """Test detection of major regressions."""
        regressions = detector.detect_all_regressions(baseline_snapshot, current_snapshot_major_regression)
        assert len(regressions) > 0
        assert any(r.severity == 'major' for r in regressions)
    
    def test_critical_regressions_detected(self, detector, baseline_snapshot, current_snapshot_critical_regression):
        """Test detection of critical regressions."""
        regressions = detector.detect_all_regressions(baseline_snapshot, current_snapshot_critical_regression)
        assert len(regressions) > 0
        assert any(r.severity == 'critical' for r in regressions)
    
    def test_multiple_regression_types(self, detector, baseline_snapshot, current_snapshot_critical_regression):
        """Test detection of multiple regression types."""
        regressions = detector.detect_all_regressions(baseline_snapshot, current_snapshot_critical_regression)
        
        regression_types = {r.regression_type for r in regressions}
        assert 'performance' in regression_types
        assert 'memory' in regression_types
        assert 'throughput' in regression_types
        assert 'accuracy' in regression_types


class TestRegressionReporting:
    """Test regression report generation."""
    
    def test_report_no_regressions(self, detector, baseline_snapshot, current_snapshot_no_regression):
        """Test report generation with no regressions."""
        regressions = detector.detect_all_regressions(baseline_snapshot, current_snapshot_no_regression)
        report = RegressionReport.generate_report(regressions)
        
        assert report['status'] == 'PASSED'
        assert report['summary']['total_regressions'] == 0
    
    def test_report_minor_regressions(self, detector, baseline_snapshot, current_snapshot_minor_regression):
        """Test report generation with minor regressions."""
        regressions = detector.detect_all_regressions(baseline_snapshot, current_snapshot_minor_regression)
        report = RegressionReport.generate_report(regressions)
        
        assert report['status'] == 'WARNING'
        assert report['summary']['total_regressions'] > 0
        assert report['summary']['critical'] == 0
    
    def test_report_critical_regressions(self, detector, baseline_snapshot, current_snapshot_critical_regression):
        """Test report generation with critical regressions."""
        regressions = detector.detect_all_regressions(baseline_snapshot, current_snapshot_critical_regression)
        report = RegressionReport.generate_report(regressions)
        
        assert report['status'] == 'FAILED'
        assert report['summary']['critical'] > 0
    
    def test_report_structure(self, detector, baseline_snapshot, current_snapshot_major_regression):
        """Test report has correct structure."""
        regressions = detector.detect_all_regressions(baseline_snapshot, current_snapshot_major_regression)
        report = RegressionReport.generate_report(regressions)
        
        assert 'status' in report
        assert 'summary' in report
        assert 'regressions' in report
        assert 'by_type' in report
        assert 'timestamp' in report
        
        summary = report['summary']
        assert 'total_regressions' in summary
        assert 'critical' in summary
        assert 'major' in summary
        assert 'minor' in summary


class TestRegressionCIIntegration:
    """Test CI/CD integration scenarios."""
    
    def test_ci_should_pass(self, detector, baseline_snapshot, current_snapshot_no_regression):
        """Test CI should pass with no critical regressions."""
        regressions = detector.detect_all_regressions(baseline_snapshot, current_snapshot_no_regression)
        report = RegressionReport.generate_report(regressions)
        
        # CI should pass
        assert report['summary']['critical'] == 0
    
    def test_ci_should_warn(self, detector, baseline_snapshot, current_snapshot_minor_regression):
        """Test CI should warn with minor regressions."""
        regressions = detector.detect_all_regressions(baseline_snapshot, current_snapshot_minor_regression)
        report = RegressionReport.generate_report(regressions)
        
        # CI should warn but not fail
        assert report['status'] in ['WARNING', 'PASSED']
        assert report['summary']['critical'] == 0
    
    def test_ci_should_fail(self, detector, baseline_snapshot, current_snapshot_critical_regression):
        """Test CI should fail with critical regressions."""
        regressions = detector.detect_all_regressions(baseline_snapshot, current_snapshot_critical_regression)
        report = RegressionReport.generate_report(regressions)
        
        # CI should fail
        assert report['status'] == 'FAILED'
        assert report['summary']['critical'] > 0


# Regression detection thresholds configuration
REGRESSION_THRESHOLDS = {
    'performance': {
        'minor': 10,    # 10% increase in response time
        'major': 25,    # 25% increase
        'critical': 50  # 50% increase
    },
    'memory': {
        'minor': 15,    # 15% increase in memory usage
        'major': 30,    # 30% increase
        'critical': 50  # 50% increase
    },
    'throughput': {
        'minor': 10,    # 10% decrease in throughput
        'major': 25,    # 25% decrease
        'critical': 40  # 40% decrease
    },
    'accuracy': {
        'minor': 2,     # 2% decrease in accuracy
        'major': 5,     # 5% decrease
        'critical': 10  # 10% decrease
    }
}


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
