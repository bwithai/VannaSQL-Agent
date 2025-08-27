import os

import numpy as np

import requests
from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore
from app.core.config import settings
from chromadb.api.types import Documents, Embeddings


# ---- Normalize embeddings ----
def normalize(vec):
    v = np.array(vec, dtype=np.float32)
    return (v / np.linalg.norm(v)).tolist()


# ---- Ollama embedding wrapper ----
def get_ollama_embedding(model: str, text: str):
    response = requests.post(
        url=f"http://{settings.OLLAMA_HOST}/api/embeddings",
        json={"model": model, "prompt": text},
    )
    response.raise_for_status()
    return normalize(response.json()["embedding"])  # 👈 normalize here


class OllamaEmbeddingFunction:
    def __init__(self, model: str = "nomic-embed-text"):
        self.model = model

    def __call__(self, input: Documents) -> Embeddings:  # 👈 change texts → input
        return [get_ollama_embedding(self.model, t) for t in input]

    def name(self) -> str:
        return f"ollama-{self.model}"


class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        if not os.path.exists(settings.RAG_LAYER_DIR):
            os.makedirs(settings.RAG_LAYER_DIR)
            print(f"📁 Created directory: {settings.RAG_LAYER_DIR}")

        if config is None:
            config = {}

        config["path"] = settings.RAG_LAYER_DIR

        ollama_url = settings.OLLAMA_HOST
        config["ollama_host"] = ollama_url

        # Choose model from env var or default
        config["model"] = settings.OLLAMA_MODEL
        config["ollama_timeout"] = 900.0
        self.model = config["model"]

        # Explicitly set required attribute
        self.ollama_options = {}

        # Call both base classes directly
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

    def get_available_models(self):
        res = requests.get(f"{settings.OLLAMA_HOST}/api/tags")
        return [m["model"] for m in res.json().get("models", [])]

    def check_db(self, question):
        if self.config is not None:
            initial_prompt = self.config.get("initial_prompt", None)
        else:
            initial_prompt = None
        question_sql_list = self.get_similar_question_sql(question)
        ddl_list = self.get_related_ddl(question)
        doc_list = self.get_related_documentation(question)
        prompt = self.get_sql_prompt(
            initial_prompt=initial_prompt,
            question=question,
            question_sql_list=question_sql_list,
            ddl_list=ddl_list,
            doc_list=doc_list
        )
        print("=" * 50)
        print(prompt)
        print("=" * 50)


vn = MyVanna({
    "embedding_function": OllamaEmbeddingFunction("nomic-embed-text"),
})
# vn.check_db("Get the names and ranks of people from unit 'Alpha Unit'.")
