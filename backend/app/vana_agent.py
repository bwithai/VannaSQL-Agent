import os
import requests
from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore
from app.core.config import settings

class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        if not os.path.exists(settings.RAG_LAYER_DIR):
            os.makedirs(settings.RAG_LAYER_DIR)
            print(f"📁 Created directory: {settings.RAG_LAYER_DIR}")

        if config is None:
            config = {"path": settings.RAG_LAYER_DIR}

        ollama_url = settings.OLLAMA_HOST
        config["ollama_host"] = ollama_url

        # Choose model from env var or default
        config["model"] = settings.OLLAMA_MODEL
        self.model = config["model"]

        # Explicitly set required attribute
        self.ollama_options = {}

        # Call both base classes directly
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

    def get_available_models(self):
        res = requests.get(f"{settings.OLLAMA_HOST}/api/tags")
        return [m["model"] for m in res.json().get("models", [])]

vn = MyVanna()