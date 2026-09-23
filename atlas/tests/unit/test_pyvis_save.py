import networkx as nx
from pyvis.network import Network
import os

def test_pyvis_save():
    G = nx.Graph()
    G.add_node(1)
    G.add_node(2)
    G.add_edge(1, 2)

    net = Network(notebook=False, height="750px", width="100%")
    net.from_nx(G)

    output_dir = "static/graphs"
    os.makedirs(output_dir, exist_ok=True)

    file_name = "test_graph.html"
    full_path = os.path.join(os.getcwd(), output_dir, file_name)

    try:
        net.save_graph(full_path)
        print(f"Graph saved successfully to: {full_path}")
    except Exception as e:
        print(f"Error saving graph: {e}")

if __name__ == "__main__":
    test_pyvis_save()
