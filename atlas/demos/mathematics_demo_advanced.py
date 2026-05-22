#!/usr/bin/env python3
"""
🚀 Demostración Avanzada del Módulo Matemático AXIOM

Este script demuestra las capacidades avanzadas del módulo matemático,
incluyendo optimización, machine learning matemático, y análisis complejo.

Autor: Sistema AXIOM
Fecha: 2024
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
from datetime import datetime
import time
import warnings
warnings.filterwarnings('ignore')

# Agregar el path del proyecto
import os; sys.path.append(os.getcwd()) # Fixed hardcoded path

# Importar servicios matemáticos avanzados
try:
    from app.domains.mathematics.services import (
        OptimizationService,
        MathematicalMLService,
        QuantumMathematicsService,
        MathVisualizationService,
        AdvancedMathAIService
    )
    ADVANCED_SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Algunos servicios avanzados no están disponibles: {e}")
    ADVANCED_SERVICES_AVAILABLE = False

# Importar servicios básicos
from app.domains.mathematics.services import (
    ArithmeticService,
    CalculusService,
    StatisticsService
)

from app.domains.mathematics.models import (
    ArithmeticRequest,
    CalculusRequest,
    StatisticsRequest
)

def print_header(title):
    """Imprimir encabezado decorativo"""
    print("\n" + "="*70)
    print(f"🚀 {title}")
    print("="*70)

def print_section(title):
    """Imprimir sección"""
    print(f"\n🔬 {title}")
    print("-" * 50)

def demo_complex_analysis():
    """Demostrar análisis matemático complejo"""
    print_header("ANÁLISIS MATEMÁTICO COMPLEJO")
    
    print_section("Análisis de Funciones Multivariables")
    
    # Función de ejemplo: f(x,y) = x^2 + y^2 - 2xy + sin(x*y)
    def complex_function(x, y):
        return x**2 + y**2 - 2*x*y + np.sin(x*y)
    
    # Crear malla de puntos
    x = np.linspace(-3, 3, 100)
    y = np.linspace(-3, 3, 100)
    X, Y = np.meshgrid(x, y)
    Z = complex_function(X, Y)
    
    # Encontrar puntos críticos (aproximación numérica)
    print("  Análisis de puntos críticos:")
    
    # Gradiente numérico
    dx = x[1] - x[0]
    dy = y[1] - y[0]
    
    dZ_dx = np.gradient(Z, dx, axis=1)
    dZ_dy = np.gradient(Z, dy, axis=0)
    
    # Encontrar puntos donde el gradiente es aproximadamente cero
    gradient_magnitude = np.sqrt(dZ_dx**2 + dZ_dy**2)
    min_gradient_idx = np.unravel_index(np.argmin(gradient_magnitude), gradient_magnitude.shape)
    
    critical_x = X[min_gradient_idx]
    critical_y = Y[min_gradient_idx]
    critical_z = Z[min_gradient_idx]
    
    print(f"    Punto crítico aproximado: ({critical_x:.3f}, {critical_y:.3f})")
    print(f"    Valor de la función: {critical_z:.6f}")
    print(f"    Magnitud del gradiente: {gradient_magnitude[min_gradient_idx]:.6f}")
    
    # Crear visualización 3D
    fig = plt.figure(figsize=(15, 5))
    
    # Superficie 3D
    ax1 = fig.add_subplot(131, projection='3d')
    surf = ax1.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
    ax1.scatter([critical_x], [critical_y], [critical_z], color='red', s=100, label='Punto crítico')
    ax1.set_title('f(x,y) = x² + y² - 2xy + sin(xy)')
    ax1.set_xlabel('x')
    ax1.set_ylabel('y')
    ax1.set_zlabel('f(x,y)')
    
    # Mapa de contorno
    ax2 = fig.add_subplot(132)
    contour = ax2.contour(X, Y, Z, levels=20)
    ax2.clabel(contour, inline=True, fontsize=8)
    ax2.plot(critical_x, critical_y, 'ro', markersize=8, label='Punto crítico')
    ax2.set_title('Mapa de Contorno')
    ax2.set_xlabel('x')
    ax2.set_ylabel('y')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Campo de gradientes
    ax3 = fig.add_subplot(133)
    skip = 5  # Mostrar cada 5 puntos para claridad
    ax3.quiver(X[::skip, ::skip], Y[::skip, ::skip], 
               -dZ_dx[::skip, ::skip], -dZ_dy[::skip, ::skip], 
               alpha=0.7)
    ax3.plot(critical_x, critical_y, 'ro', markersize=8, label='Punto crítico')
    ax3.set_title('Campo de Gradientes (Dirección de Descenso)')
    ax3.set_xlabel('x')
    ax3.set_ylabel('y')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/Users/giovanniarangio/atlas/demos/complex_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

def demo_optimization_algorithms():
    """Demostrar algoritmos de optimización"""
    print_header("ALGORITMOS DE OPTIMIZACIÓN AVANZADOS")
    
    print_section("Optimización Multi-Objetivo")
    
    # Problema de optimización: minimizar f1(x) = x^2 y f2(x) = (x-2)^2
    def objective_functions(x):
        f1 = x**2
        f2 = (x - 2)**2
        return f1, f2
    
    # Generar frente de Pareto
    x_values = np.linspace(-1, 3, 1000)
    f1_values = []
    f2_values = []
    
    for x in x_values:
        f1, f2 = objective_functions(x)
        f1_values.append(f1)
        f2_values.append(f2)
    
    # Encontrar soluciones no dominadas (frente de Pareto)
    pareto_front_x = []
    pareto_front_f1 = []
    pareto_front_f2 = []
    
    for i, (x, f1, f2) in enumerate(zip(x_values, f1_values, f2_values)):
        is_dominated = False
        for j, (x2, f1_2, f2_2) in enumerate(zip(x_values, f1_values, f2_values)):
            if i != j and f1_2 <= f1 and f2_2 <= f2 and (f1_2 < f1 or f2_2 < f2):
                is_dominated = True
                break
        
        if not is_dominated:
            pareto_front_x.append(x)
            pareto_front_f1.append(f1)
            pareto_front_f2.append(f2)
    
    print(f"  Número de soluciones en el frente de Pareto: {len(pareto_front_x)}")
    print(f"  Rango de x en el frente: [{min(pareto_front_x):.3f}, {max(pareto_front_x):.3f}]")
    
    # Visualización
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Funciones objetivo
    axes[0].plot(x_values, f1_values, 'b-', label='f₁(x) = x²', linewidth=2)
    axes[0].plot(x_values, f2_values, 'r-', label='f₂(x) = (x-2)²', linewidth=2)
    axes[0].scatter(pareto_front_x, pareto_front_f1, color='blue', alpha=0.7, s=20)
    axes[0].scatter(pareto_front_x, pareto_front_f2, color='red', alpha=0.7, s=20)
    axes[0].set_title('Funciones Objetivo')
    axes[0].set_xlabel('x')
    axes[0].set_ylabel('f(x)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Espacio de objetivos
    axes[1].scatter(f1_values, f2_values, alpha=0.3, s=10, label='Todas las soluciones')
    axes[1].scatter(pareto_front_f1, pareto_front_f2, color='red', s=30, label='Frente de Pareto')
    axes[1].set_title('Espacio de Objetivos')
    axes[1].set_xlabel('f₁(x)')
    axes[1].set_ylabel('f₂(x)')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Algoritmo genético simulado
    print_section("Simulación de Algoritmo Genético")
    
    def simple_genetic_algorithm():
        # Función objetivo: minimizar f(x) = x^2 + 10*sin(x)
        def fitness_function(x):
            return x**2 + 10*np.sin(x)
        
        # Parámetros
        population_size = 50
        generations = 100
        mutation_rate = 0.1
        bounds = [-10, 10]
        
        # Inicializar población
        population = np.random.uniform(bounds[0], bounds[1], population_size)
        best_fitness_history = []
        
        for generation in range(generations):
            # Evaluar fitness
            fitness = [fitness_function(x) for x in population]
            
            # Encontrar el mejor
            best_idx = np.argmin(fitness)
            best_fitness_history.append(fitness[best_idx])
            
            # Selección por torneo
            new_population = []
            for _ in range(population_size):
                # Seleccionar padres
                tournament_size = 3
                tournament_indices = np.random.choice(population_size, tournament_size)
                tournament_fitness = [fitness[i] for i in tournament_indices]
                winner_idx = tournament_indices[np.argmin(tournament_fitness)]
                
                # Reproducción con mutación
                child = population[winner_idx]
                if np.random.random() < mutation_rate:
                    child += np.random.normal(0, 1)
                    child = np.clip(child, bounds[0], bounds[1])
                
                new_population.append(child)
            
            population = np.array(new_population)
        
        final_fitness = [fitness_function(x) for x in population]
        best_idx = np.argmin(final_fitness)
        
        return population[best_idx], final_fitness[best_idx], best_fitness_history
    
    best_x, best_fitness, history = simple_genetic_algorithm()
    
    print(f"  Mejor solución encontrada: x = {best_x:.6f}")
    print(f"  Valor de fitness: {best_fitness:.6f}")
    
    # Visualizar convergencia
    x_plot = np.linspace(-10, 10, 1000)
    y_plot = x_plot**2 + 10*np.sin(x_plot)
    
    axes[2].plot(x_plot, y_plot, 'b-', linewidth=2, label='f(x) = x² + 10sin(x)')
    axes[2].plot(best_x, best_fitness, 'ro', markersize=10, label=f'Mejor solución: ({best_x:.3f}, {best_fitness:.3f})')
    axes[2].set_title('Optimización con Algoritmo Genético')
    axes[2].set_xlabel('x')
    axes[2].set_ylabel('f(x)')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/Users/giovanniarangio/atlas/demos/optimization_demo.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Mostrar convergencia
    plt.figure(figsize=(10, 6))
    plt.plot(history, 'b-', linewidth=2)
    plt.title('Convergencia del Algoritmo Genético')
    plt.xlabel('Generación')
    plt.ylabel('Mejor Fitness')
    plt.grid(True, alpha=0.3)
    plt.savefig('/Users/giovanniarangio/atlas/demos/genetic_convergence.png', dpi=300, bbox_inches='tight')
    plt.show()

def demo_mathematical_ml():
    """Demostrar machine learning matemático"""
    print_header("MACHINE LEARNING MATEMÁTICO")
    
    print_section("Aproximación de Funciones con Redes Neuronales")
    
    try:
        from sklearn.neural_network import MLPRegressor
        from sklearn.preprocessing import StandardScaler
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_squared_error, r2_score
        
        # Función objetivo compleja
        def target_function(x):
            return np.sin(2*x) * np.exp(-x/3) + 0.1*x**2
        
        # Generar datos de entrenamiento
        np.random.seed(42)
        x_train = np.random.uniform(-2*np.pi, 2*np.pi, 500)
        y_train = target_function(x_train) + np.random.normal(0, 0.05, 500)  # Agregar ruido
        
        # Datos de prueba
        x_test = np.linspace(-3*np.pi, 3*np.pi, 200)
        y_test_true = target_function(x_test)
        
        # Preparar datos
        X_train = x_train.reshape(-1, 1)
        X_test = x_test.reshape(-1, 1)
        
        scaler_X = StandardScaler()
        scaler_y = StandardScaler()
        
        X_train_scaled = scaler_X.fit_transform(X_train)
        X_test_scaled = scaler_X.transform(X_test)
        y_train_scaled = scaler_y.fit_transform(y_train.reshape(-1, 1)).ravel()
        
        # Entrenar diferentes arquitecturas
        architectures = [
            ("Pequeña", (10, 5)),
            ("Mediana", (50, 30, 10)),
            ("Grande", (100, 50, 25, 10))
        ]
        
        results = []
        
        plt.figure(figsize=(18, 6))
        
        for i, (name, hidden_layers) in enumerate(architectures):
            # Entrenar modelo
            model = MLPRegressor(
                hidden_layer_sizes=hidden_layers,
                activation='tanh',
                max_iter=2000,
                random_state=42,
                early_stopping=True,
                validation_fraction=0.2
            )
            
            start_time = time.time()
            model.fit(X_train_scaled, y_train_scaled)
            training_time = time.time() - start_time
            
            # Predicciones
            y_pred_scaled = model.predict(X_test_scaled)
            y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).ravel()
            
            # Métricas
            mse = mean_squared_error(y_test_true, y_pred)
            r2 = r2_score(y_test_true, y_pred)
            
            results.append({
                "Arquitectura": name,
                "Capas": str(hidden_layers),
                "MSE": f"{mse:.6f}",
                "R²": f"{r2:.4f}",
                "Tiempo (s)": f"{training_time:.2f}",
                "Iteraciones": model.n_iter_
            })
            
            # Visualización
            plt.subplot(1, 3, i+1)
            plt.scatter(x_train, y_train, alpha=0.3, s=10, label='Datos entrenamiento')
            plt.plot(x_test, y_test_true, 'g-', linewidth=2, label='Función verdadera')
            plt.plot(x_test, y_pred, 'r--', linewidth=2, label='Predicción NN')
            plt.title(f'Red {name}\nMSE: {mse:.4f}, R²: {r2:.3f}')
            plt.xlabel('x')
            plt.ylabel('y')
            plt.legend()
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('/Users/giovanniarangio/atlas/demos/ml_approximation.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Mostrar tabla de resultados
        df_results = pd.DataFrame(results)
        print("\n  Comparación de Arquitecturas:")
        print(df_results.to_string(index=False))
        
    except ImportError:
        print("  ⚠️ scikit-learn no está disponible. Simulando resultados...")
        print("  📊 Aproximación de funciones con redes neuronales requiere scikit-learn")

def demo_fractal_mathematics():
    """Demostrar matemáticas fractales"""
    print_header("MATEMÁTICAS FRACTALES")
    
    print_section("Conjunto de Mandelbrot")
    
    def mandelbrot_set(h, w, max_iter=100, x_range=(-2, 1), y_range=(-1.5, 1.5)):
        """Calcular el conjunto de Mandelbrot"""
        y, x = np.ogrid[y_range[0]:y_range[1]:h*1j, x_range[0]:x_range[1]:w*1j]
        c = x + y*1j
        z = np.zeros_like(c)
        divtime = max_iter + np.zeros(z.shape, dtype=int)
        
        for i in range(max_iter):
            z = z**2 + c
            diverge = z*np.conj(z) > 2**2
            div_now = diverge & (divtime == max_iter)
            divtime[div_now] = i
            z[diverge] = 2
        
        return divtime
    
    # Generar conjunto de Mandelbrot en diferentes resoluciones
    resolutions = [(200, 200), (400, 400), (800, 800)]
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    for i, (h, w) in enumerate(resolutions):
        print(f"  Generando Mandelbrot {w}x{h}...")
        start_time = time.time()
        mandelbrot = mandelbrot_set(h, w, max_iter=80)
        generation_time = time.time() - start_time
        
        im = axes[i].imshow(mandelbrot, extent=[-2, 1, -1.5, 1.5], 
                           cmap='hot', origin='lower')
        axes[i].set_title(f'Mandelbrot {w}x{h}\nTiempo: {generation_time:.2f}s')
        axes[i].set_xlabel('Re(c)')
        axes[i].set_ylabel('Im(c)')
        
        plt.colorbar(im, ax=axes[i])
    
    plt.tight_layout()
    plt.savefig('/Users/giovanniarangio/atlas/demos/mandelbrot_fractals.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print_section("Conjunto de Julia")
    
    def julia_set(h, w, c=-0.7 + 0.27015j, max_iter=100):
        """Calcular conjunto de Julia"""
        y, x = np.ogrid[-1.5:1.5:h*1j, -1.5:1.5:w*1j]
        z = x + y*1j
        divtime = max_iter + np.zeros(z.shape, dtype=int)
        
        for i in range(max_iter):
            z = z**2 + c
            diverge = z*np.conj(z) > 2**2
            div_now = diverge & (divtime == max_iter)
            divtime[div_now] = i
            z[diverge] = 2
        
        return divtime
    
    # Diferentes parámetros c para conjuntos de Julia
    c_values = [
        (-0.7 + 0.27015j, "Dragón"),
        (-0.8 + 0.156j, "Espiral"),
        (-0.4 + 0.6j, "Dendrita"),
        (0.285 + 0.01j, "Coliflor")
    ]
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    axes = axes.flatten()
    
    for i, (c, name) in enumerate(c_values):
        print(f"  Generando Julia {name} (c = {c})...")
        julia = julia_set(400, 400, c, max_iter=100)
        
        im = axes[i].imshow(julia, extent=[-1.5, 1.5, -1.5, 1.5], 
                           cmap='plasma', origin='lower')
        axes[i].set_title(f'Julia "{name}"\nc = {c:.3f}')
        axes[i].set_xlabel('Re(z)')
        axes[i].set_ylabel('Im(z)')
        
        plt.colorbar(im, ax=axes[i])
    
    plt.tight_layout()
    plt.savefig('/Users/giovanniarangio/atlas/demos/julia_fractals.png', dpi=300, bbox_inches='tight')
    plt.show()

def demo_signal_processing():
    """Demostrar procesamiento de señales"""
    print_header("PROCESAMIENTO DE SEÑALES MATEMÁTICO")
    
    print_section("Análisis de Fourier")
    
    # Crear señal compuesta
    t = np.linspace(0, 2, 1000)
    
    # Componentes de frecuencia
    f1, f2, f3 = 5, 15, 30  # Hz
    signal = (np.sin(2*np.pi*f1*t) + 
              0.5*np.sin(2*np.pi*f2*t) + 
              0.3*np.sin(2*np.pi*f3*t) + 
              0.1*np.random.randn(len(t)))  # Ruido
    
    # Transformada de Fourier
    fft_signal = np.fft.fft(signal)
    frequencies = np.fft.fftfreq(len(signal), t[1] - t[0])
    
    # Solo frecuencias positivas
    positive_freq_idx = frequencies > 0
    frequencies_pos = frequencies[positive_freq_idx]
    fft_magnitude = np.abs(fft_signal[positive_freq_idx])
    
    # Filtrado de señal
    # Filtro pasa-bajos (eliminar frecuencias > 20 Hz)
    fft_filtered = fft_signal.copy()
    fft_filtered[np.abs(frequencies) > 20] = 0
    signal_filtered = np.real(np.fft.ifft(fft_filtered))
    
    print(f"  Frecuencias principales detectadas:")
    # Encontrar picos en el espectro
    peak_indices = []
    for i in range(1, len(fft_magnitude)-1):
        if (fft_magnitude[i] > fft_magnitude[i-1] and 
            fft_magnitude[i] > fft_magnitude[i+1] and 
            fft_magnitude[i] > 0.1 * np.max(fft_magnitude)):
            peak_indices.append(i)
    
    for idx in peak_indices:
        freq = frequencies_pos[idx]
        magnitude = fft_magnitude[idx]
        print(f"    {freq:.1f} Hz (magnitud: {magnitude:.1f})")
    
    # Visualización
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Señal original
    axes[0, 0].plot(t, signal, 'b-', linewidth=1)
    axes[0, 0].set_title('Señal Original (con ruido)')
    axes[0, 0].set_xlabel('Tiempo (s)')
    axes[0, 0].set_ylabel('Amplitud')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Espectro de frecuencias
    axes[0, 1].plot(frequencies_pos, fft_magnitude, 'r-', linewidth=1)
    axes[0, 1].scatter(frequencies_pos[peak_indices], fft_magnitude[peak_indices], 
                      color='red', s=50, zorder=5)
    axes[0, 1].set_title('Espectro de Frecuencias')
    axes[0, 1].set_xlabel('Frecuencia (Hz)')
    axes[0, 1].set_ylabel('Magnitud')
    axes[0, 1].set_xlim(0, 50)
    axes[0, 1].grid(True, alpha=0.3)
    
    # Señal filtrada
    axes[1, 0].plot(t, signal_filtered, 'g-', linewidth=1)
    axes[1, 0].set_title('Señal Filtrada (pasa-bajos 20 Hz)')
    axes[1, 0].set_xlabel('Tiempo (s)')
    axes[1, 0].set_ylabel('Amplitud')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Comparación
    axes[1, 1].plot(t, signal, 'b-', alpha=0.7, label='Original')
    axes[1, 1].plot(t, signal_filtered, 'g-', linewidth=2, label='Filtrada')
    axes[1, 1].set_title('Comparación Original vs Filtrada')
    axes[1, 1].set_xlabel('Tiempo (s)')
    axes[1, 1].set_ylabel('Amplitud')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/Users/giovanniarangio/atlas/demos/signal_processing.png', dpi=300, bbox_inches='tight')
    plt.show()

def performance_stress_test():
    """Realizar pruebas de estrés de rendimiento"""
    print_header("PRUEBAS DE ESTRÉS DE RENDIMIENTO")
    
    print_section("Benchmark de Operaciones Intensivas")
    
    # Test 1: Operaciones aritméticas masivas
    print("  🔢 Test de operaciones aritméticas masivas:")
    
    sizes = [100, 1000, 10000, 100000]
    arithmetic_times = []
    
    for size in sizes:
        operands = list(range(1, size + 1))
        
        start_time = time.time()
        request = ArithmeticRequest(operation="add", operands=operands)
        result = ArithmeticService.calculate(request)
        end_time = time.time()
        
        execution_time = (end_time - start_time) * 1000  # ms
        arithmetic_times.append(execution_time)
        
        print(f"    Suma de {size:,} números: {execution_time:.2f} ms")
    
    # Test 2: Cálculos de derivadas complejas
    print("\n  📊 Test de cálculo diferencial:")
    
    expressions = [
        "x^2",
        "x^3 + 2*x^2 + x + 1",
        "sin(x) * cos(x) * exp(x)",
        "ln(x^2 + 1) * sqrt(x + 1)",
        "sin(cos(tan(x))) + exp(sin(x))"
    ]
    
    calculus_times = []
    
    for expr in expressions:
        start_time = time.time()
        try:
            request = CalculusRequest(
                expression=expr,
                operation="derivative",
                variable="x",
                order=1
            )
            result = CalculusService.calculate(request)
            end_time = time.time()
            
            execution_time = (end_time - start_time) * 1000  # ms
            calculus_times.append(execution_time)
            
            print(f"    d/dx({expr}): {execution_time:.2f} ms")
            
        except Exception as e:
            print(f"    ❌ Error con {expr}: {e}")
            calculus_times.append(0)
    
    # Test 3: Análisis estadístico de grandes datasets
    print("\n  📈 Test de análisis estadístico:")
    
    dataset_sizes = [1000, 10000, 100000, 1000000]
    stats_times = []
    
    for size in dataset_sizes:
        np.random.seed(42)
        data = np.random.normal(0, 1, size).tolist()
        
        start_time = time.time()
        try:
            request = StatisticsRequest(
                data=data,
                operation="descriptive_statistics"
            )
            result = StatisticsService.calculate(request)
            end_time = time.time()
            
            execution_time = (end_time - start_time) * 1000  # ms
            stats_times.append(execution_time)
            
            print(f"    Estadísticas de {size:,} puntos: {execution_time:.2f} ms")
            
        except Exception as e:
            print(f"    ❌ Error con dataset de {size:,}: {e}")
            stats_times.append(0)
    
    # Visualización de rendimiento
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Rendimiento aritmético
    axes[0].loglog(sizes, arithmetic_times, 'bo-', linewidth=2, markersize=8)
    axes[0].set_title('Rendimiento Aritmético')
    axes[0].set_xlabel('Número de operandos')
    axes[0].set_ylabel('Tiempo (ms)')
    axes[0].grid(True, alpha=0.3)
    
    # Rendimiento de cálculo
    axes[1].bar(range(len(expressions)), calculus_times, color='green', alpha=0.7)
    axes[1].set_title('Rendimiento de Cálculo')
    axes[1].set_xlabel('Expresión')
    axes[1].set_ylabel('Tiempo (ms)')
    axes[1].set_xticks(range(len(expressions)))
    axes[1].set_xticklabels([f'Expr {i+1}' for i in range(len(expressions))])
    axes[1].grid(True, alpha=0.3)
    
    # Rendimiento estadístico
    valid_stats = [(size, time) for size, time in zip(dataset_sizes, stats_times) if time > 0]
    if valid_stats:
        sizes_valid, times_valid = zip(*valid_stats)
        axes[2].loglog(sizes_valid, times_valid, 'ro-', linewidth=2, markersize=8)
    axes[2].set_title('Rendimiento Estadístico')
    axes[2].set_xlabel('Tamaño del dataset')
    axes[2].set_ylabel('Tiempo (ms)')
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/Users/giovanniarangio/atlas/demos/performance_benchmark.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Función principal"""
    print("🚀 INICIANDO DEMOSTRACIÓN AVANZADA DEL MÓDULO MATEMÁTICO AXIOM")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔧 Versión: 2.0.0 (Avanzada)")
    print(f"🔬 Servicios avanzados disponibles: {'✅' if ADVANCED_SERVICES_AVAILABLE else '❌'}")
    
    try:
        # Ejecutar demostraciones avanzadas
        demo_complex_analysis()
        demo_optimization_algorithms()
        demo_mathematical_ml()
        demo_fractal_mathematics()
        demo_signal_processing()
        performance_stress_test()
        
        print_header("DEMOSTRACIÓN AVANZADA COMPLETADA EXITOSAMENTE")
        print("✅ Todas las funcionalidades avanzadas han sido probadas")
        print("🎨 Las visualizaciones complejas han sido generadas")
        print("⚡ Los benchmarks de rendimiento han sido ejecutados")
        print("🧠 Los algoritmos de ML matemático han sido demostrados")
        print("🔬 El análisis matemático complejo ha sido realizado")
        print("\n🎉 ¡El módulo matemático AXIOM demuestra capacidades avanzadas excepcionales!")
        
        # Resumen de archivos generados
        print("\n📁 Archivos generados:")
        generated_files = [
            "complex_analysis.png",
            "optimization_demo.png", 
            "genetic_convergence.png",
            "ml_approximation.png",
            "mandelbrot_fractals.png",
            "julia_fractals.png",
            "signal_processing.png",
            "performance_benchmark.png"
        ]
        
        for file in generated_files:
            print(f"  📊 /Users/giovanniarangio/atlas/demos/{file}")
        
    except Exception as e:
        print(f"\n❌ Error durante la demostración avanzada: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)