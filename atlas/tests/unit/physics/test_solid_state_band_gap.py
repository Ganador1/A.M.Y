"""
Unit Tests for Solid State Physics Service - Band Gap Calculations
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from app.services.solid_state_physics import SolidStatePhysicsService


class TestSolidStatePhysicsBandGap:
    """Unit tests specifically for band gap calculation methods"""

    @pytest.fixture
    def service(self):
        """Fixture to provide SolidStatePhysicsService instance"""
        return SolidStatePhysicsService()

    def test_calculate_band_gap_semiconductor(self, service):
        """Test band gap calculation for semiconductor material"""
        with patch('app.services.solid_state_physics.GPAW') as mock_gpaw:
            mock_calc = Mock()

            # Semiconductor-like eigenvalues (gap ~1.0 eV)
            gamma_eigenvals = np.array([-8.0, -6.0, -4.0, -2.0, 0.0, 1.0, 3.0, 4.0])
            x_eigenvals = np.array([-7.8, -5.8, -3.8, -1.8, 0.2, 1.2, 3.2, 4.2])
            m_eigenvals = np.array([-7.9, -5.9, -3.9, -1.9, 0.1, 1.1, 3.1, 4.1])
            r_eigenvals = np.array([-8.1, -6.1, -4.1, -2.1, -0.1, 0.9, 2.9, 3.9])

            mock_calc.get_eigenvalues.side_effect = [
                gamma_eigenvals, x_eigenvals, m_eigenvals, r_eigenvals
            ]
            mock_calc.get_fermi_level.return_value = 0.0
            mock_gpaw.return_value = mock_calc

            gap = service._calculate_band_gap(mock_calc)

            assert isinstance(gap, float)
            assert 0.8 <= gap <= 1.2  # Should be around 1.0 eV

    def test_calculate_band_gap_metal(self, service):
        """Test band gap calculation for metallic material"""
        with patch('app.services.solid_state_physics.GPAW') as mock_gpaw:
            mock_calc = Mock()

            # Metal-like eigenvalues (no gap)
            gamma_eigenvals = np.array([-8.0, -6.0, -4.0, -2.0, -0.1, 0.1, 0.3, 0.5])
            x_eigenvals = np.array([-7.8, -5.8, -3.8, -1.8, -0.05, 0.15, 0.35, 0.55])
            m_eigenvals = np.array([-7.9, -5.9, -3.9, -1.9, -0.08, 0.12, 0.32, 0.52])
            r_eigenvals = np.array([-8.1, -6.1, -4.1, -2.1, -0.12, 0.08, 0.28, 0.48])

            mock_calc.get_eigenvalues.side_effect = [
                gamma_eigenvals, x_eigenvals, m_eigenvals, r_eigenvals
            ]
            mock_calc.get_fermi_level.return_value = 0.0
            mock_gpaw.return_value = mock_calc

            gap = service._calculate_band_gap(mock_calc)

            assert isinstance(gap, float)
            assert 0.0 <= gap <= 0.3  # Should be very small (metallic)

    def test_calculate_band_gap_insulator(self, service):
        """Test band gap calculation for insulating material"""
        with patch('app.services.solid_state_physics.GPAW') as mock_gpaw:
            mock_calc = Mock()

            # Insulator-like eigenvalues (large gap)
            gamma_eigenvals = np.array([-15.0, -12.0, -9.0, -6.0, -3.0, 2.0, 6.0, 9.0])
            x_eigenvals = np.array([-14.8, -11.8, -8.8, -5.8, -2.8, 2.2, 6.2, 9.2])
            m_eigenvals = np.array([-14.9, -11.9, -8.9, -5.9, -2.9, 2.1, 6.1, 9.1])
            r_eigenvals = np.array([-15.1, -12.1, -9.1, -6.1, -3.1, 1.9, 5.9, 8.9])

            mock_calc.get_eigenvalues.side_effect = [
                gamma_eigenvals, x_eigenvals, m_eigenvals, r_eigenvals
            ]
            mock_calc.get_fermi_level.return_value = 0.0
            mock_gpaw.return_value = mock_calc

            gap = service._calculate_band_gap(mock_calc)

            assert isinstance(gap, float)
            assert gap >= 5.0  # Should be large gap

    def test_calculate_band_gap_kpoint_variation(self, service):
        """Test band gap calculation with different k-point sets"""
        with patch('app.services.solid_state_physics.GPAW') as mock_gpaw:
            mock_calc = Mock()

            # Test with only Γ point (should still work)
            gamma_only = np.array([-8.0, -6.0, -4.0, -2.0, 0.0, 1.0, 3.0, 4.0])
            mock_calc.get_eigenvalues.return_value = gamma_only
            mock_calc.get_fermi_level.return_value = 0.0
            mock_gpaw.return_value = mock_calc

            gap = service._calculate_band_gap(mock_calc)

            assert isinstance(gap, float)
            assert gap >= 0.0

    def test_calculate_band_gap_edge_cases(self, service):
        """Test band gap calculation edge cases"""
        with patch('app.services.solid_state_physics.GPAW') as mock_gpaw:
            mock_calc = Mock()

            # Test with degenerate states
            degenerate_eigenvals = np.array([-8.0, -6.0, -4.0, -2.0, 0.0, 0.0, 3.0, 4.0])
            mock_calc.get_eigenvalues.return_value = degenerate_eigenvals
            mock_calc.get_fermi_level.return_value = 0.0
            mock_gpaw.return_value = mock_calc

            gap = service._calculate_band_gap(mock_calc)

            assert isinstance(gap, float)
            assert gap == 3.0  # Gap between degenerate state and conduction band

    def test_calculate_band_gap_with_fermi_level_offset(self, service):
        """Test band gap calculation with non-zero Fermi level"""
        with patch('app.services.solid_state_physics.GPAW') as mock_gpaw:
            mock_calc = Mock()

            # Eigenvalues with Fermi level at -1.0 eV
            eigenvals = np.array([-9.0, -7.0, -5.0, -3.0, -1.0, -0.8, 1.0, 2.0])
            mock_calc.get_eigenvalues.return_value = eigenvals
            mock_calc.get_fermi_level.return_value = -1.0
            mock_gpaw.return_value = mock_calc

            gap = service._calculate_band_gap(mock_calc)

            assert isinstance(gap, float)
            assert gap >= 0.0

    def test_band_gap_calculation_consistency(self, service):
        """Test that band gap calculation is consistent across multiple calls"""
        with patch('app.services.solid_state_physics.GPAW') as mock_gpaw:
            mock_calc = Mock()

            eigenvals = np.array([-8.0, -6.0, -4.0, -2.0, 0.0, 1.0, 3.0, 4.0])
            mock_calc.get_eigenvalues.return_value = eigenvals
            mock_calc.get_fermi_level.return_value = 0.0
            mock_gpaw.return_value = mock_calc

            # Calculate gap multiple times
            gaps = [service._calculate_band_gap(mock_calc) for _ in range(5)]

            # All gaps should be the same
            assert all(abs(gap - gaps[0]) < 1e-10 for gap in gaps)

    def test_band_gap_calculation_precision(self, service):
        """Test band gap calculation precision"""
        with patch('app.services.solid_state_physics.GPAW') as mock_gpaw:
            mock_calc = Mock()

            # Very precise eigenvalues
            eigenvals = np.array([
                -8.000000, -6.000000, -4.000000, -2.000000,
                 0.000000,  1.000000,  3.000000,  4.000000
            ])
            mock_calc.get_eigenvalues.return_value = eigenvals
            mock_calc.get_fermi_level.return_value = 0.0
            mock_gpaw.return_value = mock_calc

            gap = service._calculate_band_gap(mock_calc)

            assert isinstance(gap, float)
            assert abs(gap - 1.0) < 1e-6  # Should be exactly 1.0 eV

    def test_band_gap_calculation_with_different_occupations(self, service):
        """Test band gap calculation with different occupation numbers"""
        with patch('app.services.solid_state_physics.GPAW') as mock_gpaw:
            mock_calc = Mock()

            # Test with partially occupied states
            eigenvals = np.array([-8.0, -6.0, -4.0, -2.0, -0.5, 0.5, 2.0, 3.0])
            mock_calc.get_eigenvalues.return_value = eigenvals
            mock_calc.get_fermi_level.return_value = 0.0
            mock_gpaw.return_value = mock_calc

            gap = service._calculate_band_gap(mock_calc)

            assert isinstance(gap, float)
            assert gap >= 0.0

    def test_classify_material_band_gap_thresholds(self, service):
        """Test material classification with precise band gap thresholds"""
        # Test exact threshold values
        test_cases = [
            (0.0, "metal"),
            (0.099, "metal"),
            (0.101, "semiconductor"),
            (3.99, "semiconductor"),
            (4.01, "insulator"),
            (10.0, "insulator")
        ]

        for gap, expected_type in test_cases:
            material_type, _ = service._classify_material(gap)
            assert material_type == expected_type, f"Gap {gap} eV should classify as {expected_type}"

    def test_band_gap_calculation_error_handling(self, service):
        """Test band gap calculation error handling"""
        with patch('app.services.solid_state_physics.GPAW') as mock_gpaw:
            mock_calc = Mock()

            # Test with invalid eigenvalues
            mock_calc.get_eigenvalues.return_value = np.array([])  # Empty array
            mock_calc.get_fermi_level.return_value = 0.0
            mock_gpaw.return_value = mock_calc

            # Should handle gracefully
            gap = service._calculate_band_gap(mock_calc)
            assert isinstance(gap, float)

    def test_band_gap_calculation_with_spin_polarization(self, service):
        """Test band gap calculation with spin-polarized calculations"""
        with patch('app.services.solid_state_physics.GPAW') as mock_gpaw:
            mock_calc = Mock()

            # Spin-polarized eigenvalues (spin up and spin down)
            spin_up = np.array([-8.0, -6.0, -4.0, -2.0, 0.0, 1.0, 3.0, 4.0])
            spin_down = np.array([-7.5, -5.5, -3.5, -1.5, 0.5, 1.5, 3.5, 4.5])

            mock_calc.get_eigenvalues.side_effect = [spin_up, spin_down]
            mock_calc.get_fermi_level.return_value = 0.0
            mock_gpaw.return_value = mock_calc

            gap = service._calculate_band_gap(mock_calc)

            assert isinstance(gap, float)
            assert gap >= 0.0
