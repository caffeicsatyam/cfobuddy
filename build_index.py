import os
import datetime
from dotenv import load_dotenv

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings,
    StorageContext
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.file import UnstructuredReader
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.core.node_parser import SentenceSplitter

from cfobuddy_logging import configure_logging

load_dotenv()
logger = configure_logging()

DATA_FOLDER = "data"
TABLE_NAME = "data_cfo_buddy_vectors"

def build_index():
    """Build and store hybrid vectors in Neon DB."""

    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-base-en-v1.5"
    )
    Settings.llm = None

    Settings.node_parser = SentenceSplitter(
        chunk_size=512,
        chunk_overlap=100
    )

    vector_store = PGVectorStore.from_params(
        host=os.getenv("NEON_HOST"),
        database=os.getenv("NEON_DATABASE"),
        user=os.getenv("NEON_USER"),
        password=os.getenv("NEON_PASSWORD"),
        port="5432",
        table_name=TABLE_NAME,
        embed_dim=768,
        hybrid_search=True,
        text_search_config="english",
    )

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )

    logger.info("Loading documents...")

    documents = SimpleDirectoryReader(
        input_dir=DATA_FOLDER,
        recursive=True,
        file_extractor={
            ".pdf": UnstructuredReader(),
            ".docx": DocxReader(),
            ".csv": PandasCSVReader(),
        }
    ).load_data(show_progress=True)

    print(f"\nLoaded {len(documents)} documents")

    for i, doc in enumerate(documents):
        print(f"\n--- DOC {i} ---")
        print("Text length:", len(doc.text))
        print("Preview:", doc.text[:200])

    if not documents:
        raise ValueError("No documents found.")

    for doc in documents:
        doc.metadata["indexed_at"] = datetime.datetime.now().isoformat()

    logger.info("Building index...")

    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True
    )

    logger.info("Index built successfully.")


if __name__ == "__main__":
    build_index()