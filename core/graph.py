from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from core.state import State
from core.memory import checkpointer
from core.llm import llm
from tools import all_tools

# ==========================
# SYSTEM PROMPT
# ==========================

SYSTEM_PROMPT = SystemMessage(content="""
You are CFO Buddy, an intelligent financial data assistant.
You are expert in finance and finace buddy to CFO.

You have access to multiple datasets including financial statements,
customer accounts, cards, transactions, and more.

Tools available:
1. search_financial_docs — semantic search across your CSV data
2. exact_lookup — precise lookup by ID, account number, card number etc.
3. list_available_files — see what files and columns are available
4. brave_search — search the web for current news and market data
5. get_finance_data - returns 'quote' 'income'  'balance' 'cashflow' 'metrics' 'ratings'  'news' 'profile'  of any publicly available companies.

Rules:
- ONLY use tools when the user is asking a data question
- For greetings, thanks, or casual conversation → respond directly, NO tools
- For specific IDs/numbers → use exact_lookup
- For questions about internal data/CSVs → use search_financial_docs
- For current news, live market data → use brave_search
- If unsure what files exist → use list_available_files first
- Always present data clearly with labels and source file name
""")

# ==========================
# LLM WITH TOOLS
# ==========================

llm_with_tools = llm.bind_tools(all_tools, parallel_tool_calls=False)

# ==========================
# NODES
# ==========================

def model_node(state: State):
    """LLM node — decides whether to call tools or respond directly."""
    messages = [SYSTEM_PROMPT] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def upload_node(state: State):
    """
    Upload node — placeholder for future file upload handling.
    Will build per-session FAISS index from uploaded files.
    Currently just passes through.
    """
    return state

# ==========================
# BUILD GRAPH
# ==========================

graph_builder = StateGraph(State)

graph_builder.add_node("upload_node", upload_node)
graph_builder.add_node("model", model_node)
graph_builder.add_node("tools", ToolNode(all_tools))

graph_builder.add_edge(START, "upload_node")
graph_builder.add_edge("upload_node", "model")
graph_builder.add_conditional_edges("model", tools_condition)
graph_builder.add_edge("tools", "model")

# ==========================
# COMPILE
# ==========================

CFOBuddy = graph_builder.compile(checkpointer=checkpointer)