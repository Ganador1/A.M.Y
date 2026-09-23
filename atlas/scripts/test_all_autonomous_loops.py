#!/usr/bin/env python3
"""
Test comprehensivo de loops autónomos reales de AXIOM ATLAS
Objetivo: Detectar inconsistencias, errores en baselines, validación con herramientas

Loops disponibles en AXIOM:
1. Biology Loop (genomics/protein) - app/autonomous/pipelines/biology_loop.py
2. Chemistry Loop (molecular discovery) - app/autonomous/pipelines/chemistry_loop.py
3. Materials Loop (materials science) - app/autonomous/pipelines/materials_loop.py
4. Quantum Loop (quantum computing) - app/autonomous/pipelines/quantum_loop.py
5. Mathematics Loop (mathematical conjectures) - app/autonomous/pipelines/mathematics_loop.py
6. Climate Loop (climate modeling) - app/autonomous/pipelines/climate_loop.py
7. Enhanced Chemistry Loop - app/autonomous/pipelines/enhanced_chemistry_loop.py

Herramientas de validación integradas:
- EthicsGate (safety filtering)
- ToolEvidenceBridge (corroboration)
- NoveltyAssessor (originality)
- ExperimentalDesignGenerator (protocol generation)
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Importar coordinador multi-agente
try:
    from app.services.multi_agent_coordinator import MultiAgentCoordinator
except ImportError as e:
    print(f"❌ Error importing MultiAgentCoordinator: {e}")
    sys.exit(1)

# Importar loops autónomos REALES
try:
    from app.autonomous.pipelines.biology_loop import BiologyLoop
    from app.autonomous.pipelines.chemistry_loop import ChemistryLoop
    from app.autonomous.pipelines.materials_loop import MaterialsLoop
    LOOPS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: Some loops not available: {e}")
    LOOPS_AVAILABLE = False
    # Placeholders to satisfy static analysis when imports are unavailable
    BiologyLoop = None  # type: ignore
    ChemistryLoop = None  # type: ignore
    MaterialsLoop = None  # type: ignore

# Importar herramientas de validación (no estrictamente usadas aquí)
try:
    VALIDATION_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: Validation tools not available: {e}")
    VALIDATION_TOOLS_AVAILABLE = False


class LoopValidator:
    """Validador de calidad científica para outputs de loops autónomos"""

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.validation_results = {}

    def validate_hypothesis(self, hypothesis: str, domain: str) -> Dict[str, Any]:
        """Valida estructura y contenido de hipótesis"""
        # domain is currently unused; keep for future domain-specific rules
        _ = domain
        issues = []

        # Check 1: ¿Tiene predicciones cuantitativas?
        if not any(char.isdigit() for char in hypothesis):
            issues.append("⚠️ No contiene predicciones numéricas")

        # Check 2: ¿Menciona métodos/técnicas?
        methods_keywords = ['ELISA', 'qPCR', 'spectroscopy', 'XRD', 'NMR', 'mass spec',
                           'sequencing', 'crystallography', 'microscopy']
        if not any(method.lower() in hypothesis.lower() for method in methods_keywords):
            issues.append("⚠️ No menciona métodos experimentales específicos")

        # Check 3: ¿Tiene timeline?
        time_keywords = ['weeks', 'months', 'days', 'hours', 'years']
        if not any(time.lower() in hypothesis.lower() for time in time_keywords):
            issues.append("⚠️ No especifica timeline")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "length": len(hypothesis)
        }

    def validate_code(self, code: str) -> Dict[str, Any]:
        """Valida código ejecutable"""
        issues = []

        # Check 1: ¿Tiene imports?
        if "import" not in code:
            issues.append("❌ No tiene imports (probablemente incompleto)")

        # Check 2: ¿Tiene funciones?
        if "def " not in code:
            issues.append("⚠️ No define funciones (código no modular)")

        # Check 3: ¿Tiene docstrings?
        if '"""' not in code and "'''" not in code:
            issues.append("⚠️ No tiene docstrings")

        # Check 4: ¿Tiene validación de datos?
        validation_keywords = ['raise', 'assert', 'ValueError', 'if not', 'check']
        if not any(kw in code for kw in validation_keywords):
            issues.append("⚠️ No tiene validación de inputs")

        return {
            "valid": len([i for i in issues if i.startswith("❌")]) == 0,
            "issues": issues,
            "lines": len(code.split('\n'))
        }

    def extract_numerical_values(self, text: str) -> List[float]:
        """Extrae valores numéricos del texto"""
        import re
        # Pattern para números con unidades (ej: "12.5 pg/mL", "30±8%")
        pattern = r'(\d+\.?\d*)\s*±?\s*(\d+\.?\d*)?'
        matches = re.findall(pattern, text)
        values = []
        for match in matches:
            try:
                values.append(float(match[0]))
            except (ValueError, TypeError):
                continue
        return values

    def check_baseline_consistency(self, hypothesis: str, code: str) -> Dict[str, Any]:
        """Verifica consistencia de baselines entre hipótesis y código"""
        hyp_values = self.extract_numerical_values(hypothesis)
        code_values = self.extract_numerical_values(code)

        # Buscar valores comunes (con tolerancia de ±5%)
        matches = []
        mismatches = []

        for hv in hyp_values:
            found = False
            for cv in code_values:
                max_val = max(abs(hv), abs(cv))
                if max_val > 0 and abs(hv - cv) / max_val < 0.05:  # 5% tolerance
                    matches.append((hv, cv))
                    found = True
                    break
                elif max_val == 0 and hv == cv:  # Both are zero
                    matches.append((hv, cv))
                    found = True
                    break
            if not found and abs(hv) > 1:  # Ignorar valores muy pequeños (indices, etc)
                mismatches.append(hv)

        return {
            "matches": len(matches),
            "mismatches": len(mismatches),
            "consistency_score": len(matches) / max(len(hyp_values), 1) * 100,
            "mismatch_values": mismatches[:5]  # Primeros 5 valores inconsistentes
        }

    def validate_peer_review(self, review: str, hypothesis: str) -> Dict[str, Any]:
        """Valida calidad del peer review"""
        issues = []

        # Check 1: ¿Identifica weaknesses?
        if "weakness" not in review.lower() and "limitation" not in review.lower():
            issues.append("❌ No identifica debilidades (review no crítico)")

        # Check 2: ¿Menciona valores numéricos del hypothesis?
        hyp_numbers = self.extract_numerical_values(hypothesis)
        review_numbers = self.extract_numerical_values(review)

        if len(hyp_numbers) > 0 and len(review_numbers) == 0:
            issues.append("⚠️ No analiza valores cuantitativos")

        # Check 3: ¿Sugiere mejoras específicas?
        improvement_keywords = ['suggest', 'recommend', 'should add', 'improve', 'increase']
        if not any(kw in review.lower() for kw in improvement_keywords):
            issues.append("⚠️ No propone mejoras específicas")

        # Check 4: ¿Tiene veredicto?
        verdict_keywords = ['approve', 'reject', 'revise', 'accept']
        if not any(kw in review.lower() for kw in verdict_keywords):
            issues.append("❌ No tiene veredicto claro")

        return {
            "valid": len([i for i in issues if i.startswith("❌")]) == 0,
            "issues": issues,
            "critical_level": sum(1 for i in issues if i.startswith("❌"))
        }


async def test_biology_loop():
    """Test del loop de biología (genomics/protein)"""
    print("\n" + "="*80)
    print("🧬 TEST: BIOLOGY LOOP (Genomics/Protein Analysis)")
    print("="*80)

    coordinator = MultiAgentCoordinator()
    validator = LoopValidator()

    research_goal = """
    Investigate the role of APOE4 allele in Alzheimer's disease progression through
    protein-protein interaction network analysis. Hypothesis: APOE4 variant disrupts
    lipid metabolism pathways, leading to increased Aβ aggregation.
    """

    results = {}

    try:
        # Fase 1: Planning
        print("\n📋 Fase 1: Planning...")
        plan = await coordinator.plan_async(research_goal)
        print(f"   ✓ Plan generado: {len(plan)} caracteres")
        results['plan'] = plan

        # Fase 2: Hypothesis Generation
        print("\n🧪 Fase 2: Generando hipótesis...")
        hypothesis = await coordinator.generate_bio_hypothesis_async(research_goal)
        print(f"   ✓ Hipótesis generada: {len(hypothesis)} caracteres")
        results['hypothesis'] = hypothesis

        # Validar hipótesis
        hyp_validation = validator.validate_hypothesis(hypothesis, "biology")
        print(f"   📊 Validación hipótesis: {'✅ PASS' if hyp_validation['valid'] else '❌ FAIL'}")
        for issue in hyp_validation['issues']:
            print(f"      {issue}")
        results['hypothesis_validation'] = hyp_validation

        # Fase 3: Code Generation
        print("\n💻 Fase 3: Generando código experimental...")
        code = await coordinator.design_and_code_async(hypothesis)
        print(f"   ✓ Código generado: {len(code)} caracteres, {len(code.split(chr(10)))} líneas")
        results['code'] = code

        # Validar código
        code_validation = validator.validate_code(code)
        print(f"   📊 Validación código: {'✅ PASS' if code_validation['valid'] else '❌ FAIL'}")
        for issue in code_validation['issues']:
            print(f"      {issue}")
        results['code_validation'] = code_validation

        # Check consistencia hipótesis-código
        consistency = validator.check_baseline_consistency(hypothesis, code)
        print(f"\n   🔗 Consistencia hipótesis-código: {consistency['consistency_score']:.1f}%")
        print(f"      Matches: {consistency['matches']}, Mismatches: {consistency['mismatches']}")
        if consistency['mismatch_values']:
            print(f"      ⚠️ Valores inconsistentes: {consistency['mismatch_values']}")
        results['consistency'] = consistency

        # Fase 4: Peer Review
        print("\n📝 Fase 4: Peer review...")
        review = await coordinator.critical_review_async(hypothesis, code)
        print(f"   ✓ Review generado: {len(review)} caracteres")
        results['review'] = review

        # Validar review
        review_validation = validator.validate_peer_review(review, hypothesis)
        print(f"   📊 Validación review: {'✅ PASS' if review_validation['valid'] else '❌ FAIL'}")
        for issue in review_validation['issues']:
            print(f"      {issue}")
        results['review_validation'] = review_validation

        # Fase 5: Paper Generation
        print("\n📄 Fase 5: Generando paper...")
        paper = await coordinator.publish_async(hypothesis, "TBD", review, "No experimental data yet")
        print(f"   ✓ Paper generado: {len(paper)} caracteres")
        results['paper'] = paper

        # E2E adicional: ejecutar iteración real del BiologyLoop con herramientas
        try:
            if LOOPS_AVAILABLE and BiologyLoop is not None:
                print("\n▶️  E2E: BiologyLoop con corroboración de herramientas...")
                bio_loop = BiologyLoop()
                e2e = await bio_loop.run_genomics_discovery_iteration(top_n=2)
                avg_support = float(e2e.get('avg_support_score', 0.0) or 0.0)
                print(f"   🔬 avg_support_score (biology loop): {avg_support:.3f}")
                results['biology_loop_avg_support'] = avg_support
            else:
                print("   ⏭️ BiologyLoop E2E omitido: loops no disponibles")
        except (RuntimeError, ValueError, ConnectionError, TimeoutError) as _e:
            print(f"   ⚠️ BiologyLoop E2E no disponible: {_e}")

        print("\n✅ Biology Loop completado exitosamente")

    except (RuntimeError, ValueError, ConnectionError, TimeoutError) as e:
        print(f"\n❌ ERROR en Biology Loop: {e}")
        import traceback as _tb
        _tb.print_exc()
        results['error'] = str(e)

    return results


async def test_chemistry_loop():
    """Test del loop de química (molecular discovery)"""
    print("\n" + "="*80)
    print("⚗️ TEST: CHEMISTRY LOOP (Molecular Discovery)")
    print("="*80)

    coordinator = MultiAgentCoordinator()
    validator = LoopValidator()

    research_goal = """
    Design novel small-molecule inhibitors for SARS-CoV-2 main protease (Mpro).
    Hypothesis: Covalent inhibitors targeting Cys145 will show picomolar affinity
    and improved selectivity over host proteases.
    """

    results = {}

    try:
        print("\n📋 Fase 1: Planning...")
        plan = await coordinator.plan_async(research_goal)
        print(f"   ✓ Plan: {len(plan)} chars")
        results['plan'] = plan

        print("\n🧪 Fase 2: Generando hipótesis...")
        hypothesis = await coordinator.generate_bio_hypothesis_async(research_goal)
        print(f"   ✓ Hipótesis: {len(hypothesis)} chars")
        results['hypothesis'] = hypothesis

        hyp_validation = validator.validate_hypothesis(hypothesis, "chemistry")
        print(f"   📊 Validación: {'✅' if hyp_validation['valid'] else '❌'}")
        for issue in hyp_validation['issues']:
            print(f"      {issue}")
        results['hypothesis_validation'] = hyp_validation

        print("\n💻 Fase 3: Generando código...")
        code = await coordinator.design_and_code_async(hypothesis)
        print(f"   ✓ Código: {len(code.split(chr(10)))} líneas")
        results['code'] = code

        code_validation = validator.validate_code(code)
        print(f"   📊 Validación código: {'✅' if code_validation['valid'] else '❌'}")
        for issue in code_validation['issues']:
            print(f"      {issue}")
        results['code_validation'] = code_validation

        consistency = validator.check_baseline_consistency(hypothesis, code)
        print(f"\n   🔗 Consistencia: {consistency['consistency_score']:.1f}%")
        results['consistency'] = consistency

        print("\n📝 Fase 4: Peer review...")
        review = await coordinator.critical_review_async(hypothesis, code)
        print(f"   ✓ Review: {len(review)} chars")
        results['review'] = review

        review_validation = validator.validate_peer_review(review, hypothesis)
        print(f"   📊 Validación review: {'✅' if review_validation['valid'] else '❌'}")
        results['review_validation'] = review_validation

        # E2E adicional: ejecutar iteración real del ChemistryLoop con herramientas
        try:
            if LOOPS_AVAILABLE and ChemistryLoop is not None:
                print("\n▶️  E2E: ChemistryLoop con corroboración de herramientas...")
                chem_loop = ChemistryLoop()
                e2e = chem_loop.run_iteration(top_n=3)
                # Extraer soporte promedio si está disponible desde outcomes
                avg_support = float(e2e.get('summary', {}).get('avg_support_score', 0.0) or 0.0)
                print(f"   🔬 avg_support_score (chemistry loop): {avg_support:.3f}")
                results['chemistry_loop_avg_support'] = avg_support
            else:
                print("   ⏭️ ChemistryLoop E2E omitido: loops no disponibles")
        except (RuntimeError, ValueError, ConnectionError, TimeoutError) as _e:
            print(f"   ⚠️ ChemistryLoop E2E no disponible: {_e}")

        print("\n✅ Chemistry Loop completado")

    except (RuntimeError, ValueError, ConnectionError, TimeoutError) as e:
        print(f"\n❌ ERROR: {e}")
        results['error'] = str(e)

    return results


async def test_materials_loop():
    """Test del loop de materials science"""
    print("\n" + "="*80)
    print("🔩 TEST: MATERIALS LOOP (Materials Discovery)")
    print("="*80)

    coordinator = MultiAgentCoordinator()
    validator = LoopValidator()

    research_goal = """
    Discover high-entropy alloys for extreme temperature applications (>2000K).
    Hypothesis: Refractory multi-principal element alloys with HCP structure
    will exhibit superior creep resistance compared to conventional superalloys.
    """

    results = {}

    try:
        print("\n📋 Planning...")
        plan = await coordinator.plan_async(research_goal)
        results['plan'] = plan

        print("\n🧪 Hipótesis...")
        hypothesis = await coordinator.generate_bio_hypothesis_async(research_goal)
        results['hypothesis'] = hypothesis

        hyp_validation = validator.validate_hypothesis(hypothesis, "materials")
        print(f"   📊 Validación hipótesis: {'✅' if hyp_validation['valid'] else '❌'}")
        for issue in hyp_validation['issues']:
            print(f"      {issue}")
        results['hypothesis_validation'] = hyp_validation

        print("\n💻 Código...")
        code = await coordinator.design_and_code_async(hypothesis)
        results['code'] = code

        code_validation = validator.validate_code(code)
        print(f"   📊 Validación código: {'✅' if code_validation['valid'] else '❌'}")
        results['code_validation'] = code_validation

        consistency = validator.check_baseline_consistency(hypothesis, code)
        print(f"   🔗 Consistencia: {consistency['consistency_score']:.1f}%")
        results['consistency'] = consistency

        # E2E adicional: ejecutar iteración real del MaterialsLoop con herramientas
        try:
            if LOOPS_AVAILABLE and MaterialsLoop is not None:
                print("\n▶️  E2E: MaterialsLoop con corroboración de herramientas...")
                mat_loop = MaterialsLoop()
                e2e = mat_loop.run_iteration(iteration=1)
                avg_support = float(e2e.get('summary', {}).get('avg_support_score', 0.0) or 0.0)
                print(f"   🔬 avg_support_score (materials loop): {avg_support:.3f}")
                results['materials_loop_avg_support'] = avg_support
            else:
                print("   ⏭️ MaterialsLoop E2E omitido: loops no disponibles")
        except (RuntimeError, ValueError, ConnectionError, TimeoutError) as _e:
            print(f"   ⚠️ MaterialsLoop E2E no disponible: {_e}")

        print("\n✅ Materials Loop completado")

    except (RuntimeError, ValueError, ConnectionError, TimeoutError) as e:
        print(f"\n❌ ERROR: {e}")
        results['error'] = str(e)

    return results


async def test_quantum_loop():
    """Test del loop de quantum computing"""
    print("\n" + "="*80)
    print("⚛️ TEST: QUANTUM LOOP (Quantum Computing)")
    print("="*80)

    coordinator = MultiAgentCoordinator()
    validator = LoopValidator()

    research_goal = """
    Develop quantum error correction codes for topological qubits.
    Hypothesis: Surface code variants with non-Abelian anyons will achieve
    threshold error rates <0.1% for fault-tolerant quantum computation.
    """

    results = {}

    try:
        print("\n📋 Planning...")
        plan = await coordinator.plan_async(research_goal)
        results['plan'] = plan

        print("\n🧪 Hipótesis...")
        hypothesis = await coordinator.generate_bio_hypothesis_async(research_goal)
        results['hypothesis'] = hypothesis

        hyp_validation = validator.validate_hypothesis(hypothesis, "quantum")
        print(f"   📊 Validación: {'✅' if hyp_validation['valid'] else '❌'}")
        results['hypothesis_validation'] = hyp_validation

        print("\n💻 Código...")
        code = await coordinator.design_and_code_async(hypothesis)
        results['code'] = code

        code_validation = validator.validate_code(code)
        print(f"   📊 Validación código: {'✅' if code_validation['valid'] else '❌'}")
        results['code_validation'] = code_validation

        consistency = validator.check_baseline_consistency(hypothesis, code)
        print(f"   🔗 Consistencia: {consistency['consistency_score']:.1f}%")
        results['consistency'] = consistency

        print("\n✅ Quantum Loop completado")

    except (RuntimeError, ValueError, ConnectionError, TimeoutError) as e:
        print(f"\n❌ ERROR: {e}")
        results['error'] = str(e)

    return results


async def test_mathematics_loop():
    """Test del loop de matemáticas"""
    print("\n" + "="*80)
    print("📐 TEST: MATHEMATICS LOOP (Mathematical Conjectures)")
    print("="*80)

    coordinator = MultiAgentCoordinator()
    validator = LoopValidator()

    research_goal = """
    Investigate bounds for the Riemann zeta function on the critical line.
    Hypothesis: Using mollification techniques, we can prove that at least 42%
    of non-trivial zeros lie on Re(s)=1/2.
    """

    results = {}

    try:
        print("\n📋 Planning...")
        plan = await coordinator.plan_async(research_goal)
        results['plan'] = plan

        print("\n🧪 Hipótesis...")
        hypothesis = await coordinator.generate_bio_hypothesis_async(research_goal)
        results['hypothesis'] = hypothesis

        hyp_validation = validator.validate_hypothesis(hypothesis, "mathematics")
        print(f"   📊 Validación: {'✅' if hyp_validation['valid'] else '❌'}")
        results['hypothesis_validation'] = hyp_validation

        print("\n💻 Código...")
        code = await coordinator.design_and_code_async(hypothesis)
        results['code'] = code

        code_validation = validator.validate_code(code)
        print(f"   📊 Validación código: {'✅' if code_validation['valid'] else '❌'}")
        results['code_validation'] = code_validation

        consistency = validator.check_baseline_consistency(hypothesis, code)
        print(f"   🔗 Consistencia: {consistency['consistency_score']:.1f}%")
        results['consistency'] = consistency

        print("\n✅ Mathematics Loop completado")

    except (RuntimeError, ValueError, ConnectionError, TimeoutError) as e:
        print(f"\n❌ ERROR: {e}")
        results['error'] = str(e)

    return results


async def main():
    """Ejecuta todos los tests de loops autónomos"""
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "  🔬 AXIOM ATLAS - TEST COMPREHENSIVO DE LOOPS AUTÓNOMOS".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")

    start_time = datetime.now()

    all_results = {}

    # Ejecutar todos los loops
    loops = [
        ("biology", test_biology_loop),
        ("chemistry", test_chemistry_loop),
        ("materials", test_materials_loop),
        ("quantum", test_quantum_loop),
        ("mathematics", test_mathematics_loop)
    ]

    for loop_name, test_func in loops:
        try:
            results = await test_func()
            all_results[loop_name] = results
        except (RuntimeError, ValueError, ConnectionError, TimeoutError) as e:
            print(f"\n❌ Error crítico en {loop_name} loop: {e}")
            all_results[loop_name] = {"error": str(e)}

        # Pausa entre loops para no saturar API
    await asyncio.sleep(2)

    # Análisis global
    print("\n\n" + "="*80)
    print("📊 ANÁLISIS GLOBAL DE CALIDAD CIENTÍFICA")
    print("="*80)

    final_summary = {
        "timestamp": start_time.isoformat(),
        "total_loops_tested": len(loops),
        "results": {}
    }

    for loop_name, results in all_results.items():
        if 'error' in results:
            print(f"\n❌ {loop_name.upper()}: ERROR - {results['error']}")
            final_summary['results'][loop_name] = {"status": "error", "error": results['error']}
            continue

        # Calcular scores
        hyp_valid = results.get('hypothesis_validation', {}).get('valid', False)
        code_valid = results.get('code_validation', {}).get('valid', False)
        consistency_score = results.get('consistency', {}).get('consistency_score', 0)
        review_valid = results.get('review_validation', {}).get('valid', False)

        # Score global (promedio ponderado)
        global_score = (
            (30 if hyp_valid else 0)
            + (30 if code_valid else 0)
            + (consistency_score * 0.3)
            + (10 if review_valid else 0)
        )

        status = "✅ PASS" if global_score >= 70 else "⚠️ MARGINAL" if global_score >= 50 else "❌ FAIL"

        print(f"\n{status} {loop_name.upper()}: {global_score:.1f}/100")
        print(f"   Hipótesis: {'✅' if hyp_valid else '❌'}")
        print(f"   Código: {'✅' if code_valid else '❌'}")
        print(f"   Consistencia: {consistency_score:.1f}%")
        print(f"   Review: {'✅' if review_valid else '❌'}")

        final_summary['results'][loop_name] = {
            "status": "pass" if global_score >= 70 else "marginal" if global_score >= 50 else "fail",
            "global_score": global_score,
            "hypothesis_valid": hyp_valid,
            "code_valid": code_valid,
            "consistency_score": consistency_score,
            "review_valid": review_valid
    }

    # Guardar resultados
    output_file = Path("test_all_loops_results.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_summary, f, indent=2, ensure_ascii=False)

    print(f"\n\n✅ Resultados guardados en: {output_file}")

    # Estadísticas finales
    total_time = (datetime.now() - start_time).total_seconds()
    print(f"\n⏱️  Tiempo total: {total_time:.1f}s")

    passed = sum(1 for r in final_summary['results'].values() if r.get('status') == 'pass')
    print(f"📊 Loops aprobados: {passed}/{len(loops)}")

    avg_consistency = sum(r.get('consistency_score', 0) for r in final_summary['results'].values()) / len(loops)
    print(f"🔗 Consistencia promedio: {avg_consistency:.1f}%")

    return final_summary


if __name__ == "__main__":
    try:
        summary = asyncio.run(main())

        # Exit code basado en resultados
        failed = sum(1 for r in summary['results'].values() if r.get('status') == 'fail')
        sys.exit(1 if failed > 0 else 0)

    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrumpido por usuario")
        sys.exit(130)
    except (RuntimeError, ValueError, ConnectionError, TimeoutError) as e:
        print(f"\n\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
