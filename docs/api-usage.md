# Prime Math API - Usage Guide

## Overview

The Prime Math API provides high-performance number theory operations through REST endpoints. This guide covers practical usage examples, response formats, and best practices.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com` (replace with actual deployment URL)

## Authentication

Currently, no authentication is required. For production deployments, consider implementing rate limiting and API keys.

## API Endpoints

### 1. Health Check

Check if the API service is running and healthy.

**Endpoint**: `GET /health`

**Example Request**:
```bash
curl -X GET "http://localhost:8000/health"
```

**Example Response**:
```json
{
  "status": "healthy",
  "service": "Prime Math API",
  "version": "0.1.0"
}
```

**Use Cases**:
- Load balancer health checks
- Monitoring system probes
- Service availability verification

---

### 2. Primality Testing

Test if a number is prime using deterministic Miller-Rabin algorithm.

**Endpoint**: `GET /prime/{n}`

**Parameters**:
- `n` (path parameter): Non-negative integer to test (0 ≤ n ≤ 2^64-1)

**Example Requests**:

```bash
# Test if 97 is prime
curl -X GET "http://localhost:8000/prime/97"

# Test a large prime number
curl -X GET "http://localhost:8000/prime/982451653"

# Test a composite number
curl -X GET "http://localhost:8000/prime/100"
```

**Example Responses**:

```json
// Prime number
{
  "number": 97,
  "is_prime": true
}

// Composite number
{
  "number": 100,
  "is_prime": false
}

// Large prime
{
  "number": 982451653,
  "is_prime": true
}
```

**Performance**:
- Small numbers (< 10^6): < 1ms
- Medium numbers (10^6 - 10^12): 1-10ms
- Large numbers (10^12 - 2^64): 10-100ms

**Error Examples**:

```bash
# Negative number
curl -X GET "http://localhost:8000/prime/-5"
# Response: {"detail": "n must be non-negative, got -5"}

# Number too large
curl -X GET "http://localhost:8000/prime/99999999999999999999"
# Response: {"detail": "n exceeds 64-bit range (max: 18446744073709551615), got 99999999999999999999"}
```

---

### 3. Integer Factorization

Get the complete prime factorization of a number.

**Endpoint**: `GET /factor/{n}`

**Parameters**:
- `n` (path parameter): Non-negative integer to factorize (0 ≤ n ≤ 2^64-1)

**Example Requests**:

```bash
# Factor a small number
curl -X GET "http://localhost:8000/factor/60"

# Factor a perfect square
curl -X GET "http://localhost:8000/factor/144"

# Factor a large semiprime
curl -X GET "http://localhost:8000/factor/1073741827"
```

**Example Responses**:

```json
// 60 = 2² × 3 × 5
{
  "number": 60,
  "factors": [2, 2, 3, 5],
  "factor_count": 4
}

// 144 = 2⁴ × 3²
{
  "number": 144,
  "factors": [2, 2, 2, 2, 3, 3],
  "factor_count": 6
}

// Prime number (factors itself)
{
  "number": 97,
  "factors": [97],
  "factor_count": 1
}

// 1 (special case)
{
  "number": 1,
  "factors": [],
  "factor_count": 0
}
```

**Performance Notes**:
- Numbers with small factors: < 1ms
- Numbers with medium factors: 1-100ms
- Large primes or semiprimes: 100ms-10s
- Performance depends heavily on factor sizes

**Special Cases**:
- `0`: Returns `[0]`
- `1`: Returns `[]` (empty factors list)
- Prime numbers: Returns `[n]`

---

### 4. Arithmetic Progressions

Find consecutive primes in arithmetic progression.

**Endpoint**: `GET /progression/{start}/{diff}?max_terms={limit}`

**Parameters**:
- `start` (path parameter): Starting number of the sequence (≥ 0)
- `diff` (path parameter): Common difference (> 0)
- `max_terms` (query parameter, optional): Maximum terms to check (default: 1000, max: 10000)

**Example Requests**:

```bash
# Find primes in progression starting at 3 with difference 2
curl -X GET "http://localhost:8000/progression/3/2"

# Limit search to 50 terms
curl -X GET "http://localhost:8000/progression/7/6?max_terms=50"

# Large difference
curl -X GET "http://localhost:8000/progression/7/30"
```

**Example Responses**:

```json
// 3, 5, 7, 11, 13 (arithmetic progression with diff=2)
{
  "start": 3,
  "diff": 2,
  "length": 5,
  "primes": [3, 5, 7, 11, 13]
}

// 7, 13, 19 (arithmetic progression with diff=6)
{
  "start": 7,
  "diff": 6,
  "length": 3,
  "primes": [7, 13, 19]
}

// No consecutive primes found
{
  "start": 4,
  "diff": 2,
  "length": 0,
  "primes": []
}
```

**Algorithm Details**:
- Finds the longest initial run of consecutive primes
- Stops at the first composite number in the sequence
- Returns all consecutive primes found before the first gap

---

## Error Handling

The API uses standard HTTP status codes and returns detailed error messages.

### Common Error Responses

**400 Bad Request** - Invalid input parameters:
```json
{
  "detail": "n must be non-negative, got -5"
}
```

**422 Unprocessable Entity** - Validation error:
```json
{
  "detail": [
    {
      "loc": ["path", "n"],
      "msg": "ensure this value is greater than or equal to 0",
      "type": "value_error.number.not_ge"
    }
  ]
}
```

**500 Internal Server Error** - Server processing error:
```json
{
  "detail": "Internal server error: ..."
}
```

### Error Scenarios

1. **Negative numbers**: All endpoints reject negative inputs
2. **Out of range**: Numbers exceeding 2^64-1 are rejected
3. **Invalid types**: Non-integer inputs cause validation errors
4. **Resource limits**: Excessive max_terms values are rejected

---

## Rate Limiting & Performance

### Current Limitations
- No built-in rate limiting (implement client-side limiting)
- Memory usage scales with problem complexity
- CPU-intensive operations for large numbers

### Recommended Usage Patterns

1. **Batch Processing**: Group requests when possible
2. **Caching**: Cache results for frequently tested numbers
3. **Progressive Loading**: Start with smaller numbers when exploring ranges
4. **Timeouts**: Set reasonable client timeouts (10-30 seconds for large numbers)

### Performance Guidelines

| Operation | Input Range | Expected Response Time |
|-----------|-------------|----------------------|
| Primality | < 10^6 | < 1ms |
| Primality | 10^6 - 10^12 | 1-10ms |
| Primality | 10^12 - 2^64 | 10-100ms |
| Factorization | < 10^6 | < 1ms |
| Factorization | 10^6 - 10^9 | 1-100ms |
| Factorization | Large primes/semiprimes | 100ms-10s |
| Progressions | diff < 100 | < 10ms |
| Progressions | diff > 1000 | 10-100ms |

---

## Client Examples

### Python with requests

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Check if a number is prime
response = requests.get(f"{BASE_URL}/prime/97")
data = response.json()
print(f"Is 97 prime? {data['is_prime']}")

# Get prime factorization
response = requests.get(f"{BASE_URL}/factor/60")
data = response.json()
print(f"60 = {' × '.join(map(str, data['factors']))}")

# Find arithmetic progression
response = requests.get(f"{BASE_URL}/progression/3/2?max_terms=100")
data = response.json()
print(f"Found {data['length']} consecutive primes: {data['primes']}")
```

### JavaScript with fetch

```javascript
const BASE_URL = "http://localhost:8000";

async function checkPrime(n) {
  const response = await fetch(`${BASE_URL}/prime/${n}`);
  const data = await response.json();
  return data.is_prime;
}

async function getFactors(n) {
  const response = await fetch(`${BASE_URL}/factor/${n}`);
  const data = await response.json();
  return data.factors;
}

async function findProgression(start, diff, maxTerms = 1000) {
  const response = await fetch(
    `${BASE_URL}/progression/${start}/${diff}?max_terms=${maxTerms}`
  );
  const data = await response.json();
  return data.primes;
}

// Usage
checkPrime(97).then(isPrime => console.log(`97 is prime: ${isPrime}`));
```

### cURL Scripts

```bash
#!/bin/bash
# Check multiple numbers for primality
numbers=(2 3 4 5 97 100 982451653)

for num in "${numbers[@]}"; do
  result=$(curl -s "http://localhost:8000/prime/$num" | jq -r '.is_prime')
  echo "$num is prime: $result"
done
```

---

## Interactive Documentation

The API provides interactive documentation through:

- **Swagger UI**: Available at `/docs`
- **ReDoc**: Available at `/redoc`
- **OpenAPI Spec**: Available at `/openapi.json`

These interfaces allow you to:
- Test endpoints directly in the browser
- View detailed parameter specifications
- See example requests and responses
- Download the OpenAPI specification

---

## Best Practices

1. **Input Validation**: Always validate inputs on the client side
2. **Error Handling**: Implement robust error handling for network and API errors
3. **Caching**: Cache results for expensive operations
4. **Monitoring**: Monitor API response times and success rates
5. **Graceful Degradation**: Handle API unavailability gracefully
6. **Resource Management**: Be mindful of computational complexity for large inputs

---

## Support and Troubleshooting

For issues or questions:
1. Check the [API documentation](/docs)
2. Review this usage guide
3. Check server logs for error details
4. Visit the project repository for updates

Common troubleshooting steps:
1. Verify the service is running (`GET /health`)
2. Check input parameter ranges and types
3. Monitor response times for performance issues
4. Implement retry logic for transient failures