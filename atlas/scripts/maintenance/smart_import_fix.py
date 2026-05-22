#!/usr/bin/env python3
"""
Script inteligente para corregir imports específicos por tipo
"""
import os
import re
from pathlib import Path


# Tipos que están en database_models (SQLAlchemy models)
DATABASE_MODEL_TYPES = {
    'User', 'UserSession', 'Calculation', 'CachedResult',
    'SystemMetric', 'ErrorLog', 'APIRequestLog', 'ScientificDataset',
    'KnowledgeNode', 'KnowledgeRelation'
}

# Tipos que están en models (Pydantic models)
PYDANTIC_MODEL_TYPES = {
    'ArithmeticRequest', 'ArithmeticResponse', 'ArithmeticOperation', 'ArithmeticResult',
    'EquationRequest', 'EquationResponse', 'CalculusRequest', 'CalculusResponse',
    'BaseResponse', 'PartialDerivativeRequest', 'PartialDerivativeResponse',
    'FourierTransformRequest', 'FourierTransformResponse', 'OperationType'
}


def smart_fix_imports(file_path: Path) -> bool:
    """Corregir imports inteligentemente basado en tipo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = False
        
        # Buscar lines con imports problemáticos
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            # Buscar imports de app.models that could be wrong
            if re.match(r'from app\.models import', line):
                # Extraer los tipos importados
                imports_match = re.search(r'from app\.models import \(([^)]+)\)', line, re.DOTALL)
                if not imports_match:
                    imports_match = re.search(r'from app\.models import (.+)', line)
                
                if imports_match:
                    imports_text = imports_match.group(1)
                    # Parse imports
                    imported_types = [
                        t.strip().split(' as ')[0].strip() 
                        for t in re.split(r'[,\n]', imports_text) 
                        if t.strip() and not t.strip().startswith('#')
                    ]
                    
                    # Separar por tipo
                    database_types = [t for t in imported_types if t in DATABASE_MODEL_TYPES]
                    pydantic_types = [t for t in imported_types if t in PYDANTIC_MODEL_TYPES]
                    
                    # Crear nuevos imports
                    new_import_lines = []
                    if database_types:
                        if len(database_types) == 1:
                            new_import_lines.append(f"from app.models.database_models import {database_types[0]}")
                        else:
                            db_imports = ', '.join(database_types)
                            new_import_lines.append(f"from app.models.database_models import ({db_imports})")
                    
                    if pydantic_types:
                        if len(pydantic_types) == 1:
                            new_import_lines.append(f"from app.models import {pydantic_types[0]}")
                        else:
                            pyd_imports = ', '.join(pydantic_types)
                            new_import_lines.append(f"from app.models import ({pyd_imports})")
                    
                    # Si tenemos tipos unknowns, mantener import original
                    unknown_types = [t for t in imported_types if t not in DATABASE_MODEL_TYPES and t not in PYDANTIC_MODEL_TYPES]
                    if unknown_types:
                        if len(unknown_types) == 1:
                            new_import_lines.append(f"from app.models import {unknown_types[0]}")
                        else:
                            unk_imports = ', '.join(unknown_types)
                            new_import_lines.append(f"from app.models import ({unk_imports})")
                    
                    # Replace line
                    if new_import_lines:
                        new_lines.extend(new_import_lines)
                        changes_made = True
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        if changes_made:
            new_content = '\n'.join(new_lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
            
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False
    
    return False


def main():
    """Ejecutar corrección inteligente de imports"""
    print("🧠 Aplicando correcciones inteligentes de imports por tipo...")
    
    total_files = 0
    fixed_files = 0
    
    for root, dirs, files in os.walk('app'):
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'venv']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                total_files += 1
                
                if smart_fix_imports(file_path):
                    print(f"  ✅ {file_path}")
                    fixed_files += 1
    
    print(f"\n📊 Resultados:")
    print(f"   • Archivos procesados: {total_files}")
    print(f"   • Archivos corregidos: {fixed_files}")
    
    return fixed_files


if __name__ == '__main__':
    main()
