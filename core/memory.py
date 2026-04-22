import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver

load_dotenv()

DB_URI = os.environ["DATABASE_URL"]

_conn = psycopg.connect(
    DB_URI,
    autocommit=True,
    prepare_threshold=0,
    row_factory=dict_row,
)

checkpointer = PostgresSaver(_conn)

checkpointer.setup()

def retrieve_all_threads():
    """Return all existing thread IDs from memory."""
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        thread_id = checkpoint.config["configurable"]["thread_id"]
        all_threads.add(thread_id)
    return list(all_threads)