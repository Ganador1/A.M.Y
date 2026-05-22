#!/bin/bash
#
# Meta 4 Dependencies Installation Script
# AXIOM AI - Advanced Scientific Computing Enhancement
#

echo "🔬 Installing Meta 4 Scientific Computing Dependencies..."

# Activate virtual environment
source .venv/bin/activate

echo "📦 Installing core scientific computing libraries..."

# Chemistry Computing Dependencies
echo "🧪 Installing Chemistry Computing dependencies..."
pip install pymatgen==2024.8.9 --no-cache-dir --timeout=60
pip install cobra==0.29.0 --no-cache-dir --timeout=60

# Physics Computing Dependencies  
echo "🔬 Installing Physics Computing dependencies..."
pip install astropy==6.1.0 --no-cache-dir --timeout=60
pip install yt==4.3.1 --no-cache-dir --timeout=60

# Biology Computing Dependencies
echo "🧬 Installing Biology Computing dependencies..."
pip install brian2==2.7.1 --no-cache-dir --timeout=60

# Additional Scientific Computing
echo "🔬 Installing additional scientific tools..."
pip install ase==3.23.0 --no-cache-dir --timeout=60

echo "✅ Meta 4 dependencies installation completed!"

# Verify installations
echo "🔍 Verifying installations..."
python -c "
import sys
dependencies = [
    'pymatgen', 'cobra', 'astropy', 'yt', 'brian2', 'ase'
]

missing = []
for dep in dependencies:
    try:
        __import__(dep)
        print(f'✅ {dep} - OK')
    except ImportError:
        print(f'❌ {dep} - MISSING')
        missing.append(dep)

if missing:
    print(f'\n⚠️  Missing dependencies: {missing}')
    sys.exit(1)
else:
    print('\n🎉 All Meta 4 dependencies installed successfully!')
"

echo "🚀 AXIOM is now ready for advanced scientific computing!"
