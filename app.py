import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_community.document_loaders import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# your router graph
from router import router

# --------------------------------------------------
# ENV SETUP
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# LOAD FINANCIAL DATA
# --------------------------------------------------
print("Loading financial data...")

csv_path = os.path.join(
    os.path.dirname(__file__),
    "data",
    "FinancialStatements.csv"
)

loader = CSVLoader(
    file_path=csv_path,
    encoding="utf-8-sig" 
)

documents = loader.load()

if not documents:
    raise ValueError(" No documents loaded!")

print("\nSample record:")
print(documents[0])

# --------------------------------------------------
# TEXT SPLITTING
# --------------------------------------------------
print("\nSplitting documents...")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_documents(documents)

print(f"Created {len(chunks)} chunks")

# --------------------------------------------------
# EMBEDDINGS (LOCAL & FAST)
# --------------------------------------------------
print("\nLoading embedding model (first run may take time)...")

embedding = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5"   
)

# --------------------------------------------------
# VECTOR STORE (FAISS)
# --------------------------------------------------
print("\nBuilding FAISS index...")

vector_store = FAISS.from_documents(chunks, embedding)

retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4}
)

print("FAISS index ready")

# --------------------------------------------------
# INITIAL STATE (LangGraph Memory)
# --------------------------------------------------
state = {
    "messages": [],
    "financeSheet": documents,
    "summary": "",
    "next": "",
    "retriever": retriever,
}

thread_id = "cfo-session"

# --------------------------------------------------
# CLI LOOP
# --------------------------------------------------
print("\n CFOBuddy AI Ready")
print("Type 'exit' to quit\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye 👋")
        break

    # store user message
    state["messages"].append(HumanMessage(content=user_input))

    # invoke router graph
    result = router.invoke(
        state,
        config={"configurable": {"thread_id": thread_id}},
    )

    ai_reply = result["messages"][-1].content

    print("\nCFOBuddy:", ai_reply, "\n")

    # update state
    state = result