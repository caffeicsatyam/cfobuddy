import os
from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from core.embeddings import embeddings

def load_default_vector_store():
    if not os.path.exists("faiss_index"):
        raise FileNotFoundError("No FAISS index found. Run: python build_index.py")
    return FAISS.load_local(
        "faiss_index",
        embeddings=embeddings,
        allow_dangerous_deserialization=True
    )

default_vector_store = load_default_vector_store()

@tool
def search_financial_docs(query: str) -> str:
    """
    Search across all financial and customer data documents using semantic
    similarity. Best for general questions, summaries, and keyword-based queries.
    """
    docs = default_vector_store.similarity_search(query, k=5)
    formatted = []
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source_file", doc.metadata.get("source", "unknown"))
        formatted.append(f"[Source: {source}]\n{doc.page_content}")
    return "\n\n".join(formatted)