"""Cancelled experiments must release their execution resources."""

import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest

from sandbox.executor import SandboxExecutor


@pytest.mark.parametrize("language", ["python", "bash"])
async def test_cancelling_real_experiment_reaps_process(monkeypatch, language):
    """Check the actual asyncio subprocess transport as well as test doubles."""
    create_subprocess_exec = asyncio.create_subprocess_exec
    started = asyncio.Event()
    created = {}

    async def record_process(*args, **kwargs):
        proc = await create_subprocess_exec(*args, **kwargs)
        created.update(proc=proc, cwd=kwargs["cwd"])
        started.set()
        return proc

    monkeypatch.setattr(asyncio, "create_subprocess_exec", record_process)
    executor = SandboxExecutor({
        "use_docker": False, "require_isolation": False, "max_execution_time": 2,
    })
    code = "import time; time.sleep(10)" if language == "python" else "while :; do :; done"
    task = asyncio.create_task(executor.execute(code, language=language))
    try:
        await asyncio.wait_for(started.wait(), timeout=2)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(task, timeout=2)
        assert created["proc"].returncode is not None
        assert not Path(created["cwd"]).exists()
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        proc = created.get("proc")
        if proc is not None and proc.returncode is None:
            proc.kill()
            await proc.wait()


@pytest.mark.parametrize("language", ["python", "bash"])
async def test_cancelling_subprocess_experiment_kills_and_reaps_child(monkeypatch, language):
    started = asyncio.Event()

    class Process:
        returncode = None
        killed = False
        reaped = False

        async def communicate(self):
            started.set()
            await asyncio.Event().wait()

        def kill(self):
            self.killed = True
            self.returncode = -9

        async def wait(self):
            self.reaped = True
            return self.returncode

    proc = Process()
    invocation = {}

    async def create_process(*args, **kwargs):
        invocation.update(kwargs)
        return proc

    monkeypatch.setattr(asyncio, "create_subprocess_exec", create_process)
    executor = SandboxExecutor({"use_docker": False, "require_isolation": False})
    code = "print(1)" if language == "python" else "echo 1"
    task = asyncio.create_task(executor.execute(code, language=language))
    await asyncio.wait_for(started.wait(), timeout=1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    assert proc.killed, "cancelled experiment left its process alive"
    assert proc.reaped, "cancelled experiment did not reap its child"
    assert not Path(invocation["cwd"]).exists()


async def test_cancelling_docker_experiment_kills_named_container_and_cli(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    started = asyncio.Event()
    commands = []

    class Process:
        returncode = None
        killed = False
        reaped = False

        async def communicate(self):
            started.set()
            await asyncio.Event().wait()

        def kill(self):
            self.killed = True
            self.returncode = -9

        async def wait(self):
            self.reaped = True
            return self.returncode

    proc = Process()

    async def create_process(*args, **kwargs):
        commands.append(args)
        if args[:2] == ("docker", "kill"):
            cleanup = Process()
            cleanup.returncode = 0
            return cleanup
        return proc

    monkeypatch.setattr(asyncio, "create_subprocess_exec", create_process)
    monkeypatch.setattr("sandbox.executor.subprocess.run", lambda *a, **k: SimpleNamespace(stdout="sha256:test"))
    monkeypatch.setattr(SandboxExecutor, "_docker_available", staticmethod(lambda: True))
    executor = SandboxExecutor({"use_docker": True, "require_isolation": True})
    task = asyncio.create_task(executor.execute("print(1)"))
    await asyncio.wait_for(started.wait(), timeout=1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    run_command = commands[0]
    container_name = run_command[run_command.index("--name") + 1]
    assert ("docker", "kill", container_name) in commands
    assert proc.killed
    assert proc.reaped
    assert not list((tmp_path / "sandbox/scripts/docker_work").iterdir())
