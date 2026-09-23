"""
Comprehensive tests for ProtGPT2 Protein Design Service
Tests both service functionality and API endpoints
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.services.protgpt2_service import ProtGPT2ProteinDesignService
from app.routers.protgpt2_router import router
from fastapi.testclient import TestClient
from fastapi import FastAPI


@pytest.fixture
def protgpt2_service():
    """Create ProtGPT2 service instance for testing"""
    return ProtGPT2ProteinDesignService()


@pytest.fixture
def test_app():
    """Create test FastAPI app with ProtGPT2 router"""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(test_app):
    """Create test client"""
    return TestClient(test_app)


class TestProtGPT2Service:
    """Test ProtGPT2 service functionality"""
    
    @pytest.mark.asyncio
    async def test_protein_sequence_generation(self, protgpt2_service):
        """Test basic protein sequence generation"""
        prompt = "small binding protein with high affinity"
        
        result = await protgpt2_service.generate_protein_sequence(prompt)
        
        assert result['success'] is True
        assert 'data' in result
        
        generated_protein = result['data']['generated_protein']
        assert 'sequence' in generated_protein
        assert 'generation_id' in generated_protein
        assert 'confidence_score' in generated_protein
        assert generated_protein['prompt_used'] == prompt
        
        # Validate sequence format
        sequence = generated_protein['sequence']
        assert len(sequence) >= 20
        assert all(aa in "ACDEFGHIKLMNPQRSTVWY" for aa in sequence)
    
    @pytest.mark.asyncio
    async def test_protein_generation_validation(self, protgpt2_service):
        """Test input validation for protein generation"""
        # Test empty prompt
        result = await protgpt2_service.generate_protein_sequence("")
        assert result['success'] is False
        assert 'error' in result
        
        # Test short prompt
        result = await protgpt2_service.generate_protein_sequence("ab")
        assert result['success'] is False
    
    @pytest.mark.asyncio
    async def test_protein_optimization(self, protgpt2_service):
        """Test protein sequence optimization"""
        # Valid protein sequence
        sequence = "ACDEFGHIKLMNPQRSTVWYACDEFGHIKLMNPQRSTVWY"
        target_property = "stability"
        
        result = await protgpt2_service.optimize_protein_sequence(sequence, target_property)
        
        assert result['success'] is True
        assert 'data' in result
        
        optimization = result['data']['optimization']
        assert optimization['original_sequence'] == sequence
        assert 'optimized_sequence' in optimization
        assert 'mutations' in optimization
        assert optimization['target_property'] == target_property
        assert len(optimization['mutations']) > 0
    
    @pytest.mark.asyncio
    async def test_optimization_invalid_sequence(self, protgpt2_service):
        """Test optimization with invalid sequence"""
        invalid_sequence = "XBZJ"  # Invalid amino acids
        
        result = await protgpt2_service.optimize_protein_sequence(
            invalid_sequence, "stability"
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_domain_insertion(self, protgpt2_service):
        """Test domain insertion design"""
        base_sequence = "ACDEFGHIKLMNPQRSTVWYACDEFGHIKLMNPQRSTVWY"
        domain_function = "binding domain for substrate recognition"
        
        result = await protgpt2_service.design_domain_insertion(
            base_sequence, domain_function
        )
        
        assert result['success'] is True
        assert 'data' in result
        
        insertion = result['data']['domain_insertion']
        assert insertion['base_sequence'] == base_sequence
        assert 'modified_sequence' in insertion
        assert 'inserted_domain' in insertion
        assert 'insertion_position' in insertion
        
        # Modified sequence should be longer
        assert len(insertion['modified_sequence']) > len(base_sequence)
    
    @pytest.mark.asyncio
    async def test_batch_variant_generation(self, protgpt2_service):
        """Test batch variant generation"""
        base_prompt = "catalytic enzyme for hydrolysis"
        num_variants = 3
        
        result = await protgpt2_service.batch_generate_variants(
            base_prompt, num_variants
        )
        
        assert result['success'] is True
        assert 'data' in result
        
        variants = result['data']['variants']
        assert len(variants) <= num_variants  # May be fewer if some fail
        
        # Each variant should be valid
        for variant in variants:
            assert 'sequence' in variant
            assert 'generation_id' in variant
            assert len(variant['sequence']) >= 20
    
    @pytest.mark.asyncio
    async def test_batch_generation_limits(self, protgpt2_service):
        """Test batch generation limits"""
        base_prompt = "test protein"
        
        # Test exceeding limit
        result = await protgpt2_service.batch_generate_variants(
            base_prompt, 15  # Over limit of 10
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_sequence_validation(self, protgpt2_service):
        """Test protein sequence validation"""
        # Valid sequence
        valid_seq = "ACDEFGHIKLMNPQRSTVWY"
        is_valid, result = protgpt2_service._is_valid_protein_sequence(valid_seq)
        assert is_valid is True
        assert result == valid_seq
        
        # Invalid characters
        invalid_seq = "ACDEFGHIJKLMN"  # Contains 'J'
        is_valid, error = protgpt2_service._is_valid_protein_sequence(invalid_seq)
        assert is_valid is False
        assert "Invalid amino acid codes" in error
        
        # Too short
        short_seq = "ACE"
        is_valid, error = protgpt2_service._is_valid_protein_sequence(short_seq)
        assert is_valid is False
        assert "too short" in error
    
    @pytest.mark.asyncio
    async def test_health_check(self, protgpt2_service):
        """Test service health check"""
        health = await protgpt2_service.health_check()
        
        assert 'service_status' in health
        assert 'service_name' in health
        assert 'version' in health
        assert 'supported_features' in health
        assert health['service_name'] == 'ProtGPT2ProteinDesignService'


class TestProtGPT2Router:
    """Test ProtGPT2 API endpoints"""
    
    def test_generate_endpoint(self, client):
        """Test protein generation endpoint"""
        request_data = {
            "prompt": "small enzyme for ATP hydrolysis",
            "temperature": 0.8,
            "top_p": 0.9,
            "max_length": 200
        }
        
        response = client.post("/protgpt2/generate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'data' in data
        assert 'generated_protein' in data['data']
    
    def test_generate_invalid_request(self, client):
        """Test generation with invalid request"""
        # Empty prompt
        request_data = {"prompt": ""}
        
        response = client.post("/protgpt2/generate", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_optimize_endpoint(self, client):
        """Test protein optimization endpoint"""
        request_data = {
            "sequence": "ACDEFGHIKLMNPQRSTVWYACDEFGHIKLMNPQRSTVWY",
            "target_property": "stability"
        }
        
        response = client.post("/protgpt2/optimize", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'optimization' in data['data']
    
    def test_domain_insertion_endpoint(self, client):
        """Test domain insertion endpoint"""
        request_data = {
            "base_sequence": "ACDEFGHIKLMNPQRSTVWYACDEFGHIKLMNPQRSTVWY",
            "domain_function": "binding domain"
        }
        
        response = client.post("/protgpt2/insert-domain", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'domain_insertion' in data['data']
    
    def test_batch_variants_endpoint(self, client):
        """Test batch variant generation endpoint"""
        request_data = {
            "base_prompt": "binding protein",
            "num_variants": 3
        }
        
        response = client.post("/protgpt2/batch-variants", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'variants' in data['data']
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/protgpt2/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'service_status' in data['data']
    
    def test_capabilities_endpoint(self, client):
        """Test capabilities endpoint"""
        response = client.get("/protgpt2/capabilities")
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'service_name' in data['data']
        assert 'supported_operations' in data['data']
    
    def test_async_generation_endpoint(self, client):
        """Test asynchronous generation endpoint"""
        request_data = {
            "prompt": "large complex enzyme",
            "temperature": 0.7
        }
        
        response = client.post("/protgpt2/generate-async", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'status' in data['data']
        assert data['data']['status'] == 'processing'


class TestProtGPT2Integration:
    """Integration tests for ProtGPT2 service"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self, protgpt2_service):
        """Test complete protein design workflow"""
        # 1. Generate base protein
        generation_result = await protgpt2_service.generate_protein_sequence(
            "enzyme for substrate binding and catalysis"
        )
        assert generation_result['success'] is True
        
        base_sequence = generation_result['data']['generated_protein']['sequence']
        
        # 2. Optimize the protein
        optimization_result = await protgpt2_service.optimize_protein_sequence(
            base_sequence, "stability"
        )
        assert optimization_result['success'] is True
        
        # 3. Design domain insertion
        insertion_result = await protgpt2_service.design_domain_insertion(
            base_sequence, "allosteric regulation"
        )
        assert insertion_result['success'] is True
        
        # Verify all steps produced valid results
        assert len(base_sequence) >= 20
        assert len(optimization_result['data']['optimization']['mutations']) > 0
        assert len(insertion_result['data']['domain_insertion']['modified_sequence']) > len(base_sequence)
    
    @pytest.mark.asyncio
    async def test_concurrent_generations(self, protgpt2_service):
        """Test concurrent protein generations"""
        prompts = [
            "binding protein for metal ions",
            "structural protein for membrane",
            "catalytic protein for oxidation"
        ]
        
        # Run generations concurrently
        tasks = [
            protgpt2_service.generate_protein_sequence(prompt)
            for prompt in prompts
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(result['success'] for result in results)
        
        # All should produce different sequences
        sequences = [result['data']['generated_protein']['sequence'] for result in results]
        assert len(set(sequences)) == len(sequences)  # All unique
    
    @pytest.mark.asyncio
    async def test_property_based_generation(self, protgpt2_service):
        """Test generation with different property requirements"""
        properties_prompts = [
            ("stability", "thermostable enzyme for high temperature"),
            ("binding", "high affinity receptor for specific ligand"),
            ("catalytic", "efficient enzyme with high turnover rate")
        ]
        
        for property_type, prompt in properties_prompts:
            result = await protgpt2_service.generate_protein_sequence(prompt)
            
            assert result['success'] is True
            
            # Check if properties are predicted correctly
            properties = result['data']['generated_protein']['properties_predicted']
            assert 'function_prediction' in properties
            
            # Verify sequence quality
            sequence = result['data']['generated_protein']['sequence']
            assert len(sequence) >= 20
            assert all(aa in "ACDEFGHIKLMNPQRSTVWY" for aa in sequence)


class TestProtGPT2Performance:
    """Performance tests for ProtGPT2 service"""
    
    @pytest.mark.asyncio
    async def test_generation_speed(self, protgpt2_service):
        """Test generation performance"""
        prompt = "test protein for performance evaluation"
        
        start_time = datetime.now()
        result = await protgpt2_service.generate_protein_sequence(prompt)
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        assert result['success'] is True
        assert duration < 5.0  # Should complete within 5 seconds
    
    @pytest.mark.asyncio
    async def test_batch_performance(self, protgpt2_service):
        """Test batch generation performance"""
        base_prompt = "performance test protein"
        
        start_time = datetime.now()
        result = await protgpt2_service.batch_generate_variants(base_prompt, 5)
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        assert result['success'] is True
        assert duration < 15.0  # Batch should complete within 15 seconds
        assert len(result['data']['variants']) > 0


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
