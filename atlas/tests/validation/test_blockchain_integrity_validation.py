"""
Test Blockchain Validation and Integrity Verification
====================================================

Script de prueba para validar el funcionamiento completo del sistema
de validación blockchain e integridad para PINN.

Pruebas incluidas:
- Validación blockchain básica
- Verificación de integridad local
- Auditoría de integridad
- Integración entre servicios
- Verificación de consenso distribuido

Autor: AXIOM Mathematics AI Engine Team
Fecha: Septiembre 2025
Versión: 1.0.0
"""

import asyncio
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_blockchain_validation():
    """Probar validación blockchain"""
    logger.info("🚀 Iniciando pruebas de validación blockchain...")

    try:
        from app.blockchain_validation import blockchain_service, PINNResult

        # Crear resultado PINN de prueba
        test_result = PINNResult(
            result_id="test_result_001",
            model_type="pinn",
            pde_type="heat",
            input_parameters={"alpha": 0.01, "domain": [0, 1]},
            output_data={"solution": [0.1, 0.2, 0.3, 0.4], "error": 0.001},
            confidence_score=0.95,
            execution_time=1.2,
            timestamp=datetime.now(),
            node_id=blockchain_service.node_id
        )

        # Probar validación
        proof = await blockchain_service.validate_pinn_result(test_result, validator_count=3)

        logger.info(f"✅ Validación blockchain completada: {proof.consensus_reached}")
        logger.info(f"   - Proof ID: {proof.proof_id}")
        logger.info(f"   - Signatures: {len(proof.validator_signatures)}")
        logger.info(f"   - Consensus: {proof.consensus_reached}")

        # Probar verificación
        is_valid, details = blockchain_service.verify_result_integrity(
            proof.result_hash,
            proof.proof_id
        )

        logger.info(f"✅ Verificación blockchain: {is_valid}")
        if not is_valid:
            logger.warning(f"   Detalles: {details}")

        return proof.consensus_reached and is_valid

    except Exception as e:
        logger.error(f"❌ Error en validación blockchain: {e}")
        return False

async def test_integrity_verification():
    """Probar verificación de integridad"""
    logger.info("🔍 Iniciando pruebas de verificación de integridad...")

    try:
        from app.integrity_verification import integrity_service

        # Probar verificación básica
        record = await integrity_service.verify_result_integrity(
            "test_result_001",
            "comprehensive",
            True
        )

        logger.info(f"✅ Verificación de integridad completada: {record.integrity_status}")
        logger.info(f"   - Record ID: {record.record_id}")
        logger.info(f"   - Confidence: {record.confidence_score:.3f}")
        logger.info(f"   - Method: {record.verification_method}")

        # Probar auditoría con el mismo resultado que se validó
        audit = await integrity_service.perform_integrity_audit(
            "test_result_001",  # Usar el mismo resultado que se validó
            "full",
            True
        )

        logger.info(f"✅ Auditoría de integridad completada: {audit.audit_status}")
        logger.info(f"   - Audit ID: {audit.audit_id}")
        logger.info(f"   - Findings: {len(audit.findings)}")
        logger.info(f"   - Recommendations: {len(audit.recommendations)}")

        return record.integrity_status == "valid" and audit.audit_status == "passed"

    except Exception as e:
        logger.error(f"❌ Error en verificación de integridad: {e}")
        return False

async def test_service_integration():
    """Probar integración entre servicios"""
    logger.info("🔗 Iniciando pruebas de integración de servicios...")

    try:
        from app.blockchain_validation import blockchain_service, create_pinn_result_hash
        from app.integrity_verification import integrity_service

        # Crear datos de prueba
        test_data = {
            "result_id": "integration_test_001",
            "model_type": "pinn",
            "pde_type": "wave",
            "input_parameters": {"c": 1.0, "domain": [0, 2]},
            "output_data": {"solution": [0.0, 0.5, 1.0, 0.5], "error": 0.002},
            "confidence_score": 0.92,
            "execution_time": 2.1,
            "timestamp": datetime.now().isoformat()
        }

        # Crear hash usando utilidad
        result_hash = create_pinn_result_hash(test_data)
        logger.info(f"📋 Hash de resultado creado: {result_hash[:16]}...")

        # Verificar integridad
        integrity_record = await integrity_service.verify_result_integrity(
            test_data["result_id"], "comprehensive"
        )

        # Verificar con blockchain
        is_valid, blockchain_details = blockchain_service.verify_result_integrity(
            result_hash, test_data["result_id"]
        )

        logger.info(f"✅ Integración servicios: Integrity={integrity_record.integrity_status}, Blockchain={is_valid}")

        return integrity_record.integrity_status == "valid"

    except Exception as e:
        logger.error(f"❌ Error en integración de servicios: {e}")
        return False

async def test_system_stats():
    """Probar obtención de estadísticas del sistema"""
    logger.info("📊 Probando estadísticas del sistema...")

    try:
        from app.blockchain_validation import blockchain_service
        from app.integrity_verification import integrity_service

        # Estadísticas blockchain
        blockchain_stats = blockchain_service.get_validation_stats()

        logger.info("📊 Estadísticas Blockchain:")
        logger.info(f"   - Total blocks: {blockchain_stats['total_blocks']}")
        logger.info(f"   - Total validations: {blockchain_stats['total_validations']}")
        logger.info(f"   - Consensus threshold: {blockchain_stats['consensus_threshold']}")

        # Estadísticas integridad
        integrity_stats = integrity_service.get_integrity_stats()

        logger.info("📊 Estadísticas Integridad:")
        logger.info(f"   - Total records: {integrity_stats['total_records']}")
        logger.info(f"   - Valid records: {integrity_stats['valid_records']}")
        logger.info(f"   - Integrity rate: {integrity_stats['integrity_rate']:.3f}")

        return True

    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas: {e}")
        return False

async def main():
    """Función principal de pruebas"""
    logger.info("🎯 Iniciando suite de pruebas AXIOM Blockchain & Integrity Validation")
    logger.info("=" * 70)

    test_results = []

    # Ejecutar pruebas
    tests = [
        ("Validación Blockchain", test_blockchain_validation),
        ("Verificación Integridad", test_integrity_verification),
        ("Integración Servicios", test_service_integration),
        ("Estadísticas Sistema", test_system_stats)
    ]

    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"🧪 Ejecutando: {test_name}")
        logger.info(f"{'='*50}")

        try:
            result = await test_func()
            test_results.append((test_name, result))

            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.warning(f"⚠️  {test_name}: FAILED")

        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            test_results.append((test_name, False))

    # Resumen final
    logger.info(f"\n{'='*70}")
    logger.info("📋 RESUMEN FINAL DE PRUEBAS")
    logger.info(f"{'='*70}")

    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{status} {test_name}")

    logger.info(f"\n🎯 RESULTADO GLOBAL: {passed_tests}/{total_tests} pruebas pasaron")

    if passed_tests == total_tests:
        logger.info("🎉 ¡Todas las pruebas pasaron! Sistema blockchain e integridad listo.")
        return True
    else:
        logger.warning("⚠️  Algunas pruebas fallaron. Revisar logs para detalles.")
        return False

if __name__ == "__main__":
    # Ejecutar pruebas
    success = asyncio.run(main())

    # Código de salida
    exit(0 if success else 1)
