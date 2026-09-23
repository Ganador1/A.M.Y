"""
Tests for PDE Service
"""

import pytest
import numpy as np
from app.services.pde_service import PDEService


class TestPDEService:
    """Test cases for PDEService"""

    @pytest.fixture
    def service(self):
        """Fixture to provide PDEService instance"""
        return PDEService()

    def test_heat_equation_basic(self, service):
        """Test basic heat equation solving"""
        result = service.solve_heat_equation(
            L=1.0, T=0.1, alpha=0.01, nx=10, nt=10,
            initial_condition="np.sin(np.pi*x)",
            boundary_conditions={"left": "0", "right": "0"}
        )

        assert result['status'] == 'success'
        assert 'solution' in result
        assert 'x_grid' in result
        assert 't_grid' in result
        assert result['solution'].shape[0] == 11  # nt + 1
        assert result['solution'].shape[1] == 11  # nx + 1

    def test_wave_equation_basic(self, service):
        """Test basic wave equation solving"""
        result = service.solve_wave_equation(
            L=1.0, T=0.1, c=1.0, nx=10, nt=10,
            initial_displacement="np.sin(np.pi*x)",
            initial_velocity="0",
            boundary_conditions={"left": "0", "right": "0"}
        )

        assert result['status'] == 'success'
        assert 'solution' in result
        assert result['solution'].shape[0] == 11  # nt + 1
        assert result['solution'].shape[1] == 11  # nx + 1

    def test_laplace_equation_basic(self, service):
        """Test basic Laplace equation solving"""
        result = service.solve_laplace_equation(
            nx=10, ny=10,
            boundary_conditions={
                "top": "np.sin(np.pi*x)",
                "bottom": "0",
                "left": "0",
                "right": "0"
            }
        )

        assert result['status'] == 'success'
        assert 'solution' in result
        assert result['solution'].shape == (11, 11)

    def test_poisson_equation_basic(self, service):
        """Test basic Poisson equation solving"""
        result = service.solve_poisson_equation(
            nx=10, ny=10,
            source_term="np.sin(np.pi*x)*np.sin(np.pi*y)",
            boundary_conditions={
                "top": "0",
                "bottom": "0",
                "left": "0",
                "right": "0"
            }
        )

        assert result['status'] == 'success'
        assert 'solution' in result
        assert result['solution'].shape == (11, 11)

    def test_burgers_equation_basic(self, service):
        """Test basic Burgers equation solving"""
        result = service.solve_burgers_equation(
            L=1.0, T=0.1, nu=0.01, nx=10, nt=10,
            initial_condition="0.5*np.sin(np.pi*x) + 0.5",
            boundary_conditions={"left": "1", "right": "0"}
        )

        assert result['status'] == 'success'
        assert 'solution' in result
        assert result['solution'].shape[0] == 11
        assert result['solution'].shape[1] == 11

    def test_navier_stokes_basic(self, service):
        """Test basic Navier-Stokes equation solving (simplified 2D)"""
        result = service.solve_navier_stokes_2d(
            Lx=1.0, Ly=1.0, T=0.01, nu=0.01, rho=1.0,
            nx=8, ny=8, nt=5,
            initial_u="np.sin(np.pi*x)*np.cos(np.pi*y)",
            initial_v="-np.cos(np.pi*x)*np.sin(np.pi*y)",
            boundary_conditions={
                "u_top": "0", "u_bottom": "0", "u_left": "0", "u_right": "0",
                "v_top": "0", "v_bottom": "0", "v_left": "0", "v_right": "0"
            }
        )

        assert result['status'] == 'success'
        assert 'u_solution' in result
        assert 'v_solution' in result

    def test_heat_equation_invalid_parameters(self, service):
        """Test heat equation with invalid parameters"""
        result = service.solve_heat_equation(
            L=-1.0, T=0.1, alpha=0.01, nx=10, nt=10,
            initial_condition="np.sin(np.pi*x)",
            boundary_conditions={"left": "0", "right": "0"}
        )

        assert result['status'] == 'error'
        assert 'error' in result

    def test_wave_equation_invalid_initial_condition(self, service):
        """Test wave equation with invalid initial condition"""
        result = service.solve_wave_equation(
            L=1.0, T=0.1, c=1.0, nx=10, nt=10,
            initial_displacement="invalid_function(x)",
            initial_velocity="0",
            boundary_conditions={"left": "0", "right": "0"}
        )

        assert result['status'] == 'error'
        assert 'error' in result

    def test_laplace_equation_missing_boundary(self, service):
        """Test Laplace equation with missing boundary conditions"""
        result = service.solve_laplace_equation(
            nx=10, ny=10,
            boundary_conditions={
                "top": "np.sin(np.pi*x)",
                "bottom": "0"
                # Missing left and right
            }
        )

        assert result['status'] == 'error'
        assert 'error' in result

    def test_get_pde_types(self, service):
        """Test getting available PDE types"""
        result = service.get_pde_types()

        assert isinstance(result, dict)
        assert 'heat_equation' in result
        assert 'wave_equation' in result
        assert 'laplace_equation' in result
        assert 'poisson_equation' in result
        assert 'burgers_equation' in result
        assert 'navier_stokes' in result

    def test_pde_stability_analysis(self, service):
        """Test PDE stability analysis"""
        result = service.analyze_stability(
            equation_type="heat_equation",
            alpha=0.01, dx=0.1, dt=0.005
        )

        assert result['status'] == 'success'
        assert 'stability_condition' in result
        assert 'is_stable' in result

    def test_pde_convergence_analysis(self, service):
        """Test PDE convergence analysis"""
        result = service.analyze_convergence(
            equation_type="heat_equation",
            solutions=[np.random.rand(10, 10), np.random.rand(20, 20)],
            grid_sizes=[0.1, 0.05]
        )

        assert result['status'] == 'success'
        assert 'convergence_rate' in result
        assert 'order_of_accuracy' in result

    def test_pde_solution_validation(self, service):
        """Test PDE solution validation"""
        # Create a simple test solution
        x = np.linspace(0, 1, 10)
        t = np.linspace(0, 0.1, 5)
        X, T = np.meshgrid(x, t)
        solution = np.sin(np.pi*X)*np.exp(-T)

        result = service.validate_solution(
            solution=solution,
            equation_type="heat_equation",
            x_grid=x, t_grid=t,
            parameters={"alpha": 0.01}
        )

        assert result['status'] == 'success'
        assert 'residual_norm' in result
        assert 'is_valid' in result
