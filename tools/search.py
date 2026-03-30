import os
from dotenv import load_dotenv
from langchain_core.tools import tool
# from llama_index.llms.groq import Groq 
from llama_index.llms.nvidia import NVIDIA
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.postgres import PGVectorStore
from cfobuddy_logging import configure_logging

load_dotenv()
logger = configure_logging()

# ==========================
# EMBEDDING MODEL
# ==========================

Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-base-en-v1.5"
)

# Settings.llm = Groq(
#     model="llama-3.1-8b-instant",
#     temperature=0.01,
# )  

# Settings.llm = HuggingFaceEndpoint(
#     repo_id="google/gemma-3-27b-it",
#     task="text-generation",
#     max_new_tokens=512,
#     temperature=0.1,
#     huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
# )

Settings.llm = NVIDIA(model="meta/llama3-8b-instruct")


# ==========================
# LOAD INDEX FROM NEON DB
# ==========================

def load_index():
    try :
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
    logger.info("Index reloaded from Neon DB.")


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
    
    retriever = index.as_retriever(similarity_top_k=5, similarity_cutoff=0.5)
    nodes = retriever.retrieve(query)

    if not nodes:
        return "No relevant documents found."

    formatted = []
    for i, node in enumerate(nodes):
        source = node.metadata.get("file_name", "unknown")
        formatted.append(f"[Source: {source}]\n{node.get_content()}")

    return "\n\n".join(formatted)

# @tool
# def search_financial_docs(query: str) -> str:
#     """Search financial documents with AI-powered synthesis."""
#     try:
#         query_engine = index.as_query_engine(
#             similarity_top_k=5,
#             response_mode="compact"
#         )
#         response = query_engine.query(query)
        
#         sources = [node.metadata.get("file_name", "unknown") 
#                    for node in response.source_nodes]
        
#         return f"{response.response}\n\nSources: {', '.join(set(sources))}"
#     except Exception as e:
#         logger.error("Search failed: %s", e)
#         return "Failed to search documents. Please try again."