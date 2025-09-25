---
name: prime-math-api
status: backlog
created: 2025-09-25T20:05:49Z
progress: 0%
prd: .claude/prds/prime-math-api.md
github: [Will be updated when synced to GitHub]
---

# Epic: prime-math-api

## Overview
Implement a high-performance FastAPI service providing number theory operations via REST endpoints. The service will offer primality testing, integer factorization, and arithmetic progression analysis with deterministic algorithms for 64-bit integers and robust error handling.

## Architecture Decisions

### Technology Stack
- **Python 3.11+**: Leverages latest performance improvements and type system enhancements
- **FastAPI + Uvicorn**: Provides automatic OpenAPI documentation, type validation, and high performance
- **Pydantic Models**: Ensures type safety and automatic request/response validation
- **Pure Python Implementation**: No external math libraries for core algorithms to maintain control and educational value

### Algorithm Selection
- **Miller-Rabin Primality**: Deterministic for 64-bit using known base sets (2,3,5,7,11,13,17,19,23,29,31,37)
- **Pollard's Rho + Brent**: Efficient factorization for large composites after trial division
- **Arithmetic Progression**: Direct computation with early termination on first composite

### Performance Strategy
- **Request Timeouts**: 1-second soft caps with graceful degradation
- **Input Validation**: Early rejection of invalid parameters (n<2, d<=0, 64-bit overflow)
- **Algorithm Selection**: Trial division for small numbers, advanced algorithms for large composites

## Technical Approach

### Backend Services
- **FastAPI Application**: Single-file app with three endpoints and automatic OpenAPI generation
- **Number Theory Module**: Core mathematical algorithms isolated in dedicated module
- **Pydantic Models**: Request/response schemas for type safety and validation
- **Error Handling**: Comprehensive validation with detailed 422 responses for invalid inputs

### API Design
- **GET /is_prime**: Returns primality status with algorithm method used
- **GET /factorize**: Returns prime factorization as exponent dictionary
- **GET /ap/prime-run**: Computes consecutive primes in arithmetic progression with terms list

### Data Models
- **PrimalityResponse**: {n: int, is_prime: bool, method: str}
- **FactorizationResponse**: {n: int, factors: Dict[str, int]}
- **ArithmeticProgressionResponse**: {a: int, d: int, length: int, terms: List[int]}

### Core Algorithms Module
- **is_prime_64()**: Deterministic Miller-Rabin for 64-bit integers
- **is_probable_prime()**: Probabilistic fallback for edge cases
- **factorize()**: Hybrid trial division + Pollard's Rho approach
- **prime_run_length()**: Arithmetic progression analyzer with early termination

## Implementation Strategy

### Development Phases
1. **Core Math Module**: Implement and test all number theory algorithms
2. **API Layer**: Build FastAPI endpoints with proper error handling
3. **Testing Suite**: Comprehensive unit tests with behavioral validation
4. **DevOps Setup**: Makefile, pre-commit hooks, and optional containerization

### Risk Mitigation
- **Algorithm Complexity**: Use proven algorithms with well-documented base sets
- **Performance Issues**: Implement timeouts and input size limits
- **Edge Cases**: Comprehensive test coverage for boundary conditions

### Testing Approach
- **Unit Tests**: Algorithm correctness with known test vectors
- **Behavioral Tests**: Endpoint validation against acceptance criteria
- **Performance Tests**: Timeout and large input handling
- **Integration Tests**: Full request/response cycle validation

## Task Breakdown Preview
High-level task categories that will be created:
- [ ] **Core Math Implementation**: Number theory algorithms (is_prime_64, factorize, prime_run_length)
- [ ] **FastAPI Application**: REST endpoints with OpenAPI documentation and error handling
- [ ] **Testing Suite**: Comprehensive unit and behavioral tests with pytest
- [ ] **DevOps Setup**: Development workflow with ruff, black, and optional Docker
- [ ] **Documentation**: API documentation and deployment instructions

## Dependencies
- **External Dependencies**: None - pure Python implementation
- **Development Dependencies**: FastAPI, Uvicorn, pytest, ruff, black
- **Python Version**: Requires Python 3.11+ for performance and type system features
- **Deployment**: Standard Python web service deployment (container-ready)

## Success Criteria (Technical)

### Performance Benchmarks
- **Response Time**: <1 second for typical 64-bit integer operations
- **Accuracy**: 100% correct primality testing for 64-bit deterministic range
- **Robustness**: Graceful handling of edge cases and invalid inputs

### Quality Gates
- **Test Coverage**: 100% coverage of core mathematical functions
- **Type Safety**: Full type hints with mypy validation
- **Code Quality**: Clean code passing ruff and black formatting
- **API Compliance**: OpenAPI specification generation and validation

### Acceptance Criteria
- **Primality Tests**: Correctly identify 2,3,5,17 as prime; 1,0,4,21 as composite
- **Factorization**: Handle special cases (1→{}, 60→{2:2,3:1,5:1}, 97→{97:1})
- **Arithmetic Progression**: Compute correct run lengths for test sequences

## Tasks Created
- [ ] 001.md - Core Number Theory Module Implementation (parallel: true)
- [ ] 002.md - FastAPI Application and Endpoints (parallel: false)
- [ ] 003.md - Comprehensive Testing Suite (parallel: false)
- [ ] 004.md - Development Workflow and Tooling Setup (parallel: true)
- [ ] 005.md - API Documentation and Deployment Guide (parallel: true)

**Total tasks**: 5
**Parallel tasks**: 3 (001, 004, 005)
**Sequential tasks**: 2 (002, 003)
**Estimated total effort**: 42-58 hours

## Estimated Effort
- **Overall Timeline**: 3-5 days for complete implementation
- **Critical Path**: Core math algorithms (2 days) → API layer (1 day) → testing (1-2 days)
- **Resource Requirements**: Single developer with strong Python and mathematical background
- **Risk Buffer**: Additional day for performance optimization and edge case handling