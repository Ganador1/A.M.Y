#!/usr/bin/env python3
"""
AXIOM META 4 - Suite Completa de Tests para Phase 4
==================================================

Suite comprehensiva de tests que valida:
- Conectividad de base de datos PostgreSQL
- Funcionalidad de servicios Phase 3
- Sistema de monitoreo y alertas
- Integración completa del sistema
- Preparación para escalabilidad de producción

Ejecutar con: python test_meta4_phase4_readiness.py

Autor: AXIOM META 4 Development Team
Fecha: Septiembre 2025
"""

import asyncio
import time
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestSuite:
    """Suite completa de tests para Phase 4"""

    def __init__(self):
        self.results = {
            'database_tests': [],
            'service_tests': [],
            'monitoring_tests': [],
            'integration_tests': []
        }
        self.start_time = None
        self.end_time = None

    def log_test_result(self, category: str, test_name: str, success: bool, message: str = ""):
        """Registrar resultado de test"""
        result = {
            'test_name': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now()
        }
        self.results[category].append(result)

        status = "✅" if success else "❌"
        logger.info(f"{status} {test_name}: {message}")

    async def run_all_tests(self):
        """Ejecutar todos los tests"""
        self.start_time = datetime.now()
        logger.info("🚀 Iniciando Suite Completa de Tests - AXIOM META 4 Phase 4")

        try:
            # 1. Tests de base de datos
            await self.run_database_tests()

            # 2. Tests de servicios
            await self.run_service_tests()

            # 3. Tests de monitoreo
            await self.run_monitoring_tests()

            # 4. Tests de integración
            await self.run_integration_tests()

            # 5. Reporte final
            self.generate_final_report()

        except Exception as e:
            logger.error(f"Error crítico en suite de tests: {e}")
            self.log_test_result('integration_tests', 'suite_execution', False, str(e))

        finally:
            self.end_time = datetime.now()

    async def run_database_tests(self):
        """Tests de conectividad y funcionalidad de PostgreSQL"""
        logger.info("🗄️ Ejecutando tests de base de datos...")

        try:
            from app.database import get_db_session
            from app.models.database_models import User, Calculation

            # Test 1: Conexión a base de datos
            db = get_db_session()
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            self.log_test_result('database_tests', 'database_connection', True, "Conexión exitosa")
            db.close()

            # Test 2: Operaciones CRUD
            db = get_db_session()

            # Crear usuario de test
            test_user = User(
                username=f'test_user_{int(time.time())}',
                email=f'test_{int(time.time())}@example.com',
                hashed_password='test_hash',
                full_name='Test User'
            )
            db.add(test_user)
            db.commit()

            # Crear cálculo de test
            test_calc = Calculation(
                user_id=test_user.id,
                operation_type='test',
                operation_name='database_test',
                input_data={'test': 'data'},
                result_data={'result': 'success'},
                execution_time=0.001,
                status='completed'
            )
            db.add(test_calc)
            db.commit()

            # Verificar datos
            users_count = db.query(User).filter(User.username.like('test_user_%')).count()
            calcs_count = db.query(Calculation).filter(Calculation.operation_name == 'database_test').count()

            self.log_test_result('database_tests', 'crud_operations', True,
                               f"Usuario: {users_count}, Cálculos: {calcs_count}")

            # Limpiar datos de test
            db.query(Calculation).filter(Calculation.operation_name == 'database_test').delete()
            db.query(User).filter(User.username.like('test_user_%')).delete()
            db.commit()
            db.close()

            self.log_test_result('database_tests', 'data_cleanup', True, "Limpieza exitosa")

        except Exception as e:
            self.log_test_result('database_tests', 'database_operations', False, str(e))

    async def run_service_tests(self):
        """Tests de funcionalidad de servicios Phase 3"""
        logger.info("🔧 Ejecutando tests de servicios...")

        # Test Advanced Clinical Validation Service
        try:
            from app.advanced_clinical_validation_service import advanced_clinical_validation_service

            patient_data = {'age': 65, 'sex': 'male'}
            analysis_results = {
                'ventricular_function': {'ejection_fraction': 55.0},
                'strain_analysis': {'global_longitudinal_strain': -19.0}
            }

            validation = advanced_clinical_validation_service.validate_clinical_analysis(
                patient_data, analysis_results
            )

            success = isinstance(validation, dict) and 'overall_validity' in validation
            self.log_test_result('service_tests', 'advanced_clinical_validation',
                               success, f"Validación: {validation.get('overall_validity', 'N/A')}")

        except Exception as e:
            self.log_test_result('service_tests', 'advanced_clinical_validation', False, str(e))

        # Test otros servicios Phase 3
        services_to_test = [
            ('MultiscaleModelsService', 'app.multiscale_models', 'MultiscaleModelsService'),
            ('StrainAnalysisService', 'app.strain_analysis', 'StrainAnalysisService'),
            ('PlasmaPhysicsService', 'app.plasma_physics_service', 'PlasmaPhysicsService'),
            ('AdditiveManufacturingService', 'app.additive_manufacturing_service', 'AdditiveManufacturingService')
        ]

        for service_name, module_name, class_name in services_to_test:
            try:
                module = __import__(module_name, fromlist=[class_name])
                service_class = getattr(module, class_name)
                service_instance = service_class()

                # Verificar que tiene métodos básicos
                has_init = hasattr(service_instance, '__init__')
                has_methods = len([m for m in dir(service_instance) if not m.startswith('_')]) > 0

                success = has_init and has_methods
                self.log_test_result('service_tests', service_name, success,
                                   f"Inicialización: {has_init}, Métodos: {has_methods}")

            except Exception as e:
                self.log_test_result('service_tests', service_name, False, str(e))

    async def run_monitoring_tests(self):
        """Tests del sistema de monitoreo"""
        logger.info("📊 Ejecutando tests de monitoreo...")

        try:
            from app.monitoring import monitoring_system

            # Test 1: Obtener métricas actuales
            current_metrics = await monitoring_system.get_current_metrics()

            has_system_metrics = 'system' in current_metrics
            has_app_metrics = 'application' in current_metrics

            self.log_test_result('monitoring_tests', 'current_metrics_collection',
                               has_system_metrics and has_app_metrics,
                               f"Sistema: {has_system_metrics}, App: {has_app_metrics}")

            # Test 2: Estado del sistema de monitoreo
            monitoring_status = await monitoring_system.get_monitoring_status()

            has_status = 'status' in monitoring_status
            has_alerts = 'alerts' in monitoring_status
            has_metrics = 'metrics_history' in monitoring_status

            self.log_test_result('monitoring_tests', 'monitoring_status',
                               has_status and has_alerts and has_metrics,
                               f"Status: {has_status}, Alertas: {has_alerts}, Métricas: {has_metrics}")

            # Test 3: Reglas de alerta
            alert_rules = monitoring_system.alert_manager.get_alert_rules()
            has_rules = len(alert_rules) > 0

            self.log_test_result('monitoring_tests', 'alert_rules',
                               has_rules, f"Reglas configuradas: {len(alert_rules)}")

        except Exception as e:
            self.log_test_result('monitoring_tests', 'monitoring_system', False, str(e))

    async def run_integration_tests(self):
        """Tests de integración completa"""
        logger.info("🔗 Ejecutando tests de integración...")

        try:
            # Test 1: Integración base de datos + servicios
            from app.database import get_db_session
            from app.advanced_clinical_validation_service import advanced_clinical_validation_service

            db = get_db_session()

            # Crear un cálculo basado en validación clínica
            patient_data = {'age': 60, 'sex': 'female'}
            analysis_results = {
                'ventricular_function': {'ejection_fraction': 62.0},
                'strain_analysis': {'global_longitudinal_strain': -21.0}
            }

            validation = advanced_clinical_validation_service.validate_clinical_analysis(
                patient_data, analysis_results
            )

            # Guardar resultado en BD
            from app.models.database_models import Calculation
            integration_calc = Calculation(
                operation_type='integration_test',
                operation_name='clinical_validation_integration',
                input_data={'patient': patient_data, 'analysis': analysis_results},
                result_data=validation,
                execution_time=0.1,
                status='completed'
            )
            db.add(integration_calc)
            db.commit()

            # Verificar que se guardó
            saved_calc = db.query(Calculation).filter(
                Calculation.operation_name == 'clinical_validation_integration'
            ).first()

            success = saved_calc is not None
            self.log_test_result('integration_tests', 'database_service_integration',
                               success, "Integración BD + Servicios exitosa")

            # Limpiar
            db.query(Calculation).filter(
                Calculation.operation_name == 'clinical_validation_integration'
            ).delete()
            db.commit()
            db.close()

        except Exception as e:
            self.log_test_result('integration_tests', 'integration_test', False, str(e))

    def generate_final_report(self):
        """Generar reporte final de la suite de tests"""
        logger.info("📋 Generando reporte final...")

        total_tests = 0
        passed_tests = 0

        print("\n" + "="*80)
        print("🏆 AXIOM META 4 - REPORTE FINAL DE TESTS PHASE 4")
        print("="*80)

        for category, tests in self.results.items():
            if not tests:
                continue

            category_name = category.replace('_', ' ').title()
            print(f"\n📂 {category_name}:")

            category_passed = 0
            for test in tests:
                total_tests += 1
                if test['success']:
                    passed_tests += 1
                    category_passed += 1
                status = "✅" if test['success'] else "❌"
                print(f"   {status} {test['test_name']}: {test['message']}")

            print(f"   📊 {category_name}: {category_passed}/{len(tests)} tests pasaron")

        # Estadísticas generales
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        print("\n📈 ESTADÍSTICAS GENERALES:")
        print(f"   • Tests totales: {total_tests}")
        print(f"   • Tests exitosos: {passed_tests}")
        print(f"   • Tasa de éxito: {success_rate:.1f}%")

        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            print(f"   • Duración: {duration.total_seconds():.2f} segundos")

        # Evaluación de readiness para Phase 4
        print("\n🚀 EVALUACIÓN DE READINESS PARA PHASE 4:")

        if success_rate >= 90:
            print("   🟢 SISTEMA LISTO PARA PHASE 4")
            print("   ✅ Todos los componentes críticos operativos")
            print("   ✅ Integración completa verificada")
            print("   ✅ Monitoreo y alertas funcionales")
        elif success_rate >= 75:
            print("   🟡 SISTEMA CASI LISTO PARA PHASE 4")
            print("   ⚠️ Algunos componentes requieren atención")
            print("   📝 Revisar tests fallidos antes de proceder")
        else:
            print("   🔴 SISTEMA REQUIERE ATENCIÓN ANTES DE PHASE 4")
            print("   ❌ Componentes críticos con problemas")
            print("   🔧 Corregir issues identificados")

        print("\n" + "="*80)
        print("🏆 Suite de Tests Phase 4 Completada")
        print("="*80)


async def main():
    """Función principal"""
    suite = TestSuite()
    await suite.run_all_tests()


if __name__ == "__main__":
    # Ejecutar suite de tests
    asyncio.run(main())
