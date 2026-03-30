import os
from dotenv import load_dotenv
import datetime
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.file import PyMuPDFReader
from llama_index.vector_stores.postgres import PGVectorStore
from cfobuddy_logging import configure_logging
from llama_index.core.node_parser import SentenceSplitter

load_dotenv()
logger = configure_logging()

DATA_FOLDER = "data"

def build_index():
    """Build and store vectors in Neon DB."""

    required = ["NEON_HOST", "NEON_DATABASE", "NEON_USER", "NEON_PASSWORD"]
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        raise ValueError(f"Missing: {missing}") 

    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-base-en-v1.5",
    )
    Settings.llm = None
    Settings.node_parser = SentenceSplitter(
        chunk_size=1024,
        chunk_overlap=200
    )

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
    except Exception as e:
        logger.error("Failed to connect to Neon: %s", e)
        raise

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    logger.info("Loading files from '%s/'...", DATA_FOLDER)
    documents = SimpleDirectoryReader(
        input_dir=DATA_FOLDER,
        recursive=True,
        filename_as_id=True,
        file_extractor={".pdf": PyMuPDFReader()}
    ).load_data(show_progress=True)

    for doc in documents:
        doc.metadata["indexed_at"] = datetime.datetime.now().isoformat()
        doc.metadata["source_folder"] = DATA_FOLDER

    if not documents:
        raise ValueError(f"No documents found in '{DATA_FOLDER}/'.")

    logger.info("Loaded %s document chunks.", len(documents))
    logger.info("Building index and storing in Neon DB...")

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=False
    )

    logger.info("Vectors stored in Neon DB.")

    from tools.search import reload_index
    reload_index()


if __name__ == "__main__":
    build_index()