"""
Combinatorics Service
Servicio para cálculos de combinatoria
"""

import math
from typing import Dict, Any, List

class CombinatoricsService:
    """Servicio para operaciones de combinatoria"""

    @staticmethod
    def permutations(n: int, k: int) -> Dict[str, Any]:
        """
        Calcula el número de permutaciones de k elementos de un conjunto de n elementos.
        P(n, k) = n! / (n - k)!
        """
        if k < 0 or k > n:
            raise ValueError("k debe ser mayor o igual a 0 y menor o igual a n")
        
        result = math.perm(n, k)
        return {
            "n": n,
            "k": k,
            "operation": "permutations",
            "result": result,
            "formula": "P(n, k) = n! / (n - k)!"
        }

    @staticmethod
    def combinations(n: int, k: int) -> Dict[str, Any]:
        """
        Calcula el número de combinaciones de k elementos de un conjunto de n elementos.
        C(n, k) = n! / (k! * (n - k)!)
        """
        if k < 0 or k > n:
            raise ValueError("k debe ser mayor o igual a 0 y menor o igual a n")
        
        result = math.comb(n, k)
        return {
            "n": n,
            "k": k,
            "operation": "combinations",
            "result": result,
            "formula": "C(n, k) = n! / (k! * (n - k)!)"
        }

    @staticmethod
    def get_combinatorics_examples() -> List[Dict]:
        """
        Devuelve ejemplos de operaciones de combinatoria
        """
        return [
            {
                "operation": "permutations",
                "n": 5,
                "k": 2,
                "description": "Permutaciones de 2 elementos de un conjunto de 5"
            },
            {
                "operation": "combinations",
                "n": 5,
                "k": 2,
                "description": "Combinaciones de 2 elementos de un conjunto de 5"
            }
        ]






