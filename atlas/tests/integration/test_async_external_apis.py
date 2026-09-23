"""Integration tests for async migration of external_apis module.

Tests verify that:
1. fetch_literature_snippets is now async and works correctly
2. fetch_material_candidates is now async and works correctly
3. HTTP client lifecycle management works
4. Autonomous loops can call the async functions

ROADMAP 5 - ASYNC MIGRATION TEST
"""
import pytest
import asyncio
from app.autonomous.interfaces.external_apis import (
    fetch_literature_snippets,
    fetch_material_candidates,
    get_http_client,
    close_http_client
)


class TestAsyncLiteratureAPI:
    """Tests for async fetch_literature_snippets."""

    @pytest.mark.asyncio
    async def test_fetch_literature_basic(self):
        """Test basic async literature fetch."""
        results = await fetch_literature_snippets("quantum computing", limit=3)

        assert isinstance(results, list)
        assert len(results) <= 3
        assert len(results) > 0

        # Verify structure
        first = results[0]
        assert "title" in first
        assert "snippet" in first
        assert "arxiv_id" in first
        assert "citation_count" in first
        assert "relevance_score" in first

    @pytest.mark.asyncio
    async def test_fetch_literature_empty_query(self):
        """Test async fetch with minimal query."""
        results = await fetch_literature_snippets("", limit=1)

        # Should still return fallback stubs
        assert isinstance(results, list)
        assert len(results) > 0

    @pytest.mark.asyncio
    async def test_fetch_literature_parallel(self):
        """Test that multiple async calls can run in parallel."""
        queries = ["graphene", "catalysis", "nitrogen doping"]

        # Run 3 queries in parallel
        tasks = [fetch_literature_snippets(q, limit=2) for q in queries]
        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        for result in results:
            assert isinstance(result, list)
            assert len(result) > 0


class TestAsyncMaterialsAPI:
    """Tests for async fetch_material_candidates."""

    @pytest.mark.asyncio
    async def test_fetch_materials_basic(self):
        """Test basic async materials fetch."""
        results = await fetch_material_candidates("Li-Fe-P-O", limit=3)

        assert isinstance(results, list)
        assert len(results) <= 3
        assert len(results) > 0

        # Verify structure
        first = results[0]
        assert "formula" in first
        assert "material_id" in first
        assert "formation_energy" in first
        assert "predicted_stability" in first
        assert "band_gap" in first
        assert "novel" in first
        assert "source" in first

    @pytest.mark.asyncio
    async def test_fetch_materials_parallel(self):
        """Test that multiple async material queries can run in parallel."""
        formulas = ["Li-Fe-P-O", "Na-Co-O", "K-Mn-O"]

        # Run 3 queries in parallel
        tasks = [fetch_material_candidates(f, limit=2) for f in formulas]
        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        for result in results:
            assert isinstance(result, list)
            assert len(result) > 0


class TestHTTPClientLifecycle:
    """Tests for HTTP client lifecycle management."""

    @pytest.mark.asyncio
    async def test_http_client_singleton(self):
        """Test that HTTP client is a singleton."""
        client1 = get_http_client()
        client2 = get_http_client()

        assert client1 is client2  # Same instance

    @pytest.mark.asyncio
    async def test_http_client_reuse(self):
        """Test that HTTP client is reused across multiple requests."""
        # Make multiple requests
        await fetch_literature_snippets("test1", limit=1)
        await fetch_literature_snippets("test2", limit=1)
        await fetch_material_candidates("Li-Fe-O", limit=1)

        # All should use the same client
        client = get_http_client()
        assert client is not None
        assert not client.is_closed


class TestAutonomousLoopCompatibility:
    """Tests simulating autonomous loop usage patterns."""

    @pytest.mark.asyncio
    async def test_chemistry_loop_pattern(self):
        """Test pattern used by enhanced_chemistry_loop."""
        # Simulate validation with literature
        doping_level = 0.05
        search_query = f"nitrogen doped graphene electrocatalysis {doping_level:.1%} ORR"

        literature_results = await fetch_literature_snippets(query=search_query, limit=5)

        # Simulate analysis
        support_score = 0.0
        supporting_papers = []

        for paper in literature_results:
            if paper["citation_count"] > 50 and paper["relevance_score"] > 0.7:
                support_score += 0.2
                supporting_papers.append(paper)

        assert isinstance(support_score, float)
        assert isinstance(supporting_papers, list)

    @pytest.mark.asyncio
    async def test_mathematics_loop_pattern(self):
        """Test pattern used by mathematics_loop."""
        # Simulate conjecture literature fetch
        statement = "All primes greater than 2 are odd"

        # This was previously using asyncio.to_thread, now direct await
        literature = await fetch_literature_snippets(statement, 3)

        assert isinstance(literature, list)
        assert len(literature) <= 3


@pytest.fixture(scope="module", autouse=True)
async def cleanup_http_client():
    """Cleanup HTTP client after all tests."""
    yield
    # Close the global HTTP client
    await close_http_client()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
