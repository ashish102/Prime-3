# Prime Math API - Rate Limiting Strategy

## Overview

This document outlines comprehensive rate limiting strategies for the Prime Math API to ensure fair usage, prevent abuse, and maintain service quality for all users.

## Rate Limiting Rationale

### Why Rate Limiting is Essential

1. **Resource Protection**: Prevent computational resource exhaustion
2. **Fair Usage**: Ensure equitable access for all users
3. **DDoS Prevention**: Mitigate denial-of-service attacks
4. **Cost Control**: Manage infrastructure costs
5. **Quality of Service**: Maintain consistent response times

### Prime Math API Specific Considerations

- **Computational Complexity**: Operations vary from O(1) to O(log³ n)
- **Input Sensitivity**: Large numbers require more processing time
- **Memory Usage**: Factorization can consume significant memory
- **CPU Intensity**: Prime testing and factorization are CPU-bound

## Rate Limiting Strategy

### Tiered Rate Limiting Approach

#### Tier 1: Basic Usage (Default)
```
- Requests per minute: 60
- Requests per hour: 1,000
- Concurrent requests: 5
- Max input size: 2^32 (4,294,967,295)
```

#### Tier 2: Moderate Usage
```
- Requests per minute: 300
- Requests per hour: 10,000
- Concurrent requests: 20
- Max input size: 2^48
```

#### Tier 3: Heavy Usage (API Key Required)
```
- Requests per minute: 1,000
- Requests per hour: 50,000
- Concurrent requests: 50
- Max input size: 2^64-1 (full range)
```

### Endpoint-Specific Limits

Different endpoints have different computational costs:

#### `/health` Endpoint
```yaml
rate_limit:
  requests_per_minute: 300
  requests_per_hour: unlimited
  reasoning: "Lightweight endpoint for monitoring"
```

#### `/prime/{n}` Endpoint
```yaml
rate_limit:
  requests_per_minute: 60
  requests_per_hour: 1000
  reasoning: "Deterministic algorithm with predictable performance"
  input_based_limiting:
    small_numbers: # n < 10^6
      requests_per_minute: 100
    large_numbers: # n > 10^12
      requests_per_minute: 20
```

#### `/factor/{n}` Endpoint
```yaml
rate_limit:
  requests_per_minute: 30
  requests_per_hour: 500
  reasoning: "Most computationally expensive operation"
  input_based_limiting:
    composite_with_small_factors:
      requests_per_minute: 50
    large_primes_or_semiprimes:
      requests_per_minute: 5
```

#### `/progression/{start}/{diff}` Endpoint
```yaml
rate_limit:
  requests_per_minute: 40
  requests_per_hour: 800
  reasoning: "Multiple prime checks required"
  parameter_based_limiting:
    max_terms_limit: 10000
    large_diff_values: # diff > 1000
      requests_per_minute: 20
```

## Implementation Strategies

### 1. Reverse Proxy Rate Limiting (Recommended)

#### Nginx Configuration

```nginx
# Rate limiting zones
http {
    # Basic rate limiting
    limit_req_zone $binary_remote_addr zone=api_basic:10m rate=60r/m;

    # Heavy endpoints
    limit_req_zone $binary_remote_addr zone=api_heavy:10m rate=30r/m;

    # Health checks (more permissive)
    limit_req_zone $binary_remote_addr zone=api_health:10m rate=300r/m;

    # API key based limiting (future)
    limit_req_zone $http_x_api_key zone=api_key_tier2:10m rate=300r/m;
    limit_req_zone $http_x_api_key zone=api_key_tier3:10m rate=1000r/m;
}

server {
    # Health endpoint - most permissive
    location /health {
        limit_req zone=api_health burst=50 nodelay;
        proxy_pass http://prime_api;
    }

    # Prime endpoint - moderate limiting
    location /prime {
        limit_req zone=api_basic burst=20 nodelay;
        proxy_pass http://prime_api;
    }

    # Factor endpoint - strict limiting
    location /factor {
        limit_req zone=api_heavy burst=10 nodelay;
        proxy_pass http://prime_api;
    }

    # Progression endpoint - moderate limiting
    location /progression {
        limit_req zone=api_basic burst=15 nodelay;
        proxy_pass http://prime_api;
    }

    # API key based routing (future enhancement)
    location /v2/ {
        if ($http_x_api_key ~ "^tier2_") {
            limit_req zone=api_key_tier2 burst=100 nodelay;
        }
        if ($http_x_api_key ~ "^tier3_") {
            limit_req zone=api_key_tier3 burst=200 nodelay;
        }
        proxy_pass http://prime_api;
    }
}
```

#### Traefik Configuration

```yaml
# traefik.yml
api:
  dashboard: true

entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

providers:
  docker:
    exposedByDefault: false

# Rate limiting middleware
http:
  middlewares:
    # Basic rate limiting
    api-rate-limit:
      rateLimit:
        burst: 20
        average: 60  # requests per minute

    # Heavy endpoints
    heavy-rate-limit:
      rateLimit:
        burst: 10
        average: 30

    # Health checks
    health-rate-limit:
      rateLimit:
        burst: 50
        average: 300

# Docker Compose labels
services:
  api:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.prime-api.middlewares=api-rate-limit"
      - "traefik.http.routers.prime-health.rule=PathPrefix(`/health`)"
      - "traefik.http.routers.prime-health.middlewares=health-rate-limit"
      - "traefik.http.routers.prime-factor.rule=PathPrefix(`/factor`)"
      - "traefik.http.routers.prime-factor.middlewares=heavy-rate-limit"
```

### 2. Application-Level Rate Limiting

#### FastAPI with slowapi

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Endpoint-specific rate limiting
@app.get("/health")
@limiter.limit("300/minute")
async def health_check(request: Request):
    return {"status": "healthy"}

@app.get("/prime/{n}")
@limiter.limit("60/minute")
async def check_prime(request: Request, n: int):
    # Additional input-based limiting
    if n > 10**12:
        # Apply stricter limit for large numbers
        limiter.limit("20/minute")(request)

    return await check_prime_logic(n)

@app.get("/factor/{n}")
@limiter.limit("30/minute")
async def get_factors(request: Request, n: int):
    # Computational complexity based limiting
    estimated_complexity = estimate_factorization_complexity(n)
    if estimated_complexity > HIGH_COMPLEXITY_THRESHOLD:
        limiter.limit("5/minute")(request)

    return await factorize_logic(n)
```

#### Custom Rate Limiting Middleware

```python
import asyncio
import time
from collections import defaultdict, deque
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class SmartRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, default_requests_per_minute: int = 60):
        super().__init__(app)
        self.default_rpm = default_requests_per_minute
        self.request_counts = defaultdict(deque)
        self.endpoint_limits = {
            "/health": 300,
            "/prime": 60,
            "/factor": 30,
            "/progression": 40,
        }

    def get_client_id(self, request: Request) -> str:
        """Extract client identifier."""
        # Check for API key first
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"

        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        return request.client.host

    def get_rate_limit(self, request: Request) -> int:
        """Get rate limit for specific endpoint."""
        path = request.url.path

        # Check for exact matches
        if path in self.endpoint_limits:
            return self.endpoint_limits[path]

        # Check for pattern matches
        if path.startswith("/prime/"):
            return self.endpoint_limits["/prime"]
        elif path.startswith("/factor/"):
            return self.endpoint_limits["/factor"]
        elif path.startswith("/progression/"):
            return self.endpoint_limits["/progression"]

        return self.default_rpm

    def is_rate_limited(self, client_id: str, rate_limit: int) -> bool:
        """Check if client exceeds rate limit."""
        now = time.time()
        minute_ago = now - 60

        # Clean old requests
        client_requests = self.request_counts[client_id]
        while client_requests and client_requests[0] < minute_ago:
            client_requests.popleft()

        # Check current count
        if len(client_requests) >= rate_limit:
            return True

        # Add current request
        client_requests.append(now)
        return False

    async def dispatch(self, request: Request, call_next):
        client_id = self.get_client_id(request)
        rate_limit = self.get_rate_limit(request)

        if self.is_rate_limited(client_id, rate_limit):
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": rate_limit,
                    "window": "1 minute",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )

        response = await call_next(request)

        # Add rate limit headers
        remaining = max(0, rate_limit - len(self.request_counts[client_id]))
        response.headers["X-RateLimit-Limit"] = str(rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)

        return response

# Add middleware to app
app.add_middleware(SmartRateLimitMiddleware)
```

### 3. Input-Based Rate Limiting

```python
import math

def estimate_computation_cost(endpoint: str, **params) -> float:
    """Estimate computational cost for dynamic rate limiting."""

    if endpoint == "prime":
        n = params.get("n", 0)
        if n < 1000:
            return 1.0  # Very fast
        elif n < 10**6:
            return 2.0  # Fast
        elif n < 10**12:
            return 5.0  # Moderate
        else:
            return 10.0  # Expensive

    elif endpoint == "factor":
        n = params.get("n", 0)
        if n < 1000:
            return 2.0
        elif n < 10**6:
            return 5.0
        elif n < 10**9:
            return 10.0
        else:
            # For large numbers, cost depends on factor structure
            # This is a rough estimate
            return min(50.0, math.log10(n) * 5)

    elif endpoint == "progression":
        start = params.get("start", 0)
        diff = params.get("diff", 1)
        max_terms = params.get("max_terms", 1000)

        # Cost scales with max_terms and complexity of numbers
        base_cost = max_terms / 100.0
        number_complexity = math.log10(max(start, diff)) if max(start, diff) > 0 else 1
        return base_cost * number_complexity

    return 1.0

class CostBasedRateLimiter:
    def __init__(self, cost_limit_per_minute: float = 300.0):
        self.cost_limit = cost_limit_per_minute
        self.client_costs = defaultdict(deque)

    def can_process(self, client_id: str, cost: float) -> bool:
        """Check if client can afford the computational cost."""
        now = time.time()
        minute_ago = now - 60

        # Clean old costs
        client_cost_history = self.client_costs[client_id]
        while client_cost_history and client_cost_history[0][0] < minute_ago:
            client_cost_history.popleft()

        # Calculate current cost usage
        current_cost = sum(cost for _, cost in client_cost_history)

        if current_cost + cost > self.cost_limit:
            return False

        # Add current cost
        client_cost_history.append((now, cost))
        return True
```

## Advanced Rate Limiting Features

### 1. Adaptive Rate Limiting

```python
class AdaptiveRateLimiter:
    def __init__(self):
        self.base_limits = {
            "/prime": 60,
            "/factor": 30,
            "/progression": 40
        }
        self.system_load_threshold = 0.8
        self.current_multiplier = 1.0

    def get_system_load(self) -> float:
        """Get current system load (CPU, memory, etc.)."""
        import psutil
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        return max(cpu_percent, memory_percent) / 100.0

    def adjust_rate_limits(self):
        """Adjust rate limits based on system load."""
        system_load = self.get_system_load()

        if system_load > self.system_load_threshold:
            # Reduce rate limits when system is under pressure
            self.current_multiplier = max(0.1, 1.0 - system_load)
        else:
            # Gradually restore rate limits
            self.current_multiplier = min(1.0, self.current_multiplier + 0.1)

    def get_adjusted_limit(self, endpoint: str) -> int:
        """Get rate limit adjusted for current system load."""
        base_limit = self.base_limits.get(endpoint, 60)
        return int(base_limit * self.current_multiplier)
```

### 2. User Behavior Analysis

```python
class BehaviorBasedRateLimiter:
    def __init__(self):
        self.user_patterns = defaultdict(dict)
        self.abuse_threshold = 0.8

    def analyze_request_pattern(self, client_id: str, request: Request):
        """Analyze user behavior patterns."""
        pattern = self.user_patterns[client_id]

        # Track request intervals
        now = time.time()
        last_request = pattern.get("last_request", now)
        interval = now - last_request

        # Update pattern data
        pattern["last_request"] = now
        pattern.setdefault("intervals", deque(maxlen=100)).append(interval)
        pattern.setdefault("endpoints", deque(maxlen=100)).append(request.url.path)

        # Calculate abuse score
        abuse_score = self.calculate_abuse_score(pattern)
        pattern["abuse_score"] = abuse_score

        return abuse_score

    def calculate_abuse_score(self, pattern: dict) -> float:
        """Calculate abuse score based on behavior patterns."""
        score = 0.0

        # Very frequent requests (bot-like behavior)
        intervals = list(pattern.get("intervals", []))
        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            if avg_interval < 0.1:  # More than 10 req/sec
                score += 0.5

        # Repetitive endpoint usage
        endpoints = list(pattern.get("endpoints", []))
        if endpoints and len(set(endpoints)) / len(endpoints) < 0.1:
            score += 0.3

        return min(1.0, score)

    def should_apply_strict_limit(self, client_id: str) -> bool:
        """Determine if client should get strict rate limits."""
        pattern = self.user_patterns.get(client_id, {})
        abuse_score = pattern.get("abuse_score", 0.0)
        return abuse_score > self.abuse_threshold
```

## Rate Limiting Headers

### Standard Rate Limiting Headers

Always include these headers in responses:

```python
def add_rate_limit_headers(response, limit: int, remaining: int, reset_time: int):
    """Add standard rate limiting headers."""
    response.headers["X-RateLimit-Limit"] = str(limit)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(reset_time)

    # Additional context headers
    response.headers["X-RateLimit-Policy"] = "60;w=60"  # 60 per 60-second window
    response.headers["X-RateLimit-Scope"] = "user"      # Per-user limit
```

### Rate Limit Exceeded Response

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "details": {
      "limit": 60,
      "window": "1 minute",
      "reset_time": "2024-01-15T10:31:00Z",
      "retry_after": 45
    }
  },
  "meta": {
    "endpoint": "/prime/{n}",
    "cost_model": "computational",
    "upgrade_options": {
      "api_key": "Contact support for API key access",
      "enterprise": "Enterprise plans available"
    }
  }
}
```

## Monitoring and Alerting

### Key Metrics to Monitor

1. **Rate Limiting Effectiveness**
   - Requests blocked per minute
   - Rate limit hit rate by endpoint
   - False positive rate (legitimate users blocked)

2. **System Performance Impact**
   - Response time distribution
   - System resource utilization
   - Queue length and processing time

3. **User Behavior Analysis**
   - Request patterns by client
   - Abuse detection accuracy
   - API key usage patterns

### Monitoring Implementation

```python
import logging
from prometheus_client import Counter, Histogram, Gauge

# Metrics
rate_limit_blocks = Counter('rate_limit_blocks_total', 'Total rate limit blocks', ['endpoint', 'reason'])
request_duration = Histogram('request_duration_seconds', 'Request duration', ['endpoint'])
active_clients = Gauge('active_clients_total', 'Number of active clients')

class RateLimitingMetrics:
    @staticmethod
    def record_block(endpoint: str, reason: str):
        """Record a rate limit block."""
        rate_limit_blocks.labels(endpoint=endpoint, reason=reason).inc()
        logging.warning(f"Rate limit block: {endpoint} - {reason}")

    @staticmethod
    def record_request_duration(endpoint: str, duration: float):
        """Record request processing time."""
        request_duration.labels(endpoint=endpoint).observe(duration)
```

### Alert Rules

```yaml
# Prometheus alert rules
groups:
- name: rate_limiting
  rules:
  - alert: HighRateLimitBlocks
    expr: rate(rate_limit_blocks_total[5m]) > 10
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High rate of rate limit blocks"
      description: "Rate limit blocks are occurring at {{ $value }} per second"

  - alert: SystemUnderPressure
    expr: system_cpu_usage > 0.8 and rate_limit_multiplier < 0.5
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "System under pressure with reduced rate limits"
      description: "CPU usage is {{ $value }}% and rate limits are reduced"
```

## Client Implementation Guidelines

### Best Practices for API Clients

1. **Respect Rate Limits**
   ```python
   import time
   import requests
   from datetime import datetime

   class RateLimitAwareClient:
       def __init__(self, base_url: str):
           self.base_url = base_url
           self.session = requests.Session()

       def make_request(self, endpoint: str, **kwargs):
           """Make request with automatic rate limit handling."""
           while True:
               response = self.session.get(f"{self.base_url}{endpoint}", **kwargs)

               if response.status_code == 429:
                   # Rate limited - wait and retry
                   retry_after = int(response.headers.get('Retry-After', 60))
                   time.sleep(retry_after)
                   continue

               return response
   ```

2. **Implement Client-Side Rate Limiting**
   ```python
   import asyncio
   from asyncio import Semaphore

   class ClientSideRateLimiter:
       def __init__(self, requests_per_minute: int = 50):
           self.rpm = requests_per_minute
           self.semaphore = Semaphore(requests_per_minute)
           self.request_times = []

       async def acquire(self):
           """Acquire permission to make a request."""
           async with self.semaphore:
               now = asyncio.get_event_loop().time()
               # Remove old timestamps
               self.request_times = [t for t in self.request_times if now - t < 60]

               if len(self.request_times) >= self.rpm:
                   # Wait until we can make another request
                   wait_time = 60 - (now - self.request_times[0])
                   await asyncio.sleep(wait_time)

               self.request_times.append(now)
   ```

### Error Handling

```python
def handle_rate_limit_error(response):
    """Handle rate limit errors gracefully."""
    if response.status_code == 429:
        error_data = response.json().get("error", {})
        retry_after = error_data.get("details", {}).get("retry_after", 60)

        print(f"Rate limited. Retry after {retry_after} seconds")

        # Log the rate limit details
        logging.info(f"Rate limit: {error_data}")

        # Return appropriate action
        return {
            "action": "retry",
            "wait_time": retry_after,
            "upgrade_options": error_data.get("upgrade_options")
        }

    return None
```

## Future Enhancements

### 1. API Key Based Tiering

```python
class APIKeyTierManager:
    def __init__(self):
        self.tiers = {
            "basic": {"rpm": 60, "max_input": 2**32},
            "pro": {"rpm": 300, "max_input": 2**48},
            "enterprise": {"rpm": 1000, "max_input": 2**64-1}
        }

    def get_tier_for_key(self, api_key: str) -> str:
        """Get tier for API key (implement with database lookup)."""
        # This would typically query a database
        return "basic"  # placeholder

    def get_limits_for_tier(self, tier: str) -> dict:
        """Get rate limits for tier."""
        return self.tiers.get(tier, self.tiers["basic"])
```

### 2. Machine Learning Based Abuse Detection

```python
class MLAbuseDetector:
    def __init__(self):
        self.model = self.load_model()  # Load pre-trained model

    def predict_abuse_probability(self, request_features: dict) -> float:
        """Predict probability that request is abusive."""
        # Features: request_rate, endpoint_diversity, payload_size, etc.
        features = self.extract_features(request_features)
        return self.model.predict_proba([features])[0][1]  # Probability of abuse

    def should_block(self, abuse_probability: float) -> bool:
        """Determine if request should be blocked."""
        return abuse_probability > 0.8
```

### 3. Geographic Rate Limiting

```python
class GeographicRateLimiter:
    def __init__(self):
        self.country_limits = {
            "US": 100,    # Requests per minute
            "EU": 80,
            "default": 60
        }

    def get_country_from_ip(self, ip_address: str) -> str:
        """Get country from IP address (use GeoIP service)."""
        # Implement with GeoIP lookup
        return "US"  # placeholder

    def get_limit_for_country(self, country: str) -> int:
        """Get rate limit for country."""
        return self.country_limits.get(country, self.country_limits["default"])
```

## Summary

This rate limiting strategy provides:

1. **Multi-layered Protection**: Reverse proxy + application-level limiting
2. **Intelligent Adaptation**: Cost-based and behavior-based limiting
3. **Fair Usage**: Tiered limits based on usage patterns
4. **Monitoring**: Comprehensive metrics and alerting
5. **Client-Friendly**: Clear headers and error messages
6. **Scalable**: Designed for high-traffic production environments

The strategy balances protection against abuse while maintaining a good user experience for legitimate users. Regular monitoring and adjustment based on usage patterns and system performance will ensure optimal protection and service quality.