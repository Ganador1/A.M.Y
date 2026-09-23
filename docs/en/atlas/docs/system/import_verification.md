> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="política-de-verificación-de-imports"></a>
# Import Verification Policy

<a id="objetivo"></a>
## Objective

Ensure that every module in the AXIOM ATLAS ecosystem is importable without syntax errors, missing dependencies, or dangerous side effects.

<a id="alcance"></a>
## Scope

- Core: `app/`
- Ingestion: `ingestion/`
- Critical root scripts: `main`, `comprehensive_analysis`, `generate_final_report`

<a id="herramienta"></a>
## Tool

`verify_imports.py`

<a id="modos"></a>
### Modes

| Mode | Command | What it includes |
|------|---------|------------------|
| Quick | `python verify_imports.py --skip-optional` | Only `app/` |
| Full | `python verify_imports.py` | app + ingestion + root scripts |

<a id="interpretación-de-resultados"></a>
## Interpreting Results

- Lines `✅` success
- Lines `❌` failures (shows summarized exception)
- Summary by segment (if full mode)

<a id="errores-comunes-detectados"></a>
## Common Errors Detected

| Type | Example | Mitigation |
|------|---------|------------|
| SyntaxError | malformed f-string | Fix syntax and re-run |
| ImportError | Package not installed | Add to requirements / conditional mock |
| Unexpected RuntimeError | Side effect on import | Move execution under `if __name__ == '__main__'` |

<a id="buenas-prácticas"></a>
## Best Practices

1. Avoid heavy logic at module level (use functions/factories).
2. Protect startup blocks:

   ```python
   if __name__ == '__main__':
       run()
   ```

3. Use deferred imports on infrequent paths or heavy dependencies.
4. Handle optional dependencies with try/except and functional degradation.

<a id="flujo-recomendado-en-pr"></a>
## Recommended Flow in PR

1. Implement change.
2. `python verify_imports.py --skip-optional`
3. Adjust if it fails.
4. `python verify_imports.py` full before pushing.

<a id="extensión-futura"></a>
## Future Extension

- Automatic CI integration (fail pipeline if there are errors)
- JSON mode (`--json`) for aggregated metrics
- Integration with coverage (detect modules never imported in tests)

---
End of document.
