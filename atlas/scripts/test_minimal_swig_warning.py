try:
    from openbabel import openbabel
    print("OpenBabel importado sin warnings SWIG")
except ImportError:
    print("OpenBabel no disponible")
