import requests
import numpy as np
import chromadb
from chromadb.config import Settings
from chromadb.api.types import Documents, Embeddings
from app.core.config import settings


# ---- Normalize embeddings ----
def normalize(vec):
    v = np.array(vec, dtype=np.float32)
    return (v / np.linalg.norm(v)).tolist()


# ---- Ollama embedding wrapper ----
def get_ollama_embedding(model: str, text: str):
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": model, "prompt": text},
    )
    response.raise_for_status()
    return normalize(response.json()["embedding"])   # 👈 normalize here


class OllamaEmbeddingFunction:
    def __init__(self, model: str = "nomic-embed-text"):
        self.model = model

    def __call__(self, input: Documents) -> Embeddings:   # 👈 change texts → input
        return [get_ollama_embedding(self.model, t) for t in input]

    def name(self) -> str:
        return f"ollama-{self.model}"


# ---- Chroma client ----
db_path = settings.RAG_LAYER_DIR
client = chromadb.PersistentClient(
    path=db_path,
    settings=Settings(anonymized_telemetry=False),
)

# Create collection with cosine similarity
collection = client.get_or_create_collection(
    name="my_collection_ollama",
    embedding_function=OllamaEmbeddingFunction("nomic-embed-text"),
    metadata={"hnsw:space": "cosine"},   # 👈 force cosine similarity
)

# Add some docs (only once, otherwise comment this out after first run)
collection.add(
    ids=["doc1", "doc2"],
    documents=["List the top 3 units that gave the most awards.", "I like databases for AI"],
    metadatas=[{"topic": "db"}, {"topic": "ai"}],
)

# Query
results = collection.query(
    query_texts=["do you know about chroma"],
    n_results=2,
)
print(results)
