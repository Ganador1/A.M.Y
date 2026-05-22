"""Lightweight stub for libsbml to avoid heavy import during tests.
This provides minimal classes and constants often used by dependent libraries (e.g., cobra).
"""

# Common unit kind constants used by downstream code
UNIT_KIND_DIMENSIONLESS = 0
UNIT_KIND_MOLE = 1
UNIT_KIND_MOLECULE = 2
UNIT_KIND_MOLECULES = UNIT_KIND_MOLECULE
UNIT_KIND_GRAM = 3
UNIT_KIND_METRE = 4
UNIT_KIND_SECOND = 5
UNIT_KIND_ASECOND = 6
UNIT_KIND_MOLE_PER_MOLE = 7

class Unit:
    def __init__(self, kind=None, scale=0, multiplier=1, exponent=1):
        self.kind = kind
        self.scale = scale
        self.multiplier = multiplier
        self.exponent = exponent
    def __repr__(self):
        return f"Unit(kind={self.kind}, scale={self.scale}, multiplier={self.multiplier}, exponent={self.exponent})"

class SBase:
    def __init__(self):
        self.notes = None
        self.metaid = None

class UnitDefinition(SBase):
    def __init__(self, units=None):
        super().__init__()
        self.units = units or []
    def addUnit(self, unit):
        self.units.append(unit)
    def getListOfUnits(self):
        return self.units

class Species(SBase):
    def __init__(self, id=None, name=None):
        super().__init__()
        self.id = id
        self.name = name

class Compartment(SBase):
    def __init__(self, id=None, size=1.0):
        super().__init__()
        self.id = id
        self.size = size

class Model(SBase):
    def __init__(self):
        super().__init__()
        self.compartments = []
        self.species = []
    def createCompartment(self):
        comp = Compartment()
        self.compartments.append(comp)
        return comp
    def createSpecies(self):
        spc = Species()
        self.species.append(spc)
        return spc

class SBMLDocument:
    def __init__(self, level=3, version=1):
        self._level = level
        self._version = version
        self._model = None
    def createModel(self):
        self._model = SBMLModel()
        return self._model
    def getLevel(self):
        return self._level
    def getVersion(self):
        return self._version

class SBMLModel:
    def __init__(self):
        self._id = None
        self._name = None
    def setId(self, id_):
        self._id = id_
    def setName(self, name):
        self._name = name
    def getName(self):
        return self._name

# Minimal API to avoid ImportError
SBMLDocument = SBMLDocument
SBMLModel = SBMLModel
Model = SBMLModel  # compatibility alias expected by some libraries
Unit = Unit
