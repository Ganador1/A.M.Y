"""Exportador de resultados matemáticos a Markdown y LaTeX."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable

from app.domains.mathematics.services.mathematical_discovery_engine import InvestigationResult


def results_to_markdown(results: Iterable[InvestigationResult]) -> str:
    lines = ["# Informe de Descubrimientos Matemáticos\n", f"Generado: {datetime.utcnow().isoformat()}\n"]
    for r in results:
        lines.extend([
            f"## Conjetura: `{r.conjecture.statement}`\n",
            f"- ID: {r.conjecture.id}\n",
            f"- Dominio: {r.conjecture.domain}\n",
            f"- Estado: {r.status}\n",
            f"- Importancia: {r.importance}\n",
        ])
        if r.proof:
            lines.append("### Esbozo de Prueba\n\n```\n" + str(r.proof) + "\n```\n")
        if r.counterexample:
            lines.append("### Contraejemplo\n\n```\n" + str(r.counterexample) + "\n```\n")
    return "\n".join(lines)


def results_to_latex(results: Iterable[InvestigationResult]) -> str:
    body = ["% Informe de Descubrimientos", "\\section*{Descubrimientos Matemáticos}"]
    for r in results:
        body.extend([
            f"\\subsection*{{Conjetura: {r.conjecture.statement}}}",
            f"\\textbf{{ID}}: {r.conjecture.id}\\\\",
            f"\\textbf{{Dominio}}: {r.conjecture.domain}\\\\",
            f"\\textbf{{Estado}}: {r.status}\\\\",
            f"\\textbf{{Importancia}}: {r.importance}\\\\",
        ])
        if r.proof:
            body.extend([
                "\\paragraph{Prueba (resumen)}\\ ",
                f"\\begin{{verbatim}}\n{r.proof}\n\\end{{verbatim}}",
            ])
        if r.counterexample:
            body.extend([
                "\\paragraph{Contraejemplo}\\ ",
                f"\\begin{{verbatim}}\n{r.counterexample}\n\\end{{verbatim}}",
            ])
    return "\n".join(["\\documentclass{article}", "\\begin{document}"] + body + ["\\end{document}"])


class MathematicalExporter:
    """Compatibilidad para servicios que esperan un exportador orientado a objetos."""

    _FORMAT_MARKDOWN = {"md", "markdown"}
    _FORMAT_LATEX = {"tex", "latex"}

    def to_markdown(self, results: Iterable[InvestigationResult]) -> str:
        return results_to_markdown(results)

    def to_latex(self, results: Iterable[InvestigationResult]) -> str:
        return results_to_latex(results)

    def export(self, results: Iterable[InvestigationResult], export_format: str = "markdown") -> str:
        fmt = (export_format or "markdown").strip().lower()
        if fmt in self._FORMAT_MARKDOWN:
            return self.to_markdown(results)
        if fmt in self._FORMAT_LATEX:
            return self.to_latex(results)
        raise ValueError(f"Formato de exportación no soportado: {export_format}")


__all__ = ["MathematicalExporter", "results_to_markdown", "results_to_latex"]
