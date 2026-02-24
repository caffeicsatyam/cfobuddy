from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

from langchain_core.messages import BaseMessage
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

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
class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    financeSheet: object
    summary: str
    next: str

# --------------------------------------------------
# CHAT NODE
# --------------------------------------------------
def chat_node(state: ChatState):
    messages = state["messages"]

    system_prompt = """
    You are CFOBuddy, an AI assistant for CFOs. You help answer questions about financial data and provide insights."""

    prompt = system_prompt + "\n\n" + messages[-1].content

    response = llm.invoke(prompt)

    return {
        "messages": messages + [response],
    }

# --------------------------------------------------
# GRAPH BUILD
# --------------------------------------------------
checkpointer = InMemorySaver()

graph = StateGraph(ChatState)

graph.add_node("chat", chat_node)

graph.add_edge(START, "chat")
graph.add_edge("chat", END)

chatbot = graph.compile(checkpointer=checkpointer)

# --------------------------------------------------
# OPTIONAL DIRECT CALL FUNCTION
# --------------------------------------------------
def chat(message, financeSheet=None):
    state = {
        "messages": [message],
        "financeSheet": financeSheet,
        "summary": "",
        "next": "",
    }
    return chatbot.invoke(state)