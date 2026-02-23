
from langgraph.graph import StateGraph, START, END
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict, Annotated

# ----------------------------                                   -----------
#   CREATES INVOICE OF THE ANLYSED DATASET
# ---------------------------                                    -----------


