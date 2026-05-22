#!/usr/bin/env python3
"""
Test Suite for AXIOM Digital Twins Service
Comprehensive unit tests for digital twins functionality

Author: AXIOM Autonomous Laboratory System
Date: September 13, 2025
"""

import pytest
import asyncio
from datetime import datetime, timedelta

from app.services.digital_twins_service import (
    DigitalTwinsService, TwinType,
    SensorReading, ChemicalReactionTwin, BiologicalProcessTwin,
    SimulationState, SyncStatus
)

class TestDigitalTwinsService:
    """Test suite for Digital Twins Service"""
    
    @pytest.fixture
    def service(self):
        """Create a digital twins service instance for testing"""
        return DigitalTwinsService()
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """Test Digital Twins Service initialization"""
        assert service is not None
        assert len(service.twins) == 0
        assert len(service.active_simulations) == 0
        assert service.total_simulations == 0
        assert "chemical_reaction" in service.twin_models
        assert "biological_process" in service.twin_models
    
    @pytest.mark.asyncio
    async def test_create_chemical_reaction_twin(self, service):
        """Test creation of chemical reaction digital twin"""
        twin = await service.create_digital_twin(
            name="Test Chemical Reaction",
            twin_type=TwinType.PROCESS,
            model_type="chemical_reaction",
            parameters={"temperature": 65.0, "pressure": 2.5}
        )
        
        assert twin is not None
        assert twin.name == "Test Chemical Reaction"
        assert twin.twin_type == TwinType.PROCESS
        assert twin.is_active
        assert twin.sync_status == SyncStatus.NOT_CONNECTED
        assert isinstance(twin.model, ChemicalReactionTwin)
        
        # Check parameter override
        assert twin.model.parameters["temperature"].value == 65.0
        assert twin.model.parameters["pressure"].value == 2.5
        
        # Verify twin is stored in service
        assert twin.id in service.twins
    
    @pytest.mark.asyncio
    async def test_create_biological_process_twin(self, service):
        """Test creation of biological process digital twin"""
        twin = await service.create_digital_twin(
            name="Test Cell Culture",
            twin_type=TwinType.PROCESS,
            model_type="biological_process",
            parameters={"cell_density": 2e6, "ph": 7.4}
        )
        
        assert twin is not None
        assert twin.name == "Test Cell Culture"
        assert isinstance(twin.model, BiologicalProcessTwin)
        
        # Check parameter override
        assert twin.model.parameters["cell_density"].value == 2e6
        assert twin.model.parameters["ph"].value == 7.4
    
    @pytest.mark.asyncio
    async def test_invalid_model_type(self, service):
        """Test error handling for invalid model types"""
        with pytest.raises(ValueError, match="Model type invalid_model not supported"):
            await service.create_digital_twin(
                name="Invalid Twin",
                twin_type=TwinType.PROCESS,
                model_type="invalid_model"
            )
    
    @pytest.mark.asyncio
    async def test_chemical_reaction_simulation(self, service):
        """Test chemical reaction simulation functionality"""
        # Create twin
        twin = await service.create_digital_twin(
            name="Reaction Simulation Test",
            twin_type=TwinType.PROCESS,
            model_type="chemical_reaction"
        )
        
        # Run simulation
        duration = timedelta(hours=2)
        results = await service.run_simulation(
            twin_id=twin.id,
            duration=duration,
            scenario_name="test_scenario"
        )
        
        assert results is not None
        assert results.twin_id == twin.id
        assert results.state == SimulationState.COMPLETED
        assert results.duration is not None
        assert results.end_time is not None
        assert len(results.parameters) > 0
        assert "conversion" in results.parameters
        assert "reaction_rate" in results.parameters
        
        # Check that simulation was tracked
        assert service.total_simulations == 1
        assert twin.id in service.active_simulations
    
    @pytest.mark.asyncio
    async def test_biological_process_simulation(self, service):
        """Test biological process simulation functionality"""
        # Create twin
        twin = await service.create_digital_twin(
            name="Cell Culture Simulation",
            twin_type=TwinType.PROCESS,
            model_type="biological_process"
        )
        
        # Run simulation
        duration = timedelta(hours=24)
        results = await service.run_simulation(
            twin_id=twin.id,
            duration=duration,
            scenario_name="growth_phase"
        )
        
        assert results.state == SimulationState.COMPLETED
        assert "cell_density" in results.parameters
        assert "viability" in results.parameters
        assert "growth_rate" in results.parameters
        
        # Verify cell growth occurred
        final_density = results.parameters["cell_density"].value
        assert final_density > 1e6  # Should have grown from initial 1e6
    
    @pytest.mark.asyncio
    async def test_simulation_invalid_twin(self, service):
        """Test simulation error handling for non-existent twin"""
        with pytest.raises(ValueError, match="Twin nonexistent_twin not found"):
            await service.run_simulation(
                twin_id="nonexistent_twin",
                duration=timedelta(hours=1)
            )
    
    @pytest.mark.asyncio
    async def test_chemical_reaction_prediction(self, service):
        """Test prediction functionality for chemical reaction"""
        # Create and set up twin
        twin = await service.create_digital_twin(
            name="Prediction Test",
            twin_type=TwinType.PROCESS,
            model_type="chemical_reaction"
        )
        
        # Get prediction
        prediction = await service.get_prediction(
            twin_id=twin.id,
            parameter="conversion",
            time_horizon=timedelta(hours=6)
        )
        
        assert prediction is not None
        assert prediction.parameter == "conversion"
        assert prediction.predicted_value >= 0
        assert prediction.confidence > 0
        assert prediction.confidence <= 1.0
        assert prediction.prediction_method == "kinetic_model"
        assert len(prediction.uncertainty_range) == 2
        
        # Check service tracking
        assert service.successful_predictions == 1
    
    @pytest.mark.asyncio
    async def test_biological_process_prediction(self, service):
        """Test prediction functionality for biological process"""
        # Create twin
        twin = await service.create_digital_twin(
            name="Bio Prediction Test",
            twin_type=TwinType.PROCESS,
            model_type="biological_process"
        )
        
        # Get prediction for cell density
        prediction = await service.get_prediction(
            twin_id=twin.id,
            parameter="cell_density",
            time_horizon=timedelta(hours=12)
        )
        
        assert prediction.parameter == "cell_density"
        assert prediction.predicted_value > 1e6  # Should predict growth
        assert prediction.prediction_method == "biological_model"
    
    @pytest.mark.asyncio
    async def test_prediction_invalid_parameter(self, service):
        """Test prediction error handling for invalid parameter"""
        twin = await service.create_digital_twin(
            name="Error Test",
            twin_type=TwinType.PROCESS,
            model_type="chemical_reaction"
        )
        
        with pytest.raises(ValueError, match="Parameter invalid_param not found"):
            await service.get_prediction(
                twin_id=twin.id,
                parameter="invalid_param",
                time_horizon=timedelta(hours=1)
            )
    
    @pytest.mark.asyncio
    async def test_chemical_optimization(self, service):
        """Test optimization suggestions for chemical reaction"""
        twin = await service.create_digital_twin(
            name="Optimization Test",
            twin_type=TwinType.PROCESS,
            model_type="chemical_reaction"
        )
        
        suggestions = await service.optimize_experiment(
            twin_id=twin.id,
            objective="maximize_yield",
            constraints={"max_temperature": 100.0}
        )
        
        assert len(suggestions) > 0
        for suggestion in suggestions:
            assert suggestion.parameter in twin.model.parameters
            assert suggestion.expected_improvement > 0
            assert 0 < suggestion.confidence <= 1.0
            assert len(suggestion.reasoning) > 0
        
        # Check service tracking
        assert service.optimization_suggestions >= len(suggestions)
    
    @pytest.mark.asyncio
    async def test_biological_optimization(self, service):
        """Test optimization suggestions for biological process"""
        twin = await service.create_digital_twin(
            name="Bio Optimization Test",
            twin_type=TwinType.PROCESS,
            model_type="biological_process"
        )
        
        suggestions = await service.optimize_experiment(
            twin_id=twin.id,
            objective="maximize_viability"
        )
        
        assert len(suggestions) > 0
        for suggestion in suggestions:
            assert suggestion.parameter in ["dissolved_oxygen", "glucose_concentration", "ph"]
    
    @pytest.mark.asyncio
    async def test_sensor_synchronization(self, service):
        """Test synchronization with sensor data"""
        twin = await service.create_digital_twin(
            name="Sync Test",
            twin_type=TwinType.PROCESS,
            model_type="chemical_reaction"
        )
        
        # Create sensor readings
        sensor_data = [
            SensorReading(
                sensor_id="temp_001",
                parameter_name="temperature",
                value=70.0,
                unit="°C",
                timestamp=datetime.now(),
                confidence=0.95
            ),
            SensorReading(
                sensor_id="press_001",
                parameter_name="pressure",
                value=2.2,
                unit="atm",
                timestamp=datetime.now(),
                confidence=0.90
            )
        ]
        
        # Sync with sensor data
        sync_result = await service.sync_with_real_data(
            twin_id=twin.id,
            sensor_data=sensor_data
        )
        
        assert sync_result["twin_id"] == twin.id
        assert sync_result["sync_status"] == SyncStatus.CONNECTED.value
        assert sync_result["synced_parameters"] == 2
        assert sync_result["calibration_accuracy"] > 0
        
        # Verify parameters were updated
        twin_obj = service.twins[twin.id]
        assert twin_obj.model.parameters["temperature"].value == 70.0
        assert twin_obj.model.parameters["pressure"].value == 2.2
        assert twin_obj.sync_status == SyncStatus.CONNECTED
    
    @pytest.mark.asyncio
    async def test_get_twin_status(self, service):
        """Test getting detailed twin status"""
        twin = await service.create_digital_twin(
            name="Status Test",
            twin_type=TwinType.PROCESS,
            model_type="chemical_reaction"
        )
        
        status = await service.get_twin_status(twin.id)
        
        assert status["twin_id"] == twin.id
        assert status["name"] == "Status Test"
        assert status["type"] == "process"
        assert status["model_type"] == "chemical_reaction"
        assert status["is_active"]
        assert status["sync_status"] == "not_connected"
        assert "parameters" in status
        assert len(status["parameters"]) > 0
        assert "temperature" in status["parameters"]
        assert "created_at" in status
    
    @pytest.mark.asyncio
    async def test_list_digital_twins(self, service):
        """Test listing all digital twins"""
        # Create multiple twins
        await service.create_digital_twin(
            name="Twin 1", twin_type=TwinType.PROCESS, model_type="chemical_reaction"
        )
        await service.create_digital_twin(
            name="Twin 2", twin_type=TwinType.PROCESS, model_type="biological_process"
        )
        
        twins_list = await service.list_digital_twins()
        
        assert len(twins_list) == 2
        assert all("id" in twin for twin in twins_list)
        assert all("name" in twin for twin in twins_list)
        assert all("type" in twin for twin in twins_list)
        
        names = [twin["name"] for twin in twins_list]
        assert "Twin 1" in names
        assert "Twin 2" in names
    
    @pytest.mark.asyncio
    async def test_service_statistics(self, service):
        """Test service statistics retrieval"""
        # Create some twins and run operations
        twin = await service.create_digital_twin(
            name="Stats Test", twin_type=TwinType.PROCESS, model_type="chemical_reaction"
        )
        await service.run_simulation(twin.id, timedelta(hours=1))
        await service.get_prediction(twin.id, "temperature", timedelta(hours=2))
        
        stats = await service.get_service_statistics()
        
        assert stats["service_name"] == "AXIOM Digital Twins Service"
        assert stats["status"] == "operational"
        assert stats["total_twins"] == 1
        assert stats["active_twins"] == 1
        assert stats["total_simulations"] >= 1
        assert stats["successful_predictions"] >= 1
        assert "supported_models" in stats
        assert len(stats["supported_models"]) >= 2
    
    @pytest.mark.asyncio
    async def test_delete_digital_twin(self, service):
        """Test deleting a digital twin"""
        twin = await service.create_digital_twin(
            name="Delete Test", twin_type=TwinType.PROCESS, model_type="chemical_reaction"
        )
        
        # Verify twin exists
        assert twin.id in service.twins
        
        # Delete twin
        success = await service.delete_digital_twin(twin.id)
        assert success
        
        # Verify twin is gone
        assert twin.id not in service.twins
        assert twin.id not in service.active_simulations
        
        # Try to delete again (should fail)
        success = await service.delete_digital_twin(twin.id)
        assert not success
    
    @pytest.mark.asyncio
    async def test_supported_model_types(self, service):
        """Test getting supported model types information"""
        models = service.get_supported_model_types()
        
        assert "chemical_reaction" in models
        assert "biological_process" in models
        
        chem_model = models["chemical_reaction"]
        assert "name" in chem_model
        assert "description" in chem_model
        assert "parameters" in chem_model
        assert "capabilities" in chem_model
        assert "simulation" in chem_model["capabilities"]
        assert "prediction" in chem_model["capabilities"]
    
    @pytest.mark.asyncio
    async def test_parameter_validation(self, service):
        """Test parameter validation in twin models"""
        twin = await service.create_digital_twin(
            name="Validation Test",
            twin_type=TwinType.PROCESS,
            model_type="chemical_reaction"
        )
        
        # Check parameter constraints
        temp_param = twin.model.parameters["temperature"]
        assert temp_param.min_value == 0
        assert temp_param.max_value == 500
        
        pressure_param = twin.model.parameters["pressure"]
        assert pressure_param.min_value == 0.1
        assert pressure_param.max_value == 100
    
    @pytest.mark.asyncio
    async def test_twin_parameter_updates(self, service):
        """Test updating twin parameters"""
        twin = await service.create_digital_twin(
            name="Update Test",
            twin_type=TwinType.PROCESS,
            model_type="chemical_reaction"
        )
        
        # Update parameters
        original_temp = twin.model.parameters["temperature"].value
        twin.model.parameters["temperature"].value = 80.0
        twin.model.parameters["temperature"].source = "manual_update"
        
        assert twin.model.parameters["temperature"].value == 80.0
        assert twin.model.parameters["temperature"].value != original_temp
        assert twin.model.parameters["temperature"].source == "manual_update"
    
    @pytest.mark.asyncio
    async def test_simulation_error_handling(self, service):
        """Test simulation error handling"""
        twin = await service.create_digital_twin(
            name="Error Test",
            twin_type=TwinType.PROCESS,
            model_type="chemical_reaction"
        )
        
        # Try to run simulation with zero duration (should work but be very short)
        duration = timedelta(seconds=1)
        results = await service.run_simulation(twin.id, duration)
        
        # Should complete successfully even with very short duration
        assert results.state in [SimulationState.COMPLETED, SimulationState.RUNNING]
    
    @pytest.mark.asyncio
    async def test_calibration_accuracy(self, service):
        """Test calibration accuracy calculation"""
        twin = await service.create_digital_twin(
            name="Calibration Test",
            twin_type=TwinType.PROCESS,
            model_type="chemical_reaction"
        )
        
        # Create accurate sensor readings
        accurate_readings = [
            SensorReading(
                sensor_id="temp_001",
                parameter_name="temperature",
                value=25.0,  # Close to initial value
                unit="°C",
                timestamp=datetime.now()
            )
        ]
        
        # Sync with accurate data
        await service.sync_with_real_data(twin.id, accurate_readings)
        twin_obj = service.twins[twin.id]
        
        assert twin_obj.model.calibration_accuracy > 0.5  # Should be reasonably accurate
    
    @pytest.mark.asyncio
    async def test_concurrent_simulations(self, service):
        """Test running multiple simulations concurrently"""
        # Create multiple twins
        twin1 = await service.create_digital_twin(
            name="Concurrent 1", twin_type=TwinType.PROCESS, model_type="chemical_reaction"
        )
        twin2 = await service.create_digital_twin(
            name="Concurrent 2", twin_type=TwinType.PROCESS, model_type="biological_process"
        )
        
        # Run simulations concurrently
        duration = timedelta(hours=1)
        sim1_task = service.run_simulation(twin1.id, duration, "scenario_1")
        sim2_task = service.run_simulation(twin2.id, duration, "scenario_2")
        
        results1, results2 = await asyncio.gather(sim1_task, sim2_task)
        
        assert results1.twin_id == twin1.id
        assert results2.twin_id == twin2.id
        assert results1.state == SimulationState.COMPLETED
        assert results2.state == SimulationState.COMPLETED
        
        # Check that both simulations are tracked
        assert service.total_simulations == 2
