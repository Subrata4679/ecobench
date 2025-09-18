# EcoBench Backend Makefile

.PHONY: help install test test-unit test-integration test-coverage lint format clean run dev migrate upgrade downgrade

# Default target
help:
	@echo "Available commands:"
	@echo "  install       Install dependencies"
	@echo "  test          Run all tests"
	@echo "  test-unit     Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-coverage Run tests with coverage report"
	@echo "  lint          Run linting checks"
	@echo "  format        Format code"
	@echo "  clean         Clean up temporary files"
	@echo "  run           Run the application"
	@echo "  dev           Run in development mode"
	@echo "  migrate       Create new migration"
	@echo "  upgrade       Apply migrations"
	@echo "  downgrade     Downgrade migrations"

# Install dependencies
install:
	pip install -r requirements.txt

# Run all tests
test:
	pytest -v

# Run unit tests only
test-unit:
	pytest -v -m unit

# Run integration tests only
test-integration:
	pytest -v -m integration

# Run tests with coverage
test-coverage:
	pytest --cov=app --cov-report=html --cov-report=term-missing

# Lint code
lint:
	flake8 app tests
	black --check app tests
	isort --check-only app tests

# Format code
format:
	black app tests
	isort app tests

# Clean temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

# Run application
run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run in development mode
dev:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Database migrations
migrate:
	alembic revision --autogenerate -m "$(message)"

upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1
