"""Basic tests for FastAPI application."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns correct response."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["message"] == "Prime Math API"
    assert data["version"] == "0.1.0"


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_docs_endpoint():
    """Test OpenAPI docs are accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_redoc_endpoint():
    """Test ReDoc documentation is accessible."""
    response = client.get("/redoc")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_openapi_spec():
    """Test OpenAPI specification is available."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    assert "openapi" in spec
    assert spec["info"]["title"] == "Prime Math API"
    assert spec["info"]["version"] == "0.1.0"


def test_nonexistent_endpoint():
    """Test that non-existent endpoints return 404."""
    response = client.get("/nonexistent")
    assert response.status_code == 404


def test_sum_of_two_primes_valid_even():
    """Test sum of two primes for even number."""
    response = client.get("/sum-of-two-primes/10")
    assert response.status_code == 200
    data = response.json()
    assert data["number"] == 10
    assert data["is_sum_of_two_primes"] is True
    assert data["count"] == 2
    assert [3, 7] in data["pairs"]
    assert [5, 5] in data["pairs"]


def test_sum_of_two_primes_valid_small():
    """Test sum of two primes for smallest valid number."""
    response = client.get("/sum-of-two-primes/4")
    assert response.status_code == 200
    data = response.json()
    assert data["number"] == 4
    assert data["is_sum_of_two_primes"] is True
    assert data["count"] == 1
    assert data["pairs"] == [[2, 2]]


def test_sum_of_two_primes_odd():
    """Test sum of two primes for odd number."""
    response = client.get("/sum-of-two-primes/5")
    assert response.status_code == 200
    data = response.json()
    assert data["number"] == 5
    assert data["is_sum_of_two_primes"] is True
    assert data["count"] == 1
    assert data["pairs"] == [[2, 3]]


def test_sum_of_two_primes_invalid():
    """Test sum of two primes for number that cannot be expressed as sum of two primes."""
    response = client.get("/sum-of-two-primes/11")
    assert response.status_code == 200
    data = response.json()
    assert data["number"] == 11
    assert data["is_sum_of_two_primes"] is False
    assert data["count"] == 0
    assert data["pairs"] == []


def test_sum_of_two_primes_small_invalid():
    """Test sum of two primes for numbers less than 4."""
    for n in [0, 1, 2, 3]:
        response = client.get(f"/sum-of-two-primes/{n}")
        assert response.status_code == 200
        data = response.json()
        assert data["number"] == n
        assert data["is_sum_of_two_primes"] is False
        assert data["count"] == 0
        assert data["pairs"] == []


def test_sum_of_two_primes_large():
    """Test sum of two primes for larger number."""
    response = client.get("/sum-of-two-primes/100")
    assert response.status_code == 200
    data = response.json()
    assert data["number"] == 100
    assert data["is_sum_of_two_primes"] is True
    assert data["count"] > 0
    # Verify some expected pairs
    assert [3, 97] in data["pairs"]
    assert [47, 53] in data["pairs"]


def test_sum_of_two_primes_negative():
    """Test sum of two primes with negative number returns 422."""
    response = client.get("/sum-of-two-primes/-5")
    assert response.status_code == 422  # Validation error from FastAPI