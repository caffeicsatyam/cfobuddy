import os
from langchain_core.tools import tool

from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Settings,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# ==========================
# EMBEDDING MODEL 
# ==========================

Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder="C:/Users/MSI/.cache/huggingface/hub"  
)
Settings.llm = None

# ==========================
# LOAD INDEX FROM STORAGE
# ==========================

STORAGE_FOLDER = "storage"

def load_index():
    if not os.path.exists(STORAGE_FOLDER):
        raise FileNotFoundError(
            f"No index found at '{STORAGE_FOLDER}/'. Run: python build_index.py"
        )
    storage_context = StorageContext.from_defaults(persist_dir=STORAGE_FOLDER)
    return load_index_from_storage(storage_context)

index = load_index()
query_engine = index.as_query_engine(
    similarity_top_k=5,
    response_mode="no_text",  
)

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