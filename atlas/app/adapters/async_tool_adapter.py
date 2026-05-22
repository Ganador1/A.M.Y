"""Async Tool Adapter (MVP)

Extensión de ToolAdapter para ejecución asíncrona con:
- Control de concurrencia configurable
- Timeouts y cancelación
- Agregación de resultados paralelos
- Manejo de errores resiliente
"""
from __future__ import annotations
import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import os

from app.adapters.tool_adapter import ToolAdapter, ToolExecutionResult
from app.config import settings


@dataclass
class AsyncExecutionConfig:
    """Configuration for async execution"""
    max_concurrent: int = 5
    timeout_seconds: float = 30.0
    retry_attempts: int = 2
    retry_delay: float = 1.0
    fail_fast: bool = False  # Stop on first error vs collect all results


class AsyncToolAdapter(ToolAdapter):
    """Async version of ToolAdapter with concurrency control"""

    def __init__(self):
        super().__init__()
        self.config = AsyncExecutionConfig(
            max_concurrent=int(
                getattr(settings, 'async_tool_max_concurrent', os.getenv('ASYNC_TOOL_MAX_CONCURRENT', '5'))
            ),
            timeout_seconds=float(
                getattr(settings, 'async_tool_timeout', os.getenv('ASYNC_TOOL_TIMEOUT', '30.0'))
            ),
            retry_attempts=int(
                getattr(settings, 'async_tool_retry_attempts', os.getenv('ASYNC_TOOL_RETRY_ATTEMPTS', '2'))
            ),
            retry_delay=float(
                getattr(settings, 'async_tool_retry_delay', os.getenv('ASYNC_TOOL_RETRY_DELAY', '1.0'))
            ),
            fail_fast=str(
                getattr(settings, 'async_tool_fail_fast', os.getenv('ASYNC_TOOL_FAIL_FAST', 'false'))
            ).lower() == 'true'
        )

    async def execute_async(self, params: Dict[str, Any]) -> ToolExecutionResult:
        """Async version of execute"""
        start = time.perf_counter()
        ih = self._hash_input(params) if self.allow_cache else None

        # Check cache first
        if ih and hasattr(self, '_check_cache'):
            cached = await self._check_cache_async(ih)
            if cached:
                return cached

        try:
            # Async validation, hooks, and execution
            await self._validate_async(params)
            await self._pre_hook_async(params)

            output = await asyncio.wait_for(
                self._run_async(params),
                timeout=self.config.timeout_seconds
            )

            await self._post_hook_async(params, output)

            result = ToolExecutionResult(
                success=True,
                output=output,
                duration_ms=(time.perf_counter() - start) * 1000.0,
                input_hash=ih,
                metadata={"adapter": self.name, "version": self.version, "async": True},
            )

        except asyncio.TimeoutError:
            result = ToolExecutionResult(
                success=False,
                error="Execution timeout",
                duration_ms=(time.perf_counter() - start) * 1000.0,
                input_hash=ih,
                metadata={"adapter": self.name, "version": self.version, "async": True},
            )
        except Exception as e:
            result = ToolExecutionResult(
                success=False,
                error=str(e),
                duration_ms=(time.perf_counter() - start) * 1000.0,
                input_hash=ih,
                metadata={"adapter": self.name, "version": self.version, "async": True},
            )

        self._last_result = result

        # Cache successful results
        if ih and hasattr(self, '_cache_result'):
            await self._cache_result_async(ih, result)

        # Record metrics if available
        if hasattr(self, '_record_metrics'):
            await self._record_metrics_async(result)

        return result

    async def execute_batch_async(
        self,
        param_list: List[Dict[str, Any]],
        config: Optional[AsyncExecutionConfig] = None
    ) -> List[ToolExecutionResult]:
        """Execute multiple parameter sets concurrently"""
        config = config or self.config

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(config.max_concurrent)

        async def execute_with_semaphore(params: Dict[str, Any]) -> ToolExecutionResult:
            async with semaphore:
                for attempt in range(config.retry_attempts + 1):
                    try:
                        return await self.execute_async(params)
                    except Exception as e:
                        if attempt == config.retry_attempts:
                            # Final attempt failed
                            return ToolExecutionResult(
                                success=False,
                                error=f"Failed after {attempt + 1} attempts: {str(e)}",
                                duration_ms=0.0,
                                metadata={"adapter": self.name, "attempts": attempt + 1}
                            )
                        # Wait before retry
                        await asyncio.sleep(config.retry_delay)

                # This should never be reached, but provide fallback
                return ToolExecutionResult(  # pragma: no cover
                    success=False,
                    error="Unexpected execution path",
                    duration_ms=0.0,
                    metadata={"adapter": self.name}
                )

        # Execute all tasks
        if config.fail_fast:
            # Stop on first error
            results = []
            for params in param_list:
                result = await execute_with_semaphore(params)
                results.append(result)
                if not result.success:
                    break
            return results
        else:
            # Collect all results regardless of failures
            tasks = [execute_with_semaphore(params) for params in param_list]
            return await asyncio.gather(*tasks, return_exceptions=False)

    # ---- Async overridables ----
    async def _validate_async(self, params: Dict[str, Any]) -> None:
        """Async validation - default delegates to sync version"""
        self._validate(params)

    async def _pre_hook_async(self, params: Dict[str, Any]) -> None:
        """Async pre-hook - default delegates to sync version"""
        self._pre_hook(params)

    async def _run_async(self, params: Dict[str, Any]) -> Any:
        """Async execution - must be overridden"""
        raise NotImplementedError("Async adapters must implement _run_async")

    async def _post_hook_async(self, params: Dict[str, Any], output: Any) -> None:
        """Async post-hook - default delegates to sync version"""
        self._post_hook(params, output)

    # ---- Cache helpers ----
    async def _check_cache_async(self, input_hash: str) -> Optional[ToolExecutionResult]:
        """Check cache asynchronously"""
        # For now, delegate to sync cache
        try:
            from app.adapters.tool_adapter_cache import tool_adapter_cache
            if tool_adapter_cache:
                return tool_adapter_cache.get(f"{self.name}:{input_hash}")
        except Exception:  # pragma: no cover
            pass
        return None

    async def _cache_result_async(self, input_hash: str, result: ToolExecutionResult) -> None:
        """Cache result asynchronously"""
        # For now, delegate to sync cache
        try:
            from app.adapters.tool_adapter_cache import tool_adapter_cache
            if tool_adapter_cache and result.success:
                tool_adapter_cache.put(f"{self.name}:{input_hash}", result)
        except Exception:  # pragma: no cover
            pass

    async def _record_metrics_async(self, result: ToolExecutionResult) -> None:
        """Record metrics asynchronously"""
        try:
            from app.monitoring.metrics import metrics
            if metrics:
                metrics.record_tool_adapter_execution(self.name, result.success, result.duration_ms)
        except Exception:  # pragma: no cover
            pass


class BatchProcessor:
    """Utility for processing multiple tools/params combinations"""

    def __init__(self, adapters: Dict[str, Any]):  # More flexible typing
        self.adapters = adapters

    async def process_cross_product(
        self,
        tool_params: Dict[str, List[Dict[str, Any]]],
        config: Optional[AsyncExecutionConfig] = None
    ) -> Dict[str, List[ToolExecutionResult]]:
        """Process cross product of tools and their parameters"""
        results = {}

        for tool_name, param_sets in tool_params.items():
            adapter = self.adapters.get(tool_name)
            if not adapter:
                # Create error results for missing adapter
                results[tool_name] = [
                    ToolExecutionResult(
                        success=False,
                        error=f"Adapter '{tool_name}' not found",
                        duration_ms=0.0,
                        metadata={"tool": tool_name}
                    ) for _ in param_sets
                ]
                continue

            # Execute batch for this tool
            tool_results = await adapter.execute_batch_async(param_sets, config)
            results[tool_name] = tool_results

        return results

    async def process_pipeline(
        self,
        pipeline: List[Dict[str, Any]],  # [{"tool": "name", "params": {...}}, ...]
        config: Optional[AsyncExecutionConfig] = None
    ) -> List[ToolExecutionResult]:
        """Process tools in pipeline (sequential with potential parallel batches)"""
        results = []

        for step in pipeline:
            tool_name = step["tool"]
            params = step["params"]

            adapter = self.adapters.get(tool_name)
            if not adapter:
                results.append(ToolExecutionResult(
                    success=False,
                    error=f"Adapter '{tool_name}' not found",
                    duration_ms=0.0,
                    metadata={"tool": tool_name, "step": len(results)}
                ))
                continue

            # If params is a list, execute batch; otherwise single execution
            if isinstance(params, list):
                batch_results = await adapter.execute_batch_async(params, config)
                results.extend(batch_results)
            else:
                result = await adapter.execute_async(params)
                results.append(result)

        return results


# ---- Example Async Adapter ----
class AsyncEchoAdapter(AsyncToolAdapter):
    name = "async_echo"
    version = "0.1.0"
    description = "Async dev adapter for testing concurrent execution"

    async def _run_async(self, params: Dict[str, Any]) -> Any:
        # Simulate async work with delay
        delay = params.get("delay", 0.1)
        await asyncio.sleep(delay)

        return {
            "echo": params,
            "length": len(str(params)),
            "processed_at": time.time(),
            "async": True
        }


# ---- Registry integration ----
class AsyncToolRegistry:
    """Registry for async tool adapters"""

    def __init__(self):
        self._registry: Dict[str, AsyncToolAdapter] = {}

    def register(self, adapter: AsyncToolAdapter) -> None:
        self._registry[adapter.name] = adapter

    def get(self, name: str) -> Optional[AsyncToolAdapter]:
        return self._registry.get(name)

    def list(self) -> Dict[str, Dict[str, Any]]:
        return {
            k: {
                "version": v.version,
                "description": v.description,
                "async": True,
                "config": {
                    "max_concurrent": v.config.max_concurrent,
                    "timeout_seconds": v.config.timeout_seconds,
                }
            }
            for k, v in self._registry.items()
        }

    def create_batch_processor(self) -> BatchProcessor:
        return BatchProcessor(self._registry)


# Global async registry
_async_tool_registry = AsyncToolRegistry()

def get_async_tool_registry() -> AsyncToolRegistry:
    return _async_tool_registry