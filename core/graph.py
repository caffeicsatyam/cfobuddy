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
from tools.web_search import brave_search

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
4. search — search the any web based new and services when asked from duck duck go.
5. get_financial_data — live stock data (yfinance + Twelve Data):
   use data_type: 'quote' 'income' 'balance' 'cashflow' 'metrics' 'ratings' 'news' 'profile' 'history' 'realtime'

Routing rules:
- For greetings, thanks, or casual conversation → respond directly, NO tools
- For specific IDs/numbers in internal data → use exact_lookup
- For questions about internal CSV/PDF files → use search_financial_docs
- For live stock prices, financials, ratings of public companies → use get_financial_data
- For current news or general web queries → use search
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
You are a financial data presenter. Your ONLY job is to present the retrieved data clearly.

STRICT RULES — NEVER BREAK THESE:
- NEVER change, modify, round, or recalculate any numbers
- NEVER add information that is not in the retrieved data
- NEVER guess, infer, or hallucinate missing data
- NEVER calculate percentages, ratios, or derived metrics yourself
- Copy ALL financial figures EXACTLY as they appear in the source
- If data is not found, say "Data not found in the provided documents"
- Do NOT add recommendations, conclusions, or opinions unless explicitly asked

FORMATTING RULES:
- For PDF/narrative data: present as clean bullet points preserving exact numbers
- For CSV/tabular data: present as a neat labeled list or table
- For stock/API data: present with proper units (₹, $, B, M, %)
- Always mention the source at the end e.g. (Source: zomato_shareholder_letter.pdf)
- Keep response concise — only include what was asked

Response to present:
{response}
"""

# ==========================
# TOOL SETS
# ==========================

Basic_tools = [search_financial_docs, exact_lookup, list_available_files, brave_search]
internal_tool_node = ToolNode(Basic_tools)

finance_tools = [get_financial_data,  brave_search]
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
#
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
graph_builder.add_conditional_edges(
    "finance_node",
    tools_condition,
    {
        "tools": "finance_tools",
        END: END     
    }
)

# ==========================
# COMPILE
# ==========================

CFOBuddy = graph_builder.compile(checkpointer=checkpointer)