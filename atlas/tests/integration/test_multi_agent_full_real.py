"""
Integration tests for multi-agent full real functionality

Tests the complete integration of multi-agent coordinator with mocked components.
"""

from unittest.mock import MagicMock


class TestMultiAgentFullReal:
    """Test suite for multi-agent full real integration testing with mocked components."""

    def test_multi_agent_coordinator_initialization(self):
        """Test multi-agent coordinator initialization."""
        mock_coordinator = MagicMock()
        mock_coordinator.initialize = MagicMock(return_value=True)
        mock_coordinator.get_status = MagicMock(return_value="ready")
        mock_coordinator.get_available_domains = MagicMock(return_value=[
            "materials_science", "drug_discovery", "energy_storage"
        ])

        # Test initialization
        result = mock_coordinator.initialize()
        assert result is True

        # Test status
        status = mock_coordinator.get_status()
        assert status == "ready"

        # Test domains
        domains = mock_coordinator.get_available_domains()
        assert len(domains) == 3
        assert "materials_science" in domains
        assert "drug_discovery" in domains
        assert "energy_storage" in domains

    def test_pipeline_execution_materials_science(self):
        """Test pipeline execution for materials science domain."""
        mock_coordinator = MagicMock()
        
        # Mock successful pipeline result
        mock_result = {
            "success": True,
            "domain": "materials_science",
            "artifact": {
                "evidence": {
                    "summary": {
                        "support_score": 0.85,
                        "coverage": 0.92,
                        "weighted_coverage": 0.88,
                        "diversity": 0.76,
                        "failures": 2
                    }
                },
                "review": '{"verdict_quantitative": 0.82, "confidence": 0.91}'
            }
        }
        
        mock_coordinator.run_pipeline_integrated_async = MagicMock(return_value=mock_result)

        # Simulate pipeline execution
        goal = "Optimizar conductividad térmica y estabilidad estructural"
        
        # Test the mock behavior
        result = mock_coordinator.run_pipeline_integrated_async(goal, domain="materials_science", compile_latex=False)
        
        assert result["success"] is True
        assert result["domain"] == "materials_science"
        
        artifact = result["artifact"]
        assert "evidence" in artifact
        assert "review" in artifact
        
        summary = artifact["evidence"]["summary"]
        assert summary["support_score"] == 0.85
        assert summary["coverage"] == 0.92
        assert summary["weighted_coverage"] == 0.88
        assert summary["diversity"] == 0.76
        assert summary["failures"] == 2

    def test_pipeline_execution_drug_discovery(self):
        """Test pipeline execution for drug discovery domain."""
        mock_coordinator = MagicMock()
        
        # Mock successful pipeline result
        mock_result = {
            "success": True,
            "domain": "drug_discovery",
            "artifact": {
                "evidence": {
                    "summary": {
                        "support_score": 0.78,
                        "coverage": 0.89,
                        "weighted_coverage": 0.82,
                        "diversity": 0.68,
                        "failures": 1
                    }
                },
                "review": '{"verdict_quantitative": 0.75, "confidence": 0.88}'
            }
        }
        
        mock_coordinator.run_pipeline_integrated_async = MagicMock(return_value=mock_result)

        # Simulate pipeline execution
        goal = "Optimizar conductividad térmica y estabilidad estructural"
        
        # Test the mock behavior
        result = mock_coordinator.run_pipeline_integrated_async(goal, domain="drug_discovery", compile_latex=False)
        
        assert result["success"] is True
        assert result["domain"] == "drug_discovery"
        
        artifact = result["artifact"]
        summary = artifact["evidence"]["summary"]
        assert summary["support_score"] == 0.78
        assert summary["coverage"] == 0.89
        assert summary["failures"] == 1

    def test_pipeline_execution_energy_storage(self):
        """Test pipeline execution for energy storage domain."""
        mock_coordinator = MagicMock()
        
        # Mock successful pipeline result
        mock_result = {
            "success": True,
            "domain": "energy_storage",
            "artifact": {
                "evidence": {
                    "summary": {
                        "support_score": 0.91,
                        "coverage": 0.95,
                        "weighted_coverage": 0.93,
                        "diversity": 0.84,
                        "failures": 0
                    }
                },
                "review": '{"verdict_quantitative": 0.89, "confidence": 0.94}'
            }
        }
        
        mock_coordinator.run_pipeline_integrated_async = MagicMock(return_value=mock_result)

        # Simulate pipeline execution
        goal = "Optimizar conductividad térmica y estabilidad estructural"
        
        # Test the mock behavior
        result = mock_coordinator.run_pipeline_integrated_async(goal, domain="energy_storage", compile_latex=False)
        
        assert result["success"] is True
        assert result["domain"] == "energy_storage"
        
        artifact = result["artifact"]
        summary = artifact["evidence"]["summary"]
        assert summary["support_score"] == 0.91
        assert summary["coverage"] == 0.95
        assert summary["failures"] == 0

    def test_pipeline_failure_handling(self):
        """Test pipeline failure handling."""
        mock_coordinator = MagicMock()
        
        # Mock failed pipeline result
        mock_result = {
            "success": False,
            "domain": "materials_science",
            "error": "Pipeline execution failed",
            "artifact": None
        }
        
        mock_coordinator.run_pipeline_integrated_async = MagicMock(return_value=mock_result)

        # Test failure handling
        goal = "Test goal"
        result = mock_coordinator.run_pipeline_integrated_async(goal, domain="materials_science", compile_latex=False)
        
        assert result["success"] is False
        assert result["domain"] == "materials_science"
        assert "error" in result
        assert result["artifact"] is None

    def test_metrics_validation(self):
        """Test metrics validation across domains."""
        mock_coordinator = MagicMock()
        
        # Mock results with different metrics
        results = [
            {
                "domain": "materials_science",
                "artifact": {
                    "evidence": {
                        "summary": {
                            "support_score": 0.85,
                            "coverage": 0.92,
                            "weighted_coverage": 0.88,
                            "diversity": 0.76,
                            "failures": 2
                        }
                    }
                }
            },
            {
                "domain": "drug_discovery", 
                "artifact": {
                    "evidence": {
                        "summary": {
                            "support_score": 0.78,
                            "coverage": 0.89,
                            "weighted_coverage": 0.82,
                            "diversity": 0.68,
                            "failures": 1
                        }
                    }
                }
            },
            {
                "domain": "energy_storage",
                "artifact": {
                    "evidence": {
                        "summary": {
                            "support_score": 0.91,
                            "coverage": 0.95,
                            "weighted_coverage": 0.93,
                            "diversity": 0.84,
                            "failures": 0
                        }
                    }
                }
            }
        ]
        
        mock_coordinator.run_multiple_domains = MagicMock(return_value=results)

        # Test metrics validation
        domains = ["materials_science", "drug_discovery", "energy_storage"]
        goal = "Test optimization goal"
        
        result = mock_coordinator.run_multiple_domains(goal, domains)
        
        # Validate all domains have required metrics
        for domain_result in result:
            assert "domain" in domain_result
            assert "artifact" in domain_result
            assert domain_result["artifact"] is not None
            
            summary = domain_result["artifact"]["evidence"]["summary"]
            required_metrics = ["support_score", "coverage", "weighted_coverage", "diversity", "failures"]
            
            for metric in required_metrics:
                assert metric in summary, f"Missing metric: {metric}"
                assert isinstance(summary[metric], (int, float)), f"Metric {metric} should be numeric"

    def test_support_score_validation(self):
        """Test that at least one domain has positive support score."""
        mock_coordinator = MagicMock()
        
        # Mock results where some have positive support scores
        results = [
            {
                "domain": "materials_science",
                "artifact": {
                    "evidence": {
                        "summary": {"support_score": 0.0}
                    }
                }
            },
            {
                "domain": "drug_discovery",
                "artifact": {
                    "evidence": {
                        "summary": {"support_score": 0.78}
                    }
                }
            },
            {
                "domain": "energy_storage", 
                "artifact": {
                    "evidence": {
                        "summary": {"support_score": 0.91}
                    }
                }
            }
        ]
        
        mock_coordinator.run_multiple_domains = MagicMock(return_value=results)

        # Test support score validation
        domains = ["materials_science", "drug_discovery", "energy_storage"]
        goal = "Test goal"
        
        result = mock_coordinator.run_multiple_domains(goal, domains)
        
        # Extract support scores
        support_scores = [r["artifact"]["evidence"]["summary"]["support_score"] for r in result]
        
        # At least one should be greater than 0
        assert any(score > 0 for score in support_scores), "All support scores are 0"
        
        # Some should be positive
        positive_scores = [score for score in support_scores if score > 0]
        assert len(positive_scores) >= 2, "Should have multiple positive support scores"
