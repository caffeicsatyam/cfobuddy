import datetime
import os

from dotenv import load_dotenv
from llama_index.core import Settings, SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.file import DocxReader, PandasCSVReader
from llama_index.vector_stores.postgres import PGVectorStore

from cfobuddy_logging import configure_logging

load_dotenv()
logger = configure_logging()

DATA_FOLDER = "data"
TABLE_NAME = "data_cfo_buddy_vectors"


def _configure_embed_model() -> None:
    nvidia_api_key = os.getenv("NVIDIA_EMBEDDING_API_KEY")

    if nvidia_api_key:
        try:
            from llama_index.embeddings.nvidia import NVIDIAEmbedding

            Settings.embed_model = NVIDIAEmbedding(
                model="nvidia/nv-embed-v1",
                api_key=nvidia_api_key,
            )
            return
        except ImportError:
            logger.warning(
                "llama_index NVIDIA embedding package is unavailable; falling back to HuggingFace embeddings."
            )

    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    Settings.embed_model = HuggingFaceEmbedding(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        embed_batch_size=32,
    )


def build_index() -> None:
    """Build and store hybrid vectors in Neon DB."""

    _configure_embed_model()
    Settings.llm = None
    Settings.node_parser = SentenceSplitter(chunk_size=256, chunk_overlap=50)

    vector_store = PGVectorStore.from_params(
        host=os.getenv("NEON_HOST"),
        database=os.getenv("NEON_DATABASE"),
        user=os.getenv("NEON_USER"),
        password=os.getenv("NEON_PASSWORD"),
        port="5432",
        table_name=TABLE_NAME,
        embed_dim=4096,
        hybrid_search=True,
        text_search_config="english",
    )

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    logger.info("Loading documents from '%s'...", DATA_FOLDER)

    documents = SimpleDirectoryReader(
        input_dir=DATA_FOLDER,
        recursive=True,
        file_extractor={
            ".docx": DocxReader(),
            ".csv": PandasCSVReader(),
        },
    ).load_data(show_progress=True)

    if not documents:
        raise ValueError("No documents found.")

    for doc in documents:
        doc.metadata["indexed_at"] = datetime.datetime.now().isoformat()

    logger.info("Building index with %d documents...", len(documents))

    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True,
    )

    logger.info("Index built successfully!")


if __name__ == "__main__":
    build_index()
