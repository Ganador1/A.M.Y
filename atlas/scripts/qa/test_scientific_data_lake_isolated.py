#!/usr/bin/env python3
"""
Isolated test for ScientificDataLakeService
This test runs independently of the main application to avoid dependency issues.
"""

import sys
import os
import tempfile
import json
import csv
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add the app directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Mock all dependencies before importing
mock_db_service = MagicMock()
mock_db_service.save_dataset.return_value = MagicMock(id=1)

@pytest.fixture(autouse=True)
def mock_imports():
    with patch.dict('sys.modules', {
        'app.services.database_service': MagicMock(),
    }):
        with patch('app.services.database_service.DatabaseService', return_value=mock_db_service):
            yield

from app.services.scientific_data_lake_service import ScientificDataLakeService

@pytest.fixture
def temp_dir_fixture():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

def test_service_initialization(temp_dir_fixture):
    """Test 1: Service initialization"""
    with patch('os.getenv') as mock_getenv:
        mock_getenv.side_effect = lambda key, default=None: {
            'DATALAKE_ROOT': temp_dir_fixture,
            'MAX_DATALAKE_FILE_BYTES': '10485760',  # 10MB
            'STRICT_DATALAKE_PATHS': '1',
            'ENABLE_S3': '0'
        }.get(key, default)
        
        service = ScientificDataLakeService(db_service=mock_db_service)
        info = service.get_service_info()
        
        assert info['name'] == 'ScientificDataLakeService'
        assert info['version'] == '1.0.0'
        assert info['backends']['s3'] is False

@pytest.mark.asyncio
async def test_file_ingestion(temp_dir_fixture):
    """Test 2: File ingestion"""
    with patch('os.getenv') as mock_getenv:
        mock_getenv.side_effect = lambda key, default=None: {
            'DATALAKE_ROOT': temp_dir_fixture,
            'MAX_DATALAKE_FILE_BYTES': '10485760',
            'STRICT_DATALAKE_PATHS': '1',
            'ENABLE_S3': '0'
        }.get(key, default)
        
        service = ScientificDataLakeService(db_service=mock_db_service)
        
        # Create test CSV file
        test_csv = os.path.join(temp_dir_fixture, 'test.csv')
        with open(test_csv, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'value'])
            writer.writerow([1, 'test1', 100.5])
            writer.writerow([2, 'test2', 200.3])
        
        # Test ingestion
        request_data = {
            'action': 'ingest',
            'source': test_csv,
            'namespace': 'test',
            'name': 'integration_test',
            'dataset_type': 'tabular',
            'description': 'Integration test dataset'
        }
        
        result = await service.process_request(request_data)
        
        assert result['success'] is True
        assert result['data_format'] == 'csv'
        assert result['backend'] == 'local'
        assert result['size_bytes'] > 0

@pytest.mark.asyncio
async def test_error_handling(temp_dir_fixture):
    """Test 3: Error handling"""
    with patch('os.getenv') as mock_getenv:
        mock_getenv.side_effect = lambda key, default=None: {
            'DATALAKE_ROOT': temp_dir_fixture,
            'MAX_DATALAKE_FILE_BYTES': '10485760',
            'STRICT_DATALAKE_PATHS': '1',
            'ENABLE_S3': '0'
        }.get(key, default)
        
        service = ScientificDataLakeService(db_service=mock_db_service)
        
        # Test with non-existent file
        request_data = {
            'action': 'ingest',
            'source': '/non/existent/file.csv',
            'namespace': 'test',
            'name': 'nonexistent'
        }
        
        result = await service.process_request(request_data)
        
        assert result['success'] is False
        assert 'not found' in result['error'].lower() or 'exist' in result['error'].lower()