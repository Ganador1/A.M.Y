#!/usr/bin/env python3
"""
Script para añadir process_request a servicios que lo necesitan
"""

services_to_fix = [
    "app/domains/medicine/advanced_clinical_validation_service.py",
    "app/domains/astronomy/services/astronomical_ml_service.py",
    "app/domains/medicine/advanced_medical_imaging_service.py",
]

process_request_template = '''
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesador de solicitudes genérico compatible con ToolEvidenceOrchestrator
        
        Args:
            request_data: Diccionario con 'action' y parámetros específicos
            
        Returns:
            Resultado de la operación solicitada
        """
        try:
            action = request_data.get('action', '')
            
            # Mapeo de acciones a métodos
            if hasattr(self, action):
                method = getattr(self, action)
                # Eliminar 'action' del dict antes de llamar al método
                params = {k: v for k, v in request_data.items() if k != 'action'}
                
                # Llamar método async o sync
                if asyncio.iscoroutinefunction(method):
                    return await method(**params)
                else:
                    return method(**params)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": [m for m in dir(self) if not m.startswith('_') and callable(getattr(self, m))]
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "exception_type": type(e).__name__
            }
'''

def add_process_request_to_file(filepath: str):
    """Añade process_request al archivo si no lo tiene"""
    from pathlib import Path
    
    path = Path(filepath)
    if not path.exists():
        print(f"❌ No existe: {filepath}")
        return
    
    content = path.read_text()
    
    # Verificar si ya tiene process_request
    if 'def process_request(' in content or 'async def process_request(' in content:
        print(f"✅ Ya tiene process_request: {filepath}")
        return
    
    # Encontrar la clase principal
    import re
    class_match = re.search(r'class\s+(\w+Service)\s*[:(]', content)
    if not class_match:
        print(f"❌ No se encontró clase Service en: {filepath}")
        return
    
    class_name = class_match.group(1)
    print(f"🔧 Añadiendo process_request a {class_name} en {filepath}")
    
    # Encontrar el __init__ y añadir después
    init_pattern = r'(    def __init__\(self[^)]*\):.*?(?=\n    def |\n\nclass |\Z))'
    
    matches = list(re.finditer(init_pattern, content, re.DOTALL))
    if matches:
        # Insertar después del último __init__
        last_match = matches[-1]
        insert_pos = last_match.end()
        
        new_content = content[:insert_pos] + "\n" + process_request_template + content[insert_pos:]
        
        path.write_text(new_content)
        print(f"✅ Añadido process_request a {filepath}")
    else:
        print(f"❌ No se encontró __init__ en: {filepath}")

if __name__ == '__main__':
    print("🚀 Añadiendo process_request a servicios...\n")
    
    for service_path in services_to_fix:
        add_process_request_to_file(service_path)
    
    print("\n✅ Proceso completado")
