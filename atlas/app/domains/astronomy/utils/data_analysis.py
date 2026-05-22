"""
Astronomical data analysis utilities.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import statistics


@dataclass
class LightCurveAnalysis:
    """Light curve analysis results."""
    
    period: Optional[float] = None
    amplitude: Optional[float] = None
    mean_magnitude: Optional[float] = None
    variability_index: Optional[float] = None
    phase_folded_data: Optional[Dict[str, np.ndarray]] = None
    
    @classmethod
    def from_data(cls, time: np.ndarray, magnitude: np.ndarray, 
                  magnitude_error: Optional[np.ndarray] = None) -> 'LightCurveAnalysis':
        """Create analysis from light curve data."""
        
        # Basic statistics
        mean_mag = float(np.mean(magnitude))
        amplitude = float(np.max(magnitude) - np.min(magnitude))
        
        # Simple variability index (standard deviation / mean)
        variability = float(np.std(magnitude) / np.abs(mean_mag)) if mean_mag != 0 else 0.0
        
        return cls(
            amplitude=amplitude,
            mean_magnitude=mean_mag,
            variability_index=variability
        )
    
    def is_variable(self, threshold: float = 0.01) -> bool:
        """Check if object shows significant variability."""
        return self.variability_index is not None and self.variability_index > threshold


class PhotometryUtils:
    """Utilities for photometric analysis."""
    
    @staticmethod
    def calculate_magnitude_error(flux: np.ndarray, flux_error: np.ndarray) -> np.ndarray:
        """Calculate magnitude error from flux and flux error."""
        # Avoid division by zero
        flux_safe = np.where(flux > 0, flux, np.nan)
        mag_error = 2.5 * np.log10(np.e) * (flux_error / flux_safe)
        return mag_error
    
    @staticmethod
    def flux_to_magnitude(flux: np.ndarray, zero_point: float = 25.0) -> np.ndarray:
        """Convert flux to magnitude."""
        # Avoid log of negative or zero values
        flux_safe = np.where(flux > 0, flux, np.nan)
        magnitude = zero_point - 2.5 * np.log10(flux_safe)
        return magnitude
    
    @staticmethod
    def magnitude_to_flux(magnitude: np.ndarray, zero_point: float = 25.0) -> np.ndarray:
        """Convert magnitude to flux."""
        flux = 10**((zero_point - magnitude) / 2.5)
        return flux
    
    @staticmethod
    def differential_photometry(target_flux: np.ndarray, 
                              reference_fluxes: List[np.ndarray]) -> np.ndarray:
        """Perform differential photometry using reference stars."""
        if not reference_fluxes:
            return target_flux
        
        # Calculate ensemble reference
        reference_ensemble = np.mean(reference_fluxes, axis=0)
        
        # Avoid division by zero
        reference_safe = np.where(reference_ensemble > 0, reference_ensemble, np.nan)
        
        # Differential flux
        differential = target_flux / reference_safe
        
        return differential
    
    @staticmethod
    def calculate_airmass_correction(airmass: np.ndarray, 
                                   extinction_coeff: float = 0.2) -> np.ndarray:
        """Calculate airmass extinction correction."""
        correction = extinction_coeff * (airmass - 1.0)
        return correction


class StatisticalAnalysis:
    """Statistical analysis utilities for astronomical data."""
    
    @staticmethod
    def calculate_statistics(data: np.ndarray) -> Dict[str, float]:
        """Calculate basic statistics for astronomical data."""
        # Remove NaN values
        clean_data = data[~np.isnan(data)]
        
        if len(clean_data) == 0:
            return {
                'mean': np.nan,
                'median': np.nan,
                'std': np.nan,
                'min': np.nan,
                'max': np.nan,
                'count': 0
            }
        
        return {
            'mean': float(np.mean(clean_data)),
            'median': float(np.median(clean_data)),
            'std': float(np.std(clean_data)),
            'min': float(np.min(clean_data)),
            'max': float(np.max(clean_data)),
            'count': len(clean_data)
        }
    
    @staticmethod
    def detect_outliers(data: np.ndarray, sigma_threshold: float = 3.0) -> np.ndarray:
        """Detect outliers using sigma clipping."""
        clean_data = data[~np.isnan(data)]
        
        if len(clean_data) < 3:
            return np.array([], dtype=bool)
        
        mean = np.mean(clean_data)
        std = np.std(clean_data)
        
        # Create boolean mask for outliers
        outlier_mask = np.abs(data - mean) > (sigma_threshold * std)
        
        return outlier_mask
    
    @staticmethod
    def calculate_periodogram(time: np.ndarray, magnitude: np.ndarray,
                            min_period: float = 0.1, max_period: float = 100.0,
                            num_periods: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate a simple Lomb-Scargle-like periodogram."""
        
        # Generate frequency grid
        min_freq = 1.0 / max_period
        max_freq = 1.0 / min_period
        frequencies = np.linspace(min_freq, max_freq, num_periods)
        periods = 1.0 / frequencies
        
        # Simple periodogram calculation (not true Lomb-Scargle)
        power = np.zeros_like(frequencies)
        
        # Remove mean
        mag_centered = magnitude - np.mean(magnitude)
        
        for i, freq in enumerate(frequencies):
            # Simple sinusoidal fit
            phase = 2 * np.pi * freq * time
            cos_component = np.sum(mag_centered * np.cos(phase))
            sin_component = np.sum(mag_centered * np.sin(phase))
            
            # Power is the sum of squares
            power[i] = cos_component**2 + sin_component**2
        
        # Normalize
        power = power / np.sum(power)
        
        return periods, power
    
    @staticmethod
    def find_best_period(periods: np.ndarray, power: np.ndarray) -> float:
        """Find the period with maximum power."""
        max_idx = np.argmax(power)
        return float(periods[max_idx])
    
    @staticmethod
    def phase_fold_data(time: np.ndarray, data: np.ndarray, 
                       period: float, epoch: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
        """Phase fold data with given period."""
        phase = ((time - epoch) / period) % 1.0
        
        # Sort by phase
        sort_idx = np.argsort(phase)
        phase_sorted = phase[sort_idx]
        data_sorted = data[sort_idx]
        
        return phase_sorted, data_sorted
    
    @staticmethod
    def bin_data(x: np.ndarray, y: np.ndarray, bin_size: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Bin data for smoother visualization."""
        x_min, x_max = np.min(x), np.max(x)
        bin_edges = np.arange(x_min, x_max + bin_size, bin_size)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        binned_y = []
        binned_err = []
        
        for i in range(len(bin_edges) - 1):
            mask = (x >= bin_edges[i]) & (x < bin_edges[i + 1])
            if np.any(mask):
                binned_y.append(np.mean(y[mask]))
                binned_err.append(np.std(y[mask]) / np.sqrt(np.sum(mask)))
            else:
                binned_y.append(np.nan)
                binned_err.append(np.nan)
        
        return bin_centers, np.array(binned_y), np.array(binned_err)