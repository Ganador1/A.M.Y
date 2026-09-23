"""
Astronomical coordinate utilities and transformations.
"""

import math
from typing import Tuple, Dict, Any, Optional
import numpy as np


class AstronomicalCoordinates:
    """Utility class for astronomical coordinate transformations."""
    
    @staticmethod
    def ra_dec_to_cartesian(ra: float, dec: float, distance: float = 1.0) -> Tuple[float, float, float]:
        """
        Convert RA/Dec coordinates to Cartesian coordinates.
        
        Args:
            ra: Right Ascension in degrees
            dec: Declination in degrees
            distance: Distance (default 1.0 for unit sphere)
            
        Returns:
            Tuple of (x, y, z) coordinates
        """
        # Convert degrees to radians
        ra_rad = math.radians(ra)
        dec_rad = math.radians(dec)
        
        # Convert to Cartesian coordinates
        x = distance * math.cos(dec_rad) * math.cos(ra_rad)
        y = distance * math.cos(dec_rad) * math.sin(ra_rad)
        z = distance * math.sin(dec_rad)
        
        return x, y, z
    
    @staticmethod
    def cartesian_to_ra_dec(x: float, y: float, z: float) -> Tuple[float, float, float]:
        """
        Convert Cartesian coordinates to RA/Dec coordinates.
        
        Args:
            x, y, z: Cartesian coordinates
            
        Returns:
            Tuple of (ra, dec, distance) in degrees and units
        """
        distance = math.sqrt(x**2 + y**2 + z**2)
        
        # Handle edge cases
        if distance == 0:
            return 0.0, 0.0, 0.0
            
        dec_rad = math.asin(z / distance)
        ra_rad = math.atan2(y, x)
        
        # Convert to degrees and normalize RA to [0, 360)
        ra = math.degrees(ra_rad)
        if ra < 0:
            ra += 360
            
        dec = math.degrees(dec_rad)
        
        return ra, dec, distance
    
    @staticmethod
    def angular_separation(ra1: float, dec1: float, ra2: float, dec2: float) -> float:
        """
        Calculate angular separation between two celestial objects.
        
        Args:
            ra1, dec1: First object coordinates in degrees
            ra2, dec2: Second object coordinates in degrees
            
        Returns:
            Angular separation in degrees
        """
        # Convert to radians
        ra1_rad = math.radians(ra1)
        dec1_rad = math.radians(dec1)
        ra2_rad = math.radians(ra2)
        dec2_rad = math.radians(dec2)
        
        # Use haversine formula for great circle distance
        delta_ra = ra2_rad - ra1_rad
        delta_dec = dec2_rad - dec1_rad
        
        a = (math.sin(delta_dec / 2)**2 + 
             math.cos(dec1_rad) * math.cos(dec2_rad) * math.sin(delta_ra / 2)**2)
        
        c = 2 * math.asin(math.sqrt(a))
        
        return math.degrees(c)


class DistanceUtils:
    """Utility class for astronomical distance calculations."""
    
    @staticmethod
    def distance_modulus(apparent_mag: float, absolute_mag: float) -> float:
        """
        Calculate distance modulus from apparent and absolute magnitudes.
        
        Args:
            apparent_mag: Apparent magnitude
            absolute_mag: Absolute magnitude
            
        Returns:
            Distance modulus in magnitudes
        """
        return apparent_mag - absolute_mag
    
    @staticmethod
    def distance_from_modulus(distance_modulus: float) -> float:
        """
        Calculate distance in parsecs from distance modulus.
        
        Args:
            distance_modulus: Distance modulus in magnitudes
            
        Returns:
            Distance in parsecs
        """
        return 10 ** ((distance_modulus + 5) / 5)
    
    @staticmethod
    def parallax_to_distance(parallax_mas: float) -> float:
        """
        Convert parallax to distance.
        
        Args:
            parallax_mas: Parallax in milliarcseconds
            
        Returns:
            Distance in parsecs
        """
        if parallax_mas <= 0:
            raise ValueError("Parallax must be positive")
        
        return 1000.0 / parallax_mas  # Distance in parsecs
    
    @staticmethod
    def distance_to_parallax(distance_pc: float) -> float:
        """
        Convert distance to parallax.
        
        Args:
            distance_pc: Distance in parsecs
            
        Returns:
            Parallax in milliarcseconds
        """
        if distance_pc <= 0:
            raise ValueError("Distance must be positive")
        
        return 1000.0 / distance_pc  # Parallax in milliarcseconds
    
    @staticmethod
    def luminosity_distance(distance_pc: float, redshift: float = 0.0) -> float:
        """
        Calculate luminosity distance (simplified for low redshift).
        
        Args:
            distance_pc: Comoving distance in parsecs
            redshift: Cosmological redshift
            
        Returns:
            Luminosity distance in parsecs
        """
        # For low redshift approximation: D_L ≈ D_c * (1 + z)
        return distance_pc * (1 + redshift)
    
    @staticmethod
    def angular_diameter_distance(distance_pc: float, redshift: float = 0.0) -> float:
        """
        Calculate angular diameter distance (simplified for low redshift).
        
        Args:
            distance_pc: Comoving distance in parsecs
            redshift: Cosmological redshift
            
        Returns:
            Angular diameter distance in parsecs
        """
        # For low redshift approximation: D_A ≈ D_c / (1 + z)
        return distance_pc / (1 + redshift)