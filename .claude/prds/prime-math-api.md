---
name: prime-math-api
description: FastAPI service exposing number theory endpoints for primality testing, prime factorization, and arithmetic progression analysis
status: backlog
created: 2025-09-25T20:02:17Z
---

# PRD: Prime Math API (FastAPI)

## Goal
A FastAPI service that exposes number-theory endpoints:
1) Primality test
2) Prime factorization
3) Longest run length of a prime-only arithmetic progression defined by start a and step d (consecutive terms until first composite)

## Tech
- Python 3.11+
- FastAPI + Uvicorn
- Type hints, pydantic models
- Testing: pytest
- Lint/format: ruff + black

## Endpoints
### GET /is_prime?n=<int>
Response: { "n": int, "is_prime": bool, "method": "miller_rabin|trial" }

### GET /factorize?n=<int>
Response: { "n": int, "factors": { "<prime>": <exp>, ... } }

### GET /ap/prime-run?a=<int>&d=<int>&limit=<int, optional>
Compute the longest initial run length L such that a, a+d, ..., a+(L-1)d are prime, stopping at first composite or when reaching optional 'limit'.
Response: { "a": int, "d": int, "length": int, "terms": [int, ...] }

## Constraints
- Handle up to unsigned 64-bit range gracefully; detect/guard beyond that.
- Primality: deterministic for 64-bit integers using known Miller–Rabin base sets (e.g. the 12 prime bases 2..37), else probabilistic fallback with k rounds. Cite bases in code comments.
- Factorization: trial division by small primes, then Pollard's Rho (+ Brent) for large composites.
- Timeouts: per-request soft cap ~1s defaults; surface 422 on invalid params (n<2, d<=0, etc.).

## Non-goals
- Cryptographic guarantees for arbitrary bigints
- Persistence or auth

## Deliverables
- `app/main.py` with the three endpoints and OpenAPI
- `prime/nt.py` with `is_probable_prime`, `is_prime_64`, `factorize`, `prime_run_length`
- `tests/test_prime.py` with unit tests
- Makefile / task runner, pre-commit hooks, Dockerfile (optional)

## Acceptance tests (behavioral)
- /is_prime: 2,3,5,17 true; 1,0,4,21 false
- /factorize: 1 → {}; 60 → {2:2,3:1,5:1}; 97 → {97:1}
- /ap/prime-run: a=3,d=2 → length≥2 with [3,5,7,11,13] stopping at 15; a=5,d=6 → [5,11,17,23,29,35...] stopping before 35

## DevEx
- `uvicorn app.main:app --reload`
- `pytest -q`
- Black+Ruff CI via GitHub Actions