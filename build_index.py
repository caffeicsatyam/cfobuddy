import os
from dotenv import load_dotenv
from llama_index.readers.file import PyMuPDFReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
)


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
# LOAD ALL FILES FROM data/
# SimpleDirectoryReader handles CSV, PDF, Excel, Word natively
# ==========================

DATA_FOLDER = "data"
STORAGE_FOLDER = "storage"

if not os.path.exists(DATA_FOLDER):
    raise FileNotFoundError(f"'{DATA_FOLDER}/' folder not found.")

print(f"Loading files from '{DATA_FOLDER}/'...\n")

documents = SimpleDirectoryReader(
    input_dir=DATA_FOLDER,
    recursive=True,
    filename_as_id=True,
    file_extractor={".pdf": PyMuPDFReader()}  
).load_data(show_progress=True)

if not documents:
    raise ValueError(f"No documents found in '{DATA_FOLDER}/'.")

print(f"\nLoaded {len(documents)} document chunks.")
# ==========================
# BUILD INDEX
# ==========================
print("Building index...")
index = VectorStoreIndex.from_documents(
    documents,
    show_progress=True
)
# ==========================
# PERSIST TO DISK
# ==========================
index.storage_context.persist(persist_dir=STORAGE_FOLDER)
print(f"\nIndex saved to '{STORAGE_FOLDER}/'")
print("Now run: python main.py")