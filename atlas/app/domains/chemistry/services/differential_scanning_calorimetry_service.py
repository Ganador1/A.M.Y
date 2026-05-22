#!/usr/bin/env python3
"""
Differential Scanning Calorimetry Service

Este servicio proporciona análisis térmico avanzado mediante Calorimetría Diferencial de Barrido (DSC).
Incluye simulación de termogramas, detección de transiciones térmicas, análisis cinético y caracterización
de materiales. Fundamental para:

- Análisis de transiciones térmicas (fusión, cristalización, transiciones vítreas)
- Determinación de energías de activación
- Análisis cinético de reacciones térmicas
- Caracterización de polímeros y materiales
- Análisis de pureza y composición
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field
import asyncio

from app.services.base_service import BaseService
from app.exceptions.domain.chemistry import ChemistryError

# Configure logging
logger = logging.getLogger(__name__)

# Data models for DSC analysis results
class DSCThermogram(BaseModel):
    """DSC thermogram data"""
    thermogram_id: str = Field(..., description="Unique thermogram identifier")
    sample_mass: float = Field(..., description="Sample mass in mg")
    heating_rate: float = Field(..., description="Heating rate in °C/min")
    temperature_range: Tuple[float, float] = Field(..., description="Temperature range (min, max) in °C")
    atmosphere: str = Field(default="nitrogen", description="Measurement atmosphere")
    reference_material: Optional[str] = Field(default=None, description="Reference material used")

    temperature_data: List[float] = Field(..., description="Temperature values in °C")
    heat_flow_data: List[float] = Field(..., description="Heat flow values in mW")
    baseline_corrected: bool = Field(default=False, description="Whether baseline correction was applied")

    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional measurement metadata")

class ThermalTransition(BaseModel):
    """Thermal transition detected in DSC"""
    transition_id: str = Field(..., description="Unique transition identifier")
    transition_type: str = Field(..., description="Type of thermal transition")
    onset_temperature: float = Field(..., description="Onset temperature in °C")
    peak_temperature: float = Field(..., description="Peak temperature in °C")
    endset_temperature: float = Field(..., description="Endset temperature in °C")
    enthalpy: float = Field(..., description="Transition enthalpy in J/g")
    peak_width: float = Field(..., description="Peak width in °C")
    peak_area: float = Field(..., description="Peak area")
    sharpness: float = Field(..., description="Peak sharpness factor")

class ThermalAnalysisResult(BaseModel):
    """Complete thermal analysis results"""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    sample_id: str = Field(..., description="Sample identifier")
    analysis_timestamp: datetime = Field(default_factory=datetime.now, description="Analysis timestamp")

    thermogram: DSCThermogram = Field(..., description="DSC thermogram data")
    transitions: List[ThermalTransition] = Field(default_factory=list, description="Detected thermal transitions")

    # Thermal properties
    glass_transition_temp: Optional[float] = Field(default=None, description="Glass transition temperature in °C")
    melting_point: Optional[float] = Field(default=None, description="Melting point in °C")
    crystallization_temp: Optional[float] = Field(default=None, description="Crystallization temperature in °C")
    decomposition_temp: Optional[float] = Field(default=None, description="Decomposition temperature in °C")

    # Calculated properties
    specific_heat_capacity: Optional[float] = Field(default=None, description="Specific heat capacity in J/g·K")
    thermal_stability: str = Field(default="unknown", description="Thermal stability assessment")
    purity_estimate: Optional[float] = Field(default=None, description="Purity estimate from melting analysis")

    recommendations: str = Field(default="", description="Analysis recommendations")

class KineticsAnalysisResult(BaseModel):
    """Kinetics analysis results"""
    analysis_id: str = Field(..., description="Unique kinetics analysis identifier")
    reaction_type: str = Field(..., description="Type of reaction analyzed")
    activation_energy: float = Field(..., description="Activation energy in kJ/mol")
    pre_exponential_factor: float = Field(..., description="Pre-exponential factor")
    reaction_order: float = Field(..., description="Reaction order")
    temperature_range: Tuple[float, float] = Field(..., description="Temperature range analyzed in °C")
    correlation_coefficient: float = Field(..., description="Correlation coefficient of kinetic analysis")
    confidence_level: float = Field(..., description="Confidence level of results")

class DifferentialScanningCalorimetryService(BaseService):
    """Advanced Differential Scanning Calorimetry Service"""

    def __init__(self):
        super().__init__("differential_scanning_calorimetry")

        # DSC service metadata
        self.description = "Advanced thermal analysis using Differential Scanning Calorimetry"
        self.version = "1.0.0"

        # DSC configuration parameters
        self.temperature_precision = 0.1  # °C
        self.heat_flow_precision = 0.001  # mW
        self.scan_rate_range = (0.1, 100.0)  # °C/min
        self.max_temperature = 800.0  # °C

        # Analysis parameters
        self.baseline_polynomial_order = 3
        self.peak_detection_threshold = 0.05  # mW
        self.minimum_peak_width = 2.0  # °C

        logger.info(f"Initialized {self.name} v{self.version}")

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process generic DSC analysis request (required by BaseService)"""
        # This method is required by the BaseService abstract class
        # In practice, use specific methods like perform_complete_analysis()
        request_type = request_data.get("type", "complete_analysis")

        if request_type == "complete_analysis":
            result = await self.perform_complete_analysis(
                sample_id=request_data["sample_id"],
                sample_mass=request_data["sample_mass"],
                heating_rate=request_data["heating_rate"],
                temperature_range=request_data["temperature_range"],
                atmosphere=request_data.get("atmosphere", "nitrogen")
            )
            return result.dict()
        else:
            raise ValueError(f"Unsupported request type: {request_type}")

    async def acquire_thermogram(
        self,
        sample_id: str,
        sample_mass: float,
        heating_rate: float,
        temperature_range: Tuple[float, float],
        atmosphere: str = "nitrogen",
        reference_material: Optional[str] = None,
        simulate: bool = True
    ) -> DSCThermogram:
        """
        Acquire DSC thermogram data.

        Args:
            sample_id: Unique sample identifier
            sample_mass: Sample mass in mg
            heating_rate: Heating rate in °C/min
            temperature_range: Temperature range (min, max) in °C
            atmosphere: Measurement atmosphere
            reference_material: Reference material
            simulate: Whether to simulate data or use real instrument

        Returns:
            DSCThermogram with measurement data
        """
        try:
            # Validate parameters
            if not (self.scan_rate_range[0] <= heating_rate <= self.scan_rate_range[1]):
                raise ValueError(f"Heating rate must be between {self.scan_rate_range[0]} and {self.scan_rate_range[1]} °C/min")

            if temperature_range[1] > self.max_temperature:
                raise ValueError(f"Maximum temperature cannot exceed {self.max_temperature}°C")

            if sample_mass <= 0:
                raise ValueError("Sample mass must be positive")

            # Generate thermogram data
            if simulate:
                temperature_data, heat_flow_data = self._simulate_thermogram(
                    temperature_range, heating_rate, sample_mass
                )
            else:
                # In real implementation, this would interface with DSC instrument
                temperature_data, heat_flow_data = self._acquire_real_data()

            # Create thermogram
            thermogram = DSCThermogram(
                thermogram_id=f"dsc_{sample_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                sample_mass=sample_mass,
                heating_rate=heating_rate,
                temperature_range=temperature_range,
                atmosphere=atmosphere,
                reference_material=reference_material,
                temperature_data=temperature_data,
                heat_flow_data=heat_flow_data,
                baseline_corrected=False,
                metadata={
                    "acquisition_timestamp": datetime.now().isoformat(),
                    "instrument_model": "DSC_SIM_v1.0",
                    "calibration_date": "2024-01-01",
                    "operator": "AXIOM_AUTO"
                }
            )

            logger.info(f"Acquired thermogram {thermogram.thermogram_id} for sample {sample_id}")
            return thermogram

        except ChemistryError as e:
            logger.error(f"Error acquiring thermogram: {e}")
            raise

    def _simulate_thermogram(
        self,
        temperature_range: Tuple[float, float],
        heating_rate: float,
        sample_mass: float
    ) -> Tuple[List[float], List[float]]:
        """Simulate realistic DSC thermogram with multiple thermal events"""

        temp_min, temp_max = temperature_range
        n_points = int((temp_max - temp_min) / (heating_rate / 60)) + 1

        temperatures = np.linspace(temp_min, temp_max, n_points)
        heat_flow = np.zeros(n_points)

        # Base heat capacity (temperature dependent)
        base_cp = 0.5 + 0.001 * temperatures  # J/g·K
        baseline = base_cp * heating_rate / 60  # Convert to mW

        # Add thermal events
        events = [
            {"type": "glass_transition", "temp": 80, "width": 15, "intensity": 0.2},
            {"type": "melting", "temp": 165, "width": 8, "intensity": -1.5},
            {"type": "crystallization", "temp": 220, "width": 12, "intensity": 0.8},
            {"type": "decomposition", "temp": 350, "width": 25, "intensity": -2.0}
        ]

        for event in events:
            if temp_min <= event["temp"] <= temp_max:
                gaussian_peak = event["intensity"] * np.exp(
                    -0.5 * ((temperatures - event["temp"]) / (event["width"] / 4))**2
                )
                heat_flow += gaussian_peak

        # Scale by sample mass
        heat_flow = (baseline + heat_flow) * sample_mass

        # Add realistic noise
        noise_level = 0.01  # mW
        noise = np.random.normal(0, noise_level, len(heat_flow))
        heat_flow += noise

        return temperatures.tolist(), heat_flow.tolist()

    def _acquire_real_data(self) -> Tuple[List[float], List[float]]:
        """Placeholder for real DSC data acquisition"""
        # This would interface with actual DSC instrument
        raise NotImplementedError("Real DSC data acquisition not implemented")

    async def analyze_thermal_transitions(
        self,
        thermogram: DSCThermogram,
        apply_baseline_correction: bool = True
    ) -> List[ThermalTransition]:
        """
        Analyze thermogram to detect and characterize thermal transitions.

        Args:
            thermogram: DSC thermogram data
            apply_baseline_correction: Whether to apply baseline correction

        Returns:
            List of detected thermal transitions
        """
        try:
            temps = np.array(thermogram.temperature_data)
            heat_flow = np.array(thermogram.heat_flow_data)

            # Apply baseline correction if requested
            if apply_baseline_correction:
                corrected_signal = self._apply_baseline_correction(temps, heat_flow)
            else:
                corrected_signal = heat_flow

            # Detect thermal transitions
            transitions = self._detect_thermal_transitions(temps, corrected_signal)

            logger.info(f"Detected {len(transitions)} thermal transitions in {thermogram.thermogram_id}")
            return transitions

        except ChemistryError as e:
            logger.error(f"Error analyzing thermal transitions: {e}")
            raise

    def _apply_baseline_correction(self, temperatures: np.ndarray, heat_flow: np.ndarray) -> np.ndarray:
        """Apply polynomial baseline correction"""

        # Identify baseline regions (typically first and last 10% of data)
        n_points = len(temperatures)
        baseline_mask = np.zeros(n_points, dtype=bool)
        baseline_mask[:int(0.1 * n_points)] = True
        baseline_mask[int(0.9 * n_points):] = True

        # Fit polynomial to baseline regions
        baseline_temps = temperatures[baseline_mask]
        baseline_values = heat_flow[baseline_mask]

        baseline_coeffs = np.polyfit(baseline_temps, baseline_values, self.baseline_polynomial_order)
        baseline_fit = np.polyval(baseline_coeffs, temperatures)

        return heat_flow - baseline_fit

    def _detect_thermal_transitions(
        self,
        temps: np.ndarray,
        signal: np.ndarray
    ) -> List[ThermalTransition]:
        """Detect and characterize thermal transitions"""

        transitions = []

        # Smooth signal for peak detection
        window_size = min(21, len(signal) // 10)
        if window_size % 2 == 0:
            window_size += 1

        try:
            from scipy.signal import savgol_filter
            smoothed_signal = savgol_filter(signal, window_size, 3)
        except ImportError:
            # Fallback to simple moving average if scipy not available
            smoothed_signal = np.convolve(signal, np.ones(5)/5, mode='same')

        # Find peaks using derivative analysis
        # Note: first_deriv could be used for more advanced peak detection
        # first_deriv = np.gradient(smoothed_signal)

        # Detect peaks (local maxima and minima)
        for i in range(1, len(signal) - 1):
            # Check for significant peaks
            if abs(smoothed_signal[i]) > self.peak_detection_threshold:
                # Check if it's a local extremum
                is_maximum = (smoothed_signal[i] > smoothed_signal[i-1] and
                             smoothed_signal[i] > smoothed_signal[i+1])
                is_minimum = (smoothed_signal[i] < smoothed_signal[i-1] and
                             smoothed_signal[i] < smoothed_signal[i+1])

                if is_maximum or is_minimum:
                    peak_temp = temps[i]

                    # Find onset and endset temperatures
                    onset_temp = self._find_onset_temperature(temps, smoothed_signal, i)
                    endset_temp = self._find_endset_temperature(temps, smoothed_signal, i)

                    # Calculate peak characteristics
                    if abs(endset_temp - onset_temp) >= self.minimum_peak_width:
                        # Calculate enthalpy (area under peak)
                        start_idx = np.argmin(np.abs(temps - onset_temp))
                        end_idx = np.argmin(np.abs(temps - endset_temp))
                        enthalpy = float(np.trapz(smoothed_signal[start_idx:end_idx+1], temps[start_idx:end_idx+1]))

                        # Determine transition type
                        transition_type = self._classify_transition(
                            peak_temp, float(smoothed_signal[i]), enthalpy
                        )

                        # Peak characteristics
                        peak_width = endset_temp - onset_temp
                        peak_area = abs(enthalpy)
                        sharpness = abs(smoothed_signal[i]) / peak_width if peak_width > 0 else 0

                        transition = ThermalTransition(
                            transition_id=f"peak_{len(transitions)+1}",
                            transition_type=transition_type,
                            onset_temperature=onset_temp,
                            peak_temperature=peak_temp,
                            endset_temperature=endset_temp,
                            enthalpy=enthalpy,
                            peak_width=peak_width,
                            peak_area=peak_area,
                            sharpness=sharpness
                        )

                        transitions.append(transition)

        return transitions

    def _find_onset_temperature(
        self,
        temperatures: np.ndarray,
        signal: np.ndarray,
        peak_idx: int
    ) -> float:
        """Find onset temperature using tangent intersection method"""

        # Look backward from peak to find onset
        onset_idx = next(
            (i for i in range(peak_idx, max(0, peak_idx - 50), -1)
             if abs(signal[i]) < abs(signal[peak_idx]) * 0.1),
            max(0, peak_idx - 20)
        )

        return temperatures[onset_idx]

    def _find_endset_temperature(
        self,
        temperatures: np.ndarray,
        signal: np.ndarray,
        peak_idx: int
    ) -> float:
        """Find endset temperature using tangent intersection method"""

        # Look forward from peak to find endset
        endset_idx = next(
            (i for i in range(peak_idx, min(len(signal), peak_idx + 50))
             if abs(signal[i]) < abs(signal[peak_idx]) * 0.1),
            min(len(signal) - 1, peak_idx + 20)
        )

        return temperatures[endset_idx]

    def _classify_transition(
        self,
        temperature: float,
        signal_intensity: float,
        enthalpy: float
    ) -> str:
        """Classify type of thermal transition"""

        if enthalpy > 0:  # Endothermic
            if temperature < 100:
                return "glass_transition"
            elif 100 <= temperature < 400:
                return "melting"
            else:
                return "decomposition"
        # Exothermic
        elif temperature < 200:
            return "crystallization"
        elif 200 <= temperature < 400:
            return "solid_state_transition"
        else:
            return "oxidation"

    async def perform_complete_analysis(
        self,
        sample_id: str,
        sample_mass: float,
        heating_rate: float,
        temperature_range: Tuple[float, float],
        atmosphere: str = "nitrogen"
    ) -> ThermalAnalysisResult:
        """
        Perform complete DSC analysis including thermogram acquisition and transition analysis.

        Args:
            sample_id: Unique sample identifier
            sample_mass: Sample mass in mg
            heating_rate: Heating rate in °C/min
            temperature_range: Temperature range (min, max) in °C
            atmosphere: Measurement atmosphere

        Returns:
            Complete thermal analysis results
        """
        try:
            # Acquire thermogram
            thermogram = await self.acquire_thermogram(
                sample_id, sample_mass, heating_rate, temperature_range, atmosphere
            )

            # Analyze transitions
            transitions = await self.analyze_thermal_transitions(thermogram)

            # Extract key thermal properties
            glass_transition_temp = None
            melting_point = None
            crystallization_temp = None
            decomposition_temp = None

            for transition in transitions:
                if transition.transition_type == "glass_transition":
                    glass_transition_temp = transition.peak_temperature
                elif transition.transition_type == "melting":
                    melting_point = transition.peak_temperature
                elif transition.transition_type == "crystallization":
                    crystallization_temp = transition.peak_temperature
                elif transition.transition_type == "decomposition":
                    decomposition_temp = transition.peak_temperature

            # Calculate specific heat capacity (simplified)
            specific_heat_capacity = self._calculate_specific_heat_capacity(
                thermogram.heat_flow_data, thermogram.sample_mass, heating_rate
            )

            # Assess thermal stability
            thermal_stability = self._assess_thermal_stability(transitions, temperature_range[1])

            # Estimate purity from melting analysis
            purity_estimate = self._estimate_purity(transitions)

            # Generate recommendations
            recommendations = self._generate_recommendations(transitions, thermal_stability)

            # Create complete analysis result
            result = ThermalAnalysisResult(
                analysis_id=f"dsc_analysis_{sample_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                sample_id=sample_id,
                thermogram=thermogram,
                transitions=transitions,
                glass_transition_temp=glass_transition_temp,
                melting_point=melting_point,
                crystallization_temp=crystallization_temp,
                decomposition_temp=decomposition_temp,
                specific_heat_capacity=specific_heat_capacity,
                thermal_stability=thermal_stability,
                purity_estimate=purity_estimate,
                recommendations=recommendations
            )

            logger.info(f"Completed DSC analysis for sample {sample_id}")
            return result

        except ChemistryError as e:
            logger.error(f"Error in complete DSC analysis: {e}")
            raise

    def _calculate_specific_heat_capacity(
        self,
        heat_flow_data: List[float],
        sample_mass: float,
        heating_rate: float
    ) -> float:
        """Calculate average specific heat capacity"""

        # Simplified calculation: Cp = heat_flow / (mass * heating_rate)
        avg_heat_flow = np.mean(heat_flow_data)  # mW
        heating_rate_per_sec = heating_rate / 60  # °C/s

        # Convert to J/g·K
        cp = (avg_heat_flow / 1000) / (sample_mass / 1000 * heating_rate_per_sec)

        return float(abs(cp))  # Return absolute value

    def _assess_thermal_stability(
        self,
        transitions: List[ThermalTransition],
        max_temperature: float
    ) -> str:
        """Assess overall thermal stability of the material"""

        decomp_transitions = [t for t in transitions if t.transition_type == "decomposition"]

        if not decomp_transitions:
            if max_temperature > 400:
                return "excellent"
            else:
                return "good"

        min_decomp_temp = min(t.onset_temperature for t in decomp_transitions)

        if min_decomp_temp > 400:
            return "excellent"
        elif min_decomp_temp > 250:
            return "good"
        elif min_decomp_temp > 150:
            return "moderate"
        else:
            return "poor"

    def _estimate_purity(self, transitions: List[ThermalTransition]) -> Optional[float]:
        """Estimate sample purity based on melting behavior"""

        melting_transitions = [t for t in transitions if t.transition_type == "melting"]

        if not melting_transitions:
            return None

        # Use peak sharpness as purity indicator
        # Sharp, narrow peaks indicate higher purity
        primary_melting = max(melting_transitions, key=lambda t: abs(t.enthalpy))

        # Simplified purity estimation (0-100%)
        if primary_melting.sharpness > 0.5:
            purity = min(99.0, 85 + primary_melting.sharpness * 20)
        elif primary_melting.sharpness > 0.2:
            purity = 70 + primary_melting.sharpness * 60
        else:
            purity = 50 + primary_melting.sharpness * 100

        return round(purity, 1)

    def _generate_recommendations(
        self,
        transitions: List[ThermalTransition],
        thermal_stability: str
    ) -> str:
        """Generate analysis recommendations based on results"""

        recommendations = []

        # Processing temperature recommendations
        melting_temps = [t.peak_temperature for t in transitions if t.transition_type == "melting"]
        if melting_temps:
            max_melting = max(melting_temps)
            recommendations.append(f"Processing temperature should not exceed {max_melting - 10}°C")

        # Thermal stability recommendations
        if thermal_stability == "poor":
            recommendations.append("Material has poor thermal stability - use low processing temperatures")
        elif thermal_stability == "excellent":
            recommendations.append("Excellent thermal stability - suitable for high-temperature applications")

        # Glass transition recommendations
        tg_temps = [t.peak_temperature for t in transitions if t.transition_type == "glass_transition"]
        if tg_temps:
            recommendations.append(f"Glass transition at {tg_temps[0]:.1f}°C - consider for storage conditions")

        return "; ".join(recommendations)

    async def perform_kinetics_analysis(
        self,
        heating_rates: List[float],
        peak_temps: List[float],
        reaction_type: str = "decomposition"
    ) -> KineticsAnalysisResult:
        """
        Perform kinetic analysis using multiple heating rates.

        Args:
            heating_rates: List of heating rates in °C/min
            peak_temps: Corresponding peak temperatures in °C
            reaction_type: Type of reaction being analyzed

        Returns:
            Kinetics analysis results with activation energy and reaction order
        """
        try:
            if len(heating_rates) != len(peak_temps):
                raise ValueError("Heating rates and peak temperatures must have same length")

            if len(heating_rates) < 3:
                raise ValueError("At least 3 data points required for kinetic analysis")

            # Perform Kissinger analysis for activation energy
            activation_energy, pre_exp_factor, correlation = self._kissinger_analysis(
                heating_rates, peak_temps
            )

            # Determine reaction order using Ozawa method
            reaction_order = self._ozawa_analysis(heating_rates, peak_temps)

            # Calculate confidence level based on correlation
            if abs(correlation[0]) > 0.95:
                confidence = 95.0
            elif abs(correlation[0]) > 0.90:
                confidence = 90.0
            elif abs(correlation[0]) > 0.85:
                confidence = 85.0
            else:
                confidence = 75.0

            result = KineticsAnalysisResult(
                analysis_id=f"kinetics_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                reaction_type=reaction_type,
                activation_energy=activation_energy,
                pre_exponential_factor=pre_exp_factor,
                reaction_order=reaction_order,
                temperature_range=(min(peak_temps), max(peak_temps)),
                correlation_coefficient=correlation[0],
                confidence_level=confidence
            )

            logger.info(f"Completed kinetics analysis: Ea = {activation_energy:.1f} kJ/mol")
            return result

        except ChemistryError as e:
            logger.error(f"Error in kinetics analysis: {e}")
            raise

    def _kissinger_analysis(
        self,
        heating_rates: List[float],
        peak_temps: List[float]
    ) -> Tuple[float, float, Tuple[float, float]]:
        """Perform Kissinger analysis to determine activation energy"""

        # Kissinger equation: ln(β/T²) = ln(AR/E) - E/RT
        # where β = heating rate, T = peak temperature, E = activation energy

        heating_rates_arr = np.array(heating_rates)
        peak_temps_arr = np.array(peak_temps) + 273.15  # Convert to Kelvin

        # Calculate ln(β/T²)
        y = np.log(heating_rates_arr / (peak_temps_arr ** 2))

        # Calculate 1/T
        x = 1 / peak_temps_arr

        # Linear regression
        coefficients = np.polyfit(x, y, 1)
        slope, intercept = coefficients

        # Calculate activation energy (slope = -E/R)
        R = 8.314  # J/mol·K
        activation_energy = -slope * R / 1000  # Convert to kJ/mol

        # Calculate pre-exponential factor
        pre_exp_factor = np.exp(intercept) * R / activation_energy

        # Calculate correlation coefficient
        correlation = np.corrcoef(x, y)

        return activation_energy, pre_exp_factor, (correlation[0], correlation[1])

    def _ozawa_analysis(
        self,
        heating_rates: List[float],
        peak_temps: List[float]
    ) -> float:
        """Determine reaction order using Ozawa method"""

        # Simplified reaction order estimation
        # Based on the relationship between heating rate and peak temperature

        heating_rates_arr = np.array(heating_rates)
        peak_temps_arr = np.array(peak_temps)

        # Calculate correlation between ln(β) and Tp
        correlation = np.corrcoef(np.log(heating_rates_arr), peak_temps_arr)[0, 1]

        # Estimate reaction order based on correlation
        if correlation > 0.95:
            return 1.0  # First order
        elif correlation > 0.85:
            return 1.5  # Mixed order
        else:
            return 2.0  # Second order

    def _calculate_rate_constants(
        self,
        temperatures: List[float],
        activation_energy: float,
        pre_exp_factor: float
    ) -> List[float]:
        """Calculate rate constants using Arrhenius equation"""

        R = 8.314  # J/mol·K
        temps_kelvin = [t + 273.15 for t in temperatures]

        rate_constants = []
        for temp in temps_kelvin:
            k = pre_exp_factor * np.exp(-activation_energy * 1000 / (R * temp))
            rate_constants.append(k)

        return rate_constants

    async def generate_processing_recommendations(
        self,
        analysis_result: ThermalAnalysisResult,
        application: str = "general"
    ) -> Dict[str, Any]:
        """
        Generate processing and application recommendations based on DSC analysis.

        Args:
            analysis_result: Complete thermal analysis results
            application: Intended application (e.g., 'polymer_processing', 'pharmaceutical')

        Returns:
            Dictionary with processing recommendations
        """
        try:
            recommendations = {
                "processing_conditions": {},
                "storage_conditions": {},
                "quality_control": {},
                "applications": [],
                "limitations": []
            }

            # Processing temperature recommendations
            if analysis_result.melting_point:
                recommendations["processing_conditions"]["max_temperature"] = analysis_result.melting_point - 20
                recommendations["processing_conditions"]["optimal_range"] = (
                    analysis_result.melting_point - 50,
                    analysis_result.melting_point - 10
                )

            # Storage recommendations
            if analysis_result.glass_transition_temp:
                recommendations["storage_conditions"]["max_storage_temp"] = analysis_result.glass_transition_temp - 10
                recommendations["storage_conditions"]["humidity_control"] = "required"

            # Quality control parameters
            recommendations["quality_control"]["critical_temperatures"] = [
                t.peak_temperature for t in analysis_result.transitions
            ]

            if analysis_result.purity_estimate:
                recommendations["quality_control"]["purity_specification"] = f"≥{analysis_result.purity_estimate}%"

            # Application-specific recommendations
            if application == "polymer_processing":
                recommendations.update(self._polymer_processing_recommendations(analysis_result))
            elif application == "pharmaceutical":
                recommendations.update(self._pharmaceutical_recommendations(analysis_result))

            # Thermal stability assessment
            stability_map = {
                "excellent": "Suitable for high-temperature applications",
                "good": "Good thermal stability for most applications",
                "moderate": "Limited thermal stability - avoid high temperatures",
                "poor": "Poor thermal stability - requires careful temperature control"
            }

            recommendations["thermal_stability_note"] = stability_map.get(
                analysis_result.thermal_stability, "Unknown stability"
            )

            logger.info(f"Generated processing recommendations for {analysis_result.sample_id}")
            return recommendations

        except ChemistryError as e:
            logger.error(f"Error generating recommendations: {e}")
            raise

    def _polymer_processing_recommendations(self, result: ThermalAnalysisResult) -> Dict[str, Any]:
        """Generate polymer-specific processing recommendations"""

        polymer_recs = {
            "injection_molding": {},
            "extrusion": {},
            "thermoforming": {}
        }

        if result.melting_point:
            polymer_recs["injection_molding"]["barrel_temp"] = result.melting_point + 30
            polymer_recs["injection_molding"]["mold_temp"] = result.melting_point - 80

            polymer_recs["extrusion"]["barrel_temp"] = result.melting_point + 20
            polymer_recs["extrusion"]["die_temp"] = result.melting_point + 10

        if result.glass_transition_temp:
            polymer_recs["thermoforming"]["forming_temp"] = result.glass_transition_temp + 50

        return {"polymer_processing": polymer_recs}

    def _pharmaceutical_recommendations(self, result: ThermalAnalysisResult) -> Dict[str, Any]:
        """Generate pharmaceutical-specific recommendations"""

        pharma_recs = {
            "tablet_compression": {},
            "powder_handling": {},
            "stability_testing": {}
        }

        decomp_transitions = [t for t in result.transitions if t.transition_type == "decomposition"]
        if decomp_transitions:
            min_decomp = min(t.onset_temperature for t in decomp_transitions)
            pharma_recs["tablet_compression"]["max_temp"] = min_decomp - 30
            pharma_recs["stability_testing"]["stress_temp"] = min_decomp - 20

        if result.purity_estimate and result.purity_estimate < 98:
            pharma_recs["quality_control"] = {"purity_note": "Purity below pharmaceutical grade - purification required"}

        return {"pharmaceutical": pharma_recs}

    async def predict_thermal_behavior(
        self,
        material_properties: Dict[str, Any],
        temperature_profile: List[Tuple[float, float]]  # (temperature, time) pairs
    ) -> Dict[str, Any]:
        """
        Predict thermal behavior under specific temperature profiles.

        Args:
            material_properties: Known thermal properties of material
            temperature_profile: List of (temperature, time) tuples

        Returns:
            Predicted thermal behavior and reactions
        """
        try:
            predictions = {
                "temperature_profile": temperature_profile,
                "predicted_reactions": [],
                "degradation_risk": "low",
                "recommended_modifications": []
            }

            # Extract material properties
            activation_energy = material_properties.get("activation_energy", 150)  # kJ/mol
            decomposition_temp = material_properties.get("decomposition_temp", 300)  # °C

            # Analyze temperature profile
            max_temp = max(temp for temp, time in temperature_profile)
            total_time = sum(time for temp, time in temperature_profile)

            # Predict reactions at each temperature step
            for temp, time_at_temp in temperature_profile:
                if temp > decomposition_temp * 0.8:  # 80% of decomposition temperature
                    reaction_rate = self._calculate_reaction_rate(temp, activation_energy)
                    extent_of_reaction = reaction_rate * time_at_temp * 60  # Convert time to seconds

                    if extent_of_reaction > 0.1:  # Significant reaction
                        predictions["predicted_reactions"].append({
                            "temperature": temp,
                            "time": time_at_temp,
                            "reaction_extent": min(1.0, extent_of_reaction),
                            "reaction_type": self._classify_reaction_by_temp(temp, decomposition_temp)
                        })

            # Assess degradation risk
            if max_temp > decomposition_temp:
                predictions["degradation_risk"] = "high"
                predictions["recommended_modifications"].append("Reduce maximum temperature")
            elif max_temp > decomposition_temp * 0.9:
                predictions["degradation_risk"] = "moderate"
                predictions["recommended_modifications"].append("Monitor for degradation products")

            # Time-temperature recommendations
            if total_time > 60 and max_temp > decomposition_temp * 0.7:  # Long exposure
                predictions["recommended_modifications"].append("Reduce exposure time at high temperature")

            logger.info("Generated thermal behavior predictions")
            return predictions

        except ChemistryError as e:
            logger.error(f"Error predicting thermal behavior: {e}")
            raise

    def _calculate_reaction_rate(self, temperature: float, activation_energy: float) -> float:
        """Calculate reaction rate using Arrhenius equation"""

        R = 8.314  # J/mol·K
        temp_kelvin = temperature + 273.15
        pre_exp_factor = 1e10  # Assumed pre-exponential factor

        rate = pre_exp_factor * np.exp(-activation_energy * 1000 / (R * temp_kelvin))
        return rate

    def _classify_reaction_by_temp(self, temperature: float, decomposition_temp: float) -> str:
        """Classify reaction type based on temperature"""

        if temperature < decomposition_temp * 0.8:
            return "mild_degradation"
        elif temperature < decomposition_temp:
            return "thermal_degradation"
        else:
            return "severe_decomposition"

    async def comparative_analysis(
        self,
        results_list: List[ThermalAnalysisResult],
        comparison_criteria: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare multiple DSC analysis results.

        Args:
            results_list: List of thermal analysis results to compare
            comparison_criteria: Specific properties to compare

        Returns:
            Comparative analysis results
        """
        try:
            if not results_list:
                raise ValueError("At least one result required for comparison")

            if comparison_criteria is None:
                comparison_criteria = [
                    "melting_point", "glass_transition_temp", "thermal_stability",
                    "purity_estimate", "specific_heat_capacity"
                ]

            comparison = {
                "sample_ids": [r.sample_id for r in results_list],
                "comparison_summary": {},
                "ranking": {},
                "statistical_analysis": {}
            }

            # Compare each criterion
            for criterion in comparison_criteria:
                values = []
                sample_mapping = {}

                for result in results_list:
                    value = getattr(result, criterion, None)
                    if value is not None:
                        values.append(value)
                        sample_mapping[result.sample_id] = value

                if values:
                    if isinstance(values[0], (int, float)):
                        # Numerical comparison
                        comparison["comparison_summary"][criterion] = {
                            "min": min(values),
                            "max": max(values),
                            "mean": np.mean(values),
                            "std": np.std(values),
                            "sample_values": sample_mapping
                        }

                        # Ranking (higher is better for most properties)
                        sorted_samples = sorted(sample_mapping.items(), key=lambda x: x[1], reverse=True)
                        comparison["ranking"][criterion] = [sample for sample, value in sorted_samples]

                    else:
                        # Categorical comparison
                        from collections import Counter
                        value_counts = Counter(values)
                        comparison["comparison_summary"][criterion] = {
                            "distribution": dict(value_counts),
                            "sample_values": sample_mapping
                        }

            # Overall quality ranking
            comparison["overall_ranking"] = self._calculate_overall_ranking(results_list)

            logger.info(f"Completed comparative analysis of {len(results_list)} samples")
            return comparison

        except ChemistryError as e:
            logger.error(f"Error in comparative analysis: {e}")
            raise

    def _calculate_overall_ranking(self, results_list: List[ThermalAnalysisResult]) -> List[str]:
        """Calculate overall quality ranking based on multiple criteria"""

        scores = {}

        for result in results_list:
            score = 0

            # Thermal stability scoring
            stability_scores = {"excellent": 4, "good": 3, "moderate": 2, "poor": 1}
            score += stability_scores.get(result.thermal_stability, 0)

            # Purity scoring
            if result.purity_estimate:
                score += result.purity_estimate / 25  # Max 4 points for 100% purity

            # Temperature range scoring (higher melting/decomposition is often better)
            if result.decomposition_temp:
                score += min(4, result.decomposition_temp / 100)

            scores[result.sample_id] = score

        # Sort by score (descending)
        ranked_samples = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [sample for sample, score in ranked_samples]

    async def export_results(
        self,
        results: ThermalAnalysisResult,
        export_format: str = "json",
        include_raw_data: bool = True
    ) -> str:
        """
        Export analysis results in specified format.

        Args:
            results: Analysis results to export
            export_format: Export format ('json', 'csv', 'excel')
            include_raw_data: Whether to include raw thermogram data

        Returns:
            Exported data as string or file path
        """
        try:
            if export_format == "json":
                if not include_raw_data:
                    # Create copy without raw data
                    export_data = results.dict()
                    export_data["thermogram"]["temperature_data"] = f"[{len(results.thermogram.temperature_data)} data points]"
                    export_data["thermogram"]["heat_flow_data"] = f"[{len(results.thermogram.heat_flow_data)} data points]"
                else:
                    export_data = results.dict()

                import json
                return json.dumps(export_data, indent=2, default=str)

            elif export_format == "csv":
                # Create CSV with key results
                import io
                output = io.StringIO()

                # Header
                output.write("Parameter,Value,Unit\n")

                # Key parameters
                if results.melting_point:
                    output.write(f"Melting Point,{results.melting_point},°C\n")
                if results.glass_transition_temp:
                    output.write(f"Glass Transition,{results.glass_transition_temp},°C\n")
                if results.decomposition_temp:
                    output.write(f"Decomposition Temp,{results.decomposition_temp},°C\n")
                if results.specific_heat_capacity:
                    output.write(f"Specific Heat Capacity,{results.specific_heat_capacity},J/g·K\n")
                if results.purity_estimate:
                    output.write(f"Purity Estimate,{results.purity_estimate},%\n")

                output.write(f"Thermal Stability,{results.thermal_stability},-\n")

                # Transitions
                for i, transition in enumerate(results.transitions, 1):
                    output.write(f"Transition {i} Type,{transition.transition_type},-\n")
                    output.write(f"Transition {i} Onset,{transition.onset_temperature},°C\n")
                    output.write(f"Transition {i} Peak,{transition.peak_temperature},°C\n")
                    output.write(f"Transition {i} Enthalpy,{transition.enthalpy},J/g\n")

                return output.getvalue()

            else:
                raise ValueError(f"Unsupported export format: {export_format}")

        except ChemistryError as e:
            logger.error(f"Error exporting results: {e}")
            raise
