#!/usr/bin/env python3
"""
Standalone test runner for fuzz tests that don't require full app context.
"""

import sys
import os

# Add tests directory to path
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == '__main__':
    import pytest
    # Run without loading conftest that imports main.py
    sys.exit(pytest.main([
        'tests/fuzz/test_api_input_validation_fuzz.py',
        '-v',
        '--tb=short',
        '-o', 'python_files=test_*.py',
        '-o', 'python_classes=Test*',
        '-o', 'python_functions=test_*',
        '--override-ini=testpaths=tests/fuzz',
        '-p', 'no:warnings',
        '--no-header'
    ]))
