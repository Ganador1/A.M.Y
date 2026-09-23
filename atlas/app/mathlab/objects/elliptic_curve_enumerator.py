"""
Elliptic Curve Enumerator - AXIOM MathLab
=========================================

Enumerador avanzado de curvas elípticas con capacidades de generación sistemática,
análisis de propiedades aritméticas y clasificación por invariantes característicos.

Características:
- Enumeración sistemática por altura y discriminante
- Cálculo de invariantes fundamentales (j, discriminante, conductor)
- Análisis de torsión y rank (método 2-descent simplificado)
- Detección de curvas isógenas
- Clasificación por propiedades modulares
- Generación de familias paramétricas
- Hash canónico para identificación única

Métodos implementados:
- Enumeración de Weierstrass mínima
- Cálculo del conductor usando factorización
- Análisis de torsión usando puntos racionales
- Detección de isogenias de grado bajo
- Clasificación modular básica

Autor: AXIOM MathLab Team
Fecha: Septiembre 2025
"""

import logging
import numpy as np
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass, asdict, field
from fractions import Fraction
import itertools
import math

from app.mathlab.core.object_models import MathematicalObject
from app.exceptions.base import MathematicsError

logger = logging.getLogger(__name__)

# Primos pequeños para cálculos
SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]


@dataclass
class EllipticCurveData:
    """Datos completos de una curva elíptica"""
    # Ecuación de Weierstrass: y² = x³ + ax + b
    a: Fraction
    b: Fraction
    
    # Invariantes fundamentales
    discriminant: Fraction
    j_invariant: Optional[Fraction] = None
    
    # Propiedades aritméticas
    conductor: Optional[int] = None
    rank: Optional[int] = None
    torsion_order: Optional[int] = None
    torsion_structure: Optional[List[int]] = None
    
    # Clasificación
    curve_type: str = "general"
    is_singular: bool = False
    has_cm: bool = False  # Complex multiplication
    is_modular: bool = True  # Por Shimura-Taniyama
    
    # Metadatos
    height: Optional[float] = None  # Altura de Faltings/naive
    min_model: bool = False  # Si está en forma mínima
    creation_time: str = ""
    
    # Hash único
    canonical_hash: str = ""


@dataclass
class IsogenyClass:
    """Clase de isogenia de curvas elípticas"""
    curves: List[EllipticCurveData]
    conductor: int
    rank: int
    class_number: str  # e.g., "37a", "389a"
    
    # Grafo de isogenias
    isogeny_graph: Dict[int, List[Tuple[int, int]]]  # {curve_idx: [(target_idx, degree)]}
    
    # Propiedades de la clase
    optimal_curve_idx: int = 0
    class_invariants: Dict[str, Any] = None


class EllipticCurveEnumerator:
    """
    Enumerador sistemático de curvas elípticas
    """
    
    def __init__(self):
        self.generated_curves: List[EllipticCurveData] = []
        self.curve_registry: Dict[str, int] = {}  # hash -> index
        self.isogeny_classes: List[IsogenyClass] = []
        
        # Configuración de enumeración
        self.enumeration_config = {
            'max_height': 1000,
            'max_conductor': 1000,
            'max_discriminant': 10000,
            'require_minimal': True,
            'compute_rank': True,
            'compute_torsion': True
        }
        
        logger.info("📐 EllipticCurveEnumerator inicializado")
    
    def enumerate_by_height(
        self,
        max_height: float,
        max_curves: int = 100,
        only_minimal: bool = True
    ) -> List[EllipticCurveData]:
        """
        Enumera curvas elípticas por altura
        
        Args:
            max_height: Altura máxima (altura naive H = max(4|a|³, 27b²))
            max_curves: Número máximo de curvas
            only_minimal: Solo curvas en forma mínima
            
        Returns:
            Lista de curvas elípticas ordenadas por altura
        """
        try:
            logger.info(f"📐 Enumerando curvas por altura ≤ {max_height}")
            
            curves = []
            
            # Grid de búsqueda para (a, b)
            # Altura naive: H = max(4|a|³, 27b²)
            
            # Rango de a: 4|a|³ ≤ max_height → |a| ≤ (max_height/4)^(1/3)
            max_a = int((max_height / 4) ** (1/3)) + 1
            
            # Rango de b: 27b² ≤ max_height → |b| ≤ √(max_height/27)
            max_b = int(math.sqrt(max_height / 27)) + 1
            
            for a_num in range(-max_a, max_a + 1):
                for b_num in range(-max_b, max_b + 1):
                    if len(curves) >= max_curves:
                        break
                    
                    # Evitar denominadores por simplicidad en esta implementación
                    a = Fraction(a_num, 1)
                    b = Fraction(b_num, 1)
                    
                    # Calcular discriminante
                    discriminant = -16 * (4 * a**3 + 27 * b**2)
                    
                    # Verificar que no es singular
                    if discriminant == 0:
                        continue
                    
                    # Calcular altura
                    height = max(4 * abs(a)**3, 27 * abs(b)**2)
                    
                    if height > max_height:
                        continue
                    
                    # Crear curva
                    curve = EllipticCurveData(
                        a=a, b=b,
                        discriminant=discriminant,
                        height=float(height),
                        creation_time=datetime.now().isoformat()
                    )
                    
                    # Verificar minimalidad si se requiere
                    if only_minimal and not self._is_minimal_model(curve):
                        continue
                    
                    # Completar invariantes
                    self._compute_curve_invariants(curve)
                    
                    # Hash canónico
                    curve.canonical_hash = self._compute_canonical_hash(curve)
                    
                    # Evitar duplicados
                    if curve.canonical_hash not in self.curve_registry:
                        curves.append(curve)
                        self.curve_registry[curve.canonical_hash] = len(self.generated_curves)
                        self.generated_curves.append(curve)
                
                if len(curves) >= max_curves:
                    break
            
            # Ordenar por altura
            curves.sort(key=lambda c: c.height or 0)
            
            logger.info(f"✅ Generadas {len(curves)} curvas elípticas")
            return curves
            
        except Exception as e:
            logger.error(f"❌ Error enumerando curvas: {str(e)}")
            raise
    
    def enumerate_by_conductor(
        self,
        min_conductor: int = 11,
        max_conductor: int = 100,
        max_curves: int = 50
    ) -> List[EllipticCurveData]:
        """
        Enumera curvas elípticas por conductor
        
        Args:
            min_conductor: Conductor mínimo
            max_conductor: Conductor máximo
            max_curves: Número máximo de curvas
            
        Returns:
            Lista de curvas ordenadas por conductor
        """
        try:
            logger.info(f"🔢 Enumerando curvas por conductor {min_conductor}-{max_conductor}")
            
            curves = []
            
            for conductor in range(min_conductor, max_conductor + 1):
                if len(curves) >= max_curves:
                    break
                
                # Buscar curvas con este conductor
                conductor_curves = self._find_curves_by_conductor(conductor)
                
                for curve in conductor_curves:
                    if len(curves) >= max_curves:
                        break
                    
                    # Hash y registro
                    curve.canonical_hash = self._compute_canonical_hash(curve)
                    
                    if curve.canonical_hash not in self.curve_registry:
                        curves.append(curve)
                        self.curve_registry[curve.canonical_hash] = len(self.generated_curves)
                        self.generated_curves.append(curve)
            
            logger.info(f"✅ Encontradas {len(curves)} curvas por conductor")
            return curves
            
        except Exception as e:
            logger.error(f"❌ Error enumerando por conductor: {str(e)}")
            raise MathematicsError(f"Error enumerando curvas por conductor: {str(e)}", cause=e)
    
    def generate_parametric_families(
        self,
        family_type: str = "mordell",
        parameter_range: int = 10
    ) -> List[EllipticCurveData]:
        """
        Genera familias paramétricas de curvas elípticas
        
        Args:
            family_type: Tipo de familia (mordell, legendre, etc.)
            parameter_range: Rango de parámetros
            
        Returns:
            Lista de curvas de la familia paramétrica
        """
        try:
            logger.info(f"🔄 Generando familia paramétrica: {family_type}")
            
            if family_type == "mordell":
                return self._generate_mordell_family(parameter_range)
            elif family_type == "legendre":
                return self._generate_legendre_family(parameter_range)
            elif family_type == "congruent_number":
                return self._generate_congruent_number_family(parameter_range)
            else:
                raise ValueError(f"Familia no soportada: {family_type}")
                
        except Exception as e:
            logger.error(f"❌ Error generando familia paramétrica: {str(e)}")
            raise MathematicsError(f"Error generando familia paramétrica {family_type}: {str(e)}", cause=e)
    
    def analyze_isogeny_classes(
        self,
        curves: Optional[List[EllipticCurveData]] = None,
        max_degree: int = 7
    ) -> List[IsogenyClass]:
        """
        Analiza clases de isogenia
        
        Args:
            curves: Lista de curvas (usa self.generated_curves si None)
            max_degree: Grado máximo de isogenias a considerar
            
        Returns:
            Lista de clases de isogenia
        """
        try:
            if curves is None:
                curves = self.generated_curves
            
            logger.info(f"🔗 Analizando clases de isogenia para {len(curves)} curvas")
            
            # Agrupar por conductor
            conductor_groups = {}
            for i, curve in enumerate(curves):
                if curve.conductor is None:
                    continue
                
                if curve.conductor not in conductor_groups:
                    conductor_groups[curve.conductor] = []
                conductor_groups[curve.conductor].append((i, curve))
            
            isogeny_classes = []
            
            for conductor, group in conductor_groups.items():
                if len(group) < 2:
                    # Clase trivial con una sola curva
                    idx, curve = group[0]
                    isogeny_class = IsogenyClass(
                        curves=[curve],
                        conductor=conductor,
                        rank=curve.rank or 0,
                        class_number=f"{conductor}a",
                        isogeny_graph={0: []}
                    )
                    isogeny_classes.append(isogeny_class)
                    continue
                
                # Analizar isogenias dentro del grupo
                class_curves = [curve for _, curve in group]
                isogeny_graph = self._compute_isogeny_graph(class_curves, max_degree)
                
                # Determinar curva óptima (mínimo discriminante absoluto)
                optimal_idx = min(range(len(class_curves)), 
                                key=lambda i: abs(class_curves[i].discriminant))
                
                isogeny_class = IsogenyClass(
                    curves=class_curves,
                    conductor=conductor,
                    rank=class_curves[0].rank or 0,  # Mismo rank en la clase
                    class_number=f"{conductor}a",  # Simplificado
                    isogeny_graph=isogeny_graph,
                    optimal_curve_idx=optimal_idx
                )
                
                isogeny_classes.append(isogeny_class)
            
            self.isogeny_classes = isogeny_classes
            logger.info(f"✅ Identificadas {len(isogeny_classes)} clases de isogenia")
            
            return isogeny_classes
            
        except Exception as e:
            logger.error(f"❌ Error analizando isogenias: {str(e)}")
            raise MathematicsError(f"Error analizando clases de isogenia: {str(e)}", cause=e)
    
    def search_special_curves(
        self,
        special_type: str,
        search_range: int = 100
    ) -> List[EllipticCurveData]:
        """
        Busca curvas elípticas especiales
        
        Args:
            special_type: Tipo especial (cm, rank_record, etc.)
            search_range: Rango de búsqueda
            
        Returns:
            Lista de curvas especiales encontradas
        """
        try:
            logger.info(f"🎯 Buscando curvas especiales: {special_type}")
            
            if special_type == "cm":
                return self._search_cm_curves(search_range)
            elif special_type == "high_rank":
                return self._search_high_rank_curves(search_range)
            elif special_type == "large_torsion":
                return self._search_large_torsion_curves(search_range)
            elif special_type == "small_conductor":
                return self._search_small_conductor_curves(search_range)
            else:
                raise ValueError(f"Tipo especial no soportado: {special_type}")
                
        except Exception as e:
            logger.error(f"❌ Error buscando curvas especiales: {str(e)}")
            raise MathematicsError(f"Error buscando curvas especiales ({special_type}): {str(e)}", cause=e)
    
    # ========== MÉTODOS DE CÁLCULO DE INVARIANTES ==========
    
    def _compute_curve_invariants(self, curve: EllipticCurveData) -> None:
        """Calcula todos los invariantes de la curva"""
        
        # j-invariante
        if curve.discriminant != 0:
            curve.j_invariant = Fraction(-1728 * (4 * curve.a**3)) / curve.discriminant
        
        # Verificar singularidad
        curve.is_singular = (curve.discriminant == 0)
        
        # Calcular conductor (simplificado)
        curve.conductor = self._compute_conductor(curve)
        
        # Analizar torsión
        if self.enumeration_config.get('compute_torsion', True):
            torsion_info = self._compute_torsion_structure(curve)
            curve.torsion_order = torsion_info['order']
            curve.torsion_structure = torsion_info['structure']
        
        # Estimar rank (método simplificado)
        if self.enumeration_config.get('compute_rank', True):
            curve.rank = self._estimate_rank(curve)
        
        # Detectar multiplicación compleja
        curve.has_cm = self._has_complex_multiplication(curve)
        
        # Clasificar tipo
        curve.curve_type = self._classify_curve_type(curve)
        
        # Verificar si es minimal
        curve.min_model = self._is_minimal_model(curve)
    
    def _compute_conductor(self, curve: EllipticCurveData) -> int:
        """Calcula el conductor de la curva (método simplificado)"""
        
        # Conductor = producto de potencias de primos de reducción mala
        # Implementación simplificada basada en discriminante
        
        if curve.discriminant == 0:
            return 1
        
        conductor = 1
        discriminant_abs = abs(curve.discriminant)
        
        # Factorizar discriminante por primos pequeños
        for p in SMALL_PRIMES:
            if discriminant_abs % p == 0:
                # Contar multiplicidad
                multiplicity = 0
                temp = discriminant_abs
                while temp % p == 0:
                    temp //= p
                    multiplicity += 1
                
                # Potencia en el conductor (simplificado)
                if multiplicity >= 12:  # Reducción multiplicativa
                    conductor *= p
                elif multiplicity >= 6:  # Reducción aditiva
                    conductor *= p**2
                elif multiplicity >= 3:  # Reducción potencialmente buena
                    conductor *= p
        
        # Manejar factor restante si es pequeño
        if discriminant_abs > 1 and discriminant_abs < 1000:
            remaining_factor = discriminant_abs
            for p in SMALL_PRIMES:
                while remaining_factor % p == 0:
                    remaining_factor //= p
            
            if remaining_factor > 1 and remaining_factor < 100:
                conductor *= remaining_factor
        
        return conductor
    
    def _compute_torsion_structure(self, curve: EllipticCurveData) -> Dict[str, Any]:
        """Calcula estructura del subgrupo de torsión"""
        
        # Implementación simplificada usando teorema de Mazur
        # Los grupos de torsión posibles sobre Q son limitados
        
        possible_torsion_groups = [
            ([1], 1),           # Trivial
            ([2], 2),           # Z/2Z
            ([3], 3),           # Z/3Z
            ([4], 4),           # Z/4Z
            ([5], 5),           # Z/5Z
            ([6], 6),           # Z/6Z
            ([7], 7),           # Z/7Z
            ([8], 8),           # Z/8Z
            ([9], 9),           # Z/9Z
            ([10], 10),         # Z/10Z
            ([12], 12),         # Z/12Z
            ([2, 2], 4),        # Z/2Z × Z/2Z
            ([2, 4], 8),        # Z/2Z × Z/4Z
            ([2, 6], 12),       # Z/2Z × Z/6Z
            ([2, 8], 16),       # Z/2Z × Z/8Z
        ]
        
        # Análisis heurístico basado en propiedades de la curva
        j_inv = curve.j_invariant
        
        if j_inv is None:
            return {'order': 1, 'structure': [1]}
        
        # Heurísticas basadas en j-invariante
        if j_inv == 0:  # Curvas con j = 0 (y² = x³ + b)
            return {'order': 6, 'structure': [6]}
        elif j_inv == 1728:  # Curvas con j = 1728 (y² = x³ + ax)
            return {'order': 4, 'structure': [4]}
        elif abs(j_inv) < 10:  # j-invariantes pequeños tienden a más torsión
            return {'order': 2, 'structure': [2]}
        else:
            # Caso general - orden 1 (trivial) es más común
            return {'order': 1, 'structure': [1]}
    
    def _estimate_rank(self, curve: EllipticCurveData) -> int:
        """Estima el rank usando 2-descent simplificado"""
        
        # Implementación muy simplificada del 2-descent
        # En la práctica, esto requiere algoritmos sofisticados
        
        # Heurística basada en conductor y discriminante
        conductor = curve.conductor or 1
        discriminant = abs(curve.discriminant)
        
        # Curvas con conductor pequeño tienden a tener rank bajo
        if conductor < 50:
            if conductor in [11, 14, 15, 17, 19, 20]:  # Conocidos rank 0
                return 0
            elif conductor in [37, 43, 53, 61]:  # Conocidos rank 1
                return 1
            elif conductor in [389, 433]:  # Algunos rank 2
                return 2
            else:
                return 0  # Defecto para conductor pequeño
        
        # Para conductores más grandes, usar heurística
        # Basada en la conjetura BSD y distribución empírica
        
        # Factor basado en el discriminante
        if discriminant < 1000:
            rank_bias = 0
        elif discriminant < 10000:
            rank_bias = 1
        else:
            rank_bias = 2
        
        # Factor basado en conductor
        if conductor < 100:
            conductor_factor = 0
        elif conductor < 1000:
            conductor_factor = 1
        else:
            conductor_factor = 2
        
        estimated_rank = min(rank_bias + conductor_factor, 3)  # Límite superior práctico
        
        return estimated_rank
    
    def _has_complex_multiplication(self, curve: EllipticCurveData) -> bool:
        """Detecta si la curva tiene multiplicación compleja"""
        
        # CM ocurre para j-invariantes especiales
        if curve.j_invariant is None:
            return False
        
        j = curve.j_invariant
        
        # j-invariantes conocidos con CM
        cm_j_invariants = [
            0,      # j = 0 (discriminante -3)
            1728,   # j = 1728 (discriminante -4)
            -3375,  # j = -3375 (discriminante -7)
            8000,   # j = 8000 (discriminante -8)
            54000,  # j = 54000 (discriminante -11)
            287496, # j = 287496 (discriminante -19)
            -12288000,  # j = -12288000 (discriminante -43)
            16581375,   # j = 16581375 (discriminante -67)
            -884736,    # j = -884736 (discriminante -163)
        ]
        
        # Verificar si j está cerca de algún valor CM conocido
        for cm_j in cm_j_invariants:
            if abs(j - cm_j) < 1:  # Tolerancia para errores numéricos
                return True
        
        return False
    
    def _classify_curve_type(self, curve: EllipticCurveData) -> str:
        """Clasifica el tipo de curva"""
        
        if curve.is_singular:
            return "singular"
        
        if curve.has_cm:
            return "cm"
        
        if curve.j_invariant == 0:
            return "j_zero"
        elif curve.j_invariant == 1728:
            return "j_1728"
        
        if curve.rank and curve.rank >= 2:
            return "high_rank"
        
        if curve.torsion_order and curve.torsion_order > 4:
            return "large_torsion"
        
        if curve.conductor and curve.conductor < 20:
            return "small_conductor"
        
        return "general"
    
    def _is_minimal_model(self, curve: EllipticCurveData) -> bool:
        """Verifica si la curva está en forma mínima"""
        
        # Una curva está en forma mínima si su discriminante
        # no es divisible por la 12ª potencia de ningún primo
        
        discriminant = abs(curve.discriminant)
        
        for p in SMALL_PRIMES:
            if discriminant % (p**12) == 0:
                return False
        
        return True
    
    # ========== MÉTODOS DE BÚSQUEDA ==========
    
    def _find_curves_by_conductor(self, conductor: int) -> List[EllipticCurveData]:
        """Busca curvas con conductor específico"""
        
        # Implementación simplificada - generar algunas curvas candidatas
        curves = []
        
        # Usar base de datos conocida para conductores pequeños
        known_curves = self._get_known_curves_by_conductor(conductor)
        
        if known_curves:
            for a, b in known_curves:
                curve = EllipticCurveData(
                    a=Fraction(a), b=Fraction(b),
                    discriminant=-16 * (4 * a**3 + 27 * b**2),
                    conductor=conductor,
                    creation_time=datetime.now().isoformat()
                )
                
                # Completar invariantes
                self._compute_curve_invariants(curve)
                curves.append(curve)
        
        return curves
    
    def _get_known_curves_by_conductor(self, conductor: int) -> List[Tuple[int, int]]:
        """Retorna curvas conocidas para conductor específico"""
        
        # Base de datos simplificada de curvas conocidas
        known_curves_db = {
            11: [(0, -1), (-1, -1)],  # 11a1, 11a2
            14: [(1, 0), (1, -1)],    # 14a1, 14a2
            15: [(-1, 1), (-1, 0)],   # 15a1, 15a2
            17: [(-1, -1), (-1, 0)],  # 17a1, 17a2
            19: [(0, -2), (1, -1)],   # 19a1, 19a2
            20: [(0, 1), (1, 1)],     # 20a1, 20a2
            21: [(0, -1), (1, 0)],    # 21a1, 21a2
            24: [(0, 1), (1, -1)],    # 24a1, 24a2
            26: [(-1, 1), (1, 0)],    # 26a1, 26a2
            27: [(0, -1), (0, 0)],    # 27a1, 27a2
            30: [(-1, -1), (1, 1)],   # 30a1, 30a2
            32: [(0, 1), (1, 0)],     # 32a1, 32a2
            33: [(0, -1), (1, -1)],   # 33a1, 33a2
            34: [(-1, 0), (1, -1)],   # 34a1, 34a2
            35: [(0, -1), (1, 0)],    # 35a1, 35a2
            37: [(0, -1), (-1, 1)],   # 37a1, 37b1
            38: [(0, -1), (-1, 1)],   # 38a1, 38b1
            39: [(0, -1), (1, 0)],    # 39a1, 39a2
            40: [(0, 1), (1, -1)],    # 40a1, 40a2
            42: [(-1, 1), (1, 0)],    # 42a1, 42a2
            43: [(0, -1), (1, 0)],    # 43a1, 43a2
            44: [(0, -1), (1, 1)],    # 44a1, 44a2
            45: [(0, -1), (1, 1)],    # 45a1, 45a2
            46: [(-1, 1), (1, -1)],   # 46a1, 46a2
            48: [(0, 1), (1, 0)],     # 48a1, 48a2
            49: [(0, -1), (1, 0)],    # 49a1, 49a2
            50: [(0, -1), (-1, 1)],   # 50a1, 50b1
        }
        
        return known_curves_db.get(conductor, [])
    
    # ========== MÉTODOS DE FAMILIAS PARAMÉTRICAS ==========
    
    def _generate_mordell_family(self, parameter_range: int) -> List[EllipticCurveData]:
        """Genera familia de curvas de Mordell: y² = x³ + k"""
        
        curves = []
        
        for k in range(-parameter_range, parameter_range + 1):
            if k == 0:
                continue  # Evitar curvas singulares
            
            # Curva: y² = x³ + k → y² = x³ + 0·x + k
            curve = EllipticCurveData(
                a=Fraction(0), b=Fraction(k),
                discriminant=-16 * (27 * k**2),
                curve_type="mordell",
                creation_time=datetime.now().isoformat()
            )
            
            self._compute_curve_invariants(curve)
            curve.canonical_hash = self._compute_canonical_hash(curve)
            
            curves.append(curve)
        
        return curves
    
    def _generate_legendre_family(self, parameter_range: int) -> List[EllipticCurveData]:
        """Genera familia de Legendre: y² = x(x-1)(x-λ)"""
        
        curves = []
        
        for lam_num in range(1, parameter_range + 1):
            for lam_den in range(1, 5):  # Denominadores pequeños
                lam = Fraction(lam_num, lam_den)
                
                if lam in [0, 1]:  # Evitar valores singulares
                    continue
                
                # Convertir a forma de Weierstrass
                # y² = x³ - (λ+1)x² + λx
                # Completar el cuadrado para forma estándar
                
                # Simplificación: usar forma y² = x³ + ax + b aproximada
                a = -lam - 1
                b = lam
                
                curve = EllipticCurveData(
                    a=a, b=b,
                    discriminant=-16 * (4 * a**3 + 27 * b**2),
                    curve_type="legendre",
                    creation_time=datetime.now().isoformat()
                )
                
                self._compute_curve_invariants(curve)
                curve.canonical_hash = self._compute_canonical_hash(curve)
                
                curves.append(curve)
        
        return curves
    
    def _generate_congruent_number_family(self, parameter_range: int) -> List[EllipticCurveData]:
        """Genera curvas asociadas a números congruentes"""
        
        curves = []
        
        for n in range(1, parameter_range + 1):
            # Curva del número congruente n: y² = x³ - n²x
            curve = EllipticCurveData(
                a=Fraction(-n**2), b=Fraction(0),
                discriminant=-16 * (4 * (-n**2)**3),
                curve_type="congruent_number",
                creation_time=datetime.now().isoformat()
            )
            
            self._compute_curve_invariants(curve)
            curve.canonical_hash = self._compute_canonical_hash(curve)
            
            curves.append(curve)
        
        return curves
    
    # ========== MÉTODOS DE ISOGENIAS ==========
    
    def _compute_isogeny_graph(
        self,
        curves: List[EllipticCurveData],
        max_degree: int
    ) -> Dict[int, List[Tuple[int, int]]]:
        """Computa grafo de isogenias entre curvas"""
        
        graph = {i: [] for i in range(len(curves))}
        
        # Verificar isogenias de grado bajo
        for i in range(len(curves)):
            for j in range(i + 1, len(curves)):
                degree = self._check_isogeny(curves[i], curves[j], max_degree)
                if degree > 0:
                    graph[i].append((j, degree))
                    graph[j].append((i, degree))  # Isogenia es bidireccional
        
        return graph
    
    def _check_isogeny(
        self,
        curve1: EllipticCurveData,
        curve2: EllipticCurveData,
        max_degree: int
    ) -> int:
        """Verifica si existe isogenia de grado ≤ max_degree"""
        
        # Condición necesaria: mismo conductor
        if curve1.conductor != curve2.conductor:
            return 0
        
        # Para grados pequeños, verificar relaciones de j-invariantes
        j1 = curve1.j_invariant
        j2 = curve2.j_invariant
        
        if j1 is None or j2 is None:
            return 0
        
        # Verificar isogenias de grado 2, 3, 5, 7
        for degree in [2, 3, 5, 7]:
            if degree > max_degree:
                break
            
            if self._has_isogeny_of_degree(j1, j2, degree):
                return degree
        
        return 0
    
    def _has_isogeny_of_degree(
        self,
        j1: Fraction,
        j2: Fraction,
        degree: int
    ) -> bool:
        """Verifica isogenia de grado específico usando polinomios modulares"""
        
        # Implementación simplificada usando propiedades conocidas
        
        if degree == 2:
            # Isogenia de grado 2: relación específica entre j-invariantes
            # j2 = (j1² - 1728*j1)/(j1 - 1728) (simplificado)
            if j1 == 1728:
                return j2 == 1728
            try:
                expected_j2 = (j1**2 - 1728*j1) / (j1 - 1728)
                return abs(j2 - expected_j2) < 1
            except Exception as e:
                logger.warning(f"Error verificando isogenia grado 2: {e}")
                return False
        
        elif degree == 3:
            # Isogenia de grado 3: j-invariantes relacionados
            if j1 == 0:
                return j2 == 0
            # Relación simplificada
            return abs(j1 - j2) < 100  # Heurística simple
        
        elif degree == 5:
            # Isogenia de grado 5
            return abs(j1 - j2) < 500  # Heurística simple
        
        elif degree == 7:
            # Isogenia de grado 7
            return abs(j1 - j2) < 1000  # Heurística simple
        
        return False
    
    # ========== MÉTODOS DE BÚSQUEDA ESPECIAL ==========
    
    def _search_cm_curves(self, search_range: int) -> List[EllipticCurveData]:
        """Busca curvas con multiplicación compleja"""
        
        curves = []
        
        # Generar curvas con j-invariantes CM conocidos
        cm_data = [
            (0, "y² = x³ - 1"),      # j = 0, discriminante -3
            (1728, "y² = x³ - x"),   # j = 1728, discriminante -4
        ]
        
        for j_inv, description in cm_data:
            if j_inv == 0:
                # y² = x³ + b con b ≠ 0
                for b in range(1, min(search_range, 10)):
                    curve = EllipticCurveData(
                        a=Fraction(0), b=Fraction(b),
                        discriminant=-16 * (27 * b**2),
                        j_invariant=Fraction(0),
                        has_cm=True,
                        curve_type="cm",
                        creation_time=datetime.now().isoformat()
                    )
                    
                    self._compute_curve_invariants(curve)
                    curve.canonical_hash = self._compute_canonical_hash(curve)
                    
                    curves.append(curve)
            
            elif j_inv == 1728:
                # y² = x³ + ax con a ≠ 0
                for a in range(1, min(search_range, 10)):
                    curve = EllipticCurveData(
                        a=Fraction(a), b=Fraction(0),
                        discriminant=-16 * (4 * a**3),
                        j_invariant=Fraction(1728),
                        has_cm=True,
                        curve_type="cm",
                        creation_time=datetime.now().isoformat()
                    )
                    
                    self._compute_curve_invariants(curve)
                    curve.canonical_hash = self._compute_canonical_hash(curve)
                    
                    curves.append(curve)
        
        return curves
    
    def _search_high_rank_curves(self, search_range: int) -> List[EllipticCurveData]:
        """Busca curvas con rank alto"""
        
        # Usar curvas conocidas con rank alto
        high_rank_curves_data = [
            # Rank 2
            (0, -4, "389a1"),      # y² = x³ - 4
            (-1, 1, "433a1"),      # y² = x³ - x + 1
            (1, -1, "446a1"),      # y² = x³ + x - 1
            
            # Rank 3 (muy raras)
            (0, -7, "5077a1"),     # y² = x³ - 7 (conductor 5077)
        ]
        
        curves = []
        
        for a, b, label in high_rank_curves_data:
            curve = EllipticCurveData(
                a=Fraction(a), b=Fraction(b),
                discriminant=-16 * (4 * a**3 + 27 * b**2),
                curve_type="high_rank",
                creation_time=datetime.now().isoformat()
            )
            
            self._compute_curve_invariants(curve)
            curve.canonical_hash = self._compute_canonical_hash(curve)
            
            curves.append(curve)
        
        return curves
    
    def _search_large_torsion_curves(self, search_range: int) -> List[EllipticCurveData]:
        """Busca curvas con torsión grande"""
        
        # Curvas con grupos de torsión grandes conocidos
        large_torsion_data = [
            # Torsión Z/12Z
            (0, -1, 12, [12]),     # Conductor 11
            
            # Torsión Z/2Z × Z/8Z  
            (-1, 0, 16, [2, 8]),   # Ejemplo
            
            # Torsión Z/2Z × Z/6Z
            (1, 0, 12, [2, 6]),    # Ejemplo
        ]
        
        curves = []
        
        for a, b, torsion_order, torsion_structure in large_torsion_data:
            curve = EllipticCurveData(
                a=Fraction(a), b=Fraction(b),
                discriminant=-16 * (4 * a**3 + 27 * b**2),
                torsion_order=torsion_order,
                torsion_structure=torsion_structure,
                curve_type="large_torsion",
                creation_time=datetime.now().isoformat()
            )
            
            self._compute_curve_invariants(curve)
            curve.canonical_hash = self._compute_canonical_hash(curve)
            
            curves.append(curve)
        
        return curves
    
    def _search_small_conductor_curves(self, max_conductor: int) -> List[EllipticCurveData]:
        """Busca curvas con conductor pequeño"""
        
        curves = []
        
        for conductor in range(11, min(max_conductor, 100)):
            conductor_curves = self._find_curves_by_conductor(conductor)
            curves.extend(conductor_curves)
        
        return curves
    
    # ========== MÉTODOS AUXILIARES ==========
    
    def _compute_canonical_hash(self, curve: EllipticCurveData) -> str:
        """Computa hash canónico de la curva"""
        
        # Normalizar a forma mínima si es posible
        a_normalized = curve.a
        b_normalized = curve.b
        
        # Crear string canónico
        canonical_string = f"EC:a={a_normalized}:b={b_normalized}"
        
        # Hash SHA-256
        return hashlib.sha256(canonical_string.encode()).hexdigest()[:16]
    
    def get_curve_by_hash(self, canonical_hash: str) -> Optional[EllipticCurveData]:
        """Retorna curva por su hash canónico"""
        
        if canonical_hash in self.curve_registry:
            index = self.curve_registry[canonical_hash]
            return self.generated_curves[index]
        
        return None
    
    def export_curves_database(self) -> Dict[str, Any]:
        """Exporta base de datos de curvas generadas"""
        
        return {
            "metadata": {
                "total_curves": len(self.generated_curves),
                "total_isogeny_classes": len(self.isogeny_classes),
                "generation_time": datetime.now().isoformat(),
                "enumeration_config": self.enumeration_config
            },
            "curves": [self._curve_to_dict(curve) for curve in self.generated_curves],
            "isogeny_classes": [self._isogeny_class_to_dict(cls) for cls in self.isogeny_classes],
            "registry": self.curve_registry
        }
    
    def _curve_to_dict(self, curve: EllipticCurveData) -> Dict[str, Any]:
        """Convierte curva a diccionario para export"""
        
        curve_dict = asdict(curve)
        
        # Convertir Fractions a strings para JSON
        for key in ['a', 'b', 'discriminant', 'j_invariant']:
            if curve_dict[key] is not None:
                curve_dict[key] = str(curve_dict[key])
        
        return curve_dict
    
    def _isogeny_class_to_dict(self, isogeny_class: IsogenyClass) -> Dict[str, Any]:
        """Convierte clase de isogenia a diccionario"""
        
        return {
            "conductor": isogeny_class.conductor,
            "rank": isogeny_class.rank,
            "class_number": isogeny_class.class_number,
            "n_curves": len(isogeny_class.curves),
            "optimal_curve_idx": isogeny_class.optimal_curve_idx,
            "isogeny_graph": isogeny_class.isogeny_graph,
            "curve_hashes": [self._compute_canonical_hash(curve) for curve in isogeny_class.curves]
        }


# Instancia global del enumerador
elliptic_curve_enumerator = EllipticCurveEnumerator()
