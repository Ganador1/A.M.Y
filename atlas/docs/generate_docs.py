#!/usr/bin/env python3
"""
Script para generar documentación con Sphinx

Usage:
    python generate_docs.py
    python generate_docs.py --clean  # Clean build first
"""

import os
import sys
import shutil
import argparse
from pathlib import Path

def clean_build(build_dir: str = "_build"):
    """Clean previous build"""
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        print(f"Cleaned {build_dir} directory")

def generate_docs():
    """Generate Sphinx documentation"""
    try:
        # Import sphinx
        from sphinx.cmd.build import build_main

        # Build arguments
        args = [
            '-b', 'html',      # Builder type
            '.',               # Source directory
            '_build/html',     # Output directory
            '-v'               # Verbose output
        ]

        print("Generating Sphinx documentation...")
        result = build_main(args)

        if result == 0:
            print("✅ Documentation generated successfully!")
            print("📖 Open docs/_build/html/index.html in your browser")
        else:
            print("❌ Documentation generation failed")
            sys.exit(1)

    except ImportError:
        print("❌ Sphinx is not installed. Please install with:")
        print("   pip install sphinx sphinx-rtd-theme")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error generating documentation: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Generate AXIOM ATLAS documentation")
    parser.add_argument('--clean', action='store_true', help='Clean build directory first')

    args = parser.parse_args()

    if args.clean:
        clean_build()

    generate_docs()

if __name__ == "__main__":
    main()
