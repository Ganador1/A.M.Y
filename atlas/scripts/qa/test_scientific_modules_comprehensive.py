#!/usr/bin/env python3
"""
Comprehensive Scientific Modules Testing Script for AXIOM
Tests all scientific computing modules: Cryptography, Quantum Physics, Quantum Computing, and Computational Chemistry
"""

import sys
import os
import time
import json
from datetime import datetime

import pytest

# Import services
from app.services.cryptography import generate_rsa_keys, rsa_encrypt, rsa_decrypt
from app.domains.physics.quantum.quantum_physics_service import QuantumPhysicsService
from app.domains.physics.quantum.quantum_computing_service import QuantumComputingService
from app.domains.chemistry.computational.computational_chemistry_service import ComputationalChemistryService

def test_cryptography_module():
    """Test cryptography module with RSA operations"""
    # Test RSA key generation (use smaller key for faster testing)
    keys = generate_rsa_keys(128)  # Use very small key for fast testing

    # Test RSA encryption/decryption
    test_message = "Hello AXIOM!"
    encrypted = rsa_encrypt(keys["public_key"], test_message)
    decrypted = rsa_decrypt(keys["private_key"], encrypted)

    assert decrypted == test_message

def test_quantum_physics_module():
    """Test quantum physics module with various simulations"""
    service = QuantumPhysicsService()

    # Test spin evolution (simplified parameters for speed)
    params = {"Bx": 1.0, "By": 0.0, "Bz": 1.0, "t_max": 2.0, "n_points": 20}
    result = service.simulate_spin_evolution(params)
    assert "error" not in result

    # Test harmonic oscillator (simplified)
    params = {"omega": 1.0, "n_max": 3, "alpha": 1.0, "t_max": 5.0, "n_points": 50}
    result = service.simulate_harmonic_oscillator(params)
    assert "error" not in result

    # Test two-level system (simplified)
    params = {"omega": 1.0, "gamma": 0.1, "t_max": 5.0, "n_points": 50}
    result = service.simulate_two_level_system(params)
    assert "error" not in result

def test_quantum_computing_module():
    """Test quantum computing module with algorithms"""
    service = QuantumComputingService()

    # Test Bell state creation
    result = service.create_bell_state_qiskit()
    assert "error" not in result

    # Test Grover search
    result = service.create_grover_search_qiskit(2, "11")
    assert "error" not in result

    # Test Quantum Fourier Transform (simplified)
    result = service.create_quantum_fourier_transform_qiskit(2)  # Smaller QFT
    assert "error" not in result

def test_computational_chemistry_module():
    """Test computational chemistry module"""
    service = ComputationalChemistryService()

    # Test molecular analysis
    result = service.analyze_molecule("CCO")  # Ethanol
    assert "error" not in result

    # Test sequence analysis
    result = service.analyze_sequence("ATCGATCG", "dna")
    assert "error" not in result

    # Test protein sequence analysis
    result = service.analyze_sequence("MAKETLK", "protein")
    assert "error" not in result
