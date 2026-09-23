#!/usr/bin/env python3
"""
Quick import fixes for the remaining failures
"""

import os

# Define specific fixes for failing imports
FIXES = [
    # Config loader issue
    {
        'pattern': 'from app.core.config.config_loader',
        'replacement': 'from app.core.config',
        'files': [
            'app/routers/scientific_hypothesis.py',
            'app/routers/research_cycle.py',
        ]
    },
    
    # Monitoring trace missing
    {
        'pattern': 'from app.monitoring.trace import init_tracing',
        'replacement': '# from app.monitoring.trace import init_tracing  # Module not available',
        'files': ['main.py']
    },
    
    # Missing scrape function
    {
        'pattern': 'from app.monitoring.metrics import scrape as prometheus_scrape',
        'replacement': '# from app.monitoring.metrics import scrape as prometheus_scrape  # Function not available',
        'files': ['main.py']  
    },
    
    # Fix biomechanical models import
    {
        'pattern': 'from app.biomechanical_models',
        'replacement': 'from app.domains.medicine.imaging.biomechanical_models',
'files': ['app/domains/medicine/imaging/cardiac_region_models.py']
    },
    
    # Fix cross validation matrix import
    {
        'pattern': 'from app.cross_validation_matrix',
        'replacement': 'from app.validation.cross_validation_matrix',
        'files': [
            'app/validation/operational_cross_validation_matrix.py',
            'app/validation/validation_matrix_persistence.py',
            'app/routers/validation_matrix.py'
        ]
    },
    
    # Fix operational cross validation matrix import  
    {
        'pattern': 'from app.operational_cross_validation_matrix',
        'replacement': 'from app.validation.operational_cross_validation_matrix', 
        'files': ['app/infrastructure/service_registry_discovery.py']
    },
]

def apply_fixes():
    """Apply the import fixes"""
    fixed_count = 0
    
    for fix in FIXES:
        pattern = fix['pattern']
        replacement = fix['replacement']
        files = fix['files']
        
        for file_path in files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    if pattern in content:
                        new_content = content.replace(pattern, replacement)
                        with open(file_path, 'w') as f:
                            f.write(new_content)
                        print(f"✅ Fixed {file_path}: {pattern}")
                        fixed_count += 1
                    else:
                        print(f"⚠️  Pattern not found in {file_path}: {pattern}")
                        
                except Exception as e:
                    print(f"❌ Error fixing {file_path}: {e}")
            else:
                print(f"⚠️  File not found: {file_path}")
    
    print(f"\n🎯 Applied {fixed_count} import fixes")

if __name__ == "__main__":
    apply_fixes()
