from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

from graphs.chat_graph import chat_node
from graphs.analytics_graph import Analytic_node
from graphs.invoice_graph import invoice_node


class GlobalState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    financeSheet: object
    summary: str
    next: str


def router_node(state: GlobalState):
    msg = state["messages"][-1].content.lower()

    if "invoice" in msg:
        return {"next": "invoice"}

    if "profit" in msg or "finance" in msg:
        return {"next": "analytics"}

    return {"next": "chat"}


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

print(router.get_graph().draw_ascii())