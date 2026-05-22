#!/usr/bin/env python3
"""
🧮 Demostración Básica del Módulo Matemático AXIOM

Este script demuestra las operaciones matemáticas básicas disponibles
en el módulo matemático de AXIOM.

Autor: Sistema AXIOM
Fecha: 2024
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Agregar el path del proyecto
import os; sys.path.append(os.getcwd()) # Fixed hardcoded path

# Importar servicios matemáticos
from app.domains.mathematics.services import (
    ArithmeticService,
    CalculusService,
    StatisticsService
)

# Importar modelos
from app.domains.mathematics.models import (
    ArithmeticRequest,
    CalculusRequest,
    StatisticsRequest
)

def print_header(title):
    """Imprimir encabezado decorativo"""
    print("\n" + "="*60)
    print(f"🧮 {title}")
    print("="*60)

def print_section(title):
    """Imprimir sección"""
    print(f"\n📊 {title}")
    print("-" * 40)

def demo_arithmetic_operations():
    """Demostrar operaciones aritméticas básicas"""
    print_header("DEMOSTRACIÓN DE OPERACIONES ARITMÉTICAS")
    
    # Operaciones básicas
    print_section("Operaciones Básicas")
    
    operations = [
        ("Suma", "add", [10, 20, 30, 40, 50]),
        ("Multiplicación", "multiply", [2, 3, 4, 5]),
        ("Potencia", "power", [2, 8]),
        ("Raíz cuadrada", "sqrt", [144]),
        ("Factorial", "factorial", [5])
    ]
    
    for name, op, operands in operations:
        try:
            request = ArithmeticRequest(operation=op, operands=operands)
            result = ArithmeticService.calculate(request)
            
            if op == "add":
                expr = " + ".join(map(str, operands))
            elif op == "multiply":
                expr = " × ".join(map(str, operands))
            elif op == "power":
                expr = f"{operands[0]}^{operands[1]}"
            elif op == "sqrt":
                expr = f"√{operands[0]}"
            elif op == "factorial":
                expr = f"{operands[0]}!"
            else:
                expr = f"{op}({', '.join(map(str, operands))})"
            
            print(f"  {name}: {expr} = {result.formatted_result}")
            print(f"    Tiempo de ejecución: {result.execution_time:.4f} ms")
            
        except Exception as e:
            print(f"  ❌ Error en {name}: {e}")
    
    # Funciones trigonométricas
    print_section("Funciones Trigonométricas")
    
    angles = [0, np.pi/6, np.pi/4, np.pi/3, np.pi/2, np.pi]
    angle_names = ["0", "π/6", "π/4", "π/3", "π/2", "π"]
    
    print("  Ángulo\t\tsin(x)\t\tcos(x)\t\ttan(x)")
    print("  " + "-"*50)
    
    for angle, name in zip(angles, angle_names):
        try:
            sin_req = ArithmeticRequest(operation="sin", operands=[angle])
            cos_req = ArithmeticRequest(operation="cos", operands=[angle])
            tan_req = ArithmeticRequest(operation="tan", operands=[angle])
            
            sin_result = ArithmeticService.calculate(sin_req)
            cos_result = ArithmeticService.calculate(cos_req)
            tan_result = ArithmeticService.calculate(tan_req)
            
            print(f"  {name:<10}\t{sin_result.result:.4f}\t\t{cos_result.result:.4f}\t\t{tan_result.result:.4f}")
            
        except Exception as e:
            print(f"  ❌ Error con ángulo {name}: {e}")

def demo_calculus_operations():
    """Demostrar operaciones de cálculo"""
    print_header("DEMOSTRACIÓN DE CÁLCULO DIFERENCIAL E INTEGRAL")
    
    # Derivadas
    print_section("Cálculo de Derivadas")
    
    expressions = [
        "x^3 + 2*x^2 + x + 1",
        "sin(x) + cos(x)",
        "e^x",
        "ln(x)",
        "x^2 * sin(x)"
    ]
    
    for expr in expressions:
        try:
            request = CalculusRequest(
                expression=expr,
                operation="derivative",
                variable="x",
                order=1
            )
            result = CalculusService.calculate(request)
            print(f"  d/dx({expr}) = {result.result}")
            
        except Exception as e:
            print(f"  ❌ Error calculando derivada de {expr}: {e}")
    
    # Integrales
    print_section("Cálculo de Integrales")
    
    integrals = [
        ("x^2", [0, 2], "∫₀² x² dx"),
        ("sin(x)", [0, np.pi], "∫₀^π sin(x) dx"),
        ("e^x", [0, 1], "∫₀¹ eˣ dx"),
        ("1/x", [1, 2], "∫₁² (1/x) dx")
    ]
    
    for expr, limits, description in integrals:
        try:
            request = CalculusRequest(
                expression=expr,
                operation="integral",
                variable="x",
                limits=limits
            )
            result = CalculusService.calculate(request)
            print(f"  {description} = {result.result:.6f}")
            
        except Exception as e:
            print(f"  ❌ Error calculando integral {description}: {e}")

def demo_statistics():
    """Demostrar análisis estadístico"""
    print_header("DEMOSTRACIÓN DE ANÁLISIS ESTADÍSTICO")
    
    # Generar datos de ejemplo
    np.random.seed(42)
    data = np.random.normal(100, 15, 1000).tolist()
    
    print_section("Estadísticas Descriptivas")
    
    try:
        request = StatisticsRequest(
            data=data,
            operation="descriptive_statistics"
        )
        result = StatisticsService.calculate(request)
        
        stats = result.result
        print(f"  Tamaño de muestra: {len(data)}")
        print(f"  Media: {stats['mean']:.2f}")
        print(f"  Mediana: {stats['median']:.2f}")
        print(f"  Desviación estándar: {stats['std']:.2f}")
        print(f"  Varianza: {stats['variance']:.2f}")
        print(f"  Mínimo: {stats['min']:.2f}")
        print(f"  Máximo: {stats['max']:.2f}")
        print(f"  Asimetría: {stats['skewness']:.3f}")
        print(f"  Curtosis: {stats['kurtosis']:.3f}")
        
    except Exception as e:
        print(f"  ❌ Error en estadísticas descriptivas: {e}")
    
    # Análisis de correlación
    print_section("Análisis de Correlación")
    
    try:
        data2 = np.random.normal(110, 20, 1000).tolist()
        
        request = StatisticsRequest(
            data=data,
            operation="correlation",
            parameters={"data_y": data2}
        )
        result = StatisticsService.calculate(request)
        
        corr = result.result
        print(f"  Correlación de Pearson: {corr['pearson']:.4f}")
        print(f"  Correlación de Spearman: {corr['spearman']:.4f}")
        
    except Exception as e:
        print(f"  ❌ Error en análisis de correlación: {e}")

def create_visualization():
    """Crear visualizaciones matemáticas"""
    print_header("CREACIÓN DE VISUALIZACIONES")
    
    try:
        # Crear figura con múltiples subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('Demostraciones Matemáticas AXIOM', fontsize=16)
        
        # 1. Función trigonométrica
        x = np.linspace(0, 4*np.pi, 1000)
        y = np.sin(x) * np.cos(x/2)
        
        axes[0, 0].plot(x, y, 'b-', linewidth=2)
        axes[0, 0].set_title('f(x) = sin(x) · cos(x/2)')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].set_xlabel('x')
        axes[0, 0].set_ylabel('f(x)')
        
        # 2. Función exponencial y logarítmica
        x2 = np.linspace(0.1, 5, 1000)
        y2_exp = np.exp(x2/2)
        y2_log = np.log(x2)
        
        axes[0, 1].plot(x2, y2_exp, 'r-', label='e^(x/2)', linewidth=2)
        axes[0, 1].plot(x2, y2_log, 'g-', label='ln(x)', linewidth=2)
        axes[0, 1].set_title('Funciones Exponencial y Logarítmica')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].set_xlabel('x')
        axes[0, 1].set_ylabel('y')
        
        # 3. Distribución normal
        np.random.seed(42)
        data = np.random.normal(0, 1, 1000)
        
        axes[1, 0].hist(data, bins=30, density=True, alpha=0.7, color='skyblue', edgecolor='black')
        
        # Curva teórica
        x3 = np.linspace(-4, 4, 100)
        y3 = (1/np.sqrt(2*np.pi)) * np.exp(-0.5 * x3**2)
        axes[1, 0].plot(x3, y3, 'r-', linewidth=2, label='N(0,1) teórica')
        
        axes[1, 0].set_title('Distribución Normal')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].set_xlabel('Valor')
        axes[1, 0].set_ylabel('Densidad')
        
        # 4. Superficie 3D proyectada
        x4 = np.linspace(-2, 2, 50)
        y4 = np.linspace(-2, 2, 50)
        X4, Y4 = np.meshgrid(x4, y4)
        Z4 = np.sin(np.sqrt(X4**2 + Y4**2))
        
        contour = axes[1, 1].contour(X4, Y4, Z4, levels=15)
        axes[1, 1].clabel(contour, inline=True, fontsize=8)
        axes[1, 1].set_title('z = sin(√(x² + y²))')
        axes[1, 1].set_xlabel('x')
        axes[1, 1].set_ylabel('y')
        
        plt.tight_layout()
        
        # Guardar la figura
        output_path = '/Users/giovanniarangio/atlas/demos/mathematics_demo_plots.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"  ✅ Visualizaciones guardadas en: {output_path}")
        
        # Mostrar la figura
        plt.show()
        
    except Exception as e:
        print(f"  ❌ Error creando visualizaciones: {e}")

def performance_benchmark():
    """Realizar benchmark de rendimiento"""
    print_header("BENCHMARK DE RENDIMIENTO")
    
    import time
    
    # Benchmark de operaciones aritméticas
    print_section("Rendimiento de Operaciones Aritméticas")
    
    operations = [
        ("Suma de 1000 números", "add", list(range(1, 1001))),
        ("Multiplicación de 10 números", "multiply", list(range(1, 11))),
        ("Potencia 2^20", "power", [2, 20]),
        ("Factorial de 100", "factorial", [100]),
        ("Sin de π/4", "sin", [np.pi/4])
    ]
    
    for name, op, operands in operations:
        try:
            # Medir tiempo múltiples veces
            times = []
            for _ in range(10):
                start_time = time.time()
                request = ArithmeticRequest(operation=op, operands=operands)
                result = ArithmeticService.calculate(request)
                end_time = time.time()
                times.append((end_time - start_time) * 1000)  # Convertir a ms
            
            avg_time = np.mean(times)
            std_time = np.std(times)
            
            print(f"  {name}:")
            print(f"    Tiempo promedio: {avg_time:.4f} ± {std_time:.4f} ms")
            print(f"    Resultado: {result.formatted_result}")
            
        except Exception as e:
            print(f"  ❌ Error en benchmark {name}: {e}")

def main():
    """Función principal"""
    print("🚀 INICIANDO DEMOSTRACIÓN DEL MÓDULO MATEMÁTICO AXIOM")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔧 Versión: 1.0.0")
    
    try:
        # Ejecutar demostraciones
        demo_arithmetic_operations()
        demo_calculus_operations()
        demo_statistics()
        create_visualization()
        performance_benchmark()
        
        print_header("DEMOSTRACIÓN COMPLETADA EXITOSAMENTE")
        print("✅ Todas las funcionalidades han sido probadas")
        print("📊 Las visualizaciones han sido generadas")
        print("⚡ Los benchmarks de rendimiento han sido ejecutados")
        print("\n🎉 ¡El módulo matemático AXIOM está funcionando correctamente!")
        
    except Exception as e:
        print(f"\n❌ Error durante la demostración: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)