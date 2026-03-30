import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from llama_index.llms.groq import Groq
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.postgres import PGVectorStore
from cfobuddy_logging import configure_logging
from functools import lru_cache

load_dotenv()
logger = configure_logging()

# ==========================
# EMBEDDING MODEL
# ==========================

Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-base-en-v1.5"  
)

Settings.llm = Groq(
    model="llama-3.1-8b-instant",  
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.1,
)

# ==========================
# LOAD INDEX FROM NEON DB
# ==========================

def load_index():
    try:
        vector_store = PGVectorStore.from_params(
            host=os.getenv("NEON_HOST"),
            database=os.getenv("NEON_DATABASE"),
            user=os.getenv("NEON_USER"),
            password=os.getenv("NEON_PASSWORD"),
            port="5432",
            table_name="data_cfo_buddy_vectors",
            embed_dim=768,
        )
        return VectorStoreIndex.from_vector_store(vector_store)
    except Exception as e:
        logger.error("Failed to load index: %s", e)
        raise

index = load_index()  

def reload_index():
    """Refresh in-memory index after rebuild."""
    global index
    index = load_index()
    cached_retrieve.cache_clear() 
    logger.info("Index reloaded from Neon DB.")

# ==========================
# Caching 
# ==========================

@lru_cache(maxsize=128)
def cached_retrieve(query: str):
    """Cache retrieval results for repeated queries."""
    retriever = index.as_retriever(similarity_top_k=5, similarity_cutoff=0.5)
    return retriever.retrieve(query)

# ==========================
# OPTIMIZED TOOL
# ==========================

import time

@tool
def search_financial_docs(query: str) -> str:
    """
    Search across all financial and customer documents using semantic
    similarity. Best for general questions, summaries, and keyword-based queries
    about internal CSV, PDF, Excel, or Word files.
    """
    start = time.time()
    
    nodes = cached_retrieve(query)
    
    elapsed = (time.time() - start) * 1000
    logger.info(f"⏱️ search_financial_docs: {elapsed:.2f}ms | found {len(nodes)} docs")

    if not nodes:
        return "No relevant documents found."

    formatted = []
    for i, node in enumerate(nodes):
        source = node.metadata.get("file_name", "unknown")
        formatted.append(f"[Source: {source}]\n{node.get_content()}")

    return "\n\n".join(formatted)