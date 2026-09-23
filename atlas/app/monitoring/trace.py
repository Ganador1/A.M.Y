"""
AXIOM Tracing System
Distributed tracing for monitoring and debugging
"""

import time
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from app.core.bootstrap_logging import logger


@dataclass
class TraceSpan:
    """Individual span in a trace"""
    span_id: str
    operation: str
    start_time: float
    end_time: Optional[float] = None
    parent_span_id: Optional[str] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    events: List[Dict[str, Any]] = field(default_factory=list)
    duration_ms: Optional[float] = None

    def end(self):
        """End the span"""
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add an event to the span"""
        self.events.append({
            "name": name,
            "timestamp": time.time(),
            "attributes": attributes or {}
        })

    def set_tag(self, key: str, value: Any):
        """Set a tag on the span"""
        self.tags[key] = value


@dataclass
class Trace:
    """Complete trace with multiple spans"""
    trace_id: str
    root_span_id: str
    spans: Dict[str, TraceSpan] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    service_name: str = "axiom"
    attributes: Dict[str, Any] = field(default_factory=dict)

    def add_span(self, span: TraceSpan):
        """Add a span to the trace"""
        self.spans[span.span_id] = span

    def get_root_span(self) -> Optional[TraceSpan]:
        """Get the root span of the trace"""
        return self.spans.get(self.root_span_id)

    def get_duration_ms(self) -> float:
        """Get total trace duration in milliseconds"""
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return (time.time() - self.start_time) * 1000

    def end(self):
        """End the trace"""
        self.end_time = time.time()
        # End any open spans
        for span in self.spans.values():
            if span.end_time is None:
                span.end()


class TraceManager:
    """Manager for distributed tracing"""

    def __init__(self):
        self.active_traces: Dict[str, Trace] = {}
        self.completed_traces: List[Trace] = []
        self.max_completed_traces = 1000  # Keep last 1000 traces

    def start_trace(self, operation: str, service_name: str = "axiom",
                   parent_trace_id: Optional[str] = None,
                   attributes: Optional[Dict[str, Any]] = None) -> Trace:
        """Start a new trace"""
        trace_id = str(uuid.uuid4())
        root_span_id = str(uuid.uuid4())

        # Create root span
        root_span = TraceSpan(
            span_id=root_span_id,
            operation=operation,
            start_time=time.time(),
            tags={"service": service_name}
        )

        # Create trace
        trace = Trace(
            trace_id=trace_id,
            root_span_id=root_span_id,
            service_name=service_name,
            attributes=attributes or {}
        )

        trace.add_span(root_span)
        self.active_traces[trace_id] = trace

        logger.debug(f"Started trace {trace_id} for operation {operation}")
        return trace

    def get_trace(self, trace_id: str) -> Optional[Trace]:
        """Get a trace by ID"""
        return self.active_traces.get(trace_id)

    def end_trace(self, trace_id: str):
        """End a trace"""
        if trace_id in self.active_traces:
            trace = self.active_traces[trace_id]
            trace.end()

            # Move to completed traces
            self.completed_traces.append(trace)
            del self.active_traces[trace_id]

            # Keep only recent traces
            if len(self.completed_traces) > self.max_completed_traces:
                self.completed_traces = self.completed_traces[-self.max_completed_traces:]

            logger.debug(f"Ended trace {trace_id}")

    def start_span(self, trace_id: str, operation: str,
                  parent_span_id: Optional[str] = None,
                  tags: Optional[Dict[str, Any]] = None) -> Optional[TraceSpan]:
        """Start a new span within a trace"""
        trace = self.get_trace(trace_id)
        if not trace:
            return None

        span_id = str(uuid.uuid4())
        span = TraceSpan(
            span_id=span_id,
            operation=operation,
            start_time=time.time(),
            parent_span_id=parent_span_id,
            tags=tags or {}
        )

        trace.add_span(span)
        return span

    def end_span(self, trace_id: str, span_id: str):
        """End a span"""
        trace = self.get_trace(trace_id)
        if trace and span_id in trace.spans:
            trace.spans[span_id].end()

    def get_trace_summary(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of a trace"""
        trace = self.get_trace(trace_id)
        if not trace:
            return None

        return {
            "trace_id": trace.trace_id,
            "service_name": trace.service_name,
            "duration_ms": trace.get_duration_ms(),
            "span_count": len(trace.spans),
            "start_time": trace.start_time,
            "end_time": trace.end_time,
            "attributes": trace.attributes
        }

    def get_active_traces(self) -> List[Dict[str, Any]]:
        """Get summaries of all active traces"""
        return [self.get_trace_summary(trace_id) for trace_id in self.active_traces.keys()
                if self.get_trace_summary(trace_id) is not None]

    def cleanup_old_traces(self, max_age_seconds: int = 3600):
        """Clean up traces older than specified age"""
        current_time = time.time()
        to_remove = []

        for trace_id, trace in self.active_traces.items():
            if current_time - trace.start_time > max_age_seconds:
                to_remove.append(trace_id)

        for trace_id in to_remove:
            logger.warning(f"Cleaning up stale trace {trace_id}")
            del self.active_traces[trace_id]


# Global trace manager
trace_manager = TraceManager()


def get_or_create_trace(operation: str, service_name: str = "axiom",
                       parent_trace_id: Optional[str] = None,
                       attributes: Optional[Dict[str, Any]] = None) -> Trace:
    """Get existing trace or create a new one"""
    if parent_trace_id and parent_trace_id in trace_manager.active_traces:
        # Return existing trace
        return trace_manager.active_traces[parent_trace_id]
    else:
        # Create new trace
        return trace_manager.start_trace(operation, service_name, parent_trace_id, attributes)


def start_span(trace_id: str, operation: str,
              parent_span_id: Optional[str] = None,
              tags: Optional[Dict[str, Any]] = None) -> Optional[TraceSpan]:
    """Start a span in a trace"""
    return trace_manager.start_span(trace_id, operation, parent_span_id, tags)


def end_span(trace_id: str, span_id: str):
    """End a span in a trace"""
    trace_manager.end_span(trace_id, span_id)


def end_trace(trace_id: str):
    """End a trace"""
    trace_manager.end_trace(trace_id)


def get_trace_summary(trace_id: str) -> Optional[Dict[str, Any]]:
    """Get trace summary"""
    return trace_manager.get_trace_summary(trace_id)


# Context manager for tracing
class trace_context:
    """Context manager for automatic trace lifecycle management"""

    def __init__(self, operation: str, service_name: str = "axiom",
                 attributes: Optional[Dict[str, Any]] = None):
        self.operation = operation
        self.service_name = service_name
        self.attributes = attributes
        self.trace: Optional[Trace] = None

    def __enter__(self) -> Trace:
        self.trace = get_or_create_trace(self.operation, self.service_name, None, self.attributes)
        return self.trace

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.trace:
            end_trace(self.trace.trace_id)


# Decorator for tracing functions
def traced(operation: Optional[str] = None):
    """Decorator to automatically trace function calls"""
    def decorator(func):
        op_name = operation or f"{func.__module__}.{func.__name__}"

        def wrapper(*args, **kwargs):
            with trace_context(op_name):
                return func(*args, **kwargs)

        return wrapper
    return decorator


# Cleanup function
def cleanup_traces():
    """Clean up old traces"""
    trace_manager.cleanup_old_traces()


# Export functions
__all__ = [
    "Trace",
    "TraceSpan",
    "TraceManager",
    "trace_manager",
    "get_or_create_trace",
    "start_span",
    "end_span",
    "end_trace",
    "get_trace_summary",
    "trace_context",
    "traced",
    "cleanup_traces"
]
