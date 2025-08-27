import requests
import chromadb
from chromadb.config import Settings
from chromadb.api.types import Documents, Embeddings
from app.core.config import settings

# ---- Ollama embedding wrapper ----
def get_ollama_embedding(model: str, text: str):
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": model, "prompt": text}
    )
    return response.json()["embedding"]

class OllamaEmbeddingFunction:
    def __init__(self, model: str = "nomic-embed-text"):  # 👈 best local model for embeddings
        self.model = model

    def __call__(self, texts: Documents) -> Embeddings:
        return [get_ollama_embedding(self.model, t) for t in texts]

    def name(self) -> str:   # 👈 required by Chroma
        return f"ollama-{self.model}"

# ---- Chroma client ----
db_path = settings.RAG_LAYER_DIR

client = chromadb.PersistentClient(
    path=db_path,
    settings=Settings(anonymized_telemetry=False)
)

# Attach Ollama embeddings
ollama_embeddings = OllamaEmbeddingFunction(model="nomic-embed-text")

collection = client.get_or_create_collection(
    name="my_collection",
    embedding_function=ollama_embeddings
)

# Add some docs (only once)
# collection.add(
#     ids=["doc1", "doc2"],
#     documents=["Chroma is an embedding database", "I like databases for AI"],
#     metadatas=[{"topic": "db"}, {"topic": "ai"}]
# )

# Query
results = collection.query(
    query_texts=["hi there how are you. can i know your name"],
    n_results=2
)

print(results)
