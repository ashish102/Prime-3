# Makefile for Prime Math API
# Provides common development tasks for efficient workflow

# Variables
PYTHON := python3.11
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
RUFF := $(PYTHON) -m ruff
BLACK := $(PYTHON) -m black
MYPY := $(PYTHON) -m mypy
PRECOMMIT := $(PYTHON) -m pre_commit
UVICORN := $(PYTHON) -m uvicorn

# Directories
SRC_DIR := app
TEST_DIR := tests
VENV_DIR := .venv

# Colors for output
BOLD := \033[1m
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
RESET := \033[0m

.PHONY: help install install-dev clean lint format type-check test test-cov run dev build docker-build docker-run pre-commit setup-hooks check-all

# Default target
help: ## Show this help message
	@echo "$(BOLD)Prime Math API - Development Commands$(RESET)"
	@echo ""
	@echo "$(BOLD)Setup:$(RESET)"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  setup-hooks  Install pre-commit hooks"
	@echo ""
	@echo "$(BOLD)Code Quality:$(RESET)"
	@echo "  lint         Run linting with ruff"
	@echo "  format       Format code with ruff and black"
	@echo "  type-check   Run static type checking with mypy"
	@echo "  pre-commit   Run pre-commit hooks on all files"
	@echo "  check-all    Run all quality checks (lint, format, type-check)"
	@echo ""
	@echo "$(BOLD)Testing:$(RESET)"
	@echo "  test         Run tests with pytest"
	@echo "  test-cov     Run tests with coverage report"
	@echo "  test-fast    Run tests without coverage (faster)"
	@echo ""
	@echo "$(BOLD)Development:$(RESET)"
	@echo "  run          Run the development server"
	@echo "  dev          Run development server with hot reload"
	@echo ""
	@echo "$(BOLD)Build & Deploy:$(RESET)"
	@echo "  build        Build the package"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run   Run Docker container"
	@echo ""
	@echo "$(BOLD)Maintenance:$(RESET)"
	@echo "  clean        Clean temporary files and caches"
	@echo "  deps-update  Update dependency lock files"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(BLUE)%-12s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation targets
install: ## Install production dependencies
	@echo "$(YELLOW)Installing production dependencies...$(RESET)"
	$(PIP) install -r requirements.txt

install-dev: ## Install development dependencies
	@echo "$(YELLOW)Installing development dependencies...$(RESET)"
	$(PIP) install -r requirements-dev.txt
	@echo "$(GREEN)Development environment ready!$(RESET)"

setup-hooks: ## Install pre-commit hooks
	@echo "$(YELLOW)Setting up pre-commit hooks...$(RESET)"
	$(PRECOMMIT) install
	@echo "$(GREEN)Pre-commit hooks installed!$(RESET)"

# Code quality targets
lint: ## Run linting with ruff
	@echo "$(YELLOW)Running ruff linter...$(RESET)"
	$(RUFF) check $(SRC_DIR)/ --fix --show-fixes
	@echo "$(GREEN)Linting complete!$(RESET)"

format: ## Format code with ruff and black
	@echo "$(YELLOW)Formatting code...$(RESET)"
	$(RUFF) format $(SRC_DIR)/
	$(BLACK) $(SRC_DIR)/
	@echo "$(GREEN)Code formatting complete!$(RESET)"

type-check: ## Run static type checking with mypy
	@echo "$(YELLOW)Running type checks...$(RESET)"
	$(MYPY) $(SRC_DIR)/
	@echo "$(GREEN)Type checking complete!$(RESET)"

pre-commit: ## Run pre-commit hooks on all files
	@echo "$(YELLOW)Running pre-commit hooks...$(RESET)"
	$(PRECOMMIT) run --all-files
	@echo "$(GREEN)Pre-commit checks complete!$(RESET)"

check-all: lint type-check ## Run all quality checks
	@echo "$(GREEN)All code quality checks passed!$(RESET)"

# Testing targets
test: ## Run tests with pytest
	@echo "$(YELLOW)Running tests...$(RESET)"
	$(PYTEST) -v
	@echo "$(GREEN)Tests complete!$(RESET)"

test-cov: ## Run tests with coverage report
	@echo "$(YELLOW)Running tests with coverage...$(RESET)"
	$(PYTEST) -v --cov=$(SRC_DIR) --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)Coverage report generated in htmlcov/$(RESET)"

test-fast: ## Run tests without coverage (faster)
	@echo "$(YELLOW)Running fast tests...$(RESET)"
	$(PYTEST) -v --no-cov -x
	@echo "$(GREEN)Fast tests complete!$(RESET)"

# Development targets
run: ## Run the development server
	@echo "$(YELLOW)Starting Prime Math API server...$(RESET)"
	@echo "$(BLUE)Server will be available at: http://localhost:8000$(RESET)"
	@echo "$(BLUE)API documentation at: http://localhost:8000/docs$(RESET)"
	$(UVICORN) app.main:app --host 0.0.0.0 --port 8000

dev: ## Run development server with hot reload
	@echo "$(YELLOW)Starting Prime Math API development server with hot reload...$(RESET)"
	@echo "$(BLUE)Server will be available at: http://localhost:8000$(RESET)"
	@echo "$(BLUE)API documentation at: http://localhost:8000/docs$(RESET)"
	@echo "$(GREEN)Hot reload enabled - code changes will automatically restart the server$(RESET)"
	$(UVICORN) app.main:app --host 0.0.0.0 --port 8000 --reload

# Build targets
build: ## Build the package
	@echo "$(YELLOW)Building package...$(RESET)"
	$(PYTHON) -m build
	@echo "$(GREEN)Package built successfully!$(RESET)"

# Docker targets
docker-build: ## Build Docker image
	@echo "$(YELLOW)Building Docker image...$(RESET)"
	docker build -t prime-math-api:latest .
	@echo "$(GREEN)Docker image built successfully!$(RESET)"

docker-run: ## Run Docker container
	@echo "$(YELLOW)Running Docker container...$(RESET)"
	@echo "$(BLUE)Server will be available at: http://localhost:8000$(RESET)"
	docker run -p 8000:8000 prime-math-api:latest

# Maintenance targets
clean: ## Clean temporary files and caches
	@echo "$(YELLOW)Cleaning temporary files...$(RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf build/ dist/ htmlcov/ .coverage
	@echo "$(GREEN)Cleanup complete!$(RESET)"

deps-update: ## Update dependency lock files
	@echo "$(YELLOW)Updating dependencies...$(RESET)"
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install --upgrade -r requirements-dev.txt
	@echo "$(GREEN)Dependencies updated!$(RESET)"

# Development workflow shortcuts
quick-check: lint test-fast ## Quick development check (lint + fast tests)
	@echo "$(GREEN)Quick development check passed!$(RESET)"

full-check: clean install-dev check-all test-cov ## Full quality check (everything)
	@echo "$(GREEN)Full quality check passed!$(RESET)"

# CI simulation
ci: clean install-dev check-all test-cov ## Simulate CI pipeline locally
	@echo "$(GREEN)CI pipeline simulation complete!$(RESET)"

# First-time setup
setup: install-dev setup-hooks ## Complete first-time setup
	@echo "$(GREEN)$(BOLD)Setup complete! You can now:$(RESET)"
	@echo "$(GREEN)  - Run 'make dev' to start the development server$(RESET)"
	@echo "$(GREEN)  - Run 'make test' to run the test suite$(RESET)"
	@echo "$(GREEN)  - Run 'make check-all' to run code quality checks$(RESET)"
	@echo "$(GREEN)  - Visit http://localhost:8000/docs for API documentation$(RESET)"