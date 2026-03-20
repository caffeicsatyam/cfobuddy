import os
from dotenv import load_dotenv
from langchain_core.tools import tool

from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.postgres import PGVectorStore

load_dotenv()

# ==========================
# EMBEDDING MODEL
# ==========================

Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder="C:/Users/MSI/.cache/huggingface/hub"
)
Settings.llm = None

# ==========================
# LOAD INDEX FROM NEON DB
# ==========================

def load_index():
    vector_store = PGVectorStore.from_params(
        host=os.getenv("NEON_HOST"),
        database=os.getenv("NEON_DATABASE"),
        user=os.getenv("NEON_USER"),
        password=os.getenv("NEON_PASSWORD"),
        port="5432",
        table_name="cfo_buddy_vectors",
        embed_dim=384,
    )
    return VectorStoreIndex.from_vector_store(vector_store)


index = load_index()


def reload_index():
    """Refresh in-memory index after rebuild."""
    global index
    index = load_index()
    print("Index reloaded from Neon DB.")


# ==========================
# TOOL
# ==========================

@tool
def search_financial_docs(query: str) -> str:
    """
    Search across all financial and customer data documents using semantic
    similarity. Best for general questions, summaries, and keyword-based queries
    about internal CSV, PDF, Excel, or Word files.
    """
    retriever = index.as_retriever(similarity_top_k=10)
    nodes = retriever.retrieve(query)

    if not nodes:
        return "No relevant documents found."

    formatted = []
    for i, node in enumerate(nodes):
        source = node.metadata.get("file_name", "unknown")
        formatted.append(f"[Source: {source}]\n{node.get_content()}")

    return "\n\n".join(formatted)