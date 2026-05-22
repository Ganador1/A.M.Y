#!/usr/bin/env python3
"""
Análisis Automático de Código - AXIOM ATLAS

Este script realiza un análisis comprehensivo del proyecto para identificar:
- Código duplicado
- Archivos demasiado grandes
- Imports problemáticos
- Complejidad ciclomática alta
- Problemas de estructura
- Oportunidades de refactorización

Uso:
    python analyze_code.py --full         # Análisis completo
    python analyze_code.py --quick        # Análisis rápido
    python analyze_code.py --duplicates   # Solo duplicados
    python analyze_code.py --complexity   # Solo complejidad
    python analyze_code.py --imports      # Solo imports
"""

import os
import ast
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple
from collections import defaultdict, Counter
import subprocess


class CodeAnalyzer:
    """Analizador comprehensivo de código"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.issues: List[Dict[str, Any]] = []
        self.duplicates: Dict[str, List[Path]] = defaultdict(list)
        self.complexity_scores: Dict[Path, int] = {}
        self.file_sizes: Dict[Path, int] = {}

    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analizar un archivo individual"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Métricas básicas
            lines = content.split('\n')
            size_bytes = len(content.encode('utf-8'))

            analysis = {
                'path': str(file_path),
                'lines': len(lines),
                'size_bytes': size_bytes,
                'size_mb': size_bytes / (1024 * 1024),
                'is_large': len(lines) > 500,
                'is_very_large': len(lines) > 1000,
                'imports': [],
                'functions': [],
                'classes': [],
                'complexity_issues': []
            }

            # Analizar imports
            analysis['imports'] = self._analyze_imports(content)

            # Analizar funciones y clases
            analysis['functions'], analysis['classes'] = self._analyze_structure(content)

            # Calcular complejidad
            complexity = self._calculate_complexity(content)
            analysis['complexity_score'] = complexity
            analysis['complexity_level'] = self._get_complexity_level(complexity)

            # Verificar problemas comunes
            analysis['issues'] = self._check_common_issues(content, file_path)

            return analysis

        except Exception as e:
            return {
                'path': str(file_path),
                'error': str(e),
                'lines': 0,
                'size_bytes': 0
            }

    def _analyze_imports(self, content: str) -> List[str]:
        """Analizar imports en el código"""
        imports = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except:
            # Fallback: buscar imports con regex simple
            import_lines = [line.strip() for line in content.split('\n')
                          if line.startswith(('import ', 'from '))]
            imports = import_lines

        return imports

    def _analyze_structure(self, content: str) -> Tuple[List[str], List[str]]:
        """Analizar estructura del código (funciones y clases)"""
        functions = []
        classes = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
        except:
            # Fallback simple
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('def '):
                    func_name = line.split('(')[0].replace('def ', '')
                    functions.append(func_name)
                elif line.startswith('class '):
                    class_name = line.split('(')[0].replace('class ', '')
                    classes.append(class_name)

        return functions, classes

    def _calculate_complexity(self, content: str) -> int:
        """Calcular complejidad ciclomática básica"""
        complexity = 1  # Base complexity

        lines = content.split('\n')

        for line in lines:
            line = line.strip().lower()

            # Control structures that increase complexity
            if any(keyword in line for keyword in [
                'if ', 'elif ', 'else:', 'for ', 'while ',
                'try:', 'except', 'finally:', 'with '
            ]):
                complexity += 1

            # Boolean operators
            if any(op in line for op in [' and ', ' or ', ' not ']):
                complexity += 1

        return complexity

    def _get_complexity_level(self, complexity: int) -> str:
        """Obtener nivel de complejidad"""
        if complexity <= 5:
            return "Baja"
        elif complexity <= 10:
            return "Media"
        elif complexity <= 20:
            return "Alta"
        else:
            return "Muy Alta"

    def _check_common_issues(self, content: str, file_path: Path) -> List[str]:
        """Verificar problemas comunes"""
        issues = []
        lines = content.split('\n')

        # Verificar líneas demasiado largas
        for i, line in enumerate(lines):
            if len(line) > 120:
                issues.append(f"Línea {i+1} demasiado larga ({len(line)} caracteres)")

        # Verificar imports en medio del archivo
        import_lines = [i for i, line in enumerate(lines)
                       if line.strip().startswith(('import ', 'from '))]

        if import_lines and import_lines[0] > 10:  # Imports después de línea 10
            issues.append("Imports encontrados tarde en el archivo")

        # Verificar funciones muy largas
        in_function = False
        function_start = 0

        for i, line in enumerate(lines):
            if line.strip().startswith('def ') or line.strip().startswith('async def '):
                in_function = True
                function_start = i
            elif line.strip().startswith('class '):
                in_function = False
            elif in_function and line.strip() == '' and i - function_start > 50:
                issues.append(f"Función muy larga detectada desde línea {function_start}")

        return issues

    def find_duplicates(self, min_lines: int = 10):
        """Encontrar código duplicado"""
        from difflib import SequenceMatcher

        # Obtener todos los archivos Python
        python_files = list(self.project_path.rglob("*.py"))

        # Crear mapa de contenido por archivo
        content_map = {}
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Normalizar contenido para comparación
                    normalized = '\n'.join([
                        line.strip()
                        for line in content.split('\n')
                        if line.strip() and not line.strip().startswith(('#', '"""', "'''"))
                    ])
                    content_map[file_path] = normalized
            except:
                continue

        # Buscar duplicados
        checked_pairs = set()

        for file1, content1 in content_map.items():
            for file2, content2 in content_map.items():
                if file1 == file2 or (file1, file2) in checked_pairs:
                    continue

                # Calcular similitud
                matcher = SequenceMatcher(None, content1, content2)
                similarity = matcher.ratio()

                if similarity > 0.8:  # 80% similar
                    self.duplicates[str(file1)].append(file2)
                    self.duplicates[str(file2)].append(file1)

                checked_pairs.add((file1, file2))
                checked_pairs.add((file2, file1))

    def analyze_project(self, extensions: List[str] = None) -> Dict[str, Any]:
        """Analizar proyecto completo"""
        if extensions is None:
            extensions = ['.py']

        # Encontrar archivos
        files_to_analyze = []
        for ext in extensions:
            files_to_analyze.extend(self.project_path.rglob(f"*{ext}"))

        total_files = len(files_to_analyze)
        print(f"📊 Analizando {total_files} archivos...")

        # Analizar cada archivo
        file_analyses = []
        large_files = []
        complex_files = []
        problematic_imports = []

        for i, file_path in enumerate(files_to_analyze):
            if i % 10 == 0:
                print(f"  Progress: {i}/{total_files} ({i/total_files*100:.1f}%)")

            analysis = self.analyze_file(file_path)
            file_analyses.append(analysis)

            # Categorizar archivos
            if analysis.get('is_very_large', False):
                large_files.append(analysis)

            if analysis.get('complexity_level') in ['Alta', 'Muy Alta']:
                complex_files.append(analysis)

            # Verificar imports problemáticos
            imports = analysis.get('imports', [])
            if len(imports) > 20:
                problematic_imports.append(analysis)

        # Encontrar duplicados
        print("🔍 Buscando código duplicado...")
        self.find_duplicates()

        # Generar reporte
        report = {
            'summary': {
                'total_files': total_files,
                'large_files': len(large_files),
                'complex_files': len(complex_files),
                'problematic_imports': len(problematic_imports),
                'duplicate_groups': len(self.duplicates)
            },
            'large_files': large_files,
            'complex_files': complex_files,
            'problematic_imports': problematic_imports,
            'duplicates': dict(self.duplicates),
            'recommendations': self._generate_recommendations(
                large_files, complex_files, problematic_imports
            )
        }

        return report

    def _generate_recommendations(self, large_files, complex_files, problematic_imports) -> List[str]:
        """Generar recomendaciones basadas en análisis"""
        recommendations = []

        if large_files:
            recommendations.append(
                f"🔴 CRÍTICO: {len(large_files)} archivos muy grandes (>1000 líneas) "
                "deben ser divididos en módulos más pequeños"
            )

        if complex_files:
            recommendations.append(
                f"🟡 ALTA: {len(complex_files)} archivos con alta complejidad "
                "deben ser refactorizados"
            )

        if problematic_imports:
            recommendations.append(
                f"🟠 MEDIA: {len(problematic_imports)} archivos con muchos imports "
                "deben ser organizados mejor"
            )

        if self.duplicates:
            recommendations.append(
                f"🟢 INFO: {len(self.duplicates)} grupos de código duplicado "
                "encontrados - oportunidad de refactorización"
            )

        # Recomendaciones específicas
        recommendations.extend([
            "📋 Crear sistema de registro automático de routers",
            "🔄 Implementar lazy loading para mejorar startup time",
            "📦 Organizar código en módulos por dominio funcional",
            "🧪 Implementar testing comprehensivo antes de cambios",
            "📚 Documentar arquitectura y patrones de diseño"
        ])

        return recommendations

    def generate_report(self, output_file: str = "code_analysis_report.json"):
        """Generar reporte de análisis"""
        report = self.analyze_project()

        # Generar reporte en texto
        text_report = f"""
# 📊 REPORTE DE ANÁLISIS DE CÓDIGO - AXIOM ATLAS

## 📈 RESUMEN EJECUTIVO
- **Archivos totales**: {report['summary']['total_files']}
- **Archivos grandes (>1000 líneas)**: {report['summary']['large_files']}
- **Archivos complejos**: {report['summary']['complex_files']}
- **Archivos con imports problemáticos**: {report['summary']['problematic_imports']}
- **Grupos de código duplicado**: {report['summary']['duplicate_groups']}

## 🚨 PROBLEMAS CRÍTICOS

### Archivos Muy Grandes
"""

        if report['large_files']:
            text_report += "\n#### Archivos que requieren división inmediata:\n"
            for analysis in report['large_files']:
                text_report += f"- **{analysis['path']}**: {analysis['lines']} líneas\n"

        text_report += f"""

### Archivos Complejos
"""

        if report['complex_files']:
            text_report += "\n#### Archivos con alta complejidad ciclomática:\n"
            for analysis in report['complex_files']:
                text_report += f"- **{analysis['path']}**: {analysis['complexity_score']} (nivel: {analysis['complexity_level']})\n"

        text_report += f"""

### Código Duplicado
"""

        if report['duplicates']:
            text_report += f"\n#### Grupos de archivos duplicados encontrados:\n"
            for file, duplicates in list(report['duplicates'].items())[:5]:  # Top 5
                text_report += f"- **{file}** → {len(duplicates)} archivos similares\n"

        text_report += f"""

## 🎯 RECOMENDACIONES

"""

        for i, rec in enumerate(report['recommendations'], 1):
            text_report += f"{i}. {rec}\n"

        text_report += f"""

## 📋 ACCIONES INMEDIATAS

1. **Dividir archivos >1000 líneas** en módulos más pequeños
2. **Refactorizar funciones complejas** (>20 de complejidad)
3. **Eliminar código duplicado** identificado
4. **Crear sistema de router registry** para reducir acoplamiento
5. **Implementar lazy loading** para mejorar performance

---
**Generado por**: Code Analyzer - AXIOM ATLAS
**Fecha**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        # Guardar reporte JSON
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        # Guardar reporte de texto
        text_file = output_file.replace('.json', '.txt')
        with open(text_file, 'w') as f:
            f.write(text_report)

        print(f"✅ Reporte generado: {output_file}")
        print(f"📄 Reporte de texto: {text_file}")

        return report


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(description="Code Analyzer - AXIOM ATLAS")
    parser.add_argument("--full", action="store_true", help="Análisis completo")
    parser.add_argument("--quick", action="store_true", help="Análisis rápido")
    parser.add_argument("--duplicates", action="store_true", help="Solo buscar duplicados")
    parser.add_argument("--complexity", action="store_true", help="Solo analizar complejidad")
    parser.add_argument("--imports", action="store_true", help="Solo analizar imports")
    parser.add_argument("--output", default="code_analysis_report.json", help="Archivo de salida")

    args = parser.parse_args()

    analyzer = CodeAnalyzer()

    if args.full or args.quick:
        print("🔍 Iniciando análisis comprehensivo...")
        report = analyzer.generate_report(args.output)

        if args.quick:
            # Mostrar solo resumen para análisis rápido
            summary = report['summary']
            print(f"   Archivos: {summary['total_files']}")
            print(f"   Grandes: {summary['large_files']}")
            print(f"   Complejos: {summary['complex_files']}")
            print(f"   Imports problemáticos: {summary['problematic_imports']}")
            print(f"   Duplicados: {summary['duplicate_groups']}")

    elif args.duplicates:
        print("🔍 Buscando código duplicado...")
        analyzer.find_duplicates()
        print(f"📊 Grupos de duplicados encontrados: {len(analyzer.duplicates)}")

        for file, duplicates in list(analyzer.duplicates.items())[:5]:
            print(f"  📁 {file}:")
            for dup in duplicates[:3]:  # Mostrar primeros 3
                print(f"    ↳ {dup}")

    elif args.complexity:
        print("🔍 Analizando complejidad de código...")

        # Analizar algunos archivos clave
        key_files = [
            "main.py",
            "app/services/scientific_ai.py",
            "app/routers/calculus.py"
        ]

        for file_name in key_files:
            file_path = Path(file_name)
            if file_path.exists():
                analysis = analyzer.analyze_file(file_path)
                print(f"  📁 {file_name}:")
                print(f"    Líneas: {analysis['lines']}")
                print(f"    Complejidad: {analysis['complexity_score']}")
                print(f"    Nivel: {analysis['complexity_level']}")

    elif args.imports:
        print("🔍 Analizando imports...")

        # Analizar main.py específicamente
        main_path = Path("main.py")
        if main_path.exists():
            analysis = analyzer.analyze_file(main_path)
            imports = analysis.get('imports', [])

            print(f"📊 Main.py - Imports encontrados: {len(imports)}")
            print("  Top 10 imports más comunes:")

            import_counts = Counter(imports)
            for imp, count in import_counts.most_common(10):
                print(f"    - {imp}: {count}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
