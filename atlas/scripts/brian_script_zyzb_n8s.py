# Wed Oct 29 18:34:18 2025
# Run as: _temp_materialsloop_runner.py


import json
from app.autonomous.pipelines.materials_loop import MaterialsLoop

loop = MaterialsLoop()
try:
    result = loop.run_iteration(iteration=1, limit=5)
except TypeError:
    try:
        result = loop.run_iteration(limit=5)
    except TypeError:
        try:
            result = loop.run_iteration(1)
        except TypeError:
            result = loop.run_iteration()
print(json.dumps(result, default=str))
