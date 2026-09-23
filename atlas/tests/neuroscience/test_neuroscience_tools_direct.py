#!/usr/bin/env python3
"""
Test directo del ToolEvidenceOrchestrator para neuroscience
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.tool_evidence_orchestrator import ToolEvidenceOrchestratorService


import pytest


@pytest.mark.asyncio
@pytest.mark.slow
async def test_neuroscience_tools():
    orchestrator = ToolEvidenceOrchestratorService()
    hypothesis = {
        "title": "Nanoparticle Functionalization for Neural Tissue Regeneration",
        "description": "Testing if functionalized nanoparticles improve neural tissue regeneration",
        "domain": "neuroscience",
        "variables": ["nanoparticle_concentration", "growth_factors", "neural_survival"],
        "assumptions": ["biocompatible nanoparticles", "controlled delivery"],
        "expected_outcome": "Improved neural cell survival and growth"
    }

    result = await orchestrator.process_request({
        "action": "corroborate",
        "hypothesis": hypothesis,
        "domain": "neuroscience"
    })

    assert 'success' in result
