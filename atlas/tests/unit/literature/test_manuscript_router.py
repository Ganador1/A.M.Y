"""
Unit tests for manuscript router
"""

import pytest
from unittest.mock import Mock, patch
from app.routers.manuscript import assemble


class TestManuscriptRouter:
    """Test cases for manuscript assembly router endpoints."""

    @patch('app.routers.manuscript.manuscript_assembly_service')
    def test_assemble_manuscript(self, mock_service):
        """Test manuscript assembly endpoint."""
        # Setup mock
        mock_service.assemble_manuscript.return_value = {
            "title": "Test Manuscript",
            "content": "Test content",
            "sections": ["Introduction", "Methods", "Results"]
        }

        # Test payload
        payload = {
            "research_data": {"experiments": []},
            "formatting": {"style": "apa"}
        }

        # Call the endpoint function directly
        result = assemble(payload)

        # Assertions
        assert "manuscript" in result
        assert result["manuscript"]["title"] == "Test Manuscript"
        assert result["manuscript"]["content"] == "Test content"
        mock_service.assemble_manuscript.assert_called_once_with(payload)

    @patch('app.routers.manuscript.manuscript_assembly_service')
    def test_assemble_manuscript_empty_payload(self, mock_service):
        """Test manuscript assembly with empty payload."""
        mock_service.assemble_manuscript.return_value = {}

        result = assemble({})

        assert "manuscript" in result
        assert result["manuscript"] == {}
        mock_service.assemble_manuscript.assert_called_once_with({})
