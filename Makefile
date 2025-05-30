.PHONY: help install test lint format build run run-download clean docker-build docker-up docker-down docker-logs

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Puzzle Swap ETL - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with Poetry
	poetry install

test: ## Run tests
	poetry run pytest -v

lint: ## Run linting (flake8, black, isort)
	poetry run black --check .
	poetry run isort --check-only .
	poetry run flake8 .

format: ## Format code with black and isort
	poetry run black .
	poetry run isort .

build: ## Build the project
	poetry build

run: ## Run the ETL pipeline locally
	poetry run puzzle-etl run --full

run-download: ## Download blockchain data locally
	poetry run puzzle-etl download

init-db: ## Initialize database schema locally
	poetry run puzzle-etl init-db

# Docker commands
docker-build: ## Build Docker image
	docker-compose build

docker-up: ## Start services with Docker Compose
	docker-compose up -d

docker-down: ## Stop services with Docker Compose
	docker-compose down

docker-logs: ## Show logs from Docker containers
	docker-compose logs -f

docker-run: ## Build and run the complete system with Docker
	docker-compose up --build

docker-clean: ## Clean up Docker resources
	docker-compose down -v
	docker system prune -f

# Development commands
dev-setup: install ## Set up development environment
	poetry run pre-commit install

clean: ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete 