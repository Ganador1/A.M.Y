"""
Async Processing Demo
Demonstrates advanced asynchronous processing capabilities
"""

import asyncio
import time
import logging
from app.async_processor import submit_async_task, get_async_processor, TaskType, TaskPriority

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def demo_basic_async():
    """Demo basic async task submission"""
    print("Async Processing Demo")
    print("=" * 30)

    # Start the async processor
    processor = get_async_processor()
    if not processor.running:
        print("Starting async processor...")
        asyncio.create_task(processor.start())
        await asyncio.sleep(0.1)  # Give it time to start

    # Submit a simple async task
    async def simple_task():
        await asyncio.sleep(2)
        return {"result": "Hello from async task!", "timestamp": time.time()}

    task_id = await submit_async_task(
        task_id="demo_task_1",
        coroutine=simple_task,
        task_type=TaskType.CPU_INTENSIVE,
        priority=TaskPriority.NORMAL
    )

    print(f"Task submitted: {task_id}")

    # Wait for completion
    result = await processor.wait_for_task(task_id, timeout=10)

    print(f"Task completed: {result}")

async def demo_scientific_async():
    """Demo scientific computation with async processing"""
    print("\nScientific Async Demo")
    print("=" * 30)

    def fibonacci_computation():
        """CPU-intensive fibonacci computation"""
        def fib(n):
            if n <= 1:
                return n
            return fib(n-1) + fib(n-2)

        result = fib(35)  # This will take some time
        return {"fibonacci_35": result, "computation_time": time.time()}

    from app.async_processor import run_scientific_task

    task_id = await run_scientific_task(
        task_id="fibonacci_task",
        operation=fibonacci_computation,
        task_type=TaskType.CPU_INTENSIVE
    )

    print(f"Scientific task submitted: {task_id}")

    # Check status periodically
    processor = get_async_processor()
    status = None
    for i in range(10):
        status = processor.get_task_status(task_id)
        print(f"Status check {i+1}: {status['status']}")
        if status["status"] in ["completed", "failed"]:
            break
        await asyncio.sleep(1)

    if status and status["status"] == "completed":
        print(f"Scientific computation result: {status['result']}")
    elif status:
        print(f"Task failed: {status}")
    else:
        print("Task status unknown")

async def demo_concurrent_tasks():
    """Demo concurrent task execution"""
    print("\nConcurrent Tasks Demo")
    print("=" * 30)

    async def worker_task(task_num):
        await asyncio.sleep(1)  # Simulate work
        return {"task": task_num, "result": task_num * 2, "timestamp": time.time()}

    # Submit multiple tasks
    task_ids = []
    for i in range(5):
        task_id = await submit_async_task(
            task_id=f"concurrent_task_{i}",
            coroutine=lambda i=i: worker_task(i),
            task_type=TaskType.CPU_INTENSIVE,
            priority=TaskPriority.NORMAL
        )
        task_ids.append(task_id)
        print(f"Submitted task: {task_id}")

    # Wait for all tasks to complete
    processor = get_async_processor()
    results = []
    for task_id in task_ids:
        try:
            result = await processor.wait_for_task(task_id, timeout=5)
            results.append(result)
            print(f"Task {task_id} completed: {result}")
        except Exception as e:
            print(f"Task {task_id} failed: {e}")

    print(f"All tasks completed. Total results: {len(results)}")

async def demo_system_monitoring():
    """Demo system monitoring and metrics"""
    print("\nSystem Monitoring Demo")
    print("=" * 30)

    processor = get_async_processor()

    # Start some background tasks
    for i in range(3):
        await submit_async_task(
            task_id=f"monitor_task_{i}",
            coroutine=lambda: asyncio.sleep(3),
            task_type=TaskType.CPU_INTENSIVE
        )

    # Monitor system status
    for i in range(5):
        status = processor.get_system_status()
        print(f"System status {i+1}:")
        print(f"  Running: {status['running']}")
        print(f"  Active tasks: {status['metrics']['active_tasks']}")
        print(f"  Completed tasks: {status['metrics']['completed_tasks']}")
        print(f"  Queue size: {status['metrics']['queue_size']}")

        worker_util = status['metrics']['worker_utilization']
        for pool, util in worker_util.items():
            print(".1f")

        await asyncio.sleep(1)

async def run_async_demo():
    """Run complete async processing demonstration"""
    print("AXIOM Advanced Async Processing Demo")
    print("=" * 50)

    try:
        await demo_basic_async()
        await demo_scientific_async()
        await demo_concurrent_tasks()
        await demo_system_monitoring()

        print("\nDemo completed successfully!")

    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_async_demo())
