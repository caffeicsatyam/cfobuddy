from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langsmith import traceable

from core.state import State
from core.memory import checkpointer
from core.llm import llm
from tools import all_tools
from tools.finance import get_financial_data
from tools.search import search_financial_docs
from tools.lookup import exact_lookup, list_available_files
from tools.web_search import search

# ==========================
# SYSTEM PROMPTS
# ==========================

SYSTEM_PROMPT = SystemMessage(content="""
You are CFO Buddy, an intelligent financial data assistant and finance buddy to the CFO.

You have access to multiple datasets including financial statements,
customer accounts, cards, transactions, and more.

Tools available:
1. search_financial_docs — semantic search across internal CSV/PDF data
2. exact_lookup — precise lookup by ID, account number, card number etc.
3. list_available_files — see what files and columns are available
4. search — search the any web based new and services when asked.
5. get_financial_data — live stock data (yfinance + Twelve Data):
   use data_type: 'quote' 'income' 'balance' 'cashflow' 'metrics' 'ratings' 'news' 'profile' 'history' 'realtime'

Routing rules:
- For greetings, thanks, or casual conversation → respond directly, NO tools
- For specific IDs/numbers in internal data → use exact_lookup
- For questions about internal CSV/PDF files → use search_financial_docs
- For live stock prices, financials, ratings of public companies → use get_financial_data
- For current news or general web queries → use brave_search
- If unsure what files exist → use list_available_files first
- Always present data clearly with labels and mention the source
""")

FINANCE_PROMPT = SystemMessage(content="""
You are a Finance Expert and CFO's trusted advisor.

Your job is to retrieve and interpret financial data for publicly traded companies.
Use the get_financial_data tool to answer any finance-related query.

Available data_types: 'quote', 'income', 'balance', 'cashflow', 'metrics', 'ratings', 'news', 'profile', 'history', 'realtime'

Always:
- Present numbers clearly with units (B for billions, M for millions)
- Highlight key insights after presenting data
- Compare periods when multiple results are returned
- For price history → use 'history' with appropriate limit
- For most up-to-date real-time price → use 'realtime'
""")

SUMMARY_PROMPT = """
Summarize the following financial response concisely.
Keep all key numbers, insights, and sources accurate.
Format clearly for a CFO.

Response:
{response}
"""

# ==========================
# TOOL SETS
# ==========================

Basic_tools = [search_financial_docs, exact_lookup, list_available_files, search]
internal_tool_node = ToolNode(Basic_tools)

finance_tools = [get_financial_data]
finance_tool_node = ToolNode(finance_tools)

# ==========================
# LLM BINDINGS
# ==========================

llm_with_tools = llm.bind_tools(all_tools, parallel_tool_calls=False)
llm_finance = llm.bind_tools(finance_tools, parallel_tool_calls=False)

# ==========================
# ROUTER
# ==========================

def route_query(state: State):
    """Route to finance_node or internal_tools based on last message."""
    last_message = state["messages"][-1]

    # If LLM made a tool call, route to correct tool node
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_name = last_message.tool_calls[0]["name"]
        if tool_name == "get_financial_data":
            return "finance_tools"
        return "internal_tools"

    return END


def route_after_upload(state: State):
    """Route to finance_node or model after upload."""
    last_message = state["messages"][-1]
    content = last_message.content.lower()

    finance_keywords = [
        "stock", "price", "quote", "market cap", "revenue", "earnings",
        "balance sheet", "cash flow", "income statement", "analyst",
        "rating", "pe ratio", "eps", "dividend", "ipo", "nasdaq", "nyse",
        "profit", "loss", "quarterly", "annual report", "ticker"
    ]

    if any(kw in content for kw in finance_keywords):
        return "finance_node"
    return "model"

# ==========================
# NODES
# ==========================

def upload_node(state: State):
    """Placeholder for future file upload handling."""
    return state


def model_node(state: State):
    """Main LLM node — handles internal data queries."""
    messages = [SYSTEM_PROMPT] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


@traceable(run_type="chain")   # Bug fix: run_type must be 'chain', 'llm', or 'tool'
def finance_node(state: State):
    """Finance LLM node — handles public company/market queries via Yahoo Finance API."""
    messages = [FINANCE_PROMPT] + state["messages"]
    response = llm_finance.invoke(messages)
    return {"messages": [response]}


def summarize_node(state: State):
    """Summarize only if response contains actual financial data."""
    last_message = state["messages"][-1]
    content = last_message.content

    # Skip summarizing short or conversational responses
    financial_indicators = [
        "$", "revenue", "profit", "loss", "ratio", "income",
        "balance", "cash", "equity", "assets", "earnings", "pe",
        "quarter", "annual", "billion", "million", "source:"
    ]

    is_financial = any(kw in content.lower() for kw in financial_indicators)
    is_long = len(content) > 300

    if not (is_financial and is_long):
        return state  # pass through unchanged

    prompt = SUMMARY_PROMPT.format(response=content)
    summary = llm.invoke(prompt)
    return {"messages": [summary]}

# ==========================
# BUILD GRAPH
#
#           [START]
#              |
#         [upload_node]
#              |
#     finance keywords?
#       /            \
# [finance_node]   [model]
#       |              |
# [finance_tools] [internal_tools]
#       \              /
#        [summarize_node]
#              |
#            [END]
# ==========================

graph_builder = StateGraph(State)

graph_builder.add_node("upload_node", upload_node)
graph_builder.add_node("model", model_node)
graph_builder.add_node("finance_node", finance_node)
graph_builder.add_node("internal_tools", internal_tool_node)
graph_builder.add_node("finance_tools", finance_tool_node)
graph_builder.add_node("summarize_node", summarize_node)

# Entry
graph_builder.add_edge(START, "upload_node")

# Route after upload based on query type
graph_builder.add_conditional_edges(
    "upload_node",
    route_after_upload,
    {
        "model": "model",
        "finance_node": "finance_node"
    }
)

# Model → internal tools loop → summarize
graph_builder.add_conditional_edges(
    "model",
    tools_condition,
    {
        "tools": "internal_tools",
        END: "summarize_node"
    }
)
graph_builder.add_edge("internal_tools", "model")

# Finance → finance tools loop → summarize
graph_builder.add_conditional_edges(
    "finance_node",
    tools_condition,
    {
        "tools": "finance_tools",
        END: "summarize_node"
    }
)
graph_builder.add_edge("finance_tools", "finance_node")

# Summarize → END
graph_builder.add_edge("summarize_node", END)

# ==========================
# COMPILE
# ==========================

CFOBuddy = graph_builder.compile(checkpointer=checkpointer)