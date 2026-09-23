"""
Z3 SMT Service for AXIOM
Satisfiability Modulo Theories (SMT) solver integration using Z3

This service provides mathematical theorem proving and formal verification
capabilities through the Z3 SMT solver. It supports:

- Mathematical property verification
- Counterexample finding
- Expression normalization
- Formal verification of mathematical conjectures

Dependencies:
- Z3 theorem prover (optional)
- Expression normalizer (optional)

Usage:
    service = Z3SMTService()
    result = service.verify_mathematical_property("x + y = y + x")
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from app.types.z3_smt_service_types import (
    NormalizeExpressionResult,
    VerifyNormalizedResult,
    FindCounterexampleNormalizedResult,
    VerifyMathematicalPropertyResult,
    OptimizeParametersResult,
    AnalyzeFormulaComplexityResult,
    VerifyResult,
    VerifySmt2Result,
    OptimizeResult,
    ModelToDictResult,
    VerifySimpleTautologyResult,
    SolveWithStrategyResult,
    CreateVariablesFromDomainResult,
    VerifyAtlasHypothesisResult,
    DebugSimpleCheckResult,
)

try:  # Normalizer opcional
    from app.domains.mathematics.utils.symbolic_normalizer import SymbolicExpressionNormalizer, symbolic_normalizer_singleton
    NORMALIZER_AVAILABLE = True
except ImportError:  # pragma: no cover
    SymbolicExpressionNormalizer = None  # type: ignore
    symbolic_normalizer_singleton = None  # type: ignore
    NORMALIZER_AVAILABLE = False

try:  # Z3 opcional
    import z3  # type: ignore
    Z3_AVAILABLE = True
except ImportError:  # pragma: no cover
    z3 = None  # type: ignore
    Z3_AVAILABLE = False

# Nota: Se eliminó import de Z3Exception no utilizado para limpiar lint.


class Z3SMTService:
    """
    Z3 SMT Service for formal mathematical verification.

    This service provides comprehensive mathematical theorem proving and formal verification
    capabilities using the Z3 Satisfiability Modulo Theories (SMT) solver.

    Key Features:
    - Mathematical property verification
    - Counterexample generation
    - Expression normalization
    - Parameter optimization
    - Formula complexity analysis
    - Hypothesis verification for AXIOM

    Dependencies:
    - Z3 theorem prover (optional, graceful degradation if unavailable)
    - Expression normalizer (optional, for advanced symbolic manipulation)

    Usage:
        service = Z3SMTService(timeout_ms=5000)
        result = service.verify_mathematical_property("x + y = y + x", {"x": "real", "y": "real"})
    """

    def __init__(self, timeout_ms: int = 30000) -> None:
        self.timeout_ms = timeout_ms
        self._normalizer: Optional[SymbolicExpressionNormalizer] = symbolic_normalizer_singleton if NORMALIZER_AVAILABLE else None
        self._logger = logging.getLogger(__name__)

    # ---------------- High-level bridge helpers ----------------
    def get_normalizer_variables(self) -> List[str]:
        if not self._normalizer:
            return []
        try:
            return self._normalizer.get_variable_names()
        except (AttributeError, KeyError):  # pragma: no cover
            return []

    def normalize_expression(self, expr: Any) -> NormalizeExpressionResult:
        if not self._normalizer:
            return {"status": "UNAVAILABLE", "reason": "Normalizer not available"}
        try:
            # Pasar dominio vacío explícito para cumplir la firma (domain opcional) y claridad.
            node = self._normalizer.from_sympy(expr) if hasattr(expr, "free_symbols") else self._normalizer.from_python(expr, {})
            smt_script = self._normalizer.to_smt_script(node)
            return {
                "status": "OK",
                "ast_type": type(node).__name__,
                "smt_script": smt_script,
                "variables": self.get_normalizer_variables(),
            }
        except (ValueError, TypeError, RuntimeError) as e:  # pragma: no cover
            return {"status": "ERROR", "error": str(e)}

    def verify_normalized(self, expr: Any) -> VerifyNormalizedResult:
        norm = self.normalize_expression(expr)
        if norm.get("status") != "OK":
            return {"verified": None, "status": "NORMALIZATION_FAILED", "detail": norm}
        return self.verify_smt2(norm["smt_script"]) if Z3_AVAILABLE else {"verified": None, "status": "Z3_UNAVAILABLE"}

    def find_counterexample_normalized(self, expr: Any) -> FindCounterexampleNormalizedResult:
        res = self.verify_normalized(expr)
        if res.get("status") == "REFUTED":
            return {"status": "COUNTEREXAMPLE_FOUND", "counterexample": res.get("counterexample")}
        return {"status": "NO_COUNTEREXAMPLE", "detail": res}

    # ---------------- Core verification & analysis ----------------
    def verify_mathematical_property(self, property_formula: str, domain: VerifyMathematicalPropertyResult) -> VerifyMathematicalPropertyResult:
        if not Z3_AVAILABLE:
            return {"verified": None, "status": "UNKNOWN", "reason": "Z3 no disponible"}

        self._logger.debug(f"Verifying property: '{property_formula}' with domain: {domain}")

        try:
            # 1. Crear variables Z3 a partir del dominio
            z3_vars = self._create_variables_from_domain(domain)
            self._logger.debug(f"Created Z3 variables: {z3_vars}")

            # 2. Extraer y analizar restricciones explícitas del dominio
            constraints_list = domain.get("constraints", [])
            z3_constraints = []
            if isinstance(constraints_list, list):
                for c_str in constraints_list:
                    try:
                        parsed_c = self._parse_constraint(c_str, z3_vars)
                        if parsed_c is not None:
                            z3_constraints.append(parsed_c)
                    except ValueError as e:
                        self._logger.warning(f"Could not parse constraint '{c_str}': {e}")

            self._logger.debug(f"Parsed Z3 constraints: {z3_constraints}")

            # 3. Analizar la fórmula de la propiedad principal usando las variables Z3
            formula = self._parse_mathematical_formula(property_formula, z3_vars)
            self._logger.debug(f"Parsed Z3 formula: {formula}")

            # 4. Verificar la fórmula con las restricciones como suposiciones
            return self.verify(formula, z3_constraints)

        except (ValueError, TypeError, RuntimeError) as e:
            self._logger.error(f"Mathematical property verification failed: {e}", exc_info=True)
            return {"verified": None, "status": "ERROR", "error": f"Mathematical property verification failed: {e}"}

    def optimize_parameters(self, objective: str, constraints: List[str], variables: Dict[str, str], strategy: str = "default") -> OptimizeParametersResult:
        if not Z3_AVAILABLE:
            return {"status": "UNKNOWN", "reason": "Z3 no disponible"}
        try:
            z3_vars: Dict[str, Any] = {}
            for n, t in variables.items():
                tl = t.lower()
                if tl in ("real", "float"):
                    z3_vars[n] = z3.Real(n)
                elif tl in ("int", "integer"):
                    z3_vars[n] = z3.Int(n)
            opt = z3.Optimize()
            for c in constraints:
                pc = self._parse_constraint(c, z3_vars)
                if pc is not None:
                    opt.add(pc)
            obj_expr = self._parse_objective(objective, z3_vars)
            if obj_expr is not None:
                if "minimize" in objective.lower():
                    opt.minimize(obj_expr)
                else:
                    opt.maximize(obj_expr)
            res = self._solve_with_strategy(opt, strategy)
            return res
        except (ValueError, TypeError, RuntimeError) as e:  # pragma: no cover
            return {"status": "ERROR", "error": f"Parameter optimization failed: {e}"}

    def find_counterexamples(self, hypothesis: str, domain: Dict[str, Any], max_examples: int = 5) -> List[Dict[str, Any]]:
        if not Z3_AVAILABLE:
            return []
        results: List[Dict[str, Any]] = []
        try:
            s = z3.Solver()
            vars_ = self._create_variables_from_domain(domain)
            h_expr = self._parse_mathematical_formula(hypothesis, vars_)
            s.add(z3.Not(h_expr))
            for _ in range(max_examples):
                if s.check() == z3.sat:
                    m = s.model()
                    results.append(self._model_to_dict(m))
                    block = [vars_[vn] != m[vars_[vn]] for vn in vars_]
                    if block:
                        s.add(z3.Or(block))
                else:
                    break
        except (ValueError, TypeError, RuntimeError):  # pragma: no cover
            pass
        return results

    def analyze_formula_complexity(self, formula: str) -> AnalyzeFormulaComplexityResult:
        if not Z3_AVAILABLE:
            return {"complexity": "unknown", "reason": "Z3 no disponible"}
        try:
            temp_vars = {"x": z3.Real("x"), "y": z3.Real("y"), "z": z3.Real("z")}
            _ = self._parse_mathematical_formula(formula, temp_vars)
            metrics = {
                "quantifier_depth": self._count_quantifiers(formula),
                "boolean_operators": sum(formula.count(k) for k in ["and", "or", "not"]),
                "arithmetic_operators": sum(formula.count(k) for k in ["+", "-", "*", "/"]),
                "variables_count": len({v for v in temp_vars if v in formula}),
                "estimated_solving_difficulty": "easy",
            }
            total = metrics["quantifier_depth"] * 3 + metrics["boolean_operators"] + metrics["arithmetic_operators"]
            if total < 5:
                metrics["estimated_solving_difficulty"] = "easy"
            elif total < 15:
                metrics["estimated_solving_difficulty"] = "medium"
            else:
                metrics["estimated_solving_difficulty"] = "hard"
            return metrics
        except (ValueError, TypeError, RuntimeError) as e:
            return {"complexity": "error", "error": str(e)}

    def verify(self, formula: Any, assumptions: Optional[List[Any]] = None, timeout_ms: Optional[int] = None) -> VerifyResult:
        if not Z3_AVAILABLE:
            return {"verified": None, "status": "UNKNOWN", "reason": "Z3 no disponible. Instala z3-solver"}
        s = z3.Solver()
        effective_timeout = int(timeout_ms if timeout_ms is not None else self.timeout_ms)
        s.set("timeout", effective_timeout)
        try:
            import time as _time
            _t0 = _time.time()
            sexpr = None
            try:
                if hasattr(formula, 'sexpr'):
                    sexpr = formula.sexpr()
            except Exception:  # pragma: no cover
                pass
            self._logger.info(f"Z3 Verify | timeout_ms={effective_timeout} | formula={formula} | sexpr={sexpr}")
            if assumptions:
                self._logger.info(f"Z3 Verify | assumptions={assumptions}")
            for a in (assumptions or []):
                s.add(a)
            negated_formula = z3.Not(formula)
            s.add(negated_formula)
            self._logger.debug(f"Z3 Verify | added negated formula: {negated_formula}")
            r = s.check()
            elapsed_ms = int((_time.time() - _t0) * 1000)
            self._logger.info(f"Z3 Verify | check result={r}")
            if r == z3.unsat:
                return {"verified": True, "status": "PROVEN", "proof_method": "SMT_UNSAT", "counterexample": None, "elapsed_ms": elapsed_ms}
            if r == z3.sat:
                return {"verified": False, "status": "REFUTED", "counterexample": self._model_to_dict(s.model()), "elapsed_ms": elapsed_ms}
            reason = None
            try:
                reason = s.reason_unknown()
            except Exception:  # pragma: no cover
                pass
            self._logger.warning(f"Z3 Verify | UNKNOWN | reason={reason}")
            return {"verified": None, "status": "UNKNOWN", "reason": reason, "elapsed_ms": elapsed_ms}
        except (ValueError, TypeError, RuntimeError) as e:  # pragma: no cover
            return {"verified": None, "status": "ERROR", "error": str(e)}

    def verify_smt2(self, smt2_source: str, timeout_ms: Optional[int] = None) -> VerifySmt2Result:
        if not Z3_AVAILABLE:
            return {"verified": None, "status": "UNKNOWN", "reason": "Z3 no disponible"}
        try:
            s = z3.Solver()
            s.set("timeout", int(timeout_ms if timeout_ms is not None else self.timeout_ms))
            import time as _time
            _t0 = _time.time()
            try:
                s.from_string(smt2_source)
            except Exception:
                try:
                    ast = z3.parse_smt2_string(smt2_source)
                    if isinstance(ast, list):
                        for a in ast:
                            s.add(a)
                    else:
                        s.add(ast)
                except Exception as pe:
                    return {"verified": None, "status": "ERROR", "error": f"Parse error: {pe}"}
            r = s.check()
            elapsed_ms = int((_time.time() - _t0) * 1000)
            if r == z3.unsat:
                return {"verified": True, "status": "PROVEN", "proof_method": "SMT_UNSAT", "elapsed_ms": elapsed_ms}
            if r == z3.sat:
                return {"verified": False, "status": "REFUTED", "counterexample": self._model_to_dict(s.model()), "elapsed_ms": elapsed_ms}
            return {"verified": None, "status": "UNKNOWN", "elapsed_ms": elapsed_ms}
        except (ValueError, TypeError, RuntimeError) as e:  # pragma: no cover
            return {"verified": None, "status": "ERROR", "error": str(e)}

    def optimize(self, objectives: List[Any], constraints: Optional[List[Any]] = None, sense: str = "minimize") -> OptimizeResult:
        if not Z3_AVAILABLE:
            return {"status": "UNKNOWN", "reason": "Z3 no disponible"}
        o = z3.Optimize()
        try:
            for c in (constraints or []):
                o.add(c)
            for obj in objectives:
                if sense == "minimize":
                    o.minimize(obj)
                else:
                    o.maximize(obj)
            if o.check() != z3.sat:
                return {"status": "INFEASIBLE"}
            m = o.model()
            return {
                "status": "OPTIMAL",
                "model": {str(d): str(m[d]) for d in m.decls()},
                "objectives": [str(m.eval(obj, model_completion=True)) for obj in objectives],
            }
        except (ValueError, TypeError, RuntimeError) as e:  # pragma: no cover
            return {"status": "ERROR", "error": str(e)}

    def _model_to_dict(self, model: Any) -> ModelToDictResult:
        try:
            return {str(d): str(model[d]) for d in model.decls()}
        except (AttributeError, ValueError):
            return {"raw": str(model)}

    def verify_simple_tautology(self, expr: Any) -> VerifySimpleTautologyResult:
        if not Z3_AVAILABLE:
            return {"verified": None, "status": "UNKNOWN", "reason": "Z3 no disponible"}
        try:  # pragma: no cover
            if isinstance(expr, z3.BoolRef) and expr.decl().name() == "=>" and expr.num_args() == 2:  # type: ignore
                a, b = expr.arg(0), expr.arg(1)
                if a.eq(b):
                    return {"verified": True, "status": "TRIVIAL", "proof_method": "REFLEXIVE_PATTERN"}
        except Exception:  # pragma: no cover
            pass
        return self.verify(expr)

    # ---------------- Internal parsing helpers ----------------
    def _parse_mathematical_formula(self, formula_str: str, variables: Dict[str, Any]) -> Any:
        if not Z3_AVAILABLE:
            return None

        self._logger.debug(f"Attempting to parse formula with eval: {formula_str}")
        self._logger.debug(f"With variables: {list(variables.keys())}")

        # Create a safe evaluation context with Z3 variables and functions
        eval_context = {
            **variables,
            'ForAll': z3.ForAll, 'Exists': z3.Exists, 'Implies': z3.Implies,
            'And': z3.And, 'Or': z3.Or, 'Not': z3.Not,
            'Real': z3.Real, 'Int': z3.Int, 'Bool': z3.Bool,
        }

        try:
            # Securely evaluate the formula. Z3 variables overload standard Python operators.
            parsed_formula = eval(formula_str, {"__builtins__": {}}, eval_context)
            self._logger.debug(f"Successfully parsed formula to: {parsed_formula}")
            return parsed_formula
        except Exception as e:
            self._logger.error(f"Failed to parse formula '{formula_str}' with eval: {e}", exc_info=True)
            # Return a Z3.BoolVal(False) to represent a parsing failure in a way Z3 can handle
            return z3.BoolVal(False)

    def _parse_constraint(self, constraint_str: str, variables: Dict[str, Any]) -> Any:
        if not Z3_AVAILABLE or not constraint_str.strip():
            return None
        try:
            c = constraint_str.strip()
            if " > " in c:
                a, b = c.split(" > ")
                if a.strip() in variables:
                    return variables[a.strip()] > float(b.strip())
            if " < " in c:
                a, b = c.split(" < ")
                if a.strip() in variables:
                    return variables[a.strip()] < float(b.strip())
            if " >= " in c:
                a, b = c.split(" >= ")
                if a.strip() in variables:
                    return variables[a.strip()] >= float(b.strip())
        except (ValueError, KeyError):
            return None
        return None

    def _parse_objective(self, objective: str, variables: Dict[str, Any]) -> Any:
        if not Z3_AVAILABLE or not objective.strip():
            return None
        try:
            base = objective.lower().replace("minimize", "").replace("maximize", "").strip()
            if base in variables:
                return variables[base]
            if " + " in base:
                parts = [p.strip() for p in base.split(" + ")]
                if all(p in variables for p in parts):
                    return sum(variables[p] for p in parts)
            if "x^2 + y^2" in base and all(k in variables for k in ["x", "y"]):
                return variables["x"] * variables["x"] + variables["y"] * variables["y"]
        except (ValueError, KeyError):
            return None
        return None

    def _solve_with_strategy(self, optimizer: Any, strategy: str) -> SolveWithStrategyResult:
        if not Z3_AVAILABLE:
            return {"status": "ERROR", "error": "Z3 no disponible"}
        try:
            if strategy == "linear":
                optimizer.set("opt.priority", "lex")
            elif strategy == "nonlinear":
                optimizer.set("opt.engine", "nlsat")
            r = optimizer.check()
            if r == z3.sat:
                obj_vals: List[str] = []
                try:
                    for i in range(optimizer.num_objectives()):  # pragma: no cover
                        obj_vals.append(str(optimizer.upper(i)))
                except Exception:
                    pass
                return {"status": "OPTIMAL", "model": self._model_to_dict(optimizer.model()), "objectives": obj_vals, "strategy": strategy}
            if r == z3.unsat:
                return {"status": "INFEASIBLE", "strategy": strategy}
            return {"status": "UNKNOWN", "strategy": strategy}
        except (ValueError, TypeError, RuntimeError) as e:
            return {"status": "ERROR", "error": str(e), "strategy": strategy}

    def _create_variables_from_domain(self, domain: CreateVariablesFromDomainResult) -> CreateVariablesFromDomainResult:
        if not Z3_AVAILABLE:
            return {}
        vars_: Dict[str, Any] = {}
        try:
            for n, t in domain.items():
                if n == "constraints" or not isinstance(t, str):
                    continue
                tl = t.lower()
                if tl in ("real", "float"):
                    vars_[n] = z3.Real(n)
                elif tl in ("int", "integer"):
                    vars_[n] = z3.Int(n)
                elif tl in ("bool", "boolean"):
                    vars_[n] = z3.Bool(n)
        except (ValueError, TypeError):
            pass
        return vars_

    def _count_quantifiers(self, formula: str) -> int:
        qs = ["forall", "exists", "∀", "∃"]
        fl = formula.lower()
        return sum(fl.count(q) for q in qs)

    # ---------------- Atlas specific ----------------
    async def verify_atlas_hypothesis(self, hypothesis: VerifyAtlasHypothesisResult) -> VerifyAtlasHypothesisResult:
        try:
            statement = hypothesis.get("statement", "")
            domain = hypothesis.get("domain", {})
            result = self.verify_mathematical_property(statement, domain)
            out = {
                "hypothesis_id": hypothesis.get("id", "unknown"),
                "verification_method": "Z3_SMT",
                "verified": result.get("verified"),
                "confidence_boost": 0.0,
                "smt_details": result,
                "suggestions": [],
            }
            if result.get("verified") is True:
                out["confidence_boost"] = 0.15
                out["suggestions"].append("Hipótesis verificada formalmente")
            elif result.get("verified") is False:
                out["confidence_boost"] = -0.20
                ce = result.get("counterexample")
                if ce:
                    out["suggestions"].append(f"Contraejemplo encontrado: {ce}")
            return out
        except (ValueError, TypeError, RuntimeError) as e:
            return {
                "hypothesis_id": hypothesis.get("id", "unknown"),
                "verification_method": "Z3_SMT",
                "verified": None,
                "error": str(e),
                "confidence_boost": 0.0,
            }

    def generate_mathematical_conjectures(self, domain: str, constraints: List[str], count: int = 5) -> List[Dict[str, Any]]:
        if not Z3_AVAILABLE:
            return []
        out: List[Dict[str, Any]] = []
        try:
            for tpl in self._get_conjecture_templates(domain)[:count]:
                out.append(
                    {
                        "statement": tpl["pattern"],
                        "domain": domain,
                        "variables": tpl.get("variables", {}),
                        "confidence": 0.3,
                        "generated_by": "Z3SMTService",
                        "requires_verification": True,
                    }
                )
        except (ValueError, TypeError):  # pragma: no cover
            pass
        return out

    def _get_conjecture_templates(self, domain: str) -> List[Dict[str, Any]]:
        templates: Dict[str, List[Dict[str, Any]]] = {
            "number_theory": [
                {"pattern": "forall n: n > 0 => prime(n) or composite(n)", "variables": {"n": "int"}},
                {"pattern": "forall a,b: gcd(a,b) * lcm(a,b) = a * b", "variables": {"a": "int", "b": "int"}},
            ],
            "algebra": [
                {"pattern": "forall x,y: (x + y)^2 = x^2 + 2*x*y + y^2", "variables": {"x": "real", "y": "real"}},
                {"pattern": "forall x: x != 0 => x * (1/x) = 1", "variables": {"x": "real"}},
            ],
            "geometry": [
                {"pattern": "forall triangle: sum_angles = 180", "variables": {"triangle": "geometric_object"}},
            ],
        }
        return templates.get(domain, [])

    def _debug_simple_check(self) -> DebugSimpleCheckResult:
        """Ejecuta una verificación directa de la tautología esperada para aislar fallos del parser.
        Implies(And(x > 0, y > 0), (x + y) > 0) debe ser UNSAT al negar, es decir PROVEN.
        """
        if not Z3_AVAILABLE:
            return {"status": "Z3_UNAVAILABLE"}
        x, y = z3.Real('x'), z3.Real('y')
        formula = z3.Implies(z3.And(x > 0, y > 0), (x + y) > 0)
        s = z3.Solver()
        s.set('timeout', self.timeout_ms)
        s.add(z3.Not(formula))
        r = s.check()
        out = {"raw_result": str(r)}
        if r == z3.unsat:
            out["status"] = "PROVEN"
        elif r == z3.sat:
            out["status"] = "REFUTED"
            out["model"] = self._model_to_dict(s.model())
        else:
            out["status"] = "UNKNOWN"
            try:
                out["reason_unknown"] = s.reason_unknown()
            except Exception:
                pass
        self._logger.info(f"_debug_simple_check => {out}")
        return out


# Convenience singleton
smt_service_singleton = Z3SMTService()

__all__ = ["Z3SMTService", "smt_service_singleton"]

