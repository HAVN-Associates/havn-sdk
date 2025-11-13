.PHONY: help install test lint format clean

help:
	@echo "HAVN Python SDK - Development Commands"
	@echo ""
	@echo "install    : Install package and dependencies"
	@echo "test       : Run tests with coverage"
	@echo "lint       : Run linters (flake8, mypy)"
	@echo "format     : Format code (black, isort)"
	@echo "clean      : Remove build artifacts"
	@echo "build      : Build distribution packages"
	@echo "publish    : Publish to PyPI"

install:
	pip install -e ".[dev]"

test:
	pytest --cov=havn --cov-report=term-missing --cov-report=html

lint:
	flake8 havn tests
	mypy havn

format:
	black havn tests examples
	isort havn tests examples

clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf htmlcov/ .coverage .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python setup.py sdist bdist_wheel

publish: build
	twine upload dist/*
