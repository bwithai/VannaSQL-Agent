# Offline Package Installation Guide

This guide explains how to download Python packages for offline installation, resolving common dependency conflicts and ensuring all packages are in wheel format.

## Problem Overview

When setting up Python packages for offline use, you might encounter these issues:
- Some packages download as `.tar.gz` (source) instead of `.whl` (wheel) files
- Source packages require compilation and build tools on the target machine
- Dependency version conflicts between different packages
- Missing build dependencies (setuptools, wheel)

## Solution Approach

We'll download all dependencies as wheel files and resolve conflicts step by step.

## Step-by-Step Commands

### 1. Create Dependencies Directory
```bash
# Create a directory to store all package files
mkdir dep_pkg
```

### 2. Download Basic Build Dependencies
```bash
# Download essential build tools (needed for any package installation)
pip download -d dep_pkg --only-binary=:all: setuptools wheel
```
**Why this step?** Some packages require these tools even for wheel installation.

### 3. Download Core Packages
```bash
# Download the main package without optional dependencies first
pip download -d dep_pkg --only-binary=:all: vanna>=0.7.9
```
**Why separately?** This avoids complex dependency resolution conflicts.

### 4. Download Security Dependencies
```bash
# Download cryptography package (often has specific requirements)
pip download -d dep_pkg --only-binary=:all: cryptography>=45.0.5
```

### 5. Handle Package with Version Conflicts
```bash
# Download specific compatible versions to avoid conflicts
pip download -d dep_pkg --only-binary=:all: "chroma-hnswlib==0.7.5" "numpy>=1.22.5,<2.0.0"
```
**What happened?** ChromaDB needed chroma-hnswlib==0.7.6, but only 0.7.5 was available as wheel.

### 6. Fix the Version Conflict
```bash
# Download the exact version needed (might be source format)
pip download -d dep_pkg chroma-hnswlib==0.7.6 --prefer-binary

# Convert source package to wheel format
pip wheel -w dep_pkg --find-links dep_pkg chroma-hnswlib==0.7.6

# Clean up the source file
Remove-Item dep_pkg\chroma_hnswlib-0.7.6.tar.gz  # Windows PowerShell
# rm dep_pkg/chroma_hnswlib-0.7.6.tar.gz         # Linux/Mac
```
**Why convert?** Wheel files install faster and don't need compilation.

### 7. Download Missing Package
```bash
# Download package that wasn't included in initial download
pip download -d dep_pkg --only-binary=:all: flasgger
```

### 8. Handle Another Source Package
```bash
# Convert PyPika from source to wheel format
pip wheel -w dep_pkg --find-links dep_pkg --no-deps PyPika==0.48.9

# Remove the source version
Remove-Item dep_pkg\PyPika-0.48.9.tar.gz  # Windows PowerShell
# rm dep_pkg/PyPika-0.48.9.tar.gz         # Linux/Mac
```

### 9. Download Remaining Optional Dependencies
```bash
# Download database-specific packages
pip download -d dep_pkg --only-binary=:all: PyMySQL ollama psycopg2-binary db-dtypes
```

### 10. Download Main Package with All Dependencies
```bash
# Now download the complete package (this should work with resolved conflicts)
pip download -d dep_pkg --only-binary=:all: "vanna[chromadb,mysql,ollama,postgres]>=0.7.9"
```

## Verification Commands

### Test Offline Installation
```bash
# Test if all dependencies can be resolved (dry run - doesn't actually install)
pip install --find-links dep_pkg --no-index --dry-run "vanna[chromadb,mysql,ollama,postgres]>=0.7.9"
```
**What to expect:** Long list of packages that "Would install" - this means success!

### Check Package Directory
```bash
# List all downloaded packages
ls dep_pkg/          # Linux/Mac
dir dep_pkg\         # Windows

# Count packages
ls dep_pkg/ | wc -l  # Linux/Mac - should show 100+ files
```

## Offline Installation (On Target Machine)

### Method 1: Install Everything at Once
```bash
pip install --find-links dep_pkg --no-index "vanna[chromadb,mysql,ollama,postgres]>=0.7.9"
```

### Method 2: Step-by-Step Installation (Safer)
```bash
# Install core dependencies first
pip install --find-links dep_pkg --no-index cryptography>=45.0.5

# Install chromadb with specific version
pip install --find-links dep_pkg --no-index "chromadb>=0.6.3,<0.7.0"

# Install main package
pip install --find-links dep_pkg --no-index vanna>=0.7.9

# Install optional dependencies
pip install --find-links dep_pkg --no-index PyMySQL ollama psycopg2-binary db-dtypes
```

### Verify Installation Works
```bash
python -c "import vanna; print('Vanna installed successfully')"
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
- Try downloading without `--only-binary=:all:`
- Use `pip wheel` to convert the source package

### If you get dependency conflicts:
- Download packages individually rather than all at once
- Use specific version ranges to force compatibility
- Check which exact versions are conflicting in the error message

### If installation fails on offline machine:
- Ensure all `.tar.gz` files are converted to `.whl`
- Check that build dependencies (setuptools, wheel) are included
- Use `--dry-run` first to test before actual installation

## Files Structure
After completion, your `dep_pkg` directory should contain:
```
dep_pkg/
├── vanna-0.7.9-py3-none-any.whl
├── chromadb-0.6.3-py3-none-any.whl
├── chroma_hnswlib-0.7.6-cp312-cp312-win_amd64.whl
├── pypika-0.48.9-py2.py3-none-any.whl
├── ... (100+ other wheel files)
└── (no .tar.gz files remaining)
```

## Summary

This process ensures all Python packages are downloaded as wheel files for reliable offline installation, with all dependency conflicts resolved and build tools included.