"""
Script de Migración para Reorganización de Dominios Científicos
Automatiza la migración de archivos existentes a la nueva estructura
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import ast
import re
from datetime import datetime


class DomainMigrator:
    """Migrador automático de archivos a la nueva estructura de dominios"""
    
    def __init__(self, app_path: str):
        self.app_path = Path(app_path)
        self.domains_path = self.app_path / "domains"
        self.backup_path = self.app_path.parent / "migration_backup"
        
        # Mapeo de archivos a dominios
        self.migration_map = {
            # Matemáticas
            "mathematics": {
                "applied": [
                    "multiscale_models.py",
                    "cross_validation_matrix.py",
                    "operational_cross_validation_matrix.py",
                    "validation_matrix_persistence.py"
                ],
                "computational": [
                    "uncertainty_quantification.py"
                ],
                "topology": [
                    # Se moveran desde mathlab/topology/
                ]
            },
            
            # Física
            "physics": {
                "plasma": [
                    "plasma_physics_service.py"
                ],
                "quantum": [
                    # Routers que se moverán
                ],
                "computational": []
            },
            
            # Química
            "chemistry": {
                "materials": [
                    "additive_manufacturing_service.py"
                ],
                "analytical": [],
                "computational": [],
                "crystallography": []
            },
            
            # Medicina (expandir existente)
            "medicine": {
                "imaging": [
                    "medical_imaging_service.py",
                    "medical_imaging_types.py",
                    "cardiac_region_models.py"
                ],
                "biomechanics": [
                    "biomechanical_models.py"
                ],
                "personalized": [],
                "genomics": []
            },
            
            # Biología
            "biology": {
                "computational": [],
                "molecular": [],
                "genomics": [],
                "biophysics": []
            },
            
            # Ingeniería
            "engineering": {
                "materials": [],
                "biomedical": [],
                "chemical": [],
                "mechanical": []
            }
        }
        
        # Mapeo de routers por dominio
        self.router_migration_map = {
            "mathematics": [
                "calculus.py", "variational_calculus.py", "differential_equations.py",
                "pde.py", "transform.py", "statistics.py", "number_theory.py",
                "number_theory_conjectures.py", "complex_analysis.py", "equations.py",
                "optimization.py", "topology.py", "topology_reports.py",
                "combinatorics.py", "arithmetic.py", "analytical_geometry.py",
                "elliptic.py", "polynomial.py"
            ],
            "physics": [
                "quantum_computing.py", "quantum_physics.py", "quantum_algorithms.py"
            ],
            "chemistry": [
                "computational_chemistry.py", "xray_crystallography.py",
                "gnome_materials.py", "differential_scanning_calorimetry.py"
            ],
            "biology": [
                "genomics.py", "advanced_genomics.py", "dnabert2.py",
                "protgpt2_router.py", "biogpt.py"
            ],
            "medicine": [
                "personalized_medicine.py", "clinicalbert.py", "alphafold3.py"
            ],
            "astronomy": [
                # Routers de astronomía si existen
            ],
            "neuroscience": [
                "neuro_simulation.py", "neuroscience_light.py"
            ],
            "engineering": [
                "lab_automation.py", "advanced_lab_automation.py",
                "synthesis_equipment.py", "experimental_toolkit.py"
            ]
        }
    
    def create_backup(self):
        """Crea un backup completo antes de la migración"""
        print("🔄 Creando backup de seguridad...")
        
        if self.backup_path.exists():
            shutil.rmtree(self.backup_path)
        
        shutil.copytree(self.app_path, self.backup_path)
        print(f"✅ Backup creado en: {self.backup_path}")
    
    def create_domain_structure(self):
        """Crea la estructura de carpetas para los dominios"""
        print("📁 Creando estructura de dominios...")
        
        self.domains_path.mkdir(exist_ok=True)
        (self.domains_path / "__init__.py").touch()
        
        # Crear dominios a partir de migration_map y router_migration_map (para cubrir casos como neuroscience/astronomy)
        domains_to_create = set(self.migration_map.keys()) | set(self.router_migration_map.keys())
        
        for domain_name in domains_to_create:
            domain_path = self.domains_path / domain_name
            domain_path.mkdir(exist_ok=True)
            (domain_path / "__init__.py").touch()
            
            # Crear subdominios si están definidos en migration_map
            subdomains = self.migration_map.get(domain_name, {})
            for subdomain_name in subdomains.keys():
                subdomain_path = domain_path / subdomain_name
                subdomain_path.mkdir(exist_ok=True)
                (subdomain_path / "__init__.py").touch()
            
            # Crear estructura estándar
            for folder in ["services", "routers", "models", "utils", "core"]:
                folder_path = domain_path / folder
                folder_path.mkdir(exist_ok=True)
                (folder_path / "__init__.py").touch()
        
        print("✅ Estructura de dominios creada")
    
    def migrate_files(self):
        """Migra archivos de la raíz de app a los dominios correspondientes"""
        print("🔀 Migrando archivos a dominios...")
        
        migrated_files = []
        
        for domain_name, subdomains in self.migration_map.items():
            for subdomain_name, files in subdomains.items():
                for file_name in files:
                    source_path = self.app_path / file_name
                    dest_path = self.domains_path / domain_name / subdomain_name / file_name
                    
                    if source_path.exists():
                        # Mover archivo
                        shutil.move(str(source_path), str(dest_path))
                        migrated_files.append((file_name, f"{domain_name}/{subdomain_name}"))
                        print(f"   📄 {file_name} → {domain_name}/{subdomain_name}/")
        
        return migrated_files
    
    def migrate_routers(self):
        """Migra routers por dominio"""
        print("🛣️  Migrando routers...")
        
        routers_path = self.app_path / "routers"
        migrated_routers = []
        
        if not routers_path.exists():
            print("❌ Carpeta routers no encontrada")
            return migrated_routers
        
        for domain_name, router_files in self.router_migration_map.items():
            domain_routers_path = self.domains_path / domain_name / "routers"
            
            for router_file in router_files:
                source_path = routers_path / router_file
                dest_path = domain_routers_path / router_file
                
                if source_path.exists():
                    shutil.copy2(str(source_path), str(dest_path))
                    migrated_routers.append((router_file, domain_name))
                    print(f"   🛣️  {router_file} → {domain_name}/routers/")
        
        return migrated_routers
    
    def migrate_services(self):
        """Migra servicios especializados"""
        print("🔧 Migrando servicios...")
        
        services_path = self.app_path / "services"
        migrated_services = []
        
        if not services_path.exists():
            print("❌ Carpeta services no encontrada")
            return migrated_services
        
        # Mapeo específico de servicios
        service_domain_map = {
            "mathematics": [
                "mathematical_computation.py", "mathematical_discovery_engine.py",
                "mathematical_exporter.py"
            ],
            "physics": [
                "physics_informed_nn_service.py", "particle_physics_service.py"
            ],
            "chemistry": [
                "computational_chemistry.py", "materials_discovery_service.py"
            ],
            "biology": [
                "genomics_service.py", "computational_biology.py"
            ],
            "medicine": [
                "personalized_medicine_service.py", "medical_imaging_service.py"
            ]
        }
        
        for domain_name, service_files in service_domain_map.items():
            domain_services_path = self.domains_path / domain_name / "services"
            
            for service_file in service_files:
                source_path = services_path / service_file
                dest_path = domain_services_path / service_file
                
                if source_path.exists():
                    shutil.copy2(str(source_path), str(dest_path))
                    migrated_services.append((service_file, domain_name))
                    print(f"   🔧 {service_file} → {domain_name}/services/")
        
        return migrated_services
    
    def update_imports(self):
        """Actualiza imports en archivos migrados"""
        print("🔄 Actualizando imports...")
        
        import_updates = 0
        
        for domain_path in self.domains_path.iterdir():
            if domain_path.is_dir() and not domain_path.name.startswith("_"):
                import_updates += self._update_imports_in_domain(domain_path)
        
        print(f"✅ {import_updates} imports actualizados")
        return import_updates
    
    def _update_imports_in_domain(self, domain_path: Path) -> int:
        """Actualiza imports en un dominio específico"""
        updates = 0
        
        for py_file in domain_path.rglob("*.py"):
            if py_file.name != "__init__.py":
                updates += self._update_file_imports(py_file)
        
        return updates
    
    def _update_file_imports(self, file_path: Path) -> int:
        """Actualiza imports en un archivo específico"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Patrones de import a actualizar
            import_patterns = [
                # app.filename → app.domains.domain.subdomain.filename
                (r'from app\.([a-zA-Z_]+) import', r'from app.domains.\1 import'),
                (r'import app\.([a-zA-Z_]+)', r'import app.domains.\1'),
                
                # app.routers.filename → app.domains.domain.routers.filename
                (r'from app\.routers\.([a-zA-Z_]+)', r'from app.domains.mathematics.routers.\1'),
                (r'import app\.routers\.([a-zA-Z_]+)', r'import app.domains.mathematics.routers.\1'),
                
                # app.services.filename → app.domains.domain.services.filename
                (r'from app\.services\.([a-zA-Z_]+)', r'from app.domains.mathematics.services.\1'),
                (r'import app\.services\.([a-zA-Z_]+)', r'import app.domains.mathematics.services.\1'),
            ]
            
            for pattern, replacement in import_patterns:
                content = re.sub(pattern, replacement, content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return 1
            
        except Exception as e:
            print(f"❌ Error actualizando imports en {file_path}: {e}")
        
        return 0
    
    def create_domain_configs(self):
        """Crea archivos de configuración para cada dominio"""
        print("⚙️  Creando configuraciones de dominio...")
        
        domain_configs = {
            "mathematics": {
                "description": "Mathematical computational services and algorithms",
                "dependencies": [],
                "subdomains": ["pure", "applied", "computational", "topology"]
            },
            "physics": {
                "description": "Physics simulation and computational services",
                "dependencies": ["mathematics"],
                "subdomains": ["classical", "quantum", "plasma", "computational"]
            },
            "chemistry": {
                "description": "Chemistry computational and analytical services",
                "dependencies": ["mathematics", "physics"],
                "subdomains": ["computational", "analytical", "materials", "crystallography"]
            },
            "biology": {
                "description": "Biology computational and molecular services",
                "dependencies": ["mathematics", "chemistry"],
                "subdomains": ["computational", "molecular", "genomics", "biophysics"]
            },
            "medicine": {
                "description": "Medical imaging and computational services",
                "dependencies": ["mathematics", "biology"],
                "subdomains": ["imaging", "biomechanics", "personalized", "genomics"]
            }
        }
        
        for domain_name, config in domain_configs.items():
            config_path = self.domains_path / domain_name / "domain_config.py"
            config_content = f'''"""
Configuración del dominio {domain_name.title()}
"""

from app.domains.registry import DomainInfo, DomainCategory

DOMAIN_INFO = DomainInfo(
    name="{domain_name}",
    category=DomainCategory.{domain_name.upper()},
    description="{config['description']}",
    version="2.0.0",
    dependencies={config['dependencies']},
    subdomains={config['subdomains']},
    enabled=True
)

# Configuración específica del dominio
DOMAIN_SETTINGS = {{
    "max_concurrent_operations": 10,
    "cache_ttl": 3600,
    "enable_gpu_acceleration": True,
    "default_precision": "float64"
}}
'''
            
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
        
        print("✅ Configuraciones de dominio creadas")
    
    def create_domain_apis(self):
        """Crea APIs consolidadas para cada dominio"""
        print("🌐 Creando APIs de dominio...")
        
        for domain_name in self.migration_map.keys():
            api_path = self.domains_path / domain_name / "routers" / "api.py"
            
            api_content = f'''"""
API Router consolidada para el dominio {domain_name.title()}
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from app.domains.{domain_name}.models import requests, responses
from app.domains.{domain_name}.services import computation, analysis
from app.core.auth import get_current_user
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/{domain_name}", tags=["{domain_name.title()}"])


@router.get("/", response_model=Dict[str, str])
async def domain_info():
    """Información básica del dominio {domain_name.title()}"""
    return {{
        "domain": "{domain_name}",
        "description": "Domain for {domain_name} computational services",
        "version": "2.0.0",
        "status": "active"
    }}


@router.get("/services", response_model=List[str])
async def list_services():
    """Lista servicios disponibles en el dominio"""
    return [
        "computation",
        "analysis", 
        "visualization"
    ]


@router.post("/compute")
async def compute_operation(
    request: requests.ComputationRequest,
    current_user = Depends(get_current_user)
):
    """Operación de computación genérica del dominio"""
    try:
        logger.info(f"Computing {{request.operation}} for user {{current_user.username}}")
        
        result = await computation.execute_computation(
            operation=request.operation,
            parameters=request.parameters,
            user_id=current_user.id
        )
        
        return responses.ComputationResponse(
            success=True,
            result=result,
            metadata={{"domain": "{domain_name}", "operation": request.operation}}
        )
        
    except Exception as e:
        logger.error(f"Computation error: {{str(e)}}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Computation failed: {{str(e)}}"
        )


@router.post("/analyze")
async def analyze_data(
    request: requests.AnalysisRequest,
    current_user = Depends(get_current_user)
):
    """Análisis de datos del dominio"""
    try:
        logger.info(f"Analyzing data for user {{current_user.username}}")
        
        result = await analysis.execute_analysis(
            data=request.data,
            analysis_type=request.analysis_type,
            parameters=request.parameters,
            user_id=current_user.id
        )
        
        return responses.AnalysisResponse(
            success=True,
            analysis_result=result,
            metadata={{"domain": "{domain_name}", "type": request.analysis_type}}
        )
        
    except Exception as e:
        logger.error(f"Analysis error: {{str(e)}}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {{str(e)}}"
        )


# Incluir sub-routers específicos del dominio
# from .specialized_router import specialized_router
# router.include_router(specialized_router, prefix="/specialized")
'''
            
            with open(api_path, 'w', encoding='utf-8') as f:
                f.write(api_content)
        
        print("✅ APIs de dominio creadas")
    
    def create_domain_models(self):
        """Crea modelos Pydantic para cada dominio"""
        print("📋 Creando modelos de dominio...")
        
        for domain_name in self.migration_map.keys():
            # Crear models/requests.py
            requests_path = self.domains_path / domain_name / "models" / "requests.py"
            requests_content = f'''"""
Modelos de request para el dominio {domain_name.title()}
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class BaseRequest(BaseModel):
    """Modelo base para requests del dominio"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_context: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None


class ComputationRequest(BaseRequest):
    """Request para operaciones de computación"""
    operation: str = Field(..., description="Tipo de operación a realizar")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    precision: str = Field(default="float64")
    use_gpu: bool = Field(default=False)


class AnalysisRequest(BaseRequest):
    """Request para análisis de datos"""
    data: Dict[str, Any] = Field(..., description="Datos a analizar")
    analysis_type: str = Field(..., description="Tipo de análisis")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    output_format: str = Field(default="json")


class ValidationRequest(BaseRequest):
    """Request para validación de datos"""
    data: Dict[str, Any] = Field(..., description="Datos a validar")
    schema_name: str = Field(..., description="Esquema de validación")
    strict_mode: bool = Field(default=True)


class ExportRequest(BaseRequest):
    """Request para exportar resultados"""
    data: Dict[str, Any] = Field(..., description="Datos a exportar")
    format: str = Field(default="json", description="Formato de exportación")
    include_metadata: bool = Field(default=True)
'''
            
            # Crear models/responses.py
            responses_path = self.domains_path / domain_name / "models" / "responses.py"
            responses_content = f'''"""
Modelos de response para el dominio {domain_name.title()}
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class BaseResponse(BaseModel):
    """Modelo base para responses del dominio"""
    success: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    execution_time: Optional[float] = None
    trace_id: Optional[str] = None


class ComputationResponse(BaseResponse):
    """Response para operaciones de computación"""
    result: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)


class AnalysisResponse(BaseResponse):
    """Response para análisis de datos"""
    analysis_result: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    statistics: Optional[Dict[str, Any]] = None
    visualizations: List[str] = Field(default_factory=list)


class ValidationResponse(BaseResponse):
    """Response para validación de datos"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    validated_data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseResponse):
    """Response para errores"""
    success: bool = False
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None
'''
            
            with open(requests_path, 'w', encoding='utf-8') as f:
                f.write(requests_content)
            
            with open(responses_path, 'w', encoding='utf-8') as f:
                f.write(responses_content)
        
        print("✅ Modelos de dominio creados")
    
    def generate_migration_report(self, migrated_files: List[Tuple[str, str]], 
                                migrated_routers: List[Tuple[str, str]], 
                                migrated_services: List[Tuple[str, str]]) -> str:
        """Genera reporte detallado de la migración"""
        report = f"""
# 📊 REPORTE DE MIGRACIÓN DE DOMINIOS CIENTÍFICOS

**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Proyecto:** ATLAS/AXIOM - Reorganización de Dominios

## 📈 Resumen Ejecutivo

- **Dominios creados:** {len(self.migration_map)}
- **Archivos migrados:** {len(migrated_files)}
- **Routers migrados:** {len(migrated_routers)}
- **Servicios migrados:** {len(migrated_services)}
- **Estructura creada:** ✅ Completa

## 🗂️ Dominios Creados

### Estructura Principal
```
app/domains/
├── mathematics/     # Matemáticas computacionales
├── physics/         # Física y simulación
├── chemistry/       # Química computacional
├── biology/         # Biología molecular
├── medicine/        # Medicina e imagen médica
├── earth_sciences/  # Ciencias de la Tierra
├── astronomy/       # Astronomía y astrofísica
├── neuroscience/    # Neurociencias
├── engineering/     # Ingeniería especializada
└── interdisciplinary/ # Disciplinas interdisciplinarias
```

## 📄 Archivos Migrados

### Archivos de la Raíz de App
"""
        
        for file_name, destination in migrated_files:
            report += f"- `{file_name}` → `domains/{destination}/`\n"
        
        report += f"""
### Routers Migrados
"""
        
        for router_file, domain in migrated_routers:
            report += f"- `{router_file}` → `domains/{domain}/routers/`\n"
        
        report += f"""
### Servicios Migrados
"""
        
        for service_file, domain in migrated_services:
            report += f"- `{service_file}` → `domains/{domain}/services/`\n"
        
        report += f"""
## 🎯 Beneficios Obtenidos

### ✅ Organización Mejorada
- **Separación clara** de dominios científicos
- **Jerarquía lógica** por disciplina y subdisciplina
- **Localización fácil** de funcionalidades

### ✅ Mantenibilidad
- **Estructura modular** por dominio
- **Dependencias claras** entre dominios
- **Configuración centralizada** por dominio

### ✅ Escalabilidad
- **Fácil adición** de nuevos dominios
- **Extensión natural** de subdominios
- **Crecimiento orgánico** de la plataforma

### ✅ Navegación Intuitiva
- **Búsqueda rápida** por dominio científico
- **API organizada** por disciplina
- **Documentación estructurada**

## 🔄 Próximos Pasos

### 1. Validación Post-Migración
- [ ] Ejecutar tests completos
- [ ] Verificar imports actualizados
- [ ] Validar APIs funcionales

### 2. Optimización
- [ ] Optimizar dependencias entre dominios
- [ ] Implementar lazy loading de dominios
- [ ] Configurar cache por dominio

### 3. Documentación
- [ ] Actualizar documentación de APIs
- [ ] Crear guías por dominio
- [ ] Documentar nuevas estructuras

## 💡 Recomendaciones

### Para Desarrolladores
1. **Usar registry de dominios** para descubrimiento automático
2. **Seguir convenciones** de nomenclatura por dominio
3. **Implementar interfaces** consistentes entre dominios

### Para Usuarios
1. **Explorar por dominio** científico de interés
2. **Usar APIs consolidadas** de cada dominio
3. **Revisar documentación** actualizada

## 📞 Soporte

- **Backup disponible en:** `{self.backup_path}`
- **Logs de migración:** Disponibles en consola
- **Reversión:** Posible desde backup completo

---
*Migración completada exitosamente* ✅
"""
        
        return report
    
    def run_migration(self) -> str:
        """Ejecuta la migración completa"""
        print("🚀 INICIANDO MIGRACIÓN DE DOMINIOS CIENTÍFICOS")
        print("=" * 50)
        
        try:
            # 1. Crear backup
            self.create_backup()
            
            # 2. Crear estructura de dominios
            self.create_domain_structure()
            
            # 3. Migrar archivos
            migrated_files = self.migrate_files()
            
            # 4. Migrar routers
            migrated_routers = self.migrate_routers()
            
            # 5. Migrar servicios
            migrated_services = self.migrate_services()
            
            # 6. Actualizar imports
            self.update_imports()
            
            # 7. Crear configuraciones
            self.create_domain_configs()
            
            # 8. Crear APIs
            self.create_domain_apis()
            
            # 9. Crear modelos
            self.create_domain_models()
            
            # 10. Generar reporte
            report = self.generate_migration_report(
                migrated_files, migrated_routers, migrated_services
            )
            
            # Guardar reporte
            report_path = self.app_path.parent / "MIGRATION_REPORT.md"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print("=" * 50)
            print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
            print(f"📋 Reporte guardado en: {report_path}")
            print("=" * 50)
            
            return str(report_path)
            
        except Exception as e:
            print(f"❌ ERROR EN MIGRACIÓN: {e}")
            print("🔄 Restaurando desde backup...")
            
            # Restaurar backup en caso de error
            if self.backup_path.exists():
                if self.domains_path.exists():
                    shutil.rmtree(self.domains_path)
                
                # Restaurar archivos migrados
                for file_name, _ in migrated_files:
                    backup_file = self.backup_path / file_name
                    dest_file = self.app_path / file_name
                    
                    if backup_file.exists() and not dest_file.exists():
                        shutil.copy2(backup_file, dest_file)
            
            raise e


# Script principal
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Uso: python migrate_domains.py <ruta_a_app>")
        sys.exit(1)
    
    app_path = sys.argv[1]
    migrator = DomainMigrator(app_path)
    
    try:
        report_path = migrator.run_migration()
        print(f"\n🎉 Migración exitosa! Reporte en: {report_path}")
        
    except Exception as e:
        print(f"\n💥 Error en migración: {e}")
        print("🔄 Se ha restaurado el estado original desde el backup")
        sys.exit(1)