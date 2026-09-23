"""Test trace_id propagation in feedback and decision logging.

Tests que verifican que log_decision_event incluye trace_id y que
servicios como plausibility_scoring y research_cycle_manager propagan trace_id
correctamente en sus logs de decisiones.
"""
import pytest
import logging
from unittest.mock import patch, MagicMock
from contextvars import copy_context

# Imports para testing
from app.logging_config import log_decision_event
from app.middleware.trace_id_middleware import ensure_trace_id, get_current_trace_id, _trace_id_var

class LogCapture:
    """Simple log capture handler for testing."""
    def __init__(self):
        self.logs = []
        
    def capture(self, record):
        self.logs.append(record.getMessage())
        
    def clear(self):
        self.logs.clear()


@pytest.fixture
def log_capture():
    """Fixture to capture log messages during test."""
    capture = LogCapture()
    logger = logging.getLogger("axiom")
    
    # Create custom handler
    handler = logging.Handler()
    handler.emit = capture.capture
    handler.setLevel(logging.INFO)
    
    logger.addHandler(handler)
    yield capture
    logger.removeHandler(handler)


@pytest.fixture
def trace_context():
    """Fixture that sets up trace_id context."""
    ctx = copy_context()
    def setup_trace(trace_id="test-trace-123"):
        _trace_id_var.set(trace_id)
        return trace_id
    return ctx, setup_trace


def test_log_decision_event_includes_trace_id(log_capture, trace_context):
    """Test que log_decision_event incluye trace_id cuando está disponible."""
    ctx, setup_trace = trace_context
    
    def run_test():
        # Setup trace_id
        test_trace_id = setup_trace("test-feedback-456")
        
        # Log decision event
        log_decision_event(
            event_type="test_feedback_recorded",
            phase="test_phase",
            details={"test_key": "test_value"},
            outcome="test_outcome",
            trace_id=test_trace_id
        )
        
        # Verificar que el log contiene el trace_id
        assert len(log_capture.logs) == 1
        log_msg = log_capture.logs[0]
        assert "DecisionEvent:" in log_msg
        assert "event=test_feedback_recorded" in log_msg
        assert "phase=test_phase" in log_msg
        assert "outcome=test_outcome" in log_msg
        assert "trace_id=test-feedback-456" in log_msg
        assert "test_key" in log_msg
    
    ctx.run(run_test)


def test_log_decision_event_without_trace_id(log_capture):
    """Test que log_decision_event funciona sin trace_id."""
    log_decision_event(
        event_type="test_no_trace",
        phase="test_phase",
        outcome="success"
    )
    
    assert len(log_capture.logs) == 1
    log_msg = log_capture.logs[0]
    assert "DecisionEvent:" in log_msg
    assert "event=test_no_trace" in log_msg
    assert "trace_id=" not in log_msg  # No debe aparecer si no se proporciona


def test_plausibility_service_trace_propagation():
    """Test que PlausibilityScoringService propaga trace_id en sus logs."""
    from app.services.plausibility_scoring_service import PlausibilityScoringService
    
    with patch('app.services.plausibility_scoring_service.get_current_trace_id') as mock_get_trace, \
         patch('app.services.plausibility_scoring_service.log_decision_event') as mock_log_decision:
        
        mock_get_trace.return_value = "plausibility-trace-789"
        
        # Mock vector store para evitar dependencias
        with patch('app.services.plausibility_scoring_service.vector_store_singleton') as mock_vs:
            mock_vs.count.return_value = 0  # Sin duplicaciones
            mock_vs.similarity_search.return_value = []
            
            service = PlausibilityScoringService()
            
            # Score a hypothesis
            result = service.score_hypothesis({
                "title": "Test Hypothesis",
                "description": "This is a detailed test description with quantitative elements: 25% improvement",
                "variables": ["var1", "var2", "var3"],
                "assumptions": ["assumption1"],
                "domain": "test_domain",
                "hypothesis_uuid": "test-uuid-123"
            })
            
            # Verificar que fue exitoso
            assert result["success"] is True
            assert "composite" in result
            
            # Verificar que log_decision_event fue llamado con trace_id
            mock_log_decision.assert_called_once()
            args, kwargs = mock_log_decision.call_args
            
            # Verificar event_type (siempre en kwargs)
            assert kwargs.get("event_type") == "plausibility_scored"
            # Verificar trace_id (siempre en kwargs)
            assert kwargs.get("trace_id") == "plausibility-trace-789"


@patch('app.services.research_cycle_manager.get_current_trace_id')
@patch('app.services.research_cycle_manager.log_decision_event')
def test_research_cycle_manager_feedback_trace(mock_log_decision, mock_get_trace):
    """Test que ResearchCycleManager._record_phase_feedback incluye trace_id."""
    from app.services.research_cycle_manager import ResearchCycleManager, ResearchCycle, ResearchCycleStatus
    from datetime import datetime
    
    mock_get_trace.return_value = "cycle-feedback-trace-999"
    
    manager = ResearchCycleManager()
    
    # Crear un cycle mock
    test_cycle = ResearchCycle(
        cycle_id="test-cycle-123",
        research_question="Test question",
        domain="test_domain",
        status=ResearchCycleStatus.HYPOTHESIS_GENERATION
    )
    
    # Usar asyncio para llamar al método async
    import asyncio
    
    async def run_test():
        await manager._record_phase_feedback(
            cycle=test_cycle,
            phase="hypothesis_generation",
            accuracy=0.75,
            coherence=0.80,
            validity=0.65,
            source="test"
        )
        
        # Verificar que log_decision_event fue llamado
        mock_log_decision.assert_called_once()
        args, kwargs = mock_log_decision.call_args
        
        # Verificar event_type (siempre en kwargs)
        assert kwargs.get("event_type") == "feedback_recorded"
        
        # Verificar trace_id propagation (siempre en kwargs)
        assert kwargs.get("trace_id") == "cycle-feedback-trace-999"
    
    asyncio.run(run_test())


def test_structured_log_details_truncation(log_capture):
    """Test que log_decision_event trunca detalles largos correctamente."""
    # Crear details muy largos
    large_details = {
        f"key_{i}": "x" * 200 for i in range(15)  # Más de 12 keys, strings largos
    }
    
    log_decision_event(
        event_type="test_truncation",
        details=large_details,
        trace_id="truncation-test-trace"
    )
    
    assert len(log_capture.logs) == 1
    log_msg = log_capture.logs[0]
    
    # Verificar que fue truncado
    assert "__truncated__" in log_msg
    assert "trace_id=truncation-test-trace" in log_msg
    # El mensaje no debe ser excesivamente largo
    assert len(log_msg) < 3000  # Reasonable upper bound


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
