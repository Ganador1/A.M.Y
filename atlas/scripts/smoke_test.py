import importlib
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_smoke_test():
    mods = [
        'app.models.database_models',
        'app.services.hypothesis_persistence',
        'app.routers.hypothesis_persistence',
    ]
    print(f"Testing imports for: {mods}")
    for m in mods:
        try:
            importlib.import_module(m)
            print(f"✅ Imported {m}")
        except Exception as e:
            print(f"❌ Failed to import {m}: {e}")
            sys.exit(1)
    print('OK')

if __name__ == "__main__":
    run_smoke_test()
