from typing import Dict, Any

class ToolResult:
    def __init__(self, success: bool, output: Any = None, metadata: Dict[str, Any] = None):
        self.success = success
        self.output = output
        self.metadata = metadata or {}

class ToolAdapter:
    name = "base"
    def _run(self, params: Dict[str, Any]):
        raise NotImplementedError

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        try:
            out = self._run(params)
            return ToolResult(True, out, {"adapter": self.name})
        except Exception as e:
            return ToolResult(False, None, {"adapter": self.name, "error": str(e)})

class EchoAdapter(ToolAdapter):
    name = "echo"
    def _run(self, params: Dict[str, Any]):
        # return length of params and echo
        return {"length": len(params), "echo": params}

class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, adapter: ToolAdapter):
        self._tools[adapter.name] = adapter

    def get(self, name: str):
        return self._tools.get(name)

    def all(self):
        return self._tools

_registry = ToolRegistry()
_registry.register(EchoAdapter())

def get_tool_registry() -> ToolRegistry:
    return _registry
