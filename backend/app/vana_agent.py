import os
import requests
from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore

class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        if config is None:
            config = {}

        ollama_url = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
        config["ollama_host"] = ollama_url

        # Choose model from env var or default
        config["model"] = os.getenv("OLLAMA_MODEL", "phi4-mini:latest")
        self.model = config["model"]

        # Explicitly set required attribute
        self.ollama_options = {}

        # Call both base classes directly
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

# Later in the script:
OLLAMA_HOST = os.getenv("OLLAMA_HOST")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

# Fetch and print available models
res = requests.get(f"{OLLAMA_HOST}/api/tags")
print("Available models:", [m["model"] for m in res.json().get("models", [])])

# Create RAG-Layer directory if it doesn't exist
rag_layer_dir = "RAG-Layer"
if not os.path.exists(rag_layer_dir):
    os.makedirs(rag_layer_dir)
    print(f"📁 Created directory: {rag_layer_dir}")

vn = MyVanna(config={"path": rag_layer_dir})