class Network:
    def __init__(self, directed=False):
        self.directed = directed
        self.nodes = []
        self.edges = []

    def add_node(self, node, **kwargs):
        self.nodes.append((node, kwargs))

    def add_edge(self, a, b, **kwargs):
        self.edges.append((a, b, kwargs))

    def write_html(self, path):
        # Minimal stub: write a tiny HTML
        with open(path, 'w') as f:
            f.write("<html><body>pyvis network stub</body></html>")
