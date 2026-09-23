"""Tests de integración ligeros para scripts raíz.

Objetivos:
- Verificar que los scripts principales se importan sin efectos colaterales graves.
- Asegurar que exponen símbolos esperados o funciones de arranque.
"""
from importlib import import_module

ROOT_SCRIPTS = [
    ("main", []),  # no se valida símbolos específicos todavía
    ("comprehensive_analysis", []),
    ("generate_final_report", []),
]


def test_root_scripts_importable():
    failures = []
    for module_name, expected_symbols in ROOT_SCRIPTS:
        try:
            mod = import_module(module_name)
        except Exception as e:  # noqa: BLE001
            failures.append((module_name, str(e)))
            continue
        for sym in expected_symbols:
            assert hasattr(mod, sym), f"El módulo {module_name} no expone símbolo requerido: {sym}"
    assert not failures, "Fallos de importación: " + ", ".join(f"{m}: {err}" for m, err in failures)


def test_main_has_guard():
    """Verifica que main.py no ejecuta lógica pesada al importarse (heurística).

    Estrategia: Colocar un atributo opcional __MAIN_IMPORTED__ dentro de main si se desea, o
    verificar que no se definan hilos activos nuevos durante la importación. Por ahora solo
    comprobamos que no aparece 'if __name__ == "__main__"' ejecutado.
    """
    src = open("main.py", "r", encoding="utf-8").read()
    assert "if __name__ == '__main__'" in src or 'if __name__ == "__main__"' in src, (
        "Se recomienda mantener un guard en main.py para evitar ejecución al importar"
    )
