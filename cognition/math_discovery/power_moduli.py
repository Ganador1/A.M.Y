"""Shared elementary helpers for the universal power-modulus search."""
from __future__ import annotations

import math


def primes_up_to(limit: int) -> list[int]:
    if limit < 2:
        return []
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for candidate in range(2, math.isqrt(limit) + 1):
        if sieve[candidate]:
            start = candidate * candidate
            sieve[start : limit + 1 : candidate] = b"\x00" * (
                ((limit - start) // candidate) + 1
            )
    return [value for value in range(2, limit + 1) if sieve[value]]


def predicted_modulus(exponent: int) -> int:
    if exponent < 2:
        raise ValueError("exponent must be at least two")
    product = 1
    for prime in primes_up_to(exponent):
        if (exponent - 1) % (prime - 1) == 0:
            product *= prime
    return product
