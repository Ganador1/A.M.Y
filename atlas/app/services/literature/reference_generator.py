#!/usr/bin/env python3
"""
Reference Generator Service - Generación automática de bibliografías
Extrae DOIs, citas y papers de tool evidence para crear sección de Referencias
"""

import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ReferenceGeneratorService:
    """Servicio para generar referencias bibliográficas automáticamente"""
    
    def __init__(self):
        self.citation_styles = {
            "APA": self._format_apa,
            "IEEE": self._format_ieee,
            "Nature": self._format_nature,
            "Chicago": self._format_chicago
        }
    
    def generate_references_section(
        self, 
        tool_evidence: Dict[str, Any],
        domain: str = "general",
        style: str = "APA",
        max_references: int = 30
    ) -> str:
        """
        Genera sección de Referencias basada en tool evidence
        
        Args:
            tool_evidence: Evidence items de las herramientas ejecutadas
            domain: Dominio científico
            style: Estilo de citación (APA, IEEE, Nature, Chicago)
            max_references: Número máximo de referencias
            
        Returns:
            Texto formateado de la sección References
        """
        logger.info(f"Generando referencias en estilo {style} para dominio {domain}")
        
        # Extraer referencias de tool evidence
        references = self._extract_references_from_evidence(tool_evidence)
        
        # Agregar referencias estándar del dominio
        domain_refs = self._get_domain_standard_references(domain)
        references.extend(domain_refs)
        
        # Eliminar duplicados
        unique_refs = self._deduplicate_references(references)
        
        # Limitar cantidad
        final_refs = unique_refs[:max_references]
        
        # Formatear según estilo
        formatter = self.citation_styles.get(style, self._format_apa)
        formatted_refs = [formatter(ref, idx + 1) for idx, ref in enumerate(final_refs)]
        
        # Construir sección
        references_section = "\n## References\n\n"
        references_section += "\n".join(formatted_refs)
        
        logger.info(f"Generadas {len(final_refs)} referencias en estilo {style}")
        return references_section
    
    def _extract_references_from_evidence(self, tool_evidence: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extrae referencias de evidencia de herramientas"""
        references = []
        
        evidence_items = tool_evidence.get("evidence_items", [])
        
        for item in evidence_items:
            tool_name = item.get("tool_name", "")
            metadata = item.get("metadata", {})
            content = item.get("content", "")
            
            # Extraer DOI si existe
            doi = metadata.get("doi") or self._extract_doi_from_text(content)
            
            # Crear referencia basada en la herramienta
            if "pubmed" in tool_name.lower():
                ref = self._create_pubmed_reference(metadata, doi)
                if ref:
                    references.append(ref)
            
            elif "arxiv" in tool_name.lower():
                ref = self._create_arxiv_reference(metadata)
                if ref:
                    references.append(ref)
            
            elif "crossref" in tool_name.lower() or "openalex" in tool_name.lower():
                ref = self._create_doi_reference(metadata, doi)
                if ref:
                    references.append(ref)
            
            elif "chembl" in tool_name.lower():
                ref = self._create_database_reference("ChemBL", metadata)
                if ref:
                    references.append(ref)
            
            # Extraer citas del contenido si tiene formato [Author et al., Year]
            text_citations = self._extract_citations_from_text(content)
            references.extend(text_citations)
        
        return references
    
    def _create_pubmed_reference(self, metadata: Dict, doi: Optional[str]) -> Optional[Dict]:
        """Crea referencia de PubMed"""
        title = metadata.get("title", "")
        authors = metadata.get("authors", "Unknown Authors")
        year = metadata.get("year", str(datetime.now().year))
        journal = metadata.get("journal", "PubMed Database")
        pmid = metadata.get("pmid", "")
        
        if not title:
            return None
        
        return {
            "type": "article",
            "authors": authors,
            "year": year,
            "title": title,
            "journal": journal,
            "doi": doi,
            "pmid": pmid
        }
    
    def _create_arxiv_reference(self, metadata: Dict) -> Optional[Dict]:
        """Crea referencia de arXiv"""
        title = metadata.get("title", "")
        authors = metadata.get("authors", "Unknown Authors")
        year = metadata.get("year", str(datetime.now().year))
        arxiv_id = metadata.get("arxiv_id", metadata.get("id", ""))
        
        if not title:
            return None
        
        return {
            "type": "preprint",
            "authors": authors,
            "year": year,
            "title": title,
            "arxiv_id": arxiv_id,
            "url": f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else ""
        }
    
    def _create_doi_reference(self, metadata: Dict, doi: Optional[str]) -> Optional[Dict]:
        """Crea referencia basada en DOI"""
        if not doi:
            return None
        
        title = metadata.get("title", "Research Article")
        authors = metadata.get("authors", "Unknown Authors")
        year = metadata.get("year", str(datetime.now().year))
        journal = metadata.get("journal", "Scientific Journal")
        
        return {
            "type": "article",
            "authors": authors,
            "year": year,
            "title": title,
            "journal": journal,
            "doi": doi
        }
    
    def _create_database_reference(self, db_name: str, metadata: Dict) -> Optional[Dict]:
        """Crea referencia de base de datos"""
        return {
            "type": "database",
            "database": db_name,
            "year": str(datetime.now().year),
            "url": metadata.get("url", f"https://{db_name.lower()}.org"),
            "access_date": datetime.now().strftime("%Y-%m-%d")
        }
    
    def _extract_doi_from_text(self, text: str) -> Optional[str]:
        """Extrae DOI del texto usando regex"""
        doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
        match = re.search(doi_pattern, text, re.IGNORECASE)
        return match.group(0) if match else None
    
    def _extract_citations_from_text(self, text: str) -> List[Dict]:
        """Extrae citas del formato [Author et al., Year]"""
        citations = []
        
        # Patrón: [Apellido et al., YYYY]
        pattern = r'\[([A-Z][a-z]+)\s+et\s+al\.,?\s+(\d{4})\]'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            author = match.group(1)
            year = match.group(2)
            
            citations.append({
                "type": "article",
                "authors": f"{author} et al.",
                "year": year,
                "title": "Referenced Work",  # Placeholder
                "journal": "Scientific Literature"
            })
        
        return citations
    
    def _get_domain_standard_references(self, domain: str) -> List[Dict]:
        """Obtiene referencias estándar por dominio"""
        standard_refs = {
            "neuroscience": [
                {
                    "type": "article",
                    "authors": "Kandel, E. R., Schwartz, J. H., & Jessell, T. M.",
                    "year": "2000",
                    "title": "Principles of Neural Science",
                    "journal": "McGraw-Hill",
                    "edition": "4th"
                },
                {
                    "type": "article",
                    "authors": "Hebb, D. O.",
                    "year": "1949",
                    "title": "The Organization of Behavior",
                    "journal": "Wiley"
                },
                {
                    "type": "article",
                    "authors": "Dayan, P., & Abbott, L. F.",
                    "year": "2001",
                    "title": "Theoretical Neuroscience: Computational and Mathematical Modeling",
                    "journal": "MIT Press"
                },
                {
                    "type": "article",
                    "authors": "LeCun, Y., Bengio, Y., & Hinton, G.",
                    "year": "2015",
                    "title": "Deep learning",
                    "journal": "Nature",
                    "doi": "10.1038/nature14539"
                }
            ],
            "mathematics": [
                {
                    "type": "book",
                    "authors": "Rudin, W.",
                    "year": "1976",
                    "title": "Principles of Mathematical Analysis",
                    "journal": "McGraw-Hill",
                    "edition": "3rd"
                },
                {
                    "type": "article",
                    "authors": "Press, W. H., Teukolsky, S. A., Vetterling, W. T., & Flannery, B. P.",
                    "year": "2007",
                    "title": "Numerical Recipes: The Art of Scientific Computing",
                    "journal": "Cambridge University Press",
                    "edition": "3rd"
                },
                {
                    "type": "article",
                    "authors": "Knuth, D. E.",
                    "year": "1997",
                    "title": "The Art of Computer Programming",
                    "journal": "Addison-Wesley",
                    "edition": "3rd"
                },
                {
                    "type": "article",
                    "authors": "Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C.",
                    "year": "2009",
                    "title": "Introduction to Algorithms",
                    "journal": "MIT Press",
                    "edition": "3rd"
                }
            ],
            "chemistry": [
                {
                    "type": "article",
                    "authors": "Ertl, P., & Schuffenhauer, A.",
                    "year": "2009",
                    "title": "Estimation of synthetic accessibility score of drug-like molecules",
                    "journal": "Journal of Cheminformatics",
                    "doi": "10.1186/1758-2946-1-8"
                },
                {
                    "type": "article",
                    "authors": "Lipinski, C. A., Lombardo, F., Dominy, B. W., & Feeney, P. J.",
                    "year": "2001",
                    "title": "Experimental and computational approaches to estimate solubility",
                    "journal": "Advanced Drug Delivery Reviews",
                    "doi": "10.1016/S0169-409X(00)00129-0"
                },
                {
                    "type": "article",
                    "authors": "Gaulton, A. et al.",
                    "year": "2017",
                    "title": "The ChEMBL database in 2017",
                    "journal": "Nucleic Acids Research",
                    "doi": "10.1093/nar/gkw1074"
                },
                {
                    "type": "article",
                    "authors": "Landrum, G.",
                    "year": "2023",
                    "title": "RDKit: Open-source cheminformatics",
                    "journal": "rdkit.org"
                }
            ],
            "physics": [
                {
                    "type": "article",
                    "authors": "Nielsen, M. A., & Chuang, I. L.",
                    "year": "2010",
                    "title": "Quantum Computation and Quantum Information",
                    "journal": "Cambridge University Press",
                    "edition": "10th Anniversary"
                },
                {
                    "type": "article",
                    "authors": "Preskill, J.",
                    "year": "2018",
                    "title": "Quantum Computing in the NISQ era and beyond",
                    "journal": "Quantum",
                    "doi": "10.22331/q-2018-08-06-79"
                },
                {
                    "type": "article",
                    "authors": "Arute, F. et al.",
                    "year": "2019",
                    "title": "Quantum supremacy using a programmable superconducting processor",
                    "journal": "Nature",
                    "doi": "10.1038/s41586-019-1666-5"
                },
                {
                    "type": "article",
                    "authors": "Feynman, R. P.",
                    "year": "1982",
                    "title": "Simulating physics with computers",
                    "journal": "International Journal of Theoretical Physics",
                    "doi": "10.1007/BF02650179"
                }
            ],
            "biology": [
                {
                    "type": "article",
                    "authors": "Alberts, B. et al.",
                    "year": "2014",
                    "title": "Molecular Biology of the Cell",
                    "journal": "Garland Science",
                    "edition": "6th"
                },
                {
                    "type": "article",
                    "authors": "Watson, J. D., & Crick, F. H.",
                    "year": "1953",
                    "title": "Molecular structure of nucleic acids",
                    "journal": "Nature",
                    "doi": "10.1038/171737a0"
                },
                {
                    "type": "article",
                    "authors": "Sanger, F., & Coulson, A. R.",
                    "year": "1975",
                    "title": "A rapid method for determining sequences in DNA",
                    "journal": "Journal of Molecular Biology",
                    "doi": "10.1016/0022-2836(75)90213-2"
                },
                {
                    "type": "article",
                    "authors": "Venter, J. C. et al.",
                    "year": "2001",
                    "title": "The sequence of the human genome",
                    "journal": "Science",
                    "doi": "10.1126/science.1058040"
                }
            ]
        }
        
        return standard_refs.get(domain, [])[:5]  # Máximo 5 referencias estándar (AUMENTADO)
    
    def _deduplicate_references(self, references: List[Dict]) -> List[Dict]:
        """Elimina referencias duplicadas"""
        seen = set()
        unique = []
        
        for ref in references:
            # Crear key basada en título, autores y año
            key = f"{ref.get('authors', '')}_{ref.get('year', '')}_{ref.get('title', '')}"
            key = key.lower().strip()
            
            if key and key not in seen:
                seen.add(key)
                unique.append(ref)
        
        return unique
    
    # ========================================================================
    # FORMATTERS POR ESTILO
    # ========================================================================
    
    def _format_apa(self, ref: Dict, index: int) -> str:
        """Formato APA (American Psychological Association)"""
        authors = ref.get("authors", "Unknown")
        year = ref.get("year", "n.d.")
        title = ref.get("title", "Untitled")
        
        if ref.get("type") == "article":
            journal = ref.get("journal", "")
            doi = ref.get("doi", "")
            
            formatted = f"{index}. {authors} ({year}). {title}. *{journal}*"
            if doi:
                formatted += f". https://doi.org/{doi}"
            return formatted
        
        elif ref.get("type") == "preprint":
            arxiv_id = ref.get("arxiv_id", "")
            url = ref.get("url", "")
            
            formatted = f"{index}. {authors} ({year}). {title}. arXiv preprint"
            if arxiv_id:
                formatted += f" arXiv:{arxiv_id}"
            if url:
                formatted += f". {url}"
            return formatted
        
        elif ref.get("type") == "database":
            db_name = ref.get("database", "Database")
            url = ref.get("url", "")
            access_date = ref.get("access_date", "")
            
            formatted = f"{index}. {db_name} Database. ({year})"
            if url:
                formatted += f". Retrieved from {url}"
            if access_date:
                formatted += f" (accessed {access_date})"
            return formatted
        
        else:
            return f"{index}. {authors} ({year}). {title}."
    
    def _format_ieee(self, ref: Dict, index: int) -> str:
        """Formato IEEE"""
        authors = ref.get("authors", "Unknown")
        title = ref.get("title", "Untitled")
        year = ref.get("year", "n.d.")
        
        # IEEE usa corchetes para números
        if ref.get("type") == "article":
            journal = ref.get("journal", "")
            doi = ref.get("doi", "")
            
            formatted = f"[{index}] {authors}, \"{title},\" *{journal}*, {year}"
            if doi:
                formatted += f", doi: {doi}"
            formatted += "."
            return formatted
        
        else:
            return f"[{index}] {authors}, \"{title},\" {year}."
    
    def _format_nature(self, ref: Dict, index: int) -> str:
        """Formato Nature"""
        authors = ref.get("authors", "Unknown")
        title = ref.get("title", "Untitled")
        year = ref.get("year", "n.d.")
        journal = ref.get("journal", "")
        
        # Nature usa formato compacto
        formatted = f"{index}. {authors} {title}. *{journal}* ({year})"
        
        doi = ref.get("doi", "")
        if doi:
            formatted += f". https://doi.org/{doi}"
        
        return formatted
    
    def _format_chicago(self, ref: Dict, index: int) -> str:
        """Formato Chicago"""
        authors = ref.get("authors", "Unknown")
        year = ref.get("year", "n.d.")
        title = ref.get("title", "Untitled")
        
        if ref.get("type") == "article":
            journal = ref.get("journal", "")
            
            formatted = f"{index}. {authors}. \"{title}.\" *{journal}* ({year})"
            
            doi = ref.get("doi", "")
            if doi:
                formatted += f". https://doi.org/{doi}"
            
            formatted += "."
            return formatted
        
        else:
            return f"{index}. {authors}. {title}. {year}."


# ============================================================================
# UTILIDADES PARA INTEGRACIÓN CON PIPELINES
# ============================================================================

def add_references_to_paper(
    paper_text: str,
    tool_evidence: Dict[str, Any],
    domain: str = "general",
    style: str = "APA"
) -> str:
    """
    Agrega sección de Referencias a un paper científico
    
    Args:
        paper_text: Texto del paper
        tool_evidence: Evidencia de herramientas
        domain: Dominio científico
        style: Estilo de citación
        
    Returns:
        Paper con sección References agregada o expandida
    """
    # Validación de tipo
    if not isinstance(paper_text, str):
        logger.error(f"paper_text debe ser str, recibido {type(paper_text)}")
        # Si es un dict con clave "text" o "content", extraer
        if isinstance(paper_text, dict):
            if "text" in paper_text:
                paper_text = paper_text["text"]
            elif "content" in paper_text:
                paper_text = paper_text["content"]
            else:
                raise TypeError(f"paper_text es dict sin claves 'text'/'content': {list(paper_text.keys())}")
        else:
            raise TypeError(f"paper_text debe ser str, recibido {type(paper_text)}")
    
    generator = ReferenceGeneratorService()
    
    # Generar nuevas referencias
    references_section = generator.generate_references_section(
        tool_evidence=tool_evidence,
        domain=domain,
        style=style
    )
    
    # Verificar si ya tiene referencias
    if "## References" in paper_text or "## Bibliography" in paper_text:
        logger.info("Paper ya contiene sección de Referencias, AGREGANDO nuevas referencias")
        
        # Buscar el final de la sección References
        import re
        ref_pattern = r'(## References?|## Bibliography)\s*\n'
        match = re.search(ref_pattern, paper_text, re.IGNORECASE)
        
        if match:
            # Encontrar siguiente sección (## algo) o final del documento
            end_match = re.search(r'\n##\s+\w+', paper_text[match.end():])
            
            if end_match:
                # Insertar antes de la siguiente sección
                insert_pos = match.end() + end_match.start()
                # Extraer solo las referencias (sin el encabezado "## References")
                new_refs_only = references_section.split("\n\n", 1)[1] if "\n\n" in references_section else ""
                enhanced_paper = paper_text[:insert_pos] + "\n" + new_refs_only + "\n" + paper_text[insert_pos:]
                logger.info("Referencias agregadas a sección existente (antes de siguiente sección)")
            else:
                # Agregar al final del documento
                new_refs_only = references_section.split("\n\n", 1)[1] if "\n\n" in references_section else ""
                enhanced_paper = paper_text.rstrip() + "\n" + new_refs_only + "\n"
                logger.info("Referencias agregadas al final de sección existente")
        else:
            # Fallback: agregar al final
            enhanced_paper = paper_text.rstrip() + "\n\n" + references_section
            logger.info("No se pudo parsear sección existente, agregando al final")
    else:
        # No hay referencias, crear nueva sección
        enhanced_paper = paper_text.rstrip() + "\n\n" + references_section
        logger.info("Nueva sección de Referencias creada")
    
    return enhanced_paper


def extract_in_text_citations(paper_text: str) -> List[str]:
    """
    Extrae citas in-text del formato [X] o (Author, Year)
    
    Args:
        paper_text: Texto del paper
        
    Returns:
        Lista de citas encontradas
    """
    citations = []
    
    # Patrón [1], [2], etc.
    numeric_pattern = r'\[(\d+)\]'
    numeric_matches = re.findall(numeric_pattern, paper_text)
    citations.extend([f"[{m}]" for m in numeric_matches])
    
    # Patrón (Author, Year)
    author_year_pattern = r'\(([A-Z][a-z]+(?:\s+et\s+al\.)?),\s+(\d{4})\)'
    author_year_matches = re.findall(author_year_pattern, paper_text)
    citations.extend([f"({author}, {year})" for author, year in author_year_matches])
    
    return list(set(citations))  # Unique


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Ejemplo de tool evidence
    sample_evidence = {
        "evidence_items": [
            {
                "tool_name": "pubmed",
                "metadata": {
                    "title": "Neural plasticity and learning",
                    "authors": "Smith, J. et al.",
                    "year": "2023",
                    "journal": "Nature Neuroscience",
                    "pmid": "12345678"
                },
                "content": "Study on synaptic plasticity...",
                "signal_strength": 0.85
            },
            {
                "tool_name": "arxiv",
                "metadata": {
                    "title": "Quantum algorithms for optimization",
                    "authors": "Doe, A. and Lee, B.",
                    "year": "2024",
                    "arxiv_id": "2401.12345"
                },
                "content": "Novel quantum approach...",
                "signal_strength": 0.72
            }
        ]
    }
    
    # Generar referencias
    generator = ReferenceGeneratorService()
    references = generator.generate_references_section(
        tool_evidence=sample_evidence,
        domain="neuroscience",
        style="APA"
    )
    
    print(references)
    print("\n" + "="*80)
    print("✅ Reference Generator Service - DEMO COMPLETADO")
