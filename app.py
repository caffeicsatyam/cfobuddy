import os
import glob
import pandas as pd

from langgraph.graph import StateGraph, MessagesState, START, END
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict, NotRequired
from pydantic import BaseModel

from dotenv import load_dotenv

checkpointer = InMemorySaver()

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

class State(TypedDict):
    message: str
    obj: NotRequired[object]
    file_name: str


def call_faiss_index(state: State):
    """ 
    Search for the vector store in the files
    """
    if not os.path.exists("faiss_index"):
        raise FileExistsError(" No Vectore Store Found !")
    else :
        return FAISS.load_local(
            "faiss_index",
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
vector_store = call_faiss_index()

def Search_files():
    """
    Search for All the types of file present in data folder.
    """
    DATA_FOLDER = []
    dataframes = {}

    for filepath in glob.glob(os.path.join(DATA_FOLDER, "*.csv")):
        filename = os.path.basename(filepath)
        try:
            df = pd.read_csv(filepath)
            df.columns = df.columns.str.strip().str.lower()
            dataframes[filename] = df
        except Exception as e:
            print(f"Warning: Could not load {filename} for exact search: {e}")

    return {DATA_FOLDER: list, dataframes: dict}

files = Search_files()

@tool
def search_financial_docs(query: str) -> str:
    """
    Search across all financial and customer data documents using semantic
    similarity. Best for general questions, summaries, and keyword-based queries.
    """
    docs = vector_store.similarity_search(query, k=5)
    formatted = []

    for i, doc in enumerate(docs):
        source = doc.metadata.get("source_file", doc.metadata.get("source", "unknown"))
        formatted.append(f"[Source: {source}]\n{doc.page_content}")

    return "\n\n".join(formatted)


@tool
def exact_lookup(file_name: str, column: str, value: str) -> str:
    """
    Perform an exact lookup in a CSV file by matching a column to a value.
    Use this for specific ID lookups, account numbers, card numbers, client IDs etc.

    Args:
        file_name: CSV filename e.g. 'cards_data.csv'
        column: column name to search in e.g. 'client_id', 'id', 'card_number'
        value: exact value to match e.g. '825'
    """
    dataframes = files.dataframe
    if file_name not in dataframes:
        available = ", ".join(dataframes.keys())
        return f"File '{file_name}' not found. Available files: {available}"

    df = dataframes[file_name]
    col = column.strip().lower()

    if col not in df.columns:
        available = ", ".join(df.columns.tolist())
        return f"Column '{column}' not found in {file_name}. Available columns: {available}"

    # Match as string to handle both int and string columns
    matches = df[df[col].astype(str).str.strip() == str(value).strip()]

    if matches.empty:
        return f"No records found in {file_name} where {column} = {value}"

    results = []
    for _, row in matches.iterrows():
        results.append(row.to_string())

    return f"[Source: {file_name}]\nFound {len(matches)} record(s):\n\n" + "\n\n---\n\n".join(results)


class OutputSchema(BaseModel):
    """Schema for response."""
    answer: str
    justification: str


structured_llm = llm.bind_tools(
    [exact_lookup, search_financial_docs, Search_files],
    response = OutputSchema,
    strict=True
)

def chat_node(state: State):
    message = state["message"]
    response = structured_llm.invoke(message)
    return {'message' : response}

graph = StateGraph(State)

graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)
