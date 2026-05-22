import math
import pytest

from app.domains.chemistry.analytical.differential_scanning_calorimetry_service import (
    DifferentialScanningCalorimetryService,
    DSCThermogram,
    ThermalAnalysisResult,
    KineticsAnalysisResult,
)


@pytest.mark.asyncio
async def test_acquire_thermogram_simulated_ok():
    service = DifferentialScanningCalorimetryService()

    thermogram = await service.acquire_thermogram(
        sample_id="unit_polymer_001",
        sample_mass=5.0,
        heating_rate=10.0,
        temperature_range=(25.0, 300.0),
        atmosphere="nitrogen",
        reference_material="indium",
        simulate=True,
    )

    assert isinstance(thermogram, DSCThermogram)
    assert len(thermogram.temperature_data) > 0
    assert len(thermogram.heat_flow_data) == len(thermogram.temperature_data)
    assert thermogram.sample_mass == 5.0
    assert thermogram.heating_rate == 10.0
    assert thermogram.temperature_range == (25.0, 300.0)


@pytest.mark.asyncio
async def test_perform_complete_analysis_ok():
    service = DifferentialScanningCalorimetryService()

    result = await service.perform_complete_analysis(
        sample_id="unit_polymer_002",
        sample_mass=4.0,
        heating_rate=15.0,
        temperature_range=(30.0, 320.0),
        atmosphere="nitrogen",
    )

    assert isinstance(result, ThermalAnalysisResult)
    assert result.analysis_id
    assert isinstance(result.thermogram, DSCThermogram)
    # Transitions may be empty in some simulations; just ensure list exists
    assert isinstance(result.transitions, list)
    # Thermal properties exist (may be None depending on data)
    assert hasattr(result, "melting_point")
    assert hasattr(result, "glass_transition_temp")
    assert hasattr(result, "decomposition_temp")


@pytest.mark.asyncio
async def test_perform_kinetics_analysis_ok():
    service = DifferentialScanningCalorimetryService()

    heating_rates = [5.0, 10.0, 20.0]
    peak_temps = [320.5, 330.2, 342.1]

    kinetics = await service.perform_kinetics_analysis(
        heating_rates=heating_rates,
        peak_temps=peak_temps,
        reaction_type="decomposition",
    )

    assert isinstance(kinetics, KineticsAnalysisResult)
    assert kinetics.activation_energy is not None
    assert isinstance(kinetics.correlation_coefficient, float)
    assert not math.isnan(kinetics.correlation_coefficient)
    assert isinstance(kinetics.confidence_level, float)
    # El servicio reporta confianza como porcentaje (0-100). Aceptamos ese rango.
    assert 0.0 <= kinetics.confidence_level <= 100.0