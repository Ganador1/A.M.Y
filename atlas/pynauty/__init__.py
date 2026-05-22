class Graph:
    def __init__(self, n, directed=False):
        self.n = n
        self.directed = directed
        self.adj = {i: set() for i in range(n)}

    def add_edge(self, a, b):
        self.adj[a].add(b)
        if not self.directed:
            self.adj[b].add(a)


def certificate(graph):
    # A trivial canonicalization: return sorted degree sequence string
    degrees = sorted([len(graph.adj[i]) for i in range(graph.n)])
    return "-".join(map(str, degrees))
