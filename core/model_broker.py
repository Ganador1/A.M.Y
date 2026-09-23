"""Bounded, priority-aware broker for all high-volume Ollama workloads.

The discovery scheduler can create hundreds of virtual-agent jobs, but this broker
allows only ``max_concurrency`` remote calls to execute at once.  A local coordinator
therefore does not consume a model slot, and queued work can be reprioritized without
creating more Ollama sessions.

This module deliberately wraps an existing client instead of knowing about API keys.
Key selection, Retry-After handling and HTTP transport remain the responsibility of
``OllamaCloudClient``.
"""
from __future__ import annotations

import asyncio
import os
import threading
from contextlib import asynccontextmanager
from contextvars import Context, copy_context
from dataclasses import asdict, dataclass, field
from itertools import count
from typing import Any


@dataclass
class GlobalGateMetrics:
    acquired: int = 0
    active: int = 0
    peak_active: int = 0
    wait_cycles: int = 0

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


class GlobalRequestGate:
    """Process-wide, event-loop-independent limit for remote model requests.

    ``asyncio.Semaphore`` is ideal inside one scheduler, but AMY historically creates
    clients in several modules and tests may run them on different event loops. A
    threading semaphore is shared safely across those loops. Acquisition is polled
    without blocking the loop, which also makes task cancellation safe: a cancelled
    waiter cannot acquire a slot later in a background thread and leak it.
    """

    def __init__(self, max_concurrency: int = 3, poll_interval: float = 0.005):
        if max_concurrency < 1:
            raise ValueError("max_concurrency must be at least 1")
        if poll_interval <= 0:
            raise ValueError("poll_interval must be positive")
        self.max_concurrency = int(max_concurrency)
        self.poll_interval = float(poll_interval)
        self.metrics = GlobalGateMetrics()
        self._semaphore = threading.BoundedSemaphore(self.max_concurrency)
        self._metrics_lock = threading.Lock()

    async def acquire(self) -> None:
        while not self._semaphore.acquire(blocking=False):
            with self._metrics_lock:
                self.metrics.wait_cycles += 1
            await asyncio.sleep(self.poll_interval)
        with self._metrics_lock:
            self.metrics.acquired += 1
            self.metrics.active += 1
            self.metrics.peak_active = max(
                self.metrics.peak_active,
                self.metrics.active,
            )

    def release(self) -> None:
        with self._metrics_lock:
            if self.metrics.active < 1:
                raise RuntimeError("global model gate released without acquisition")
            self.metrics.active -= 1
        self._semaphore.release()

    @asynccontextmanager
    async def slot(self):
        await self.acquire()
        try:
            yield
        finally:
            self.release()


_GLOBAL_GATE: GlobalRequestGate | None = None
_GLOBAL_GATE_LOCK = threading.Lock()


def get_global_request_gate(max_concurrency: int | None = None) -> GlobalRequestGate:
    """Return AMY's process-wide transport gate.

    The first caller fixes the limit for the process. Production uses the
    ``AMY_MAX_CONCURRENT_LLM_CALLS`` environment variable and defaults to three.
    A later conflicting explicit value fails loudly instead of silently weakening
    the guarantee.
    """
    global _GLOBAL_GATE
    requested = int(
        max_concurrency
        if max_concurrency is not None
        else os.getenv("AMY_MAX_CONCURRENT_LLM_CALLS", "3")
    )
    with _GLOBAL_GATE_LOCK:
        if _GLOBAL_GATE is None:
            _GLOBAL_GATE = GlobalRequestGate(requested)
        elif max_concurrency is not None and _GLOBAL_GATE.max_concurrency != requested:
            raise RuntimeError(
                "global model concurrency was already fixed at "
                f"{_GLOBAL_GATE.max_concurrency}, cannot change it to {requested}"
            )
        return _GLOBAL_GATE


def _reset_global_request_gate_for_tests(max_concurrency: int = 3) -> GlobalRequestGate:
    """Replace the singleton in hermetic tests; never call from production code."""
    global _GLOBAL_GATE
    with _GLOBAL_GATE_LOCK:
        if _GLOBAL_GATE is not None and _GLOBAL_GATE.metrics.active:
            raise RuntimeError("cannot reset global model gate while requests are active")
        _GLOBAL_GATE = GlobalRequestGate(max_concurrency, poll_interval=0.001)
        return _GLOBAL_GATE


@dataclass
class BrokerMetrics:
    submitted: int = 0
    completed: int = 0
    failed: int = 0
    cancelled: int = 0
    active: int = 0
    peak_active: int = 0

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass(order=True)
class _QueuedRequest:
    priority: int
    sequence: int
    method: str
    kwargs: dict[str, Any]
    future: asyncio.Future
    context: Context = field(compare=False, repr=False)


class ModelBroker:
    """Run client methods through a bounded priority queue.

    Lower numeric priorities run first.  Requests already executing are never
    preempted; priority only affects queued requests.  One broker should be shared by
    a campaign so its metrics describe the entire campaign.
    """

    def __init__(self, client: Any, max_concurrency: int = 3):
        if max_concurrency < 1:
            raise ValueError("max_concurrency must be at least 1")
        self.client = client
        self.max_concurrency = int(max_concurrency)
        self.metrics = BrokerMetrics()
        self._queue: asyncio.PriorityQueue[_QueuedRequest] | None = None
        self._workers: list[asyncio.Task] = []
        self._sequence = count()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._closed = False

    async def chat(self, *, priority: int = 100, **kwargs) -> dict:
        return await self._submit("chat", priority, kwargs)

    async def generate(self, *, priority: int = 100, **kwargs) -> dict:
        return await self._submit("generate", priority, kwargs)

    async def embed(self, *, priority: int = 100, **kwargs):
        return await self._submit("embed", priority, kwargs)

    async def _submit(self, method: str, priority: int, kwargs: dict[str, Any]):
        if self._closed:
            raise RuntimeError("ModelBroker is closed")
        self._ensure_workers()
        assert self._queue is not None
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        request = _QueuedRequest(
            priority=int(priority),
            sequence=next(self._sequence),
            method=method,
            kwargs=kwargs,
            future=future,
            context=copy_context(),
        )
        self.metrics.submitted += 1
        await self._queue.put(request)
        try:
            return await future
        except asyncio.CancelledError:
            if not future.done():
                future.cancel()
            raise

    def _ensure_workers(self) -> None:
        loop = asyncio.get_running_loop()
        if self._loop is not None and self._loop is not loop:
            raise RuntimeError("ModelBroker cannot be shared across event loops")
        if self._queue is None:
            self._loop = loop
            self._queue = asyncio.PriorityQueue()
            self._workers = [
                Context().run(loop.create_task, self._worker(index), name=f"model-broker-{index}")
                for index in range(self.max_concurrency)
            ]

    async def _worker(self, _index: int) -> None:
        assert self._queue is not None
        while True:
            request = await self._queue.get()
            try:
                if request.future.cancelled():
                    self.metrics.cancelled += 1
                    continue
                self.metrics.active += 1
                self.metrics.peak_active = max(
                    self.metrics.peak_active,
                    self.metrics.active,
                )
                cancel_call = None
                try:
                    method = getattr(self.client, request.method)
                    # Persistent workers must not reuse the first submitter's
                    # tracing/request context. Create this awaitable and its
                    # task in a copy of the current request's caller context.
                    call = request.context.run(
                        lambda: asyncio.ensure_future(method(**request.kwargs))
                    )

                    def cancel_call(future, pending=call):
                        if future.cancelled():
                            pending.cancel()

                    request.future.add_done_callback(cancel_call)
                    result = await call
                except asyncio.CancelledError:
                    self.metrics.cancelled += 1
                    if not request.future.done():
                        request.future.cancel()
                    # Caller cancellation stops its transport call, but must not
                    # retire this worker and strand the remaining queue. Broker
                    # shutdown cancels the worker itself and still propagates.
                    if asyncio.current_task().cancelling():
                        raise
                except Exception as exc:
                    self.metrics.failed += 1
                    if not request.future.done():
                        request.future.set_exception(exc)
                else:
                    if request.future.cancelled():
                        self.metrics.cancelled += 1
                    else:
                        self.metrics.completed += 1
                        request.future.set_result(result)
                finally:
                    if cancel_call is not None:
                        request.future.remove_done_callback(cancel_call)
                    self.metrics.active -= 1
            finally:
                self._queue.task_done()

    async def close(self, *, drain: bool = True) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            if self._queue is not None and drain:
                await self._queue.join()
        finally:
            # A cancelled campaign can also cancel its graceful close. Always
            # settle workers/callers and close the transport before propagating
            # cancellation; otherwise _closed prevents a later cleanup attempt.
            cleanup = asyncio.create_task(self._close_resources())
            try:
                await asyncio.shield(cleanup)
            except asyncio.CancelledError:
                await cleanup
                raise

    async def _close_resources(self) -> None:
        for worker in self._workers:
            worker.cancel()
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)
        # Workers can no longer consume queued requests. Resolve their callers
        # and balance task_done so close(drain=False) cannot leave hung jobs.
        if self._queue is not None:
            while not self._queue.empty():
                request = self._queue.get_nowait()
                request.future.cancel()
                self.metrics.cancelled += 1
                self._queue.task_done()
        close = getattr(self.client, "close", None)
        if close is not None:
            result = close()
            if hasattr(result, "__await__"):
                await result
