from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from dotenv import load_dotenv
import os

# --------------------------------------------------
# ENV SETUP
# --------------------------------------------------
load_dotenv()
hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

hf_model = "Qwen/Qwen2.5-7B-Instruct"

endpoint = HuggingFaceEndpoint(
    repo_id=hf_model,
    temperature=0.7,
    max_new_tokens=256,
    huggingfacehub_api_token=hf_token,
)

llm = ChatHuggingFace(llm=endpoint)

# -------------------------------------------------
# STATE (must match router/global state)
# --------------------------------------------------
class AnalyticsState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    financeSheet: object
    summary: str
    next: str

# --------------------------------------------------
# ANALYTICS NODE
# --------------------------------------------------
def Analytic_node(state: AnalyticsState):
    """
    Analytics node that processes financial data.
    Receives data from app.py via state - does NOT load CSV directly.
    """
    messages = state["messages"]
    finance_data = state["financeSheet"]  # Data passed from app.py

    # Debug: Show what data we're receiving from app.py
    print("\n[DEBUG] Analytics Node Called")
    print(f"[DEBUG] Fetching financial data from app.py state...")
    print(f"[DEBUG] Received {len(finance_data)} financial records from app.py")
    
    if finance_data:
        print(f"[DEBUG] First record: {finance_data[0]}")
        data_summary = f"Financial data from app.py: {len(finance_data)} records available\n\nSample: {finance_data[0]}"
    else:
        data_summary = "No financial data provided from app.py"
        print("[DEBUG] WARNING: No financial data from app.py!")

    system_prompt = """You are CFOBuddy Analytics, an expert financial analyst. 
You analyze financial data provided and give insights."""

    prompt = f"""{system_prompt}

{data_summary}

User query: {messages[-1].content}

Provide a concise financial analysis."""

    print(f"[DEBUG] Sending to LLM with {len(prompt)} characters")
    response = llm.invoke(prompt)
    print(f"[DEBUG] LLM Response received")

    return {
        "messages": messages + [response],
        "summary": response.content,
    }