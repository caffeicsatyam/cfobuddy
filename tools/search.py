import os
import time
from functools import lru_cache
from dotenv import load_dotenv
from sqlalchemy import make_url
from langchain_core.tools import tool
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.postgres import PGVectorStore

# ==========================
# LOAD ENV
# ==========================
load_dotenv()

TABLE_NAME = "data_cfo_buddy_vectors"

# ==========================
# SETTINGS
# ==========================
Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    embed_batch_size=32,
)

Settings.llm = Groq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.1,
)

# ==========================
# DB CONNECTION
# ==========================
connection_string = os.getenv("DATABASE_URL")
if not connection_string:
    raise ValueError("DATABASE_URL is not set")

url = make_url(connection_string)

vector_store = PGVectorStore.from_params(
    database=url.database,
    host=url.host,
    password=url.password,
    port=url.port or 5432,
    user=url.username,
    table_name=TABLE_NAME,
    embed_dim=4096,          
    hybrid_search=True,
    text_search_config="english",
)

# ==========================
# LOAD INDEX
# ==========================
index = VectorStoreIndex.from_vector_store(vector_store)

# ==========================
# RELOAD SUPPORT
# ==========================
def reload_index():
    global index
    index = VectorStoreIndex.from_vector_store(vector_store)
    get_query_engine.cache_clear()
    print("Index reloaded")

# ==========================
# CACHE QUERY ENGINE
# ==========================
@lru_cache(maxsize=1)
def get_query_engine():
    retriever = index.as_retriever(
        similarity_top_k=5,
        similarity_cutoff=0.5,
        vector_store_query_mode="hybrid"
    )

    return RetrieverQueryEngine.from_args(
        retriever=retriever,
        response_mode="compact"
    )

# ==========================
# CLEAN QUERY
# ==========================
def clean_query(q: str):
    return q.replace("", "").strip()

# ==========================
# TOOL
# ==========================
from pydantic import BaseModel

class SearchInput(BaseModel):
    query: str

@tool(args_schema=SearchInput)
def search_financial_docs(query: str) -> str:
    """Search internal financial documents using hybrid semantic + keyword search."""
    
    start = time.time()

    query = clean_query(query)

    query_engine = get_query_engine()
    response = query_engine.query(query)

    elapsed = (time.time() - start) * 1000
    print(f" {elapsed:.2f} ms")

    return str(response)