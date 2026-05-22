"""
Tests for Number Theory Service
"""

import pytest
from app.services.number_theory import NumberTheoryService
from app.models.models import NumberTheoryRequest, NumberTheoryResult


class TestNumberTheoryService:
    """Test cases for NumberTheoryService"""

    @pytest.fixture
    def service(self):
        """Fixture to provide NumberTheoryService instance"""
        return NumberTheoryService()

    def test_is_prime(self, service):
        """Test checking if a number is prime"""
        request = NumberTheoryRequest(number=7, operation="is_prime")

        result = service.is_prime(request)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "is_prime"
        assert isinstance(result.result, bool)
        assert result.result is True

    def test_is_not_prime(self, service):
        """Test checking if a number is not prime"""
        request = NumberTheoryRequest(number=9, operation="is_prime")

        result = service.is_prime(request)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "is_prime"
        assert isinstance(result.result, bool)
        assert result.result is False

    def test_prime_factors(self, service):
        """Test prime factorization"""
        request = NumberTheoryRequest(number=60, operation="prime_factors")

        result = service.prime_factors(request)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "prime_factors"
        assert isinstance(result.result, dict)
        assert "factors" in result.result
        assert result.result["factors"] == {2: 2, 3: 1, 5: 1}

    def test_greatest_common_divisor(self, service):
        """Test GCD calculation"""
        result = service.gcd(48, 18)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "gcd"
        assert isinstance(result.result, int)
        assert result.result == 6

    def test_least_common_multiple(self, service):
        """Test LCM calculation"""
        result = service.lcm(12, 18)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "lcm"
        assert isinstance(result.result, int)
        assert result.result == 36

    def test_euler_totient(self, service):
        """Test Euler's totient function"""
        request = NumberTheoryRequest(number=12, operation="euler_totient")

        result = service.euler_totient(request)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "euler_totient"
        assert isinstance(result.result, int)
        assert result.result == 4

    def test_modular_inverse(self, service):
        """Test modular inverse calculation"""
        result = service.modular_inverse(3, 11)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "modular_inverse"
        assert isinstance(result.result, int)
        assert result.result == 4  # 3 * 4 = 12 ≡ 1 mod 11

    def test_modular_exponentiation(self, service):
        """Test modular exponentiation"""
        result = service.modular_exponentiation(2, 10, 1000)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "modular_exponentiation"
        assert isinstance(result.result, int)
        assert result.result == 24  # 2^10 = 1024, 1024 mod 1000 = 24

    def test_chinese_remainder_theorem(self, service):
        """Test Chinese Remainder Theorem"""
        congruences = [(2, 3), (3, 5), (2, 7)]  # x ≡ 2 mod 3, x ≡ 3 mod 5, x ≡ 2 mod 7

        result = service.chinese_remainder_theorem(congruences)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "chinese_remainder"
        assert isinstance(result.result, dict)
        assert "solution" in result.result
        assert "modulus" in result.result

    def test_quadratic_residues(self, service):
        """Test quadratic residues modulo n"""
        request = NumberTheoryRequest(number=7, operation="quadratic_residues")

        result = service.quadratic_residues(request)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "quadratic_residues"
        assert isinstance(result.result, list)
        # For mod 7, quadratic residues are 0, 1, 2, 4
        assert set(result.result) == {0, 1, 2, 4}

    def test_legendre_symbol(self, service):
        """Test Legendre symbol calculation"""
        result = service.legendre_symbol(5, 7)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "legendre_symbol"
        assert isinstance(result.result, int)
        assert result.result == 1  # 5 is quadratic residue mod 7

    def test_jacobi_symbol(self, service):
        """Test Jacobi symbol calculation"""
        result = service.jacobi_symbol(5, 9)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "jacobi_symbol"
        assert isinstance(result.result, int)

    def test_primitive_root(self, service):
        """Test finding primitive root modulo n"""
        request = NumberTheoryRequest(number=7, operation="primitive_root")

        result = service.primitive_root(request)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "primitive_root"
        assert isinstance(result.result, list)
        assert len(result.result) > 0

    def test_discrete_logarithm(self, service):
        """Test discrete logarithm calculation"""
        result = service.discrete_logarithm(2, 9, 11)  # 2^x ≡ 9 mod 11

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "discrete_logarithm"
        assert isinstance(result.result, int)
        assert result.result == 6  # 2^6 = 64 ≡ 9 mod 11

    def test_factorial(self, service):
        """Test factorial calculation"""
        request = NumberTheoryRequest(number=5, operation="factorial")

        result = service.factorial(request)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "factorial"
        assert isinstance(result.result, int)
        assert result.result == 120

    def test_binomial_coefficient(self, service):
        """Test binomial coefficient calculation"""
        result = service.binomial_coefficient(5, 2)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "binomial_coefficient"
        assert isinstance(result.result, int)
        assert result.result == 10

    def test_fibonacci_number(self, service):
        """Test Fibonacci number calculation"""
        request = NumberTheoryRequest(number=8, operation="fibonacci")

        result = service.fibonacci(request)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "fibonacci"
        assert isinstance(result.result, int)
        assert result.result == 21

    def test_catalan_number(self, service):
        """Test Catalan number calculation"""
        request = NumberTheoryRequest(number=4, operation="catalan")

        result = service.catalan(request)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "catalan"
        assert isinstance(result.result, int)
        assert result.result == 14

    def test_partition_function(self, service):
        """Test partition function calculation"""
        request = NumberTheoryRequest(number=5, operation="partition")

        result = service.partition_function(request)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "partition"
        assert isinstance(result.result, int)
        assert result.result == 7  # p(5) = 7

    def test_mersenne_prime_check(self, service):
        """Test Mersenne prime check"""
        request = NumberTheoryRequest(number=3, operation="mersenne_prime")  # 2^3 - 1 = 7

        result = service.mersenne_prime(request)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "mersenne_prime"
        assert isinstance(result.result, bool)
        assert result.result is True

    def test_perfect_number_check(self, service):
        """Test perfect number check"""
        request = NumberTheoryRequest(number=6, operation="perfect_number")

        result = service.perfect_number(request)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "perfect_number"
        assert isinstance(result.result, bool)
        assert result.result is True

    def test_abundant_number_check(self, service):
        """Test abundant number check"""
        request = NumberTheoryRequest(number=12, operation="abundant_number")

        result = service.abundant_number(request)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "abundant_number"
        assert isinstance(result.result, bool)
        assert result.result is True

    def test_deficient_number_check(self, service):
        """Test deficient number check"""
        request = NumberTheoryRequest(number=8, operation="deficient_number")

        result = service.deficient_number(request)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "deficient_number"
        assert isinstance(result.result, bool)
        assert result.result is True

    def test_amicable_numbers_check(self, service):
        """Test amicable numbers check"""
        result = service.amicable_numbers(220, 284)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "amicable_numbers"
        assert isinstance(result.result, bool)
        assert result.result is True

    def test_goldbach_conjecture(self, service):
        """Test Goldbach conjecture for even number"""
        request = NumberTheoryRequest(number=10, operation="goldbach")

        result = service.goldbach_conjecture(request)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "goldbach"
        assert isinstance(result.result, list)
        assert len(result.result) > 0

    def test_riemann_hypothesis_test(self, service):
        """Test Riemann hypothesis (simplified test)"""
        request = NumberTheoryRequest(number=100, operation="riemann_test")

        result = service.riemann_hypothesis_test(request)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "riemann_test"
        assert isinstance(result.result, dict)
        assert "zeros_on_critical_line" in result.result

    def test_number_theory_with_invalid_input(self, service):
        """Test number theory with invalid input"""
        request = NumberTheoryRequest(number=-5, operation="is_prime")

        with pytest.raises(ValueError):
            service.is_prime(request)

    def test_modular_inverse_no_solution(self, service):
        """Test modular inverse when no solution exists"""
        with pytest.raises(ValueError):
            service.modular_inverse(2, 4)  # 2 and 4 are not coprime

    def test_chinese_remainder_inconsistent(self, service):
        """Test Chinese Remainder Theorem with inconsistent system"""
        congruences = [(2, 4), (4, 6)]  # x ≡ 2 mod 4, x ≡ 4 mod 6

        with pytest.raises(ValueError):
            service.chinese_remainder_theorem(congruences)

    def test_discrete_logarithm_no_solution(self, service):
        """Test discrete logarithm when no solution exists"""
        with pytest.raises(ValueError):
            service.discrete_logarithm(2, 3, 4)  # May not have solution

    def test_binomial_coefficient_invalid(self, service):
        """Test binomial coefficient with invalid parameters"""
        with pytest.raises(ValueError):
            service.binomial_coefficient(5, 7)  # k > n

    def test_factorial_large_number(self, service):
        """Test factorial with large number (should handle gracefully)"""
        request = NumberTheoryRequest(number=1000, operation="factorial")

        result = service.factorial(request)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "factorial"
        assert isinstance(result.result, int)

    def test_prime_factors_one(self, service):
        """Test prime factors of 1"""
        request = NumberTheoryRequest(number=1, operation="prime_factors")

        result = service.prime_factors(request)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "prime_factors"
        assert isinstance(result.result, dict)
        assert result.result["factors"] == {}

    def test_gcd_with_zero(self, service):
        """Test GCD with zero"""
        result = service.gcd(0, 12)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "gcd"
        assert result.result == 12

    def test_lcm_with_zero(self, service):
        """Test LCM with zero"""
        result = service.lcm(0, 12)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "lcm"
        assert result.result == 0

    def test_euler_totient_prime(self, service):
        """Test Euler's totient for prime number"""
        request = NumberTheoryRequest(number=7, operation="euler_totient")

        result = service.euler_totient(request)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "euler_totient"
        assert result.result == 6  # φ(7) = 6

    def test_euler_totient_prime_power(self, service):
        """Test Euler's totient for prime power"""
        request = NumberTheoryRequest(number=8, operation="euler_totient")  # 2^3

        result = service.euler_totient(request)

        assert isinstance(result, NumberTheoryResult)
        assert result.operation == "euler_totient"
        assert result.result == 4  # φ(8) = 4
