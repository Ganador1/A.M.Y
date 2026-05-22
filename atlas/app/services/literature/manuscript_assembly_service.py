"""Manuscript Assembly Service (Stub)
Construcción modular de secciones de manuscrito científico.
"""
from __future__ import annotations
from typing import Dict, Any

class ManuscriptAssemblyService:
    def __init__(self):
        self.version = "v0"
        self.section_order = ["title", "abstract", "introduction", "methods", "results", "discussion", "conclusion"]

    def build_sections(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        out: Dict[str, str] = {}
        out["title"] = inputs.get("title", "Untitled Study")
        out["abstract"] = self._abstract(inputs)
        out["introduction"] = self._intro(inputs)
        out["methods"] = self._methods(inputs)
        out["results"] = self._results(inputs)
        out["discussion"] = self._discussion(inputs)
        out["conclusion"] = self._conclusion(inputs)
        return out

    def assemble_manuscript(self, inputs: Dict[str, Any]) -> str:
        sections = self.build_sections(inputs)
        return "\n\n".join(
            f"# {k.capitalize()}\n\n{sections[k]}" for k in self.section_order if k in sections
        )

    # --- internal simple builders ---
    def _abstract(self, inputs: Dict[str, Any]) -> str:
        return inputs.get("abstract", "Resumen pendiente.")

    def _intro(self, inputs: Dict[str, Any]) -> str:
        return inputs.get("introduction", "Introducción generada minimal.")

    def _methods(self, inputs: Dict[str, Any]) -> str:
        return inputs.get("methods", "Métodos: TBD")

    def _results(self, inputs: Dict[str, Any]) -> str:
        return inputs.get("results", "Resultados preliminares.")

    def _discussion(self, inputs: Dict[str, Any]) -> str:
        return inputs.get("discussion", "Discusión inicial.")

    def _conclusion(self, inputs: Dict[str, Any]) -> str:
        return inputs.get("conclusion", "Conclusiones provisionales.")

manuscript_assembly_service = ManuscriptAssemblyService()
