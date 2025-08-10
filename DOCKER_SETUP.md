# VannaSQL Agent Docker Setup

This guide helps you run your VannaSQL Agent application in Docker while maintaining a development-friendly environment.

## Prerequisites

1. **Docker & Docker Compose** installed on your system
2. **Ollama running on your host machine** (port 11434)
3. **MySQL running on your host machine** (port 3306) with the `cfms` database
4. **Python 3.12+** (for local development)

## Quick Start

### 1. Build and Run the Application

```bash
# Build and start the application
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### 2. Access the Application

- **Main Application**: Container will run `hello.py`
- **Web Interface**: http://localhost:5000 (if using `web_interface.py`)
- **API Endpoints**: http://localhost:8000 (if using FastAPI)

### 3. Development Workflow

The setup includes volume mounting for development:

```bash
# Your code changes are immediately reflected in the container
# Edit files on your host machine, and they'll be available in Docker

# To run a specific script in the container:
docker-compose exec vannasql-agent python example_usage.py

# To access the container shell:
docker-compose exec vannasql-agent bash

# To view logs:
docker-compose logs -f vannasql-agent
```

## Configuration

### Environment Variables

The application uses these environment variables (set in `docker-compose.yml`):

- `DB_HOST=host.docker.internal` - MySQL host (your local machine)
- `DB_PORT=3306` - MySQL port
- `DB_NAME=cfms` - Database name
- `DB_USER=newuser` - Database user
- `DB_PASSWORD=newpassword` - Database password
- `OLLAMA_HOST=http://host.docker.internal:11434` - Ollama service URL
- `OLLAMA_MODEL=phi4-mini:latest` - Ollama model to use

### Updating Your Application Code

If you need to modify your application to use environment variables:

```python
import os

# Database connection using environment variables
host = os.getenv('DB_HOST', 'localhost')
port = int(os.getenv('DB_PORT', '3306'))
dbname = os.getenv('DB_NAME', 'cfms')
user = os.getenv('DB_USER', 'newuser')
password = os.getenv('DB_PASSWORD', 'newpassword')

vn.connect_to_mysql(host=host, dbname=dbname, user=user, password=password, port=port)

# Ollama configuration
ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
model = os.getenv('OLLAMA_MODEL', 'phi4-mini:latest')
```

## Advanced Usage

### Running with Optional MySQL Container

If you want to run MySQL in Docker instead of using your host MySQL:

```bash
# Start with MySQL container
docker-compose --profile database up -d --build

# This will run MySQL on port 3307 (to avoid conflict with host MySQL)
# Update your application to connect to localhost:3307
```

### Debugging and Development

```bash
# Run specific Python scripts
docker-compose exec vannasql-agent python reasoning_vanna.py
docker-compose exec vannasql-agent python train-helper.py
docker-compose exec vannasql-agent python web_interface.py

# Install additional packages for development
docker-compose exec vannasql-agent pip install package-name

# Access Python REPL
docker-compose exec vannasql-agent python
```

### Rebuilding After Dependency Changes

When you update `pyproject.toml`:

```bash
# Rebuild the image
docker-compose build --no-cache

# Restart services
docker-compose up -d
```

## Data Persistence

- **ChromaDB Data**: Stored in `./RAG-Layer/` (mounted as volume)
- **MySQL Data**: If using Docker MySQL, stored in Docker volume `mysql_data`

## Troubleshooting

### Common Issues

1. **Cannot connect to Ollama**:
   - Ensure Ollama is running on host: `ollama serve`
   - Check if Ollama is accessible: `curl http://localhost:11434/api/version`

2. **Cannot connect to MySQL**:
   - Verify MySQL is running: `mysql -u newuser -p`
   - Check database exists: `SHOW DATABASES;`

3. **Permission issues with RAG-Layer**:
   ```bash
   # Fix permissions
   sudo chown -R $USER:$USER ./RAG-Layer/
   chmod -R 755 ./RAG-Layer/
   ```

4. **Import errors in container**:
   ```bash
   # Check installed packages
   docker-compose exec vannasql-agent pip list
   
   # Reinstall if needed
   docker-compose exec vannasql-agent pip install -e .
   ```

### Debugging Commands

```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs vannasql-agent

# Check container health
docker-compose exec vannasql-agent python -c "import vanna; print('Vanna imported successfully')"
docker-compose exec vannasql-agent python -c "import chromadb; print('ChromaDB imported successfully')"
docker-compose exec vannasql-agent python -c "import ollama; print('Ollama imported successfully')"
```

## Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (careful - this deletes data!)
docker-compose down -v

# Stop and remove images
docker-compose down --rmi all
```

## Next Steps

1. Modify your Python scripts to use environment variables for configuration
2. Test your application workflows in the Docker environment
3. Consider setting up automated testing in Docker
4. Use Docker for consistent deployment across different environments

## Notes

- The `dep_pkg/` directory is excluded from Docker (using `.dockerignore`)
- Dependencies are installed fresh from PyPI using **UV package manager** for faster builds
- Your source code is mounted as a volume for development convenience
- ChromaDB and ONNX Runtime are properly configured for the Docker environment
- UV package manager provides significantly faster dependency resolution and installation

## UV Package Manager Benefits

This Docker setup uses UV instead of pip for:
- ⚡ **10-100x faster** dependency installation
- 🔒 **Better dependency resolution** 
- 🚀 **Faster Docker builds**
- 💾 **Smaller image sizes**

### UV Commands in Container

```bash
# Install additional packages using UV (updates pyproject.toml)
make install-package-dev

# Install development packages
docker-compose exec vannasql-agent-dev uv add --dev package-name

# List installed packages
make list-packages-dev

# Sync dependencies after pyproject.toml changes
make sync-deps-dev

# Manual UV usage in container
docker-compose exec vannasql-agent-dev uv add package-name
docker-compose exec vannasql-agent-dev uv sync
docker-compose exec vannasql-agent-dev uv pip list
```

## Quick Start Commands

```bash
# Build and run in development mode
make dev

# Access the container shell
make shell-dev

# Run your main application
docker-compose -f docker-compose.dev.yml exec vannasql-agent-dev python hello.py

# Run web interface
docker-compose -f docker-compose.dev.yml exec vannasql-agent-dev python web_interface.py
```