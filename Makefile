# VannaSQL Agent Docker Management

.PHONY: help build run dev stop clean logs shell test

# Default target
help:
	@echo "VannaSQL Agent Docker Commands:"
	@echo "  build      - Build the Docker image"
	@echo "  run        - Run the application in Docker"
	@echo "  dev        - Start development environment"
	@echo "  stop       - Stop all containers"
	@echo "  clean      - Remove containers and images"
	@echo "  logs       - View container logs"
	@echo "  shell      - Access container shell"
	@echo "  test       - Run tests in container"
	@echo "  rebuild    - Clean build and run"

# Build the Docker image
build:
	docker-compose build

# Run the application
run:
	docker-compose up -d

# Start development environment with live code reloading
dev:
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Development environment started!"
	@echo "Access shell with: make shell-dev"
	@echo "Run your app with: docker-compose -f docker-compose.dev.yml exec vannasql-agent-dev python hello.py"

# Stop all containers
stop:
	docker-compose down
	docker-compose -f docker-compose.dev.yml down

# Clean up containers and images
clean:
	docker-compose down --rmi all -v
	docker-compose -f docker-compose.dev.yml down --rmi all -v
	docker system prune -f

# View logs
logs:
	docker-compose logs -f

# View development logs
logs-dev:
	docker-compose -f docker-compose.dev.yml logs -f

# Access container shell
shell:
	docker-compose exec vannasql-agent bash

# Access development container shell
shell-dev:
	docker-compose -f docker-compose.dev.yml exec vannasql-agent-dev bash

# Run tests in container
test:
	docker-compose exec vannasql-agent python -m pytest

# Run specific script
run-script:
	@read -p "Enter script name (e.g., hello.py): " script; \
	docker-compose exec vannasql-agent python $$script

# Run specific script in dev environment
run-script-dev:
	@read -p "Enter script name (e.g., hello.py): " script; \
	docker-compose -f docker-compose.dev.yml exec vannasql-agent-dev python $$script

# Rebuild everything
rebuild: clean build run

# Rebuild development environment
rebuild-dev: clean dev

# Check if Ollama is accessible from container
check-ollama:
	docker-compose exec vannasql-agent curl -f http://host.docker.internal:11434/api/version || echo "Ollama not accessible"

# Check if MySQL is accessible from container
check-mysql:
	docker-compose exec vannasql-agent mysql -h host.docker.internal -u newuser -pnewpassword -e "SHOW DATABASES;" || echo "MySQL not accessible"

# Install additional Python package in running container using UV
install-package:
	@read -p "Enter package name: " package; \
	docker-compose exec vannasql-agent uv add $$package

# Install additional Python package in dev container using UV
install-package-dev:
	@read -p "Enter package name: " package; \
	docker-compose -f docker-compose.dev.yml exec vannasql-agent-dev uv add --group dev $$package

# Show installed packages
list-packages:
	docker-compose exec vannasql-agent uv pip list

# Show installed packages in dev
list-packages-dev:
	docker-compose -f docker-compose.dev.yml exec vannasql-agent-dev uv pip list

# Sync dependencies (useful after pyproject.toml changes)
sync-deps:
	docker-compose exec vannasql-agent uv sync

# Sync dev dependencies
sync-deps-dev:
	docker-compose -f docker-compose.dev.yml exec vannasql-agent-dev uv sync --group dev