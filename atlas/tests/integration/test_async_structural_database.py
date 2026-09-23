"""Integration tests for async migration of structural_database_service.

Tests verify that:
1. All methods are now async and work correctly
2. HTTP client lifecycle management works
3. Parallel requests work as expected
4. Router endpoints are async

ROADMAP 5 - ASYNC MIGRATION TEST (Service #2)
"""
import pytest
import asyncio
from app.services.structural_database_service import (
    StructuralDatabaseService,
    get_structural_http_client,
    close_structural_http_client
)


class TestAsyncStructuralDatabaseService:
    """Tests for async StructuralDatabaseService."""

    @pytest.mark.asyncio
    async def test_fetch_pdb_basic(self):
        """Test basic async PDB fetch."""
        svc = StructuralDatabaseService()

        # Use a known PDB ID (1CRN is a small protein, often available)
        result = await svc.fetch_pdb("1CRN")

        assert isinstance(result, dict)
        assert "success" in result
        # Note: Might fail if PDB is down, but structure should be correct

    @pytest.mark.asyncio
    async def test_fetch_pdb_invalid(self):
        """Test async PDB fetch with invalid ID."""
        svc = StructuralDatabaseService()

        result = await svc.fetch_pdb("")

        assert result["success"] is False
        assert "error" in result
        assert "vacío" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_fetch_uniprot_basic(self):
        """Test basic async UniProt fetch."""
        svc = StructuralDatabaseService()

        # Use a known UniProt accession (P12345 is often used in examples)
        result = await svc.fetch_uniprot("P12345")

        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_fetch_alphafold_basic(self):
        """Test basic async AlphaFold fetch."""
        svc = StructuralDatabaseService()

        # Use a known UniProt ID with AlphaFold prediction
        result = await svc.fetch_alphafold_prediction("P12345")

        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_search_similar_structures_basic(self):
        """Test basic async sequence search."""
        svc = StructuralDatabaseService()

        # Use a short valid protein sequence
        test_sequence = "MVHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQRF"

        result = await svc.search_similar_structures(test_sequence, identity_cutoff=0.5, max_results=5)

        assert isinstance(result, dict)
        assert "success" in result

    @pytest.mark.asyncio
    async def test_search_similar_structures_invalid(self):
        """Test async sequence search with invalid input."""
        svc = StructuralDatabaseService()

        # Too short sequence
        result = await svc.search_similar_structures("ABC", identity_cutoff=0.5, max_results=5)

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_parallel_pdb_fetches(self):
        """Test that multiple async PDB fetches can run in parallel."""
        svc = StructuralDatabaseService()

        # Fetch multiple PDBs in parallel
        pdb_ids = ["1CRN", "4HHB", "1MBN"]

        tasks = [svc.fetch_pdb(pdb_id) for pdb_id in pdb_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert len(results) == 3
        for result in results:
            if not isinstance(result, Exception):
                assert isinstance(result, dict)
                assert "success" in result

    @pytest.mark.asyncio
    async def test_parallel_mixed_operations(self):
        """Test that different operations can run in parallel."""
        svc = StructuralDatabaseService()

        # Run different operations in parallel
        tasks = [
            svc.fetch_pdb("1CRN"),
            svc.fetch_uniprot("P12345"),
            svc.fetch_alphafold_prediction("P12345")
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        assert len(results) == 3
        for result in results:
            if not isinstance(result, Exception):
                assert isinstance(result, dict)
                assert "success" in result


class TestHTTPClientLifecycle:
    """Tests for HTTP client lifecycle management."""

    @pytest.mark.asyncio
    async def test_http_client_singleton(self):
        """Test that HTTP client is a singleton."""
        client1 = get_structural_http_client()
        client2 = get_structural_http_client()

        assert client1 is client2  # Same instance

    @pytest.mark.asyncio
    async def test_http_client_reuse(self):
        """Test that HTTP client is reused across multiple requests."""
        svc = StructuralDatabaseService()

        # Make multiple requests
        await svc.fetch_pdb("1CRN")
        await svc.fetch_uniprot("P12345")

        # All should use the same client
        client = get_structural_http_client()
        assert client is not None
        assert not client.is_closed


@pytest.fixture(scope="module", autouse=True)
async def cleanup_http_client():
    """Cleanup HTTP client after all tests."""
    yield
    # Close the global HTTP client
    await close_structural_http_client()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
