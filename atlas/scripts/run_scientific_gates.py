#!/usr/bin/env python3
"""
Scientific Gates Validation - AXIOM ATLAS
Verifica compuertas científicas antes de deployment
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScientificGatesValidator:
    """Validador de compuertas científicas"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "gates": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0
            }
        }
    
    def check_ethics_gate(self) -> Dict[str, Any]:
        """Verificar ética gate está configurada"""
        logger.info("🔒 Verificando Ethics Gate...")
        
        ethics_config = Path("config/ethics_policy.yaml")
        gate = {
            "name": "ethics_gate",
            "status": "passed" if ethics_config.exists() else "failed",
            "config_exists": ethics_config.exists(),
            "message": "Ethics policy configuration found" if ethics_config.exists() 
                      else "Ethics policy configuration missing"
        }
        
        return gate
    
    def check_plausibility_model(self) -> Dict[str, Any]:
        """Verificar modelo de plausibilidad"""
        logger.info("🎯 Verificando Plausibility Model...")
        
        plausibility_config = Path("config/plausibility.yaml")
        gate = {
            "name": "plausibility_model",
            "status": "passed" if plausibility_config.exists() else "failed",
            "config_exists": plausibility_config.exists(),
            "message": "Plausibility model configured" if plausibility_config.exists()
                      else "Plausibility model configuration missing"
        }
        
        return gate
    
    def check_integrity_system(self) -> Dict[str, Any]:
        """Verificar sistema de integridad"""
        logger.info("🛡️ Verificando Integrity System...")
        
        integrity_core = Path("app/integrity_core.py")
        gate = {
            "name": "integrity_system",
            "status": "passed" if integrity_core.exists() else "failed",
            "core_exists": integrity_core.exists(),
            "message": "Integrity system available" if integrity_core.exists()
                      else "Integrity system missing"
        }
        
        return gate
    
    def check_reproducibility_framework(self) -> Dict[str, Any]:
        """Verificar framework de reproducibilidad"""
        logger.info("♻️ Verificando Reproducibility Framework...")
        
        repro_service = Path("app/services/reproducibility_service.py")
        gate = {
            "name": "reproducibility_framework",
            "status": "passed" if repro_service.exists() else "warning",
            "service_exists": repro_service.exists(),
            "message": "Reproducibility framework available" if repro_service.exists()
                      else "Reproducibility service not found (optional)"
        }
        
        return gate
    
    def run_all_gates(self) -> Dict[str, Any]:
        """Ejecutar todas las compuertas"""
        logger.info("🚀 Ejecutando validación de Scientific Gates...")
        
        gates = [
            self.check_ethics_gate(),
            self.check_plausibility_model(),
            self.check_integrity_system(),
            self.check_reproducibility_framework()
        ]
        
        # Compilar resultados
        for gate in gates:
            self.results["gates"].append(gate)
            self.results["summary"]["total"] += 1
            
            if gate["status"] == "passed":
                self.results["summary"]["passed"] += 1
            elif gate["status"] == "failed":
                self.results["summary"]["failed"] += 1
        
        return self.results
    
    def print_summary(self):
        """Imprimir resumen"""
        print("\n" + "=" * 50)
        print("🔬 SCIENTIFIC GATES VALIDATION")
        print("=" * 50)
        
        for gate in self.results["gates"]:
            status_icon = "✅" if gate["status"] == "passed" else "❌" if gate["status"] == "failed" else "⚠️"
            print(f"{status_icon} {gate['name']}: {gate['message']}")
        
        print("\n" + "-" * 50)
        print(f"Total gates: {self.results['summary']['total']}")
        print(f"✅ Passed: {self.results['summary']['passed']}")
        print(f"❌ Failed: {self.results['summary']['failed']}")
        print("=" * 50)


def main():
    """Función principal"""
    validator = ScientificGatesValidator()
    results = validator.run_all_gates()
    validator.print_summary()
    
    # Exit code basado en fallos críticos
    # Nota: algunos gates pueden ser warnings, no fallos críticos
    critical_failures = sum(1 for g in results["gates"] 
                          if g["status"] == "failed" and g["name"] in ["ethics_gate", "integrity_system"])
    
    if critical_failures > 0:
        logger.error("❌ Fallos críticos en scientific gates")
        exit(1)
    else:
        logger.info("✅ Scientific gates validation passed")
        exit(0)


if __name__ == "__main__":
    main()
