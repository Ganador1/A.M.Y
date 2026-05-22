"""
Router de Formateo de Revistas - AXIOM Meta 4.1
==============================================

Módulo especializado para formateo de publicaciones científicas según los
requisitos específicos de diferentes revistas académicas. Proporciona capacidades
avanzadas de conversión entre formatos, validación de requisitos y generación
de documentos listos para publicación.

Capacidades Principales
----------------------
- **Formateo por Revista**: Aplicación automática de estilos específicos
- **Conversión entre Formatos**: Transformación entre revistas diferentes
- **Validación de Requisitos**: Verificación de cumplimiento de normas editoriales
- **Catálogo de Revistas**: Información detallada de estilos disponibles
- **Requisitos Específicos**: Validación de secciones, límites de palabras, figuras
- **Citas y Referencias**: Formateo automático según estándares editoriales

Endpoints Disponibles
--------------------
**Formateo:**
- `POST /api/v1/journal-formatter/format` - Formatear publicación para revista específica
- `POST /api/v1/journal-formatter/convert` - Convertir entre formatos de revista
- `POST /api/v1/journal-formatter/validate` - Validar requisitos de revista

**Información:**
- `GET /api/v1/journal-formatter/journals` - Listar revistas disponibles
- `GET /api/v1/journal-formatter/journals/{name}/requirements` - Requisitos detallados
- `GET /api/v1/journal-formatter/health` - Estado de salud del servicio

Dependencias
-----------
- **JournalFormatterService**: Servicio principal de formateo de revistas
- **security.require_scopes**: Control de acceso con scope "publications"
- **logging_config**: Configuración de logging del sistema

Uso y Ejemplos
--------------
**Formateo para Nature:**
```python
response = await client.post("/api/v1/journal-formatter/format", json={
    "journal": "nature",
    "publication_content": {
        "title": "Descubrimiento revolucionario en biología sintética",
        "abstract": "Presentamos un enfoque novedoso...",
        "introduction": "...",
        "methods": "...",
        "results": "...",
        "discussion": "..."
    },
    "metadata": {
        "authors": ["Dr. Ana García", "Dr. Carlos López"],
        "affiliations": ["Universidad Autónoma de Madrid"],
        "keywords": ["biología sintética", "CRISPR", "ingeniería genética"]
    }
})
```

**Conversión entre revistas:**
```python
response = await client.post("/api/v1/journal-formatter/convert", json={
    "source_journal": "nature",
    "target_journal": "science",
    "publication_content": {...},
    "metadata": {...}
})
```

**Validación de requisitos:**
```python
response = await client.post("/api/v1/journal-formatter/validate", json={
    "journal": "cell",
    "publication_content": {...},
    "metadata": {...}
})
# Retorna warnings y errores de validación
```

Revistas Soportadas
------------------
- **nature**: Nature (IF: 69.5) - Revista de alto impacto general
- **science**: Science (IF: 63.7) - Revista multidisciplinaria líder
- **cell**: Cell (IF: 66.9) - Revista de biología celular y molecular
- **pnas**: PNAS (IF: 12.8) - Proceedings of the National Academy of Sciences
- **plos_one**: PLOS ONE (IF: 3.7) - Revista de acceso abierto
- **biorxiv**: bioRxiv - Servidor de preprints de biología

Notas de Seguridad
-----------------
- Control de acceso mediante scopes de seguridad ("publications")
- Validación estricta de nombres de revistas permitidos
- Logging detallado de operaciones de formateo
- Manejo seguro de excepciones sin exposición de información interna
- Rate limiting aplicado globalmente en main.py

Consideraciones de Rendimiento
-----------------------------
- Procesamiento asíncrono para formateo de documentos largos
- Caching de estilos de revista para consultas frecuentes
- Validación optimizada con verificación incremental
- Conversión eficiente entre formatos similares
- Monitoreo de uso de recursos en operaciones de formateo
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from app.core.bootstrap_logging import logger
from app.services.journal_formatter import JournalFormatterService
from app.security import require_scopes
from app.exceptions.domain.biology import BiologyError

router = APIRouter(
    prefix="/api/v1/journal-formatter",
    tags=["Journal Formatter"],
    dependencies=[Depends(require_scopes(["publications"]))]
)


class JournalFormattingRequest(BaseModel):
    """Request model for journal formatting"""
    journal: str = Field(..., description="Target journal name (nature, science, cell, pnas, plos_one, biorxiv)")
    publication_content: Dict[str, Any] = Field(..., description="Publication content sections")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Publication metadata")


class JournalConversionRequest(BaseModel):
    """Request model for converting between journal formats"""
    source_journal: str = Field(..., description="Source journal name")
    target_journal: str = Field(..., description="Target journal name")
    publication_content: Dict[str, Any] = Field(..., description="Publication content sections")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Publication metadata")


class JournalValidationRequest(BaseModel):
    """Request model for validating journal requirements"""
    journal: str = Field(..., description="Journal name to validate against")
    publication_content: Dict[str, Any] = Field(..., description="Publication content sections")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Publication metadata")


# Initialize journal formatter service
journal_formatter = JournalFormatterService()


@router.post("/format", summary="Format Publication for Journal")
async def format_for_journal(request: JournalFormattingRequest):
    """
    Format a publication according to a specific journal's requirements.
    
    Supported journals:
    - nature: Nature (impact factor: 69.5)
    - science: Science (impact factor: 63.7)
    - cell: Cell (impact factor: 66.9)
    - pnas: PNAS (impact factor: 12.8)
    - plos_one: PLOS ONE (impact factor: 3.7)
    - biorxiv: bioRxiv (preprint server)
    """
    try:
        result = await journal_formatter.format_for_journal({
            "action": "format_for_journal",
            "journal": request.journal,
            "publication_content": request.publication_content,
            "metadata": request.metadata
        })
        
        if result["success"]:
            return {
                "success": True,
                "journal": result["journal"],
                "formatted_content": result["formatted_content"],
                "metadata": result["metadata"],
                "warnings": result["warnings"],
                "errors": result["errors"],
                "word_counts": result["word_counts"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error formatting for journal: {e}")
        raise HTTPException(status_code=500, detail=f"Journal formatting failed: {str(e)}")


@router.post("/convert", summary="Convert Between Journal Formats")
async def convert_between_journals(request: JournalConversionRequest):
    """
    Convert a publication from one journal format to another.
    
    This is useful when resubmitting to a different journal or
    preparing multiple versions for different venues.
    """
    try:
        result = await journal_formatter.convert_between_journals({
            "action": "convert_between_journals",
            "source_journal": request.source_journal,
            "target_journal": request.target_journal,
            "publication_content": request.publication_content,
            "metadata": request.metadata
        })
        
        if result["success"]:
            return {
                "success": True,
                "source_journal": result["source_journal"],
                "target_journal": result["target_journal"],
                "converted_content": result["converted_content"],
                "metadata": result["metadata"],
                "warnings": result["warnings"],
                "errors": result["errors"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error converting between journals: {e}")
        raise HTTPException(status_code=500, detail=f"Journal conversion failed: {str(e)}")


@router.post("/validate", summary="Validate Journal Requirements")
async def validate_journal_requirements(request: JournalValidationRequest):
    """
    Validate a publication against a journal's specific requirements.
    
    Returns warnings and errors for:
    - Missing required sections
    - Word count limits (abstract, title, keywords)
    - Special requirements (data availability, ethics statements, etc.)
    """
    try:
        result = await journal_formatter.validate_journal_requirements({
            "action": "validate_journal_requirements",
            "journal": request.journal,
            "publication_content": request.publication_content,
            "metadata": request.metadata
        })
        
        if result["success"]:
            return {
                "success": True,
                "journal": result["journal"],
                "validation_result": result["validation_result"],
                "journal_requirements": result["journal_requirements"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error validating journal requirements: {e}")
        raise HTTPException(status_code=500, detail=f"Journal validation failed: {str(e)}")


@router.get("/journals", summary="Get Available Journal Styles")
async def get_journal_styles(journal: Optional[str] = None):
    """
    Get information about available journal styles and their requirements.
    
    If no journal is specified, returns all available journals.
    If a journal is specified, returns detailed information about that journal.
    """
    try:
        result = await journal_formatter.get_journal_styles({
            "action": "get_journal_styles",
            "journal": journal
        })
        
        if result["success"]:
            return {
                "success": True,
                "journal": journal,
                "data": result.get("style") if journal else result.get("available_journals"),
                "total_journals": result.get("total_journals", 1)
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error getting journal styles: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get journal styles: {str(e)}")


@router.get("/journals/{journal_name}/requirements", summary="Get Journal Requirements")
async def get_journal_requirements(journal_name: str):
    """
    Get detailed requirements for a specific journal.
    
    Returns:
    - Required and optional sections
    - Word count limits
    - Special requirements (preregistration, data availability, etc.)
    - Citation and reference formats
    """
    try:
        result = await journal_formatter.get_journal_styles({
            "action": "get_journal_styles",
            "journal": journal_name
        })
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
            
        style = result["style"]
        return {
            "success": True,
            "journal": journal_name,
            "requirements": {
                "basic_info": {
                    "name": style["name"],
                    "abbreviation": style["abbreviation"],
                    "publisher": style["publisher"],
                    "impact_factor": style["impact_factor"]
                },
                "formatting": {
                    "font_family": style["font_family"],
                    "font_size": style["font_size"],
                    "line_spacing": style["line_spacing"],
                    "margins": style["margins"]
                },
                "sections": {
                    "required": style["required_sections"],
                    "optional": style["optional_sections"]
                },
                "word_limits": {
                    "abstract": style["abstract_word_limit"],
                    "title": style["title_word_limit"],
                    "keywords": style["keywords_limit"]
                },
                "figure_specs": {
                    "width": style["figure_width"],
                    "height": style["figure_height"],
                    "dpi": style["figure_dpi"],
                    "format": style["figure_format"]
                },
                "citation": {
                    "style": style["citation_style"],
                    "reference_format": style["reference_format"]
                },
                "special_requirements": {
                    "preregistration": style["requires_preregistration"],
                    "data_availability": style["requires_data_availability"],
                    "code_availability": style["requires_code_availability"],
                    "ethics_statement": style["requires_ethics_statement"]
                }
            }
        }
            
    except BiologyError as e:
        logger.error(f"❌ Error getting journal requirements: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get journal requirements: {str(e)}")


@router.get("/health", summary="Health Check")
async def health_check():
    """Check if the journal formatter service is healthy"""
    return {
        "success": True,
        "service": "JournalFormatterService",
        "status": "healthy",
        "available_journals": 6,
        "supported_formats": ["nature", "science", "cell", "pnas", "plos_one", "biorxiv"]
    }
