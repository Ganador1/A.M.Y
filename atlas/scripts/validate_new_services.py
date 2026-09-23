"""
Validación Determinística de Servicios Ronda 4
================================================

Script para validar las 20 operaciones implementadas en Ronda 4:
- SciPyService: 7 operaciones
- ScikitLearnService: 6 operaciones  
- MatplotlibService: 7 operaciones

Sin loops, sin randomness - validación directa y determinística.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List


class ServiceValidator:
    """Validador determin

ístico de servicios científicos"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "summary": {
                "total_operations": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0.0
            }
        }
    
    async def validate_scipy(self) -> Dict:
        """Valida las 7 operaciones de SciPy"""
        from app.services.scipy_service import SciPyService
        
        service = SciPyService()
        operations = []
        
        # 1. Integración numérica
        print("  📊 Testing integrate...")
        result = await service.process_request({
            "action": "integrate",
            "function": "x**2",
            "limits": [0, 1],
            "method": "quad"
        })
        operations.append({
            "name": "integrate",
            "success": result.get("success", False),
            "result": result
        })
        
        # 2. Optimización
        print("  📊 Testing optimize...")
        result = await service.process_request({
            "action": "optimize",
            "function": "x**2 + 3*x + 2",
            "initial_guess": 0.0,
            "method": "minimize"
        })
        operations.append({
            "name": "optimize",
            "success": result.get("success", False),
            "result": result
        })
        
        # 3. Interpolación
        print("  📊 Testing interpolate...")
        result = await service.process_request({
            "action": "interpolate",
            "x_data": [0, 1, 2, 3, 4],
            "y_data": [0, 1, 4, 9, 16],
            "kind": "cubic",
            "num_points": 10
        })
        operations.append({
            "name": "interpolate",
            "success": result.get("success", False),
            "result": result
        })
        
        # 4. FFT
        print("  📊 Testing fft...")
        result = await service.process_request({
            "action": "fft",
            "signal": [1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0],
            "sampling_rate": 100.0
        })
        operations.append({
            "name": "fft",
            "success": result.get("success", False),
            "result": result
        })
        
        # 5. Estadística
        print("  📊 Testing stats...")
        result = await service.process_request({
            "action": "stats",
            "data": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            "test_type": "ttest"
        })
        operations.append({
            "name": "stats",
            "success": result.get("success", False),
            "result": result
        })
        
        # 6. Álgebra lineal
        print("  📊 Testing linear_algebra...")
        result = await service.process_request({
            "action": "linear_algebra",
            "matrix": [[1, 2], [3, 4]],
            "type": "det"  # Parámetro correcto es 'type', no 'operation'
        })
        operations.append({
            "name": "linear_algebra",
            "success": result.get("success", False),
            "result": result
        })
        
        # 7. Resolver ODE
        print("  📊 Testing ode_solve...")
        result = await service.process_request({
            "action": "ode_solve",
            "equation_type": "exponential_decay",
            "initial_conditions": [1.0],
            "time_span": [0.0, 5.0],
            "decay_rate": 0.5
        })
        operations.append({
            "name": "ode_solve",
            "success": result.get("success", False),
            "result": result
        })
        
        successful = sum(1 for op in operations if op["success"])
        return {
            "service": "SciPyService",
            "total_operations": len(operations),
            "successful": successful,
            "failed": len(operations) - successful,
            "success_rate": successful / len(operations),
            "operations": operations
        }
    
    async def validate_scikit_learn(self) -> Dict:
        """Valida las 6 operaciones de Scikit-Learn"""
        from app.services.scikit_learn_service import ScikitLearnService
        
        service = ScikitLearnService()
        operations = []
        
        # 1. Clasificación
        print("  🤖 Testing classification...")
        result = await service.process_request({
            "action": "classification",
            "n_samples": 50,
            "n_features": 3,
            "test_size": 0.3
        })
        operations.append({
            "name": "classification",
            "success": result.get("success", False),
            "result": result
        })
        
        # 2. Regresión
        print("  🤖 Testing regression...")
        result = await service.process_request({
            "action": "regression",
            "n_samples": 50,
            "n_features": 2,
            "test_size": 0.3
        })
        operations.append({
            "name": "regression",
            "success": result.get("success", False),
            "result": result
        })
        
        # 3. Clustering
        print("  🤖 Testing clustering...")
        result = await service.process_request({
            "action": "clustering",
            "n_samples": 60,
            "n_features": 2,
            "n_clusters": 3
        })
        operations.append({
            "name": "clustering",
            "success": result.get("success", False),
            "result": result
        })
        
        # 4. Reducción de dimensionalidad
        print("  🤖 Testing dimensionality_reduction...")
        result = await service.process_request({
            "action": "dimensionality_reduction",
            "n_samples": 50,
            "n_features": 8,
            "n_components": 2
        })
        operations.append({
            "name": "dimensionality_reduction",
            "success": result.get("success", False),
            "result": result
        })
        
        # 5. Validación cruzada
        print("  🤖 Testing cross_validation...")
        result = await service.process_request({
            "action": "cross_validation",
            "n_samples": 50,
            "n_features": 3,
            "cv_folds": 3
        })
        operations.append({
            "name": "cross_validation",
            "success": result.get("success", False),
            "result": result
        })
        
        # 6. Selección de features
        print("  🤖 Testing feature_selection...")
        result = await service.process_request({
            "action": "feature_selection",
            "n_samples": 50,
            "n_features": 6,
            "k_best": 3
        })
        operations.append({
            "name": "feature_selection",
            "success": result.get("success", False),
            "result": result
        })
        
        successful = sum(1 for op in operations if op["success"])
        return {
            "service": "ScikitLearnService",
            "total_operations": len(operations),
            "successful": successful,
            "failed": len(operations) - successful,
            "success_rate": successful / len(operations),
            "operations": operations
        }
    
    async def validate_matplotlib(self) -> Dict:
        """Valida las 7 operaciones de Matplotlib"""
        from app.services.matplotlib_service import MatplotlibService
        
        service = MatplotlibService()
        operations = []
        
        # 1. Line plot
        print("  📈 Testing create_line_plot...")
        result = await service.process_request({
            "action": "create_line_plot",
            "x_data": [1, 2, 3, 4, 5],
            "y_data": [1, 4, 9, 16, 25],
            "title": "Validation Line Plot"
        })
        operations.append({
            "name": "create_line_plot",
            "success": result.get("success", False),
            "has_plot": "plot_base64" in result if result.get("success") else False
        })
        
        # 2. Scatter plot
        print("  📈 Testing create_scatter_plot...")
        result = await service.process_request({
            "action": "create_scatter_plot",
            "x_data": [1, 2, 3, 4, 5],
            "y_data": [2, 4, 6, 8, 10],
            "title": "Validation Scatter"
        })
        operations.append({
            "name": "create_scatter_plot",
            "success": result.get("success", False),
            "has_plot": "plot_base64" in result if result.get("success") else False
        })
        
        # 3. Histogram
        print("  📈 Testing create_histogram...")
        result = await service.process_request({
            "action": "create_histogram",
            "data": [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5],
            "bins": 5,
            "title": "Validation Histogram"
        })
        operations.append({
            "name": "create_histogram",
            "success": result.get("success", False),
            "has_plot": "plot_base64" in result if result.get("success") else False
        })
        
        # 4. Bar plot
        print("  📈 Testing create_bar_plot...")
        result = await service.process_request({
            "action": "create_bar_plot",
            "categories": ["A", "B", "C", "D"],
            "values": [10, 25, 15, 30],
            "title": "Validation Bar Plot"
        })
        operations.append({
            "name": "create_bar_plot",
            "success": result.get("success", False),
            "has_plot": "plot_base64" in result if result.get("success") else False
        })
        
        # 5. Heatmap
        print("  📈 Testing create_heatmap...")
        result = await service.process_request({
            "action": "create_heatmap",
            "data": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            "title": "Validation Heatmap"
        })
        operations.append({
            "name": "create_heatmap",
            "success": result.get("success", False),
            "has_plot": "plot_base64" in result if result.get("success") else False
        })
        
        # 6. Contour plot
        print("  📈 Testing create_contour_plot...")
        result = await service.process_request({
            "action": "create_contour_plot",
            "function": "x**2 + y**2",
            "x_range": [-5, 5],
            "y_range": [-5, 5],
            "title": "Validation Contour"
        })
        operations.append({
            "name": "create_contour_plot",
            "success": result.get("success", False),
            "has_plot": "plot_base64" in result if result.get("success") else False
        })
        
        # 7. 3D Surface
        print("  📈 Testing create_3d_surface...")
        result = await service.process_request({
            "action": "create_3d_surface",
            "function": "np.sin(np.sqrt(x**2 + y**2))",
            "x_range": [-5, 5],
            "y_range": [-5, 5],
            "title": "Validation 3D Surface"
        })
        operations.append({
            "name": "create_3d_surface",
            "success": result.get("success", False),
            "has_plot": "plot_base64" in result if result.get("success") else False
        })
        
        successful = sum(1 for op in operations if op["success"])
        return {
            "service": "MatplotlibService",
            "total_operations": len(operations),
            "successful": successful,
            "failed": len(operations) - successful,
            "success_rate": successful / len(operations),
            "operations": operations
        }
    
    async def run_validation(self):
        """Ejecuta validación completa"""
        print("\n" + "="*70)
        print("🔬 VALIDACIÓN DETERMINÍSTICA - SERVICIOS RONDA 4")
        print("="*70 + "\n")
        
        # SciPy
        print("📊 SciPyService (7 operaciones):")
        scipy_results = await self.validate_scipy()
        self.results["services"]["scipy"] = scipy_results
        print(f"   ✅ {scipy_results['successful']}/{scipy_results['total_operations']} exitosas ({scipy_results['success_rate']*100:.1f}%)\n")
        
        # Scikit-Learn
        print("🤖 ScikitLearnService (6 operaciones):")
        scikit_results = await self.validate_scikit_learn()
        self.results["services"]["scikit_learn"] = scikit_results
        print(f"   ✅ {scikit_results['successful']}/{scikit_results['total_operations']} exitosas ({scikit_results['success_rate']*100:.1f}%)\n")
        
        # Matplotlib
        print("📈 MatplotlibService (7 operaciones):")
        matplotlib_results = await self.validate_matplotlib()
        self.results["services"]["matplotlib"] = matplotlib_results
        print(f"   ✅ {matplotlib_results['successful']}/{matplotlib_results['total_operations']} exitosas ({matplotlib_results['success_rate']*100:.1f}%)\n")
        
        # Summary
        total_ops = scipy_results["total_operations"] + scikit_results["total_operations"] + matplotlib_results["total_operations"]
        total_success = scipy_results["successful"] + scikit_results["successful"] + matplotlib_results["successful"]
        total_failed = total_ops - total_success
        
        self.results["summary"]["total_operations"] = total_ops
        self.results["summary"]["successful"] = total_success
        self.results["summary"]["failed"] = total_failed
        self.results["summary"]["success_rate"] = total_success / total_ops if total_ops > 0 else 0.0
        
        print("="*70)
        print(f"📊 RESUMEN FINAL:")
        print(f"   Total operaciones: {total_ops}")
        print(f"   ✅ Exitosas: {total_success}")
        print(f"   ❌ Fallidas: {total_failed}")
        print(f"   📈 Tasa de éxito: {self.results['summary']['success_rate']*100:.1f}%")
        print("="*70 + "\n")
        
        # Save results
        output_file = f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"💾 Resultados guardados en: {output_file}\n")
        
        return self.results


async def main():
    """Entry point"""
    validator = ServiceValidator()
    await validator.run_validation()


if __name__ == "__main__":
    asyncio.run(main())
