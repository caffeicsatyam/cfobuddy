import os
from dotenv import load_dotenv

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.file import PyMuPDFReader
from llama_index.vector_stores.postgres import PGVectorStore

load_dotenv()

DATA_FOLDER = "data"


def build_index():
    """Build and store vectors in Neon DB."""

    Settings.embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        cache_folder="C:/Users/MSI/.cache/huggingface/hub"
    )
    Settings.llm = None

    # Connect to Neon via individual params
    vector_store = PGVectorStore.from_params(
        host=os.getenv("NEON_HOST"),
        database=os.getenv("NEON_DATABASE"),
        user=os.getenv("NEON_USER"),
        password=os.getenv("NEON_PASSWORD"),
        port="5432",
        table_name="cfo_buddy_vectors",
        embed_dim=384,
    )

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

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
    print("Building index and storing in Neon DB...")

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True
    )

    print("\n✅ Vectors stored in Neon DB!")

    from tools.search import reload_index
    reload_index()


if __name__ == "__main__":
    build_index()