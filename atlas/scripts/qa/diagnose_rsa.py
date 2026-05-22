#!/usr/bin/env python3
"""
Diagnostic script for RSA key format

⚠️ Advertencia de Seguridad

Este script interactúa con funcionalidades criptográficas (RSA). Úsalo solo con datos de prueba.
- No introduzcas claves privadas reales ni PII.
- No compartas salidas que puedan incluir materiales sensibles.
- Verifica el cumplimiento legal sobre uso/exportación de criptografía en tu jurisdicción.

Consulta `ETHICS_AND_SAFETY.md` para prácticas seguras.
"""

import sys
sys.path.append('.')

from sympy.crypto.crypto import rsa_private_key, rsa_public_key
from sympy import randprime

# Generate small RSA keys for testing
p = randprime(2**32, 2**33)
q = randprime(2**32, 2**33)
n = p * q
e = 65537

private_key = rsa_private_key(p, q, e)
public_key = rsa_public_key(n, e)

print("Private key format:")
print(f"Type: {type(private_key)}")
print(f"String representation: {str(private_key)}")
print(f"Repr: {repr(private_key)}")

print("\nPublic key format:")
print(f"Type: {type(public_key)}")
print(f"String representation: {str(public_key)}")
print(f"Repr: {repr(public_key)}")

# Try to understand the structure
if hasattr(private_key, 'args'):
    print(f"\nPrivate key args: {private_key.args}")
if hasattr(public_key, 'args'):
    print(f"Public key args: {public_key.args}")
