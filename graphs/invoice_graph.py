from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

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
    temperature=0.2,
    max_new_tokens=512,
    huggingfacehub_api_token=hf_token,
)

llm = ChatHuggingFace(llm=endpoint)

# --------------------------------------------------
# GLOBAL STATE (must match router)
# --------------------------------------------------
class InvoiceState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    financeSheet: object
    summary: str
    next: str

# --------------------------------------------------
# INVOICE NODE
# --------------------------------------------------
def invoice_node(state: InvoiceState):
    user_input = state["messages"][-1].content

    prompt = f"""
You are an accounting assistant.

Extract invoice details from the user's request and create a professional invoice.

Return the invoice in this format:

Invoice Number:
Date:

Bill To:
Client Name
Address

Items:
- item | quantity | price | total

Subtotal:
Tax (18%):
Grand Total:

User Request:
{user_input}
"""

    response = llm.invoke(prompt)

    return {
        "messages": state["messages"] + [response],
        "summary": response.content,
    }

# --------------------------------------------------
# GRAPH BUILD (optional standalone use)
# --------------------------------------------------
checkpointer = InMemorySaver()

graph = StateGraph(InvoiceState)

graph.add_node("invoice", invoice_node)
graph.add_edge(START, "invoice")
graph.add_edge("invoice", END)

invoice_agent = graph.compile(checkpointer=checkpointer)

# --------------------------------------------------
# OPTIONAL DIRECT CALL FUNCTION
# --------------------------------------------------
def generate_invoice(message):
    state = {
        "messages": [message],
        "financeSheet": None,
        "summary": "",
        "next": "",
    }
    return invoice_agent.invoke(state)