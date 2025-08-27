# Offline Package Installation Guide

This guide explains how to download Python packages for offline installation, resolving common dependency conflicts and ensuring all packages are in wheel format.

## Problem Overview

When setting up Python packages for offline use, you might encounter these issues:
- Some packages download as `.tar.gz` (source) instead of `.whl` (wheel) files
- Source packages require compilation and build tools on the target machine
- Dependency version conflicts between different packages
- Missing build dependencies (setuptools, wheel)

## Solution Approach

We'll download all dependencies as wheel files and resolve conflicts step by step using a simplified approach.

## Step-by-Step Commands

### 1. Create Dependencies Directory
```bash
# Create a directory to store all package files
mkdir docker_pkg
```

### 2. Download Basic Build Dependencies
```bash
# Download essential build tools (needed for any package installation)
pip download -d docker_pkg --only-binary=:all: setuptools wheel
```
**Why this step?** Some packages require these tools even for wheel installation.

### 3. Download Security Dependencies
```bash
# Download cryptography package (often has specific requirements)
pip download -d docker_pkg --only-binary=:all: cryptography>=45.0.5
```

### 4. Download Core Vanna Package
```bash
# Download the main package without optional dependencies first
pip download -d docker_pkg --only-binary=:all: vanna>=0.7.9
```
**Why separately?** This avoids complex dependency resolution conflicts.

### 5. Download Database-Specific Dependencies
```bash
# Download database-specific packages
pip download -d docker_pkg --only-binary=:all: PyMySQL ollama psycopg2-binary db-dtypes
```

### 6. Download ChromaDB (Latest Version)
```bash
# Download ChromaDB separately to avoid version conflicts
pip download -d docker_pkg --prefer-binary chromadb
```
**Note:** This downloads the latest stable version (1.0.x) which works better than older versions.

### 7. Convert Any Source Packages to Wheels
```bash
# Check if PyPika was downloaded as source and convert it
pip wheel -w docker_pkg --find-links docker_pkg --no-deps PyPika==0.48.9

# Remove any .tar.gz files (keep only .whl files)
# Windows PowerShell:
Get-ChildItem docker_pkg\*.tar.gz | Remove-Item
# Linux/Mac:
# rm dep_pkg/*.tar.gz
```

## Verification Commands

### Test Offline Installation
```bash
# Test if all dependencies can be resolved (dry run - doesn't actually install)
# Note: This may take time due to dependency resolution, but should eventually succeed
pip install --find-links docker_pkg --no-index --dry-run cryptography chromadb PyMySQL ollama psycopg2-binary db-dtypes
```
**What to expect:** List of packages that "Would install" - this means success!

### Check Package Directory
```bash
# List all downloaded packages
ls dep_pkg/          # Linux/Mac
dir dep_pkg\         # Windows

# Count packages (should show 100+ files)
ls dep_pkg/ | wc -l                    # Linux/Mac
(Get-ChildItem dep_pkg\).Count         # Windows PowerShell
```

## Offline Installation (On Target Machine)

### Method 1: Install Core Components First (Recommended)
```bash
# Install build tools first
pip install --find-links dep_pkg --no-index setuptools wheel

# Install core dependencies
pip install --find-links dep_pkg --no-index cryptography

# Install main package
pip install --find-links dep_pkg --no-index vanna

# Install ChromaDB
pip install --find-links dep_pkg --no-index chromadb

# Install database-specific dependencies
pip install --find-links dep_pkg --no-index PyMySQL ollama psycopg2-binary db-dtypes
```

### Method 2: Install Everything at Once (Alternative)
```bash
# Try to install all at once (may have dependency resolution issues)
uv pip install --find-links docker_pkg --no-index cryptography chromadb PyMySQL ollama psycopg2-binary db-dtypes pydantic_settings sqlparse plotly tabulate
uv pip install --find-links docker_pkg/fastapi --no-index fastapi uvicorn pydantic tabulate
```

### Verify Installation Works
```bash
python -c "import vanna; print('Vanna installed successfully')"
python -c "import chromadb; print('ChromaDB installed successfully')"
```

## Key Command Explanations

### `--only-binary=:all:`
Forces pip to only download wheel files, refusing source distributions.

### `--find-links dep_pkg`
Tells pip to look for packages in the local `dep_pkg` directory.

### `--no-index`
Prevents pip from checking PyPI (Python Package Index) online.

### `--dry-run`
Simulates installation without actually installing anything.

### `pip wheel`
Converts source packages (.tar.gz) to wheel format (.whl).

### `--no-deps`
Only processes the specified package, ignoring its dependencies.

## Troubleshooting Tips

### If you get "No matching distribution found":
- The package might not have a wheel version available
- Remove `--only-binary=:all:` flag and use `--prefer-binary` instead
- Use `pip wheel` to convert any source package to wheel format

### If you get dependency conflicts:
- Download packages individually rather than all at once (as shown in our step-by-step approach)
- Use the latest ChromaDB version (1.0.x) instead of trying to force older versions
- Install packages one by one on the target machine instead of all at once

### If installation fails on offline machine:
- Ensure all `.tar.gz` files are converted to `.whl` (use the cleanup command)
- Check that build dependencies (setuptools, wheel) are included
- Use the step-by-step installation method instead of installing everything at once
- Use `--dry-run` first to test before actual installation

### Common Issues and Solutions:
- **ChromaDB version conflicts**: Use the latest version (1.0.x) which is more stable
- **PyPika source package**: Convert to wheel using `pip wheel` command
- **Long dependency resolution**: Be patient, modern pip can take time to resolve complex dependencies

## Files Structure
After completion, your `dep_pkg` directory should contain:
```
dep_pkg/
├── vanna-0.7.9-py3-none-any.whl
├── chromadb-1.0.15-cp39-abi3-win_amd64.whl
├── pypika-0.48.9-py2.py3-none-any.whl
├── cryptography-45.0.6-cp311-abi3-win_amd64.whl
├── pymysql-1.1.1-py3-none-any.whl
├── ollama-0.5.2-py3-none-any.whl
├── psycopg2_binary-2.9.10-cp312-cp312-win_amd64.whl
├── db_dtypes-1.4.3-py3-none-any.whl
├── ... (100+ other wheel files)
└── (no .tar.gz files remaining)
```

## Summary

This simplified process downloads all Python packages as wheel files for reliable offline installation. The key improvements:
- Uses latest ChromaDB version (1.0.x) to avoid legacy conflicts
- Downloads packages in logical groups to avoid complex dependency resolution
- Converts any source packages to wheels for better compatibility
- Provides step-by-step installation method for reliable offline deployment

# New Packages
```bash
pip download -d docker_pkg/new --only-binary=:all: pydantic_settings
```