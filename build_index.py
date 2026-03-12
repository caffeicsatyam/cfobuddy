import os
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import (
    CSVLoader,
    PyPDFLoader,
    UnstructuredExcelLoader,
    Docx2txtLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# ==========================
# EMBEDDINGS
# ==========================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)

# ==========================
# FILE LOADER MAP
# ==========================

LOADERS = {
    ".csv":  CSVLoader,
    ".pdf":  PyPDFLoader,
    ".xlsx": UnstructuredExcelLoader,
    ".xls":  UnstructuredExcelLoader,
    ".docx": Docx2txtLoader,
}

SUPPORTED_EXTENSIONS = set(LOADERS.keys())

# ==========================
# LOAD ALL FILES FROM data/ FOLDER
# ==========================

DATA_FOLDER = "data"
all_documents = []

if not os.path.exists(DATA_FOLDER):
    raise FileNotFoundError(f"'{DATA_FOLDER}/' folder not found.")

all_files = [
    f for f in os.listdir(DATA_FOLDER)
    if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS
]

if not all_files:
    raise FileNotFoundError(
        f"No supported files found in '{DATA_FOLDER}/'. "
        f"Supported types: {', '.join(SUPPORTED_EXTENSIONS)}"
    )

print(f"Found {len(all_files)} files:\n")

for filename in all_files:
    filepath = os.path.join(DATA_FOLDER, filename)
    ext = os.path.splitext(filename)[1].lower()

    try:
        loader_class = LOADERS[ext]
        loader = loader_class(filepath)
        docs = loader.load()

        for doc in docs:
            doc.metadata["source_file"] = filename
            doc.metadata["source"] = filename
            doc.metadata["file_type"] = ext.lstrip(".")

        all_documents.extend(docs)
        print(f" {filename} ({ext}) — {len(docs)} chunks loaded")

    except Exception as e:
        print(f"  {filename} — failed to load: {e}")

print(f"\nTotal documents loaded: {len(all_documents)}")

# ==========================
# TEXT SPLITTING
# ==========================

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

texts = splitter.split_documents(all_documents)
print(f"Split into {len(texts)} chunks.\n")

# ==========================
# BUILD FAISS INDEX IN BATCHES
# ==========================

BATCH_SIZE = 100

total_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE
print(f"Building FAISS index in {total_batches} batches of {BATCH_SIZE}...")

vector_store = None

for i in range(0, len(texts), BATCH_SIZE):
    batch = texts[i:i + BATCH_SIZE]
    batch_num = (i // BATCH_SIZE) + 1

    print(f"  Embedding batch {batch_num}/{total_batches} ({len(batch)} chunks)...")

    if vector_store is None:
        vector_store = FAISS.from_documents(batch, embeddings)
    else:
        batch_store = FAISS.from_documents(batch, embeddings)
        vector_store.merge_from(batch_store)

vector_store.save_local("faiss_index")
print("\nFAISS index saved to 'faiss_index/'")
print("Now run: python main.py")