from __future__ import annotations

from typing import Dict, Any
import sympy as sp

from app.mathlab.core.object_models import MathematicalObject


def prime_factor_signature_embedding(obj: MathematicalObject, k: int = 16) -> Dict[str, Any]:
    """Embedding básico para enteros basado en la firma de factores primos.
    Construye un vector de longitud k con los exponentes correspondientes a los k primos
    más pequeños presentes en la factorización de |n|, en orden ascendente de los primos.
    Si hay menos de k primos, se rellena con ceros.
    """
    payload = obj.payload_json
    if obj.type != "integer":
        raise ValueError("Object is not an integer")
    n = int(payload.get("value", 0))
    sign = -1 if n < 0 else (0 if n == 0 else 1)

    # Casos degenerados
    if n == 0:
        vec = [0.0] * k
        return {
            "embedding_type": "number/prime_factor_signature",
            "vector": vec,
            "dim": k,
            "metadata": {"n": n, "k": k, "sign": sign, "note": "zero has no prime factorization"},
        }
    if abs(n) == 1:
        vec = [0.0] * k
        return {
            "embedding_type": "number/prime_factor_signature",
            "vector": vec,
            "dim": k,
            "metadata": {"n": n, "k": k, "sign": sign, "note": "unit has empty factorization"},
        }

    fac = sp.factorint(abs(n))  # {prime: exponent}
    primes_sorted = sorted(fac.keys())

    # Asegurar que tenemos al menos k primos en la base (usar primeros k primos naturales)
    needed = max(0, k - len(primes_sorted))
    if needed > 0:
        # Genera primos adicionales desde el último conocido o desde 2
        gen_start = primes_sorted[-1] + 1 if primes_sorted else 2
        extra_primes = []
        p = sp.nextprime(gen_start - 1)
        while len(extra_primes) < needed:
            if p not in fac:
                extra_primes.append(p)
            p = sp.nextprime(p)
        basis_primes = sorted(primes_sorted + extra_primes)[:k]
    else:
        basis_primes = primes_sorted[:k]

    vec = [float(fac.get(p, 0)) for p in basis_primes]
    if len(vec) < k:
        vec = vec + [0.0] * (k - len(vec))

    return {
        "embedding_type": "number/prime_factor_signature",
        "vector": vec,
        "dim": k,
        "metadata": {"n": n, "k": k, "sign": sign, "basis_primes": basis_primes},
    }