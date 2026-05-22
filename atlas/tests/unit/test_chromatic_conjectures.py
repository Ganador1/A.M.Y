import sys
import json
import hashlib
sys.path.append('./app')

from app.mathlab.conjectures.chromatic_graphs import ChromaticConjecturePlugin
from app.mathlab.core.object_models import MathematicalObject

def test_complete_graph():
    # Grafo completo K4
    payload = {
        "type": "graph",
        "directed": False,
        "nodes": [0, 1, 2, 3],
        "edges": [[0,1], [0,2], [0,3], [1,2], [1,3], [2,3]]
    }
    semantic_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    obj = MathematicalObject(id="k4", type="graph", semantic_hash=semantic_hash, payload_json=payload)
    plugin = ChromaticConjecturePlugin()
    
    conjectures = plugin.generate_conjectures(obj)
    print("Conjectures for K4:", conjectures)
    
    brooks_result = plugin.test_conjecture(obj, "brooks")
    print("Brooks test:", brooks_result)
    
    assert brooks_result["verified"] == True
    assert any("completo" in c for c in conjectures)

def test_odd_cycle():
    # Ciclo impar C5
    payload = {
        "type": "graph",
        "directed": False,
        "nodes": [0, 1, 2, 3, 4],
        "edges": [[0,1], [1,2], [2,3], [3,4], [4,0]]
    }
    semantic_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    obj = MathematicalObject(id="c5", type="graph", semantic_hash=semantic_hash, payload_json=payload)
    plugin = ChromaticConjecturePlugin()
    
    conjectures = plugin.generate_conjectures(obj)
    print("Conjectures for C5:", conjectures)
    
    brooks_result = plugin.test_conjecture(obj, "brooks")
    print("Brooks test:", brooks_result)
    
    assert brooks_result["verified"] == True
    assert any("ciclo impar" in c for c in conjectures)

def test_mycielski():
    plugin = ChromaticConjecturePlugin()
    payload, desc = plugin.generate_mycielski_graph(3)
    print("Mycielski description:", desc)
    
    semantic_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    obj = MathematicalObject(id="mycielski3", type="graph", semantic_hash=semantic_hash, payload_json=payload)
    
    conjectures = plugin.generate_conjectures(obj)
    print("Conjectures for Mycielski 3:", conjectures)
    
    vizing_result = plugin.test_conjecture(obj, "vizing")
    print("Vizing test:", vizing_result)
    
    assert "sin triángulos" in desc
    assert vizing_result["verified"] == True

def test_perfect_graph():
    # Grafo no perfecto, e.g., C5
    payload = {
        "type": "graph",
        "directed": False,
        "nodes": [0, 1, 2, 3, 4],
        "edges": [[0,1], [1,2], [2,3], [3,4], [4,0]]
    }
    semantic_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    obj = MathematicalObject(id="c5", type="graph", semantic_hash=semantic_hash, payload_json=payload)
    plugin = ChromaticConjecturePlugin()
    
    result = plugin.test_conjecture(obj, "perfect_graph")
    print("Perfect graph test for C5:", result)
    
    assert result["verified"] == False  # C5 has chi=3, omega=2

if __name__ == "__main__":
    test_complete_graph()
    test_odd_cycle()
    test_mycielski()
    test_perfect_graph()
    print("All tests passed!")