import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

from graphs.chat_graph import chat_node
from graphs.analytics_graph import Analytic_node
from graphs.invoice_graph import invoice_node

from Tools import tools

from dotenv import load_dotenv


# --------------------------------------------------
# ENV SETUP & LLM
# --------------------------------------------------
load_dotenv()
hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

router_endpoint = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    temperature=0,
    max_new_tokens=10,
    huggingfacehub_api_token=hf_token,
)

router_llm = ChatHuggingFace(llm=router_endpoint)
llm_with_tools = router_llm.bind_tools(tools)


class GlobalState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    financeSheet: object
    summary: str
    next: str


def router_node(state: GlobalState):
    user_msg = state["messages"][-1].content

    prompt = f"""You are an intelligent router for a financial assistant system.

    and as "user_msg" asks.
    User query: {user_msg}"""

    decision = router_llm.invoke(prompt).content.strip().lower()

    # Fallback to chat if decision is not recognized
    if decision not in ["analytics", "invoice", "chat"]:
        decision = "chat"
    return {"next": decision}


graph = StateGraph(GlobalState)

graph.add_node("router", router_node)
graph.add_node("chat", chat_node)
graph.add_node("analytics", Analytic_node)
graph.add_node("invoice", invoice_node)

graph.add_edge(START, "router")

graph.add_conditional_edges(
    "router",
    lambda s: s["next"],
    {
        "chat": "chat",
        "analytics": "analytics",
        "invoice": "invoice",
    },
)

graph.add_edge("chat", END)
graph.add_edge("analytics", END)
graph.add_edge("invoice", END)

router = graph.compile()
