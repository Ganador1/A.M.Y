"""
Unit tests for Mathematics Loop Advanced Services Integration

Tests the integration of 6 advanced mathematics services:
- SagemathService
- AutomatedTheoremProvingService
- AdvancedNumberTheoryService
- AdvancedTopologyService
- JuliaService
- SymbolicAIService
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.autonomous.pipelines.mathematics_loop import MathematicsLoop
from app.domains.mathematics.services.mathematical_discovery_engine import Conjecture


class TestMathematicsLoopAdvancedServices:
    """Test advanced mathematics services integration"""

    @pytest.fixture
    def math_loop(self):
        """Create MathematicsLoop instance for testing"""
        return MathematicsLoop()

    @pytest.mark.asyncio
    async def test_all_services_initialized(self, math_loop):
        """Test that all 6 advanced services are initialized"""
        # Check service existence
        assert hasattr(math_loop, 'sagemath')
        assert hasattr(math_loop, 'atp')
        assert hasattr(math_loop, 'number_theory')
        assert hasattr(math_loop, 'topology')
        assert hasattr(math_loop, 'julia')
        assert hasattr(math_loop, 'symbolic_ai')
        
        # Check services are not None
        assert math_loop.sagemath is not None
        assert math_loop.atp is not None
        assert math_loop.number_theory is not None
        assert math_loop.topology is not None
        assert math_loop.julia is not None
        assert math_loop.symbolic_ai is not None


class TestNumberTheoryConjectures:
    """Test number theory conjecture generation"""

    @pytest.fixture
    def math_loop(self):
        return MathematicsLoop()

    @pytest.fixture
    def mock_algebraic_field_result(self):
        """Mock result from algebraic number field creation"""
        return {
            "success": True,
            "field": {
                "name": "Q(√2)",
                "defining_polynomial": [1, 0, -2],
                "degree": 2,
                "discriminant": 8,
                "class_number": 1,
                "unit_group_rank": 1,
                "integral_basis": [[1, 0], [0, 1]]
            }
        }

    @pytest.fixture
    def mock_elliptic_curve_result(self):
        """Mock result from elliptic curve creation"""
        return {
            "success": True,
            "curve": {
                "equation": "y² = x³ + 7",
                "a": 0,
                "b": 7,
                "discriminant": -5488,
                "torsion_order": 2,
                "rank_bound": 0
            }
        }

    @pytest.mark.asyncio
    async def test_number_theory_algebraic_fields(self, math_loop, mock_algebraic_field_result):
        """Test algebraic number field conjecture generation"""
        # Mock number theory service
        math_loop.number_theory.algebraic_number_fields = AsyncMock(
            return_value=mock_algebraic_field_result
        )
        
        conjectures = []
        await math_loop._generate_number_theory_conjectures_async(conjectures, limit=5)
        
        # Should have generated at least one conjecture
        assert len(conjectures) > 0
        
        # Check conjecture properties
        conj = conjectures[0]
        assert isinstance(conj, Conjecture)
        assert "class number" in conj.statement.lower() or "Q(√2)" in conj.statement
        assert conj.domain == "number_theory"
        assert "algebraic_number_field" in conj.metadata.get("source", "")

    @pytest.mark.asyncio
    async def test_number_theory_elliptic_curves(self, math_loop, mock_elliptic_curve_result):
        """Test elliptic curve conjecture generation"""
        math_loop.number_theory.algebraic_number_fields = AsyncMock(
            return_value={"success": False}
        )
        math_loop.number_theory.elliptic_curves = AsyncMock(
            return_value=mock_elliptic_curve_result
        )
        
        conjectures = []
        await math_loop._generate_number_theory_conjectures_async(conjectures, limit=5)
        
        # Should have elliptic curve conjecture
        assert any("elliptic curve" in c.statement.lower() for c in conjectures)
        assert any("torsion" in c.statement.lower() for c in conjectures)


class TestTopologyConjectures:
    """Test topology conjecture generation"""

    @pytest.fixture
    def math_loop(self):
        return MathematicsLoop()

    @pytest.fixture
    def mock_persistence_result(self):
        """Mock persistent homology result"""
        return {
            "success": True,
            "persistence_diagram": [
                (0, 0.0, 0.5),  # H0 feature
                (1, 0.2, 0.8),  # H1 feature (hole)
                (1, 0.3, 0.6),  # Another H1 feature
                (2, 0.4, 0.5)   # H2 feature
            ],
            "barcode": [
                (0.0, 0.5),
                (0.2, 0.8),
                (0.3, 0.6)
            ],
            "betti_numbers": {
                "b0": 1,
                "b1": 2,
                "b2": 1
            }
        }

    @pytest.mark.asyncio
    async def test_topology_persistent_homology(self, math_loop, mock_persistence_result):
        """Test persistent homology conjecture generation"""
        math_loop.topology.persistent_homology = AsyncMock(
            return_value=mock_persistence_result
        )
        
        conjectures = []
        await math_loop._generate_topology_conjectures_async(conjectures, limit=5)
        
        # Should have topology conjectures
        assert len(conjectures) > 0
        
        # Check for topological content
        conj_texts = [c.statement.lower() for c in conjectures]
        assert any("topological" in text or "h₁" in text or "holes" in text for text in conj_texts)

    @pytest.mark.asyncio
    async def test_topology_barcode_analysis(self, math_loop, mock_persistence_result):
        """Test barcode analysis conjecture generation"""
        math_loop.topology.persistent_homology = AsyncMock(
            return_value=mock_persistence_result
        )
        
        conjectures = []
        await math_loop._generate_topology_conjectures_async(conjectures, limit=5)
        
        # Should have barcode-related conjecture
        assert any("barcode" in c.metadata.get("source", "") for c in conjectures)
        assert any("lifetime" in c.statement.lower() or "persistence" in c.statement.lower() 
                   for c in conjectures)


class TestATPProofComplexity:
    """Test Automated Theorem Proving complexity estimation"""

    @pytest.fixture
    def math_loop(self):
        return MathematicsLoop()

    def test_atp_complexity_simple_statement(self, math_loop):
        """Test complexity estimation for simple statements"""
        simple_conj = Conjecture(
            id="test-001",
            statement="a + b = b + a",
            domain="algebra"
        )
        
        result = math_loop._estimate_proof_complexity(simple_conj)
        
        assert "atp_difficulty" in result
        assert "proof_strategy" in result
        assert "likely_provable" in result
        assert 0.0 <= result["atp_difficulty"] <= 1.0

    def test_atp_complexity_advanced_statement(self, math_loop):
        """Test complexity estimation for advanced statements"""
        advanced_conj = Conjecture(
            id="test-002",
            statement="Class number of Q(√-163) equals 1 and the elliptic curve has torsion order 2",
            domain="number_theory"
        )
        
        result = math_loop._estimate_proof_complexity(advanced_conj)
        
        # Should have higher difficulty
        assert result["atp_difficulty"] > 0.5
        assert result["proof_strategy"] in ["automated", "interactive"]

    def test_atp_topological_complexity(self, math_loop):
        """Test complexity for topological statements"""
        topo_conj = Conjecture(
            id="test-003",
            statement="The persistent homology exhibits topological invariants in dimension 3",
            domain="topology"
        )
        
        result = math_loop._estimate_proof_complexity(topo_conj)
        
        # Should detect topological keywords
        assert "atp_difficulty" in result
        assert result["atp_difficulty"] > 0.4  # Non-trivial


class TestPrepareCandidatesIntegration:
    """Test _prepare_candidates method with all services"""

    @pytest.fixture
    def math_loop(self):
        return MathematicsLoop()

    def test_prepare_candidates_number_theory_domain(self, math_loop):
        """Test candidate preparation for number theory domain"""
        # Mock number theory service
        math_loop.number_theory.algebraic_number_fields = AsyncMock(
            return_value={
                "success": True,
                "field": {"name": "Q(√5)", "class_number": 1}
            }
        )
        
        candidates = math_loop._prepare_candidates(limit=5, domain="number_theory")
        
        # Should have candidates
        assert isinstance(candidates, list)
        assert len(candidates) > 0
        
        # Check candidate structure
        if len(candidates) > 0:
            cand = candidates[0]
            assert "id" in cand
            assert "statement" in cand
            assert "domain" in cand
            assert "atp_metadata" in cand

    def test_prepare_candidates_topology_domain(self, math_loop):
        """Test candidate preparation for topology domain"""
        math_loop.topology.persistent_homology = AsyncMock(
            return_value={"success": True, "persistence_diagram": []}
        )
        
        candidates = math_loop._prepare_candidates(limit=5, domain="topology")
        
        assert isinstance(candidates, list)
        assert len(candidates) > 0

    def test_prepare_candidates_fallback_to_basic(self, math_loop):
        """Test fallback to basic discovery engine when advanced services fail"""
        # Mock all advanced services to fail
        math_loop.number_theory.algebraic_number_fields = AsyncMock(
            side_effect=Exception("Service unavailable")
        )
        
        # Should still generate candidates using basic engine
        candidates = math_loop._prepare_candidates(limit=5, domain="number_theory")
        
        assert isinstance(candidates, list)
        # May be empty or have basic conjectures


class TestAsyncMethodsExecution:
    """Test async helper methods execution"""

    @pytest.fixture
    def math_loop(self):
        return MathematicsLoop()

    @pytest.mark.asyncio
    async def test_generate_number_theory_async_execution(self, math_loop):
        """Test async number theory generation executes without errors"""
        math_loop.number_theory.algebraic_number_fields = AsyncMock(
            return_value={"success": True, "field": {"name": "test", "class_number": 1}}
        )
        math_loop.number_theory.elliptic_curves = AsyncMock(
            return_value={"success": True, "curve": {"equation": "y²=x³+1", "torsion_order": 1}}
        )
        
        conjectures = []
        await math_loop._generate_number_theory_conjectures_async(conjectures, limit=3)
        
        # Should execute without raising
        assert isinstance(conjectures, list)

    @pytest.mark.asyncio
    async def test_generate_topology_async_execution(self, math_loop):
        """Test async topology generation executes without errors"""
        math_loop.topology.persistent_homology = AsyncMock(
            return_value={"success": True, "persistence_diagram": [], "barcode": []}
        )
        
        conjectures = []
        await math_loop._generate_topology_async_execution(conjectures, limit=3)
        
        assert isinstance(conjectures, list)


class TestConjectureQuality:
    """Test quality of generated conjectures"""

    @pytest.fixture
    def math_loop(self):
        return MathematicsLoop()

    def test_conjectures_are_non_trivial(self, math_loop):
        """Test that generated conjectures are non-trivial"""
        math_loop.number_theory.algebraic_number_fields = AsyncMock(
            return_value={
                "success": True,
                "field": {"name": "Q(√-163)", "class_number": 1}
            }
        )
        
        candidates = math_loop._prepare_candidates(limit=5, domain="number_theory")
        
        # Check for non-trivial content
        if len(candidates) > 0:
            statements = [c["statement"] for c in candidates]
            # Should NOT have trivial identities
            assert not all("a + b = b + a" in s for s in statements)
            assert not all("x = x" in s for s in statements)

    def test_conjectures_have_metadata(self, math_loop):
        """Test that conjectures have proper metadata"""
        candidates = math_loop._prepare_candidates(limit=3, domain="algebra")
        
        if len(candidates) > 0:
            cand = candidates[0]
            required_keys = ["id", "statement", "domain", "importance", 
                           "novelty", "information_gain", "atp_metadata"]
            assert all(key in cand for key in required_keys)


class TestServiceErrorHandling:
    """Test error handling for service failures"""

    @pytest.fixture
    def math_loop(self):
        return MathematicsLoop()

    @pytest.mark.asyncio
    async def test_number_theory_service_timeout(self, math_loop):
        """Test handling of number theory service timeout"""
        math_loop.number_theory.algebraic_number_fields = AsyncMock(
            side_effect=asyncio.TimeoutError("Service timeout")
        )
        
        conjectures = []
        # Should not raise, just warn
        await math_loop._generate_number_theory_conjectures_async(conjectures, limit=3)
        
        # May have empty conjectures but shouldn't crash
        assert isinstance(conjectures, list)

    @pytest.mark.asyncio
    async def test_topology_service_failure(self, math_loop):
        """Test handling of topology service failure"""
        math_loop.topology.persistent_homology = AsyncMock(
            return_value={"success": False, "error": "GUDHI unavailable"}
        )
        
        conjectures = []
        await math_loop._generate_topology_conjectures_async(conjectures, limit=3)
        
        # Should handle gracefully
        assert isinstance(conjectures, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
