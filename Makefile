.PHONY: help install install-dev test lint format clean build publish

help:
	@echo "Available commands:"
	@echo "  make install      - Install package"
	@echo "  make install-dev  - Install package with dev dependencies"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters (ruff, mypy)"
	@echo "  make format       - Format code (black, ruff)"
	@echo "  make clean        - Remove build artifacts"
	@echo "  make build        - Build package"
	@echo "  make publish      - Publish to PyPI (requires credentials)"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest

lint:
	ruff check src tests
	mypy src

format:
	black src tests
	ruff check --fix src tests

clean:
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

publish: build
	twine check dist/*
	twine upload dist/*
