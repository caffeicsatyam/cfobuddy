import os
import glob
import pandas as pd
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS

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
# LOAD FAISS INDEX
# ==========================

vector_store = FAISS.load_local(
    "faiss_index",
    embeddings=embeddings,
    allow_dangerous_deserialization=True
)

if not os.path.exists("faiss_index"):
    raise FileNotFoundError(
        "No FAISS index found.\n"
        "Please add your CSV files to the data/ folder and run:\n"
        "    python build_index.py"
    )

vector_store = FAISS.load_local(
    "faiss_index",
    embeddings=embeddings,
    allow_dangerous_deserialization=True
)

# ==========================
# LOAD ALL CSVs INTO DATAFRAMES (for exact lookup)
# ==========================

DATA_FOLDER = "data"
dataframes = {}

for filepath in glob.glob(os.path.join(DATA_FOLDER, "*.csv")):
    filename = os.path.basename(filepath)
    try:
        df = pd.read_csv(filepath)
        # Normalize column names: strip spaces, lowercase
        df.columns = df.columns.str.strip().str.lower()
        dataframes[filename] = df
    except Exception as e:
        print(f"Warning: Could not load {filename} for exact search: {e}")

# ==========================
# LLM
# ==========================



# ==========================
# TOOLS
# ==========================

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

# ==========================
# AGENT
# ==========================

agent = create_agent(
    model=llm,
    tools=[search_financial_docs, exact_lookup],
    system_prompt="""
You are CFO Buddy, an intelligent financial data assistant.

You have access to multiple datasets including financial statements,
customer accounts, cards, transactions, and more.

You have TWO tools:
1. search_financial_docs — for general/semantic questions
2. exact_lookup — for specific ID, account, card number lookups

Rules:
- For questions with specific IDs, numbers, or exact values → use exact_lookup
- For general questions, summaries, trends → use search_financial_docs
- Always present data clearly with proper labels
- Always mention which file the data came from
- If data is not found, say so clearly
"""
)

# ==========================
# RESPONSE PARSER
# ==========================

def parse_response(content):
    """Handle all Gemini response formats."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, str):
                text_parts.append(block)
            elif isinstance(block, dict):
                text = block.get("text") or block.get("content") or ""
                if text:
                    text_parts.append(text)
        result = "\n".join(text_parts)
        if result:
            return result

    return str(content)

# ==========================
# CHAT LOOP
# ==========================

print("=" * 50)
print("  CFO Buddy — Ready!")
print("  Type 'exit' to quit.")
print("=" * 50 + "\n")

while True:

    user_input = input("You: ").strip()

    if user_input.lower() in ["quit", "exit"]:
        print("Goodbye!")
        break

    if not user_input:
        continue

    try:
        response = agent.invoke({
            "messages": [
                {"role": "user", "content": user_input}
            ]
        })

        last_message = response["messages"][-1]
        content = parse_response(last_message.content)
        print("\nCFO Buddy:", content, "\n")

    except Exception as e:
        print("\nError:", e, "\n")