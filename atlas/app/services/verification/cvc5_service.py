"""
CVC5 SMT Service for AXIOM Meta/Atlas
- Verificación SMT complementaria a Z3 usando CVC5
- Especializado en teorías específicas: strings, sets, bags, floating-point
- Soporte para SMT-LIB 2.6 completo
- Integración con pipeline de verificación formal de Atlas
"""

from __future__ import annotations
import aiofiles

import asyncio
import os
import tempfile
import subprocess
from typing import Any, Dict, List, Optional
import json
from app.exceptions.domain.biology import BiologyError
from app.types.cvc5_service_types import (
    VerifyStringConstraintsResult,
    VerifySetTheoryResult,
    VerifyFloatingPointResult,
    VerifyAtlasHypothesisAdvancedResult,
    CompareWithZ3Result,
    VerifyWithPythonBindingsResult,
    VerifyWithCliResult,
    ParseResultResult,
)

# CVC5 availability check
CVC5_AVAILABLE = None

def _check_cvc5():
    """Check if CVC5 is available"""
    global CVC5_AVAILABLE
    if CVC5_AVAILABLE is None:
        try:
            # Try Python bindings first
            import cvc5  # noqa: F401
            CVC5_AVAILABLE = "python"
            return True
        except ImportError:
            try:
                # Try command-line version
                result = subprocess.run(['cvc5', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                CVC5_AVAILABLE = "cli" if result.returncode == 0 else False
                return CVC5_AVAILABLE != False
            except (FileNotFoundError, subprocess.TimeoutExpired):
                CVC5_AVAILABLE = False
                return False
    return CVC5_AVAILABLE != False


class CVC5Service:
    """
    Servicio de verificación SMT usando CVC5
    Complementa Z3 con teorías específicas y mayor expresividad
    """
    
    def __init__(self, timeout_ms: int = 60000):
        self.timeout_ms = timeout_ms
        self.cvc5_available = _check_cvc5()
        self.cvc5_mode = CVC5_AVAILABLE
        self.temp_dir = tempfile.mkdtemp(prefix="cvc5_axiom_")
        
        # Configuraciones especializadas por teoría
        self.theory_configs = {
            "strings": {"strings-exp": True, "strings-fmf": True},
            "sets": {"sets-ext": True},
            "fp": {"fp-exp": True},  # floating-point
            "arrays": {"array-eager-index": True},
            "datatypes": {"dt-rewrite-error-sel": True},
            "quantifiers": {"finite-model-find": True, "fmf-inst-engine": True}
        }
        
    def __del__(self):
        """Limpia archivos temporales de forma segura durante shutdown"""
        try:
            import shutil
            import os
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            # Capturar todas las excepciones incluyendo ImportError durante shutdown
            pass

    # --- Core SMT Verification ---
    async def verify(self, formula: str, theory: str = "QF_LIA", 
                    logic: Optional[str] = None) -> Dict[str, Any]:
        """
        Verifica una fórmula usando CVC5
        
        Args:
            formula: Fórmula en formato SMT-LIB2
            theory: Teoría SMT (QF_LIA, QF_S, QF_ABV, etc.)
            logic: Lógica específica (opcional)
        """
        if not self.cvc5_available:
            return {
                "verified": None,
                "status": "UNKNOWN", 
                "reason": "CVC5 no disponible. Instala: pip install cvc5"
            }
        
        try:
            # Generar SMT-LIB2 completo
            smt_script = self._build_smt_script(formula, theory, logic)
            
            if self.cvc5_mode == "python":
                result = await self._verify_with_python_bindings(smt_script, theory)
            else:
                result = await self._verify_with_cli(smt_script)
            
            return self._parse_result(result)
            
        except BiologyError as e:
            return {
                "verified": None,
                "status": "ERROR",
                "error": f"CVC5 verification failed: {str(e)}"
            }

    async def verify_string_constraints(self, constraints: List[VerifyStringConstraintsResult]) -> VerifyStringConstraintsResult:
        """
        Verifica constraints de strings - especialidad de CVC5
        
        Args:
            constraints: Lista de constraints sobre strings
            Ejemplo: [{"var": "x", "type": "string", "constraint": "contains", "value": "abc"}]
        """
        if not self.cvc5_available:
            return {"verified": None, "reason": "CVC5 no disponible"}
            
        try:
            # Construir script SMT-LIB2 para strings
            smt_script = "(set-logic QF_S)\n"
            
            # Declarar variables
            variables = set()
            for constraint in constraints:
                var = constraint.get("var", "x")
                if var not in variables:
                    smt_script += f"(declare-const {var} String)\n"
                    variables.add(var)
            
            # Agregar constraints
            for constraint in constraints:
                var = constraint.get("var", "x")
                constraint_type = constraint.get("constraint", "")
                value = constraint.get("value", "")
                
                if constraint_type == "contains":
                    smt_script += f"(assert (str.contains {var} \"{value}\"))\n"
                elif constraint_type == "length":
                    length = int(value)
                    smt_script += f"(assert (= (str.len {var}) {length}))\n"
                elif constraint_type == "prefix":
                    smt_script += f"(assert (str.prefixof \"{value}\" {var}))\n"
                elif constraint_type == "suffix":
                    smt_script += f"(assert (str.suffixof \"{value}\" {var}))\n"
                elif constraint_type == "regex":
                    smt_script += f"(assert (str.in_re {var} (re.++ (str.to_re \"{value}\"))))\n"
            
            smt_script += "(check-sat)\n(get-model)\n"
            
            # Ejecutar con CVC5
            if self.cvc5_mode == "python":
                result = await self._verify_with_python_bindings(smt_script, "strings")
            else:
                result = await self._verify_with_cli(smt_script)
                
            parsed = self._parse_result(result)
            
            # Extraer valores de strings del modelo
            if parsed.get("status") == "SAT" and "model" in result:
                string_values = self._extract_string_values(result["output"])
                parsed["string_assignments"] = string_values
            
            return parsed
            
        except BiologyError as e:
            return {
                "verified": None,
                "status": "ERROR", 
                "error": f"String constraint verification failed: {str(e)}"
            }

    async def verify_set_theory(self, set_operations: List[VerifySetTheoryResult]) -> VerifySetTheoryResult:
        """
        Verifica propiedades de teoría de conjuntos
        """
        if not self.cvc5_available:
            return {"verified": None, "reason": "CVC5 no disponible"}
            
        try:
            smt_script = "(set-logic QF_S)\n"  # Sets theory
            
            # Declarar conjuntos
            sets_declared = set()
            for op in set_operations:
                for set_name in [op.get("set1", ""), op.get("set2", ""), op.get("result", "")]:
                    if set_name and set_name not in sets_declared:
                        smt_script += f"(declare-const {set_name} (Set Int))\n"
                        sets_declared.add(set_name)
            
            # Agregar operaciones
            for op in set_operations:
                operation = op.get("operation", "")
                set1 = op.get("set1", "A")
                set2 = op.get("set2", "B")
                result = op.get("result", "C")
                
                if operation == "union":
                    smt_script += f"(assert (= {result} (set.union {set1} {set2})))\n"
                elif operation == "intersection":
                    smt_script += f"(assert (= {result} (set.inter {set1} {set2})))\n"
                elif operation == "difference":
                    smt_script += f"(assert (= {result} (set.minus {set1} {set2})))\n"
                elif operation == "subset":
                    smt_script += f"(assert (set.subset {set1} {set2}))\n"
                elif operation == "member":
                    element = op.get("element", 0)
                    smt_script += f"(assert (set.member {element} {set1}))\n"
            
            smt_script += "(check-sat)\n(get-model)\n"
            
            if self.cvc5_mode == "python":
                result = await self._verify_with_python_bindings(smt_script, "sets")
            else:
                result = await self._verify_with_cli(smt_script)
                
            return self._parse_result(result)
            
        except BiologyError as e:
            return {
                "verified": None,
                "status": "ERROR",
                "error": f"Set theory verification failed: {str(e)}"
            }

    async def verify_floating_point(self, fp_constraints: List[VerifyFloatingPointResult]) -> VerifyFloatingPointResult:
        """
        Verifica propiedades de punto flotante - fortaleza de CVC5
        """
        if not self.cvc5_available:
            return {"verified": None, "reason": "CVC5 no disponible"}
            
        try:
            smt_script = "(set-logic QF_FP)\n"
            
            # Declarar variables de punto flotante
            fp_vars = set()
            for constraint in fp_constraints:
                var = constraint.get("var", "x")
                if var not in fp_vars:
                    # IEEE 754 single precision por defecto
                    exp_bits = constraint.get("exp_bits", 8)
                    sig_bits = constraint.get("sig_bits", 24)
                    smt_script += f"(declare-const {var} (_ FloatingPoint {exp_bits} {sig_bits}))\n"
                    fp_vars.add(var)
            
            # Agregar constraints de FP
            for constraint in fp_constraints:
                var = constraint.get("var", "x")
                constraint_type = constraint.get("constraint", "")
                value = constraint.get("value", "0.0")
                
                if constraint_type == "greater":
                    fp_value = f"((_ to_fp 8 24) RNE {value})"
                    smt_script += f"(assert (fp.gt {var} {fp_value}))\n"
                elif constraint_type == "equal":
                    fp_value = f"((_ to_fp 8 24) RNE {value})"
                    smt_script += f"(assert (fp.eq {var} {fp_value}))\n"
                elif constraint_type == "is_normal":
                    smt_script += f"(assert (fp.isNormal {var}))\n"
                elif constraint_type == "is_nan":
                    smt_script += f"(assert (fp.isNaN {var}))\n"
                elif constraint_type == "is_infinite":
                    smt_script += f"(assert (fp.isInfinite {var}))\n"
            
            smt_script += "(check-sat)\n(get-model)\n"
            
            if self.cvc5_mode == "python":
                result = await self._verify_with_python_bindings(smt_script, "fp")
            else:
                result = await self._verify_with_cli(smt_script)
                
            return self._parse_result(result)
            
        except BiologyError as e:
            return {
                "verified": None,
                "status": "ERROR",
                "error": f"Floating-point verification failed: {str(e)}"
            }

    # --- Advanced Atlas Integration ---
    async def verify_atlas_hypothesis_advanced(self, hypothesis: VerifyAtlasHypothesisAdvancedResult) -> VerifyAtlasHypothesisAdvancedResult:
        """
        Verificación avanzada de hipótesis Atlas usando teorías específicas de CVC5
        """
        try:
            domain = hypothesis.get("domain", "general")
            statement = hypothesis.get("statement", "")
            
            # Router por dominio especializado
            if "string" in domain.lower() or "text" in domain.lower():
                # Convertir a constraints de strings
                string_constraints = self._extract_string_constraints(statement)
                result = await self.verify_string_constraints(string_constraints)
                
            elif "set" in domain.lower() or "collection" in domain.lower():
                # Convertir a operaciones de conjuntos
                set_ops = self._extract_set_operations(statement)
                result = await self.verify_set_theory(set_ops)
                
            elif "floating" in domain.lower() or "numerical" in domain.lower():
                # Convertir a constraints FP
                fp_constraints = self._extract_fp_constraints(statement)
                result = await self.verify_floating_point(fp_constraints)
                
            else:
                # Verificación general SMT-LIB2
                result = await self.verify(statement)
            
            # Adaptar resultado para Atlas
            atlas_result = {
                "hypothesis_id": hypothesis.get("id", "unknown"),
                "verification_method": "CVC5_SMT",
                "verified": result.get("verified"),
                "confidence_boost": 0.0,
                "cvc5_details": result,
                "specialized_theory": domain
            }
            
            # Boost de confianza por verificación CVC5
            if result.get("status") == "SAT":
                atlas_result["confidence_boost"] = 0.12
            elif result.get("status") == "UNSAT":
                atlas_result["confidence_boost"] = -0.15
            
            return atlas_result
            
        except BiologyError as e:
            return {
                "hypothesis_id": hypothesis.get("id", "unknown"),
                "verification_method": "CVC5_SMT",
                "verified": None,
                "error": str(e)
            }

    async def compare_with_z3(self, formula: str, theory: str = "QF_LIA") -> CompareWithZ3Result:
        """
        Compara resultados entre CVC5 y Z3 para validación cruzada
        """
        try:
            # Resultado CVC5
            cvc5_result = await self.verify(formula, theory)
            
            # Intentar Z3 para comparación (si está disponible)
            z3_result = None
            try:
                from app.services.theorem_proving.z3_smt_service import Z3SMTService
                z3_service = Z3SMTService()
                z3_result = z3_service.verify_smt2(formula)
            except BiologyError:
                z3_result = {"status": "UNAVAILABLE"}
            
            comparison = {
                "cvc5": cvc5_result,
                "z3": z3_result,
                "agreement": None,
                "recommendation": ""
            }
            
            # Analizar concordancia
            cvc5_status = cvc5_result.get("status", "UNKNOWN")
            z3_status = z3_result.get("status", "UNKNOWN")
            
            if cvc5_status == z3_status:
                comparison["agreement"] = "AGREE"
                comparison["recommendation"] = "Both solvers agree"
            elif "UNAVAILABLE" in [cvc5_status, z3_status]:
                comparison["agreement"] = "INCOMPLETE"
                comparison["recommendation"] = "Only one solver available"
            else:
                comparison["agreement"] = "DISAGREE"
                comparison["recommendation"] = "Solvers disagree - investigate further"
            
            return comparison
            
        except BiologyError as e:
            return {"error": f"Comparison failed: {str(e)}"}

    # --- Helper Methods ---
    def _build_smt_script(self, formula: str, theory: str, logic: Optional[str]) -> str:
        """Construye script SMT-LIB2 completo"""
        script = ""
        
        # Set logic
        if logic:
            script += f"(set-logic {logic})\n"
        else:
            script += f"(set-logic {theory})\n"
        
        # Configuraciones específicas por teoría
        if theory in self.theory_configs:
            for option, value in self.theory_configs[theory].items():
                script += f"(set-option :{option} {str(value).lower()})\n"
        
        # Formula (asume que ya está en formato SMT-LIB2)
        if not formula.strip().startswith("("):
            # Formula simple - wrap en assert
            script += f"(assert {formula})\n"
        else:
            script += formula + "\n"
        
        script += "(check-sat)\n"
        
        return script

    async def _verify_with_python_bindings(self, smt_script: str, theory: str) -> VerifyWithPythonBindingsResult:
        """Verifica usando bindings Python de CVC5"""
        try:
            import cvc5
            from cvc5 import pythonic as pycvc5
            
            solver = pycvc5.Solver()
            
            # Configurar teoría
            if theory == "strings":
                solver.setOption("strings-exp", "true")
            elif theory == "sets":
                solver.setOption("sets-ext", "true")
            elif theory == "fp":
                solver.setOption("fp-exp", "true")
            
            # Parse y ejecutar script
            solver.setOption("incremental", "false")
            result = solver.checkSatFromString(smt_script)
            
            output_dict = {
                "status": str(result),
                "output": smt_script,
                "method": "python_bindings"
            }
            
            # Si es SAT, obtener modelo
            if result == cvc5.Result.SAT:
                try:
                    model = solver.getModel()
                    output_dict["model"] = str(model)
                except BiologyError:
                    pass
            
            return output_dict
            
        except BiologyError as e:
            return {
                "status": "ERROR",
                "error": f"Python bindings failed: {str(e)}",
                "method": "python_bindings"
            }

    async def _verify_with_cli(self, smt_script: str) -> VerifyWithCliResult:
        """Verifica usando CVC5 CLI"""
        try:
            # Crear archivo temporal
            temp_file = os.path.join(self.temp_dir, f"cvc5_script_{os.getpid()}.smt2")
            
            with aiofiles.aiofiles.open(temp_file, 'w') as f:
                f.write(smt_script)
            
            # Ejecutar CVC5
            proc = await asyncio.create_subprocess_exec(
                'cvc5', '--produce-models', temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=self.timeout_ms / 1000
                )
                
                # Limpiar archivo temporal
                try:
                    os.remove(temp_file)
                except BiologyError:
                    pass
                
                output = stdout.decode('utf-8').strip()
                error = stderr.decode('utf-8').strip()
                
                return {
                    "status": output.split('\n')[0] if output else "ERROR",
                    "output": output,
                    "stderr": error,
                    "returncode": proc.returncode,
                    "method": "cli"
                }
                
            except asyncio.TimeoutError:
                proc.kill()
                return {
                    "status": "TIMEOUT",
                    "error": f"CVC5 timeout ({self.timeout_ms}ms)",
                    "method": "cli"
                }
                
        except BiologyError as e:
            return {
                "status": "ERROR",
                "error": f"CLI execution failed: {str(e)}",
                "method": "cli"
            }

    def _parse_result(self, result: ParseResultResult) -> ParseResultResult:
        """Parse resultado de CVC5 a formato estándar"""
        status = result.get("status", "UNKNOWN").upper()
        
        if status in ["SAT", "SATISFIABLE"]:
            return {
                "verified": False,  # SAT significa que la negación es satisfacible
                "status": "SAT",
                "satisfiable": True,
                "model": result.get("model"),
                "raw_result": result
            }
        elif status in ["UNSAT", "UNSATISFIABLE"]:
            return {
                "verified": True,  # UNSAT significa que la fórmula es válida
                "status": "UNSAT", 
                "satisfiable": False,
                "raw_result": result
            }
        else:
            return {
                "verified": None,
                "status": "UNKNOWN",
                "error": result.get("error"),
                "raw_result": result
            }

    def _extract_string_constraints(self, statement: str) -> List[Dict[str, Any]]:
        """Extrae constraints de strings de una declaración"""
        # Implementación básica - en producción sería más sofisticada
        constraints = []
        
        if "contains" in statement.lower():
            constraints.append({
                "var": "x",
                "type": "string", 
                "constraint": "contains",
                "value": "abc"  # Placeholder
            })
        
        if "length" in statement.lower():
            constraints.append({
                "var": "x",
                "type": "string",
                "constraint": "length", 
                "value": "5"  # Placeholder
            })
        
        return constraints

    def _extract_set_operations(self, statement: str) -> List[Dict[str, Any]]:
        """Extrae operaciones de conjuntos de una declaración"""
        operations = []
        
        if "union" in statement.lower():
            operations.append({
                "operation": "union",
                "set1": "A",
                "set2": "B", 
                "result": "C"
            })
        
        if "intersection" in statement.lower():
            operations.append({
                "operation": "intersection",
                "set1": "A",
                "set2": "B",
                "result": "C"
            })
        
        return operations

    def _extract_fp_constraints(self, statement: str) -> List[Dict[str, Any]]:
        """Extrae constraints de punto flotante"""
        constraints = []
        
        if ">" in statement:
            constraints.append({
                "var": "x",
                "constraint": "greater",
                "value": "0.0"
            })
        
        if "nan" in statement.lower():
            constraints.append({
                "var": "x", 
                "constraint": "is_nan",
                "value": ""
            })
        
        return constraints

    def _extract_string_values(self, output: str) -> Dict[str, str]:
        """Extrae valores de strings del output del modelo"""
        values = {}
        lines = output.split('\n')
        
        for line in lines:
            if '(define-fun' in line and 'String' in line:
                # Parse línea de definición de string
                # Formato: (define-fun x () String "valor")
                try:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        var_name = parts[1]
                        string_value = ' '.join(parts[4:]).strip('")')
                        values[var_name] = string_value
                except BiologyError:
                    continue
        
        return values
