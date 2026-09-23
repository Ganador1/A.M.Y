#!/usr/bin/env python3
"""
Router Registry System - Implementación inicial para AXIOM ATLAS

Este script implementa un sistema de registro automático de routers para reducir
el acoplamiento en main.py y mejorar el startup time mediante lazy loading.

Uso:
    python router_registry.py --analyze    # Analizar routers actuales
    python router_registry.py --create     # Crear sistema de registry
    python router_registry.py --migrate    # Migrar routers existentes
"""

import os
import sys
import json
import importlib
import inspect
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class RouterConfig:
    """Configuración para un router"""
    name: str
    module_path: str
    prefix: str
    tags: List[str]
    dependencies: List[str] = field(default_factory=list)
    is_active: bool = True
    description: str = ""


class RouterRegistry:
    """Sistema de registro y carga diferida de routers"""

    def __init__(self):
        self._routers: Dict[str, RouterConfig] = {}
        self._loaded_routers: Dict[str, Any] = {}
        self._router_configs_path = Path("config/router_registry.json")

    def register_router(self, config: RouterConfig):
        """Registrar un router en el sistema"""
        self._routers[config.name] = config
        print(f"✅ Router '{config.name}' registrado: {config.module_path}")

    def get_router(self, name: str):
        """Obtener router con lazy loading"""
        if name not in self._loaded_routers:
            if name not in self._routers:
                raise KeyError(f"Router '{name}' no encontrado en registry")

            config = self._routers[name]
            try:
                # Lazy loading del módulo
                module = importlib.import_module(config.module_path)
                router = getattr(module, 'router')

                # Verificar dependencias
                self._check_dependencies(config.dependencies)

                self._loaded_routers[name] = router
                print(f"📦 Router '{name}' cargado exitosamente")

            except Exception as e:
                print(f"❌ Error cargando router '{name}': {e}")
                raise

        return self._loaded_routers[name]

    def _check_dependencies(self, dependencies: List[str]):
        """Verificar que las dependencias estén disponibles"""
        for dep in dependencies:
            try:
                importlib.import_module(dep)
            except ImportError as e:
                print(f"⚠️ Dependencia faltante para router: {dep} - {e}")

    def save_config(self):
        """Guardar configuración de routers"""
        config_data = {
            name: {
                "module_path": config.module_path,
                "prefix": config.prefix,
                "tags": config.tags,
                "dependencies": config.dependencies,
                "is_active": config.is_active,
                "description": config.description
            }
            for name, config in self._routers.items()
        }

        self._router_configs_path.parent.mkdir(exist_ok=True)
        with open(self._router_configs_path, 'w') as f:
            json.dump(config_data, f, indent=2)

        print(f"💾 Configuración guardada en {self._router_configs_path}")

    def load_config(self):
        """Cargar configuración de routers"""
        if not self._router_configs_path.exists():
            print(f"⚠️ Archivo de configuración no encontrado: {self._router_configs_path}")
            return

        with open(self._router_configs_path, 'r') as f:
            config_data = json.load(f)

        for name, config in config_data.items():
            self._routers[name] = RouterConfig(
                name=name,
                module_path=config["module_path"],
                prefix=config["prefix"],
                tags=config["tags"],
                dependencies=config.get("dependencies", []),
                is_active=config.get("is_active", True),
                description=config.get("description", "")
            )

        print(f"📖 Configuración cargada: {len(self._routers)} routers")

    def analyze_current_routers(self) -> Dict[str, Any]:
        """Analizar routers actuales en main.py"""
        main_py_path = Path("main.py")

        if not main_py_path.exists():
            print("❌ main.py no encontrado")
            return {}

        analysis = {
            "total_routers": 0,
            "routers_found": [],
            "import_lines": [],
            "include_lines": []
        }

        with open(main_py_path, 'r') as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            line = line.strip()

            # Buscar imports de routers
            if line.startswith("from app.routers import") or "import" in line:
                if "router" in line.lower():
                    analysis["import_lines"].append({
                        "line_number": i + 1,
                        "content": line
                    })

            # Buscar include_router
            if "include_router" in line:
                analysis["include_lines"].append({
                    "line_number": i + 1,
                    "content": line
                })
                analysis["total_routers"] += 1

        return analysis

    def create_router_modules(self):
        """Crear estructura de módulos organizados"""
        base_path = Path("app/routers")

        # Crear directorios por dominio
        domains = {
            "mathematics": [
                "calculus", "algebra", "geometry", "statistics",
                "equations", "graphing", "optimization", "number_theory"
            ],
            "scientific": [
                "scientific_ai", "biomedical_nlp", "quantum_computing",
                "computational_chemistry", "materials_science"
            ],
            "infrastructure": [
                "health_checks", "metrics", "monitoring", "cache"
            ],
            "laboratory": [
                "lab_automation", "experimental_protocols", "synthesis_equipment"
            ]
        }

        for domain, routers in domains.items():
            domain_path = base_path / domain
            domain_path.mkdir(exist_ok=True)

            # Crear __init__.py para cada dominio
            init_file = domain_path / "__init__.py"
            if not init_file.exists():
                with open(init_file, 'w') as f:
                    f.write(f'''"""
{domain.title()} Routers Module

Routers relacionados con {domain.lower()}.
"""

from . import {", ".join(routers)}

__all__ = {routers}
''')

            print(f"📁 Creado módulo {domain}")

    def generate_router_config(self) -> Dict[str, RouterConfig]:
        """Generar configuración automática basada en análisis"""
        analysis = self.analyze_current_routers()

        configs = {}

        # Mapeo de routers a dominios
        domain_mapping = {
            "mathematics": [
                "calculus", "algebra", "geometry", "statistics", "equations",
                "graphing", "optimization", "number_theory", "analytical_geometry"
            ],
            "scientific": [
                "scientific_ai", "biomedical_nlp", "quantum_computing",
                "computational_chemistry", "quantum_physics"
            ],
            "infrastructure": [
                "health_checks", "metrics", "monitoring", "cache"
            ],
            "laboratory": [
                "lab_automation", "experimental_protocols", "synthesis_equipment"
            ]
        }

        for router_name in domain_mapping["mathematics"][:3]:  # Ejemplo con algunos routers
            configs[router_name] = RouterConfig(
                name=router_name,
                module_path=f"app.routers.mathematics.{router_name}",
                prefix=f"/api/{router_name.replace('_', '-')}",
                tags=[router_name.replace('_', '-')],
                description=f"Router for {router_name} operations",
                is_active=True
            )

        return configs


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(description="Router Registry System")
    parser.add_argument("--analyze", action="store_true", help="Analizar routers actuales")
    parser.add_argument("--create", action="store_true", help="Crear sistema de registry")
    parser.add_argument("--migrate", action="store_true", help="Migrar routers existentes")
    parser.add_argument("--config", action="store_true", help="Mostrar configuración actual")

    args = parser.parse_args()

    registry = RouterRegistry()

    if args.analyze:
        print("🔍 Analizando routers actuales...")
        analysis = registry.analyze_current_routers()

        print(f"📊 Routers encontrados: {analysis['total_routers']}")
        print(f"📋 Líneas de import: {len(analysis['import_lines'])}")
        print(f"🔗 Líneas de include_router: {len(analysis['include_lines'])}")

        if analysis['include_lines']:
            print("\n🔗 Routers incluidos:")
            for item in analysis['include_lines'][:5]:  # Mostrar primeros 5
                print(f"  Línea {item['line_number']}: {item['content']}")

    elif args.create:
        print("🏗️ Creando sistema de router registry...")

        # Crear estructura de módulos
        registry.create_router_modules()

        # Generar configuración
        configs = registry.generate_router_config()

        # Registrar routers
        for config in configs.values():
            registry.register_router(config)

        # Guardar configuración
        registry.save_config()

        print("✅ Sistema de router registry creado exitosamente!")

    elif args.migrate:
        print("🔄 Migrando routers existentes...")

        # Cargar configuración existente
        registry.load_config()

        # Generar configuración automática
        auto_configs = registry.generate_router_config()

        # Fusionar configuraciones
        for name, config in auto_configs.items():
            if name not in registry._routers:
                registry.register_router(config)

        # Guardar configuración actualizada
        registry.save_config()

        print("✅ Migración completada!")

    elif args.config:
        print("⚙️ Configuración actual del router registry:")

        registry.load_config()

        for name, config in registry._routers.items():
            print(f"\n🔹 {name}:")
            print(f"   📦 Module: {config.module_path}")
            print(f"   🔗 Prefix: {config.prefix}")
            print(f"   🏷️ Tags: {config.tags}")
            print(f"   📝 Description: {config.description}")
            print(f"   ✅ Active: {config.is_active}")

    else:
        print("❓ Uso:")
        print("  python router_registry.py --analyze    # Analizar routers actuales")
        print("  python router_registry.py --create     # Crear sistema de registry")
        print("  python router_registry.py --migrate    # Migrar routers existentes")
        print("  python router_registry.py --config     # Mostrar configuración")


if __name__ == "__main__":
    main()
