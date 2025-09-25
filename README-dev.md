# Prime Math API - Development Setup

A high-performance FastAPI service providing number theory operations including primality testing, integer factorization, and arithmetic progression analysis.

## Quick Start

### Prerequisites
- Python 3.11 or higher
- Git
- Docker (optional, for containerized development)

### Development Setup

1. **Clone and setup the project:**
   ```bash
   git clone <repository-url>
   cd Prime-3
   make setup  # Install dependencies and setup pre-commit hooks
   ```

2. **Start development server:**
   ```bash
   make dev    # Start with hot reload
   ```

3. **Access the API:**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## Development Commands

### Essential Commands
```bash
make help          # Show all available commands
make setup         # First-time setup (install deps + hooks)
make dev           # Start development server with hot reload
make test          # Run test suite
make check-all     # Run all code quality checks
```

### Code Quality
```bash
make lint          # Run ruff linting
make format        # Format code with ruff and black
make type-check    # Run mypy type checking
make pre-commit    # Run all pre-commit hooks
```

### Testing
```bash
make test          # Run tests with pytest
make test-cov      # Run tests with coverage report
make test-fast     # Run tests without coverage (faster)
```

### Docker Development
```bash
# Production-like container
make docker-build  # Build Docker image
make docker-run    # Run container

# Development container with hot reload
docker-compose --profile dev up api-dev
```

## Project Structure

```
Prime-3/
├── app/                    # FastAPI application
│   ├── __init__.py
│   └── main.py            # Main application entry point
├── tests/                 # Test files (created automatically)
├── .github/workflows/     # CI/CD pipeline
├── .pre-commit-config.yaml # Pre-commit hooks
├── pyproject.toml         # Project configuration
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── Makefile              # Development commands
├── Dockerfile            # Production container
├── Dockerfile.dev        # Development container
└── docker-compose.yml    # Docker compose configuration
```

## Development Workflow

### Setting up Development Environment

1. **Install Python 3.11+** (if not already installed)
2. **Clone the repository and navigate to project directory**
3. **Run first-time setup:**
   ```bash
   make setup
   ```
   This will:
   - Install all development dependencies
   - Set up pre-commit hooks
   - Prepare the development environment

### Daily Development

1. **Start development server:**
   ```bash
   make dev
   ```

2. **Run tests while developing:**
   ```bash
   make test-fast  # Quick feedback
   make test-cov   # Full coverage report
   ```

3. **Code quality checks:**
   ```bash
   make lint       # Fix linting issues
   make format     # Format code
   make type-check # Check types
   ```

4. **Before committing:**
   ```bash
   make check-all  # Run all quality checks
   ```

### Pre-commit Hooks

Pre-commit hooks automatically run on every commit to ensure code quality:
- **Ruff**: Fast Python linting and formatting
- **Black**: Code formatting (backup to ruff)
- **MyPy**: Static type checking
- **Bandit**: Security linting
- **Standard checks**: trailing whitespace, file endings, etc.

## Configuration

### Tool Configuration

All tools are configured in `pyproject.toml`:
- **Ruff**: Linting and formatting rules
- **Black**: Code style preferences
- **MyPy**: Type checking configuration
- **Pytest**: Test runner settings
- **Coverage**: Code coverage reporting

### Environment Variables

Development environment variables:
- `PYTHONPATH=/app` (set automatically)
- `PORT=8000` (default API port)
- `ENVIRONMENT=development` (in dev containers)

## API Documentation

Once the server is running, visit:
- **Interactive API docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative docs**: http://localhost:8000/redoc (ReDoc)
- **OpenAPI spec**: http://localhost:8000/openapi.json

## Testing

### Running Tests
```bash
# Quick test run
make test-fast

# Full test with coverage
make test-cov

# Specific test file
pytest tests/test_main.py -v

# With coverage details
pytest --cov=app --cov-report=html
```

### Test Structure
- Tests are automatically created in the `tests/` directory
- Basic API tests are included by default
- Coverage reports available in `htmlcov/index.html`

## Docker Development

### Production Container
```bash
# Build and run production container
make docker-build
make docker-run
```

### Development Container
```bash
# Run development container with hot reload
docker-compose --profile dev up api-dev

# Build development container
docker build -f Dockerfile.dev -t prime-math-api:dev .
```

## CI/CD Pipeline

GitHub Actions automatically:
- Run code quality checks (ruff, black, mypy)
- Execute test suite on Python 3.11 and 3.12
- Build and test Docker images
- Generate coverage reports
- Run security scans
- Perform basic performance tests

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure `PYTHONPATH` is set correctly
2. **Pre-commit hook failures**: Run `make check-all` to see specific issues
3. **Docker build failures**: Check `.dockerignore` excludes unnecessary files
4. **Port conflicts**: Change port in `make dev` or use `PORT=9000 make dev`

### Development Commands Reference

| Command | Description |
|---------|-------------|
| `make setup` | First-time development setup |
| `make dev` | Start development server |
| `make test` | Run test suite |
| `make lint` | Run code linting |
| `make format` | Format code |
| `make check-all` | Run all quality checks |
| `make clean` | Clean temporary files |
| `make docker-build` | Build Docker image |

## Getting Help

- Run `make help` for all available commands
- Check GitHub Actions logs for CI failures
- Review tool configurations in `pyproject.toml`
- Consult individual tool documentation for advanced usage

## Next Steps

After setup, you can:
1. Start implementing the core number theory algorithms
2. Add comprehensive test coverage
3. Implement the FastAPI endpoints
4. Set up monitoring and logging
5. Configure production deployment