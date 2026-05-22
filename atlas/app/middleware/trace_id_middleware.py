import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar

_trace_id_var: ContextVar[str | None] = ContextVar("trace_id", default=None)

TRACE_HEADER = "X-Trace-Id"


def get_current_trace_id() -> str | None:  # pragma: no cover - trivial
    return _trace_id_var.get()

def ensure_trace_id(existing: str | None = None) -> str:
    cur = _trace_id_var.get()
    if cur:
        return cur
    new_id = existing or str(uuid.uuid4())
    _trace_id_var.set(new_id)
    return new_id

class TraceIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        incoming = request.headers.get(TRACE_HEADER)
        trace_id = ensure_trace_id(incoming)
        # Exponer también en request.state
        request.state.trace_id = trace_id
        response: Response = await call_next(request)
        response.headers[TRACE_HEADER] = trace_id
        return response
