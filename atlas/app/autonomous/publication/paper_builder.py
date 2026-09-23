"""Generador de mini-papers Markdown/LaTeX para el Agente 3.

Este módulo construye una representación estructurada de un "mini-paper" a partir de
artefactos producidos por los loops autónomos (conjeturas, bosquejos de prueba,
planes experimentales, métricas y análisis de novedad/dificultad).

API mínima inicial (se ampliará):

build_paper(metadata: dict, sections: dict, artifacts: dict) -> dict
    Retorna un diccionario estructurado con claves: title, authors, sections (ordenadas),
    artifacts (referencias), y una función auxiliar para render a Markdown.

Riesgos / Futuras extensiones:
    - Plantillas parametrizables (Jinja2) para LaTeX.
    - Gestión de referencias bibliográficas.
    - Integración con export_manager para persistencia y versionado.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any


@dataclass
class PaperSection:
    key: str
    title: str
    content: str
    order: int


@dataclass
class PaperArtifactRef:
    name: str
    path: str
    kind: str  # e.g. 'figure', 'table', 'dataset', 'model'


@dataclass
class MiniPaper:
    title: str
    authors: List[str]
    created_at: str
    sections: List[PaperSection] = field(default_factory=list)
    artifacts: List[PaperArtifactRef] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", "", f"_Autores_: {', '.join(self.authors)}", "", f"_Creado_: {self.created_at}", ""]
        for sec in sorted(self.sections, key=lambda s: s.order):
            lines.append(f"## {sec.title}")
            lines.append("")
            lines.append(sec.content.strip())
            lines.append("")
        if self.artifacts:
            lines.append("## Artefactos Adjuntos")
            lines.append("")
            for a in self.artifacts:
                lines.append(f"- **{a.kind}** {a.name}: `{a.path}`")
        return "\n".join(lines) + "\n"

    def to_latex(self, style: str = "article", include_bib: bool = True) -> str:
        """Generate a LaTeX document with proper academic structure.
        
        Args:
            style: Document class (article, report, etc.)
            include_bib: Whether to include bibliography section
            
        Returns:
            Complete LaTeX source code
        """
        def escape_latex(text: str) -> str:
            """Escape special LaTeX characters."""
            replacements = [
                ('\\', r'\textbackslash{}'),
                ('&', r'\&'),
                ('%', r'\%'),
                ('$', r'\$'),
                ('#', r'\#'),
                ('_', r'\_'),
                ('{', r'\{'),
                ('}', r'\}'),
                ('~', r'\textasciitilde{}'),
                ('^', r'\textasciicircum{}'),
            ]
            for old, new in replacements:
                if old != '\\':  # Handle backslash first
                    text = text.replace(old, new)
            return text
        
        lines = []
        
        # Document preamble
        lines.append(f"\\documentclass[12pt]{{{style}}}")
        lines.append("\\usepackage[utf8]{inputenc}")
        lines.append("\\usepackage{amsmath,amssymb,amsthm}")
        lines.append("\\usepackage{graphicx}")
        lines.append("\\usepackage{hyperref}")
        lines.append("\\usepackage{booktabs}")
        lines.append("\\usepackage{listings}")
        lines.append("")
        
        # Title and authors
        lines.append(f"\\title{{{escape_latex(self.title)}}}")
        author_str = " \\and ".join(escape_latex(a) for a in self.authors)
        lines.append(f"\\author{{{author_str}}}")
        lines.append(f"\\date{{{self.created_at[:10]}}}")
        lines.append("")
        
        # Begin document
        lines.append("\\begin{document}")
        lines.append("\\maketitle")
        lines.append("")
        
        # Abstract (if present in metadata)
        abstract = self.metadata.get("abstract", "")
        if abstract:
            lines.append("\\begin{abstract}")
            lines.append(escape_latex(abstract))
            lines.append("\\end{abstract}")
            lines.append("")
        
        # Keywords
        keywords = self.metadata.get("keywords", [])
        if keywords:
            lines.append(f"\\textbf{{Keywords:}} {', '.join(escape_latex(k) for k in keywords)}")
            lines.append("")
        
        # Sections
        for sec in sorted(self.sections, key=lambda s: s.order):
            lines.append(f"\\section{{{escape_latex(sec.title)}}}")
            # Convert markdown-style content to LaTeX
            content = sec.content.strip()
            # Handle code blocks
            content = content.replace("```json", "\\begin{lstlisting}[language=json]")
            content = content.replace("```", "\\end{lstlisting}")
            # Handle markdown tables (basic conversion)
            if "|" in content and "---" in content:
                table_lines = content.split("\n")
                new_content = []
                in_table = False
                for tl in table_lines:
                    if tl.strip().startswith("|") and "---" not in tl:
                        if not in_table:
                            cols = tl.count("|") - 1
                            new_content.append(f"\\begin{{tabular}}{{{'l' * cols}}}")
                            new_content.append("\\toprule")
                            in_table = True
                        cells = [c.strip() for c in tl.split("|")[1:-1]]
                        new_content.append(" & ".join(escape_latex(c) for c in cells) + " \\\\")
                    elif "---" in tl and in_table:
                        new_content.append("\\midrule")
                    elif in_table and not tl.strip().startswith("|"):
                        new_content.append("\\bottomrule")
                        new_content.append("\\end{tabular}")
                        in_table = False
                        new_content.append(tl)
                    else:
                        new_content.append(tl)
                if in_table:
                    new_content.append("\\bottomrule")
                    new_content.append("\\end{tabular}")
                content = "\n".join(new_content)
            lines.append(content)
            lines.append("")
        
        # Artifacts as figures/tables references
        if self.artifacts:
            lines.append("\\section{Supplementary Materials}")
            for a in self.artifacts:
                lines.append(f"\\textbf{{{escape_latex(a.kind.title())}}}: {escape_latex(a.name)} -- \\texttt{{{escape_latex(a.path)}}}")
                lines.append("")
        
        # Bibliography
        if include_bib:
            literature = self.metadata.get("literature_sources", [])
            if literature:
                lines.append("\\section*{References}")
                lines.append("\\begin{thebibliography}{99}")
                for i, lit in enumerate(literature[:20]):  # Limit to 20 refs
                    authors_str = ", ".join(lit.get("authors", ["Unknown"])[:3])
                    title_str = lit.get("title", "Untitled")
                    year = lit.get("published_date", "")[:4] or "n.d."
                    arxiv = lit.get("arxiv_id", "")
                    lines.append(f"\\bibitem{{ref{i+1}}} {escape_latex(authors_str)}. " +
                               f"\\textit{{{escape_latex(title_str)}}}. {year}. " +
                               f"arXiv:{escape_latex(arxiv)}" if arxiv else "")
                lines.append("\\end{thebibliography}")
        
        lines.append("\\end{document}")
        
        return "\n".join(lines)


def build_paper(
    metadata: Dict[str, Any], 
    sections: Dict[str, Dict[str, Any]], 
    artifacts: Dict[str, Dict[str, Any]],
    experimental_results: Dict[str, Any] = None
) -> MiniPaper:
    """Build a comprehensive scientific paper including experimental data."""
    title = metadata.get("title", "Mini-Paper Autónomo")
    authors = metadata.get("authors", ["Agente 3 Autónomo"])
    created_at = datetime.utcnow().isoformat()

    sec_objs: List[PaperSection] = []
    
    # Add manually provided sections
    for k, spec in sections.items():
        sec_objs.append(
            PaperSection(
                key=k,
                title=spec.get("title", k.title()),
                content=spec.get("content", "(vacío)"),
                order=int(spec.get("order", 100)),
            )
        )

    # Automatically generate "Computational Validation" section if results exist
    if experimental_results or metadata.get("tool_evidence"):
        validation_content = _generate_validation_section(
            experimental_results or {}, 
            metadata.get("tool_evidence", {})
        )
        
        sec_objs.append(
            PaperSection(
                key="computational_validation",
                title="Computational Validation & Experimental Results",
                content=validation_content,
                order=50  # Place after methodology (typically order 30-40)
            )
        )
        
    art_objs: List[PaperArtifactRef] = []
    for k, spec in artifacts.items():
        art_objs.append(
            PaperArtifactRef(
                name=spec.get("name", k),
                path=spec.get("path", f"artifacts/{k}"),
                kind=spec.get("kind", "generic"),
            )
        )

    return MiniPaper(
        title=title,
        authors=authors,
        created_at=created_at,
        sections=sec_objs,
        artifacts=art_objs,
        metadata=metadata,
    )


def _generate_validation_section(results: Dict[str, Any], evidence: Dict[str, Any]) -> str:
    """Generate Markdown content for computational validation section."""
    lines = []
    lines.append("This hypothesis has been computationally validated using the following methods:")
    lines.append("")
    
    # 1. Evidence Summary
    if evidence:
        support_score = evidence.get("aggregate", {}).get("support_score", 0.0)
        lines.append(f"**Aggregate Support Score**: {support_score:.2f} / 1.0")
        lines.append("")
        
        items = evidence.get("evidence_items", [])
        if items:
            lines.append("### Automated Verification Results")
            lines.append("| Method | Success | Confidence | Output Summary |")
            lines.append("|--------|---------|------------|----------------|")
            
            for item in items:
                method = item.get("source", "Unknown Tool")
                success = "✅" if item.get("success") else "❌"
                confidence = f"{item.get('confidence', 0.0):.2f}"
                raw = str(item.get("raw_result", ""))
                summary = raw[:100] + "..." if len(raw) > 100 else raw
                summary = summary.replace("\n", " ") # Keep table clean
                
                lines.append(f"| {method} | {success} | {confidence} | {summary} |")
            lines.append("")

    # 2. Experimental Data
    if results:
        lines.append("### Experimental Data")
        for key, value in results.items():
            lines.append(f"**{key.replace('_', ' ').title()}**:")
            if isinstance(value, (list, dict)):
                lines.append("```json")
                import json
                lines.append(json.dumps(value, indent=2))
                lines.append("```")
            else:
                lines.append(f"{value}")
            lines.append("")
            
    return "\n".join(lines)


__all__ = ["PaperSection", "PaperArtifactRef", "MiniPaper", "build_paper"]
