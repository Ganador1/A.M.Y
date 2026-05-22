"""
Supplementary Materials Generator Service - AXIOM META 4
Automated generation of supplementary materials for scientific publications.
"""

from __future__ import annotations
import asyncio

import json
import csv
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from jinja2 import Environment, FileSystemLoader

from app.core.bootstrap_logging import logger
from app.services.base_service import BaseService
from app.exceptions.domain.biology import BiologyError
from app.types.supplementary_materials_generator_types import (
    ProcessRequestResult,
    GenerateSupplementaryPackageResult,
    GenerateExtendedMethodsResult,
    GenerateSupplementaryDataResult,
    GenerateProtocolResult,
    GenerateSupplementaryFigureResult,
    GenerateSupplementaryTableResult,
)


@dataclass
class SupplementaryMaterial:
    """Individual supplementary material item"""
    material_id: str
    title: str
    description: str
    material_type: str  # 'extended_methods', 'supplementary_data', 'protocol', 'figure', 'table'
    content: Dict[str, Any]
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SupplementaryPackage:
    """Complete supplementary materials package"""
    package_id: str
    publication_id: str
    materials: List[SupplementaryMaterial]
    package_path: Path
    manifest: Dict[str, Any]
    total_size: int = 0
    created_at: datetime = field(default_factory=datetime.now)


class SupplementaryMaterialsGenerator(BaseService):
    """Service for generating supplementary materials for publications"""
    
    def __init__(self):
        super().__init__("SupplementaryMaterialsGenerator")
        
        # Initialize template engine
        self.template_engine = self._initialize_template_engine()
        
        # Material type configurations
        self.material_types = {
            "extended_methods": {
                "template": "extended_methods.md",
                "description": "Extended methods and detailed protocols",
                "required_sections": ["overview", "detailed_protocols", "equipment", "reagents", "data_analysis"]
            },
            "supplementary_data": {
                "template": "supplementary_data.md",
                "description": "Raw data and supplementary datasets",
                "required_sections": ["data_description", "data_format", "data_access", "metadata"]
            },
            "protocol": {
                "template": "protocol.md",
                "description": "Detailed experimental protocols",
                "required_sections": ["objective", "materials", "procedure", "troubleshooting", "notes"]
            },
            "figure": {
                "template": "supplementary_figure.md",
                "description": "Supplementary figures and visualizations",
                "required_sections": ["figure_description", "data_source", "analysis_methods", "interpretation"]
            },
            "table": {
                "template": "supplementary_table.md",
                "description": "Supplementary tables and datasets",
                "required_sections": ["table_description", "data_source", "statistical_methods", "interpretation"]
            }
        }
        
        logger.info("✅ SupplementaryMaterialsGenerator initialized")
    
    def _initialize_template_engine(self) -> Environment:
        """Initialize Jinja2 template engine for supplementary materials"""
        templates_dir = Path(__file__).parent.parent / "templates" / "supplementary_materials"
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Create default templates if they don't exist
        self._create_supplementary_templates(templates_dir)
        
        return Environment(loader=FileSystemLoader(str(templates_dir)))
    
    def _create_supplementary_templates(self, templates_dir: Path):
        """Create default supplementary materials templates"""
        templates = {
            "extended_methods.md": """# Extended Methods

## Overview

{{ overview }}

## Detailed Protocols

{% for protocol in detailed_protocols %}
### {{ protocol.name }}

**Objective**: {{ protocol.objective }}

**Materials**:
{% for material in protocol.materials %}
- {{ material }}
{% endfor %}

**Procedure**:
{% for step in protocol.procedure %}
{{ loop.index }}. {{ step }}
{% endfor %}

**Expected Results**: {{ protocol.expected_results }}

**Troubleshooting**:
{% for issue in protocol.troubleshooting %}
- **{{ issue.problem }}**: {{ issue.solution }}
{% endfor %}

---
{% endfor %}

## Equipment and Software

{% for equipment in equipment_list %}
### {{ equipment.name }}
- **Type**: {{ equipment.type }}
- **Manufacturer**: {{ equipment.manufacturer }}
- **Model**: {{ equipment.model }}
- **Settings**: {{ equipment.settings }}
- **Calibration**: {{ equipment.calibration }}

{% endfor %}

## Reagents and Materials

{% for reagent in reagents_list %}
### {{ reagent.name }}
- **CAS Number**: {{ reagent.cas_number }}
- **Purity**: {{ reagent.purity }}
- **Supplier**: {{ reagent.supplier }}
- **Storage Conditions**: {{ reagent.storage }}
- **Safety Information**: {{ reagent.safety }}

{% endfor %}

## Data Analysis Methods

{{ data_analysis_methods }}

## Statistical Analysis

{{ statistical_analysis }}

## Quality Control

{{ quality_control }}

---

*Generated by AXIOM META 4 - Autonomous Scientific Discovery Platform*
""",
            
            "supplementary_data.md": """# Supplementary Data

## Data Description

{{ data_description }}

## Data Format

{{ data_format }}

## Data Access

{{ data_access }}

## Metadata

{% for dataset in datasets %}
### {{ dataset.name }}
- **Type**: {{ dataset.type }}
- **Size**: {{ dataset.size }}
- **Format**: {{ dataset.format }}
- **Description**: {{ dataset.description }}
- **Hash**: `{{ dataset.hash }}`
- **Access URL**: {{ dataset.access_url }}

{% endfor %}

## Data Processing Pipeline

{{ data_processing_pipeline }}

## Validation and Quality Control

{{ validation_methods }}

---

*Generated by AXIOM META 4 - Autonomous Scientific Discovery Platform*
""",
            
            "protocol.md": """# Experimental Protocol

## Objective

{{ objective }}

## Materials

{% for material in materials %}
- {{ material.name }} ({{ material.specifications }})
{% endfor %}

## Equipment

{% for equipment in equipment %}
- {{ equipment.name }} ({{ equipment.specifications }})
{% endfor %}

## Procedure

{% for step in procedure %}
### Step {{ loop.index }}: {{ step.title }}

{{ step.description }}

**Duration**: {{ step.duration }}
**Temperature**: {{ step.temperature }}
**Notes**: {{ step.notes }}

---
{% endfor %}

## Troubleshooting

{% for issue in troubleshooting %}
### {{ issue.problem }}

**Symptoms**: {{ issue.symptoms }}
**Cause**: {{ issue.cause }}
**Solution**: {{ issue.solution }}
**Prevention**: {{ issue.prevention }}

---
{% endfor %}

## Notes and Considerations

{{ notes }}

## Safety Information

{{ safety_information }}

---

*Generated by AXIOM META 4 - Autonomous Scientific Discovery Platform*
""",
            
            "supplementary_figure.md": """# Supplementary Figure {{ figure_number }}: {{ figure_title }}

## Figure Description

{{ figure_description }}

## Data Source

{{ data_source }}

## Analysis Methods

{{ analysis_methods }}

## Interpretation

{{ interpretation }}

## Technical Details

- **Software Used**: {{ software_used }}
- **Parameters**: {{ parameters }}
- **Resolution**: {{ resolution }}
- **Color Scheme**: {{ color_scheme }}

## Related Data

{% for related_data in related_data %}
- {{ related_data }}
{% endfor %}

---

*Generated by AXIOM META 4 - Autonomous Scientific Discovery Platform*
""",
            
            "supplementary_table.md": """# Supplementary Table {{ table_number }}: {{ table_title }}

## Table Description

{{ table_description }}

## Data Source

{{ data_source }}

## Statistical Methods

{{ statistical_methods }}

## Interpretation

{{ interpretation }}

## Table Data

{{ table_data }}

## Notes

{{ notes }}

---

*Generated by AXIOM META 4 - Autonomous Scientific Discovery Platform*
"""
        }
        
        for filename, content in templates.items():
            template_path = templates_dir / filename
            if not template_path.exists():
                template_path.write_text(content)
                logger.info(f"✅ Created supplementary template: {filename}")
    
    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Process supplementary materials generation requests"""
        try:
            action = request_data.get("action", "")
            
            if action == "generate_supplementary_package":
                return await self.generate_supplementary_package(request_data)
            elif action == "generate_extended_methods":
                return await self.generate_extended_methods(request_data)
            elif action == "generate_supplementary_data":
                return await self.generate_supplementary_data(request_data)
            elif action == "generate_protocol":
                return await self.generate_protocol(request_data)
            elif action == "generate_supplementary_figure":
                return await self.generate_supplementary_figure(request_data)
            elif action == "generate_supplementary_table":
                return await self.generate_supplementary_table(request_data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": [
                        "generate_supplementary_package", "generate_extended_methods",
                        "generate_supplementary_data", "generate_protocol",
                        "generate_supplementary_figure", "generate_supplementary_table"
                    ]
                }
                
        except BiologyError as e:
            return self.handle_error(e, "process_request")
    
    async def generate_supplementary_package(self, request_data: GenerateSupplementaryPackageResult) -> GenerateSupplementaryPackageResult:
        """Generate complete supplementary materials package"""
        try:
            publication_id = request_data.get("publication_id", "unknown")
            materials_config = request_data.get("materials_config", {})
            output_path = request_data.get("output_path", "./supplementary_materials")
            
            # Generate package ID
            package_id = f"supp_{publication_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create output directory
            package_path = Path(output_path) / package_id
            package_path.mkdir(parents=True, exist_ok=True)
            
            # Generate materials
            materials = []
            total_size = 0
            
            # Generate extended methods if requested
            if materials_config.get("include_extended_methods", True):
                extended_methods = await self.generate_extended_methods({
                    "action": "generate_extended_methods",
                    "publication_id": publication_id,
                    "experimental_data": request_data.get("experimental_data", {}),
                    "output_path": str(package_path)
                })
                
                if extended_methods["success"]:
                    materials.append(extended_methods["material"])
                    total_size += extended_methods["material"].file_size or 0
            
            # Generate supplementary data if requested
            if materials_config.get("include_supplementary_data", True):
                supplementary_data = await self.generate_supplementary_data({
                    "action": "generate_supplementary_data",
                    "publication_id": publication_id,
                    "data_sources": request_data.get("data_sources", {}),
                    "output_path": str(package_path)
                })
                
                if supplementary_data["success"]:
                    materials.append(supplementary_data["material"])
                    total_size += supplementary_data["material"].file_size or 0
            
            # Generate protocols if requested
            if materials_config.get("include_protocols", True):
                protocols = await self.generate_protocol({
                    "action": "generate_protocol",
                    "publication_id": publication_id,
                    "protocol_data": request_data.get("protocol_data", {}),
                    "output_path": str(package_path)
                })
                
                if protocols["success"]:
                    materials.append(protocols["material"])
                    total_size += protocols["material"].file_size or 0
            
            # Generate supplementary figures if requested
            if materials_config.get("include_supplementary_figures", True):
                figures_count = materials_config.get("figures_count", 3)
                for i in range(figures_count):
                    figure_data = request_data.get("figure_data", {}).get(f"figure_{i+1}", {})
                    if figure_data:
                        supplementary_figure = await self.generate_supplementary_figure({
                            "action": "generate_supplementary_figure",
                            "publication_id": publication_id,
                            "figure_number": i + 1,
                            "figure_data": figure_data,
                            "output_path": str(package_path)
                        })
                        
                        if supplementary_figure["success"]:
                            materials.append(supplementary_figure["material"])
                            total_size += supplementary_figure["material"].file_size or 0
            
            # Generate supplementary tables if requested
            if materials_config.get("include_supplementary_tables", True):
                tables_count = materials_config.get("tables_count", 2)
                for i in range(tables_count):
                    table_data = request_data.get("table_data", {}).get(f"table_{i+1}", {})
                    if table_data:
                        supplementary_table = await self.generate_supplementary_table({
                            "action": "generate_supplementary_table",
                            "publication_id": publication_id,
                            "table_number": i + 1,
                            "table_data": table_data,
                            "output_path": str(package_path)
                        })
                        
                        if supplementary_table["success"]:
                            materials.append(supplementary_table["material"])
                            total_size += supplementary_table["material"].file_size or 0
            
            # Create package manifest
            manifest = {
                "package_id": package_id,
                "publication_id": publication_id,
                "created_at": datetime.now().isoformat(),
                "total_materials": len(materials),
                "total_size": total_size,
                "materials": [
                    {
                        "material_id": material.material_id,
                        "title": material.title,
                        "type": material.material_type,
                        "file_path": material.file_path,
                        "file_size": material.file_size
                    } for material in materials
                ]
            }
            
            # Write manifest
            (package_path / "manifest.json").write_text(json.dumps(manifest, indent=2))
            
            # Create package
            package = SupplementaryPackage(
                package_id=package_id,
                publication_id=publication_id,
                materials=materials,
                package_path=package_path,
                manifest=manifest,
                total_size=total_size
            )
            
            logger.info(f"✅ Generated supplementary package: {package_id} with {len(materials)} materials")
            
            return {
                "success": True,
                "package_id": package_id,
                "package_path": str(package_path),
                "total_materials": len(materials),
                "total_size": total_size,
                "materials": [material.__dict__ for material in materials],
                "manifest": manifest
            }
            
        except BiologyError as e:
            return self.handle_error(e, "generate_supplementary_package")
    
    async def generate_extended_methods(self, request_data: GenerateExtendedMethodsResult) -> GenerateExtendedMethodsResult:
        """Generate extended methods document"""
        try:
            publication_id = request_data.get("publication_id", "unknown")
            experimental_data = request_data.get("experimental_data", {})
            output_path = request_data.get("output_path", "./supplementary_materials")
            
            # Generate material ID
            material_id = f"ext_methods_{publication_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create output directory
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Prepare template context
            context = {
                "overview": experimental_data.get("overview", "Detailed experimental methods and protocols used in this study."),
                "detailed_protocols": experimental_data.get("protocols", [
                    {
                        "name": "Sample Preparation Protocol",
                        "objective": "Prepare samples for analysis",
                        "materials": ["Sample material", "Buffer solution", "Reagents"],
                        "procedure": ["Clean sample", "Add buffer", "Incubate", "Analyze"],
                        "expected_results": "Prepared samples ready for analysis",
                        "troubleshooting": [
                            {"problem": "Sample contamination", "solution": "Use sterile techniques"},
                            {"problem": "Buffer precipitation", "solution": "Filter buffer before use"}
                        ]
                    }
                ]),
                "equipment_list": experimental_data.get("equipment", [
                    {
                        "name": "Analytical Balance",
                        "type": "Laboratory Equipment",
                        "manufacturer": "AXIOM Lab",
                        "model": "AL-2000",
                        "settings": "Standard analytical mode",
                        "calibration": "Daily calibration with certified weights"
                    }
                ]),
                "reagents_list": experimental_data.get("reagents", [
                    {
                        "name": "Buffer Solution",
                        "cas_number": "N/A",
                        "purity": "Analytical Grade",
                        "supplier": "AXIOM Chemicals",
                        "storage": "Room temperature",
                        "safety": "Standard laboratory safety protocols"
                    }
                ]),
                "data_analysis_methods": experimental_data.get("data_analysis", "Standard statistical analysis methods were employed."),
                "statistical_analysis": experimental_data.get("statistical_analysis", "Data were analyzed using appropriate statistical tests."),
                "quality_control": experimental_data.get("quality_control", "Quality control measures were implemented throughout the study.")
            }
            
            # Render template
            template = self.template_engine.get_template("extended_methods.md")
            content = template.render(**context)
            
            # Write file
            filename = f"{material_id}.md"
            file_path = output_dir / filename
            file_path.write_text(content)
            
            # Create material
            material = SupplementaryMaterial(
                material_id=material_id,
                title="Extended Methods",
                description="Detailed experimental methods and protocols",
                material_type="extended_methods",
                content=context,
                file_path=str(file_path),
                file_size=file_path.stat().st_size
            )
            
            logger.info(f"✅ Generated extended methods: {filename}")
            
            return {
                "success": True,
                "material": material,
                "filename": filename,
                "file_path": str(file_path),
                "file_size": material.file_size
            }
            
        except BiologyError as e:
            return self.handle_error(e, "generate_extended_methods")
    
    async def generate_supplementary_data(self, request_data: GenerateSupplementaryDataResult) -> GenerateSupplementaryDataResult:
        """Generate supplementary data document"""
        try:
            publication_id = request_data.get("publication_id", "unknown")
            data_sources = request_data.get("data_sources", {})
            output_path = request_data.get("output_path", "./supplementary_materials")
            
            # Generate material ID
            material_id = f"supp_data_{publication_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create output directory
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Prepare template context
            context = {
                "data_description": data_sources.get("description", "Supplementary data and datasets used in this study."),
                "data_format": data_sources.get("format", "CSV, JSON, and other standard formats"),
                "data_access": data_sources.get("access", "Data available through AXIOM platform"),
                "datasets": data_sources.get("datasets", [
                    {
                        "name": "Primary Dataset",
                        "type": "Experimental Data",
                        "size": "1.2 MB",
                        "format": "CSV",
                        "description": "Main experimental dataset",
                        "hash": "abc123def456",
                        "access_url": "https://axiom.ai/data/primary_dataset.csv"
                    }
                ]),
                "data_processing_pipeline": data_sources.get("processing_pipeline", "Standard data processing pipeline was used."),
                "validation_methods": data_sources.get("validation_methods", "Data validation was performed using standard methods.")
            }
            
            # Render template
            template = self.template_engine.get_template("supplementary_data.md")
            content = template.render(**context)
            
            # Write file
            filename = f"{material_id}.md"
            file_path = output_dir / filename
            file_path.write_text(content)
            
            # Create material
            material = SupplementaryMaterial(
                material_id=material_id,
                title="Supplementary Data",
                description="Raw data and supplementary datasets",
                material_type="supplementary_data",
                content=context,
                file_path=str(file_path),
                file_size=file_path.stat().st_size
            )
            
            logger.info(f"✅ Generated supplementary data: {filename}")
            
            return {
                "success": True,
                "material": material,
                "filename": filename,
                "file_path": str(file_path),
                "file_size": material.file_size
            }
            
        except BiologyError as e:
            return self.handle_error(e, "generate_supplementary_data")
    
    async def generate_protocol(self, request_data: GenerateProtocolResult) -> GenerateProtocolResult:
        """Generate detailed experimental protocol"""
        try:
            publication_id = request_data.get("publication_id", "unknown")
            protocol_data = request_data.get("protocol_data", {})
            output_path = request_data.get("output_path", "./supplementary_materials")
            
            # Generate material ID
            material_id = f"protocol_{publication_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create output directory
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Prepare template context
            context = {
                "objective": protocol_data.get("objective", "Detailed experimental protocol for this study"),
                "materials": protocol_data.get("materials", [
                    {"name": "Sample Material", "specifications": "High purity"},
                    {"name": "Buffer Solution", "specifications": "pH 7.4"}
                ]),
                "equipment": protocol_data.get("equipment", [
                    {"name": "Analytical Balance", "specifications": "0.1 mg precision"},
                    {"name": "Incubator", "specifications": "37°C ± 0.5°C"}
                ]),
                "procedure": protocol_data.get("procedure", [
                    {
                        "title": "Sample Preparation",
                        "description": "Prepare samples according to standard protocol",
                        "duration": "30 minutes",
                        "temperature": "Room temperature",
                        "notes": "Use sterile techniques"
                    }
                ]),
                "troubleshooting": protocol_data.get("troubleshooting", [
                    {
                        "problem": "Sample contamination",
                        "symptoms": "Unexpected results",
                        "cause": "Improper sterile technique",
                        "solution": "Use sterile techniques and clean equipment",
                        "prevention": "Regular equipment maintenance"
                    }
                ]),
                "notes": protocol_data.get("notes", "Additional notes and considerations"),
                "safety_information": protocol_data.get("safety_information", "Follow standard laboratory safety protocols")
            }
            
            # Render template
            template = self.template_engine.get_template("protocol.md")
            content = template.render(**context)
            
            # Write file
            filename = f"{material_id}.md"
            file_path = output_dir / filename
            file_path.write_text(content)
            
            # Create material
            material = SupplementaryMaterial(
                material_id=material_id,
                title="Experimental Protocol",
                description="Detailed experimental protocol",
                material_type="protocol",
                content=context,
                file_path=str(file_path),
                file_size=file_path.stat().st_size
            )
            
            logger.info(f"✅ Generated protocol: {filename}")
            
            return {
                "success": True,
                "material": material,
                "filename": filename,
                "file_path": str(file_path),
                "file_size": material.file_size
            }
            
        except BiologyError as e:
            return self.handle_error(e, "generate_protocol")
    
    async def generate_supplementary_figure(self, request_data: GenerateSupplementaryFigureResult) -> GenerateSupplementaryFigureResult:
        """Generate supplementary figure document"""
        try:
            publication_id = request_data.get("publication_id", "unknown")
            figure_number = request_data.get("figure_number", 1)
            figure_data = request_data.get("figure_data", {})
            output_path = request_data.get("output_path", "./supplementary_materials")
            
            # Generate material ID
            material_id = f"supp_fig_{figure_number}_{publication_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create output directory
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Prepare template context
            context = {
                "figure_number": figure_number,
                "figure_title": figure_data.get("title", f"Supplementary Figure {figure_number}"),
                "figure_description": figure_data.get("description", f"Description of supplementary figure {figure_number}"),
                "data_source": figure_data.get("data_source", "Experimental data from this study"),
                "analysis_methods": figure_data.get("analysis_methods", "Standard analysis methods"),
                "interpretation": figure_data.get("interpretation", "Interpretation of the figure"),
                "software_used": figure_data.get("software_used", "AXIOM Analysis Software"),
                "parameters": figure_data.get("parameters", "Standard parameters"),
                "resolution": figure_data.get("resolution", "300 DPI"),
                "color_scheme": figure_data.get("color_scheme", "Standard scientific color scheme"),
                "related_data": figure_data.get("related_data", ["Primary dataset", "Analysis results"])
            }
            
            # Render template
            template = self.template_engine.get_template("supplementary_figure.md")
            content = template.render(**context)
            
            # Write file
            filename = f"{material_id}.md"
            file_path = output_dir / filename
            file_path.write_text(content)
            
            # Create material
            material = SupplementaryMaterial(
                material_id=material_id,
                title=f"Supplementary Figure {figure_number}",
                description=f"Supplementary figure {figure_number} documentation",
                material_type="figure",
                content=context,
                file_path=str(file_path),
                file_size=file_path.stat().st_size
            )
            
            logger.info(f"✅ Generated supplementary figure: {filename}")
            
            return {
                "success": True,
                "material": material,
                "filename": filename,
                "file_path": str(file_path),
                "file_size": material.file_size
            }
            
        except BiologyError as e:
            return self.handle_error(e, "generate_supplementary_figure")
    
    async def generate_supplementary_table(self, request_data: GenerateSupplementaryTableResult) -> GenerateSupplementaryTableResult:
        """Generate supplementary table document"""
        try:
            publication_id = request_data.get("publication_id", "unknown")
            table_number = request_data.get("table_number", 1)
            table_data = request_data.get("table_data", {})
            output_path = request_data.get("output_path", "./supplementary_materials")
            
            # Generate material ID
            material_id = f"supp_table_{table_number}_{publication_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create output directory
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Prepare template context
            context = {
                "table_number": table_number,
                "table_title": table_data.get("title", f"Supplementary Table {table_number}"),
                "table_description": table_data.get("description", f"Description of supplementary table {table_number}"),
                "data_source": table_data.get("data_source", "Experimental data from this study"),
                "statistical_methods": table_data.get("statistical_methods", "Standard statistical methods"),
                "interpretation": table_data.get("interpretation", "Interpretation of the table"),
                "table_data": table_data.get("table_data", "Table data will be included here"),
                "notes": table_data.get("notes", "Additional notes about the table")
            }
            
            # Render template
            template = self.template_engine.get_template("supplementary_table.md")
            content = template.render(**context)
            
            # Write file
            filename = f"{material_id}.md"
            file_path = output_dir / filename
            file_path.write_text(content)
            
            # Create material
            material = SupplementaryMaterial(
                material_id=material_id,
                title=f"Supplementary Table {table_number}",
                description=f"Supplementary table {table_number} documentation",
                material_type="table",
                content=context,
                file_path=str(file_path),
                file_size=file_path.stat().st_size
            )
            
            logger.info(f"✅ Generated supplementary table: {filename}")
            
            return {
                "success": True,
                "material": material,
                "filename": filename,
                "file_path": str(file_path),
                "file_size": material.file_size
            }
            
        except BiologyError as e:
            return self.handle_error(e, "generate_supplementary_table")
