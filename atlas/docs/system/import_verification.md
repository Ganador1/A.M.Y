# Política de Verificación de Imports

## Objetivo

Garantizar que cada módulo del ecosistema AXIOM ATLAS sea importable sin errores de sintaxis, dependencias faltantes o efectos secundarios peligrosos.

## Alcance

- Núcleo: `app/`
- Ingestión: `ingestion/`
- Scripts críticos raíz: `main`, `comprehensive_analysis`, `generate_final_report`

## Herramienta

`verify_imports.py`

### Modos

| Modo | Comando | Qué incluye |
|------|---------|-------------|
| Rápido | `python verify_imports.py --skip-optional` | Solo `app/` |
| Completo | `python verify_imports.py` | app + ingestion + scripts raíz |

## Interpretación de Resultados

- Líneas `✅` éxito
- Líneas `❌` fallos (muestra excepción resumida)
- Resumen por segmento (si modo completo)

## Errores Comunes Detectados

| Tipo | Ejemplo | Mitigación |
|------|---------|------------|
| SyntaxError | f-string malformada | Corregir sintaxis y re-ejecutar |
| ImportError | Paquete no instalado | Añadir a requirements / mock condicional |
| RuntimeError inesperado | Side-effect en import | Mover ejecución bajo `if __name__ == '__main__'` |

## Buenas Prácticas

1. Evitar lógica pesada al nivel módulo (usar funciones/fábricas).
2. Proteger bloques de arranque:

   ```python
   if __name__ == '__main__':
       run()
   ```

3. Usar imports diferidos en rutas poco frecuentes o dependencias pesadas.
4. Manejar dependencias opcionales con try/except y degradación funcional.

## Flujo Recomendado en PR

1. Implementar cambio.
2. `python verify_imports.py --skip-optional`
3. Ajustar si falla.
4. `python verify_imports.py` completo antes de empujar.

## Extensión Futura

- Integración CI automática (fallar pipeline si hay errores)
- Modo JSON (`--json`) para métricas agregadas
- Integración con coverage (detectar módulos nunca importados en tests)

---
Fin del documento.
