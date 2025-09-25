"""
Prime Number Theory Module

A comprehensive implementation of number theory algorithms including:
- Deterministic Miller-Rabin primality testing for 64-bit integers
- Hybrid factorization using trial division and Pollard's Rho
- Arithmetic progression analysis for consecutive primes

This module provides educational implementations with full algorithmic control
and comprehensive documentation.
"""

__version__ = "1.0.0"
__author__ = "Claude Code PM System"

from .nt import (
    is_prime_64,
    is_probable_prime,
    factorize,
    prime_run_length
)

__all__ = [
    "is_prime_64",
    "is_probable_prime",
    "factorize",
    "prime_run_length"
]