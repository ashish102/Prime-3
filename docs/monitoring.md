# Prime Math API - Monitoring and Observability Guide

## Overview

Comprehensive monitoring and observability strategy for the Prime Math API to ensure high availability, performance, and operational excellence in production environments.

## Monitoring Philosophy

### The Three Pillars of Observability

1. **Metrics**: Quantitative measurements over time
2. **Logs**: Discrete events with context
3. **Traces**: Request flows through distributed systems

### Prime Math API Specific Considerations

- **Computational Complexity**: Variable response times based on input size
- **Resource Utilization**: CPU-intensive mathematical operations
- **Algorithm Performance**: Different algorithms for different input ranges
- **User Behavior**: Detecting abuse and optimizing for legitimate usage

## Key Performance Indicators (KPIs)

### Service Level Indicators (SLIs)

#### Availability Metrics
```yaml
availability:
  target: 99.9%
  measurement: "Percentage of successful health check responses"
  threshold: "< 99.9% triggers alert"

uptime:
  target: 99.95%
  measurement: "Service uptime over 30-day period"
  threshold: "< 99.9% triggers incident review"
```

#### Performance Metrics
```yaml
response_time:
  target: "95% of requests < 100ms"
  measurement: "Response time percentiles"
  endpoints:
    health: "95% < 10ms, 99% < 50ms"
    prime: "95% < 100ms, 99% < 500ms"
    factor: "95% < 500ms, 99% < 5000ms"
    progression: "95% < 200ms, 99% < 1000ms"

throughput:
  target: "1000 requests per minute"
  measurement: "Requests processed per unit time"
  threshold: "< 500 rpm indicates capacity issues"
```

#### Error Rate Metrics
```yaml
error_rate:
  target: "< 0.1% (4xx + 5xx errors)"
  measurement: "Error rate over 5-minute windows"
  breakdown:
    4xx_errors: "< 1% (client errors)"
    5xx_errors: "< 0.01% (server errors)"
    timeout_errors: "< 0.05%"
```

#### Resource Utilization
```yaml
cpu_utilization:
  target: "< 70% average, < 90% peak"
  measurement: "CPU usage across all containers"

memory_utilization:
  target: "< 80% average, < 95% peak"
  measurement: "Memory usage including cache"

disk_io:
  target: "< 80% disk utilization"
  measurement: "Read/write operations per second"
```

## Metrics Collection

### Application Metrics

#### FastAPI Metrics Implementation

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import FastAPI, Request, Response
import time
import asyncio
from typing import Callable

# Metrics definitions
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, float('inf'))
)

ACTIVE_REQUESTS = Gauge(
    'http_active_requests',
    'Number of active HTTP requests'
)

PRIME_CHECKS = Counter(
    'prime_checks_total',
    'Total prime number checks',
    ['result', 'input_range']
)

FACTORIZATION_DURATION = Histogram(
    'factorization_duration_seconds',
    'Time spent on factorization',
    ['input_range', 'complexity'],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, float('inf'))
)

SYSTEM_RESOURCES = Gauge(
    'system_resource_usage',
    'System resource usage',
    ['resource_type']
)

class MetricsMiddleware:
    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope, receive)

        # Skip metrics for metrics endpoint
        if request.url.path == "/metrics":
            return await self.app(scope, receive, send)

        method = request.method
        path = request.url.path

        # Normalize path for metrics (remove dynamic parts)
        normalized_path = self.normalize_path(path)

        ACTIVE_REQUESTS.inc()
        start_time = time.time()

        try:
            # Call the application
            status_code = 500  # Default for exceptions

            async def send_wrapper(message):
                nonlocal status_code
                if message["type"] == "http.response.start":
                    status_code = message["status"]
                await send(message)

            await self.app(scope, receive, send_wrapper)

        finally:
            # Record metrics
            duration = time.time() - start_time

            REQUEST_COUNT.labels(
                method=method,
                endpoint=normalized_path,
                status_code=status_code
            ).inc()

            REQUEST_DURATION.labels(
                method=method,
                endpoint=normalized_path
            ).observe(duration)

            ACTIVE_REQUESTS.dec()

    def normalize_path(self, path: str) -> str:
        """Normalize paths for metrics to avoid high cardinality."""
        if path.startswith('/prime/'):
            return '/prime/{n}'
        elif path.startswith('/factor/'):
            return '/factor/{n}'
        elif path.startswith('/progression/'):
            return '/progression/{start}/{diff}'
        return path

# Add middleware
app.add_middleware(MetricsMiddleware)

# Metrics endpoint
@app.get("/metrics", include_in_schema=False)
async def get_metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type="text/plain")
```

#### Business Logic Metrics

```python
from functools import wraps
import math

def track_prime_check(func):
    """Decorator to track prime checking metrics."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        n = kwargs.get('n') or args[1] if len(args) > 1 else 0

        start_time = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start_time

        # Determine input range
        input_range = get_input_range(n)

        # Track the check
        PRIME_CHECKS.labels(
            result='prime' if result.is_prime else 'composite',
            input_range=input_range
        ).inc()

        # Track duration by complexity
        REQUEST_DURATION.labels(
            method='GET',
            endpoint='/prime/{n}'
        ).observe(duration)

        return result
    return wrapper

def track_factorization(func):
    """Decorator to track factorization metrics."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        n = kwargs.get('n') or args[1] if len(args) > 1 else 0

        start_time = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start_time

        # Determine complexity
        complexity = estimate_factorization_complexity(n, result.factors)
        input_range = get_input_range(n)

        FACTORIZATION_DURATION.labels(
            input_range=input_range,
            complexity=complexity
        ).observe(duration)

        return result
    return wrapper

def get_input_range(n: int) -> str:
    """Categorize input by size for metrics."""
    if n < 1000:
        return 'small'
    elif n < 10**6:
        return 'medium'
    elif n < 10**12:
        return 'large'
    else:
        return 'very_large'

def estimate_factorization_complexity(n: int, factors: list) -> str:
    """Estimate factorization complexity."""
    if len(factors) <= 2:
        return 'simple'
    elif len(factors) <= 5:
        return 'moderate'
    else:
        return 'complex'
```

#### System Metrics Collection

```python
import psutil
import asyncio

class SystemMetricsCollector:
    def __init__(self, interval: int = 30):
        self.interval = interval
        self.running = False

    async def start_collection(self):
        """Start collecting system metrics."""
        self.running = True
        while self.running:
            try:
                # CPU metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                SYSTEM_RESOURCES.labels(resource_type='cpu_percent').set(cpu_percent)

                # Memory metrics
                memory = psutil.virtual_memory()
                SYSTEM_RESOURCES.labels(resource_type='memory_percent').set(memory.percent)
                SYSTEM_RESOURCES.labels(resource_type='memory_available_mb').set(memory.available / 1024 / 1024)

                # Disk metrics
                disk = psutil.disk_usage('/')
                disk_percent = disk.used / disk.total * 100
                SYSTEM_RESOURCES.labels(resource_type='disk_percent').set(disk_percent)

                # Network metrics
                network = psutil.net_io_counters()
                SYSTEM_RESOURCES.labels(resource_type='network_bytes_sent').set(network.bytes_sent)
                SYSTEM_RESOURCES.labels(resource_type='network_bytes_recv').set(network.bytes_recv)

                await asyncio.sleep(self.interval)

            except Exception as e:
                print(f"Error collecting system metrics: {e}")
                await asyncio.sleep(self.interval)

    def stop_collection(self):
        """Stop collecting system metrics."""
        self.running = False

# Start system metrics collection
metrics_collector = SystemMetricsCollector()

@app.on_event("startup")
async def start_metrics_collection():
    asyncio.create_task(metrics_collector.start_collection())

@app.on_event("shutdown")
async def stop_metrics_collection():
    metrics_collector.stop_collection()
```

### Infrastructure Metrics

#### Docker Container Metrics

```yaml
# docker-compose.yml with monitoring
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    labels:
      - "prometheus.scrape=true"
      - "prometheus.port=8000"
      - "prometheus.path=/metrics"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Prometheus for metrics collection
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  # Grafana for dashboards
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning

volumes:
  prometheus_data:
  grafana_data:
```

#### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  # Prime Math API
  - job_name: 'prime-math-api'
    static_configs:
      - targets: ['api:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s

  # Node exporter for system metrics
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  # Docker container metrics
  - job_name: 'docker'
    static_configs:
      - targets: ['docker-host:9323']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

## Logging Strategy

### Structured Logging Implementation

```python
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict
from contextvars import ContextVar

# Context variables for request tracking
request_id_var: ContextVar[str] = ContextVar('request_id', default='')
user_id_var: ContextVar[str] = ContextVar('user_id', default='')

class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter for logs."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add request context
        request_id = request_id_var.get('')
        if request_id:
            log_entry['request_id'] = request_id

        user_id = user_id_var.get('')
        if user_id:
            log_entry['user_id'] = user_id

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)

        return json.dumps(log_entry)

# Configure logging
def setup_logging():
    """Setup structured logging."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove default handlers
    logger.handlers.clear()

    # Add structured handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    logger.addHandler(handler)

# Request logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    # Generate request ID
    request_id = f"{int(time.time() * 1000000)}"
    request_id_var.set(request_id)

    # Extract user info (if available)
    api_key = request.headers.get("X-API-Key", "anonymous")
    user_id_var.set(api_key)

    start_time = time.time()

    # Log request start
    logging.info("Request started", extra={
        'extra_fields': {
            'event': 'request_start',
            'method': request.method,
            'url': str(request.url),
            'user_agent': request.headers.get('user-agent'),
            'client_ip': request.client.host,
        }
    })

    try:
        response = await call_next(request)
        duration = time.time() - start_time

        # Log successful response
        logging.info("Request completed", extra={
            'extra_fields': {
                'event': 'request_complete',
                'status_code': response.status_code,
                'duration_ms': round(duration * 1000, 2),
            }
        })

        return response

    except Exception as e:
        duration = time.time() - start_time

        # Log error
        logging.error("Request failed", extra={
            'extra_fields': {
                'event': 'request_error',
                'error_type': type(e).__name__,
                'error_message': str(e),
                'duration_ms': round(duration * 1000, 2),
            }
        }, exc_info=True)

        raise

setup_logging()
```

### Business Logic Logging

```python
import logging

def log_prime_check(n: int, result: bool, duration: float, algorithm: str):
    """Log prime checking operations."""
    logging.info("Prime check completed", extra={
        'extra_fields': {
            'event': 'prime_check',
            'input_number': n,
            'is_prime': result,
            'duration_ms': round(duration * 1000, 4),
            'algorithm': algorithm,
            'input_size_category': get_input_range(n),
        }
    })

def log_factorization(n: int, factors: list, duration: float):
    """Log factorization operations."""
    logging.info("Factorization completed", extra={
        'extra_fields': {
            'event': 'factorization',
            'input_number': n,
            'factor_count': len(factors),
            'factors': factors[:10],  # Log first 10 factors only
            'duration_ms': round(duration * 1000, 4),
            'complexity': estimate_factorization_complexity(n, factors),
        }
    })

def log_rate_limit_violation(client_id: str, endpoint: str, limit: int):
    """Log rate limiting violations."""
    logging.warning("Rate limit exceeded", extra={
        'extra_fields': {
            'event': 'rate_limit_exceeded',
            'client_id': client_id,
            'endpoint': endpoint,
            'rate_limit': limit,
            'action': 'request_blocked',
        }
    })

def log_security_event(event_type: str, details: dict):
    """Log security-related events."""
    logging.warning("Security event detected", extra={
        'extra_fields': {
            'event': 'security_event',
            'type': event_type,
            'details': details,
            'severity': 'high' if event_type in ['abuse_detected', 'attack_pattern'] else 'medium',
        }
    })
```

### Log Aggregation with ELK Stack

```yaml
# docker-compose.yml with ELK stack
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:8.5.0
    ports:
      - "5044:5044"
    volumes:
      - ./monitoring/logstash.conf:/usr/share/logstash/pipeline/logstash.conf

  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:
```

## Distributed Tracing

### OpenTelemetry Implementation

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

def setup_tracing():
    """Setup distributed tracing with Jaeger."""
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(__name__)

    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=6831,
    )

    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    # Auto-instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)
    RequestsInstrumentor().instrument()

# Custom tracing for business logic
@app.get("/prime/{n}")
async def check_prime_traced(n: int):
    tracer = trace.get_tracer(__name__)

    with tracer.start_as_current_span("prime_check") as span:
        span.set_attribute("input.number", n)
        span.set_attribute("input.size_category", get_input_range(n))

        start_time = time.time()

        with tracer.start_as_current_span("algorithm.miller_rabin"):
            result = is_prime_64(n)

        duration = time.time() - start_time

        span.set_attribute("result.is_prime", result)
        span.set_attribute("performance.duration_ms", duration * 1000)

        return PrimeResponse(number=n, is_prime=result)

setup_tracing()
```

## Alerting Rules

### Prometheus Alert Rules

```yaml
# monitoring/alert_rules.yml
groups:
- name: prime_math_api_alerts
  rules:
  # Availability alerts
  - alert: APIDown
    expr: up{job="prime-math-api"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Prime Math API is down"
      description: "The Prime Math API has been down for more than 1 minute."

  - alert: HighErrorRate
    expr: rate(http_requests_total{status_code=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.01
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value | humanizePercentage }} over the last 5 minutes."

  # Performance alerts
  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time"
      description: "95th percentile response time is {{ $value }}s."

  - alert: HighCPUUsage
    expr: system_resource_usage{resource_type="cpu_percent"} > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage"
      description: "CPU usage is {{ $value }}%."

  - alert: HighMemoryUsage
    expr: system_resource_usage{resource_type="memory_percent"} > 90
    for: 3m
    labels:
      severity: critical
    annotations:
      summary: "High memory usage"
      description: "Memory usage is {{ $value }}%."

  # Business logic alerts
  - alert: UnusuallyLongFactorization
    expr: histogram_quantile(0.95, rate(factorization_duration_seconds_bucket[10m])) > 30
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Unusually long factorization times"
      description: "95th percentile factorization time is {{ $value }}s."

  - alert: HighRateLimitHitRate
    expr: rate(rate_limit_blocks_total[5m]) > 10
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High rate limit hit rate"
      description: "Rate limit is being hit {{ $value }} times per second."
```

### Alert Manager Configuration

```yaml
# monitoring/alertmanager.yml
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@yourdomain.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  routes:
  - match:
      severity: critical
    receiver: 'critical-alerts'
  - match:
      severity: warning
    receiver: 'warning-alerts'

receivers:
- name: 'web.hook'
  webhook_configs:
  - url: 'http://127.0.0.1:5001/'

- name: 'critical-alerts'
  email_configs:
  - to: 'oncall@yourdomain.com'
    subject: 'CRITICAL: {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      Description: {{ .Annotations.description }}
      {{ end }}

  slack_configs:
  - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    channel: '#alerts-critical'
    title: 'CRITICAL Alert'
    text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'

- name: 'warning-alerts'
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    channel: '#alerts-warning'
    title: 'Warning Alert'
    text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

## Dashboards

### Grafana Dashboard Configuration

```json
{
  "dashboard": {
    "title": "Prime Math API Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time Percentiles",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          },
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "99th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status_code=~\"4..\"}[5m])",
            "legendFormat": "4xx errors"
          },
          {
            "expr": "rate(http_requests_total{status_code=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          }
        ]
      },
      {
        "title": "System Resources",
        "type": "graph",
        "targets": [
          {
            "expr": "system_resource_usage{resource_type=\"cpu_percent\"}",
            "legendFormat": "CPU %"
          },
          {
            "expr": "system_resource_usage{resource_type=\"memory_percent\"}",
            "legendFormat": "Memory %"
          }
        ]
      },
      {
        "title": "Prime Check Distribution",
        "type": "piechart",
        "targets": [
          {
            "expr": "sum by (result) (prime_checks_total)",
            "legendFormat": "{{result}}"
          }
        ]
      },
      {
        "title": "Factorization Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(factorization_duration_seconds_bucket[10m]))",
            "legendFormat": "95th percentile duration"
          }
        ]
      }
    ]
  }
}
```

### Custom Dashboard for Business Metrics

```python
# Custom dashboard endpoint
@app.get("/dashboard/metrics", include_in_schema=False)
async def get_dashboard_metrics():
    """Custom metrics endpoint for dashboard."""

    # Collect current metrics
    metrics = {
        "current_time": datetime.utcnow().isoformat(),
        "service_info": {
            "version": "0.1.0",
            "uptime_seconds": time.time() - start_time,
            "active_requests": ACTIVE_REQUESTS._value.get(),
        },
        "request_stats": {
            "total_requests": sum(REQUEST_COUNT._metrics.values()),
            "requests_per_minute": calculate_rpm(),
            "average_response_time": calculate_average_response_time(),
        },
        "algorithm_stats": {
            "prime_checks": dict(PRIME_CHECKS._metrics),
            "factorizations": get_factorization_stats(),
        },
        "system_stats": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
        }
    }

    return metrics
```

## Health Checks

### Comprehensive Health Check Implementation

```python
from typing import Dict, Any
import asyncio

class HealthChecker:
    def __init__(self):
        self.checks = {
            "database": self.check_database,
            "external_services": self.check_external_services,
            "system_resources": self.check_system_resources,
            "algorithm_performance": self.check_algorithm_performance,
        }

    async def check_database(self) -> Dict[str, Any]:
        """Check database connectivity (if applicable)."""
        return {
            "status": "healthy",
            "details": "No database required"
        }

    async def check_external_services(self) -> Dict[str, Any]:
        """Check external service dependencies."""
        # Test any external dependencies
        return {
            "status": "healthy",
            "details": "No external dependencies"
        }

    async def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource availability."""
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        status = "healthy"
        details = []

        if cpu_percent > 90:
            status = "unhealthy"
            details.append(f"High CPU usage: {cpu_percent}%")

        if memory.percent > 95:
            status = "unhealthy"
            details.append(f"High memory usage: {memory.percent}%")

        if disk.percent > 95:
            status = "unhealthy"
            details.append(f"High disk usage: {disk.percent}%")

        return {
            "status": status,
            "details": details if details else "Resources within normal limits",
            "metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent
            }
        }

    async def check_algorithm_performance(self) -> Dict[str, Any]:
        """Check algorithm performance with test cases."""
        try:
            # Test prime checking
            start = time.time()
            result = is_prime_64(97)  # Known prime
            prime_duration = time.time() - start

            if not result or prime_duration > 0.1:  # Should be very fast
                return {
                    "status": "degraded",
                    "details": f"Prime check performance degraded: {prime_duration}s"
                }

            # Test factorization
            start = time.time()
            factors = factorize(60)  # Known factorization
            factor_duration = time.time() - start

            expected_factors = [2, 2, 3, 5]
            if factors != expected_factors or factor_duration > 0.1:
                return {
                    "status": "degraded",
                    "details": f"Factorization performance degraded: {factor_duration}s"
                }

            return {
                "status": "healthy",
                "details": "Algorithm performance normal",
                "metrics": {
                    "prime_check_duration": prime_duration,
                    "factorization_duration": factor_duration
                }
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "details": f"Algorithm test failed: {str(e)}"
            }

    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks."""
        results = {}
        overall_status = "healthy"

        for check_name, check_func in self.checks.items():
            try:
                result = await check_func()
                results[check_name] = result

                if result["status"] == "unhealthy":
                    overall_status = "unhealthy"
                elif result["status"] == "degraded" and overall_status != "unhealthy":
                    overall_status = "degraded"

            except Exception as e:
                results[check_name] = {
                    "status": "unhealthy",
                    "details": f"Health check failed: {str(e)}"
                }
                overall_status = "unhealthy"

        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": results
        }

health_checker = HealthChecker()

@app.get("/health/detailed")
async def detailed_health_check():
    """Comprehensive health check endpoint."""
    return await health_checker.run_all_checks()

@app.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe endpoint."""
    health_result = await health_checker.run_all_checks()

    if health_result["status"] in ["healthy", "degraded"]:
        return {"status": "ready"}
    else:
        raise HTTPException(status_code=503, detail="Service not ready")

@app.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe endpoint."""
    # Simple check - if we can respond, we're alive
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
```

## Monitoring Best Practices

### 1. Monitoring Strategy

1. **Start with the Four Golden Signals**:
   - Latency (response time)
   - Traffic (request rate)
   - Errors (error rate)
   - Saturation (resource utilization)

2. **Monitor User Experience**:
   - End-to-end response times
   - Success rates for different input ranges
   - API reliability from user perspective

3. **Monitor System Health**:
   - Resource utilization trends
   - Service dependencies
   - Infrastructure performance

### 2. Alert Strategy

1. **Alert on Symptoms, Not Causes**:
   - Alert on user-impacting issues
   - Use causes for investigation, not alerting

2. **Reduce Alert Fatigue**:
   - Set appropriate thresholds
   - Implement alert escalation
   - Regular alert review and tuning

3. **Actionable Alerts**:
   - Every alert should have a clear response
   - Include runbook links in alert descriptions
   - Provide context for troubleshooting

### 3. Dashboard Design

1. **Hierarchy of Information**:
   - High-level overview at the top
   - Detailed metrics below
   - Drill-down capabilities

2. **User-Centric Views**:
   - Show metrics that matter to users
   - Business impact over technical details
   - Clear visualization of health status

## Summary

This comprehensive monitoring and observability strategy provides:

1. **Full Visibility**: Metrics, logs, and traces cover all aspects of the system
2. **Proactive Monitoring**: Early detection of issues before they impact users
3. **Operational Excellence**: Clear dashboards, actionable alerts, and comprehensive health checks
4. **Performance Optimization**: Data-driven insights for continuous improvement
5. **Incident Response**: Rapid detection, investigation, and resolution capabilities

Regular review and refinement of monitoring based on operational experience will ensure the system remains reliable, performant, and maintainable in production environments.