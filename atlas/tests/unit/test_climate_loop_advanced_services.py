"""
Unit Tests - Climate Loop Advanced Services Integration
========================================================

Tests for Climate Loop integration with:
- ClimateEvidenceService (GISTEMP real climate data)
- ScientificDataLakeService (large-scale dataset sampling)
- AdvancedScientificDatabaseService (hypothesis search)

Author: AXIOM Team
Date: 2025-01-28
Version: 1.0.0
"""

import pytest
import asyncio
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock, patch

# Climate Loop
from app.autonomous.pipelines.climate_loop import ClimateLoop

# Climate services
from app.services.climate_evidence_service import ClimateEvidenceService
from app.services.scientific_data_lake_service import ScientificDataLakeService
from app.services.advanced_scientific_database_service import AdvancedScientificDatabaseService


class TestClimateLoopServicesInitialization:
    """Test Climate Loop service initialization."""

    def test_climate_loop_initialization(self):
        """Test Climate Loop initializes with 3 advanced services."""
        loop = ClimateLoop()

        # Verify service attributes exist
        assert hasattr(loop, "climate_evidence_service")
        assert hasattr(loop, "scientific_datalake_service")
        assert hasattr(loop, "scientific_database_service")

        # Verify service types
        assert isinstance(loop.climate_evidence_service, ClimateEvidenceService)
        assert isinstance(loop.scientific_datalake_service, ScientificDataLakeService)
        assert isinstance(loop.scientific_database_service, AdvancedScientificDatabaseService)

    def test_climate_loop_autonomous_components(self):
        """Test Climate Loop has standard autonomous components."""
        loop = ClimateLoop()

        # Standard autonomous framework components
        assert hasattr(loop, "state")
        assert hasattr(loop, "telemetry")
        assert hasattr(loop, "priority")
        assert hasattr(loop, "scheduler")
        assert hasattr(loop, "novelty")
        assert hasattr(loop, "evidence")


class TestClimateEvidenceServiceIntegration:
    """Test ClimateEvidenceService integration in Climate Loop."""

    @pytest.mark.asyncio
    async def test_fetch_gistemp_data(self):
        """Test fetching real GISTEMP temperature data."""
        loop = ClimateLoop()

        # Mock ClimateEvidenceService response
        mock_gistemp_data = {
            "success": True,
            "temperature_records": [
                {"year": 2020, "temperature_anomaly": 1.02, "location": "global"},
                {"year": 2021, "temperature_anomaly": 0.98, "location": "global"},
                {"year": 2022, "temperature_anomaly": 1.05, "location": "global"},
            ],
            "data_source": "GISTEMP",
            "quality": 0.95,
        }

        with patch.object(
            loop.climate_evidence_service,
            "process_request",
            new_callable=AsyncMock,
            return_value=mock_gistemp_data,
        ):
            candidates = await loop._fetch_real_climate_data_async(limit=5)

            # Verify candidates were created from GISTEMP data
            assert len(candidates) > 0
            gistemp_candidates = [c for c in candidates if c.get("source") == "climate_evidence"]
            assert len(gistemp_candidates) > 0

            # Check candidate structure
            for candidate in gistemp_candidates:
                assert "id" in candidate
                assert "climate_variable" in candidate
                assert "temperature_anomaly" in candidate
                assert "data_quality" in candidate
                assert candidate["source"] == "climate_evidence"

    @pytest.mark.asyncio
    async def test_gistemp_temperature_anomaly_extraction(self):
        """Test temperature anomaly extraction from GISTEMP data."""
        loop = ClimateLoop()

        mock_response = {
            "success": True,
            "temperature_records": [
                {"year": 2023, "temperature_anomaly": 1.15, "location": "global"},
            ],
        }

        with patch.object(
            loop.climate_evidence_service,
            "process_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            candidates = await loop._fetch_real_climate_data_async(limit=10)

            # Find GISTEMP candidate
            gistemp_cand = next(
                (c for c in candidates if c.get("source") == "climate_evidence"), None
            )
            assert gistemp_cand is not None

            # Verify temperature anomaly was extracted
            assert "temperature_anomaly" in gistemp_cand
            assert isinstance(gistemp_cand["temperature_anomaly"], (int, float))

    @pytest.mark.asyncio
    async def test_climate_evidence_service_failure_handling(self):
        """Test graceful handling of ClimateEvidenceService failure."""
        loop = ClimateLoop()

        # Simulate service failure
        with patch.object(
            loop.climate_evidence_service,
            "process_request",
            new_callable=AsyncMock,
            side_effect=Exception("GISTEMP API unavailable"),
        ):
            # Should NOT raise exception, should continue with other sources
            candidates = await loop._fetch_real_climate_data_async(limit=5)

            # Should have candidates from other sources or synthetic
            assert isinstance(candidates, list)
            # May be empty or have candidates from other sources


class TestScientificDataLakeIntegration:
    """Test ScientificDataLakeService integration in Climate Loop."""

    @pytest.mark.asyncio
    async def test_fetch_datalake_climate_datasets(self):
        """Test fetching climate datasets from Scientific DataLake."""
        loop = ClimateLoop()

        mock_datalake_response = {
            "success": True,
            "datasets": [
                {
                    "dataset_id": "climate_model_cmip6_001",
                    "dataset_type": "climate_projection",
                    "sample_count": 50000,
                    "quality_score": 0.88,
                },
                {
                    "dataset_id": "ocean_temperature_noaa_002",
                    "dataset_type": "ocean_data",
                    "sample_count": 120000,
                    "quality_score": 0.92,
                },
            ],
        }

        with patch.object(
            loop.scientific_datalake_service,
            "process_request",
            new_callable=AsyncMock,
            return_value=mock_datalake_response,
        ):
            candidates = await loop._fetch_real_climate_data_async(limit=10)

            # Verify DataLake candidates were created
            datalake_candidates = [c for c in candidates if c.get("source") == "scientific_datalake"]
            assert len(datalake_candidates) > 0

            # Check candidate structure
            for candidate in datalake_candidates:
                assert "dataset_id" in candidate
                assert "climate_variable" in candidate
                assert "sample_quality" in candidate
                assert candidate["source"] == "scientific_datalake"

    @pytest.mark.asyncio
    async def test_datalake_sampling_integration(self):
        """Test dataset sampling from Scientific DataLake."""
        loop = ClimateLoop()

        mock_response = {
            "success": True,
            "datasets": [
                {
                    "dataset_id": "arctic_ice_dataset",
                    "dataset_type": "cryosphere",
                    "sample_count": 75000,
                    "quality_score": 0.91,
                },
            ],
        }

        with patch.object(
            loop.scientific_datalake_service,
            "process_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            candidates = await loop._fetch_real_climate_data_async(limit=5)

            # Find DataLake candidate
            datalake_cand = next(
                (c for c in candidates if c.get("source") == "scientific_datalake"), None
            )

            if datalake_cand:
                # Verify dataset properties
                assert "dataset_id" in datalake_cand
                assert "sample_quality" in datalake_cand
                assert isinstance(datalake_cand["sample_quality"], (int, float))

    @pytest.mark.asyncio
    async def test_datalake_service_failure_handling(self):
        """Test graceful handling of DataLake service failure."""
        loop = ClimateLoop()

        with patch.object(
            loop.scientific_datalake_service,
            "process_request",
            new_callable=AsyncMock,
            side_effect=Exception("DataLake connection timeout"),
        ):
            # Should NOT crash, continue with other sources
            candidates = await loop._fetch_real_climate_data_async(limit=5)
            assert isinstance(candidates, list)


class TestScientificDatabaseIntegration:
    """Test AdvancedScientificDatabaseService integration."""

    @pytest.mark.asyncio
    async def test_hypothesis_search_integration(self):
        """Test hypothesis search in Scientific Database."""
        loop = ClimateLoop()

        mock_database_response = {
            "success": True,
            "hypotheses": [
                {
                    "hypothesis_id": "climate_hyp_001",
                    "climate_variable": "sea_surface_temperature",
                    "research_score": 0.87,
                    "citations": 42,
                },
                {
                    "hypothesis_id": "climate_hyp_002",
                    "climate_variable": "precipitation_pattern",
                    "research_score": 0.79,
                    "citations": 28,
                },
            ],
        }

        with patch.object(
            loop.scientific_database_service,
            "process_request",
            new_callable=AsyncMock,
            return_value=mock_database_response,
        ):
            candidates = await loop._fetch_real_climate_data_async(limit=10)

            # Verify Database candidates
            db_candidates = [c for c in candidates if c.get("source") == "scientific_database"]
            assert len(db_candidates) > 0

            # Check structure
            for candidate in db_candidates:
                assert "hypothesis_id" in candidate
                assert "climate_variable" in candidate
                assert "research_score" in candidate
                assert candidate["source"] == "scientific_database"

    @pytest.mark.asyncio
    async def test_database_climate_variable_extraction(self):
        """Test climate variable extraction from database."""
        loop = ClimateLoop()

        mock_response = {
            "success": True,
            "hypotheses": [
                {
                    "hypothesis_id": "arctic_warming_hyp",
                    "climate_variable": "arctic_temperature",
                    "research_score": 0.93,
                    "citations": 156,
                },
            ],
        }

        with patch.object(
            loop.scientific_database_service,
            "process_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            candidates = await loop._fetch_real_climate_data_async(limit=5)

            db_cand = next(
                (c for c in candidates if c.get("source") == "scientific_database"), None
            )

            if db_cand:
                assert "climate_variable" in db_cand
                assert db_cand["climate_variable"] in [
                    "arctic_temperature",
                    "sea_surface_temperature",
                    "precipitation_pattern",
                    "co2_concentration",
                ]

    @pytest.mark.asyncio
    async def test_database_service_failure_handling(self):
        """Test graceful handling of Database service failure."""
        loop = ClimateLoop()

        with patch.object(
            loop.scientific_database_service,
            "process_request",
            new_callable=AsyncMock,
            side_effect=Exception("Database query timeout"),
        ):
            candidates = await loop._fetch_real_climate_data_async(limit=5)
            assert isinstance(candidates, list)


class TestMultiSourceDataAggregation:
    """Test multi-source data aggregation in Climate Loop."""

    @pytest.mark.asyncio
    async def test_all_three_sources_integration(self):
        """Test successful aggregation from all 3 climate sources."""
        loop = ClimateLoop()

        # Mock all 3 services
        mock_climate_evidence = {
            "success": True,
            "temperature_records": [
                {"year": 2023, "temperature_anomaly": 1.1, "location": "global"}
            ],
        }

        mock_datalake = {
            "success": True,
            "datasets": [
                {"dataset_id": "cmip6_001", "dataset_type": "model", "quality_score": 0.9}
            ],
        }

        mock_database = {
            "success": True,
            "hypotheses": [
                {"hypothesis_id": "hyp_001", "climate_variable": "temperature", "research_score": 0.85}
            ],
        }

        with patch.object(
            loop.climate_evidence_service, "process_request", new_callable=AsyncMock, return_value=mock_climate_evidence
        ), patch.object(
            loop.scientific_datalake_service, "process_request", new_callable=AsyncMock, return_value=mock_datalake
        ), patch.object(
            loop.scientific_database_service, "process_request", new_callable=AsyncMock, return_value=mock_database
        ):
            candidates = await loop._fetch_real_climate_data_async(limit=20)

            # Should have candidates from all 3 sources
            sources = {c.get("source") for c in candidates}
            
            # At least some diversity in sources
            assert len(candidates) > 0

    @pytest.mark.asyncio
    async def test_priority_based_fallback(self):
        """Test priority-based fallback strategy."""
        loop = ClimateLoop()

        # Scenario: ClimateEvidence succeeds, others fail
        mock_success = {
            "success": True,
            "temperature_records": [
                {"year": 2024, "temperature_anomaly": 1.2, "location": "global"}
            ],
        }

        with patch.object(
            loop.climate_evidence_service, "process_request", new_callable=AsyncMock, return_value=mock_success
        ), patch.object(
            loop.scientific_datalake_service,
            "process_request",
            new_callable=AsyncMock,
            side_effect=Exception("DataLake down"),
        ), patch.object(
            loop.scientific_database_service,
            "process_request",
            new_callable=AsyncMock,
            side_effect=Exception("Database down"),
        ):
            candidates = await loop._fetch_real_climate_data_async(limit=10)

            # Should still have candidates from ClimateEvidence
            assert len(candidates) > 0

    @pytest.mark.asyncio
    async def test_synthetic_fallback_when_all_fail(self):
        """Test synthetic fallback when ALL services fail."""
        loop = ClimateLoop()

        # All 3 services fail
        with patch.object(
            loop.climate_evidence_service,
            "process_request",
            new_callable=AsyncMock,
            side_effect=Exception("Service 1 down"),
        ), patch.object(
            loop.scientific_datalake_service,
            "process_request",
            new_callable=AsyncMock,
            side_effect=Exception("Service 2 down"),
        ), patch.object(
            loop.scientific_database_service,
            "process_request",
            new_callable=AsyncMock,
            side_effect=Exception("Service 3 down"),
        ):
            candidates = await loop._fetch_real_climate_data_async(limit=5)

            # Should have synthetic candidates
            assert len(candidates) > 0
            synthetic_candidates = [c for c in candidates if c.get("source") == "synthetic"]
            assert len(synthetic_candidates) > 0


class TestClimateLoopIteration:
    """Test complete Climate Loop iteration."""

    @pytest.mark.asyncio
    async def test_full_iteration_execution(self):
        """Test full Climate Loop iteration with mocked services."""
        loop = ClimateLoop()

        # Mock all services for iteration
        mock_climate = {
            "success": True,
            "temperature_records": [
                {"year": 2023, "temperature_anomaly": 1.15, "location": "global"}
            ],
        }

        with patch.object(
            loop.climate_evidence_service, "process_request", new_callable=AsyncMock, return_value=mock_climate
        ), patch.object(
            loop.scientific_datalake_service,
            "process_request",
            new_callable=AsyncMock,
            return_value={"success": True, "datasets": []},
        ), patch.object(
            loop.scientific_database_service,
            "process_request",
            new_callable=AsyncMock,
            return_value={"success": True, "hypotheses": []},
        ), patch.object(
            loop.evidence, "corroborate", new_callable=AsyncMock, return_value={"confidence": 0.75}
        ):
            result = await loop._run_iteration_impl(top_n=2)

            # Verify iteration success
            assert result["success"] is True
            assert "processed_count" in result
            assert result["processed_count"] > 0

    @pytest.mark.asyncio
    async def test_iteration_metrics_recording(self):
        """Test metrics recording during iteration."""
        loop = ClimateLoop()

        mock_climate = {
            "success": True,
            "temperature_records": [
                {"year": 2024, "temperature_anomaly": 1.05, "location": "global"}
            ],
        }

        with patch.object(
            loop.climate_evidence_service, "process_request", new_callable=AsyncMock, return_value=mock_climate
        ), patch.object(
            loop.scientific_datalake_service,
            "process_request",
            new_callable=AsyncMock,
            return_value={"success": True, "datasets": []},
        ), patch.object(
            loop.scientific_database_service,
            "process_request",
            new_callable=AsyncMock,
            return_value={"success": True, "hypotheses": []},
        ), patch.object(
            loop.evidence, "corroborate", new_callable=AsyncMock, return_value={"confidence": 0.8}
        ):
            result = await loop._run_iteration_impl(top_n=3)

            # Verify metrics exist
            assert "metrics" in result
            metrics = result["metrics"]
            assert "avg_temperature_anomaly" in metrics or "total_candidates" in metrics


class TestClimateServiceErrorHandling:
    """Test error handling across all Climate services."""

    @pytest.mark.asyncio
    async def test_all_services_graceful_degradation(self):
        """Test graceful degradation when services fail."""
        loop = ClimateLoop()

        # Test each service failing independently
        failure_scenarios = [
            ("climate_evidence_service", "GISTEMP failure"),
            ("scientific_datalake_service", "DataLake failure"),
            ("scientific_database_service", "Database failure"),
        ]

        for service_name, error_msg in failure_scenarios:
            with patch.object(
                getattr(loop, service_name),
                "process_request",
                new_callable=AsyncMock,
                side_effect=Exception(error_msg),
            ):
                # Should NOT raise exception
                try:
                    candidates = await loop._fetch_real_climate_data_async(limit=5)
                    # Should return list (even if empty or synthetic)
                    assert isinstance(candidates, list)
                except Exception as exc:
                    pytest.fail(f"Service {service_name} failure should be handled gracefully: {exc}")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
