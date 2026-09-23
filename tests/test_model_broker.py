import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
import yaml

from core.model_broker import (
    GlobalRequestGate,
    ModelBroker,
    _reset_global_request_gate_for_tests,
)
from core.ollama_client import OllamaCloudClient


ROOT = Path(__file__).resolve().parents[1]


class _FakeClient:
    def __init__(self):
        self.active = 0
        self.peak = 0
        self.started: list[str] = []
        self.closed = False

    async def chat(self, *, marker: str, delay: float = 0.01, **_kwargs):
        self.active += 1
        self.peak = max(self.peak, self.active)
        self.started.append(marker)
        try:
            await asyncio.sleep(delay)
            return {"message": {"content": marker}}
        finally:
            self.active -= 1

    async def close(self):
        self.closed = True


async def test_broker_never_exceeds_three_active_requests():
    client = _FakeClient()
    broker = ModelBroker(client=client, max_concurrency=3)

    responses = await asyncio.gather(
        *(broker.chat(marker=f"job-{index}") for index in range(30))
    )

    assert client.peak == 3
    assert broker.metrics.peak_active == 3
    assert broker.metrics.completed == 30
    assert [item["message"]["content"] for item in responses] == [
        f"job-{index}" for index in range(30)
    ]
    await broker.close()
    assert client.closed is True


async def test_broker_priority_applies_to_waiting_jobs():
    client = _FakeClient()
    broker = ModelBroker(client=client, max_concurrency=1)

    blocker = asyncio.create_task(
        broker.chat(marker="blocker", delay=0.04, priority=100)
    )
    await asyncio.sleep(0.005)
    low = asyncio.create_task(broker.chat(marker="low", priority=100))
    high = asyncio.create_task(broker.chat(marker="high", priority=1))
    await asyncio.gather(blocker, low, high)

    assert client.started == ["blocker", "high", "low"]
    await broker.close()


async def test_broker_propagates_failures_and_keeps_processing():
    class FailingClient(_FakeClient):
        async def chat(self, *, marker: str, **kwargs):
            if marker == "bad":
                raise ValueError("expected failure")
            return await super().chat(marker=marker, **kwargs)

    client = FailingClient()
    broker = ModelBroker(client=client, max_concurrency=2)

    with pytest.raises(ValueError, match="expected failure"):
        await broker.chat(marker="bad")
    result = await broker.chat(marker="good")

    assert result["message"]["content"] == "good"
    assert broker.metrics.failed == 1
    assert broker.metrics.completed == 1
    await broker.close()


async def test_broker_rejects_new_work_after_close():
    broker = ModelBroker(client=_FakeClient(), max_concurrency=3)
    await broker.close()

    with pytest.raises(RuntimeError, match="closed"):
        await broker.chat(marker="late")


async def test_broker_cancelled_caller_stops_active_call_and_releases_worker():
    started = asyncio.Event()
    stopped = asyncio.Event()

    class CancellableClient(_FakeClient):
        async def chat(self, *, marker: str, **kwargs):
            if marker == "cancel-me":
                started.set()
                try:
                    await asyncio.Event().wait()
                finally:
                    stopped.set()
            return await super().chat(marker=marker, **kwargs)

    broker = ModelBroker(CancellableClient(), max_concurrency=1)
    abandoned = asyncio.create_task(broker.chat(marker="cancel-me"))
    try:
        await asyncio.wait_for(started.wait(), timeout=1)
        abandoned.cancel()
        with pytest.raises(asyncio.CancelledError):
            await abandoned
        await asyncio.wait_for(stopped.wait(), timeout=0.2)
        response = await asyncio.wait_for(broker.chat(marker="next"), timeout=1)
        assert response["message"]["content"] == "next"
        assert broker.metrics.cancelled == 1
        assert broker.metrics.completed == 1
        assert broker.metrics.active == 0
    finally:
        await broker.close(drain=False)


async def test_broker_close_without_drain_resolves_every_waiting_caller():
    started = asyncio.Event()

    class BlockingClient(_FakeClient):
        async def chat(self, **_kwargs):
            started.set()
            await asyncio.Event().wait()

    broker = ModelBroker(BlockingClient(), max_concurrency=1)
    active = asyncio.create_task(broker.chat(marker="active"))
    await asyncio.wait_for(started.wait(), timeout=1)
    queued = [asyncio.create_task(broker.chat(marker=str(i))) for i in range(3)]
    await asyncio.sleep(0)  # Let each caller enqueue before closing.
    try:
        await broker.close(drain=False)
        _, pending = await asyncio.wait([active, *queued], timeout=0.2)
        assert not pending, "closing the broker left queued callers hanging"
        assert all(task.cancelled() for task in [active, *queued])
        assert broker.metrics.cancelled == 4
        assert broker.metrics.active == 0
        assert broker._queue.empty()
        await asyncio.wait_for(broker._queue.join(), timeout=0.2)
    finally:
        for task in [active, *queued]:
            task.cancel()
        await asyncio.gather(active, *queued, return_exceptions=True)


async def test_cancelling_broker_close_still_cleans_workers_queue_and_client():
    started = asyncio.Event()

    class BlockingClient(_FakeClient):
        async def chat(self, **_kwargs):
            started.set()
            await asyncio.Event().wait()

    client = BlockingClient()
    broker = ModelBroker(client, max_concurrency=1)
    active = asyncio.create_task(broker.chat(marker="active"))
    await asyncio.wait_for(started.wait(), timeout=1)
    queued = asyncio.create_task(broker.chat(marker="queued"))
    closing = asyncio.create_task(broker.close())
    await asyncio.sleep(0)  # Close is now waiting for the blocked queue to drain.
    try:
        closing.cancel()
        with pytest.raises(asyncio.CancelledError):
            await closing
        assert client.closed, "cancelling close left the model client open"
        assert all(worker.done() for worker in broker._workers)
        assert active.cancelled() and queued.cancelled()
        assert broker.metrics.active == 0
        assert broker.metrics.cancelled == 2
        await asyncio.wait_for(broker._queue.join(), timeout=0.2)
    finally:
        for task in [active, queued, closing, *broker._workers]:
            task.cancel()
        await asyncio.gather(active, queued, closing, *broker._workers, return_exceptions=True)


async def test_direct_ollama_clients_share_transport_limit():
    gate = _reset_global_request_gate_for_tests(3)
    tracker = {"active": 0, "peak": 0}
    tracker_lock = threading.Lock()

    class Response:
        status_code = 200

        def json(self):
            return {"message": {"content": "ok"}}

    class FakeHttp:
        async def post(self, *_args, **_kwargs):
            with tracker_lock:
                tracker["active"] += 1
                tracker["peak"] = max(tracker["peak"], tracker["active"])
            try:
                await asyncio.sleep(0.01)
                return Response()
            finally:
                with tracker_lock:
                    tracker["active"] -= 1

    clients = []
    for _ in range(12):
        client = OllamaCloudClient.__new__(OllamaCloudClient)
        client.base_url = "https://example.invalid/api"
        client._request_gate = gate
        client._get_http = lambda http=FakeHttp(): _async_value(http)
        client._total_timeout = lambda: 1.0
        clients.append(client)

    await asyncio.gather(
        *(client._do_request("/chat", {}, "secret") for client in clients)
    )

    assert tracker["peak"] == 3
    assert gate.metrics.peak_active == 3
    assert gate.metrics.acquired == 12


async def _async_value(value):
    return value


def test_global_gate_works_across_distinct_event_loops():
    gate = GlobalRequestGate(3, poll_interval=0.001)
    tracker = {"active": 0, "peak": 0}
    tracker_lock = threading.Lock()

    async def one_call():
        async with gate.slot():
            with tracker_lock:
                tracker["active"] += 1
                tracker["peak"] = max(tracker["peak"], tracker["active"])
            try:
                await asyncio.sleep(0.01)
            finally:
                with tracker_lock:
                    tracker["active"] -= 1

    # asyncio.gather must be created inside each thread's running loop.
    def run_thread():
        async def batch():
            await asyncio.gather(*(one_call() for _ in range(6)))

        asyncio.run(batch())

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(run_thread) for _ in range(2)]
        for future in futures:
            future.result(timeout=5)

    assert tracker["peak"] == 3
    assert gate.metrics.peak_active == 3


def test_release_config_pins_current_model_and_role_specific_thinking():
    config = yaml.safe_load((ROOT / "config.release.yaml").read_text(encoding="utf-8"))

    assert config["llm"]["max_concurrency"] == 2
    assert config["llm"]["reasoner"] == {
        "model": "deepseek-v4.1-flash:cloud",
        "temperature": 0.7,
        "max_tokens": 16384,
        "num_ctx": 1048576,
        "think": True,
    }
    assert config["llm"]["fast"]["model"] == "deepseek-v4.1-flash:cloud"
    assert config["llm"]["fast"]["think"] is False


@pytest.mark.asyncio
async def test_ollama_chat_accepts_native_json_schema():
    client = OllamaCloudClient.__new__(OllamaCloudClient)
    client._keys = ["secret"]
    client._key_failures = {}
    client._pick_key = lambda: (0, "secret")
    captured = {}

    async def fake_request(endpoint, payload, api_key):
        captured.update(endpoint=endpoint, payload=payload, api_key=api_key)
        return {"message": {"content": "{}"}}

    client._do_request = fake_request
    schema = {
        "type": "object",
        "properties": {"verdict": {"type": "string"}},
        "required": ["verdict"],
    }

    await client.chat(
        model="deepseek-v4-flash:0731-cloud",
        messages=[{"role": "user", "content": "test"}],
        format_schema=schema,
        think=False,
    )

    assert captured["endpoint"] == "/chat"
    assert captured["payload"]["format"] == schema
    assert captured["payload"]["think"] is False

    with pytest.raises(ValueError, match="mutually exclusive"):
        await client.chat(
            model="deepseek-v4-flash:0731-cloud",
            messages=[],
            format_json=True,
            format_schema=schema,
        )
