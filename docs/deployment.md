# Prime Math API - Deployment Guide

## Overview

This guide covers production deployment of the Prime Math API, including Docker configurations, environment setup, monitoring, and security considerations.

## Quick Start

### Docker Deployment (Recommended)

```bash
# Build production image
docker build -t prime-math-api:latest .

# Run with default settings
docker run -d \
  --name prime-math-api \
  -p 8000:8000 \
  --restart unless-stopped \
  prime-math-api:latest

# Verify deployment
curl http://localhost:8000/health
```

### Docker Compose (Production)

```bash
# Start production services
docker-compose up -d api

# Check status
docker-compose ps
docker-compose logs api
```

---

## Environment Configuration

### Required Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `PORT` | HTTP server port | `8000` | `8000` |
| `PYTHONPATH` | Python module path | `/app` | `/app` |

### Optional Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `ENVIRONMENT` | Deployment environment | `production` | `development`, `staging`, `production` |
| `LOG_LEVEL` | Logging level | `info` | `debug`, `info`, `warning`, `error` |
| `WORKERS` | Number of worker processes | `1` | `4` (CPU cores) |
| `MAX_REQUESTS` | Max requests per worker | `1000` | `2000` |
| `TIMEOUT` | Worker timeout (seconds) | `30` | `60` |

### Environment File Example

Create `.env` file for production:

```bash
# Production Configuration
ENVIRONMENT=production
PORT=8000
LOG_LEVEL=info
WORKERS=4
MAX_REQUESTS=2000
TIMEOUT=60

# Security
PYTHONHASHSEED=random
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
```

---

## Docker Configuration

### Production Dockerfile Features

The production Dockerfile (`Dockerfile`) includes:

- **Multi-stage build** for optimized image size
- **Non-root user** for enhanced security
- **Health checks** for container orchestration
- **Minimal base image** (Python 3.11 slim)
- **Security labels** and metadata
- **Optimized layer caching**

### Build Arguments

Customize the build with build arguments:

```bash
docker build \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  --build-arg VERSION=0.1.0 \
  --build-arg VCS_REF=$(git rev-parse --short HEAD) \
  -t prime-math-api:0.1.0 \
  .
```

### Development vs Production

| Feature | Development | Production |
|---------|-------------|------------|
| Base Image | `python:3.11-slim` | Multi-stage build |
| User | `appuser` | `appuser` (non-root) |
| Hot Reload | ✅ Enabled | ❌ Disabled |
| Debug Tools | ✅ Included | ❌ Excluded |
| Security Scan | ❌ Optional | ✅ Recommended |
| Health Check | ❌ Optional | ✅ Required |

---

## Container Orchestration

### Docker Compose Production Setup

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        BUILD_DATE: ${BUILD_DATE:-now}
        VERSION: ${VERSION:-0.1.0}
        VCS_REF: ${VCS_REF:-local}
    image: prime-math-api:${VERSION:-latest}
    container_name: prime-math-api
    ports:
      - "${HOST_PORT:-8000}:8000"
    environment:
      - PYTHONPATH=/app
      - PORT=8000
      - ENVIRONMENT=production
      - WORKERS=${WORKERS:-4}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health', timeout=10)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    # Resource limits (uncomment for production)
    # deploy:
    #   resources:
    #     limits:
    #       cpus: '2.0'
    #       memory: 1G
    #     reservations:
    #       cpus: '0.5'
    #       memory: 256M
    networks:
      - prime-api-network
    # Logging configuration
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  prime-api-network:
    driver: bridge
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prime-math-api
  labels:
    app: prime-math-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: prime-math-api
  template:
    metadata:
      labels:
        app: prime-math-api
    spec:
      containers:
      - name: api
        image: prime-math-api:0.1.0
        ports:
        - containerPort: 8000
        env:
        - name: PORT
          value: "8000"
        - name: WORKERS
          value: "1"  # Single worker per pod
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: false  # FastAPI needs write access
          runAsNonRoot: true
          runAsUser: 1000

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: prime-math-api-service
spec:
  selector:
    app: prime-math-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP
```

---

## Load Balancer Configuration

### Nginx Configuration

```nginx
upstream prime_api {
    server 127.0.0.1:8000;
    # Add more backend servers as needed
    # server 127.0.0.1:8001;
    # server 127.0.0.1:8002;

    # Load balancing method
    least_conn;

    # Health check
    keepalive 32;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Configuration
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # API routes
    location / {
        proxy_pass http://prime_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # Health check endpoint (bypass proxy cache)
    location /health {
        proxy_pass http://prime_api;
        proxy_cache off;
        access_log off;
    }

    # Rate limiting
    location /prime {
        limit_req zone=api_rate_limit burst=20 nodelay;
        proxy_pass http://prime_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Access logs
    access_log /var/log/nginx/prime-api-access.log;
    error_log /var/log/nginx/prime-api-error.log;
}

# Rate limiting configuration
http {
    limit_req_zone $binary_remote_addr zone=api_rate_limit:10m rate=10r/s;
}
```

### Traefik Configuration (Docker)

```yaml
# docker-compose.yml with Traefik
version: '3.8'

services:
  traefik:
    image: traefik:v2.9
    command:
      - --api.dashboard=true
      - --providers.docker=true
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
      - --certificatesresolvers.letsencrypt.acme.email=your-email@domain.com
      - --certificatesresolvers.letsencrypt.acme.storage=/acme.json
      - --certificatesresolvers.letsencrypt.acme.tlschallenge=true
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./acme.json:/acme.json
    labels:
      - traefik.enable=true

  api:
    build: .
    labels:
      - traefik.enable=true
      - traefik.http.routers.prime-api.rule=Host(`api.yourdomain.com`)
      - traefik.http.routers.prime-api.entrypoints=websecure
      - traefik.http.routers.prime-api.tls.certresolver=letsencrypt
      - traefik.http.services.prime-api.loadbalancer.server.port=8000
    networks:
      - traefik-network

networks:
  traefik-network:
    external: true
```

---

## Performance Optimization

### Worker Configuration

For production deployment, configure multiple workers:

```bash
# Docker run with multiple workers
docker run -d \
  --name prime-math-api \
  -p 8000:8000 \
  -e WORKERS=4 \
  -e MAX_REQUESTS=2000 \
  -e TIMEOUT=60 \
  --restart unless-stopped \
  prime-math-api:latest
```

### Resource Limits

Set appropriate resource limits:

```yaml
# docker-compose.yml
services:
  api:
    # ... other config ...
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 256M
```

### Performance Tuning Guidelines

| Deployment Size | CPU Cores | Memory | Workers | Max Requests |
|----------------|-----------|---------|---------|--------------|
| Small | 1-2 | 512MB | 2 | 1000 |
| Medium | 2-4 | 1-2GB | 4 | 2000 |
| Large | 4-8 | 2-4GB | 8 | 3000 |
| Enterprise | 8+ | 4GB+ | 16+ | 5000 |

---

## Monitoring and Observability

### Health Checks

The API provides health check endpoints:

```bash
# Basic health check
curl http://localhost:8000/health

# Response
{
  "status": "healthy",
  "service": "Prime Math API",
  "version": "0.1.0"
}
```

### Logging Configuration

Configure structured logging in production:

```python
# Custom logging configuration (optional)
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
```

### Monitoring with Prometheus (Optional)

Add Prometheus metrics endpoint:

```bash
# Install prometheus client
pip install prometheus-client

# Add to requirements.txt
echo "prometheus-client>=0.15.0" >> requirements.txt
```

### Application Monitoring

Monitor these key metrics:

1. **Response Times**: Track API response latency
2. **Error Rates**: Monitor 4xx and 5xx error rates
3. **Request Volume**: Track requests per second
4. **Resource Usage**: Monitor CPU and memory usage
5. **Health Status**: Continuous health check monitoring

---

## Security Considerations

### Container Security

1. **Non-root user**: Container runs as `appuser` (UID 1000)
2. **Minimal base image**: Uses Python 3.11 slim
3. **No privileged access**: Container runs without elevated privileges
4. **Read-only filesystems**: Where possible
5. **Security scanning**: Regular image vulnerability scans

### Network Security

1. **TLS encryption**: Use HTTPS in production
2. **Firewall rules**: Restrict access to necessary ports only
3. **VPC/subnet isolation**: Deploy in isolated networks
4. **Rate limiting**: Implement request rate limiting
5. **DDoS protection**: Use CDN or DDoS protection services

### Application Security

1. **Input validation**: Comprehensive input validation
2. **Error handling**: Don't expose internal details in errors
3. **Request size limits**: Limit request payload sizes
4. **Timeout protection**: Set reasonable operation timeouts
5. **Security headers**: Implement security-focused HTTP headers

### Security Scanning

```bash
# Docker security scanning with Trivy
trivy image prime-math-api:latest

# OWASP dependency checking
pip install safety
safety check -r requirements.txt

# Static analysis
pip install bandit
bandit -r app/
```

---

## Backup and Recovery

### Data Considerations

The Prime Math API is stateless and doesn't require data backups. However:

1. **Configuration backups**: Backup environment configs and secrets
2. **Image registry**: Maintain versioned container images
3. **Infrastructure as Code**: Version control deployment configurations

### Disaster Recovery Plan

1. **Multi-region deployment**: Deploy across multiple availability zones
2. **Image redundancy**: Store images in multiple registries
3. **Automated failover**: Configure automatic failover mechanisms
4. **Recovery procedures**: Document recovery procedures

---

## Scaling Strategies

### Horizontal Scaling

1. **Load balancer**: Use load balancer for multiple instances
2. **Container orchestration**: Use Kubernetes or Docker Swarm
3. **Auto-scaling**: Configure automatic scaling based on metrics
4. **Session affinity**: Not required (stateless API)

### Vertical Scaling

1. **Resource limits**: Increase CPU and memory allocation
2. **Worker processes**: Increase worker count
3. **Connection pooling**: Optimize connection handling

### Caching Strategies

1. **CDN caching**: Cache responses at CDN level
2. **Application caching**: Implement result caching for expensive operations
3. **Database caching**: Not applicable (computational API)

---

## Production Deployment Checklist

### Pre-deployment

- [ ] Security review completed
- [ ] Performance testing completed
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Monitoring configured
- [ ] Backup procedures documented
- [ ] SSL certificates configured
- [ ] Domain DNS configured

### Deployment

- [ ] Production environment variables set
- [ ] Container image built and tested
- [ ] Health checks responding
- [ ] Load balancer configured
- [ ] Firewall rules configured
- [ ] Monitoring alerts configured
- [ ] Log aggregation configured

### Post-deployment

- [ ] Smoke tests passed
- [ ] Performance monitoring active
- [ ] Error tracking configured
- [ ] Security scanning scheduled
- [ ] Maintenance procedures documented
- [ ] Incident response plan ready
- [ ] Team access configured
- [ ] Documentation deployed

---

## Troubleshooting

### Common Issues

1. **Container won't start**:
   - Check environment variables
   - Verify image build
   - Review container logs

2. **High response times**:
   - Check CPU/memory usage
   - Review worker configuration
   - Analyze request patterns

3. **Health checks failing**:
   - Verify application startup
   - Check network connectivity
   - Review timeout settings

4. **Memory issues**:
   - Check for memory leaks
   - Review worker recycling
   - Increase memory limits

### Debugging Commands

```bash
# Check container status
docker ps -a
docker logs prime-math-api

# Container resource usage
docker stats prime-math-api

# Execute commands in container
docker exec -it prime-math-api /bin/bash

# Test API endpoints
curl -v http://localhost:8000/health
curl -X GET "http://localhost:8000/prime/97"
```

### Support Resources

1. Application logs and metrics
2. Container orchestration logs
3. Load balancer metrics
4. Network monitoring tools
5. Performance profiling tools

---

## Updates and Maintenance

### Rolling Updates

```bash
# Build new version
docker build -t prime-math-api:0.1.1 .

# Update with zero downtime
docker service update --image prime-math-api:0.1.1 prime-api-service

# Or with docker-compose
docker-compose pull
docker-compose up -d
```

### Maintenance Windows

1. Schedule regular maintenance windows
2. Plan for dependency updates
3. Security patch management
4. Performance optimization reviews

### Version Management

1. Semantic versioning for releases
2. Tagged container images
3. Rollback procedures documented
4. Change log maintenance