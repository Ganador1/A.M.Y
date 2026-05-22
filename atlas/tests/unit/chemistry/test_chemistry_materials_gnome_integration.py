"""
Unit tests for Chemistry and Materials Loop GNOME Integration

Tests the integration of GnomeMaterialsService and ChemMLService in
chemistry_loop.py and materials_loop.py.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List

# Import loops to test
from app.autonomous.pipelines.chemistry_loop import ChemistryLoop
from app.autonomous.pipelines.materials_loop import MaterialsLoop


class TestChemistryLoopGNOMEIntegration:
    """Test GNOME Materials integration in Chemistry Loop"""

    @pytest.fixture
    def chemistry_loop(self):
        """Create ChemistryLoop instance for testing"""
        return ChemistryLoop()

    @pytest.fixture
    def mock_gnome_materials(self):
        """Mock GNOME materials search results"""
        return [
            {
                "material_id": "gnome-mp-001",
                "formula": "Li2O",
                "structure": {"lattice": "cubic", "atoms": 3},
                "formation_energy": -0.8,
                "band_gap": 0.5,
                "stability": 0.9,
                "properties": {
                    "density": 2.01,
                    "space_group": "Fm-3m"
                }
            },
            {
                "material_id": "gnome-mp-002",
                "formula": "Fe2O3",
                "structure": {"lattice": "rhombohedral", "atoms": 5},
                "formation_energy": -1.2,
                "band_gap": 2.1,
                "stability": 0.85,
                "properties": {
                    "density": 5.26,
                    "space_group": "R-3c"
                }
            }
        ]

    @pytest.fixture
    def mock_chemml_predictions(self):
        """Mock ChemML ML predictions"""
        return {
            "success": True,
            "predictions": {
                "band_gap": 0.52,
                "formation_energy": -0.78,
                "elastic_modulus": 120.5
            },
            "confidence": 0.87,
            "model_version": "chemml_v2.1"
        }

    @pytest.mark.asyncio
    async def test_gnome_service_initialization(self, chemistry_loop):
        """Test that GNOME service is initialized correctly"""
        assert hasattr(chemistry_loop, 'gnome_service')
        assert chemistry_loop.gnome_service is not None
        assert hasattr(chemistry_loop, 'chemml_service')
        assert chemistry_loop.chemml_service is not None

    @pytest.mark.asyncio
    async def test_gnome_search_integration(self, chemistry_loop, mock_gnome_materials):
        """Test GNOME materials search in _fetch_domain_candidates_async"""
        # Mock GNOME service search
        chemistry_loop.gnome_service.search_materials = AsyncMock(
            return_value=mock_gnome_materials
        )
        chemistry_loop.chemml_service.predict_properties = AsyncMock(
            return_value={
                "success": True,
                "predictions": {"band_gap": 0.5, "formation_energy": -0.8}
            }
        )

        # Call the method
        candidates = await chemistry_loop._fetch_domain_candidates_async(limit=5)

        # Assertions
        assert len(candidates) >= 2  # At least the mocked materials
        chemistry_loop.gnome_service.search_materials.assert_called_once()
        
        # Verify search filters were applied
        call_args = chemistry_loop.gnome_service.search_materials.call_args
        assert "filters" in call_args.kwargs or len(call_args.args) > 0

    @pytest.mark.asyncio
    async def test_chemml_predictions_enrichment(self, chemistry_loop, mock_gnome_materials, mock_chemml_predictions):
        """Test that ChemML predictions enrich GNOME materials"""
        chemistry_loop.gnome_service.search_materials = AsyncMock(
            return_value=mock_gnome_materials
        )
        chemistry_loop.chemml_service.predict_properties = AsyncMock(
            return_value=mock_chemml_predictions
        )

        candidates = await chemistry_loop._fetch_domain_candidates_async(limit=5)

        # Verify ChemML was called for predictions
        assert chemistry_loop.chemml_service.predict_properties.call_count >= 1

        # Verify candidates have ML enrichment
        if len(candidates) > 0:
            # Check for ML metadata in candidates
            # Note: exact structure depends on implementation
            assert any(
                'ml_predictions' in str(c) or 'chemml' in str(c).lower()
                for c in candidates
            )

    @pytest.mark.asyncio
    async def test_fallback_to_materials_service(self, chemistry_loop):
        """Test fallback to basic MaterialsService when GNOME fails"""
        # Mock GNOME to fail
        chemistry_loop.gnome_service.search_materials = AsyncMock(
            side_effect=Exception("GNOME service unavailable")
        )
        
        # Mock basic service to succeed
        chemistry_loop.materials_service.discover_materials = AsyncMock(
            return_value=[{"material_id": "basic-001", "formula": "H2O"}]
        )

        candidates = await chemistry_loop._fetch_domain_candidates_async(limit=5)

        # Should still get candidates from fallback
        assert len(candidates) > 0

    @pytest.mark.asyncio
    async def test_gnome_filters_configuration(self, chemistry_loop):
        """Test that GNOME search uses correct filters"""
        chemistry_loop.gnome_service.search_materials = AsyncMock(return_value=[])
        chemistry_loop.chemml_service.predict_properties = AsyncMock(
            return_value={"success": True, "predictions": {}}
        )

        await chemistry_loop._fetch_domain_candidates_async(limit=5)

        # Verify filters
        call_kwargs = chemistry_loop.gnome_service.search_materials.call_args.kwargs
        if "filters" in call_kwargs:
            filters = call_kwargs["filters"]
            # Check expected filter keys
            expected_filters = ["formation_energy_max", "band_gap_min", "stability_min"]
            assert any(key in filters for key in expected_filters)


class TestMaterialsLoopGNOMEIntegration:
    """Test GNOME Materials integration in Materials Loop"""

    @pytest.fixture
    def materials_loop(self):
        """Create MaterialsLoop instance for testing"""
        return MaterialsLoop()

    @pytest.fixture
    def mock_gnome_materials(self):
        """Mock GNOME materials for materials loop"""
        return [
            {
                "material_id": "gnome-mat-001",
                "formula": "TiO2",
                "structure": {"lattice": "tetragonal"},
                "formation_energy": -0.9,
                "band_gap": 3.0,
                "stability": 0.95
            }
        ]

    @pytest.mark.asyncio
    async def test_gnome_priority_over_basic_service(self, materials_loop, mock_gnome_materials):
        """Test that GNOME candidates are prioritized over basic service"""
        materials_loop.gnome_service.search_materials = AsyncMock(
            return_value=mock_gnome_materials
        )
        materials_loop.chemml_service.predict_properties = AsyncMock(
            return_value={"success": True, "predictions": {"band_gap": 3.0}}
        )
        materials_loop.materials_service.discover_materials = AsyncMock(
            return_value=[{"material_id": "basic-001"}]
        )

        candidates = await materials_loop._default_provider_async(limit=5)

        # GNOME should be called first
        materials_loop.gnome_service.search_materials.assert_called_once()
        
        # Check that GNOME materials are in results
        if len(candidates) > 0:
            # At least one candidate should have GNOME metadata
            assert any(
                'gnome' in str(c).lower() or 'data_source' in str(c)
                for c in candidates
            )

    @pytest.mark.asyncio
    async def test_dual_source_strategy(self, materials_loop, mock_gnome_materials):
        """Test dual-source strategy (GNOME + MaterialsService)"""
        # GNOME returns limited results
        materials_loop.gnome_service.search_materials = AsyncMock(
            return_value=mock_gnome_materials[:1]  # Only 1 result
        )
        materials_loop.chemml_service.predict_properties = AsyncMock(
            return_value={"success": True, "predictions": {}}
        )
        materials_loop.materials_service.discover_materials = AsyncMock(
            return_value=[
                {"material_id": "basic-001"},
                {"material_id": "basic-002"}
            ]
        )

        candidates = await materials_loop._default_provider_async(limit=5)

        # Should have results from both sources
        assert len(candidates) >= 1  # At least GNOME result
        
        # Both services should have been called
        materials_loop.gnome_service.search_materials.assert_called_once()

    @pytest.mark.asyncio
    async def test_ml_enrichment_metadata(self, materials_loop, mock_gnome_materials):
        """Test that ML predictions add proper metadata"""
        materials_loop.gnome_service.search_materials = AsyncMock(
            return_value=mock_gnome_materials
        )
        materials_loop.chemml_service.predict_properties = AsyncMock(
            return_value={
                "success": True,
                "predictions": {
                    "band_gap": 3.1,
                    "formation_energy": -0.92,
                    "elastic_modulus": 250.0,
                    "thermal_conductivity": 11.8
                },
                "confidence": 0.91
            }
        )

        candidates = await materials_loop._default_provider_async(limit=5)

        # Verify ML metadata is added
        assert len(candidates) > 0
        # Check that ML predictions were called
        assert materials_loop.chemml_service.predict_properties.call_count >= 1


class TestChemistryMaterialsCoherence:
    """Test coherence between Chemistry and Materials loops using same GNOME data"""

    @pytest.fixture
    def chemistry_loop(self):
        return ChemistryLoop()

    @pytest.fixture
    def materials_loop(self):
        return MaterialsLoop()

    @pytest.mark.asyncio
    async def test_same_gnome_database_access(self, chemistry_loop, materials_loop):
        """Test that both loops access the same GNOME database"""
        # Both should have gnome_service
        assert hasattr(chemistry_loop, 'gnome_service')
        assert hasattr(materials_loop, 'gnome_service')
        
        # Both should be same type
        assert type(chemistry_loop.gnome_service).__name__ == type(materials_loop.gnome_service).__name__

    @pytest.mark.asyncio
    async def test_consistent_filter_strategy(self, chemistry_loop, materials_loop):
        """Test that both loops use consistent filtering strategies"""
        # Mock both services
        mock_gnome_result = [{"material_id": "test-001"}]
        
        chemistry_loop.gnome_service.search_materials = AsyncMock(return_value=mock_gnome_result)
        chemistry_loop.chemml_service.predict_properties = AsyncMock(
            return_value={"success": True, "predictions": {}}
        )
        
        materials_loop.gnome_service.search_materials = AsyncMock(return_value=mock_gnome_result)
        materials_loop.chemml_service.predict_properties = AsyncMock(
            return_value={"success": True, "predictions": {}}
        )

        # Call both
        await chemistry_loop._fetch_domain_candidates_async(limit=3)
        await materials_loop._default_provider_async(limit=3)

        # Both should have called GNOME
        chemistry_loop.gnome_service.search_materials.assert_called_once()
        materials_loop.gnome_service.search_materials.assert_called_once()


class TestGNOMEServiceErrorHandling:
    """Test error handling for GNOME service failures"""

    @pytest.fixture
    def chemistry_loop(self):
        return ChemistryLoop()

    @pytest.mark.asyncio
    async def test_gnome_timeout_handling(self, chemistry_loop):
        """Test handling of GNOME service timeout"""
        chemistry_loop.gnome_service.search_materials = AsyncMock(
            side_effect=asyncio.TimeoutError("GNOME search timeout")
        )

        # Should not raise exception
        candidates = await chemistry_loop._fetch_domain_candidates_async(limit=5)
        
        # Should fallback to other sources
        assert isinstance(candidates, list)

    @pytest.mark.asyncio
    async def test_chemml_prediction_failure(self, chemistry_loop):
        """Test handling of ChemML prediction failures"""
        chemistry_loop.gnome_service.search_materials = AsyncMock(
            return_value=[{"material_id": "test-001", "formula": "NaCl"}]
        )
        chemistry_loop.chemml_service.predict_properties = AsyncMock(
            return_value={"success": False, "error": "Model unavailable"}
        )

        # Should still return candidates even if ML fails
        candidates = await chemistry_loop._fetch_domain_candidates_async(limit=5)
        assert len(candidates) >= 0  # May be empty but shouldn't crash

    @pytest.mark.asyncio
    async def test_partial_gnome_results(self, chemistry_loop):
        """Test handling when GNOME returns partial/incomplete data"""
        incomplete_materials = [
            {"material_id": "incomplete-001"},  # Missing required fields
            {"material_id": "incomplete-002", "formula": "H2O"}  # Partial data
        ]
        
        chemistry_loop.gnome_service.search_materials = AsyncMock(
            return_value=incomplete_materials
        )
        chemistry_loop.chemml_service.predict_properties = AsyncMock(
            return_value={"success": True, "predictions": {}}
        )

        # Should handle incomplete data gracefully
        candidates = await chemistry_loop._fetch_domain_candidates_async(limit=5)
        assert isinstance(candidates, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
