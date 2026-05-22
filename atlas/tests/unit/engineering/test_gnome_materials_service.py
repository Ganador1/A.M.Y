import pytest

from app.services.gnome_materials_service import GNOMEMaterialsService


@pytest.mark.asyncio
async def test_suggest_candidates():
    svc = GNOMEMaterialsService()
    res = svc.suggest_candidates({"target": "high thermal conductivity", "top_n": 2})
    assert res["success"] is True
    assert res["count"] <= 2


@pytest.mark.asyncio
async def test_predict_properties_known_and_unknown():
    svc = GNOMEMaterialsService()
    known = svc.predict_properties({"formula": "LiFePO4"})
    assert known["success"] is True
    assert "predicted_properties" in known
    unk = svc.predict_properties({"formula": "XyZ"})
    assert unk["success"] is True
    assert "stability" in unk["predicted_properties"]
