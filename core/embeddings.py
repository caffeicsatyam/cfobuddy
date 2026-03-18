from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

Settings.embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_folder="C:/Users/MSI/.cache/huggingface/hub"
)
Settings.llm = None