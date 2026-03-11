import os
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ==========================
# LOAD ENV VARIABLES
# ==========================

load_dotenv()

# ==========================
# EMBEDDINGS
# ==========================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)

# ==========================
# LOAD ALL CSVs FROM data/ FOLDER
# ==========================

DATA_FOLDER = "data"
all_documents = []

csv_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]

if not csv_files:
    raise FileNotFoundError(f"No CSV files found in '{DATA_FOLDER}/' folder.")

print(f"Found {len(csv_files)} CSV files:\n")

for filename in csv_files:
    filepath = os.path.join(DATA_FOLDER, filename)
    try:
        loader = CSVLoader(filepath)
        docs = loader.load()
        for doc in docs:
            doc.metadata["source_file"] = filename
            doc.metadata["source"] = filename
        all_documents.extend(docs)
        print(f"   {filename} — {len(docs)} rows loaded")
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
