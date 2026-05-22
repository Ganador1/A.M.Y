from app.tool_adapter import ToolAdapter, get_tool_registry

def test_echo_adapter_execution():
    reg = get_tool_registry()
    echo = reg.get("echo")
    assert echo is not None
    res = echo.execute({"a":1, "b":2})
    assert res.success
    assert res.output["length"] == 2
    assert res.metadata["adapter"] == "echo"

class SampleAdapter(ToolAdapter):
    name = "sample"
    def _run(self, params):
        return sum(v for v in params.values() if isinstance(v, (int,float)))

def test_custom_adapter_registration():
    from app.tool_adapter import get_tool_registry
    reg = get_tool_registry()
    adapter = SampleAdapter()
    reg.register(adapter)
    fetched = reg.get("sample")
    assert fetched is not None
    res = fetched.execute({"x":5, "y":7})
    assert res.success and res.output == 12
