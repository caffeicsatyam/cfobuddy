import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

conn = sqlite3.connect("memory.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)


def retrieve_all_threads():
    """Return all existing thread IDs from memory."""
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        thread_id = checkpoint.config["configurable"]["thread_id"]
        all_threads.add(thread_id)
    return list(all_threads)