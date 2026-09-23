from __future__ import annotations

from typing import Dict, Any, List, Tuple
import networkx as nx
import numpy as np
from app.mathlab.core.object_models import MathematicalObject
from app.mathlab.invariants.graph_invariants import GraphInvariants

class ChromaticConjecturePlugin:
    """Plugin para generar y probar conjeturas sobre propiedades cromáticas de grafos."""

    def __init__(self):
        self.invariants = GraphInvariants()
        self.theorems = {
            "brooks": "El teorema de Brooks establece que para cualquier grafo conexo G que no es un grafo completo o un ciclo impar, χ(G) ≤ Δ(G), donde Δ(G) es el grado máximo.",
            "vizing": "El teorema de Vizing establece que el índice cromático χ'(G) de un grafo simple es Δ(G) o Δ(G) + 1.",
            "hadwiger": "La conjetura de Hadwiger establece que si un grafo G no tiene un Kₙ₊₁ como menor, entonces χ(G) ≤ n.",
            "mycielski": "La construcción de Mycielski permite crear grafos con número cromático k+1 sin triángulos a partir de grafos con número cromático k."
        }

    def generate_conjectures(self, obj: MathematicalObject) -> List[str]:
        """Genera conjeturas posibles basadas en invariantes del grafo."""
        inv = self.invariants.compute(obj)
        conjectures = []

        # Convertir a grafo NetworkX para análisis
        G = self._to_networkx(obj)
        
        # Conjetura sobre número cromático y clique
        if 'clique_number_approx' in inv and 'chromatic_number_approx' in inv:
            omega = inv['clique_number_approx']
            chi = inv['chromatic_number_approx']
            if omega == chi:
                conjectures.append(f"El grafo es perfecto: χ(G) = ω(G) = {chi}")
            else:
                conjectures.append(f"El número cromático χ(G) = {chi} es mayor que el tamaño de la clique máxima ω(G) = {omega}")

        # Conjetura basada en el teorema de Brooks
        if 'chromatic_number_approx' in inv and G.number_of_nodes() > 0:
            delta = max([d for _, d in G.degree()]) if G.number_of_edges() > 0 else 0
            chi = inv['chromatic_number_approx']
            
            is_complete = nx.density(G) == 1.0
            is_odd_cycle = (G.number_of_nodes() % 2 == 1 and 
                           all(d == 2 for _, d in G.degree()) and 
                           nx.is_connected(G))
            
            if is_complete:
                conjectures.append(f"El grafo es completo, por lo que χ(G) = n = {G.number_of_nodes()}")
            elif is_odd_cycle:
                conjectures.append(f"El grafo es un ciclo impar, por lo que χ(G) = 3")
            elif chi <= delta:
                conjectures.append(f"Cumple el teorema de Brooks: χ(G) = {chi} ≤ Δ(G) = {delta}")
            else:
                conjectures.append(f"Caso especial: χ(G) = {chi} > Δ(G) = {delta}")

        # Conjetura sobre coloración de aristas (índice cromático)
        if G.number_of_edges() > 0:
            try:
                edge_coloring = nx.greedy_color(nx.line_graph(G))
                edge_chromatic_number = max(edge_coloring.values()) + 1
                delta = max([d for _, d in G.degree()])
                
                if edge_chromatic_number == delta:
                    conjectures.append(f"El grafo es de Clase 1: χ'(G) = Δ(G) = {delta}")
                elif edge_chromatic_number == delta + 1:
                    conjectures.append(f"El grafo es de Clase 2: χ'(G) = Δ(G) + 1 = {delta + 1}")
                else:
                    conjectures.append(f"Anomalía en coloración de aristas: χ'(G) = {edge_chromatic_number}")
            except Exception:
                pass  # Ignorar errores en cálculo de coloración de aristas

        # Conjetura sobre número de independencia
        if 'independence_number_approx' in inv and 'n' in inv:
            alpha = inv['independence_number_approx']
            n = inv['n']
            conjectures.append(f"El número de independencia α(G) = {alpha}, lo que cubre {alpha/n:.2f} del grafo")

        return conjectures

    def test_conjecture(self, obj: MathematicalObject, conjecture_id: str) -> Dict[str, Any]:
        """Prueba una conjetura específica y devuelve resultados."""
        G = self._to_networkx(obj)
        inv = self.invariants.compute(obj)
        
        results = {"conjecture_id": conjecture_id, "verified": False, "explanation": "", "counterexample": None}
        
        if conjecture_id == "brooks":
            # Probar el teorema de Brooks
            if G.number_of_nodes() == 0:
                results["verified"] = True
                results["explanation"] = "Grafo vacío, el teorema no aplica."
                return results
                
            delta = max([d for _, d in G.degree()]) if G.number_of_edges() > 0 else 0
            chi = inv.get('chromatic_number_approx', 0)
            
            is_complete = nx.density(G) == 1.0
            is_odd_cycle = (G.number_of_nodes() % 2 == 1 and 
                           all(d == 2 for _, d in G.degree()) and 
                           nx.is_connected(G))
            
            if is_complete or is_odd_cycle:
                results["verified"] = True
                results["explanation"] = "El grafo es completo o un ciclo impar, excepciones válidas al teorema."
            elif chi <= delta:
                results["verified"] = True
                results["explanation"] = f"Cumple el teorema: χ(G) = {chi} ≤ Δ(G) = {delta}"
            else:
                results["verified"] = False
                results["explanation"] = f"Viola el teorema: χ(G) = {chi} > Δ(G) = {delta}"
                results["counterexample"] = obj.id
                
        elif conjecture_id == "vizing":
            # Probar el teorema de Vizing
            if G.number_of_edges() == 0:
                results["verified"] = True
                results["explanation"] = "Grafo sin aristas, el teorema no aplica."
                return results
                
            try:
                edge_coloring = nx.greedy_color(nx.line_graph(G))
                edge_chromatic_number = max(edge_coloring.values()) + 1
                delta = max([d for _, d in G.degree()])
                
                if edge_chromatic_number <= delta + 1:
                    results["verified"] = True
                    results["explanation"] = f"Cumple el teorema: χ'(G) = {edge_chromatic_number} ≤ Δ(G) + 1 = {delta + 1}"
                else:
                    results["verified"] = False
                    results["explanation"] = f"Viola el teorema: χ'(G) = {edge_chromatic_number} > Δ(G) + 1 = {delta + 1}"
                    results["counterexample"] = obj.id
            except Exception as e:
                results["verified"] = None
                results["explanation"] = f"Error al calcular: {str(e)}"
                
        elif conjecture_id == "perfect_graph":
            # Probar si el grafo es perfecto (χ(H) = ω(H) para todo subgrafo inducido H)
            if 'clique_number_approx' in inv and 'chromatic_number_approx' in inv:
                omega = inv['clique_number_approx']
                chi = inv['chromatic_number_approx']
                
                if omega == chi:
                    # Verificación aproximada - para ser riguroso habría que verificar todos los subgrafos inducidos
                    results["verified"] = True
                    results["explanation"] = f"Posiblemente perfecto: χ(G) = ω(G) = {chi}"
                else:
                    results["verified"] = False
                    results["explanation"] = f"No es perfecto: χ(G) = {chi} > ω(G) = {omega}"
            else:
                results["verified"] = None
                results["explanation"] = "No se pudieron calcular los invariantes necesarios."
        
        return results
    
    def get_theorem_description(self, theorem_id: str) -> str:
        """Devuelve la descripción de un teorema por su ID."""
        return self.theorems.get(theorem_id, "Teorema no encontrado")
    
    def _to_networkx(self, obj: MathematicalObject) -> nx.Graph:
        """Convierte un objeto matemático de grafo a un grafo NetworkX."""
        payload = obj.payload_json
        directed = bool(payload.get("directed", False))
        G = nx.DiGraph() if directed else nx.Graph()
        
        nodes = payload.get("nodes")
        if nodes is not None:
            G.add_nodes_from(nodes)
            
        for u, v in payload.get("edges", []):
            G.add_edge(u, v)
            
        return G
    
    def generate_mycielski_graph(self, k: int) -> Tuple[Dict[str, Any], str]:
        """
        Genera un grafo de Mycielski con número cromático k y sin triángulos.
        
        Args:
            k: Número cromático deseado (k ≥ 2)
            
        Returns:
            Tuple con el payload del grafo y una descripción
        """
        if k < 2:
            raise ValueError("El número cromático debe ser al menos 2")
            
        # Empezar con K₂ (número cromático 2)
        if k == 2:
            G = nx.Graph()
            G.add_edge(0, 1)
            description = "Grafo K₂ con número cromático 2"
        else:
            # Generar grafo de Mycielski recursivamente
            G_prev = self.generate_mycielski_graph(k-1)[0]
            G_prev_nx = nx.Graph()
            for u, v in G_prev.get("edges", []):
                G_prev_nx.add_edge(u, v)
                
            # Aplicar construcción de Mycielski
            G = nx.mycielskian(G_prev_nx)
            description = f"Grafo de Mycielski con número cromático {k} y sin triángulos"
        
        # Convertir a formato de payload
        nodes = list(G.nodes())
        edges = [[u, v] for u, v in G.edges()]
        payload = {"type": "graph", "directed": False, "nodes": nodes, "edges": edges}
        
        return payload, description