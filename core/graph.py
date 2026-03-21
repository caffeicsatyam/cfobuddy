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
from tools.web_search import web_search
from tools.sql import sql_query, list_tables

# ==========================
# SYSTEM PROMPTS
# ==========================

SYSTEM_PROMPT = SystemMessage(content="""
You are CFO Buddy, an intelligent financial data assistant and finance buddy to the CFO.

You have access to multiple datasets including financial statements,
customer accounts, cards, transactions, and more.

Tools available:
1. search_financial_docs — semantic search across PDF/Word documents (NOT for math)
2. sql_query — EXACT SQL on CSV data in Neon — use for ALL math, averages, sums, counts, filters, rankings
3. list_tables — list available database tables and columns
4. exact_lookup — precise lookup by ID, account number, card number etc.
5. list_available_files — see what files are available
6. web_search — search the web for news and general queries via DuckDuckGo
7. get_financial_data — live stock data (yfinance + Twelve Data):
   use data_type: 'quote' 'income' 'balance' 'cashflow' 'metrics' 'ratings' 'news' 'profile' 'history' 'realtime'

Routing rules:
- For greetings, thanks, or casual conversation → respond directly, NO tools
- Questions with math, averages, sums, counts, rankings on CSV data → sql_query
- Questions about PDF/Word documents, narratives → search_financial_docs
- Specific row lookup by ID → exact_lookup
- Unsure what tables exist → list_tables first
- Unsure what files exist → list_available_files first
- Live stock prices, financials, ratings of public companies → get_financial_data
- Current news or general web queries → web_search
- When user mentions a specific file (e.g. 'from zomato.pdf') → ALWAYS use search_financial_docs
- After retrieving data with any tool → always summarize clearly, never dump raw output
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

# ==========================
# TOOL SETS
# ==========================

basic_tools = [search_financial_docs, exact_lookup, list_available_files, web_search, sql_query, list_tables]
internal_tool_node = ToolNode(basic_tools)

finance_tools = [get_financial_data, web_search]
finance_tool_node = ToolNode(finance_tools)

# ==========================
# LLM BINDINGS
# ==========================

llm_with_tools = llm.bind_tools(all_tools, parallel_tool_calls=False)
llm_finance = llm.bind_tools(finance_tools, parallel_tool_calls=False)

# ==========================
# ROUTER
# ==========================

def route_after_upload(state: State):
    """Let the LLM decide routing instead of keyword matching."""
    last_message = state["messages"][-1]

    router_prompt = f"""You are a query router. Classify this query into one of two categories:

1. "finance_node" - ONLY for live market data queries:
   - Real-time stock prices, quotes
   - Live market cap, PE ratio
   - Current analyst ratings
   - Stock news from today

2. "model" - For everything else:
   - Questions about uploaded documents (PDFs, CSVs)
   - Historical financial data from internal files
   - Customer/account data lookups
   - Math, aggregations, calculations on internal data
   - General financial questions

Query: {last_message.content}

Reply with ONLY "finance_node" or "model". Nothing else."""

    response = llm.invoke(router_prompt)
    decision = response.content.strip().lower()

    if "finance_node" in decision:
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


@traceable(run_type="chain")
def finance_node(state: State):
    """Finance LLM node — handles public company/market queries via Yahoo Finance API."""
    messages = [FINANCE_PROMPT] + state["messages"]
    response = llm_finance.invoke(messages)
    return {"messages": [response]}

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
#              |
#            [END]
# ==========================

graph_builder = StateGraph(State)

graph_builder.add_node("upload_node", upload_node)
graph_builder.add_node("model", model_node)
graph_builder.add_node("finance_node", finance_node)
graph_builder.add_node("internal_tools", internal_tool_node)
graph_builder.add_node("finance_tools", finance_tool_node)

# Entry
graph_builder.add_edge(START, "upload_node")

graph_builder.add_conditional_edges(
    "upload_node",
    route_after_upload,
    {
        "model": "model",
        "finance_node": "finance_node"
    }
)

graph_builder.add_conditional_edges(
    "model",
    tools_condition,
    {
        "tools": "internal_tools",
        END: END
    }
)

graph_builder.add_edge("internal_tools", "model")

graph_builder.add_conditional_edges(
    "finance_node",
    tools_condition,
    {
        "tools": "finance_tools",
        END: END
    }
)

graph_builder.add_edge("finance_tools", "finance_node")

# ==========================
# COMPILE
# ==========================

CFOBuddy = graph_builder.compile(checkpointer=checkpointer)