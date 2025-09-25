"""
Prime Math API - FastAPI application for number theory operations.

This module provides REST endpoints for:
- Primality testing
- Integer factorization
- Arithmetic progression analysis
"""

from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field, validator
from typing import List, Union
import sys
import os

# Add the project root to the Python path to import prime module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prime.nt import is_prime_64, factorize, prime_run_length, MAX_64BIT

app = FastAPI(
    title="Prime Math API",
    description="""
    ## High-Performance Number Theory API

    A production-ready FastAPI service providing optimized algorithms for number theory operations.

    ### Features
    - **Deterministic Primality Testing**: Uses Miller-Rabin with proven base sets for 64-bit integers
    - **Efficient Factorization**: Hybrid approach with trial division and Pollard's Rho algorithm
    - **Arithmetic Progressions**: Find consecutive primes in arithmetic sequences
    - **High Performance**: Optimized algorithms with O(log³ n) complexity for most operations
    - **Input Validation**: Comprehensive validation for 64-bit integer range
    - **Production Ready**: Health checks, error handling, and monitoring support

    ### Algorithm Details
    - **Primality Testing**: Deterministic Miller-Rabin using Sinclair's proven base set
    - **Factorization**: Trial division for small factors, Pollard's Rho with Brent optimization
    - **Input Range**: Supports all non-negative integers up to 2^64 - 1 (18,446,744,073,709,551,615)
    - **Performance**: Sub-millisecond response times for most inputs

    ### Rate Limits & Usage
    Please limit requests to reasonable rates. For high-volume usage, implement client-side rate limiting.

    ### Security
    This API performs mathematical computations only and does not store or log input values.
    """,
    version="0.1.0",
    contact={
        "name": "Prime Math API Team",
        "url": "https://github.com/ashish102/Prime-3",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "health",
            "description": "Health check and system status endpoints"
        },
        {
            "name": "primality",
            "description": "Prime number testing operations"
        },
        {
            "name": "factorization",
            "description": "Integer factorization operations"
        },
        {
            "name": "progressions",
            "description": "Arithmetic progression analysis"
        }
    ]
)


# Pydantic models for request/response validation
class PrimeResponse(BaseModel):
    """Response model for prime checking endpoint."""
    number: int = Field(..., description="The number that was tested")
    is_prime: bool = Field(..., description="Whether the number is prime")

    class Config:
        schema_extra = {
            "example": {
                "number": 97,
                "is_prime": True
            }
        }


class FactorResponse(BaseModel):
    """Response model for factorization endpoint."""
    number: int = Field(..., description="The number that was factorized")
    factors: List[int] = Field(..., description="List of prime factors (with repetition)")
    factor_count: int = Field(..., description="Total number of prime factors")

    class Config:
        schema_extra = {
            "example": {
                "number": 60,
                "factors": [2, 2, 3, 5],
                "factor_count": 4
            }
        }


class ProgressionResponse(BaseModel):
    """Response model for arithmetic progression endpoint."""
    start: int = Field(..., description="Starting number of the progression")
    diff: int = Field(..., description="Common difference")
    length: int = Field(..., description="Number of consecutive primes found")
    primes: List[int] = Field(..., description="List of consecutive primes in the progression")

    class Config:
        schema_extra = {
            "example": {
                "start": 3,
                "diff": 2,
                "length": 5,
                "primes": [3, 5, 7, 11, 13]
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    details: str = Field(None, description="Additional error details")


def validate_64bit_integer(value: int, param_name: str) -> int:
    """Validate that a value is within 64-bit integer range."""
    if value < 0:
        raise HTTPException(
            status_code=400,
            detail=f"{param_name} must be non-negative, got {value}"
        )
    if value > MAX_64BIT:
        raise HTTPException(
            status_code=400,
            detail=f"{param_name} exceeds 64-bit range (max: {MAX_64BIT}), got {value}"
        )
    return value


@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "Prime Math API",
        "version": "0.1.0",
        "docs_url": "/docs"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns basic service health status. Use this endpoint for:
    - Load balancer health checks
    - Monitoring system probes
    - Service availability verification

    Returns:
        dict: Health status with "healthy" status
    """
    return {
        "status": "healthy",
        "service": "Prime Math API",
        "version": "0.1.0"
    }


@app.get("/prime/{n}", response_model=PrimeResponse, tags=["primality"])
async def check_prime(
    n: int = Path(..., description="Integer to test for primality", ge=0)
) -> PrimeResponse:
    """
    Check if a number is prime using deterministic Miller-Rabin algorithm.

    This endpoint uses Sinclair's proven base set for 100% deterministic results
    for all integers up to 2^64.

    Args:
        n: Non-negative integer to test (0 ≤ n ≤ 2^64-1)

    Returns:
        PrimeResponse with the number and whether it's prime

    Raises:
        HTTPException: If n is negative or exceeds 64-bit range
    """
    try:
        # Validate input range
        validate_64bit_integer(n, "n")

        # Check primality
        is_prime = is_prime_64(n)

        return PrimeResponse(number=n, is_prime=is_prime)

    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/factor/{n}", response_model=FactorResponse, tags=["factorization"])
async def get_factors(
    n: int = Path(..., description="Integer to factorize", ge=0)
) -> FactorResponse:
    """
    Get prime factorization of a number using hybrid algorithm.

    Uses trial division for small primes and Pollard's Rho with Brent optimization
    for larger factors. Returns all prime factors with repetition.

    Args:
        n: Non-negative integer to factorize (0 ≤ n ≤ 2^64-1)

    Returns:
        FactorResponse with the number, factors list, and factor count

    Raises:
        HTTPException: If n is negative or exceeds 64-bit range
    """
    try:
        # Validate input range
        validate_64bit_integer(n, "n")

        # Get prime factorization
        factors = factorize(n)

        return FactorResponse(
            number=n,
            factors=factors,
            factor_count=len(factors)
        )

    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/progression/{start}/{diff}", response_model=ProgressionResponse, tags=["progressions"])
async def get_prime_progression(
    start: int = Path(..., description="First term of arithmetic sequence", ge=0),
    diff: int = Path(..., description="Common difference (must be positive)", gt=0),
    max_terms: int = Query(1000, description="Maximum number of terms to check", ge=1, le=10000)
) -> ProgressionResponse:
    """
    Find consecutive primes in arithmetic progression.

    Computes the longest initial run of consecutive primes in the arithmetic
    sequence: start, start+diff, start+2*diff, ...

    Args:
        start: Non-negative starting number (0 ≤ start ≤ 2^64-1)
        diff: Positive common difference (1 ≤ diff ≤ 2^64-1)
        max_terms: Maximum number of terms to check (1 ≤ max_terms ≤ 10000)

    Returns:
        ProgressionResponse with start, diff, length, and list of consecutive primes

    Raises:
        HTTPException: If parameters are invalid or exceed 64-bit range
    """
    try:
        # Validate input ranges
        validate_64bit_integer(start, "start")
        validate_64bit_integer(diff, "diff")

        if diff <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"diff must be positive, got {diff}"
            )

        if max_terms < 1 or max_terms > 10000:
            raise HTTPException(
                status_code=400,
                detail=f"max_terms must be between 1 and 10000, got {max_terms}"
            )

        # Find prime progression
        length, primes = prime_run_length(start, diff, max_terms)

        return ProgressionResponse(
            start=start,
            diff=diff,
            length=length,
            primes=primes
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)