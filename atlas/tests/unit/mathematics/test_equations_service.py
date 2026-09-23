"""
Tests for Equations Service
"""

import pytest
from app.domains.mathematics.services.equation_service import EquationService
from app.models.models import EquationSolver


class TestEquationService:
    """Test cases for EquationService"""

    @pytest.fixture
    def service(self):
        """Fixture to provide EquationService instance"""
        return EquationService()

    def test_solve_equation_linear(self, service):
        """Test solving linear equation"""
        request = EquationSolver(equation="2*x + 3 = 7", variable="x")
        result = service.solve_equation(request)

        assert result.equation == "2*x + 3 = 7"
        assert result.variable == "x"
        assert len(result.solutions) > 0
        assert 2.0 in result.solutions

    def test_solve_equation_quadratic(self, service):
        """Test solving quadratic equation"""
        request = EquationSolver(equation="x**2 - 5*x + 6 = 0", variable="x")
        result = service.solve_equation(request)

        assert result.equation == "x**2 - 5*x + 6 = 0"
        assert result.variable == "x"
        assert len(result.solutions) == 2
        assert set(result.solutions) == {2.0, 3.0}

    def test_solve_equation_cubic(self, service):
        """Test solving cubic equation"""
        request = EquationSolver(equation="x**3 - 6*x**2 + 11*x - 6 = 0", variable="x")
        result = service.solve_equation(request)

        assert result.equation == "x**3 - 6*x**2 + 11*x - 6 = 0"
        assert result.variable == "x"
        assert len(result.solutions) == 3

    def test_solve_equation_transcendental(self, service):
        """Test solving transcendental equation"""
        request = EquationSolver(equation="exp(x) = 2", variable="x")
        result = service.solve_equation(request)

        assert result.equation == "exp(x) = 2"
        assert result.variable == "x"
        assert len(result.solutions) > 0

    def test_solve_equation_trigonometric(self, service):
        """Test solving trigonometric equation"""
        request = EquationSolver(equation="sin(x) = 0.5", variable="x")
        result = service.solve_equation(request)

        assert result.equation == "sin(x) = 0.5"
        assert result.variable == "x"
        assert len(result.solutions) > 0

    def test_solve_equation_exponential(self, service):
        """Test solving exponential equation"""
        request = EquationSolver(equation="2**x = 8", variable="x")
        result = service.solve_equation(request)

        assert result.equation == "2**x = 8"
        assert result.variable == "x"
        assert len(result.solutions) > 0
        assert 3.0 in result.solutions

    def test_solve_equation_logarithmic(self, service):
        """Test solving logarithmic equation"""
        request = EquationSolver(equation="log(x) = 1", variable="x")
        result = service.solve_equation(request)

        assert result.equation == "log(x) = 1"
        assert result.variable == "x"
        assert len(result.solutions) > 0
        assert 10.0 in result.solutions

    def test_solve_system_2x2(self, service):
        """Test solving 2x2 system"""
        equations = ["x + y = 5", "2*x - y = 1"]
        variables = ["x", "y"]

        result = service.solve_system(equations, variables)

        assert "equations" in result
        assert "variables" in result
        assert "solutions" in result
        assert result["solutions"]["x"] == 2.0
        assert result["solutions"]["y"] == 3.0

    def test_solve_system_3x3(self, service):
        """Test solving 3x3 system"""
        equations = ["x + y + z = 6", "2*x - y + z = 3", "x + 2*y - z = 2"]
        variables = ["x", "y", "z"]

        result = service.solve_system(equations, variables)

        assert "equations" in result
        assert "variables" in result
        assert "solutions" in result
        assert len(result["solutions"]) == 3

    def test_solve_system_inconsistent(self, service):
        """Test solving inconsistent system"""
        equations = ["x + y = 1", "x + y = 2"]
        variables = ["x", "y"]

        with pytest.raises(ValueError):
            service.solve_system(equations, variables)

    def test_solve_system_dependent(self, service):
        """Test solving dependent system"""
        equations = ["x + y = 1", "2*x + 2*y = 2"]
        variables = ["x", "y"]

        result = service.solve_system(equations, variables)

        assert "equations" in result
        assert "variables" in result
        assert "solutions" in result

    def test_get_equation_examples(self, service):
        """Test getting equation examples"""
        examples = service.get_equation_examples()

        assert isinstance(examples, list)
        assert len(examples) > 0

        # Check structure of first example
        example = examples[0]
        assert "equation" in example
        assert "description" in example
        assert "variable" in example

    def test_solve_equation_with_invalid_input(self, service):
        """Test solving equation with invalid input"""
        request = EquationSolver(equation="invalid equation", variable="x")

        with pytest.raises(ValueError):
            service.solve_equation(request)

    def test_solve_equation_no_solution(self, service):
        """Test solving equation with no solution"""
        request = EquationSolver(equation="x = x + 1", variable="x")
        result = service.solve_equation(request)

        assert result.equation == "x = x + 1"
        assert result.variable == "x"
        assert len(result.solutions) == 0

    def test_solve_equation_complex_solutions(self, service):
        """Test solving equation with complex solutions"""
        request = EquationSolver(equation="x**2 + 1 = 0", variable="x")
        result = service.solve_equation(request)

        assert result.equation == "x**2 + 1 = 0"
        assert result.variable == "x"
        assert len(result.solutions) == 2
        # Complex solutions should be strings
        assert all(isinstance(sol, str) for sol in result.solutions)

    def test_solve_equation_polynomial_higher_degree(self, service):
        """Test solving higher degree polynomial equation"""
        request = EquationSolver(equation="x**4 - 5*x**2 + 4 = 0", variable="x")
        result = service.solve_equation(request)

        assert result.equation == "x**4 - 5*x**2 + 4 = 0"
        assert result.variable == "x"
        assert len(result.solutions) == 4

    def test_solve_equation_rational(self, service):
        """Test solving rational equation"""
        request = EquationSolver(equation="(x-1)/(x+1) = 2", variable="x")
        result = service.solve_equation(request)

        assert result.equation == "(x-1)/(x+1) = 2"
        assert result.variable == "x"
        assert len(result.solutions) > 0

    def test_solve_equation_with_multiple_variables(self, service):
        """Test solving equation with multiple variables (should work with specified variable)"""
        request = EquationSolver(equation="x + y = 5", variable="x")
        result = service.solve_equation(request)

        assert result.equation == "x + y = 5"
        assert result.variable == "x"
        # This might not solve cleanly due to multiple variables, but shouldn't crash
        assert isinstance(result.solutions, list)

    def test_solve_equation_steps_format(self, service):
        """Test that solution steps are properly formatted"""
        request = EquationSolver(equation="x**2 - 4 = 0", variable="x")
        result = service.solve_equation(request)

        assert result.equation == "x**2 - 4 = 0"
        assert result.variable == "x"
        assert hasattr(result, 'steps')
        assert isinstance(result.steps, list)
        assert len(result.steps) > 0

    def test_solve_equation_solution_type(self, service):
        """Test that solution type is properly determined"""
        request = EquationSolver(equation="x**2 - 4 = 0", variable="x")
        result = service.solve_equation(request)

        assert result.equation == "x**2 - 4 = 0"
        assert result.variable == "x"
        assert hasattr(result, 'solution_type')
        assert isinstance(result.solution_type, str)
        assert "solución" in result.solution_type.lower() or "única" in result.solution_type.lower() or "múltiples" in result.solution_type.lower()

    def test_solve_system_empty_equations(self, service):
        """Test solving system with empty equations list"""
        equations = []
        variables = ["x", "y"]

        with pytest.raises(ValueError):
            service.solve_system(equations, variables)

    def test_solve_system_empty_variables(self, service):
        """Test solving system with empty variables list"""
        equations = ["x + y = 5"]
        variables = []

        with pytest.raises(ValueError):
            service.solve_system(equations, variables)

    def test_solve_system_mismatched_dimensions(self, service):
        """Test solving system with mismatched dimensions"""
        equations = ["x + y = 5", "2*x - y = 1"]
        variables = ["x"]  # Only one variable for two equations

        # This might work or raise an error depending on implementation
        result = service.solve_system(equations, variables)
        assert "equations" in result
        assert "variables" in result
