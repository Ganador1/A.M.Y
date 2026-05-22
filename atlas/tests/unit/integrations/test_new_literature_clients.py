import pytest
from unittest.mock import MagicMock, patch
from app.integrations.literature_clients import OpenTargetsClient, GwasCatalogClient

class TestOpenTargetsClient:
    @pytest.fixture
    def client(self):
        return OpenTargetsClient()

    def test_search_success(self, client):
        mock_resp = {
            "data": {
                "search": {
                    "hits": [
                        {
                            "id": "ENSG000001",
                            "name": "Target 1",
                            "entity": "target",
                            "description": "Description 1"
                        }
                    ]
                }
            }
        }
        with patch.object(client, 'post', return_value=mock_resp) as mock_post:
            res = client.search("test")
            assert res["success"] is True
            assert len(res["results"]) == 1
            assert res["results"][0]["id"] == "ENSG000001"
            assert res["results"][0]["source"] == "open_targets"
            mock_post.assert_called_once()

    def test_search_failure(self, client):
        with patch.object(client, 'post', return_value={"error": "API Error"}):
            res = client.search("test")
            assert res["success"] is False
            assert res["error"] == "API Error"

    def test_get_associated_diseases(self, client):
        mock_resp = {
            "data": {
                "target": {
                    "associatedDiseases": {
                        "rows": [
                            {
                                "disease": {"id": "EFO_001", "name": "Disease 1"},
                                "score": 0.9
                            }
                        ]
                    }
                }
            }
        }
        with patch.object(client, 'post', return_value=mock_resp):
            res = client.get_associated_diseases("ENSG000001")
            assert res["success"] is True
            assert len(res["results"]) == 1
            assert res["results"][0]["id"] == "EFO_001"

class TestGwasCatalogClient:
    @pytest.fixture
    def client(self):
        return GwasCatalogClient()

    def test_search_studies_success(self, client):
        mock_resp = {
            "_embedded": {
                "studies": [
                    {
                        "accessionId": "GCST001",
                        "title": "Study 1",
                        "diseaseTrait": {"trait": "Trait 1"}
                    }
                ]
            }
        }
        with patch.object(client, 'get', return_value=mock_resp) as mock_get:
            res = client.search_studies("test")
            assert res["success"] is True
            assert len(res["results"]) == 1
            assert res["results"][0]["id"] == "GCST001"
            assert res["results"][0]["source"] == "gwas_catalog"
            mock_get.assert_called_once()

    def test_search_studies_failure(self, client):
        with patch.object(client, 'get', return_value={"error": "API Error"}):
            res = client.search_studies("test")
            assert res["success"] is False
            assert res["error"] == "API Error"
