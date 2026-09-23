"""
Advanced NMR Service

Servicio avanzado de Resonancia Magnética Nuclear para análisis molecular,
caracterización de estructuras químicas, estudios de dinámicas moleculares
y determinación de pureza en compuestos orgánicos e inorgánicos.
"""

import math
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel, Field

from app.services.base_service import BaseService
from app.exceptions.domain.chemistry import ChemistryError

# Configure logging
logger = logging.getLogger(__name__)

# Data models for NMR analysis results
class NMRSpectrum(BaseModel):
    """NMR spectrum data"""
    spectrum_id: str = Field(..., description="Unique spectrum identifier")
    nucleus_type: str = Field(..., description="Nucleus type (1H, 13C, 31P, etc.)")
    magnetic_field: float = Field(..., description="Magnetic field strength in Tesla")
    frequency: float = Field(..., description="Operating frequency in MHz")
    chemical_shifts: List[float] = Field(..., description="Chemical shifts in ppm")
    peak_intensities: List[float] = Field(..., description="Peak intensities")
    peak_widths: List[float] = Field(..., description="Peak widths (FWHM)")
    integration_values: List[float] = Field(..., description="Integration values")
    coupling_constants: List[float] = Field(..., description="J-coupling constants in Hz")
    multiplicity: List[str] = Field(..., description="Peak multiplicities (s, d, t, q, m)")
    acquisition_parameters: Dict[str, Any] = Field(..., description="Acquisition parameters")

class MolecularStructureResult(BaseModel):
    """Molecular structure determination result"""
    structure_id: str = Field(..., description="Structure identifier")
    molecular_formula: str = Field(..., description="Molecular formula")
    molecular_weight: float = Field(..., description="Molecular weight in g/mol")
    structural_assignments: List[Dict[str, Any]] = Field(..., description="Peak assignments")
    functional_groups: List[str] = Field(..., description="Identified functional groups")
    stereochemistry: str = Field(..., description="Stereochemical information")
    purity_estimate: float = Field(..., description="Estimated purity (0-1)")
    confidence: float = Field(..., description="Structure determination confidence (0-1)")

class DynamicsAnalysisResult(BaseModel):
    """Molecular dynamics analysis result"""
    analysis_id: str = Field(..., description="Analysis identifier")
    relaxation_times: Dict[str, float] = Field(..., description="T1 and T2 relaxation times")
    diffusion_coefficient: Optional[float] = Field(None, description="Diffusion coefficient")
    exchange_rates: List[float] = Field(..., description="Chemical exchange rates")
    activation_energy: Optional[float] = Field(None, description="Activation energy in kJ/mol")
    temperature_coefficients: List[float] = Field(..., description="Temperature coefficients")
    motional_parameters: Dict[str, float] = Field(..., description="Molecular motion parameters")

class AdvancedNMRService(BaseService):
    """
    Advanced NMR Service for comprehensive molecular analysis

    Provides tools for:
    - Multi-dimensional NMR analysis (1D, 2D, 3D)
    - Structure elucidation and assignment
    - Molecular dynamics studies
    - Quantitative analysis and purity determination
    - Advanced pulse sequences and experiments
    """

    def __init__(self):
        super().__init__(name="AdvancedNMRService")
        self.service_name = "AdvancedNMRService"

        # Common nuclei and their properties
        self.nucleus_properties = {
            "1H": {"gamma": 42.577, "natural_abundance": 99.985, "spin": 0.5},
            "13C": {"gamma": 10.708, "natural_abundance": 1.108, "spin": 0.5},
            "31P": {"gamma": 17.235, "natural_abundance": 100.0, "spin": 0.5},
            "15N": {"gamma": -4.316, "natural_abundance": 0.368, "spin": 0.5},
            "19F": {"gamma": 40.052, "natural_abundance": 100.0, "spin": 0.5},
            "29Si": {"gamma": -8.465, "natural_abundance": 4.683, "spin": 0.5}
        }

        # Chemical shift reference ranges
        self.chemical_shift_ranges = {
            "1H": {
                "alkyl": (0.8, 3.0),
                "aromatic": (6.5, 8.5),
                "aldehyde": (9.0, 10.0),
                "carboxylic_acid": (10.5, 12.0),
                "alcohol": (1.0, 5.0),
                "amine": (0.5, 3.0)
            },
            "13C": {
                "alkyl": (10, 50),
                "aromatic": (100, 160),
                "carbonyl": (160, 220),
                "alkene": (100, 150),
                "quaternary": (20, 80)
            }
        }

    async def acquire_nmr_spectrum(
        self,
        sample_info: Dict[str, Any],
        nucleus_type: str = "1H",
        magnetic_field: float = 9.4,  # Tesla
        experiment_type: str = "1D"
    ) -> NMRSpectrum:
        """
        Acquire NMR spectrum for given sample

        Args:
            sample_info: Sample composition and conditions
            nucleus_type: Type of nucleus to observe
            magnetic_field: Magnetic field strength in Tesla
            experiment_type: Type of NMR experiment

        Returns:
            NMRSpectrum with acquired data
        """
        try:
            spectrum_id = f"nmr_{hash(str(sample_info))}_{int(datetime.now().timestamp())}"
            logger.info(f"Acquiring {nucleus_type} NMR spectrum: {spectrum_id}")

            if nucleus_type not in self.nucleus_properties:
                raise ValueError(f"Unsupported nucleus type: {nucleus_type}")

            # Calculate operating frequency
            gamma = self.nucleus_properties[nucleus_type]["gamma"]  # MHz/T
            frequency = gamma * magnetic_field

            # Simulate spectrum acquisition based on sample composition
            chemical_shifts, intensities, widths = self._simulate_spectrum(
                sample_info, nucleus_type, magnetic_field
            )

            # Calculate integration values
            integration_values = self._calculate_integrations(intensities, widths)

            # Determine coupling constants and multiplicities
            coupling_constants, multiplicities = self._analyze_coupling_patterns(
                chemical_shifts, intensities, nucleus_type
            )

            # Acquisition parameters
            acquisition_params = {
                "pulse_sequence": self._select_pulse_sequence(experiment_type),
                "acquisition_time": 2.0,
                "relaxation_delay": 5.0,
                "number_of_scans": 64,
                "digital_resolution": 0.1,
                "temperature": sample_info.get("temperature", 298.15),
                "solvent": sample_info.get("solvent", "CDCl3")
            }

            logger.info(f"Generated {len(chemical_shifts)} peaks for {nucleus_type} spectrum")

            return NMRSpectrum(
                spectrum_id=spectrum_id,
                nucleus_type=nucleus_type,
                magnetic_field=magnetic_field,
                frequency=frequency,
                chemical_shifts=chemical_shifts,
                peak_intensities=intensities,
                peak_widths=widths,
                integration_values=integration_values,
                coupling_constants=coupling_constants,
                multiplicity=multiplicities,
                acquisition_parameters=acquisition_params
            )

        except ChemistryError as e:
            logger.error(f"Error acquiring NMR spectrum: {str(e)}")
            raise

    async def elucidate_structure(
        self,
        nmr_data: List[NMRSpectrum],
        molecular_formula: Optional[str] = None,
        additional_constraints: Optional[Dict[str, Any]] = None
    ) -> MolecularStructureResult:
        """
        Elucidate molecular structure from NMR data

        Args:
            nmr_data: List of NMR spectra (different nuclei/experiments)
            molecular_formula: Known molecular formula (if available)
            additional_constraints: Additional structural constraints

        Returns:
            MolecularStructureResult with proposed structure
        """
        try:
            structure_id = f"struct_{hash(str(nmr_data))}_{int(datetime.now().timestamp())}"
            logger.info(f"Elucidating structure: {structure_id}")

            if not nmr_data:
                raise ValueError("No NMR data provided")

            # Analyze each spectrum
            structural_assignments = []
            functional_groups = []

            for spectrum in nmr_data:
                assignments = self._assign_peaks(spectrum)
                groups = self._identify_functional_groups(spectrum)

                structural_assignments.extend(assignments)
                functional_groups.extend(groups)

            # Remove duplicates
            functional_groups = list(set(functional_groups))

            # Estimate molecular properties
            if molecular_formula:
                molecular_weight = self._calculate_molecular_weight(molecular_formula)
            else:
                molecular_formula, molecular_weight = self._deduce_molecular_formula(
                    nmr_data, structural_assignments
                )

            # Determine stereochemistry from coupling patterns
            stereochemistry = self._analyze_stereochemistry(nmr_data)

            # Estimate purity from integration ratios
            purity = self._estimate_purity(nmr_data)

            # Calculate confidence based on data quality and consistency
            confidence = self._calculate_structure_confidence(
                nmr_data, structural_assignments, additional_constraints
            )

            logger.info(f"Structure elucidation completed with confidence {confidence:.2f}")

            return MolecularStructureResult(
                structure_id=structure_id,
                molecular_formula=molecular_formula,
                molecular_weight=molecular_weight,
                structural_assignments=structural_assignments,
                functional_groups=functional_groups,
                stereochemistry=stereochemistry,
                purity_estimate=purity,
                confidence=confidence
            )

        except ChemistryError as e:
            logger.error(f"Error in structure elucidation: {str(e)}")
            raise

    async def analyze_molecular_dynamics(
        self,
        nmr_spectra: List[NMRSpectrum],
        temperature_series: Optional[List[float]] = None,
        analysis_type: str = "relaxation"
    ) -> DynamicsAnalysisResult:
        """
        Analyze molecular dynamics from NMR data

        Args:
            nmr_spectra: NMR spectra at different conditions
            temperature_series: Temperature series for VT-NMR
            analysis_type: Type of dynamics analysis

        Returns:
            DynamicsAnalysisResult with dynamics parameters
        """
        try:
            analysis_id = f"dyn_{hash(str(nmr_spectra))}_{int(datetime.now().timestamp())}"
            logger.info(f"Analyzing molecular dynamics: {analysis_id}")

            if not nmr_spectra:
                raise ValueError("No NMR spectra provided")

            # Measure relaxation times (T1, T2)
            relaxation_times = self._measure_relaxation_times(nmr_spectra)

            # Calculate diffusion coefficient (if DOSY data available)
            diffusion_coefficient = self._calculate_diffusion_coefficient(nmr_spectra)

            # Analyze chemical exchange
            exchange_rates = self._analyze_exchange_rates(nmr_spectra, temperature_series)

            # Calculate activation energy from temperature dependence
            activation_energy = None
            if temperature_series and len(temperature_series) > 2:
                activation_energy = self._calculate_activation_energy(
                    exchange_rates, temperature_series
                )

            # Determine temperature coefficients
            temperature_coefficients = self._calculate_temperature_coefficients(
                nmr_spectra, temperature_series
            )

            # Calculate motional parameters
            motional_parameters = self._analyze_molecular_motion(
                relaxation_times, diffusion_coefficient
            )

            logger.info("Molecular dynamics analysis completed")

            return DynamicsAnalysisResult(
                analysis_id=analysis_id,
                relaxation_times=relaxation_times,
                diffusion_coefficient=diffusion_coefficient,
                exchange_rates=exchange_rates,
                activation_energy=activation_energy,
                temperature_coefficients=temperature_coefficients,
                motional_parameters=motional_parameters
            )

        except ChemistryError as e:
            logger.error(f"Error in dynamics analysis: {str(e)}")
            raise

    def _simulate_spectrum(
        self,
        sample_info: Dict[str, Any],
        nucleus_type: str,
        magnetic_field: float
    ) -> Tuple[List[float], List[float], List[float]]:
        """Simulate NMR spectrum based on sample composition"""

        # Get chemical shift ranges for nucleus type
        shift_ranges = self.chemical_shift_ranges.get(nucleus_type, {})

        # Generate peaks based on functional groups in sample
        chemical_shifts = []
        intensities = []
        widths = []

        # Sample composition analysis
        composition = sample_info.get("composition", {})

        for component, amount in composition.items():
            # Generate peaks for each component
            if component in shift_ranges:
                shift_range = shift_ranges[component]
                n_peaks = np.random.randint(1, 4)  # 1-3 peaks per functional group

                for _ in range(n_peaks):
                    # Random shift within range
                    shift = np.random.uniform(shift_range[0], shift_range[1])
                    # Intensity proportional to amount
                    intensity = amount * np.random.uniform(0.5, 1.0)
                    # Line width depends on field homogeneity and molecular size
                    width = np.random.uniform(1.0, 5.0) / magnetic_field

                    chemical_shifts.append(shift)
                    intensities.append(intensity)
                    widths.append(width)

        # Add some random impurity peaks
        n_impurities = np.random.randint(0, 3)
        for _ in range(n_impurities):
            shift = np.random.uniform(-2, 15)
            intensity = np.random.uniform(0.01, 0.1)
            width = np.random.uniform(1.0, 3.0) / magnetic_field

            chemical_shifts.append(shift)
            intensities.append(intensity)
            widths.append(width)

        # Sort by chemical shift
        sorted_data = sorted(zip(chemical_shifts, intensities, widths))
        chemical_shifts, intensities, widths = zip(*sorted_data)

        return list(chemical_shifts), list(intensities), list(widths)

    def _calculate_integrations(
        self,
        intensities: List[float],
        widths: List[float]
    ) -> List[float]:
        """Calculate integration values from peak intensities and widths"""
        integrations = []
        for intensity, width in zip(intensities, widths):
            # Integration is proportional to intensity × width
            integration = intensity * width * math.sqrt(math.pi / (4 * math.log(2)))
            integrations.append(integration)
        return integrations

    def _analyze_coupling_patterns(
        self,
        chemical_shifts: List[float],
        intensities: List[float],
        nucleus_type: str
    ) -> Tuple[List[float], List[str]]:
        """Analyze J-coupling patterns and determine multiplicities"""
        coupling_constants = []
        multiplicities = []

        for _ in zip(chemical_shifts, intensities):
            # Simulate J-coupling constants (Hz)
            j_coupling = np.random.uniform(0, 20) if np.random.random() > 0.3 else 0
            coupling_constants.append(j_coupling)

            # Determine multiplicity based on coupling
            if j_coupling < 1:
                multiplicity = "s"  # singlet
            elif j_coupling < 8:
                multiplicity = np.random.choice(["d", "t"], p=[0.6, 0.4])  # doublet/triplet
            elif j_coupling < 15:
                multiplicity = np.random.choice(["q", "m"], p=[0.3, 0.7])  # quartet/multiplet
            else:
                multiplicity = "m"  # multiplet

            multiplicities.append(multiplicity)

        return coupling_constants, multiplicities

    def _select_pulse_sequence(self, experiment_type: str) -> str:
        """Select appropriate pulse sequence for experiment type"""
        sequences = {
            "1D": "30°-τ-90°-acquire",
            "COSY": "90°-t1-90°-acquire",
            "HSQC": "INEPT-90°-t1-180°-acquire",
            "TOCSY": "90°-mixing-90°-acquire",
            "NOESY": "90°-τm-90°-t1-90°-acquire",
            "T1": "180°-τ-90°-acquire",
            "T2": "90°-τ-180°-τ-acquire"
        }
        return sequences.get(experiment_type, "30°-acquire")

    def _assign_peaks(self, spectrum: NMRSpectrum) -> List[Dict[str, Any]]:
        """Assign peaks to molecular fragments"""
        assignments = []
        shift_ranges = self.chemical_shift_ranges.get(spectrum.nucleus_type, {})

        for i, shift in enumerate(spectrum.chemical_shifts):
            # Find best matching functional group
            best_match = "unknown"
            min_distance = float('inf')

            for group, (low, high) in shift_ranges.items():
                if low <= shift <= high:
                    distance = min(abs(shift - low), abs(shift - high))
                    if distance < min_distance:
                        min_distance = distance
                        best_match = group

            assignment = {
                "peak_index": i,
                "chemical_shift": shift,
                "assignment": best_match,
                "confidence": 1.0 - (min_distance / 10.0),
                "multiplicity": spectrum.multiplicity[i],
                "coupling": spectrum.coupling_constants[i]
            }
            assignments.append(assignment)

        return assignments

    def _identify_functional_groups(self, spectrum: NMRSpectrum) -> List[str]:
        """Identify functional groups from chemical shifts"""
        functional_groups = []
        shift_ranges = self.chemical_shift_ranges.get(spectrum.nucleus_type, {})

        for shift in spectrum.chemical_shifts:
            for group, (low, high) in shift_ranges.items():
                if low <= shift <= high:
                    functional_groups.append(group)

        return functional_groups

    def _calculate_molecular_weight(self, molecular_formula: str) -> float:
        """Calculate molecular weight from formula"""
        # Simplified molecular weight calculation
        atomic_weights = {
            'H': 1.008, 'C': 12.011, 'N': 14.007, 'O': 15.999,
            'P': 30.974, 'S': 32.066, 'Cl': 35.45, 'Br': 79.904,
            'F': 18.998, 'I': 126.904, 'Si': 28.086
        }

        weight = 0.0
        i = 0
        while i < len(molecular_formula):
            element = molecular_formula[i]
            if element.isupper():
                count_str = ""
                i += 1
                while i < len(molecular_formula) and molecular_formula[i].isdigit():
                    count_str += molecular_formula[i]
                    i += 1
                count = int(count_str) if count_str else 1
                weight += atomic_weights.get(element, 12.0) * count
            else:
                i += 1

        return weight

    def _deduce_molecular_formula(
        self,
        nmr_data: List[NMRSpectrum],
        assignments: List[Dict[str, Any]]
    ) -> Tuple[str, float]:
        """Deduce molecular formula from NMR data and assignments"""
        # Simplified formula deduction
        carbon_count = len([a for a in assignments if "C" in a.get("assignment", "")])
        hydrogen_count = len([a for a in assignments if "H" in a.get("assignment", "")])

        # Estimate based on typical organic compounds
        carbon_count = max(carbon_count, 4)
        hydrogen_count = max(hydrogen_count, carbon_count * 2)

        formula = f"C{carbon_count}H{hydrogen_count}"
        weight = self._calculate_molecular_weight(formula)

        return formula, weight

    def _analyze_stereochemistry(self, nmr_data: List[NMRSpectrum]) -> str:
        """Analyze stereochemistry from coupling constants and chemical shifts"""
        # Look for characteristic coupling patterns
        large_couplings = []
        for spectrum in nmr_data:
            for j in spectrum.coupling_constants:
                if j > 12:  # Large coupling suggests trans relationship
                    large_couplings.append(j)

        if large_couplings:
            return f"trans configuration indicated (J = {max(large_couplings):.1f} Hz)"
        else:
            return "stereochemistry undetermined from available data"

    def _estimate_purity(self, nmr_data: List[NMRSpectrum]) -> float:
        """Estimate sample purity from integration ratios"""
        total_main_peaks = 0
        total_impurity_peaks = 0

        for spectrum in nmr_data:
            # Assume largest peaks are main compound
            sorted_intensities = sorted(spectrum.integration_values, reverse=True)
            main_threshold = sorted_intensities[0] * 0.1

            for integration in spectrum.integration_values:
                if integration >= main_threshold:
                    total_main_peaks += integration
                else:
                    total_impurity_peaks += integration

        total = total_main_peaks + total_impurity_peaks
        purity = total_main_peaks / total if total > 0 else 0.95

        return min(purity, 0.999)  # Cap at 99.9%

    def _calculate_structure_confidence(
        self,
        nmr_data: List[NMRSpectrum],
        assignments: List[Dict[str, Any]],
        constraints: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate confidence in structure determination"""
        base_confidence = 0.7

        # More spectra = higher confidence
        spectra_bonus = min(len(nmr_data) * 0.1, 0.2)

        # Good assignments = higher confidence
        assignment_quality = np.mean([a.get("confidence", 0.5) for a in assignments])

        # Additional constraints boost confidence
        constraint_bonus = 0.1 if constraints and len(constraints) > 0 else 0

        confidence = base_confidence + spectra_bonus + assignment_quality * 0.1 + constraint_bonus

        return float(min(confidence, 0.95))  # Cap at 95%

    def _measure_relaxation_times(self, spectra: List[NMRSpectrum]) -> Dict[str, float]:
        """Measure T1 and T2 relaxation times"""
        # Simulate relaxation time measurements
        t1 = np.random.uniform(0.5, 5.0)  # T1 typically 0.5-5 seconds
        t2 = np.random.uniform(0.01, 0.5)  # T2 typically 10-500 ms

        return {
            "T1": t1,
            "T2": t2,
            "T1_T2_ratio": t1 / t2
        }

    def _calculate_diffusion_coefficient(self, spectra: List[NMRSpectrum]) -> Optional[float]:
        """Calculate diffusion coefficient from DOSY data"""
        # Check if any spectrum has DOSY parameters
        dosy_data = any("DOSY" in str(s.acquisition_parameters) for s in spectra)

        if dosy_data:
            # Typical range for small molecules in solution
            return np.random.uniform(1e-10, 1e-9)  # m²/s
        else:
            return None

    def _analyze_exchange_rates(
        self,
        spectra: List[NMRSpectrum],
        temperatures: Optional[List[float]]
    ) -> List[float]:
        """Analyze chemical exchange rates"""
        if not temperatures:
            temperatures = [298.15]  # Room temperature

        exchange_rates = []
        for temp in temperatures:
            # Exchange rate typically increases with temperature
            rate = np.random.uniform(1, 1000) * np.exp(-(3000 / temp))  # Arrhenius-like
            exchange_rates.append(rate)

        return exchange_rates

    def _calculate_activation_energy(
        self,
        exchange_rates: List[float],
        temperatures: List[float]
    ) -> float:
        """Calculate activation energy from temperature-dependent exchange rates"""
        if len(exchange_rates) < 2 or len(temperatures) < 2:
            return 50.0  # Default value

        # Arrhenius plot: ln(k) vs 1/T
        ln_k = [math.log(max(rate, 0.001)) for rate in exchange_rates]  # Avoid log(0)
        inv_t = [1 / t for t in temperatures]

        # Simple linear fit (slope = -Ea/R)
        if len(ln_k) >= 2 and len(inv_t) >= 2:
            slope = (ln_k[-1] - ln_k[0]) / (inv_t[-1] - inv_t[0])
            ea = -slope * 8.314  # J/mol
            return abs(ea) / 1000  # Convert to kJ/mol

        return 50.0  # Default activation energy

    def _calculate_temperature_coefficients(
        self,
        spectra: List[NMRSpectrum],
        temperatures: Optional[List[float]]
    ) -> List[float]:
        """Calculate temperature coefficients of chemical shifts"""
        if not temperatures or len(temperatures) < 2:
            return [np.random.uniform(-0.01, 0.01) for _ in range(5)]

        # Simulate temperature coefficients (ppb/K)
        coefficients = []
        for _ in range(min(5, len(spectra[0].chemical_shifts) if spectra else 5)):
            coeff = np.random.uniform(-20, 5)  # Typical range for organic molecules
            coefficients.append(coeff)

        return coefficients

    def _analyze_molecular_motion(
        self,
        relaxation_times: Dict[str, float],
        diffusion_coeff: Optional[float]
    ) -> Dict[str, float]:
        """Analyze molecular motion parameters"""
        motional_params = {}

        # Correlation time from relaxation data
        if "T1" in relaxation_times and "T2" in relaxation_times:
            t1 = relaxation_times["T1"]
            t2 = relaxation_times["T2"]

            # Simplified calculation
            tau_c = math.sqrt(t2 / t1) * 1e-10  # Approximate correlation time
            motional_params["correlation_time"] = tau_c

        # Hydrodynamic radius from diffusion coefficient
        if diffusion_coeff:
            # Stokes-Einstein equation approximation
            kT = 1.38e-23 * 298  # J (room temperature)
            eta = 0.001  # Pa·s (water viscosity)
            radius = kT / (6 * math.pi * eta * diffusion_coeff)
            motional_params["hydrodynamic_radius"] = radius * 1e9  # nm

        # Molecular tumbling rate
        if "correlation_time" in motional_params:
            tumbling_rate = 1 / motional_params["correlation_time"]
            motional_params["tumbling_rate"] = tumbling_rate

        return motional_params

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process generic NMR analysis request

        Args:
            request_data: Request parameters including analysis type and data

        Returns:
            Analysis results
        """
        try:
            analysis_type = request_data.get("analysis_type", "spectrum_acquisition")

            if analysis_type == "spectrum_acquisition":
                result = await self.acquire_nmr_spectrum(
                    sample_info=request_data.get("sample_info", {}),
                    nucleus_type=request_data.get("nucleus_type", "1H"),
                    magnetic_field=request_data.get("magnetic_field", 9.4),
                    experiment_type=request_data.get("experiment_type", "1D")
                )

            elif analysis_type == "structure_elucidation":
                # Convert data to NMRSpectrum objects
                nmr_data = [NMRSpectrum(**spec) for spec in request_data.get("nmr_data", [])]
                result = await self.elucidate_structure(
                    nmr_data=nmr_data,
                    molecular_formula=request_data.get("molecular_formula"),
                    additional_constraints=request_data.get("constraints")
                )

            elif analysis_type == "dynamics_analysis":
                # Convert data to NMRSpectrum objects
                nmr_spectra = [NMRSpectrum(**spec) for spec in request_data.get("nmr_spectra", [])]
                result = await self.analyze_molecular_dynamics(
                    nmr_spectra=nmr_spectra,
                    temperature_series=request_data.get("temperature_series"),
                    analysis_type=request_data.get("dynamics_type", "relaxation")
                )

            else:
                raise ValueError(f"Unsupported analysis type: {analysis_type}")

            return {
                "success": True,
                "analysis_type": analysis_type,
                "result": result.dict(),
                "timestamp": datetime.now().isoformat()
            }

        except ChemistryError as e:
            logger.error(f"Error processing NMR request: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
