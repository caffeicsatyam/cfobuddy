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
    max_new_tokens=512,
    huggingfacehub_api_token=hf_token,
)

llm = ChatHuggingFace(llm=endpoint)

# --------------------------------------------------
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
    messages = state["messages"]
    finance_data = state["financeSheet"]

    system_prompt = """
    You are CFOBuddy Analytics, an expert financial analyst. You help analyze financial statements and provide insights."""

    prompt = system_prompt + "\n\nFinancial Data:\n" + str(finance_data) + "\n\nQuestion: " + messages[-1].content

    response = llm.invoke(prompt)

    return {
        "messages": messages + [response],
    }