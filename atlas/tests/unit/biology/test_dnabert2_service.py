import pytest

from app.services.dnabert2_service import DNABERT2GenomicsService


@pytest.mark.asyncio
async def test_encode_sequence_kmers():
    svc = DNABERT2GenomicsService()
    res = svc.encode_sequence({"sequence": "ACGTACGT", "k": 4})
    assert res["success"] is True
    assert res["k"] == 4
    assert isinstance(res["tokens"], list)
    assert len(res["tokens"]) == 5  # ACGTACGT with k=4 gives 5 tokens


@pytest.mark.asyncio
async def test_predict_motifs_and_classify():
    svc = DNABERT2GenomicsService()
    seq = "TTTTTATAAACGCG"
    res1 = svc.predict_motifs({"sequence": seq})
    assert res1["success"] is True
    assert "motifs" in res1
    assert isinstance(res1["motifs"], dict)
    assert len(res1["motifs"]["TATA_box"]) > 0

    res2 = svc.classify_promoter({"sequence": seq})
    assert res2["success"] is True
    assert "label" in res2
    assert res2["confidence"] >= 0.2
