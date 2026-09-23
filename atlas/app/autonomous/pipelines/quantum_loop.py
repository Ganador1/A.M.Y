"""Quantum exploration loop with integration of QuantumComputingService."""
from __future__ import annotations

import asyncio
import time
from typing import Any, Callable, Dict, List, Optional

from app.autonomous.core.budget_allocator import BudgetAllocator
from app.autonomous.core.priority_scoring import PriorityScorer
from app.autonomous.core.state_manager import IterationRecord, StateManager
from app.autonomous.core.task_scheduler import TaskScheduler
from app.autonomous.evaluation.empirical_feedback import process_feedback
from app.autonomous.evaluation.novelty_assessor import NoveltyAssessor
from app.autonomous.generators.experimental_design_generator import generate_experimental_design
from app.autonomous.interfaces.external_apis import fetch_quantum_circuit_templates
from app.autonomous.metrics.telemetry_collector import telemetry
from app.autonomous.integration import EvidenceSummary, ToolEvidenceBridge
from app.autonomous.models.difficulty_estimator import DifficultyEstimator
from app.core.bootstrap_logging import logger
from app.domains.physics.services.quantum_computing import QuantumComputingService
# ⭐ SERVICIOS CUÁNTICOS AVANZADOS (7 servicios funcionales)
from app.domains.physics.services.quantum_algorithms_service import QuantumAlgorithmsService
from app.domains.physics.services.quantum_chemistry_service import QuantumChemistryService
from app.domains.physics.services.async_quantum_computing_service import AsyncQuantumComputingService
from app.domains.physics.services.particle_physics_service import ParticlePhysicsService
from app.domains.physics.services.solid_state_physics import SolidStatePhysicsService
# from app.domains.physics.computational.physics_informed_nn_service import PhysicsInformedNNService  # ❌ DISABLED: Requires PyTorch
from app.compliance.ethics_gate import EthicsGate, ExperimentRequest
from app.exceptions.domain.physics import QuantumError
# ⭐ NUEVO: LLM para generación de candidatos
import json
import re

QuantumCandidateProvider = Callable[[], List[Dict[str, Any]]]


class QuantumLoop:
    def __init__(
        self,
        provider: QuantumCandidateProvider | None = None,
        state: StateManager | None = None,
    ):
        self.provider = provider
        self.state = state or StateManager()
        
        # ⭐ SCORING with diversity bonus (0.30 weight - doubled for stronger differentiation)
        self.scorer = PriorityScorer()
        self.scorer.weights.diversity_bonus = 0.30  # Enable diversity bonus (increased from 0.15)
        
        # ⭐ SCHEDULING with stochastic top-k selection
        self.scheduler = TaskScheduler(
            diversity_quota=5,
            stochastic_topk=True,      # Enable probabilistic selection
            topk_size=10,               # Sample from top-10 candidates
            selection_temperature=0.5  # Moderate randomness (0.1=deterministic, 1.0=random)
        )
        
        self.budget = BudgetAllocator(total_budget=8.0)
        self.difficulty = DifficultyEstimator()
        self.novelty = NoveltyAssessor()
        self.quantum_service = QuantumComputingService()
        # ⭐ SERVICIOS CUÁNTICOS AVANZADOS (6 servicios activos, PINN disabled)
        self.quantum_algorithms_service = QuantumAlgorithmsService()  # Advanced quantum algorithms
        self.quantum_chemistry_service = QuantumChemistryService()  # Quantum chemistry calculations
        # self.physics_informed_nn_service = PhysicsInformedNNService()  # ❌ DISABLED: Requires PyTorch
        self.async_quantum_service = AsyncQuantumComputingService()  # Async quantum computing
        self.particle_physics = ParticlePhysicsService()  # Particle physics simulations
        self.solid_state_physics = SolidStatePhysicsService()  # Solid state physics
        self._cached_design: Dict[str, Any] | None = None
        self.tool_evidence = ToolEvidenceBridge(default_domain="quantum")
        self.ethics_gate = EthicsGate()
        self._seen_names: List[str] = []  # Track all generated candidate names for diversity

    @staticmethod
    def _run_coro_sync(coro):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(coro)
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    async def _generate_candidates_with_huggingface(
        self, 
        limit: int,
        model_id: str = "Qwen/Qwen2.5-Coder-32B-Instruct",
        temperature: float = 0.8,
        config_id: str = "default",
        seen_names: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Genera candidatos cuánticos usando HuggingFace Inference API.
        
        Args:
            limit: Número de circuitos a generar
            model_id: ID del modelo HF (DeepSeek-V3, Qwen2.5-Coder-32B, etc.)
            temperature: Temperatura para diversidad
            config_id: Identificador único de configuración para máxima variabilidad
            seen_names: Lista de nombres ya usados (para evitar duplicados)
            
        Returns:
            Lista de especificaciones de circuitos cuánticos
        """
        import requests
        from app.config.api_keys_manager import get_api_key
        
        # Obtener API key desde almacenamiento cifrado (mismo sistema que HuggingFaceProvider)
        hf_token = get_api_key("HUGGINGFACE")
        if not hf_token:
            logger.warning("⚠️ HUGGINGFACE API key not found, usando templates fallback")
            return []
        
        # Usar nuevo endpoint (router.huggingface.co/v1) compatible con OpenAI API
        api_url = "https://router.huggingface.co/v1/chat/completions"
        
        # Generar seed único basado en config_id para máxima diversidad
        config_seed = hash(config_id) % 10000
        seen_names = seen_names or []
        avoid_list = ", ".join(seen_names[-10:]) if seen_names else "None"
        
        prompt = f"""Generate {limit} novel quantum circuit designs for configuration: {config_id}

CRITICAL UNIQUENESS REQUIREMENTS:
- Configuration seed: {config_seed}
- Avoid these names: {avoid_list}
- Generate MAXIMALLY DIFFERENT circuits from any previous calls
- Be EXTREMELY CREATIVE and VARIED in your approach

Respond with ONLY a valid JSON array.

Each circuit must have:
- "name": unique ID (e.g., "AdaptiveVQE_H2_v3")
- "algorithm": "vqe" or "qaoa"
- "n_qubits": integer 3-8
- "depth": integer 2-8
- "parameters": object with optimizer, layers
- "motivation": one sentence scientific rationale

Requirements:
1. Each circuit MUST be different and scientifically novel
2. Focus on quantum chemistry (VQE), optimization (QAOA), or quantum ML
3. Vary complexity and approach across circuits
4. Be creative but grounded

Example format (respond with {limit} circuits):
[
  {{"name": "AdaptiveVQE_LiH_v2", "algorithm": "vqe", "n_qubits": 4, "depth": 3, "parameters": {{"optimizer": "COBYLA", "layers": 3}}, "motivation": "Ground state energy for lithium hydride with adaptive ansatz"}},
  {{"name": "QAOA_TSP_8node", "algorithm": "qaoa", "n_qubits": 8, "depth": 5, "parameters": {{"optimizer": "SPSA", "p": 5}}, "motivation": "Traveling salesman problem with 8 nodes using QAOA"}},
  ...
]

Generate {limit} quantum circuits NOW (JSON array only):"""
        
        headers = {
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": "application/json"
        }
        
        # Payload compatible con OpenAI Chat Completions API
        payload = {
            "model": model_id,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature,
            "max_tokens": 2048,
            "top_p": 0.95,
            "stream": False
        }
        
        try:
            llm_text = ""  # Initialize for error handling
            logger.info(f"🌐 Calling HuggingFace Router API ({model_id}) for {limit} quantum circuits...")
            logger.info(f"🎲 Temperature: {temperature}, max_tokens: 2048")
            
            # Retry logic for HuggingFace API (max 3 attempts)
            max_retries = 3
            retry_delay = 5  # seconds
            last_error = None
            response = None  # Initialize response
            
            for attempt in range(1, max_retries + 1):
                try:
                    response = await asyncio.to_thread(
                        requests.post,
                        api_url,
                        headers=headers,
                        json=payload,
                        timeout=120  # 2 min timeout para modelos grandes
                    )
                    
                    if response.status_code == 200:
                        break  # Success!
                    else:
                        last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                        if attempt < max_retries:
                            logger.warning(f"⚠️ Attempt {attempt}/{max_retries} failed: {last_error}")
                            logger.info(f"🔄 Retrying in {retry_delay}s...")
                            await asyncio.sleep(retry_delay)
                        else:
                            logger.error(f"❌ All {max_retries} attempts failed: {last_error}")
                            return []
                            
                except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
                    last_error = str(e)
                    if attempt < max_retries:
                        logger.warning(f"⚠️ Attempt {attempt}/{max_retries} failed with {type(e).__name__}: {e}")
                        logger.info(f"🔄 Retrying in {retry_delay}s...")
                        await asyncio.sleep(retry_delay)
                    else:
                        logger.error(f"❌ All {max_retries} attempts failed with exception: {e}")
                        return []
            
            # Parse response after successful attempt
            if response is None or response.status_code != 200:
                logger.error(f"❌ No valid response after {max_retries} attempts")
                return []
            
            result = response.json()
            
            # Chat Completions format: result['choices'][0]['message']['content']
            if isinstance(result, dict) and 'choices' in result:
                llm_text = result['choices'][0]['message']['content']
            else:
                logger.error(f"❌ Unexpected HF response format: {type(result)}")
                logger.error(f"Keys: {result.keys() if isinstance(result, dict) else 'not a dict'}")
                return []
            
            logger.info(f"📝 LLM response ({len(llm_text)} chars): {llm_text[:300]}...")
            
            # Extraer JSON del texto (puede venir con markdown o explicaciones)
            json_match = re.search(r'\[\s*\{.*?\}\s*\]', llm_text, re.DOTALL)
            if json_match:
                circuits = json.loads(json_match.group(0))
            else:
                # Intentar parsear todo el texto como JSON
                circuits = json.loads(llm_text.strip())
            
            if isinstance(circuits, list) and len(circuits) > 0:
                logger.info(f"✅ HuggingFace API generated {len(circuits)} quantum circuits")
                return circuits[:limit]
            else:
                logger.warning(f"⚠️ Invalid response format: {type(circuits)}")
                return []
                
        except requests.exceptions.RequestException as exc:
            logger.error(f"❌ HuggingFace API request failed: {exc}")
            return []
        except json.JSONDecodeError as exc:
            logger.error(f"❌ JSON decode error: {exc}")
            return []
        except Exception as exc:
            logger.error(f"❌ Unexpected error in HuggingFace generation: {exc}")
            import traceback
            traceback.print_exc()
            return []
    
    async def _default_provider_async(self, limit: int, config_id: str = "default", seen_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Genera candidatos cuánticos usando HuggingFace LLM para mayor diversidad.
        
        CAMBIO ARQUITECTÓNICO (Phase 8.4):
        - Antes: fetch_quantum_circuit_templates() → candidatos fijos
        - Ahora: HF API genera circuitos únicos → cada config/ejecución obtiene candidatos diferentes
        
        Args:
            limit: Número de candidatos a generar
            config_id: Identificador único de configuración (para máxima variabilidad)
            seen_names: Lista de nombres ya usados (para evitar duplicados)
        """
        candidates: List[Dict[str, Any]] = []
        seen_names = seen_names or []
        
        # ⭐ NUEVO: Detectar modelo asignado desde config/agents.yaml
        try:
            from app.config.config_loader import load_config_section
            agents_config = load_config_section("agents")
            physchem_model = agents_config.get("roles", {}).get("physchem_coder", {}).get("model")
            temperature_config = agents_config.get("roles", {}).get("physchem_coder", {}).get("params", {}).get("temperature", 0.7)
            
            # Si el modelo es Ollama local (e.g., "llama2:7b"), usar modelo HF por defecto
            if physchem_model and ("huggingface.co" in physchem_model or "/" in physchem_model):
                model_id = physchem_model
                logger.info(f"🎯 Using model from config: {model_id}")
            else:
                # Fallback a Qwen2.5-Coder-32B-Instruct (modelo por defecto para código)
                model_id = "Qwen/Qwen2.5-Coder-32B-Instruct"
                logger.warning(f"⚠️ Config model '{physchem_model}' is local Ollama, using HF default: {model_id}")
            
            # Aumentar temperatura para MÁXIMA diversidad (+0.4 boost)
            generation_temp = min(0.95, temperature_config + 0.4)  # Phase 8.5: +0.4 para 0.75-0.85 range
            
        except Exception as exc:
            logger.warning(f"⚠️ Could not load model from config: {exc}, using default")
            model_id = "Qwen/Qwen2.5-Coder-32B-Instruct"
            generation_temp = 0.85  # Higher default for diversity
        
        # ⭐ NUEVO: Usar HuggingFace Inference API para generar candidatos únicos
        try:
            llm_candidates = await self._generate_candidates_with_huggingface(
                limit=limit,
                model_id=model_id,
                temperature=generation_temp,
                config_id=config_id,
                seen_names=seen_names
            )
            
            if llm_candidates:
                logger.info(f"✅ HF LLM generated {len(llm_candidates)} quantum candidates")
                
                # Convertir candidatos LLM a formato interno
                for idx, llm_cand in enumerate(llm_candidates):
                    name = llm_cand.get("name", f"llm_quantum_{idx}")
                    algorithm = llm_cand.get("algorithm", "vqe").lower()
                    n_qubits = int(llm_cand.get("n_qubits", 3))
                    depth = int(llm_cand.get("depth", 2))
                    params = llm_cand.get("parameters", {})
                    
                    # Calcular métricas derivadas
                    hardware_efficiency = min(1.0, 0.5 + (8 - n_qubits) * 0.05)
                    information_gain = min(1.0, 0.4 + depth * 0.1)
                    
                    candidates.append({
                        "id": name,
                        "algorithm": algorithm,
                        "n_qubits": n_qubits,
                        "depth": depth,
                        "parameters": params,
                        "embedding": [float(n_qubits), float(depth), hardware_efficiency],
                        "literature_frequency": 10 + idx * 2,  # Synthetic
                        "dependency_count": max(1, depth // 2),
                        "impact_potential": float(min(1.0, 0.6 + idx * 0.05)),
                        "proveability": 0.5 + idx * 0.05,
                        "novelty": max(0.3, 0.9 - idx * 0.05),  # Mayor novelty para primeros
                        "information_gain": information_gain,
                        "estimated_cost": 0.2 + idx * 0.03,
                        "data_source": "hf_llm_generated",
                        "hf_model": model_id,  # ⭐ NUEVO: Tracking de modelo usado
                        "motivation": llm_cand.get("motivation", "HF LLM-generated quantum circuit"),
                    })
                
                logger.info(f"🎯 Converted {len(candidates)} HF LLM candidates to internal format")
            else:
                logger.warning("⚠️ HF LLM generation failed, falling back to template-based generation")
                raise ValueError("HF LLM generation produced no valid candidates")
                
        except Exception as llm_exc:
            logger.warning(f"⚠️ HF LLM generation error: {llm_exc}, falling back to templates")
            
            # FALLBACK: Usar templates si LLM falla
            def _blocking_fetch() -> List[Dict[str, Any]]:
                try:
                    return fetch_quantum_circuit_templates(limit)
                except Exception as exc:  # noqa: BLE001
                    logger.debug("Quantum templates fetch failed: %s", exc)
                    return []

            templates = await asyncio.to_thread(_blocking_fetch)
            for idx, template in enumerate(templates):
                if len(candidates) >= limit:
                    break
                depth = int(template.get("depth", 3) or 3)
                two_qubit_gates = int(template.get("two_qubit_gates", 6) or 6)
                hardware_efficiency = float(template.get("hardware_efficiency", 0.7) or 0.7)
                name_lower = str(template.get("name", "")).lower()
                algorithm = "qaoa" if "qaoa" in name_lower else ("vqe" if "vqe" in name_lower else "template")
                n_qubits = max(2, two_qubit_gates // 2 + 2)
                information_gain = min(1.0, 0.5 + hardware_efficiency * 0.4)
                candidates.append({
                    "id": template.get("name", f"q_template_{idx}"),
                    "algorithm": algorithm,
                    "n_qubits": n_qubits,
                    "depth": depth,
                    "parameters": template.get("parameters", {"problem_size": two_qubit_gates, "layers": depth}),
                    "embedding": [float(n_qubits), float(depth), hardware_efficiency],
                    "literature_frequency": template.get("literature_mentions", 20 + idx * 2),
                    "dependency_count": max(1, 1 + two_qubit_gates // 3),
                    "impact_potential": float(min(1.0, 0.55 + hardware_efficiency * 0.35)),
                    "proveability": float(min(1.0, 0.5 + hardware_efficiency * 0.3)),
                    "novelty": float(max(0.15, 0.8 - hardware_efficiency * 0.2)),
                    "information_gain": information_gain,
                    "estimated_cost": float(max(0.15, 0.25 - hardware_efficiency * 0.05)),
                    "template": template,
                    "data_source": template.get("source", "axiom_quantum_bridge"),
                })

        # Si aún no tenemos suficientes, generar sintéticos
        if len(candidates) < limit:
            for idx in range(len(candidates), limit):
                depth = 2 + idx % 3
                n_qubits = 3 + (idx % 2)
                candidates.append({
                    "id": f"q_candidate_{idx}",
                    "algorithm": "vqe" if idx % 2 == 0 else "qaoa",
                    "n_qubits": n_qubits,
                    "depth": depth,
                    "parameters": {
                        "problem_size": 4 + idx,
                        "layers": depth,
                        "optimizer": "COBYLA" if idx % 2 == 0 else "SPSA",
                    },
                    "embedding": [float(n_qubits), float(depth), float(0.5 + idx * 0.1)],
                    "literature_frequency": 15 + idx * 3,
                    "dependency_count": 1 + idx % 3,
                    "impact_potential": min(1.0, 0.6 + idx * 0.05),
                    "proveability": 0.5 + idx * 0.05,
                    "novelty": max(0.2, 0.8 - idx * 0.05),
                    "information_gain": min(1.0, 0.5 + idx * 0.08),
                    "estimated_cost": 0.2 + idx * 0.03,
                    "data_source": "synthetic_fallback",
                })

        return candidates
    
    def _parse_llm_quantum_response(self, llm_response: str, expected_count: int) -> List[Dict[str, Any]]:
        """
        Parsea la respuesta del LLM y extrae especificaciones de circuitos cuánticos.
        
        Args:
            llm_response: Texto generado por el LLM
            expected_count: Número esperado de circuitos
            
        Returns:
            Lista de diccionarios con especificaciones de circuitos
        """
        try:
            # Intentar parsear como JSON directo
            # Buscar array JSON en la respuesta
            json_match = re.search(r'\[\s*\{.*?\}\s*\]', llm_response, re.DOTALL)
            if json_match:
                circuits = json.loads(json_match.group(0))
                if isinstance(circuits, list) and len(circuits) > 0:
                    logger.info(f"✅ Parsed {len(circuits)} circuits from LLM JSON response")
                    return circuits[:expected_count]
            
            # Fallback: parseo manual si el JSON no es válido
            logger.warning("⚠️ JSON parsing failed, attempting manual parsing")
            circuits = []
            
            # Buscar patrones de circuitos en texto
            lines = llm_response.split('\n')
            current_circuit = {}
            
            for line in lines:
                line = line.strip()
                
                # Detectar inicio de nuevo circuito
                if '"name"' in line or 'name:' in line:
                    if current_circuit:
                        circuits.append(current_circuit)
                    current_circuit = {}
                    
                    # Extraer nombre
                    name_match = re.search(r'["\']name["\']\s*:\s*["\']([^"\']+)["\']', line)
                    if name_match:
                        current_circuit['name'] = name_match.group(1)
                
                # Extraer algorithm
                if '"algorithm"' in line or 'algorithm:' in line:
                    alg_match = re.search(r'["\']algorithm["\']\s*:\s*["\']([^"\']+)["\']', line)
                    if alg_match:
                        current_circuit['algorithm'] = alg_match.group(1)
                
                # Extraer n_qubits
                if 'n_qubits' in line or 'qubits' in line:
                    qubit_match = re.search(r'(\d+)', line)
                    if qubit_match:
                        current_circuit['n_qubits'] = int(qubit_match.group(1))
                
                # Extraer depth
                if 'depth' in line:
                    depth_match = re.search(r'(\d+)', line)
                    if depth_match:
                        current_circuit['depth'] = int(depth_match.group(1))
            
            if current_circuit:
                circuits.append(current_circuit)
            
            if circuits:
                logger.info(f"✅ Manual parsing extracted {len(circuits)} circuits")
                return circuits[:expected_count]
            
            logger.error("❌ Failed to parse any circuits from LLM response")
            return []
            
        except Exception as exc:
            logger.error(f"❌ Error parsing LLM response: {exc}")
            logger.debug(f"LLM response was: {llm_response[:500]}...")
            return []

    async def _evaluate_candidate_async(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        algorithm = candidate.get("algorithm", "vqe")
        parameters = candidate.get("parameters", {})
        simulation: Dict[str, Any]

        try:
            if algorithm == "vqe":
                simulation = self.quantum_service._run_vqe(parameters)
            elif algorithm == "qaoa":
                simulation = self.quantum_service._run_qaoa(parameters)
            else:
                simulation = self.quantum_service.create_bell_state_qiskit()
        except (RuntimeError, ValueError, NotImplementedError) as exc:  # pragma: no cover
            simulation = {"error": str(exc)}

        # ⭐ NUEVO: Análisis adicional con servicios cuánticos avanzados
        advanced_analysis: Dict[str, Any] = {}
        
        # 1. Quantum Algorithms Service - análisis de ventaja cuántica
        n_qubits = candidate.get("n_qubits", 3)
        depth = candidate.get("depth", 2)
        try:
            logger.info("🔬 Analyzing quantum advantage...")
            advanced_analysis["quantum_advantage"] = await asyncio.to_thread(
                self.quantum_algorithms_service.analyze_quantum_advantage,
                n_qubits
            )
            logger.info("✓ Quantum advantage analysis complete")
        except Exception as exc:
            logger.warning(f"Quantum advantage analysis failed: {exc}")
            advanced_analysis["quantum_advantage"] = {"error": str(exc)}
        
                # 2. Physics-Informed Neural Networks (PINN) - solo para circuitos pequeños
        # Note: PhysicsInformedNNService not available (missing implementation)
        # if algorithm == "qaoa" and n_qubits <= 6:
        #     try:
        #         logger.info("🧠 Running PINN simulation...")
        #         pinn_config = {...}
        #         advanced_analysis["pinn_simulation"] = await asyncio.to_thread(
        #             self.physics_informed_nn_service.solve_pde_pytorch,
        #             pinn_config
        #         )
        #         logger.info("✓ PINN simulation complete")
        #     except Exception as exc:
        #         logger.warning(f"PINN simulation failed: {exc}")
        #         advanced_analysis["pinn_simulation"] = {"error": str(exc)}
        
        # 3. Quantum Chemistry - análisis molecular para VQE (muy pequeño)
        # Note: QuantumChemistryService not available in chemistry domain
        # if algorithm == "vqe" and n_qubits <= 4:
        #     try:
        #         logger.info("⚛️ Running quantum chemistry analysis...")
        #         qc_result = await asyncio.to_thread(
        #             self.quantum_chemistry_service.molecular_energy_calculation,
        #             {"molecule": "H2", "method": "hf", "basis": "sto-3g"}
        #         )
        #         advanced_analysis["quantum_chemistry"] = qc_result
        #         logger.info("✓ Quantum chemistry analysis complete")
        #     except Exception as exc:
        #         logger.warning(f"Quantum chemistry analysis failed: {exc}")
        #         advanced_analysis["quantum_chemistry"] = {"error": str(exc)}

        return {
            "algorithm": algorithm,
            "simulation": simulation,
            "advanced_analysis": advanced_analysis,  # ⭐ NUEVO
        }

    def _build_quantum_hypothesis(
        self,
        candidate: Dict[str, Any],
        evaluation: Dict[str, Any],
    ) -> Dict[str, Any]:
        circuit_id = candidate.get("id", "quantum_candidate")
        algorithm = candidate.get("algorithm", "unknown")
        description = (
            f"Corroborar si el circuito {circuit_id} basado en {algorithm.upper()} muestra soporte externo"
            " para continuar exploración experimental."
        )
        variables: Dict[str, Any] = {
            "algorithm": algorithm,
            "n_qubits": candidate.get("n_qubits"),
            "depth": candidate.get("depth"),
            "difficulty_hint": candidate.get("difficulty_hint"),
            "simulation": evaluation.get("simulation"),
        }
        assumptions = [
            "Las simulaciones provienen del QuantumComputingService",
            "El circuito será ejecutado en hardware superconducting de escala intermedia",
        ]
        extras = {
            "parameters": candidate.get("parameters"),
            "keywords": [algorithm, circuit_id],
        }
        return self.tool_evidence.build_hypothesis(
            title=f"Validación circuito {circuit_id}",
            description=description,
            variables=variables,
            assumptions=assumptions,
            expected_outcome="Determinar viabilidad para ejecución en hardware integrado",
            extras=extras,
        )

    async def _run_iteration_impl(
        self,
        iteration: int,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        start = time.time()
        if limit is None:
            limit = 6

        # Generar config_id único para máxima variabilidad
        # INCLUYE: iteration, timestamp, modelo actual, temperature
        import hashlib
        timestamp_ms = int(time.time() * 1000)
        
        # Extraer info del modelo actual para diferenciar configs
        try:
            from app.config.config_loader import load_config_section
            agents_config = load_config_section("agents")
            current_model = agents_config.get("roles", {}).get("physchem_coder", {}).get("model", "unknown")
            current_temp = agents_config.get("roles", {}).get("physchem_coder", {}).get("params", {}).get("temperature", 0.7)
            model_signature = f"{current_model}@{current_temp}"
        except Exception:
            model_signature = "unknown"
        
        config_seed_str = f"quantum_iter{iteration}_ts{timestamp_ms}_model{model_signature}"
        config_id = hashlib.sha256(config_seed_str.encode()).hexdigest()[:16]
        
        candidates: List[Dict[str, Any]] = []
        if self.provider:
            candidates = self.provider()

        if not candidates:
            candidates = await self._default_provider_async(
                limit=limit,
                config_id=config_id,
                seen_names=self._seen_names
            )
            
            # Acumular nombres generados para evitar duplicados en futuras iteraciones
            for cand in candidates:
                cand_name = cand.get("id") or cand.get("name", "unknown")
                if cand_name not in self._seen_names:
                    self._seen_names.append(cand_name)

        if not candidates:
            logger.warning("No quantum candidates provided")
            return {"success": False, "reason": "no_candidates"}

        for candidate in candidates:
            candidate["difficulty_hint"] = self.difficulty.estimate(candidate)

        novelty_scores: List[float] = []
        for candidate in candidates:
            emb = candidate.get("embedding") or []
            score = self.novelty.assess(emb)["novelty_score"]
            candidate["novelty_score"] = score
            novelty_scores.append(score)

        ranked = self.scorer.rank(candidates)
        scheduled = self.scheduler.select(ranked, limit=4)
        allocated = self.budget.allocate(scheduled)
        mutations = [{"parent": a.get("id", "?"), "type": "param_tweak"} for a in allocated]

        if self._cached_design is None:
            design_config = {
                "factors": {"lr": [0.01, 0.02], "depth": [2, 4]},
                "max_runs": 4,
                "stop_metric": "energy",
            }
            self._cached_design = generate_experimental_design(design_config)

        feedback_event = {
            "metric_name": "mutation_volume",
            "value": len(mutations),
            "improved": len(mutations) > 0,
            "confidence": 0.55,
        }
        feedback_result = process_feedback(feedback_event)

        enriched_allocated: List[Dict[str, Any]] = []
        outcomes: Dict[str, Any] = {}
        support_scores: List[float] = []
        for candidate in allocated:
            evaluation = await self._evaluate_candidate_async(candidate)
            evidence_summary: Optional[EvidenceSummary] = None
            ethics_metadata = {"ethics_approved": True, "ethics_decision_id": None, "ethics_risk_level": "LOW"}
            
            if self.tool_evidence:
                try:
                    hypothesis = self._build_quantum_hypothesis(candidate, evaluation)
                    
                    # Ethics evaluation before execution
                    circuit_id = candidate.get("id", "unknown")
                    keywords = [circuit_id, "quantum_computing", "circuit_simulation"]
                    if candidate.get("domain"):
                        keywords.append(candidate["domain"])
                    
                    ethics_request = ExperimentRequest(
                        domain="quantum_physics",
                        description=hypothesis.get("description", ""),
                        data_sensitivity="low",
                        declared_intent="research",
                        keywords=keywords,
                        user_id="quantum_loop",
                        metadata={
                            "candidate_id": circuit_id,
                            "iteration": iteration,
                        }
                    )
                    
                    ethics_decision = self.ethics_gate.evaluate(ethics_request)
                    ethics_metadata.update({
                        "ethics_approved": ethics_decision.allowed,
                        "ethics_decision_id": ethics_decision.decision_id,
                        # Pydantic v2: EthicsDecision uses `level` instead of `risk_level`
                        "ethics_risk_level": getattr(ethics_decision, "level", getattr(ethics_decision, "risk_level", "UNKNOWN")),
                    })
                    
                    if not ethics_decision.allowed:
                        logger.warning(
                            f"Quantum hypothesis {circuit_id} blocked by ethics gate: "
                            f"{getattr(ethics_decision, 'level', 'UNKNOWN')} risk, reasons: {ethics_decision.escalation_reasons}"
                        )
                        # Skip this candidate if blocked
                        continue
                    
                    if ethics_decision.requires_signature:
                        logger.info(
                            f"Quantum hypothesis {circuit_id} requires human review: "
                            f"{ethics_decision.recommended_actions}"
                        )
                    
                    # Add extra quantum-centric keywords to help external evidence search
                    hypothesis.setdefault("extras", {})
                    kw = set(hypothesis["extras"].get("keywords", []) or [])
                    alg = candidate.get("algorithm") or evaluation.get("algorithm") or "quantum"
                    kw.update({
                        "quantum", "quantum_circuit", "qiskit", "quant-ph", "arxiv",
                        str(alg), str(alg).upper(), "VQE", "QAOA", "Bell state"
                    })
                    hypothesis["extras"]["keywords"] = list(kw)
                    evidence_summary = await self.tool_evidence.corroborate(hypothesis, domain="quantum")
                    if evidence_summary.success:
                        candidate["impact_potential"] = min(
                            1.0,
                            float(candidate.get("impact_potential", 0.5)) + evidence_summary.support_score * 0.1,
                        )
                        support_scores.append(evidence_summary.support_score)
                    else:
                        # Minimal fallback support even if external corroboration fails
                        # Slightly higher if simulation executed without errors
                        sim = evaluation.get("simulation", {}) if isinstance(evaluation, dict) else {}
                        fallback_support = 0.05 if (isinstance(sim, dict) and not sim.get("error")) else 0.03
                        support_scores.append(fallback_support)
                except (RuntimeError, ValueError, ConnectionError, TimeoutError) as exc:
                    logger.debug("Quantum corroboration failed for %s: %s", candidate.get("id"), exc)
                    # Graceful minimal fallback
                    support_scores.append(0.0)
            enriched = {
                **candidate,
                "evaluation": evaluation,
                "tool_evidence": evidence_summary.as_dict() if evidence_summary else None,
                "ethics": ethics_metadata,
            }
            enriched_allocated.append(enriched)
            outcomes[candidate.get("id", "?")] = {
                "mutation_type": "param_tweak",
                "evaluation": evaluation,
                "tool_evidence": evidence_summary.as_dict() if evidence_summary else None,
                "ethics": ethics_metadata,
            }

        record = IterationRecord(
            iteration=iteration,
            domain="quantum",
            selected_ids=[c.get("id", "?") for c in allocated],
            actions=["param_tweak"],
            outcomes={**outcomes, "feedback_adjustment": feedback_result["adjustment"]},
        )
        self.state.add_iteration(record)
        duration = time.time() - start
        avg_novelty = sum(novelty_scores) / len(novelty_scores) if novelty_scores else 0.0
        design_size = self._cached_design["total_planned"] if self._cached_design else 0
        avg_support = sum(support_scores) / len(support_scores) if support_scores else 0.0
        summary = {
            "iteration": iteration,
            "duration_s": duration,
            "selected": len(allocated),
            "mutations": len(mutations),
            "sketches": 0,
            "avg_novelty": avg_novelty,
            "design_size": design_size,
            "avg_support_score": avg_support,
        }
        try:
            telemetry.record_iteration(
                domain="quantum",
                duration_s=duration,
                selected=len(allocated),
                mutations=len(mutations),
                sketches=0,
            )
        except (ValueError, RuntimeError) as exc:
            logger.warning("Telemetry recording failed (quantum): %s", exc)
        try:
            from app.monitoring.metrics import metrics  # local import

            metrics.set_gauge("autonomous_novelty_last", float(avg_novelty))
            metrics.set_gauge("autonomous_feedback_adjustment_last", feedback_result["adjustment"])
            if support_scores:
                metrics.set_gauge("autonomous_support_score_last", avg_support)
        except (ImportError, AttributeError):  # pragma: no cover
            logger.debug("Could not set novelty gauge")
        logger.info("Quantum loop iteration %d: %s", iteration, summary)
        
        # ✅ FIX: Retornar enriched_allocated en múltiples keys para compatibilidad
        return {
            "success": True,
            "summary": summary,
            "mutations": mutations,
            "selected": enriched_allocated,
            "outcomes": enriched_allocated,  # Para orchestrador
            "candidates": enriched_allocated,  # ⭐ AGREGADO: para tests y consistencia
            "avg_support_score": avg_support,
        }

    def run_iteration(self, iteration: int, limit: Optional[int] = None) -> Dict[str, Any]:
        return self._run_coro_sync(self._run_iteration_impl(iteration=iteration, limit=limit))

    async def run_quantum_discovery_iteration(
        self,
        iteration: int = 1,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Iteración asíncrona para pipelines cuánticos Meta 4."""

        return await self._run_iteration_impl(iteration=iteration, limit=limit)

__all__ = ["QuantumLoop"]
