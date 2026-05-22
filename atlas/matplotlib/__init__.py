# Lightweight stub for matplotlib package to speed up tests and avoid heavy installs
# Only provides the submodules/tests import (e.g., pyplot) and minimal API used at import-time
__all__ = ["pyplot", "use", "rcParams"]
from . import pyplot as pyplot

# Minimal backend setter used by code that calls matplotlib.use('Agg')
def use(backend):
    # no-op: tests only need the call not actual rendering
    return None

# Minimal configuration mapping
rcParams = {}
