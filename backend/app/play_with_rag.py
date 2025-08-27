import json
from pprint import pprint

from chromadb.utils import embedding_functions
from app.core.config import settings
import chromadb
from chromadb.config import Settings

db_path = settings.RAG_LAYER_DIR

chroma_client = chromadb.PersistentClient(
                path=db_path, settings=Settings(anonymized_telemetry=False)
            )

default_ef = embedding_functions.DefaultEmbeddingFunction()
n_results_ddl = 10


ddl_collection = chroma_client.get_or_create_collection(
            name="ddl",
            embedding_function=default_ef,
            metadata=None,
        )




def _extract_documents(query_results) -> list:
    """
    Static method to extract the documents from the results of a query.

    Args:
        query_results (pd.DataFrame): The dataframe to use.

    Returns:
        List[str] or None: The extracted documents, or an empty list or
        single document if an error occurred.
    """
    if query_results is None:
        return []

    if "documents" in query_results:
        documents = query_results["documents"]

        if len(documents) == 1 and isinstance(documents[0], list):
            try:
                documents = [json.loads(doc) for doc in documents[0]]
            except Exception as e:
                return documents[0]

        return documents

result = ddl_collection.query(
                query_texts=["question"],
                n_results=n_results_ddl,
            )
print("-"*50)
print(result)
print("-"*50)
ddl_list = _extract_documents(result)


def str_to_approx_token_count(string: str) -> int:
    return len(string) / 4

def add_ddl_to_prompt(
        initial_prompt: str, ddl_list: list[str], max_tokens: int = 14000
) -> str:
    if len(ddl_list) > 0:
        initial_prompt += "\n===Tables \n"

        for ddl in ddl_list:
            if (
                    str_to_approx_token_count(initial_prompt)
                    + str_to_approx_token_count(ddl)
                    < max_tokens
            ):
                initial_prompt += f"{ddl}\n\n"

    return initial_prompt

if __name__ == "__main__":
    initial_prompt = f"You are a MySQL 8 expert. " + \
                "Please help to generate a SQL query to answer the question. Your response should ONLY be based on the given context and follow the response guidelines and format instructions. "
    initial_prompt = add_ddl_to_prompt(
                initial_prompt, ddl_list, max_tokens=14000
            )
    print("len: ", len(ddl_list))
    print("="*50)
    print(ddl_list)
    print("="*50)
    print(initial_prompt)