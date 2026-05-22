#!/usr/bin/env python3
"""verify_imports
Script para verificar importación de:

1. Todos los módulos bajo `app/` (core obligatorio)
2. Módulos bajo `ingestion/` (anteriormente fuera del scan principal)
3. Scripts raíz críticos (main, comprehensive_analysis, generate_final_report)

Características añadidas:
 - Parámetro CLI `--skip-optional` para omitir ingestion y scripts raíz si se desea rapidez.
 - Reporte separado de módulos opcionales para visibilidad clara.
 - Posibilidad de extender fácilmente añadiendo rutas en las listas correspondientes.
"""

import sys
import importlib
import traceback
from pathlib import Path
from typing import List, Tuple
import os

def collect_package_modules(package: str, base_dir: str) -> List[str]:
    """Recorrer un directorio base y devolver nombres de módulos importables para un paquete.

    Args:
        package: prefijo del paquete lógico (e.g. 'app', 'ingestion').
        base_dir: ruta en filesystem donde viven los archivos (e.g. 'app').
    """
    root = Path(base_dir)
    if not root.exists():
        return []
    modules: List[str] = []
    for py_file in root.rglob('*.py'):
        if py_file.name.startswith('__'):
            continue
        rel_path = py_file.relative_to(root)
        module_name = f'{package}.{rel_path.with_suffix("").as_posix().replace("/", ".")}'
        modules.append(module_name)
    return sorted(modules)


def get_all_app_modules() -> List[str]:
    """Backward compatible wrapper para mantener nombre de función existente."""
    return collect_package_modules('app', 'app')


def get_ingestion_modules() -> List[str]:
    return collect_package_modules('ingestion', 'ingestion')


ROOT_SCRIPTS = [
    # Scripts raíz críticos que deben ser importables. Se listan sin sufijo .py
    'main',
    'comprehensive_analysis',
    'generate_final_report',
]

def test_module_import(module_name: str, verbose: bool = False) -> Tuple[bool, str | None]:
    """Intentar importar un módulo devolviendo estado y error opcional."""
    try:
        importlib.import_module(module_name)
        return True, None
    except Exception as e:  # noqa: BLE001 - queremos capturar cualquier excepción para el reporte
        error_msg = f'{type(e).__name__}: {str(e)}'
        if verbose:
            error_msg += f'\n{traceback.format_exc()}'
        return False, error_msg

def main(argv: list[str] | None = None) -> bool:
    argv = argv or sys.argv[1:]
    include_optional = True
    if '--skip-optional' in argv:
        include_optional = False

    core_modules = get_all_app_modules()
    optional_modules: list[str] = []
    root_script_modules: list[str] = []

    if include_optional:
        optional_modules = get_ingestion_modules()
        # Scripts raíz: intentar importarlos como módulos (sin .py)
        for script in ROOT_SCRIPTS:
            # Evitar duplicados si nombre coincide con paquete
            if Path(f'{script}.py').exists():
                root_script_modules.append(script)

    all_modules = core_modules + optional_modules + root_script_modules

    print('🔍 Verificando módulos...')
    print('=' * 80)
    print(f'   Núcleo (app/): {len(core_modules)}')
    if include_optional:
        print(f'   Ingestion: {len(optional_modules)}')
        print(f'   Scripts raíz: {len(root_script_modules)}')
    else:
        print('   (Opcionales omitidos)')
    print('-' * 80)

    success_count = 0
    errors: list[tuple[str, str]] = []

    # Señal a módulos para que omitan inicializaciones pesadas durante la verificación
    os.environ.setdefault('AXIOM_SKIP_AUTOINIT', '1')

    for i, module_name in enumerate(all_modules, 1):
        success, error = test_module_import(module_name)
        if success:
            success_count += 1
            print(f'{i:3d}. ✅ {module_name}')
        else:
            print(f'{i:3d}. ❌ {module_name}')
            print(f'     {error}')
            errors.append((module_name, error))

    print('\n' + '=' * 80)
    print(f'📊 RESULTADO FINAL GLOBAL: {success_count}/{len(all_modules)} módulos importados')
    if all_modules:
        print(f'📈 Tasa de éxito: {success_count/len(all_modules)*100:.2f}%')

    # Resumen segmentado
    if include_optional:
        print('\n📂 Desglose:')
        def count_ok(candidates: list[str]) -> int:
            error_names = {em for em, _ in errors}
            return sum(1 for m in candidates if m not in error_names)
        print(f'   • app/: {count_ok(core_modules)}/{len(core_modules)}')
        if optional_modules:
            print(f'   • ingestion/: {count_ok(optional_modules)}/{len(optional_modules)}')
        if root_script_modules:
            print(f'   • scripts raíz: {count_ok(root_script_modules)}/{len(root_script_modules)}')

    if errors:
        print(f'\n❌ {len(errors)} módulos con errores:')
        for module, error in errors[:15]:
            print(f'   • {module}: {error[:120]}...')
        if len(errors) > 15:
            print(f'   ... y {len(errors) - 15} más')
    else:
        print('\n🎉 ÉXITO COMPLETO: Todos los módulos importan correctamente.')

    print('\nUso: python verify_imports.py [--skip-optional]')
    return len(errors) == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
