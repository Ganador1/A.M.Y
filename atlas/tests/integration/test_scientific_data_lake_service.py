"""
Integration Tests for ScientificDataLakeService
================================================

Comprehensive integration tests for the AXIOM ScientificDataLakeService.
These tests validate the complete data lake operations including:
- File ingestion from local and S3 sources
- Dataset catalog registration and management  
- Data sampling and preview functionality
- File statistics and metadata operations
- Error handling and security policies

Author: AXIOM Scientific Data Management Team
Date: September 2025
"""

import pytest
import tempfile
import json
import csv
from pathlib import Path
from unittest.mock import patch, MagicMock

# Mock the database service to avoid dependency issues
with patch.dict('sys.modules', {
    'app.services.database_service': MagicMock(),
    'app.services': MagicMock()
}):
    from app.services.scientific_data_lake_service import ScientificDataLakeService


class TestScientificDataLakeServiceIntegration:
    """Integration test suite for ScientificDataLakeService operations."""

    @pytest.fixture(scope="class")
    def data_lake_service(self):
        """ScientificDataLakeService instance with test configuration."""
        # Use temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('os.getenv') as mock_getenv:
                # Configure environment variables for testing
                mock_getenv.side_effect = lambda key, default=None: {
                    "DATALAKE_ROOT": temp_dir,
                    "MAX_DATALAKE_FILE_BYTES": "10485760",  # 10MB
                    "STRICT_DATALAKE_PATHS": "1",
                    "ENABLE_S3": "0"
                }.get(key, default)
                
                # Mock database service
                with patch('app.services.scientific_data_lake_service.DatabaseService') as mock_db:
                    mock_db_instance = MagicMock()
                    mock_db.return_value = mock_db_instance
                    
                    # Configure mock database methods
                    mock_db_instance.save_dataset = MagicMock()
                    mock_db_instance.get_datasets = MagicMock(return_value=[])
                    
                    service = ScientificDataLakeService()
                    yield service

    @pytest.fixture
    def test_csv_file(self):
        """Create a test CSV file for ingestion."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'value'])
            writer.writerow([1, 'test1', 100.5])
            writer.writerow([2, 'test2', 200.3])
            writer.writerow([3, 'test3', 300.7])
            return f.name

    @pytest.fixture
    def test_json_file(self):
        """Create a test JSON file for ingestion."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([
                {"id": 1, "name": "item1", "data": {"value": 42}},
                {"id": 2, "name": "item2", "data": {"value": 84}}
            ], f)
            return f.name

    def test_service_info(self, data_lake_service):
        """Test service information endpoint."""
        info = data_lake_service.get_service_info()
        
        assert info["name"] == "ScientificDataLakeService"
        assert info["version"] == "1.0.0"
        assert "capabilities" in info
        assert "limits" in info
        assert "backends" in info
        assert info["backends"]["s3"] is False

    @pytest.mark.asyncio
    async def test_local_file_ingestion(self, data_lake_service, test_csv_file):
        """Test ingestion of local CSV file."""
        request_data = {
            "action": "ingest",
            "source": test_csv_file,
            "namespace": "test",
            "name": "integration_test",
            "dataset_type": "tabular",
            "description": "Integration test dataset"
        }
        
        result = await data_lake_service.process_request(request_data)
        
        assert result["success"] is True
        assert "dataset_id" in result
        assert "file_path" in result
        assert "size_bytes" in result
        assert result["size_bytes"] > 0
        assert result["data_format"] == "csv"
        assert result["backend"] == "local"
        
        # Verify database registration was called
        data_lake_service.db.save_dataset.assert_called_once()

    @pytest.mark.asyncio
    async def test_file_ingestion_with_metadata(self, data_lake_service, test_json_file):
        """Test ingestion with custom metadata."""
        custom_metadata = {
            "source": "test_integration",
            "version": "1.0.0",
            "columns": ["id", "name", "data"]
        }
        
        request_data = {
            "action": "ingest",
            "source": test_json_file,
            "namespace": "metadata_test",
            "name": "json_dataset",
            "dataset_type": "json",
            "metadata": custom_metadata,
            "is_public": True
        }
        
        result = await data_lake_service.process_request(request_data)
        
        assert result["success"] is True
        assert result["data_format"] == "json"
        
        # Verify metadata was passed to database
        call_args = data_lake_service.db.save_dataset.call_args
        assert "metadata" in call_args[1]
        saved_metadata = call_args[1]["metadata"]
        assert saved_metadata["namespace"] == "metadata_test"
        assert "checksum" in saved_metadata

    @pytest.mark.asyncio
    async def test_file_sampling_csv(self, data_lake_service, test_csv_file):
        """Test CSV file sampling functionality."""
        # First ingest the file
        ingest_request = {
            "action": "ingest",
            "source": test_csv_file,
            "namespace": "sampling_test",
            "name": "csv_sample"
        }
        
        ingest_result = await data_lake_service.process_request(ingest_request)
        assert ingest_result["success"] is True
        
        # Test sampling
        sample_request = {
            "action": "sample",
            "file_path": ingest_result["file_path"],
            "n": 2
        }
        
        sample_result = await data_lake_service.process_request(sample_request)
        
        assert sample_result["success"] is True
        assert "preview" in sample_result
        preview = sample_result["preview"]
        assert preview["kind"] == "tabular"
        assert "rows" in preview
        assert len(preview["rows"]) == 2  # Header + 1 data row

    @pytest.mark.asyncio
    async def test_file_sampling_json(self, data_lake_service, test_json_file):
        """Test JSON file sampling functionality."""
        # First ingest the file
        ingest_request = {
            "action": "ingest",
            "source": test_json_file,
            "namespace": "sampling_test",
            "name": "json_sample"
        }
        
        ingest_result = await data_lake_service.process_request(ingest_request)
        assert ingest_result["success"] is True
        
        # Test sampling
        sample_request = {
            "action": "sample",
            "file_path": ingest_result["file_path"],
            "n": 1
        }
        
        sample_result = await data_lake_service.process_request(sample_request)
        
        assert sample_result["success"] is True
        assert "preview" in sample_result
        preview = sample_result["preview"]
        assert preview["kind"] == "json"
        assert "data" in preview

    @pytest.mark.asyncio
    async def test_file_statistics(self, data_lake_service, test_csv_file):
        """Test file statistics functionality."""
        # First ingest the file
        ingest_request = {
            "action": "ingest",
            "source": test_csv_file,
            "namespace": "stats_test",
            "name": "csv_stats"
        }
        
        ingest_result = await data_lake_service.process_request(ingest_request)
        assert ingest_result["success"] is True
        
        # Test statistics
        stat_request = {
            "action": "stat",
            "file_path": ingest_result["file_path"]
        }
        
        stat_result = await data_lake_service.process_request(stat_request)
        
        assert stat_result["success"] is True
        assert "info" in stat_result
        info = stat_result["info"]
        assert "path" in info
        assert "size_bytes" in info
        assert "modified" in info
        assert "checksum" in info
        assert info["size_bytes"] > 0

    @pytest.mark.asyncio
    async def test_dataset_listing(self, data_lake_service):
        """Test dataset listing functionality."""
        # Mock database response
        mock_datasets = [MagicMock()]
        mock_datasets[0].id = 1
        mock_datasets[0].name = "test:dataset"
        mock_datasets[0].dataset_type = "tabular"
        mock_datasets[0].data_format = "csv"
        mock_datasets[0].file_path = "/test/path.csv"
        mock_datasets[0].created_at = MagicMock()
        mock_datasets[0].created_at.isoformat.return_value = "2025-09-01T12:00:00"
        mock_datasets[0].is_public = True
        
        data_lake_service.db.get_datasets.return_value = mock_datasets
        
        list_request = {
            "action": "list",
            "limit": 10
        }
        
        list_result = await data_lake_service.process_request(list_request)
        
        assert list_result["success"] is True
        assert "datasets" in list_result
        assert "filesystem" in list_result
        assert len(list_result["datasets"]) == 1
        assert list_result["datasets"][0]["id"] == 1

    @pytest.mark.asyncio
    async def test_file_size_limit_enforcement(self, data_lake_service):
        """Test that file size limits are properly enforced."""
        # Create a file that exceeds the size limit
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            # Write enough data to exceed 10MB limit
            writer = csv.writer(f)
            writer.writerow(['id', 'data'])
            for i in range(100000):  # Large number of rows
                writer.writerow([i, 'x' * 100])  # Each row ~100 bytes
            large_file = f.name
        
        request_data = {
            "action": "ingest",
            "source": large_file,
            "namespace": "test",
            "name": "large_file"
        }
        
        result = await data_lake_service.process_request(request_data)
        
        assert result["success"] is False
        assert "exceeds max size limit" in result["error"]
        
        # Clean up
        Path(large_file).unlink()

    @pytest.mark.asyncio
    async def test_invalid_file_handling(self, data_lake_service):
        """Test handling of non-existent files."""
        request_data = {
            "action": "ingest",
            "source": "/non/existent/file.csv",
            "namespace": "test",
            "name": "nonexistent"
        }
        
        result = await data_lake_service.process_request(request_data)
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_unsupported_action(self, data_lake_service):
        """Test handling of unsupported actions."""
        request_data = {
            "action": "invalid_action",
            "source": "test.csv"
        }
        
        result = await data_lake_service.process_request(request_data)
        
        assert result["success"] is False
        assert "Unknown action" in result["error"]
        assert "available_actions" in result

    @pytest.mark.asyncio
    async def test_security_path_validation(self, data_lake_service, test_csv_file):
        """Test strict path security validation."""
        # Test with a non-existent file (should fail)
        nonexistent_file = "/definitely/does/not/exist.csv"
        
        request_data = {
            "action": "ingest",
            "source": nonexistent_file,
            "namespace": "test",
            "name": "nonexistent"
        }
        
        result = await data_lake_service.process_request(request_data)
        
        # Should fail because file doesn't exist
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_auto_format_detection(self, data_lake_service, test_csv_file):
        """Test automatic format detection."""
        request_data = {
            "action": "ingest",
            "source": test_csv_file,
            "namespace": "format_test",
            "name": "auto_format",
            "data_format": "auto"
        }
        
        result = await data_lake_service.process_request(request_data)
        
        assert result["success"] is True
        assert result["data_format"] == "csv"

    @pytest.mark.asyncio
    async def test_error_handling(self, data_lake_service):
        """Test comprehensive error handling."""
        # Test with missing source
        request_data = {
            "action": "ingest",
            "namespace": "test",
            "name": "test"
        }
        
        result = await data_lake_service.process_request(request_data)
        assert result["success"] is False
        assert "source" in result["error"]

    def test_s3_backend_initialization(self):
        """Test S3 backend initialization when enabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('os.getenv') as mock_getenv:
                mock_getenv.side_effect = lambda key, default=None: {
                    "DATALAKE_ROOT": temp_dir,
                    "ENABLE_S3": "1"
                }.get(key, default)
                
                # Mock S3 availability
                with patch('app.services.scientific_data_lake_service.S3FS_AVAILABLE', True):
                    # Mock S3 filesystem
                    mock_s3_instance = MagicMock()
                    with patch('app.services.scientific_data_lake_service.s3fs') as mock_s3fs:
                        mock_s3fs.S3FileSystem.return_value = mock_s3_instance
                        
                        # Mock database
                        with patch('app.services.scientific_data_lake_service.DatabaseService'):
                            service = ScientificDataLakeService()
                            
                            assert service.enable_s3 is True
                            assert service.s3 is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])