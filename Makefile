# Makefile for Kong MCP Server

.PHONY: help install test-local lint format type-check test clean

# Default target
help:
	@echo "Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make test-local  - Run all CI checks locally"
	@echo "  make lint        - Run linting checks"
	@echo "  make format      - Format code with black and isort"
	@echo "  make type-check  - Run type checking"
	@echo "  make test        - Run tests"
	@echo "  make clean       - Clean up build artifacts"

# Install dependencies
install:
	python -m pip install --upgrade pip
	pip install -e .[dev]

# Run all CI checks locally (mirrors CI pipeline)
test-local:
	@echo "🔍 Running local CI tests..."
	@echo "============================"
	@./test-local.sh

# Run linting checks
lint:
	black --check src tests
	isort --check-only src tests
	flake8 src tests

# Format code
format:
	black src tests
	isort src tests

# Run type checking
type-check:
	mypy src

# Run tests
test:
	pytest --cov=kong_mcp_server --cov-report=txt --cov-report=term-missing

# Clean up build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf coverage.txt
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete