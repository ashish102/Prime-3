# Prime Math API - Versioning Strategy

## Overview

This document outlines the API versioning strategy for the Prime Math API, ensuring backward compatibility while enabling continuous improvement and feature development.

## Versioning Philosophy

The Prime Math API follows **Semantic Versioning (SemVer)** principles with the following guidelines:

- **MAJOR** version when making incompatible API changes
- **MINOR** version when adding functionality in a backwards compatible manner
- **PATCH** version when making backwards compatible bug fixes

Current version: **0.1.0**

## Versioning Methods

### 1. URL Path Versioning (Recommended)

Future versions will use URL path versioning for major version changes:

```
# Current (v1 implicit)
GET /prime/97
GET /factor/60
GET /progression/3/2

# Future versions
GET /v1/prime/97
GET /v2/prime/97
GET /v3/prime/97
```

### 2. Header Versioning (Alternative)

Alternative approach using custom headers:

```bash
curl -H "API-Version: 1.0" http://localhost:8000/prime/97
curl -H "API-Version: 2.0" http://localhost:8000/prime/97
```

### 3. Query Parameter Versioning (Fallback)

Fallback method for specific use cases:

```bash
curl "http://localhost:8000/prime/97?version=1.0"
curl "http://localhost:8000/prime/97?version=2.0"
```

## Version Support Policy

### Support Timeline

| Version Status | Support Duration | Security Updates | Bug Fixes | New Features |
|----------------|------------------|------------------|-----------|--------------|
| Current | Indefinite | ✅ Yes | ✅ Yes | ✅ Yes |
| Previous Major | 12 months | ✅ Yes | ✅ Yes | ❌ No |
| Legacy | 6 months | ✅ Yes | ❌ No | ❌ No |
| Deprecated | 3 months notice | ❌ No | ❌ No | ❌ No |

### Current Roadmap

- **v0.1.x**: Initial implementation (current)
- **v0.2.x**: Performance optimizations and enhanced error handling
- **v1.0.x**: Stable API with comprehensive documentation
- **v1.1.x**: Extended factorization algorithms
- **v2.0.x**: Breaking changes for improved performance

## Implementation Plan

### Phase 1: Current State (v0.1.x)

**Current Implementation**:
- No explicit versioning in URLs
- Version information in OpenAPI spec
- Semantic versioning for releases

**API Endpoints**:
```
GET /health
GET /prime/{n}
GET /factor/{n}
GET /progression/{start}/{diff}
```

### Phase 2: Version-Aware Routes (v0.2.x)

**Backwards Compatible Enhancement**:
- Add version detection middleware
- Support both versioned and unversioned routes
- Default to latest version for unversioned requests

**Implementation**:
```python
from fastapi import FastAPI, Request
from typing import Optional

def get_api_version(request: Request) -> str:
    """Extract API version from request."""
    # 1. Check URL path
    if request.url.path.startswith('/v'):
        return request.url.path.split('/')[1]

    # 2. Check custom header
    if 'API-Version' in request.headers:
        return request.headers['API-Version']

    # 3. Check query parameter
    if 'version' in request.query_params:
        return request.query_params['version']

    # 4. Default to latest
    return 'v1'

app = FastAPI()

# Version-aware middleware
@app.middleware("http")
async def version_middleware(request: Request, call_next):
    version = get_api_version(request)
    request.state.api_version = version
    response = await call_next(request)
    response.headers["API-Version"] = version
    return response
```

### Phase 3: Explicit Versioning (v1.0.x)

**Major Version Release**:
- Introduce `/v1/` prefix for all endpoints
- Maintain backward compatibility with unversioned routes
- Add deprecation warnings for unversioned endpoints

**New URL Structure**:
```
# V1 endpoints (explicit)
GET /v1/health
GET /v1/prime/{n}
GET /v1/factor/{n}
GET /v1/progression/{start}/{diff}

# Legacy endpoints (deprecated but functional)
GET /health        # → redirect to /v1/health
GET /prime/{n}     # → redirect to /v1/prime/{n}
```

### Phase 4: Version-Specific Features (v2.0.x)

**Breaking Changes Example**:
- Enhanced response formats
- New algorithm implementations
- Modified parameter validation

**V2 Features**:
```json
// V1 Response Format
{
  "number": 97,
  "is_prime": true
}

// V2 Response Format (Enhanced)
{
  "number": 97,
  "is_prime": true,
  "algorithm": "miller-rabin-deterministic",
  "execution_time_ms": 0.42,
  "confidence": 1.0,
  "metadata": {
    "witnesses_used": ["2", "3", "5"],
    "complexity": "O(log³ n)"
  }
}
```

## Backward Compatibility Strategy

### 1. Graceful Deprecation

```python
import warnings
from fastapi import FastAPI, Request
from datetime import datetime, timedelta

# Deprecation decorator
def deprecated_endpoint(version: str, removal_date: str):
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            warnings.warn(
                f"Endpoint deprecated in {version}, "
                f"will be removed on {removal_date}",
                DeprecationWarning
            )
            # Add deprecation headers
            response = await func(request, *args, **kwargs)
            response.headers["Deprecation"] = "true"
            response.headers["Sunset"] = removal_date
            response.headers["Link"] = f'</v2{request.url.path}>; rel="successor-version"'
            return response
        return wrapper
    return decorator

# Usage
@app.get("/prime/{n}")
@deprecated_endpoint("v1.1.0", "2024-12-31")
async def check_prime_legacy(n: int):
    return await check_prime_v1(n)
```

### 2. Content Negotiation

```python
from fastapi import FastAPI, Header
from typing import Optional

@app.get("/prime/{n}")
async def check_prime(
    n: int,
    accept_version: Optional[str] = Header(None, alias="Accept-Version")
):
    version = accept_version or "v1"

    if version == "v1":
        return check_prime_v1(n)
    elif version == "v2":
        return check_prime_v2(n)
    else:
        raise HTTPException(
            status_code=406,
            detail=f"API version {version} not supported"
        )
```

### 3. Response Format Negotiation

```python
from pydantic import BaseModel
from typing import Union

# V1 Models
class PrimeResponseV1(BaseModel):
    number: int
    is_prime: bool

# V2 Models
class PrimeResponseV2(BaseModel):
    number: int
    is_prime: bool
    algorithm: str
    execution_time_ms: float
    confidence: float
    metadata: dict

# Version-aware endpoint
@app.get("/v1/prime/{n}", response_model=PrimeResponseV1)
async def check_prime_v1(n: int) -> PrimeResponseV1:
    is_prime = is_prime_64(n)
    return PrimeResponseV1(number=n, is_prime=is_prime)

@app.get("/v2/prime/{n}", response_model=PrimeResponseV2)
async def check_prime_v2(n: int) -> PrimeResponseV2:
    start_time = time.time()
    is_prime = is_prime_64(n)
    execution_time = (time.time() - start_time) * 1000

    return PrimeResponseV2(
        number=n,
        is_prime=is_prime,
        algorithm="miller-rabin-deterministic",
        execution_time_ms=execution_time,
        confidence=1.0,
        metadata={
            "witnesses_used": ["2", "3", "5", "7"],
            "complexity": "O(log³ n)"
        }
    )
```

## Client Migration Guide

### Version Detection

Clients should implement version detection:

```python
import requests

def get_api_info(base_url: str):
    """Detect supported API versions."""
    response = requests.get(f"{base_url}/")
    data = response.json()
    return {
        "version": data.get("version"),
        "supported_versions": response.headers.get("Supported-Versions", "v1").split(",")
    }

# Usage
api_info = get_api_info("http://localhost:8000")
print(f"Current version: {api_info['version']}")
print(f"Supported: {api_info['supported_versions']}")
```

### Version-Aware Client

```python
class PrimeMathClient:
    def __init__(self, base_url: str, api_version: str = "v1"):
        self.base_url = base_url.rstrip('/')
        self.api_version = api_version
        self.session = requests.Session()
        self.session.headers.update({"API-Version": api_version})

    def check_prime(self, n: int):
        """Check if number is prime using specified API version."""
        url = f"{self.base_url}/{self.api_version}/prime/{n}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def migrate_to_version(self, new_version: str):
        """Migrate client to new API version."""
        self.api_version = new_version
        self.session.headers.update({"API-Version": new_version})

# Usage
client = PrimeMathClient("http://localhost:8000", "v1")
result = client.check_prime(97)

# Upgrade to v2 when available
client.migrate_to_version("v2")
```

### Gradual Migration Strategy

1. **Phase 1**: Detect current version support
2. **Phase 2**: Test new version in staging
3. **Phase 3**: Gradual rollout with fallback
4. **Phase 4**: Complete migration

```python
class MigrationAwarePrimeMathClient:
    def __init__(self, base_url: str, preferred_version: str = "v2", fallback_version: str = "v1"):
        self.base_url = base_url
        self.preferred_version = preferred_version
        self.fallback_version = fallback_version
        self.current_version = self._detect_best_version()

    def _detect_best_version(self) -> str:
        """Detect the best available version."""
        try:
            # Try preferred version
            response = requests.get(
                f"{self.base_url}/{self.preferred_version}/health",
                timeout=5
            )
            if response.status_code == 200:
                return self.preferred_version
        except:
            pass

        # Fall back to stable version
        return self.fallback_version

    def check_prime(self, n: int):
        """Check prime with automatic fallback."""
        try:
            return self._make_request(self.current_version, "prime", n)
        except Exception:
            # Fallback to older version
            if self.current_version != self.fallback_version:
                return self._make_request(self.fallback_version, "prime", n)
            raise
```

## Testing Strategy

### Version Compatibility Testing

```python
import pytest
from fastapi.testclient import TestClient

def test_version_compatibility():
    """Test that all supported versions work correctly."""
    versions = ["v1", "v2"]
    test_cases = [97, 100, 2]

    for version in versions:
        for number in test_cases:
            response = client.get(f"/{version}/prime/{number}")
            assert response.status_code == 200
            data = response.json()
            assert "number" in data
            assert "is_prime" in data
            assert data["number"] == number

def test_version_negotiation():
    """Test version negotiation via headers."""
    # Test header-based version selection
    response = client.get("/prime/97", headers={"API-Version": "v1"})
    assert response.status_code == 200
    assert response.headers["API-Version"] == "v1"

def test_deprecation_warnings():
    """Test that deprecated endpoints return proper warnings."""
    response = client.get("/prime/97")  # Unversioned, deprecated
    assert "Deprecation" in response.headers
    assert "Sunset" in response.headers
```

### Contract Testing

```python
import jsonschema

# V1 Schema
v1_prime_schema = {
    "type": "object",
    "properties": {
        "number": {"type": "integer"},
        "is_prime": {"type": "boolean"}
    },
    "required": ["number", "is_prime"]
}

# V2 Schema (extended)
v2_prime_schema = {
    "type": "object",
    "properties": {
        "number": {"type": "integer"},
        "is_prime": {"type": "boolean"},
        "algorithm": {"type": "string"},
        "execution_time_ms": {"type": "number"},
        "confidence": {"type": "number"},
        "metadata": {"type": "object"}
    },
    "required": ["number", "is_prime", "algorithm", "execution_time_ms", "confidence"]
}

def test_response_schemas():
    """Validate response schemas for different versions."""
    # Test V1 response
    response = client.get("/v1/prime/97")
    jsonschema.validate(response.json(), v1_prime_schema)

    # Test V2 response
    response = client.get("/v2/prime/97")
    jsonschema.validate(response.json(), v2_prime_schema)
```

## Documentation Strategy

### Version-Specific Documentation

1. **Separate OpenAPI specs** for each major version
2. **Version-aware interactive docs** at `/docs?version=v1`
3. **Migration guides** for each version transition
4. **Changelog** with version-specific changes

### Documentation Structure

```
/docs
├── v1/
│   ├── openapi.json
│   ├── swagger-ui/
│   └── migration-from-v0.md
├── v2/
│   ├── openapi.json
│   ├── swagger-ui/
│   └── migration-from-v1.md
└── versioning-guide.md
```

### Automated Documentation Updates

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

def custom_openapi(app: FastAPI, version: str):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=f"Prime Math API {version}",
        version=version,
        description=f"Prime Math API version {version} documentation",
        routes=app.routes,
    )

    # Add version-specific metadata
    openapi_schema["info"]["x-api-version"] = version
    openapi_schema["servers"] = [
        {"url": f"http://localhost:8000/{version}"}
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema
```

## Monitoring and Analytics

### Version Usage Tracking

```python
from collections import Counter
import logging

version_usage = Counter()

@app.middleware("http")
async def track_version_usage(request: Request, call_next):
    version = get_api_version(request)
    version_usage[version] += 1

    # Log version usage
    logging.info(f"API request: {version} - {request.url.path}")

    response = await call_next(request)
    return response

def get_version_statistics():
    """Get version usage statistics."""
    total = sum(version_usage.values())
    return {
        version: {"count": count, "percentage": count/total*100}
        for version, count in version_usage.items()
    }
```

### Deprecation Metrics

Track deprecated endpoint usage for migration planning:

```python
deprecated_usage = Counter()

def track_deprecated_usage(endpoint: str, version: str):
    """Track usage of deprecated endpoints."""
    key = f"{endpoint}@{version}"
    deprecated_usage[key] += 1

    # Alert if usage is high
    if deprecated_usage[key] % 100 == 0:
        logging.warning(f"Deprecated endpoint {key} used {deprecated_usage[key]} times")
```

## Summary

This versioning strategy ensures:

1. **Backward Compatibility**: Existing clients continue to work
2. **Smooth Migrations**: Clear migration paths and documentation
3. **Flexible Evolution**: Support for new features and improvements
4. **Client Control**: Clients can choose when to upgrade
5. **Monitoring**: Track usage patterns and deprecation metrics

The strategy balances stability with innovation, ensuring the Prime Math API can evolve while maintaining reliability for existing users.