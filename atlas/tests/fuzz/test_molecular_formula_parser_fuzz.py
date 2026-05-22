"""
Fuzz Testing for Molecular Formula Parser

This module provides comprehensive fuzz testing for molecular formula parsers,
including SMILES (Simplified Molecular Input Line Entry System) and InChI
(International Chemical Identifier) formats.

Test Categories:
1. Random string injection
2. Valid character fuzzing
3. Edge case detection
4. Malformed input handling
5. Security testing
6. Performance testing

Author: Atlas AI Mathematics System
Date: October 2025
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from hypothesis import HealthCheck
import string
import time


class MolecularFormulaParser:
    """
    Mock molecular formula parser for testing purposes.
    
    In production, this would be replaced with actual RDKit or similar
    chemistry library integration.
    """
    
    def __init__(self):
        self.supported_atoms = {
            'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
            'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca',
            'Br', 'I', 'Fe', 'Cu', 'Zn', 'Ag', 'Au', 'Pt'
        }
        self.smiles_special_chars = set('()[]=#@+-\\/')
        self.inchi_prefix = 'InChI='
    
    def parse_smiles(self, smiles: str) -> dict:
        """
        Parse SMILES notation.
        
        Args:
            smiles: SMILES string representation
            
        Returns:
            dict: Parsed structure information
            
        Raises:
            ValueError: If SMILES is invalid
        """
        if not isinstance(smiles, str):
            raise TypeError("SMILES must be a string")
        
        if not smiles:
            raise ValueError("SMILES cannot be empty")
        
        if len(smiles) > 10000:
            raise ValueError("SMILES too long (max 10000 characters)")
        
        # Basic validation
        if any(c.isspace() for c in smiles):
            raise ValueError("SMILES cannot contain whitespace")
        
        # Check for balanced parentheses
        if smiles.count('(') != smiles.count(')'):
            raise ValueError("Unbalanced parentheses in SMILES")
        
        if smiles.count('[') != smiles.count(']'):
            raise ValueError("Unbalanced brackets in SMILES")
        
        return {
            'type': 'smiles',
            'valid': True,
            'length': len(smiles),
            'has_rings': any(c.isdigit() for c in smiles),
            'has_branches': '(' in smiles
        }
    
    def parse_inchi(self, inchi: str) -> dict:
        """
        Parse InChI notation.
        
        Args:
            inchi: InChI string representation
            
        Returns:
            dict: Parsed structure information
            
        Raises:
            ValueError: If InChI is invalid
        """
        if not isinstance(inchi, str):
            raise TypeError("InChI must be a string")
        
        if not inchi:
            raise ValueError("InChI cannot be empty")
        
        if not inchi.startswith(self.inchi_prefix):
            raise ValueError("InChI must start with 'InChI='")
        
        if len(inchi) > 10000:
            raise ValueError("InChI too long (max 10000 characters)")
        
        # Extract version and layers
        parts = inchi[len(self.inchi_prefix):].split('/')
        if not parts:
            raise ValueError("Invalid InChI format")
        
        return {
            'type': 'inchi',
            'valid': True,
            'version': parts[0] if parts else None,
            'layers': len(parts) - 1 if len(parts) > 1 else 0
        }
    
    def parse_molecular_formula(self, formula: str) -> dict:
        """
        Parse simple molecular formula (e.g., H2O, C6H12O6).
        
        Args:
            formula: Molecular formula string
            
        Returns:
            dict: Parsed composition
            
        Raises:
            ValueError: If formula is invalid
        """
        if not isinstance(formula, str):
            raise TypeError("Formula must be a string")
        
        if not formula:
            raise ValueError("Formula cannot be empty")
        
        if len(formula) > 1000:
            raise ValueError("Formula too long (max 1000 characters)")
        
        # Basic validation: should start with capital letter
        if not formula[0].isupper():
            raise ValueError("Formula must start with uppercase element symbol")
        
        # Parse atoms and counts
        atoms = {}
        i = 0
        while i < len(formula):
            if formula[i].isupper():
                atom = formula[i]
                i += 1
                
                # Check for second lowercase letter
                if i < len(formula) and formula[i].islower():
                    atom += formula[i]
                    i += 1
                
                # Check for count
                count_str = ''
                while i < len(formula) and formula[i].isdigit():
                    count_str += formula[i]
                    i += 1
                
                count = int(count_str) if count_str else 1
                atoms[atom] = atoms.get(atom, 0) + count
            else:
                raise ValueError(f"Invalid character at position {i}")
        
        return {
            'type': 'formula',
            'valid': True,
            'atoms': atoms,
            'total_atoms': sum(atoms.values())
        }


# Test fixtures
@pytest.fixture
def parser():
    return MolecularFormulaParser()


class TestSMILESFuzzing:
    """Fuzz tests for SMILES parser."""
    
    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_random_strings_dont_crash(self, random_string):
        """SMILES parser should handle random strings without crashing."""
        parser = MolecularFormulaParser()
        try:
            result = parser.parse_smiles(random_string)
            assert isinstance(result, dict)
        except (ValueError, TypeError) as e:
            # Expected exceptions for invalid input
            assert str(e)
    
    @given(st.text(alphabet=string.ascii_letters + string.digits + '()[]=#@', min_size=1, max_size=50))
    @settings(max_examples=200)
    def test_valid_smiles_characters(self, smiles_string):
        """Test with valid SMILES character set."""
        parser = MolecularFormulaParser()
        try:
            result = parser.parse_smiles(smiles_string)
            assert isinstance(result, dict)
            assert result['type'] == 'smiles'
        except ValueError as e:
            # Unbalanced brackets/parentheses are expected
            assert 'balanced' in str(e).lower() or 'empty' in str(e).lower()
    
    @given(st.integers(min_value=0, max_value=20))
    @settings(max_examples=100)
    def test_nested_parentheses(self, depth):
        """Test SMILES with nested parentheses."""
        parser = MolecularFormulaParser()
        smiles = 'C' + '(' * depth + 'C' + ')' * depth
        try:
            result = parser.parse_smiles(smiles)
            assert result['has_branches'] == (depth > 0)
        except ValueError:
            pass
    
    @given(st.lists(st.sampled_from(['C', 'N', 'O', 'S', 'P']), min_size=1, max_size=20))
    @settings(max_examples=100)
    def test_atom_sequences(self, atoms):
        """Test sequences of valid atoms."""
        parser = MolecularFormulaParser()
        smiles = ''.join(atoms)
        result = parser.parse_smiles(smiles)
        assert result['valid']
        assert result['length'] == len(smiles)
    
    @given(st.text(alphabet=string.whitespace, min_size=1, max_size=10))
    @settings(max_examples=50)
    def test_whitespace_rejection(self, whitespace):
        """SMILES should reject whitespace."""
        parser = MolecularFormulaParser()
        smiles = f"C{whitespace}C"
        with pytest.raises(ValueError, match="whitespace"):
            parser.parse_smiles(smiles)
    
    @given(st.integers(min_value=10001, max_value=20000))
    @settings(max_examples=50)
    def test_length_limits(self, length):
        """Test SMILES length validation."""
        parser = MolecularFormulaParser()
        smiles = 'C' * length
        with pytest.raises(ValueError, match="too long"):
            parser.parse_smiles(smiles)


class TestInChIFuzzing:
    """Fuzz tests for InChI parser."""
    
    @given(st.text(min_size=1, max_size=100))
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_random_strings_dont_crash(self, random_string):
        """InChI parser should handle random strings without crashing."""
        parser = MolecularFormulaParser()
        try:
            result = parser.parse_inchi(random_string)
            assert isinstance(result, dict)
        except (ValueError, TypeError) as e:
            assert str(e)
    
    @given(st.text(alphabet=string.ascii_letters + string.digits + '/-', min_size=1, max_size=50))
    @settings(max_examples=200)
    def test_valid_inchi_characters(self, inchi_body):
        """Test with valid InChI character set."""
        parser = MolecularFormulaParser()
        inchi = f"InChI={inchi_body}"
        try:
            result = parser.parse_inchi(inchi)
            assert isinstance(result, dict)
            assert result['type'] == 'inchi'
        except ValueError:
            pass
    
    @given(st.lists(st.text(alphabet=string.ascii_uppercase, min_size=1, max_size=10), min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_inchi_layers(self, layers):
        """Test InChI with various layer combinations."""
        parser = MolecularFormulaParser()
        inchi = "InChI=1S/" + "/".join(layers)
        try:
            result = parser.parse_inchi(inchi)
            assert result['layers'] >= 0
        except ValueError:
            pass
    
    def test_missing_prefix(self):
        """InChI must start with 'InChI=' prefix."""
        parser = MolecularFormulaParser()
        with pytest.raises(ValueError, match="must start with"):
            parser.parse_inchi("1S/C6H12O6/c7-1-2-3(8)4(9)5(10)6(11)12-2")
    
    @given(st.integers(min_value=10001, max_value=20000))
    @settings(max_examples=50)
    def test_length_limits(self, length):
        """Test InChI length validation."""
        parser = MolecularFormulaParser()
        inchi = "InChI=" + 'C' * length
        with pytest.raises(ValueError, match="too long"):
            parser.parse_inchi(inchi)


class TestMolecularFormulaFuzzing:
    """Fuzz tests for molecular formula parser."""
    
    @given(st.text(min_size=1, max_size=50))
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_random_strings_dont_crash(self, random_string):
        """Formula parser should handle random strings without crashing."""
        parser = MolecularFormulaParser()
        try:
            result = parser.parse_molecular_formula(random_string)
            assert isinstance(result, dict)
        except (ValueError, TypeError) as e:
            assert str(e)
    
    @given(st.lists(
        st.tuples(
            st.sampled_from(['H', 'C', 'N', 'O', 'S', 'P', 'Cl', 'Br']),
            st.integers(min_value=1, max_value=20)
        ),
        min_size=1,
        max_size=10
    ))
    @settings(max_examples=150)
    def test_valid_formulas(self, atom_counts):
        """Test with valid atomic compositions."""
        parser = MolecularFormulaParser()
        formula = ''.join(f"{atom}{count if count > 1 else ''}" for atom, count in atom_counts)
        try:
            result = parser.parse_molecular_formula(formula)
            assert result['valid']
            assert result['total_atoms'] > 0
        except ValueError:
            pass
    
    @given(st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=20))
    @settings(max_examples=100)
    def test_lowercase_rejection(self, lowercase_string):
        """Formulas starting with lowercase should be rejected."""
        parser = MolecularFormulaParser()
        with pytest.raises(ValueError, match="must start with uppercase"):
            parser.parse_molecular_formula(lowercase_string)
    
    @given(st.integers(min_value=1001, max_value=2000))
    @settings(max_examples=50)
    def test_length_limits(self, length):
        """Test formula length validation."""
        parser = MolecularFormulaParser()
        formula = 'C' * length
        with pytest.raises(ValueError, match="too long"):
            parser.parse_molecular_formula(formula)
    
    @given(st.text(alphabet=string.punctuation, min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_special_character_rejection(self, special_chars):
        """Formulas with special characters should be rejected."""
        parser = MolecularFormulaParser()
        formula = f"C{special_chars}H"
        with pytest.raises(ValueError):
            parser.parse_molecular_formula(formula)


class TestSecurityFuzzing:
    """Security-focused fuzz tests."""
    
    @given(st.text(alphabet=string.printable, min_size=1, max_size=100))
    @settings(max_examples=150, suppress_health_check=[HealthCheck.too_slow])
    def test_injection_attempts(self, malicious_input):
        """Test resistance to injection attacks."""
        parser = MolecularFormulaParser()
        
        # Test all parsers with potentially malicious input
        parsers = [
            parser.parse_smiles,
            parser.parse_inchi,
            parser.parse_molecular_formula
        ]
        
        for parse_func in parsers:
            try:
                result = parse_func(malicious_input)
                # If it parses, verify it returns safe data types
                assert isinstance(result, dict)
                assert all(isinstance(k, str) for k in result.keys())
            except (ValueError, TypeError):
                # Expected for invalid input
                pass
    
    @given(st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_repeated_parsing(self, inputs):
        """Test parser stability with repeated calls."""
        parser = MolecularFormulaParser()
        
        for inp in inputs:
            try:
                parser.parse_smiles(inp)
            except (ValueError, TypeError):
                pass
        
        # Parser should still be functional
        result = parser.parse_smiles('CCO')
        assert result['valid']
    
    @given(st.binary(min_size=1, max_size=100))
    @settings(max_examples=100)
    def test_binary_input_handling(self, binary_data):
        """Test handling of binary data (should fail gracefully)."""
        parser = MolecularFormulaParser()
        
        try:
            # Try to decode as UTF-8
            text = binary_data.decode('utf-8', errors='ignore')
            if text:
                parser.parse_smiles(text)
        except (ValueError, TypeError, UnicodeDecodeError):
            pass


class TestPerformanceFuzzing:
    """Performance-focused fuzz tests."""
    
    @given(st.integers(min_value=10, max_value=1000))
    @settings(max_examples=50, deadline=5000)
    def test_smiles_performance_scaling(self, size):
        """Test SMILES parsing performance with increasing size."""
        parser = MolecularFormulaParser()
        smiles = 'C' * size
        
        start = time.perf_counter()
        try:
            result = parser.parse_smiles(smiles)
            elapsed = time.perf_counter() - start
            
            # Should complete in reasonable time
            assert elapsed < 1.0, f"Parsing took {elapsed:.3f}s for {size} chars"
        except ValueError:
            pass
    
    @given(st.integers(min_value=10, max_value=500))
    @settings(max_examples=50, deadline=5000)
    def test_formula_performance_scaling(self, size):
        """Test formula parsing performance with increasing complexity."""
        parser = MolecularFormulaParser()
        # Create complex formula
        formula = ''.join(f"C{i}" for i in range(1, size))
        
        start = time.perf_counter()
        try:
            result = parser.parse_molecular_formula(formula)
            elapsed = time.perf_counter() - start
            
            # Should complete in reasonable time
            assert elapsed < 1.0, f"Parsing took {elapsed:.3f}s for formula size {len(formula)}"
        except ValueError:
            pass


class TestEdgeCases:
    """Edge case fuzz tests."""
    
    def test_empty_string(self):
        """Test empty string handling."""
        parser = MolecularFormulaParser()
        
        with pytest.raises(ValueError, match="cannot be empty"):
            parser.parse_smiles('')
        
        with pytest.raises(ValueError, match="cannot be empty"):
            parser.parse_inchi('')
        
        with pytest.raises(ValueError, match="cannot be empty"):
            parser.parse_molecular_formula('')
    
    @given(st.none())
    @settings(max_examples=10)
    def test_none_input(self, none_value):
        """Test None input handling."""
        parser = MolecularFormulaParser()
        
        with pytest.raises(TypeError):
            parser.parse_smiles(none_value)
    
    @given(st.integers() | st.floats() | st.booleans())
    @settings(max_examples=100)
    def test_non_string_types(self, non_string):
        """Test non-string input handling."""
        parser = MolecularFormulaParser()
        
        with pytest.raises(TypeError):
            parser.parse_smiles(non_string)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--hypothesis-show-statistics'])
