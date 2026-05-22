"""
Generador y sampler de curvas elípticas para el MathLab
- Enumeración sistemática de curvas y² = x³ + Ax + B
- Validación de discriminante no nulo
- Integración con registry y hashing semántico
"""

from __future__ import annotations

import itertools
from typing import Dict, Any, List, Iterator, Optional
import random

from app.mathlab.core.object_models import MathematicalObject
from app.mathlab.core.object_registry import REGISTRY


class EllipticCurveSampler:
    """Generador sistemático de curvas elípticas sobre Q"""
    
    def __init__(self):
        self.max_coefficient_range = 100
        self.batch_size = 50
    
    def sample_curves_systematic(self, 
                                A_range: tuple[int, int] = (-10, 10),
                                B_range: tuple[int, int] = (-10, 10),
                                exclude_singular: bool = True) -> Iterator[MathematicalObject]:
        """
        Enumera curvas elípticas y² = x³ + Ax + B sistemáticamente
        
        Args:
            A_range: Rango para coeficiente A
            B_range: Rango para coeficiente B  
            exclude_singular: Si excluir curvas singulares (discriminante = 0)
            
        Yields:
            MathematicalObject: Curva elíptica válida
        """
        for A in range(A_range[0], A_range[1] + 1):
            for B in range(B_range[0], B_range[1] + 1):
                # Calcular discriminante: Δ = -16(4A³ + 27B²)
                discriminant = -16 * (4 * A**3 + 27 * B**2)
                
                if exclude_singular and discriminant == 0:
                    continue
                
                # Crear objeto curva elíptica
                curve_data = {
                    "form": "weierstrass_short",
                    "A": A,
                    "B": B,
                    "discriminant": discriminant,
                    "equation": f"y^2 = x^3 + {A}*x + {B}",
                    "field": "Q"  # Racionales por ahora
                }
                
                curve_obj = MathematicalObject(
                    type="elliptic_curve",
                    payload_json=curve_data
                )
                
                yield curve_obj
    
    def sample_curves_random(self, 
                            count: int = 100,
                            coefficient_bound: int = 50,
                            exclude_singular: bool = True) -> List[MathematicalObject]:
        """
        Genera muestra aleatoria de curvas elípticas
        
        Args:
            count: Número de curvas a generar
            coefficient_bound: Bound para coeficientes |A|, |B| ≤ bound
            exclude_singular: Si excluir singulares
            
        Returns:
            List[MathematicalObject]: Lista de curvas válidas
        """
        curves = []
        attempts = 0
        max_attempts = count * 10  # Evitar bucle infinito
        
        while len(curves) < count and attempts < max_attempts:
            A = random.randint(-coefficient_bound, coefficient_bound)
            B = random.randint(-coefficient_bound, coefficient_bound)
            
            discriminant = -16 * (4 * A**3 + 27 * B**2)
            
            if exclude_singular and discriminant == 0:
                attempts += 1
                continue
                
            curve_data = {
                "form": "weierstrass_short",
                "A": A,
                "B": B,
                "discriminant": discriminant,
                "equation": f"y^2 = x^3 + {A}*x + {B}",
                "field": "Q"
            }
            
            curve_obj = MathematicalObject(
                type="elliptic_curve", 
                payload_json=curve_data
            )
            
            curves.append(curve_obj)
            attempts += 1
        
        return curves
    
    def generate_special_curves(self) -> List[MathematicalObject]:
        """
        Genera curvas elípticas con propiedades especiales conocidas
        
        Returns:
            List[MathematicalObject]: Curvas con propiedades interesantes
        """
        special_curves = []
        
        # Curvas famosas con rank alto
        famous_curves = [
            # Rank 2: y² = x³ - x
            {"A": -1, "B": 0, "name": "secp256k1_family", "expected_rank": 2},
            # Rank 1: y² = x³ - 2  
            {"A": 0, "B": -2, "name": "mordell_curve", "expected_rank": 1},
            # Rank 0: y² = x³ + 1
            {"A": 0, "B": 1, "name": "basic_cubic", "expected_rank": 0},
            # Ejemplo con torsión: y² = x³ - 43*x + 166
            {"A": -43, "B": 166, "name": "torsion_example", "expected_rank": 0},
            # Conductor pequeño: y² = x³ - x² - 10*x - 20 (conductor 11)
            {"A": 0, "B": -7, "name": "conductor_37", "expected_rank": 1}
        ]
        
        for curve_spec in famous_curves:
            A, B = curve_spec["A"], curve_spec["B"]
            discriminant = -16 * (4 * A**3 + 27 * B**2)
            
            curve_data = {
                "form": "weierstrass_short",
                "A": A,
                "B": B,  
                "discriminant": discriminant,
                "equation": f"y^2 = x^3 + {A}*x + {B}",
                "field": "Q",
                "name": curve_spec.get("name"),
                "expected_rank": curve_spec.get("expected_rank"),
                "special": True
            }
            
            curve_obj = MathematicalObject(
                type="elliptic_curve",
                payload_json=curve_data
            )
            
            special_curves.append(curve_obj)
        
        return special_curves
    
    def register_curve_batch(self, 
                           curves: List[MathematicalObject]) -> Dict[str, Any]:
        """
        Registra un lote de curvas en el registry
        
        Args:
            curves: Lista de curvas a registrar
            
        Returns:
            Dict con estadísticas de registro
        """
        registered = 0
        duplicates = 0
        errors = []
        object_ids = []
        
        for curve in curves:
            try:
                obj_id = REGISTRY.register(curve)
                if obj_id:
                    object_ids.append(obj_id)
                    registered += 1
                else:
                    duplicates += 1
            except Exception as e:
                errors.append(str(e))
        
        return {
            "total_curves": len(curves),
            "registered": registered,
            "duplicates": duplicates,
            "errors": len(errors),
            "object_ids": object_ids,
            "error_details": errors[:5]  # Primeros 5 errores
        }
    
    def discover_curves_by_conductor(self, 
                                   max_conductor: int = 100) -> List[MathematicalObject]:
        """
        Genera curvas organizadas por conductor (aproximado)
        
        Args:
            max_conductor: Conductor máximo aproximado
            
        Returns:
            List[MathematicalObject]: Curvas ordenadas por conductor estimado
        """
        curves_by_conductor = []
        
        # Heurística simple: conductor relacionado con discriminante
        for A in range(-20, 21):
            for B in range(-20, 21):
                discriminant = -16 * (4 * A**3 + 27 * B**2)
                
                if discriminant == 0:
                    continue
                
                # Conductor aproximado (heurística simple)
                conductor_est = abs(discriminant) // 16
                
                if conductor_est > max_conductor:
                    continue
                
                curve_data = {
                    "form": "weierstrass_short",
                    "A": A,
                    "B": B,
                    "discriminant": discriminant,
                    "conductor_estimate": conductor_est,
                    "equation": f"y^2 = x^3 + {A}*x + {B}",
                    "field": "Q"
                }
                
                curve_obj = MathematicalObject(
                    type="elliptic_curve",
                    payload_json=curve_data
                )
                
                curves_by_conductor.append((conductor_est, curve_obj))
        
        # Ordenar por conductor y devolver solo las curvas
        curves_by_conductor.sort(key=lambda x: x[0])
        return [curve for _, curve in curves_by_conductor]


def create_curve_from_coefficients(A: int, B: int, 
                                 extra_data: Optional[Dict[str, Any]] = None) -> MathematicalObject:
    """
    Función utilitaria para crear curva elíptica desde coeficientes
    
    Args:
        A: Coeficiente de x
        B: Término constante  
        extra_data: Metadatos adicionales
        
    Returns:
        MathematicalObject: Curva elíptica
    """
    discriminant = -16 * (4 * A**3 + 27 * B**2)
    
    curve_data = {
        "form": "weierstrass_short",
        "A": A,
        "B": B,
        "discriminant": discriminant,
        "equation": f"y^2 = x^3 + {A}*x + {B}",
        "field": "Q"
    }
    
    if extra_data:
        curve_data.update(extra_data)
    
    return MathematicalObject(
        type="elliptic_curve",
        payload_json=curve_data
    )


# Instancia global para uso en endpoints
ELLIPTIC_SAMPLER = EllipticCurveSampler()
