import warnings
try:
    from openbabel import openbabel
    print("OpenBabel importado")
except ImportError:
    print("OpenBabel no disponible")
    
try:
    from pymatgen.core import Structure
    print("PyMatGen importado")
except ImportError:
    print("PyMatGen no disponible")
