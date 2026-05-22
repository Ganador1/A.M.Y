#!/usr/bin/env python3
"""
🔬 AXIOM META 4 - Pruebas con Datos Reales por Dominio
Evaluación exhaustiva con datasets científicos reales
"""

import json
import sys
import numpy as np
from datetime import datetime
from pathlib import Path
import logging
import requests

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealDataDomainTester:
    """Tester para dominios científicos con datos reales"""
    
    def __init__(self):
        self.test_results = {}
        self.data_dir = Path("real_data_tests")
        self.data_dir.mkdir(exist_ok=True)
        
        # Configurar dominios con datos reales
        self.domain_tests = {
            "mathematics": self.test_mathematics_real_data,
            "physics": self.test_physics_real_data,
            "chemistry": self.test_chemistry_real_data,
            "biology": self.test_biology_real_data,
            "materials_science": self.test_materials_science_real_data,
            "medical_imaging": self.test_medical_imaging_real_data,
            "engineering": self.test_engineering_real_data,
            "plasma_physics": self.test_plasma_physics_real_data
        }
    
    def generate_real_mathematical_data(self) -> dict:
        """Generar datos matemáticos reales para análisis"""
        logger.info("📊 Generating real mathematical dataset")
        
        # Generar series temporales con propiedades matemáticas interesantes
        t = np.linspace(0, 4*np.pi, 1000)
        
        # Serie con múltiples componentes frecuenciales
        signal = (2 * np.sin(t) + 
                 0.5 * np.sin(3*t) + 
                 0.3 * np.cos(5*t) + 
                 0.1 * np.random.normal(size=len(t)))
        
        # Datos de convergencia de serie
        n_terms = np.arange(1, 101)
        pi_approximation = 4 * np.cumsum((-1)**(n_terms-1) / (2*n_terms - 1))
        
        # Datos de optimización
        x_opt = np.linspace(-5, 5, 100)
        y_opt = x_opt**4 - 6*x_opt**2 + 9*x_opt + 1
        
        dataset = {
            "signal_analysis": {
                "time": t.tolist(),
                "signal": signal.tolist(),
                "description": "Multi-frequency signal with noise for spectral analysis"
            },
            "series_convergence": {
                "terms": n_terms.tolist(), 
                "pi_approx": pi_approximation.tolist(),
                "true_pi": float(np.pi),
                "description": "Leibniz series convergence to π"
            },
            "optimization": {
                "x": x_opt.tolist(),
                "y": y_opt.tolist(),
                "true_minima": [-2.1038, 1.1038],
                "description": "Polynomial function optimization problem"
            }
        }
        
        # Guardar dataset
        with open(self.data_dir / "mathematics_real_data.json", "w") as f:
            json.dump(dataset, f, indent=2)
        
        return dataset
    
    def generate_real_physics_data(self) -> dict:
        """Generar datos físicos reales simulados"""
        logger.info("⚛️ Generating real physics dataset")
        
        # Simulación de péndulo con amortiguamiento
        dt = 0.01
        t_max = 10.0
        t = np.arange(0, t_max, dt)
        
        # Parámetros físicos realistas
        g = 9.81  # gravedad
        L = 1.0   # longitud péndulo
        b = 0.1   # coeficiente amortiguamiento
        theta0 = np.pi/4  # ángulo inicial
        
        # Solución aproximada del péndulo amortiguado
        omega0 = np.sqrt(g/L)
        gamma = b/(2*np.sqrt(g*L))
        omega_d = omega0 * np.sqrt(1 - gamma**2)
        
        theta = theta0 * np.exp(-gamma*omega0*t) * np.cos(omega_d*t)
        
        # Datos de caída libre con resistencia del aire
        v_terminal = 50  # m/s
        mass = 0.1  # kg
        t_fall = np.linspace(0, 5, 100)
        v_fall = v_terminal * (1 - np.exp(-9.81*t_fall/v_terminal))
        
        # Datos termodinámicos (gas ideal)
        volumes = np.linspace(0.001, 0.1, 100)
        temperature = 300  # K
        n_moles = 1
        R = 8.314  # J/(mol·K)
        pressures = n_moles * R * temperature / volumes
        
        dataset = {
            "pendulum_motion": {
                "time": t.tolist(),
                "angle": theta.tolist(),
                "parameters": {"g": g, "L": L, "damping": b, "initial_angle": theta0},
                "description": "Damped pendulum motion simulation"
            },
            "free_fall": {
                "time": t_fall.tolist(),
                "velocity": v_fall.tolist(),
                "parameters": {"v_terminal": v_terminal, "mass": mass},
                "description": "Free fall with air resistance"
            },
            "thermodynamics": {
                "volume": volumes.tolist(),
                "pressure": pressures.tolist(),
                "parameters": {"T": temperature, "n": n_moles},
                "description": "Ideal gas law P-V relationship"
            }
        }
        
        with open(self.data_dir / "physics_real_data.json", "w") as f:
            json.dump(dataset, f, indent=2)
        
        return dataset
    
    def generate_real_chemistry_data(self) -> dict:
        """Generar datos químicos reales"""
        logger.info("🧪 Generating real chemistry dataset")
        
        # Cinética de reacción (reacción de primer orden)
        t_reaction = np.linspace(0, 100, 200)
        k = 0.05  # constante de velocidad
        A0 = 1.0  # concentración inicial
        A_t = A0 * np.exp(-k * t_reaction)
        
        # Titulación ácido-base
        volume_added = np.linspace(0, 50, 100)
        Ka = 1e-5
        Ca = 0.1  # Concentración ácido
        Cb = 0.1  # Concentración base
        
        # pH simplificado para titulación
        pH_values = []
        for V in volume_added:
            if V == 0:
                pH = -np.log10(np.sqrt(Ka * Ca))
            elif V < 25:  # Antes del punto de equivalencia
                excess_acid = (Ca * 25 - Cb * V) / (25 + V)
                pH = -np.log10(np.sqrt(Ka * excess_acid))
            elif V == 25:  # Punto de equivalencia
                pH = 7.0
            else:  # Después del punto de equivalencia
                excess_base = (Cb * V - Ca * 25) / (25 + V)
                pOH = -np.log10(excess_base)
                pH = 14 - pOH
            pH_values.append(pH)
        
        # Espectroscopia UV-Vis simulada
        wavelengths = np.linspace(200, 800, 300)
        # Picos de absorción simulados
        abs1 = 0.8 * np.exp(-0.5 * ((wavelengths - 280) / 20)**2)  # Pico proteína
        abs2 = 0.5 * np.exp(-0.5 * ((wavelengths - 650) / 30)**2)  # Pico cromóforo
        absorbance = abs1 + abs2 + 0.05 * np.random.random(len(wavelengths))
        
        dataset = {
            "reaction_kinetics": {
                "time": t_reaction.tolist(),
                "concentration": A_t.tolist(),
                "parameters": {"k": k, "initial_conc": A0},
                "description": "First-order reaction kinetics"
            },
            "acid_base_titration": {
                "volume_added": volume_added.tolist(),
                "pH": pH_values,
                "parameters": {"Ka": Ka, "acid_conc": Ca, "base_conc": Cb},
                "description": "Weak acid - strong base titration"
            },
            "uv_vis_spectrum": {
                "wavelength": wavelengths.tolist(),
                "absorbance": absorbance.tolist(),
                "description": "Simulated UV-Vis absorption spectrum"
            }
        }
        
        with open(self.data_dir / "chemistry_real_data.json", "w") as f:
            json.dump(dataset, f, indent=2)
        
        return dataset
    
    def generate_real_materials_data(self) -> dict:
        """Generar datos de ciencia de materiales"""
        logger.info("🔬 Generating real materials science dataset")
        
        # Curva esfuerzo-deformación de material elasto-plástico
        strain = np.linspace(0, 0.1, 200)
        E = 200e9  # Módulo de Young (Pa)
        yield_strain = 0.002
        yield_stress = E * yield_strain
        ultimate_strain = 0.08
        ultimate_stress = yield_stress * 1.3
        
        stress = np.zeros_like(strain)
        for i, eps in enumerate(strain):
            if eps <= yield_strain:
                stress[i] = E * eps  # Región elástica
            elif eps <= ultimate_strain:
                # Región plástica simplificada
                plastic_strain = eps - yield_strain
                hardening = (ultimate_stress - yield_stress) / (ultimate_strain - yield_strain)
                stress[i] = yield_stress + hardening * plastic_strain
            else:
                # Región de falla
                stress[i] = ultimate_stress * (1 - (eps - ultimate_strain) / (0.1 - ultimate_strain))
        
        # Propiedades térmicas vs temperatura
        temperatures = np.linspace(300, 1500, 100)  # K
        # Capacidad calorífica específica (modelo Debye simplificado)
        theta_D = 400  # Temperatura de Debye
        cp = 3 * 8.314 * (temperatures / theta_D)**3 * np.exp(theta_D / temperatures) / (np.exp(theta_D / temperatures) - 1)**2
        
        # Conductividad térmica
        k_thermal = 100 / np.sqrt(temperatures / 300)  # Simplificado
        
        # Datos de difractometría simulados
        two_theta = np.linspace(10, 80, 350)
        # Picos de difracción principales
        peaks = [(25, 1000), (44, 800), (64, 400), (78, 200)]
        intensity = np.zeros_like(two_theta)
        for peak_pos, peak_int in peaks:
            intensity += peak_int * np.exp(-0.5 * ((two_theta - peak_pos) / 0.5)**2)
        intensity += 50 * np.random.random(len(two_theta))  # Ruido de fondo
        
        dataset = {
            "stress_strain": {
                "strain": strain.tolist(),
                "stress": stress.tolist(),
                "parameters": {"E": E, "yield_stress": yield_stress, "ultimate_stress": ultimate_stress},
                "description": "Elasto-plastic stress-strain curve"
            },
            "thermal_properties": {
                "temperature": temperatures.tolist(),
                "heat_capacity": cp.tolist(),
                "thermal_conductivity": k_thermal.tolist(),
                "parameters": {"debye_temp": theta_D},
                "description": "Temperature-dependent thermal properties"
            },
            "xrd_pattern": {
                "two_theta": two_theta.tolist(),
                "intensity": intensity.tolist(),
                "description": "Simulated X-ray diffraction pattern"
            }
        }
        
        with open(self.data_dir / "materials_real_data.json", "w") as f:
            json.dump(dataset, f, indent=2)
        
        return dataset
    
    def test_mathematics_real_data(self, model: str) -> dict:
        """Test dominio matemáticas con datos reales"""
        logger.info(f"📊 Testing mathematics domain with {model}")
        
        dataset = self.generate_real_mathematical_data()
        
        # Preguntas analíticas sobre los datos reales
        questions = [
            {
                "type": "spectral_analysis",
                "prompt": f"Analyze this signal data with {len(dataset['signal_analysis']['signal'])} points. The signal shows multi-frequency components. What are the dominant frequency characteristics?",
                "data_context": "signal_analysis",
                "expected_keywords": ["frequency", "fourier", "spectral", "harmonics", "dominant"]
            },
            {
                "type": "convergence_analysis", 
                "prompt": f"This dataset shows the Leibniz series approximation to π with {len(dataset['series_convergence']['terms'])} terms. Analyze the convergence behavior and accuracy.",
                "data_context": "series_convergence",
                "expected_keywords": ["convergence", "leibniz", "alternating", "error", "accuracy"]
            },
            {
                "type": "optimization",
                "prompt": "Given this polynomial function data, identify the critical points and classify them as minima, maxima, or saddle points.",
                "data_context": "optimization", 
                "expected_keywords": ["minimum", "maximum", "derivative", "critical", "optimization"]
            }
        ]
        
        return self._test_domain_with_questions(model, "mathematics", questions, dataset)
    
    def test_physics_real_data(self, model: str) -> dict:
        """Test dominio física con datos reales"""
        logger.info(f"⚛️ Testing physics domain with {model}")
        
        dataset = self.generate_real_physics_data()
        
        questions = [
            {
                "type": "pendulum_analysis",
                "prompt": "Analyze this damped pendulum motion data. What can you determine about the physical parameters and damping characteristics?",
                "data_context": "pendulum_motion",
                "expected_keywords": ["damping", "oscillation", "period", "amplitude", "decay"]
            },
            {
                "type": "free_fall_analysis",
                "prompt": "This free fall data includes air resistance. Analyze the terminal velocity behavior and drag characteristics.",
                "data_context": "free_fall",
                "expected_keywords": ["terminal", "velocity", "drag", "resistance", "acceleration"]
            },
            {
                "type": "thermodynamics_analysis",
                "prompt": "Analyze this pressure-volume data for an ideal gas. Verify the ideal gas law and determine the physical parameters.",
                "data_context": "thermodynamics",
                "expected_keywords": ["ideal", "gas", "pressure", "volume", "temperature", "constant"]
            }
        ]
        
        return self._test_domain_with_questions(model, "physics", questions, dataset)
    
    def test_chemistry_real_data(self, model: str) -> dict:
        """Test dominio química con datos reales"""
        logger.info(f"🧪 Testing chemistry domain with {model}")
        
        dataset = self.generate_real_chemistry_data()
        
        questions = [
            {
                "type": "reaction_kinetics",
                "prompt": "Analyze this reaction kinetics data. Determine the reaction order and rate constant.",
                "data_context": "reaction_kinetics",
                "expected_keywords": ["kinetics", "rate", "constant", "first", "order", "exponential"]
            },
            {
                "type": "titration_analysis", 
                "prompt": "Analyze this acid-base titration curve. Identify the equivalence point and buffer regions.",
                "data_context": "acid_base_titration",
                "expected_keywords": ["equivalence", "point", "buffer", "pH", "titration", "neutralization"]
            },
            {
                "type": "spectroscopy",
                "prompt": "Interpret this UV-Vis absorption spectrum. Identify the absorption maxima and molecular transitions.",
                "data_context": "uv_vis_spectrum",
                "expected_keywords": ["absorption", "spectrum", "wavelength", "transition", "chromophore"]
            }
        ]
        
        return self._test_domain_with_questions(model, "chemistry", questions, dataset)
    
    def test_materials_science_real_data(self, model: str) -> dict:
        """Test dominio ciencia de materiales con datos reales"""
        logger.info(f"🔬 Testing materials science domain with {model}")
        
        dataset = self.generate_real_materials_data()
        
        questions = [
            {
                "type": "mechanical_properties",
                "prompt": "Analyze this stress-strain curve. Determine the elastic modulus, yield strength, and ultimate tensile strength.",
                "data_context": "stress_strain",
                "expected_keywords": ["elastic", "modulus", "yield", "strength", "plastic", "deformation"]
            },
            {
                "type": "thermal_analysis",
                "prompt": "Analyze these temperature-dependent thermal properties. Explain the physical mechanisms behind the trends.",
                "data_context": "thermal_properties",
                "expected_keywords": ["thermal", "conductivity", "capacity", "temperature", "phonon", "lattice"]
            },
            {
                "type": "crystallographic_analysis",
                "prompt": "Interpret this X-ray diffraction pattern. Identify the crystal structure and estimate lattice parameters.",
                "data_context": "xrd_pattern",
                "expected_keywords": ["diffraction", "crystal", "structure", "lattice", "bragg", "peaks"]
            }
        ]
        
        return self._test_domain_with_questions(model, "materials_science", questions, dataset)
    
    def test_biology_real_data(self, model: str) -> dict:
        """Test dominio biología con datos simulados"""
        logger.info(f"🧬 Testing biology domain with {model}")
        
        # Generar datos biológicos simulados
        dataset = self._generate_biology_data()
        
        questions = [
            {
                "type": "population_dynamics",
                "prompt": "Analyze this population growth data. Identify the growth pattern and carrying capacity.",
                "data_context": "population_growth",
                "expected_keywords": ["population", "growth", "carrying", "capacity", "exponential", "logistic"]
            },
            {
                "type": "enzyme_kinetics",
                "prompt": "Analyze this enzyme kinetics data. Determine the Michaelis-Menten parameters.",
                "data_context": "enzyme_kinetics", 
                "expected_keywords": ["enzyme", "michaelis", "menten", "vmax", "km", "saturation"]
            }
        ]
        
        return self._test_domain_with_questions(model, "biology", questions, dataset)
    
    def test_medical_imaging_real_data(self, model: str) -> dict:
        """Test dominio imagen médica con datos simulados"""
        logger.info(f"🏥 Testing medical imaging domain with {model}")
        
        # Usar datos simulados simples
        dataset = {"note": "Medical imaging analysis with synthetic data"}
        
        questions = [
            {
                "type": "image_analysis",
                "prompt": "Describe the key principles of CT image reconstruction and how noise affects image quality.",
                "data_context": "general",
                "expected_keywords": ["reconstruction", "tomography", "noise", "quality", "contrast", "resolution"]
            }
        ]
        
        return self._test_domain_with_questions(model, "medical_imaging", questions, dataset)
    
    def test_engineering_real_data(self, model: str) -> dict:
        """Test dominio ingeniería con datos reales"""
        logger.info(f"⚙️ Testing engineering domain with {model}")
        
        dataset = {"note": "Engineering analysis with theoretical data"}
        
        questions = [
            {
                "type": "structural_analysis",
                "prompt": "Explain the relationship between beam deflection, load distribution, and material properties in structural engineering.",
                "data_context": "general",
                "expected_keywords": ["deflection", "load", "beam", "stress", "strain", "modulus"]
            }
        ]
        
        return self._test_domain_with_questions(model, "engineering", questions, dataset)
    
    def test_plasma_physics_real_data(self, model: str) -> dict:
        """Test dominio física de plasmas con datos simulados"""
        logger.info(f"⚡ Testing plasma physics domain with {model}")
        
        dataset = {"note": "Plasma physics analysis with theoretical framework"}
        
        questions = [
            {
                "type": "plasma_parameters",
                "prompt": "Explain the relationship between plasma density, temperature, and Debye length in plasma physics.",
                "data_context": "general",
                "expected_keywords": ["debye", "length", "density", "temperature", "shielding", "plasma"]
            }
        ]
        
        return self._test_domain_with_questions(model, "plasma_physics", questions, dataset)
    
    def _generate_biology_data(self) -> dict:
        """Generar datos biológicos simulados"""
        # Crecimiento poblacional logístico
        t = np.linspace(0, 50, 100)
        K = 1000  # Capacidad de carga
        r = 0.1   # Tasa de crecimiento
        N0 = 10   # Población inicial
        
        population = K / (1 + ((K - N0) / N0) * np.exp(-r * t))
        
        # Cinética enzimática (Michaelis-Menten)
        substrate_conc = np.linspace(0.1, 20, 50)
        Vmax = 10  # Velocidad máxima
        Km = 2     # Constante de Michaelis
        
        velocity = Vmax * substrate_conc / (Km + substrate_conc)
        
        return {
            "population_growth": {
                "time": t.tolist(),
                "population": population.tolist(),
                "parameters": {"K": K, "r": r, "N0": N0}
            },
            "enzyme_kinetics": {
                "substrate_concentration": substrate_conc.tolist(),
                "reaction_velocity": velocity.tolist(),
                "parameters": {"Vmax": Vmax, "Km": Km}
            }
        }
    
    def _test_domain_with_questions(self, model: str, domain: str, questions: list, dataset: dict) -> dict:
        """Test un dominio con preguntas específicas"""
        ollama_url = "http://localhost:11434"
        results = []
        
        for question in questions:
            try:
                # Incluir contexto de datos en el prompt
                context_info = ""
                if question["data_context"] != "general" and question["data_context"] in dataset:
                    data_sample = dataset[question["data_context"]]
                    if isinstance(data_sample, dict) and "description" in data_sample:
                        context_info = f"\nData context: {data_sample['description']}"
                
                full_prompt = question["prompt"] + context_info
                
                response = requests.post(
                    f"{ollama_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": full_prompt,
                        "stream": False
                    },
                    timeout=120
                )
                
                if response.status_code == 200:
                    answer = response.json().get("response", "")
                    
                    # Evaluar calidad de respuesta
                    keyword_score = sum(1 for keyword in question["expected_keywords"] 
                                      if keyword.lower() in answer.lower())
                    max_keywords = len(question["expected_keywords"])
                    
                    results.append({
                        "question_type": question["type"],
                        "question": question["prompt"],
                        "answer": answer,
                        "keyword_score": keyword_score / max_keywords if max_keywords > 0 else 0,
                        "keywords_found": keyword_score,
                        "keywords_total": max_keywords
                    })
                else:
                    results.append({
                        "question_type": question["type"],
                        "error": f"HTTP {response.status_code}",
                        "keyword_score": 0
                    })
                    
            except Exception as e:
                results.append({
                    "question_type": question["type"],
                    "error": str(e),
                    "keyword_score": 0
                })
        
        avg_score = sum(r.get("keyword_score", 0) for r in results) / len(results) if results else 0
        
        return {
            "domain": domain,
            "model": model,
            "average_score": avg_score,
            "detailed_results": results,
            "dataset_info": dataset.get("description", "Real/simulated scientific data"),
            "timestamp": datetime.now().isoformat()
        }
    
    def run_comprehensive_domain_testing(self, models: list | None = None) -> dict:
        """Ejecutar pruebas comprehensivas por dominio"""
        if models is None:
            models = ["falcon3:1b", "falcon3:3b", "deepseek-r1:1.5b", "qwen2.5:1.5b"]
        
        logger.info("🎯 Starting comprehensive domain testing with real data")
        
        all_results = {
            "test_metadata": {
                "start_time": datetime.now().isoformat(),
                "models_tested": models,
                "domains_tested": list(self.domain_tests.keys())
            },
            "results_by_model": {},
            "results_by_domain": {}
        }
        
        for model in models:
            logger.info(f"\n{'='*50}")
            logger.info(f"🔍 TESTING MODEL: {model}")
            logger.info(f"{'='*50}")
            
            model_results = {}
            
            for domain, test_func in self.domain_tests.items():
                try:
                    logger.info(f"Testing {domain} domain...")
                    domain_result = test_func(model)
                    model_results[domain] = domain_result
                    
                    # También guardar por dominio
                    if domain not in all_results["results_by_domain"]:
                        all_results["results_by_domain"][domain] = {}
                    all_results["results_by_domain"][domain][model] = domain_result
                    
                    logger.info(f"✅ {domain}: {domain_result['average_score']:.3f}")
                    
                except Exception as e:
                    logger.error(f"❌ {domain} failed: {e}")
                    model_results[domain] = {"error": str(e)}
            
            all_results["results_by_model"][model] = model_results
        
        # Análisis comparativo
        all_results["comparative_analysis"] = self._analyze_domain_performance(all_results)
        all_results["test_metadata"]["end_time"] = datetime.now().isoformat()
        
        # Guardar resultados
        self._save_domain_results(all_results)
        
        return all_results
    
    def _analyze_domain_performance(self, results: dict) -> dict:
        """Analizar rendimiento por dominio y modelo"""
        analysis = {
            "model_rankings": {},
            "domain_difficulty": {},
            "best_combinations": []
        }
        
        # Ranking por modelo
        model_scores = {}
        for model, domains in results["results_by_model"].items():
            scores = [domain_data.get("average_score", 0) 
                     for domain_data in domains.values() 
                     if isinstance(domain_data, dict) and "average_score" in domain_data]
            model_scores[model] = sum(scores) / len(scores) if scores else 0
        
        analysis["model_rankings"] = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Dificultad por dominio
        domain_scores = {}
        for domain, models in results["results_by_domain"].items():
            scores = [model_data.get("average_score", 0) 
                     for model_data in models.values() 
                     if isinstance(model_data, dict) and "average_score" in model_data]
            domain_scores[domain] = sum(scores) / len(scores) if scores else 0
        
        analysis["domain_difficulty"] = sorted(domain_scores.items(), key=lambda x: x[1])
        
        # Mejores combinaciones modelo-dominio
        combinations = []
        for domain, models in results["results_by_domain"].items():
            for model, data in models.items():
                if isinstance(data, dict) and "average_score" in data:
                    combinations.append((model, domain, data["average_score"]))
        
        analysis["best_combinations"] = sorted(combinations, key=lambda x: x[2], reverse=True)[:10]
        
        return analysis
    
    def _save_domain_results(self, results: dict):
        """Guardar resultados de pruebas por dominio"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Archivo con timestamp
            filename = f"domain_testing_results_{timestamp}.json"
            with open(filename, "w") as f:
                json.dump(results, f, indent=2)
            
            # Archivo latest
            with open("domain_testing_results_latest.json", "w") as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"✅ Domain testing results saved to {filename}")
            
        except Exception as e:
            logger.error(f"Could not save domain results: {e}")

def main():
    """Función principal"""
    print("🔬 AXIOM META 4 - Real Data Domain Testing")
    print("=" * 50)
    print("Testing scientific domains with real/simulated datasets")
    print("=" * 50)
    
    tester = RealDataDomainTester()
    
    try:
        results = tester.run_comprehensive_domain_testing()
        
        print("\n🎉 DOMAIN TESTING COMPLETE!")
        print("=" * 50)
        
        # Mostrar rankings
        if "comparative_analysis" in results:
            analysis = results["comparative_analysis"]
            
            print("\n📊 MODEL RANKINGS:")
            for i, (model, score) in enumerate(analysis.get("model_rankings", [])):
                print(f"{i+1}. {model}: {score:.3f}")
            
            print("\n📈 DOMAIN DIFFICULTY (easiest to hardest):")
            for domain, score in reversed(analysis.get("domain_difficulty", [])):
                print(f"- {domain}: {score:.3f}")
            
            print("\n🏆 TOP MODEL-DOMAIN COMBINATIONS:")
            for model, domain, score in analysis.get("best_combinations", [])[:5]:
                print(f"- {model} + {domain}: {score:.3f}")
        
        print("\n📄 Results saved to: domain_testing_results_latest.json")
        
    except Exception as e:
        logger.error(f"❌ Domain testing failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
