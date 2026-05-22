from app.services.llm_routing_service import llm_routing_service


def test_llm_routing_small():
    res = llm_routing_service.route("hola")
    assert res["tier"] == "small"
    assert res["chosen_model"]


def test_llm_routing_promote_precision():
    long_prompt = "x" * 3000
    res = llm_routing_service.route(long_prompt, metadata={"high_precision": True})
    assert res["tier"] in {"medium", "large"}
