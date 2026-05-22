"""
Hybrid Verification Service - Combina fuzzing inteligente con verificación formal

Este servicio integra:
1. Fuzzing inteligente para búsqueda rápida de contraejemplos
2. Verificación formal con Z3 para casos complejos
3. Caché de resultados para optimización
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel, Field
from app.exceptions.domain.biology import BiologyError

# Importar servicios existentes
try:
    from .counterexample_fuzzer import IntelligentFuzzer, FuzzingResult
    from .formal_verification_service import FormalVerificationService
    from .theorem_proving.z3_smt_service import Z3SMTService
except ImportError:
    # Fallback para imports relativos
    from app.services.counterexample_fuzzer import IntelligentFuzzer, FuzzingResult
    from app.services.formal_verification_service import FormalVerificationService
    from app.services.theorem_proving.z3_smt_service import Z3SMTService

logger = logging.getLogger(__name__)


class VerificationStrategy(BaseModel):
    """Estrategia de verificación con prioridad y configuración"""
    name: str = Field(..., description="Nombre de la estrategia")
    priority: int = Field(1, description="Prioridad (1=alta, 3=baja)")
    timeout: float = Field(5.0, description="Tiempo máximo en segundos")
    enabled: bool = Field(True, description="Si la estrategia está habilitada")


class HybridVerificationResult(BaseModel):
    """Resultado de verificación híbrida"""
    verified: bool = Field(False, description="Si la proposición es válida")
    counterexample: Optional[Dict[str, Any]] = Field(None, description="Contraejemplo encontrado")
    strategy_used: str = Field("unknown", description="Estrategia que resolvió el problema")
    time_taken: float = Field(0.0, description="Tiempo tomado en segundos")
    confidence: float = Field(0.0, description="Confianza en el resultado (0-1)")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detalles adicionales")


class HybridVerificationService:
    """Servicio de verificación híbrida que combina múltiples técnicas"""
    
    def __init__(self):
        self.fuzzer = IntelligentFuzzer()
        self.formal_verifier = FormalVerificationService()
        self.z3_service = Z3SMTService()
        
        # Estrategias de verificación ordenadas por prioridad
        self.strategies = [
            VerificationStrategy(
                name="quick_fuzzing",
                priority=1,
                timeout=2.0,
                enabled=True
            ),
            VerificationStrategy(
                name="smart_fuzzing", 
                priority=2,
                timeout=5.0,
                enabled=True
            ),
            VerificationStrategy(
                name="z3_formal",
                priority=3,
                timeout=30.0,
                enabled=True
            ),
            VerificationStrategy(
                name="brute_force",
                priority=4,
                timeout=10.0,
                enabled=False  # Deshabilitado por defecto
            )
        ]
        
        # Caché de resultados para optimización
        self.result_cache: Dict[str, HybridVerificationResult] = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def _get_cache_key(self, proposition: str) -> str:
        """Generar clave única para el caché"""
        # Normalizar la proposición para caché
        import hashlib
        normalized = proposition.strip().lower().replace(" ", "")
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def verify_proposition(self, proposition: str) -> HybridVerificationResult:
        """
        Verificar una proposición matemática usando estrategias híbridas
        
        Args:
            proposition: Expresión matemática a verificar
            
        Returns:
            HybridVerificationResult con el resultado de la verificación
        """
        start_time = time.time()
        
        # Verificar caché primero
        cache_key = self._get_cache_key(proposition)
        if cache_key in self.result_cache:
            self.cache_hits += 1
            result = self.result_cache[cache_key]
            result.time_taken = time.time() - start_time
            logger.info(f"Cache hit for proposition: {proposition}")
            return result
        
        self.cache_misses += 1
        logger.info(f"Verifying proposition: {proposition}")
        
        # Ejecutar estrategias en orden de prioridad
        result = None
        strategy_used = "none"
        
        for strategy in sorted(self.strategies, key=lambda x: x.priority):
            if not strategy.enabled:
                continue
                
            logger.info(f"Trying strategy: {strategy.name}")
            
            try:
                strategy_result = self._execute_strategy(strategy, proposition)
                
                if strategy_result is not None:
                    result = strategy_result
                    strategy_used = strategy.name
                    break
                    
            except BiologyError as e:
                logger.warning(f"Strategy {strategy.name} failed: {e}")
                continue
        
        # Si ninguna estrategia encontró resultado, usar verificación formal completa
        if result is None:
            logger.info("Falling back to complete formal verification")
            result = self._complete_formal_verification(proposition)
            strategy_used = "complete_formal"
        
        # Calcular tiempo y confianza
        time_taken = time.time() - start_time
        confidence = self._calculate_confidence(result, strategy_used, time_taken)
        
        # Construir resultado final
        final_result = HybridVerificationResult(
            verified=result.get("verified", False) if isinstance(result, dict) else False,
            counterexample=result.get("counterexample") if isinstance(result, dict) else None,
            strategy_used=strategy_used,
            time_taken=time_taken,
            confidence=confidence,
            details={"cache_hits": self.cache_hits, "cache_misses": self.cache_misses}
        )
        
        # Almacenar en caché
        self.result_cache[cache_key] = final_result
        
        logger.info(f"Verification completed in {time_taken:.2f}s with strategy: {strategy_used}")
        return final_result
    
    def _execute_strategy(self, strategy: VerificationStrategy, proposition: str) -> Optional[Dict[str, Any]]:
        """Ejecutar una estrategia específica"""
        
        if strategy.name == "quick_fuzzing":
            # Fuzzing rápido con pocas iteraciones
            fuzzing_result = self.fuzzer.find_counterexample(proposition, max_iterations=100)
            
            if fuzzing_result.success:
                return {
                    "verified": False,
                    "counterexample": fuzzing_result.counterexample
                }
            
        elif strategy.name == "smart_fuzzing":
            # Fuzzing inteligente con más iteraciones
            fuzzing_result = self.fuzzer.find_counterexample(proposition, max_iterations=1000)
            
            if fuzzing_result.success:
                return {
                    "verified": False, 
                    "counterexample": fuzzing_result.counterexample
                }
            
        elif strategy.name == "z3_formal":
            # Verificación formal con Z3
            try:
                z3_result = self.z3_service.find_counterexamples(proposition, {"x": "Real"})
                
                if z3_result:
                    return {
                        "verified": False,
                        "counterexample": z3_result[0]
                    }
                else:
                    # Si no hay contraejemplos, la proposición podría ser válida
                    return {"verified": True}
                    
            except BiologyError as e:
                logger.error(f"Z3 verification failed: {e}")
                return None
        
        elif strategy.name == "brute_force":
            # Fuerza bruta (solo para proposiciones simples)
            brute_result = self.formal_verifier.generate_counterexample(proposition)
            
            if brute_result and brute_result.counterexample:
                return {
                    "verified": False,
                    "counterexample": brute_result.counterexample
                }
        
        return None
    
    def _complete_formal_verification(self, proposition: str) -> Dict[str, Any]:
        """Verificación formal completa como último recurso"""
        try:
            # Intentar verificación formal completa usando generate_counterexample
            import asyncio
            
            # Ejecutar de forma síncrona usando el bucle de eventos existente
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Usar generate_counterexample para buscar contraejemplos
            counterexample_result = loop.run_until_complete(
                self.formal_verifier.generate_counterexample(proposition, "z3")
            )
            
            if counterexample_result and counterexample_result.has_counterexample:
                return {
                    "verified": False,
                    "counterexample": counterexample_result.counterexamples[0] if counterexample_result.counterexamples else None
                }
            else:
                # Si no hay contraejemplos, asumir que es válida (con baja confianza)
                return {"verified": True}
            
        except BiologyError as e:
            logger.error(f"Complete formal verification failed: {e}")
        
        # Resultado por defecto si todo falla
        return {"verified": False}
    
    def _calculate_confidence(self, result: Dict[str, Any], strategy: str, time_taken: float) -> float:
        """Calcular confianza en el resultado basado en la estrategia y tiempo"""
        
        confidence = 0.8  # Confianza base
        
        # Ajustar confianza basado en la estrategia
        strategy_confidence = {
            "z3_formal": 0.95,
            "complete_formal": 0.90, 
            "smart_fuzzing": 0.75,
            "quick_fuzzing": 0.60,
            "brute_force": 0.70,
            "none": 0.50
        }
        
        confidence = strategy_confidence.get(strategy, 0.5)
        
        # Ajustar por tiempo (resultados más rápidos son menos confiables)
        if time_taken < 1.0:
            confidence *= 0.9
        elif time_taken > 10.0:
            confidence *= 1.1  # Más tiempo → más confianza
        
        return min(max(confidence, 0.0), 1.0)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del servicio"""
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_size": len(self.result_cache),
            "cache_hit_rate": self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0,
            "strategies": [s.dict() for s in self.strategies]
        }
    
    def clear_cache(self):
        """Limpiar el caché de resultados"""
        self.result_cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info("Verification cache cleared")


# Singleton para uso global
hybrid_verifier = HybridVerificationService()