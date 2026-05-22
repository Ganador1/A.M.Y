"""
Journal Formatter Service - AXIOM META 4
Automated formatting of scientific publications for specific journals.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from jinja2 import Environment, FileSystemLoader

from app.core.bootstrap_logging import logger
from app.services.base_service import BaseService
from app.exceptions.domain.biology import BiologyError
from app.types.journal_formatter_types import (
    ProcessRequestResult,
    FormatForJournalResult,
    ConvertBetweenJournalsResult,
    ValidateJournalRequirementsResult,
    GetJournalStylesResult,
)


@dataclass
class JournalStyle:
    """Style configuration for a specific journal"""
    name: str
    abbreviation: str
    publisher: str
    impact_factor: Optional[float] = None
    
    # Formatting specifications
    font_family: str = "Times New Roman"
    font_size: int = 12
    line_spacing: float = 1.5
    margins: Dict[str, float] = field(default_factory=lambda: {"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0})
    
    # Figure specifications
    figure_width: float = 6.0  # inches
    figure_height: float = 4.0  # inches
    figure_dpi: int = 300
    figure_format: str = "png"
    
    # Citation style
    citation_style: str = "numeric"  # numeric, author-year, superscript
    reference_format: str = "vancouver"  # vancouver, apa, mla, chicago
    
    # Section requirements
    required_sections: List[str] = field(default_factory=lambda: ["abstract", "introduction", "methods", "results", "discussion", "conclusions"])
    optional_sections: List[str] = field(default_factory=lambda: ["acknowledgments", "author_contributions", "conflicts_of_interest"])
    
    # Word limits
    abstract_word_limit: int = 250
    title_word_limit: int = 20
    keywords_limit: int = 6
    
    # Special requirements
    requires_preregistration: bool = False
    requires_data_availability: bool = True
    requires_code_availability: bool = True
    requires_ethics_statement: bool = False


@dataclass
class FormattingResult:
    """Result of journal formatting operation"""
    success: bool
    formatted_content: Dict[str, str]
    metadata: Dict[str, Any]
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    word_counts: Dict[str, int] = field(default_factory=dict)


class JournalFormatterService(BaseService):
    """Service for formatting publications for specific journals"""
    
    def __init__(self):
        super().__init__("JournalFormatterService")
        
        # Initialize journal styles database
        self.journal_styles = self._initialize_journal_styles()
        
        # Initialize template engine
        self.template_engine = self._initialize_template_engine()
        
        logger.info("✅ JournalFormatterService initialized")
    
    def _initialize_journal_styles(self) -> Dict[str, JournalStyle]:
        """Initialize database of journal formatting styles"""
        return {
            "nature": JournalStyle(
                name="Nature",
                abbreviation="Nat",
                publisher="Nature Publishing Group",
                impact_factor=69.5,
                font_family="Times New Roman",
                font_size=11,
                line_spacing=1.5,
                margins={"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0},
                figure_width=7.0,
                figure_height=5.0,
                figure_dpi=300,
                citation_style="numeric",
                reference_format="nature",
                required_sections=["abstract", "introduction", "methods", "results", "discussion"],
                optional_sections=["acknowledgments", "author_contributions", "conflicts_of_interest", "data_availability"],
                abstract_word_limit=150,
                title_word_limit=15,
                keywords_limit=5,
                requires_preregistration=False,
                requires_data_availability=True,
                requires_code_availability=True,
                requires_ethics_statement=True
            ),
            
            "science": JournalStyle(
                name="Science",
                abbreviation="Sci",
                publisher="American Association for the Advancement of Science",
                impact_factor=63.7,
                font_family="Times New Roman",
                font_size=11,
                line_spacing=1.5,
                margins={"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0},
                figure_width=7.0,
                figure_height=5.0,
                figure_dpi=300,
                citation_style="numeric",
                reference_format="science",
                required_sections=["abstract", "introduction", "methods", "results", "discussion"],
                optional_sections=["acknowledgments", "author_contributions", "conflicts_of_interest"],
                abstract_word_limit=125,
                title_word_limit=15,
                keywords_limit=5,
                requires_preregistration=False,
                requires_data_availability=True,
                requires_code_availability=True,
                requires_ethics_statement=True
            ),
            
            "cell": JournalStyle(
                name="Cell",
                abbreviation="Cell",
                publisher="Cell Press",
                impact_factor=66.9,
                font_family="Times New Roman",
                font_size=11,
                line_spacing=1.5,
                margins={"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0},
                figure_width=7.0,
                figure_height=5.0,
                figure_dpi=300,
                citation_style="numeric",
                reference_format="cell",
                required_sections=["abstract", "introduction", "methods", "results", "discussion"],
                optional_sections=["acknowledgments", "author_contributions", "conflicts_of_interest", "data_availability"],
                abstract_word_limit=150,
                title_word_limit=15,
                keywords_limit=5,
                requires_preregistration=False,
                requires_data_availability=True,
                requires_code_availability=True,
                requires_ethics_statement=True
            ),
            
            "pnas": JournalStyle(
                name="Proceedings of the National Academy of Sciences",
                abbreviation="PNAS",
                publisher="National Academy of Sciences",
                impact_factor=12.8,
                font_family="Times New Roman",
                font_size=11,
                line_spacing=1.5,
                margins={"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0},
                figure_width=6.0,
                figure_height=4.0,
                figure_dpi=300,
                citation_style="numeric",
                reference_format="pnas",
                required_sections=["abstract", "introduction", "methods", "results", "discussion"],
                optional_sections=["acknowledgments", "author_contributions", "conflicts_of_interest"],
                abstract_word_limit=250,
                title_word_limit=20,
                keywords_limit=6,
                requires_preregistration=False,
                requires_data_availability=True,
                requires_code_availability=False,
                requires_ethics_statement=False
            ),
            
            "plos_one": JournalStyle(
                name="PLOS ONE",
                abbreviation="PLOS ONE",
                publisher="Public Library of Science",
                impact_factor=3.7,
                font_family="Arial",
                font_size=12,
                line_spacing=1.5,
                margins={"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0},
                figure_width=6.0,
                figure_height=4.0,
                figure_dpi=300,
                citation_style="numeric",
                reference_format="plos",
                required_sections=["abstract", "introduction", "methods", "results", "discussion"],
                optional_sections=["acknowledgments", "author_contributions", "conflicts_of_interest", "data_availability"],
                abstract_word_limit=300,
                title_word_limit=25,
                keywords_limit=8,
                requires_preregistration=True,
                requires_data_availability=True,
                requires_code_availability=True,
                requires_ethics_statement=True
            ),
            
            "biorxiv": JournalStyle(
                name="bioRxiv",
                abbreviation="bioRxiv",
                publisher="Cold Spring Harbor Laboratory",
                impact_factor=None,  # Preprint server
                font_family="Times New Roman",
                font_size=12,
                line_spacing=1.5,
                margins={"top": 1.0, "bottom": 1.0, "left": 1.0, "right": 1.0},
                figure_width=6.0,
                figure_height=4.0,
                figure_dpi=300,
                citation_style="numeric",
                reference_format="vancouver",
                required_sections=["abstract", "introduction", "methods", "results", "discussion"],
                optional_sections=["acknowledgments", "author_contributions", "conflicts_of_interest"],
                abstract_word_limit=250,
                title_word_limit=25,
                keywords_limit=10,
                requires_preregistration=False,
                requires_data_availability=True,
                requires_code_availability=True,
                requires_ethics_statement=False
            )
        }
    
    def _initialize_template_engine(self) -> Environment:
        """Initialize Jinja2 template engine for journal formatting"""
        templates_dir = Path(__file__).parent.parent / "templates" / "journal_formats"
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Create default templates if they don't exist
        self._create_journal_templates(templates_dir)
        
        return Environment(loader=FileSystemLoader(str(templates_dir)))
    
    def _create_journal_templates(self, templates_dir: Path):
        """Create default journal formatting templates"""
        templates = {
            "nature_template.md": """# {{ title }}

**Authors**: {{ authors | join(", ") }}

**Affiliations**: {{ affiliations | join("; ") }}

**Corresponding Author**: {{ corresponding_author }}

**Email**: {{ corresponding_email }}

---

## Abstract

{{ abstract }}

**Keywords**: {{ keywords | join(", ") }}

---

## Introduction

{{ introduction }}

---

## Methods

{{ methods }}

---

## Results

{{ results }}

---

## Discussion

{{ discussion }}

---

## Acknowledgments

{{ acknowledgments }}

---

## Author Contributions

{{ author_contributions }}

---

## Data Availability

{{ data_availability }}

---

## References

{% for ref in references %}
{{ loop.index }}. {{ ref.citation }}
{% endfor %}

---

*Manuscript prepared for submission to Nature*
""",
            
            "science_template.md": """# {{ title }}

**Authors**: {{ authors | join(", ") }}

**Affiliations**: {{ affiliations | join("; ") }}

**Corresponding Author**: {{ corresponding_author }}

**Email**: {{ corresponding_email }}

---

## Abstract

{{ abstract }}

**Keywords**: {{ keywords | join(", ") }}

---

## Introduction

{{ introduction }}

---

## Materials and Methods

{{ methods }}

---

## Results

{{ results }}

---

## Discussion

{{ discussion }}

---

## Acknowledgments

{{ acknowledgments }}

---

## Author Contributions

{{ author_contributions }}

---

## Data and Materials Availability

{{ data_availability }}

---

## References

{% for ref in references %}
{{ loop.index }}. {{ ref.citation }}
{% endfor %}

---

*Manuscript prepared for submission to Science*
""",
            
            "cell_template.md": """# {{ title }}

**Authors**: {{ authors | join(", ") }}

**Affiliations**: {{ affiliations | join("; ") }}

**Corresponding Author**: {{ corresponding_author }}

**Email**: {{ corresponding_email }}

---

## Summary

{{ abstract }}

**Keywords**: {{ keywords | join(", ") }}

---

## Introduction

{{ introduction }}

---

## Results

{{ results }}

---

## Discussion

{{ discussion }}

---

## STAR Methods

{{ methods }}

---

## Acknowledgments

{{ acknowledgments }}

---

## Author Contributions

{{ author_contributions }}

---

## Data and Code Availability

{{ data_availability }}

---

## References

{% for ref in references %}
{{ loop.index }}. {{ ref.citation }}
{% endfor %}

---

*Manuscript prepared for submission to Cell*
""",
            
            "pnas_template.md": """# {{ title }}

**Authors**: {{ authors | join(", ") }}

**Affiliations**: {{ affiliations | join("; ") }}

**Corresponding Author**: {{ corresponding_author }}

**Email**: {{ corresponding_email }}

---

## Abstract

{{ abstract }}

**Significance Statement**: {{ significance_statement }}

**Keywords**: {{ keywords | join(", ") }}

---

## Introduction

{{ introduction }}

---

## Methods

{{ methods }}

---

## Results

{{ results }}

---

## Discussion

{{ discussion }}

---

## Acknowledgments

{{ acknowledgments }}

---

## Author Contributions

{{ author_contributions }}

---

## Data Availability

{{ data_availability }}

---

## References

{% for ref in references %}
{{ loop.index }}. {{ ref.citation }}
{% endfor %}

---

*Manuscript prepared for submission to PNAS*
""",
            
            "plos_template.md": """# {{ title }}

**Authors**: {{ authors | join(", ") }}

**Affiliations**: {{ affiliations | join("; ") }}

**Corresponding Author**: {{ corresponding_author }}

**Email**: {{ corresponding_email }}

---

## Abstract

### Background
{{ abstract_background }}

### Methods
{{ abstract_methods }}

### Results
{{ abstract_results }}

### Conclusions
{{ abstract_conclusions }}

---

## Introduction

{{ introduction }}

---

## Materials and Methods

{{ methods }}

---

## Results

{{ results }}

---

## Discussion

{{ discussion }}

---

## Acknowledgments

{{ acknowledgments }}

---

## Author Contributions

{{ author_contributions }}

---

## Data Availability

{{ data_availability }}

---

## References

{% for ref in references %}
{{ loop.index }}. {{ ref.citation }}
{% endfor %}

---

*Manuscript prepared for submission to PLOS ONE*
""",
            
            "biorxiv_template.md": """# {{ title }}

**Authors**: {{ authors | join(", ") }}

**Affiliations**: {{ affiliations | join("; ") }}

**Corresponding Author**: {{ corresponding_author }}

**Email**: {{ corresponding_email }}

**Preprint Server**: bioRxiv

**Date**: {{ submission_date }}

---

## Abstract

{{ abstract }}

**Keywords**: {{ keywords | join(", ") }}

---

## Introduction

{{ introduction }}

---

## Methods

{{ methods }}

---

## Results

{{ results }}

---

## Discussion

{{ discussion }}

---

## Acknowledgments

{{ acknowledgments }}

---

## Author Contributions

{{ author_contributions }}

---

## Data Availability

{{ data_availability }}

---

## References

{% for ref in references %}
{{ loop.index }}. {{ ref.citation }}
{% endfor %}

---

*Preprint submitted to bioRxiv*
"""
        }
        
        for filename, content in templates.items():
            template_path = templates_dir / filename
            if not template_path.exists():
                template_path.write_text(content)
                logger.info(f"✅ Created journal template: {filename}")
    
    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Process journal formatting requests"""
        try:
            action = request_data.get("action", "")
            
            if action == "format_for_journal":
                return await self.format_for_journal(request_data)
            elif action == "convert_between_journals":
                return await self.convert_between_journals(request_data)
            elif action == "validate_journal_requirements":
                return await self.validate_journal_requirements(request_data)
            elif action == "get_journal_styles":
                return await self.get_journal_styles(request_data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": [
                        "format_for_journal", "convert_between_journals",
                        "validate_journal_requirements", "get_journal_styles"
                    ]
                }
                
        except BiologyError as e:
            return self.handle_error(e, "process_request")
    
    async def format_for_journal(self, request_data: FormatForJournalResult) -> FormatForJournalResult:
        """Format publication content for a specific journal"""
        try:
            journal_name = request_data.get("journal", "nature")
            publication_content = request_data.get("publication_content", {})
            metadata = request_data.get("metadata", {})
            
            if journal_name not in self.journal_styles:
                return {
                    "success": False,
                    "error": f"Unknown journal: {journal_name}",
                    "available_journals": list(self.journal_styles.keys())
                }
            
            journal_style = self.journal_styles[journal_name]
            
            # Validate requirements
            validation_result = await self._validate_journal_requirements(
                publication_content, metadata, journal_style
            )
            
            # Format content
            formatted_content = await self._format_content_for_journal(
                publication_content, metadata, journal_style
            )
            
            # Generate word counts
            word_counts = self._calculate_word_counts(formatted_content)
            
            # Create result
            result = FormattingResult(
                success=True,
                formatted_content=formatted_content,
                metadata={
                    "journal": journal_name,
                    "journal_style": journal_style.__dict__,
                    "word_counts": word_counts,
                    "validation_warnings": validation_result.get("warnings", []),
                    "validation_errors": validation_result.get("errors", [])
                },
                warnings=validation_result.get("warnings", []),
                errors=validation_result.get("errors", []),
                word_counts=word_counts
            )
            
            logger.info(f"✅ Formatted publication for {journal_name}")
            
            return {
                "success": True,
                "journal": journal_name,
                "formatted_content": formatted_content,
                "metadata": result.metadata,
                "warnings": result.warnings,
                "errors": result.errors,
                "word_counts": word_counts
            }
            
        except BiologyError as e:
            return self.handle_error(e, "format_for_journal")
    
    async def convert_between_journals(self, request_data: ConvertBetweenJournalsResult) -> ConvertBetweenJournalsResult:
        """Convert publication from one journal format to another"""
        try:
            source_journal = request_data.get("source_journal", "nature")
            target_journal = request_data.get("target_journal", "science")
            publication_content = request_data.get("publication_content", {})
            metadata = request_data.get("metadata", {})
            
            if source_journal not in self.journal_styles or target_journal not in self.journal_styles:
                return {
                    "success": False,
                    "error": f"Unknown journal(s): {source_journal} -> {target_journal}",
                    "available_journals": list(self.journal_styles.keys())
                }
            
            # First format for source journal (if not already formatted)
            if not publication_content.get("formatted_for_journal"):
                source_result = await self.format_for_journal({
                    "journal": source_journal,
                    "publication_content": publication_content,
                    "metadata": metadata
                })
                
                if not source_result["success"]:
                    return source_result
                
                publication_content = source_result["formatted_content"]
            
            # Then convert to target journal
            target_result = await self.format_for_journal({
                "journal": target_journal,
                "publication_content": publication_content,
                "metadata": metadata
            })
            
            if target_result["success"]:
                logger.info(f"✅ Converted publication from {source_journal} to {target_journal}")
                
                return {
                    "success": True,
                    "source_journal": source_journal,
                    "target_journal": target_journal,
                    "converted_content": target_result["formatted_content"],
                    "metadata": target_result["metadata"],
                    "warnings": target_result["warnings"],
                    "errors": target_result["errors"]
                }
            else:
                return target_result
                
        except BiologyError as e:
            return self.handle_error(e, "convert_between_journals")
    
    async def validate_journal_requirements(self, request_data: ValidateJournalRequirementsResult) -> ValidateJournalRequirementsResult:
        """Validate publication against journal requirements"""
        try:
            journal_name = request_data.get("journal", "nature")
            publication_content = request_data.get("publication_content", {})
            metadata = request_data.get("metadata", {})
            
            if journal_name not in self.journal_styles:
                return {
                    "success": False,
                    "error": f"Unknown journal: {journal_name}",
                    "available_journals": list(self.journal_styles.keys())
                }
            
            journal_style = self.journal_styles[journal_name]
            validation_result = await self._validate_journal_requirements(
                publication_content, metadata, journal_style
            )
            
            return {
                "success": True,
                "journal": journal_name,
                "validation_result": validation_result,
                "journal_requirements": {
                    "required_sections": journal_style.required_sections,
                    "optional_sections": journal_style.optional_sections,
                    "word_limits": {
                        "abstract": journal_style.abstract_word_limit,
                        "title": journal_style.title_word_limit,
                        "keywords": journal_style.keywords_limit
                    },
                    "special_requirements": {
                        "preregistration": journal_style.requires_preregistration,
                        "data_availability": journal_style.requires_data_availability,
                        "code_availability": journal_style.requires_code_availability,
                        "ethics_statement": journal_style.requires_ethics_statement
                    }
                }
            }
            
        except BiologyError as e:
            return self.handle_error(e, "validate_journal_requirements")
    
    async def get_journal_styles(self, request_data: GetJournalStylesResult) -> GetJournalStylesResult:
        """Get information about available journal styles"""
        try:
            journal_name = request_data.get("journal")
            
            if journal_name:
                if journal_name in self.journal_styles:
                    return {
                        "success": True,
                        "journal": journal_name,
                        "style": self.journal_styles[journal_name].__dict__
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Unknown journal: {journal_name}",
                        "available_journals": list(self.journal_styles.keys())
                    }
            else:
                # Return all available journals
                journals_info = {}
                for name, style in self.journal_styles.items():
                    journals_info[name] = {
                        "name": style.name,
                        "abbreviation": style.abbreviation,
                        "publisher": style.publisher,
                        "impact_factor": style.impact_factor,
                        "required_sections": style.required_sections,
                        "abstract_word_limit": style.abstract_word_limit,
                        "title_word_limit": style.title_word_limit
                    }
                
                return {
                    "success": True,
                    "available_journals": journals_info,
                    "total_journals": len(self.journal_styles)
                }
                
        except BiologyError as e:
            return self.handle_error(e, "get_journal_styles")
    
    async def _validate_journal_requirements(self, content: Dict[str, Any], 
                                           metadata: Dict[str, Any], 
                                           journal_style: JournalStyle) -> Dict[str, Any]:
        """Validate publication against journal requirements"""
        warnings = []
        errors = []
        
        # Check required sections
        for section in journal_style.required_sections:
            if section not in content or not content[section].strip():
                errors.append(f"Missing required section: {section}")
        
        # Check word limits
        if "abstract" in content:
            abstract_words = len(content["abstract"].split())
            if abstract_words > journal_style.abstract_word_limit:
                warnings.append(f"Abstract exceeds word limit: {abstract_words}/{journal_style.abstract_word_limit}")
        
        if "title" in metadata:
            title_words = len(metadata["title"].split())
            if title_words > journal_style.title_word_limit:
                warnings.append(f"Title exceeds word limit: {title_words}/{journal_style.title_word_limit}")
        
        if "keywords" in metadata:
            keyword_count = len(metadata["keywords"])
            if keyword_count > journal_style.keywords_limit:
                warnings.append(f"Keywords exceed limit: {keyword_count}/{journal_style.keywords_limit}")
        
        # Check special requirements
        if journal_style.requires_data_availability and "data_availability" not in content:
            warnings.append("Data availability statement required")
        
        if journal_style.requires_code_availability and "code_availability" not in content:
            warnings.append("Code availability statement required")
        
        if journal_style.requires_ethics_statement and "ethics_statement" not in content:
            warnings.append("Ethics statement required")
        
        return {
            "warnings": warnings,
            "errors": errors,
            "valid": len(errors) == 0
        }
    
    async def _format_content_for_journal(self, content: Dict[str, Any], 
                                        metadata: Dict[str, Any], 
                                        journal_style: JournalStyle) -> Dict[str, str]:
        """Format content according to journal style"""
        try:
            # Select appropriate template
            template_name = f"{journal_style.name.lower().replace(' ', '_')}_template.md"
            
            # Prepare template context
            context = {
                "title": metadata.get("title", "Untitled"),
                "authors": metadata.get("authors", ["AXIOM Research Agent"]),
                "affiliations": metadata.get("affiliations", ["AXIOM Research Platform"]),
                "corresponding_author": metadata.get("corresponding_author", "AXIOM Research Agent"),
                "corresponding_email": metadata.get("corresponding_email", "research@axiom.ai"),
                "abstract": content.get("abstract", ""),
                "keywords": metadata.get("keywords", []),
                "introduction": content.get("introduction", ""),
                "methods": content.get("methods", ""),
                "results": content.get("results", ""),
                "discussion": content.get("discussion", ""),
                "conclusions": content.get("conclusions", ""),
                "acknowledgments": content.get("acknowledgments", ""),
                "author_contributions": content.get("author_contributions", ""),
                "data_availability": content.get("data_availability", ""),
                "references": content.get("references", []),
                "submission_date": datetime.now().strftime("%Y-%m-%d")
            }
            
            # Add journal-specific sections
            if journal_style.name.lower() == "pnas":
                context["significance_statement"] = content.get("significance_statement", "")
            elif journal_style.name.lower() == "plos_one":
                context["abstract_background"] = content.get("abstract_background", "")
                context["abstract_methods"] = content.get("abstract_methods", "")
                context["abstract_results"] = content.get("abstract_results", "")
                context["abstract_conclusions"] = content.get("abstract_conclusions", "")
            
            # Render template
            try:
                template = self.template_engine.get_template(template_name)
                formatted_manuscript = template.render(**context)
            except BiologyError as e:
                logger.warning(f"⚠️ Could not load template {template_name}: {e}")
                # Fallback to basic formatting
                formatted_manuscript = self._create_basic_format(content, metadata, journal_style)
            
            return {
                "manuscript": formatted_manuscript,
                "formatted_for_journal": journal_style.name.lower(),
                "template_used": template_name
            }
            
        except BiologyError as e:
            logger.error(f"❌ Error formatting content: {e}")
            return {
                "manuscript": f"Error formatting content: {str(e)}",
                "formatted_for_journal": journal_style.name.lower(),
                "template_used": "error"
            }
    
    def _create_basic_format(self, content: Dict[str, Any], 
                           metadata: Dict[str, Any], 
                           journal_style: JournalStyle) -> str:
        """Create basic formatted manuscript as fallback"""
        manuscript = f"""# {metadata.get('title', 'Untitled')}

**Authors**: {', '.join(metadata.get('authors', ['AXIOM Research Agent']))}

---

## Abstract

{content.get('abstract', '')}

---

## Introduction

{content.get('introduction', '')}

---

## Methods

{content.get('methods', '')}

---

## Results

{content.get('results', '')}

---

## Discussion

{content.get('discussion', '')}

---

## Conclusions

{content.get('conclusions', '')}

---

*Manuscript formatted for {journal_style.name}*
"""
        return manuscript
    
    def _calculate_word_counts(self, content: Dict[str, str]) -> Dict[str, int]:
        """Calculate word counts for different sections"""
        word_counts = {}
        
        for section, text in content.items():
            if isinstance(text, str):
                word_counts[section] = len(text.split())
        
        return word_counts
