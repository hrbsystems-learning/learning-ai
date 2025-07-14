.PHONY: help install test lint format clean setup deploy

# Default target
help:
	@echo "Available commands:"
	@echo "  install     Install project dependencies"
	@echo "  setup       Complete project setup (install + env + hooks)"
	@echo "  test        Run tests"
	@echo "  test-cov    Run tests with coverage"
	@echo "  lint        Run linting checks"
	@echo "  format      Format code"
	@echo "  clean       Clean up generated files"
	@echo "  deploy      Deploy flows to Prefect"
	@echo "  docs        Serve documentation"

# Installation
install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install -e .

setup:
	python scripts/setup.py all

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# Code quality
lint:
	ruff check src/
	black --check src/
	mypy src/

format:
	ruff check src/ --fix
	black src/

# Cleanup
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name '*.pyc' -delete
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/

# Deployment
deploy:
	python scripts/deploy.py deploy-all

# Documentation
docs:
	mkdocs serve

# Development workflow
dev: format lint test
	@echo "Development checks passed!"
