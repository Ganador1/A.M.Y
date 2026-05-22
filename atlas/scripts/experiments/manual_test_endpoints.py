"""
Legacy ad-hoc endpoint tester kept for manual runs. Renamed to avoid pytest name clash.

⚠️ Advertencia
- No ejecutar contra entornos de producción sin autenticación/TLS.
- Evita volcar tokens o PII en consola o logs.
- Refiérete a `ETHICS_AND_SAFETY.md` para guías de uso responsable.
"""

if __name__ == "__main__":
    print("Use test_endpoints.sh for manual API smoke tests.")
