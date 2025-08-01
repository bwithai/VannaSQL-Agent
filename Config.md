# Download all dependencies as wheel files
pip download -d dep_pkg cryptography>=45.0.5 "vanna[chromadb,mysql,ollama,postgres]>=0.7.9"

# Install from local wheels (no internet required)
pip install --find-links dep_pkg --no-index cryptography>=45.0.5
pip install --find-links dep_pkg --no-index "vanna[chromadb,mysql,ollama,postgres]>=0.7.9"